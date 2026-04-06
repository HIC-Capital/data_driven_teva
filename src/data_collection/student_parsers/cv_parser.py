"""
Student CV parser.

Extracts structured information from a student's CV PDF:
  - Personal info (name, email, phone)
  - Education entries (degree, institution, dates, GPA/grade)
  - Work/internship experience (title, company, dates, description)
  - Skills (languages, software, other)
  - Interests / extracurriculars

The extracted data is returned as a CVData object that can be merged
into the matching pipeline alongside the grade transcript.
"""

import re
import fitz  # PyMuPDF
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class EducationEntry:
    degree: str
    institution: str
    start_date: Optional[str]
    end_date: Optional[str]
    grade: Optional[str]       # GPA, grade, or distinction (free text)
    description: Optional[str]

    def to_dict(self) -> dict:
        return {
            "degree": self.degree,
            "institution": self.institution,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "grade": self.grade,
            "description": self.description,
        }


@dataclass
class ExperienceEntry:
    title: str
    company: str
    start_date: Optional[str]
    end_date: Optional[str]
    description: Optional[str]

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "company": self.company,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "description": self.description,
        }


@dataclass
class CVData:
    # Personal
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]

    # Structured sections
    education: list[EducationEntry] = field(default_factory=list)
    experience: list[ExperienceEntry] = field(default_factory=list)

    # Flat lists
    skills: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    interests: list[str] = field(default_factory=list)

    # Raw section texts (fallback if structured parsing fails)
    raw_sections: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "education": [e.to_dict() for e in self.education],
            "experience": [e.to_dict() for e in self.experience],
            "skills": self.skills,
            "languages": self.languages,
            "interests": self.interests,
            "raw_sections": self.raw_sections,
        }

    @property
    def all_text(self) -> str:
        """Single string of all CV content for embedding."""
        parts = []
        if self.name:
            parts.append(self.name)
        for edu in self.education:
            parts.append(f"{edu.degree} {edu.institution}")
            if edu.description:
                parts.append(edu.description)
        for exp in self.experience:
            parts.append(f"{exp.title} {exp.company}")
            if exp.description:
                parts.append(exp.description)
        parts.extend(self.skills)
        parts.extend(self.interests)
        for text in self.raw_sections.values():
            parts.append(text)
        return " ".join(p for p in parts if p)


# ---------------------------------------------------------------------------
# Section detection
# ---------------------------------------------------------------------------

# Keywords that mark the start of a CV section (case-insensitive)
_SECTION_PATTERNS = {
    "education": re.compile(
        r"^\s*(education|ausbildung|études|formation|academic background|studies)\s*$",
        re.IGNORECASE
    ),
    "experience": re.compile(
        r"^\s*(experience|work experience|internships?|berufserfahrung|"
        r"professional experience|employment|career)\s*$",
        re.IGNORECASE
    ),
    "skills": re.compile(
        r"^\s*(skills|technical skills|competences?|kompetenzen|"
        r"it skills|software|tools)\s*$",
        re.IGNORECASE
    ),
    "languages": re.compile(
        r"^\s*(languages?|sprachen|langues?)\s*$",
        re.IGNORECASE
    ),
    "interests": re.compile(
        r"^\s*(interests?|hobbies|activities|extracurricular|"
        r"volunteer|engagement|interests & activities)\s*$",
        re.IGNORECASE
    ),
    "awards": re.compile(
        r"^\s*(awards?|honors?|achievements?|scholarships?|prizes?)\s*$",
        re.IGNORECASE
    ),
    "publications": re.compile(
        r"^\s*(publications?|research|papers?)\s*$",
        re.IGNORECASE
    ),
}


def _detect_section(line: str) -> Optional[str]:
    """Return section key if line is a section header, else None."""
    stripped = line.strip()
    if not stripped or len(stripped) > 60:
        return None
    for key, pattern in _SECTION_PATTERNS.items():
        if pattern.match(stripped):
            return key
    return None


# ---------------------------------------------------------------------------
# Header extraction (personal info)
# ---------------------------------------------------------------------------

