"""Entry point: fetch → store → compare → notify."""

import sys
from datetime import date

from fetcher import fetch_all_jobs
from store import save, load_yesterday, load_today
from compare import compare
from notifier import send_email


def run():
    print("공고 수집 중...")
    jobs = fetch_all_jobs()
    print(f"수집 완료: {len(jobs)}개")
    save(jobs)

    yesterday = load_yesterday()
    today = load_today()

    if yesterday is None:
        print("어제 데이터 없음 — 오늘 첫 실행입니다. 내일부터 비교 알림이 발송됩니다.")
        # Still send a summary email on first run
        diff = {"added": today, "removed": [], "total_today": len(today)}
    else:
        diff = compare(yesterday, today)
        print(f"새 공고: {len(diff['added'])}개 / 마감: {len(diff['removed'])}개")

    send_email(diff)


if __name__ == "__main__":
    run()
