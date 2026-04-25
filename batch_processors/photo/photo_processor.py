# -*- coding: utf-8 -*-
"""
照片批量处理器基类

提供照片/图像特定批量处理操作的基本功能。
继承BaseBatchProcessor并添加照片专用工具。
"""

import os
from typing import Optional, List, Dict, Any

from ..base.base_processor import BaseBatchProcessor


class PhotoBatchProcessor(BaseBatchProcessor):
    """
    照片批量处理操作基类。
    """
    
    # 常见照片/图像扩展名
    PHOTO_EXTENSIONS = [
        '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif',
        '.webp', '.heic', '.heif', '.raw', '.arw', '.nef', 
        '.dng', '.raf', '.rw2', '.orf', '.cr2', '.cr3', '.nrw'
    ]
    
    # 标准照片格式用于输出
    STANDARD_PHOTO_EXTENSIONS = [
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化照片批量处理器。
        
        参数:
            config: 可选的配置字典
        """
        super().__init__(config)
        
    def scan_photos(self, 
                    folder_path: str, 
                    extensions: Optional[List[str]] = None,
                    recursive: bool = True) -> List[str]:
        """
        扫描文件夹中的照片文件。
        
        参数:
            folder_path: 要扫描的文件夹
            extensions: 要过滤的特定扩展名。如果为None，使用PHOTO_EXTENSIONS
            recursive: 是否递归扫描
            
        返回:
            照片文件路径列表
        """
        if extensions is None:
            extensions = self.PHOTO_EXTENSIONS
            
        return self.scan_files(folder_path, extensions, recursive)
    
    def scan_raw_photos(self, folder_path: str, recursive: bool = True) -> List[str]:
        """
        扫描文件夹中的RAW照片文件（相机特定格式）。
        
        参数:
            folder_path: 要扫描的文件夹
            recursive: 是否递归扫描
            
        返回:
            RAW照片文件路径列表
        """
        raw_extensions = ['.arw', '.nef', '.dng', '.raf', '.raw', '.rw2', '.orf', '.cr2', '.cr3']
        return self.scan_files(folder_path, raw_extensions, recursive)
    
    def scan_jpeg_photos(self, folder_path: str, recursive: bool = True) -> List[str]:
        """
        扫描文件夹中的JPEG文件。
        
        参数:
            folder_path: 要扫描的文件夹
            recursive: 是否递归扫描
            
        返回:
            JPEG文件路径列表
        """
        jpeg_extensions = ['.jpg', '.jpeg']
        return self.scan_files(folder_path, jpeg_extensions, recursive)
    
    def get_photo_info(self, photo_path: str) -> Optional[Dict[str, Any]]:
        """
        获取照片文件信息。
        
        参数:
            photo_path: 照片文件路径
            
        返回:
            包含照片信息的字典或None
        """
        if not os.path.exists(photo_path):
            return None
            
        try:
            return {
                'path': photo_path,
                'name': os.path.basename(photo_path),
                'size': os.path.getsize(photo_path),
                'ext': os.path.splitext(photo_path)[1],
                'modified': os.path.getmtime(photo_path)
            }
        except Exception as e:
            self.logger.error(f"获取照片信息失败: {e}")
            return None
    
    def get_dimension(self, photo_path: str) -> Optional[tuple]:
        """
        使用PIL获取照片尺寸。
        
        参数:
            photo_path: 照片文件路径
            
        返回:
            (宽度, 高度)元组或None
        """
        try:
            from PIL import Image
            with Image.open(photo_path) as img:
                return img.size
        except Exception as e:
            self.logger.warning(f"无法获取尺寸 {photo_path}: {e}")
            return None