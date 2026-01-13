#!/usr/bin/env python3
"""
generate_detailed_checklist_m0_m1.py

Generates a comprehensive, executable checklist for M0 + M1:
  docs/EXEC_CHECKLIST_M0_M1_DETAILED.md

Usage:
  python tools/generate_detailed_checklist_m0_m1.py --root "C:\\Users\\User\\Desktop\\Writers_dashboard"
"""

from pathlib import Path
from datetime import datetime
import argparse


def now_stamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Repo root path")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    out = docs_dir / "EXEC_CHECKLIST_M0_M1_DETAILED.md"

    text = f"""# EXECUTABLE CHECKLIST — M0 + M1 (DETAILED)

Generated: {now_stamp()}

This is the **no-interpretation** runbook. Execute in order.
Every section has **DoD** (Definition of Done) and **STOP-THE-LINE** gates.

---

## 0) Pre-flight

### 0.1 Confirm repo root + clean status
```powershell
cd "{root}"
git status
