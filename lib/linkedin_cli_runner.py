"""LinkedIn feed fetch + comment via @bcharleson/linkedincli (Voyager API)."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from typing import Any

from feed_post_classify import parse_post_age_hours


class LinkedInRunnerError(RuntimeError):
    pass


def _linkedin_cmd() -> list[str]:
    if shutil.which("linkedin"):
        return ["linkedin"]
    npx = shutil.which("npx")
    if not npx:
        raise LinkedInRunnerError("Install linkedincli: npm install -g @bcharleson/linkedincli")
    return [npx, "-y", "@bcharleson/linkedincli"]


def _strip_cookie(value: str) -> str:
    cleaned = value.strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] == '"':
        return cleaned[1:-1]
    return cleaned


def _env() -> dict[str, str]:
    env = os.environ.copy()
    li_at = _strip_cookie(env.get("LINKEDIN_LI_AT") or env.get("LI_AT") or "")
    jsession = _strip_cookie(env.get("LINKEDIN_JSESSIONID") or env.get("JSESSIONID") or "")
    if not li_at or not jsession:
        raise LinkedInRunnerError(
            "Set LINKEDIN_LI_AT and LINKEDIN_JSESSIONID in ~/.zshrc "
            "(run scripts/import_linkedin_cookies.sh)"
        )
    env["LINKEDIN_LI_AT"] = li_at
    env["LINKEDIN_JSESSIONID"] = jsession
    return env


def _run(args: list[str]) -> Any:
    cmd = _linkedin_cmd() + args
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, env=_env())
    raw = (proc.stdout or proc.stderr or "").strip()
    if proc.returncode != 0:
        raise LinkedInRunnerError(raw[:800] or f"linkedincli failed: {args}")
    idx = raw.find("{")
    if idx < 0:
        idx = raw.find("[")
    if idx < 0:
        raise LinkedInRunnerError(f"No JSON in linkedincli output: {raw[:400]}")
    return json.loads(raw[idx:])


def _text_view(obj: Any) -> str:
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return str(obj.get("text") or "")
    return ""


def _activity_id(entity_urn: str) -> str | None:
    match = re.search(r"activity:(\d+)", entity_urn or "")
    return match.group(1) if match else None


def _included_index(included: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for block in included:
        for key in ("entityUrn", "$id", "urn"):
            urn = block.get(key)
            if isinstance(urn, str) and urn:
                index[urn] = block
    return index


def _resolve_ref(ref: Any, index: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    if isinstance(ref, dict):
        return ref
    if isinstance(ref, str) and ref in index:
        return index[ref]
    return None


def parse_voyager_feed(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Turn linkedincli feed JSON into normalized post dicts."""
    included = data.get("included") or []
    index = _included_index(included)
    items: list[dict[str, Any]] = []

    for block in included:
        if block.get("$type") != "com.linkedin.voyager.feed.render.UpdateV2":
            continue

        entity_urn = block.get("entityUrn") or block.get("dashEntityUrn") or ""
        activity_id = _activity_id(entity_urn)
        if not activity_id:
            continue

        actor = block.get("actor") or {}
        actor_urn = str(actor.get("urn") or "")
        author_name = _text_view(actor.get("name"))
        headline = _text_view(actor.get("description"))
        sub_desc = _text_view(actor.get("subDescription"))
        commentary = block.get("commentary") or {}
        text = _text_view(commentary.get("text"))

        post_age_hours = parse_post_age_hours(sub_desc)

        social = _resolve_ref(block.get("*socialDetail") or block.get("socialDetail"), index)
        reactions = None
        comments_count = None
        if social:
            counts = social.get("totalSocialActivityCounts") or {}
            if isinstance(counts, dict):
                reactions = counts.get("numLikes")
                comments_count = counts.get("numComments")

        meta = block.get("updateMetadata") or {}
        share_urn = meta.get("shareUrn") if isinstance(meta, dict) else None

        items.append(
            {
                "activity_id": activity_id,
                "urn": f"urn:li:activity:{activity_id}",
                "share_urn": share_urn,
                "entityUrn": entity_urn,
                "text": text,
                "author": author_name,
                "author_headline": headline,
                "reactions": reactions,
                "comments_count": comments_count,
                "actor_urn": actor_urn,
                "is_company": "company" in actor_urn,
                "is_group": "group" in actor_urn,
                "is_promoted": "promoted" in sub_desc.lower(),
                "post_age_hours": post_age_hours,
                "posted_ago": sub_desc.strip(),
                "raw": block,
            }
        )

    return items


