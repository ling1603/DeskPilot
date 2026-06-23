"""
数据模型：文件操作记录
--------------------
定义文件移动的最小单元（FileMove）和一次整理操作的集合（OperationBatch），
供 Organizer 和 UndoManager 共同使用。
"""

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class FileMove:
    """单次文件移动的源路径与目标路径"""
    src: str
    dst: str


@dataclass
class OperationBatch:
    """一次"整理"操作中所有 FileMove 的集合，是撤回的最小单位"""
    moves: List[FileMove] = field(default_factory=list)

    @property
    def file_count(self) -> int:
        """本次操作移动的文件总数"""
        return len(self.moves)

    @property
    def first_file_name(self) -> str:
        """本次操作中第一个文件的名称（用于 UI 摘要显示）"""
        if not self.moves:
            return ""
        return os.path.basename(self.moves[0].src)
