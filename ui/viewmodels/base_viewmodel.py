"""
ViewModel基类
提供数据绑定、命令和属性通知的基础功能
"""
from PySide6.QtCore import QObject, Signal, Property
from typing import Any, Optional, Callable
import threading


class Command:
    """命令模式实现"""
    def __init__(self, execute_func: Callable, can_execute_func: Optional[Callable] = None):
        self.execute = execute_func
        self.can_execute = can_execute_func or (lambda: True)


class BaseViewModel(QObject):
    """ViewModel基类，所有ViewModel都应继承此类"""
    
    # 错误信号
    error_occurred = Signal(str, str)  # error_type, message
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._properties = {}
        self._property_lock = threading.RLock()
        
    def _get_property(self, name: str, default: Any = None) -> Any:
        """获取属性值"""
        with self._property_lock:
            return self._properties.get(name, default)
    
    def _set_property(self, name: str, value: Any, notify: bool = True) -> None:
        """设置属性值并可选地发送通知"""
        with self._property_lock:
            old_value = self._properties.get(name)
            if old_value != value:
                self._properties[name] = value
                if notify and hasattr(self, f'{name}_changed'):
                    getattr(self, f'{name}_changed').emit(value)
    
    def create_property(self, name: str, default_value: Any = None) -> None:
        """动态创建属性"""
        self._properties[name] = default_value
        
    def raise_error(self, error_type: str, message: str) -> None:
        """引发错误"""
        self.error_occurred.emit(error_type, message)
        
    def dispose(self) -> None:
        """清理资源"""
        # 子类可以重写此方法以进行清理
        pass