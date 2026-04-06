"""
Two-stage thesis supervisor matcher.

Stage 1 — Embedding filter (fast, cheap)
    Encodes the student profile and every professor profile into embedding
    vectors. Computes cosine similarity and returns the top-K candidates.

Stage 2 — Claude reranker (nuanced, expensive)
    Sends the student profile + top-K candidates to Claude.
    Claude reasons about factors that embeddings miss:
      - Methodology alignment (quantitative vs qualitative)
      - Temporal/availability signals
      - Industry vs academic orientation mismatch
      - Whether the student's experience level fits the prof's expectations
    Returns final ranked results with per-match explanations.

Usage:
    from src.data_processing.profile_builder import ProfileStore
    from src.matching.matcher import ThesisMatcher

    store = ProfileStore()
    matcher = ThesisMatcher(store)
    results = matcher.match(student_profile, embed_top_k=20, final_top_k=5)
    for r in results:
        print(r)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Optional

from src.models.professor import ProfessorProfile
from src.models.student import StudentProfile


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class MatchResult:
    professor: ProfessorProfile
    embedding_score: float          # cosine similarity [0, 1]
    embedding_rank: int             # rank in stage-1 output (1 = best)

    # Stage-2 fields — populated only after Claude reranking
    claude_rank: Optional[int] = None
    claude_score: Optional[float] = None   # 0–10
    topic_fit: Optional[int] = None        # 0–10
    methodology_fit: Optional[int] = None  # 0–10
    strengths: list[str] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)
    summary: Optional[str] = None

    def __str__(self) -> str:
        rank = self.claude_rank or self.embedding_rank
        score = self.claude_score or round(self.embedding_score * 10, 1)
        sep = "-" * 56
        lines = [
            sep,
            f"#{rank}  {self.professor.name}",
            f"    Match score: {score}/10"
            + (f"  (topic fit: {self.topic_fit}/10, method fit: {self.methodology_fit}/10)"
               if self.topic_fit is not None else ""),
        ]
        # Why this match — lead with the explanation
        if self.summary:
            lines.append(f"\n  Why this supervisor?\n  {self.summary}")
        if self.strengths:
            lines.append("\n  What makes it a good fit:")
            for s in self.strengths:
                lines.append(f"    • {s}")
        if self.red_flags:
            lines.append("\n  Points to discuss before committing:")
            for f in self.red_flags:
                lines.append(f"    ⚠  {f}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# ThesisMatcher
# ---------------------------------------------------------------------------

class ThesisMatcher:

    def __init__(self, store, openai_client=None):
        """
        Parameters
        ----------
        store : ProfileStore
            Loaded professor profiles.
        openai_client : openai.OpenAI, optional
            Shared client — created lazily from OPENAI_API_KEY env var if None.
            Used for embeddings only. Reranking uses NVIDIA NIM via llm_client.
        """
        self._store = store
        self._openai = openai_client

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def match(
        self,
        student: StudentProfile,
        embed_top_k: int = 20,
        final_top_k: int = 5,
        skip_claude: bool = False,
    ) -> list[MatchResult]:
        """
        Run the full two-stage matching pipeline.

        Parameters
        ----------
        student : StudentProfile
        embed_top_k : int
            How many professors to keep after stage 1 (embedding filter).
        final_top_k : int
            How many to return after stage 2 (Claude reranking).
        skip_claude : bool
            Return stage-1 results only (faster, cheaper — useful for testing).
        """
        # Stage 1
        candidates = self._embedding_stage(student, embed_top_k)

        if skip_claude:
            return candidates[:final_top_k]

        # Stage 2
        reranked = self._claude_stage(student, candidates, final_top_k)
        return reranked

    # ------------------------------------------------------------------
    # Stage 1: Embedding similarity
    # ------------------------------------------------------------------

    def _embedding_stage(
        self, student: StudentProfile, top_k: int
    ) -> list[MatchResult]:
        from src.matching.embedder import embed_text, embed_batch, cosine_similarity
        from src.data_processing.text_processing import (
            build_student_matching_text,
            build_professor_matching_text,
        )

        print(f"[Stage 1] Embedding student profile…")
        student_text = build_student_matching_text(student)
        student_vec = embed_text(student_text, client=self._openai_client())

        professors = self._store.all()
        print(f"[Stage 1] Embedding {len(professors)} professor profiles…")

        prof_texts = [
            build_professor_matching_text(prof.to_dict()) for prof in professors
        ]
        prof_vecs = embed_batch(prof_texts, client=self._openai_client())

        scored: list[tuple[ProfessorProfile, float]] = []
        for prof, vec in zip(professors, prof_vecs):
            sim = cosine_similarity(student_vec, vec)
            scored.append((prof, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:top_k]

        results = [
            MatchResult(
                professor=prof,
                embedding_score=score,
                embedding_rank=rank + 1,
            )
            for rank, (prof, score) in enumerate(top)
        ]
        print(f"[Stage 1] Top {top_k} candidates selected.")
        return results

    # ------------------------------------------------------------------
    # Stage 2: Claude reranker
    # ------------------------------------------------------------------

    def _claude_stage(
        self,
        student: StudentProfile,
        candidates: list[MatchResult],
        final_top_k: int,
    ) -> list[MatchResult]:
        print(f"[Stage 2] Sending top {len(candidates)} candidates to NIM reranker…")

        student_block = _format_student(student)
        professors_block = _format_professors(candidates)

        prompt = _build_claude_prompt(student_block, professors_block, final_top_k)

        from src.agents.llm_client import chat as nim_chat
        raw = nim_chat(
            messages=[{"role": "user", "content": prompt}],
            system="You are an expert academic advisor. Return valid JSON only.",
            max_tokens=4096,
            temperature=0.3,
        )

        # Extract JSON from the response
        rankings = _parse_claude_response(raw)
        if not rankings:
            print("[Stage 2] Warning: could not parse NIM response — returning embedding order.")
            return candidates[:final_top_k]

        # Attach results to MatchResult objects
        name_to_result = {r.professor.name: r for r in candidates}
        final: list[MatchResult] = []

        for rank, item in enumerate(rankings[:final_top_k], start=1):
            name = item.get("professor_name", "")
            result = name_to_result.get(name) or _fuzzy_find(name, name_to_result)
            if result is None:
                continue
            result.claude_rank = rank
            result.claude_score = item.get("score")
            result.topic_fit = item.get("topic_fit")
            result.methodology_fit = item.get("methodology_fit")
            result.strengths = item.get("strengths", [])
            result.red_flags = item.get("red_flags", [])
            result.summary = item.get("summary", "")
            final.append(result)

        print(f"[Stage 2] Reranking complete. {len(final)} results.")
        return final

    # ------------------------------------------------------------------
    # Lazy client init
    # ------------------------------------------------------------------

    def _openai_client(self):
        if self._openai is None:
            from openai import OpenAI
            self._openai = OpenAI()
        return self._openai


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def _format_student(student: StudentProfile) -> str:
    lines = [
        f"Name: {student.first_name} {student.last_name}",
        f"Programme: {student.programme} ({student.level})",
        f"Research area: {student.research_area}",
        f"Thesis title: {student.thesis_title}",
        f"Thesis description: {student.thesis_description}",
        f"Keywords: {', '.join(student.keywords)}",
        f"Skills: {', '.join(getattr(student, 'skills', []))}",
        f"Objectives: {', '.join(getattr(student, 'objectives', []))}",
    ]
    about = getattr(student, "about", None)
    if about:
        lines.append(f"About: {about}")
    if student.additional_notes:
        lines.append(f"Additional notes: {student.additional_notes}")
    return "\n".join(lines)


def _format_professors(candidates: list[MatchResult]) -> str:
    blocks = []
    for r in candidates:
        p = r.professor
        block = [
            f"--- Professor: {p.name} (embedding rank #{r.embedding_rank}, score {r.embedding_score:.3f}) ---",
            f"Main focuses: {', '.join(p.main_focuses)}",
            f"Fields of research: {', '.join(p.fields_of_research)}",
        ]
        if p.openalex_topics:
            block.append(f"Research topics (OpenAlex): {', '.join(p.openalex_topics[:8])}")
        if p.top_publications:
            titles = [pub.title for pub in p.top_publications[:5]]
            block.append(f"Top publications: {' | '.join(titles)}")
        if p.thesis_proposals:
            proposals = [
                f"{tp.title} [{tp.research_area}]"
                for tp in p.thesis_proposals[:4]
            ]
            block.append(f"Open thesis proposals: {' | '.join(proposals)}")
        if p.courses:
            course_titles = [c.title for c in p.courses[:5]]
            block.append(f"Courses taught: {', '.join(course_titles)}")
        blocks.append("\n".join(block))
    return "\n\n".join(blocks)


def _build_claude_prompt(student_block: str, professors_block: str, final_top_k: int) -> str:
    return f"""You are an expert academic advisor helping a student find the best thesis supervisor.

