"""
Course recommender — suggests relevant courses for a thesis topic.

Two-stage pipeline (same pattern as professor matching):
  Stage 1 — Embedding cosine similarity: rank all known courses by
             relevance to the thesis topic/description.
  Stage 2 — LLM reranker: pick the top N and explain why each course
             is relevant to the specific thesis.
"""
from __future__ import annotations
import json
import os


def _load_all_courses() -> list[dict]:
    """
    Load all courses from professor_profiles.json.
    Returns a flat list of {title, professor, course_number, description}.
    """
    path = os.path.join("data", "professor_profiles.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        profiles = json.load(f)

    courses = []
    seen = set()
    for prof_name, prof in profiles.items():
        for c in prof.get("courses", []):
            title = c.get("title", "") if isinstance(c, dict) else c
            if not title or title in seen:
                continue
            seen.add(title)
            desc = ""
            if isinstance(c, dict):
                desc = c.get("pdf_content", {}).get("description", "") if isinstance(c.get("pdf_content"), dict) else ""
            courses.append({
                "title": title,
                "professor": prof_name,
                "course_number": c.get("course_number", "") if isinstance(c, dict) else "",
                "description": desc,
            })
    return courses


def _course_text(course: dict) -> str:
    parts = [course["title"]]
    if course.get("description"):
        parts.append(course["description"][:300])
    return " | ".join(parts)


def recommend_courses(
    thesis_title: str,
    thesis_description: str = "",
    keywords: list[str] | None = None,
    top_k: int = 5,
) -> list[dict]:
    """
    Return up to top_k course recommendations for the given thesis topic.
    Each result: {title, professor, course_number, score, explanation}
    """
    courses = _load_all_courses()
    if not courses:
        return []

    # ── Stage 1: embedding similarity ────────────────────────────────────────
    from src.matching.embedder import embed_text, embed_batch, cosine_similarity

    query = thesis_title
    if thesis_description:
        query += " " + thesis_description
    if keywords:
        query += " " + " ".join(keywords)

    student_vec = embed_text(query)
    course_texts = [_course_text(c) for c in courses]
    course_vecs  = embed_batch(course_texts)

    scored = sorted(
        zip(courses, course_vecs),
        key=lambda x: cosine_similarity(student_vec, x[1]),
        reverse=True,
    )
    candidates = [c for c, _ in scored[:min(top_k * 3, len(scored))]]

    # ── Stage 2: LLM explanation ──────────────────────────────────────────────
    from src.agents.llm_client import chat

    courses_block = "\n".join(
        f"- {c['title']} (taught by {c['professor']})"
        for c in candidates
    )

    prompt = f"""You are an academic advisor at HSG (University of St. Gallen).

A student is writing a thesis on:
Title: {thesis_title}
Description: {thesis_description or 'N/A'}
Keywords: {', '.join(keywords or [])}

Here are candidate courses available at HSG:
{courses_block}

Select the {top_k} most relevant courses for this thesis. For each, write a short 1-sentence explanation of why it is relevant.

Respond ONLY with valid JSON, no markdown:
{{
  "recommendations": [
    {{
      "title": "exact course title as listed above",
      "explanation": "one sentence why this course helps with the thesis"
    }}
  ]
}}"""

    try:
        raw = chat(
            messages=[{"role": "user", "content": prompt}],
            system="You are an expert academic advisor. Return valid JSON only.",
            max_tokens=1024,
            temperature=0.3,
        )
        # Parse JSON
        start = raw.find("{")
        end = raw.rfind("}") + 1
        data = json.loads(raw[start:end])
        recs = data.get("recommendations", [])
    except Exception:
        # Fall back to embedding order with no explanation
        recs = [{"title": c["title"], "explanation": ""} for c in candidates[:top_k]]

    # Merge with course metadata
    title_to_course = {c["title"]: c for c in courses}
    results = []
    for r in recs[:top_k]:
        course = title_to_course.get(r["title"])
        if course:
            results.append({**course, "explanation": r.get("explanation", "")})

    return results
