"""
Alexandria scraper — uses the DSpace 7 REST API directly (no browser / no CAPTCHA).

Confirmed HSG field names from live API inspection:
  stgallen.person.title          → Title (e.g. "Prof. Ph.D.")
  person.familyName              → Last Name
  person.givenName               → First Name
  person.email                   → Email
  stgallen.person.phone          → Phone
  oairecerif.identifier.url      → Website / profile URLs
  stgallen.person.mainFocuses    → Main focuses (list)
  stgallen.person.fieldsOfResarch→ Fields of research (list, note HSG typo)
  stgallen.person.career         → Professional career (HTML)
  stgallen.person.education      → Education (HTML)
  stgallen.person.additionalInfo → Additional info (HTML)
"""

import html
import re
import requests
from typing import Optional

from .constants import full_professors_SoM

API_BASE = "https://www.alexandria.unisg.ch/server/api"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (research scraper)",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get(url: str, params: dict = None) -> dict:
    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()


def _meta_values(metadata: dict, field: str) -> list:
    return [e["value"] for e in metadata.get(field, []) if e.get("value")]


def _meta_one(metadata: dict, field: str) -> Optional[str]:
    vals = _meta_values(metadata, field)
    return vals[0] if vals else None


# Domains that are NOT personal websites (social media, academic databases, etc.)
_NON_PERSONAL_DOMAINS = {
    "linkedin.com", "researchgate.net", "twitter.com", "x.com",
    "facebook.com", "instagram.com", "xing.com", "scholar.google.com",
    "orcid.org", "scopus.com", "webofscience.com", "ssrn.com",
    "academia.edu", "mendeley.com", "alexandria.unisg.ch",
    "youtube.com", "github.com",
}
# unisg.ch subdomains that are generic portals, not personal pages
_NON_PERSONAL_UNISG = {"www.unisg.ch", "unisg.ch", "courses.unisg.ch", "compass.unisg.ch"}


def _extract_personal_website(urls: list) -> Optional[str]:
    """
    From a list of URLs, return the first that looks like a personal/lab website.
    Skips social media, academic databases, and HSG internal pages.
    """
    for url in urls:
        url = url.strip()
        if not url.startswith("http"):
            continue
        # Extract domain
        domain = url.split("//")[-1].split("/")[0].lower()
        domain = domain.lstrip("www.")
        # Check against known non-personal domains
        if any(domain == d or domain.endswith("." + d) for d in _NON_PERSONAL_DOMAINS):
            continue
        if domain in _NON_PERSONAL_UNISG:
            continue
        return url
    return None


def _strip_html(raw: str) -> str:
    """Remove HTML tags, decode entities, and collapse whitespace."""
    text = re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def _search_person(last_name: str, first_name: str) -> Optional[dict]:
    """
    Use the DSpace search API to find a person item by name.
    Returns the raw item dict (with 'uuid' and 'metadata') or None.
    """
    try:
        data = _get(
            f"{API_BASE}/discover/search/objects",
            params={
                "query": f"{first_name} {last_name}",
                "dsoType": "item",
                "f.entityType": "Person,equals",
                "size": 10,
            },
        )
    except Exception as e:
        print(f"  [error] Search API failed: {e}")
        return None

    objects = (
        data.get("_embedded", {})
            .get("searchResult", {})
            .get("_embedded", {})
            .get("objects", [])
    )

    first_lower = first_name.lower()
    last_lower = last_name.lower()

    for obj in objects:
        item = obj.get("_embedded", {}).get("indexableObject", {})
        if item.get("type") != "item":
            continue
        meta = item.get("metadata", {})
        item_last = (_meta_one(meta, "person.familyName") or "").lower()
        item_first = (_meta_one(meta, "person.givenName") or "").lower()
        if item_last == last_lower and first_lower in item_first:
            return item

    # Fallback: last name only
    for obj in objects:
        item = obj.get("_embedded", {}).get("indexableObject", {})
        if item.get("type") != "item":
            continue
        meta = item.get("metadata", {})
        if (_meta_one(meta, "person.familyName") or "").lower() == last_lower:
            return item

    return None


# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------

def _parse_metadata(metadata: dict, uuid: str) -> dict:
    """Map confirmed HSG/DSpace metadata fields to a clean output dict."""

    result = {
        "profile_url": f"https://www.alexandria.unisg.ch/entities/person/{uuid}",
    }

    # --- Basic info ---
    if val := _meta_one(metadata, "stgallen.person.title"):
        result["Title"] = val
    if val := _meta_one(metadata, "person.familyName"):
        result["Last Name"] = val
    if val := _meta_one(metadata, "person.givenName"):
        result["First Name"] = val
    if val := _meta_one(metadata, "person.email"):
        result["Email"] = val
    if val := _meta_one(metadata, "person.identifier.orcid"):
        result["ORCID"] = val
    if val := _meta_one(metadata, "stgallen.person.phone"):
        result["Phone"] = val

    urls = _meta_values(metadata, "oairecerif.identifier.url")
    if urls:
        result["URLs"] = urls
        personal = _extract_personal_website(urls)
        if personal:
            result["personal_website"] = personal

    # --- Other info ---
    focuses = _meta_values(metadata, "stgallen.person.mainFocuses")
    if focuses:
        result["Main focuses"] = focuses

    fields = _meta_values(metadata, "stgallen.person.fieldsOfResarch")  # HSG typo
    if fields:
        result["Fields of research"] = fields

    if raw := _meta_one(metadata, "stgallen.person.career"):
        result["Professional career"] = _strip_html(raw)

    if raw := _meta_one(metadata, "stgallen.person.education"):
        result["Education"] = _strip_html(raw)

    if raw := _meta_one(metadata, "stgallen.person.additionalInfo"):
        result["Additional info"] = _strip_html(raw)

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scrape_professor(full_name: str) -> Optional[dict]:
    """
    Fetch all available info for a professor from the Alexandria REST API.
    Returns a dict with the extracted fields, or None if not found.
    """
    parts = full_name.strip().split()
    first_name = parts[0]
    last_name = parts[-1]

    print(f"[alexandria] Searching for: {full_name}")

    item = _search_person(last_name, first_name)
    if not item:
        print(f"  [warn] Not found: {full_name}")
        return None

    uuid = item["uuid"]
    print(f"  Found UUID: {uuid}")

    metadata = item.get("metadata", {})
    result = _parse_metadata(metadata, uuid)
    result["name"] = full_name
    return result


def scrape_all_professors() -> dict:
    """
    Scrape Alexandria data for every professor listed in constants.py.
    Returns a dict keyed by professor name.
    """
    results = {}
    for professor in full_professors_SoM:
        data = scrape_professor(professor)
        if data:
            results[professor] = data
    return results
