#!/bin/bash
# macOS notification when feed engage is armed (Buffer post live).
set -euo pipefail

# shellcheck source=lib.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

TITLE="${1:-LinkedIn post}"

/usr/bin/osascript <<EOF
display notification "Post live — 30 feed comments in ~30 min (continuous auto). Keep Cursor + LinkedIn open." with title "Feed engage armed" subtitle "$TITLE"
EOF

if [[ -x "/Applications/Cursor.app/Contents/Resources/app/bin/cursor" ]]; then
  "/Applications/Cursor.app/Contents/Resources/app/bin/cursor" -r "$ROOT" >/dev/null 2>&1 || true
fi
