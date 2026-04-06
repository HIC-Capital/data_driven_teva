"""
Compass (courses.unisg.ch) scraper.

Uses Selenium because courses.unisg.ch requires TLS 1.3+ (incompatible
with Python 3.9's LibreSSL). Chrome has no such limitation.

Flow:
  1. Fetch lecturer overview → find matching professor by name
  2. Fetch lecturer detail page → collect courses (title, number, URL)
  3. For each course, fetch detail page → get PDF URL
  4. Download PDFs to data/course_pdfs/{professor_slug}/
"""

import os
import re
import time
import unicodedata
from typing import Optional

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .constants import full_professors_SoM

BASE_URL = "https://courses.unisg.ch"
PDF_OUTPUT_DIR = "data/course_pdfs"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_argument("--js-flags=--max-old-space-size=512")
    return webdriver.Chrome(options=opts)


def _wait_for(driver, css_selector: str, timeout: int = 15) -> bool:
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
        )
        return True
    except Exception:
        return False


def _normalize(name: str) -> str:
    name = name.lower().strip()
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    name = re.sub(r"[^a-z\s]", "", name)
    return name


def _names_match(site_name: str, full_name: str) -> bool:
    """Match 'Lastname Firstname' (site) against 'Firstname Lastname' (ours)."""
    site_tokens = set(_normalize(site_name).split())
    our_tokens = set(_normalize(full_name).split())
    return site_tokens == our_tokens


def _download_pdf(pdf_url: str, dest_path: str) -> bool:
    try:
        resp = requests.get(pdf_url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0"
        })
        if resp.status_code == 200 and b"%PDF" in resp.content[:10]:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(resp.content)
            return True
        return False
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Scraping steps
# ---------------------------------------------------------------------------

def _get_all_term_labels(driver: webdriver.Chrome) -> list[str]:
    """Open the term dropdown on the current page and return all term labels."""
    from selenium.webdriver.common.keys import Keys
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "[data-test='event-term-selector.current-term']")
            )
        )
        btn.click()
        time.sleep(0.8)
        items = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "button[mat-menu-item], .mat-mdc-menu-item")
            )
        )
        labels = [el.text.strip() for el in items if el.text.strip()]
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(0.3)
        return labels
    except Exception as e:
        print(f"  [warn] Could not read term selector: {e}")
        return []


def _find_lecturer_urls_for_terms(driver: webdriver.Chrome, full_name: str, num_semesters: int) -> list[tuple]:
    """
    For each of the last num_semesters, navigate fresh to the lecturer list,
    select the term, and collect (term_label, lecturer_url).
    Navigates to the list page fresh for every term to avoid stale elements.
    Returns a list of (term_label, url) tuples.
    """
    from selenium.webdriver.common.keys import Keys

    # First load: get all available term labels
    driver.get(f"{BASE_URL}/lecturer/lecturers")
    if not _wait_for(driver, "table tbody tr td a", timeout=20):
        print("  [error] Lecturer table did not load")
        return []
    time.sleep(1)

    all_terms = _get_all_term_labels(driver)
    terms_to_fetch = all_terms[:num_semesters] if all_terms else []
    if not terms_to_fetch:
        # Fallback: just grab current term
        links = driver.find_elements(By.CSS_SELECTOR, "table tbody tr td a")
        for link in links:
            if _names_match(link.text.strip(), full_name):
                return [("current", link.get_attribute("href"))]
        return []

    results = []
    for term_label in terms_to_fetch:
        # Navigate fresh to the list page each time to avoid stale elements
        driver.get(f"{BASE_URL}/lecturer/lecturers")
        if not _wait_for(driver, "table tbody tr td a", timeout=20):
            continue
        time.sleep(1)

        # Click the term selector and select this term
        try:
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[data-test='event-term-selector.current-term']")
                )
            )
            current_term_text = btn.text.strip()

            # Skip clicking if already on this term
            if term_label in current_term_text:
                pass  # already on correct term, just find the link
            else:
                btn.click()
                time.sleep(0.8)
                options = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "button[mat-menu-item], .mat-mdc-menu-item")
                    )
                )
                clicked = False
                for opt in options:
                    if opt.text.strip() == term_label:
                        opt.click()
                        clicked = True
                        break
                if not clicked:
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    continue
                time.sleep(2)
                if not _wait_for(driver, "table tbody tr td a", timeout=15):
                    continue

        except Exception as e:
            print(f"  [warn] Term '{term_label}': {e}")
            continue

        # Find the lecturer link for this term
        links = driver.find_elements(By.CSS_SELECTOR, "table tbody tr td a")
        for link in links:
            if _names_match(link.text.strip(), full_name):
                results.append((term_label, link.get_attribute("href")))
                break

    return results


