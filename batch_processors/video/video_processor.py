# -*- coding: utf-8 -*-
"""
视频批量处理器基类

提供视频特定批量处理操作的基本功能。
继承BaseBatchProcessor并添加视频专用工具。
"""

import os
from typing import Optional, List, Dict, Any

from ..base.base_processor import BaseBatchProcessor


class VideoBatchProcessor(BaseBatchProcessor):
    """
    视频批量处理操作基类。
    """
    
    # 常见视频扩展名
    VIDEO_EXTENSIONS = [
        '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm',
        '.m4v', '.mpg', '.mpeg', '.3gp', '.3g2', '.ts', '.mts'
    ]
    
    # 需要处理的扩展名（RAW相机格式）
    RAW_VIDEO_EXTENSIONS = [
        '.arw', '.nef', '.dng', '.raf', '.raw', '.rw2', '.orf'
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化视频批量处理器。
        
        参数:
            config: 可选的配置字典
        """
        super().__init__(config)
        
    def scan_videos(self, 
                    folder_path: str, 
                    extensions: Optional[List[str]] = None,
                    recursive: bool = True) -> List[str]:
        """
        扫描文件夹中的视频文件。
        
        参数:
            folder_path: 要扫描的文件夹
            extensions: 要过滤的特定扩展名。如果为None，使用VIDEO_EXTENSIONS
            recursive: 是否递归扫描
            
        返回:
            视频文件路径列表
        """
        if extensions is None:
            extensions = self.VIDEO_EXTENSIONS
            
        return self.scan_files(folder_path, extensions, recursive)
    
    def get_video_info(self, video_path: str) -> Optional[Dict[str, Any]]:
        """
        获取视频文件信息。
        
        参数:
            video_path: 视频文件路径
            
        返回:
            包含视频信息的字典或None
        """
        if not os.path.exists(video_path):
            return None
            
        try:
            return {
                'path': video_path,
                'name': os.path.basename(video_path),
                'size': os.path.getsize(video_path),
                'ext': os.path.splitext(video_path)[1],
                'modified': os.path.getmtime(video_path)
            }
        except Exception as e:
            self.logger.error(f"获取视频信息失败: {e}")
            return None
            
    def filter_by_resolution(self, 
                          folder_path: str, 
                          min_width: Optional[int] = None,
                          min_height: Optional[int] = None) -> List[str]:
        """
        按分辨率筛选视频（需要ffprobe）。
        
        参数:
            folder_path: 要扫描的文件夹
            min_width: 最小宽度（像素）
            min_height: 最小高度（像素）
            
        返回:
            符合条件的视频文件路径列表
        """
        import subprocess
        import json
        
        videos = self.scan_videos(folder_path)
        filtered = []
        
        for video_path in videos:
            try:
                cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
                      '-show_streams', video_path]
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                     encoding='utf-8', errors='ignore')
                
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    for stream in info.get('streams', []):
                        if stream.get('codec_type') == 'video':
                            width = stream.get('width', 0)
                            height = stream.get('height', 0)
                            
                            if min_width and width < min_width:
                                break
                            if min_height and height < min_height:
                                break
                            else:
                                filtered.append(video_path)
                            break
            except Exception as e:
                self.logger.warning(f"无法检查分辨率 {video_path}: {e}")
                
        return filtered