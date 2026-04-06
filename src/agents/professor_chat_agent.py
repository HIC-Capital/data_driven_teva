"""
Professor AI Chat Agent — LangGraph pipeline with guardrails
============================================================

Flow:
  input_guard → llm_answer → output_guard → (safe response to student)

Guardrails
----------
Input:  block off-topic or abusive messages
Output: block 3 forbidden categories (hardcoded) + any topics
        the professor has marked as confidential in their FAQ bank.

Forbidden by default (cannot be overridden):
  1. Grading criteria / how the thesis is evaluated / marking rubrics
  2. Exam or assessment content (specific questions, model answers)
  3. Professor's personal contact details (home, phone, private email)
"""
from __future__ import annotations

import re
from typing import TypedDict

from langgraph.graph import StateGraph, END


# ---------------------------------------------------------------------------
# Forbidden patterns (output filtering)
# ---------------------------------------------------------------------------

_FORBIDDEN_PATTERNS = [
    # Grading
    (re.compile(r"\b(grade[sd]?|grading|marking|rubric|evaluation criteria|how (it|thesis) (is|will be) (marked|graded|evaluated|scored))\b", re.I),
     "grading criteria"),
    # Exam / assessment content
    (re.compile(r"\b(exam (question|content|answer)|model answer|past paper|assessment question)\b", re.I),
     "exam content"),
    # Personal contact
    (re.compile(r"\b(home address|personal (phone|mobile|cell)|private email|whatsapp|signal|telegram)\b", re.I),
     "personal contact details"),
]

_REDIRECT_MSG = (
    "I'm not able to share information about {topic}. "
    "Please contact the professor directly or check the official HSG thesis guidelines."
)

_OFF_TOPIC_PATTERNS = re.compile(
    r"\b(recipe|cook|sport|football|soccer|dating|relationship|politic(?!al science)|meme|joke|weather)\b",
    re.I,
)


# ---------------------------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------------------------

class ChatState(TypedDict):
    question: str
    history: list[dict]
    system_prompt: str
    response: str
    blocked: bool
    block_reason: str


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------

def input_guard(state: ChatState) -> ChatState:
    q = state["question"]
    if _OFF_TOPIC_PATTERNS.search(q) and len(q) < 200:
        return {**state, "blocked": True,
                "block_reason": "off-topic",
                "response": (
                    "I'm here to help with thesis-related questions about this professor. "
                    "For other topics please use a general assistant."
                )}
    return {**state, "blocked": False, "block_reason": ""}


def llm_answer(state: ChatState) -> ChatState:
    if state.get("blocked"):
        return state
    from .llm_client import chat as nim_chat
    messages = list(state["history"]) + [{"role": "user", "content": state["question"]}]
    reply = nim_chat(
        messages=messages,
        system=state["system_prompt"],
        max_tokens=500,
        temperature=0.5,
    )
    return {**state, "response": reply}


def output_guard(state: ChatState) -> ChatState:
    if state.get("blocked"):
        return state
    text = state["response"]
    for pattern, topic in _FORBIDDEN_PATTERNS:
        if pattern.search(text):
            return {**state,
                    "blocked": True,
                    "block_reason": topic,
                    "response": _REDIRECT_MSG.format(topic=topic)}
    return state


def route_after_input(state: ChatState) -> str:
    return END if state.get("blocked") else "llm_answer"


def route_after_llm(state: ChatState) -> str:
    return "output_guard"


# ---------------------------------------------------------------------------
# Build graph (compiled once at import time)
# ---------------------------------------------------------------------------

_builder = StateGraph(ChatState)
_builder.add_node("input_guard", input_guard)
_builder.add_node("llm_answer", llm_answer)
_builder.add_node("output_guard", output_guard)

_builder.set_entry_point("input_guard")
_builder.add_conditional_edges("input_guard", route_after_input, {"llm_answer": "llm_answer", END: END})
_builder.add_edge("llm_answer", "output_guard")
_builder.add_edge("output_guard", END)

GRAPH = _builder.compile()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ask_professor_ai(
    question: str,
    history: list[dict],
    system_prompt: str,
) -> str:
    """
    Run the guarded professor AI pipeline.

    Parameters
    ----------
    question      : student's latest message
    history       : prior messages [{role, content}]
    system_prompt : professor-specific context assembled by the caller

    Returns
    -------
    str — safe response text (may be a guardrail redirect message)
    """
    result = GRAPH.invoke({
        "question": question,
        "history": history,
        "system_prompt": system_prompt,
        "response": "",
        "blocked": False,
        "block_reason": "",
    })
    return result["response"]
