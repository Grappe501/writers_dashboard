from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\Writers_dashboard")
ORPHAN_SRC = ROOT / "src"
ARCHIVE = ROOT / "archive" / "_orphaned_src"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
DEST = ARCHIVE / f"src_{STAMP}"

print("=== QUARANTINE ORPHAN SRC ===")
print(f"Orphan src: {ORPHAN_SRC}")
print(f"Archive to: {DEST}")
print("")

if not ORPHAN_SRC.exists():
    print("No orphan src found. Nothing to do.")
    raise SystemExit(0)

ARCHIVE.mkdir(parents=True, exist_ok=True)

print("Moving orphan src into archive...")
shutil.move(str(ORPHAN_SRC), str(DEST))
print("✅ Orphan src quarantined safely.")
