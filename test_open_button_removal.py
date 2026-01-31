#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试打开按钮是否已移除
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ui.windows.main_window import MainWindow

def test_open_button_removal():
    """测试打开按钮是否已移除"""
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    
    # 检查菜单栏中的文件菜单
    menubar = window.menuBar()
    file_menu = None
    
    for menu in menubar.findChildren(QMainWindow):
        if hasattr(menu, 'title') and menu.title() == "文件(&F)":
            file_menu = menu
            break
    
    if not file_menu:
        print("未找到文件菜单")
        return False
    
    # 检查文件菜单中的动作
    actions = file_menu.actions()
    action_names = [action.text() for action in actions]
    
    print(f"文件菜单中的动作: {action_names}")
    
    # 检查是否有"打开"动作
    has_open_action = any("打开" in name for name in action_names)
    
    if has_open_action:
        print("❌ 错误：仍然存在'打开'按钮")
        return False
    else:
        print("✅ 成功：'打开'按钮已移除")
        return True

if __name__ == "__main__":
    test_open_button_removal()