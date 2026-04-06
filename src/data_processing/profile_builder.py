"""
Professor profile store.

Loads professors.json → builds ProfessorProfile objects → optionally saves
them as structured profiles.json for fast access during matching.

Usage:
    from src.data_processing.profile_builder import ProfileStore

    store = ProfileStore()               # loads from data/professors.json
    store.save()                         # writes data/professor_profiles.json

    prof = store.get("Björn Ambos")      # → ProfessorProfile
    all_profs = store.all()              # → list[ProfessorProfile]
"""

import json
import os
from src.models.professor import ProfessorProfile

PROFESSORS_RAW = "data/professors.json"
PROFILES_CACHE = "data/professor_profiles.json"


class ProfileStore:
    """
    In-memory store of ProfessorProfile objects built from professors.json.
    Call save() to persist as professor_profiles.json.
    """

    def __init__(self, raw_path: str = PROFESSORS_RAW):
        self._profiles: dict[str, ProfessorProfile] = {}
        self._load(raw_path)

    def _load(self, path: str) -> None:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Raw data not found: {path}. Run main.py first.")

        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        for name, data in raw.items():
            self._profiles[name] = ProfessorProfile.from_dict(name, data)

        print(f"[ProfileStore] Loaded {len(self._profiles)} professor profiles.")

    def get(self, name: str) -> ProfessorProfile:
        """Look up a professor by full name. Raises KeyError if not found."""
        return self._profiles[name]

    def all(self) -> list:
        return list(self._profiles.values())

    def names(self) -> list[str]:
        return list(self._profiles.keys())

    def save(self, path: str = PROFILES_CACHE) -> None:
        """Persist all profiles to JSON (useful for inspection / debugging)."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {name: prof.to_dict() for name, prof in self._profiles.items()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[ProfileStore] Saved {len(self._profiles)} profiles → {path}")

    def summary(self) -> None:
        """Print a quick overview of all loaded profiles."""
        print(f"\n{'Name':<30} {'Pubs':>5} {'Courses':>8} {'Proposals':>10} {'h':>4}")
        print("-" * 60)
        for prof in self.all():
            print(
                f"{prof.name:<30} "
                f"{len(prof.publications):>5} "
                f"{len(prof.courses):>8} "
                f"{len(prof.thesis_proposals):>10} "
                f"{prof.h_index or '-':>4}"
            )
