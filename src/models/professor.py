"""
ProfessorProfile — unified, embedding-ready professor data model.

Built from the raw professors.json by calling ProfessorProfile.from_dict().
Stores everything needed for matching in one place.
"""

from dataclasses import dataclass, field
from typing import Optional

# Imported lazily at runtime to avoid circular imports — populated on first use
_RESEARCH_AREA_TO_FIELD_IDS: dict = {}


@dataclass
class Publication:
    title: str
    year: Optional[int]
    cited_by_count: int
    topics: list[str] = field(default_factory=list)
    abstract: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "year": self.year,
            "cited_by_count": self.cited_by_count,
            "topics": self.topics,
            "abstract": self.abstract,
        }

    @staticmethod
    def from_dict(d: dict) -> "Publication":
        return Publication(
            title=d.get("title", ""),
            year=d.get("year"),
            cited_by_count=d.get("cited_by_count", 0),
            topics=d.get("topics", []),
            abstract=d.get("abstract"),
        )


@dataclass
class ThesisProposal:
    title: str
    description: str
    research_area: str
    level: str              # "Bachelor", "Master", "Both" (raw string from source)
    requirements: str

    # Studyond-aligned fields
    topic_type: str = "topic"            # "topic" | "job" (studyond TopicType)
    employment: str = "no"              # "yes" | "no" | "open" (studyond TopicEmployment)
    employment_type: Optional[str] = None   # "internship" | "working_student" | "graduate_program" | "direct_entry"
    workplace_type: Optional[str] = None    # "on_site" | "hybrid" | "remote"
    degrees: list[str] = field(default_factory=list)  # ["bsc"] | ["msc"] | ["phd"] | combinations
    field_ids: list[str] = field(default_factory=list)  # references to fields.json IDs

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "research_area": self.research_area,
            "level": self.level,
            "requirements": self.requirements,
            "topic_type": self.topic_type,
            "employment": self.employment,
            "employment_type": self.employment_type,
            "workplace_type": self.workplace_type,
            "degrees": self.degrees,
            "field_ids": self.field_ids,
        }

    @staticmethod
    def from_dict(d: dict) -> "ThesisProposal":
        global _RESEARCH_AREA_TO_FIELD_IDS
        if not _RESEARCH_AREA_TO_FIELD_IDS:
            try:
                from src.data_collection.scrapers.constants import RESEARCH_AREA_TO_FIELD_IDS
                _RESEARCH_AREA_TO_FIELD_IDS = RESEARCH_AREA_TO_FIELD_IDS
            except ImportError:
                pass

        # Derive degrees list from level string if not explicitly stored
        level = d.get("level", "")
        degrees = d.get("degrees") or _level_to_degrees(level)

        # Derive field_ids from research_area if not explicitly stored
        research_area = d.get("research_area", "")
        field_ids = d.get("field_ids") or _RESEARCH_AREA_TO_FIELD_IDS.get(research_area, [])

        return ThesisProposal(
            title=d.get("title", ""),
            description=d.get("description", ""),
            research_area=research_area,
            level=level,
            requirements=d.get("requirements", ""),
            topic_type=d.get("topic_type", "topic"),
            employment=d.get("employment", "no"),
            employment_type=d.get("employment_type"),
            workplace_type=d.get("workplace_type"),
            degrees=degrees,
            field_ids=field_ids,
        )


def _level_to_degrees(level: str) -> list[str]:
    """Convert a level string like 'Bachelor & Master' to Studyond degrees list."""
    level_lower = level.lower()
    degrees = []
    if "bachelor" in level_lower:
        degrees.append("bsc")
    if "master" in level_lower:
        degrees.append("msc")
    if "phd" in level_lower or "doctorate" in level_lower or "doctoral" in level_lower:
        degrees.append("phd")
    return degrees or ["msc"]  # default to msc if unclear


@dataclass
class Course:
    title: str
    url: Optional[str] = None
    pdf_path: Optional[str] = None
    # Extracted from PDF fact sheet
    learning_objectives: Optional[str] = None
    content: Optional[str] = None
    topics_covered: Optional[str] = None
    prerequisites: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "pdf_path": self.pdf_path,
            "learning_objectives": self.learning_objectives,
            "content": self.content,
            "topics_covered": self.topics_covered,
            "prerequisites": self.prerequisites,
        }

    @staticmethod
    def from_dict(d: dict) -> "Course":
        pdf = d.get("pdf_content") or {}
        return Course(
            title=d.get("title", ""),
            url=d.get("url"),
            pdf_path=d.get("pdf_path"),
            learning_objectives=pdf.get("learning_objectives"),
            content=pdf.get("content"),
            topics_covered=pdf.get("topics_covered"),
            prerequisites=pdf.get("prerequisites"),
        )


