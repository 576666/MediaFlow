# -*- coding: utf-8 -*-
"""
照片灰度转换器

将照片转换为灰度图。
基于Tool文件夹中的png2grey.py脚本。
"""

import os
from typing import Optional, Dict, Any

from PIL import Image

from .photo_processor import PhotoBatchProcessor


class PhotoGrayscaleConverter(PhotoBatchProcessor):
    """
    将照片转换为灰度图。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化灰度转换器。
        
        参数:
            config: 可选的配置字典
        """
        super().__init__(config)
    
    def convert_to_grayscale(self, 
                            folder_path: str,
                            output_folder: Optional[str] = None,
                            extensions: Optional[list] = None,
                            recursive: bool = True,
                            preserve_alpha: bool = False) -> Dict[str, Any]:
        """
        将文件夹中的所有照片转换为灰度图。
        
        参数:
            folder_path: 包含照片的文件夹
            output_folder: 输出文件夹（None = 覆盖原文件）
            extensions: 要处理的照片扩展名。如果为None，处理所有标准格式
            recursive: 是否扫描子文件夹
            preserve_alpha: 是否保留alpha通道
            
        返回:
            包含'success'和'failure'列表的字典
        """
        if not self.validate_path(folder_path):
            return {'success': [], 'failure': [], 'error': '无效路径'}
        
        # 默认扩展名
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        
        results = {'success': [], 'failure': []}
        
        files = self.scan_files(folder_path, extensions, recursive)
        
        for file_path in files:
            try:
                directory = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                name_without_ext = os.path.splitext(filename)[0]
                
                # 确定输出路径
                if output_folder:
                    rel_path = os.path.relpath(file_path, folder_path)
                    out_dir = os.path.dirname(rel_path)
                    if out_dir and out_dir != '.':
                        out_path = os.path.join(output_folder, out_dir)
                        os.makedirs(out_path, exist_ok=True)
                    else:
                        out_path = output_folder
                    out_file = os.path.join(out_path, filename)
                else:
                    # 就地转换
                    out_file = file_path
                
                # 打开并转换
                with Image.open(file_path) as img:
                    # 转换为灰度图
                    if preserve_alpha and img.mode == 'RGBA':
                        # 保留alpha转换为灰度
                        gray_img = img.convert('LA').convert('RGBA')
                    else:
                        gray_img = img.convert('L')
                    
                    # 保存
                    gray_img.save(out_file)
                    
                    self.logger.info(f"已转换为灰度图: {filename}")
                    results['success'].append(file_path)
                    
            except Exception as e:
                self.logger.error(f"转换失败 {file_path}: {e}")
                results['failure'].append(file_path)
                
        self.logger.info(f"完成: {len(results['success'])}/{len(files)} 个文件已转换")
        return results
    
    def convert_png_to_grayscale(self, 
                                  folder_path: str,
                                  output_folder: Optional[str] = None) -> Dict[str, Any]:
        """
        便利方法：将PNG文件转换为灰度图。
        
        参数:
            folder_path: 包含PNG文件的文件夹
            output_folder: 可选的输出文件夹
            
        返回:
            包含结果的字典
        """
        return self.convert_to_grayscale(folder_path, output_folder, extensions=['.png'])
    
    def convert_jpg_to_grayscale(self, 
                               folder_path: str,
                               output_folder: Optional[str] = None) -> Dict[str, Any]:
        """
        便利方法：将JPG文件转换为灰度图。
        
        参数:
            folder_path: 包含JPG文件的文件夹
            output_folder: 可选的输出文件夹
            
        返回:
            包含结果的字典
        """
        return self.convert_to_grayscale(folder_path, output_folder, extensions=['.jpg', '.jpeg'])


# 便利函数
def convert_to_grayscale(folder_path: str, 
                          output_folder: Optional[str] = None,
                          extensions: Optional[list] = None) -> Dict[str, Any]:
    """
    便利函数，将照片转换为灰度图。
    
    参数:
        folder_path: 包含照片的文件夹
        output_folder: 可选的输出文件夹
        extensions: 要处理的扩展名
        
    返回:
        包含结果的字典
    """
    converter = PhotoGrayscaleConverter()
    return converter.convert_to_grayscale(folder_path, output_folder, extensions)