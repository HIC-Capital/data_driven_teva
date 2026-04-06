"""
HSG Grade Transcript parser.

Handles both languages:
  - German: "Notenauszug", note scale 1.0–6.0
  - English: "Grade Transcript", same scale

Extracts:
  - student name, ID, program, date
  - overall GPA and total credits earned
  - individual courses: name, language, credits, grade
  - section-level summaries (Fachstudium, Kontextstudium, etc.)
"""

import re
import fitz  # PyMuPDF
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CourseEntry:
    name: str
    language: Optional[str]   # "EN", "DE", or None
    credits: Optional[float]
    grade: Optional[float]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "language": self.language,
            "credits": self.credits,
            "grade": self.grade,
        }


@dataclass
class TranscriptData:
    # Header
    student_name: str
    student_id: str
    program: str
    date: str
    language: str             # "DE" or "EN"

    # Summary
    gpa: Optional[float]
    credits_earned: Optional[float]
    credits_required: Optional[float]

    # Courses
    courses: list[CourseEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "student_name": self.student_name,
            "student_id": self.student_id,
            "program": self.program,
            "date": self.date,
            "language": self.language,
            "gpa": self.gpa,
            "credits_earned": self.credits_earned,
            "credits_required": self.credits_required,
            "courses": [c.to_dict() for c in self.courses],
        }

    @property
    def graded_courses(self) -> list[CourseEntry]:
        """Only courses that have an actual grade (not just section headers)."""
        return [c for c in self.courses if c.grade is not None]

    @property
    def course_names(self) -> list[str]:
        return [c.name for c in self.graded_courses]

    @property
    def strong_areas(self) -> list[str]:
        """Course names where grade >= 5.5 (very good or excellent)."""
        return [c.name for c in self.graded_courses if c.grade and c.grade >= 5.5]


# ---------------------------------------------------------------------------
# Section headers to skip (not individual courses)
# ---------------------------------------------------------------------------

_SECTION_HEADERS = {
    # German
    "fachstudium", "pflichtbereich", "pflichtwahl- und wahlbereich",
    "pflichtwahlbereich", "wahlbereich", "kontextstudium", "fokusbereiche",
    "skills und sprachen", "skills", "sprachen", "bachelor-arbeit",
    "leistungen ohne credits",
    # English
    "core studies", "compulsory subjects", "core electives and electives",
    "core electives", "electives", "contextual studies", "area of concentration",
    "skills and languages", "languages", "bachelor's thesis",
    "work without credits",
}

def _is_section_header(name: str) -> bool:
    return name.lower().strip() in _SECTION_HEADERS


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_transcript(pdf_path: str) -> TranscriptData:
    """
    Parse an HSG grade transcript PDF (German or English).
    Returns a TranscriptData object.
    """
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()

    # Detect language
    lang = "EN" if "Grade Transcript" in text or "Bachelor of Arts in Economics" in text else "DE"

    # --- Header ---
    # Name and ID: "Lassoeur, Timo, 24609067"
    name_match = re.search(r"([A-ZÄÖÜa-zäöü\-]+,\s+[A-ZÄÖÜa-zäöü\-]+),\s+(\d{7,8})", text)
    student_name = name_match.group(1).strip() if name_match else ""
    student_id = name_match.group(2).strip() if name_match else ""

    # Program
    program_pattern = (
        r"(Bachelor of Arts in [^\n]+|Master of [^\n]+|"
        r"Bachelor of Science[^\n]+|"
        r"Volkswirtschaftslehre[^\n]*|Betriebswirtschaft[^\n]*)"
    )
    prog_match = re.search(program_pattern, text)
    program = prog_match.group(1).strip() if prog_match else ""

    # Date
    date_match = re.search(r"(\d{2}\.\d{2}\.\d{4})", text)
    date = date_match.group(1) if date_match else ""

    # --- Overall summary ---
    # Line with total credits and GPA:
    # "120.00 120.00 32.00 5.20"
    summary_match = re.search(
        r"(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d\.\d+)",
        text
    )
    gpa = float(summary_match.group(4)) if summary_match else None
    credits_required = float(summary_match.group(1)) if summary_match else None
    credits_earned = float(summary_match.group(3)) if summary_match else None

    # --- Individual courses ---
    courses = _extract_courses(text)

    return TranscriptData(
        student_name=student_name,
        student_id=student_id,
        program=program,
        date=date,
        language=lang,
        gpa=gpa,
        credits_earned=credits_earned,
        credits_required=credits_required,
        courses=courses,
    )


def _extract_courses(text: str) -> list[CourseEntry]:
    """
    Extract individual course rows from the transcript text.

    HSG transcript line formats:
      "Course Name  EN  4.00  5.50"       (with language code, with grade)
      "Course Name  6.00  6.00"           (no language code, with grade)
      "Course Name  6.00  6.00  4.00"     (with min/max credits + earned)
      "Section Header  52.00  52.00  28.00"  (section — skip)
    """
    courses = []

    # Grade is always a float between 1.0 and 6.0 (one decimal)
    # Credits are floats ending in .00 or .25 etc.
    # Language codes: EN, DE, FR (2 uppercase letters)

    grade_pattern = re.compile(
        r"^(.+?)"                          # course name (greedy up to first number)
        r"\s+(EN|DE|FR)?"                  # optional language code
        r"\s*(\d+\.\d+)?"                  # optional min credits
        r"\s+(\d+\.\d+)"                   # credits or max credits
        r"\s+([1-6]\.\d{2})\s*$",          # grade (1.00–6.00)
        re.MULTILINE
    )

    seen = set()
    for m in grade_pattern.finditer(text):
        name = m.group(1).strip()

        # Skip section headers and duplicates
        if _is_section_header(name) or name in seen:
            continue
        # Skip very short or obviously non-course lines
        if len(name) < 4:
            continue

        seen.add(name)
        lang = m.group(2)
        credits = float(m.group(4))
        grade = float(m.group(5))

        courses.append(CourseEntry(
            name=name,
            language=lang,
            credits=credits,
            grade=grade,
        ))

    return courses
