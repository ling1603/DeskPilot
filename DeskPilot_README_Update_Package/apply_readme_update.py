from pathlib import Path
from datetime import datetime
import shutil
import sys

root = Path(__file__).resolve().parent
src = root / "README_new.md"
dst = root / "README.md"

if not src.exists():
    print("[ERROR] 未找到 README_new.md")
    print("请将本脚本与 README_new.md 一起放到 DeskPilot 仓库根目录。")
    sys.exit(1)

if dst.exists():
    backup = root / f"README.backup.{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    shutil.copy2(dst, backup)
    print(f"[OK] 已备份旧 README：{backup.name}")
else:
    print("[WARN] 当前目录没有旧 README.md，将直接创建新 README.md")

shutil.copy2(src, dst)
print("[OK] README.md 已替换完成。")
print("建议继续执行：git diff README.md")
