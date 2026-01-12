#!/usr/bin/env python3
"""
repo_reorg.py
Reorganize Writers_dashboard into a clean repo layout.
- DRY RUN by default (prints what it would do)
- Use --apply to actually move files
- Moves duplicates (content hash) into archive/_duplicates
- Moves non-build / redundant artifacts into archive/_not_needed
- Keeps & relocates canonical build-plan HTML into Build_plan/
- Generates reports in reports/reorg/

Usage:
  python repo_reorg.py --root "C:\\Users\\User\\Desktop\\Writers_dashboard"
  python repo_reorg.py --root "C:\\Users\\User\\Desktop\\Writers_dashboard" --apply
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# -----------------------------
# Configuration (tune as needed)
# -----------------------------

REPO_LAYOUT = {
    "Build_plan": "Human-readable build plan readers (HTML, assets)",
    "docs": "General documentation / notes",
    "spec": "Machine-readable specs (schemas/contracts)",
    "src": "Implementation code",
    "fixtures": "Test fixtures (ToyBook, Book1Window, etc.)",
    "golden": "Golden outputs / snapshots for determinism",
    "tools": "Utility scripts (build, validate, export)",
    "reports": "Generated reports (kept in repo, but subfolders can be ignored)",
    "archive": "Moved-aside items not needed or duplicates (safe holding area)",
}

ARCHIVE_SUBFOLDERS = [
    "archive/_duplicates",
    "archive/_not_needed",
    "archive/_unknown_review",
]

# Common "non-needed for build" patterns (you can expand)
NOT_NEEDED_EXTENSIONS = {
    ".zip", ".7z", ".rar",
    ".bak", ".tmp", ".log",
}

# Keep these extensions in repo (usually)
KEEP_EXTENSIONS = {
    ".html", ".css", ".js", ".json", ".md", ".txt",
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg",
    ".py", ".ts", ".tsx", ".jsx", ".yaml", ".yml",
    ".csv",
}

# Don't touch git internals
SKIP_DIRS = {".git", ".svn", ".hg", "__pycache__", "node_modules", ".venv"}

# Heuristics for canonical Build_plan files
BUILD_PLAN_HINTS = [
    "Build_plan",
    "MASTER_BUILD_PLAN",
    "MICROSTEP",
    "microsteps",
    "module",
    "m0", "m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8",
]

# A file with these names in root is treated as canonical entrypoint and moved into Build_plan/
CANONICAL_ROOT_FILES = {
    "MASTER_BUILD_PLAN_CONSOLIDATED.html",
    "MASTER_BUILD_PLAN_CONSOLIDATED_V2.html",
    "MASTER_BUILD_PLAN_CONSOLIDATED.html".lower(),
    "index.html",
}

# -----------------------------
# Data structures
# -----------------------------

@dataclass
class FileRecord:
    rel_path: str
    abs_path: str
    size: int
    mtime: str
    sha256: Optional[str] = None
    action: str = "KEEP_IN_PLACE"   # MOVE / KEEP / ARCHIVE
    reason: str = ""
    dest_rel_path: Optional[str] = None


# -----------------------------
# Utility functions
# -----------------------------

def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def is_in_skip_dir(path: Path) -> bool:
    # Checks any part in path (relative) for skip dirs
    return any(part in SKIP_DIRS for part in path.parts)

def normalize_rel(root: Path, p: Path) -> str:
    return str(p.relative_to(root)).replace("\\", "/")

def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def choose_destination(root: Path, rel: str, name: str) -> Tuple[str, str]:
    """
    Determine destination and reason for file.
    Returns: (dest_rel, reason)
    """
    rel_l = rel.lower()
    name_l = name.lower()
    ext = Path(name).suffix.lower()

    # Canonical Build_plan entrypoints
    if name in CANONICAL_ROOT_FILES or name_l in CANONICAL_ROOT_FILES:
        return f"Build_plan/{name}", "Canonical plan entrypoint"

    # Anything already under Build_plan stays there
    if rel_l.startswith("build_plan/"):
        return rel.replace("\\", "/"), "Already in Build_plan"

    # Build-plan-ish HTML goes to Build_plan/
    if ext == ".html" and any(h.lower() in rel_l for h in [h.lower() for h in BUILD_PLAN_HINTS]):
        return f"Build_plan/{Path(name).name}", "HTML appears to be build-plan related"

    # Markdown docs
    if ext == ".md":
        # If it looks like a spec doc
        if any(k in rel_l for k in ["contract", "schema", "spec"]):
            return f"spec/{Path(name).name}", "Spec-like markdown"
        return f"docs/{Path(name).name}", "General markdown documentation"

    # Schemas/contracts
    if ext in {".json", ".yaml", ".yml"} and any(k in rel_l for k in ["schema", "contract", "spec"]):
        return f"spec/{Path(name).name}", "Schema/contract file"

    # Source code
    if ext in {".py", ".js", ".ts", ".tsx", ".jsx"}:
        # If it's clearly a tool
        if any(k in rel_l for k in ["tool", "script", "build", "validate", "export"]):
            return f"tools/{Path(name).name}", "Tooling script"
        return f"src/{Path(name).name}", "Source code"

    # Images: prefer Build_plan/assets if they're plan screenshots/icons
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
        if any(k in rel_l for k in ["build_plan", "micro", "reader", "module", "m0", "m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8"]):
            return f"Build_plan/assets/{Path(name).name}", "Build-plan asset image"
        return f"docs/assets/{Path(name).name}", "Documentation asset image"

    # Fixtures/golden
    if any(k in rel_l for k in ["fixture", "toybook", "book1window"]):
        return f"fixtures/{Path(name).name}", "Fixture file"
    if any(k in rel_l for k in ["golden", "snapshot", "expected_output"]):
        return f"golden/{Path(name).name}", "Golden output"

    # Everything else: keep in docs if it's a known safe extension
    if ext in KEEP_EXTENSIONS:
        return f"docs/misc/{Path(name).name}", "Misc keep-extension file"

    # Otherwise unknown
    return "archive/_unknown_review/" + Path(name).name, "Unknown file type; review"


def classify_not_needed(path: Path, rel: str) -> Optional[str]:
    """
    Return reason if file should be archived as not needed.
    """
    ext = path.suffix.lower()
    rel_l = rel.lower()

    # Archive packaged artifacts
    if ext in NOT_NEEDED_EXTENSIONS:
        return f"Packaged artifact ({ext})"

    # Common exported duplicates or old builds
    if any(k in rel_l for k in ["old", "backup", "export", "exports", "tmp", "temp"]):
        # Avoid archiving if it's clearly canonical build plan
        if "build_plan" not in rel_l:
            return "Looks like export/backup/temp"

    return None


def move_file(src: Path, dest: Path) -> None:
    safe_mkdir(dest.parent)
    # If destination exists, disambiguate
    if dest.exists():
        stem = dest.stem
        suffix = dest.suffix
        parent = dest.parent
        i = 2
        while True:
            candidate = parent / f"{stem}__{i}{suffix}"
            if not candidate.exists():
                dest = candidate
                break
            i += 1
    shutil.move(str(src), str(dest))


# -----------------------------
# Main logic
# -----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Repo root path")
    ap.add_argument("--apply", action="store_true", help="Actually move files (default is dry-run)")
    ap.add_argument("--hash", action="store_true", help="Compute sha256 for all files (slower)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Root does not exist: {root}")

    # Ensure layout dirs exist (dry-run still prints)
    planned_dirs = list(REPO_LAYOUT.keys()) + ARCHIVE_SUBFOLDERS

    stamp = now_stamp()
    report_dir = root / "reports" / "reorg" / stamp
    report_csv = report_dir / "reorg_report.csv"
    report_json = report_dir / "reorg_report.json"

    # Scan files
    records: List[FileRecord] = []
    hash_map: Dict[str, List[Path]] = {}  # sha -> paths

    for p in root.rglob("*"):
        if p.is_dir():
            continue
        rel = normalize_rel(root, p)
        if is_in_skip_dir(Path(rel)):
            continue

        stat = p.stat()
        rec = FileRecord(
            rel_path=rel,
            abs_path=str(p),
            size=stat.st_size,
            mtime=datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        )

        # hash for duplicates (always hash if --apply? no; optional for speed)
        if args.hash:
            try:
                rec.sha256 = sha256_file(p)
                hash_map.setdefault(rec.sha256, []).append(p)
            except Exception as e:
                rec.reason = f"Hash failed: {e}"

        records.append(rec)

    # Identify duplicates (only if hashing enabled)
    dup_paths = set()
    if args.hash:
        for sha, paths in hash_map.items():
            if len(paths) > 1:
                # Keep the newest (mtime) as canonical, archive others
                paths_sorted = sorted(paths, key=lambda x: x.stat().st_mtime, reverse=True)
                keep = paths_sorted[0]
                for d in paths_sorted[1:]:
                    dup_paths.add(d.resolve())

    # Decide actions
    actions: List[Tuple[Path, Path]] = []

    for rec in records:
        src = Path(rec.abs_path)
        rel = rec.rel_path
        name = src.name

        # Skip anything already in .git or in archive? We'll still allow in archive review.
        rel_l = rel.lower()

        # Create directories (planned)
        # (done later)

        # Duplicate handling (hash-based)
        if args.hash and src.resolve() in dup_paths:
            rec.action = "MOVE_TO_ARCHIVE_DUPLICATE"
            rec.reason = "Duplicate content (sha256 match)"
            dest_rel = f"archive/_duplicates/{name}"
            rec.dest_rel_path = dest_rel
            actions.append((src, root / dest_rel))
            continue

        # Not needed handling (zip/old/temp)
        not_needed_reason = classify_not_needed(src, rel)
        if not_needed_reason and not rel_l.startswith("archive/"):
            rec.action = "MOVE_TO_ARCHIVE_NOT_NEEDED"
            rec.reason = not_needed_reason
            dest_rel = f"archive/_not_needed/{name}"
            rec.dest_rel_path = dest_rel
            actions.append((src, root / dest_rel))
            continue

        # Choose destination for keep files
        dest_rel, reason = choose_destination(root, rel, name)

        # If already at destination, keep
        if normalize_rel(root, src) == dest_rel:
            rec.action = "KEEP_IN_PLACE"
            rec.reason = reason
            rec.dest_rel_path = dest_rel
            continue

        # If destination is archive unknown, mark for archive review
        if dest_rel.startswith("archive/_unknown_review/"):
            rec.action = "MOVE_TO_ARCHIVE_UNKNOWN"
        else:
            rec.action = "MOVE_TO_DEST"

        rec.reason = reason
        rec.dest_rel_path = dest_rel

        # Avoid moving files that are already in correct folder tree (e.g. subfiles under Build_plan)
        # But if they are outside, we move them in.
        actions.append((src, root / dest_rel))

    # DRY RUN output
    print("\n=== Planned directories ===")
    for d in planned_dirs:
        print("  ", d)

    print("\n=== Planned moves ===")
    for src, dst in actions:
        # do not move if src is inside dst already (rare); just print
        print(f"  MOVE: {src} -> {dst}")

    # Apply
    if args.apply:
        print("\n=== Applying changes ===")
        # Create layout dirs
        for d in planned_dirs:
            safe_mkdir(root / d)
        safe_mkdir(report_dir)

        # Execute moves
        for src, dst in actions:
            # Skip if src doesn't exist (may have been moved already due to earlier operations)
            if not src.exists():
                continue
            # Don't move report files into themselves
            if report_dir in src.parents:
                continue
            move_file(src, dst)

        print("Moves complete.")

    # Always write reports (even dry run) into console only unless apply (to avoid creating dirs)
    # If apply, write to disk; if dry run, print summary + suggestion
    summary = {
        "root": str(root),
        "timestamp": stamp,
        "apply": args.apply,
        "hashing": args.hash,
        "counts": {
            "total_files_scanned": len(records),
            "moves_planned": len(actions),
            "duplicates_detected": len(dup_paths) if args.hash else None,
        },
        "records": [asdict(r) for r in records],
    }

    if args.apply:
        safe_mkdir(report_dir)
        # CSV
        with report_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["rel_path", "action", "reason", "dest_rel_path", "size", "mtime", "sha256"])
            for r in records:
                w.writerow([r.rel_path, r.action, r.reason, r.dest_rel_path or "", r.size, r.mtime, r.sha256 or ""])
        # JSON
        with report_json.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"\nReports written to: {report_dir}")
    else:
        # Dry run summary
        from collections import Counter
        c = Counter(r.action for r in records)
        print("\n=== DRY RUN SUMMARY ===")
        for k, v in c.most_common():
            print(f"  {k}: {v}")
        print("\nTip: Run again with --hash to detect duplicates by content.")
        print("Tip: Run again with --apply to perform moves (no deletes).")


if __name__ == "__main__":
    main()
