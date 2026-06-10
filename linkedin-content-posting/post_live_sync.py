#!/usr/bin/env python3
"""Wrapper — use `golden_hour.py cleanup-content-library` (Buffer sent → Notion Posted)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / "linkedin-golden-hour" / "golden_hour.py"

if __name__ == "__main__":
    args = ["cleanup-content-library"]
    if "--dry-run" in sys.argv[1:]:
        args.append("--dry-run")
    raise SystemExit(subprocess.call([sys.executable, str(PY), *args]))
