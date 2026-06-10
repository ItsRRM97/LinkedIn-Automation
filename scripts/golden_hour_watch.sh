#!/bin/bash
# Golden hour watcher — runs `golden_hour.py watch` every 10m for 90m.
set -euo pipefail

INTERVAL_SEC="${1:-600}"
DURATION_SEC="${2:-5400}"
ROOT="/Users/rawshn/Projects/LinkedIn Automation"
PY="$ROOT/linkedin-golden-hour/golden_hour.py"
LOG_DIR="$ROOT/logs"

mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/golden-hour-watch-$(date +%Y-%m-%d).log"

if [[ -f "$HOME/.zshrc" ]]; then
  # shellcheck disable=SC1090
  source "$HOME/.zshrc"
fi

export PATH="${COMPOSIO_INSTALL_DIR:-$HOME/.composio}:$PATH"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] $*" | tee -a "$LOG"
}

log "Starting Buffer golden-hour watch (interval=${INTERVAL_SEC}s duration=${DURATION_SEC}s)"

deadline=$((SECONDS + DURATION_SEC))
tick=0
while (( SECONDS < deadline )); do
  tick=$((tick + 1))
  log "--- watch tick $tick ---"
  SYNC_PY="$ROOT/linkedin-golden-hour/golden_hour.py"
  if [[ -f "$SYNC_PY" ]]; then
    log "notion sync from buffer get_post"
    if python3 "$SYNC_PY" cleanup-content-library >>"$LOG" 2>&1; then
      log "notion sync ok"
    else
      log "notion sync failed (see log)"
    fi
  fi
  if python3 "$PY" watch >>"$LOG" 2>&1; then
    log "tick $tick ok"
  else
    log "tick $tick failed (see log)"
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

log "Golden hour watch finished ($tick ticks)"
