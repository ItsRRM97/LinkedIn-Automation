---
name: linkedin-content-posting
description: >-
  Draft, schedule, and publish LinkedIn from Notion Content Library using
  Buffer MCP (scheduled text/image/PDF), Composio (instant publish + comments),
  and Canva MCP (carousel PDFs). Use for LinkedIn posts, carousels, calendar,
  or job-search content workflow.
---

# LinkedIn Content Posting

Changelog: [`SKILL_CHANGELOG.md`](SKILL_CHANGELOG.md) · IDs & 2026 deltas: [`reference.md`](reference.md)

Operate Roshan's LinkedIn pipeline from **Notion** (strategy + calendar), **Buffer MCP** (scheduled publish), and **Composio** (instant publish + comments). Never hardcode post copy, API tokens, or stale job titles.

**Every schedule/publish run:** `notion-fetch` the live strategy page first (do not rely on memory or skill excerpts alone).

**Every run (required):** **Content Library cleanup** — reconcile pipeline rows with Buffer before drafting or scheduling (see § Content Library cleanup).

## Prerequisites

1. **Notion MCP** (`plugin-notion-workspace-notion`) — content system of record.
2. **Buffer MCP** — `buffer` in `~/.cursor/mcp.json` → `https://mcp.buffer.com/mcp` · token `BUFFER_MCP_TOKEN` in `~/.zshrc` (never commit).
3. **Canva MCP** — `canva` in `~/.cursor/mcp.json` → `https://mcp.canva.com/mcp` via `mcp-remote` (OAuth on first use). **Composio `canva`** ACTIVE for list/create shell/export (`CANVA_POST_DESIGNS`, `CANVA_POST_EXPORTS`).
4. **Composio CLI** — `linkedin` ACTIVE; read `/Users/rawshn/.claude/skills/composio-cli/SKILL.md`.

Restart Cursor after MCP config changes.

```bash
composio connections linkedin   # before Composio publish
```

If Buffer MCP fails → stop and report; **do not use Zapier** (webhook disabled).

**Post-live (scheduled):** local `golden_hour.py cleanup-content-library` (alias `sync-notion`) uses Buffer **`get_post`** when Cursor is not open — same response fields as Buffer MCP.

Golden hour + feed engage → **`install_publish_day_schedule.sh`** (all Buffer posts, including CON-138).

## Notion system map (load on demand)

