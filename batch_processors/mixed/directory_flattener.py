# -*- coding: utf-8 -*-
"""
目录扁平化器

通过将所有文件移动到根级别来扁平化嵌套目录结构。
基于Tool文件夹中的flatten_directory.py脚本。
"""

import os
import shutil
from typing import Optional, Dict, Any

from .mixed_processor import MixedBatchProcessor


class DirectoryFlattener(MixedBatchProcessor):
    """
    扁平化嵌套目录结构。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化目录扁平化器。
        
        参数:
            config: 可选的配置字典
        """
        super().__init__(config)
    
    def flatten(self, 
               folder_path: str,
               confirm: bool = True) -> Dict[str, Any]:
        """
        扁平化目录结构，将所有文件移动到根级别。
        
        参数:
            folder_path: 要扁平化的文件夹
            confirm: 是否需要确认
            
        返回:
            包含'success'和'failure'列表的字典
        """
        if not self.validate_path(folder_path):
            return {'success': [], 'failure': [], 'error': '无效路径'}
        
        # 警告
        self.logger.warning(f"这将扁平化目录: {folder_path}")
        self.logger.warning("所有子目录将被删除!")
        
        if confirm:
            response = input("继续? (y/n): ").lower().strip()
            if response != 'y':
                self.logger.info("操作已取消")
                return {'success': [], 'failure': [], 'error': '已取消'}
        
        # 阶段1：收集所有文件路径（排除根目录中的文件）
        files_to_move = []
        for root, dirs, files in os.walk(folder_path):
            if root == folder_path:
                continue  # 跳过根目录文件
            for filename in files:
                src_path = os.path.join(root, filename)
                files_to_move.append(src_path)
        
        self.logger.info(f"找到 {len(files_to_move)} 个文件待移动")
        
        results = {'success': [], 'failure': []}
        
        # 阶段2：移动文件并处理冲突
        for src_path in files_to_move:
            try:
                filename = os.path.basename(src_path)
                dest_path = os.path.join(folder_path, filename)
                
                # 处理文件名冲突
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        new_name = f"{base} ({counter}){ext}"
                        dest_path = os.path.join(folder_path, new_name)
                        counter += 1
                
                shutil.move(src_path, dest_path)
                self.logger.info(f"已移动: {filename}")
                results['success'].append(src_path)
                
            except Exception as e:
                self.logger.error(f"移动失败 {src_path}: {e}")
                results['failure'].append(src_path)
        
        # 阶段3：删除空子目录
        for root, dirs, _ in os.walk(folder_path, topdown=False):
            if root == folder_path:
                continue
            try:
                os.rmdir(root)
                self.logger.info(f"已删除空目录: {root}")
            except OSError as e:
                self.logger.debug(f"无法删除目录 {root}: {e}")
        
        self.logger.info(f"扁平化完成: {len(results['success'])} 个文件已移动")
        return results
    
    def copy_and_flatten(self, 
                      source_folder: str,
                      dest_folder: str,
                      confirm: bool = True) -> Dict[str, Any]:
        """
        将文件从源复制到目标并扁平化。
        
        参数:
            source_folder: 源文件夹
            dest_folder: 目标文件夹
            confirm: 是否需要确认
            
        返回:
            包含结果的字典
        """
        if not self.validate_path(source_folder):
            return {'success': [], 'failure': [], 'error': '无效源路径'}
        
        if confirm:
            self.logger.warning(f"这将从 {source_folder} 复制文件到 {dest_folder}")
            response = input("继续? (y/n): ").lower().strip()
            if response != 'y':
                self.logger.info("操作已取消")
                return {'success': [], 'failure': [], 'error': '已取消'}
        
        os.makedirs(dest_folder, exist_ok=True)
        
        # 收集所有文件路径
        files_to_copy = []
        for root, dirs, files in os.walk(source_folder):
            for filename in files:
                src_path = os.path.join(root, filename)
                files_to_copy.append(src_path)
        
        results = {'success': [], 'failure': []}
        
        # 复制文件
        for src_path in files_to_copy:
            try:
                filename = os.path.basename(src_path)
                dest_path = os.path.join(dest_folder, filename)
                
                # 处理冲突
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        new_name = f"{base} ({counter}){ext}"
                        dest_path = os.path.join(dest_folder, new_name)
                        counter += 1
                
                shutil.copy2(src_path, dest_path)
                self.logger.info(f"已复制: {filename}")
                results['success'].append(src_path)
                
            except Exception as e:
                self.logger.error(f"复制失败 {src_path}: {e}")
                results['failure'].append(src_path)
        
        self.logger.info(f"复制完成: {len(results['success'])} 个文件已复制")
        return results


# 便利函数
def flatten_directory(folder_path: str, confirm: bool = True) -> Dict[str, Any]:
    """
    便利函数，扁平化目录。
    
    参数:
        folder_path: 要扁平化的文件夹
        confirm: 是否需要确认
        
    返回:
        包含结果的字典
    """
    flattener = DirectoryFlattener()
    return flattener.flatten(folder_path, confirm)