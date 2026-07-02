---
name: linkedin-feed-engage
description: >-
  Proactive LinkedIn feed comments. Default: hands-off daemon (linkedincli read,
  Groq LLM, Composio post) on Buffer publish days. Legacy: Cursor browser MCP
  for assisted sessions. PM/builder niche, post-type routing (opinion questions
  vs career ack). Not golden-hour replies on your posts.
---

# LinkedIn Feed Engage

Changelog: [`SKILL_CHANGELOG.md`](SKILL_CHANGELOG.md) · Config: [`config.json`](config.json) · Daemon docs: [`docs/FEED_ENGAGE_DAEMON.md`](../docs/FEED_ENGAGE_DAEMON.md)

**Goal:** Substantive comments on fresh PM/builder posts with niche filters and post-type routing (`opinion_question` vs `career_ack`). **Not** golden-hour replies on your own posts — see [`linkedin-golden-hour`](../linkedin-golden-hour/SKILL.md).

## Runner modes

| Mode | `runner_mode` | When to use |
|------|---------------|-------------|
| **Daemon (default)** | `daemon` | Publish-day automation, hands-off ticks, no Cursor |
| **Browser (legacy)** | `browser` | Manual assisted sessions in main Cursor chat |

### Daemon mode (default)

**Stack:** Buffer window → `feed_engage_daemon.py` → linkedincli **read** → Groq draft → Composio `LINKEDIN_CREATE_COMMENT_ON_POST`.

**One-time env** (in `~/.zshrc` as `export VAR=...` — launchd reads via [`scripts/load_launch_env.sh`](../scripts/load_launch_env.sh)):

| Variable | Required |
|----------|----------|
| `GROQ_API_KEY` | Yes (default LLM) |
| `LINKEDIN_LI_AT` / `LINKEDIN_JSESSIONID` | Yes (feed read) |
| `BUFFER_MCP_TOKEN` | Yes (publish-day window) |
| `COMPOSIO_API_KEY` or Composio CLI login | Yes (comment post) |

**Preflight:**

```bash
bash scripts/preflight_feed_engage.sh
```

**Manual tick:**

```bash
python3 linkedin-feed-engage/feed_engage_daemon.py --dry-run --force --max-comments 5
python3 linkedin-feed-engage/feed_engage_daemon.py --force --max-comments 5
```

**Discovery:** Home feed via linkedincli (`feed view`). If fewer than `thought_leader_fallback_min_eligible` posts pass filters, daemon pulls recent activity from [`thought_leaders.json`](thought_leaders.json) via `feed user <slug>`.

**Publish day:** `bash scripts/install_publish_day_schedule.sh` → launchd runs `publish_day_watch.sh` every 10 min × 90 min (Tue–Thu 10:00 local). **Mac awake required; Cursor does not.**

Full setup: [`docs/FEED_ENGAGE_DAEMON.md`](../docs/FEED_ENGAGE_DAEMON.md).

### Browser legacy mode

Set `"runner_mode": "browser"` in config. Requires **Cursor browser MCP** in **main agent chat** (not Task subagent). Sections below through § Publish-day browser notes apply to this path only.

**Tool:** `cursor-ide-browser` MCP only (no Playwright in Phase 1).

## Browser MCP scope (legacy — `runner_mode: browser`)

`cursor-ide-browser` tabs are **scoped to the Cursor agent context** that created or last interacted with them. **Background Task subagents do not inherit the parent agent's browser tabs** — `browser_tabs` list often returns empty even when the main chat has 8+ LinkedIn tabs open.

| Context | Browser tabs | Feed engage |
|---------|--------------|-------------|
| **Main Cursor agent** (user chat) | Sees user's LinkedIn tabs | **Run here** |
| **Task / background subagent** | Usually empty; prior `browser_view_id` invalid | **Do not delegate** |
| **cursor-sdk `Agent.prompt`** | Separate local agent — same isolation risk | Use only if verified; prefer main chat |

**Coordinator rules (`single_agent_only: true` in config):**

1. **Never** use the Task tool to spawn feed engage — it will silently fail or block on empty `browser_tabs`.
2. **Never** hand off mid-session to a subagent — one main agent, one browser lock, until `status: completed`.
3. Publish-day trigger writes `state/agent_prompt.txt` — user or main agent pastes/resumes in **the same chat** that has browser MCP, not a subagent.

