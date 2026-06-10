# linkedin-content-posting changelog

Rule: `.cursor/rules/skill-self-improvement.mdc`

## 2026-06-03 — Docs/paths polish (Projects root, cleanup CLI)

- **Triggered:** User asked to apply optional repo polish after cleanup + NOTION_TOKEN setup.
- **Learned:** Stale `~/LinkedIn Automation/` paths in skills; publish-day scripts now call `cleanup-content-library` by default.
- **Skill updates:** README publish-day tick order; reference.md; golden-hour SKILL publish-day section; deprecated CON-138 launchd note.

## 2026-06-03 — Content Library cleanup required every run

- **Triggered:** User reported posted Buffer posts still showing `Scheduled` in Content Library; asked for cleanup on each skill run.
- **Learned:** `sync-notion` only queried `Scheduled` (not `Ready`); launchd often lacks `NOTION_TOKEN` — Cursor must run cleanup via MCP when scheduling in chat.
- **Skill updates:** § Content Library cleanup; checklist step 0; `lib/notion_sync.py` `cleanup_content_library()`; CLI `cleanup-content-library` alias.

## 2026-05-31 — CON-139 end-to-end (Tue 2 Jun text post)

- **Triggered:** User asked for new post + full pipeline scheduled Tuesday.
- **Learned:** Text post CON-139 · Buffer `6a1bfe9aefeb482ae3405f25` · campaign JSON with notion_page_id · publish_day_watch handles go-live.
- **Skill updates:** none (read-only workflow execution).

## 2026-05-31 — Publish-day script canonical for all posts

- **Triggered:** User confirmed CON-138 and all posts use `install_publish_day_schedule.sh`.
- **Learned:** Single launchd job; CON-138 campaign JSON only for reply context, not separate schedule.
- **Skill updates:** §7 publish day + golden hour pointer → `install_publish_day_schedule.sh`.

## 2026-05-30 — Feed browser automation plan (30/90)

- **Triggered:** User asked about browser feed scroll + 30 comments in 90 min vs 3–5/day queue.
- **Learned:** Composio cannot discover feed; browser required for volume; ToS/DOM risks; hybrid browser discover + Composio post is best path.
- **Skill updates:** proactive-comments-plan.md rewritten (browser-first, 30/90 goal, Playwright phases).

## 2026-05-30 — Notion sync from Buffer response (not separate poller)

- **Triggered:** User asked to update Notion directly from Buffer MCP response when posted.
- **Learned:** `customScheduled` create_post returns `scheduled` only; at publish time use same `get_post` fields → Notion; Cursor can notion-update-page inline when `sent`.
- **Skill updates:** Buffer response table in SKILL §4; §6 sync-notion; `lib/notion_sync.py`; golden_hour `sync-notion` command.

## 2026-05-30 — Post-live Notion sync + proactive comments plan

- **Triggered:** User asked to implement post-live sync and plan proactive niche comments; dropped poll/video/metrics/carousel-comment scope.
- **Learned:** `post_live_sync.py` maps campaigns + Scheduled rows → Buffer `sent` → Notion `Posted` + URN block; needs `NOTION_TOKEN` in zshrc.
- **Skill updates:** §6 post-live sync; proactive-comments-plan.md; golden_hour_watch runs sync each tick.

## 2026-05-30 — Zapier disabled; automation matrix; drop metrics

- **Triggered:** User disabled Zapier webhook; asked what formats are automated and skill cleanup.
- **Learned:** No Zapier fallback; metrics section deferred; Buffer MCP is sole schedule path.
- **Skill updates:** Automation coverage table; Zapier marked disabled in SKILL + reference; metrics removed; golden hour → `watch` + launchd.

## 2026-05-30 — Moved to LinkedIn Automation folder

- **Triggered:** User asked to consolidate automation files under `LinkedIn Automation/`.
- **Learned:** New root `~/LinkedIn Automation/`; manifest + SKILLS_INDEX paths updated.
- **Skill updates:** `golden_hour.py` path references in SKILL.md.

## 2026-05-30 — Golden hour auto-reply skill

