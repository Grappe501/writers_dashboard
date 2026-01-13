#!/usr/bin/env python3
"""
READ-ONLY repo mapper for Writers_dashboard.

Outputs:
- reports/repo_tree.txt            (tree view)
- reports/src_locations.txt        (all src folders + key file presence)
- reports/suspicious_paths.txt     (nested-app patterns + duplicate roots)

Usage (from repo root):
  python tools/map_repo.py

Or point at a specific root:
  python tools/map_repo.py "C:\\Users\\User\\Desktop\\Writers_dashboard"
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from datetime import datetime

# Keep these lean: we want structure, not noise.
DEFAULT_IGNORES = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    ".turbo",
    ".cache",
    ".idea",
    ".vscode",
}

KEY_SRC_FILES = [
    "App.tsx",
    "main.tsx",
    "index.tsx",
    "vite-env.d.ts",
    "App.jsx",
    "main.jsx",
]

def should_ignore(path: Path) -> bool:
    parts = set(path.parts)
    if parts & DEFAULT_IGNORES:
        return True
    # Ignore huge lock/artefact dirs if needed; keep conservative.
    return False

def write_tree(root: Path, out_path: Path, max_files_per_dir: int = 80) -> None:
    """
    Write a tree representation. We cap files per directory to avoid megadumps.
    """
    lines = []
    root = root.resolve()

    def walk(dir_path: Path, prefix: str = ""):
        try:
            entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            lines.append(f"{prefix}[PERMISSION DENIED] {dir_path.name}/")
            return

        # Filter ignored
        entries = [e for e in entries if not should_ignore(e)]

        # Cap noisy dirs
        if len(entries) > max_files_per_dir:
            shown = entries[:max_files_per_dir]
            omitted = len(entries) - max_files_per_dir
        else:
            shown = entries
            omitted = 0

        for i, entry in enumerate(shown):
            is_last = (i == len(shown) - 1) and (omitted == 0)
            connector = "└── " if is_last else "├── "
            if entry.is_dir():
                lines.append(f"{prefix}{connector}{entry.name}/")
                walk(entry, prefix + ("    " if is_last else "│   "))
            else:
                lines.append(f"{prefix}{connector}{entry.name}")

        if omitted > 0:
            lines.append(f"{prefix}└── ... ({omitted} more items omitted)")

    lines.append(f"ROOT: {root}")
    lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")
    lines.append(f"{root.name}/")
    walk(root)
    out_path.write_text("\n".join(lines), encoding="utf-8")

def find_src_folders(root: Path) -> list[Path]:
    srcs: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        p = Path(dirpath)
        if should_ignore(p):
            dirnames[:] = []  # don't descend
            continue
        # quick ignore for node_modules already handled by should_ignore
        if p.name == "src":
            srcs.append(p)
            # still descend? usually not needed; skip for speed
            dirnames[:] = []
    return sorted(set(s.resolve() for s in srcs))

def describe_src(src_path: Path) -> str:
    """
    For each src folder, report presence of key files.
    """
    present = []
    for f in KEY_SRC_FILES:
        if (src_path / f).exists():
            present.append(f)
    # top-level first few entries for sanity
    top_entries = []
    try:
        for e in sorted(src_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))[:25]:
            top_entries.append(e.name + ("/" if e.is_dir() else ""))
    except Exception:
        top_entries = ["[unreadable]"]
    return (
        f"SRC: {src_path}\n"
        f"  Key files present: {', '.join(present) if present else '(none)'}\n"
        f"  First entries: {', '.join(top_entries)}\n"
    )

def suspicious_patterns(root: Path) -> list[str]:
    """
    Flag common flip-flop / nesting issues:
    - writers-dashboard-app/writers-dashboard-app/
    - multiple app roots with package.json
    - src folders outside intended app root
    """
    flags: list[str] = []
    root = root.resolve()

    # 1) Nested folder pattern
    for p in root.rglob("*"):
        if should_ignore(p):
            continue
        if p.is_dir():
            parts = [x.lower() for x in p.parts]
            # detect .../writers-dashboard-app/writers-dashboard-app/...
            for i in range(len(parts) - 1):
                if parts[i] == "writers-dashboard-app" and parts[i + 1] == "writers-dashboard-app":
                    flags.append(f"Nested app folder detected: {p}")
                    break

    # 2) package.json locations
    package_jsons = []
    for pj in root.rglob("package.json"):
        if should_ignore(pj):
            continue
        package_jsons.append(pj.resolve())
    if len(package_jsons) > 1:
        flags.append("Multiple package.json detected (possible multiple app roots):")
        flags.extend([f"  - {p}" for p in package_jsons])
    elif len(package_jsons) == 1:
        flags.append(f"Single package.json detected at: {package_jsons[0]}")

    # 3) src folder locations
    srcs = find_src_folders(root)
    if len(srcs) == 0:
        flags.append("No src/ folders found (unexpected for Vite app).")
    else:
        flags.append("All src/ folders found:")
        flags.extend([f"  - {s}" for s in srcs])

    # 4) Common “empty app root” check: writers-dashboard-app exists but has no src
    expected = root / "writers-dashboard-app" / "src"
    if (root / "writers-dashboard-app").exists():
        if not expected.exists():
            flags.append(f"Expected app src missing: {expected}")
        else:
            flags.append(f"Expected app src present: {expected}")

    return flags

def main():
    arg_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    root = arg_root.resolve()

    reports_dir = root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    tree_out = reports_dir / "repo_tree.txt"
    src_out = reports_dir / "src_locations.txt"
    sus_out = reports_dir / "suspicious_paths.txt"

    write_tree(root, tree_out)

    srcs = find_src_folders(root)
    src_lines = [f"ROOT: {root}", f"Generated: {datetime.now().isoformat(timespec='seconds')}", ""]
    if not srcs:
        src_lines.append("No src/ folders found.")
    else:
        for s in srcs:
            src_lines.append(describe_src(s))
    src_out.write_text("\n".join(src_lines), encoding="utf-8")

    flags = suspicious_patterns(root)
    sus_out.write_text("\n".join(flags), encoding="utf-8")

    print("✅ Repo mapping complete.")
    print(f"- {tree_out}")
    print(f"- {src_out}")
    print(f"- {sus_out}")

if __name__ == "__main__":
    main()
