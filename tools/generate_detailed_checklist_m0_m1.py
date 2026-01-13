#!/usr/bin/env python3
"""
generate_detailed_checklist_m0_m1.py

Generates a comprehensive, executable checklist for M0 + M1:
  docs/EXEC_CHECKLIST_M0_M1_DETAILED.md
"""

from pathlib import Path
from datetime import datetime
import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    out = docs_dir / "EXEC_CHECKLIST_M0_M1_DETAILED.md"

    timestamp = datetime.now().isoformat(timespec="seconds")

    text = (
        "# EXECUTABLE CHECKLIST — M0 + M1 (DETAILED)\n\n"
        f"Generated: {timestamp}\n\n"
        "This document is the authoritative execution runbook.\n"
        "Follow steps in order. STOP if any Definition of Done fails.\n\n"
        "---\n\n"
        "## M0 — Repo Discipline (Support Phase)\n\n"
        "- Verify repo structure\n"
        "- Enforce git hygiene (.gitignore, .gitattributes)\n"
        "- Lock CI expectations\n\n"
        "**DoD:** Repo is stable and reproducible.\n\n"
        "---\n\n"
        "## M1 — Cockpit Foundation\n\n"
        "### M1.1 App Location Check\n"
        "- writers-dashboard-app/package.json exists\n"
        "- No nested writers-dashboard-app/writers-dashboard-app/\n\n"
        "**STOP-THE-LINE:** Fix structure if nested.\n\n"
        "### M1.2 Run App\n"
        "cd writers-dashboard-app\n"
        "npm install\n"
        "npm run dev\n\n"
        "**DoD:** Vite dev server runs and page loads.\n\n"
        "### M1.3 Cockpit Layout\n"
        "- Left nav\n"
        "- Center editor\n"
        "- Right inspector\n\n"
        "**DoD:** Three panels render consistently.\n\n"
        "### M1.4 Contracts\n"
        "- spec/contracts/ProjectManifest.json\n"
        "- spec/contracts/PlanNode.json\n"
        "- spec/contracts/ValidationIssue.json\n"
        "- spec/contracts/OverrideRequest.json\n\n"
        "**DoD:** Schemas exist and are committed.\n\n"
        "### M1.5 Persistence\n"
        "- localStorage for node selection\n"
        "- localStorage for notes\n"
        "- localStorage for overrides\n\n"
        "**DoD:** Refresh restores state.\n\n"
        "### M1.6 Validation UI (Stub)\n"
        "- Mock issues rendered\n"
        "- Clicking issue focuses node\n\n"
        "**DoD:** Interaction works.\n\n"
        "### M1.7 Notes Editor\n"
        "- Textarea per node\n"
        "- Auto-save enabled\n\n"
        "**DoD:** Notes persist after refresh.\n\n"
        "### M1.8 Fixtures + Smoke Test\n"
        "- fixtures/toy_project/manifest.json\n"
        "- fixtures/toy_project/nodes.json\n"
        "- npm test passes\n\n"
        "**DoD:** Smoke test green.\n\n"
        "---\n\n"
        "EXIT M1 ONLY WHEN ALL ABOVE CONDITIONS ARE MET.\n"
    )

    out.write_text(text, encoding="utf-8")
    print(f"Wrote detailed checklist to: {out}")


if __name__ == "__main__":
    main()