def fetch_user_feed(profile_id: str, count: int = 5) -> list[dict[str, Any]]:
    data = _run(["feed", "user", profile_id, "--limit", str(count)])
    if isinstance(data, dict):
        parsed = parse_voyager_feed(data)
        if parsed:
            return parsed
        for key in ("items", "feed", "data", "elements"):
            val = data.get(key)
            if isinstance(val, list) and val and isinstance(val[0], dict):
                return val
    if isinstance(data, list):
        return data
    raise LinkedInRunnerError(f"Unexpected user feed shape for {profile_id}: {json.dumps(data)[:400]}")


def fetch_feed(count: int = 30, *, retries: int = 3) -> list[dict[str, Any]]:
    last_err: LinkedInRunnerError | None = None
    for attempt in range(retries):
        try:
            data = _run(["feed", "view", "--limit", str(count)])
            if isinstance(data, dict):
                parsed = parse_voyager_feed(data)
                if parsed:
                    return parsed
                for key in ("items", "feed", "data", "elements"):
                    val = data.get(key)
                    if isinstance(val, list) and val and isinstance(val[0], dict):
                        return val
            if isinstance(data, list):
                return data
            raise LinkedInRunnerError(f"Unexpected feed shape: {json.dumps(data)[:400]}")
        except LinkedInRunnerError as exc:
            last_err = exc
            if attempt < retries - 1:
                time.sleep(2**attempt)
    raise last_err or LinkedInRunnerError("fetch_feed failed")


def post_comment(post_urn: str, text: str, *, share_urn: str | None = None) -> dict[str, Any]:
    if share_urn:
        from composio_linkedin import ComposioLinkedInError, create_comment

        try:
            return create_comment(share_urn, text)
        except ComposioLinkedInError as exc:
            raise LinkedInRunnerError(str(exc)) from exc

    urn = post_urn.split(":")[-1] if ":" in post_urn else post_urn
    return _run(["engage", "comment", urn, "--text", text])


def normalize_feed_item(item: dict[str, Any]) -> dict[str, Any]:
    if item.get("activity_id"):
        return item

    text = (
        item.get("commentary")
        or item.get("text")
        or item.get("message")
        or item.get("content")
        or ""
    )
    if isinstance(text, dict):
        text = _text_view(text)

    author = item.get("author") or item.get("actor") or {}
    if isinstance(author, dict):
        author_name = author.get("name") or author.get("firstName") or author.get("publicIdentifier")
        if isinstance(author_name, dict):
            author_name = _text_view(author_name)
        headline = author.get("headline") or author.get("occupation")
        if isinstance(headline, dict):
            headline = _text_view(headline)
    else:
        author_name = str(author) if author else None
        headline = None

    urn = (
        item.get("activity_id")
        or item.get("activityUrn")
        or item.get("urn")
        or item.get("entityUrn")
        or item.get("updateUrn")
        or item.get("id")
    )
    if isinstance(urn, str) and "activity:" in urn:
        urn = _activity_id(urn) or urn

    return {
        "urn": f"urn:li:activity:{urn}" if urn and not str(urn).startswith("urn:") else urn,
        "activity_id": str(urn).split(":")[-1] if urn else None,
        "text": text,
        "author": author_name,
        "author_headline": headline,
        "reactions": item.get("numLikes") or item.get("reactions"),
        "comments_count": item.get("numComments") or item.get("comments"),
        "raw": item,
    }
