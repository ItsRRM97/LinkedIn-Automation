"""Classify feed posts for comment style and filter eligibility."""

from __future__ import annotations

import re
from typing import Any

COMMENT_STYLE_OPINION = "opinion_question"
COMMENT_STYLE_CAREER = "career_ack"

_CAREER_UPDATE_RES = [
    re.compile(p, re.I)
    for p in (
        r"\bexcited to share\b.*\b(role|position|promot|join)",
        r"\bhappy to share\b.*\b(role|position|join|promot)",
        r"\bthrilled to share\b.*\b(role|position|join|promot)",
        r"\bstarting a new (role|position|chapter)\b",
        r"\bstepping into\b.*\b(role|position)\b",
        r"\bpromoted to\b",
        r"\bnew role at\b",
        r"\bjoining \b",
        r"\bi joined\b",
        r"\bjoined .+ to (work|lead|build)\b",
        r"\blast working day\b",
        r"\bnew chapter\b",
        r"\btaking on a new\b",
        r"\bjoined (the team|as)\b",
        r"\bstarted a new position\b",
        r"\bforward graduate\b",
        r"\bmckinsey forward\b",
        r"\bnew position as\b",
    )
]

_JOB_POSTING_RES = [
    re.compile(p, re.I)
    for p in (
        r"\bwe'?re hiring\b",
        r"\bnow hiring\b",
        r"\bjob opening\b",
        r"\bopen role\b",
        r"\bopen position\b",
        r"\bhiring for\b",
        r"\bapply (now|here|today|via)\b",
        r"\bproduct owner role\b",
        r"\bproduct manager role\b",
        r"\bpm role\b",
        r"\blooking for a (product|pm|po)\b",
    )
]

_SKIP_CELEBRATION_RES = [
    re.compile(p, re.I)
    for p in (
        r"\bwork anniversary\b",
        r"\bworkiversary\b",
        r"#opentowork\b",
        r"\bopen to work\b",
        r"\bcertified in\b",
        r"\bcourse completion\b",
        r"\bso proud to announce\b",
        r"\bpleased to announce\b",
        r"\bi'?m pleased to announce\b",
    )
]

_ENGAGEMENT_BAIT_RES = [
    re.compile(p, re.I)
    for p in (
        r"\bagree\?\s*$",
        r"\blike if\b",
        r"\bcomment below\b",
        r"\brepost if\b",
        r"\bfollow for\b",
        r"\bdm me for\b",
    )
]

_PM_HEADLINE_RES = [
    re.compile(p, re.I)
    for p in (
        r"product manager",
        r"product management",
        r"product owner",
        r"product lead",
        r"head of product",
        r"vp product",
        r"chief product",
        r"product @",
    )
]


def parse_post_age_hours(sub_description: str | None) -> float | None:
    if not sub_description or "promoted" in sub_description.lower():
        return None
    match = re.search(
        r"(\d+)\s*(s|sec|secs|second|seconds|m|min|mins|minute|minutes|"
        r"h|hr|hrs|hour|hours|d|day|days|w|wk|week|weeks|mo|month|months|yr|year|years)\b",
        sub_description.lower(),
    )
    if not match:
        return None
    amount = int(match.group(1))
    unit = match.group(2)
    hours = {
        "s": 1 / 3600,
        "sec": 1 / 3600,
        "secs": 1 / 3600,
        "second": 1 / 3600,
        "seconds": 1 / 3600,
        "m": 1 / 60,
        "min": 1 / 60,
        "mins": 1 / 60,
        "minute": 1 / 60,
        "minutes": 1 / 60,
        "h": 1,
        "hr": 1,
        "hrs": 1,
        "hour": 1,
        "hours": 1,
        "d": 24,
        "day": 24,
        "days": 24,
        "w": 168,
        "wk": 168,
        "week": 168,
        "weeks": 168,
        "mo": 720,
        "month": 720,
        "months": 720,
        "yr": 8760,
        "year": 8760,
        "years": 8760,
    }
    return amount * hours.get(unit, 1)


