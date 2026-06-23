"""
主窗口（MainWindow）
-------------------
DeskPilot 的完整 Tkinter 界面。

职责：
  1. 构建所有 UI 组件（按钮、标签、进度条、文本框等）
  2. 绑定用户事件到对应的处理方法
  3. 协调 FileOrganizer 和 UndoManager 两个服务
  4. 通过回调接收服务层通知并更新界面

不包含任何整理业务逻辑 —— 所有逻辑都在 services/ 层。
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import PhotoImage
from typing import Optional

from config.settings import (
    CONFIG_FILE,
    FONT_TITLE,
    FONT_NORMAL,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
)
from utils.helpers import resource_path
from utils.tray_manager import TrayManager
from services.organizer import FileOrganizer
from services.undo_manager import UndoManager
from services.monitor_service import FolderMonitor
from services.stats_service import StatsService
from services.feature_gate import feature_gate
from models.operation import OperationBatch
from ui.rule_editor import RuleEditorDialog
from config.settings import load_rules


class MainWindow:
    """DeskPilot 主窗口"""

    def __init__(self):
        # ==================== 根窗口 ====================
        self.root = tk.Tk()
        self.root.title("DeskPilot")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        # 设置窗口图标（加载失败不影响程序运行）
        try:
            # .ico 格式（Windows 任务栏原生支持）
            self.root.iconbitmap(resource_path("app.ico"))
        except Exception:
            try:
                icon = PhotoImage(file=resource_path("app.png"))
                self.root.iconphoto(True, icon)
            except Exception:
                pass

        # ==================== 初始化服务 ====================
        self.organizer = FileOrganizer()
        self.undo_manager = UndoManager(on_log=self._append_log)

        # ==================== 统计服务 ====================
        self.stats = StatsService()

        # ==================== 监控服务 ====================
        self._monitor: Optional[FolderMonitor] = None
        self._monitor_folder: str = ""

        # ==================== 状态 ====================
        self.last_folder = self._load_last_folder()

        # ==================== 构建界面 ====================
        self._build_ui()

        # 初始化操作历史显示
        self._update_history_ui()

        # ==================== 系统托盘 ====================
        try:
            self._tray = TrayManager(
                icon_path=resource_path("app.png"),
                on_show_window=self._on_show_window,
                on_quit=self._on_real_quit,
            )
            self._tray.start()
        except Exception:
            self._tray = None  # 托盘不可用时不影响程序运行

        # 窗口关闭 → 最小化到托盘（而非退出）
        self.root.protocol("WM_DELETE_WINDOW", self._on_minimize_to_tray)

    # ================================================================
    #  持久化配置
    # ================================================================

    @staticmethod
    def _load_last_folder() -> str:
        """从配置文件读取上次选择的文件夹路径"""
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                path = f.read().strip()
                return path if path else "尚未选择文件夹"
        except FileNotFoundError:
            return "尚未选择文件夹"

    @staticmethod
    def _save_last_folder(path: str) -> None:
        """将文件夹路径写入配置文件"""
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(path)

    # ================================================================
    #  UI 构建
    # ================================================================

    def _build_ui(self) -> None:
        """一次性构建所有界面组件（按从上到下的布局顺序）"""

        # ================================================================
        #  顶部品牌区
        # ================================================================
        header_frame = tk.Frame(self.root)
        header_frame.pack(fill="x", padx=12, pady=(10, 2))

        title_row = tk.Frame(header_frame)
        title_row.pack()

        tk.Label(
            title_row, text="📂 DeskPilot", font=FONT_TITLE
        ).pack(side="left")

        # 版本标识
        version_color = "#0078D4" if feature_gate.is_pro else "#E67E22"
        tk.Label(
            title_row,
            text=f" {feature_gate.version_label} ",
            font=("Arial", 8, "bold"),
            fg="white",
            bg=version_color,
            padx=5, pady=1,
        ).pack(side="left", padx=(6, 0))

        # ================================================================
        #  文件夹面板
        # ================================================================
        folder_frame = tk.LabelFrame(
            self.root, text="当前文件夹",
            font=("Arial", 10, "bold"), padx=8, pady=4,
        )
        folder_frame.pack(fill="x", padx=10, pady=(8, 4))

        self.path_label = tk.Label(
            folder_frame,
            text=f"📁 {self.last_folder}",
            font=FONT_NORMAL, anchor="w",
        )
        self.path_label.pack(fill="x")

        # ================================================================
        #  状态面板（监控状态 + 统计信息）
        # ================================================================
        status_frame = tk.LabelFrame(
            self.root, text="运行状态",
            font=("Arial", 10, "bold"), padx=8, pady=4,
        )
        status_frame.pack(fill="x", padx=10, pady=(4, 8))

        self.monitor_status_label = tk.Label(
            status_frame,
            text="🔴 自动整理：未开启",
            fg="gray",
            font=FONT_NORMAL, anchor="w",
        )
        self.monitor_status_label.pack(fill="x")

        self.stats_label = tk.Label(
            status_frame,
            text=self.stats.format_display(),
            font=FONT_NORMAL, fg="#555555", anchor="w",
        )
        self.stats_label.pack(fill="x")

        # ================================================================
        #  主操作按钮（Hero）
        # ================================================================
        tk.Button(
            self.root,
            text="📂  整理文件",
            command=self._on_start,
            font=("Arial", 12, "bold"),
            bg="#0078D4", fg="white",
            activebackground="#005A9E", activeforeground="white",
            relief="flat", cursor="hand2",
            height=2,
        ).pack(fill="x", padx=10, pady=(2, 2))

        # ================================================================
        #  辅助按钮行
        # ================================================================
        secondary_frame = tk.Frame(self.root)
        secondary_frame.pack(fill="x", padx=10, pady=(2, 4))

        tk.Button(
            secondary_frame, text="↩ 撤销",
            command=self._on_undo, width=10,
        ).pack(side="left", padx=(0, 4))

        tk.Button(
            secondary_frame, text="清空日志",
            command=self._on_clear_log, width=10,
        ).pack(side="left", padx=4)

        tk.Button(
            secondary_frame, text="⚙ 分类设置",
            command=self._on_edit_rules, width=10,
        ).pack(side="left", padx=4)

        # ================================================================
        #  进度指示器（整理时显示）
        # ================================================================
        self.progress = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.root, variable=self.progress, maximum=100
        )
        self.progress_bar.pack(fill="x", padx=10, pady=(6, 2))

        self.progress_label = tk.Label(
            self.root, text="",
            font=FONT_NORMAL, fg="#888888",
        )
        self.progress_label.pack()

        self.current_file_label = tk.Label(
            self.root, text="",
            font=FONT_NORMAL, fg="#888888",
        )
        self.current_file_label.pack()

        # ================================================================
        #  自动整理控制
        # ================================================================
        monitor_ctrl = tk.Frame(self.root)
        monitor_ctrl.pack(fill="x", padx=10, pady=(6, 4))

        self.btn_start_monitor = tk.Button(
            monitor_ctrl, text="▶ 自动整理",
            command=self._on_start_monitor, width=13,
        )
        self.btn_start_monitor.pack(side="left", padx=(0, 4))

        self.btn_stop_monitor = tk.Button(
            monitor_ctrl, text="⏸ 停止",
            command=self._on_stop_monitor, width=13,
            state="disabled",
        )
        self.btn_stop_monitor.pack(side="left")

        # ================================================================
        #  整理记录面板
        # ================================================================
        tk.Label(
            self.root, text="整理记录",
            font=("Arial", 10, "bold"), anchor="w",
        ).pack(fill="x", padx=10, pady=(8, 0))

        self.history_text = tk.Text(
            self.root,
            height=10,
            font=FONT_NORMAL,
            padx=8, pady=8,
            state="disabled",
            relief="solid", borderwidth=1,
        )
        self.history_text.pack(fill="both", expand=True, padx=10, pady=(2, 4))

        # ================================================================
        #  日志 + 状态栏
        # ================================================================
        self.log_text = tk.Text(
            self.root, height=4,
            relief="solid", borderwidth=1,
        )
        self.log_text.pack(fill="x", padx=10, pady=(2, 2))

        self.status_label = tk.Label(
            self.root, text="✅ 就绪 — 点击「整理文件」开始",
            font=FONT_NORMAL, anchor="w", fg="#333333",
        )
        self.status_label.pack(fill="x", padx=10, pady=(2, 8))

    # ================================================================
    #  事件处理（UI → 服务）
    # ================================================================

    def _on_start(self) -> None:
        """「整理文件」按钮回调"""
        folder = filedialog.askdirectory()
        if not folder:
            return

        self.status_label.config(text="⏳ 正在整理文件...")

        # 显示进度指示器
        self.progress.set(0)
        self.progress_label.config(text="准备中...")
        self.current_file_label.config(text="")

        # 调用整理服务（只调用一次，避免原代码的双调用 Bug）
        count, skip_count, batch = self.organizer.organize(
            target_dir=folder,
            on_progress=self._on_progress,
            on_log=self._append_log,
        )

        # 持久化路径
        self._save_last_folder(folder)
        self.last_folder = folder
        self.path_label.config(text=f"📁 {folder}")

        # 记录操作历史
        if batch:
            self.undo_manager.push(batch)
            self._update_history_ui()

        # 更新统计
        self.stats.record_manual_organize(count)
        self._update_stats_ui()

        # 隐藏进度指示器
        self.progress.set(0)
        self.progress_label.config(text="")
        self.current_file_label.config(text="")

        self.status_label.config(text="✅ 整理完成")

        # 结果弹窗
        messagebox.showinfo(
            "DeskPilot",
            f"整理完成\n\n整理成功：{count} 个\n跳过文件：{skip_count} 个",
        )

    def _on_undo(self) -> None:
        """「撤销」按钮回调"""
        self.undo_manager.undo()
        self._update_history_ui()

    def _on_clear_log(self) -> None:
        """「清空日志」按钮回调"""
        self.log_text.delete("1.0", tk.END)

    def _on_edit_rules(self) -> None:
        """「分类设置」按钮回调 —— 打开规则编辑器弹窗（Pro 功能）"""
        if not feature_gate.require_pro("分类设置", parent=self.root):
            return

        editor = RuleEditorDialog(self.root)
        result = editor.show()

        if result is not None:
            # 用户保存了 → 重新加载规则到整理器
            self.organizer.rules = load_rules()
            self._append_log("📋 规则已更新并生效")

    # ================================================================
    #  监控控制
    # ================================================================

    def _on_start_monitor(self) -> None:
        """「自动整理」按钮回调（Pro 功能）"""
        if not feature_gate.require_pro("自动整理", parent=self.root):
            return

        # 默认使用上次整理的文件夹，否则让用户选择
        initial_dir = ""
        if self.last_folder and self.last_folder != "尚未选择文件夹":
            initial_dir = self.last_folder

        folder = filedialog.askdirectory(
            title="选择要监控的文件夹",
            initialdir=initial_dir if os.path.isdir(initial_dir) else "",
        )
        if not folder:
            return

        self._start_monitoring(folder)

    def _start_monitoring(self, folder: str) -> None:
        """创建并启动 FolderMonitor"""
        if self._monitor and self._monitor.is_running:
            self._monitor.stop()

        try:
            self._monitor = FolderMonitor(
                target_dir=folder,
                on_file_detected=self._on_file_detected,
                on_log=self._append_log,
                on_error=self._append_log,
            )
            self._monitor.start()
        except Exception as e:
            self._append_log(f"❌ 启动监控失败：{e}")
            self._set_monitor_status(False)
            return

        self._monitor_folder = folder
        self._set_monitor_status(True)

    def _on_stop_monitor(self) -> None:
        """「停止监控」按钮回调"""
        if self._monitor:
            self._monitor.stop()
        self._set_monitor_status(False)

    def _on_file_detected(self, file_path: str) -> None:
        """
        监控到新文件时的回调（由 watchdog 后台线程调用）。

        通过 root.after() 将所有 UI 操作调度到主线程，确保线程安全。
        """
        # 使用 after 将处理切换到主线程
        self.root.after(0, self._handle_new_file, file_path)

    def _handle_new_file(self, file_path: str) -> None:
        """在主线程中处理新文件（整理 + 记录历史 + 更新 UI）"""
        # 调用单文件整理
        move = self.organizer.organize_file(
            file_path=file_path,
            on_log=self._append_log,
        )

        if move is None:
            return

        # 记录到撤回历史
        batch = OperationBatch(moves=[move])
        self.undo_manager.push(batch)
        self._update_history_ui()

        # 更新统计（监控触发）
        self.stats.record_monitor_organize()
        self._update_stats_ui()

    def _set_monitor_status(self, running: bool) -> None:
        """更新监控状态指示器"""
        if running:
            folder_name = os.path.basename(self._monitor_folder.rstrip(os.sep))
            self.monitor_status_label.config(
                text=f"🟢 自动整理：已开启 · {folder_name}",
                fg="green",
            )
            self.btn_start_monitor.config(state="disabled")
            self.btn_stop_monitor.config(state="normal")
            self.status_label.config(
                text=f"🟢 自动整理运行中 — 监控 {folder_name}"
            )
        else:
            self.monitor_status_label.config(
                text="🔴 自动整理：未开启",
                fg="gray",
            )
            self.btn_start_monitor.config(state="normal")
            self.btn_stop_monitor.config(state="disabled")
            self.status_label.config(text="✅ 就绪 — 点击「整理文件」开始")

    def _update_stats_ui(self) -> None:
        """刷新统计信息显示"""
        self.stats_label.config(text=self.stats.format_display())

    # ================================================================
    #  回调（服务 → UI）
    # ================================================================

    def _on_progress(self, filename: str, done: int, total: int) -> None:
        """进度回调 —— 由 FileOrganizer 在每处理一个文件时调用"""
        percent = int(done / total * 100)
        self.progress.set(percent)
        self.progress_label.config(
            text=f"进度：{percent}%（{done}/{total}）"
        )
        self.current_file_label.config(
            text=f"当前文件：{filename}"
        )
        self.root.update_idletasks()

    def _append_log(self, msg: str) -> None:
        """日志回调 —— 由服务层调用以输出日志"""
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    # ================================================================
    #  历史显示刷新
    # ================================================================

    def _update_history_ui(self) -> None:
        """从 UndoManager 读取历史并刷新历史记录面板"""
        self.history_text.config(state="normal")
        self.history_text.delete("1.0", tk.END)

        history = self.undo_manager.get_history()
        if not history:
            if self.stats.get_stats()["total_files_organized"] == 0:
                # 首次启动 — 显示欢迎引导
                self.history_text.insert(tk.END, "👋  欢迎使用 DeskPilot！\n\n")
                self.history_text.insert(tk.END, "DeskPilot 帮您自动整理文件夹中的文件，\n")
                self.history_text.insert(tk.END, "按类型归类到对应的子文件夹中。\n\n")
                self.history_text.insert(tk.END, "🚀  三步开始：\n")
                self.history_text.insert(tk.END, "    1️⃣  点击「📂 整理文件」\n")
                self.history_text.insert(tk.END, "    2️⃣  选择要整理的文件夹\n")
                self.history_text.insert(tk.END, "    3️⃣  文件自动归类，一键撤销\n\n")
                self.history_text.insert(tk.END, "💡  开启「自动整理」后，新文件会实时自动归类。\n")
            else:
                self.history_text.insert(tk.END, "📭 暂无操作记录\n")
        else:
            # 倒序显示（最近的在最上面）
            for i, batch in enumerate(reversed(history), 1):
                self.history_text.insert(
                    tk.END,
                    f"{i}. 整理{batch.file_count}个文件"
                    f"（示例：{batch.first_file_name}）\n",
                )

        self.history_text.config(state="disabled")

    # ================================================================
    #  生命周期（托盘模式）
    # ================================================================

    def _on_minimize_to_tray(self) -> None:
        """点击窗口关闭按钮 → 隐藏到托盘而非退出"""
        self.root.withdraw()  # 隐藏窗口，托盘图标保持

    def _on_show_window(self) -> None:
        """托盘菜单「显示窗口」→ 恢复并置顶"""
        self.root.deiconify()  # 恢复隐藏的窗口
        self.root.lift()       # 置顶
        self.root.focus_force()

    def _on_real_quit(self) -> None:
        """托盘菜单「退出程序」→ 真正退出"""
        # 停止监控
        if self._monitor and self._monitor.is_running:
            self._monitor.stop()
        # 停止托盘
        if self._tray:
            self._tray.stop()
        # 销毁窗口
        self.root.destroy()

    def run(self) -> None:
        """启动 Tkinter 主事件循环"""
        # 防闪退优化（按需取消注释）
        # try:
        #     self.root.mainloop()
        # except Exception as e:
        #     print("程序异常", e)
        self.root.mainloop()
