"""
PDF text extractor for HSG course fact sheets.

Extracts key sections from the structured PDF format:
  - course_number, course_title, ects, semester
  - prerequisites
  - learning_objectives
  - topics_covered
  - content
  - literature
  - full_text  (entire PDF text, for embedding if needed)
"""

import re
import fitz  # PyMuPDF
from typing import Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


_KNOWN_SECTIONS = [
    "Prerequisites", "Voraussetzungen",
    "Learning objectives", "Learning goals", "Lernziele", "Objectives",
    "Structure and indications", "Struktur",
    "Topics covered",
    "Content", "Inhalt",
    "Literature", "Literatur",
    "Examination", "Assessment",
    "Attached courses", "Overview examination",
    "Course information", "Timetable",
]


def _section_fence() -> str:
    return "|".join(re.escape(s) for s in _KNOWN_SECTIONS)


def _extract_section(text: str, *headings: str) -> Optional[str]:
    """Extract text block after any of headings, up to next known section."""
    heading_pattern = "|".join(re.escape(h) for h in headings)
    match = re.search(
        rf"(?:^|\n)\s*(?:{heading_pattern})\s*\n(.*?)(?=\n\s*(?:{_section_fence()})|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if match:
        return _clean(match.group(1))
    return None


# ---------------------------------------------------------------------------
# Main extractor
# ---------------------------------------------------------------------------

def extract_course_pdf(pdf_path: str) -> dict:
    """
    Extract structured data from an HSG course fact sheet PDF.
    Returns a dict with all extracted fields.
    """
    doc = fitz.open(pdf_path)
    full_text = "\n".join(page.get_text() for page in doc)
    doc.close()

    result = {"full_text": _clean(full_text)}

    # Course number and title: "10,281: Empirical Corporate Finance"
    m = re.search(r"(\d[\d,]+):\s*(.+?)\n", full_text)
    if m:
        result["course_number"] = m.group(1).strip()
        result["course_title"] = m.group(2).strip()

    # ECTS
    m = re.search(r"ECTS credits?:\s*([\d.]+)", full_text, re.IGNORECASE)
    if m:
        result["ects"] = m.group(1)

    # Semester
    m = re.search(r"(Spring|Autumn|Fall)\s+Semester\s+(\d{4})", full_text, re.IGNORECASE)
    if m:
        result["semester"] = m.group(0)

    # Lecturer
    m = re.search(r"--\s*(?:English|German|French)\s*--\s*(.+?)(?:\n|$)", full_text)
    if m:
        result["lecturer"] = m.group(1).strip()

    # Prerequisites
    val = _extract_section(full_text, "Prerequisites", "Voraussetzungen")
    if val:
        result["prerequisites"] = val

    # Learning objectives
    val = _extract_section(full_text, "Learning objectives", "Learning goals", "Lernziele", "Objectives")
    if val:
        result["learning_objectives"] = val

    # Topics covered
    m = re.search(
        r"[Tt]opics covered[^:]*:?\s*\n?(.*?)(?=\n\s*(?:Assessment|Examination|Content|Literature)|$)",
        full_text, re.DOTALL,
    )
    if m:
        result["topics_covered"] = _clean(m.group(1))

    # Content
    val = _extract_section(full_text, "Content", "Inhalt")
    if val:
        result["content"] = val

    # Literature
    val = _extract_section(full_text, "Literature", "Literatur")
    if val:
        result["literature"] = val

    return result


# ---------------------------------------------------------------------------
# Batch helper
# ---------------------------------------------------------------------------

def extract_courses_for_professor(courses: list[dict]) -> list[dict]:
    """
    For each course dict that has a pdf_path, extract text and store it
    under 'pdf_content'. Returns the updated list.
    """
    for course in courses:
        pdf_path = course.get("pdf_path")
        if not pdf_path:
            continue
        try:
            course["pdf_content"] = extract_course_pdf(pdf_path)
        except Exception as e:
            course["pdf_content"] = {"error": str(e)}
    return courses
