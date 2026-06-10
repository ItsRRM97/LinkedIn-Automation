---
name: linkedin-feed-engage
description: >-
  Proactive LinkedIn feed comments via Cursor browser MCP. Default targeting: 50 curated PM
  thought leaders (real humans, not company pages); skip promotion/success-story posts.
  Depth Score comments with verified @mentions. Home feed is fallback only. Use for feed
  engagement or publish-day companion sessions (not golden-hour replies on your posts).
---

# LinkedIn Feed Engage (Cursor browser)

Changelog: [`SKILL_CHANGELOG.md`](SKILL_CHANGELOG.md) · Config: [`config.json`](config.json) · Roster: [`thought_leaders.json`](thought_leaders.json)

**Goal:** Substantive comments on **real PM thought leaders’** posts (see roster), **one uninterrupted run** when executing — no “keep going” prompts, no mid-session subagents. Default session size remains **30** (`target_comments`); user may set **50** for a full-roster pass. **Not** golden-hour replies on your own posts — see [`linkedin-golden-hour`](../linkedin-golden-hour/SKILL.md).

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
3. **Config** — [`config.json`](config.json) (`target_mode`, `target_comments`, delays, skip rules).
4. **Thought leaders** — [`thought_leaders.json`](thought_leaders.json) when `target_mode` is `thought_leaders` (default).

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

- Matches `skip_keywords` (engagement bait, hiring-only, DM me, **success-story / promotion language**)
- **Company or media page** author (not a person on the roster)
- **Success-story post** on a person’s profile (promotion, new job, anniversary, certificate, open-to-work celebration) — scroll to next post or next leader
- Already commented (same author in session log)
- Promoted/sponsored card (usually labeled “Promoted”)
- You already commented on this post URL in session file

**Prefer:** **top-level comments on distinct feed posts** — one comment per post card, then scroll for the next. Do **not** stack multiple replies on the same thread unless the user explicitly asks for thread depth.

**Prefer engaged posts (post–golden-hour):** When the user wants traction, not cold outreach — skip brand-new zero-engagement posts from `Latest`. Target posts with visible reactions/comments, typically **12h–3d** old (after the author’s golden hour).

**Discovery (default — `target_mode: thought_leaders`):** Work the **50-person roster** in [`thought_leaders.json`](thought_leaders.json). One comment per leader per session (track `author` in session JSON). Do **not** comment on company/media pages.

**Discovery (fallback):** Home feed Top or `discovery_urls.content_search_past_week` only when a leader has no eligible post ≤ `max_post_age_hours` after checking their activity page.

### 3a. Thought-leader targeting (default)

| Rule | Action |
|------|--------|
| **Real humans only** | Author must be a person (`/in/{slug}`), with a personal headline on the card. **Skip** company pages, newsletters, and “Follow {Brand}” cards (`skip_company_pages`, `company_page_signals` in config). |
| **Roster order** | Load `thought_leaders.json` → pick next leader not in session `comments[]` → open `https://www.linkedin.com/in/{slug}/recent-activity/all/` (config `discovery_urls.thought_leader_activity`). |
| **Post pick** | Newest **original** post ≤ `max_post_age_hours` with PM/builder substance (`niche_keywords`). Prefer posts with reactions/comments (`prefer_engaged_posts`). |
| **Hard skip — success stories** | No comments on promotions, new roles, anniversaries, certifications, open-to-work celebrations, or generic “excited to announce” posts (`skip_success_story_posts` + `skip_keywords` in config). Scroll to their next post or skip leader and log `skipped`. |
| **Mention** | `@` + listbox select → verify `[data-type="mention"]` chip (required for people). |
| **Questions** | Do **not** aim every closing question at the thought leader — mix targets (§4). |
| **Session target 50** | When user asks for full roster: set `target: 50` in session JSON; one leader = one comment max. |

**The 50 (display names)** — slugs in JSON:

Marty Cagan · Teresa Torres · Lenny Rachitsky · Shreyas Doshi · Gibson Biddle · April Dunford · Melissa Perri · John Cutler · Janna Bastow · Roman Pichler · Nikhyl Singhal · Scott Belsky · Jeff Patton · Brian Balfour · Rich Mironov · Jackie Bavaro · Deb Liu · Elena Verna · Casey Winters · Fareed Mosavat · Hiten Shah · Wes Kao · Ravi Mehta · Ken Norton · Martin Eriksson · Todd Olson · Julie Zhuo · Rahul Vohra · Paul Adams · Anna Marie Clifton · Heidi Helfand · Tim Herbig · Matt LeMay · Jeff Gothelf · Dan Olsen · Christina Wodtke · Sachin Rekhi · Cindy Alvarez · Ant Murphy · Noah Weiss · Lane Shackleton · Andrew Chen · Petra Wille · Josh Porter · Aakash Gupta · Itamar Gilad · Giff Constable · Shishir Mehrotra · David Cancel · Hunter Walk

**Do not run** a engage session unless the user explicitly asks (skill/config updates alone are not a trigger).

### 3b. Home feed (fallback only)

`https://www.linkedin.com/feed/` with **Sort by: Top** when thought-leader activity is dry. Same skip rules: **no company pages**, **no success-story posts**.

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

**Chat draft format:** show as `@Ayush Muniya — …` for your planning, but the browser must contain a real mention chip before submit (see §5).

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

Same as [`proactive-comments-plan.md`](../linkedin-content-posting/proactive-comments-plan.md) plus §4 **Post relevance**:

- No “Great post!” / “Thanks for sharing!”
- No links, hashtags stacks, DM CTAs
- **See more** expanded; part 2 cites a **specific** phrase/claim from the full post (or commenter line)
- Insight + question tied to **that** claim — not generic PM platitudes or your publish-day topic
- Pre-submit: *“Could this apply to a different post?”* → if yes, rewrite
- On thought-leader posts: **vary who the closing question addresses** — not always the post author

## Mention verification checklist (agent)

Before every submit, confirm ALL of:

- [ ] Post age ≤ `max_post_age_hours` (or skip)
- [ ] **See more** clicked when truncated; full post read
- [ ] Part 2 names a **specific** phrase/claim from the post (`post_snippet_referenced` ready for JSON)
- [ ] Pre-submit relevance test passed (not interchangeable with another post)
- [ ] Feed refreshed since previous pick
- [ ] Editor has `[data-type="mention"]` for post author
- [ ] Posted comment shows author as clickable mention link in snapshot
- [ ] `tagged: true` in session log (only if mention chip verified)

## Examples

**"Run feed engagement 30/30"** → Thought-leader mode: roster loop, human posts only, skip success stories → auto-post without stopping.

**"Comment on the 50 PM leaders"** → `target: 50` in session; one comment per roster name; same skip rules.

**"5 comment warmup"** → `target_comments: 5`; first five roster leaders with eligible posts.

**"Update skill only"** → Edit SKILL/config/roster; **do not** open browser or post.

**"I'm logged in, go"** → Start thought-leader discovery (activity pages), not generic feed spam.

## Security

- Never type LinkedIn password or 2FA in chat or automation.
- Session logs in `state/` — no credentials; comment text only.

## Publish-day automation (go-live trigger)

When **your** Buffer LinkedIn post enters golden hour, local launchd arms feed engage automatically:

```bash
bash ~/Projects/LinkedIn\ Automation/scripts/install_publish_day_schedule.sh
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
