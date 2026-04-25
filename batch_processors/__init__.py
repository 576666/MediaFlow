# -*- coding: utf-8 -*-
"""
MediaFlow 批量处理器包

本包包含用于视频、照片和混合媒体操作的批量处理脚本。
所有处理器都设计为与MediaFlow的配置系统配合使用，而非硬编码路径。

结构:
- video/     : 视频特定的批量处理脚本
- photo/     : 照片/图像特定的批量处理脚本  
- mixed/     : 混合媒体操作（视频和照片）
- base/      : 基类和工具

使用示例:
    from MediaFlow.batch_processors import VideoBatchProcessor, PhotoBatchProcessor, MixedBatchProcessor
    
    # 处理视频文件
    processor = VideoBatchProcessor()
    processor.rename_extension_case('A:/素材/视频', 'mp4', 'MP4')
    
    # 处理照片文件  
    processor = PhotoBatchProcessor()
    processor.convert_format('A:/素材/照片', 'jpg', 'png')
"""

from .base.base_processor import BaseBatchProcessor

__version__ = "1.0.0"
__all__ = ['BaseBatchProcessor']