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
        from PyQt5.QtWidgets import (QComboBox, QRadioButton, QButtonGroup, 
                                     QHBoxLayout, QCheckBox, QSpinBox, 
                                     QLineEdit, QFormLayout, QScrollArea, QWidget)
        from PyQt5.QtCore import pyqtSignal
        
        group_box = QGroupBox("处理选项")
        layout = QVBoxLayout(group_box)
        
        # 添加处理选项
        layout.addWidget(QLabel("选择处理类型:"))
        
        # 创建处理类型单选按钮
        process_type_layout = QHBoxLayout()
        self.image_radio = QRadioButton("图像")
        self.video_radio = QRadioButton("视频")
        self.mixed_radio = QRadioButton("混合")
        
        # 处理类型单选按钮组
        self.process_type_group = QButtonGroup()
        self.process_type_group.addButton(self.image_radio, 1)
        self.process_type_group.addButton(self.video_radio, 2)
        self.process_type_group.addButton(self.mixed_radio, 3)
        
        process_type_layout.addWidget(self.image_radio)
        process_type_layout.addWidget(self.video_radio)
        process_type_layout.addWidget(self.mixed_radio)
        layout.addLayout(process_type_layout)
        
        # 图像选项组
        self.image_group = QGroupBox("图像选项")
        image_layout = QVBoxLayout(self.image_group)
        
        # 图像选项单选按钮
        self.photo_suffix_cut = QRadioButton("照片后缀剪切")
        self.photo_reorder = QRadioButton("照片重排序")
        
        # 图像选项单选按钮组
        self.image_options_group = QButtonGroup()
        self.image_options_group.addButton(self.photo_suffix_cut)
        self.image_options_group.addButton(self.photo_reorder)
        
        image_layout.addWidget(self.photo_suffix_cut)
        image_layout.addWidget(self.photo_reorder)
        
        # 照片后缀剪切配置区域（初始隐藏）
        self.photo_suffix_config_group = QGroupBox("照片后缀剪切配置")
        self.photo_suffix_config_group.setVisible(False)
        config_layout = QFormLayout(self.photo_suffix_config_group)
        
        # 后缀编号配置
        self.suffix_number_spin = QSpinBox()
        self.suffix_number_spin.setRange(1, 999)
        self.suffix_number_spin.setValue(1)
        self.suffix_number_spin.setToolTip("设置DSC文件的后缀编号（如-1、-2等）")
        config_layout.addRow("后缀编号:", self.suffix_number_spin)
        
        # 功能复选框（带帮助按钮）
        self.rename_dsc_check = QCheckBox("重命名DSC文件")
        self.rename_dsc_check.setChecked(True)
        self.rename_dsc_check.setToolTip("将_DSC0001-2.jpg等文件重命名为统一后缀")
        rename_layout = QHBoxLayout()
        rename_layout.addWidget(self.rename_dsc_check)
        self.rename_help_btn = QPushButton("?")
        self.rename_help_btn.setFixedSize(25, 25)
        self.rename_help_btn.setToolTip("点击查看详细说明")
        self.rename_help_btn.clicked.connect(lambda: self.show_option_help("rename_dsc"))
        rename_layout.addWidget(self.rename_help_btn)
        rename_layout.addStretch()
        config_layout.addRow("", rename_layout)
        
        self.process_denoised_jpg_check = QCheckBox("处理降噪JPG文件")
        self.process_denoised_jpg_check.setChecked(True)
        self.process_denoised_jpg_check.setToolTip("处理_已增强-降噪.jpg文件")
        denoise_jpg_layout = QHBoxLayout()
        denoise_jpg_layout.addWidget(self.process_denoised_jpg_check)
        self.denoise_jpg_help_btn = QPushButton("?")
        self.denoise_jpg_help_btn.setFixedSize(25, 25)
        self.denoise_jpg_help_btn.setToolTip("点击查看详细说明")
        self.denoise_jpg_help_btn.clicked.connect(lambda: self.show_option_help("process_denoised_jpg"))
        denoise_jpg_layout.addWidget(self.denoise_jpg_help_btn)
        denoise_jpg_layout.addStretch()
        config_layout.addRow("", denoise_jpg_layout)
        
        self.delete_denoised_dng_check = QCheckBox("删除降噪DNG文件")
        self.delete_denoised_dng_check.setChecked(True)
        self.delete_denoised_dng_check.setToolTip("删除_已增强-降噪.dng文件")
        delete_dng_layout = QHBoxLayout()
        delete_dng_layout.addWidget(self.delete_denoised_dng_check)
        self.delete_dng_help_btn = QPushButton("?")
        self.delete_dng_help_btn.setFixedSize(25, 25)
        self.delete_dng_help_btn.setToolTip("点击查看详细说明")
        self.delete_dng_help_btn.clicked.connect(lambda: self.show_option_help("delete_denoised_dng"))
        delete_dng_layout.addWidget(self.delete_dng_help_btn)
        delete_dng_layout.addStretch()
        config_layout.addRow("", delete_dng_layout)
        
        self.remove_date_prefix_check = QCheckBox("移除日期前缀")
        self.remove_date_prefix_check.setChecked(True)
        self.remove_date_prefix_check.setToolTip("移除YYYY-MM-DD-或YYYYMMDD+等日期前缀")
        date_prefix_layout = QHBoxLayout()
        date_prefix_layout.addWidget(self.remove_date_prefix_check)
        self.date_prefix_help_btn = QPushButton("?")
        self.date_prefix_help_btn.setFixedSize(25, 25)
        self.date_prefix_help_btn.setToolTip("点击查看详细说明")
        self.date_prefix_help_btn.clicked.connect(lambda: self.show_option_help("remove_date_prefix"))
        date_prefix_layout.addWidget(self.date_prefix_help_btn)
        date_prefix_layout.addStretch()
        config_layout.addRow("", date_prefix_layout)
        
        # 日期前缀模式
        self.date_prefix_edit = QLineEdit()
        self.date_prefix_edit.setText("YYYY-MM-DD-, YYYYMMDD+")
        self.date_prefix_edit.setToolTip("日期前缀模式，用逗号分隔多个模式")
        config_layout.addRow("日期前缀模式:", self.date_prefix_edit)
        
        # 文件扩展名
        self.file_extensions_edit = QLineEdit()
        self.file_extensions_edit.setText(".jpg, .JPG, .dng, .DNG")
        self.file_extensions_edit.setToolTip("处理的文件扩展名，用逗号分隔（输入小写会自动包含大写）")
        config_layout.addRow("文件扩展名:", self.file_extensions_edit)
        
        # 常见扩展名快速选择
        common_extensions_layout = QHBoxLayout()
        common_extensions_layout.addWidget(QLabel("快速选择:"))
        
        # 常见照片扩展名
        self.common_ext_buttons = {}
        common_extensions = ['.jpg', '.dng', '.nef', '.arw', '.xef', '.cr2', '.tif', '.tiff']
        for ext in common_extensions:
            btn = QPushButton(ext)
            btn.setCheckable(True)
            btn.setChecked(ext in ['.jpg', '.dng'])
            btn.setFixedSize(50, 25)
            btn.clicked.connect(self.update_file_extensions_from_common)
            common_extensions_layout.addWidget(btn)
            self.common_ext_buttons[ext] = btn
        
        common_extensions_layout.addStretch()
        config_layout.addRow("", common_extensions_layout)
        
        image_layout.addWidget(self.photo_suffix_config_group)
        
        layout.addWidget(self.image_group)
        
        # 视频选项组
        self.video_group = QGroupBox("视频选项")
        video_layout = QVBoxLayout(self.video_group)
        
        # 视频选项单选按钮
        self.framerate_integer = QRadioButton("帧率整数化")
        self.compress_video = QRadioButton("压缩视频")
        
        # 视频选项单选按钮组
        self.video_options_group = QButtonGroup()
        self.video_options_group.addButton(self.framerate_integer)
        self.video_options_group.addButton(self.compress_video)
        
        video_layout.addWidget(self.framerate_integer)
        video_layout.addWidget(self.compress_video)
        layout.addWidget(self.video_group)
        
        # 混合选项组
        self.mixed_group = QGroupBox("混合选项")
        mixed_layout = QVBoxLayout(self.mixed_group)
        
        # 混合选项单选按钮
        self.file_compact = QRadioButton("文件缩小化")
        self.file_extension_upper = QRadioButton("文件后缀大写化")
        
        # 混合选项单选按钮组
        self.mixed_options_group = QButtonGroup()
        self.mixed_options_group.addButton(self.file_compact)
        self.mixed_options_group.addButton(self.file_extension_upper)
        
        mixed_layout.addWidget(self.file_compact)
        mixed_layout.addWidget(self.file_extension_upper)
        layout.addWidget(self.mixed_group)
        
        # 初始状态下隐藏所有选项组
        self.image_group.setVisible(False)
        self.video_group.setVisible(False)
        self.mixed_group.setVisible(False)
        
        # 连接信号槽以切换选项组显示
        self.image_radio.toggled.connect(lambda checked: self.toggle_option_group(checked, self.image_group))
        self.video_radio.toggled.connect(lambda checked: self.toggle_option_group(checked, self.video_group))
        self.mixed_radio.toggled.connect(lambda checked: self.toggle_option_group(checked, self.mixed_group))
        
        # 连接照片后缀剪切单选按钮，显示/隐藏配置
        self.photo_suffix_cut.toggled.connect(self.toggle_photo_suffix_config)
        
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
    
    def toggle_option_group(self, checked, group):
        """切换选项组的可见性"""
        if checked:
            # 隐藏所有选项组
            self.image_group.setVisible(False)
            self.video_group.setVisible(False)
            self.mixed_group.setVisible(False)
            
            # 显示选中的选项组
            group.setVisible(True)

    def toggle_photo_suffix_config(self, checked):
        """显示/隐藏照片后缀剪切配置"""
        self.photo_suffix_config_group.setVisible(checked)

    def update_file_extensions_from_common(self):
        """从常见扩展名按钮更新文件扩展名输入框"""
        selected_extensions = []
        for ext, btn in self.common_ext_buttons.items():
            if btn.isChecked():
                selected_extensions.append(ext)
        
        # 更新输入框，用逗号分隔
        self.file_extensions_edit.setText(', '.join(selected_extensions))

    def show_option_help(self, option_type):
        """显示选项的帮助信息"""
        from PyQt5.QtWidgets import QMessageBox
        
        help_messages = {
            "rename_dsc": {
                "title": "重命名DSC文件",
                "message": """
                <html>
                <head>
                <style>
                table { border-collapse: collapse; margin: 10px 0; }
                th { background-color: #f2f2f2; padding: 8px; text-align: left; }
                td { padding: 8px; border: 1px solid #ddd; }
                .section { margin: 15px 0; }
                .warning { color: #d9534f; font-weight: bold; }
                </style>
                </head>
                <body>
                <div class="section">
                <h3>效果</h3>
                <p>将Lightroom批量导出的DSC文件重命名为统一后缀编号。</p>
                </div>
                
                <div class="section">
                <h3>示例</h3>
                <table>
                <tr><th>原始文件名</th><th>→</th><th>新文件名</th></tr>
                <tr><td>_DSC0001-2.jpg</td><td>→</td><td>_DSC0001-1.jpg</td></tr>
                <tr><td>_DSC0002-3.JPG</td><td>→</td><td>_DSC0002-1.JPG</td></tr>
                <tr><td>_DSC0003-4.dng</td><td>→</td><td>_DSC0003-1.dng</td></tr>
                </table>
                </div>
                
                <div class="section">
                <h3>注意</h3>
                <ol>
                <li>只处理_DSC开头、带数字后缀的文件</li>
                <li>使用上方设置的统一后缀编号（默认为1）</li>
                <li>如果目标文件已存在，则跳过重命名</li>
                </ol>
                </div>
                </body>
                </html>
                """
            },
            "process_denoised_jpg": {
                "title": "处理降噪JPG文件",
                "message": """
                <html>
                <head>
                <style>
                table { border-collapse: collapse; margin: 10px 0; }
                th { background-color: #f2f2f2; padding: 8px; text-align: left; }
                td { padding: 8px; border: 1px solid #ddd; }
                .section { margin: 15px 0; }
                .warning { color: #d9534f; font-weight: bold; }
                </style>
                </head>
                <body>
                <div class="section">
                <h3>效果</h3>
                <p>将降噪处理后的JPG文件重命名为统一格式。</p>
                </div>
                
                <div class="section">
                <h3>示例</h3>
                <table>
                <tr><th>原始文件名</th><th>→</th><th>新文件名</th></tr>
                <tr><td>_DSC0001-已增强-降噪.jpg</td><td>→</td><td>_DSC0001-1.jpg</td></tr>
                <tr><td>_DSC0002-已增强-降噪-3.JPG</td><td>→</td><td>_DSC0002-1.JPG</td></tr>
                </table>
                </div>
                
                <div class="section">
                <h3>注意</h3>
                <ol>
                <li>处理包含"已增强-降噪"字样的JPG文件</li>
                <li>移除降噪标记，保留DSC编号和统一后缀</li>
                <li>如果文件带有序号（如-3），也会被移除</li>
                </ol>
                </div>
                </body>
                </html>
                """
            },
            "delete_denoised_dng": {
                "title": "删除降噪DNG文件",
                "message": """
                <html>
                <head>
                <style>
                table { border-collapse: collapse; margin: 10px 0; }
                th { background-color: #f2f2f2; padding: 8px; text-align: left; }
                td { padding: 8px; border: 1px solid #ddd; }
                .section { margin: 15px 0; }
                .warning { color: #d9534f; font-weight: bold; }
                </style>
                </head>
                <body>
                <div class="section">
                <h3>效果</h3>
                <p>删除降噪处理后的DNG原始文件。</p>
                </div>
                
                <div class="section">
                <h3>示例</h3>
                <table>
                <tr><th>操作</th><th>文件名</th></tr>
                <tr><td>删除：</td><td>_DSC0001-已增强-降噪.dng</td></tr>
                <tr><td>删除：</td><td>_DSC0002-已增强-降噪.DNG</td></tr>
                </table>
                </div>
                
                <div class="section">
                <h3>注意</h3>
                <ol>
                <li><span class="warning">永久删除文件，无法恢复！</span></li>
                <li>只删除_DSC开头、包含"已增强-降噪"的DNG文件</li>
                <li>建议在处理前备份重要文件</li>
                </ol>
                </div>
                </body>
                </html>
                """
            },
            "remove_date_prefix": {
                "title": "移除日期前缀",
                "message": """
                <html>
                <head>
                <style>
                table { border-collapse: collapse; margin: 10px 0; }
                th { background-color: #f2f2f2; padding: 8px; text-align: left; }
                td { padding: 8px; border: 1px solid #ddd; }
                .section { margin: 15px 0; }
                .warning { color: #d9534f; font-weight: bold; }
                </style>
                </head>
                <body>
                <div class="section">
                <h3>效果</h3>
                <p>移除文件名开头的日期前缀。</p>
                </div>
                
                <div class="section">
                <h3>示例</h3>
                <table>
                <tr><th>原始文件名</th><th>→</th><th>新文件名</th></tr>
                <tr><td>2025-11-12-test.jpg</td><td>→</td><td>test.jpg</td></tr>
                <tr><td>20251112+photo.dng</td><td>→</td><td>photo.dng</td></tr>
                </table>
                </div>
                
                <div class="section">
                <h3>注意</h3>
                <ol>
                <li>支持多种日期格式（可自定义）</li>
                <li>默认支持：YYYY-MM-DD- 和 YYYYMMDD+</li>
                <li>如果目标文件已存在，则跳过重命名</li>
                </ol>
                </div>
                </body>
                </html>
                """
            }
        }
        
        if option_type in help_messages:
            help_info = help_messages[option_type]
            QMessageBox.information(self, help_info["title"], help_info["message"])

    def get_photo_suffix_options(self):
        """获取照片后缀剪切配置选项"""
        # 解析日期前缀模式
        date_patterns_text = self.date_prefix_edit.text().strip()
        date_patterns = []
        for pattern in date_patterns_text.split(','):
            pattern = pattern.strip()
            if pattern == 'YYYY-MM-DD-':
                date_patterns.append(r'^\d{4}-\d{2}-\d{2}-')
            elif pattern == 'YYYYMMDD+':
                date_patterns.append(r'^\d{8}\+')
            elif pattern:
                # 允许用户自定义正则表达式
                date_patterns.append(pattern)
        
        # 解析文件扩展名
        extensions_text = self.file_extensions_edit.text().strip()
        extensions = []
        for ext in extensions_text.split(','):
            ext = ext.strip()
            if ext:
                # 添加小写版本
                extensions.append(ext.lower())
                # 如果扩展名是小写，自动添加大写版本
                if ext.islower():
                    extensions.append(ext.upper())
        
        # 去重并保持顺序
        seen = set()
        unique_extensions = []
        for ext in extensions:
            if ext not in seen:
                seen.add(ext)
                unique_extensions.append(ext)
        
        return {
            'rename_dsc_files': self.rename_dsc_check.isChecked(),
            'dsc_suffix_number': self.suffix_number_spin.value(),
            'process_denoised_jpg': self.process_denoised_jpg_check.isChecked(),
            'delete_denoised_dng': self.delete_denoised_dng_check.isChecked(),
            'remove_date_prefix': self.remove_date_prefix_check.isChecked(),
            'date_prefix_patterns': date_patterns,
            'file_extensions': unique_extensions
        }
