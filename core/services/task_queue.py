"""
统一任务队列管理器
"""
from PySide6.QtCore import QObject, Signal, QThreadPool, QRunnable, QTimer
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import threading
from dataclasses import dataclass
from enum import Enum


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


class TaskQueue(QObject):
    """统一任务队列，支持优先级、暂停、进度反馈"""
    
    # 信号定义
    task_added = Signal(str)  # 任务ID
    task_started = Signal(str)  # 任务ID
    task_progress = Signal(str, int, int)  # 任务ID, 当前进度, 总进度
    task_completed = Signal(str, dict)  # 任务ID, 结果
    task_failed = Signal(str, Exception)  # 任务ID, 异常
    task_cancelled = Signal(str)  # 任务ID
    queue_empty = Signal()
    
    def __init__(self, max_workers: int = 4):
        super().__init__()
        self._tasks: Dict[str, VideoTask] = {}
        self._pending_tasks: List[str] = []  # 按优先级排序的任务ID列表
        self._running_tasks: Dict[str, Any] = {}
        self._completed_tasks: Dict[str, VideoTask] = {}
        self._failed_tasks: Dict[str, VideoTask] = {}
        
        self._thread_pool = QThreadPool()
        self._thread_pool.setMaxThreadCount(max_workers)
        
        self._lock = threading.RLock()
        
        # 用于存储预览任务
        self._preview_tasks: Dict[str, VideoTask] = {}
        
        # 定时器用于处理任务调度
        self._scheduler_timer = QTimer()
        self._scheduler_timer.timeout.connect(self._process_pending_tasks)
        self._scheduler_timer.start(100)  # 每100毫秒检查一次
    
    def submit_preview_task(self, task: VideoTask) -> str:
        """提交5秒预览任务"""
        task_id = str(uuid.uuid4())
        task.task_id = task_id
        
        with self._lock:
            self._preview_tasks[task_id] = task
            self._tasks[task_id] = task
            self._pending_tasks.append(task_id)
            # 预览任务优先级设为高
            task.priority = TaskPriority.HIGH
        
        self.task_added.emit(task_id)
        return task_id
    
    def submit_batch_task(self, task: VideoTask) -> str:
        """提交批量处理任务"""
        task_id = str(uuid.uuid4())
        task.task_id = task_id
        
        with self._lock:
            self._tasks[task_id] = task
            self._pending_tasks.append(task_id)
        
        self.task_added.emit(task_id)
        return task_id
    
    def cancel_task(self, task_id: str) -> bool:
        """取消指定任务"""
        with self._lock:
            if task_id in self._pending_tasks:
                self._pending_tasks.remove(task_id)
                task = self._tasks[task_id]
                task.mark_cancelled()
                self._failed_tasks[task_id] = task
                self.task_cancelled.emit(task_id)
                return True
            elif task_id in self._running_tasks:
                # 对于正在运行的任务，需要在worker中处理取消
                worker = self._running_tasks[task_id]
                worker.cancel()
                return True
        return False
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        with self._lock:
            if task_id in self._tasks:
                return self._tasks[task_id].status
        return None
    
    def get_task_progress(self, task_id: str) -> float:
        """获取任务进度"""
        with self._lock:
            if task_id in self._tasks:
                return self._tasks[task_id].progress
        return 0.0
    
    def _process_pending_tasks(self):
        """处理待处理的任务"""
        # 检查是否有空闲线程，并分配任务
        while (self._thread_pool.activeThreadCount() < self._thread_pool.maxThreadCount() and 
               self._pending_tasks):
            with self._lock:
                if not self._pending_tasks:
                    break
                # 按优先级排序选择任务
                task_id = self._select_next_task()
                if not task_id:
                    continue
                
                self._pending_tasks.remove(task_id)
                task = self._tasks[task_id]
                task.mark_started()
                
                # 创建任务工作器
                worker = TaskWorker(task, self)
                worker.task_completed.connect(self._on_task_completed)
                worker.task_failed.connect(self._on_task_failed)
                worker.progress_updated.connect(self._on_task_progress)
                
                self._running_tasks[task_id] = worker
                self._thread_pool.start(worker)
                
                self.task_started.emit(task_id)
    
    def _select_next_task(self) -> Optional[str]:
        """根据优先级选择下一个任务"""
        if not self._pending_tasks:
            return None
        
        # 按优先级排序
        def get_priority_value(task_id):
            task = self._tasks[task_id]
            priority_map = {
                TaskPriority.CRITICAL: 4,
                TaskPriority.HIGH: 3,
                TaskPriority.NORMAL: 2,
                TaskPriority.LOW: 1
            }
            return priority_map.get(task.priority, 2)
        
        self._pending_tasks.sort(key=get_priority_value, reverse=True)
        return self._pending_tasks[0] if self._pending_tasks else None
    
    def _on_task_completed(self, task_id: str, result: dict):
        """任务完成回调"""
        with self._lock:
            if task_id in self._running_tasks:
                del self._running_tasks[task_id]
            
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.mark_completed(result)
                self._completed_tasks[task_id] = task
        
        self.task_completed.emit(task_id, result)
        
        # 检查队列是否为空
        if not self._pending_tasks and not self._running_tasks:
            self.queue_empty.emit()
    
    def _on_task_failed(self, task_id: str, exception: Exception):
        """任务失败回调"""
        with self._lock:
            if task_id in self._running_tasks:
                del self._running_tasks[task_id]
            
            if task_id in self._tasks:
                task = self._tasks[task_id]
                task.mark_failed(str(exception))
                self._failed_tasks[task_id] = task
        
        self.task_failed.emit(task_id, exception)
        
        # 检查队列是否为空
        if not self._pending_tasks and not self._running_tasks:
            self.queue_empty.emit()
    
    def _on_task_progress(self, task_id: str, progress: float):
        """任务进度更新回调"""
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].update_progress(progress)
        
        # 发射进度信号，这里简单地发射当前进度为100%
        self.task_progress.emit(task_id, int(progress * 100), 100)
    
    def clear_completed_tasks(self):
        """清除已完成的任务"""
        with self._lock:
            self._completed_tasks.clear()
    
    def clear_failed_tasks(self):
        """清除失败的任务"""
        with self._lock:
            self._failed_tasks.clear()


