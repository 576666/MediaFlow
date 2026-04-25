# -*- coding: utf-8 -*-
"""
照片格式转换器

在不同的照片格式之间转换（jpg, png, bmp等）。
基于Tool文件夹中的jpg2png.py和png2grey.py脚本。
"""

import os
from typing import Optional, List, Dict, Any

from PIL import Image

from .photo_processor import PhotoBatchProcessor


class PhotoFormatConverter(PhotoBatchProcessor):
    """
    在不同照片格式之间转换照片文件。
    """
    
    SUPPORTED_FORMATS = {
        'jpg': {'extensions': ['.jpg', '.jpeg'], 'pil_format': 'JPEG'},
        'jpeg': {'extensions': ['.jpg', '.jpeg'], 'pil_format': 'JPEG'},
        'png': {'extensions': ['.png'], 'pil_format': 'PNG'},
        'bmp': {'extensions': ['.bmp'], 'pil_format': 'BMP'},
        'tiff': {'extensions': ['.tiff', '.tif'], 'pil_format': 'TIFF'},
        'webp': {'extensions': ['.webp'], 'pil_format': 'WEBP'},
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化照片格式转换器。
        
        参数:
            config: 可选的配置字典
        """
        super().__init__(config)
    
    def convert(self, 
                 folder_path: str, 
                 from_format: str, 
                 to_format: str,
                 output_folder: Optional[str] = None,
                 recursive: bool = True,
                 quality: int = 95) -> Dict[str, Any]:
        """
        将所有照片从一种格式转换为另一种格式。
        
        参数:
            folder_path: 包含照片的文件夹
            from_format: 源格式（例如 'jpg', 'jpeg', 'png'）
            to_format: 目标格式（例如 'jpg', 'png', 'bmp'）
            output_folder: 输出文件夹（None = 使用源文件夹）
            recursive: 是否扫描子文件夹
            quality: 有损格式的质量（1-100）
            
        返回:
            包含'success'和'failure'列表的字典
        """
        if not self.validate_path(folder_path):
            return {'success': [], 'failure': [], 'error': '无效路径'}
        
        # 解析格式
        from_format = from_format.lower()
        to_format = to_format.lower()
        
        if from_format not in self.SUPPORTED_FORMATS:
            return {'success': [], 'failure': [], 'error': f'不支持的源格式: {from_format}'}
        
        if to_format not in self.SUPPORTED_FORMATS:
            return {'success': [], 'failure': [], 'error': f'不支持的目标格式: {to_format}'}
        
        source_extensions = self.SUPPORTED_FORMATS[from_format]['extensions']
        target_format_info = self.SUPPORTED_FORMATS[to_format]
        target_extension = target_format_info['extensions'][0]
        pil_format = target_format_info['pil_format']
        
        results = {'success': [], 'failure': []}
        
        # 获取源文件
        files = self.scan_files(folder_path, source_extensions, recursive)
        
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
                    new_filename = name_without_ext + target_extension
                    out_file = os.path.join(out_path, new_filename)
                else:
                    # 就地转换
                    out_file = os.path.join(directory, name_without_ext + target_extension)
                
                # 转换图像
                with Image.open(file_path) as img:
                    # 处理JPEG的RGBA到RGB
                    if pil_format == 'JPEG' and img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'RGBA':
                            background.paste(img, mask=img.split()[3])
                        else:
                            background.paste(img, mask=img.split()[1])
                        img = background
                    elif img.mode == 'P':
                        img = img.convert('RGBA')
                    
                    # 带质量保存
                    save_kwargs = {}
                    if pil_format in ('JPEG', 'WEBP'):
                        save_kwargs['quality'] = quality
                    elif pil_format == 'PNG':
                        save_kwargs['compress_level'] = 6
                    
                    img.save(out_file, pil_format, **save_kwargs)
                    self.logger.info(f"已转换: {filename} -> {os.path.basename(out_file)}")
                    results['success'].append((file_path, out_file))
                    
            except Exception as e:
                self.logger.error(f"转换失败 {file_path}: {e}")
                results['failure'].append(file_path)
                
        self.logger.info(f"完成: {len(results['success'])}/{len(files)} 个文件已转换")
        return results
    
    def jpg_to_png(self, folder_path: str, output_folder: Optional[str] = None) -> Dict[str, Any]:
        """
        便利方法：将JPG/JPEG转换为PNG。
        
        参数:
            folder_path: 包含JPG文件的文件夹
            output_folder: 可选的输出文件夹
            
        返回:
            包含结果的字典
        """
        return self.convert(folder_path, 'jpg', 'png', output_folder)
    
    def png_to_jpg(self, folder_path: str, output_folder: Optional[str] = None, quality: int = 95) -> Dict[str, Any]:
        """
        便利方法：将PNG转换为JPG。
        
        参数:
            folder_path: 包含PNG文件的文件夹
            output_folder: 可选的输出文件夹
            quality: JPEG质量（1-100）
            
        返回:
            包含结果的字典
        """
        return self.convert(folder_path, 'png', 'jpg', output_folder, quality=quality)
    
    def jpeg_to_jpg(self, folder_path: str) -> Dict[str, Any]:
        """
        将所有.jpeg文件重命名为.jpg。
        
        参数:
            folder_path: 包含JPEG文件的文件夹
            
        返回:
            包含结果的字典
        """
        files = self.scan_files(folder_path, ['.jpeg'], recursive=True)
        results = {'success': [], 'failure': []}
        
        for file_path in files:
            try:
                directory = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                new_filename = os.path.splitext(filename)[0] + '.jpg'
                new_path = os.path.join(directory, new_filename)
                
                if os.path.exists(new_path):
                    self.logger.warning(f"目标已存在，跳过: {new_filename}")
                    results['failure'].append(file_path)
                    continue
                    
                os.rename(file_path, new_path)
                self.logger.info(f"已重命名: {filename} -> {new_filename}")
                results['success'].append(file_path)
            except Exception as e:
                self.logger.error(f"重命名失败: {e}")
                results['failure'].append(file_path)
                
        return results


# 便利函数
def convert_photos(folder_path: str, from_format: str, to_format: str) -> Dict[str, Any]:
    """
    便利函数，转换照片格式。
    
    参数:
        folder_path: 包含照片的文件夹
        from_format: 源格式
        to_format: 目标格式
        
    返回:
        包含结果的字典
    """
    converter = PhotoFormatConverter()
    return converter.convert(folder_path, from_format, to_format)