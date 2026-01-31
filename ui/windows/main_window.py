"""
现代化主窗口界面
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QStatusBar, QToolBar, QTabWidget, QDockWidget,
    QMessageBox, QFileDialog, QLabel, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QKeySequence

from ui.widgets.video_comparison_widget import VideoComparisonWidget
from ui.widgets.task_progress_widget import TaskProgressWidget
from ui.widgets.encode_config_panel import EncodeConfigPanel
from ui.viewmodels.main_viewmodel import MainViewModel


class MainWindow(QMainWindow):
    """现代化主窗口"""
    
    def __init__(self):
        super().__init__()
        self.viewmodel = MainViewModel()
        
        self.setWindowTitle('MediaFlow - 高性能媒体批处理工具')
        self.setGeometry(100, 100, 1400, 900)
        
        # 设置样式
        self._apply_style()
        
        # 初始化界面
        self._init_actions()
        self._init_menus()
        self._init_toolbar()
        self._init_central_widget()
        self._init_status_bar()
        self._init_dock_widgets()
        
        # 连接信号
        self._connect_signals()
    
    def _apply_style(self):
        """应用现代化样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
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
            }
            QToolBar QToolButton {
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px;
            }
            QToolBar QToolButton:hover {
                background-color: #f0f0f0;
            }
            QToolBar QToolButton:checked {
                background-color: #e6f3ff;
            }
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #007acc;
            }
            QStatusBar {
                background-color: #f5f5f5;
                border-top: 1px solid #e0e0e0;
            }
            QSplitter::handle {
                background-color: #e0e0e0;
            }
            QSplitter::handle:hover {
                background-color: #d0d0d0;
            }
        """)
    
    def _init_actions(self):
        """初始化动作"""
        # 文件操作
        
        self.add_folder_action = QAction("添加文件夹", self)
        self.add_folder_action.setShortcut(QKeySequence.StandardKey.New)
        self.add_folder_action.setStatusTip("添加媒体文件夹")
        
        self.save_action = QAction("保存", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setStatusTip("保存处理结果")
        
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
        file_menu.addAction(self.save_action)
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
        toolbar.addSeparator()
        toolbar.addAction(self.preview_action)
        toolbar.addAction(self.batch_process_action)
    
    def _init_central_widget(self):
        """初始化中央部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器 - 左侧文件浏览器，右侧处理面板
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板 - 文件浏览器
        self.file_browser = self._create_file_browser()
        splitter.addWidget(self.file_browser)
        
        # 右侧面板 - 处理选项卡
        self.right_panel = self._create_right_panel()
        splitter.addWidget(self.right_panel)
        
        # 设置分割比例
        splitter.setSizes([400, 1000])
        
        main_layout.addWidget(splitter)
    
    def _create_file_browser(self):
        """创建文件浏览器"""
        # 这里暂时创建一个简单的框架，后续可以扩展
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        
        # 标题
        title_label = QLabel("文件浏览器")
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; padding: 10px;")
        
        # 文件列表（这里使用占位符，实际实现需要文件系统模型）
        placeholder = QLabel("文件浏览器区域\n\n支持拖拽上传\n支持多选操作")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("""
            background-color: #f9f9f9;
            border: 2px dashed #d0d0d0;
            border-radius: 8px;
            padding: 40px;
            font-size: 14px;
            color: #888888;
        """)
        
        browser_layout.addWidget(title_label)
        browser_layout.addWidget(placeholder)
        
        return browser_widget
    
    def _create_right_panel(self):
        """创建右侧处理面板"""
        # 使用选项卡组织不同的功能
        tab_widget = QTabWidget()
        
        # 预览对比选项卡
        self.comparison_widget = VideoComparisonWidget()
        tab_widget.addTab(self.comparison_widget, "预览对比")
        
        # 处理配置选项卡
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        
        # 编码配置面板
        self.encode_config_panel = EncodeConfigPanel()
        config_layout.addWidget(self.encode_config_panel)
        
        # 预留其他配置面板的位置
        advanced_config_label = QLabel("高级配置选项...")
        advanced_config_label.setStyleSheet("color: #888888; font-style: italic;")
        config_layout.addWidget(advanced_config_label)
        
        config_layout.addStretch()
        tab_widget.addTab(config_widget, "处理配置")
        
        # 任务管理选项卡
        self.task_progress_widget = TaskProgressWidget()
        tab_widget.addTab(self.task_progress_widget, "任务进度")
        
        return tab_widget
    
    def _init_status_bar(self):
        """初始化状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 添加状态信息
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 添加处理统计信息
        self.stats_label = QLabel("0 个任务 | 0% 完成")
        self.status_bar.addPermanentWidget(self.stats_label)
    
    def _init_dock_widgets(self):
        """初始化停靠窗口"""
        # 处理历史停靠窗口
        history_dock = QDockWidget("处理历史", self)
        history_widget = QWidget()
        
        history_layout = QVBoxLayout(history_widget)
        history_placeholder = QLabel("处理历史记录\n\n暂无历史记录")
        history_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        history_placeholder.setStyleSheet("color: #888888;")
        history_layout.addWidget(history_placeholder)
        
        history_dock.setWidget(history_widget)
        history_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                    Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, history_dock)
    
    def _connect_signals(self):
        """连接信号"""
        # 连接动作信号
        self.exit_action.triggered.connect(self.close)
        self.about_action.triggered.connect(self._show_about_dialog)
        
        # 连接视图模型信号
        self.viewmodel.status_message_changed.connect(self._update_status)
        
        # 连接任务进度信号
        self.task_progress_widget.task_cancelled.connect(self._cancel_task)
    
    def _show_about_dialog(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 MediaFlow",
            "MediaFlow - 高性能媒体批处理工具\n\n"
            "版本: 2.0\n"
            "使用PySide6和现代化架构\n"
            "支持视频/图像批处理、质量分析、硬件加速等特性"
        )
    
    def _update_status(self, message: str):
        """更新状态栏"""
        self.status_label.setText(message)
    
    def _cancel_task(self, task_id: str):
        """取消任务"""
        self.viewmodel.cancel_task(task_id)
        self.task_progress_widget.remove_task(task_id)
    
    def closeEvent(self, event):
        """关闭事件处理"""
        # 清理资源
        self.viewmodel.dispose()
        event.accept()