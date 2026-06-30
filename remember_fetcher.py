"""
Fetches QA job listings from Remember career (career.rememberapp.co.kr).
Searches with keyword "QA", sorts by latest (id_desc), fetches up to MAX_PAGES pages.
"""

import json
import time

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://career.rememberapp.co.kr",
    "Referer": "https://career.rememberapp.co.kr/",
}

BASE_URL = "https://career-api.rememberapp.co.kr/job_postings"

SEARCH_PARAMS = {
    "includeAppliedJobPosting": False,
    "leaderPosition": False,
    "organizationType": "all",
    "applicationType": "all",
    "keywords": ["QA"],
}

MAX_PAGES = 10
PER_PAGE = 100


def _fetch_page(page: int) -> dict:
    resp = requests.get(
        BASE_URL,
        params={
            "search": json.dumps(SEARCH_PARAMS, ensure_ascii=False),
            "sort": "id_desc",
            "per": PER_PAGE,
            "page": page,
        },
        headers=HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_all_jobs() -> list[dict]:
    all_jobs = {}
    page = 1

    while page <= MAX_PAGES:
        data = _fetch_page(page)
        jobs = data.get("data", [])
        meta = data.get("meta", {})

        if not jobs:
            break

        for job in jobs:
            jid = job.get("id")
            if jid and jid not in all_jobs:
                all_jobs[jid] = normalize(job)

        total_pages = meta.get("total_pages", 1)
        if page >= total_pages:
            break

        page += 1
        time.sleep(0.3)

    return list(all_jobs.values())


def normalize(job: dict) -> dict:
    org = job.get("organization") or job.get("company") or {}
    company_name = org.get("name", "") if isinstance(org, dict) else ""

    addr = job.get("normalized_address") or {}
    level1 = addr.get("level1", "")
    level2 = addr.get("level2", "")
    location = f"{level1} {level2}".strip() if level1 or level2 else ""

    job_id = job.get("id")
    return {
        "id": job_id,
        "title": job.get("title", ""),
        "company": company_name,
        "location": location,
        "url": f"https://career.rememberapp.co.kr/job/postings/{job_id}",
        "ends_at": job.get("ends_at"),
    }
