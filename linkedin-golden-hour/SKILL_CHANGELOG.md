# linkedin-golden-hour changelog

Rule: `.cursor/rules/skill-self-improvement.mdc`

## 2026-06-04 — CON-158 golden hour armed

- **Triggered:** User asked to start commenting for golden hour.
- **Learned:** CON-158 live (`urn:li:share:7468157097751461888`); first `watch` ticks had zero Gmail comment notifications; agent loop every 10m armed alongside existing `publish_day_watch.sh`.
- **Skill updates:** none.

## 2026-06-03 — Publish-day docs + cleanup CLI in scripts

- **Triggered:** Repo polish with `linkedin-content-posting`.
- **Learned:** `publish_day_watch.sh` calls `cleanup-content-library` first; `sync-notion` remains CLI alias.
- **Skill updates:** SKILL publish-day tick list; `~/Projects/LinkedIn Automation/` paths; `launchd/README.md`.

## 2026-06-02 — Fix: Notion sync crash blocks comment-watching

- **Triggered:** User started service; `golden_hour.py watch` crashed on Notion token missing.
- **Learned:** `sync_publish_state` tries Notion even when `NOTION_TOKEN` not set (launchd env gap). Core watch loop must not block on Notion sync. Fix: wrap `sync_notion_from_buffer_post` call in `try/except RuntimeError`; log warning to stderr, continue.
- **Skill updates:** none — fix is in `golden_hour.py`. Service now runs cleanly: active post CON-139 found, share URN resolved, comment replies fire when Gmail notifications arrive.

## 2026-05-31 — Canonical publish_day_watch (all posts incl. CON-138)

- **Triggered:** User confirmed single script path for every Buffer publish.
- **Learned:** Generic watcher + CON-138 `campaigns/CON-138.json` for rich themes; no per-post launchd.
- **Skill updates:** Publish-day section; deprecated CON-138 launchd + Cursor Automation schedule refs.

## 2026-05-31 — Publish-day orchestrator (feed engage trigger)

- **Triggered:** User stopped manual feed session; wants 30 feed comments auto on Buffer go-live.
- **Learned:** `publish_day_watch.sh` chains `watch` + `feed_engage_trigger.py`; launchd `com.rawshn.linkedin-publish-day-watch` replaces golden-hour-only job.
- **Skill updates:** Fallback install → `install_publish_day_schedule.sh`; cross-ref feed-engage skill.

## 2026-05-30 — Generic Buffer watch (`watch` command)

- **Triggered:** User asked for auto-reply on every Buffer-published post, not just CON-138.
- **Learned:** `watch` polls Buffer sent posts in 90m window · auto-campaign from caption · manual campaign matched by `buffer_post_id` · `config.json` skip list.
- **Skill updates:** Generic watch section + Cursor Automation prefill **Buffer Watch**.

## 2026-05-30 — Cursor Agent Automation (preferred schedule)

- **Triggered:** User asked for 10:00 automation via Cursor Automations tab, not launchd.
- **Learned:** `open_automation` prefill with cron `0 10 3 6 *` + golden hour agent prompt; backend create_automation MCP not enabled in session.
- **Skill updates:** Automations tab as recommended path; launchd demoted to fallback.

## 2026-05-30 — launchd schedule for CON-138 golden hour

- **Triggered:** User cannot manually start loop at 10:00; asked for automation.
- **Learned:** `scripts/golden_hour_watch.sh` + launchd plist fires Tue 3 Jun 2026 10:00 local · self-unloads after 90m.
- **Skill updates:** Scheduled run section in SKILL.md + README install command.

## 2026-05-30 — Moved to LinkedIn Automation folder

- **Triggered:** User consolidated automation under `~/LinkedIn Automation/`.
- **Learned:** Skills moved from `~/.cursor/skills/`; registry paths updated.
- **Skill updates:** Path examples in SKILL.md.

## 2026-05-30 — Auto-reply golden hour (no approval)

- **Triggered:** User requested fully automatic comment replies using post context + comment text, no approval.
- **Learned:** Composio `LINKEDIN_CREATE_COMMENT_ON_POST` works on API-created shares; Buffer-published shares often return 404/403 on comment API · actor `2P7nq91zOA` · Gmail `from:linkedin.com (commented OR replied)` for detection · no list-comments API.
- **Skill updates:** New skill + `golden_hour.py` tick/reply commands; campaigns CON-138 + TEST-PIPELINE.
