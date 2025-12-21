#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
示例处理器插件 - 将文件扩展名转换为大写
"""

import os
from plugins.base_processor import BaseProcessor


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

    def process(self, file_path: str) -> bool:
        """
        将单个文件的扩展名改为大写
        
        Args:
            file_path: 文件路径
            
        Returns:
            处理成功返回True，否则返回False
        """
        try:
            if not os.path.exists(file_path):
                return False
                
            base_name, ext = os.path.splitext(file_path)
            if ext and ext.islower():
                new_ext = ext.upper()
                new_file_path = base_name + new_ext
                os.rename(file_path, new_file_path)
            return True
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
            return False