from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class VideoTask:
    """视频处理任务数据模型"""
    task_id: str                   # 任务ID
    input_path: str                # 输入文件路径
    output_path: str               # 输出文件路径
    config: Dict[str, Any]         # 处理配置
    status: TaskStatus = TaskStatus.PENDING  # 任务状态
    priority: TaskPriority = TaskPriority.NORMAL  # 任务优先级
    progress: float = 0.0          # 进度（0.0-1.0）
    created_time: datetime = None  # 创建时间
    started_time: Optional[datetime] = None  # 开始时间
    completed_time: Optional[datetime] = None  # 完成时间
    result: Optional[Dict[str, Any]] = None  # 处理结果
    error_message: Optional[str] = None  # 错误信息

    def __post_init__(self):
        if self.created_time is None:
            self.created_time = datetime.now()

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
class QualityMetrics:
    """质量指标数据模型"""
    psnr: Optional[float] = None
    ssim: Optional[float] = None
    vmaf: Optional[float] = None
    bitrate_original: Optional[float] = None
    bitrate_compressed: Optional[float] = None
    compression_ratio: Optional[float] = None