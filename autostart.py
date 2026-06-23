"""
开机自启动管理（Windows 注册表方式）
----------------------------------
通过写入 HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
实现程序的开机自启动。

安全设计：
  - 仅操作用户级别的注册表（HKCU），不需要管理员权限
  - 自动区分开发环境（python main.py）和打包环境（exe）

使用方式：
    from utils.autostart import enable_autostart, disable_autostart, is_autostart_enabled

    enable_autostart()    # 启用开机自启
    disable_autostart()   # 禁用开机自启
    is_autostart_enabled()  # 查询当前状态 → bool
"""

import os
import sys
import winreg

# 注册表中使用的程序名称（避免与其他程序冲突）
_APP_NAME = "DeskPilot"

# 注册表键路径
_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _get_exe_path() -> str:
    """
    获取程序的可执行路径。

    PyInstaller 打包后：返回 exe 的绝对路径
    开发环境：        返回 'pythonw.exe main.py' 格式的命令行
    """
    if hasattr(sys, "_MEIPASS"):
        # 打包后的 exe 路径
        return sys.executable

    # 开发环境：用 pythonw 启动避免弹出控制台窗口
    main_py = os.path.join(os.path.dirname(sys.executable), "..", "..", "main.py")
    main_py = os.path.abspath(main_py)
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    return f'"{pythonw}" "{main_py}"'


def enable_autostart() -> bool:
    """
    启用开机自启动。

    Returns:
        True 表示设置成功
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _REG_KEY,
            0, winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, _APP_NAME, 0, winreg.REG_SZ, _get_exe_path())
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def disable_autostart() -> bool:
    """
    禁用开机自启动。

    Returns:
        True 表示删除成功（或本来就不存在）
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _REG_KEY,
            0, winreg.KEY_SET_VALUE,
        )
        try:
            winreg.DeleteValue(key, _APP_NAME)
        except FileNotFoundError:
            pass  # 本来就不存在，不算失败
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def is_autostart_enabled() -> bool:
    """
    查询开机自启动是否已启用。

    Returns:
        True 表示已在注册表中注册
    """
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _REG_KEY,
            0, winreg.KEY_READ,
        )
        try:
            winreg.QueryValueEx(key, _APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False
