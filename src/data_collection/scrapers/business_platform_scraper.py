"""
BusinessPlatform (businessplatform.unisg.ch) thesis topic scraper.

Scrapes all published thesis proposals from the marketplace and extracts:
  - title, author (professor), description, requirements, research area,
    keywords, state, sys_id, url

Uses Selenium because the site is ServiceNow/AngularJS rendered.
If a login wall is detected, Chrome opens visibly so the user can log in.
"""

import json
import os
import time
import unicodedata
import re
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://businessplatform.unisg.ch"
MARKETPLACE_URL = f"{BASE_URL}/csp?id=ww_topic_marketplace"

# Dedicated scraper profile — separate from your normal Chrome, keeps cookies
CHROME_SCRAPER_PROFILE = os.path.expanduser("~/chrome_scraper_profile")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def _make_driver(headless: bool = False) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1440,900")
    opts.add_argument(f"--user-data-dir={CHROME_SCRAPER_PROFILE}")
    return webdriver.Chrome(options=opts)


def _wait(driver, timeout: int = 20) -> WebDriverWait:
    return WebDriverWait(driver, timeout)


def _is_login_page(driver) -> bool:
    url = driver.current_url.lower()
    return any(kw in url for kw in ["login", "sso", "auth", "saml", "adfs", "microsoft", "google", "signin"])


def _wait_for_login(driver, timeout: int = 300):
    """Block until we're past the login page (user logs in manually)."""
    print("  [auth] Login page detected — please log in in the browser window.")
    print(f"  [auth] Waiting up to {timeout}s...")
    for _ in range(timeout):
        if not _is_login_page(driver):
            print("  [auth] Login successful.")
            return
        time.sleep(1)
    raise TimeoutError("Login not completed within timeout.")


# ---------------------------------------------------------------------------
# Field extraction helpers
# ---------------------------------------------------------------------------

def _get_field_value(driver, field_id: str) -> Optional[str]:
    """
    Extract value from a ServiceNow form field.
    Handles: input (readonly), textarea, select2 reference/choice.
    """
    # Try select2 display value first (reference/choice fields)
    try:
        el = driver.find_element(
            By.CSS_SELECTOR,
            f"#s2id_sp_formfield_{field_id} .select2-chosen"
        )
        val = el.text.strip()
        if val and val != "-- None --":
            return val
    except Exception:
        pass

    # Try input or textarea
    try:
        el = driver.find_element(By.ID, f"sp_formfield_{field_id}")
        val = el.get_attribute("value") or el.text.strip()
        if val:
            return val.strip()
    except Exception:
        pass

    return None


def _get_all_form_fields(driver) -> dict:
    """
    Generic extractor: reads all visible form field label/value pairs.
    Falls back to reading aria-label attributes for field identification.
    """
    data = {}

    # Read select2 fields (choice/reference)
    for el in driver.find_elements(By.CSS_SELECTOR, ".select2-container"):
        container_id = el.get_attribute("id") or ""
        if not container_id.startswith("s2id_sp_formfield_"):
            continue
        field_name = container_id.replace("s2id_sp_formfield_", "")
        chosen = el.find_elements(By.CSS_SELECTOR, ".select2-chosen")
        if chosen:
            val = chosen[0].text.strip()
            if val and val != "-- None --":
                data[field_name] = val

    # Read input/textarea fields
    for el in driver.find_elements(
        By.CSS_SELECTOR,
        "input.form-control[id^='sp_formfield_'], textarea[id^='sp_formfield_']"
    ):
        field_name = el.get_attribute("id").replace("sp_formfield_", "")
        val = el.get_attribute("value") or el.text.strip()
        if val and field_name not in data:
            data[field_name] = val.strip()

    return data


# ---------------------------------------------------------------------------
# Step 1: Collect all thesis card links from marketplace
# ---------------------------------------------------------------------------

def _collect_page_cards(driver) -> list[dict]:
    """Collect all thesis cards visible on the current page."""
    theses = []
    cards = driver.find_elements(By.CSS_SELECTOR, "li.item-card-column")
    for card in cards:
        try:
            link = card.find_element(By.CSS_SELECTOR, "a[href*='x_unsg_ww_thesis_topic']")
            href = link.get_attribute("href")
            sys_id_match = re.search(r"sys_id=([a-f0-9]+)", href)
            sys_id = sys_id_match.group(1) if sys_id_match else None
            panel = card.find_element(By.CSS_SELECTOR, "[data-original-title]")
            title_preview = panel.get_attribute("data-original-title").strip()
            theses.append({
                "sys_id": sys_id,
                "url": href if href.startswith("http") else BASE_URL + "/" + href,
                "title_preview": title_preview,
            })
        except Exception:
            continue
    return theses


