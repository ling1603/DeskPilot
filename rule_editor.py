"""
规则编辑器弹窗（RuleEditorDialog）
---------------------------------
提供一个文本编辑器风格的规则编辑界面。

用户可直接编辑 JSON 格式的分类规则，保存后立即生效（重新加载到 FileOrganizer）。

JSON 格式支持两种写法：
  旧（仅扩展名）：   { "图片": ["jpg", "png"] }
  新（扩展名+关键词）：{ "图片": { "extensions": [...], "keywords": [...] } }
"""

import json
import os
import tkinter as tk
from tkinter import messagebox

from config.settings import RULES_FILE, FONT_NORMAL
from utils.helpers import resource_path

# 打包附带的默认规则（rule_editor 首次打开时展示）
_RULES_BUNDLED = resource_path(os.path.join("config", "rules.json"))


class RuleEditorDialog:
    """规则编辑弹窗 —— 基于 tk.Toplevel 的模态对话框"""

    def __init__(self, parent: tk.Tk):
        """
        Args:
            parent: 父窗口（Tk 实例）
        """
        self._parent = parent
        self._result: dict | None = None  # 保存后的结果

        # ========== 构建弹窗 ==========
        self._dialog = tk.Toplevel(parent)
        self._dialog.title("管理分类规则")
        self._dialog.geometry("560x480")
        self._dialog.resizable(True, True)
        self._dialog.transient(parent)   # 保持在父窗口之上
        self._dialog.grab_set()           # 模态：阻塞父窗口交互

        self._build_ui()

        # 居中并等待
        self._dialog.update_idletasks()
        self._center_window()

    # ================================================================
    #  UI 构建
    # ================================================================

    def _build_ui(self) -> None:
        """构建编辑器界面"""
        # 说明文字
        hint = (
            "编辑分类规则（JSON 格式）\n"
            "格式：{\"分类名\": {\"extensions\": [\"扩展名\"], \"keywords\": [\"关键词\"]}}\n"
            "旧格式 {\"分类名\": [\"扩展名\"]} 也兼容，以 _ 开头的键会被忽略"
        )
        tk.Label(
            self._dialog, text=hint,
            font=FONT_NORMAL, fg="gray", justify="left",
        ).pack(padx=10, pady=(10, 5), anchor="w")

        # 编辑框容器
        frame = tk.Frame(self._dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        self._text = tk.Text(
            frame,
            font=("Consolas", 10),
            wrap="none",
            undo=True,
        )
        # 水平 + 垂直滚动条
        v_scroll = tk.Scrollbar(frame, orient="vertical", command=self._text.yview)
        h_scroll = tk.Scrollbar(frame, orient="horizontal", command=self._text.xview)
        self._text.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self._text.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # 加载当前规则
        self._load_current_rules()

        # 按钮行
        btn_frame = tk.Frame(self._dialog)
        btn_frame.pack(fill="x", padx=10, pady=(5, 10))

        tk.Button(
            btn_frame, text="保存", width=10,
            command=self._on_save,
        ).pack(side="right", padx=4)

        tk.Button(
            btn_frame, text="取消", width=10,
            command=self._on_cancel,
        ).pack(side="right", padx=4)

    # ================================================================
    #  数据加载
    # ================================================================

    def _load_current_rules(self) -> None:
        """加载当前规则 — 优先用户修改版，其次打包默认版，最后硬编码模板"""
        # 依次尝试：用户修改版 → 打包默认版
        for source in (RULES_FILE, _RULES_BUNDLED):
            try:
                with open(source, "r", encoding="utf-8") as f:
                    data = json.load(f)
                formatted = json.dumps(data, ensure_ascii=False, indent=4)
                self._text.insert("1.0", formatted)
                return
            except Exception:
                continue

        # 都不存在 → 硬编码模板
        formatted = (
            '{\n'
            '    "_说明": "自定义分类规则",\n'
            '    "图片": {\n'
            '        "extensions": ["jpg", "png", "jpeg"],\n'
            '        "keywords": ["screenshot"]\n'
            '    },\n'
            '    "文档": {\n'
            '        "extensions": ["pdf", "docx", "txt"],\n'
            '        "keywords": ["report"]\n'
            '    }\n'
            '}'
        )
        self._text.insert("1.0", formatted)

    # ================================================================
    #  按钮回调
    # ================================================================

    def _on_save(self) -> None:
        """保存按钮：验证 JSON → 写入文件 → 关闭弹窗"""
        raw = self._text.get("1.0", tk.END).strip()

        # 验证 JSON 格式
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            messagebox.showerror(
                "JSON 格式错误",
                f"规则不是有效的 JSON：\n\n{e}",
                parent=self._dialog,
            )
            return

        if not isinstance(data, dict):
            messagebox.showerror(
                "格式错误",
                "规则顶层必须是一个 JSON 对象（{ ... }）",
                parent=self._dialog,
            )
            return

        # 写入 rules.json
        try:
            with open(RULES_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            messagebox.showerror(
                "保存失败",
                f"无法写入 {RULES_FILE}：\n\n{e}",
                parent=self._dialog,
            )
            return

        self._result = data
        self._dialog.destroy()

    def _on_cancel(self) -> None:
        """取消按钮：丢弃修改，关闭弹窗"""
        self._dialog.destroy()

    # ================================================================
    #  工具方法
    # ================================================================

    def _center_window(self) -> None:
        """将弹窗居中于父窗口"""
        pw, ph = self._parent.winfo_width(), self._parent.winfo_height()
        px, py = self._parent.winfo_x(), self._parent.winfo_y()
        dw = self._dialog.winfo_width()
        dh = self._dialog.winfo_height()
        x = px + (pw - dw) // 2
        y = py + (ph - dh) // 2
        self._dialog.geometry(f"+{x}+{y}")

    # ================================================================
    #  公开接口
    # ================================================================

    def show(self) -> dict | None:
        """
        显示弹窗并等待用户操作。

        Returns:
            用户保存的规则 dict，取消则返回 None
        """
        self._dialog.wait_window()
        return self._result
