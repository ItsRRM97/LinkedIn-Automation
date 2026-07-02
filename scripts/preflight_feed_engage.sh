#!/usr/bin/env bash
# Verify env vars for feed_engage_daemon (Groq, cookies, Composio).
set -euo pipefail

# shellcheck source=lib.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

# shellcheck source=load_launch_env.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/load_launch_env.sh"
load_launch_env

CONFIG="$ROOT/linkedin-feed-engage/config.json"
runner_mode="daemon"
if [[ -f "$CONFIG" ]]; then
  runner_mode=$(python3 -c "import json; print(json.load(open('$CONFIG')).get('runner_mode','daemon'))" 2>/dev/null || echo daemon)
fi

if [[ "$runner_mode" != "daemon" ]]; then
  echo "preflight: runner_mode=$runner_mode (browser) — skipping daemon env checks"
  exit 0
fi

missing=()
warnings=()

provider=$(python3 -c "import json; c=json.load(open('$CONFIG')); print((c.get('llm') or {}).get('provider','groq'))" 2>/dev/null || echo groq)

if [[ "$provider" == "groq" ]] && [[ -z "${GROQ_API_KEY:-}" ]]; then
  missing+=(GROQ_API_KEY)
fi
if [[ "$provider" == "openrouter" ]] && [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  missing+=(OPENROUTER_API_KEY)
fi

if [[ -z "${LINKEDIN_LI_AT:-${LI_AT:-}}" ]] || [[ -z "${LINKEDIN_JSESSIONID:-${JSESSIONID:-}}" ]]; then
  missing+=(LINKEDIN_LI_AT/LINKEDIN_JSESSIONID)
fi

if [[ -z "${BUFFER_MCP_TOKEN:-}" ]]; then
  warnings+=(BUFFER_MCP_TOKEN)
fi

if ! command -v composio >/dev/null 2>&1; then
  warnings+=(composio_cli)
fi

if (( ${#missing[@]} > 0 )); then
  echo "preflight FAILED — missing required env:" >&2
  for v in "${missing[@]}"; do
    echo "  - $v" >&2
  done
  echo "" >&2
  echo "Add to ~/.zshrc (must start with export):" >&2
  echo '  export GROQ_API_KEY="gsk_..."' >&2
  echo '  export LINKEDIN_LI_AT="..."' >&2
  echo '  export LINKEDIN_JSESSIONID="ajax:..."' >&2
  echo "" >&2
  echo "Then: source ~/.zshrc" >&2
  echo "Cookies: bash scripts/import_linkedin_cookies.sh" >&2
  echo "See: .env.example and docs/FEED_ENGAGE_DAEMON.md" >&2
  exit 1
fi

if (( ${#warnings[@]} > 0 )); then
  echo "preflight OK with warnings: ${warnings[*]}"
else
  echo "preflight OK (provider=$provider, runner_mode=daemon)"
fi
