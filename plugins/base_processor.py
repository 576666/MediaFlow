from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, Signal
from dataclasses import dataclass


class ProcessingResult:
    """处理结果"""
    task_id: str
    file_path: str
    success: bool
    message: str = ""
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MediaTask:
    """媒体处理任务"""
    file_path: str
    config: Dict[str, Any]
    task_id: str = ""


@dataclass
class PreviewResult:
    """预览结果"""
    original_name: str
    processed_name: str
    success: bool
    message: str = ""


# 创建一个混合元类，继承自QObject的元类和ABCMeta
class _QObjectMeta(type(QObject), type(ABC)):
    pass

class BaseProcessor(QObject, ABC, metaclass=_QObjectMeta):
    """重构后的处理器基类，支持异步和进度反馈"""
    
    # 进度信号
    progress_changed = Signal(str, float)  # 任务ID, 进度(0.0-1.0)
    task_completed = Signal(str, ProcessingResult)  # 任务ID, 结果
    task_failed = Signal(str, str)  # 任务ID, 错误信息
    
    @property
    @abstractmethod
    def name(self) -> str:
        """处理器名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """处理器描述"""
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """支持的文件格式"""
        pass
    
    @abstractmethod
    def create_task(self, file_path: str, config: Dict[str, Any]) -> MediaTask:
        """创建处理任务，而不是直接执行"""
        pass
    
    @abstractmethod
    def get_config_widget(self) -> QWidget:
        """返回配置UI控件"""
        pass
    
    @abstractmethod
    def process_task(self, task: MediaTask) -> ProcessingResult:
        """处理单个任务"""
        pass
    
    def generate_preview(self, file_path: str, preview_config: Dict[str, Any]) -> PreviewResult:
        """生成预览效果（可选实现）"""
        # 默认实现：直接处理小规模数据
        task = self.create_task(file_path, preview_config)
        result = self.process_task(task)
        return PreviewResult(
            original_name=file_path,
            processed_name=file_path + "_preview",
            success=result.success,
            message=result.message
        )