"""
功能权限门禁（FeatureGate）
---------------------------
根据许可证版本控制 Pro 功能的可用性。

用法：
    from services.feature_gate import feature_gate

    if feature_gate.is_pro:
        # 执行 Pro 功能
        ...

    # 或者带弹窗提示的检查
    if feature_gate.require_pro("自动监控", parent_window):
        ...

设计原则：
  - 不删除任何现有功能代码，仅在调用前加权限判断
  - 所有 Pro 功能默认拒绝（fail-closed），许可证损坏 = Free 模式
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional

from config.license import load_license


class FeatureGate:
    """功能权限门禁 —— 模块级单例"""

    def __init__(self):
        self._license = load_license()

    # ========== 版本查询 ==========

    @property
    def is_pro(self) -> bool:
        """是否为 Pro 版本"""
        return self._license.get("version") == "pro"

    @property
    def version(self) -> str:
        """返回当前版本字符串 'free' 或 'pro'"""
        return self._license.get("version", "free")

    @property
    def version_label(self) -> str:
        """返回 UI 展示用的版本标签"""
        return "Pro" if self.is_pro else "Free"

    # ========== 功能权限检查 ==========

    def can_use_monitor(self) -> bool:
        """是否可以使用文件夹监控"""
        return self.is_pro

    def can_use_keywords(self) -> bool:
        """是否可以使用关键词匹配"""
        return self.is_pro

    def can_edit_rules(self) -> bool:
        """是否可以使用规则编辑器"""
        return self.is_pro

    # ========== 带提示的权限检查 ==========

    def require_pro(
        self,
        feature_name: str,
        parent: Optional[tk.Tk] = None,
    ) -> bool:
        """
        检查 Pro 权限，非 Pro 时弹出升级提示。

        Args:
            feature_name: 功能名称（用于提示文案）
            parent:       父窗口（用于弹窗模态）

        Returns:
            True 表示权限通过，False 表示已拦截并弹出提示
        """
        if self.is_pro:
            return True

        messagebox.showinfo(
            "Pro 功能",
            f"「{feature_name}」需要 Pro 版本才能使用。\n\n"
            f"当前版本：Free\n"
            f"请升级到 Pro 版本以解锁此功能。",
            parent=parent,
        )
        return False


# 模块级单例 —— 全局共享一个实例
feature_gate = FeatureGate()
