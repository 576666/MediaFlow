#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
处理插件基类
"""

from abc import ABC, abstractmethod


class BaseProcessor(ABC):
    """
    处理器插件基类
    所有具体处理插件都需要继承此类并实现相应方法
    """

    def __init__(self):
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """返回处理器名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """返回处理器描述"""
        pass

    @abstractmethod
    def process(self, file_path: str) -> bool:
        """
        处理单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            处理成功返回True，否则返回False
        """
        pass

    def batch_process(self, file_list: list) -> dict:
        """
        批量处理文件
        
        Args:
            file_list: 文件路径列表
            
        Returns:
            处理结果字典，包含成功和失败的文件列表
        """
        success_list = []
        failure_list = []

        for file_path in file_list:
            try:
                if self.process(file_path):
                    success_list.append(file_path)
                else:
                    failure_list.append(file_path)
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {str(e)}")
                failure_list.append(file_path)

        return {
            'success': success_list,
            'failure': failure_list
        }