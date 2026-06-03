#!/bin/bash
# Install local launchd publish-day watcher (golden hour + feed engage trigger).
set -euo pipefail

PLIST_SRC="/Users/rawshn/Projects/LinkedIn Automation/launchd/com.rawshn.linkedin-publish-day-watch.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.rawshn.linkedin-publish-day-watch.plist"
ROOT="/Users/rawshn/Projects/LinkedIn Automation"

mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$ROOT/logs"

chmod +x "$ROOT/scripts/publish_day_watch.sh"
chmod +x "$ROOT/scripts/notify_feed_engage_armed.sh"
chmod +x "$ROOT/scripts/trigger_feed_engage_agent.sh"
chmod +x "$ROOT/linkedin-feed-engage/feed_engage_trigger.py"

cp "$PLIST_SRC" "$PLIST_DST"

USER_UID=$(id -u)
launchctl bootout "gui/$USER_UID" "$PLIST_DST" 2>/dev/null || true
launchctl bootstrap "gui/$USER_UID" "$PLIST_DST"

echo "Installed publish-day watcher."
echo "Schedule: Tue/Wed/Thu 10:00 (Mac local time) → every 10m × 90m"
echo "  • golden_hour.py watch — auto-replies on YOUR post comments"
echo "  • feed_engage_trigger.py — arms 30 feed comments when Buffer marks post sent"
echo ""
echo "Requirements on publish day:"
echo "  1. Mac awake + logged in"
echo "  2. Cursor open; LinkedIn logged in at linkedin.com/feed/"
echo "  3. Optional full zero-click: CURSOR_API_KEY + pip install cursor-sdk"
echo ""
echo "Logs: ~/Projects/LinkedIn Automation/logs/"
