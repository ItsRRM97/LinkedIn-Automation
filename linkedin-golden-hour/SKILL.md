---
name: linkedin-golden-hour
description: >-
  Auto-reply to LinkedIn post comments during golden hour (60–90 min after publish).
  Detects comments via Gmail, drafts 4-part Depth Score replies from post context,
  posts via Composio with no user approval. Use for golden hour, comment automation,
  or CON-138 publish-day engagement.
---

# LinkedIn Golden Hour (auto-reply)

Changelog: [`SKILL_CHANGELOG.md`](SKILL_CHANGELOG.md)

**Mode:** Fully automatic — **no approval** for replies. Use post context + comment text → post via Composio.

Pair with [`linkedin-content-posting`](../linkedin-content-posting/SKILL.md) for schedule/publish.

## Prerequisites

| Tool | Role |
|------|------|
| **Composio** `linkedin` ACTIVE · actor `urn:li:person:2P7nq91zOA` | Post replies |
| **Composio** `gmail` ACTIVE | Detect LinkedIn comment emails |
| **Buffer MCP** `get_post` | Capture `externalLink` → share URN after publish |
| **Loop skill** | `/loop 10m` for 90 min after go-live |

Enable LinkedIn email notifications: **Settings → Notifications → Comments on your posts → Email ON**.

## Campaign files

| Type | File | Notes |
|------|------|-------|
| **Global config** | `config.json` | Buffer org/channel, golden-hour window, skip test posts |
| **Manual campaign** | `campaigns/CON-138.json` | Rich `post_context`; matched by `buffer_post_id` |
| **Auto campaign** | `campaigns/buf-{buffer_post_id}.json` | Created on first watch for any sent Buffer post |
| **Registry** | `state/buffer_registry.json` | Active posts seen by watcher |

Per-post state: `state/{campaign_id}.json`

### Generic Buffer watch (recommended)

Watches **every LinkedIn post Buffer marks `sent`** within the golden-hour window (default **90 min** after `sentAt`):

```bash
python3 ~/LinkedIn\ Automation/linkedin-golden-hour/golden_hour.py watch
```

Each run:
1. `list_posts` (Buffer API) → LinkedIn channel, status `sent`
2. Skip test posts in `config.json` (`skip_buffer_post_ids`, `skip_text_contains`)
3. Match manual campaign by `buffer_post_id` (CON-138 keeps rich themes) or **auto-build** context from caption
4. Gmail comment detect → reply on the right post (single active post, or best caption match)
5. Composio post — no approval

**Cursor Automation (generic):** cron every **10 min** Tue–Thu 10:00–11:30 (`*/10 10-11 * * 2,3,4`) → run `watch`.

Legacy per-campaign:

| Campaign | File | Buffer post |
|----------|------|-------------|
| **CON-138** | `campaigns/CON-138.json` | `6a19809c417d9b6a6a946636` |

## Reply rules (Depth Score — May 2026)

From strategy `36f3dffe-a139-8195-9dac-f3b5a76003b7`:

1. **Name** — first name only  
2. **Cite** — paraphrase their comment (not “Great post!”)  
3. **Value** — one mini insight tied to carousel themes  
4. **Question** — open follow-up  

**Never** include links in replies. Max ~1250 chars.

## Run

### One tick — all Buffer posts (generic)

```bash
python3 ~/LinkedIn\ Automation/linkedin-golden-hour/golden_hour.py watch
```

### One tick — single campaign

Dry-run (generate only):

```bash
python3 ~/LinkedIn\ Automation/linkedin-golden-hour/golden_hour.py tick --campaign CON-138 --dry-run
```

### Manual comment → auto-reply (no Gmail)

```bash
python3 ~/LinkedIn\ Automation/linkedin-golden-hour/golden_hour.py reply \
  --campaign CON-138 \
  --commenter "Alex Kumar" \
  --comment "We do weekly user calls but struggle with saying no."
```

### Golden hour loop (publish day)

**Canonical — all Buffer posts (including CON-138):**

```bash
bash ~/LinkedIn\ Automation/scripts/install_publish_day_schedule.sh
```

Launchd `com.rawshn.linkedin-publish-day-watch` · Tue–Thu 10:00 local → `publish_day_watch.sh` every 10m × 90m (`watch` + `feed_engage_trigger`).

**Manual one-off:**

```bash
python3 ~/LinkedIn\ Automation/linkedin-golden-hour/golden_hour.py watch
```

Do **not** use per-campaign launchd plists (`com.rawshn.linkedin-golden-hour-con138`) or Cursor Automations scheduled per post — the generic watcher matches any sent Buffer LinkedIn post; CON-138 keeps rich reply context via `campaigns/CON-138.json` when `buffer_post_id` matches.

Each tick:

1. `get_post` Buffer ID → save `share_urn` when `status=sent`  
2. `GMAIL_FETCH_EMAILS` `from:linkedin.com (commented OR replied) newer_than:3h`  
3. Parse new comment notifications → generate reply → `LINKEDIN_CREATE_COMMENT_ON_POST`  
4. Dedupe via `state/CON-138.json` `processed_message_ids`

## Composio comment payload

```json
{
  "actor": "urn:li:person:2P7nq91zOA",
  "object": "urn:li:share:<ID>",
  "target_urn": "urn:li:share:<ID>",
  "message": { "text": "<4-part reply, no links>" }
}
```

Thread reply: set `target_urn` + `parentComment` to parent comment URN.

## Known limits

| Limit | Mitigation |
|-------|------------|
| **No LinkedIn list-comments API** | Gmail comment notifications (primary) |
| **Buffer-published shares often 404 on Composio comment API** | After publish, retry `GET_POST_CONTENT`; if still blocked, browser fallback on logged-in LinkedIn session |
| **API-native posts work** | Verified on Composio-created share `7466433583725895680` |
| Gmail may lag 5–15 min | Loop every 10 min for 90 min |

## Agent checklist (auto mode)

```
- [ ] notion-fetch strategy 36f3dffe-a139-8195-9dac-f3b5a76003b7
- [ ] Load campaign JSON + post_context
- [ ] tick --campaign <ID> (no approval gate)
- [ ] On Composio 404 for Buffer URN: queue pending in state; try browser if session exists
- [ ] Append posted replies to Notion page body (optional)
```

## Examples

**"Auto golden hour for CON-138"** → Arm `/loop 10m` from 10:00–11:30 IST 3 Jun → `tick --campaign CON-138` each wake.

**"Reply to this comment automatically"** → `reply --campaign CON-138 --commenter "…" --comment "…"`.
