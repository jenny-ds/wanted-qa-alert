"""Saves and loads daily job snapshots from data/ directory."""

import json
import os
from datetime import date, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _path(d: date, source: str = "wanted") -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{source}_{d.isoformat()}.json")


def save(jobs: list[dict], d: date | None = None, source: str = "wanted") -> None:
    if d is None:
        d = date.today()
    with open(_path(d, source), "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)


def load(d: date, source: str = "wanted") -> list[dict] | None:
    path = _path(d, source)
    # Fallback: support legacy filenames without source prefix (wanted only)
    if not os.path.exists(path) and source == "wanted":
        legacy = os.path.join(DATA_DIR, f"{d.isoformat()}.json")
        if os.path.exists(legacy):
            with open(legacy, encoding="utf-8") as f:
                return json.load(f)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_yesterday(source: str = "wanted") -> list[dict] | None:
    return load(date.today() - timedelta(days=1), source)


def load_today(source: str = "wanted") -> list[dict] | None:
    return load(date.today(), source)
