"""
主窗口视图模型
"""
from PySide6.QtCore import Signal
from typing import List, Dict, Any, Optional
import os

from ui.viewmodels.base_viewmodel import BaseViewModel, Command
from core.services.task_queue import TaskQueue
from core.models.video_task import VideoTask, TaskPriority
from core.models.media_file import MediaFile
from core.processor_manager import ProcessorManager


class MainViewModel(BaseViewModel):
    """主窗口视图模型"""
    
    # 信号定义
    root_paths_changed = Signal(List[str])
    current_folder_changed = Signal(str)
    preview_text_changed = Signal(str)
    status_message_changed = Signal(str)
    
    def __init__(self, parent: Optional[object] = None):
        super().__init__(parent)
        
        # 创建属性
        self.create_property('root_paths', [])
        self.create_property('current_folder', '')
        self.create_property('preview_text', '')
        self.create_property('status_message', '就绪')
        
        # 初始化服务
        self._task_queue = TaskQueue()
        self._processor_manager = ProcessorManager()
        
        # 命令
        self.add_folder_command = Command(self.add_folder)
        self.delete_folder_command = Command(self.delete_selected_folder, self.can_delete_folder)
        self.preview_command = Command(self.preview_processing)
        
        # 连接信号
        self._task_queue.task_completed.connect(self._on_task_completed)
        self._task_queue.task_failed.connect(self._on_task_failed)
        self._task_queue.task_progress.connect(self._on_task_progress)
        
    # 属性访问器
    @property
    def root_paths(self) -> List[str]:
        return self._get_property('root_paths')
    
    @root_paths.setter
    def root_paths(self, value: List[str]):
        self._set_property('root_paths', value)
        self.root_paths_changed.emit(value)
    
    @property
    def current_folder(self) -> str:
        return self._get_property('current_folder')
    
    @current_folder.setter
    def current_folder(self, value: str):
        self._set_property('current_folder', value)
        self.current_folder_changed.emit(value)
    
    @property
    def preview_text(self) -> str:
        return self._get_property('preview_text')
    
    @preview_text.setter
    def preview_text(self, value: str):
        self._set_property('preview_text', value)
        self.preview_text_changed.emit(value)
    
    @property
    def status_message(self) -> str:
        return self._get_property('status_message')
    
    @status_message.setter
    def status_message(self, value: str):
        self._set_property('status_message', value)
        self.status_message_changed.emit(value)
    
    # 命令实现
    def add_folder(self, folder_path: Optional[str] = None) -> None:
        """添加文件夹"""
        # 如果未提供路径，则应由UI打开文件夹选择对话框
        # 这里只是模拟，实际UI应调用此方法并传入路径
        if folder_path and os.path.isdir(folder_path):
            if folder_path not in self.root_paths:
                new_paths = self.root_paths + [folder_path]
                self.root_paths = new_paths
                self.status_message = f'已添加文件夹: {folder_path}'
    
    def delete_selected_folder(self, folder_path: Optional[str] = None) -> None:
        """删除选中的文件夹"""
        if folder_path and folder_path in self.root_paths:
            new_paths = [p for p in self.root_paths if p != folder_path]
            self.root_paths = new_paths
            self.status_message = f'已从列表中移除文件夹: {os.path.basename(folder_path)}'
    
    def can_delete_folder(self) -> bool:
        """检查是否可以删除文件夹"""
        return len(self.root_paths) > 0
    
    def preview_processing(self, options: Optional[Dict[str, Any]] = None) -> None:
        """预览处理效果"""
        # 这里应该根据选项生成预览文本
        # 由于当前插件系统还未重构，我们先模拟一个预览
        preview = "预览结果：\n"
        preview += "1. 文件1.jpg → 文件1_processed.jpg\n"
        preview += "2. 文件2.png → 文件2_processed.png\n"
        preview += "3. 文件3.bmp → 文件3_processed.bmp\n"
        
        self.preview_text = preview
        self.status_message = '预览完成'
    
    # 任务处理
    def submit_processing_task(self, file_list: List[str], processor_name: str, 
                               config: Dict[str, Any]) -> str:
        """提交处理任务"""
        # 创建媒体文件列表
        media_files = [MediaFile(path=path) for path in file_list]
        
        # 创建任务
        task = VideoTask(
            task_id='',  # 由任务队列生成
            input_path=file_list[0] if file_list else '',
            output_path=file_list[0] + '_processed' if file_list else '',
            config=config,
            priority=TaskPriority.NORMAL
        )
        
        # 提交到任务队列
        task_id = self._task_queue.submit_batch_task(task)
        self.status_message = f'已提交任务: {task_id}'
        
        return task_id
    
    def submit_preview_task(self, file_list: List[str], processor_name: str,
                           config: Dict[str, Any]) -> str:
        """提交预览任务"""
        media_files = [MediaFile(path=path) for path in file_list]
        
        task = VideoTask(
            task_id='',
            input_path=file_list[0] if file_list else '',
            output_path=file_list[0] + '_preview' if file_list else '',
            config=config,
            priority=TaskPriority.HIGH
        )
        
        task_id = self._task_queue.submit_preview_task(task)
        self.status_message = f'已提交预览任务: {task_id}'
        
        return task_id
    
    def cancel_task(self, task_id: str) -> None:
        """取消任务"""
        success = self._task_queue.cancel_task(task_id)
        if success:
            self.status_message = f'已取消任务: {task_id}'
        else:
            self.status_message = f'取消任务失败: {task_id}'
    
    # 任务队列信号处理
    def _on_task_completed(self, task_id: str, result: dict) -> None:
        """任务完成处理"""
        self.status_message = f'任务完成: {task_id}'
    
    def _on_task_failed(self, task_id: str, error: Exception) -> None:
        """任务失败处理"""
        self.status_message = f'任务失败: {task_id}, 错误: {str(error)}'
        self.raise_error('TaskError', str(error))
    
    def _on_task_progress(self, task_id: str, current: int, total: int) -> None:
        """任务进度更新"""
        if total > 0:
            percent = (current / total) * 100
            self.status_message = f'任务 {task_id}: {percent:.1f}%'
    
    # 插件管理
    def get_available_processors(self) -> List[str]:
        """获取可用处理器列表"""
        return self._processor_manager.get_processor_names()
    
    def get_processor_info(self, name: str) -> Dict[str, Any]:
        """获取处理器信息"""
        processor = self._processor_manager.get_processor(name)
        if processor:
            return {
                'name': processor.name,
                'description': processor.description
            }
        return {}
    
    # 配置管理
    def load_config(self) -> None:
        """加载配置"""
        # 这里应该从配置文件加载
        # 暂时只加载根目录
        pass
    
    def save_config(self) -> None:
        """保存配置"""
        # 这里应该保存到配置文件
        pass
    
    def dispose(self) -> None:
        """清理资源"""
        super().dispose()
        if hasattr(self, '_task_queue'):
            self._task_queue.dispose()