# Proactive feed engagement — strategy plan

**Goal:** **≥30 substantive comments in 90 minutes** on others’ posts in your niche (aligned with golden-hour window when you publish). No links. Quality bar unchanged from Depth Score.

**Status:** **Phase 1 built** — skill [`linkedin-feed-engage`](../linkedin-feed-engage/SKILL.md) (Cursor browser MCP). Playwright unattended = later phase.

---

## Why browser automation on the feed?

| Approach | Discovery | Comment | Blocker |
|----------|-----------|---------|---------|
| **Composio API only** | No home-feed API | Yes, if you have post URN | You must manually find 30 posts/day |
| **Notion queue only** | Manual save | API or manual | Doesn’t scale to 30/session |
| **Browser (feed scroll)** | Yes — scroll, filter, open posts | Type + submit in UI (or extract URN → Composio) | ToS risk, DOM changes, login/captcha |

**Conclusion:** For **30 comments / 90 min**, you need **feed discovery**. That basically means **browser** (Cursor browser MCP for assisted runs, or **Playwright** on your logged-in Chrome profile for local scheduled runs). API alone cannot scroll the feed.

---

## Target volume & pacing

| Metric | Target |
|--------|--------|
| **Window** | 90 min (same block as golden hour on publish days, or standalone Tue–Thu) |
| **Comments** | **≥30** (~1 every 2–3 min including scroll/read time) |
| **Quality** | Depth Score 4-part (see below) — **no** “Great post!” spam |
| **Skip** | Engagement bait, polls you didn’t read, posts >48h old, non-niche |

Pace math: 90 min ÷ 30 = **3 min/comment** (scroll + read + draft + post). Tight but feasible if comments stay short (120–400 chars) and scroll is filtered (niche keywords, followed creators, hashtags).

---

## Comment quality rubric (unchanged)

1. **Acknowledge** — specific line from their post  
2. **Add** — one insight or counter-point  
3. **Extend** — max one sentence of your experience  
4. **Question** — one open question  

**Never:** URLs, DM CTAs, hashtag stacks.

---

## Proposed architecture (browser-first)

```
LinkedIn feed (logged-in browser)
  → scroll + extract post cards (author, snippet, permalink, activity URN if visible)
  → niche filter (PM, builder, India startup, skip bait)
  → LLM draft comment (persona + strategy from Notion)
  → post via UI comment box OR Composio if URN resolved
  → log to Notion Engagement Queue (Posted / Skipped)
  → random delay 90–180s before next
```

### Option A — Cursor browser MCP (assisted)

- **You** stay logged into LinkedIn in Cursor’s browser tab.
- Agent: `browser_navigate` → feed → `browser_scroll` → snapshot → pick posts → draft → `browser_click` + `browser_type` on comment box.
- **Pros:** No new stack; you can approve/skip per comment in chat.
- **Cons:** Not unattended 90 min; cloud agents can’t use your session; fragile if LinkedIn UI shifts.

### Option B — Local Playwright (recommended for 90 min / 30 comments)

- Script under `~/LinkedIn Automation/linkedin-feed-engage/` using **persistent Chrome profile** (already logged in).
- launchd same days as golden hour, or chained after your post goes live.
- **Pros:** Runs 90 min locally; human-like delays; full scroll loop.
- **Cons:** Build + maintain selectors; account restriction risk if too robotic.

### Option C — Hybrid (best risk/reward)

- **Browser:** discover + filter only → write candidates to Notion queue or JSONL.
- **Composio:** post comment when URN extracted (faster, no comment-box DOM).
- **Fallback:** browser UI if Composio 404 on URN.

---

## Risks (read before building)

1. **LinkedIn ToS** — automated scrolling and bulk commenting can trigger restrictions or bans.  
2. **Detection** — identical timing, same comment patterns, new accounts = higher risk. Use jitter, varied openers, skip low-fit posts.  
3. **DOM fragility** — LinkedIn changes class names often; Playwright selectors break.  
4. **Login** — passkey/2FA/captcha stops unattended runs; Mac must be awake.  
5. **Quality at 30** — volume increases spam perception; filter aggressively (niche-only, skip generic viral posts).

---

## Notion logging (lightweight)

Engagement Queue DB — one row per comment attempt:

| Property | Use |
|----------|-----|
| `Status` | `Drafted` → `Posted` / `Skipped` / `Failed` |
| `Post URL` | Permalink |
| `Author` | From feed card |
| `Draft comment` | Agent output |
| `Posted on` | Timestamp |

No metrics dashboard — qualitative weekly review only.

---

## Phases

| Phase | Build | Outcome |
|-------|-------|---------|
| **0** | Manual: you scroll 30 min, agent drafts in Cursor from pasted URLs | Validate quality at volume |
| **1** | Browser MCP proof: scroll feed, comment on **5** posts with approval | Prove selectors + draft loop |
| **2** | Playwright `feed_engage.py --limit 30 --duration 5400 --dry-run` | Unattended discovery + draft log |
| **3** | Live post with delays + Notion log; optional Composio for submit | Full 30/90 goal |

**Do not** jump to Phase 3 without Phase 1 on your real account.

---

## Success criteria

- **≥30 comments** in a 90 min session on publish days (or 3×/week)
- **≥80%** pass quality rubric on spot-check (you review 10 random from Notion log)
- **Zero** link drops in comments
- **No** LinkedIn restriction warnings for 30 days

---

## Related automation (already live)

- **Golden hour:** replies on **your** posts — `golden_hour.py watch`
- **Post-live Notion:** `golden_hour.py sync-notion` when Buffer `get_post` → `sent`

---

## Recommended next step

**Phase 1 proof in Cursor browser:** one 15 min session — scroll home feed, niche-filter 5 posts, draft + post comments with your approval. If that works, spec Playwright for 30/90.

Confirm login at https://www.linkedin.com/login then say **"I'm logged in, run feed engage"** — agent uses [`linkedin-feed-engage`](../linkedin-feed-engage/SKILL.md).
