"""Entry point: fetch → store → compare → notify (Wanted + Remember)."""

from fetcher import fetch_all_jobs as fetch_wanted
from remember_fetcher import fetch_all_jobs as fetch_remember
from store import save, load_yesterday, load_today
from compare import compare
from notifier import send_email


def _run_source(source: str, fetch_fn) -> dict:
    print(f"[{source}] 공고 수집 중...")
    jobs = fetch_fn()
    print(f"[{source}] 수집 완료: {len(jobs)}개")
    save(jobs, source=source)

    yesterday = load_yesterday(source=source)
    today = load_today(source=source)

    if yesterday is None:
        print(f"[{source}] 어제 데이터 없음 — 첫 실행입니다.")
        return {"added": today, "removed": [], "total_today": len(today)}

    diff = compare(yesterday, today)
    print(f"[{source}] 새 공고: {len(diff['added'])}개 / 마감: {len(diff['removed'])}개")
    return diff


def run():
    wanted_diff = _run_source("wanted", fetch_wanted)
    remember_diff = _run_source("remember", fetch_remember)
    send_email(wanted_diff, remember_diff)


if __name__ == "__main__":
    run()
