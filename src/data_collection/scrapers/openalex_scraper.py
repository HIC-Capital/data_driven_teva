"""
OpenAlex scraper — fetches publication data for HSG professors.

API docs: https://docs.openalex.org
No API key required (polite pool with email in params recommended).

Per publication we collect:
  - title         (used now for matching)
  - year
  - abstract      (stored for future use — richer matching)
  - topics        (OpenAlex auto-tagged research topics)
  - cited_by_count
"""

import requests
from typing import Optional

OPENALEX_API = "https://api.openalex.org"
POLITE_EMAIL = "research-scraper@unisg.ch"  # keeps us in the polite pool

HEADERS = {"User-Agent": f"mailto:{POLITE_EMAIL}"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get(url: str, params: dict = None, retries: int = 3) -> dict:
    p = params or {}
    p["mailto"] = POLITE_EMAIL
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=p, headers=HEADERS, timeout=60)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                print(f"  [warn] Timeout, retrying ({attempt + 2}/{retries})...")
            else:
                raise


def _reconstruct_abstract(inverted_index: Optional[dict]) -> Optional[str]:
    """
    OpenAlex stores abstracts as an inverted index {word: [positions]}.
    This reconstructs the original text.
    """
    if not inverted_index:
        return None
    words = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
    return " ".join(words[i] for i in sorted(words))


# ---------------------------------------------------------------------------
# Author lookup
# ---------------------------------------------------------------------------

HSG_OPENALEX_ID = "I114027177"  # University of St. Gallen OpenAlex institution ID


def _find_author(full_name: str, email: Optional[str] = None) -> Optional[dict]:
    """
    Search OpenAlex for an HSG author.
    Strategy:
      1. Search filtered to University of St. Gallen — avoids name collisions
      2. Fallback: unfiltered search, validate last_known_institution is HSG
      3. Last resort: first result (with a warning)
    """
    last_name = full_name.strip().split()[-1]

    # 1. Search within HSG
    data = _get(f"{OPENALEX_API}/authors", {
        "search": full_name,
        "filter": f"last_known_institutions.id:{HSG_OPENALEX_ID}",
        "per_page": 5,
    })
    results = data.get("results", [])
    if results:
        return results[0]

    # 2. Unfiltered search — check institution manually
    data = _get(f"{OPENALEX_API}/authors", {
        "search": full_name,
        "per_page": 10,
    })
    results = data.get("results", [])
    if not results:
        return None

    for author in results:
        institutions = author.get("last_known_institutions") or []
        for inst in institutions:
            if "gallen" in (inst.get("display_name") or "").lower():
                return author

    # 3. Last resort — warn and take top result
    print(f"  [warn] Could not confirm HSG affiliation for '{full_name}', using top result")
    return results[0]


# ---------------------------------------------------------------------------
# Publications
# ---------------------------------------------------------------------------

def _fetch_publications(author_id: str, max_results: int = 100) -> list:
    """
    Fetch publications for an OpenAlex author ID.
    Returns a list of publication dicts.
    """
    publications = []
    cursor = "*"

    while len(publications) < max_results:
        batch_size = min(50, max_results - len(publications))
        data = _get(f"{OPENALEX_API}/works", {
            "filter": f"author.id:{author_id}",
            "select": "title,publication_year,abstract_inverted_index,topics,cited_by_count,type",
            "per_page": batch_size,
            "cursor": cursor,
            "sort": "cited_by_count:desc",
        })

        results = data.get("results", [])
        if not results:
            break

        for work in results:
            pub = {
                "title": work.get("title"),
                "year": work.get("publication_year"),
                "type": work.get("type"),
                "cited_by_count": work.get("cited_by_count", 0),
                "topics": [
                    t["display_name"]
                    for t in (work.get("topics") or [])
                ],
                # Abstract stored but not used in matching yet
                "abstract": _reconstruct_abstract(
                    work.get("abstract_inverted_index")
                ),
            }
            publications.append(pub)

        next_cursor = data.get("meta", {}).get("next_cursor")
        if not next_cursor:
            break
        cursor = next_cursor

    return publications


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scrape_professor_publications(
    full_name: str,
    email: Optional[str] = None,
    max_results: int = 100,
) -> Optional[dict]:
    """
    Fetch OpenAlex data for a professor.

    Returns:
      {
        "openalex_id": str,
        "openalex_name": str,
        "works_count": int,
        "h_index": int,
        "topics": [...],       # OpenAlex author-level topic tags
        "publications": [
          {
            "title": str,
            "year": int,
            "cited_by_count": int,
            "topics": [...],   # per-paper topics
            "abstract": str,   # stored for future use
          }, ...
        ]
      }
    Or None if the author is not found.
    """
    print(f"[openalex] Searching for: {full_name}")

    author = _find_author(full_name, email)
    if not author:
        print(f"  [warn] Not found: {full_name}")
        return None

    author_id = author["id"].split("/")[-1]  # e.g. "A123456789"
    print(f"  Found: {author['display_name']} ({author_id}), {author.get('works_count', '?')} works")

    publications = _fetch_publications(author_id, max_results=max_results)

    # Author-level topics (OpenAlex aggregates across all works)
    author_topics = [
        t["display_name"]
        for t in (author.get("topics") or [])
    ]

    return {
        "openalex_id": author_id,
        "openalex_name": author.get("display_name"),
        "works_count": author.get("works_count"),
        "h_index": author.get("summary_stats", {}).get("h_index"),
        "topics": author_topics,
        "publications": publications,
    }
