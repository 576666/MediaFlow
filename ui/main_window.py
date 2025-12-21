#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口界面
"""

import sys
import json
import os
import subprocess
from PyQt5.QtWidgets import (QMainWindow, QTreeView, QFileSystemModel, 
                             QVBoxLayout, QWidget, QMenuBar, QToolBar, 
                             QAction, QStatusBar, QListView, QAbstractItemView,
                             QGroupBox, QPushButton, QHBoxLayout, QLabel, QFileDialog,
                             QHeaderView, QTextEdit, QSplitter)
from PyQt5.QtCore import QDir, Qt, QFileInfo
from PyQt5.QtGui import QKeySequence


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MediaFlow - 照片批处理工具')
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置窗口最大化显示
        self.showMaximized()
        
        # 存储根目录路径
        self.root_paths = []
        self.models = {}  # 存储每个根目录对应的模型
        
        # 配置文件路径
        self.config_file = "mediaflow_config.json"
        
        # 初始化UI
        self.init_ui()
        
        # 加载配置
        self.load_config()
        
    def init_ui(self):
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建中央部件
        self.create_central_widget()
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('就绪')
        
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu('文件(&F)')
        open_action = QAction('添加文件夹(&A)', self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.add_folder)
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(open_action)
        file_menu.addAction(exit_action)
        
        # 处理菜单
        process_menu = menu_bar.addMenu('处理(&P)')
        batch_process_action = QAction('批量处理(&B)', self)
        process_menu.addAction(batch_process_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu('帮助(&H)')
        about_action = QAction('关于(&A)', self)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        toolbar = self.addToolBar('工具栏')
        
        open_action = QAction('添加文件夹', self)
        open_action.setToolTip('添加新的文件夹到项目中')
        open_action.triggered.connect(self.add_folder)
        toolbar.addAction(open_action)
        
        process_action = QAction('开始处理', self)
        process_action.setToolTip('开始处理选中的文件')
        toolbar.addAction(process_action)
        
    def create_central_widget(self):
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)
        
        # 左侧文件浏览器
        left_panel = self.create_file_browser()
        layout.addWidget(left_panel, 1)
        
        # 右侧处理面板
        right_panel = self.create_processing_panel()
        layout.addWidget(right_panel, 1)
        
        self.setCentralWidget(central_widget)
        
    def create_file_browser(self):
        group_box = QGroupBox("文件浏览器")
        layout = QVBoxLayout(group_box)
        
        # 文件树视图
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.doubleClicked.connect(self.open_file)  # 双击打开文件
        
        # 文件列表视图（用于显示根目录）
        self.list_view = QListView()
        self.list_view.setViewMode(QListView.ListMode)  # 改为列表模式
        self.list_view.clicked.connect(self.on_root_selected)
        
        layout.addWidget(QLabel("根目录:"))
        layout.addWidget(self.list_view)
        layout.addWidget(QLabel("目录结构:"))
        layout.addWidget(self.tree_view)
        
        return group_box
        
    def create_processing_panel(self):
        # 创建一个分割器来实现上下布局
        splitter = QSplitter(Qt.Vertical)
        
        # 上方面板 - 处理选项
        top_panel = self.create_processing_options_panel()
        splitter.addWidget(top_panel)
        
        # 下方面板 - 预览区域
        bottom_panel = self.create_preview_panel()
        splitter.addWidget(bottom_panel)
        
        # 设置初始大小比例
        splitter.setSizes([300, 500])  # 上面300像素，下面500像素
        
        return splitter
    
    def create_processing_options_panel(self):
        group_box = QGroupBox("处理选项")
        layout = QVBoxLayout(group_box)
        
        # 添加处理选项
        layout.addWidget(QLabel("选择处理类型:"))
        # 这里将在后续添加实际的处理选项
        
        layout.addStretch()
        return group_box
        
    def create_preview_panel(self):
        group_box = QGroupBox("预览")
        layout = QVBoxLayout(group_box)
        
        # 添加预览文本区域
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlainText("在此处预览批处理操作的效果...")
        layout.addWidget(self.preview_text)
        
        return group_box
        
    def add_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            if folder_path not in self.root_paths:
                self.root_paths.append(folder_path)
                # 为每个根目录创建文件系统模型
                model = QFileSystemModel()
                model.setRootPath(QDir.rootPath())  # 设置为根路径以显示驱动器
                self.models[folder_path] = model
                
            self.update_root_list()
            self.save_config()
            self.statusBar.showMessage(f'已添加文件夹: {folder_path}')
    
    def update_root_list(self):
        # 创建一个模型来显示根目录列表
        from PyQt5.QtGui import QStandardItemModel, QStandardItem
        model = QStandardItemModel()
        
        for path in self.root_paths:
            item = QStandardItem(os.path.basename(path))
            item.setData(path, Qt.UserRole)  # 存储完整路径
            model.appendRow(item)
            
        self.list_view.setModel(model)
    
    def on_root_selected(self, index):
        # 获取选中的根目录路径
        model = self.list_view.model()
        if model:
            item = model.itemFromIndex(index)
            folder_path = item.data(Qt.UserRole)
            
            # 获取该根目录对应的模型
            fs_model = self.models.get(folder_path)
            if not fs_model:
                # 如果模型不存在，创建一个新的
                fs_model = QFileSystemModel()
                fs_model.setRootPath(QDir.rootPath())
                self.models[folder_path] = fs_model
                
            # 更新树视图，显示选中的根目录内容
            self.tree_view.setModel(fs_model)
            self.tree_view.setRootIndex(fs_model.index(folder_path))
            self.tree_view.setHeaderHidden(False)
            
            # 调整列宽以优化显示效果
            self.tree_view.header().setSectionResizeMode(0, QHeaderView.Stretch)
            self.tree_view.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.tree_view.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.tree_view.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            
            self.statusBar.showMessage(f'当前文件夹: {folder_path}')
    
    def open_file(self, index):
        """双击文件时使用默认程序打开"""
        model = self.tree_view.model()
        if model:
            file_path = model.filePath(index)
            file_info = QFileInfo(file_path)
            
            if file_info.isFile():  # 确保是文件而不是目录
                try:
                    if sys.platform.startswith('win'):
                        # Windows系统
                        os.startfile(file_path)
                    elif sys.platform.startswith('darwin'):
                        # macOS系统
                        subprocess.call(['open', file_path])
                    else:
                        # Linux系统
                        subprocess.call(['xdg-open', file_path])
                    
                    self.statusBar.showMessage(f'已打开文件: {file_path}')
                except Exception as e:
                    self.statusBar.showMessage(f'打开文件失败: {str(e)}')
    
    def save_config(self):
        config = {
            "root_paths": self.root_paths
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.root_paths = config.get("root_paths", [])
                    
                # 为加载的根目录创建模型
                for path in self.root_paths:
                    if os.path.exists(path):
                        model = QFileSystemModel()
                        model.setRootPath(QDir.rootPath())
                        self.models[path] = model
                        
                self.update_root_list()
                self.statusBar.showMessage(f'已加载 {len(self.root_paths)} 个文件夹')
            except Exception as e:
                print(f"加载配置失败: {e}")