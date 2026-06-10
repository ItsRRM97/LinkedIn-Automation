# Launchd jobs

## Canonical (install this)

| Label | Template | Install |
|-------|----------|---------|
| `com.linkedin.publish-day-watch` | `com.linkedin.publish-day-watch.plist.in` | `../scripts/install_publish_day_schedule.sh` |

The installer substitutes `@REPO_ROOT@` and `@HOME@` in the template and copies the result to `~/Library/LaunchAgents/`.

**Schedule:** Tue–Thu 10:00 local → `publish_day_watch.sh` every 10m × 90m:

1. `cleanup-content-library` — Buffer `sent` → Notion **Posted**
2. `golden_hour watch` — auto-replies on comments on **your** post
3. `feed_engage_trigger` — arms feed comments when Buffer marks post `sent`

## Deprecated — do not install

| Label | Plist | Notes |
|-------|-------|-------|
| `com.rawshn.linkedin-golden-hour-con138` | `com.rawshn.linkedin-golden-hour-con138.plist` | Superseded by publish-day watcher |
| `com.rawshn.linkedin-golden-hour-watch` | `com.rawshn.linkedin-golden-hour-watch.plist` | Use publish-day watcher instead |
| `com.rawshn.linkedin-publish-day-watch` | `com.rawshn.linkedin-publish-day-watch.plist` | Hardcoded paths; use template installer |

Unload a deprecated job if it was loaded earlier:

```bash
launchctl bootout "gui/$(id -u)" ~/Library/LaunchAgents/com.rawshn.linkedin-golden-hour-con138.plist 2>/dev/null || true
launchctl bootout "gui/$(id -u)" ~/Library/LaunchAgents/com.rawshn.linkedin-publish-day-watch.plist 2>/dev/null || true
```

`install_golden_hour_schedule.sh` forwards to `install_publish_day_schedule.sh`.