**If `browser_tabs` list is empty at session start:**

1. In **main agent only**: try `browser_tabs` action **`new`**, then `browser_navigate` to `https://www.linkedin.com/feed/` (omit `viewId` on navigate right after `new`).
2. In **Task subagent**: `browser_tabs` `new` may return a `viewId` but `browser_navigate` often still fails ("No browser tab available") — treat as blocked immediately; do not retry.
3. If navigate fails → set session `status: blocked` (below) and **stop**. User logs into LinkedIn in Cursor browser from **main agent** chat, then resumes.

**Blocked session JSON** (write when browser unavailable):

```json
{
  "status": "blocked",
  "blocked_reason": "browser_tabs_empty",
  "blocked_message": "cursor-ide-browser has no tab in this agent context. Run feed engage in main Cursor chat (not Task subagent). Log into linkedin.com/feed/ in Cursor browser, then resume.",
  "blocked_at": "<ISO>",
  "resume_hint": "Main agent only — paste state/agent_prompt.txt or say resume feed engage"
}
```

## Continuous run rules (mandatory for 30/30)

When `continuous_mode: true` in config (default):

| Do | Don't |
|----|-------|
| One agent, one feed tab, `browser_lock` once at start | Parallel subagents or handoffs mid-session |
| Post all 30 back-to-back; update JSON after each | Ask “keep going” or wait for user between batches |
| Unlock browser only at `status: completed` or hard stop | Stop at 5/10/17 “for review” unless user says stop |
| Scroll `main` during inter-comment wait | Full page reload every pick |

Hard stops unchanged: login/captcha, 4× same failure, user says stop.

## Login (user must do this once per session)

**URL:** https://www.linkedin.com/login

After sign-in, confirm feed loads: https://www.linkedin.com/feed/

**Stop and ask user** if you see login, captcha, email verification, or passkey prompt — never enter credentials.

## Prerequisites

1. **Cursor browser MCP** (`cursor-ide-browser`) — user logged into LinkedIn in browser tab.
2. **Notion MCP** — load persona + strategy before drafting (same as content posting).
3. **Config** — [`config.json`](config.json) (`target_mode`, `target_comments`, delays, skip rules).
4. **Thought leaders** — [`thought_leaders.json`](thought_leaders.json) when home feed is dry (`target_mode: home_feed`, default). Roster excludes leaders with no post in **>5 days** (`roster_prune_if_no_post_days`).

```text
notion-fetch: 36f3dffe-a139-8195-9dac-f3b5a76003b7   # strategy
notion-fetch: b9887b1f-3282-4a72-874f-b35a70d9d17b   # persona
```

Pair with [`linkedin-content-posting`](../linkedin-content-posting/SKILL.md) for voice rules (no external links in comments).

## Session targets

| Setting | Default (`config.json`) |
|---------|-------------------------|
| Duration | **30 min** (`session_minutes`) |
| Target comments | 30 |
| Max post age | **Strictly &lt;8 hours** (`max_post_age_hours: 8`, `max_post_age_strict: true`) — skip `8h`, `1d`, `2d`, etc. |
| Delay between posts | **45–60 s** (`min_delay_seconds` / `max_delay_seconds`) |
| Feed refresh | **Scroll `main` each pick** — full reload only every 8 picks or when dry |
| Continuous mode | **Yes** — single agent until `posted >= target`; no batch stops |
| Phase 1 approval | **0** (auto mode) |
| Mention required | **Yes** — verified `data-type="mention"` chip before submit |

## Browser workflow (agent loop)

**Order:** `browser_tabs` list → (if empty: `browser_tabs` **new**) → `browser_navigate` feed → `browser_lock` → loop → `browser_lock` unlock.

### 0. Start session

**Browser guard (before any LinkedIn URL):**

1. `browser_tabs` action `list` — if tabs exist, note `viewId` for lock/navigate.
2. If list empty → `browser_tabs` action `new` → `browser_navigate` `https://www.linkedin.com/feed/`.
3. If navigate fails with "No browser tab available" → write blocked session JSON (§ Browser MCP scope) and **stop** (do not delegate to Task).

- Navigate `https://www.linkedin.com/feed/` (or reload if already there — see §1)
- Confirm **Sort by: Top** (not Recent) when visible in feed controls
- If URL contains `/login` or `/checkpoint` → **stop**, user must log in at https://www.linkedin.com/login
- Create/update `state/session-{YYYY-MM-DD}.json`:

