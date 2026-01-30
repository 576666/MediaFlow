"""
插件管理器
"""
import os
import importlib.util
from typing import Dict, Type, List
from plugins.base_processor import BaseProcessor


class ProcessorManager:
    """管理所有处理器插件"""
    
    def __init__(self, plugin_dir='plugins'):
        self.plugin_dir = plugin_dir
        self.processors: Dict[str, Type[BaseProcessor]] = {}
        self.instances: Dict[str, BaseProcessor] = {}
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
                            
                            # 创建实例并注册
                            processor_instance = attr()
                            self.processors[processor_instance.name] = attr
                            self.instances[processor_instance.name] = processor_instance
                            
                except Exception as e:
                    print(f"加载插件 {filename} 时出错: {str(e)}")
    
    def get_processor(self, name: str) -> BaseProcessor:
        """获取指定名称的处理器实例"""
        return self.instances.get(name)
    
    def get_processor_names(self) -> List[str]:
        """获取所有可用处理器名称"""
        return list(self.instances.keys())
    
    def register_processor(self, processor_class: Type[BaseProcessor]):
        """注册新的处理器类"""
        instance = processor_class()
        self.processors[instance.name] = processor_class
        self.instances[instance.name] = instance
    
    def create_task(self, processor_name: str, file_path: str, config: dict) -> object:
        """为指定处理器创建任务"""
        processor = self.get_processor(processor_name)
        if processor:
            return processor.create_task(file_path, config)
        return None