def _get_thesis_links(driver) -> list[dict]:
    """
    Load the marketplace and collect all thesis card links across all pages.
    Handles pagination via the Next button.
    """
    driver.get(MARKETPLACE_URL)
    time.sleep(3)

    print(f"  [debug] Current URL: {driver.current_url}")

    if _is_login_page(driver) or "item-card-column" not in driver.page_source:
        _wait_for_login(driver)
        driver.get(MARKETPLACE_URL)
        time.sleep(3)

    print(f"  [debug] URL after login check: {driver.current_url}")

    _wait(driver, timeout=30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li.item-card-column"))
    )
    time.sleep(2)

    all_theses = []
    page = 1

    while True:
        cards = _collect_page_cards(driver)
        all_theses.extend(cards)
        print(f"  Page {page}: {len(cards)} topics (total so far: {len(all_theses)})")

        # Look for a visible "Next" button
        next_btns = driver.find_elements(
            By.XPATH,
            "//button[contains(@class,'nav-button') and normalize-space(text())='Next' and not(@aria-hidden='true')]"
        )
        if not next_btns:
            break

        next_btn = next_btns[0]
        driver.execute_script("arguments[0].click();", next_btn)
        page += 1
        time.sleep(2)  # wait for Angular to re-render

        _wait(driver).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.item-card-column"))
        )
        time.sleep(1)

    return all_theses


# ---------------------------------------------------------------------------
# Step 2: Scrape individual thesis detail page
# ---------------------------------------------------------------------------

def _scrape_thesis(driver, thesis_info: dict) -> dict:
    """Navigate to a thesis detail page and extract all fields."""
    url = thesis_info["url"]
    if not url.startswith("http"):
        url = BASE_URL + "/csp?" + url.split("csp?")[-1]

    driver.get(url)

    try:
        _wait(driver, timeout=15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#sp_formfield_title"))
        )
        time.sleep(1)
    except Exception:
        return {**thesis_info, "error": "page did not load"}

    fields = _get_all_form_fields(driver)

    # Map raw ServiceNow field names to clean names
    field_map = {
        "title": "title",
        "author": "author",
        "description": "description",
        "application_requirement": "requirements",
        "state": "state",
        "are_you_a_student_or_a_supervisor": "role",
        "research_area": "research_area",
        "keywords": "keywords",
        "thesis_type": "thesis_type",
        "language": "language",
        "level": "level",
    }

    result = {
        "sys_id": thesis_info["sys_id"],
        "url": thesis_info["url"],
    }
    for raw, clean in field_map.items():
        if raw in fields:
            result[clean] = fields[raw]

    # Include any unmapped fields with raw_ prefix (future-proofing)
    mapped_raw = set(field_map.keys())
    for k, v in fields.items():
        if k not in mapped_raw:
            result[f"_raw_{k}"] = v

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scrape_all_thesis_topics(output_path: str = "data/thesis_topics.json") -> list[dict]:
    """
    Scrape all thesis topics from the marketplace.

    Saves results to output_path and returns the list.
    """
    print("[business_platform] Starting thesis topic scrape...")
    driver = _make_driver(headless=False)

    try:
        print("  Loading marketplace...")
        thesis_links = _get_thesis_links(driver)
        print(f"  Found {len(thesis_links)} thesis topics")

        results = []
        for i, info in enumerate(thesis_links, 1):
            print(f"  [{i}/{len(thesis_links)}] {info['title_preview'][:60]}")
            try:
                thesis = _scrape_thesis(driver, info)
                results.append(thesis)
            except Exception as e:
                print(f"    [error] {e}")
                results.append({**info, "error": str(e)})
            time.sleep(0.5)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n  Saved {len(results)} thesis topics to {output_path}")
        return results

    finally:
        driver.quit()


def match_theses_to_professors(
    thesis_topics: list[dict],
    professors: dict,
) -> dict:
    """
    Group thesis topics by professor name, matching against the professor dataset.

    Returns a dict: {professor_name: [thesis, ...]}
    """
    def normalize(name: str) -> str:
        name = name.lower().strip()
        name = unicodedata.normalize("NFD", name)
        name = "".join(c for c in name if unicodedata.category(c) != "Mn")
        return re.sub(r"[^a-z\s]", "", name)

    # Build lookup: normalized_name → professor_name
    prof_lookup = {normalize(name): name for name in professors}

    grouped = {name: [] for name in professors}
    unmatched = []

    for thesis in thesis_topics:
        author = thesis.get("author", "")
        if not author:
            unmatched.append(thesis)
            continue

        norm_author = normalize(author)
        matched_prof = None

        # Try exact token match
        author_tokens = set(norm_author.split())
        for norm_prof, prof_name in prof_lookup.items():
            prof_tokens = set(norm_prof.split())
            if author_tokens == prof_tokens or author_tokens.issubset(prof_tokens):
                matched_prof = prof_name
                break

        if matched_prof:
            grouped[matched_prof].append(thesis)
        else:
            unmatched.append(thesis)

    if unmatched:
        grouped["_unmatched"] = unmatched

    return grouped
