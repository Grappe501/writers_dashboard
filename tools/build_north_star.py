#!/usr/bin/env python3
"""
build_north_star.py
Creates/updates Build_plan/index.html as the single "North Star" hub.

Usage:
  python tools/build_north_star.py --root "C:\\Users\\User\\Desktop\\Writers_dashboard"
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def rel(from_dir: Path, target: Path) -> str:
    return target.relative_to(from_dir).as_posix()


def pick_master(bp: Path) -> Path | None:
    preferred = [
        bp / "MASTER_BUILD_PLAN_CONSOLIDATED_V2.html",
        bp / "MASTER_BUILD_PLAN_CONSOLIDATED.html",
    ]
    for p in preferred:
        if p.exists():
            return p

    hits = sorted(bp.glob("*MASTER_BUILD_PLAN*.html"))
    return hits[0] if hits else None


def pick_microsteps(bp: Path) -> Path | None:
    candidates = [
        bp / "microsteps_full" / "index.html",
        bp / "m0_m8_microsteps" / "index.html",
        bp / "m6_m8_microsteps" / "index.html",
        bp / "m6_m8_microsteps" / "index__2.html",
    ]
    for c in candidates:
        if c.exists():
            return c

    hits = sorted(
        [p for p in bp.rglob("*.html") if p.name.lower().startswith("index") and "micro" in str(p).lower()]
    )
    return hits[0] if hits else None


def discover_module_pages(bp: Path, max_items: int = 80) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    seen: set[str] = set()

    def add(p: Path):
        rp = p.relative_to(bp).as_posix()
        if rp in seen:
            return
        seen.add(rp)
        items.append((rp, rp))

    for p in sorted(bp.rglob("*.html")):
        rp = p.relative_to(bp).as_posix()
        low = rp.lower()
        if low == "index.html":
            continue

        is_moduleish = any(f"/m{i}/" in low or low.startswith(f"m{i}/") for i in range(0, 9))
        is_moduleish = is_moduleish or any(k in low for k in ["v_01", "module", "build_plan", "microsteps"])

        if is_moduleish and ("overview" in low or p.name.lower().startswith("index")):
            add(p)

    if not items:
        for p in sorted(bp.glob("*.html")):
            if p.name.lower() != "index.html":
                add(p)

    return items[:max_items]


HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Writers Dashboard — North Star</title>
<style>
:root{{--bg:#0b0f14;--panel:#111826;--text:#e6edf3;--muted:#9fb0c0;--accent:#6aa9ff;--border:rgba(255,255,255,.08)}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial;background:var(--bg);color:var(--text)}}
.wrap{{display:flex;min-height:100vh}}
nav{{width:340px;max-width:90vw;background:var(--panel);border-right:1px solid var(--border);padding:18px;position:sticky;top:0;height:100vh;overflow:auto}}
main{{flex:1;padding:28px;max-width:1100px}}
h1{{margin:0 0 10px;font-size:28px}}
h2{{margin:22px 0 10px;font-size:18px}}
p{{color:var(--muted);line-height:1.45}}
a{{color:var(--accent);text-decoration:none}}
a:hover{{text-decoration:underline}}
.card{{border:1px solid var(--border);border-radius:14px;padding:14px;background:rgba(255,255,255,.02);margin:10px 0}}
.small{{font-size:13px;color:var(--muted)}}
ul{{margin:8px 0 0 18px;color:var(--muted)}}
code{{background:rgba(255,255,255,.06);padding:2px 6px;border-radius:8px}}
hr{{border:0;border-top:1px solid var(--border);margin:18px 0}}
</style>
</head>
<body>
<div class="wrap">
<nav>
  <h2>North Star</h2>
  <div class="small">Updated: {updated}</div>
  <hr/>
  <div class="card">
    <div><strong>Primary Entry Points</strong></div>
    <ul>
      {primary_links}
    </ul>
  </div>
  <div class="card">
    <div><strong>Module Pages</strong></div>
    <ul>
      {module_links}
    </ul>
  </div>
  <div class="card">
    <div><strong>Repo</strong></div>
    <ul>
      <li><a href="../reports/">Reports</a></li>
      <li><a href="../archive/">Archive</a></li>
    </ul>
  </div>
</nav>
<main>
  <h1>Writers Dashboard — Master Build Plan Hub</h1>
  <p>This is the single file you open. It links to the master reader, microsteps, and module pages.</p>

  <h2>Build Discipline</h2>
  <div class="card">
    <ul>
      <li>No drift: changes must be explicit and logged.</li>
      <li>Determinism: builds reproducible from fixtures + schemas.</li>
      <li>DoD gating: every microstep page ends with Definition of Done.</li>
    </ul>
  </div>

  <h2>Next Actions</h2>
  <div class="card">
    <ul>
      <li>Start with <strong>Microsteps</strong> → follow module order.</li>
      <li>Use <code>reports/</code> for audits (link polish, determinism checks).</li>
      <li>Once verified, keep <code>archive/</code> out of git (optional).</li>
    </ul>
  </div>
</main>
</div>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--build-plan", default="Build_plan")
    args = ap.parse_args()

    repo = Path(args.root).resolve()
    bp = (repo / args.build_plan).resolve()
    bp.mkdir(parents=True, exist_ok=True)

    master = pick_master(bp)
    micro = pick_microsteps(bp)

    primary_items: list[tuple[str, str]] = []
    if master:
        primary_items.append(("Master Reader", rel(bp, master)))
    if micro:
        primary_items.append(("Microsteps (M0–M8)", rel(bp, micro)))
    if not primary_items:
        primary_items.append(("Master Reader (not found)", "#"))
        primary_items.append(("Microsteps (not found)", "#"))

    module_items = discover_module_pages(bp)

    primary_links = "\n      ".join(
        [f'<li><a href="{href}">{label}</a></li>' for label, href in primary_items]
    )
    module_links = "\n      ".join(
        [f'<li><a href="{href}">{label}</a></li>' for label, href in module_items]
    ) or "<li><span class='small'>No module pages found</span></li>"

    out = bp / "index.html"
    out.write_text(
        HTML.format(
            updated=stamp(),
            primary_links=primary_links,
            module_links=module_links,
        ),
        encoding="utf-8",
    )

    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()
