"""
Professor Document Import Agent — powered by NVIDIA NIM (llama-3.3-70b)
"""
from __future__ import annotations
import json


def extract_text_from_file(uploaded_file) -> str:
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        try:
            import pdfplumber, io
            with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages).strip()
        except ImportError:
            uploaded_file.seek(0)
            return uploaded_file.read().decode("utf-8", errors="ignore")
    elif filename.endswith(".docx"):
        try:
            import docx, io
            doc = docx.Document(io.BytesIO(uploaded_file.read()))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            uploaded_file.seek(0)
            return uploaded_file.read().decode("utf-8", errors="ignore")
    else:
        uploaded_file.seek(0)
        return uploaded_file.read().decode("utf-8", errors="ignore")


def import_professor_document(
    raw_text: str,
    professor_name: str,
    document_name: str,
) -> dict:
    from .llm_client import chat as nim_chat

    system = (
        "You are an academic data extraction assistant for HSG (University of St. Gallen). "
        "Extract structured information from professor documents to help students find supervisors. "
        "Be precise, extract only what is actually in the document. "
        "Respond with valid JSON only — no markdown fences, no prose outside JSON."
    )

    user = f"""Professor: {professor_name}
Document: {document_name}

CONTENT:
---
{raw_text[:8000]}
---

Return this JSON:
{{
  "document_type": "thesis_proposals" | "course_material" | "faq" | "requirements" | "research_overview" | "other",
  "thesis_proposals": [{{"title":"","description":"","level":"Bachelor|Master|Bachelor & Master","methodology":"","requirements":""}}],
  "faq_entries": [{{"question":"","answer":""}}],
  "requirements": ["..."],
  "key_topics": ["..."],
  "courses": ["..."],
  "summary": "1-2 sentence summary",
  "raw_insights": "other useful info for matching"
}}

Generate 2-4 FAQ entries students would commonly ask based on this document."""

    raw = nim_chat(messages=[{"role": "user", "content": user}], system=system, max_tokens=2000, temperature=0.3)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    result = json.loads(raw)
    result["professor_name"] = professor_name
    result["document_name"] = document_name
    return result
