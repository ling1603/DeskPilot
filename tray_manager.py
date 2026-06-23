"""
系统托盘管理器（TrayManager）
----------------------------
基于 pystray 实现系统托盘图标，支持：
  - 最小化到托盘（关闭窗口时隐藏而非退出）
  - 托盘右键菜单（显示窗口 / 退出程序）
  - 左键单击图标 = 显示窗口

使用方式：
    tray = TrayManager(
        icon_path="assets/app.png",
        on_show_window=callback,   # 显示窗口的回调
        on_quit=callback,          # 真正退出程序的回调
    )
    tray.start()   # 启动托盘（在后台守护线程运行）
    tray.stop()    # 停止托盘
"""

import threading
from typing import Callable

import pystray
from PIL import Image


class TrayManager:
    """系统托盘管理器 —— 封装 pystray 图标与菜单"""

    def __init__(
        self,
        icon_path: str,
        on_show_window: Callable[[], None],
        on_quit: Callable[[], None],
    ):
        """
        Args:
            icon_path:      托盘图标的 PNG 文件路径
            on_show_window: 点击「显示窗口」时的回调
            on_quit:        点击「退出程序」时的回调
        """
        self._icon_path = icon_path
        self._on_show_window = on_show_window
        self._on_quit = on_quit

        # 加载图标图像
        self._image = Image.open(icon_path)

        # 构建托盘菜单
        menu = pystray.Menu(
            pystray.MenuItem(
                "显示窗口",
                self._handle_show_window,
                default=True,  # 左键单击图标 = 显示窗口
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "退出程序",
                self._handle_quit,
            ),
        )

        # 创建托盘图标实例
        self._icon = pystray.Icon(
            name="DeskPilot",
            icon=self._image,
            title="DeskPilot",
            menu=menu,
        )

    # ========== 公开接口 ==========

    def start(self) -> None:
        """在后台守护线程中启动托盘图标"""
        thread = threading.Thread(target=self._icon.run, daemon=True)
        thread.start()

    def stop(self) -> None:
        """停止托盘图标"""
        self._icon.stop()

    # ========== 菜单回调 ==========

    def _handle_show_window(self, icon, item) -> None:
        """托盘菜单「显示窗口」"""
        self._on_show_window()

    def _handle_quit(self, icon, item) -> None:
        """托盘菜单「退出程序」"""
        self._on_quit()
