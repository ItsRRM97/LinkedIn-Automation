"""Notion Content Library updates from Buffer post responses (status=sent)."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTENT_LIBRARY_DB = "753369dc15fb4b3c82dd9c88cb753c3c"
CAMPAIGNS_DIR = Path(__file__).resolve().parent.parent / "linkedin-golden-hour" / "campaigns"
BUFFER_POST_ID_RE = re.compile(r"(?:Buffer post(?: ID)?[:：]?\s*`?)([0-9a-f]{24})", re.I)
SHARE_URN_RE = re.compile(r"urn:li:share:\d+")


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def notion_token() -> str:
    token = os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY")
    if not token:
        raise RuntimeError("NOTION_TOKEN not set (add Notion integration secret to ~/.zshrc)")
    return token


def notion_request(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
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
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Notion API {method} {path}: {exc.code} {detail[:500]}") from exc


def extract_share_urn(external_link: str | None) -> str | None:
    if not external_link:
        return None
    m = SHARE_URN_RE.search(external_link)
    return m.group(0) if m else None


def extract_buffer_post_id(page_text: str) -> str | None:
    preferred: str | None = None
    fallback: str | None = None
    for line in page_text.splitlines():
        if re.search(r"cancelled|deleted|superseded", line, re.I):
            continue
        m = re.search(r"Buffer post ID[:：]?\s*`?([0-9a-f]{24})", line, re.I)
        if m:
            preferred = m.group(1)
            continue
        for post_id in BUFFER_POST_ID_RE.findall(line):
            fallback = post_id
    return preferred or fallback


def fetch_page_text(page_id: str) -> str:
    chunks: list[str] = []
    cursor: str | None = None
    while True:
        path = f"blocks/{page_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        data = notion_request("GET", path)
        for block in data.get("results", []):
            btype = block.get("type")
            if not btype or btype not in block:
                continue
            rich = block[btype].get("rich_text") or []
            chunks.append("".join(part.get("plain_text", "") for part in rich))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return "\n".join(chunks)


def mappings_from_campaigns() -> dict[str, str]:
    out: dict[str, str] = {}
    if not CAMPAIGNS_DIR.exists():
        return out
    for path in CAMPAIGNS_DIR.glob("*.json"):
        data = json.loads(path.read_text())
        page_id = data.get("notion_page_id")
        post_id = data.get("buffer_post_id")
        if page_id and post_id:
            out[post_id] = page_id
    return out


def mappings_from_notion_pipeline_statuses(statuses: tuple[str, ...] = ("Scheduled", "Ready")) -> dict[str, str]:
    """Map Buffer post IDs from Content Library rows still in the active pipeline."""
    out: dict[str, str] = {}
    for status in statuses:
        cursor: str | None = None
        while True:
            body: dict[str, Any] = {
                "filter": {"property": "Status", "status": {"equals": status}},
                "page_size": 100,
            }
            if cursor:
                body["start_cursor"] = cursor
            data = notion_request("POST", f"databases/{CONTENT_LIBRARY_DB}/query", body)
            for page in data.get("results", []):
                page_id = page["id"]
                post_id = extract_buffer_post_id(fetch_page_text(page_id))
                if post_id:
                    out[post_id] = page_id
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")
    return out


def mappings_from_notion_scheduled() -> dict[str, str]:
    return mappings_from_notion_pipeline_statuses(("Scheduled",))


def fetch_page_status(page_id: str) -> str | None:
    data = notion_request("GET", f"pages/{page_id}")
    prop = (data.get("properties") or {}).get("Status") or {}
    if prop.get("type") == "status":
        return (prop.get("status") or {}).get("name")
    return None


def page_has_publish_block(page_text: str) -> bool:
    return "Published live" in page_text or bool(SHARE_URN_RE.search(page_text))


def collect_mappings() -> dict[str, str]:
    merged = mappings_from_campaigns()
    merged.update(mappings_from_notion_pipeline_statuses(("Scheduled", "Ready")))
    return merged


def rich_text(content: str) -> list[dict[str, Any]]:
    return [{"type": "text", "text": {"content": content}}]


def append_publish_block(page_id: str, post: dict[str, Any], share_urn: str | None) -> None:
    sent_at = post.get("sentAt") or "unknown"
    lines = [
        f"Published live ({sent_at[:10] if sent_at != 'unknown' else 'unknown'})",
        f"Buffer post ID: {post.get('id', post.get('postId', ''))}",
    ]
    if share_urn:
        lines.append(f"Share URN: {share_urn}")
    link = post.get("externalLink")
    if link:
        lines.append(f"LinkedIn: {link}")
    lines.append(f"Synced at: {utcnow_iso()}")

    children = [{"object": "block", "type": "heading_2", "heading_2": {"rich_text": rich_text(lines[0])}}]
    for line in lines[1:]:
        children.append({"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": rich_text(line)}})
    notion_request("PATCH", f"blocks/{page_id}/children", {"children": children})


def update_page_posted(page_id: str, sent_at: str | None) -> None:
    props: dict[str, Any] = {"Status": {"status": {"name": "Posted"}}}
    if sent_at:
        props["Posting on"] = {"date": {"start": sent_at[:10]}}
    notion_request("PATCH", f"pages/{page_id}", {"properties": props})


def sync_notion_from_buffer_post(
    post: dict[str, Any],
    *,
    notion_page_id: str,
    state: dict[str, Any] | None = None,
    dry_run: bool = False,
    force: bool = False,
) -> dict[str, Any] | None:
    """Update Notion when Buffer response shows status=sent. Idempotent via state + Notion status."""
    if state and state.get("notion_synced") and not force:
        notion_status = fetch_page_status(notion_page_id)
        if notion_status == "Posted":
            return None

    status = post.get("status")
    if status != "sent":
        return None

    notion_status = fetch_page_status(notion_page_id)
    page_text = fetch_page_text(notion_page_id)
    already_posted = notion_status == "Posted"

    share_urn = extract_share_urn(post.get("externalLink"))
    entry: dict[str, Any] = {
        "notion_page_id": notion_page_id,
        "buffer_post_id": post.get("id"),
        "share_urn": share_urn,
        "external_link": post.get("externalLink"),
        "sent_at": post.get("sentAt"),
        "synced_at": utcnow_iso(),
        "notion_status_before": notion_status,
    }
    if already_posted:
        entry["action"] = "already_posted"
        if state is not None:
            state["notion_synced"] = True
            state["notion_sync_at"] = entry["synced_at"]
        return entry

    if dry_run:
        entry["dry_run"] = True
        entry["action"] = "would_mark_posted"
        return entry

    update_page_posted(notion_page_id, post.get("sentAt"))
    if not page_has_publish_block(page_text):
        append_publish_block(notion_page_id, post, share_urn)
    else:
        entry["publish_block_skipped"] = True
    entry["action"] = "marked_posted"
    if state is not None:
        state["notion_synced"] = True
        state["notion_sync_at"] = entry["synced_at"]
    return entry


def cleanup_content_library(
    buffer_get_post: Any,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Reconcile Content Library rows with Buffer: any tracked post with status=sent
    → Notion Status Posted + publish block (idempotent).
    """
    mappings = collect_mappings()
    results: list[dict[str, Any]] = []
    for post_id, page_id in sorted(mappings.items()):
        try:
            post = buffer_get_post(post_id)
        except Exception as exc:  # noqa: BLE001
            results.append(
                {
                    "buffer_post_id": post_id,
                    "notion_page_id": page_id,
                    "error": str(exc)[:300],
                }
            )
            continue
        if not post:
            results.append(
                {
                    "buffer_post_id": post_id,
                    "notion_page_id": page_id,
                    "skipped": "buffer_post_not_found",
                }
            )
            continue
        entry = sync_notion_from_buffer_post(
            post,
            notion_page_id=page_id,
            state=None,
            dry_run=dry_run,
            force=True,
        )
        if entry:
            results.append(entry)
        elif post.get("status") != "sent":
            results.append(
                {
                    "buffer_post_id": post_id,
                    "notion_page_id": page_id,
                    "skipped": post.get("status"),
                }
            )
    marked = [r for r in results if r.get("action") == "marked_posted"]
    already = [r for r in results if r.get("action") == "already_posted"]
    would = [r for r in results if r.get("action") == "would_mark_posted"]
    return {
        "mappings_checked": len(mappings),
        "marked_posted": len(marked),
        "already_posted": len(already),
        "would_mark_posted": len(would),
        "results": results,
    }
