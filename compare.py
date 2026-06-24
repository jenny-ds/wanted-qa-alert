"""Compares two snapshots and returns added/removed job lists."""


def compare(yesterday: list[dict], today: list[dict]) -> dict:
    yesterday_ids = {j["id"]: j for j in yesterday}
    today_ids = {j["id"]: j for j in today}

    added = [j for jid, j in today_ids.items() if jid not in yesterday_ids]
    removed = [j for jid, j in yesterday_ids.items() if jid not in today_ids]

    return {"added": added, "removed": removed, "total_today": len(today)}