# Studyond-aligned supervisor objective types
SUPERVISOR_OBJECTIVES = [
    "student_matching",        # wants to find suitable thesis students
    "research_collaboration",  # interested in joint research with other supervisors/companies
    "network_expansion",       # wants to connect with industry and other academics
    "funding_access",          # looking for funded project opportunities
    "project_management",      # focused on managing ongoing thesis projects
]


@dataclass
class ProfessorProfile:
    # Identity
    name: str
    first_name: str
    last_name: str
    email: Optional[str]
    title: Optional[str]
    profile_url: Optional[str]

    # Research profile
    main_focuses: list[str] = field(default_factory=list)
    fields_of_research: list[str] = field(default_factory=list)
    openalex_id: Optional[str] = None
    h_index: Optional[int] = None
    works_count: Optional[int] = None
    openalex_topics: list[str] = field(default_factory=list)

    # Studyond-aligned fields
    objectives: list[str] = field(default_factory=list)   # from SUPERVISOR_OBJECTIVES
    field_ids: list[str] = field(default_factory=list)    # references to fields.json IDs

    # Content
    publications: list[Publication] = field(default_factory=list)
    courses: list[Course] = field(default_factory=list)
    thesis_proposals: list[ThesisProposal] = field(default_factory=list)

    # Background text
    professional_career: str = ""
    education: str = ""
    additional_info: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "title": self.title,
            "profile_url": self.profile_url,
            "main_focuses": self.main_focuses,
            "fields_of_research": self.fields_of_research,
            "openalex_id": self.openalex_id,
            "h_index": self.h_index,
            "works_count": self.works_count,
            "openalex_topics": self.openalex_topics,
            "objectives": self.objectives,
            "field_ids": self.field_ids,
            "publications": [p.to_dict() for p in self.publications],
            "courses": [c.to_dict() for c in self.courses],
            "thesis_proposals": [t.to_dict() for t in self.thesis_proposals],
            "professional_career": self.professional_career,
            "education": self.education,
            "additional_info": self.additional_info,
        }

    @staticmethod
    def from_dict(name: str, d: dict) -> "ProfessorProfile":
        """Build a ProfessorProfile from a raw professors.json entry."""
        oa = d.get("openalex") or {}

        publications = [
            Publication.from_dict(p)
            for p in oa.get("publications", [])
        ]
        courses = [Course.from_dict(c) for c in d.get("courses", [])]
        proposals = [
            ThesisProposal.from_dict(t)
            for t in d.get("thesis_proposals", [])
        ]

        return ProfessorProfile(
            name=name,
            first_name=d.get("First Name", ""),
            last_name=d.get("Last Name", ""),
            email=d.get("Email"),
            title=d.get("Title"),
            profile_url=d.get("profile_url"),
            main_focuses=d.get("Main focuses", []),
            fields_of_research=d.get("Fields of research", []),
            openalex_id=oa.get("openalex_id"),
            h_index=oa.get("h_index"),
            works_count=oa.get("works_count"),
            openalex_topics=oa.get("topics", []),
            objectives=d.get("objectives", []),
            field_ids=d.get("field_ids", []),
            publications=publications,
            courses=courses,
            thesis_proposals=proposals,
            professional_career=d.get("Professional career", ""),
            education=d.get("Education", ""),
            additional_info=d.get("Additional info", ""),
        )

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def top_publications(self) -> list[Publication]:
        """Top 50 publications by citation count."""
        return sorted(self.publications, key=lambda p: p.cited_by_count, reverse=True)[:50]

    @property
    def has_thesis_proposals(self) -> bool:
        return len(self.thesis_proposals) > 0

    def __repr__(self) -> str:
        return (
            f"ProfessorProfile({self.name!r}, "
            f"pubs={len(self.publications)}, "
            f"courses={len(self.courses)}, "
            f"proposals={len(self.thesis_proposals)})"
        )
