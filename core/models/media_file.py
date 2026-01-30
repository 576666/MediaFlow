from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import os


@dataclass
class MediaFile:
    """媒体文件信息模型"""
    path: str                     # 文件路径
    size: int = 0                 # 文件大小（字节）
    created_time: Optional[datetime] = None  # 创建时间
    modified_time: Optional[datetime] = None # 修改时间
    metadata: Dict[str, Any] = None  # 元数据

    @property
    def filename(self) -> str:
        """获取文件名"""
        return os.path.basename(self.path)

    @property
    def extension(self) -> str:
        """获取文件扩展名"""
        return os.path.splitext(self.path)[1].lower()

    @property
    def directory(self) -> str:
        """获取文件所在目录"""
        return os.path.dirname(self.path)