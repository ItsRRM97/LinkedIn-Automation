"""Daily comment quota tracking for feed engage daemon."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_day() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_quota(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"day": utc_day(), "posted": 0, "skipped": 0, "comments": []}
    with path.open() as f:
        data = json.load(f)
    if data.get("day") != utc_day():
        return {"day": utc_day(), "posted": 0, "skipped": 0, "comments": []}
    data.setdefault("posted", 0)
    data.setdefault("skipped", 0)
    data.setdefault("comments", [])
    return data


def save_quota(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def remaining_today(data: dict[str, Any], daily_cap: int) -> int:
    return max(0, daily_cap - int(data.get("posted", 0)))


def can_post(data: dict[str, Any], daily_cap: int) -> bool:
    return remaining_today(data, daily_cap) > 0


def record_post(path: Path, data: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    data["posted"] = int(data.get("posted", 0)) + 1
    comments = list(data.get("comments", []))
    comments.append(entry)
    data["comments"] = comments[-200:]
    save_quota(path, data)
    return data


def compute_delay_seconds(
    *,
    window_seconds: float,
    comments_left_in_window: int,
    daily_remaining: int,
    min_delay: int,
    max_delay: int,
) -> int:
    if comments_left_in_window <= 0 or daily_remaining <= 0:
        return max_delay
    spread = window_seconds / max(1, min(comments_left_in_window, daily_remaining))
    delay = int(max(min_delay, min(max_delay, spread)))
    return delay
