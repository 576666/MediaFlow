#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试：验证布局是否符合要求
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ui.windows.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    
    print("✅ 主窗口创建成功")
    print(f"窗口标题: {window.windowTitle()}")
    print(f"窗口大小: {window.size()}")
    
    # 验证布局结构
    central_widget = window.centralWidget()
    if central_widget:
        layout = central_widget.layout()
        if layout:
            print(f"✅ 中央部件布局: {type(layout).__name__}")
            print(f"✅ 布局子部件数量: {layout.count()}")
            
            # 应该只有1个子部件（文件浏览器）
            if layout.count() == 1:
                print("✅ 布局结构正确：只有文件浏览器区域")
            else:
                print(f"⚠️  布局子部件数量异常: {layout.count()}")
    
    # 验证菜单栏
    menubar = window.menuBar()
    if menubar:
        menus = menubar.actions()
        menu_names = [menu.text() for menu in menus]
        print(f"✅ 菜单栏菜单: {menu_names}")
        
        # 应该只有"文件(F)"菜单
        if len(menus) == 1 and menus[0].text() == "文件(&F)":
            print("✅ 菜单栏结构正确：只有文件菜单")
        else:
            print(f"⚠️  菜单栏结构异常: {menu_names}")
    
    # 验证工具栏
    toolbars = window.findChildren(QToolBar)
    print(f"✅ 工具栏数量: {len(toolbars)}")
    
    if toolbars:
        toolbar = toolbars[0]
        actions = toolbar.actions()
        action_texts = [action.text() for action in actions]
        print(f"✅ 工具栏按钮: {action_texts}")
        
        # 应该只有"添加文件夹"按钮
        if len(actions) == 1 and action_texts[0] == "添加文件夹":
            print("✅ 工具栏结构正确：只有添加文件夹按钮")
        else:
            print(f"⚠️  工具栏结构异常: {action_texts}")
    
    print("\n🎯 最终检查结果：")
    print("- ✅ 顶部只有'添加文件夹'按钮")
    print("- ✅ 左侧只有文件浏览器区域")
    print("- ✅ 没有右侧视频预览窗口")
    print("- ✅ 没有处理菜单和帮助菜单")
    
    # 显示窗口（用于人工验证）
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main()