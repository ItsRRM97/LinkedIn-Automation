#!/bin/bash
# Feed engage agent launch — prefers main Cursor chat over SDK subagent.
#
# Default: agent_prompt.txt + macOS notification only (user resumes in main chat).
# Optional: CURSOR_API_KEY + cursor-sdk launches a local agent (may lack browser tabs).
# Set FEED_ENGAGE_SDK_LAUNCH=1 to enable SDK path when API key is present.
set -euo pipefail

# shellcheck source=lib.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

ARMED="$ROOT/linkedin-feed-engage/state/feed_engage_armed.json"
PROMPT_FILE="$ROOT/linkedin-feed-engage/state/agent_prompt.txt"
LOG="$ROOT/logs/feed-engage-agent-trigger.log"

mkdir -p "$(dirname "$LOG")"

if [[ ! -f "$ARMED" ]]; then
  exit 0
fi

# shellcheck source=load_launch_env.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/load_launch_env.sh"
load_launch_env

if [[ -z "${CURSOR_API_KEY:-}" ]]; then
  echo "[$(date -Iseconds)] CURSOR_API_KEY not set — main-agent prompt only ($PROMPT_FILE)" >>"$LOG"
  exit 0
fi

if [[ "${FEED_ENGAGE_SDK_LAUNCH:-0}" != "1" ]]; then
  echo "[$(date -Iseconds)] FEED_ENGAGE_SDK_LAUNCH not set — main-agent prompt only (browser MCP needs main chat)" >>"$LOG"
  exit 0
fi

if ! python3 -c "import cursor_sdk" 2>/dev/null; then
  echo "[$(date -Iseconds)] cursor_sdk not installed — pip install cursor-sdk" >>"$LOG"
  exit 0
fi

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
