#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
照片后缀剪切处理器插件
"""

import os
import re
import uuid
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QLineEdit, QSpinBox, QFormLayout
from plugins.base_processor import BaseProcessor, MediaTask, ProcessingResult


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

    @property
    def supported_formats(self) -> List[str]:
        """支持的文件格式"""
        return ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.dng', '.nef', '.arw', '.xef', '.cr2']

    def create_task(self, file_path: str, config: Dict[str, Any]) -> MediaTask:
        """创建处理任务"""
        return MediaTask(
            file_path=file_path,
            config=config,
            task_id=str(uuid.uuid4())
        )

    def get_config_widget(self) -> QWidget:
        """返回配置UI控件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("照片后缀剪切配置")
        layout.addWidget(label)
        
        # 创建表单布局用于配置选项
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        # 文件前缀配置
        self.file_prefix_edit = QLineEdit(self.options['file_prefix'])
        form_layout.addRow("文件前缀:", self.file_prefix_edit)
        
        # 后缀编号配置
        self.suffix_spin = QSpinBox()
        self.suffix_spin.setRange(1, 999)
        self.suffix_spin.setValue(self.options['dsc_suffix_number'])
        form_layout.addRow("后缀编号:", self.suffix_spin)
        
        # 复选框配置
        self.rename_jpg_check = QCheckBox("重命名JPG文件")
        self.rename_jpg_check.setChecked(self.options['rename_jpg_files'])
        form_layout.addRow("", self.rename_jpg_check)
        
        self.denoised_jpg_check = QCheckBox("处理降噪JPG文件")
        self.denoised_jpg_check.setChecked(self.options['process_denoised_jpg'])
        form_layout.addRow("", self.denoised_jpg_check)
        
        self.delete_dng_check = QCheckBox("删除降噪DNG文件")
        self.delete_dng_check.setChecked(self.options['delete_denoised_dng'])
        form_layout.addRow("", self.delete_dng_check)
        
        self.remove_date_check = QCheckBox("移除日期前缀")
        self.remove_date_check.setChecked(self.options['remove_date_prefix'])
        form_layout.addRow("", self.remove_date_check)
        
        layout.addWidget(form_widget)
        layout.addStretch()
        return widget

    def _process_impl(self, task: MediaTask) -> ProcessingResult:
        """
        具体的处理实现
        注意：此处理器主要针对文件夹操作，单个文件处理可能无意义
        """
        try:
            file_path = task.file_path
            config = task.config
            
            # 合并配置：任务配置覆盖默认配置
            options = self.options.copy()
            options.update(config)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return ProcessingResult(
                    task_id=task.task_id,
                    file_path=file_path,
                    success=False,
                    message="文件不存在"
                )
            
            # 如果是文件，则处理单个文件
            if os.path.isfile(file_path):
                success = self._process_single_file(file_path, options)
                if success:
                    return ProcessingResult(
                        task_id=task.task_id,
                        file_path=file_path,
                        success=True,
                        message="文件处理完成"
                    )
                else:
                    return ProcessingResult(
                        task_id=task.task_id,
                        file_path=file_path,
                        success=False,
                        message="文件处理失败"
                    )
            # 如果是文件夹，则处理整个文件夹
            elif os.path.isdir(file_path):
                self._process_folder(file_path, options)
                return ProcessingResult(
                    task_id=task.task_id,
                    file_path=file_path,
                    success=True,
                    message="文件夹处理完成"
                )
            else:
                return ProcessingResult(
                    task_id=task.task_id,
                    file_path=file_path,
                    success=False,
                    message="不是文件或文件夹"
                )
                
        except Exception as e:
            return ProcessingResult(
                task_id=task.task_id,
                file_path=task.file_path,
                success=False,
                message=f"处理失败: {str(e)}"
            )

    # 保持向后兼容的方法
    def set_options(self, options: dict):
        """
        设置处理选项（向后兼容）
        
        Args:
            options: 包含处理选项的字典
        """
        self.options.update(options)

    def process(self, file_path: str) -> bool:
        """
        处理单个文件（向后兼容）
        
        Args:
            file_path: 文件路径
            
        Returns:
            处理成功返回True，否则返回False
        """
        task = self.create_task(file_path, {})
        result = self._process_impl(task)
        return result.success

    def batch_process(self, file_list: list) -> dict:
        """
        批量处理文件（向后兼容）
        
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
                self._process_folder(folder_path, self.options)
                success_list.append(folder_path)
            except Exception as e:
                print(f"处理文件夹 {folder_path} 时出错: {str(e)}")
                failure_list.append(folder_path)

        return {
            'success': success_list,
            'failure': failure_list
        }

    def _process_single_file(self, file_path: str, options: Dict[str, Any]) -> bool:
        """
        处理单个文件
        
        Args:
            file_path: 文件路径
            options: 处理选项
            
        Returns:
            处理成功返回True，否则返回False
        """
        try:
            # 获取文件扩展名
            filename = os.path.basename(file_path)
            folder_path = os.path.dirname(file_path)
            file_ext = os.path.splitext(filename)[1]
            
            # 检查文件扩展名是否在配置的扩展名列表中（不区分大小写）
            extensions = options.get('file_extensions', ['.jpg', '.JPG', '.dng', '.DNG'])
            if file_ext.lower() not in [ext.lower() for ext in extensions]:
                return False
            
            success = False
            
            # 1. 重命名JPG文件（如果启用）
            if options['rename_jpg_files']:
                result = self._rename_single_file(filename, folder_path, file_ext, options)
                if result:
                    success = True
            
            # 2. 处理降噪JPG文件（如果启用）
            if options['process_denoised_jpg'] and not success:
                result = self._process_denoised_single_file(filename, folder_path, file_ext, options)
                if result:
                    success = True
            
            # 3. 移除日期前缀（如果启用）
            if options['remove_date_prefix'] and not success:
                result = self._remove_date_prefix_single_file(filename, folder_path, file_ext, options)
                if result:
                    success = True
            
            # 4. 删除降噪DNG文件（如果启用）
            if options['delete_denoised_dng']:
                self._delete_denoised_single_file(filename, folder_path, file_ext, options)
            
            return success
            
        except Exception as e:
            print(f"处理单个文件 {file_path} 时出错: {str(e)}")
            return False
    
    def _process_folder(self, folder_path: str, options: Dict[str, Any] = None):
        """
        处理单个文件夹
        
        Args:
            folder_path: 文件夹路径
            options: 处理选项，如果为None则使用self.options
        """
        # 保存原来的选项
        original_options = self.options.copy()
        
        try:
            # 使用传入的选项或默认选项
            if options is not None:
                self.options = options
            
            if self.options['rename_jpg_files']:
                self._rename_jpg_files(folder_path)
                
            if self.options['process_denoised_jpg']:
                self._process_denoised_jpg(folder_path)
                
            if self.options['delete_denoised_dng']:
                self._delete_denoised_dng(folder_path)
                
            if self.options['remove_date_prefix']:
                self._remove_date_prefix(folder_path)
        
        finally:
            # 恢复原来的选项
            self.options = original_options

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

    def _rename_single_file(self, filename: str, folder_path: str, file_ext: str, options: Dict[str, Any]) -> bool:
        """重命名单个文件"""
        suffix_number = options['dsc_suffix_number']
        file_prefix = options.get('file_prefix', '_DSC')
        
        # 使用配置的前缀，匹配如 _DSC0001-2.ext 或 _Z80001-3.ext 等模式
        escaped_prefix = re.escape(file_prefix)
        escaped_ext = re.escape(file_ext)
        pattern = r'(' + escaped_prefix + r'\d{4})-(\d+)' + escaped_ext + r'$'
        match = re.match(pattern, filename, re.IGNORECASE)
        if match:
            prefix_number = match.group(1)
            new_base = f"{prefix_number}-{suffix_number}"
            new_filename = new_base + file_ext
            old_file = os.path.join(folder_path, filename)
            new_file = os.path.join(folder_path, new_filename)
            
            # 检查目标文件是否已存在
            if not os.path.exists(new_file):
                os.rename(old_file, new_file)
                print(f'重命名文件: {filename} -> {new_filename}')
                return True
            else:
                print(f'跳过重命名（目标文件已存在）: {filename}')
        return False

    def _process_denoised_single_file(self, filename: str, folder_path: str, file_ext: str, options: Dict[str, Any]) -> bool:
        """处理单个降噪JPG文件"""
        suffix_number = options['dsc_suffix_number']
        
        # 匹配降噪JPG文件，如 _DSC0001-已增强-降噪.jpg 或 _DSC0001-已增强-降噪-3.jpg
        match = re.match(r'(_DSC\d{4})-已增强-降噪(-(\d+))?\.jpg$', filename, re.IGNORECASE)
        if match:
            dsc_number = match.group(1)
            new_filename = f"{dsc_number}-{suffix_number}{file_ext}"
            old_file = os.path.join(folder_path, filename)
            new_file = os.path.join(folder_path, new_filename)
            
            # 检查目标文件是否已存在
            if not os.path.exists(new_file):
                os.rename(old_file, new_file)
                print(f'处理降噪JPG: {filename} -> {new_filename}')
                return True
            else:
                print(f'跳过降噪JPG（目标文件已存在）: {filename}')
        return False

    def _remove_date_prefix_single_file(self, filename: str, folder_path: str, file_ext: str, options: Dict[str, Any]) -> bool:
        """移除单个文件的日期前缀"""
        for pattern in options['date_prefix_patterns']:
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
                    return True
                else:
                    print(f'跳过日期前缀（目标文件已存在）: {filename}')
                break  # 匹配到一个模式就处理，不再尝试其他模式
        return False

    def _delete_denoised_single_file(self, filename: str, folder_path: str, file_ext: str, options: Dict[str, Any]) -> bool:
        """删除单个降噪DNG文件"""
        match = re.match(r'(_DSC\d{4})-已增强-降噪\.dng$', filename, re.IGNORECASE)
        if match:
            file_to_delete = os.path.join(folder_path, filename)
            try:
                os.remove(file_to_delete)
                print(f'Deleted: {filename}')
                return True
            except Exception as e:
                print(f'Failed to delete {filename}: {str(e)}')
        return False
