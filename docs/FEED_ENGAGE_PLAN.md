# Feed Engage Daemon — Project Plan

See also: [FEED_ENGAGE_DAEMON.md](./FEED_ENGAGE_DAEMON.md) (setup steps).

Status: **Phase 1 shipped**. Phase 2–3 pending.

## OpenRouter cost estimate

| Model | $/month @ 100 comments/day |
|-------|----------------------------|
| `nvidia/nemotron-3-nano-30b-a3b:free` | **$0** |
| Groq free tier | **$0** |
| OpenRouter paid fallback | ~$3–12 |

~200k tokens/day. Free tier may 429 at peak; daemon spreads comments to reduce hits.

## Cursor Cloud Agent

**Cannot run this daemon when your laptop is off.** Cloud Agents edit code in the cloud; they do not hold LinkedIn cookies or run local launchd. For 24/7: always-on Mac or VPS with same env vars.

## Phases

### Phase 1 — Done

CLI daemon, Buffer windows, quota, OpenRouter/Groq, linkedincli runner, publish_day_watch integration.

### Phase 2 — Next

- `scripts/setup_feed_daemon.sh`
- Notion persona import
- @mention verification
- Daily background launchd (non-publish days)

### Phase 3 — Optional

- VPS deploy for laptop-off
- Cookie refresh runbook
- Quota metrics → Notion
