---
name: linkedin-feed-engage
description: >-
  Proactive LinkedIn feed comments via Cursor browser MCP: refresh home feed (Top),
  pick posts ≤12h old with visible traction, draft Depth Score comments with verified
  @mentions (mention chip required), post through UI. Target 30 comments in 30 minutes,
  continuous auto mode (no batch stops). Use for feed engagement or publish-day companion
  sessions (not golden-hour replies on your posts).
---

# LinkedIn Feed Engage (Cursor browser)

Changelog: [`SKILL_CHANGELOG.md`](SKILL_CHANGELOG.md) · Config: [`config.json`](config.json)

**Goal:** **≥30 substantive comments in 30 minutes** on others’ posts (PM / builder / India startup niche), **one uninterrupted run** — no “keep going” prompts, no mid-session subagents. **Not** golden-hour replies on your own posts — see [`linkedin-golden-hour`](../linkedin-golden-hour/SKILL.md).

**Tool:** `cursor-ide-browser` MCP only (no Playwright in Phase 1).

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
3. **Config** — [`config.json`](config.json) (`target_comments`, delays, niche/skip keywords).

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
| Max post age | **≤12 hours** (hard skip older) |
| Delay between posts | **45–60 s** (`min_delay_seconds` / `max_delay_seconds`) |
| Feed refresh | **Scroll `main` each pick** — full reload only every 8 picks or when dry |
| Continuous mode | **Yes** — single agent until `posted >= target`; no batch stops |
| Phase 1 approval | **0** (auto mode) |
| Mention required | **Yes** — verified `data-type="mention"` chip before submit |

## Browser workflow (agent loop)

**Order:** `browser_tabs` list → `browser_navigate` feed → `browser_lock` → loop → `browser_lock` unlock.

### 0. Start session

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
3. **Full reload** only when: feed is dry (no ≤12h PM/builder cards after scroll + Load more), **or** every `full_reload_every_n_picks` (default 8)

Confirm **Sort by: Top** after any reload.

### 2. Scroll and snapshot

- `browser_scroll` down 2–3 viewport heights between picks (after refresh)
- `browser_snapshot` — collect visible post cards (author name, age like `3h` / `1d`, reactions/comments, Comment button ref)

### 3. Post selection (niche + age + engagement)

**Include** if post text matches any `niche_keywords` in config (PM, startup, workflow, etc.).

**Skip** if:

- Matches `skip_keywords` (engagement bait, hiring-only, DM me)
- Already commented (same author in session log)
- Promoted/sponsored card (usually labeled “Promoted”)
- You already commented on this post URL in session file

**Prefer:** **top-level comments on distinct feed posts** — one comment per post card, then scroll for the next. Do **not** stack multiple replies on the same thread unless the user explicitly asks for thread depth.

**Prefer engaged posts (post–golden-hour):** When the user wants traction, not cold outreach — skip brand-new zero-engagement posts from `Latest`. Target posts with visible reactions/comments, typically **12h–3d** old (after the author’s golden hour).

**Discovery (default):** **Home feed only** — `https://www.linkedin.com/feed/` with **Sort by: Top**; refresh + scroll before each pick (§1). Do **not** use content search or date filters unless the user explicitly asks. Fallback content search is documented in `config.json` `discovery_urls` only for exceptional scarcity.

### 3. Open comment box

On selected post card:

1. Click **Comment** (or focus comment area under post)
2. `browser_snapshot` — confirm comment textbox visible (`placeholder` often “Add a comment…”)
3. If “See more” truncates post → expand before drafting

### 4. Draft comment (Depth Score — others’ posts)

4-part frame, **no URLs**:

1. **Verified `@` tag the post author** (LinkedIn mention chip — clickable, notifies them). **Plain `@Name` text does not count as tagged.**
2. `{specific line you're reacting to}.`
3. One concrete insight or counter-point
4. Optional: one sentence experience (“I've seen this with…”)
5. Open question

**Chat draft format:** show as `@Ayush Muniya — …` for your planning, but the browser must contain a real mention chip before submit (see §5).

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
- Append to session JSON: `{ "author", "snippet", "comment", "posted_at", "status": "posted", "tagged": true }`

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

Same as [`proactive-comments-plan.md`](../linkedin-content-posting/proactive-comments-plan.md):

- No “Great post!” / “Thanks for sharing!”
- No links, hashtags stacks, DM CTAs
- Must reference something **specific** in their post

## Mention verification checklist (agent)

Before every submit, confirm ALL of:

- [ ] Post age ≤ 12h (or skip)
- [ ] Feed refreshed since previous pick
- [ ] Editor has `[data-type="mention"]` for post author
- [ ] Posted comment shows author as clickable mention link in snapshot
- [ ] `tagged: true` in session log (only if mention chip verified)

## Examples

**"Run feed engagement 30/30"** → Confirm logged in → load Notion persona → session file → continuous scroll/filter loop → auto-post all 30 without stopping.

**"5 comment warmup"** → Same flow; `target_comments: 5` in session; all with approval.

**"I'm logged in, go"** → `browser_navigate` feed → start loop immediately.

## Security

- Never type LinkedIn password or 2FA in chat or automation.
- Session logs in `state/` — no credentials; comment text only.

## Publish-day automation (go-live trigger)

When **your** Buffer LinkedIn post enters golden hour, local launchd arms feed engage automatically:

```bash
bash ~/LinkedIn\ Automation/scripts/install_publish_day_schedule.sh
```

Each **10 min × 90 min** tick (Tue–Thu 10:00 local):

1. `golden_hour.py watch` — auto-replies on comments **your** post (Composio, no approval)
2. `feed_engage_trigger.py` — on first `sent` Buffer post → creates auto session + `state/feed_engage_armed.json` + agent prompt

**Requirements (publish day):**

| Requirement | Why |
|-------------|-----|
| Mac awake + logged in | launchd runs locally |
| Cursor open | Browser MCP needs IDE |
| LinkedIn logged in at `/feed/` | Comment UI |
| Optional: `CURSOR_API_KEY` + `pip install cursor-sdk` | Zero-click agent launch via `trigger_feed_engage_agent.sh` |

**Manual fallback:** When notification fires, paste prompt from `state/agent_prompt.txt` into Cursor agent.

**Fully unattended** (no Cursor open) = Phase 2 Playwright — see [`proactive-comments-plan.md`](../linkedin-content-posting/proactive-comments-plan.md).

## Related

| Skill | Role |
|-------|------|
| `linkedin-golden-hour` | Replies on **your** posts (Gmail + Composio) |
| `linkedin-content-posting` | Schedule/publish **your** content |
