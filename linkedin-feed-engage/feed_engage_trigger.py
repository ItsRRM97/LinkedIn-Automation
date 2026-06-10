#!/usr/bin/env python3
"""Arm proactive feed engage when a Buffer LinkedIn post enters golden hour."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FEED_DIR = Path(__file__).resolve().parent
GH_DIR = FEED_DIR.parent / "linkedin-golden-hour"
STATE_DIR = FEED_DIR / "state"
CONFIG_PATH = FEED_DIR / "config.json"
REGISTRY_PATH = STATE_DIR / "trigger_registry.json"
ARMED_PATH = STATE_DIR / "feed_engage_armed.json"
AGENT_PROMPT_PATH = STATE_DIR / "agent_prompt.txt"
NOTIFY_SCRIPT = FEED_DIR.parent / "scripts" / "notify_feed_engage_armed.sh"

if str(GH_DIR) not in sys.path:
    sys.path.insert(0, str(GH_DIR))

from golden_hour import (  # noqa: E402
    discover_active_buffer_posts,
    load_config as load_golden_hour_config,
    utcnow_iso,
)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def load_feed_config() -> dict[str, Any]:
    with CONFIG_PATH.open() as f:
        return json.load(f)


def session_path() -> Path:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return STATE_DIR / f"session-{day}.json"


def agent_prompt_text(buffer_post_id: str, sent_at: str | None, title: str | None, feed_cfg: dict[str, Any]) -> str:
    mins = feed_cfg.get("session_minutes", 30)
    min_d = feed_cfg.get("min_delay_seconds", 45)
    max_d = feed_cfg.get("max_delay_seconds", 60)
    target = feed_cfg.get("target_comments", 30)
    mode = feed_cfg.get("target_mode", "thought_leaders")
    if mode == "thought_leaders":
        discovery = (
            "4. Default discovery: thought_leaders mode (SKILL §3a). "
            "Load thought_leaders.json → one comment per leader via /in/{slug}/recent-activity/all/. "
            "Skip company pages and success-story posts. Home feed Top is fallback only when a leader has no eligible post."
        )
    else:
        discovery = (
            "4. Home feed Sort by Top only; scroll main + Load more between picks (no content search)."
        )
    return f"""Publish-day feed engage — continuous auto mode (no approval, no batch stops).

Buffer post {buffer_post_id} is live (sent_at={sent_at or "unknown"}).
Your post: {title or "LinkedIn publish"}.

Run linkedin-feed-engage end-to-end in ONE uninterrupted pass:
1. Read ~/Projects/LinkedIn Automation/linkedin-feed-engage/SKILL.md and config.json (phase1_approval_limit=0, continuous_mode=true, target_mode={mode}).
2. Confirm LinkedIn logged in at https://www.linkedin.com/feed/ — if /login or /checkpoint, stop and notify user.
3. Load session file {session_path()} — run until posted >= target ({target}) or {mins} min elapsed. Do NOT stop early for review.
{discovery}
5. One top-level comment per distinct post; verified @ mention chip (SKILL §5).
6. Pace {min_d}–{max_d}s between comments; scroll during waits. No links in comments.

Do not ask for approval. Do not spawn subagents. Stop only on captcha, auth failure, or 4× same failure."""


def create_or_update_session(
    buffer_post_id: str,
    sent_at: str | None,
    title: str | None,
    feed_cfg: dict[str, Any],
) -> Path:
    path = session_path()
    existing = load_json(path)
    if existing.get("status") == "running" and existing.get("buffer_post_id") == buffer_post_id:
        return path

    data: dict[str, Any] = {
        "started_at": utcnow_iso(),
        "status": "running",
        "phase": "auto",
        "trigger": "buffer_sent",
        "buffer_post_id": buffer_post_id,
        "buffer_sent_at": sent_at,
        "publish_title": title,
        "target": feed_cfg.get("target_comments", 30),
        "posted": existing.get("posted", 0) if existing.get("buffer_post_id") == buffer_post_id else 0,
        "skipped": existing.get("skipped", 0) if existing.get("buffer_post_id") == buffer_post_id else 0,
        "approval_remaining": 0,
        "comments": existing.get("comments", []) if existing.get("buffer_post_id") == buffer_post_id else [],
    }
    save_json(path, data)
    return path


def arm_feed_engage(post: dict[str, Any], gh_cfg: dict[str, Any], feed_cfg: dict[str, Any], dry_run: bool = False) -> dict[str, Any]:
    buffer_post_id = post["id"]
    sent_at = post.get("sentAt")
    title = (post.get("text") or "")[:120].split("\n")[0].strip() or None

    session_file = create_or_update_session(buffer_post_id, sent_at, title, feed_cfg)
    prompt = agent_prompt_text(buffer_post_id, sent_at, title, feed_cfg)
    armed = {
        "armed_at": utcnow_iso(),
        "buffer_post_id": buffer_post_id,
        "buffer_sent_at": sent_at,
        "publish_title": title,
        "session_file": str(session_file),
        "agent_prompt_file": str(AGENT_PROMPT_PATH),
        "target_comments": feed_cfg.get("target_comments", 30),
        "auto_mode": True,
        "status": "armed",
    }

    if dry_run:
        return {"status": "dry_run", "armed": armed, "prompt_preview": prompt[:400]}

    AGENT_PROMPT_PATH.write_text(prompt + "\n")
    save_json(ARMED_PATH, armed)

    registry = load_json(REGISTRY_PATH)
    registry.setdefault("triggered", {})
    registry["triggered"][buffer_post_id] = {
        "armed_at": armed["armed_at"],
        "session_file": str(session_file),
    }
    registry["last_arm_at"] = utcnow_iso()
    save_json(REGISTRY_PATH, registry)

    if NOTIFY_SCRIPT.exists():
        subprocess.run([str(NOTIFY_SCRIPT), title or "LinkedIn post"], check=False)

    agent_script = FEED_DIR.parent / "scripts" / "trigger_feed_engage_agent.sh"
    if agent_script.exists():
        subprocess.run([str(agent_script)], check=False)

    return {"status": "armed", "buffer_post_id": buffer_post_id, "session_file": str(session_file)}


def tick(dry_run: bool = False) -> dict[str, Any]:
    gh_cfg = load_golden_hour_config()
    feed_cfg = load_feed_config()
    if not feed_cfg.get("auto_mode", True):
        return {"status": "disabled", "message": "auto_mode=false in feed engage config"}

    active = discover_active_buffer_posts(gh_cfg)
    if not active:
        return {"status": "idle", "message": "No Buffer LinkedIn posts in golden-hour window"}

    registry = load_json(REGISTRY_PATH)
    triggered = registry.get("triggered", {})
    results = []

    for post in active:
        bid = post["id"]
        if bid in triggered:
            results.append({"buffer_post_id": bid, "skipped": "already_armed"})
            continue
        results.append(arm_feed_engage(post, gh_cfg, feed_cfg, dry_run=dry_run))

    return {
        "status": "ok",
        "active_posts": len(active),
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Arm feed engage on Buffer go-live")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(json.dumps(tick(dry_run=args.dry_run), indent=2))


if __name__ == "__main__":
    main()