- **Triggered:** User requested automatic comment replies without approval.
- **Learned:** New `linkedin-golden-hour` skill + `golden_hour.py`; Composio comments work on API posts; Buffer shares may 404.
- **Skill updates:** Golden hour section → auto mode + link to golden-hour skill; checklist item 7 updated.

## 2026-05-29 — CON-138 scheduled + mandatory strategy fetch

- **Triggered:** User asked schedule per May 2026 strategy; skill must reference strategy doc each time.
- **Learned:** Tue 3 Jun 2026 10:00 IST · Buffer `6a19809c417d9b6a6a946636` · PDF `1Iv9nNTSBoU10l9dAYitCVEQIDrrV4Hbj`.
- **Skill updates:** Mandatory `notion-fetch` `36f3dffe-a139-8195-9dac-f3b5a76003b7` at start of schedule/publish; checklist reordered.

## 2026-05-29 — CON-138 cover layout + branding polish

- **Triggered:** Title overlapped header on slide 1; user wanted subtle branding upgrade, black primary.
- **Learned:** Reposition cover title below header band; @rawshn `#00D4AA` on all slides; PDF v2 `1CngATX9xhf46QnVK1k_3Ty1SXSUUL8oT`.
- **Skill updates:** none (workflow note: fix cover title `top` ~360 after long titles).

## 2026-05-29 — CON-138 branded from Full-Stack PM template

- **Triggered:** User wanted carousels branded like Full-Stack PM deck (photo, name, @rawshn).
- **Learned:** `copy-design` DAF4WMk_grY + edit transaction → DAHLC_5OJsQ; PDF `1iM0XmeGUhoEBRg4gJyGqEtbs3e0y6Al8`; 12 slides incl. Follow Me.
- **Skill updates:** Template-copy workflow promoted over AI-only generate.

## 2026-05-29 — CON-138 Canva MCP 1:1 carousel

- **Triggered:** User wanted eye-catching design + 1:1 layout (not plain Slides).
- **Learned:** `generate-design` presentation + `resize-design` 1080×1080 → `DAHLC7DxIy8`; Drive PDF `1-kIVLVjFNMjps-4KfDXi_ES0GOK-rKvu`; cover title verified; slide 1 may include placeholder subtitle to remove in Canva.
- **Skill updates:** Canva MCP primary for carousels; Slides demoted to draft-only.

## 2026-05-29 — CON-138 carousel via Google Slides (automated)

- **Triggered:** User chose Google Slides over Canva for CON-138 rebuild.
- **Learned:** `GOOGLESLIDES_CREATE_SLIDES_MARKDOWN` + export + `UPLOAD_FROM_URL` + `CREATE_PERMISSION` → Buffer-ready PDF; deck `1_qN9ecf-1rtrWhrClR44nMzpFzdMm3-DbvxWLr-w5Fg`, PDF `1lf_AhMQrag6CX9mj6BdV8ogfhuhyNF-b`; slide 1 title verified.
- **Skill updates:** Promoted Google Slides as primary carousel path in `SKILL.md`.

## 2026-05-29 — CON-138 cancel: PDF/title mismatch

- **Triggered:** User flagged wrong carousel PDF vs post title; cancel schedule.
- **Learned:** Notion attached `Carousel_Post_-_Full-Stack_PM.pdf` ≠ title-specific deck; always verify PDF before `create_post`. Deleted Buffer `6a1977f5932246f1065b9b78`.
- **Skill updates:** Pre-flight carousel check in `SKILL.md`.

## 2026-05-29 — CON-138 carousel scheduled via Buffer MCP

- **Triggered:** User step 2 — repost + carousel.
- **Learned:** Drive file `1uUzdJ3ipV2jzaGYdRj8WOFMa-6j5vTlB` was wrong asset for CON-138.
- **Skill updates:** superseded by cancel entry.

## 2026-05-29 — Skill rewrite (Buffer MCP primary)

- **Triggered:** User asked to update posting skill + next steps after Buffer MCP test.
- **Learned:** `create_post` + `customScheduled` + `dueAt` works; channel/org IDs stable; Zapier demoted to fallback.
- **Skill updates:** Full `SKILL.md` + `reference.md` routing; manifest description.

