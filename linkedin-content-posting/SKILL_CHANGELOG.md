# linkedin-content-posting changelog

Rule: `.cursor/rules/skill-self-improvement.mdc`

## 2026-07-01 — Copy review gate + Notion pipeline full URLs

- **Triggered:** User flagged weak ChiefDesk/BASB carousel copy; asked for expert writer review before Canva; Notion pipeline must use full clickable Canva + Drive URLs, not bare IDs.
- **Learned:** Draft caption + slides in Notion first; expert pass before `copy-design`. Pipeline table: Canva `edit_url`, Drive `view` + Buffer `uc?export=download` links. CON-167 Buffer `6a4498511a8d4d6ab1a2d1d6` carousel refresh.
- **Skill updates:** Workflow checklist step **3b** (copy review before Canva); Pipeline block table with full `https://` URLs; carousel creation gate references 3b.

## 2026-06-24 — CON-166 polish (agent-era PM thesis)

- **Triggered:** Full workflow rerun: disguised portfolio / open-for-opportunities text post; avoid CON-165 feature tour; richer SHA-256 dedup beat from `rawshns-health-hub` (`dedup.ts`, `body-metrics.ts` sync/update logic).
- **Learned:** Text-only (#3 format) fits thesis + recruiter signal without repeating CON-165 image carousel. Thu 25 Jun 10:05 IST next slot after Wed CON-165. Buffer `edit_post` on `6a3b0a519247fdcf91345b2d`; Notion CON-166 `3883dffea139810d9320db22033a9768`. Hashtags: #ProductManagement #BuildInPublic #OpenToWork (PM + builder + opportunity pyramid).
- **Skill updates:** none.

## 2026-06-24 — Agent-era PM opportunities post (CON-166)

- **Triggered:** User scheduled new open-for-opportunities / PM thesis post for Thu 25 Jun 10:05 IST; prior draft agent had not finished Buffer/Notion sync.
- **Learned:** Text-only thesis post (SHA-256 dedup beat from Health Hub, what/why vs how, PM class naming question, open-to-work CTA). Buffer `create_post` `6a3b0a519247fdcf91345b2d`; CON-165 `6a3adf9f09a816a60cbcdfa8` untouched (Wed). Notion `3883dffea139810d9320db22033a9768` · Posting on 2026-06-25 · Status Scheduled. Hashtags: #ProductManagement #BuildInPublic #OpenToWork.
- **Skill updates:** none.

## 2026-06-24 — Personal Health Hub hashtag trim (3 tags)

- **Triggered:** User requested researched 3-hashtag swap on CON-165; drop all five prior tags (#ProductManagement #BuildInPublic #AI #HealthTech #FullStackPM).
- **Learned:** 2025-2026 guidance favors exactly 3 intent-matched tags (pyramid: community + niche vertical + builder narrative). Picked #IndieHackers (solo builder audience), #DigitalHealth (health data unification, less saturated than #HealthTech), #LearnInPublic (build-journey share without #BuildInPublic). Buffer `edit_post` text-only on `6a3adf9f09a816a60cbcdfa8`; 6 images unchanged. Notion `3883dffe-a139-8144-958f-d32091b53da1` Hashtags section added. Wed 24 Jun 10:05 IST (`2026-06-24T10:05:00+05:30`) unchanged.
- **Skill updates:** none.

## 2026-06-24 — Personal Health Hub Gemini stopgap beat

- **Triggered:** User added interim Gemini-app beat (upload screenshots, AI coach, no charts/persistence) to CON-165; PM/builder voice bridge after fragmentation silos, before "So I made them talk."
- **Learned:** One beat between problem and solution clarifies the gap (coaching without unified viz + persistence). Buffer `edit_post` text-only on `6a3adf9f09a816a60cbcdfa8`; 6 images unchanged. Notion `3883dffe-a139-8144-958f-d32091b53da1` Body synced. Wed 24 Jun 10:05 IST (`2026-06-24T10:05:00+05:30`) unchanged.
- **Skill updates:** none.

## 2026-06-24 — Personal Health Hub builder close swap

- **Triggered:** User replaced reflective/teaser close ("Personal Health Hub is for me first" / "Already on the next project") with PM-voice builder pivot: Cursor, zero budget left, not-very-good coding skills, onto next builder projects.
- **Learned:** Close sits after honest reflective paragraph, immediately before hashtags. Expert draft body restored in full; only final line changed. Buffer `edit_post` text-only on `6a3adf9f09a816a60cbcdfa8`; 6 images unchanged. Notion `3883dffe-a139-8144-958f-d32091b53da1` Hook/Body/CTA synced. Wed 24 Jun 10:05 IST (`2026-06-24T10:05:00+05:30`) unchanged.
- **Skill updates:** none.

## 2026-06-24 — Personal Health Hub technical + motivation copy refresh

- **Triggered:** User wanted richer PM-voice copy on CON-165: keep $20/Auto/boring-stack lead, add explicit stack (PWA, Vision OCR, Notion, CSV, Web Share Target, RAG coach, Recharts), siloed Android app chain (HealthSense→FitDays, Amazfit→Zepp, Strong), fitness motivation + "what you cannot measure" line, honest reflective close.
- **Learned:** Hook order still wins: cost/Auto → 2-night boring stack → motivation → siloed apps → technical bullets → Android one-liner → reflective close. Buffer `edit_post` text-only on `6a3adf9f09a816a60cbcdfa8`; 6 mobile images unchanged. Notion `3883dffe-a139-8144-958f-d32091b53da1` Hook/Body/CTA synced. Wed 24 Jun 10:05 IST (`2026-06-24T04:35:00Z`) unchanged.
- **Skill updates:** none.

## 2026-06-24 — Personal Health Hub 6-image mobile carousel swap

- **Triggered:** User supplied 6 new native mobile screenshots to replace 2 cropped images on CON-165 before Wed 24 Jun 10:05 IST publish.
- **Learned:** Native 465×1024 Android shots need no status-bar crop. Portfolio path `public/assets/health-hub-mobile-01-coach.png` through `06-fitness.png` → `https://rawshn.com/assets/...` after `vercel deploy --prod`. Buffer `edit_post` accepts all 6 images on LinkedIn (no 4-image cap hit). `get_post` confirms dimensions + URLs post-edit. Copy unchanged; Notion `3883dffe-a139-8144-958f-d32091b53da1` Assets + Buffer image count updated.
- **Skill updates:** none.

## 2026-06-24 — Personal Health Hub key-message restore (cost + boring stack lead)

- **Triggered:** User said key message was lost after app-source/Android edits; restore $20 Cursor budget + standard-software skill insight as primary takeaway; app ecosystem details as supporting context only.
- **Learned:** CON-165 hook order matters: cost → boring-stack PM-engineer skill → 2-night proof → product context → Android one-liner → teaser. Replaced agent 0649ff70 copy (opened with Strong/FitDays/Zepp) entirely. Buffer `6a3adf9f09a816a60cbcdfa8` + Notion `3883dffe-a139-8144-958f-d32091b53da1` synced; Wed 24 Jun 10:05 IST unchanged; images unchanged.
- **Skill updates:** none.

## 2026-06-24 — Personal Health Hub FitDays/HealthSense + Android openness

- **Triggered:** User refined CON-165 copy: FitDays = app, HealthSense = scale brand; add thoughtful Android openness vs Apple walled-garden builder insight (custom PWA, share targets, Coach Stryder).
- **Learned:** Scale telemetry wording: "body composition through FitDays, the app for my HealthSense scale." Android paragraph belongs after product features, before build-honesty block. Wed 24 Jun 10:05 IST (`2026-06-24T04:35:00Z`) unchanged.
- **Skill updates:** none.

## 2026-06-24 — Personal Health Hub app-source clarity (Android)

- **Triggered:** User clarified data sources for CON-165 copy: Strong = gym set logging, FitDays = weighing-scale body composition, Zepp = Amazfit Active sleep + food logging, Android-only stack. Personal Health Hub naming only.
- **Learned:** User-facing copy should name the device/app role per source (not generic "gym/sleep/body comp"). Web Share Target is accurate Android ingestion hook from portfolio MDX. Wed 24 Jun 10:05 IST slot still valid (~8h ahead at edit time).
- **Skill updates:** none.

## 2026-06-24 — Personal Health Hub copy + mobile screenshot crop

- **Triggered:** User requested repo-grounded copy refresh (Personal Health Hub naming, 2-night build narrative, curiosity close) and mobile portrait screenshot crops before Wed 24 Jun 10:05 IST publish.
- **Learned:** Factual stack from `rawshn-portfolio/src/content/work/rawshns-health-hub.mdx` (Strong/FitDays/Zepp → Notion, Vision OCR, SHA-256 dedup, Coach Stryder RAG + Intelligence Dossier + 8-week telemetry, Recharts, Next.js PWA on Vercel). PIL venv crop to 420px width overwrote `health-hub-{coach,progress}.png`; Buffer `edit_post` on `6a3adf9f09a816a60cbcdfa8` updates text + assets in one call. **Portfolio deploy required** for `rawshn.com` URLs to serve new crops before Buffer fetches at publish.
- **Skill updates:** none.

## 2026-06-24 — Health Hub reschedule + copy revision (cost/skill framing)

- **Triggered:** User bumped Health Hub post to Thu 25 Jun 10:05 IST and reframed copy around build cost ($20 Cursor budget, Auto mode) and standard-software skill vs exotic AI.
- **Learned:** `edit_post` on existing scheduled ID (`6a3adf9f09a816a60cbcdfa8`) updates text + `dueAt` in one call; carry `assets` + `metadata` forward. Notion CON-165 (`3883dffe-a139-8144-958f-d32091b53da1`) `Posting on` + pipeline block updated in same turn.
- **Skill updates:** none.

## 2026-06-24 — Health Hub image post (dual screenshots)

- **Triggered:** Autonomous Health Hub LinkedIn post: draft, Notion row, Buffer schedule.
- **Learned:** Portfolio screenshots at `rawshn-portfolio/public/assets/health-hub-{coach,progress,preview}.png` are publicly served at `https://rawshn.com/assets/...` (no Drive upload needed for Buffer). Buffer `create_post` accepts multiple `image` assets for LinkedIn. `cleanup-content-library` CLI failed locally (SSL cert verify); Notion MCP cleanup still viable in Cursor. Wed 24 Jun 2026 10:00 IST slot used per strategy doc.
- **Skill updates:** none.

## 2026-06-16 — Notion Posted auto-sync fix (NOTION_CONTENT_LIBRARY_DB default)

- **Triggered:** User reported Notion board never updates to Posted after Buffer publish; fix + feed engage.
- **Learned:** `cleanup-content-library` crashed immediately when `NOTION_CONTENT_LIBRARY_DB` unset — `collect_mappings()` raised before any Buffer/Notion reconciliation. Default DB ID `753369dc15fb4b3c82dd9c88cb753c3c` (Content Library) + graceful pipeline-scan fallback fixes launchd/CLI without zshrc env. Verified: 1 row `Scheduled` → `Posted` (`3803dffe-a139-81f7-bc7d-cab7d5f463df`, Buffer `6a302dc712418296f2223ed6`).
- **Skill updates:** `lib/notion_sync.py` default DB ID; `.env.example` documents override.

## 2026-06-16 — PARA preview layout fix + re-export (carousel + infographic)

- **Triggered:** User reported text/image alignment issues on PARA preview Canva carousel and infographic; re-export, Drive, Buffer, Notion refresh.
- **Learned:** Carousel `DAHMqh_yc88`: cover title `left:92 top:360` + manual `\n` breaks; all title/body blocks `text_align:start` at `left:92` with titles `top:470` and body `top:588`; removed duplicate profile photo page 2. Infographic `DAHMqvW7-gI`: normalized section text to `left:92`, images to `left:92` / `left:700`, footer `top:2520`. Drive in-place update via `GOOGLEDRIVE_UPLOAD_UPDATE_FILE` (same IDs). Carousel `create_post` + `draftId` → Buffer `6a306771c5cca7fb316a4366` Wed 18 Jun 10:05 IST. Infographic asset refresh on `6a30645e2cefeda2a31bc304` Thu 19 Jun 10:05 IST unchanged.
- **Skill updates:** none (re-run of existing layout rules).

## 2026-06-16 — CON-163 PARA infographic Thu schedule

- **Triggered:** Ensure PARA Preview infographic scheduled Thu 19 Jun 10:05 IST after prior Buffer ID deleted.
- **Learned:** Deleted Buffer IDs return `Post not found`; reschedule from existing draft via `edit_post` with `mode: customScheduled`, `dueAt`, and **`saveToDraft: false`** (without it, post keeps `draft` status despite `dueAt`). CON-163 draft `6a30645e2cefeda2a31bc304` → scheduled Thu 19 Jun 2026 10:05 IST · Drive PNG `1A66W1_1TCum5mjtl0_VJXRqt_hsZcwnW` · Notion `3803dffe-a139-81ac-963c-cc3d099c5e3a` → **Scheduled**.
- **Skill updates:** none.

## 2026-06-16 — Content Type tagging + calendar swap policy (no delete)

- **Triggered:** User flagged Paperclip image post mis-tagged as carousel in Notion; asked to demote bumped posts instead of deleting.
- **Learned:** Notion `Content Type` must follow primary Buffer **asset** (`image` → `4. Image`, PDF `document` → `2. Carousel`), not Buffer `metadata.type` (single-image posts often still say `carousel`). Calendar swap: **new** Content Library row per new post; bumped rows → Notion **Ready** + Buffer `create_post`/`edit_post` with `saveToDraft: true`; avoid `delete_post` unless user explicitly discards. Restored CON-162/163 as Ready with drafts `6a30645a4b32b4b3c4018d7b` / `6a30645e2cefeda2a31bc304`; Paperclip on CON-164 (`3803dffe-a139-81c1-a5d8-cfed1c8895e7`, `4. Image`).
- **Skill updates:** `SKILL.md` § Content Type table + Calendar swaps (do not delete planned posts).

## 2026-06-16 — Paperclip screenshot replaces Wed slot; Fri PARA infographic cancelled

- **Triggered:** User screenshot of Paperclip/Projekt Rawshn dashboard; schedule Paperclip OSS post Wed with image; cancel Fri PARA infographic.
- **Learned:** `edit_post` on existing Buffer ID swaps PDF carousel → single image + new caption + `dueAt` in one call. Fri delete via `delete_post` (`6a304aa2d677f2362ccfcb63`). Drive upload to `Content & Media` folder `1VZ2ksX8UtBJb0O3RI68NBOLsQMHRWrCq` + `CREATE_PERMISSION` anyone/reader → Buffer `uc?export=download&id=`. Repurposed Notion CON-162 row (`3803dffe-a139-814d-bbad-f81d8190f548`); CON-163 → Rejected. Buffer `6a304a9b64a5ec97de565333` Wed 17 Jun 2026 10:05 IST · Drive `1pjXnVBrlCoTFRhPESgmCk-g-PwtNkydv`.
- **Skill updates:** none (workflow execution).

## 2026-06-16 — PARA preview carousel + infographic scheduled (Wed/Thu)

- **Triggered:** Full pipeline: Wed 8-slide carousel + Thu infographic for PARA dashboard preview; Notion + Buffer + Canva + Drive.
- **Learned:** AI-generated infographic (`generate-design` → `create-design-from-candidate`) blocks `export-design` until `copy-design` + optional `resize-design` (custom 1080×2700); edit via `start-editing-transaction` works on original ID. Carousel `copy-design` with `page_numbers` [1–8] may still return 12 pages — export with `format.pages: [1..8]`. Cover title overlap: reposition to `top:360` after long hooks. Buffer slots Wed/Thu 10:05 IST match channel schedule. Carousel `DAHMqh_yc88` · Drive PDF `1rExBZ8rgoSNDMkVXj0f_LSdN_qKhmnQj` · Buffer `6a304a9b64a5ec97de565333` · Notion `3803dffe-a139-814d-bbad-f81d8190f548`. Infographic `DAHMqvW7-gI` · Drive PNG `1A66W1_1TCum5mjtl0_VJXRqt_hsZcwnW` · Buffer `6a304aa2d677f2362ccfcb63` · Notion `3803dffe-a139-81ac-963c-cc3d099c5e3a`.
- **Skill updates:** none (workflow execution).

## 2026-06-15 — PARA preview posts (India market + persona bridge)

- **Triggered:** Deep research task: Wed carousel + Thu infographic previewing PARA dashboard for business leaders/freelancers; audience-building, no hard sell.
- **Learned:** India productivity/PKM is a paradox market (high app downloads, WhatsApp as de facto OS, horizontal note-taking crowded by Notion/Zoho; vertical/outcome SaaS wins). Honest “small market” framing works as builder credibility, not defeatism. Persona bridge: frame as **PM building personal OS** (strategy pillar 2: AI-assisted workflows), not productivity guru. Pair formats: carousel = market honesty + why PARA + build preview; infographic = framework/decision tree (different angle, saveable). India callout: observational stats (founder profiles +104% YoY, freelancers ~₹1,200/mo SaaS stack) not lecturing. No em/en dash clause separators in post/slide copy. Soft CTA: “what do you actually use?” + optional waitlist/DM, no pricing.
- **Skill updates:** none (research deliverable; patterns reusable for future PARA-preview content).

## 2026-06-15 — Manual Canva edit re-export (CON-161, 11 slides)

- **Triggered:** User manually updated Canva MCP carousel; asked to complete pipeline + schedule for tomorrow.
- **Learned:** After manual Canva edits, re-check `get-design-pages` (count may grow; CON-161 went 10→11 with follow CTA on page 11). Export all content pages. Pre-flight page 1 title still matched Notion Name. Drive v4: `1wM0DRYirpJXb2yWn469ZX04uSmPYzAn3`. Buffer `6a302dc712418296f2223ed6` document asset refreshed; dueAt unchanged Tue 16 Jun 2026 10:05 IST.
- **Skill updates:** none (workflow re-run).

## 2026-06-15 — Cover hook line breaks + left-align fix

- **Triggered:** User screenshot: justified cover headline with huge word gaps on MCP carousel ("Try in Agentic"); re-export + Buffer refresh.
- **Learned:** Cover needs manual `\n` in `replace_text` plus `format_text` `text_align: start` on all title/body blocks pages 1–10. MCP cover: `7 MCPs PMs\nShould Try in\nAgentic Workflows`. Open-source: `7 Open Source Tools\nEvery PM Should Try\nin 2026`. Template `DAF4WMk_grY` + `DAHMqHX1_ms` + `DAHMqNt-qds` committed. Drive v3 MCP: `19juEjyvh3ZnwBnstWjaf7Uc4u24ZzXfa`. Buffer `6a302dc712418296f2223ed6` document asset updated. Notion `3803dffe-a139-81f7-bc7d-cab7d5f463df`.
- **Skill updates:** `SKILL.md` § Carousel — cover hook line-break row + checklist.

## 2026-06-15 — Carousel text_align start refresh (MCP + open-source)

- **Triggered:** User reported justified body text still looked bad on scheduled MCP carousel; re-export both decks.
- **Learned:** `format_text` `text_align: start` on 19 body/title elements per deck (pages 1–10; skip name/handle/©). Drive v3: MCP `10qocxMwPBcHCcNN6Xul-1LVCNq1TpBcO` · open-source `1udbcq-cKmqVSMwr0tFPNOYJpl3cpIp33`. Buffer `6a302dc712418296f2223ed6` document asset → MCP v3. Notion MCP + open-source pages updated.
- **Skill updates:** none (re-run of existing layout rule).

## 2026-06-15 — Carousel layout: left-align + copyright footer

- **Triggered:** User asked for left-aligned carousel body text (not justified) and `© 2026 Roshan Raj Mishra` footer on branded template + live decks.
- **Learned:** Canva MCP: repurpose `@rawshn` text element → copyright at `top:1010, left:92`; merge `@rawshn` into name element. Template `DAF4WMk_grY` committed. MCP `DAHMqHX1_ms` + open-source `DAHMqNt-qds` pages 1–10 updated. Drive v2: MCP `1mjg5J8NFACE4l6hzXihgsOlC7G3dTyUE` · open-source `1Y8cQ3RJ97hVvLqenbNahWFKR0C8lnu1P`. Buffer `6a302dc712418296f2223ed6` document asset refreshed.
- **Skill updates:** `SKILL.md` § Carousel creation — layout & copy rules table (left-align, copyright, branding, no-dash copy).

## 2026-06-15 — MCP agentic workflows carousel (replaced open-source post)

- **Triggered:** User cancelled open-source carousel; wanted **7 MCPs PMs Should Try in Agentic Workflows** instead.
- **Learned:** Deleted Buffer `6a302ce02fea4bc95eb07849` · new Buffer `6a302dc712418296f2223ed6` · Drive `1mbYo2NYJKIaMMv5CVa_oc55_x4HEtJMN` · Canva `DAHMqHX1_ms` · Notion `3803dffe-a139-81f7-bc7d-cab7d5f463df`.
- **Skill updates:** none (workflow execution).

## 2026-06-15 — Open source PM carousel (Buffer Tue 10:05 IST)

- **Triggered:** User asked to schedule a PM carousel about open source projects for tomorrow via Buffer.
- **Learned:** Canva copy `DAHMqNt-qds` from Full-Stack PM template · 10 slides · Drive `1ceK3cSMSriKw5vUj55u4IK2e09lWeGtU` · Buffer `6a302ce02fea4bc95eb07849` · Notion `3803dffe-a139-81ff-b0a0-e2d096a1d063`.
- **Skill updates:** none (workflow execution).

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
