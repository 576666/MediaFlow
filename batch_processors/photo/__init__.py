# -*- coding: utf-8 -*-
"""
照片批量处理器

本模块包含专门用于照片/图像文件的批量处理脚本。

类:
    PhotoBatchProcessor: 照片处理基类
    PhotoFormatConverter: 在照片格式之间转换 (jpg, png 等)
    PhotoExtensionRenamer: 处理照片扩展名大小写转换
    PhotoGrayscaleConverter: 将照片转换为灰度图

使用示例:
    from MediaFlow.batch_processors.photo import PhotoBatchProcessor, PhotoFormatConverter
    
    # 将jpg转换为png
    converter = PhotoFormatConverter()
    converter.convert('A:/素材/照片', 'jpg', 'png')
"""

from .photo_processor import PhotoBatchProcessor
from .format_converter import PhotoFormatConverter
from .extension_renamer import PhotoExtensionRenamer
from .grayscale_converter import PhotoGrayscaleConverter

__all__ = ['PhotoBatchProcessor', 'PhotoFormatConverter', 'PhotoExtensionRenamer', 'PhotoGrayscaleConverter']