```json
{
  "started_at": "<ISO>",
  "target": 30,
  "posted": 0,
  "skipped": 0,
  "comments": []
}
```

### 1. Surface feed cards (every pick — fast path)

**Default (30/30):** do **not** full-reload every pick — that burns ~10–15 s per comment.

1. Scroll `document.querySelector('main')` to bottom (CDP `Runtime.evaluate` or `browser_scroll` on main column)
2. Click **Load more** when visible
3. **Full reload** only when: feed is dry (no **&lt;8h** PM/builder cards after scroll + Load more), **or** every `full_reload_every_n_picks` (default 8)

Confirm **Sort by: Top** after any reload.

### 2. Scroll and snapshot

- `browser_scroll` down 2–3 viewport heights between picks (after refresh)
- `browser_snapshot` — collect visible post cards (author name, age like `3h` / `1d`, reactions/comments, Comment button ref)

### 3. Post selection (niche + age + engagement)

**Include** if post text matches any `niche_keywords` in config (PM, startup, workflow, etc.).

**Skip** if:

- Matches `skip_keywords` (engagement bait, hiring-only, DM me, **success-story / promotion language**)
- **Company or media page** author (not a person on the roster)
- **Success-story post** on a person’s profile (promotion, new job, anniversary, certificate, open-to-work celebration) — scroll to next post or next leader
- Already commented (same author in session log)
- Promoted/sponsored card (usually labeled “Promoted”)
- You already commented on this post URL in session file

**Prefer:** **top-level comments on distinct feed posts** — one comment per post card, then scroll for the next. Do **not** stack multiple replies on the same thread unless the user explicitly asks for thread depth.

**Prefer engaged posts:** Within the **&lt;8h** window, prefer cards with visible reactions/comments over zero-engagement posts.

**Discovery (default — `target_mode: home_feed`):** `https://www.linkedin.com/feed/` with **Sort by: Top**. Scroll `main`, **Load more**, snapshot cards. Pick PM/builder posts **strictly under 8 hours** (`7h`, `6h`, `45m` — not `8h` or `1d`). One comment per post card; track authors in session JSON.

**Discovery (fallback — thought leaders):** When home feed is dry after scroll + Load more (+ optional content search), work [`thought_leaders.json`](thought_leaders.json). One comment per leader per session. Roster is pre-pruned: drop anyone whose newest original post is **older than 5 days** (`roster_prune_if_no_post_days`).

**Age parse (strict):** `45m`, `2h`, `7h` → eligible. `8h`, `9h`, `1d`, `2d`, `1w` → **skip**. When ambiguous, CDP `innerText` on post #1 and err skip.

### 3a. Thought-leader targeting (fallback)

| Rule | Action |
|------|--------|
| **Real humans only** | Author must be a person (`/in/{slug}`), with a personal headline on the card. **Skip** company pages, newsletters, and “Follow {Brand}” cards (`skip_company_pages`, `company_page_signals` in config). |
| **Roster order** | Load `thought_leaders.json` → pick next leader not in session `comments[]` → open `https://www.linkedin.com/in/{slug}/recent-activity/all/` (config `discovery_urls.thought_leader_activity`). |
| **Post pick** | Newest **original** post **strictly &lt;** `max_post_age_hours` (8) with PM/builder substance (`niche_keywords`). Prefer posts with reactions/comments (`prefer_engaged_posts`). |
| **Roster hygiene** | Remove from `thought_leaders.json` any leader whose newest original post is **&gt;5 days** old; log pruned names in changelog. Re-add when they post again. |
| **Hard skip — success stories** | No comments on promotions, new roles, anniversaries, certifications, open-to-work celebrations, or generic “excited to announce” posts (`skip_success_story_posts` + `skip_keywords` in config). Scroll to their next post or skip leader and log `skipped`. |
| **Mention** | `@` + listbox select → verify `[data-type="mention"]` chip (required for people). |
| **Questions** | Do **not** aim every closing question at the thought leader — mix targets (§4). |
| **Session target 15** | Roster cap is 15 (`thought_leader_count`); one leader = one comment max per session. |

**The 15 (display names)** — slugs + audit ages in JSON:

