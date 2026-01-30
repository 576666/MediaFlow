#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
示例处理器插件 - 将文件扩展名转换为大写
"""

import os
import re
from typing import List, Dict, Any
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox
from plugins.base_processor import BaseProcessor, MediaTask, ProcessingResult


class ExtensionUpperProcessor(BaseProcessor):
    """将文件扩展名转换为大写的处理器"""

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "扩展名大写"

    @property
    def description(self) -> str:
        return "将选中文件的扩展名转换为大写形式"

    @property
    def supported_formats(self) -> List[str]:
        """支持的文件格式"""
        return ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.dng', '.nef', '.arw', '.xef', '.cr2']

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
        
        label = QLabel("扩展名大写处理配置")
        layout.addWidget(label)
        
        # 添加一些配置选项
        self.recursive_check = QCheckBox("递归处理子文件夹")
        self.recursive_check.setChecked(True)
        layout.addWidget(self.recursive_check)
        
        self.backup_check = QCheckBox("创建备份文件")
        self.backup_check.setChecked(False)
        layout.addWidget(self.backup_check)
        
        layout.addStretch()
        return widget

    def _process_impl(self, task: MediaTask) -> ProcessingResult:
        """具体的处理实现"""
        try:
            file_path = task.file_path
            config = task.config
            
            if not os.path.exists(file_path):
                return ProcessingResult(
                    task_id=task.task_id,
                    file_path=file_path,
                    success=False,
                    message="文件不存在"
                )
            
            # 检查是否为文件
            if not os.path.isfile(file_path):
                return ProcessingResult(
                    task_id=task.task_id,
                    file_path=file_path,
                    success=False,
                    message="不是文件"
                )
            
            # 检查文件扩展名
            base_name, ext = os.path.splitext(file_path)
            if ext and ext.islower():
                new_ext = ext.upper()
                new_file_path = base_name + new_ext
                
                # 检查目标文件是否已存在
                if os.path.exists(new_file_path):
                    return ProcessingResult(
                        task_id=task.task_id,
                        file_path=file_path,
                        success=False,
                        message="目标文件已存在"
                    )
                
                # 执行重命名
                os.rename(file_path, new_file_path)
                
                return ProcessingResult(
                    task_id=task.task_id,
                    file_path=file_path,
                    success=True,
                    message=f"扩展名已转换为大写: {ext} -> {new_ext}",
                    metadata={
                        'original_path': file_path,
                        'new_path': new_file_path,
                        'original_extension': ext,
                        'new_extension': new_ext
                    }
                )
            else:
                return ProcessingResult(
                    task_id=task.task_id,
                    file_path=file_path,
                    success=True,
                    message="扩展名已是大写，无需处理"
                )
                
        except Exception as e:
            return ProcessingResult(
                task_id=task.task_id,
                file_path=task.file_path,
                success=False,
                message=f"处理失败: {str(e)}"
            )

    # 保持向后兼容的方法
    def process(self, file_path: str) -> bool:
        """
        将单个文件的扩展名改为大写（向后兼容）
        
        Args:
            file_path: 文件路径
            
        Returns:
            处理成功返回True，否则返回False
        """
        task = self.create_task(file_path, {})
        result = self._process_impl(task)
        return result.success
