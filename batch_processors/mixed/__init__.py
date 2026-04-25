# -*- coding: utf-8 -*-
"""
混合批量处理器

本模块包含同时处理视频和照片文件的批量处理脚本。

类:
    MixedBatchProcessor: 混合媒体处理基类
    DirectoryFlattener: 扁平化嵌套目录结构
    AutoBackupProcessor: 处理自动备份和优化

使用示例:
    from MediaFlow.batch_processors.mixed import MixedBatchProcessor, DirectoryFlattener
    
    # 扁平化目录结构
    flattener = DirectoryFlattener()
    flattener.flatten('A:/素材/整理文件夹')
"""

from .mixed_processor import MixedBatchProcessor
from .directory_flattener import DirectoryFlattener
from .auto_backup_processor import AutoBackupProcessor

__all__ = ['MixedBatchProcessor', 'DirectoryFlattener', 'AutoBackupProcessor']