"""LinkedIn comment posting via Composio (official Social Actions API)."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

_ACTOR_ID: str | None = None


class ComposioLinkedInError(RuntimeError):
    pass


def composio_execute(slug: str, args: dict[str, Any] | None = None, *, timeout: int = 90) -> dict[str, Any]:
    cmd = ["composio", "execute", slug]
    if args is not None:
        cmd.extend(["-d", json.dumps(args)])
    env = os.environ.copy()
    composio_dir = os.path.expanduser("~/.composio")
    env["PATH"] = f"{composio_dir}:{env.get('PATH', '')}"
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=timeout, env=env)
    raw = proc.stdout or proc.stderr
    idx = raw.find("{")
    if idx < 0:
        raise ComposioLinkedInError(f"Composio {slug} returned no JSON: {raw[:500]}")
    envelope = json.loads(raw[idx:])
    if envelope.get("storedInFile") and envelope.get("outputFilePath"):
        with open(envelope["outputFilePath"]) as f:
            payload = json.load(f)
        return payload.get("data", payload)
    if not envelope.get("successful", True):
        raise ComposioLinkedInError(envelope.get("error") or envelope)
    return envelope.get("data", envelope)


def actor_id() -> str:
    global _ACTOR_ID
    if _ACTOR_ID:
        return _ACTOR_ID
    env_id = (os.environ.get("LINKEDIN_ACTOR_ID") or "").strip()
    if env_id:
        _ACTOR_ID = env_id
        return _ACTOR_ID
    info = composio_execute("LINKEDIN_GET_MY_INFO", {})
    person_id = str(info.get("id") or "").strip()
    if not person_id:
        raise ComposioLinkedInError("LINKEDIN_GET_MY_INFO returned no id")
    _ACTOR_ID = person_id
    return _ACTOR_ID


def normalize_share_urn(share_urn: str) -> str:
    urn = share_urn.strip()
    if urn.startswith("urn:li:"):
        if "activity:" in urn:
            raise ComposioLinkedInError(f"Activity URN not supported for comments: {urn}")
        return urn
    if urn.startswith("share:") or urn.startswith("ugcPost:"):
        return f"urn:li:{urn}"
    raise ComposioLinkedInError(f"Unsupported share URN: {urn}")


def create_comment(share_urn: str, text: str) -> dict[str, Any]:
    target = normalize_share_urn(share_urn)
    if "share:" not in target and "ugcPost:" not in target:
        raise ComposioLinkedInError(f"Need share or ugcPost URN, got: {target}")
    actor = f"urn:li:person:{actor_id()}"
    return composio_execute(
        "LINKEDIN_CREATE_COMMENT_ON_POST",
        {
            "target_urn": target,
            "object": target,
            "actor": actor,
            "message": {"text": text[:1250]},
        },
    )
