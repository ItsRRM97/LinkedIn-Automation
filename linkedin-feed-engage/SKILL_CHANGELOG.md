# linkedin-feed-engage changelog

## 2026-07-02 — Remaining devex concerns (SKILL, GROQ preflight, feed yield)

- **Triggered:** User asked to address remaining devex concerns.
- **Learned:** `GROQ_API_KEY` was absent from `~/.zshrc` (preflight catches before feed fetch). Home feed often group/company/promoted noise; `lib/feed_discover.py` drops noise at parse and falls back to `linkedincli feed user <slug>` when home eligible &lt; `thought_leader_fallback_min_eligible`.
- **Skill updates:** SKILL.md restructured — daemon default at top, browser legacy below; publish-day section updated.

## 2026-07-02 — devex-review: classify bug + docs alignment

- **Triggered:** `/devex-review` on code, docs, bugs.
- **Learned:** `classify_post()` wrongly returned `job_posting` for every PM author (broken merge); fixed `job_posting` branch. Default LLM provider should be `groq`. `prefer_engaged_posts` was config-only until wired in classify. linkedincli `*socialDetail` refs need `included` index for reaction counts. Feed posts via Composio only (linkedincli write 400).
- **Skill updates:** promoted daemon path to README + `FEED_ENGAGE_DAEMON.md`; SKILL.md daemon section still pending full pass.

## 2026-07-02 — Post-type comment styles + filter overhaul

- **Triggered:** User wanted opinion posts to get follow-up questions only; career/job posts get acknowledgment without questions; fix niche/recency/filters.
- **Learned:** `post_age_hours` from actor `subDescription` (not raw `createdAt`); `niche_keywords_strong` + `min_niche_score`; `lib/feed_post_classify.py` routes `opinion_question` vs `career_ack`; Composio post path unchanged.
- **Skill updates:** pending — align SKILL § success-story skip with career_ack exception.

## 2026-07-02 — Composio comment posting (linkedincli write broken)

- **Triggered:** User asked to run live feed commenting.
- **Learned:** linkedincli `engage comment`/`react` return HTTP 400; Composio `LINKEDIN_CREATE_COMMENT_ON_POST` works with `urn:li:share:` / `urn:li:ugcPost:` from feed `updateMetadata.shareUrn`. Feed fetch via linkedincli; post via `lib/composio_linkedin.py`.
- **Skill updates:** pending — document Composio post path in daemon docs.

## 2026-07-02 — Cookie import script + daemon demo blockers

- **Triggered:** User asked for `scripts/import_linkedin_cookies.sh` and live demo (5 comments).
- **Learned:** Groq API returns Cloudflare 1010 from Python without `User-Agent`; add header in `_groq_chat`.
- **Skill updates:** pending — import script + `--force` in SKILL.md runner section.

## 2026-07-02 — Hands-off CLI daemon (OpenRouter + linkedincli)

- **Triggered:** User wanted hands-off feed engage tied to Buffer publish window, 100/day cap, OpenRouter free NVIDIA models.
- **Learned:** `feed_engage_daemon.py` + `lib/feed_*` replace browser MCP hot path; `publish_day_watch.sh` calls daemon when `runner_mode=daemon`. Cursor Cloud Agent not suitable for LinkedIn cookie automation when laptop off.
- **Skill updates:** pending — document daemon in SKILL.md § runner modes.

## 2026-06-19 — Retry success, 1/30 Vik Gambhir

- **Triggered:** User retry after MCP drop; resume feed engage.
- **Learned:** `browser_navigate` `newTab: true` reliable when `browser_tabs` list empty. Home feed dry for &lt;8h on roster (Cutler 12h, Hiten 15h, Melissa 19h); Vik Gambhir 3h Zomato UX post eligible on feed Top. Scroll-into-view needed before Comment click on lower cards.
- **Skill updates:** none.

## 2026-06-19 — Session start, MCP drop before first comment

- **Triggered:** User: start feed engage in browser.
- **Learned:** `browser_tabs` `new` timed out on glass browser view; `browser_navigate` with `newTab: true` succeeded (viewId `f96aa9`, feed loaded, logged in). `cursor-ide-browser` MCP dropped immediately after `browser_lock` (server unavailable on scroll/snapshot).
- **Skill updates:** none.

