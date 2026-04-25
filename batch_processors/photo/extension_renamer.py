# -*- coding: utf-8 -*-
"""
照片扩展名重命名器

批量重命名照片文件扩展名为大写或小写。
基于Tool文件夹中的jpeg2JPG.py脚本。
"""

import os
import re
from typing import Optional, Dict, Any

from .photo_processor import PhotoBatchProcessor


class PhotoExtensionRenamer(PhotoBatchProcessor):
    """
    重命名照片文件扩展名（例如 jpg -> JPG, JPEG -> jpg）。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化照片扩展名重命名器。
        
        参数:
            config: 可选的配置字典
        """
        super().__init__(config)
    
    def rename_extensions(self, 
                          folder_path: str, 
                          from_ext: str, 
                          to_ext: str,
                          recursive: bool = True) -> Dict[str, Any]:
        """
        批量重命名照片文件扩展名。
        
        参数:
            folder_path: 包含照片的文件夹
            from_ext: 要更改的扩展名（例如 'jpg'）
            to_ext: 要更改到的扩展名（例如 'JPG'）
            recursive: 是否扫描子文件夹
            
        返回:
            包含'success'和'failure'列表的字典
        """
        if not self.validate_path(folder_path):
            return {'success': [], 'failure': [], 'error': '无效路径'}
        
        # 标准化扩展名
        from_ext = from_ext.lower()
        if not from_ext.startswith('.'):
            from_ext = '.' + from_ext
        if not to_ext.startswith('.'):
            to_ext = '.' + to_ext
            
        results = {'success': [], 'failure': []}
        
        files = self.scan_photos(folder_path, [from_ext], recursive)
        
        for file_path in files:
            try:
                directory = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                
                name_without_ext = os.path.splitext(filename)[0]
                file_ext = os.path.splitext(filename)[1].lower()
                
                if file_ext == from_ext:
                    new_filename = name_without_ext + to_ext
                    new_path = os.path.join(directory, new_filename)
                    
                    if os.path.exists(new_path):
                        self.logger.warning(f"目标已存在，跳过: {new_filename}")
                        results['failure'].append(file_path)
                        continue
                    
                    os.rename(file_path, new_path)
                    self.logger.info(f"已重命名: {filename} -> {new_filename}")
                    results['success'].append(file_path)
                    
            except Exception as e:
                self.logger.error(f"重命名失败 {file_path}: {e}")
                results['failure'].append(file_path)
                
        self.logger.info(f"完成: {len(results['success'])} 个文件已重命名")
        return results
    
    def to_uppercase(self, folder_path: str, recursive: bool = True) -> Dict[str, Any]:
        """
        将所有照片扩展名改为大写。
        
        参数:
            folder_path: 包含照片的文件夹
            recursive: 是否扫描子文件夹
            
        返回:
            包含结果的字典
        """
        return self.rename_extensions(folder_path, 'jpg', 'JPG', recursive)
    
    def to_lowercase(self, folder_path: str, recursive: bool = True) -> Dict[str, Any]:
        """
        将所有照片扩展名改为小写。
        
        参数:
            folder_path: 包含照片的文件夹
            recursive: 是否扫描子文件夹
            
        返回:
            包含结果的字典
        """
        return self.rename_extensions(folder_path, 'JPG', 'jpg', recursive)
    
    def normalize_jpeg_extensions(self, folder_path: str, recursive: bool = True) -> Dict[str, Any]:
        """
        将所有JPEG扩展名规范化为.JPG。
        
        参数:
            folder_path: 包含照片的文件夹
            recursive: 是否扫描子文件夹
            
        返回:
            包含结果的字典
        """
        if not self.validate_path(folder_path):
            return {'success': [], 'failure': []}
            
        results = {'success': [], 'failure': []}
        
        # 转换.jpeg到.JPG
        files = self.scan_files(folder_path, ['.jpeg'], recursive)
        
        for file_path in files:
            try:
                directory = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                new_filename = os.path.splitext(filename)[0] + '.JPG'
                new_path = os.path.join(directory, new_filename)
                
                if os.path.exists(new_path):
                    results['failure'].append(file_path)
                    continue
                    
                os.rename(file_path, new_path)
                self.logger.info(f"已重命名: {filename} -> {new_filename}")
                results['success'].append(file_path)
            except Exception as e:
                self.logger.error(f"失败: {e}")
                results['failure'].append(file_path)
        
        # 转换.jpg到.JPG
        files = self.scan_files(folder_path, ['.jpg'], recursive)
        
        for file_path in files:
            try:
                directory = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                new_filename = os.path.splitext(filename)[0] + '.JPG'
                new_path = os.path.join(directory, new_filename)
                
                if os.path.exists(new_path):
                    results['failure'].append(file_path)
                    continue
                    
                os.rename(file_path, new_path)
                self.logger.info(f"已重命名: {filename} -> {new_filename}")
                results['success'].append(file_path)
            except Exception as e:
                self.logger.error(f"失败: {e}")
                results['failure'].append(file_path)
                
        return results


# 便利函数
def rename_photo_extensions(folder_path: str, from_ext: str, to_ext: str) -> Dict[str, Any]:
    """
    便利函数，重命名照片扩展名。
    
    参数:
        folder_path: 包含照片的文件夹
        from_ext: 要更改的扩展名
        to_ext: 要更改到的扩展名
        
    返回:
        包含结果的字典
    """
    renamer = PhotoExtensionRenamer()
    return renamer.rename_extensions(folder_path, from_ext, to_ext)