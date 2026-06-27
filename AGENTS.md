# LinkedIn Automation — Agent bootstrap

Cursor Agent skills + Python/bash automation for a LinkedIn content pipeline (Notion → Buffer scheduling, golden-hour replies, feed engagement). See `README.md` for the full module map and CLI reference.

## Cursor Cloud specific instructions

- The Python scripts (`linkedin-golden-hour/golden_hour.py`, `linkedin-feed-engage/feed_engage_trigger.py`, etc.) use **only the standard library** (Notion is called via `urllib`) — there is nothing to `pip install` and no virtualenv is needed. Python 3.10+ is sufficient (cloud VM has 3.12). `python3 <script> -h` works out of the box.
- This is a macOS-oriented automation toolkit and **cannot run end-to-end in the cloud VM**: scripts need a local `linkedin-golden-hour/config.json` (copy from `config.example.json`), env vars (`NOTION_TOKEN`, `BUFFER_MCP_TOKEN`, …), external accounts (Notion, Buffer, Composio), an authenticated browser LinkedIn session, and macOS `launchd` scheduling. Without config/tokens, commands like `golden_hour.py watch --dry-run` correctly fail fast with a clear "Missing config" / missing-token error — that confirms the Python environment is healthy.
