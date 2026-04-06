"""
Thesis Proposition Agent — powered by NVIDIA NIM (llama-3.3-70b)
"""
from __future__ import annotations
import json


def generate_thesis_ideas(
    programme: str,
    research_area: str,
    interests: str,
    skills: str = "",
    level: str = "Master",
    n: int = 5,
) -> list[dict]:
    from .llm_client import chat as nim_chat

    system = (
        "You are a senior academic advisor at the University of St. Gallen (HSG), Switzerland. "
        "Propose concrete, original, and feasible thesis topics for students. "
        "Each idea must be: (1) academically rigorous, (2) feasible within 6 months, "
        "(3) specific enough to start writing a proposal tomorrow. "
        "Always respond with valid JSON only — no markdown, no prose outside JSON."
    )

    user = f"""Student profile:
- Programme: {programme}
- Level: {level}
- Research area: {research_area}
- Interests / background: {interests}
- Skills: {skills or "not specified"}

Generate exactly {n} distinct thesis topic ideas. Return a JSON array where each element has:
{{
  "title": "concise working title (10-15 words)",
  "research_question": "one precise, testable research question",
  "methodology": "2-3 sentences on the empirical or theoretical approach",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4"],
  "difficulty": "standard" | "challenging" | "ambitious",
  "why_fit": "one sentence explaining why this fits the student's background"
}}

Vary methodology (quantitative, qualitative, mixed) and sub-fields within {research_area}."""

    raw = nim_chat(messages=[{"role": "user", "content": user}], system=system, max_tokens=2000, temperature=0.7)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)
