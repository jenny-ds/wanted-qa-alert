"""
Fetches QA job listings from Wanted with filters:
- Experience: 3~7 years (years=3 means 3+ years; API doesn't support upper bound directly)
- Location: Seoul, Incheon, Gyeonggi
- Sort: latest
"""

import requests
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer": "https://www.wanted.co.kr/jobs?query=QA",
    "Wanted-User-Agent": "wanted-web",
    "X-Wanted-Language": "ko",
}

BASE_PARAMS = {
    "query": "QA",
    "country": "kr",
    "job_sort": "job.latest_order",
    "limit": 100,
}

# years=3 means "3년 이상" — we'll filter max 7 years client-side via annual_to/experience
EXPERIENCE_YEARS = ["3", "4", "5", "6", "7"]
LOCATIONS = ["seoul", "incheon", "gyeonggi"]


def _fetch_page(years: str, offset: int) -> dict:
    params = {
        **BASE_PARAMS,
        "years": years,
        "offset": offset,
    }
    for loc in LOCATIONS:
        params.setdefault("locations", [])
        if isinstance(params["locations"], list):
            params["locations"].append(loc)

    resp = requests.get(
        "https://www.wanted.co.kr/api/v4/jobs",
        params=params,
        headers=HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_all_jobs() -> list[dict]:
    all_jobs = {}

    for years in EXPERIENCE_YEARS:
        offset = 0
        while True:
            data = _fetch_page(years, offset)
            jobs = data.get("data", [])
            if not jobs:
                break
            for job in jobs:
                jid = job.get("id")
                if jid and jid not in all_jobs:
                    all_jobs[jid] = normalize(job)
            next_link = data.get("links", {}).get("next")
            if not next_link:
                break
            offset += len(jobs)
            time.sleep(0.3)

    return list(all_jobs.values())


def normalize(job: dict) -> dict:
    return {
        "id": job.get("id"),
        "title": job.get("position"),
        "company": job.get("company", {}).get("name"),
        "location": job.get("address", {}).get("location"),
        "url": f"https://www.wanted.co.kr/wd/{job.get('id')}",
        "due_time": job.get("due_time"),
    }
