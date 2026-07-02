#!/bin/bash
# Publish day: golden-hour auto-replies + feed engage trigger when Buffer post goes live.
set -euo pipefail

# shellcheck source=lib.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

INTERVAL_SEC="${1:-600}"
DURATION_SEC="${2:-5400}"
GH_PY="$ROOT/linkedin-golden-hour/golden_hour.py"
FEED_PY="$ROOT/linkedin-feed-engage/feed_engage_trigger.py"
FEED_DAEMON="$ROOT/linkedin-feed-engage/feed_engage_daemon.py"
LOG_DIR="$ROOT/logs"

mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/publish-day-watch-$(date +%Y-%m-%d).log"

# shellcheck source=load_launch_env.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/load_launch_env.sh"
load_launch_env

export PATH="${COMPOSIO_INSTALL_DIR:-$HOME/.composio}:/Applications/Cursor.app/Contents/Resources/app/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] $*" | tee -a "$LOG"
}

log "Starting publish-day watch (interval=${INTERVAL_SEC}s duration=${DURATION_SEC}s)"
log "Tasks: cleanup-content-library → golden_hour watch → feed_engage_daemon"

deadline=$((SECONDS + DURATION_SEC))
tick=0
while (( SECONDS < deadline )); do
  tick=$((tick + 1))
  log "--- publish-day tick $tick ---"

  if [[ -f "$GH_PY" ]]; then
    log "notion sync from buffer get_post"
    if python3 "$GH_PY" cleanup-content-library >>"$LOG" 2>&1; then
      log "notion sync ok"
    else
      log "notion sync failed (see log)"
    fi

    log "golden hour auto-replies (your post comments)"
    if python3 "$GH_PY" watch >>"$LOG" 2>&1; then
      log "golden hour watch ok"
    else
      log "golden hour watch failed (see log)"
    fi
  fi

  if [[ -f "$FEED_DAEMON" ]]; then
    log "feed engage daemon (hands-off CLI comments)"
    if python3 "$FEED_DAEMON" >>"$LOG" 2>&1; then
      log "feed engage daemon ok"
    else
      log "feed engage daemon failed (see log)"
    fi
  elif [[ -f "$FEED_PY" ]]; then
    log "feed engage trigger (legacy Cursor browser arm)"
    if python3 "$FEED_PY" >>"$LOG" 2>&1; then
      log "feed engage trigger ok"
    else
      log "feed engage trigger failed (see log)"
    fi
  fi

  remaining=$((deadline - SECONDS))
  if (( remaining <= 0 )); then
    break
  fi
  sleep_for=$INTERVAL_SEC
  if (( remaining < sleep_for )); then
    sleep_for=$remaining
  fi
  log "sleeping ${sleep_for}s"
  sleep "$sleep_for"
done

log "Publish-day watch finished ($tick ticks)"
