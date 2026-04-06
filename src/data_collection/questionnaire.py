"""
Student input questionnaire — terminal interface.

Collects thesis information from a student via prompted questions.
Inspired by the application form used by Prof. Michèle Müller-Itten (HSG).
Returns a StudentProfile object ready for matching.
"""

import os

from src.data_collection.scrapers.constants import (
    RESEARCH_AREAS,
    RESEARCH_AREA_TO_FIELD_IDS,
    HSG_BACHELOR_PROGRAMMES,
    HSG_MASTER_PROGRAMMES,
)
from src.models.student import StudentProfile, STUDENT_OBJECTIVES


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def _ask(prompt: str, required: bool = True) -> str:
    while True:
        answer = input(f"\n{prompt}\n> ").strip()
        if answer or not required:
            return answer
        print("  This field is required.")


def _ask_choice(prompt: str, choices: list, required: bool = True) -> str:
    """Display a numbered list and return the chosen value."""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        print(f"  {i:2}. {choice}")

    while True:
        raw = input("> ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(choices):
            return choices[int(raw) - 1]
        matches = [c for c in choices if raw.lower() in c.lower()]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            print(f"  Ambiguous — did you mean: {', '.join(matches)}?")
        elif not required and raw == "":
            return ""
        else:
            print("  Please enter a number or type the option name.")


def _ask_keywords(prompt: str) -> list:
    """Ask for comma-separated keywords, return as a list."""
    raw = input(f"\n{prompt}\n> ").strip()
    if not raw:
        return []
    return [kw.strip() for kw in raw.split(",") if kw.strip()]


def _ask_multi_choice(prompt: str, choices: list) -> list:
    """Display a numbered list and return the chosen values (comma-separated numbers)."""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        print(f"  {i:2}. {choice}")
    print("  Enter numbers separated by commas (e.g. 1,3):")
    while True:
        raw = input("> ").strip()
        if not raw:
            return []
        parts = [p.strip() for p in raw.split(",")]
        selected = []
        valid = True
        for p in parts:
            if p.isdigit() and 1 <= int(p) <= len(choices):
                selected.append(choices[int(p) - 1])
            else:
                print(f"  Invalid choice: {p!r}. Enter numbers between 1 and {len(choices)}.")
                valid = False
                break
        if valid:
            return selected


# ---------------------------------------------------------------------------
# Questionnaire
# ---------------------------------------------------------------------------

def run_questionnaire() -> StudentProfile:
    print("\n" + "=" * 60)
    print("  HSG Thesis Supervisor Matching — Student Application")
    print("=" * 60)
    print("Please answer the following questions about your thesis.")
    print("None of the information below is binding.")
    print("It helps us identify the best supervisor for your project.\n")

    # --- Identity ---
    first_name = _ask("1. Your first name:")
    last_name = _ask("2. Your last name:")
    email = _ask("3. Your HSG email address:")

    # --- Programme & level ---
    level = _ask_choice(
        "4. Are you writing a Bachelor's or Master's thesis?",
        ["Bachelor", "Master"],
    )

    programme_list = HSG_BACHELOR_PROGRAMMES if level == "Bachelor" else HSG_MASTER_PROGRAMMES
    programme = _ask_choice(
        "5. Which programme are you enrolled in?",
        programme_list,
    )

    semester = _ask(
        "6. Current semester (e.g. 5th semester Bachelor, 1st semester Master):"
    )

    # --- Thesis planning ---
    start_date = _ask(
        "7. Planned start date of your thesis (e.g. September 2025):"
    )
    end_date = _ask(
        "8. Planned submission date (e.g. February 2026):"
    )

    # --- Research area ---
    research_area = _ask_choice(
        "9. Which research area best describes your thesis?\n"
        "   (Enter the number or type a keyword)",
        RESEARCH_AREAS,
    )

    # --- Thesis content (Michele Itten-style questions) ---
    thesis_title = _ask(
        "10. Working title or topic of your thesis:"
    )

    research_question = _ask(
        "11. What is/are your research question(s)?\n"
        "    (What specific question do you want to answer?)"
    )

    motivation = _ask(
        "12. What is your main motivation for this research project?\n"
        "    (Why does this topic matter to you?)"
    )

    approach = _ask(
        "13. Do you plan to answer your question using theory, experiments,\n"
        "    or empirical analysis of existing data?\n"
        "    Briefly describe your planned approach and suggested methods:"
    )

    relevant_courses = _ask(
        "14. What courses have you taken that prepare you for this research?\n"
        "    (e.g. Econometrics, Corporate Finance, Game Theory)"
    )

    references = _ask(
        "15. What sources or references on the topic have you already consulted?\n"
        "    (Lecture materials, newspaper articles, academic papers — brief list)",
        required=False,
    )

    data_strategy = _ask(
        "16. Data procurement strategy (if applicable):\n"
        "    (Where will your data come from? How will you access it?)",
        required=False,
    )

    # Build thesis_description from structured answers
    thesis_description = _build_description(
        research_question=research_question,
        motivation=motivation,
        approach=approach,
        relevant_courses=relevant_courses,
        references=references,
        data_strategy=data_strategy,
    )

    # --- Skills ---
    skills = _ask_keywords(
        "17. List your key skills (comma-separated):\n"
        "    e.g. Python, econometrics, R, qualitative research, financial modelling"
    )

    # --- Keywords ---
    keywords = _ask_keywords(
        "18. List 3–5 keywords that describe your topic (comma-separated):\n"
        "    e.g. corporate governance, board diversity, firm performance"
    )

    # --- Objectives (Studyond-aligned) ---
    _objective_labels = {
        "topic":            "I am looking for a thesis topic",
        "supervision":      "I am looking for a supervisor",
        "career_start":     "I hope this thesis leads to a job/internship",
        "industry_access":  "I want a company as a collaboration partner",
        "project_guidance": "I need help structuring / managing my project",
    }
    objectives = _ask_multi_choice(
        "19. What are your main objectives? (select all that apply)",
        list(_objective_labels.values()),
    )
    # Map labels back to objective keys
    _label_to_key = {v: k for k, v in _objective_labels.items()}
    objectives = [_label_to_key[o] for o in objectives]

    # --- About / Bio ---
    about = _ask(
        "20. Write a short bio (2–3 sentences) describing your background and thesis goals:\n"
        "    (This will be shown to potential supervisors — optional, press Enter to skip)",
        required=False,
    ) or None

    # --- Language & notes ---
    language = _ask_choice(
        "21. Preferred language for your thesis:",
        ["English", "German", "French"],
    )

    additional_notes = _ask(
        "22. Anything else the supervisor should know? (optional — press Enter to skip)",
        required=False,
    )

    # Derive field_ids from the chosen research_area
    field_ids = RESEARCH_AREA_TO_FIELD_IDS.get(research_area, [])

    profile = StudentProfile(
        first_name=first_name,
        last_name=last_name,
        email=email,
        level=level,
        programme=programme,
        research_area=research_area,
        thesis_title=thesis_title,
        thesis_description=thesis_description,
        skills=skills,
        about=about,
        objectives=objectives,
        field_ids=field_ids,
        keywords=keywords,
        language=language,
        additional_notes=additional_notes,
    )

    # Store extra fields not on the dataclass directly
    profile._semester = semester
    profile._start_date = start_date
    profile._end_date = end_date

    # --- Optional document uploads ---
    transcript_path = _ask(
        "23. Path to your grade transcript PDF (optional — press Enter to skip):",
        required=False,
    )
    if transcript_path:
        transcript_path = transcript_path.strip().strip('"').strip("'")
        if os.path.exists(transcript_path):
            try:
                from src.data_collection.student_parsers.transcript_parser import parse_transcript
                profile.transcript = parse_transcript(transcript_path)
                print(f"  Transcript loaded: {len(profile.transcript.courses)} courses, GPA {profile.transcript.gpa}")
            except Exception as exc:
                print(f"  Warning: could not parse transcript — {exc}")
        else:
            print(f"  Warning: file not found: {transcript_path}")

    cv_path = _ask(
        "24. Path to your CV PDF (optional — press Enter to skip):",
        required=False,
    )
    if cv_path:
        cv_path = cv_path.strip().strip('"').strip("'")
        if os.path.exists(cv_path):
            try:
                from src.data_collection.student_parsers.cv_parser import parse_cv
                profile.cv = parse_cv(cv_path)
                print(f"  CV loaded: {len(profile.cv.education)} education entries, "
                      f"{len(profile.cv.experience)} experience entries")
            except Exception as exc:
                print(f"  Warning: could not parse CV — {exc}")
        else:
            print(f"  Warning: file not found: {cv_path}")

    print("\n" + "=" * 60)
    print("  Profile saved. Running matching...")
    print("=" * 60)

    return profile


def _build_description(
    research_question: str,
    motivation: str,
    approach: str,
    relevant_courses: str,
    references: str,
    data_strategy: str,
) -> str:
    """
    Combine the structured Michele Itten-style answers into a single
    thesis_description string used for embedding.
    """
    parts = []
    if research_question:
        parts.append(f"Research question: {research_question}")
    if motivation:
        parts.append(f"Motivation: {motivation}")
    if approach:
        parts.append(f"Approach and methods: {approach}")
    if relevant_courses:
        parts.append(f"Relevant courses: {relevant_courses}")
    if references:
        parts.append(f"References consulted: {references}")
    if data_strategy:
        parts.append(f"Data strategy: {data_strategy}")
    return " | ".join(parts)
