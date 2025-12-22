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
                             QHeaderView, QTextEdit, QSplitter, QDialog, 
                             QTableWidget, QTableWidgetItem, QDialogButtonBox,
                             QMessageBox, QLineEdit, QComboBox, QRadioButton, 
                             QButtonGroup, QCheckBox, QSpinBox, QScrollArea, QFormLayout,
                             QShortcut)
from PyQt5.QtCore import QDir, Qt, QFileInfo, pyqtSignal
from PyQt5.QtGui import QKeySequence, QStandardItemModel, QStandardItem


class CustomSuffixDialog(QDialog):
    """自定义后缀对话框"""
    
    def __init__(self, parent=None, saved_suffixes=None):
        super().__init__(parent)
        self.setWindowTitle("添加自定义后缀")
        self.setModal(True)
        
        self.saved_suffixes = saved_suffixes or []
        
        self.init_ui()
        # 调整窗口大小以适应内容，确保所有行都可见
        self.adjustSizeToFitContent()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题和说明
        title_label = QLabel("<h3>添加自定义文件后缀</h3>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        info_label = QLabel("在下方表格中填写你想要添加的自定义后缀。\n小写后缀会自动包含大写版本（例如.jpg也会处理.JPG）")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 创建表格（10行：1行标题 + 9行数据），单列
        self.table = QTableWidget(10, 1)
        self.table.setHorizontalHeaderLabels(["想要消除的后缀"])
        self.table.horizontalHeader().setStretchLastSection(True)
        # 设置行高，确保所有行都能清晰显示
        self.table.verticalHeader().setDefaultSectionSize(30)
        # 设置最小宽度
        self.table.setMinimumWidth(300)
        
        # 加载已保存的自定义后缀
        self.load_saved_suffixes()
        
        layout.addWidget(self.table)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def adjustSizeToFitContent(self):
        """调整窗口大小以确保表格内容完全可见"""
        # 确保表格已经布局完成
        self.table.updateGeometry()
        self.table.viewport().update()
        
        # 精确计算表格所需高度（10行 * 行高30像素 + 表头高度 + 表格边框）
        row_height = 30  # 每行高度
        header_height = self.table.horizontalHeader().height()
        vertical_spacing = 5  # 垂直间距
        
        # 计算表格总高度
        table_height = 10 * row_height + header_height + vertical_spacing
        
        # 计算其他部件的高度
        # 标题标签高度约50px，说明标签高度约50px，按钮区域高度约50px，边距约50px
        extra_height = 200  # 增加额外高度确保所有内容可见
        
        # 计算宽度：确保列标题完全可见，加上一些边距
        min_width = 400  # 增加宽度确保列标题和内容可见
        
        # 设置窗口大小，确保所有行都可见
        total_height = table_height + extra_height
        
        # 确保窗口不会超过屏幕高度（留出100像素边距）
        screen_geometry = self.screen().availableGeometry()
        max_height = screen_geometry.height() - 100
        if total_height > max_height:
            total_height = max_height
        
        # 设置窗口大小
        self.resize(min_width, total_height)
        # 居中显示
        self.moveToCenter()
    
    def moveToCenter(self):
        """将窗口移动到屏幕中央"""
        screen_geometry = self.screen().availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def load_saved_suffixes(self):
        """加载已保存的自定义后缀到表格中"""
        for i, suffix in enumerate(self.saved_suffixes[:9], 1):
            if i < 10:
                item = QTableWidgetItem(suffix)
                self.table.setItem(i, 0, item)  # 单列，所以列索引为0
    
    def get_suffixes(self):
        """获取表格中填写的后缀列表"""
        suffixes = []
        for i in range(1, 10):
            item = self.table.item(i, 0)  # 单列，所以列索引为0
            if item and item.text().strip():
                suffix = item.text().strip()
                # 确保后缀以点开头
                if not suffix.startswith('.'):
                    suffix = '.' + suffix
                suffixes.append(suffix)
        return suffixes


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
        
        # 添加快捷键：Ctrl+D 和 Delete 键删除选中的文件夹
        self.setup_shortcuts()
        
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
        # 禁用双击展开文件夹的功能
        self.tree_view.setExpandsOnDoubleClick(False)
        # 隐藏展开箭头
        self.tree_view.setRootIsDecorated(False)
        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)  # 双击处理
        self.tree_view.clicked.connect(self.on_tree_item_clicked)  # 单击处理
        
        # 文件列表视图（用于显示根目录）
        self.list_view = QListView()
        self.list_view.setViewMode(QListView.ListMode)  # 改为列表模式
        self.list_view.setSelectionMode(QAbstractItemView.SingleSelection)  # 单选模式
        self.list_view.clicked.connect(self.on_root_selected)
        # 选中项变化时更新删除按钮状态（在update_root_list中连接）
        
        # 删除按钮
        self.delete_folder_btn = QPushButton("删除")
        self.delete_folder_btn.setToolTip("删除选中的文件夹（或使用 Ctrl+D / Delete 键）")
        self.delete_folder_btn.clicked.connect(self.delete_selected_folder)
        self.delete_folder_btn.setEnabled(False)  # 初始禁用，直到有选中项
        
        # 根目录标题行：标签 + 删除按钮
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(QLabel("根目录:"))
        header_layout.addStretch()
        header_layout.addWidget(self.delete_folder_btn)
        
        # 面包屑导航
        breadcrumb_container = QWidget()
        breadcrumb_layout = QHBoxLayout(breadcrumb_container)
        breadcrumb_layout.setContentsMargins(0, 0, 0, 0)
        breadcrumb_layout.setSpacing(2)
        self.breadcrumb_layout = breadcrumb_layout
        self.breadcrumb_container = breadcrumb_container
        
        # 添加所有部件到主布局
        layout.addWidget(header_container)      # 根目录标题行（带删除按钮）
        layout.addWidget(self.list_view)        # 根目录列表
        layout.addWidget(QLabel("目录结构:"))    # 目录结构标签
        layout.addWidget(self.breadcrumb_container)  # 面包屑导航
        layout.addWidget(self.tree_view)        # 文件树视图
        
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
        
        # 文件名前缀配置
        self.file_prefix_combo = QComboBox()
        self.file_prefix_combo.setEditable(True)  # 允许自定义输入
        self.file_prefix_combo.setToolTip("选择或输入文件名前缀，支持自定义")
        config_layout.addRow("文件名前缀:", self.file_prefix_combo)
        
        # 后缀编号配置
        self.suffix_number_spin = QSpinBox()
        self.suffix_number_spin.setRange(1, 999)
        self.suffix_number_spin.setValue(1)
        self.suffix_number_spin.setToolTip("设置文件的后缀编号（如-1、-2等）")
        config_layout.addRow("后缀编号:", self.suffix_number_spin)
        
        # 功能复选框（带帮助按钮）
        self.rename_jpg_check = QCheckBox("重命名JPG文件")
        self.rename_jpg_check.setChecked(True)
        self.rename_jpg_check.setToolTip("将带前缀的文件重命名为统一后缀")
        rename_layout = QHBoxLayout()
        rename_layout.addWidget(self.rename_jpg_check)
        self.rename_help_btn = QPushButton("?")
        self.rename_help_btn.setFixedSize(25, 25)
        self.rename_help_btn.setToolTip("点击查看详细说明")
        self.rename_help_btn.clicked.connect(lambda: self.show_option_help("rename_jpg"))
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
        
        # 文件扩展名快速选择区域
        extensions_layout = QHBoxLayout()
        extensions_layout.addWidget(QLabel("文件扩展名:"))
        
        # 加号按钮用于添加自定义后缀
        self.add_suffix_btn = QPushButton("+")
        self.add_suffix_btn.setFixedSize(25, 25)
        self.add_suffix_btn.setToolTip("添加自定义后缀")
        self.add_suffix_btn.clicked.connect(self.show_custom_suffix_dialog)
        extensions_layout.addWidget(self.add_suffix_btn)
        
        # 感叹号提示标签（带边框，悬停提示延迟短）
        self.info_label = QLabel("!")
        self.info_label.setToolTip("提示：小写后缀自动包含大写版本，例如.jpg也会处理.JPG")
        self.info_label.setFixedSize(24, 24)  # 固定为正方形
        self.info_label.setAlignment(Qt.AlignCenter)  # 内容居中
        self.info_label.setStyleSheet("""
            QLabel {
                color: orange;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid orange;
                border-radius: 0px;
                background-color: #fff8e1;
                text-align: center;
            }
            QLabel::hover {
                background-color: #ffecb3;
                border-color: #ff9800;
            }
        """)
        # 设置tooltip显示延迟较短（毫秒）
        self.info_label.setToolTipDuration(1000)  # 1秒后显示
        extensions_layout.addWidget(self.info_label)
        
        extensions_layout.addWidget(QLabel("快速选择:"))
        
        # 常见照片扩展名
        self.common_ext_buttons = {}
        common_extensions = ['.jpg', '.dng', '.nef', '.arw', '.xef', '.cr2', '.tif']
        for ext in common_extensions:
            btn = QPushButton(ext)
            btn.setCheckable(True)
            btn.setChecked(ext in ['.jpg', '.dng'])
            btn.setFixedSize(50, 25)
            btn.clicked.connect(self.update_selected_extensions)
            extensions_layout.addWidget(btn)
            self.common_ext_buttons[ext] = btn
        
        # 自定义后缀按钮（动态加载）
        self.custom_suffix_buttons = {}
        
        extensions_layout.addStretch()
        config_layout.addRow("", extensions_layout)
        
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
        
        # 创建预览按钮容器（带边框）
        preview_button_container = QWidget()
        preview_button_container.setStyleSheet("""
            QWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f8f9fa;
                padding: 5px;
            }
        """)
        preview_button_layout = QHBoxLayout(preview_button_container)
        preview_button_layout.setContentsMargins(5, 5, 5, 5)
        
        # 预览按钮
        self.preview_button = QPushButton("预览效果")
        self.preview_button.setToolTip("预览处理后文件名的变化")
        self.preview_button.clicked.connect(self.preview_processing)
        self.preview_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        
        # 添加一些说明文本
        preview_label = QLabel("点击预览按钮查看处理后文件名的变化：")
        preview_label.setStyleSheet("color: #666666;")
        
        preview_button_layout.addWidget(preview_label)
        preview_button_layout.addStretch()
        preview_button_layout.addWidget(self.preview_button)
        
        # 添加预览文本区域
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlainText("在此处预览批处理操作的效果...")
        
        layout.addWidget(preview_button_container)
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
        model = QStandardItemModel()
        
        for path in self.root_paths:
            item = QStandardItem(os.path.basename(path))
            item.setData(path, Qt.UserRole)  # 存储完整路径
            model.appendRow(item)
            
        self.list_view.setModel(model)
        
        # 连接选中项变化信号以更新删除按钮状态
        if self.list_view.selectionModel():
            self.list_view.selectionModel().selectionChanged.connect(self.on_root_selection_changed)
    
    
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

    def on_item_double_clicked(self, index):
        """树视图双击事件处理：双击文件夹进入，双击文件打开"""
        if index.isValid():
            model = self.tree_view.model()
            if model:
                file_path = model.filePath(index)
                file_info = QFileInfo(file_path)
                
                if file_info.isDir():
                    # 双击文件夹：进入该文件夹
                    self.tree_view.setRootIndex(index)
                    # 更新面包屑导航
                    self.update_breadcrumb(index)
                    # 更新状态栏
                    self.statusBar.showMessage(f'当前文件夹: {file_path}')
                else:
                    # 双击文件：使用默认程序打开
                    self.open_file(index)
    
    def save_config(self):
        config = {
            "root_paths": self.root_paths,
            "custom_prefixes": self.get_custom_prefixes(),
            "custom_suffixes": self.get_custom_suffixes()
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
                
                # 加载自定义前缀
                if "custom_prefixes" in config:
                    self.load_custom_prefixes(config["custom_prefixes"])
                    
                self.statusBar.showMessage(f'已加载 {len(self.root_paths)} 个文件夹')
            except Exception as e:
                print(f"加载配置失败: {e}")
        
        # 初始化前缀组合框（如果配置中没有或加载失败）
        if not hasattr(self, 'file_prefix_combo') or self.file_prefix_combo.count() == 0:
            self.init_prefix_combo()
            
    def init_prefix_combo(self):
        """初始化前缀组合框"""
        # 默认前缀列表
        default_prefixes = ["_DSC", "_Z8", "_Z72", "_A3R3", "_ILCE-7M4"]
        
        # 清除现有项目
        self.file_prefix_combo.clear()
        
        # 添加默认前缀
        for prefix in default_prefixes:
            self.file_prefix_combo.addItem(prefix)
        
        # 设置默认值
        self.file_prefix_combo.setCurrentText("_DSC")
        
        # 加载已保存的自定义前缀
        self.load_saved_custom_prefixes()
    
    def load_custom_prefixes(self, prefixes):
        """加载自定义前缀到组合框"""
        if hasattr(self, 'file_prefix_combo'):
            # 添加自定义前缀（去重）
            current_items = [self.file_prefix_combo.itemText(i) for i in range(self.file_prefix_combo.count())]
            for prefix in prefixes:
                if prefix not in current_items:
                    self.file_prefix_combo.addItem(prefix)
    
    def load_saved_custom_prefixes(self):
        """从配置文件加载已保存的自定义前缀"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if "custom_prefixes" in config:
                        self.load_custom_prefixes(config["custom_prefixes"])
            except Exception as e:
                print(f"加载自定义前缀失败: {e}")
    
    def save_custom_prefixes(self):
        """保存自定义前缀到配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                config = {}
        else:
            config = {}
        
        # 获取当前组合框中的所有项目
        all_prefixes = [self.file_prefix_combo.itemText(i) for i in range(self.file_prefix_combo.count())]
        
        # 获取默认前缀列表
        default_prefixes = ["_DSC", "_Z8", "_Z72", "_A3R3", "_ILCE-7M4"]
        
        # 筛选出自定义前缀（不在默认列表中的）
        custom_prefixes = [prefix for prefix in all_prefixes if prefix not in default_prefixes]
        
        # 更新配置
        config["custom_prefixes"] = custom_prefixes
        
        # 保存配置
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存自定义前缀失败: {e}")
    
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

    def update_selected_extensions(self):
        """更新选中的扩展名（包括常见和自定义后缀）"""
        selected_extensions = []
        
        # 收集常见后缀按钮的状态
        for ext, btn in self.common_ext_buttons.items():
            if btn.isChecked():
                selected_extensions.append(ext)
        
        # 收集自定义后缀按钮的状态
        for ext, btn in self.custom_suffix_buttons.items():
            if btn.isChecked():
                selected_extensions.append(ext)
        
        # 保存当前选择到配置
        self.save_config()
        
        # 更新预览或状态信息
        if selected_extensions:
            self.statusBar.showMessage(f'已选择 {len(selected_extensions)} 个文件扩展名')
        else:
            self.statusBar.showMessage('未选择任何文件扩展名')

    def show_custom_suffix_dialog(self):
        """显示自定义后缀对话框"""
        # 加载已保存的自定义后缀
        saved_suffixes = self.get_custom_suffixes()
        
        dialog = CustomSuffixDialog(self, saved_suffixes)
        if dialog.exec_() == QDialog.Accepted:
            suffixes = dialog.get_suffixes()
            if suffixes:
                # 保存新的后缀
                self.save_custom_suffixes(suffixes)
                # 更新UI显示
                self.load_custom_suffixes()
                self.statusBar.showMessage(f'已添加 {len(suffixes)} 个自定义后缀')

    def get_custom_suffixes(self):
        """从配置文件获取自定义后缀列表"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get("custom_suffixes", [])
            except Exception as e:
                print(f"获取自定义后缀失败: {e}")
        return []

    def save_custom_suffixes(self, suffixes):
        """保存自定义后缀到配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception as e:
                config = {}
        else:
            config = {}
        
        # 更新自定义后缀
        config["custom_suffixes"] = suffixes
        
        # 保存配置
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存自定义后缀失败: {e}")

    def load_custom_suffixes(self):
        """加载自定义后缀并更新UI"""
        suffixes = self.get_custom_suffixes()
        
        # 清除现有的自定义后缀按钮
        for btn in self.custom_suffix_buttons.values():
            btn.deleteLater()
        self.custom_suffix_buttons.clear()
        
        # 获取扩展名区域的布局
        config_layout = self.photo_suffix_config_group.layout()
        if config_layout is None:
            return
            
        # 找到扩展名布局的行
        for i in range(config_layout.rowCount()):
            item = config_layout.itemAt(i, QFormLayout.FieldRole)
            if item and hasattr(item, 'layout'):
                layout = item.layout()
                if layout and layout.indexOf(self.add_suffix_btn) >= 0:
                    # 这是扩展名布局
                    extensions_layout = layout
                    break
        else:
            extensions_layout = None
            
        if not extensions_layout:
            return
            
        # 在加号按钮后添加自定义后缀按钮
        add_btn_index = extensions_layout.indexOf(self.add_suffix_btn)
        
        # 添加自定义后缀按钮
        for suffix in suffixes:
            if suffix not in self.common_ext_buttons and suffix not in self.custom_suffix_buttons:
                btn = QPushButton(suffix)
                btn.setCheckable(True)
                btn.setChecked(False)
                btn.setFixedSize(50, 25)
                btn.clicked.connect(self.update_selected_extensions)
                extensions_layout.insertWidget(add_btn_index + 1, btn)
                self.custom_suffix_buttons[suffix] = btn
        
        # 确保感叹号标签在最右侧
        if hasattr(self, 'info_label'):
            extensions_layout.removeWidget(self.info_label)
            extensions_layout.addWidget(self.info_label)
            
        # 确保快速选择标签在正确位置
        quick_select_labels = []
        for i in range(extensions_layout.count()):
            widget = extensions_layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.text() == "快速选择:":
                quick_select_labels.append(widget)
        
        # 如果有多个快速选择标签，移除多余的
        for i, label in enumerate(quick_select_labels):
            if i > 0:
                extensions_layout.removeWidget(label)
                label.deleteLater()

    def get_custom_prefixes(self):
        """获取自定义前缀列表"""
        if hasattr(self, 'file_prefix_combo'):
            all_items = [self.file_prefix_combo.itemText(i) for i in range(self.file_prefix_combo.count())]
            default_prefixes = ["_DSC", "_Z8", "_Z72", "_A3R3", "_ILCE-7M4"]
            return [prefix for prefix in all_items if prefix not in default_prefixes]
        return []

    def show_option_help(self, option_type):
        """显示选项的帮助信息"""
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
        
        # 收集选中的扩展名（包括常见和自定义后缀）
        selected_extensions = []
        
        # 常见后缀按钮
        for ext, btn in self.common_ext_buttons.items():
            if btn.isChecked():
                # 添加小写版本
                selected_extensions.append(ext.lower())
                # 自动添加大写版本
                selected_extensions.append(ext.upper())
        
        # 自定义后缀按钮
        for ext, btn in self.custom_suffix_buttons.items():
            if btn.isChecked():
                # 确保后缀以点开头
                ext_with_dot = ext if ext.startswith('.') else '.' + ext
                selected_extensions.append(ext_with_dot.lower())
                # 自动添加大写版本
                selected_extensions.append(ext_with_dot.upper())
        
        # 去重
        unique_extensions = []
        seen = set()
        for ext in selected_extensions:
            if ext not in seen:
                seen.add(ext)
                unique_extensions.append(ext)
        
        # 获取前缀
        file_prefix = self.file_prefix_combo.currentText().strip()
        
        return {
            'rename_jpg_files': self.rename_jpg_check.isChecked(),
            'file_prefix': file_prefix,
            'dsc_suffix_number': self.suffix_number_spin.value(),
            'process_denoised_jpg': self.process_denoised_jpg_check.isChecked(),
            'delete_denoised_dng': self.delete_denoised_dng_check.isChecked(),
            'remove_date_prefix': self.remove_date_prefix_check.isChecked(),
            'date_prefix_patterns': date_patterns,
            'file_extensions': unique_extensions
        }

    def on_tree_item_clicked(self, index):
        """树视图单击事件处理：单击只选中，不展开也不进入目录"""
        if index.isValid():
            # 只选中，不展开也不进入目录
            self.tree_view.setCurrentIndex(index)
            self.tree_view.scrollTo(index)

    def update_breadcrumb(self, index):
        """更新面包屑导航"""
        # 清除现有的面包屑部件
        while self.breadcrumb_layout.count():
            child = self.breadcrumb_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not index.isValid():
            return
        
        model = self.tree_view.model()
        if not model:
            return
        
        # 收集从根到当前索引的路径（绝对路径）
        path_parts = []
        absolute_paths = []
        current = index
        while current.isValid():
            path_parts.insert(0, model.fileName(current))
            absolute_paths.insert(0, model.filePath(current))
            current = current.parent()
        
        # 为每个部分创建面包屑按钮
        for i, (part, path) in enumerate(zip(path_parts, absolute_paths)):
            btn = QPushButton(part)
            btn.setFlat(True)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 2px 5px;
                    color: #0078d7;
                    text-decoration: underline;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
            # 修复lambda函数：使用默认参数正确捕获路径
            btn.clicked.connect(lambda checked, path=path: self.navigate_to_path(path))
            self.breadcrumb_layout.addWidget(btn)
            
            # 添加分隔符（如果不是最后一个）
            if i < len(path_parts) - 1:
                separator = QLabel(">")
                separator.setStyleSheet("color: #666; padding: 0 2px;")
                self.breadcrumb_layout.addWidget(separator)
        
        # 添加伸缩项以确保面包屑不会过度拉伸
        self.breadcrumb_layout.addStretch()

    def navigate_to_path(self, path):
        """通过绝对路径导航"""
        model = self.tree_view.model()
        if model:
            index = model.index(path)
            if index.isValid():
                # 设置该路径为根索引
                self.tree_view.setRootIndex(index)
                # 更新面包屑导航
                self.update_breadcrumb(index)
                # 更新状态栏
                self.statusBar.showMessage(f'当前文件夹: {path}')

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
            
            # 更新面包屑导航
            root_index = fs_model.index(folder_path)
            self.update_breadcrumb(root_index)
            
            self.statusBar.showMessage(f'当前文件夹: {folder_path}')

    def on_root_selection_changed(self):
        """根目录选中项变化时更新删除按钮状态"""
        has_selection = self.list_view.selectionModel().hasSelection()
        self.delete_folder_btn.setEnabled(has_selection)

    def delete_selected_folder(self):
        """删除选中的根目录"""
        # 获取当前选中的索引
        selected_indexes = self.list_view.selectionModel().selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "警告", "请先选择一个文件夹")
            return
        
        index = selected_indexes[0]
        model = self.list_view.model()
        if not model:
            return
        
        item = model.itemFromIndex(index)
        folder_path = item.data(Qt.UserRole)
        folder_name = item.text()
        
        # 确认删除对话框
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要从列表中删除文件夹 '{folder_name}' 吗？\n\n注意：这只会从列表中移除，不会删除实际文件。",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 从根目录列表中移除
            if folder_path in self.root_paths:
                self.root_paths.remove(folder_path)
            
            # 从模型字典中移除
            if folder_path in self.models:
                del self.models[folder_path]
            
            # 更新列表显示
            self.update_root_list()
            
            # 保存配置
            self.save_config()
            
            # 更新状态栏
            self.statusBar.showMessage(f'已从列表中移除文件夹: {folder_name}')
            
            # 如果没有选中的根目录，重置树视图
            if not self.root_paths:
                self.tree_view.setModel(None)
                # 清除面包屑导航
                while self.breadcrumb_layout.count():
                    child = self.breadcrumb_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

    def preview_processing(self):
        """预览处理后文件名的变化"""
        # 获取当前树视图的根目录路径
        model = self.tree_view.model()
        if not model:
            self.preview_text.setPlainText("错误：没有加载任何文件夹")
            return
        
        root_index = self.tree_view.rootIndex()
        if not root_index.isValid():
            self.preview_text.setPlainText("错误：请先选择一个文件夹")
            return
        
        folder_path = model.filePath(root_index)
        if not folder_path or not os.path.exists(folder_path):
            self.preview_text.setPlainText("错误：文件夹不存在")
            return
        
        # 检查是否选择了照片后缀剪切处理器
        if not self.image_radio.isChecked() or not self.photo_suffix_cut.isChecked():
            self.preview_text.setPlainText("错误：请先选择'图像'类型和'照片后缀剪切'选项")
            return
        
        # 获取配置选项
        options = self.get_photo_suffix_options()
        
        # 收集预览结果
        preview_results = []
        file_count = 0
        processed_count = 0
        
        # 获取配置的文件扩展名（不区分大小写）
        extensions = options.get('file_extensions', [])
        extensions_lower = [ext.lower() for ext in extensions]
        
        # 遍历文件夹中的文件
        for filename in os.listdir(folder_path):
            file_count += 1
            original_name = filename
            new_name = filename  # 默认不变
            
            # 检查文件扩展名是否在配置的扩展名列表中
            file_ext = os.path.splitext(filename)[1]
            if file_ext.lower() not in extensions_lower:
                # 不在处理范围内的文件，跳过
                continue
            
            # 1. 重命名JPG文件（如果启用）
            if options['rename_jpg_files']:
                new_name = self._preview_rename_jpg(filename, options)
            
            # 2. 处理降噪JPG文件（如果启用）
            if options['process_denoised_jpg'] and new_name == filename:
                # 如果前面的处理没有改变文件名，才检查降噪文件
                new_name = self._preview_process_denoised_jpg(filename, options)
            
            # 3. 移除日期前缀（如果启用）
            if options['remove_date_prefix'] and new_name == filename:
                # 如果前面的处理没有改变文件名，才检查日期前缀
                new_name = self._preview_remove_date_prefix(filename, options)
            
            # 如果文件名有变化，添加到结果
            if new_name != original_name:
                processed_count += 1
                preview_results.append(f"{original_name}  →  {new_name}")
        
        # 4. 删除降噪DNG文件（如果启用） - 在预览中显示将被删除的文件
        if options['delete_denoised_dng']:
            deleted_files = []
            for filename in os.listdir(folder_path):
                file_ext = os.path.splitext(filename)[1]
                if file_ext.lower() not in extensions_lower:
                    continue
                
                # 检查是否为降噪DNG文件
                import re
                if re.match(r'(_DSC\d{4})-已增强-降噪\.dng$', filename, re.IGNORECASE):
                    deleted_files.append(filename)
            
            if deleted_files:
                preview_results.append("\n--- 以下文件将被删除 ---")
                for filename in deleted_files:
                    preview_results.append(f"[删除] {filename}")
        
        # 生成预览文本
        if preview_results:
            summary = f"预览结果（文件夹：{os.path.basename(folder_path)}）\n"
            summary += f"总文件数：{file_count}，预计处理文件数：{processed_count}\n"
            summary += "=" * 50 + "\n"
            preview_text = summary + "\n".join(preview_results)
        else:
            preview_text = f"预览结果（文件夹：{os.path.basename(folder_path)}）\n"
            preview_text += f"总文件数：{file_count}，没有需要处理的文件。\n"
            preview_text += "请检查配置选项或文件扩展名设置。"
        
        self.preview_text.setPlainText(preview_text)
        self.statusBar.showMessage(f'预览完成：{processed_count}个文件将被处理')

    def _preview_rename_jpg(self, filename, options):
        """预览重命名JPG文件"""
        import re
        
        file_prefix = options.get('file_prefix', '_DSC')
        suffix_number = options.get('dsc_suffix_number', 1)
        file_ext = os.path.splitext(filename)[1]
        
        # 转义特殊字符
        escaped_prefix = re.escape(file_prefix)
        escaped_ext = re.escape(file_ext)
        
        # 匹配模式：前缀 + 4位数字 + '-' + 数字 + 扩展名
        pattern = r'(' + escaped_prefix + r'\d{4})-(\d+)' + escaped_ext + r'$'
        match = re.match(pattern, filename, re.IGNORECASE)
        if match:
            prefix_number = match.group(1)  # 例如 _DSC0001
            new_base = f"{prefix_number}-{suffix_number}"
            return new_base + file_ext
        
        return filename

    def _preview_process_denoised_jpg(self, filename, options):
        """预览处理降噪JPG文件"""
        import re
        
        suffix_number = options.get('dsc_suffix_number', 1)
        file_ext = os.path.splitext(filename)[1]
        
        # 匹配降噪JPG文件，如 _DSC0001-已增强-降噪.jpg 或 _DSC0001-已增强-降噪-3.jpg
        match = re.match(r'(_DSC\d{4})-已增强-降噪(-(\d+))?\.jpg$', filename, re.IGNORECASE)
        if match:
            dsc_number = match.group(1)
            return f"{dsc_number}-{suffix_number}{file_ext}"
        
        return filename

    def _preview_remove_date_prefix(self, filename, options):
        """预览移除日期前缀"""
        import re
        
        date_patterns = options.get('date_prefix_patterns', [])
        
        for pattern in date_patterns:
            match = re.match(pattern, filename)
            if match:
                # 计算匹配的日期前缀长度
                match_end = match.end()
                return filename[match_end:]  # 移除日期前缀
        
        return filename

    def setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+D 删除选中的文件夹
        ctrl_d_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        ctrl_d_shortcut.activated.connect(self.delete_selected_folder)
        
        # Delete 键删除选中的文件夹
        delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_shortcut.activated.connect(self.delete_selected_folder)
