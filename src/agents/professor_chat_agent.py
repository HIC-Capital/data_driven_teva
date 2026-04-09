"""
Professor AI Chat Agent — LangGraph pipeline with guardrails + suspicious activity detection
============================================================================================

Flow:
  input_guard → suspicious_check → llm_answer → output_guard → (safe response)

Guardrails
----------
Input:  block off-topic or abusive messages
        detect suspicious activity (prompt injection, social engineering, data mining)
Output: block 3 forbidden categories (hardcoded) + any topics
        the professor has marked as confidential in their FAQ bank.

Forbidden by default (cannot be overridden):
  1. Grading criteria / how the thesis is evaluated / marking rubrics
  2. Exam or assessment content (specific questions, model answers)
  3. Professor's personal contact details (home, phone, private email)

Suspicious activity (flagged but still answered safely):
  1. Prompt injection attempts ("ignore your instructions", "act as", etc.)
  2. Persona override attempts ("forget you are", "jailbreak", etc.)
  3. Social engineering ("the professor told me", "I have special permission")
  4. Restriction probing ("what are you not allowed to say?")
  5. Student data mining ("list all applicants", "who else is applying")
"""
from __future__ import annotations

import re
from datetime import datetime
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
# Suspicious activity patterns
# ---------------------------------------------------------------------------

_SUSPICIOUS_PATTERNS = [
    # Prompt injection
    (re.compile(r"\b(ignore|forget|disregard|override|bypass).{0,40}(instruction|rule|guideline|system prompt|context|restriction)\b", re.I),
     "prompt injection attempt"),
    # Persona override
    (re.compile(r"\b(act as|pretend (you are|to be)|you are now|jailbreak|DAN|developer mode|unrestricted mode)\b", re.I),
     "persona override attempt"),
    # System prompt extraction
    (re.compile(r"\b(reveal|show|print|output|repeat|dump).{0,30}(system prompt|your instructions|your context|your rules|what you (were|are) told)\b", re.I),
     "system prompt extraction attempt"),
    # Social engineering
    (re.compile(r"\b(i have (special|explicit|direct) permission|professor (said|told me|authorized|approved)|confidentially|just between us|off the record)\b", re.I),
     "social engineering attempt"),
    # Restriction probing
    (re.compile(r"\b(what (are you|can'?t|cannot) (not allowed|allowed) to (say|share|reveal|tell)|what (topics?|info|information) (is|are) (restricted|hidden|blocked)|tell me what you (won'?t|can'?t) say)\b", re.I),
     "restriction probing"),
    # Student data mining
    (re.compile(r"\b(list all (students?|applicants?)|who (else is|are) applying|other students?|how many (other )?(students?|applicants?) (are|have))\b", re.I),
     "student data mining"),
    # Role / trust escalation
    (re.compile(r"\b(i am (the professor|a (faculty|admin|staff|moderator))|on behalf of the professor|professor'?s (account|assistant))\b", re.I),
     "role escalation attempt"),
]

_SUSPICIOUS_RESPONSE = (
    "I can only help with thesis-related questions about this professor's research and supervision. "
    "For other requests, please contact the professor or HSG directly."
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
    suspicious: bool
    suspicious_reason: str


# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------

def input_guard(state: ChatState) -> ChatState:
    q = state["question"]
    if _OFF_TOPIC_PATTERNS.search(q) and len(q) < 200:
        return {**state, "blocked": True,
                "block_reason": "off-topic",
                "suspicious": False,
                "suspicious_reason": "",
                "response": (
                    "I'm here to help with thesis-related questions about this professor. "
                    "For other topics please use a general assistant."
                )}
    return {**state, "blocked": False, "block_reason": "", "suspicious": False, "suspicious_reason": ""}


def suspicious_check(state: ChatState) -> ChatState:
    """Detect suspicious / adversarial patterns and flag them without blocking the conversation."""
    if state.get("blocked"):
        return state
    q = state["question"]
    for pattern, label in _SUSPICIOUS_PATTERNS:
        if pattern.search(q):
            return {**state,
                    "suspicious": True,
                    "suspicious_reason": label,
                    "blocked": True,
                    "block_reason": label,
                    "response": _SUSPICIOUS_RESPONSE}
    return state


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
    return END if state.get("blocked") else "suspicious_check"


def route_after_suspicious(state: ChatState) -> str:
    return END if state.get("blocked") else "llm_answer"


# ---------------------------------------------------------------------------
# Build graph (compiled once at import time)
# ---------------------------------------------------------------------------

_builder = StateGraph(ChatState)
_builder.add_node("input_guard",     input_guard)
_builder.add_node("suspicious_check", suspicious_check)
_builder.add_node("llm_answer",      llm_answer)
_builder.add_node("output_guard",    output_guard)

_builder.set_entry_point("input_guard")
_builder.add_conditional_edges("input_guard",      route_after_input,     {"suspicious_check": "suspicious_check", END: END})
_builder.add_conditional_edges("suspicious_check", route_after_suspicious, {"llm_answer": "llm_answer",            END: END})
_builder.add_edge("llm_answer",   "output_guard")
_builder.add_edge("output_guard", END)

GRAPH = _builder.compile()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ask_professor_ai(
    question: str,
    history: list[dict],
    system_prompt: str,
) -> dict:
    """
    Run the guarded professor AI pipeline.

    Returns
    -------
    dict with keys:
      response  (str)  — safe response text
      suspicious (bool) — True if adversarial pattern detected
      reason    (str)  — human-readable label for the suspicious pattern
      timestamp (str)  — ISO timestamp of the interaction
    """
    result = GRAPH.invoke({
        "question":      question,
        "history":       history,
        "system_prompt": system_prompt,
        "response":      "",
        "blocked":       False,
        "block_reason":  "",
        "suspicious":    False,
        "suspicious_reason": "",
    })
    return {
        "response":   result["response"],
        "suspicious": result.get("suspicious", False),
        "reason":     result.get("suspicious_reason", ""),
        "timestamp":  datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    }
