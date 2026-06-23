"""
文件整理服务（FileOrganizer）
----------------------------
核心业务逻辑：扫描目录 → 按扩展名分类 → 移动到对应子文件夹 → 生成报告。

通过回调函数与 UI 层彻底解耦：
  - on_progress(filename, done, total) — 进度更新
  - on_log(message)                 — 日志输出
"""

import os
import shutil
from datetime import datetime
from typing import Callable, List, Optional, Tuple

from config.settings import load_rules, REPORT_FILE
from models.operation import FileMove, OperationBatch
from services.feature_gate import feature_gate


class FileOrganizer:
    """文件分类整理器 —— 纯业务逻辑，不依赖任何 UI 框架"""

    def __init__(self, rules: dict = None):
        """
        Args:
            rules: 自定义分类规则，格式 {文件夹名: [扩展名列表]}。
                   不传则自动调用 load_rules()：优先从 config/rules.json 加载，
                   加载失败时回退到 settings.py 中的硬编码默认规则。
        """
        self.rules = rules if rules is not None else load_rules()
        self._use_keywords = feature_gate.can_use_keywords()

    def organize(
        self,
        target_dir: str,
        on_progress: Optional[Callable[[str, int, int], None]] = None,
        on_log: Optional[Callable[[str], None]] = None,
    ) -> Tuple[int, int, Optional[OperationBatch]]:
        """
        执行文件分类整理。

        Args:
            target_dir:  要整理的目标目录绝对路径
            on_progress: 进度回调，签名 (filename: str, done: int, total: int)
            on_log:      日志回调，签名 (message: str)

        Returns:
            (整理成功数, 跳过数, 操作批次) — 当没有任何文件被移动时 batch 为 None
        """
        # ---- 1. 校验目录 ----
        if not os.path.exists(target_dir):
            self._emit(on_log, f"❌ 目录不存在：{target_dir}")
            return 0, 0, None

        # ---- 2. 获取文件列表（不含子目录） ----
        files = [
            f for f in os.listdir(target_dir)
            if os.path.isfile(os.path.join(target_dir, f))
        ]

        if not files:
            self._emit(on_log, "📂 目录为空，没有文件需要整理")
            return 0, 0, None

        total = len(files)
        count = 0
        skip_count = 0
        moves: List[FileMove] = []
        logs: List[str] = []

        # ---- 3. 遍历分类 ----
        for done, filename in enumerate(files, 1):
            # 通知进度
            if on_progress:
                on_progress(filename, done, total)

            # 提取扩展名（去掉点号，转小写）
            ext = os.path.splitext(filename)[1].lstrip(".").lower()

            # 无扩展名 → 跳过
            if not ext:
                self._emit(on_log, f"⏭️  跳过无扩展名文件：{filename}")
                continue

            # 查找匹配的分类规则（扩展名 + 关键词）
            target_folder = self._find_category(ext, filename)
            if target_folder is None:
                self._emit(on_log, f"⏭️  跳过未分类文件：{filename}（.{ext}）")
                skip_count += 1
                continue

            # ---- 4. 创建目标文件夹 ----
            folder_path = os.path.join(target_dir, target_folder)
            os.makedirs(folder_path, exist_ok=True)

            # ---- 5. 移动文件（自动处理重名） ----
            src = os.path.join(target_dir, filename)
            dst = self._resolve_dst(folder_path, filename)

            shutil.move(src, dst)

            # 记录本次移动
            moves.append(FileMove(src=src, dst=dst))
            log_msg = f"{filename} → {target_folder}"
            logs.append(log_msg)
            self._emit(on_log, log_msg)
            count += 1

        # ---- 6. 输出汇总 ----
        self._emit(on_log, f"📊 共整理 {count} 个文件")
        self._emit(on_log, f"📊 共跳过 {skip_count} 个文件")
        self._emit(on_log, "🎉 DeskPilot 整理完成！")

        # ---- 7. 生成报告文件 ----
        if logs:
            self._write_report(logs, count, skip_count)

        batch = OperationBatch(moves=moves) if moves else None
        return count, skip_count, batch

    def organize_file(
        self,
        file_path: str,
        on_log: Optional[Callable[[str], None]] = None,
    ) -> Optional[FileMove]:
        """
        整理单个文件（供监控服务调用）。

        与 organize() 的区别：
          - organize() 扫描整个目录批量处理
          - organize_file() 只处理指定的单个文件

        Args:
            file_path: 文件的绝对路径
            on_log:    日志回调

        Returns:
            FileMove 对象（成功时），None（跳过或无法分类时）
        """
        if not os.path.isfile(file_path):
            return None

        target_dir = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        # 提取扩展名
        ext = os.path.splitext(filename)[1].lstrip(".").lower()
        if not ext:
            self._emit(on_log, f"⏭️  跳过无扩展名文件：{filename}")
            return None

        # 查找分类（扩展名 + 关键词）
        target_folder = self._find_category(ext, filename)
        if target_folder is None:
            self._emit(on_log, f"⏭️  跳过未分类文件：{filename}（.{ext}）")
            return None

        # 创建目标文件夹
        folder_path = os.path.join(target_dir, target_folder)
        os.makedirs(folder_path, exist_ok=True)

        # 移动文件（处理重名）
        dst = self._resolve_dst(folder_path, filename)
        shutil.move(file_path, dst)

        self._emit(on_log, f"📥 {filename} → {target_folder}")
        return FileMove(src=file_path, dst=dst)

    # ========== 内部方法 ==========

    def _find_category(self, ext: str, filename: str = "") -> Optional[str]:
        """
        根据扩展名和文件名关键词查找对应的分类。

        匹配优先级：扩展名 > 关键词（先匹配扩展名，命中即返回）。
        同时支持新旧两种规则格式：
          旧：{"图片": ["jpg", "png"]}
          新：{"图片": {"extensions": [...], "keywords": [...]}}
          新旧格式在 load_rules() 中已统一规范化。

        Args:
            ext:      文件扩展名（不含点号，小写）
            filename: 完整文件名（用于关键词匹配）

        Returns:
            分类文件夹名，未匹配返回 None
        """
        name_lower = filename.lower()
        for folder_name, rule in self.rules.items():
            # 兼容旧格式（list）和新格式（dict）
            if isinstance(rule, list):
                # 旧格式：仅扩展名列表
                if ext in rule:
                    return folder_name
            else:
                # 新格式：{"extensions": [...], "keywords": [...]}
                if ext in rule.get("extensions", []):
                    return folder_name
                # 关键词匹配 —— 仅 Pro 版本可用
                if self._use_keywords:
                    for kw in rule.get("keywords", []):
                        if kw.lower() in name_lower:
                            return folder_name
        return None

    @staticmethod
    def _resolve_dst(folder_path: str, filename: str) -> str:
        """
        解析目标路径，自动处理重名冲突。
        若 "file.txt" 已存在，则生成 "file(1).txt"、"file(2).txt" ...
        """
        dst = os.path.join(folder_path, filename)
        if not os.path.exists(dst):
            return dst

        name, ext_part = os.path.splitext(filename)
        i = 1
        while os.path.exists(
            os.path.join(folder_path, f"{name}({i}){ext_part}")
        ):
            i += 1
        return os.path.join(folder_path, f"{name}({i}){ext_part}")

    @staticmethod
    def _write_report(logs: List[str], count: int, skip_count: int) -> None:
        """将整理结果写入报告文件"""
        current_time = datetime.now()
        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write("DeskPilot 整理报告\n")
            f.write("===================\n")
            f.write(f"时间：{time_str}\n\n")
            f.write("整理记录：\n")
            for log in logs:
                f.write(f"{log}\n")
            f.write(f"\n整理成功：{count}\n")
            f.write(f"跳过文件：{skip_count}\n")

    @staticmethod
    def _emit(callback: Optional[Callable[[str], None]], msg: str) -> None:
        """安全调用日志回调"""
        if callback:
            callback(msg)
