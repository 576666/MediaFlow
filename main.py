#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MediaFlow - 高性能媒体批处理工具
现代化主入口
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.windows.main_window import MainWindow


def main():
    # 设置高DPI缩放支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置应用属性
    app.setApplicationName("MediaFlow")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("MediaFlow Team")
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 启动事件循环
    sys.exit(app.exec())


if __name__ == '__main__':
    main()