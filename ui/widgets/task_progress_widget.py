"""
任务进度控件
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from core.services.task_queue import TaskStatus


class TaskProgressWidget(QWidget):
    """任务进度控件"""
    
    task_cancelled = Signal(str)  # 任务ID
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
        
        # 存储任务信息的映射
        self._task_items = {}
    
    def _setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("任务进度")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # 进度列表
        self.progress_list = QListWidget()
        
        # 添加到布局
        layout.addWidget(title_label)
        layout.addWidget(self.progress_list)
    
    def _connect_signals(self):
        """连接信号"""
        pass
    
    def add_task(self, task_id: str, task_name: str):
        """添加任务到进度列表"""
        # 创建列表项
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        
        # 任务名称标签
        name_label = QLabel(task_name)
        name_label.setMinimumWidth(150)
        
        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        
        # 状态标签
        status_label = QLabel("等待中")
        status_label.setStyleSheet("color: #666666;")
        status_label.setMinimumWidth(80)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setMaximumWidth(60)
        cancel_btn.clicked.connect(lambda: self._cancel_task(task_id))
        
        # 添加到布局
        item_layout.addWidget(name_label)
        item_layout.addWidget(progress_bar)
        item_layout.addWidget(status_label)
        item_layout.addWidget(cancel_btn)
        item_layout.setContentsMargins(2, 2, 2, 2)
        
        # 创建列表项并设置
        list_item = QListWidgetItem(self.progress_list)
        list_item.setSizeHint(item_widget.sizeHint())
        self.progress_list.addItem(list_item)
        self.progress_list.setItemWidget(list_item, item_widget)
        
        # 存储引用
        self._task_items[task_id] = {
            'item': list_item,
            'widget': item_widget,
            'name_label': name_label,
            'progress_bar': progress_bar,
            'status_label': status_label,
            'cancel_btn': cancel_btn
        }
    
    def update_task_progress(self, task_id: str, progress: int, status: str = None):
        """更新任务进度"""
        if task_id in self._task_items:
            item_data = self._task_items[task_id]
            item_data['progress_bar'].setValue(progress)
            
            if status:
                # 根据状态设置颜色
                color_map = {
                    'pending': '#666666',
                    'processing': '#0066CC',
                    'completed': '#00AA00',
                    'failed': '#CC0000',
                    'cancelled': '#AAAAAA'
                }
                color = color_map.get(status.lower(), '#666666')
                item_data['status_label'].setText(status.title())
                item_data['status_label'].setStyleSheet(f"color: {color};")
    
    def _cancel_task(self, task_id: str):
        """取消任务"""
        self.task_cancelled.emit(task_id)
    
    def remove_task(self, task_id: str):
        """移除任务"""
        if task_id in self._task_items:
            item_data = self._task_items[task_id]
            list_item = item_data['item']
            
            # 从列表中移除
            row = self.progress_list.row(list_item)
            self.progress_list.takeItem(row)
            
            # 清理引用
            del self._task_items[task_id]