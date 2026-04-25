# -*- coding: utf-8 -*-
"""
视频扩展名重命名器

批量重命名视频文件扩展名为大写或小写。
基于Tool文件夹中的mp4_to_MP4.py脚本。
"""

import os
from typing import Optional, List, Dict, Any

from .video_processor import VideoBatchProcessor


class VideoExtensionRenamer(VideoBatchProcessor):
    """
    重命名视频文件扩展名（例如 mp4 -> MP4, MOV -> mov）。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化视频扩展名重命名器。
        
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
        批量重命名视频文件扩展名。
        
        参数:
            folder_path: 包含视频的文件夹
            from_ext: 要更改的扩展名（例如 'mp4'）
            to_ext: 要更改到的扩展名（例如 'MP4'）
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
        
        files = self.scan_videos(folder_path, [from_ext], recursive)
        
        for file_path in files:
            try:
                directory = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                
                # 检查文件是否具有源扩展名
                name_without_ext = os.path.splitext(filename)[0]
                file_ext = os.path.splitext(filename)[1].lower()
                
                if file_ext == from_ext:
                    new_filename = name_without_ext + to_ext
                    new_path = os.path.join(directory, new_filename)
                    
                    # 处理名称冲突
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
                
        self.logger.info(f"完成: {len(results['success'])}/{len(files)} 个文件已重命名")
        return results
    
    def to_uppercase(self, folder_path: str, recursive: bool = True) -> Dict[str, Any]:
        """
        将所有视频扩展名改为大写。
        
        参数:
            folder_path: 包含视频的文件夹
            recursive: 是否扫描子文件夹
            
        返回:
            包含结果的字典
        """
        if not self.validate_path(folder_path):
            return {'success': [], 'failure': []}
            
        results = {'success': [], 'failure': []}
        
        for root, _, files in os.walk(folder_path) if recursive else [(folder_path, [], os.listdir(folder_path))]:
            for filename in files:
                file_path = os.path.join(root, filename)
                name, ext = os.path.splitext(filename)
                
                if ext and ext != ext.upper():
                    new_path = os.path.join(root, name + ext.upper())
                    
                    try:
                        os.rename(file_path, new_path)
                        self.logger.info(f"已改为大写: {filename} -> {name + ext.upper()}")
                        results['success'].append(file_path)
                    except Exception as e:
                        self.logger.error(f"失败: {filename}: {e}")
                        results['failure'].append(file_path)
                        
        return results
    
    def to_lowercase(self, folder_path: str, recursive: bool = True) -> Dict[str, Any]:
        """
        将所有视频扩展名改为小写。
        
        参数:
            folder_path: 包含视频的文件夹
            recursive: 是否扫描子文件夹
            
        返回:
            包含结果的字典
        """
        if not self.validate_path(folder_path):
            return {'success': [], 'failure': []}
            
        results = {'success': [], 'failure': []}
        
        # 获取具有大写扩展名的视频文件
        videos = self.scan_videos(folder_path, recursive=recursive)
        
        for file_path in videos:
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            
            if ext and ext == ext.upper():
                new_ext = ext.lower()
                new_path = os.path.join(os.path.dirname(file_path), name + new_ext)
                
                try:
                    os.rename(file_path, new_path)
                    self.logger.info(f"已改为小写: {filename} -> {name + new_ext}")
                    results['success'].append(file_path)
                except Exception as e:
                    self.logger.error(f"失败: {filename}: {e}")
                    results['failure'].append(file_path)
                    
        return results


# 简单的便利函数
def rename_video_extensions(folder_path: str, from_ext: str, to_ext: str) -> Dict[str, Any]:
    """
    便利函数，重命名视频扩展名。
    
    参数:
        folder_path: 包含视频的文件夹
        from_ext: 要更改的扩展名（例如 'mp4'）
        to_ext: 要更改到的扩展名（例如 'MP4'）
        
    返回:
        包含结果的字典
    """
    renamer = VideoExtensionRenamer()
    return renamer.rename_extensions(folder_path, from_ext, to_ext)