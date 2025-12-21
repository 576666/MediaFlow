#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
照片后缀剪切处理器插件
"""

import os
import re
from plugins.base_processor import BaseProcessor


class PhotoSuffixCutterProcessor(BaseProcessor):
    """照片后缀剪切处理器"""

    def __init__(self):
        super().__init__()
        # 默认配置选项
        self.options = {
            'rename_jpg_files': True,          # 是否重命名JPG文件
            'file_prefix': '_DSC',             # 文件名前缀（如_DSC、_Z8等）
            'dsc_suffix_number': 1,            # 文件后缀编号（如-1、-2等）
            'process_denoised_jpg': True,      # 是否处理降噪JPG文件
            'delete_denoised_dng': True,       # 是否删除降噪DNG文件
            'remove_date_prefix': True,        # 是否移除日期前缀
            'date_prefix_patterns': [          # 日期前缀模式列表
                r'^\d{4}-\d{2}-\d{2}-',        # YYYY-MM-DD-
                r'^\d{8}\+',                   # YYYYMMDD+
            ],
            'file_extensions': ['.jpg', '.JPG', '.dng', '.DNG'],  # 处理的文件扩展名
        }

    @property
    def name(self) -> str:
        return "照片后缀剪切"

    @property
    def description(self) -> str:
        return "批量删除文件名的后缀，可选择性处理不同类别的文件"

    def set_options(self, options: dict):
        """
        设置处理选项
        
        Args:
            options: 包含处理选项的字典
        """
        self.options.update(options)

    def process(self, file_path: str) -> bool:
        """
        处理单个文件（此处理器主要针对整个文件夹操作，单个文件处理无意义）
        
        Args:
            file_path: 文件路径
            
        Returns:
            处理成功返回True，否则返回False
        """
        # 单个文件处理无意义，直接返回True
        return True

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
        
        # 获取所有文件所在的目录
        folders = set()
        for file_path in file_list:
            folder_path = os.path.dirname(file_path)
            folders.add(folder_path)
        
        # 对每个目录执行操作
        for folder_path in folders:
            try:
                self._process_folder(folder_path)
                success_list.append(folder_path)
            except Exception as e:
                print(f"处理文件夹 {folder_path} 时出错: {str(e)}")
                failure_list.append(folder_path)

        return {
            'success': success_list,
            'failure': failure_list
        }

    def _process_folder(self, folder_path: str):
        """
        处理单个文件夹
        
        Args:
            folder_path: 文件夹路径
        """
        if self.options['rename_jpg_files']:
            self._rename_jpg_files(folder_path)
            
        if self.options['process_denoised_jpg']:
            self._process_denoised_jpg(folder_path)
            
        if self.options['delete_denoised_dng']:
            self._delete_denoised_dng(folder_path)
            
        if self.options['remove_date_prefix']:
            self._remove_date_prefix(folder_path)

    def _rename_jpg_files(self, folder_path: str):
        """重命名JPG文件（支持多种前缀）"""
        suffix_number = self.options['dsc_suffix_number']
        file_prefix = self.options.get('file_prefix', '_DSC')
        # 获取配置的文件扩展名
        extensions = self.options.get('file_extensions', ['.jpg', '.JPG', '.dng', '.DNG'])
        
        for filename in os.listdir(folder_path):
            # 检查文件扩展名是否在配置的扩展名列表中（不区分大小写）
            file_ext = os.path.splitext(filename)[1]
            if file_ext.lower() not in [ext.lower() for ext in extensions]:
                continue
                
            # 使用配置的前缀，匹配如 _DSC0001-2.ext 或 _Z80001-3.ext 等模式
            # 注意：前缀可能包含特殊字符，需要转义
            escaped_prefix = re.escape(file_prefix)
            escaped_ext = re.escape(file_ext)
            # 匹配模式：前缀 + 4位数字 + '-' + 数字 + 扩展名
            pattern = r'(' + escaped_prefix + r'\d{4})-(\d+)' + escaped_ext + r'$'
            match = re.match(pattern, filename, re.IGNORECASE)
            if match:
                prefix_number = match.group(1)  # 例如 _DSC0001
                # 使用配置的后缀编号，保持原扩展名
                new_base = f"{prefix_number}-{suffix_number}"
                new_filename = new_base + file_ext
                old_file = os.path.join(folder_path, filename)
                new_file = os.path.join(folder_path, new_filename)
                
                # 检查目标文件是否已存在
                if not os.path.exists(new_file):
                    os.rename(old_file, new_file)
                    print(f'重命名文件: {filename} -> {new_filename}')
                else:
                    print(f'跳过重命名（目标文件已存在）: {filename}')

    def _process_denoised_jpg(self, folder_path: str):
        """处理降噪JPG文件"""
        suffix_number = self.options['dsc_suffix_number']
        # 获取配置的文件扩展名
        extensions = self.options.get('file_extensions', ['.jpg', '.JPG', '.dng', '.DNG'])
        
        for filename in os.listdir(folder_path):
            # 检查文件扩展名是否在配置的扩展名列表中
            file_ext = os.path.splitext(filename)[1]
            if file_ext.lower() not in [ext.lower() for ext in extensions]:
                continue
                
            # 匹配降噪JPG文件，如 _DSC0001-已增强-降噪.jpg 或 _DSC0001-已增强-降噪-3.jpg
            match = re.match(r'(_DSC\d{4})-已增强-降噪(-(\d+))?\.jpg$', filename, re.IGNORECASE)
            if match:
                dsc_number = match.group(1)
                # 使用配置的后缀编号，保持原扩展名
                new_filename = f"{dsc_number}-{suffix_number}{file_ext}"
                old_file = os.path.join(folder_path, filename)
                new_file = os.path.join(folder_path, new_filename)
                
                # 检查目标文件是否已存在
                if not os.path.exists(new_file):
                    os.rename(old_file, new_file)
                    print(f'处理降噪JPG: {filename} -> {new_filename}')
                else:
                    print(f'跳过降噪JPG（目标文件已存在）: {filename}')

    def _delete_denoised_dng(self, folder_path: str):
        """删除降噪DNG文件"""
        # 获取配置的文件扩展名
        extensions = self.options.get('file_extensions', ['.jpg', '.JPG', '.dng', '.DNG'])
        
        for filename in os.listdir(folder_path):
            # 检查文件扩展名是否在配置的扩展名列表中（不区分大小写）
            file_ext = os.path.splitext(filename)[1]
            if file_ext.lower() not in [ext.lower() for ext in extensions]:
                continue
                
            match = re.match(r'(_DSC\d{4})-已增强-降噪\.dng$', filename, re.IGNORECASE)
            if match:
                file_to_delete = os.path.join(folder_path, filename)
                try:
                    os.remove(file_to_delete)
                    print(f'Deleted: {filename}')
                except Exception as e:
                    print(f'Failed to delete {filename}: {str(e)}')

    def _remove_date_prefix(self, folder_path: str):
        """移除日期前缀"""
        # 获取配置的文件扩展名
        extensions = self.options.get('file_extensions', ['.jpg', '.JPG', '.dng', '.DNG'])
        
        for filename in os.listdir(folder_path):
            # 检查文件扩展名是否在配置的扩展名列表中（不区分大小写）
            file_ext = os.path.splitext(filename)[1]
            if file_ext.lower() not in [ext.lower() for ext in extensions]:
                continue
                
            for pattern in self.options['date_prefix_patterns']:
                match = re.match(pattern, filename)
                if match:
                    # 计算匹配的日期前缀长度
                    match_end = match.end()
                    new_name = filename[match_end:]  # 移除日期前缀
                    old_path = os.path.join(folder_path, filename)
                    new_path = os.path.join(folder_path, new_name)

                    # 检查目标文件是否已存在
                    if not os.path.exists(new_path):
                        # 执行重命名
                        os.rename(old_path, new_path)
                        print(f'移除日期前缀: {filename} -> {new_name}')
                    else:
                        print(f'跳过日期前缀（目标文件已存在）: {filename}')
                    break  # 匹配到一个模式就处理，不再尝试其他模式
