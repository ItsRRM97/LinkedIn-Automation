#!/usr/bin/env python3
"""Create LinkedIn Automation project summary page in Notion (fallback when MCP unavailable)."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

PARENT_PAGE_ID = "1d63dffe-a139-8083-adde-e5fa98f11c2a"
TITLE = "LinkedIn Automation — Project Summary (Jun 2026)"
ICON = "🔧"

CONTENT = """## Overview
End-to-end publish-day engine: content planned in Notion, scheduled through Buffer, and when a post goes live the system automatically syncs status, replies to comments on your post, and arms proactive engagement on others' posts.

## Architecture
Notion Content Library → Buffer schedule → Post goes live → three parallel automations:
1. Notion sync (Buffer sent → Posted)
2. Golden hour replies (Gmail + Composio)
3. Feed engage (CLI daemon: linkedincli read + Groq + Composio post)

## Three Core Modules

### 1. Content Posting (linkedin-content-posting/)
- Draft, schedule, publish from Notion Content Library
- Integrations: Notion MCP, Buffer MCP, Canva MCP, Composio
- Content Library cleanup reconciles Buffer sent → Notion Posted every run
- Automated formats: text, single image, PDF carousel. Manual: polls, video, live

### 2. Golden Hour (linkedin-golden-hour/)
- Auto-replies on YOUR posts during 60-90 min after publish (no approval)
- Gmail detects LinkedIn comment emails → Depth Score replies (name, cite, value, question) → Composio LinkedIn API
- Campaigns: CON-138, CON-158, CON-159 + generic auto-campaigns for any Buffer post

### 3. Feed Engage (linkedin-feed-engage/)
- Proactive comments on OTHERS' posts via **daemon** (default): linkedincli feed read, Groq drafts, Composio `LINKEDIN_CREATE_COMMENT_ON_POST`
- Legacy: Cursor browser MCP when `runner_mode=browser`
- 50-person PM thought-leader roster, continuous mode, 30 comments/session, 45-60s delays
- Skips promotion posts, company pages, engagement bait, posts >12h old
- Multiple 30/30 sessions completed in production

## Orchestration
- `scripts/publish_day_watch.sh` — every 10 min for 90 min on publish days
- `lib/notion_sync.py` — shared Notion ↔ Buffer reconciliation
- launchd Tue-Thu 10:00 local via `install_publish_day_schedule.sh`
- Each tick: cleanup-content-library → golden_hour watch → feed_engage_trigger

## Cursor Agent Skills
- linkedin-content-posting — schedule/publish, cleanup
- linkedin-golden-hour — comment auto-replies
- linkedin-feed-engage — proactive feed comments

## Automated vs Manual
**Automated:** Buffer scheduling, Notion sync, golden-hour replies, 30 feed comments/session, Tue-Thu launchd

**Manual:** polls, native video, live; Mac awake + Cursor open for feed engage

## Stack
macOS, Python 3.10+, Cursor with Notion/Buffer/browser MCPs, Composio CLI (LinkedIn + Gmail)

**Env:** `BUFFER_MCP_TOKEN`, `NOTION_TOKEN`, `NOTION_CONTENT_LIBRARY_DB`, `LINKEDIN_ACTOR_ID`

## Repo
`~/Projects/LinkedIn Automation`
"""


def notion_token() -> str:
    token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not token:
        raise RuntimeError("NOTION_TOKEN not set (add Notion integration secret to ~/.zshrc)")
    return token


def notion_request(method: str, path: str, body: dict | None = None) -> dict:
    url = f"https://api.notion.com/v1/{path.lstrip('/')}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {notion_token()}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Notion API {method} {path}: {exc.code} {detail[:800]}") from exc


def rich_text(text: str) -> list[dict]:
    return [{"type": "text", "text": {"content": text}}]


def paragraph_block(text: str) -> dict:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": rich_text(text)}}


def heading_block(level: int, text: str) -> dict:
    key = f"heading_{level}"
    return {"object": "block", "type": key, key: {"rich_text": rich_text(text), "is_toggleable": False}}


def bulleted_item(text: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": rich_text(text)},
    }


def parse_markdown_to_blocks(md: str) -> list[dict]:
    blocks: list[dict] = []
    lines = md.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("### "):
            blocks.append(heading_block(3, line[4:]))
        elif line.startswith("## "):
            blocks.append(heading_block(2, line[3:]))
        elif line.startswith("- "):
            blocks.append(bulleted_item(line[2:]))
        elif line.startswith("**") and line.endswith("**"):
            blocks.append(paragraph_block(line))
        else:
            blocks.append(paragraph_block(line))
        i += 1
    return blocks


def main() -> int:
    children = parse_markdown_to_blocks(CONTENT)
    body = {
        "parent": {"type": "page_id", "page_id": PARENT_PAGE_ID.replace("-", "")},
        "icon": {"type": "emoji", "emoji": ICON},
        "properties": {
            "title": {"title": [{"type": "text", "text": {"content": TITLE}}]},
        },
        "children": children[:100],
    }
    result = notion_request("POST", "pages", body)
    page_id = result.get("id", "")
    url = result.get("url", "")
    print(json.dumps({"id": page_id, "url": url}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
