#!/usr/bin/env python3
"""Golden hour auto-reply — per-campaign tick or Buffer-wide watch."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parent
LIB_DIR = SKILL_DIR.parent / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from notion_sync import collect_mappings, sync_notion_from_buffer_post  # noqa: E402
STATE_DIR = SKILL_DIR / "state"
CAMPAIGNS_DIR = SKILL_DIR / "campaigns"
CONFIG_PATH = SKILL_DIR / "config.json"
REGISTRY_PATH = STATE_DIR / "buffer_registry.json"

ACTOR_ID = "2P7nq91zOA"
ACTOR_URN = f"urn:li:person:{ACTOR_ID}"

COMMENT_SUBJECT_RE = re.compile(
    r"(?P<name>.+?)\s+(?:commented on your post|commented on this|replied to your comment)",
    re.I,
)
COMMENT_BODY_RE = re.compile(
    r"(?P<name>[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:commented|replied):\s*(?P<text>.+?)(?:\n|View|$)",
    re.I | re.S,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def utcnow_iso() -> str:
    return utcnow().isoformat()


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


def load_config() -> dict[str, Any]:
    cfg = load_json(CONFIG_PATH)
    if not cfg:
        raise RuntimeError(f"Missing config: {CONFIG_PATH}")
    return cfg


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def composio_execute(slug: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
    cmd = ["composio", "execute", slug]
    if args is not None:
        cmd.extend(["-d", json.dumps(args)])
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    raw = proc.stdout or proc.stderr
    idx = raw.find("{")
    if idx < 0:
        raise RuntimeError(f"Composio {slug} returned no JSON: {raw[:500]}")
    envelope = json.loads(raw[idx:])
    if envelope.get("storedInFile") and envelope.get("outputFilePath"):
        with open(envelope["outputFilePath"]) as f:
            payload = json.load(f)
        return payload.get("data", payload)
    if not envelope.get("successful", True):
        raise RuntimeError(envelope.get("error") or envelope)
    return envelope.get("data", envelope)


def buffer_graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    import urllib.request

    token = os.environ.get("BUFFER_MCP_TOKEN")
    if not token:
        raise RuntimeError("BUFFER_MCP_TOKEN not set (source ~/.zshrc)")
    req = urllib.request.Request(
        "https://api.buffer.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        body = json.load(resp)
    if body.get("errors"):
        raise RuntimeError(f"Buffer GraphQL error: {body['errors']}")
    return body.get("data", {})


def buffer_get_post(post_id: str) -> dict[str, Any]:
    data = buffer_graphql(
        """
        query GetPost($input: PostInput!) {
          post(input: $input) {
            id status sentAt externalLink text channelService
          }
        }
        """,
        {"input": {"id": post_id}},
    )
    post = data.get("post")
    if not post:
        raise RuntimeError(f"Buffer post not found: {post_id}")
    return post


def buffer_list_sent_posts(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    data = buffer_graphql(
        """
        query ListPosts($input: PostsInput!, $first: Int!) {
          posts(input: $input, first: $first) {
            edges { node { id status text sentAt channelService via externalLink } }
          }
        }
        """,
        {
            "input": {
                "organizationId": cfg["buffer_organization_id"],
                "filter": {
                    "channelIds": [cfg["linkedin_channel_id"]],
                    "status": ["sent"],
                },
                "sort": [{"field": "dueAt", "direction": "desc"}],
            },
            "first": int(cfg.get("list_posts_limit", 15)),
        },
    )
    return [e["node"] for e in data.get("posts", {}).get("edges", []) if e.get("node")]


def extract_share_urn(external_link: str | None) -> str | None:
    if not external_link:
        return None
    m = re.search(r"urn:li:share:\d+", external_link)
    return m.group(0) if m else None


def should_skip_post(post: dict[str, Any], cfg: dict[str, Any]) -> bool:
    if post.get("id") in cfg.get("skip_buffer_post_ids", []):
        return True
    text = (post.get("text") or "").lower()
    return any(n.lower() in text for n in cfg.get("skip_text_contains", []))


def caption_themes(caption: str, max_themes: int = 4) -> list[str]:
    lines = [ln.strip() for ln in caption.splitlines() if ln.strip()]
    themes: list[str] = []
    for ln in lines:
        if ln.startswith("#") or len(ln) < 25:
            continue
        if "?" in ln and themes:
            continue
        themes.append(ln[:220])
        if len(themes) >= max_themes:
            break
    return themes or ([lines[0][:220]] if lines else ["LinkedIn post insight"])


def extract_cta_question(caption: str) -> str | None:
    for ln in reversed([l.strip() for l in caption.splitlines() if l.strip()]):
        if "?" in ln and not ln.startswith("#"):
            return ln[:200]
    return None


def build_post_context_from_caption(caption: str) -> dict[str, Any]:
    lines = [ln.strip() for ln in caption.splitlines() if ln.strip() and not ln.startswith("#")]
    return {
        "title": (lines[0][:120] if lines else "LinkedIn post"),
        "caption_hook": caption[:400].strip(),
        "themes": caption_themes(caption),
        "cta_question": extract_cta_question(caption),
    }


def campaign_id_for_buffer_post(post_id: str) -> str:
    return f"buf-{post_id}"


def find_manual_campaign_for_post(post_id: str) -> dict[str, Any] | None:
    for path in CAMPAIGNS_DIR.glob("*.json"):
        data = load_json(path)
        if data.get("buffer_post_id") == post_id:
            return data
    return None


def ensure_campaign_for_post(post: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    manual = find_manual_campaign_for_post(post["id"])
    if manual:
        return manual
    cid = campaign_id_for_buffer_post(post["id"])
    path = CAMPAIGNS_DIR / f"{cid}.json"
    if path.exists():
        return load_json(path)
    campaign = {
        "campaign_id": cid,
        "buffer_post_id": post["id"],
        "auto_generated": True,
        "golden_hour_minutes": cfg.get("golden_hour_minutes", 90),
        "gmail_since_hours": cfg.get("gmail_since_hours", 3),
        "post_context": build_post_context_from_caption(post.get("text") or ""),
    }
    save_json(path, campaign)
    return campaign


def load_state(campaign_id: str) -> dict[str, Any]:
    data = load_json(STATE_DIR / f"{campaign_id}.json")
    data.setdefault("processed_message_ids", [])
    data.setdefault("posted_replies", [])
    return data


def save_state(campaign_id: str, state: dict[str, Any]) -> None:
    save_json(STATE_DIR / f"{campaign_id}.json", state)


def load_registry() -> dict[str, Any]:
    reg = load_json(REGISTRY_PATH)
    reg.setdefault("posts", {})
    return reg


def golden_hour_end(sent_at: datetime, minutes: int) -> datetime:
    return sent_at + timedelta(minutes=minutes)


def is_in_golden_hour(post: dict[str, Any], cfg: dict[str, Any], now: datetime | None = None) -> bool:
    now = now or utcnow()
    sent = parse_ts(post.get("sentAt"))
    if not sent:
        return False
    return sent <= now <= golden_hour_end(sent, int(cfg.get("golden_hour_minutes", 90)))


def discover_active_buffer_posts(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    now = utcnow()
    lookback = now - timedelta(hours=int(cfg.get("sent_lookback_hours", 24)))
    active = []
    for post in buffer_list_sent_posts(cfg):
        if post.get("channelService") != "linkedin" or should_skip_post(post, cfg):
            continue
        sent = parse_ts(post.get("sentAt"))
        if sent and sent >= lookback and is_in_golden_hour(post, cfg, now):
            active.append(post)
    active.sort(key=lambda p: parse_ts(p.get("sentAt")) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return active


def first_name(full_name: str) -> str:
    name = full_name.strip().split(",")[0].strip()
    return name.split()[0] if name else "there"


def pick_theme_insight(comment_text: str, post_context: dict[str, Any]) -> str:
    text = comment_text.lower()
    for key, insight in {
        "decision": "The best PMs treat the one-page decision doc as the real deliverable — not the slide deck.",
        "user": "Weekly user contact beats quarterly research — patterns show up in conversation.",
        "metric": "Defining success metrics before launch keeps teams honest about what 'done' means.",
        "meeting": "Protecting maker time is one of the highest-leverage things a PM can do.",
    }.items():
        if key in text:
            return insight
    themes = post_context.get("themes") or []
    if themes:
        return themes[0]
    hook = post_context.get("caption_hook") or post_context.get("title") or ""
    return hook[:240] if hook else "The best replies add a concrete insight, not just agreement."


def pick_follow_up(comment_text: str, post_context: dict[str, Any]) -> str:
    cta = post_context.get("cta_question")
    if cta and "?" in cta:
        return cta[:200]
    if "?" in comment_text:
        return "What nuance would you add from your own experience?"
    title = (post_context.get("title") or "this")[:60]
    return f"What part of {title} would you push back on or extend?"


def generate_reply(commenter: str, comment_text: str, post_context: dict[str, Any]) -> str:
    fname = first_name(commenter)
    snippet = comment_text.strip()
    if len(snippet) > 180:
        snippet = snippet[:177].rstrip() + "…"
    cite = f'your point about "{snippet}"' if snippet else "you jumping in here"
    return "\n\n".join([
        f"{fname} — appreciate {cite}.",
        pick_theme_insight(comment_text, post_context),
        pick_follow_up(comment_text, post_context),
    ])[:1240]


def normalize_email_record(record: dict[str, Any]) -> dict[str, str]:
    subject = str(record.get("subject") or record.get("Subject") or "")
    body = record.get("body")
    body_text = str(body.get("body") or body.get("text") or "") if isinstance(body, dict) else str(record.get("snippet") or record.get("body") or "")
    return {
        "message_id": str(record.get("messageId") or record.get("id") or ""),
        "subject": subject,
        "body": body_text,
        "snippet": str(record.get("snippet") or body_text[:240]),
    }


def find_messages(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        return payload
    if isinstance(payload, dict):
        for key in ("messages", "emails", "data", "items"):
            if isinstance(payload.get(key), list):
                return payload[key]
        for value in payload.values():
            found = find_messages(value)
            if found:
                return found
    return []


def parse_comment_notification(email: dict[str, str]) -> dict[str, str] | None:
    hay = f"{email['subject']}\n{email['body']}\n{email['snippet']}"
    if not any(x in hay.lower() for x in ("commented", "replied to your comment", "comment on your post")):
        return None
    name, text = "", email["snippet"] or email["body"]
    m = COMMENT_SUBJECT_RE.search(email["subject"])
    if m:
        name = m.group("name").strip()
    m = COMMENT_BODY_RE.search(hay)
    if m:
        name = name or m.group("name").strip()
        text = m.group("text").strip()
    if not name:
        m = re.search(r"^(.+?)\s+commented on your post:?\s*(.*)$", email["subject"], re.I)
        if m:
            name, text = m.group(1).strip(), (m.group(2) or text).strip()
    if not name:
        return None
    return {
        "commenter": name,
        "comment_text": text[:500] or "thanks for engaging",
        "message_id": email.get("message_id") or email.get("subject", ""),
        "email_hay": hay[:800],
    }


def fetch_linkedin_comment_emails(since_hours: int = 2) -> list[dict[str, str]]:
    payload = composio_execute("GMAIL_FETCH_EMAILS", {
        "query": f"from:linkedin.com (commented OR comment OR replied) newer_than:{since_hours}h",
        "max_results": 25,
        "verbose": True,
    })
    return [normalize_email_record(r) for r in find_messages(payload) if isinstance(r, dict)]


def post_reply(share_urn: str, reply_text: str) -> dict[str, Any]:
    payload = {"actor": ACTOR_URN, "object": share_urn, "target_urn": share_urn, "message": {"text": reply_text}}
    try:
        return composio_execute("LINKEDIN_CREATE_COMMENT_ON_POST", payload)
    except RuntimeError as exc:
        if "not found" not in str(exc).lower() and "403" not in str(exc):
            raise
        numeric = re.search(r"\d+", share_urn)
        if not numeric:
            raise
        alt = f"urn:li:ugcPost:{numeric.group(0)}"
        payload["object"] = alt
        payload["target_urn"] = alt
        return composio_execute("LINKEDIN_CREATE_COMMENT_ON_POST", payload)


def sync_publish_state(campaign: dict[str, Any], state: dict[str, Any], dry_run: bool = False) -> dict[str, Any] | None:
    post_id = campaign.get("buffer_post_id")
    if not post_id:
        return None
    post = buffer_get_post(post_id)
    state.update({
        "buffer_status": post.get("status"),
        "buffer_sent_at": post.get("sentAt"),
        "caption": post.get("text"),
    })
    urn = extract_share_urn(post.get("externalLink"))
    if urn:
        state["share_urn"] = urn
        state["external_link"] = post.get("externalLink")
    page_id = campaign.get("notion_page_id")
    if not page_id:
        return None
    try:
        return sync_notion_from_buffer_post(post, notion_page_id=page_id, state=state, dry_run=dry_run)
    except RuntimeError as exc:
        if "NOTION_TOKEN" in str(exc):
            print(f"[watch] Notion sync skipped (token not set): {exc}", file=__import__("sys").stderr)
            return None
        raise


def match_comment_to_campaign(comment: dict[str, str], active: list[tuple]) -> tuple | None:
    if len(active) == 1:
        return active[0]
    hay = comment.get("email_hay", "").lower()
    best, best_score = None, 0
    for post, campaign, state in active:
        caption = (state.get("caption") or post.get("text") or "").lower()
        score = sum(1 for t in re.findall(r"[a-z]{5,}", caption[:200]) if t in hay)
        if score > best_score:
            best_score, best = score, (post, campaign, state)
    return best or active[0]


def watch(dry_run: bool = False) -> dict[str, Any]:
    cfg = load_config()
    registry = load_registry()
    registry.setdefault("posts", {})
    active_triples = []

    for post in discover_active_buffer_posts(cfg):
        campaign = ensure_campaign_for_post(post, cfg)
        cid = campaign.get("campaign_id") or campaign_id_for_buffer_post(post["id"])
        state = load_state(cid)
        notion_sync = sync_publish_state(campaign, state, dry_run=dry_run)
        save_state(cid, state)
        sent = parse_ts(post.get("sentAt"))
        end = golden_hour_end(sent, int(cfg.get("golden_hour_minutes", 90))) if sent else None
        registry["posts"][post["id"]] = {
            "campaign_id": cid,
            "sent_at": post.get("sentAt"),
            "golden_hour_ends_at": end.isoformat() if end else None,
            "share_urn": state.get("share_urn"),
            "title": (campaign.get("post_context") or {}).get("title"),
        }
        active_triples.append((post, campaign, state))

    registry["last_watch_at"] = utcnow_iso()
    save_json(REGISTRY_PATH, registry)

    if not active_triples:
        return {"status": "idle", "active_posts": 0, "message": "No Buffer posts in golden-hour window"}

    comments = [c for e in fetch_linkedin_comment_emails(int(cfg.get("gmail_since_hours", 3)))
                if (c := parse_comment_notification(e))]
    results = []

    for comment in comments:
        match = match_comment_to_campaign(comment, active_triples)
        if not match:
            continue
        post, campaign, state = match
        cid = campaign.get("campaign_id") or campaign_id_for_buffer_post(post["id"])
        mid = comment.get("message_id", "")
        if not mid or mid in set(state.get("processed_message_ids", [])):
            continue
        share_urn = state.get("share_urn")
        if not share_urn:
            results.append({"campaign": cid, "skipped": "no share_urn"})
            continue
        reply = generate_reply(comment["commenter"], comment["comment_text"], campaign.get("post_context", {}))
        entry = {"campaign": cid, "buffer_post_id": post["id"], "commenter": comment["commenter"], "reply": reply, "posted": False}
        if dry_run:
            entry["dry_run"] = True
        else:
            try:
                entry["response"] = post_reply(share_urn, reply)
                entry["posted"] = True
                state.setdefault("posted_replies", []).append({"at": utcnow_iso(), "commenter": comment["commenter"], "reply": reply, "message_id": mid})
                state.setdefault("processed_message_ids", []).append(mid)
            except RuntimeError as exc:
                entry["error"] = str(exc)
                entry["needs_browser_fallback"] = True
                state.setdefault("pending_replies", []).append({"at": utcnow_iso(), "commenter": comment["commenter"], "reply": reply, "message_id": mid, "error": str(exc)})
            save_state(cid, state)
        results.append(entry)

    return {
        "status": "watching",
        "active_posts": len(active_triples),
        "posts": [{"buffer_post_id": p["id"], "campaign": c.get("campaign_id"), "title": (c.get("post_context") or {}).get("title"), "share_urn": load_state(c.get("campaign_id") or campaign_id_for_buffer_post(p["id"])).get("share_urn")} for p, c, _ in active_triples],
        "comment_replies": results,
    }


def tick(campaign_id: str, dry_run: bool = False) -> dict[str, Any]:
    path = CAMPAIGNS_DIR / f"{campaign_id}.json"
    if not path.exists():
        raise RuntimeError(f"Unknown campaign: {campaign_id}")
    campaign = load_json(path)
    state = load_state(campaign_id)
    state["last_tick_at"] = utcnow_iso()
    notion_sync = sync_publish_state(campaign, state, dry_run=dry_run)
    share_urn = state.get("share_urn")
    if not share_urn:
        save_state(campaign_id, state)
        return {"campaign": campaign_id, "status": "waiting_for_publish", "buffer_status": state.get("buffer_status")}
    processed = set(state.get("processed_message_ids", []))
    results = []
    for email in fetch_linkedin_comment_emails(int(campaign.get("gmail_since_hours", 3))):
        parsed = parse_comment_notification(email)
        if not parsed:
            continue
        mid = parsed.get("message_id", "")
        if not mid or mid in processed:
            continue
        reply = generate_reply(parsed["commenter"], parsed["comment_text"], campaign.get("post_context", {}))
        entry = {"commenter": parsed["commenter"], "reply": reply, "posted": False}
        if not dry_run:
            try:
                entry["response"] = post_reply(share_urn, reply)
                entry["posted"] = True
                processed.add(mid)
                state.setdefault("posted_replies", []).append({"at": utcnow_iso(), "commenter": parsed["commenter"], "reply": reply, "message_id": mid})
            except RuntimeError as exc:
                entry["error"] = str(exc)
                state.setdefault("pending_replies", []).append({"at": utcnow_iso(), "commenter": parsed["commenter"], "reply": reply, "message_id": mid, "error": str(exc)})
        results.append(entry)
    state["processed_message_ids"] = sorted(processed)
    save_state(campaign_id, state)
    return {"campaign": campaign_id, "status": "live", "share_urn": share_urn, "notion_sync": notion_sync, "replies": results}


def post_manual(campaign_id: str, commenter: str, comment_text: str, dry_run: bool = False) -> dict[str, Any]:
    campaign = load_json(CAMPAIGNS_DIR / f"{campaign_id}.json")
    state = load_state(campaign_id)
    sync_publish_state(campaign, state)
    share_urn = state.get("share_urn")
    if not share_urn:
        raise RuntimeError("Post URN missing")
    reply = generate_reply(commenter, comment_text, campaign.get("post_context", {}))
    if dry_run:
        return {"share_urn": share_urn, "reply": reply, "dry_run": True}
    resp = post_reply(share_urn, reply)
    state.setdefault("posted_replies", []).append({"at": utcnow_iso(), "commenter": commenter, "reply": reply, "manual": True})
    save_state(campaign_id, state)
    return {"share_urn": share_urn, "reply": reply, "posted": True, "response": resp}


def sync_notion(dry_run: bool = False) -> dict[str, Any]:
    """For each tracked Buffer post, call get_post; when status=sent, update Notion."""
    mappings = collect_mappings()
    results: list[dict[str, Any]] = []
    for post_id, page_id in sorted(mappings.items()):
        post = buffer_get_post(post_id)
        if not post:
            results.append({"buffer_post_id": post_id, "notion_page_id": page_id, "skipped": "buffer_post_not_found"})
            continue
        cid = campaign_id_for_buffer_post(post_id)
        manual = find_manual_campaign_for_post(post_id)
        if manual:
            cid = manual.get("campaign_id") or cid
        state = load_state(cid)
        entry = sync_notion_from_buffer_post(post, notion_page_id=page_id, state=state, dry_run=dry_run)
        if entry:
            results.append(entry)
            if not dry_run:
                save_state(cid, state)
        elif post.get("status") != "sent":
            results.append({"buffer_post_id": post_id, "notion_page_id": page_id, "skipped": post.get("status")})
    return {"mappings": len(mappings), "synced": len([r for r in results if r.get("synced_at") and not r.get("dry_run")]), "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(description="LinkedIn golden hour auto-replies")
    sub = parser.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("watch", help="Watch all Buffer LinkedIn posts in golden-hour window")
    w.add_argument("--dry-run", action="store_true")
    t = sub.add_parser("tick", help="Single campaign tick")
    t.add_argument("--campaign", required=True)
    t.add_argument("--dry-run", action="store_true")
    r = sub.add_parser("reply", help="Manual reply for one campaign")
    r.add_argument("--campaign", required=True)
    r.add_argument("--commenter", required=True)
    r.add_argument("--comment", required=True)
    r.add_argument("--dry-run", action="store_true")
    s = sub.add_parser("sync-notion", help="Update Notion from Buffer get_post when status=sent")
    s.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.cmd == "watch":
        out = watch(dry_run=args.dry_run)
    elif args.cmd == "tick":
        out = tick(args.campaign, dry_run=args.dry_run)
    elif args.cmd == "sync-notion":
        out = sync_notion(dry_run=args.dry_run)
    else:
        out = post_manual(args.campaign, args.commenter, args.comment, dry_run=args.dry_run)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
