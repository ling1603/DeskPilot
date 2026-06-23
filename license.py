"""
许可证配置加载器
----------------
从 license.json 读取版本信息（用户修改优先，打包默认兜底）。

格式：
    { "version": "free" }  或  { "version": "pro" }

加载失败（文件缺失/格式错误）时默认返回 free。
"""

import json
import os
from typing import Dict

from utils.helpers import resource_path, get_user_path


# 许可证文件路径
LICENSE_FILE = get_user_path("license.json")
_LICENSE_BUNDLED = resource_path(os.path.join("config", "license.json"))


def load_license() -> Dict[str, str]:
    """
    加载许可证配置（用户修改版优先，打包默认版兜底）。

    Returns:
        dict: {"version": "free"} 或 {"version": "pro"}
    """
    default = {"version": "free"}

    # 依次尝试：用户修改版 → 打包默认版
    for source_path in (LICENSE_FILE, _LICENSE_BUNDLED):
        if not os.path.exists(source_path):
            continue

        try:
            with open(source_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                continue

            version = data.get("version", "free")
            if version not in ("free", "pro"):
                continue

            return {"version": version}

        except (json.JSONDecodeError, IOError):
            continue

    return default
