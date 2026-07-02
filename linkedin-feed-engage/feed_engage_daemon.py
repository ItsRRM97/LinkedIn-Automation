#!/usr/bin/env python3
"""Hands-off feed engage daemon: Buffer windows + Groq LLM + Composio comments."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FEED_DIR = Path(__file__).resolve().parent
REPO_ROOT = FEED_DIR.parent
LIB_DIR = REPO_ROOT / "lib"
STATE_DIR = FEED_DIR / "state"
CONFIG_PATH = FEED_DIR / "config.json"
QUOTA_PATH = STATE_DIR / "daily_quota.json"
PERSONA_PATH = FEED_DIR / "persona.txt"

if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from feed_buffer_windows import discover_active_engagement_posts  # noqa: E402
from feed_discover import discover_feed_items  # noqa: E402
from feed_post_classify import classify_post, rank_key  # noqa: E402
from feed_llm import LLMError, draft_comment, resolve_llm_provider  # noqa: E402
from feed_quota import (  # noqa: E402
    can_post,
    compute_delay_seconds,
    load_quota,
    record_post,
    remaining_today,
)
from linkedin_cli_runner import (  # noqa: E402
    LinkedInRunnerError,
    normalize_feed_item,
    post_comment,
)


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def load_feed_config() -> dict[str, Any]:
    with CONFIG_PATH.open() as f:
        return json.load(f)


def load_persona() -> str:
    if PERSONA_PATH.exists():
        return PERSONA_PATH.read_text().strip()
    return os.environ.get("FEED_PERSONA", "").strip()


def check_daemon_prereqs(llm_cfg: dict[str, Any]) -> str | None:
    provider = resolve_llm_provider(llm_cfg)
    if provider == "groq" and not (os.environ.get("GROQ_API_KEY") or llm_cfg.get("groq_api_key")):
        return (
            "GROQ_API_KEY not set. Add export GROQ_API_KEY=gsk_... to ~/.zshrc, "
            "run source ~/.zshrc, then bash scripts/preflight_feed_engage.sh"
        )
    if provider == "openrouter" and not (
        os.environ.get("OPENROUTER_API_KEY") or llm_cfg.get("openrouter_api_key")
    ):
        return "OPENROUTER_API_KEY not set (add to ~/.zshrc or set GROQ_API_KEY for Groq)"
    if not (os.environ.get("LINKEDIN_LI_AT") or os.environ.get("LI_AT")):
        return "LINKEDIN_LI_AT not set — run bash scripts/import_linkedin_cookies.sh"
    if not (os.environ.get("LINKEDIN_JSESSIONID") or os.environ.get("JSESSIONID")):
        return "LINKEDIN_JSESSIONID not set — run bash scripts/import_linkedin_cookies.sh"
    return None


def post_matches_filters(item: dict[str, Any], cfg: dict[str, Any]) -> tuple[bool, str, str | None]:
    allowed, reason, style = classify_post(item, cfg)
    return allowed, reason, style


def sanitize_comment(text: str, max_chars: int, style: str | None = None) -> str:
    cleaned = text.strip().strip('"').strip("'")
    cleaned = re.sub(r"[—–]", ", ", cleaned)
    if len(cleaned) > max_chars:
        cleaned = cleaned[: max_chars - 1].rsplit(" ", 1)[0] + "…"
    if style == "career_ack":
        if "?" in cleaned:
            cleaned = cleaned.split("?", 1)[0].strip().rstrip(",").rstrip(".")
            if cleaned and not cleaned.endswith((".", "!", "…")):
                cleaned += "."
        return cleaned
    if style == "opinion_question" and "?" not in cleaned:
        cleaned = cleaned.rstrip(".")
        if cleaned:
            cleaned += "?"
    return cleaned


def tick(*, dry_run: bool = False, max_comments: int | None = None, force: bool = False) -> dict[str, Any]:
    cfg = load_feed_config()
    if cfg.get("runner_mode", "daemon") != "daemon":
        return {"status": "skipped", "message": "runner_mode is not daemon"}

    daily_cap = int(cfg.get("daily_comment_cap", 100))
    quota = load_quota(QUOTA_PATH)
    if not can_post(quota, daily_cap):
        return {"status": "quota_exhausted", "posted_today": quota.get("posted", 0), "cap": daily_cap}

    windows: list[dict[str, Any]] = []
    if force:
        windows = [{"id": "force-demo", "window_seconds_remaining": 3600}]
    else:
        try:
            windows = discover_active_engagement_posts(cfg)
        except Exception as exc:  # noqa: BLE001 — surface setup errors as JSON
            return {"status": "blocked", "blocked_reason": "buffer_config", "message": str(exc)}
        if not windows:
            return {"status": "idle", "message": "No Buffer posts in engagement window (-15m to +90m)"}

    llm_cfg = cfg.get("llm", {})
    prereq_err = check_daemon_prereqs(llm_cfg)
    if prereq_err:
        return {"status": "blocked", "blocked_reason": "env", "message": prereq_err}

    llm_provider = resolve_llm_provider(llm_cfg)
    persona = load_persona()
    min_d = int(cfg.get("min_delay_seconds", 45))
    max_d = int(cfg.get("max_delay_seconds", 120))
    per_tick = max_comments or int(cfg.get("comments_per_tick", 3))
    per_tick = min(per_tick, remaining_today(quota, daily_cap))

    try:
        feed_items = discover_feed_items(cfg, feed_dir=FEED_DIR)
    except LinkedInRunnerError as exc:
        return {"status": "blocked", "blocked_reason": "linkedin_cli", "message": str(exc)}

    feed_items.sort(key=lambda item: rank_key(item, cfg))

    results: list[dict[str, Any]] = []
    commented_urns = {c.get("post_urn") for c in quota.get("comments", [])}
    posted_this_tick = 0

    for item in feed_items:
        if posted_this_tick >= per_tick:
            break
        urn = item.get("urn")
        if not urn or urn in commented_urns:
            continue
        if not item.get("share_urn"):
            results.append({"post_urn": urn, "skipped": "no_share_urn"})
            continue
        ok, reason, comment_style = post_matches_filters(item, cfg)
        if not ok:
            results.append({"post_urn": urn, "skipped": reason})
            continue
        item = {**item, "post_kind": reason}
        try:
            comment = draft_comment(
                item,
                persona=persona,
                rules=cfg,
                llm_cfg=llm_cfg,
                comment_style=comment_style,
            )
            comment = sanitize_comment(comment, int(cfg.get("max_comment_chars", 900)), comment_style)
        except LLMError as exc:
            results.append({"post_urn": urn, "error": f"llm:{exc}"})
            continue

        min_chars = int(cfg.get("min_comment_chars", 0))
        if min_chars and len(comment.strip()) < min_chars:
            results.append({"post_urn": urn, "skipped": "comment_too_short"})
            continue

        if dry_run:
            results.append(
                {
                    "post_urn": urn,
                    "dry_run": True,
                    "post_kind": reason,
                    "comment_style": comment_style,
                    "comment_preview": comment[:200],
                }
            )
            posted_this_tick += 1
            continue

        try:
            post_comment(str(urn), comment, share_urn=item.get("share_urn"))
        except LinkedInRunnerError as exc:
            results.append({"post_urn": urn, "error": f"post:{exc}"})
            continue

        entry = {
            "at": utcnow_iso(),
            "post_urn": urn,
            "author": item.get("author"),
            "comment_style": comment_style,
            "post_kind": reason,
            "buffer_windows": [w["id"] for w in windows],
            "comment_preview": comment[:160],
        }
        quota = record_post(QUOTA_PATH, quota, entry)
        results.append({"post_urn": urn, "posted": True})
        posted_this_tick += 1

        window = windows[0]
        delay = compute_delay_seconds(
            window_seconds=float(window.get("window_seconds_remaining") or 3600),
            comments_left_in_window=int(cfg.get("target_comments", 30)),
            daily_remaining=remaining_today(quota, daily_cap),
            min_delay=min_d,
            max_delay=max_d,
        )
        if posted_this_tick < per_tick:
            time.sleep(delay)

    return {
        "status": "ok",
        "llm_provider": llm_provider,
        "active_buffer_posts": len(windows),
        "posted_today": quota.get("posted", 0),
        "daily_cap": daily_cap,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Hands-off feed engage daemon tick")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Skip Buffer window check (demo/manual)")
    parser.add_argument("--max-comments", type=int, default=None)
    args = parser.parse_args()
    print(json.dumps(tick(dry_run=args.dry_run, max_comments=args.max_comments, force=args.force), indent=2))


if __name__ == "__main__":
    main()
