"""
通用工具函数
-----------
提供 PyInstaller 打包后的资源路径解析、用户数据目录等辅助功能。
"""

import os
import sys


def get_app_dir() -> str:
    """
    获取可读写的用户数据目录。

    PyInstaller 打包后：exe 所在目录
    开发环境：          当前工作目录（项目根目录）
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(".")


def get_user_path(filename: str) -> str:
    """
    获取用户数据文件的绝对路径（在可读写目录中）。

    Args:
        filename: 相对于应用数据目录的文件名，如 "stats.json"

    Returns:
        文件的绝对路径
    """
    return os.path.join(get_app_dir(), filename)


def resource_path(relative_path: str) -> str:
    """
    获取资源文件的绝对路径，自动适配开发环境和 PyInstaller 打包环境。

    当程序被 PyInstaller 打包为 exe 时，资源文件会被解压到临时目录
    （sys._MEIPASS），此时需要使用该临时路径；开发环境下则使用当前目录。

    Args:
        relative_path: 相对于项目根目录的资源路径

    Returns:
        资源的绝对路径
    """
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
