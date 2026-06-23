#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -f "README_new.md" ]; then
  echo "[ERROR] 未找到 README_new.md"
  echo "请将本脚本与 README_new.md 一起放到 DeskPilot 仓库根目录。"
  exit 1
fi

timestamp=$(date +"%Y%m%d-%H%M%S")
backup="README.backup.${timestamp}.md"

if [ -f "README.md" ]; then
  cp "README.md" "$backup"
  echo "[OK] 已备份旧 README：$backup"
else
  echo "[WARN] 当前目录没有旧 README.md，将直接创建新 README.md"
fi

cp "README_new.md" "README.md"
echo "[OK] README.md 已替换完成。"
echo "建议继续执行：git diff README.md"
