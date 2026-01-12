#!/usr/bin/env python3
"""
polish_links.py
Audit + fix broken relative href/src links across Build_plan HTML after reorg.

- DRY RUN by default (does not modify files)
- Use --apply to write fixes
- Creates backups: *.bak_polish (only when applying)
- Writes reports:
    reports/polish/<timestamp>/broken_links.csv
    reports/polish/<timestamp>/fixed_links.csv

Usage:
  python tools/polish_links.py --root "C:\\Users\\User\\Desktop\\Writers_dashboard"
  python tools/polish_links.py --root "C:\\Users\\User\\Desktop\\Writers_dashboard" --apply
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, unquote

ATTR_RE = re.compile(r"""(?P<attr>\bhref\b|\bsrc\b)\s*=\s*["'](?P<val>[^"']+)["']""", re.IGNORECASE)
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#", "javascript:")

@dataclass
class LinkIssue:
    file: str
    attr: str
    original: str
    resolved_from: str
    status: str  # BROKEN / FIXED
    suggestion: str

def stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def is_external(v: str) -> bool:
    v = v.strip()
    return any(v.lower().startswith(p) for p in SKIP_PREFIXES)

def strip_fragment_query(v: str) -> str:
    parsed = urlparse(v)
    return unquote(parsed.path)

def preserve_suffix(original: str, new_path_only: str) -> str:
    parsed = urlparse(original)
    suffix = ""
    if parsed.query:
        suffix += "?" + parsed.query
    if parsed.fragment:
        suffix += "#" + parsed.fragment
    return new_path_only + suffix

def build_filename_index(build_plan_root: Path) -> dict[str, list[Path]]:
    idx: dict[str, list[Path]] = {}
    for p in build_plan_root.rglob("*"):
        if p.is_file():
            idx.setdefault(p.name.lower(), []).append(p.resolve())
    return idx

def resolve_target(html_file: Path, link_val: str) -> Path:
    raw = strip_fragment_query(link_val)
    return (html_file.parent / raw).resolve()

def to_rel(from_dir: Path, target: Path) -> str:
    rel_path = os.path.relpath(str(target), start=str(from_dir))
    return rel_path.replace("\\", "/")

def choose_best_candidate(current_html: Path, candidates: list[Path]) -> Path:
    cur_dir = current_html.parent.resolve()

    def score(p: Path) -> tuple[int, int, str]:
        same_dir = 1 if p.parent.resolve() == cur_dir else 0
        try:
            relp = os.path.relpath(str(p), start=str(cur_dir)).replace("\\", "/")
            depth = relp.count("/") + 1
        except Exception:
            depth = 9999
        return (same_dir, -depth, str(p).lower())

    return sorted(candidates, key=score, reverse=True)[0]

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Repo root path")
    ap.add_argument("--apply", action="store_true", help="Write changes (default dry-run)")
    ap.add_argument("--build-plan", default="Build_plan", help="Build plan folder (default Build_plan)")
    args = ap.parse_args()

    repo = Path(args.root).resolve()
    bp = (repo / args.build_plan).resolve()
    if not bp.exists():
        raise SystemExit(f"Build plan folder not found: {bp}")

    outdir = repo / "reports" / "polish" / stamp()
    outdir.mkdir(parents=True, exist_ok=True)

    broken_csv = outdir / "broken_links.csv"
    fixed_csv = outdir / "fixed_links.csv"

    filename_index = build_filename_index(bp)

    broken: list[LinkIssue] = []
    fixed: list[LinkIssue] = []

    html_files = sorted([p for p in bp.rglob("*.html") if p.is_file()])

    for f in html_files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        replacements: list[tuple[int, int, str]] = []

        for m in ATTR_RE.finditer(text):
            attr = m.group("attr")
            val = m.group("val")

            if not val or is_external(val):
                continue

            # ignore absolute disk paths like C:\...
            if re.match(r"^[A-Za-z]:[\\/]", val):
                continue

            # ignore data URIs
            if val.lower().startswith("data:"):
                continue

            raw_path = strip_fragment_query(val)
            if not raw_path:
                continue

            target = resolve_target(f, val)
            if target.exists():
                continue

            filename = Path(raw_path).name.lower()
            candidates = filename_index.get(filename, [])

            if not candidates:
                broken.append(
                    LinkIssue(
                        file=f.relative_to(repo).as_posix(),
                        attr=attr,
                        original=val,
                        resolved_from=f.parent.relative_to(repo).as_posix(),
                        status="BROKEN",
                        suggestion="",
                    )
                )
                continue

            best = choose_best_candidate(f, candidates)
            new_rel_path = to_rel(f.parent.resolve(), best.resolve())
            new_val = preserve_suffix(val, new_rel_path)

            broken.append(
                LinkIssue(
                    file=f.relative_to(repo).as_posix(),
                    attr=attr,
                    original=val,
                    resolved_from=f.parent.relative_to(repo).as_posix(),
                    status="BROKEN",
                    suggestion=new_val,
                )
            )
            fixed.append(
                LinkIssue(
                    file=f.relative_to(repo).as_posix(),
                    attr=attr,
                    original=val,
                    resolved_from=f.parent.relative_to(repo).as_posix(),
                    status="FIXED",
                    suggestion=new_val,
                )
            )
            replacements.append((m.start("val"), m.end("val"), new_val))

        if replacements and args.apply:
            bak = f.with_suffix(f.suffix + ".bak_polish")
            if not bak.exists():
                bak.write_text(text, encoding="utf-8", errors="ignore")

            new_text = text
            for start, end, new_val in sorted(replacements, key=lambda x: x[0], reverse=True):
                new_text = new_text[:start] + new_val + new_text[end:]
            f.write_text(new_text, encoding="utf-8", errors="ignore")

    with broken_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "attr", "original", "resolved_from", "status", "suggestion"])
        for r in broken:
            w.writerow([r.file, r.attr, r.original, r.resolved_from, r.status, r.suggestion])

    with fixed_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "attr", "original", "resolved_from", "status", "suggestion"])
        for r in fixed:
            w.writerow([r.file, r.attr, r.original, r.resolved_from, r.status, r.suggestion])

    print(f"\nScanned HTML files: {len(html_files)}")
    print(f"Broken links found: {len(broken)}")
    print(f"Fixes suggested: {len(fixed)}")
    print(f"Reports written to: {outdir}")
    if not args.apply:
        print("Dry run only. Re-run with --apply to write fixes (creates *.bak_polish backups).")

if __name__ == "__main__":
    main()
