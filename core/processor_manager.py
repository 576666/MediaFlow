#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
插件管理器
"""

import os
import importlib
from plugins.base_processor import BaseProcessor


class ProcessorManager:
    """管理所有处理器插件"""

    def __init__(self, plugin_dir='plugins'):
        self.plugin_dir = plugin_dir
        self.processors = {}
        self.load_processors()

    def load_processors(self):
        """加载所有可用的处理器插件"""
        if not os.path.exists(self.plugin_dir):
            return

        for filename in os.listdir(self.plugin_dir):
            if (filename.endswith('.py') and 
                filename != '__init__.py' and 
                filename != 'base_processor.py'):
                
                module_name = filename[:-3]  # 移除.py扩展名
                try:
                    # 动态导入模块
                    spec = importlib.util.spec_from_file_location(
                        module_name, 
                        os.path.join(self.plugin_dir, filename)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # 查找继承自BaseProcessor的类
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, BaseProcessor) and 
                            attr != BaseProcessor):
                            
                            processor_instance = attr()
                            self.processors[processor_instance.name] = processor_instance
                            break
                except Exception as e:
                    print(f"加载插件 {filename} 时出错: {str(e)}")

    def get_processor(self, name: str) -> BaseProcessor:
        """根据名称获取处理器实例"""
        return self.processors.get(name)

    def get_all_processors(self) -> dict:
        """获取所有处理器"""
        return self.processors.copy()

    def get_processor_names(self) -> list:
        """获取所有处理器名称列表"""
        return list(self.processors.keys())