#!/bin/bash
# Install local launchd publish-day watcher (golden hour + feed engage trigger).
set -euo pipefail

# shellcheck source=lib.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

PLIST_LABEL="com.linkedin.publish-day-watch"
PLIST_DST="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
PLIST_TEMPLATE="$ROOT/launchd/com.linkedin.publish-day-watch.plist.in"

mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$ROOT/logs"

chmod +x "$ROOT/scripts/publish_day_watch.sh"
chmod +x "$ROOT/scripts/notify_feed_engage_armed.sh"
chmod +x "$ROOT/scripts/trigger_feed_engage_agent.sh"
chmod +x "$ROOT/linkedin-feed-engage/feed_engage_trigger.py"

sed -e "s|@REPO_ROOT@|$ROOT|g" -e "s|@HOME@|$HOME|g" "$PLIST_TEMPLATE" > "$PLIST_DST"

USER_UID=$(id -u)
launchctl bootout "gui/$USER_UID" "$PLIST_DST" 2>/dev/null || true
launchctl bootstrap "gui/$USER_UID" "$PLIST_DST"

echo "Installed publish-day watcher."
echo "Schedule: Tue/Wed/Thu 10:00 (Mac local time) → every 10m × 90m"
echo "  • cleanup-content-library — Buffer sent → Notion Posted"
echo "  • golden_hour.py watch — auto-replies on YOUR post comments"
echo "  • feed_engage_daemon.py — hands-off feed comments via linkedincli + Groq"
echo ""
echo "Deprecated (unload if still loaded):"
echo "  com.rawshn.linkedin-publish-day-watch"
echo "  com.rawshn.linkedin-golden-hour-con138"
echo ""
echo "Requirements on publish day:"
echo "  1. Mac awake + logged in"
echo "  2. Env vars in ~/.zshrc (loaded via scripts/load_launch_env.sh)"
echo "  3. LinkedIn cookies: bash scripts/import_linkedin_cookies.sh"
echo ""
echo "Logs: $ROOT/logs/"
