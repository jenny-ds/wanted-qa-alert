"""Saves and loads daily job snapshots from data/ directory."""

import json
import os
from datetime import date, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _path(d: date) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{d.isoformat()}.json")


def save(jobs: list[dict], d: date | None = None) -> None:
    if d is None:
        d = date.today()
    with open(_path(d), "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)


def load(d: date) -> list[dict] | None:
    path = _path(d)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_yesterday() -> list[dict] | None:
    return load(date.today() - timedelta(days=1))


def load_today() -> list[dict] | None:
    return load(date.today())