John Cutler · Hiten Shah · Melissa Perri · Roman Pichler · Aakash Gupta · Paul Adams · Elena Verna · Janna Bastow · Scott Belsky · Lenny Rachitsky · Itamar Gilad · Sachin Rekhi · Fareed Mosavat · April Dunford · Nikhyl Singhal

**Do not run** a engage session unless the user explicitly asks (skill/config updates alone are not a trigger).

### 3b. Home feed (default)

`https://www.linkedin.com/feed/` with **Sort by: Top**. Same skip rules: **no company pages**, **no success-story posts**, **strict &lt;8h age**.

### 3c. Roster maintenance

When auditing or ending a session, if a roster leader’s newest original post is **&gt;5 days** ago, **remove** them from [`thought_leaders.json`](thought_leaders.json) and note in [`SKILL_CHANGELOG.md`](SKILL_CHANGELOG.md). Wrong-profile slugs (`hwalker`, `noahweiss`) remove or fix slug before re-add.

### 3. Open comment box

On selected post card:

1. Click **Comment** (or focus comment area under post)
2. `browser_snapshot` — confirm comment textbox visible (`placeholder` often “Add a comment…”)
3. **MUST** click **See more** / **…more** if the post body is truncated — read the **full** text (and skim visible thread comments) **before** drafting. Never draft from card title, webinar promo line, or first sentence alone.

### 4. Draft comment (Depth Score — others’ posts)

4-part frame, **no URLs**:

