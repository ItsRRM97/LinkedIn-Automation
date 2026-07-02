#!/usr/bin/env bash
# Load automation env vars for launchd/bash without sourcing full ~/.zshrc.
# Avoids zsh-only completions (e.g. bun) breaking bash under launchd.
# shellcheck shell=bash

load_launch_env() {
  local script_dir repo_env zshrc
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  repo_env="$(cd "$script_dir/.." && pwd)"
  zshrc="${HOME}/.zshrc"

  if [[ -f "$repo_env/.env" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$repo_env/.env"
    set +a
  fi

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
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    if [[ "$line" =~ ^export[[:space:]]+((${pattern}))= ]]; then
      # shellcheck disable=SC2163
      eval "$line"
    elif [[ "$line" =~ ^(${pattern})= ]]; then
      # shellcheck disable=SC2163
      eval "export $line"
    fi
  done < <(grep -E "^export (${pattern})=|^(${pattern})=" "$zshrc" 2>/dev/null || true)
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  load_launch_env
  exec "${@:-/bin/bash}"
fi
