"""
现代化主窗口界面 - 文件管理器布局
左侧：文件浏览器（真实文件结构）
右侧：预览面板（处理后的效果）
"""
import os
import json
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QStatusBar, QToolBar, QTabWidget, QDockWidget,
    QMessageBox, QFileDialog, QLabel, QFrame, QTreeView,
    QFileSystemModel, QListView, QAbstractItemView, QGroupBox,
    QPushButton, QTextEdit, QLineEdit, QSplitter as QtSplitter, 
    QHeaderView, QComboBox, QSizePolicy, QToolBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, QDir, QFileInfo, Signal, QModelIndex
from PySide6.QtGui import QAction, QIcon, QKeySequence, QStandardItemModel, QStandardItem


from ui.viewmodels.main_viewmodel import MainViewModel


class MainWindow(QMainWindow):
    """现代化主窗口 - 左右分栏布局"""
    
    def __init__(self):
        super().__init__()
        self.viewmodel = MainViewModel()
        
        self.setWindowTitle('MediaFlow - 文管理器')
        self.setGeometry(100, 100, 1400, 900)
        
        # 存储根目录路径
        self.root_paths = []
        self.file_models = {}  # 存储每个根目录对应的文件系统模型
        
        # 当前选中的文件
        self.current_files = []
        
        # 配置文件路径
        self.config_file = "mediaflow_config.json"
        
        # 设置样式
        self._apply_style()
        
        # 初始化界面
        self._init_actions()
        self._init_menus()
        self._init_toolbar()
        self._init_central_widget()
        self._init_status_bar()
        
        # 加载配置
        self._load_config()
        
        # 连接信号
        self._connect_signals()
    
    def _apply_style(self):
        """应用现代化样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QMenuBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
                spacing: 6px;
            }
            QMenuBar::item {
                padding: 8px 12px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background: #e6f3ff;
            }
            QMenuBar::item:pressed {
                background: #cce6ff;
            }
            QToolBar {
                background-color: #ffffff;
                border: none;
                spacing: 6px;
                padding: 6px;
                border-bottom: 1px solid #e0e0e0;
            }
            QToolBar QToolButton {
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px;
            }
            QToolBar QToolButton:hover {
                background-color: #e0e0e0;
            }
            QToolBar QToolButton:checked {
                background-color: #c0e0ff;
            }
            QStatusBar {
                background-color: #f5f5f5;
                border-top: 1px solid #e0e0e0;
            }
            QSplitter::handle {
                background-color: #d0d0d0;
                width: 4px;
            }
            QSplitter::handle:hover {
                background-color: #007acc;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
            QTreeView {
                border: 1px solid #d0d0d0;
                background-color: #ffffff;
            }
            QTreeView::item:hover {
                background-color: #e6f3ff;
            }
            QTreeView::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            QListView {
                border: 1px solid #d0d0d0;
                background-color: #ffffff;
            }
            QListView::item:hover {
                background-color: #e6f3ff;
            }
            QListView::item:selected {
                background-color: #007acc;
                color: #ffffff;
            }
            QTextEdit {
                border: 1px solid #d0d0d0;
                background-color: #ffffff;
            }
            QPushButton {
                padding: 6px 16px;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QPushButton:hover {
                background-color: #e6f3ff;
            }
            QPushButton:pressed {
                background-color: #c0e0ff;
            }
        """)
    
    def _init_actions(self):
        """初始化动作"""
        # 文件操作
        self.add_folder_action = QAction("添加文件夹", self)
        self.add_folder_action.setShortcut(QKeySequence.StandardKey.New)
        self.add_folder_action.setStatusTip("添加媒体文件夹")
        
        self.exit_action = QAction("退出", self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.setStatusTip("退出应用程序")
        
        # 处理操作
        self.preview_action = QAction("预览处理", self)
        self.preview_action.setShortcut("Ctrl+P")
        self.preview_action.setStatusTip("预览处理效果")
        
        self.batch_process_action = QAction("批量处理", self)
        self.batch_process_action.setShortcut("Ctrl+B")
        self.batch_process_action.setStatusTip("执行批量处理")
        
        # 帮助操作
        self.about_action = QAction("关于", self)
        self.about_action.setStatusTip("关于MediaFlow")
    
    def _init_menus(self):
        """初始化菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        file_menu.addAction(self.add_folder_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # 处理菜单
        process_menu = menubar.addMenu("处理(&P)")
        process_menu.addAction(self.preview_action)
        process_menu.addAction(self.batch_process_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        help_menu.addAction(self.about_action)
    
    def _init_toolbar(self):
        """初始化工具栏"""
        toolbar = self.addToolBar("主工具栏")
        toolbar.addAction(self.add_folder_action)
        toolbar.addAction(self.preview_action)
        toolbar.addAction(self.batch_process_action)
    
    def _init_central_widget(self):
        """初始化中央部件 - 左右分栏布局"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主水平布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        
        # 创建分割器 - 左侧文件浏览器和右侧预览面板
        splitter = QtSplitter(Qt.Horizontal)
        
        # 侧面板 - 文件浏览器
        left_panel = self._create_file_browser_panel()
        splitter.addWidget(left_panel)
        
        # 右侧面板 - 预览面板
        right_panel = self._create_preview_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割比例 (40% : 60%)
        splitter.setSizes([560, 840])
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 6)
        
        main_layout.addWidget(splitter)
    
    def _create_file_browser_panel(self) -> QWidget:
        """创建左侧文件浏览器面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel("📁 文件浏览器")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # 根目录列表
        group_box = QGroupBox("已添加的文件夹")
        group_layout = QVBoxLayout(group_box)
        
        # 根目录列表视图
        self.root_list_view = QListView()
        self.root_list_view.setMaximumHeight(120)
        self.root_list_view.setViewMode(QListView.ListMode)
        self.root_list_view.clicked.connect(self._on_root_selected)
        group_layout.addWidget(self.root_list_view)
        
        # 按钮行
        button_layout = QHBoxLayout()
        add_folder_btn = QPushButton("➕ 添加文件夹")
        add_folder_btn.clicked.connect(self._add_folder)
        remove_folder_btn = QPushButton("➖ 移除")
        remove_folder_btn.clicked.connect(self._remove_folder)
        button_layout.addWidget(add_folder_btn)
        button_layout.addWidget(remove_folder_btn)
        button_layout.addStretch()
        group_layout.addLayout(button_layout)
        
        layout.addWidget(group_box)
        
        # 文件树视图
        tree_group = QGroupBox("目录结构")
        tree_layout = QVBoxLayout(tree_group)
        
        self.file_tree_view = QTreeView()
        self.file_tree_view.setHeaderHidden(False)
        self.file_tree_view.setAlternatingRowColors(True)
        self.file_tree_view.doubleClicked.connect(self._on_file_double_clicked)
        self.file_tree_view.clicked.connect(self._on_file_clicked)
        tree_layout.addWidget(self.file_tree_view)
        
        layout.addWidget(tree_group)
        
        # 文件信息显示
        info_group = QGroupBox("文件信息")
        info_layout = QVBoxLayout(info_group)
        
        self.file_info_text = QTextEdit()
        self.file_info_text.setReadOnly(True)
        self.file_info_text.setMaximumHeight(100)
        self.file_info_text.setPlaceholderText("选择文件查看信息...")
        info_layout.addWidget(self.file_info_text)
        
        layout.addWidget(info_group)
        
        return panel
    
    def _create_preview_panel(self) -> QWidget:
        """创建右侧预览面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel("👁️ 预览效果")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # 文件路径配置 (紧凑布局)
        path_group = QGroupBox("文件路径")
        path_layout = QVBoxLayout(path_group)
        path_layout.setSpacing(14)  # 增加行间距
        path_layout.setContentsMargins(4, 4, 4, 4)
        
        # 限制最大高度
        from PySide6.QtWidgets import QSizePolicy
        path_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        path_group.setFixedHeight(120)  # 增加高度到120

        # 输入文件夹行 (只读，自动填充) - 紧凑行
        input_layout = QHBoxLayout()
        input_layout.setSpacing(6)  # 增加间距
        input_label = QLabel("输入:")
        input_label.setFixedWidth(30)
        self.input_path_edit = QLineEdit()  # 用QLineEdit替代，更紧凑
        self.input_path_edit.setReadOnly(True)
        self.input_path_edit.setFixedHeight(32)
        self.input_path_edit.setPlaceholderText("选择后自动填充...")
        input_layout.addWidget(input_label, 0)
        input_layout.addWidget(self.input_path_edit, 1)
        path_layout.addLayout(input_layout)

        # 输出文件夹行 - 紧凑行
        output_layout = QHBoxLayout()
        output_layout.setSpacing(6)  # 增加间距
        output_label = QLabel("输出:")
        output_label.setFixedWidth(30)
        self.output_path_edit = QLineEdit()  # 用QLineEdit替代
        self.output_path_edit.setFixedHeight(32)
        self.output_path_edit.setPlaceholderText("为空则默认同输入...")
        output_browse_btn = QPushButton("浏览")
        output_browse_btn.setFixedSize(80, 32)  # 增加按钮尺寸
        output_browse_btn.clicked.connect(self._browse_output_folder)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(output_browse_btn)
        path_layout.addLayout(output_layout)

        layout.addWidget(path_group)

        # 处理选项
        options_group = QGroupBox("处理选项")
        options_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        options_group.setMinimumHeight(340)
        options_layout = QVBoxLayout(options_group)

        # 插件选择抽屉
        self.plugin_group = QButtonGroup(self)

        self.plugin_toolbox = QToolBox()
        self.plugin_toolbox.setMinimumHeight(260)

        # 照片处理页
        photo_page = QWidget()
        photo_page.setMinimumHeight(160)
        photo_layout = QVBoxLayout(photo_page)
        photo_layout.setSpacing(10)
        photo_layout.setContentsMargins(8, 8, 8, 8)
        photo_options = [
            ("通用扩展名重命名", "photo_batch_rename"),
            ("照片灰度转换", "photo_grayscale"),
        ]
        for text, key in photo_options:
            rb = QRadioButton(text)
            rb.setProperty("plugin_key", key)
            self.plugin_group.addButton(rb)
            photo_layout.addWidget(rb)
        photo_layout.addStretch()
        self.plugin_toolbox.addItem(photo_page, "📷 照片处理")

        # 视频处理页
        video_page = QWidget()
        video_page.setMinimumHeight(160)
        video_layout = QVBoxLayout(video_page)
        video_layout.setSpacing(10)
        video_layout.setContentsMargins(8, 8, 8, 8)
        video_options = [
            ("通用扩展名重命名", "video_batch_rename"),
        ]
        for text, key in video_options:
            rb = QRadioButton(text)
            rb.setProperty("plugin_key", key)
            self.plugin_group.addButton(rb)
            video_layout.addWidget(rb)
        video_layout.addStretch()
        self.plugin_toolbox.addItem(video_page, "🎬 视频处理")

        # 混合处理页
        mixed_page = QWidget()
        mixed_page.setMinimumHeight(160)
        mixed_layout = QVBoxLayout(mixed_page)
        mixed_layout.setSpacing(10)
        mixed_layout.setContentsMargins(8, 8, 8, 8)
        mixed_options = [
            ("通用扩展名重命名", "mixed_batch_rename"),
            ("目录扁平化", "mixed_flatten"),
            ("自动备份(带转码)", "mixed_backup"),
        ]
        for text, key in mixed_options:
            rb = QRadioButton(text)
            rb.setProperty("plugin_key", key)
            self.plugin_group.addButton(rb)
            mixed_layout.addWidget(rb)
        mixed_layout.addStretch()
        self.plugin_toolbox.addItem(mixed_page, "🔄 混合处理")

        options_layout.addWidget(self.plugin_toolbox)

        # 格式转换参数
        rename_params_group = QGroupBox("格式转换参数")
        rename_params_layout = QVBoxLayout(rename_params_group)
        rename_params_layout.setSpacing(8)

        # 照片参数行
        photo_param_layout = QHBoxLayout()
        photo_param_layout.addWidget(QLabel("照片:"))
        self.photo_input_fmt = QComboBox()
        self.photo_input_fmt.addItems(["JPG", "JPEG", "PNG", "TIF", "TIFF"])
        self.photo_input_fmt.setFixedWidth(70)
        photo_param_layout.addWidget(self.photo_input_fmt)

        photo_param_layout.addWidget(QLabel("➡️"))
        self.photo_output_fmt = QComboBox()
        self.photo_output_fmt.addItems(["JPG", "JPEG", "PNG", "TIF", "TIFF"])
        self.photo_output_fmt.setFixedWidth(70)
        photo_param_layout.addWidget(self.photo_output_fmt)

        photo_param_layout.addWidget(QLabel("大小写:"))
        self.photo_case_combo = QComboBox()
        self.photo_case_combo.addItems(["保持原样", "全部大写", "全部小写"])
        self.photo_case_combo.setFixedWidth(90)
        photo_param_layout.addWidget(self.photo_case_combo)
        photo_param_layout.addStretch()
        rename_params_layout.addLayout(photo_param_layout)

        # 视频参数行
        video_param_layout = QHBoxLayout()
        video_param_layout.addWidget(QLabel("视频:"))
        self.video_input_fmt = QComboBox()
        self.video_input_fmt.addItems(["MP4", "MOV", "TS", "AVI", "MKV"])
        self.video_input_fmt.setFixedWidth(70)
        video_param_layout.addWidget(self.video_input_fmt)

        video_param_layout.addWidget(QLabel("➡️"))
        self.video_output_fmt = QComboBox()
        self.video_output_fmt.addItems(["MP4", "MOV", "TS", "AVI", "MKV"])
        self.video_output_fmt.setFixedWidth(70)
        video_param_layout.addWidget(self.video_output_fmt)

        video_param_layout.addWidget(QLabel("大小写:"))
        self.video_case_combo = QComboBox()
        self.video_case_combo.addItems(["保持原样", "全部大写", "全部小写"])
        self.video_case_combo.setFixedWidth(90)
        video_param_layout.addWidget(self.video_case_combo)
        video_param_layout.addStretch()
        rename_params_layout.addLayout(video_param_layout)

        options_layout.addWidget(rename_params_group)

        # 按钮行
        button_layout = QHBoxLayout()
        preview_btn = QPushButton("🔍 预览效果")
        preview_btn.clicked.connect(self._on_preview)
        process_btn = QPushButton("▶️ 执行处理")
        process_btn.clicked.connect(self._on_batch_process)
        button_layout.addWidget(preview_btn)
        button_layout.addWidget(process_btn)
        button_layout.addStretch()
        options_layout.addLayout(button_layout)

        layout.addWidget(options_group)
        
        # 处理结果预览
        preview_group = QGroupBox("处理结果预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("预览处理效果...\n\n选择左侧文件和处理插件后，点击「预览效果」按钮查看处理后的文件名和变化。")
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        return panel
    
    def _init_status_bar(self):
        """初始化状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 添加状态信息
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 文件计数
        self.file_count_label = QLabel("文件: 0")
        self.status_bar.addPermanentWidget(self.file_count_label)
    
    def _connect_signals(self):
        """连接信号"""
        # 连接动作信号
        self.exit_action.triggered.connect(self.close)
        self.about_action.triggered.connect(self._show_about)
        
        # 连接视图模型信号
        self.viewmodel.status_message_changed.connect(self._update_status)
    
    def _update_status(self, message: str):
        """更新状态栏"""
        self.status_label.setText(message)
    
    def _add_folder(self):
        """添加文件夹"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", QDir.homePath())
        if folder_path:
            if folder_path not in self.root_paths:
                self.root_paths.append(folder_path)
                # 为每个根目录创建文件系统模型
                model = QFileSystemModel()
                model.setRootPath(QDir.rootPath())
                self.file_models[folder_path] = model
                
                self._update_root_list()
                self._save_config()
                self._update_status(f"已添加文件夹: {folder_path}")
    
    def _remove_folder(self):
        """移除选中的文件夹"""
        current_index = self.root_list_view.currentIndex()
        if current_index.isValid():
            model = self.root_list_view.model()
            item = model.itemFromIndex(current_index)
            folder_path = item.data(Qt.UserRole)
            if folder_path in self.root_paths:
                self.root_paths.remove(folder_path)
                if folder_path in self.file_models:
                    del self.file_models[folder_path]
                self._update_root_list()
                self._save_config()
                self._update_status(f"已移除文件夹: {folder_path}")
    
    def _update_root_list(self):
        """更新根目录列表"""
        model = QStandardItemModel()
        for path in self.root_paths:
            item = QStandardItem(os.path.basename(path))
            item.setData(path, Qt.UserRole)
            item.setToolTip(path)
            model.appendRow(item)
        self.root_list_view.setModel(model)
    
    def _on_root_selected(self, index: QModelIndex):
        """根目录选中事件"""
        model = self.root_list_view.model()
        if model:
            item = model.itemFromIndex(index)
            folder_path = item.data(Qt.UserRole)
            
            # 获取该根目录对应的模型
            fs_model = self.file_models.get(folder_path)
            if not fs_model:
                fs_model = QFileSystemModel()
                fs_model.setRootPath(QDir.rootPath())
                self.file_models[folder_path] = fs_model
            
            # 更新树视图
            self.file_tree_view.setModel(fs_model)
            self.file_tree_view.setRootIndex(fs_model.index(folder_path))
            
            # 设置列宽
            header = self.file_tree_view.header()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            
            # 自动填充输入文件夹路径
            self.input_path_edit.setText(folder_path)
            
            self._update_status(f"当前文件夹: {folder_path}")

    def _browse_output_folder(self):
        """浏览选择输出文件夹"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择输出文件夹", QDir.homePath())
        if folder_path:
            self.output_path_edit.setText(folder_path)
            self._update_status(f"已设置输出文件夹: {folder_path}")
    
    def _on_file_clicked(self, index: QModelIndex):
        """文件点击事件"""
        model = self.file_tree_view.model()
        if model:
            file_path = model.filePath(index)
            file_info = QFileInfo(file_path)
            
            # 自动填充输入路径：如果是文件则取父文件夹，否则直接用该文件夹
            if file_info.isFile():
                target_path = os.path.dirname(file_path)
            else:
                target_path = file_path
            self.input_path_edit.setText(target_path)
            
            # 显示文件信息
            if file_info.isFile():
                size = file_info.size()
                size_str = self._format_size(size)
                modified = file_info.lastModified().toString("yyyy-MM-dd hh:mm:ss")
                info = f"文件: {file_info.fileName()}\n路径: {file_path}\n大小: {size_str}\n修改时间: {modified}"
                self.file_info_text.setPlainText(info)
            elif file_info.isDir():
                info = f"文件夹: {file_info.fileName()}\n路径: {file_path}"
                self.file_info_text.setPlainText(info)
    
    def _on_file_double_clicked(self, index: QModelIndex):
        """文件双击事件"""
        model = self.file_tree_view.model()
        if model:
            file_path = model.filePath(index)
            file_info = QFileInfo(file_path)
            
            if file_info.isFile():
                # 使用系统默认程序打开文件
                import subprocess
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                elif os.name == 'posix':
                    if subprocess.call(['which', 'xdg-open']) == 0:
                        subprocess.call(['xdg-open', file_path])
    
    def _on_preview(self):
        """预览处理效果"""
        input_path = self.input_path_edit.text().strip()
        if not input_path or not os.path.isdir(input_path):
            self.preview_text.setPlainText("⚠️ 请先选择左侧输入文件夹（有效目录）。")
            self._update_status("未选择有效输入文件夹")
            return

        checked_btn = self.plugin_group.checkedButton()
        if not checked_btn:
            self.preview_text.setPlainText("⚠️ 请先选择一个处理插件。")
            self._update_status("未选择处理插件")
            return

        plugin_key = checked_btn.property("plugin_key")
        preview_text = self._generate_preview_text(input_path, plugin_key)
        self.preview_text.setPlainText(preview_text)
        self._update_status("预览生成完成")

    def _generate_preview_text(self, folder_path: str, plugin_key: str) -> str:
        """根据插件类型生成预览文本"""
        lines = []
        base_name = os.path.basename(folder_path) or folder_path
        lines.append(f"📁 {base_name}/")
        lines.append("")

        if plugin_key == "mixed_flatten":
            lines.extend(self._preview_flatten(folder_path))
        elif plugin_key == "mixed_backup":
            lines.extend(self._preview_backup(folder_path))
        elif plugin_key == "photo_grayscale":
            lines.extend(self._preview_grayscale(folder_path))
        else:
            lines.extend(self._preview_rename(folder_path, plugin_key))

        return "\n".join(lines)

    def _preview_rename(self, folder_path: str, plugin_key: str) -> list:
        """生成重命名类操作的目录树预览"""
        lines = []
        photo_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.raw', '.cr2', '.nef', '.arw'}
        video_exts = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg'}

        for root, dirs, files in os.walk(folder_path):
            rel_root = os.path.relpath(root, folder_path)
            level = 0 if rel_root == '.' else rel_root.count(os.sep) + 1
            indent = "    " * level

            if level > 0:
                dir_name = os.path.basename(root)
                lines.append(f"{indent}📁 {dir_name}/")

            for f in sorted(files):
                new_name = self._simulate_rename(f, plugin_key, photo_exts, video_exts)
                if new_name != f:
                    lines.append(f"{indent}    📄 {f} ➡️ {new_name}")
                else:
                    lines.append(f"{indent}    📄 {f}")

        return lines

    def _simulate_rename(self, filename: str, plugin_key: str, photo_exts: set, video_exts: set) -> str:
        """模拟重命名操作，返回新文件名"""
        name, ext = os.path.splitext(filename)
        ext_lower = ext.lower()

        # 新的通用批量重命名（读取前端参数）
        if plugin_key in ("photo_batch_rename", "video_batch_rename", "mixed_batch_rename"):
            photo_in = self.photo_input_fmt.currentText().strip().lower()
            photo_out = self.photo_output_fmt.currentText().strip()
            photo_case = self.photo_case_combo.currentIndex()

            video_in = self.video_input_fmt.currentText().strip().lower()
            video_out = self.video_output_fmt.currentText().strip()
            video_case = self.video_case_combo.currentIndex()

            def apply_case(text: str, case_idx: int) -> str:
                if case_idx == 1:
                    return text.upper()
                elif case_idx == 2:
                    return text.lower()
                return text

            if plugin_key in ("photo_batch_rename", "mixed_batch_rename"):
                if ext_lower == '.' + photo_in:
                    return f"{name}.{apply_case(photo_out, photo_case)}"

            if plugin_key in ("video_batch_rename", "mixed_batch_rename"):
                if ext_lower == '.' + video_in:
                    return f"{name}.{apply_case(video_out, video_case)}"

            return filename

        # 旧的固定插件（兼容保留）
        if plugin_key == "photo_ext_upper":
            if ext_lower in photo_exts:
                return name + ext.upper()
        elif plugin_key == "photo_ext_lower":
            if ext_lower in photo_exts:
                return name + ext.lower()
        elif plugin_key == "video_ext_upper":
            if ext_lower in video_exts:
                return name + ext.upper()
        elif plugin_key == "video_ext_lower":
            if ext_lower in video_exts:
                return name + ext.lower()
        elif plugin_key == "photo_jpg_to_png":
            if ext_lower in {'.jpg', '.jpeg'}:
                return name + '.png'
        elif plugin_key == "photo_png_to_jpg":
            if ext_lower == '.png':
                return name + '.jpg'

        return filename

    def _preview_flatten(self, folder_path: str) -> list:
        """生成目录扁平化预览"""
        lines = []
        file_moves = []
        removed_dirs = []

        for root, dirs, files in os.walk(folder_path):
            rel_root = os.path.relpath(root, folder_path)
            if rel_root == '.':
                for f in sorted(files):
                    lines.append(f"    📄 {f} (已在根目录)")
                continue

            level = rel_root.count(os.sep) + 1
            indent = "    " * level
            dir_name = os.path.basename(root)
            lines.append(f"{indent}📁 {dir_name}/ 🚫")
            removed_dirs.append(dir_name)

            for f in sorted(files):
                file_moves.append(f"    📄 {f} ➡️ 📁 {os.path.basename(folder_path)}/📄 {f}")

        if file_moves:
            lines.append("")
            lines.append("【扁平化后文件位置】")
            lines.extend(file_moves)

        return lines

    def _preview_grayscale(self, folder_path: str) -> list:
        """生成照片灰度转换预览"""
        lines = []
        photo_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

        for root, dirs, files in os.walk(folder_path):
            rel_root = os.path.relpath(root, folder_path)
            level = 0 if rel_root == '.' else rel_root.count(os.sep) + 1
            indent = "    " * level

            if level > 0:
                dir_name = os.path.basename(root)
                lines.append(f"{indent}📁 {dir_name}/")

            for f in sorted(files):
                _, ext = os.path.splitext(f)
                if ext.lower() in photo_exts:
                    lines.append(f"{indent}    📄 {f} (灰度转换)")
                else:
                    lines.append(f"{indent}    📄 {f}")

        return lines

    def _preview_backup(self, folder_path: str) -> list:
        """生成自动备份预览"""
        lines = []
        output_path = self.output_path_edit.text().strip()
        if not output_path:
            output_path = f"{folder_path}_backup"

        lines.append(f"备份目标: {output_path}")
        lines.append("")

        for root, dirs, files in os.walk(folder_path):
            rel_root = os.path.relpath(root, folder_path)
            level = 0 if rel_root == '.' else rel_root.count(os.sep) + 1
            indent = "    " * level

            if level > 0:
                dir_name = os.path.basename(root)
                lines.append(f"{indent}📁 {dir_name}/")

            for f in sorted(files):
                _, ext = os.path.splitext(f)
                if ext.lower() in {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}:
                    lines.append(f"{indent}    📄 {f} (复制+转码)")
                else:
                    lines.append(f"{indent}    📄 {f} (复制)")

        return lines
    
    def _on_batch_process(self):
        """执行批量处理"""
        input_path = self.input_path_edit.text().strip()
        if not input_path or not os.path.isdir(input_path):
            QMessageBox.warning(self, "提示", "请先选择有效的输入文件夹。")
            return

        checked_btn = self.plugin_group.checkedButton()
        if not checked_btn:
            QMessageBox.warning(self, "提示", "请先选择一个处理插件。")
            return

        plugin_key = checked_btn.property("plugin_key")

        try:
            if plugin_key == "photo_batch_rename":
                self._run_photo_batch_rename(input_path)
            elif plugin_key == "video_batch_rename":
                self._run_video_batch_rename(input_path)
            elif plugin_key == "mixed_batch_rename":
                self._run_mixed_batch_rename(input_path)
            elif plugin_key == "photo_grayscale":
                self._update_status("照片灰度转换执行中...")
            elif plugin_key == "mixed_flatten":
                self._update_status("目录扁平化执行中...")
            elif plugin_key == "mixed_backup":
                self._update_status("自动备份执行中...")
            else:
                self._update_status("该插件执行功能待实现...")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"执行失败: {str(e)}")

    def _run_photo_batch_rename(self, folder_path: str):
        from batch_processors.photo.batch_extension_renamer import BatchPhotoExtensionRenamer
        input_ext = self.photo_input_fmt.currentText().strip()
        output_ext = self.photo_output_fmt.currentText().strip()
        case_map = {0: "as_is", 1: "upper", 2: "lower"}
        case_option = case_map.get(self.photo_case_combo.currentIndex(), "as_is")

        renamer = BatchPhotoExtensionRenamer(input_ext, output_ext, case_option)
        result = renamer.rename(folder_path)

        msg = f"照片格式转换完成：成功 {result['success']}，失败 {result['failed']}，跳过 {result['skipped']}"
        self.preview_text.setPlainText("\n".join(result["details"]))
        self._update_status(msg)
        QMessageBox.information(self, "完成", msg)

    def _run_video_batch_rename(self, folder_path: str):
        from batch_processors.video.batch_extension_renamer import BatchVideoExtensionRenamer
        input_ext = self.video_input_fmt.currentText().strip()
        output_ext = self.video_output_fmt.currentText().strip()
        case_map = {0: "as_is", 1: "upper", 2: "lower"}
        case_option = case_map.get(self.video_case_combo.currentIndex(), "as_is")

        renamer = BatchVideoExtensionRenamer(input_ext, output_ext, case_option)
        result = renamer.rename(folder_path)

        msg = f"视频格式转换完成：成功 {result['success']}，失败 {result['failed']}，跳过 {result['skipped']}"
        self.preview_text.setPlainText("\n".join(result["details"]))
        self._update_status(msg)
        QMessageBox.information(self, "完成", msg)

    def _run_mixed_batch_rename(self, folder_path: str):
        from batch_processors.mixed.batch_extension_renamer import BatchMixedExtensionRenamer
        photo_in = self.photo_input_fmt.currentText().strip()
        photo_out = self.photo_output_fmt.currentText().strip()
        video_in = self.video_input_fmt.currentText().strip()
        video_out = self.video_output_fmt.currentText().strip()
        case_map = {0: "as_is", 1: "upper", 2: "lower"}
        photo_case = case_map.get(self.photo_case_combo.currentIndex(), "as_is")
        video_case = case_map.get(self.video_case_combo.currentIndex(), "as_is")

        renamer = BatchMixedExtensionRenamer(
            photo_in, photo_out, video_in, video_out,
            photo_case, video_case
        )
        result = renamer.rename(folder_path)

        msg = f"混合格式转换完成：成功 {result['success']}，失败 {result['failed']}，跳过 {result['skipped']}"
        self.preview_text.setPlainText("\n".join(result["details"]))
        self._update_status(msg)
        QMessageBox.information(self, "完成", msg)
    
    def _show_about(self):
        """显示关于"""
        QMessageBox.about(self, "关于 MediaFlow", 
                        "MediaFlow - 文件管理器\n\n"
                        "高性能媒体批处理工具\n"
                        "版本: 2.0\n\n"
                        "左侧：文件浏览器\n"
                        "右侧：预览效果")
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    def _save_config(self):
        """保存配置"""
        config = {"root_paths": self.root_paths}
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def _load_config(self):
        """加载配置"""
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
                        self.file_models[path] = model
                
                self._update_root_list()
                self._update_status(f"已加载 {len(self.root_paths)} 个文件夹")
            except Exception as e:
                print(f"加载配置失败: {e}")
    
    def closeEvent(self, event):
        """关闭事件处理"""
        # 清理资源
        self.viewmodel.dispose()
        event.accept()