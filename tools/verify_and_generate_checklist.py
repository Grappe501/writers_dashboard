#!/usr/bin/env python3
"""
verify_and_generate_checklist.py

Verifies that required M0 and M1 build-plan artifacts exist,
then generates an executable checklist at:

  docs/EXEC_CHECKLIST_M0_M1.md

Usage:
  python tools/verify_and_generate_checklist.py --root "C:\\Users\\User\\Desktop\\Writers_dashboard"
"""

from pathlib import Path
from datetime import datetime
import argparse
import sys


REQUIRED = [
    "Build_plan",
    "Build_plan/index.html",
    "Build_plan/MASTER_BUILD_PLAN_CONSOLIDATED.html",

    "Build_plan/m0/overview.html",
    "Build_plan/m0/env_setup.html",
    "Build_plan/m0/repo_structure.html",
    "Build_plan/m0/change_control.html",
    "Build_plan/m0/testing_strategy.html",
    "Build_plan/m0/ci_pipeline.html",

    "Build_plan/m1/overview.html",
    "Build_plan/m1/cockpit_layout.html",
    "Build_plan/m1/versioning_autosave.html",
    "Build_plan/m1/validation_conflicts_ui.html",
    "Build_plan/m1/override_workflow.html",
    "Build_plan/m1/item_editor.html",
    "Build_plan/m1/api_contracts.html",
    "Build_plan/m1/tests_fixtures.html",

    "tools/polish_links.py",
    "tools/build_north_star.py",
]


CHECKLIST_TEXT = (
"# Executable Checklist — M0 + M1 (Writers Dashboard)\n\n"
"Generated: {generated}\n\n"
"This checklist is the **authoritative execution runbook** for beginning implementation.\n"
"Follow in order. **STOP means do not proceed.**\n\n"
"---\n\n"
"## M0 — Repo Constitution & Discipline\n\n"
"- [ ] Verify Python, Git, Node, NPM installed\n"
"- [ ] Lock repo folder structure (`Build_plan`, `src`, `tools`, `fixtures`, `spec`, `docs`, `reports`)\n"
"- [ ] Add `.gitattributes` to enforce LF\n"
"- [ ] Update `.gitignore` to exclude archive/reports noise\n"
"- [ ] Create `docs/CHANGELOG_PLAN.md`\n"
"- [ ] Create `docs/testing_strategy.md`\n"
"- [ ] Create `.github/workflows/ci.yml`\n\n"
"**M0 EXIT GATE:** Repo stable, hygiene enforced, CI stub exists\n\n"
"---\n\n"
"## M1 — Cockpit Foundation\n\n"
"- [ ] Scaffold app (Vite + React + TS recommended)\n"
"- [ ] App boots locally (`npm run dev`)\n"
"- [ ] 3-panel cockpit layout renders\n"
"- [ ] Define contracts in `spec/contracts/`\n"
"- [ ] Local autosave via localStorage\n"
"- [ ] Validation panel renders stub issues\n"
"- [ ] Override workflow logs requests\n"
"- [ ] Notes editor persists content\n"
"- [ ] Fixture loads and smoke test passes\n\n"
"**M1 EXIT GATE:** App runs, cockpit exists, persistence + validation work\n\n"
"---\n\n"
"GO if all above boxes are checked.\n"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Repo root path")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    missing = []
    present = []

    for rel in REQUIRED:
        p = root / rel
        if p.exists():
            present.append(rel)
        else:
            missing.append(rel)

    # Write verification report
    report_dir = root / "reports" / "verify"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / f"verify_M0_M1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with report_file.open("w", encoding="utf-8") as f:
        f.write("VERIFY — M0/M1 REQUIRED ARTIFACTS\n\n")
        f.write(f"Root: {root}\n\n")
        f.write("PRESENT:\n")
        for p in present:
            f.write(f"  OK  {p}\n")
        f.write("\nMISSING:\n")
        if not missing:
            f.write("  (none)\n")
        else:
            for m in missing:
                f.write(f"  MISSING  {m}\n")

    # Write checklist
    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    checklist_file = docs_dir / "EXEC_CHECKLIST_M0_M1.md"

    checklist_file.write_text(
        CHECKLIST_TEXT.format(
            generated=datetime.now().isoformat(timespec="seconds")
        ),
        encoding="utf-8",
    )

    print(f"\nVerification report written to:\n  {report_file}")
    print(f"Executable checklist written to:\n  {checklist_file}")

    if missing:
        print("\nSTOP — Missing required artifacts. See report.")
        sys.exit(2)

    print("\nALL REQUIRED ARTIFACTS PRESENT — CLEARED TO BEGIN M1 IMPLEMENTATION.")


if __name__ == "__main__":
    main()