def _combined_text(item: dict[str, Any]) -> str:
    text = (item.get("text") or "").lower()
    headline = (item.get("author_headline") or "").lower()
    return f"{text}\n{headline}"


def niche_score(item: dict[str, Any], cfg: dict[str, Any]) -> int:
    combined = _combined_text(item)
    score = 0
    for kw in cfg.get("niche_keywords_strong", []):
        if kw.lower() in combined:
            score += 2
    for kw in cfg.get("niche_keywords", []):
        if kw.lower() in combined:
            score += 1
    return score


def detect_post_kind(text: str) -> str:
    lower = text.lower()
    for pattern in _SKIP_CELEBRATION_RES:
        if pattern.search(lower):
            return "celebration"
    for pattern in _JOB_POSTING_RES:
        if pattern.search(lower):
            return "job_posting"
    for pattern in _CAREER_UPDATE_RES:
        if pattern.search(lower):
            return "career_update"
    return "opinion"


def author_is_pm(item: dict[str, Any]) -> bool:
    headline = item.get("author_headline") or ""
    return any(p.search(headline) for p in _PM_HEADLINE_RES)


def classify_post(item: dict[str, Any], cfg: dict[str, Any]) -> tuple[bool, str, str | None]:
    """Return (allowed, reason, comment_style)."""
    if item.get("is_promoted"):
        return False, "promoted", None
    if item.get("is_group"):
        return False, "group_post", None
    if cfg.get("skip_company_pages") and item.get("is_company"):
        return False, "company_page", None

    share_urn = str(item.get("share_urn") or "")
    if "groupPost" in share_urn:
        return False, "group_post", None
    if not share_urn or ("share:" not in share_urn and "ugcPost" not in share_urn):
        return False, "no_share_urn", None

    text = item.get("text") or ""
    if len(text.strip()) < 40:
        return False, "too_short", None

    for pattern in _ENGAGEMENT_BAIT_RES:
        if pattern.search(text):
            return False, "engagement_bait", None

    for kw in cfg.get("skip_keywords", []):
        if kw.lower() in text.lower():
            return False, f"skip_keyword:{kw}", None

    max_age = float(cfg.get("max_post_age_hours", 8))
    age_h = item.get("post_age_hours")
    if cfg.get("max_post_age_strict", True):
        if age_h is None:
            return False, "unknown_age", None
        if age_h > max_age:
            return False, "too_old", None

    kind = detect_post_kind(text)
    if kind == "celebration":
        return False, "celebration_post", None

    score = niche_score(item, cfg)
    min_score = int(cfg.get("min_niche_score", 2))
    if author_is_pm(item):
        min_score = min(min_score, 1)
        if score < min_score and not any(
            k in text.lower()
            for k in ("product manager", "product owner", "product management", " pm ", "po role")
        ):
            return False, "job_not_pm_niche", None
        return True, "job_posting", COMMENT_STYLE_CAREER

    if kind == "career_update":
        if score < min_score and not author_is_pm(item):
            return False, "career_not_pm_niche", None
        return True, "career_update", COMMENT_STYLE_CAREER

    if score < min_score:
        return False, "no_niche_match", None

    if len(text.strip()) < int(cfg.get("min_opinion_chars", 80)):
        return False, "too_short_for_opinion", None

    return True, "opinion", COMMENT_STYLE_OPINION


def rank_key(item: dict[str, Any], cfg: dict[str, Any]) -> tuple[int, float, int]:
    """Sort: opinion first, fresher first, higher niche score."""
    kind = detect_post_kind(item.get("text") or "")
    kind_rank = 0 if kind == "opinion" else 1 if kind in ("career_update", "job_posting") else 2
    age = item.get("post_age_hours")
    age_rank = age if age is not None else 999
    return (kind_rank, age_rank, -niche_score(item, cfg))
