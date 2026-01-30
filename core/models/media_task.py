#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
媒体处理任务数据模型
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 等待中
    PROCESSING = "processing" # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MediaFile:
    """媒体文件信息模型"""
    path: str                     # 文件路径
    size: int = 0                 # 文件大小（字节）
    created_time: Optional[datetime] = None  # 创建时间
    modified_time: Optional[datetime] = None # 修改时间
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据
    
    @property
    def filename(self) -> str:
        """获取文件名"""
        import os
        return os.path.basename(self.path)
    
    @property
    def extension(self) -> str:
        """获取文件扩展名"""
        import os
        return os.path.splitext(self.path)[1].lower()
    
    @property
    def directory(self) -> str:
        """获取文件所在目录"""
        import os
        return os.path.dirname(self.path)


@dataclass
class MediaTask:
    """媒体处理任务数据模型"""
    task_id: str                   # 任务ID
    media_files: List[MediaFile]   # 媒体文件列表
    processor_name: str            # 处理器名称
    config: Dict[str, Any]         # 处理配置
    status: TaskStatus = TaskStatus.PENDING  # 任务状态
    priority: TaskPriority = TaskPriority.NORMAL  # 任务优先级
    progress: float = 0.0          # 进度（0.0-1.0）
    created_time: datetime = field(default_factory=datetime.now)  # 创建时间
    started_time: Optional[datetime] = None  # 开始时间
    completed_time: Optional[datetime] = None  # 完成时间
    result: Optional[Dict[str, Any]] = None  # 处理结果
    error_message: Optional[str] = None  # 错误信息
    
    @property
    def total_files(self) -> int:
        """获取总文件数"""
        return len(self.media_files)
    
    @property
    def elapsed_time(self) -> Optional[float]:
        """获取已用时间（秒）"""
        if self.started_time is None:
            return None
        end_time = self.completed_time or datetime.now()
        return (end_time - self.started_time).total_seconds()
    
    def update_progress(self, progress: float) -> None:
        """更新任务进度"""
        self.progress = max(0.0, min(1.0, progress))
    
    def mark_started(self) -> None:
        """标记任务开始"""
        self.status = TaskStatus.PROCESSING
        self.started_time = datetime.now()
    
    def mark_completed(self, result: Optional[Dict[str, Any]] = None) -> None:
        """标记任务完成"""
        self.status = TaskStatus.COMPLETED
        self.completed_time = datetime.now()
        self.progress = 1.0
        self.result = result
    
    def mark_failed(self, error_message: str) -> None:
        """标记任务失败"""
        self.status = TaskStatus.FAILED
        self.completed_time = datetime.now()
        self.error_message = error_message
    
    def mark_cancelled(self) -> None:
        """标记任务取消"""
        self.status = TaskStatus.CANCELLED
        self.completed_time = datetime.now()


@dataclass
class EncodeConfig:
    """编码配置参数"""
    codec: str = "h264"           # 编码器
    preset: str = "medium"        # 预设
    crf: int = 23                 # CRF值
    bitrate: Optional[int] = None # 比特率（kbps）
    resolution: Optional[tuple] = None  # 分辨率（宽，高）
    framerate: Optional[float] = None  # 帧率
    hardware_acceleration: bool = False  # 是否使用硬件加速
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "codec": self.codec,
            "preset": self.preset,
            "crf": self.crf,
            "bitrate": self.bitrate,
            "resolution": self.resolution,
            "framerate": self.framerate,
            "hardware_acceleration": self.hardware_acceleration
        }


@dataclass
class QualityMetrics:
    """质量指标数据模型"""
    psnr: Optional[float] = None      # PSNR值
    ssim: Optional[float] = None      # SSIM值
    vmaf: Optional[float] = None      # VMAF值
    bitrate: Optional[int] = None     # 比特率
    compression_ratio: Optional[float] = None  # 压缩比
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "psnr": self.psnr,
            "ssim": self.ssim,
            "vmaf": self.vmaf,
            "bitrate": self.bitrate,
            "compression_ratio": self.compression_ratio
        }
