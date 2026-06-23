"""
应用配置常量
-----------
集中管理所有可配置项：分类规则、字体样式、窗口尺寸、文件路径等。
修改配置时只需编辑此文件或 config/rules.json，无需改动业务代码。
"""

# 第一个问题： 整理不了doc文档
# 第二个问题： 整理记录可以改为详细的，比如整理了具体的文件
# 第三个问题： 整理了文件，不要有三个文本文档,report.txt,config,stats.json,直接在软件里显示就好


import json
import os

from utils.helpers import resource_path, get_user_path

# ========== 文件路径 ==========
# 用户数据文件（可读写，exe 同目录 / 开发时项目根目录）
CONFIG_FILE = get_user_path("config.txt")
REPORT_FILE = get_user_path("report.txt")
RULES_FILE = get_user_path("rules.json")

# 打包时随 exe 附带的默认规则（只读，仅作首次加载兜底）
_RULES_BUNDLED = resource_path(os.path.join("config", "rules.json"))

# ========== 默认文件分类规则（硬编码兜底） ==========
# 当 rules.json 加载失败时使用此默认规则，确保程序不会因配置损坏而崩溃。
# 格式：{文件夹名: [扩展名列表]}，扩展名不含点号，统一小写。
RULES = {
    "图片":   ["jpg", "png", "jpeg"],
    "文档":   ["pdf", "docx", "txt"],
    "表格":   ["xlsx", "csv"],
    "视频":   ["mp4", "mov"],
    "压缩包": ["zip", "rar", "7z"],
    "代码":   ["py", "js", "html", "css"],
}


def load_rules() -> dict:
    """
    加载分类规则，并规范化为内部格式。

    加载策略：
      1. 优先读取用户修改过的 rules.json（RULES_FILE）
      2. 若不存在，读取打包附带的默认 rules.json（_RULES_BUNDLED）
      3. 若都不存在或格式错误，回退到硬编码 RULES
      4. 以 "_" 开头的辅助键（如 "_说明"）自动过滤

    支持两种 JSON 写法（自动识别）：
      旧格式（仅扩展名）：
          { "图片": ["jpg", "png", "jpeg"] }
      新格式（扩展名 + 关键词）：
          { "图片": { "extensions": ["jpg", "png"], "keywords": ["screenshot"] } }

    内部统一格式：
          { "图片": { "extensions": [...], "keywords": [...] } }

    Returns:
        dict: 规范化分类规则 {文件夹名: {"extensions": [...], "keywords": [...]}}
    """
    # 依次尝试：用户修改版 → 打包默认版
    for source_path in (RULES_FILE, _RULES_BUNDLED):
        try:
            with open(source_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                continue

            rules = {}
            for key, value in data.items():
                if key.startswith("_"):
                    continue  # 跳过辅助键

                # 规范化：统一转为 {extensions: [...], keywords: [...]}
                if isinstance(value, list):
                    rules[key] = {"extensions": value, "keywords": []}
                elif isinstance(value, dict):
                    rules[key] = {
                        "extensions": value.get("extensions", []),
                        "keywords": value.get("keywords", []),
                    }
                # 其他类型跳过

            if rules:
                return rules

        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            continue

    # 全部失败 → 硬编码默认规则兜底
    return {
        name: {"extensions": exts, "keywords": []}
        for name, exts in RULES.items()
    }

# ========== UI 字体样式 ==========
FONT_TITLE  = ("Arial", 14, "bold")
FONT_NORMAL = ("Arial", 10)

# ========== 窗口设置 ==========
WINDOW_WIDTH  = 600
WINDOW_HEIGHT = 600
