# LinkedIn Automation

Cursor skills + scripts for Roshan's LinkedIn pipeline (Notion → Buffer → Composio).

| Folder | Purpose |
|--------|---------|
| `linkedin-content-posting/` | Schedule/publish · Content Library cleanup · proactive comments plan |
| `linkedin-golden-hour/` | Auto-reply to comments on **your** posts |
| `linkedin-feed-engage/` | Proactive feed comments via **Cursor browser** (30/30 continuous) |

**Registry:** `~/.agent-skills/skills.manifest.json`

**Env (`~/.zshrc`):** `BUFFER_MCP_TOKEN` · `NOTION_TOKEN` (and `NOTION_API_KEY` alias) for launchd / CLI.

## Quick run

```bash
python3 ~/Projects/LinkedIn\ Automation/linkedin-golden-hour/golden_hour.py watch
```

**Content Library cleanup** (run before schedule/publish sessions, or via publish-day ticks):

```bash
python3 ~/Projects/LinkedIn\ Automation/linkedin-golden-hour/golden_hour.py cleanup-content-library
```

Alias: `sync-notion`.

## Publish day (all Buffer LinkedIn sends)

```bash
bash ~/Projects/LinkedIn\ Automation/scripts/install_publish_day_schedule.sh
```

**Installed job:** `com.rawshn.linkedin-publish-day-watch` · Tue–Thu 10:00 local → every 10m × 90m.

Each tick (`publish_day_watch.sh`):

1. `cleanup-content-library` — Buffer `sent` → Notion **Posted**
2. `golden_hour watch` — auto-replies on comments on **your** post
3. `feed_engage_trigger` — arms 30 feed comments when Buffer marks post `sent`

Campaign-specific reply themes: `linkedin-golden-hour/campaigns/*.json` (e.g. CON-138, CON-158, CON-159) matched by `buffer_post_id`.

**On publish day:** Mac awake · Cursor open · LinkedIn logged in at [linkedin.com/feed/](https://www.linkedin.com/feed/).

### Deprecated launchd (do not install)

- `com.rawshn.linkedin-golden-hour-con138` — superseded by publish-day watcher above
- `install_golden_hour_schedule.sh` — forwards to `install_publish_day_schedule.sh`

If an old per-post plist is still loaded:

```bash
launchctl bootout "gui/$(id -u)" ~/Library/LaunchAgents/com.rawshn.linkedin-golden-hour-con138.plist 2>/dev/null || true
```