## 2026-05-29 — Buffer official MCP

- **Triggered:** User provided Buffer MCP URL + token.
- **Learned:** `https://mcp.buffer.com/mcp` exposes `create_post`, `list_channels`, etc.; token in `BUFFER_MCP_TOKEN` env (not skill/git).
- **Skill updates:** `~/.cursor/mcp.json` + reference routing.

## 2026-05-29 — Composio for text; one Zap for carousel

- **Triggered:** User asked if Zap A (text) is needed vs Composio.
- **Learned:** Text/image via Composio; single Buffer Zap sufficient for PDF carousels on Free.
- **Skill updates:** Notion + SKILL routing simplified to 1-Zap minimal.

## 2026-05-29 — Free plan: three webhooks

- **Triggered:** User chose Zapier Free over Paths.
- **Learned:** Clone Zap twice; separate text/image/PDF hooks; Cursor routes by `content_type` + payload fields.
- **Skill updates:** Notion step-by-step clone guide; SKILL publish routing table.

## 2026-05-29 — Repost + media Zap setup

- **Triggered:** User asked to repost old Content Library item and configure image/PDF carousels.
- **Learned:** Queued text repost `083ada63…` (PM Gems); Notion PDF URLs not public for Buffer; Paths or 3 hooks for media.
- **Skill updates:** Notion Zap page media section; `reference.md` Zapier media notes.

## 2026-05-29 — Zapier → Buffer verified live

- **Triggered:** User fixed Text mapping; retest landed in Buffer queue.
- **Learned:** Map **Text** → `commentary` (not `Object.to_json(Raw Output)`); retest trigger if fields missing in picker.
- **Skill updates:** Notion setup page has live webhook; pipeline confirmed working.

## 2026-05-29 — Zapier Catch Hook live

- **Triggered:** User shared webhook URL after Zap setup.
- **Learned:** Catch Hook `4365665/…` returns 200; Buffer step fails if **Text** not mapped to `commentary`.
- **Skill updates:** Webhook URL stored on Notion setup page `36f3dffe-a139-81d9-939b-e062e1e9d771` (not in git).

## 2026-05-29 — Depth Score strategy page (user research)

- **Triggered:** User pasted May 2026 LinkedIn ecosystem report; asked short Notion update.
- **Learned:** First-comment links now ~60% penalty; carousels 6–9 slides; IST windows; commenting 4-part framework.
- **Skill updates:** Links rule → Featured only; Notion page `36f3dffe-a139-8195-9dac-f3b5a76003b7`.

## 2026-05-29 — Zapier + Buffer automation path

- **Triggered:** User asked to link Zapier for ~100% LinkedIn posting via Cursor.
- **Learned:** Composio has no Zapier toolkit; Buffer+Zapier Catch Hook covers PDF carousels; Composio remains for text/image/comments.
- **Skill updates:** New Notion setup page `36f3dffe-a139-81d9-939b-e062e1e9d771`; SKILL publish routing updated.

## 2026-05-29 — Notion sync (workflow page + pipeline reset)

- **Triggered:** User asked to update Notion with new info and mark prior posts done.
- **Learned:** ~129 Content Library rows updated to `Posted`; hub workflow page `36f3dffe-a139-8108-98d2-e9daff72881a`; Getting Started + Guidelines + Algorithm + Persona + Starter Prompt synced.
- **Skill updates:** none (Notion is source of truth for IDs in reference).

## 2026-05-29 — Initial skill from Notion audit

- **Triggered:** User request to review LinkedIn Notion system and set up posting workflow/skill.
- **Learned:** Pipeline is **Content Library** DB (`753369dc…`) with Status calendar; hub at LinkedIn Resource `1d63dffe…`; persona/guidelines/prompt pages; Composio `LINKEDIN_CREATE_LINKED_IN_POST` available; 2026 algorithm favors carousels + niche consistency over polls; SMM onboarding page contains plaintext credentials (excluded from skill).
- **Skill updates:** Created `SKILL.md`, `reference.md`; registered in manifest + SKILLS_INDEX.