def _extract_header(lines: list[str]) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract name, email, phone from the first ~10 lines of the CV."""
    name = None
    email = None
    phone = None

    email_pattern = re.compile(r"[\w.\-+]+@[\w.\-]+\.[a-zA-Z]{2,}")
    phone_pattern = re.compile(r"[\+\d][\d\s\-\(\)]{7,20}")

    # Name heuristic: first non-empty line that contains 2+ capitalized words
    for i, line in enumerate(lines[:15]):
        line = line.strip()
        if not line:
            continue
        words = line.split()
        if (
            2 <= len(words) <= 5
            and all(w[0].isupper() for w in words if w)
            and not any(c.isdigit() for c in line)
            and name is None
        ):
            name = line

        em = email_pattern.search(line)
        if em and email is None:
            email = em.group(0)

        ph = phone_pattern.search(line)
        if ph and phone is None and "@" not in line:
            phone = ph.group(0).strip()

    return name, email, phone


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------

def _split_sections(lines: list[str]) -> dict:
    """
    Walk lines, detect section headers, collect each section's raw text.
    Returns {section_key: [lines]} plus "header" for the top part.
    """
    sections = {"header": []}
    current = "header"

    for line in lines:
        sec = _detect_section(line)
        if sec:
            current = sec
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, [])
            sections[current].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


# ---------------------------------------------------------------------------
# Section-specific parsers
# ---------------------------------------------------------------------------

_DATE_RANGE = re.compile(
    r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?\d{4}"
    r"\s*[-–—]\s*"
    r"(?:((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+)?\d{4}|present|heute|ongoing)",
    re.IGNORECASE
)

_YEAR_ONLY = re.compile(r"\b(20\d{2}|19\d{2})\b")


def _extract_date_range(text: str) -> tuple[Optional[str], Optional[str]]:
    m = _DATE_RANGE.search(text)
    if m:
        raw = m.group(0)
        parts = re.split(r"\s*[-–—]\s*", raw, maxsplit=1)
        return parts[0].strip(), parts[1].strip() if len(parts) > 1 else None
    years = _YEAR_ONLY.findall(text)
    if years:
        return years[0], years[-1] if len(years) > 1 else None
    return None, None


def _parse_education(text: str) -> list[EducationEntry]:
    entries = []
    # Split on date-range lines or degree keywords
    degree_keywords = re.compile(
        r"\b(bachelor|master|msc|mba|bsc|ba|ma|phd|dr\.|diplom|licence|"
        r"exchange|program|certificate|cfa)\b",
        re.IGNORECASE
    )

    blocks = re.split(r"\n{2,}", text)
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue

        degree = ""
        institution = ""
        grade = None
        description_lines = []

        # First line often has degree or institution
        first = lines[0]
        if degree_keywords.search(first):
            degree = first
            institution = lines[1] if len(lines) > 1 else ""
        else:
            institution = first
            degree = lines[1] if len(lines) > 1 and degree_keywords.search(lines[1]) else ""

        start, end = _extract_date_range(block)

        # Look for grade/GPA
        grade_match = re.search(
            r"(gpa|grade|note|grade point|ø|average)[:\s]*([0-9.,]+(?:\s*/\s*[0-9.,]+)?)",
            block, re.IGNORECASE
        )
        if grade_match:
            grade = grade_match.group(0).strip()

        # Remaining lines = description
        desc_start = 2 if (degree and institution) else 1
        for l in lines[desc_start:]:
            if l == degree or l == institution:
                continue
            if _DATE_RANGE.search(l) or _YEAR_ONLY.search(l):
                continue
            description_lines.append(l)

        if institution or degree:
            entries.append(EducationEntry(
                degree=degree,
                institution=institution,
                start_date=start,
                end_date=end,
                grade=grade,
                description=" ".join(description_lines) or None,
            ))

    return entries


def _parse_experience(text: str) -> list[ExperienceEntry]:
    entries = []
    blocks = re.split(r"\n{2,}", text)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue

        title = lines[0]
        company = lines[1] if len(lines) > 1 else ""
        start, end = _extract_date_range(block)

        desc_lines = []
        for l in lines[2:]:
            if _DATE_RANGE.search(l) or (l == company):
                continue
            desc_lines.append(l)

        if title:
            entries.append(ExperienceEntry(
                title=title,
                company=company,
                start_date=start,
                end_date=end,
                description=" ".join(desc_lines) or None,
            ))

    return entries


def _parse_list_section(text: str) -> list[str]:
    """Parse a flat list section (skills, languages, interests) into items."""
    items = []
    for line in text.splitlines():
        line = line.strip().lstrip("-•·▪▸►◆").strip()
        if not line or len(line) < 2:
            continue
        # Split on commas or semicolons for inline lists
        for part in re.split(r"[,;]", line):
            part = part.strip()
            if part and len(part) > 1:
                items.append(part)
    return items


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_cv(pdf_path: str) -> CVData:
    """
    Parse a student CV PDF and return a CVData object.
    Works best with single-column, text-based PDFs.
    """
    doc = fitz.open(pdf_path)
    lines = []
    for page in doc:
        page_lines = page.get_text().splitlines()
        lines.extend(page_lines)
    doc.close()

    # Personal info from header
    name, email, phone = _extract_header(lines)

    # Split into sections
    sections = _split_sections(lines)

    # Parse each section
    education = _parse_education(sections.get("education", ""))
    experience = _parse_experience(sections.get("experience", ""))
    skills = _parse_list_section(sections.get("skills", ""))
    languages = _parse_list_section(sections.get("languages", ""))
    interests = _parse_list_section(sections.get("interests", ""))

    # Keep raw text for sections we didn't structured-parse
    raw = {}
    for key in ("awards", "publications"):
        if sections.get(key):
            raw[key] = sections[key]

    return CVData(
        name=name,
        email=email,
        phone=phone,
        education=education,
        experience=experience,
        skills=skills,
        languages=languages,
        interests=interests,
        raw_sections=raw,
    )
