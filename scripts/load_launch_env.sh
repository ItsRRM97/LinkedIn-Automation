#!/usr/bin/env bash
# Load automation env vars for launchd/bash without sourcing full ~/.zshrc.
# Avoids zsh-only completions (e.g. bun) breaking bash under launchd.
# shellcheck shell=bash

load_launch_env() {
  local zshrc="${HOME}/.zshrc"
  [[ -f "$zshrc" ]] || return 0

  local -a vars=(
    BUFFER_MCP_TOKEN
    NOTION_TOKEN
    NOTION_API_KEY
    NOTION_CONTENT_LIBRARY_DB
    LINKEDIN_ACTOR_ID
    GROQ_API_KEY
    OPENROUTER_API_KEY
    FEED_GROQ_MODEL
    OPENROUTER_MODEL
    FEED_OPENROUTER_MODEL
    FEED_LLM_PROVIDER
    LINKEDIN_LI_AT
    LINKEDIN_JSESSIONID
    LI_AT
    JSESSIONID
    FEED_PERSONA
    CURSOR_API_KEY
    COMPOSIO_INSTALL_DIR
    COMPOSIO_API_KEY
  )

  local pattern
  pattern="$(IFS='|'; echo "${vars[*]}")"

  while IFS= read -r line; do
    [[ "$line" =~ ^export[[:space:]]+((${pattern}))= ]] || continue
    # shellcheck disable=SC2163
    eval "$line"
  done < <(grep -E "^export (${pattern})=" "$zshrc" 2>/dev/null || true)
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  load_launch_env
  exec "${@:-/bin/bash}"
fi
