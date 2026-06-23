"""
撤回管理器（UndoManager）
------------------------
管理文件整理操作的历史记录，支持"按批次撤回"。

每一次调用 push() 存入一个 OperationBatch，
调用 undo() 则反向移动最近一批的所有文件。
"""

import shutil
from typing import Callable, List, Optional

from models.operation import OperationBatch


class UndoManager:
    """操作历史管理器 —— 纯逻辑，不依赖 UI"""

    def __init__(self, on_log: Optional[Callable[[str], None]] = None):
        """
        Args:
            on_log: 日志回调，用于输出撤回状态信息
        """
        self._history: List[OperationBatch] = []
        self._on_log = on_log

    # ========== 公开接口 ==========

    def push(self, batch: OperationBatch) -> None:
        """
        将一个操作批次压入历史栈。

        Args:
            batch: 一次整理操作产生的文件移动集合
        """
        if batch and batch.moves:
            self._history.append(batch)

    def undo(self) -> Optional[OperationBatch]:
        """
        撤回最近一次整理操作（LIFO）。

        将最近一批移动过的文件从目标位置移回原始位置。

        Returns:
            被撤回的操作批次；如果历史为空则返回 None
        """
        if not self._history:
            self._emit("没有可撤回的操作")
            return None

        batch = self._history.pop()

        # 反向移动：从 dst 移回 src
        for move in reversed(batch.moves):
            shutil.move(move.dst, move.src)

        self._emit("↩ 撤回完成")
        return batch

    def get_history(self) -> List[OperationBatch]:
        """
        获取历史记录副本（用于 UI 展示）。

        Returns:
            按时间顺序排列的操作批次列表（最早的在前面）
        """
        return list(self._history)

    @property
    def batch_count(self) -> int:
        """历史中的操作批次数"""
        return len(self._history)

    def clear(self) -> None:
        """清空所有历史记录"""
        self._history.clear()

    # ========== 内部方法 ==========

    def _emit(self, msg: str) -> None:
        """安全调用日志回调"""
        if self._on_log:
            self._on_log(msg)
