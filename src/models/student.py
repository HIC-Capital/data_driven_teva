from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.data_collection.student_parsers.transcript_parser import TranscriptData
    from src.data_collection.student_parsers.cv_parser import CVData

# Studyond-aligned objective types
STUDENT_OBJECTIVES = [
    "topic",             # looking for a thesis topic
    "supervision",       # looking for a supervisor
    "career_start",      # interested in job/internship through thesis
    "industry_access",   # wants industry collaboration / company partner
    "project_guidance",  # needs help structuring / managing their project
]


@dataclass
class StudentProfile:
    # Identity
    first_name: str
    last_name: str
    email: str

    # Thesis info
    level: str                    # "Bachelor" | "Master"
    programme: str                # full programme name from HSG_BACHELOR_PROGRAMMES / HSG_MASTER_PROGRAMMES
    research_area: str            # from RESEARCH_AREAS list
    thesis_title: str             # working title or idea
    thesis_description: str       # free-text description of the topic

    # Studyond-aligned fields
    skills: list[str] = field(default_factory=list)       # specific competencies (e.g. "Python", "econometrics")
    about: Optional[str] = None                            # LinkedIn-style bio (~2-3 sentences)
    objectives: list[str] = field(default_factory=list)   # from STUDENT_OBJECTIVES
    field_ids: list[str] = field(default_factory=list)    # references to fields.json IDs

    # Optional questionnaire fields
    keywords: list[str] = field(default_factory=list)     # student-provided free-text keywords
    language: str = "English"                             # preferred thesis language
    additional_notes: str = ""                            # any other context

    # Parsed documents (attached after questionnaire, not serialized to JSON)
    transcript: Optional[object] = field(default=None, repr=False)  # TranscriptData
    cv: Optional[object] = field(default=None, repr=False)          # CVData

    def to_dict(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "level": self.level,
            "programme": self.programme,
            "research_area": self.research_area,
            "thesis_title": self.thesis_title,
            "thesis_description": self.thesis_description,
            "skills": self.skills,
            "about": self.about,
            "objectives": self.objectives,
            "field_ids": self.field_ids,
            "keywords": self.keywords,
            "language": self.language,
            "additional_notes": self.additional_notes,
            "has_transcript": self.transcript is not None,
            "has_cv": self.cv is not None,
        }
