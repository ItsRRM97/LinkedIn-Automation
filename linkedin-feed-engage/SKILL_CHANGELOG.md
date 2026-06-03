# linkedin-feed-engage changelog

## 2026-06-03 — 30/30 continuous mode (user speed target)

- **Triggered:** User wants 30 comments in 30 minutes, no stopping between batches.
- **Learned:** 90–180s pacing + full reload each pick + parallel subagents stretched runs to ~90 min; `main` scroll + Load more during 45–60s waits keeps inventory without reload tax.
- **Skill updates:** config `session_minutes: 30`, delays 45–60s, `continuous_mode` / `single_agent_only`; SKILL § continuous rules + fast feed surfacing; `feed_engage_trigger.py` prompt reads config.

## 2026-06-03 — session completed 30/30 (home feed)

- **Triggered:** Subagents db1377d9 / e85bfc88 / finish pass from 26→30.
- **Learned:** `main` scroll + Load more surfaced late picks (Rajeev Roy, Teresa Torres, Dhrumil Barot, Adarsh Panda); session `status: completed` reconciles all parallel runs.
- **Skill updates:** none.

## 2026-06-03 — MCP feed scroll stall at 17/30

- **Triggered:** Subagent resume to 30 on home feed Top; session `posted: 17`.
- **Learned:** After ~15 comments, MCP feed often shows only 2–3 cards (hiring/promoted/suggested); `main#workspace` scroll maxes without loading more; Sort menu can flip to Recent — re-select Top + hard reload; Ant Murphy 5h + Abhinav Bhatt 1h strong picks when cards appear.
- **Skill updates:** none.

## 2026-06-03 — home feed only (user preference)

- **Triggered:** User rejected content-search discovery; wants engagement from account home feed (what LinkedIn shows others).
- **Learned:** Feed already on Sort by Top; Shruti Verma 3h PM pivot post strong home-feed target; subagent ran parallel — coordinate single browser.
- **Skill updates:** SKILL §3 discovery default = home feed Top only, no search unless user asks.

## 2026-06-03 — past-24h search mention workflow

- **Triggered:** Resume session to 30; content search `past-24h` + `date_posted`.
- **Learned:** `@partial` + slow type → listbox; **ArrowDown + Enter** selects first match when CDP click unavailable; verify `[data-type="mention"]` before submit; Chandrahas/venkatesh strong PM targets amid hiring noise.
- **Skill updates:** none.

## 2026-06-03 — CON-138 publish-day session resumed

- **Triggered:** User asked to start golden hour commenting after recent post (CON-138, Buffer `6a19809c417d9b6a6a946636`).
- **Learned:** Golden-hour auto-reply window had ended (~11:30 IST); feed session was armed at 10:04 but `posted: 0` until manual browser run; home Top feed mostly >12h — past-week PM search surfaced ≤12h targets (Masai 1h).
- **Skill updates:** none (operational run).

## 2026-06-02 — ≤12h posts, feed refresh, verified mentions

- **Triggered:** User reported low engagement; asked to only target posts ≤12h, refresh feed before each pick, and require real LinkedIn mention tags (not plain `@text`).
- **Learned:** Plain `@Author` in editor ≠ tagged mention; must verify `[data-type="mention"]` before submit; edit-mode listbox often omits post author — delete and re-post with listbox selection; feed must be refreshed each cycle to avoid stale cards.
- **Skill updates:** SKILL §1 refresh loop, §3 hard 12h age rule, §5 mention gate + CDP verify; config `max_post_age_hours: 12`, `refresh_feed_each_pick`, `require_verified_mention`; agent_prompt aligned.

## 2026-06-02 — Engaged posts after golden hour

- **Triggered:** User asked to comment on posts that already have engagement and performed well post–golden hour (not fresh zero-engagement Latest/24h).
- **Learned:** Past-week content search + home Top feed surfaces 1d–3d posts with reactions; skip polls (`Do you agree?`), hiring, connection-only comment locks; Naren M. often missing from @ mention list — plain-text name OK.
- **Skill updates:** SKILL §2 prefer engaged; `config.json` `prefer_engaged_posts` + discovery URLs.

## 2026-05-31 — Canonical publish_day_watch for all posts

- **Triggered:** User confirmed CON-138 and all future posts use `publish_day_watch.sh` only.
- **Learned:** Per-campaign launchd (CON-138 plist) and golden-hour-only schedule deprecated; CON-138 campaign JSON still supplies rich reply context via `buffer_post_id` match.
- **Skill updates:** README, content-posting §7, golden-hour publish-day section; legacy plists disabled.

## 2026-05-31 — Publish-day auto trigger (no approval)

- **Triggered:** User stopped manual session; asked for 30 feed comments auto on go-live during golden hour.
- **Learned:** Feed engage needs Cursor browser MCP — launchd can arm session when Buffer `sent`, but Mac + Cursor + LinkedIn login required; optional `cursor-sdk` + `CURSOR_API_KEY` for zero-click agent launch.
- **Skill updates:** `feed_engage_trigger.py`, `publish_day_watch.sh`, launchd plist, config `auto_mode` + `phase1_approval_limit: 0`, SKILL § publish-day automation.

## 2026-05-31 — @ mention tagging

- **Triggered:** User asked to tag authors directly, not plain-text names.
- **Learned:** Type `@` + partial name → listbox → click matching option; verify linked mention before submit. `browser_fill` won't create tags.
- **Skill updates:** Draft frame + §5 submit workflow with mention steps.

## 2026-05-31 — One post per comment

- **Triggered:** User redirected session away from stacking replies on one Product Growth thread.
- **Learned:** Prefer top-level comments on distinct feed posts; scroll/load-more before reusing same card.
- **Skill updates:** Niche filter section — explicit one-post-per-comment rule.

## 2026-05-30 — Initial Cursor browser skill

- **Triggered:** User chose Cursor browser for feed engagement; 30 comments / 90 min goal.
- **Learned:** Login at linkedin.com/login; agent loop scroll → filter → draft → browser submit; Phase 1 first 5 with approval.
- **Skill updates:** SKILL.md + config.json + state session logs.

## 2026-05-31 — Mention chip verification

- **Triggered:** Comment #4 on Ayush Muniya posted without a real tag (plain text); user asked to edit/fix.
- **Learned:** Editor had `[data-type="mention"]` only when listbox option clicked + rest typed slowly; edit-mode listbox skips post author; confirm posted comment has author **link** ref in snapshot.
- **Skill updates:** §5 chip CDP check, slow remainder typing, delete+repost over edit for broken tags.
