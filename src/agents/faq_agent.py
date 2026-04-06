"""
FAQ / Student Assistant Agent — powered by NVIDIA NIM (llama-3.3-70b)
"""
from __future__ import annotations

SYSTEM_PROMPT = """\
You are an AI thesis advisor for HSG (University of St. Gallen), embedded in \
the Thesis Match platform. Your role:

1. Answer questions about the HSG thesis process, supervision, and requirements.
2. Give personalised advice based on the student profile provided.
3. Suggest concrete next steps, not vague platitudes.
4. If a question is clearly outside your scope, politely redirect to the relevant HSG office.
5. Keep answers concise — 2-4 short paragraphs max.
6. You may use light markdown (bold, bullet lists) in your answers.

THINGS YOU KNOW:
- HSG thesis registration typically opens 3 months before the intended start.
- Supervisors must be HSG professors (Habilitation or Full Professor).
- Most theses are 60-90 pages for Master level.
- Students contact professors directly — Thesis Match helps find the right one.
- The supervision agreement (Betreuungsvereinbarung) must be signed before thesis registration.
- Topic submission: 2 weeks after registration. Thesis submission: 6 months from start (Master).
- Official registration: https://businessplatform.unisg.ch/csp?id=ww_my_thesis
"""


def chat(
    question: str,
    history: list[dict],
    student_context: str = "",
) -> str:
    from .llm_client import chat as nim_chat

    messages = []
    if not history and student_context:
        messages.append({
            "role": "user",
            "content": f"[STUDENT CONTEXT — use this to personalise answers]\n{student_context}",
        })
        messages.append({
            "role": "assistant",
            "content": "Understood. I have your profile details. How can I help you with your thesis?",
        })
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    return nim_chat(messages=messages, system=SYSTEM_PROMPT, max_tokens=600, temperature=0.6)


def draft_professor_reply(
    student_message: str,
    professor_name: str,
    professor_context: str = "",
    conversation_history: list[dict] | None = None,
) -> str:
    from .llm_client import chat as nim_chat

    context_block = f"\n\nRELEVANT PROFESSOR CONTEXT:\n{professor_context}" if professor_context else ""
    system = (
        f"You are drafting a reply on behalf of {professor_name}, an HSG professor. "
        "The reply should be professional, warm, and concise (3-6 sentences). "
        "Use academic language appropriate for professor-student communication. "
        f"Sign off as {professor_name.split()[-1]}."
        f"{context_block}"
    )

    history = conversation_history or []
    messages = history + [{"role": "user", "content": student_message}]
    return nim_chat(messages=messages, system=system, max_tokens=400, temperature=0.5)


def build_student_context(s) -> str:
    parts = []
    if getattr(s, "first_name", ""):
        parts.append(f"Name: {s.first_name} {s.last_name}")
    if getattr(s, "programme", ""):
        parts.append(f"Programme: {s.programme} ({getattr(s, 'level', '')})")
    if getattr(s, "thesis_title", ""):
        parts.append(f"Thesis title: {s.thesis_title}")
    if getattr(s, "research_area", ""):
        parts.append(f"Research area: {s.research_area}")
    if getattr(s, "research_question", ""):
        parts.append(f"Research question: {s.research_question}")
    if getattr(s, "approach", ""):
        parts.append(f"Methodology: {s.approach}")
    return "\n".join(parts) if parts else ""
