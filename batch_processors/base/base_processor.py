# -*- coding: utf-8 -*-
"""
基类批量处理器

所有批量处理器都继承自此类，提供以下功能：
- 与MediaFlow配置系统集成
- 路径验证
- 日志记录
- 常见文件操作
"""

import os
import re
import logging
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path


class BaseBatchProcessor:
    """
    基类批量处理器，为所有处理器提供通用功能。
    
    所有特定处理器（视频、照片、混合）都应继承此类并实现其特定的处理逻辑。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化批量处理器。
        
        参数:
            config: 可选的配置字典。如果未提供，
                   将使用MediaFlow的app_config。
        """
        self.config = config or {}
        self._setup_logging()
        
    def _setup_logging(self):
        """设置处理器的日志记录。"""
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def validate_path(self, path: str) -> bool:
        """
        验证提供的路径存在且为目录。
        
        参数:
            path: 要验证的路径
            
        返回:
            如果路径存在且为目录返回True，否则返回False
        """
        if not path:
            self.logger.error("路径不能为空")
            return False
            
        if not os.path.exists(path):
            self.logger.error(f"路径不存在: {path}")
            return False
            
        if not os.path.isdir(path):
            self.logger.error(f"路径不是目录: {path}")
            return False
            
        return True
    
    def get_output_path(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        获取输出路径，如果未提供则使用配置。
        
        参数:
            input_path: 基于输入路径
            output_path: 显式输出路径，或None使用配置
            
        返回:
            输出路径字符串
        """
        if output_path:
            return output_path
            
        # 使用配置默认或创建'processed'子文件夹
        config_output = self.config.get('paths.default_output', '')
        if config_output:
            if '{input}' in config_output:
                return config_output.replace('{input}', input_path)
            return config_output
            
        # 默认：创建'processed'子文件夹
        return os.path.join(input_path, 'processed')
    
    def scan_files(self, 
                 folder_path: str, 
                 extensions: Optional[List[str]] = None,
                 recursive: bool = True) -> List[str]:
        """
        扫描文件夹中具有指定扩展名的文件。
        
        参数:
            folder_path: 要扫描的文件夹
            extensions: 要过滤的扩展名列表（例如 ['.jpg', '.png']）
                      如果为None，返回所有文件
            recursive: 是否递归扫描
            
        返回:
            文件路径列表
        """
        if not self.validate_path(folder_path):
            return []
            
        files = []
        walk_func = os.walk if recursive else lambda p: [(p, [], os.listdir(p))]
        
        for root, _, filenames in walk_func(folder_path):
            for filename in filenames:
                if extensions:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext not in [e.lower() for e in extensions]:
                        continue
                files.append(os.path.join(root, filename))
                
        return files
    
    def get_files_by_pattern(self, 
                          folder_path: str, 
                          pattern: str,
                          recursive: bool = True) -> List[str]:
        """
        获取与正则表达式匹配的文件。
        
        参数:
            folder_path: 要扫描的文件夹
            pattern: 要匹配文件名的正则表达式模式
            recursive: 是否递归扫描
            
        返回:
            匹配的文件路径列表
        """
        if not self.validate_path(folder_path):
            return []
            
        regex = re.compile(pattern, re.IGNORECASE)
        files = []
        
        walk_func = os.walk if recursive else lambda p: [(p, [], os.listdir(p))]
        
        for root, _, filenames in walk_func(folder_path):
            for filename in filenames:
                if regex.match(filename):
                    files.append(os.path.join(root, filename))
                    
        return files
    
    def process_with_progress(self, 
                               files: List[str], 
                               process_func,
                               **kwargs) -> Dict[str, Any]:
        """
        使用进度跟踪处理文件。
        
        参数:
            files: 要处理的文件列表
            process_func: 要应用于每个文件的函数
            **kwargs: 要传递给process_func的其他参数
            
        返回:
            包含'success'和'failure'列表的字典
        """
        results = {'success': [], 'failure': []}
        total = len(files)
        
        for i, file_path in enumerate(files, 1):
            try:
                self.logger.info(f"[{i}/{total}] 处理中: {os.path.basename(file_path)}")
                process_func(file_path, **kwargs)
                results['success'].append(file_path)
            except Exception as e:
                self.logger.error(f"处理失败 {file_path}: {e}")
                results['failure'].append(file_path)
                
        self.logger.info(f"完成: {len(results['success'])}/{total} 个文件")
        return results
    
    def rename_file(self, old_path: str, new_name: str) -> bool:
        """
        重命名单个文件。
        
        参数:
            old_path: 当前文件路径
            new_name: 新文件名（不是完整路径）
            
        返回:
            如果成功返回True，否则返回False
        """
        try:
            directory = os.path.dirname(old_path)
            new_path = os.path.join(directory, new_name)
            
            # 处理名称冲突
            if os.path.exists(new_path):
                base, ext = os.path.splitext(new_name)
                counter = 1
                while os.path.exists(new_path):
                    new_name = f"{base} ({counter}){ext}"
                    new_path = os.path.join(directory, new_name)
                    counter += 1
                    
            os.rename(old_path, new_path)
            self.logger.info(f"已重命名: {os.path.basename(old_path)} -> {new_name}")
            return True
        except Exception as e:
            self.logger.error(f"重命名失败 {old_path}: {e}")
            return False
    
    def batch_rename(self, 
                   files: List[str], 
                   name_func) -> Dict[str, Any]:
        """
        使用命名函数批量重命名文件。
        
        参数:
            files: 文件路径列表
            name_func: 接受(索引, 原文件名)并返回新名称的函数
            
        返回:
            包含'success'和'failure'列表的字典
        """
        results = {'success': [], 'failure': []}
        
        for i, file_path in enumerate(files):
            try:
                original_name = os.path.basename(file_path)
                new_name = name_func(i, original_name)
                
                directory = os.path.dirname(file_path)
                new_path = os.path.join(directory, new_name)
                
                # 处理冲突
                if os.path.exists(new_path) and new_path != file_path:
                    base, ext = os.path.splitext(new_name)
                    counter = 1
                    while os.path.exists(new_path):
                        new_name = f"{base} ({counter}){ext}"
                        new_path = os.path.join(directory, new_name)
                        counter += 1
                
                os.rename(file_path, new_path)
                results['success'].append((file_path, new_path))
            except Exception as e:
                self.logger.error(f"重命名失败 {file_path}: {e}")
                results['failure'].append(file_path)
                
        return results