"""
DeskPilot — 程序入口
====================
技术栈：Python + Tkinter

项目结构：
  main.py                 — 入口（本文件）
  config/settings.py      — 配置常量
  utils/helpers.py        — 工具函数
  models/operation.py     — 数据模型
  services/organizer.py   — 整理服务
  services/undo_manager.py — 撤回管理器
  ui/main_window.py       — 主窗口 UI
"""

import os
import sys

# 确保项目根目录在 Python 搜索路径中，使得各模块可互相导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置控制台输出编码为 UTF-8，避免 emoji 等字符乱码
if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8")

from ui.main_window import MainWindow


if __name__ == "__main__":
    app = MainWindow()
    app.run()
