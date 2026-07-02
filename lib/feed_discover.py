"""Feed discovery: home feed + thought-leader fallback when home feed is dry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from feed_post_classify import classify_post
from linkedin_cli_runner import LinkedInRunnerError, fetch_feed, fetch_user_feed, normalize_feed_item


def _is_noise_post(item: dict[str, Any], cfg: dict[str, Any]) -> bool:
    if item.get("is_group"):
        return True
    share_urn = str(item.get("share_urn") or "")
    if "groupPost" in share_urn:
        return True
    if item.get("is_promoted"):
        return True
    if cfg.get("skip_company_pages") and item.get("is_company"):
        return True
    return False


def _eligible_count(items: list[dict[str, Any]], cfg: dict[str, Any]) -> int:
    return sum(1 for item in items if classify_post(item, cfg)[0])


def load_thought_leaders(roster_path: Path) -> list[dict[str, Any]]:
    if not roster_path.exists():
        return []
    with roster_path.open() as f:
        data = json.load(f)
    leaders = data.get("leaders") or []
    return [leader for leader in leaders if isinstance(leader, dict) and leader.get("slug")]


def discover_feed_items(cfg: dict[str, Any], *, feed_dir: Path) -> list[dict[str, Any]]:
    """Fetch home feed; supplement with thought-leader activity when home feed is dry."""
    count = int(cfg.get("feed_fetch_count", 40))
    items = [normalize_feed_item(raw) for raw in fetch_feed(count)]
    items = [item for item in items if not _is_noise_post(item, cfg)]

    if cfg.get("target_mode", "home_feed") != "home_feed":
        return items

    threshold = int(cfg.get("thought_leader_fallback_min_eligible", 3))
    if _eligible_count(items, cfg) >= threshold:
        return items

    roster_file = cfg.get("thought_leaders_file", "thought_leaders.json")
    roster_path = feed_dir / roster_file
    per_leader = int(cfg.get("thought_leader_posts_per_leader", 3))
    leader_cap = int(cfg.get("thought_leader_count", 15))

    seen_urns = {item.get("urn") for item in items if item.get("urn")}
    for leader in load_thought_leaders(roster_path)[:leader_cap]:
        slug = str(leader.get("slug") or "").strip()
        if not slug:
            continue
        try:
            raw_posts = fetch_user_feed(slug, per_leader)
        except LinkedInRunnerError:
            continue
        for raw in raw_posts:
            item = normalize_feed_item(raw)
            urn = item.get("urn")
            if not urn or urn in seen_urns:
                continue
            if _is_noise_post(item, cfg):
                continue
            items.append(item)
            seen_urns.add(urn)

    return items