## Student Profile
{student_block}

## Candidate Supervisors
These professors were pre-selected by semantic similarity. Your job is to rerank them, considering factors that semantic search misses.

{professors_block}

## Your Task
Rank the top {final_top_k} supervisors for this student. For each, provide:
- **topic_fit** (0–10): How well the professor's research matches the thesis topic
- **methodology_fit** (0–10): Does the professor's approach match the student's planned methods?
- **score** (0–10): Overall match quality
- **strengths**: 2–3 specific reasons why this professor is a good fit
- **red_flags**: Any mismatches to flag (e.g., "prof is very theory-focused, student wants empirical work")
- **summary**: 2–3 sentences written directly to the student (use "you" / "your thesis"), explaining concretely why this professor is recommended — what specific overlap exists between their research and the student's topic, and what the student can expect from working with them

## Factors to weigh
- Prioritise topic and methodology fit over shared courses
- Shared courses are a mild positive signal (background knowledge), not a strong match indicator
- If the student signals wanting industry exposure, flag professors who are very theory-focused
- Consider whether the student's skill set (e.g., Python, R, qualitative methods) aligns with what the professor typically uses
- If the student has open thesis proposals listed, those are strong matches

## Output format
Respond ONLY with valid JSON. No markdown, no explanation outside the JSON.

{{
  "rankings": [
    {{
      "professor_name": "Full name exactly as listed above",
      "score": 8.5,
      "topic_fit": 9,
      "methodology_fit": 8,
      "strengths": ["...", "..."],
      "red_flags": ["..."],
      "summary": "..."
    }}
  ]
}}"""


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------

def _parse_claude_response(raw: str) -> list[dict]:
    """Extract the rankings list from Claude's JSON response."""
    # Try direct parse first
    try:
        data = json.loads(raw.strip())
        return data.get("rankings", [])
    except json.JSONDecodeError:
        pass

    # Extract JSON block if wrapped in markdown
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        try:
            data = json.loads(raw[start:end])
            return data.get("rankings", [])
        except json.JSONDecodeError:
            pass

    return []


def _fuzzy_find(name: str, name_to_result: dict[str, MatchResult]) -> Optional[MatchResult]:
    """Match by last name if exact name lookup fails."""
    name_lower = name.lower()
    for key, result in name_to_result.items():
        if result.professor.last_name.lower() in name_lower:
            return result
    return None
