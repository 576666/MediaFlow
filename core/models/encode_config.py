from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class EncodeConfig:
    """编码配置参数"""
    codec: str = "h264"           # 编码器
    preset: str = "medium"        # 预设
    crf: int = 23                 # CRF值
    bitrate: Optional[int] = None # 比特率（kbps）
    resolution: Optional[Tuple[int, int]] = None  # 分辨率（宽，高）
    framerate: Optional[float] = None  # 帧率
    hardware_acceleration: bool = False  # 是否使用硬件加速
    
    def to_dict(self) -> dict:
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