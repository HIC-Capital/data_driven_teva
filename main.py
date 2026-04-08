"""
Data collection pipeline. Each step is cached — re-running skips already
completed steps unless you pass --force or delete the cache file.

Usage:
  python main.py              # run all missing steps
  python main.py --force      # re-run everything
  python main.py --step 4     # run only step 4
"""

import argparse
import json
import os

PROFESSORS_CACHE = "data/professors.json"
THESIS_CACHE = "data/thesis_topics.json"

os.makedirs("data", exist_ok=True)


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------


def _load_cache(path: str):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def _save(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Parse args
# ---------------------------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument("--force", action="store_true", help="Re-run all steps")
parser.add_argument("--step", type=int, help="Run only this step (1-6)")
args = parser.parse_args()

run_all = args.step is None
force = args.force


def should_run(step: int) -> bool:
    if args.step is not None:
        return args.step == step
    return True


# ---------------------------------------------------------------------------
# Step 1: Alexandria
# ---------------------------------------------------------------------------

if should_run(1):
    cached = _load_cache(PROFESSORS_CACHE)
    if cached and not force:
        professors = cached
        print(f"[step 1] Loaded {len(professors)} professors from cache.")
    else:
        from src.data_collection.scrapers.alexandria_scrapper import scrape_all_professors
        print("=" * 50)
        print("STEP 1 — Alexandria")
        print("=" * 50)
        # Preserve existing enrichment data (openalex, courses, etc.) when re-running step 1
        existing = _load_cache(PROFESSORS_CACHE) or {}
        fresh = scrape_all_professors()
        for name, data in fresh.items():
            if name in existing:
                # Merge: keep enriched fields, update Alexandria fields
                merged = existing[name].copy()
                merged.update(data)
                fresh[name] = merged
        professors = fresh
        _save(PROFESSORS_CACHE, professors)
else:
    professors = _load_cache(PROFESSORS_CACHE) or {}


# ---------------------------------------------------------------------------
# Step 2: OpenAlex
# ---------------------------------------------------------------------------

if should_run(2):
    needs_openalex = [n for n, d in professors.items() if "openalex" not in d]
    if not needs_openalex and not force:
        print(f"[step 2] OpenAlex already complete for all professors.")
    else:
        from src.data_collection.scrapers.openalex_scraper import scrape_professor_publications
        print("=" * 50)
        print("STEP 2 — OpenAlex")
        print("=" * 50)
        targets = list(professors.keys()) if force else needs_openalex
        for name in targets:
            data = professors[name]
            result = scrape_professor_publications(name, email=data.get("Email"))
            if result:
                professors[name]["openalex"] = result
        _save(PROFESSORS_CACHE, professors)


# ---------------------------------------------------------------------------
# Step 3: Compass
# ---------------------------------------------------------------------------

if should_run(3):
    needs_courses = [n for n, d in professors.items() if "courses" not in d]
    if not needs_courses and not force:
        print(f"[step 3] Compass already complete for all professors.")
    else:
        from src.data_collection.scrapers.compass_scraper import scrape_professor_courses
        print("=" * 50)
        print("STEP 3 — Compass")
        print("=" * 50)
        targets = list(professors.keys()) if force else needs_courses
        MAX_COURSES = 50
        total_courses = sum(len(d.get("courses", [])) for d in professors.values())
        for name in targets:
            if total_courses >= MAX_COURSES:
                print(f"[step 3] Reached {MAX_COURSES} courses limit — stopping.")
                break
            result = scrape_professor_courses(name, num_semesters=2)
            if result:
                professors[name]["courses"] = result["courses"]
                total_courses += len(result["courses"])
                _save(PROFESSORS_CACHE, professors)  # save after each professor
        _save(PROFESSORS_CACHE, professors)


# ---------------------------------------------------------------------------
# Step 4: BusinessPlatform thesis topics
# ---------------------------------------------------------------------------

if should_run(4):
    cached_theses = _load_cache(THESIS_CACHE)
    if cached_theses and not force:
        print(f"[step 4] Loaded {len(cached_theses)} thesis topics from cache.")
        thesis_topics = cached_theses
    else:
        from src.data_collection.scrapers.business_platform_scraper import scrape_all_thesis_topics
        print("=" * 50)
        print("STEP 4 — BusinessPlatform Thesis Topics")
        print("=" * 50)
        thesis_topics = scrape_all_thesis_topics(output_path=THESIS_CACHE)

    from src.data_collection.scrapers.business_platform_scraper import match_theses_to_professors
    grouped = match_theses_to_professors(thesis_topics, professors)
    for name in professors:
        if grouped.get(name):
            professors[name]["thesis_proposals"] = grouped[name]
    _save(PROFESSORS_CACHE, professors)


# ---------------------------------------------------------------------------
# Step 5: PDF text extraction from course fact sheets
# ---------------------------------------------------------------------------

if should_run(5):
    needs_pdf = [
        n for n, d in professors.items()
        if any(c.get("pdf_path") and "pdf_content" not in c for c in d.get("courses", []))
    ]
    if not needs_pdf and not force:
        print("[step 5] PDF extraction already complete.")
    else:
        from src.data_collection.course_pdf_parser import extract_courses_for_professor
        print("=" * 50)
        print("STEP 5 — Course PDF extraction")
        print("=" * 50)
        targets = list(professors.keys()) if force else needs_pdf
        for name in targets:
            courses = professors[name].get("courses", [])
            if courses:
                professors[name]["courses"] = extract_courses_for_professor(courses)
                n_ok = sum(1 for c in courses if c.get("pdf_content") and "error" not in c.get("pdf_content", {}))
                print(f"  {name}: {n_ok}/{len(courses)} PDFs extracted")
        _save(PROFESSORS_CACHE, professors)


# ---------------------------------------------------------------------------
# Step 6: Build professor profiles
# ---------------------------------------------------------------------------

if should_run(6):
    print("=" * 50)
    print("STEP 6 — Building professor profiles")
    print("=" * 50)
    from src.data_processing.profile_builder import ProfileStore
    store = ProfileStore()
    store.save()
    store.summary()


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print(f"\nProfessors in dataset: {len(professors)}")
for name, data in professors.items():
    oa = data.get("openalex", {})
    print(f"\n{name}")
    print(f"  Publications : {len(oa.get('publications', []))}")
    print(f"  Courses      : {len(data.get('courses', []))}")
    print(f"  Proposals    : {len(data.get('thesis_proposals', []))}")
