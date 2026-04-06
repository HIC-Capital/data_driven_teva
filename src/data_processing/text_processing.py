"""
Text processing for matching.

Builds a unified "matching text" from a student profile or professor profile.
This is the single string that gets encoded into an embedding vector.

For the student, it combines:
  - thesis title + description (most important)
  - research area
  - keywords

For the professor, it combines:
  - main focuses + fields of research (most important)
  - publication titles
  - course titles + learning objectives
  - thesis proposals they've written

The idea: if both texts are about the same topic, their embeddings will be
close in vector space → high cosine similarity → good match.
"""

import re
import unicodedata
from src.models.student import StudentProfile

# Words that carry no meaning for matching — filtered out
_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "this", "that", "these", "those",
    "it", "its", "as", "up", "about", "into", "through", "during", "i",
    "we", "you", "he", "she", "they", "my", "our", "their", "how", "what",
    "which", "who", "when", "where", "why", "not", "also", "both", "each",
    "between", "such", "than", "more", "very", "can", "course", "students",
    "student", "university", "unisg", "hsg", "st", "gallen", "thesis",
    "master", "bachelor", "semester", "lecture", "seminar", "exam",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Lowercase, remove accents, strip punctuation."""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _remove_stop_words(text: str) -> str:
    words = text.split()
    return " ".join(w for w in words if w not in _STOP_WORDS and len(w) > 2)


def clean_text(text: str) -> str:
    """Normalize + remove stop words. Used for all text fields."""
    return _remove_stop_words(_normalize(text))


# ---------------------------------------------------------------------------
# Student profile → matching text
# ---------------------------------------------------------------------------

def build_student_matching_text(profile: StudentProfile, transcript=None, cv=None) -> str:
    """
    Build a single string representing the student's thesis topic.
    Fields are weighted by repetition: more important fields appear more times.

    Optional transcript (TranscriptData) and cv (CVData) objects enrich the
    profile with strong course areas, skills, and work experience.
    """
    # Fall back to documents attached to the profile
    if transcript is None:
        transcript = getattr(profile, "transcript", None)
    if cv is None:
        cv = getattr(profile, "cv", None)

    parts = []

    # Title + description — most important, repeated 2x
    parts.append(clean_text(profile.thesis_title))
    parts.append(clean_text(profile.thesis_title))
    parts.append(clean_text(profile.thesis_description))
    parts.append(clean_text(profile.thesis_description))

    # Research area
    parts.append(clean_text(profile.research_area))

    # Skills — high signal for supervisor matching
    for skill in getattr(profile, "skills", []):
        parts.append(clean_text(skill))
        parts.append(clean_text(skill))

    # About / bio
    about = getattr(profile, "about", None)
    if about:
        parts.append(clean_text(about))

    # Keywords — repeated for emphasis
    for kw in profile.keywords:
        parts.append(clean_text(kw))
        parts.append(clean_text(kw))

    # Additional notes
    if profile.additional_notes:
        parts.append(clean_text(profile.additional_notes))

    # Grade transcript — strong courses signal academic interest areas
    if transcript is not None:
        for course_name in transcript.strong_areas:
            parts.append(clean_text(course_name))
        # All graded courses once (lower weight)
        for course_name in transcript.course_names:
            parts.append(clean_text(course_name))

    # CV — skills and interests add signal
    if cv is not None:
        for skill in cv.skills:
            parts.append(clean_text(skill))
        for interest in cv.interests:
            parts.append(clean_text(interest))
        # Work experience descriptions
        for exp in cv.experience:
            if exp.description:
                parts.append(clean_text(exp.description))

    return " ".join(p for p in parts if p)


# ---------------------------------------------------------------------------
# Professor profile → matching text
# ---------------------------------------------------------------------------

def build_professor_matching_text(prof_data: dict) -> str:
    """
    Build a single string representing a professor's research profile.
    """
    parts = []

    # Main focuses + fields of research — most important, repeated 3x
    for _ in range(3):
        for field in prof_data.get("Main focuses", []):
            parts.append(clean_text(field))
        for field in prof_data.get("Fields of research", []):
            parts.append(clean_text(field))

    # OpenAlex author-level topics
    oa = prof_data.get("openalex", {})
    for topic in oa.get("topics", []):
        parts.append(clean_text(topic))

    # Publication titles (top 50 by citation — already sorted by OpenAlex)
    for pub in oa.get("publications", [])[:50]:
        title = pub.get("title") or ""
        if title:
            parts.append(clean_text(title))
        # Per-publication topics
        for topic in pub.get("topics", []):
            parts.append(clean_text(topic))

    # Course titles + learning objectives only.
    # Excluding "content", "topics_covered", "prerequisites" — those fields are
    # verbose and would flood the embedding vector, drowning out research signal.
    for course in prof_data.get("courses", []):
        parts.append(clean_text(course.get("title", "")))
        pdf = course.get("pdf_content", {})
        lo = pdf.get("learning_objectives") or ""
        if lo:
            # Cap at 300 chars to prevent a single course from dominating
            parts.append(clean_text(lo[:300]))

    # Thesis proposals the professor has written
    for proposal in prof_data.get("thesis_proposals", []):
        parts.append(clean_text(proposal.get("title", "")))
        parts.append(clean_text(proposal.get("description", "")))
        parts.append(clean_text(proposal.get("research_area", "")))

    # Career + education (lower weight, just once)
    parts.append(clean_text(prof_data.get("Professional career", "")))
    parts.append(clean_text(prof_data.get("Education", "")))

    return " ".join(p for p in parts if p)
