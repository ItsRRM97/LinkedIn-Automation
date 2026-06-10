# LinkedIn posting — reference

## Canonical Notion pages

| Page | ID |
|------|-----|
| [Strategy 2026 — Depth Score](https://www.notion.so/36f3dffea13981959dacf3b5a76003b7) | `36f3dffe-a139-8195-9dac-f3b5a76003b7` |
| [Workflow & Composio](https://www.notion.so/36f3dffea139810898d2e9daff72881a) | `36f3dffe-a139-8108-98d2-e9daff72881a` |
| [Zapier + Buffer (archived — disabled)](https://www.notion.so/36f3dffea13981d9939be062e1e9d771) | `36f3dffe-a139-81d9-939b-e062e1e9d771` |

## Buffer MCP (primary)

| Item | Value |
|------|--------|
| Endpoint | `https://mcp.buffer.com/mcp` |
| Config | `~/.cursor/mcp.json` → `buffer` |
| Token | `BUFFER_MCP_TOKEN` in `~/.zshrc` |
| Org | `6256ef66943190835092e486` (Codepth Pvt Ltd) |
| LinkedIn channel | `6257083b6be9a557a27ea205` |
| Timezone | `Asia/Kolkata` |

**Tools:** `get_account` · `list_channels` · `create_post` · `list_posts` · `edit_post` · `delete_post`

**create_post modes:** `customScheduled` (+ `dueAt` ISO with offset) · `addToQueue` · `shareNow` · `shareNext` · `recommendedTime`

**Assets:** `image.url` + `metadata.altText` · `document.url` + `title` + `thumbnailUrl` (PDF carousel)

**Media URLs:** Google Drive `https://drive.google.com/uc?export=download&id=FILE_ID` only. Notion S3 = 403.

## Composio (instant + comments)

| Slug | Use |
|------|-----|
| `LINKEDIN_GET_MY_INFO` | Person URN |
| `LINKEDIN_CREATE_LINKED_IN_POST` | Immediate text/image |
| `LINKEDIN_CREATE_COMMENT_ON_POST` | Comments (avoid URLs per 2026) |
| `LINKEDIN_INITIALIZE_IMAGE_UPLOAD` | Image attach |

No Buffer toolkit in Composio.

## Zapier

**Disabled** — webhook no longer works. Do not use as fallback. Buffer MCP only for scheduled publish.

## Automation coverage (Cursor stack)

| Format | Schedule (Buffer MCP) | Publish now (Composio) | Create asset |
|--------|----------------------|------------------------|--------------|
| Text | Yes | Yes | N/A |
| Single image + caption | Yes | Yes | Canva/Drive |
| PDF carousel | Yes | No | Canva MCP → PDF → Drive |
| Poll / video / Live | No | No | Manual LinkedIn UI |
| Golden hour replies | N/A | Yes | `linkedin-golden-hour` + launchd |

**Post-live sync:** `golden_hour.py cleanup-content-library` — Notion **Posted** when Buffer **`get_post`** returns `status=sent` (same fields as Buffer MCP). In Cursor, use **`notion-update-page` from MCP response** directly when scheduling or when you call `get_post`.

## Post-live sync

```bash
python3 ~/Projects/LinkedIn\ Automation/linkedin-golden-hour/golden_hour.py cleanup-content-library [--dry-run]
```

Run at the start of every `linkedin-content-posting` session and on each `publish_day_watch` tick.

Alias: `sync-notion` · wrapper: `post_live_sync.py`. Env: `NOTION_TOKEN` + `BUFFER_MCP_TOKEN` in `~/.zshrc` (integration token; same as Antigravity `~/.gemini/config/mcp_config.json` → `notion-mcp-server`).

## Posting slots (IST)

1. Primary: Tue–Thu **09:30–11:30** (default anchor **10:00**)
2. Primary: Tue–Thu **15:00–17:00**
3. Secondary: tech **06:00–07:00** · India+EU **13:30**

Legacy 2024 slots: Wed 8–10am, Wed 12pm, Thu 9am, Thu 1–2pm, Fri 9am, Tue 8am; evenings Tue–Thu ~19:30.

## Monthly mix (target)

| Format | /month |
|--------|--------|
| Carousel/PDF | 3+ |
| Text | 8–12 |
| Poll | 0–2 |
| Video (no face) | 1–2 |

## Content Library schema

`Status` · `Content Type` · `Theme` · `Persona` · `Posting on` · `Tags` · page body · file attachments
