#!/bin/bash
# Optional: launch local Cursor agent for feed engage when CURSOR_API_KEY + cursor_sdk exist.
set -euo pipefail

ROOT="/Users/rawshn/Projects/LinkedIn Automation"
ARMED="$ROOT/linkedin-feed-engage/state/feed_engage_armed.json"
PROMPT_FILE="$ROOT/linkedin-feed-engage/state/agent_prompt.txt"
LOG="$ROOT/logs/feed-engage-agent-trigger.log"

mkdir -p "$(dirname "$LOG")"

if [[ ! -f "$ARMED" ]]; then
  exit 0
fi

if [[ -f "$HOME/.zshrc" ]]; then
  # shellcheck disable=SC1090
  source "$HOME/.zshrc"
fi

if [[ -z "${CURSOR_API_KEY:-}" ]]; then
  echo "[$(date -Iseconds)] CURSOR_API_KEY not set — skipping SDK agent launch (use Cursor + armed prompt file)" >>"$LOG"
  exit 0
fi

if ! python3 -c "import cursor_sdk" 2>/dev/null; then
  echo "[$(date -Iseconds)] cursor_sdk not installed — pip install cursor-sdk" >>"$LOG"
  exit 0
fi

PROMPT="$(cat "$PROMPT_FILE")"

python3 <<PY >>"$LOG" 2>&1
import os
from cursor_sdk import Agent, AgentOptions, LocalAgentOptions

prompt = open("$PROMPT_FILE").read()
result = Agent.prompt(
    prompt,
    AgentOptions(
        api_key=os.environ["CURSOR_API_KEY"],
        model="composer-2.5",
        local=LocalAgentOptions(cwd="$ROOT"),
    ),
)
print(result.status, (result.result or "")[:500])
PY

echo "[$(date -Iseconds)] SDK agent launch attempted" >>"$LOG"
