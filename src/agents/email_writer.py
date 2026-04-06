"""
Email Writing Agent — powered by NVIDIA NIM (llama-3.3-70b)
"""
from __future__ import annotations
import json


def draft_email(
    student_first: str,
    student_last: str,
    student_programme: str,
    student_level: str,
    thesis_title: str,
    thesis_description: str,
    professor_name: str,
    professor_dept: str,
    professor_research_focus: list[str],
    professor_open_proposals: list[str] | None = None,
    match_summary: str = "",
    language: str = "English",
) -> dict:
    from .llm_client import chat as nim_chat

    focus_str = ", ".join(professor_research_focus) if professor_research_focus else "research"
    proposals_str = (
        "Open thesis proposals: " + "; ".join(professor_open_proposals)
        if professor_open_proposals else "No listed open proposals."
    )

    system = (
        "You are an expert academic writing assistant helping HSG students draft "
        "outreach emails to thesis supervisors. Your emails are professional, "
        "warm but not sycophantic, concise (150-200 words body), and always "
        "reference specific aspects of the professor's work. "
        "Respond with valid JSON only — no markdown fences."
    )

    user = f"""Draft a thesis supervision request email.

STUDENT:
- Name: {student_first} {student_last}
- Programme: {student_programme} ({student_level})
- Thesis title: {thesis_title}
- Thesis description: {thesis_description}

PROFESSOR:
- Name: {professor_name}
- Department: {professor_dept}
- Research focus: {focus_str}
- {proposals_str}
- Why matched: {match_summary or "Strong research alignment"}

REQUIREMENTS:
- Language: {language}
- Tone: professional, direct, HSG academic standard
- Length: 150-200 words body
- Must mention at least one specific aspect of the professor's research
- Must include a concrete request (office hours / short meeting)
- Do NOT start with "Dear Professor, I hope this email finds you well"

Return JSON:
{{
  "subject": "Subject line",
  "body": "Full email body including greeting and sign-off",
  "tips": ["tip1", "tip2", "tip3"]
}}"""

    raw = nim_chat(messages=[{"role": "user", "content": user}], system=system, max_tokens=800, temperature=0.5)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)
