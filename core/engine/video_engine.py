#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
视频处理引擎基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass

from core.models.media_task import EncodeConfig, QualityMetrics


@dataclass
class EncodeResult:
    """编码结果"""
    success: bool
    output_path: str
    elapsed_time: float
    output_size: int
    original_size: int
    compression_ratio: float
    error_message: Optional[str] = None


@dataclass
class FrameExtractionResult:
    """帧提取结果"""
    frames: List[np.ndarray]
    timestamps: List[float]
    frame_rate: float
    resolution: Tuple[int, int]


class VideoEngine(ABC):
    """视频处理引擎基类"""
    
    @abstractmethod
    def compress_video(self, input_path: str, output_path: str, 
                      config: EncodeConfig) -> EncodeResult:
        """压缩视频"""
        pass
    
    @abstractmethod
    def extract_frames(self, video_path: str, interval: float = 1.0) -> FrameExtractionResult:
        """提取视频帧"""
        pass
    
    @abstractmethod
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        pass
    
    @abstractmethod
    def get_hardware_acceleration_info(self) -> Dict[str, Any]:
        """获取硬件加速信息"""
        pass
    
    def calculate_compression_ratio(self, original_size: int, compressed_size: int) -> float:
        """计算压缩比"""
        if original_size == 0:
            return 0.0
        return (original_size - compressed_size) / original_size


class CodecEngine(ABC):
    """编解码引擎接口"""
    
    @abstractmethod
    def encode(self, input_path: str, output_path: str, config: EncodeConfig) -> EncodeResult:
        """编码视频"""
        pass
    
    @abstractmethod
    def decode(self, video_path: str) -> FrameExtractionResult:
        """解码视频为帧"""
        pass
    
    @abstractmethod
    def get_supported_codecs(self) -> List[str]:
        """获取支持的编解码器"""
        pass
    
    @abstractmethod
    def is_hardware_accelerated(self) -> bool:
        """是否支持硬件加速"""
        pass


class QualityAnalyzer(ABC):
    """质量分析引擎接口"""
    
    @abstractmethod
    def compare_videos(self, original_path: str, processed_path: str) -> QualityMetrics:
        """对比视频质量"""
        pass
    
    @abstractmethod
    def compare_frames(self, original_frame: np.ndarray, 
                      processed_frame: np.ndarray) -> Dict[str, float]:
        """对比单帧质量"""
        pass
    
    @abstractmethod
    def generate_quality_report(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """生成质量分析报告"""
        pass
