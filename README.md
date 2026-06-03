# LinkedIn Automation

Cursor skills + scripts for Roshan's LinkedIn pipeline (Notion → Buffer → Composio).

| Folder | Purpose |
|--------|---------|
| `linkedin-content-posting/` | Schedule/publish · post-live Notion sync · proactive comments plan |
| `linkedin-golden-hour/` | Auto-reply to comments on **your** posts |
| `linkedin-feed-engage/` | Proactive feed comments via **Cursor browser** (30/30 continuous) |

**Registry:** `~/.agent-skills/skills.manifest.json`

**Quick run (manual tick):**

```bash
python3 ~/Projects/LinkedIn\ Automation/linkedin-golden-hour/golden_hour.py watch
```

**Publish day (all posts — CON-138 and every future Buffer send):**

```bash
bash ~/Projects/LinkedIn\ Automation/scripts/install_publish_day_schedule.sh
```

Already installed: `com.rawshn.linkedin-publish-day-watch` · Tue–Thu 10:00 → every 10m × 90m.

Each tick: `golden_hour watch` (reply on your post) + `feed_engage_trigger` (arm 30 feed comments when Buffer `sent`). CON-138 uses the same watcher; rich reply themes come from `linkedin-golden-hour/campaigns/CON-138.json`.

**Publish day:** Mac awake · Cursor open · LinkedIn logged in at `/feed/`.

**Post-live Notion sync:**

```bash
python3 ~/Projects/LinkedIn\ Automation/linkedin-golden-hour/golden_hour.py sync-notion
```