1. **Verified `@` tag the post author** (LinkedIn mention chip — clickable, notifies them). **Plain `@Name` text does not count as tagged.**
2. **Quote or paraphrase one concrete phrase/claim** from the expanded post (or a commenter's line when engaging the thread) — e.g. their named framework, number, example, or contrast they drew. **Not** your publish-day topic or a generic PM theme.
3. One concrete insight or counter-point **about that same claim**
4. Optional: one sentence experience — only if it **directly illustrates the cited claim** (not a tangent onto your own post topic)
5. Open question — **target varies** (see below); must be answerable only given **this** post/thread

**Chat draft format:** show as `@Ayush Muniya` then the body for planning; the browser must contain a real mention chip before submit (see §5). The `@Name` chip line is fine; everything after it is the **body** and must follow punctuation rules below.

#### No dashes in comments (mandatory — current + future comments)

Do **not** use em dash (—), en dash (–), or hyphen as a clause separator in the comment **body**. Use periods, commas, or colons instead. Hyphens inside compound words or names (e.g. `build-to-learn`, `AI-heavy`) are OK.

| OK | Not OK |
|----|--------|
| `@Name` mention chip at the start | Em/en dash between clauses in the body |
| Hyphens in quoted terms or compound adjectives | `…replicate — where does that gap…` |
| Period, comma, or colon between ideas | `…lands hard — I've seen…` |

**Bad:** `framing EQ as what AI can't replicate — where does that gap show up`

**Good:** `framing EQ as what AI can't replicate. Where does that gap show up`

#### Post relevance (mandatory — current + future comments)

Comments that *sound* like Depth Score but ignore the post read generic. Enforce **before every submit**:

| Rule | Requirement |
|------|-------------|
| **Expand first** | Click **See more** when present; draft only after reading full body (+ thread if ≥2 substantive comments). |
| **Cite in part 2** | Part 2 MUST include **one specific phrase, term, number, or named example** from the post (or commenter line). Paraphrase OK; vague theme (“indispensability”, “three generations”) without their wording is not enough. |
| **Match primary subject** | Comment topic = post's **main** argument. Do not pivot to enterprise onboarding, tradeoff calls, or AI-roadmap platitudes unless **they** raised that exact angle. |
| **No publish-day bleed** | Do not inject themes from **your** Buffer post / golden-hour topic into unrelated leader posts. |
| **Ban generic closers** | Reject questions that could fit any PM post: “What signals keep stakeholders patient?”, “Where does that split show up on AI roadmaps?”, “How do you balance speed vs quality?” Rewrite until the question names **their** example, constraint, or framework. |
| **Pre-submit test** | Ask: *“Could this comment apply to a different post?”* → **if yes, rewrite** before typing in browser. |
| **Session log** | Append `post_snippet_referenced` — the exact phrase/claim you anchored on (10–80 chars). |

**Bad (generic — rewrite):** `@Janna — framing indispensability as judgment + context lands hard. I've seen B2B teams stall on tradeoff calls. Where does that split show up on AI-heavy roadmaps?` — paraphrases title only; experience + question fit any AI post.

**Good (anchored):** `@Janna — your line that AI won't replace PMs who own *which* problems to solve (not prompt libraries) is the filter I'd use in hiring. When you run the webinar exercise, what artifact proves someone picked judgment over tooling?` — cites her claim; question only makes sense on **this** post.

#### Question targets on thought-leader posts (mandatory variety)

Do **not** end every comment with a question aimed at the thought leader (“What would you add, Marty?”). That reads sycophantic and repetitive.

| Situation | What to do |
|-----------|------------|
| Post has **0–1** shallow comments | Insight + question can go to the **post author** (still specific to their post). |
| Post has **≥2** substantive comments | **Often** anchor on a commenter's point; close by questioning **the thread** or a **commenter** (not the leader). |
| Strong disagreement in thread | Add a nuance or counter-frame; ask **commenters** to weigh tradeoffs (“@Name — you framed X as Y; where would that break in enterprise?”). |
| Leader already asked a question in the post | **Do not** ask them another mirror question — extend the debate toward **commenters** or “others in this thread”. |

**Mix (thought-leader mode):** Across a session, aim for **≤50%** of closing questions primarily directed at the roster author; the rest should engage **existing commentators** (by name when visible) or the **audience in the thread** without interrogating the leader again.

**Ways to question commenters (top-level or reply):**

- Reference their line: “@Commenter — the bit about {X} assumes {Y}; what would falsify that in a B2B rollout?”
- Reply under their comment when the UI offers **Reply** (preferred for direct back-and-forth); session log `reply_to` with their display name.
- Second `@` chip for a commenter is optional when it fits length; **post author chip stays required** on top-level comments for notify/visibility.

**Still avoid:** “Great take!”-only praise, leader worship, or duplicate questions the leader already answered in the post body.

Length: **120–280 chars** ideal for 30/30 pace; max 900. Load persona tone from Notion. Shorter beats longer when on the clock.

**Auto mode (default):** Post without approval when `auto_mode: true` and `phase1_approval_limit: 0`.

**Manual override:** Set `phase1_approval_limit: 5` and show drafts until user says **“post it”**.

### 5. Submit via browser

**Insert `@` mention (required):**

1. Focus comment textbox → type `@` + enough of the author's name to surface them (e.g. `@Ayush` for Ayush Muniya)
2. `browser_snapshot` — confirm **listbox** with author options (match headline to post card)
3. `browser_click` the correct **option** (post author, not a namesake)
4. **Verify chip** — `browser_cdp` `Runtime.evaluate`: active editor must contain `[data-type="mention"]` (plain `@Name` text is not tagged)
5. Type the rest **slowly** (`slowly: true`) — fast typing after the chip can flatten it to plain text
6. Re-verify mention chip before submit

**Fix broken tags:** Edit mode often omits the post author from the listbox → **Delete** comment → repost with steps above. Do not edit plain-text names into tags.

**Submit:**

- Click **Comment** / **Reply** submit button after typing (appears once text is present — not Enter alone)
- `browser_snapshot` — confirm a **`link`** named author appears in the comment row (not only plain text in the comment body string)
- Append to session JSON: `{ "author", "snippet", "post_snippet_referenced", "comment", "posted_at", "status": "posted", "tagged": true, "question_target": "author|commenter|thread" }` (optional `reply_to` when nested). **`post_snippet_referenced`** = the exact phrase/claim from the post (or commenter) used in part 2.

### 6. Pace (30/30 continuous)

Read delays from `config.json` (default **45–60 s** jitter between submits).

- **While waiting:** scroll `main` + Load more to queue the next eligible post — do not idle
- Increment `posted` after each JSON append; stop when `posted >= target` OR `session_minutes` elapsed
- **Never** ask “keep going”, pause for approval (auto mode), or spawn parallel subagents — one browser tab, one agent, lock once at start

**Budget:** ~30 s comment + mention + submit, ~45 s gap ≈ **30 comments in ~37 min** worst case; tighter drafts and overlap scroll during wait hit **≤30 min**.

### 7. End session

- Write final counts to session JSON
- `browser_lock` unlock
- Summarize: posted / skipped / failures

## Stop conditions (mandatory)

| Signal | Action |
|--------|--------|
| Redirect to `/login` or `/checkpoint` | Stop — user re-auth |
| Captcha / “unusual activity” | Stop — user manual |
| Same action fails **4×** | Stop — report snapshot |
| User says stop | Unlock browser, exit |

## Comment quality bar

Same as [`proactive-comments-plan.md`](../linkedin-content-posting/proactive-comments-plan.md) plus §4 **Post relevance** and **No dashes**:

- No “Great post!” / “Thanks for sharing!”
- No em dash, en dash, or hyphen as clause separators in the comment body (§4)
- No links, hashtags stacks, DM CTAs
- **See more** expanded; part 2 cites a **specific** phrase/claim from the full post (or commenter line)
- Insight + question tied to **that** claim — not generic PM platitudes or your publish-day topic
- Pre-submit: *“Could this apply to a different post?”* → if yes, rewrite
- On thought-leader posts: **vary who the closing question addresses** — not always the post author

## Mention verification checklist (agent)

Before every submit, confirm ALL of:

- [ ] Post age **strictly &lt;** `max_post_age_hours` (8h exactly = skip)
- [ ] **See more** clicked when truncated; full post read
- [ ] Part 2 names a **specific** phrase/claim from the post (`post_snippet_referenced` ready for JSON)
- [ ] Comment body has **no** em dash, en dash, or hyphen used as clause separators (§4)
- [ ] Pre-submit relevance test passed (not interchangeable with another post)
- [ ] Feed refreshed since previous pick
- [ ] Editor has `[data-type="mention"]` for post author
- [ ] Posted comment shows author as clickable mention link in snapshot
- [ ] `tagged: true` in session log (only if mention chip verified)

## Examples

**"Run feed engagement 30/30"** → Home feed Top first; posts **&lt;8h** only; roster fallback when dry; auto-post without stopping.

**"Comment on the PM leader roster"** → Roster fallback (15 active); still **&lt;8h** posts only; re-audit roster when dry.

**"5 comment warmup"** → `target_comments: 5`; first five roster leaders with eligible posts.

**"Update skill only"** → Edit SKILL/config/roster; **do not** open browser or post.

**"I'm logged in, go"** → Start on home feed Top; scroll for **&lt;8h** PM cards before opening roster activity pages.

## Security

- Never type LinkedIn password or 2FA in chat or automation.
- Session logs in `state/` — no credentials; comment text only.

## Publish-day automation

When **your** Buffer LinkedIn post enters the engagement window (−15m to +90m), local launchd runs feed engage automatically:

```bash
bash ~/Projects/LinkedIn\ Automation/scripts/install_publish_day_schedule.sh
```

Each **10 min × 90 min** tick (Tue–Thu 10:00 local):

1. `golden_hour.py watch` — auto-replies on comments **your** post (Composio)
2. **`feed_engage_daemon.py`** (default) — hands-off feed comments (linkedincli + Groq + Composio)

**Requirements (daemon, default):**

| Requirement | Why |
|-------------|-----|
| Mac awake + logged in | launchd runs locally |
| `export GROQ_API_KEY=...` in `~/.zshrc` | LLM drafts (run `bash scripts/preflight_feed_engage.sh`) |
| LinkedIn cookies in `~/.zshrc` | `bash scripts/import_linkedin_cookies.sh` |
| Composio LinkedIn connected | Comment API |

**Legacy browser path** (`runner_mode: browser`):

| Requirement | Why |
|-------------|-----|
| Cursor open | Browser MCP needs IDE |
| LinkedIn logged in at `/feed/` | Comment UI |
| Optional: `CURSOR_API_KEY` + SDK | `trigger_feed_engage_agent.sh` |

**Manual fallback (browser):** Paste prompt from `state/agent_prompt.txt` into **main Cursor agent chat**.

**SDK launch (browser):** `scripts/trigger_feed_engage_agent.sh` — set `FEED_ENGAGE_SDK_LAUNCH=1` only if you accept SDK agent may lack browser tabs.

See [`docs/FEED_ENGAGE_DAEMON.md`](../docs/FEED_ENGAGE_DAEMON.md) for daemon troubleshooting.

## Related

| Skill | Role |
|-------|------|
| `linkedin-golden-hour` | Replies on **your** posts (Gmail + Composio) |
| `linkedin-content-posting` | Schedule/publish **your** content |
