#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批处理引擎
"""

from core.processor_manager import ProcessorManager


class BatchProcessor:
    """批处理引擎，负责协调和执行批量处理任务"""

    def __init__(self):
        self.processor_manager = ProcessorManager()

    def process_files(self, file_list: list, processor_name: str) -> dict:
        """
        使用指定处理器处理文件列表
        
        Args:
            file_list: 文件路径列表
            processor_name: 处理器名称
            
        Returns:
            处理结果字典
        """
        processor = self.processor_manager.get_processor(processor_name)
        if not processor:
            return {
                'success': [],
                'failure': file_list,
                'error': f'找不到处理器: {processor_name}'
            }

        return processor.batch_process(file_list)

    def get_available_processors(self) -> list:
        """获取所有可用的处理器名称"""
        return self.processor_manager.get_processor_names()