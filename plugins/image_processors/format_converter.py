"""
格式转换处理器插件
"""
import os
import cv2
from typing import List, Dict, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox

from plugins.base_processor import BaseProcessor, MediaTask, ProcessingResult


class FormatConverterProcessor(BaseProcessor):
    """格式转换处理器"""
    
    def __init__(self):
        super().__init__()
        self.supported_formats_list = [
            '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'
        ]
        self.target_format = '.jpg'  # 默认转换为目标格式
    
    @property
    def name(self) -> str:
        return "格式转换"
    
    @property
    def description(self) -> str:
        return "将图像文件转换为指定格式"
    
    @property
    def supported_formats(self) -> List[str]:
        """支持的输入文件格式"""
        return self.supported_formats_list
    
    def create_task(self, file_path: str, config: Dict[str, Any]) -> MediaTask:
        """创建处理任务"""
        import uuid
        return MediaTask(
            file_path=file_path,
            config=config,
            task_id=str(uuid.uuid4())
        )
    
    def get_config_widget(self) -> QWidget:
        """返回配置UI控件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title_label = QLabel("格式转换配置")
        title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(title_label)
        
        # 目标格式选择
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("目标格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['.jpg', '.png', '.bmp', '.webp'])
        self.format_combo.setCurrentText(self.target_format)
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)
        
        layout.addStretch()
        return widget
    
    def _on_format_changed(self, text: str):
        """格式选择变化处理"""
        self.target_format = text
    
    def process_task(self, task: MediaTask) -> ProcessingResult:
        """处理单个任务"""
        try:
            input_path = task.file_path
            config = task.config
            
            # 获取目标格式
            target_format = config.get('target_format', self.target_format)
            
            # 读取图像
            image = cv2.imread(input_path)
            if image is None:
                return ProcessingResult(
                    task_id=task.task_id,
                    file_path=input_path,
                    success=False,
                    message="无法读取图像文件"
                )
            
            # 生成输出路径
            base_path = os.path.splitext(input_path)[0]
            output_path = base_path + target_format
            
            # 保存图像
            success = cv2.imwrite(output_path, image)
            
            if success:
                return ProcessingResult(
                    task_id=task.task_id,
                    file_path=output_path,
                    success=True,
                    message=f"成功转换为 {target_format} 格式"
                )
            else:
                return ProcessingResult(
                    task_id=task.task_id,
                    file_path=input_path,
                    success=False,
                    message="图像保存失败"
                )
                
        except Exception as e:
            return ProcessingResult(
                task_id=task.task_id,
                file_path=task.file_path,
                success=False,
                message=f"处理失败: {str(e)}"
            )