## 2026-06-16 — Feed-first, &lt;8h posts, roster → top 15 active

- **Triggered:** User: posts strictly &lt;8h; prefer home feed over thought leaders; prune inactive (&gt;5d); then cap roster at 15 most active.
- **Learned:** Browser audit 2026-06-16: top freshness = Cutler 41m, Hiten Shah 2h, Melissa 5h, Roman 7h, Aakash 19h, then six at 1d (Paul Adams, Elena, Janna, Scott, Lenny, Itamar), Sachin + Fareed 4d, April + Nikhyl 5d. Dropped 35 (inactive &gt;1w, wrong slug `debliu`/`hwalker`/`noahweiss`, empty `teresatorres`, Gibson ~1mo, Jeff Patton ~7mo, etc.). Fast-type after mention chip breaks `ql-mention`; use CDP `insertText` for body after listbox select.
- **Skill updates:** `config.json` `target_mode: home_feed`, `max_post_age_hours: 8`, `max_post_age_strict`, `thought_leader_count: 15`; `thought_leaders.json` v2 top-15 with `newest_post` audit field; SKILL §3 discovery order, §3a/3b/3c, examples, checklist.

## 2026-06-16 — Resume main-agent session (3/30)

- **Triggered:** Continue Feed Engage from 1/30 after context summary; complete Aakash + roster sweep.
- **Learned:** Aakash Matthew Wensing post (19h) good thread target; mentioning "Customer.io" in body can auto-attach link preview (posted anyway). Elena Verna 1d "3 hours" post at 262 comments is high-engagement pick. Gibson Biddle dry (newest ~1 month). Mention listbox: type `@First` then slow ` Lastname`, click `option` not `button`.
- **Skill updates:** none.

## 2026-06-16 — Subagent browser scope fix + blocked resume (5/30)

- **Triggered:** Resolve subagent `browser_tabs` blocker; resume from `next_leader_index: 10` (Nikhyl Singhal).
- **Learned:** `cursor-ide-browser` tabs are agent-context scoped — Task subagents do not see parent's 8+ LinkedIn tabs. `browser_tabs` list empty; `browser_tabs` `new` returns `viewId` but `browser_navigate` still fails ("No browser tab available") in subagent. Main agent chat is the only reliable execution context. SDK `Agent.prompt` has same isolation risk — default trigger now main-agent prompt only (`FEED_ENGAGE_SDK_LAUNCH=1` to opt in).
- **Skill updates:** SKILL § **Browser MCP scope** + §0 browser guard + blocked session JSON; `.cursor/rules/linkedin-feed-engage-single-agent.mdc`; `trigger_feed_engage_agent.sh` SDK gated; `feed_engage_trigger.py` prompt warns no Task handoffs.

## 2026-06-16 — Resume blocked (no browser tab, 3/30)

- **Triggered:** Continue from `next_leader_index: 9` (Roman Pichler); 3 posted, 4 skipped, 27 remaining.
- **Learned:** `browser_tabs` list empty in subagent; prior `browser_view_id` `0544c7` unavailable. Session set `status: blocked`.
- **Skill updates:** none.

## 2026-06-16 — Resume blocked (no browser tab, 2/30)

- **Triggered:** Resume continuous 30/30 from `next_leader_index: 3` (Shreyas Doshi); user required `browser_tabs` list first.
- **Learned:** `browser_tabs` returned empty in subagent context; prior `browser_view_id` `b2c72e` not available. Session left at posted=2, skipped=1.
- **Skill updates:** none.

## 2026-06-16 — Feed engage blocked (browser MCP no tab)

- **Triggered:** User asked to run feed commenting after Notion Posted fix.
- **Learned:** `cursor-ide-browser` `browser_navigate` returns "No browser tab available" in subagent context (same as 2026-06-10). Composio has `LINKEDIN_CREATE_COMMENT_ON_POST` but no roster activity discovery; feed engage requires Cursor browser with LinkedIn logged in. `feed_engage_trigger.py` → idle (no posts in golden-hour window today).
- **Skill updates:** none.

## 2026-06-10 — 30/30 roster completion (48h override)

