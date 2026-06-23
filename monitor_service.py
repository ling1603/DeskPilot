"""
文件夹监控服务（FolderMonitor）
------------------------------
基于 watchdog 实现目录监控，当检测到新增文件时自动触发整理。

使用方式：
    monitor = FolderMonitor(
        target_dir="/path/to/watch",
        on_file_detected=callback,   # 检测到新文件时调用
        on_log=log_callback,         # 日志输出
        on_error=error_callback,     # 异常通知
    )
    monitor.start()   # 开始监控
    monitor.stop()    # 停止监控

线程安全：
    watchdog 的回调在后台线程执行，本模块通过内部锁保护共享状态。
    所有用户回调通过 threading.Timer 延迟触发，以等待文件写入完成。
"""

import os
import threading
from typing import Callable, Dict, Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent


# 文件写入完成等待时间（秒）—— 部分应用先创建空文件再逐步写入
DEBOUNCE_SECONDS = 0.5


class _NewFileHandler(FileSystemEventHandler):
    """
    文件系统事件处理器（内部类）。
    只监听根目录下的文件创建事件，忽略子目录内的变化。
    """

    def __init__(self, target_dir: str, on_detected: Callable[[str], None]):
        super().__init__()
        self._target_dir = os.path.abspath(target_dir)
        self._on_detected = on_detected
        # 防抖：{文件绝对路径: threading.Timer}
        self._pending: Dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def on_created(self, event: FileCreatedEvent) -> None:
        """文件创建事件 —— 仅处理根目录下的文件，忽略子目录"""
        if event.is_directory:
            return

        file_path = event.src_path

        # 只监听目标目录的直接子文件，不监听子文件夹内的变化
        if os.path.dirname(file_path) != self._target_dir:
            return

        # 防抖：重置该文件对应的计时器，等文件写入稳定后再触发
        with self._lock:
            if file_path in self._pending:
                self._pending[file_path].cancel()

            timer = threading.Timer(
                DEBOUNCE_SECONDS,
                self._fire,
                args=[file_path],
            )
            timer.daemon = True
            self._pending[file_path] = timer
            timer.start()

    def _fire(self, file_path: str) -> None:
        """计时器到期：确认文件仍存在后触发回调"""
        with self._lock:
            self._pending.pop(file_path, None)

        # 再次确认文件存在（可能已被用户删除）
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self._on_detected(file_path)

    def cleanup(self) -> None:
        """取消所有待处理的计时器"""
        with self._lock:
            for timer in self._pending.values():
                timer.cancel()
            self._pending.clear()


class FolderMonitor:
    """
    文件夹监控器 —— 封装 watchdog，提供简洁的 start/stop 接口。

    线程模型：
        watchdog Observer 在自己的线程中运行事件回调。
        本类通过 _NewFileHandler 内部的防抖机制延迟触发，避免文件写入未完成就移动。
    """

    def __init__(
        self,
        target_dir: str,
        on_file_detected: Callable[[str], None],
        on_log: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        """
        Args:
            target_dir:       要监控的目录绝对路径
            on_file_detected: 检测到新文件时的回调，签名 (file_path: str)
            on_log:           日志回调，签名 (message: str)
            on_error:         异常回调，签名 (error_message: str)
        """
        self._target_dir = os.path.abspath(target_dir)
        self._on_log = on_log
        self._on_error = on_error

        # 事件处理器
        self._handler = _NewFileHandler(self._target_dir, on_file_detected)

        # watchdog Observer
        self._observer = Observer()
        self._observer.schedule(self._handler, self._target_dir, recursive=False)

    # ========== 公开接口 ==========

    def start(self) -> None:
        """启动监控"""
        if self._observer.is_alive():
            self._emit_log("⚠️ 监控已在运行中")
            return

        self._observer.start()
        self._emit_log(f"👁️ 开始监控：{self._target_dir}")

    def stop(self) -> None:
        """停止监控"""
        if not self._observer.is_alive():
            return

        self._observer.stop()
        self._observer.join(timeout=2)
        self._handler.cleanup()
        self._emit_log("🛑 监控已停止")

    @property
    def is_running(self) -> bool:
        """监控是否正在运行"""
        return self._observer.is_alive()

    @property
    def target_dir(self) -> str:
        """当前监控的目录路径"""
        return self._target_dir

    # ========== 内部方法 ==========

    def _emit_log(self, msg: str) -> None:
        if self._on_log:
            self._on_log(msg)

    def _emit_error(self, msg: str) -> None:
        if self._on_error:
            self._on_error(msg)
        elif self._on_log:
            self._on_log(f"❌ {msg}")