def _get_courses(driver: webdriver.Chrome, lecturer_url: str, term_label: str = "current") -> list[dict]:
    """
    Navigate to a lecturer URL (already term-specific) and return courses.
    """
    driver.get(lecturer_url)
    time.sleep(3)

    items = driver.find_elements(By.CSS_SELECTOR, "[data-test='event-event-list-item']")
    courses = []
    for item in items:
        try:
            title_el = item.find_element(By.CSS_SELECTOR, "[data-test='event-event-list-item-title'] a")
            number_el = item.find_element(By.CSS_SELECTOR, "[data-test='event-event-list-item-id']")
            courses.append({
                "title": title_el.text.strip(),
                "course_number": number_el.text.strip(),
                "url": title_el.get_attribute("href"),
                "semester": term_label,
            })
        except Exception:
            continue

    return courses


def _get_pdf_url(driver: webdriver.Chrome, course_url: str) -> Optional[str]:
    """Fetch course detail page and return the fact-sheet PDF URL."""
    driver.get(course_url)

    if not _wait_for(driver, "a[href*='CourseInformationSheet']", timeout=15):
        return None

    els = driver.find_elements(By.CSS_SELECTOR, "a[href*='CourseInformationSheet']")
    if els:
        return els[0].get_attribute("href")
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scrape_professor_courses(full_name: str, num_semesters: int = 6) -> Optional[dict]:
    """
    Scrape courses and download PDFs for a single professor across the last
    num_semesters semesters (default 6). Deduplicates by course_number.
    Returns {"courses": [...]} or None if not found.
    """
    print(f"[compass] Scraping courses for: {full_name}")
    driver = _make_driver()

    try:
        # Collect (term_label, lecturer_url) for each semester by iterating the list page
        term_urls = _find_lecturer_urls_for_terms(driver, full_name, num_semesters)

        if not term_urls:
            print(f"  [warn] Not found in lecturer list: {full_name}")
            return None

        print(f"  Found in {len(term_urls)} semester(s)")

        slug = _normalize(full_name).replace(" ", "_")
        pdf_dir = os.path.join(PDF_OUTPUT_DIR, slug)

        all_courses = []

        for term_label, lecturer_url in term_urls:
            term_courses = _get_courses(driver, lecturer_url, term_label=term_label)
            print(f"  [{term_label}] {len(term_courses)} course(s)")

            for course in term_courses:
                time.sleep(0.5)
                try:
                    pdf_url = _get_pdf_url(driver, course["url"])
                    course["pdf_url"] = pdf_url
                    if pdf_url:
                        filename = re.sub(r"[^\w\-.]", "_", course["title"])[:60] + ".pdf"
                        dest = os.path.join(pdf_dir, filename)
                        # Only download if not already on disk (same course, different semester)
                        if os.path.exists(dest):
                            course["pdf_path"] = dest
                            print(f"    = {course['title']} (PDF reused)")
                        else:
                            ok = _download_pdf(pdf_url, dest)
                            course["pdf_path"] = dest if ok else None
                            print(f"    {'✓' if ok else '✗'} {course['title']}")
                    else:
                        course["pdf_path"] = None
                        print(f"    ? No PDF: {course['title']}")
                except Exception as e:
                    course["pdf_url"] = None
                    course["pdf_path"] = None
                    print(f"    [error] {course['title']}: {e}")

                all_courses.append(course)

        return {"courses": all_courses}

    finally:
        driver.quit()


def scrape_all_professors_courses() -> dict:
    """Scrape courses for all professors in constants.py."""
    results = {}
    for professor in full_professors_SoM:
        data = scrape_professor_courses(professor)
        if data:
            results[professor] = data
        time.sleep(1)
    return results
