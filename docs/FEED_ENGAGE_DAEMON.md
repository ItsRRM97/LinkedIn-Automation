# Feed Engage Daemon (hands-off)

Automated feed comments tied to your Buffer publish schedule. No Cursor browser agent.

## Cost (LLM)

| Provider | Model | Est. monthly @ 100 comments/day |
|----------|-------|----------------------------------|
| **Groq** (default) | `llama-3.3-70b-versatile` | **$0** on free tier (rate limits apply) |
| **OpenRouter** | `google/gemini-2.5-flash-lite` or Nemotron free | **$0** to low cost depending on model |

Token math: ~2k tokens per comment × 100/day ≈ **200k tokens/day**. Free NVIDIA models on OpenRouter are **$0/M** but may throttle at peak hours. Spread pacing (built in) helps stay under limits.

## What runs where

| Component | Runs on | Laptop off? |
|-----------|---------|-------------|
| `publish_day_watch.sh` (launchd) | Your Mac | **No** — Mac must be awake |
| Feed fetch | linkedincli (cookies) | Your Mac |
| Comment post | **Composio** `LINKEDIN_CREATE_COMMENT_ON_POST` | Your Mac |
| Golden hour (Composio) | Your Mac | **No** |
| **Cursor Cloud Agent** | Cursor cloud | **Not for this** — no access to your LinkedIn cookies, Buffer token, or local launchd |

For laptop-off operation you need a **small always-on host** (Mac mini, VPS, or cloud VM) with the same env vars and launchd/cron. Cursor Cloud Agent is for code tasks in GitHub repos, not for driving your LinkedIn session locally.

## One-time setup (you do this once)

### 1. Groq API key (free tier, default)

1. Sign up at [console.groq.com](https://console.groq.com)
2. Create an API key
3. Add to `~/.zshrc`:

```bash
export GROQ_API_KEY="gsk_..."
export FEED_GROQ_MODEL="llama-3.3-70b-versatile"
```

Default model in `config.json`: `llama-3.3-70b-versatile` (free tier with rate limits).

**OpenRouter (optional fallback):** set `llm.provider` to `openrouter` in `config.json` and export `OPENROUTER_API_KEY`.

### 2. LinkedIn session cookies (linkedincli)

```bash
bash scripts/import_linkedin_cookies.sh
```

Requires Chrome logged into [linkedin.com](https://www.linkedin.com) and `pip install browser_cookie3` (script installs if missing). Writes `LINKEDIN_LI_AT` and `LINKEDIN_JSESSIONID` to `~/.zshrc`.

Manual fallback (DevTools → Application → Cookies → `linkedin.com`):

```bash
export LINKEDIN_LI_AT="..."
export LINKEDIN_JSESSIONID='ajax:...'
```

Verify read access:

```bash
npx -y @bcharleson/linkedincli feed view --limit 3
```

Verify write access (optional smoke test):

```bash
npx -y @bcharleson/linkedincli engage comment <activity-id> --text "Test comment"
```

If import fails with missing `li_at`, log into LinkedIn in Chrome again and re-run the import script.

### 3. Buffer + golden hour config (already in repo)

```bash
cp linkedin-golden-hour/config.example.json linkedin-golden-hour/config.json
# Edit buffer_organization_id, linkedin_channel_id
```

Ensure `BUFFER_MCP_TOKEN` is in `~/.zshrc` (same as golden hour).

### 4. Persona (optional)

Edit `linkedin-feed-engage/persona.txt` or set `FEED_PERSONA` in zshrc.

### 5. Install publish-day schedule

```bash
source ~/.zshrc
bash scripts/install_publish_day_schedule.sh
```

## Daily operation (automatic)

On publish days, launchd runs `publish_day_watch.sh` every **10 minutes** for **105 minutes** (covers −15m pre to +90m post):

1. Notion sync from Buffer
2. Golden hour replies on **your** post
3. **Feed engage daemon** — up to 3 comments per tick, max **100/day**, spread delays

## Manual test

```bash
# Dry run (LLM + filters, no LinkedIn post)
python3 linkedin-feed-engage/feed_engage_daemon.py --dry-run

# Live (posts comments)
python3 linkedin-feed-engage/feed_engage_daemon.py

# Check daily quota
cat linkedin-feed-engage/state/daily_quota.json
```

## Config (`linkedin-feed-engage/config.json`)

| Field | Default | Purpose |
|-------|---------|---------|
| `runner_mode` | `daemon` | Use CLI daemon (`daemon`) or legacy Cursor browser (`browser`) |
| `daily_comment_cap` | `100` | Max comments per UTC day |
| `comments_per_tick` | `3` | Comments per 10-min watch tick |
| `engage_pre_publish_minutes` | `15` | Start commenting before Buffer `dueAt` / live |
| `engage_post_publish_minutes` | `90` | Stop after publish anchor |
| `llm.provider` | `groq` | `groq` or `openrouter` |
| `llm.groq_model` | `llama-3.3-70b-versatile` | Groq model id |

## Troubleshooting

| Error | Fix |
|-------|-----|
| `OPENROUTER_API_KEY not set` | Export key in `~/.zshrc`, `source ~/.zshrc` |
| `LINKEDIN_LI_AT` missing | Export cookies; refresh when session expires |
| `quota_exhausted` | Wait until UTC midnight or lower `daily_comment_cap` |
| `idle` / no window | No Buffer LinkedIn post in −15m…+90m window |
| OpenRouter 429 | Free tier throttle; reduce `comments_per_tick` or switch to Groq |

## Legacy browser mode

Set `"runner_mode": "browser"` in config to restore Cursor browser MCP + `feed_engage_trigger.py`.
