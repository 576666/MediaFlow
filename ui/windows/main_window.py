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
        

        

    
    def _init_toolbar(self):
        """初始化工具栏"""
        toolbar = self.addToolBar("主工具栏")

        toolbar.addAction(self.add_folder_action)

    
    def _init_central_widget(self):
        """初始化中央部件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 只显示文件浏览器区域
        self.file_browser = self._create_file_browser()
        main_layout.addWidget(self.file_browser)
    
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
    

    
    def _init_status_bar(self):
        """初始化状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 添加状态信息
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        

    

    
    def _connect_signals(self):
        """连接信号"""
        # 连接动作信号
        self.exit_action.triggered.connect(self.close)

        
        # 连接视图模型信号
        self.viewmodel.status_message_changed.connect(self._update_status)
        

    

    
    def _update_status(self, message: str):
        """更新状态栏"""
        self.status_label.setText(message)
    

    
    def closeEvent(self, event):
        """关闭事件处理"""
        # 清理资源
        self.viewmodel.dispose()
        event.accept()