class TaskWorker(QRunnable):
    """任务工作器，在单独的线程中执行任务."""
    
    progress_updated = Signal(str, float)  # 任务ID, 进度
    task_completed = Signal(str, dict)  # 任务ID, 结果
    task_failed = Signal(str, Exception)  # 任务ID, 异常
    
    def __init__(self, task: VideoTask, task_queue: TaskQueue):
        super().__init__()
        self.task = task
        self.task_queue = task_queue
        self._is_cancelled = False
        
    def run(self) -> None:
        """执行任务"""
        try:
            # 这里应该根据任务类型调用相应的处理器
            # 由于我们还没有具体的处理器，这里先模拟处理过程
            result = self._process_task()
            
            if not self._is_cancelled:
                self.task_completed.emit(self.task.task_id, result)
        
        except Exception as e:
            if not self._is_cancelled:
                self.task_failed.emit(self.task.task_id, e)
    
    def _process_task(self) -> dict:
        """处理任务的具体逻辑（示例）"""
        # 模拟处理过程
        import time
        for i in range(100):
            if self._is_cancelled:
                break
            time.sleep(0.01)  # 模拟处理延迟
            # 更新进度
            progress = (i + 1) / 100.0
            self.progress_updated.emit(self.task.task_id, progress)
        
        return {
            'success': not self._is_cancelled,
            'processed_file': self.task.output_path,
            'task_id': self.task.task_id
        }
    
    def cancel(self) -> None:
        """取消任务"""
        self._is_cancelled = True