- **Triggered:** Resume 25→30/30 with `thought_leader_activity`, 48h high-engagement override, no-dash comments.
- **Learned:** Roster very dry inside 48h after ~20 leaders scanned (wrong profiles, reposts-only, 404s, empty activity). Final five: Melissa Perri (22h/46r), Paul Adams (19h/274r), Sachin Rekhi (1d/~31r), John Cutler (2d/53r), Lane Shackleton (4h/2r — only fresh original left). Submit often needs CDP click on `.comments-comment-box__submit-button`; mention via slow-type + listbox `option` click. `hwalker` = wrong person (Heidi Walker); `noahweiss` = wrong Noah W.
- **Skill updates:** none.

## 2026-06-10 — No dashes in comment body

- **Triggered:** User rule — no dashes in LinkedIn comments; set as durable rule across feed engage.
- **Learned:** Em/en dashes and hyphen clause separators read AI-generated; periods, commas, or colons read more natural. `@Name` chip prefix is fine; body after the mention must avoid dash punctuation. Compound terms (`build-to-learn`) and quoted hyphens still OK.
- **Skill updates:** SKILL §4 **No dashes** subsection + quality bar + checklist; `agent_prompt.txt` NO DASHES block; workspace rule `.cursor/rules/linkedin-comments-no-dashes.mdc`; active session `comment_style_rules.no_dashes` for remaining picks.

## 2026-06-10 — home_feed_top exhausted at 18/30

- **Triggered:** Resume home_feed_top from 12/30; aggressive scroll+Load-more until dry or 30/30.
- **Learned:** Four scroll/load cycles surfaced 6 more eligible PM posts (Sahil Garg, Kevin Thomas, Amit Mutreja, Usman Zahid, Ankit Shukla, Lokesh Gupta). After 18/30, remainder is already-commented, success stories, promoted/company, >24h, or off-topic — honest `hard_stopped` at 18. Submit via CDP parent-walk to Comment button when click intercepted; mention via listbox `option` click (not `button`).
- **Skill updates:** none.

## 2026-06-10 — Post relevance enforcement (generic comment fix)

- **Triggered:** User complaint — feed comments “do not appear relevant to the post”; fix for current and future runs.
- **Learned:** Today’s session (`session-2026-06-10.json`, 2 posted): Lenny comment cited Fadell frame but injected publish-day “enterprise onboarding” tangent + generic “stakeholders patient through business-fix phase” closer; Janna comment paraphrased webinar title only, then generic B2B/tradeoff/AI-roadmap platitudes — both fail “could this apply to another post?” Root causes: drafting from truncated card/snippet without **See more**, part 2 thematic not lexical, publish-day topic bleed, template closers.
- **Skill updates:** SKILL §3 (MUST expand See more), §4 **Post relevance** table + bad/good examples, session `post_snippet_referenced` field, quality bar + checklist; `agent_prompt.txt` relevance block.

## 2026-06-10 — Roster slug fixes + 24h window resume

- **Triggered:** Resume session from `next_leader: romanpichler` after hard-stop at 1/30; user wants high-engagement posts ≤24h (not 12h).
- **Learned:** Seven broken roster slugs verified via web search: `aakashg0`→`aagupta`, `hitenism`→`hnshah`, `fareedmosavat`→`fareed`, `johncutlerdept`→`johnpcutler`, `danolsen`→`danolsen98`, `petrawille`→`petra-wille-b8b1329`; `melissaperri`→`melissajeanperri` (wrong PR profile). `config.json` already had `max_post_age_hours: 24`, `prefer_engaged_posts: true`, delays 15–25s.
- **Skill updates:** `thought_leaders.json` slug corrections; session `roster_fixes` block extended.

## 2026-06-10 — Resume hard-stop: 12h window roster dry

- **Triggered:** Resume continuous run from `next_leader: shreyasdoshi` toward 30/30.
- **Learned:** With `max_post_age_hours: 12`, only Lenny had an eligible post today (already commented). Next-closest: Teresa 14h, Janna 18h, Elena 17h. Six roster slugs 404 (`aakashg0`, `hitenism`, `fareedmosavat`, `johncutlerdept`, `danolsen`, `petrawille`); `melissaperri` resolves to wrong person. 30/30 in one session needs either relaxed age window or multi-day roster cadence.
- **Skill updates:** none.

