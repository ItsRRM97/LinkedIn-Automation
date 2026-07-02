"""LLM comment drafting for feed engage daemon (OpenRouter, Groq)."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any


DEFAULT_OPENROUTER_MODEL = "nvidia/nemotron-3-nano-30b-a3b:free"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"


class LLMError(RuntimeError):
    pass


def resolve_llm_provider(llm_cfg: dict[str, Any] | None = None) -> str:
    """Use configured provider; fall back to OpenRouter when Groq key is missing."""
    llm_cfg = llm_cfg or {}
    provider = (llm_cfg.get("provider") or os.environ.get("FEED_LLM_PROVIDER") or "groq").lower()
    if provider == "groq" and not (os.environ.get("GROQ_API_KEY") or llm_cfg.get("groq_api_key")):
        if os.environ.get("OPENROUTER_API_KEY") or llm_cfg.get("openrouter_api_key"):
            return "openrouter"
    return provider


def _post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout: int = 60) -> dict[str, Any]:
    from http_ssl import ssl_context

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")[:800]
        raise LLMError(f"HTTP {exc.code}: {body}") from exc


def _extract_chat_text(data: dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if not choices:
        raise LLMError(f"No choices in LLM response: {json.dumps(data)[:400]}")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
        joined = "\n".join(p for p in parts if p).strip()
        if joined:
            return joined
    raise LLMError("Empty LLM response content")


def _system_prompt(persona: str, rules: dict[str, Any], comment_style: str | None = None) -> str:
    skip = ", ".join(rules.get("skip_keywords", [])[:12])
    niche_strong = ", ".join(rules.get("niche_keywords_strong", [])[:12])
    max_chars = rules.get("max_comment_chars", 900)
    ideal = rules.get("ideal_comment_chars", 280)

    style_block = ""
    if comment_style == "career_ack":
        style_block = """
Post type: career update or job posting.
- Write a warm, brief acknowledgment or congratulations.
- Reference one specific detail from the post.
- Do NOT ask any questions. No question marks.
- Keep it peer-level, not sycophantic."""
    elif comment_style == "opinion_question":
        style_block = """
Post type: opinion or thought piece.
- Add one concrete observation tied to a specific claim in the post.
- End with exactly one sharp follow-up question the author can answer from this post alone.
- The question must not be generic PM platitudes."""

    return f"""You write LinkedIn feed comments as Rawshn.

Persona:
{persona.strip() or "PM/builder voice: concrete, curious, no hype."}
{style_block}

Rules:
- One comment only. No links. No hashtags unless the post uses them naturally.
- Do not use em dash, en dash, or hyphen as a clause separator in the body.
- Prefer {ideal} characters; hard max {max_chars}.
- Relevant topics: {niche_strong or "product management, builders, AI workflows"}.
- Avoid engagement bait tone: {skip or "like if, comment below"}.
- Use @FirstName mention when author name is known.
- Return ONLY the comment text, no quotes or preamble."""


def _looks_like_reasoning_leak(text: str) -> bool:
    lower = text.lower()
    if len(text) > 450 and any(
        phrase in lower
        for phrase in (
            "we need to",
            "must be only comment",
            "return only the comment",
            "draft a comment",
            "produce a single comment",
        )
    ):
        return True
    return False


def _sanitize_llm_comment(text: str) -> str:
    cleaned = text.strip().strip('"').strip("'")
    if not _looks_like_reasoning_leak(cleaned):
        return cleaned

    # Reasoning models sometimes embed the draft in quotes near the end.
    quoted = re.findall(r'"([^"]{40,900})"', cleaned)
    for candidate in reversed(quoted):
        if not _looks_like_reasoning_leak(candidate):
            return candidate.strip()

    lines = [ln.strip() for ln in cleaned.splitlines() if ln.strip()]
    for line in reversed(lines):
        if len(line) < 40 or _looks_like_reasoning_leak(line):
            continue
        if line.startswith("@") or "?" in line or line.endswith("."):
            return line
    return cleaned


def draft_comment(
    post: dict[str, Any],
    *,
    persona: str = "",
    rules: dict[str, Any] | None = None,
    llm_cfg: dict[str, Any] | None = None,
    comment_style: str | None = None,
) -> str:
    rules = rules or {}
    llm_cfg = llm_cfg or {}
    provider = resolve_llm_provider(llm_cfg)
    user_block = json.dumps(
        {
            "author": post.get("author") or post.get("author_name"),
            "headline": post.get("author_headline"),
            "post_text": post.get("text") or post.get("commentary"),
            "post_kind": post.get("post_kind"),
            "comment_style": comment_style,
            "post_age_hours": post.get("post_age_hours"),
        },
        ensure_ascii=False,
    )
    messages = [
        {"role": "system", "content": _system_prompt(persona, rules, comment_style)},
        {"role": "user", "content": f"Draft a comment for this post JSON:\n{user_block}"},
    ]
    if provider == "groq":
        text = _groq_chat(messages, llm_cfg)
    else:
        text = _openrouter_chat(messages, llm_cfg)

    cleaned = _sanitize_llm_comment(text)
    if _looks_like_reasoning_leak(cleaned) and provider != "groq":
        fallback_model = os.environ.get("OPENROUTER_MODEL")
        if fallback_model and fallback_model != llm_cfg.get("openrouter_model"):
            fallback_cfg = {**llm_cfg, "openrouter_model": fallback_model}
            cleaned = _sanitize_llm_comment(_openrouter_chat(messages, fallback_cfg))
    return cleaned


def _openrouter_chat(messages: list[dict[str, str]], llm_cfg: dict[str, Any]) -> str:
    key = os.environ.get("OPENROUTER_API_KEY") or llm_cfg.get("openrouter_api_key")
    if not key:
        raise LLMError("OPENROUTER_API_KEY not set")
    model = (
        llm_cfg.get("openrouter_model")
        or os.environ.get("FEED_OPENROUTER_MODEL")
        or os.environ.get("OPENROUTER_MODEL")
        or DEFAULT_OPENROUTER_MODEL
    )
    payload = {
        "model": model,
        "messages": messages,
        "temperature": float(llm_cfg.get("temperature", 0.7)),
        "max_tokens": int(llm_cfg.get("max_tokens", 400)),
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "HTTP-Referer": llm_cfg.get(
            "http_referer",
            os.environ.get("OPENROUTER_HTTP_REFERER", "https://rawshn.com/linkedin-automation"),
        ),
        "X-Title": llm_cfg.get(
            "app_title",
            os.environ.get("OPENROUTER_APP_TITLE", "LinkedIn Feed Engage Daemon"),
        ),
    }
    data = _post_json("https://openrouter.ai/api/v1/chat/completions", headers, payload)
    return _extract_chat_text(data)


def _groq_chat(messages: list[dict[str, str]], llm_cfg: dict[str, Any]) -> str:
    key = os.environ.get("GROQ_API_KEY") or llm_cfg.get("groq_api_key")
    if not key:
        raise LLMError("GROQ_API_KEY not set")
    model = llm_cfg.get("groq_model") or os.environ.get("FEED_GROQ_MODEL") or DEFAULT_GROQ_MODEL
    payload = {
        "model": model,
        "messages": messages,
        "temperature": float(llm_cfg.get("temperature", 0.7)),
        "max_tokens": int(llm_cfg.get("max_tokens", 400)),
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "User-Agent": "LinkedIn-Feed-Engage-Daemon/1.0",
    }
    data = _post_json("https://api.groq.com/openai/v1/chat/completions", headers, payload)
    return _extract_chat_text(data)
