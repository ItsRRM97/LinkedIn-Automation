"""Buffer publish windows for feed engage daemon."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

GH_DIR = Path(__file__).resolve().parent.parent / "linkedin-golden-hour"
if str(GH_DIR) not in sys.path:
    sys.path.insert(0, str(GH_DIR))

from golden_hour import (  # noqa: E402
    buffer_graphql,
    load_config as load_golden_hour_config,
    parse_ts,
    should_skip_post,
    utcnow,
)


def buffer_list_posts(cfg: dict[str, Any], statuses: list[str]) -> list[dict[str, Any]]:
    data = buffer_graphql(
        """
        query ListPosts($input: PostsInput!, $first: Int!) {
          posts(input: $input, first: $first) {
            edges {
              node {
                id
                status
                text
                sentAt
                dueAt
                channelService
                via
                externalLink
              }
            }
          }
        }
        """,
        {
            "input": {
                "organizationId": cfg["buffer_organization_id"],
                "filter": {
                    "channelIds": [cfg["linkedin_channel_id"]],
                    "status": statuses,
                },
                "sort": [{"field": "dueAt", "direction": "desc"}],
            },
            "first": int(cfg.get("list_posts_limit", 20)),
        },
    )
    return [e["node"] for e in data.get("posts", {}).get("edges", []) if e.get("node")]


def publish_anchor(post: dict[str, Any]) -> datetime | None:
    sent = parse_ts(post.get("sentAt"))
    if sent:
        return sent
    return parse_ts(post.get("dueAt"))


def engagement_window(
    post: dict[str, Any],
    *,
    pre_minutes: int = 15,
    post_minutes: int = 90,
) -> tuple[datetime | None, datetime | None]:
    anchor = publish_anchor(post)
    if not anchor:
        return None, None
    start = anchor - timedelta(minutes=pre_minutes)
    end = anchor + timedelta(minutes=post_minutes)
    return start, end


def in_engagement_window(
    post: dict[str, Any],
    cfg: dict[str, Any],
    now: datetime | None = None,
) -> bool:
    now = now or utcnow()
    pre = int(cfg.get("engage_pre_publish_minutes", 15))
    post = int(cfg.get("engage_post_publish_minutes", 90))
    start, end = engagement_window(post, pre_minutes=pre, post_minutes=post)
    if not start or not end:
        return False
    return start <= now <= end


def discover_active_engagement_posts(feed_cfg: dict[str, Any]) -> list[dict[str, Any]]:
    gh_cfg = load_golden_hour_config()
    now = utcnow()
    lookback = now - timedelta(hours=int(feed_cfg.get("buffer_lookback_hours", 48)))
    statuses = feed_cfg.get("buffer_statuses", ["scheduled", "sent"])
    active: list[dict[str, Any]] = []

    for post in buffer_list_posts(gh_cfg, statuses):
        if post.get("channelService") != "linkedin" or should_skip_post(post, gh_cfg):
            continue
        anchor = publish_anchor(post)
        if not anchor or anchor < lookback:
            continue
        if not in_engagement_window(post, feed_cfg, now):
            continue
        pre = int(feed_cfg.get("engage_pre_publish_minutes", 15))
        post_m = int(feed_cfg.get("engage_post_publish_minutes", 90))
        start, end = engagement_window(post, pre_minutes=pre, post_minutes=post_m)
        active.append(
            {
                **post,
                "publish_anchor": anchor.isoformat(),
                "window_start": start.isoformat() if start else None,
                "window_end": end.isoformat() if end else None,
                "window_seconds_remaining": max(0, (end - now).total_seconds()) if end else 0,
            }
        )

    active.sort(key=lambda p: p.get("window_seconds_remaining") or 0)
    return active
