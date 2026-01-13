from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\User\Desktop\Writers_dashboard")
APP = ROOT / "writers-dashboard-app"
LEGACY_SRC = APP / "archive" / "_legacy_src" / "src"
TARGET_SRC = APP / "src"

STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = APP / "archive" / "_restore_backups" / f"src_backup_{STAMP}"

print("=== RESTORE APP SRC ===")
print(f"Legacy src:  {LEGACY_SRC}")
print(f"Target src:  {TARGET_SRC}")
print(f"Backup dir:  {BACKUP_DIR}")
print("")

if not LEGACY_SRC.exists():
    raise RuntimeError("Legacy src not found — aborting")

if TARGET_SRC.exists():
    raise RuntimeError("Target src already exists — aborting (manual review required)")

# 1) Backup (copy) legacy src first
BACKUP_DIR.parent.mkdir(parents=True, exist_ok=True)
print("1) Creating backup copy of legacy src...")
shutil.copytree(LEGACY_SRC, BACKUP_DIR)
print("   ✅ Backup created.")

# 2) Move legacy src back into place as writers-dashboard-app/src
print("2) Restoring app src (move)...")
shutil.move(str(LEGACY_SRC), str(TARGET_SRC))
print("   ✅ Restore completed.")

print("\nDONE.")
print("Next: run `dir writers-dashboard-app\\src` and confirm main.tsx exists.")
