#!/usr/bin/env bash
# Import li_at + JSESSIONID from Chrome into the current shell and ~/.zshrc.
# Requires: pip install browser_cookie3
set -euo pipefail

ZSHRC="${HOME}/.zshrc"
MARKER="# LinkedIn feed engage cookies (import_linkedin_cookies.sh)"
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

if ! python3 -c "import browser_cookie3" 2>/dev/null; then
  echo "Installing browser_cookie3..."
  python3 -m pip install --user browser_cookie3
fi

python3 <<'PY' >"$TMP"
import json
import browser_cookie3

def strip_cookie(value: str) -> str:
    cleaned = value.strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] == '"':
        return cleaned[1:-1]
    return cleaned

cj = browser_cookie3.chrome(domain_name=".linkedin.com")
li_at = jsession = None
for c in cj:
    if c.name == "li_at" and c.value:
        li_at = strip_cookie(c.value)
    elif c.name == "JSESSIONID" and c.value:
        jsession = strip_cookie(c.value)

if not li_at or not jsession:
    raise SystemExit(
        "Could not read li_at/JSESSIONID from Chrome. "
        "Log into linkedin.com in Chrome, then re-run this script."
    )

print(json.dumps({"li_at": li_at, "jsessionid": jsession}))
PY

eval "$(python3 <<PY
import json, shlex
with open("$TMP") as f:
    data = json.load(f)
print(f"export LINKEDIN_LI_AT={shlex.quote(data['li_at'])}")
print(f"export LINKEDIN_JSESSIONID={shlex.quote(data['jsessionid'])}")
PY
)"

python3 <<PY
import json
import shlex
from pathlib import Path

with open("$TMP") as f:
    data = json.load(f)

zshrc = Path("${ZSHRC}")
marker = "${MARKER}"
li_at = data["li_at"]
jsession = data["jsessionid"]

block = f"""{marker}
export LINKEDIN_LI_AT={shlex.quote(li_at)}
export LINKEDIN_JSESSIONID={shlex.quote(jsession)}
"""

text = zshrc.read_text() if zshrc.exists() else ""
if marker in text:
    start = text.index(marker)
    end = text.find("\n\n", start)
    if end == -1:
        end = len(text)
    else:
        end += 2
    text = text[:start] + block + text[end:]
else:
    if text and not text.endswith("\n"):
        text += "\n"
    text += "\n" + block

zshrc.write_text(text)
print(f"Updated {zshrc}")
PY

echo "Exported LINKEDIN_LI_AT and LINKEDIN_JSESSIONID for this shell."
echo "Verify:"
echo "  npx -y @bcharleson/linkedincli feed view --limit 2"