| Role | Name | ID |
|------|------|-----|
| Hub | LinkedIn (Resource) | `1d63dffe-a139-8083-adde-e5fa98f11c2a` |
| **Strategy 2026 (required)** | **[Depth Score (May)](https://www.notion.so/36f3dffea13981959dacf3b5a76003b7)** | `36f3dffe-a139-8195-9dac-f3b5a76003b7` |
| Workflow | LinkedIn Workflow & Composio | `36f3dffe-a139-8108-98d2-e9daff72881a` |
| ~~Zapier~~ | ~~Zapier + Buffer setup~~ | `36f3dffe-a139-81d9-939b-e062e1e9d771` — **disabled; do not use** |
| **Pipeline** | **Content Library** | `753369dc15fb4b3c82dd9c88cb753c3c` · DS `collection://76e3d273-ba2e-4ae6-9e46-284628343940` |
| Persona | My Persona - LinkedIn | `b9887b1f-3282-4a72-874f-b35a70d9d17b` |
| Guidelines | Posting Guidelines & Formats | `5fe29b4c-a21a-4834-bc2e-bacc0588e10e` |

**Content Library:** `Name`, `Status`, `Posting on`, `Content Type`, `Theme`, `Persona`, `Tags`, body in page; PDFs in `Files & media` (upload to Drive before publish — Notion URLs are 403 for Buffer).

**Content Type (Notion `Content Type` — must match asset, not Buffer metadata):**

| Notion value | When to use | Buffer asset |
|--------------|-------------|--------------|
| `2. Carousel` | PDF carousel (6–9 slides) | `document` (PDF) |
| `4. Image` | Single photo/screenshot + caption | one `image` |
| `5. Infographics` | Tall/static infographic (usually one image) | one `image` |
| `13. Text` | Text-only | no `assets` |

**Do not** copy Buffer `metadata.type` (`carousel` / `post`) into Notion — it often mislabels single-image posts. Set `Content Type` from the **primary asset** and `Name` suffix (`(Carousel)`, `(Infographic)`, screenshot posts omit carousel suffix).

**Status:** `Drafting` → `Ready` → `Scheduled` → `Posted` / `Rejected`. Set `Scheduled` after Buffer confirms; **`Posted` immediately when Buffer is `sent`** (cleanup step — do not leave live posts on `Scheduled`).

### Calendar swaps (do not delete planned posts)

When the user bumps, replaces, or reschedules a slot:

1. **Add** a new Content Library row for the new post (correct `Content Type`, `Name`, body, assets).
2. **Demote** bumped rows: Notion `Status` → **Ready**; clear or archive `Posting on` only if the slot is truly open (optional: keep target date as note in pipeline block).
3. **Buffer:** `edit_post` with `saveToDraft: true` **or** `create_post` + `saveToDraft: true` to preserve copy/assets — **never `delete_post`** on planned content unless the user explicitly asks to discard it.
4. **Schedule** the new post with a **new** `create_post` (or an unused Buffer ID). Do not overwrite an existing planned post's Buffer row in place.
5. Link each Notion row to its own Buffer ID in the pipeline block (`Buffer post ID` when scheduled; `Buffer draft ID` when Ready).

**Rejected** is for content the user will not publish — not for calendar bumps.

### Content Library cleanup (required every run)

Stale `Scheduled` / `Ready` rows clutter the board and break the calendar. Run **before** steps 2–8 whenever you use this skill (schedule, draft, publish, or calendar review).

| Where | How |
|-------|-----|
| **Cursor (preferred)** | For each `linkedin-golden-hour/campaigns/*.json` with `notion_page_id` + `buffer_post_id`: Buffer MCP **`get_post`** → if `status` = `sent` and Notion `Status` ≠ **Posted**, `notion-update-page` → **Posted** + append publish block (Buffer ID, share URN, LinkedIn URL from `externalLink`). Also scan Content Library rows still **Scheduled** or **Ready** whose page body contains a Buffer post ID. |
| **CLI (launchd / no MCP)** | `python3 ~/Projects/LinkedIn\ Automation/linkedin-golden-hour/golden_hour.py cleanup-content-library` (alias: `sync-notion`) — needs `NOTION_TOKEN` + `BUFFER_MCP_TOKEN` in `~/.zshrc`. `NOTION_CONTENT_LIBRARY_DB` optional (defaults to Content Library `753369dc15fb4b3c82dd9c88cb753c3c`). Token source: Notion internal integration (same as Antigravity `~/.gemini/config/mcp_config.json` → `notion-mcp-server` env). |

**Idempotent:** Skip rows already **Posted** with a publish block; do not duplicate blocks.

**After instant Composio publish:** set Notion **Posted** in the same turn (cleanup still catches anything missed).

### Manual Overrides & Manual Publishing

If a post is published manually or via another method, or if its Buffer post ID is missing/deleted from Buffer but the post is live on LinkedIn:
1. Update Notion **Status** → **Posted** using Notion MCP.
2. Manually append a publish block in the page body containing the LinkedIn post URL or share URN (if known).
3. Do not leave the row as **Scheduled** or **Ready** if you or the user confirms it is already live.

## Strategy doc (mandatory — May 2026)

**Page:** [LinkedIn Strategy 2026 — Depth Score (May)](https://www.notion.so/36f3dffea13981959dacf3b5a76003b7) · `36f3dffe-a139-8195-9dac-f3b5a76003b7`

At the **start** of any draft, schedule, or publish task:

```text
notion-fetch: 36f3dffe-a139-8195-9dac-f3b5a76003b7
```

Apply from that page (summaries below are hints only — **the Notion page wins** if they drift):

| Topic | Rule |
|-------|------|
| **When (IST)** | Primary: **Tue–Thu 9:30–11:30** or **15:00–17:00**; also tech **06:00–07:00**, India+EU **13:30**; **avoid weekends**; Mon/Fri softer |
| **Cadence** | 3–5 posts/week, 2–3 pillars, 90-day consistency |
| **Formats** | PDF carousel #1 (6–9 slides); no external links in post **or** first comment |
| **Golden hour** | 60–90 min engaged; substantive replies; target 10+ real comments in first 30 min |
| **Hashtags** | 3–5 max |

Pick `dueAt` in the next valid primary window unless the user names a time. Default anchor: **10:00 IST** Tue–Thu.

Legacy 2024 slots: [`reference.md`](reference.md) · persona/guidelines still load for copy tone.

## Automation coverage (Cursor stack)

| Format | Schedule (Buffer MCP) | Publish now (Composio) | Create asset (Canva/Drive) |
|--------|----------------------|------------------------|----------------------------|
| **Text** | Yes | Yes | N/A |
| **Single image + caption** | Yes | Yes (upload flow) | Canva export or Drive URL |
| **PDF carousel** | Yes (`document` asset) | No | Yes — Canva MCP template copy → PDF → Drive |
| **Poll** | No | No | Manual LinkedIn UI |
| **Native video** | No | No | Manual LinkedIn UI |
| **Live** | No | No | Manual |
| **Comment replies (golden hour)** | N/A | Yes (`LINKEDIN_CREATE_COMMENT_ON_POST`) | N/A — see `linkedin-golden-hour` |

**Automated post-live:** Buffer `sent` → Notion `Posted` + share URN via `post_live_sync.py` (runs each golden-hour watch tick).

**Planned (not built):** proactive niche comments — [`proactive-comments-plan.md`](proactive-comments-plan.md) · **feed engage:** [`linkedin-feed-engage`](../linkedin-feed-engage/SKILL.md) (Cursor browser).

## Workflow checklist

```
- [ ] 0. Content Library cleanup — campaigns + Scheduled/Ready rows vs Buffer `sent` → Notion **Posted** (required)
- [ ] 1. notion-fetch strategy 36f3dffe-a139-8195-9dac-f3b5a76003b7 (required)
- [ ] 2. Notion RAG — persona + guidelines
- [ ] 3. Content Library row — Ready; set **Content Type** from asset table; PDF pre-flight
- [ ] 4. Pick slot from strategy (IST) unless user overrides
- [ ] 5. Buffer MCP create_post OR Composio instant
- [ ] 6. Notion from Buffer response — **Scheduled** after `create_post`; **Posted** when `get_post`/`create_post` shows `sent`
- [ ] 7. Post-live (scheduled only) — `golden_hour.py cleanup-content-library` if step 0/6 did not run in Cursor
- [ ] 8. Golden hour — **auto** via `linkedin-golden-hour` skill (no approval)
```

### 1. Strategy (required first)

```text
notion-fetch: 36f3dffe-a139-8195-9dac-f3b5a76003b7
```

### 2. Persona + guidelines

```text
notion-fetch: b9887b1f-3282-4a72-874f-b35a70d9d17b
notion-fetch: 5fe29b4c-a21a-4834-bc2e-bacc0588e10e
```

### 3. Content Library

Create/update on `collection://76e3d273-ba2e-4ae6-9e46-284628343940`. Body: hook → value → specific CTA. `<3000` chars.

### 4. Publish routing (after explicit approval)

| Need | Tool |
|------|------|
| **Scheduled** text / image / PDF carousel | **Buffer MCP** `create_post` |
| **Publish now** text / image | Composio `LINKEDIN_CREATE_LINKED_IN_POST` (+ image upload tools) |
| **Golden hour replies** | `linkedin-golden-hour` · `golden_hour.py watch` (local launchd) |
| **First comment on own post** | Composio `LINKEDIN_CREATE_COMMENT_ON_POST` (2026: no URLs) |
| Buffer MCP down | **Stop** — Zapier webhook is disabled |

#### Buffer MCP (primary — scheduled)

**Flow:** `get_account` (confirm org) → `list_channels` → pick LinkedIn → `create_post`.

**Stable IDs** (re-verify with `list_channels` if publish fails):

| Entity | ID |
|--------|-----|
| Organization | `6256ef66943190835092e486` (Codepth Pvt Ltd) |
| LinkedIn channel | `6257083b6be9a557a27ea205` (rawshn) |

**Text / image (scheduled):**

```json
{
  "channelId": "6257083b6be9a557a27ea205",
  "schedulingType": "automatic",
  "mode": "customScheduled",
  "dueAt": "2026-06-04T10:00:00+05:30",
  "text": "<final commentary, no URLs>"
}
```

Add `assets` for image: `[{"image":{"url":"<direct-url>","metadata":{"altText":"..."}}}]`

**PDF carousel:**

```json
{
  "channelId": "6257083b6be9a557a27ea205",
  "schedulingType": "automatic",
  "mode": "customScheduled",
  "dueAt": "<from Posting on, IST offset>",
  "text": "<caption>",
  "assets": [{
    "document": {
      "url": "https://drive.google.com/uc?export=download&id=FILE_ID",
      "title": "<short title>",
      "thumbnailUrl": "https://drive.google.com/uc?export=download&id=FILE_ID"
    }
  }]
}
```

- `dueAt` must be ISO 8601 with timezone (`+05:30` for IST). Use `get_account` timezone (`Asia/Kolkata`).
- `mode` options: `customScheduled` (needs `dueAt`), `addToQueue`, `shareNow`, `shareNext`, `recommendedTime`.
- **Notion from Buffer MCP response (same Cursor session):**

| `create_post` / `get_post` response | Notion action (`notion-update-page`) |
|-------------------------------------|--------------------------------------|
| `status` = `scheduled` (typical for `customScheduled`) | `Status` → **Scheduled** · append `Buffer post ID: {id}` |
| `status` = `sent` (`shareNow`, or `get_post` after publish) | `Status` → **Posted** · append share URN + LinkedIn URL from `externalLink` |

Buffer does **not** push to Cursor when a scheduled post goes live — the agent session from schedule day is gone. At publish time, local `golden_hour.py cleanup-content-library` (or `watch`) calls the same **`get_post`** shape and updates Notion when `status=sent`.

- **Pre-flight (carousels):** Confirm PDF filename and slide 1 title match Content Library `Name` / hook. Do not reuse generic `Full-Stack PM` decks for unrelated titles. Search Drive by post title keywords; if mismatch, stop and ask user.

#### Carousel creation (automated)

**Primary — Canva MCP + branded template** (looks like yours):

1. **Template:** `search-designs` → `Carousel Post - Full-Stack PM` (`DAF4WMk_grY`) — 1080×1080, photo, **Roshan Raj Mishra**, **@rawshn** on every slide.
2. `copy-design` → `start-editing-transaction` → `replace_text` per slide (keep branding elements) → `commit-editing-transaction`.
3. `export-design` (pdf) → Drive upload + public `CREATE_PERMISSION`.
4. **Pre-flight:** `get-design-content` page 1 title = Content Library `Name`; not a different post’s PDF.
5. Buffer `create_post` with `uc?export=download&id=`.

**Layout & copy rules (every carousel):**

| Rule | Detail |
|------|--------|
| **Body alignment** | Title + body/description blocks: **left-aligned only** (`format_text` → `text_align: start`). Never justified. Cover title included. |
| **Cover hook line breaks** | `replace_text` on cover headline (`PBDgGb2ZkRF12DlX-LBsHQfvHKw4pnSMf`) with **manual `\n` breaks** before `format_text`. Canva auto-wrap + justified = wide word gaps. Aim for 3 lines, natural phrasing, no orphan words. Example MCP hook: `7 MCPs PMs\nShould Try in\nAgentic Workflows`. Example open-source: `7 Open Source Tools\nEvery PM Should Try\nin 2026`. |
| **Copyright footer** | Every slide: `© 2026 Roshan Raj Mishra` (or `© Roshan Raj Mishra`) at **bottom**, same position/size on all pages. Add in template edits so `copy-design` inherits it. |
| **Branding** | Keep header photo + **Roshan Raj Mishra** + **@rawshn** on every slide; normalize `@_rawshn_` → `@rawshn` if copied from older slides. |
| **LinkedIn copy** | No em dash, en dash, or hyphen as clause separators in caption or slide text (repo rule). Use periods, commas, or colons. |

**Edit transaction checklist:** cover `replace_text` with manual line breaks → `format_text` (`text_align: start`) on cover + all title/body blocks pages 1–10 → verify copyright on each page → `commit-editing-transaction`.

**Alternate — AI generate** (new visual style): `generate-design` + `resize-design` 1080×1080 — use only when no template match.

**Fast draft — Google Slides (Composio):** copy proof only.

**Manual fallback:** Composio `CANVA_POST_DESIGNS` custom 1080×1080 shell.

#### Composio (instant + comments)

```bash
composio execute LINKEDIN_GET_MY_INFO
composio execute LINKEDIN_CREATE_LINKED_IN_POST -d '{
  "author": "urn:li:person:<ID>",
  "commentary": "<text, no external URLs>"
}'
```

Save `x_restli_id` on Notion row. Images: `LINKEDIN_INITIALIZE_IMAGE_UPLOAD` flow.

Save `x_restli_id` on Notion row; set `Status` → **Posted** via Notion MCP in the same turn.

### 6. Post-live Notion sync

**In Cursor (preferred when you are in chat):** read `status` + `externalLink` from Buffer MCP `create_post` or `get_post` → `notion-update-page` immediately when `sent`.

**Scheduled posts (CON-138-style):** `create_post` returns `scheduled` only — update Notion to **Scheduled** then. When Buffer publishes later, **`get_post` response** drives Notion **Posted** (no separate “sync job” logic — same API fields):

```bash
python3 ~/Projects/LinkedIn\ Automation/linkedin-golden-hour/golden_hour.py cleanup-content-library
```

(`sync-notion` is an alias.)

Runs each golden-hour watch tick. Requires `NOTION_TOKEN` in `~/.zshrc` for local scripts; Cursor uses Notion MCP instead.

Campaigns with `notion_page_id` (e.g. CON-138) sync on first `watch`/`tick` when Buffer returns `sent`.

### 7. Publish day (golden hour + feed engage)

Load **`linkedin-golden-hour`** and **`linkedin-feed-engage`** skills. **No approval** for replies or feed comments when launchd is installed.

```bash
bash ~/Projects/LinkedIn\ Automation/scripts/install_publish_day_schedule.sh
```

Tue–Thu 10:00 local → `publish_day_watch.sh` every 10m × 90m:

- **`golden_hour.py watch`** — auto-replies on comments on **your** post (all Buffer sends, including CON-138)
- **`feed_engage_trigger.py`** — arms 30 feed comments when Buffer marks post `sent`

Manual one-off: `python3 ~/Projects/LinkedIn\ Automation/linkedin-golden-hour/golden_hour.py watch`

- **Detect:** Buffer sent posts + Gmail comment emails  
- **Reply:** 4-part Depth Score frame · Composio `LINKEDIN_CREATE_COMMENT_ON_POST`  
- **Limit:** Buffer carousel shares may 404 on comment API → `pending_replies` in state

User approves **publish** only; publish-day automation runs without further approval when Mac + Cursor + LinkedIn login are ready.

## Security

- Never copy passwords or tokens into skills, chat logs, or git. Rotate `BUFFER_MCP_TOKEN` if exposed.
- User must approve every **publish** (schedule/instant post). Golden-hour **comment replies** are automatic when `linkedin-golden-hour` is armed — no per-reply approval.

## Examples

**"Swap Wednesday slot for new image post"** → New Notion row (`4. Image`) + `create_post` schedule → bumped row **Ready** + Buffer `saveToDraft` (or new draft via `create_post`) — do not delete or overwrite the old row's Buffer post in place.

**"Schedule Thursday carousel"** → Fetch Content Library row → Drive PDF URL → Buffer `create_post` with `customScheduled` → Notion `Scheduled`.

**"Post Ready text now"** → Composio `LINKEDIN_CREATE_LINKED_IN_POST` → `Posted`.

**"Repost old CON-138"** → notion-fetch row → refresh caption (2026 rules) → Buffer schedule at next IST window.
