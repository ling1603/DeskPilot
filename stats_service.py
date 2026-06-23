"""
使用统计服务（StatsService）
----------------------------
记录并持久化程序的运行统计，数据保存到本地 JSON 文件。

追踪指标：
  - total_files_organized  : 累计整理文件数
  - manual_organize_count  : 手动点击「开始整理」的次数
  - monitor_trigger_count  : 监控自动触发整理的次数

线程安全：所有写操作通过内部锁保护。
"""

import json
import os
import threading
from typing import Dict

from utils.helpers import get_user_path


STATS_FILE = get_user_path("stats.json")


class StatsService:
    """本地统计服务 —— 记录 + 持久化 + 查询"""

    def __init__(self, file_path: str = None):
        self._file = file_path or STATS_FILE
        self._lock = threading.Lock()
        self._data = self._load()

    # ========== 公开接口 ==========

    def record_manual_organize(self, file_count: int) -> None:
        """记录一次手动整理操作"""
        with self._lock:
            self._data["total_files_organized"] += file_count
            self._data["manual_organize_count"] += 1
            self._save()

    def record_monitor_organize(self) -> None:
        """记录一次监控触发的文件整理"""
        with self._lock:
            self._data["total_files_organized"] += 1
            self._data["monitor_trigger_count"] += 1
            self._save()

    def get_stats(self) -> Dict[str, int]:
        """返回当前统计数据的副本"""
        with self._lock:
            return dict(self._data)

    def format_display(self) -> str:
        """生成 UI 展示用的统计字符串"""
        d = self.get_stats()
        return (
            f"📊 共整理 {d['total_files_organized']} 个文件  "
            f"|  手动 {d['manual_organize_count']} 次  "
            f"|  监控触发 {d['monitor_trigger_count']} 次"
        )

    # ========== 内部方法 ==========

    def _load(self) -> Dict[str, int]:
        """从 JSON 文件加载统计，文件缺失时返回默认值"""
        default = {
            "total_files_organized": 0,
            "manual_organize_count": 0,
            "monitor_trigger_count": 0,
        }
        if not os.path.exists(self._file):
            return default
        try:
            with open(self._file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 补齐可能缺失的键
            for key in default:
                if key not in data:
                    data[key] = default[key]
            return data
        except Exception:
            return default

    def _save(self) -> None:
        """将当前统计写入 JSON 文件"""
        try:
            with open(self._file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # 保存失败不影响主流程