## 2026-06-10 — First comment posted (Lenny Rachitsky)

- **Triggered:** User "try" — resume session from `next_leader: lennyrachitsky`.
- **Learned:** `cursor-ide-browser` available in this agent context (feed tab pre-open, logged in). Mention chip via `@Lenny` + listbox select (`ql-mention`); plain `@Name` typing alone fails. Post 1 on Lenny activity (7h, Tony Fadell three generations) — 20→21 comments after submit.
- **Skill updates:** none.

## 2026-06-10 — Start feed engage; browser MCP unavailable (subagent)

- **Triggered:** User asked to start feed commenting and fix browser MCP access.
- **Learned:** `cursor-ide-browser` is a Cursor built-in (not in `~/.cursor/mcp.json`); descriptors exist under `~/.cursor/projects/Users-rawshn-LinkedIn-Automation/mcps/` but were missing from `Users-rawshn-Projects-LinkedIn-Automation/mcps/` — symlink alone does not register the server. This subagent context gets `CallMcpTool` → "MCP server does not exist"; browser MCP worked earlier today in parent window `wb0` (allowlist log). `feed_engage_trigger.py --dry-run` → idle (golden-hour window passed); session already armed from CON-159 publish.
- **Skill updates:** none (enable Browser in Cursor Settings → MCP; run commenting from parent agent with browser tools, not subagent).

## 2026-06-10 — Resume blocked (browser MCP); Marty slug fix

- **Triggered:** Resume session `session-2026-06-10.json` from `next_leader: lennyrachitsky` after prior browser disconnect.
- **Learned:** `cursor-ide-browser` MCP not in enabled servers for this workspace (`CallMcpTool` → "MCP server does not exist"); cannot verify login or post. Marty Cagan slug `marty-cagan` → 404; correct slug is `cagan` (verified via public profile fetch).
- **Skill updates:** `thought_leaders.json` Marty slug `cagan`; session `roster_fixes` block.

## 2026-06-04 — Question commenters, not only thought leaders

- **Triggered:** User asked not to always question thought leaders directly — sometimes question commentators on their posts.
- **Learned:** Leader-directed “what do you think?” every time feels repetitive; threads with ≥2 substantive comments are better engagement targets.
- **Skill updates:** SKILL §4 question-target table + session `question_target` / `reply_to`; `config.json` `thought_leader_question_mix`.

## 2026-06-04 — Thought-leader targeting (50 humans, no company/success posts)

- **Triggered:** User asked to focus on 50 PM thought leaders, real humans only, skip business pages and promotion/success posts; skill update only (no run).
- **Learned:** Company-page comments (`tagged: false`) and cert/promo noise wasted publish-day passes; roster-driven `/in/{slug}/recent-activity/all/` beats generic content search.
- **Skill updates:** `thought_leaders.json` (50 names + slugs); `config.json` `target_mode: thought_leaders`, expanded `skip_keywords`, `company_page_signals`; SKILL §3a/3b discovery default + explicit “do not run unless asked”.

## 2026-06-04 — 30/30 completed (CON-158 publish day, no approval prompts)

- **Triggered:** User asked to finish all 30 comments without mid-run approval; stop at 30/30.
- **Learned:** Session `posted: 18` lagged `comments[]` (11 rows) — reconcile before marking complete; content search past-24h (`product management AI`, PRD, roadmap, GenAI, India startup) + home feed; company pages (Product Station, IT Tech Pulse) use plain name prefix (`tagged: false`); IT Tech Pulse submit confirmed live (`Roshan Raj Mishra • You`); final session `session-2026-06-04.json` has 30 authors, `status: completed`.
- **Learned (parallel):** Subagent `e2c94212` on view `8bfc71` posted a different 13-author batch while parent finished another 30 — session `comments[]` is canonical for parent pass only; `reconciliation` block added; avoid parallel subagents per `single_agent_only`.
- **Skill updates:** none.

## 2026-06-04 — Feed engage started (CON-158 publish day)

- **Triggered:** User asked to start feed engagement alongside golden hour.
- **Learned:** Session armed from publish-day trigger; browser MCP began 30/30 on home feed Top (Ashley Collier 11h, Akshita Agrawal 3h — verified mention chips).
- **Skill updates:** none.

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
