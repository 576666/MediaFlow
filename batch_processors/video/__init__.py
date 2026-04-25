# -*- coding: utf-8 -*-
"""
视频批量处理器

本模块包含专门用于视频文件的批量处理脚本。

类:
    VideoBatchProcessor: 视频处理基类
    VideoExtensionRenamer: 处理视频扩展名大小写转换 (mp4 -> MP4)

使用示例:
    from MediaFlow.batch_processors.video import VideoBatchProcessor, VideoExtensionRenamer
    
    # 重命名视频扩展名
    renamer = VideoExtensionRenamer()
    renamer.rename_extensions('A:/素材/视频', 'mp4', 'MP4')
"""

from .video_processor import VideoBatchProcessor
from .extension_renamer import VideoExtensionRenamer

__all__ = ['VideoBatchProcessor', 'VideoExtensionRenamer']