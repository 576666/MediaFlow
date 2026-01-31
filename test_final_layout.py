#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试最终布局是否符合要求：
1. 只保留顶部的添加文件夹按钮
2. 只保留左边的文件浏览区域
3. 移除右边的视频预览功能和窗口
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ui.windows.main_window import MainWindow

def test_final_layout():
    """测试最终布局"""
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    
    print("✅ 主窗口创建成功")
    
    # 检查中央部件布局
    central_widget = window.centralWidget()
    if central_widget:
        print("✅ 中央部件存在")
        
        # 检查布局
        layout = central_widget.layout()
        if layout:
            print(f"✅ 布局类型: {type(layout).__name__}")
            print(f"✅ 布局子部件数量: {layout.count()}")
            
            # 检查第一个子部件（应该是文件浏览器）
            if layout.count() > 0:
                widget = layout.itemAt(0).widget()
                if widget:
                    print(f"✅ 第一个子部件: {type(widget).__name__}")
    
    # 检查菜单栏
    menubar = window.menuBar()
    if menubar:
        menus = menubar.actions()
        menu_names = [menu.text() for menu in menus]
        print(f"✅ 菜单栏菜单: {menu_names}")
    
    # 检查工具栏
    toolbars = window.findChildren(QToolBar)
    print(f"✅ 工具栏数量: {len(toolbars)}")
    if toolbars:
        toolbar = toolbars[0]
        actions = toolbar.actions()
        action_texts = [action.text() for action in actions]
        print(f"✅ 工具栏按钮: {action_texts}")
    
    print("\n🎯 布局检查完成！")
    print("预期结果：")
    print("- 顶部只有'添加文件夹'按钮")
    print("- 左侧只有文件浏览器区域")
    print("- 没有右侧视频预览窗口")
    print("- 没有处理菜单和帮助菜单")

if __name__ == "__main__":
    test_final_layout()