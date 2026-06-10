# Launchd jobs

## Use this (canonical)

| Label | Plist | Install |
|-------|-------|---------|
| `com.rawshn.linkedin-publish-day-watch` | `com.rawshn.linkedin-publish-day-watch.plist` | `../scripts/install_publish_day_schedule.sh` |

Tue–Thu 10:00 local → `publish_day_watch.sh` every 10m × 90m:

1. `cleanup-content-library`
2. `golden_hour watch`
3. `feed_engage_trigger`

## Deprecated — do not install

| Label | Plist | Notes |
|-------|-------|-------|
| `com.rawshn.linkedin-golden-hour-con138` | `com.rawshn.linkedin-golden-hour-con138.plist` | Superseded by publish-day watcher |
| `com.rawshn.linkedin-golden-hour-watch` | `com.rawshn.linkedin-golden-hour-watch.plist` | Use publish-day watcher instead |

Unload a deprecated job if it was loaded earlier:

```bash
launchctl bootout "gui/$(id -u)" ~/Library/LaunchAgents/com.rawshn.linkedin-golden-hour-con138.plist 2>/dev/null || true
```

`install_golden_hour_schedule.sh` forwards to `install_publish_day_schedule.sh`.
