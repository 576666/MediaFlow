"""
左右分屏视频对比控件
"""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QLabel, QSlider, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap, QPainter
import pyqtgraph as pg
import numpy as np


class VideoComparisonWidget(QWidget):
    """左右分屏视频对比控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
        
        # 存储原始和处理后的帧
        self.original_frame = None
        self.processed_frame = None
    
    def _setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 创建对比视图的分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：原始视频视图
        self.original_view = pg.GraphicsLayoutWidget()
        self.original_plot = self.original_view.addPlot(title="原始视频")
        self.original_image = pg.ImageItem()
        self.original_plot.addItem(self.original_image)
        self.original_plot.hideAxis('left')
        self.original_plot.hideAxis('bottom')
        
        # 右侧：处理后视频视图
        self.processed_view = pg.GraphicsLayoutWidget()
        self.processed_plot = self.processed_view.addPlot(title="处理后视频")
        self.processed_image = pg.ImageItem()
        self.processed_plot.addItem(self.processed_image)
        self.processed_plot.hideAxis('left')
        self.processed_plot.hideAxis('bottom')
        
        # 添加到分割器
        splitter.addWidget(self.original_view)
        splitter.addWidget(self.processed_view)
        splitter.setSizes([500, 500])  # 初始平分
        
        # 控制面板
        controls_layout = QHBoxLayout()
        
        # 同步缩放按钮
        self.sync_zoom_btn = QPushButton("同步缩放")
        self.sync_zoom_btn.setCheckable(True)
        self.sync_zoom_btn.setChecked(True)
        
        # 滑块控制对比度等
        contrast_label = QLabel("对比度:")
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(0, 200)
        self.contrast_slider.setValue(100)
        
        controls_layout.addWidget(self.sync_zoom_btn)
        controls_layout.addWidget(contrast_label)
        controls_layout.addWidget(self.contrast_slider)
        controls_layout.addStretch()
        
        # 添加到主布局
        layout.addWidget(splitter)
        layout.addLayout(controls_layout)
    
    def _connect_signals(self):
        """连接信号"""
        self.contrast_slider.valueChanged.connect(self._on_contrast_changed)
        
        # 连接两个视图的缩放和移动事件
        if self.sync_zoom_btn.isChecked():
            self._sync_views()
    
    def update_frames(self, original_frame, processed_frame):
        """更新左右视图的帧"""
        # 存储帧
        self.original_frame = original_frame
        self.processed_frame = processed_frame
        
        # 更新左侧视图
        if original_frame is not None:
            # 将numpy数组转换为适合显示的格式
            img_data = self._convert_to_display_format(original_frame)
            self.original_image.setImage(img_data)
        
        # 更新右侧视图
        if processed_frame is not None:
            # 将numpy数组转换为适合显示的格式
            img_data = self._convert_to_display_format(processed_frame)
            self.processed_image.setImage(img_data)
    
    def _convert_to_display_format(self, frame):
        """将帧数据转换为适合pyqtgraph显示的格式"""
        if frame is None:
            return np.zeros((100, 100, 3))
        
        # 如果是BGR格式，转换为RGB
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            # OpenCV默认是BGR，转换为RGB
            frame_rgb = frame[:, :, [2, 1, 0]]  # BGR to RGB
        elif len(frame.shape) == 2:
            # 灰度图，复制到三个通道
            frame_rgb = np.stack([frame, frame, frame], axis=2)
        else:
            frame_rgb = frame
        
        return frame_rgb.astype(np.uint8)
    
    def _on_contrast_changed(self, value):
        """对比度变化处理"""
        # 这里可以实现对比度调整逻辑
        contrast_factor = value / 100.0
        # 更新显示...
    
    def _sync_views(self):
        """同步两个视图的视图范围"""
        # 当一个视图缩放或平移时，同步到另一个视图
        def sync_left_to_right():
            if self.sync_zoom_btn.isChecked():
                self.processed_plot.setXRange(*self.original_plot.viewRange()[0], padding=0)
                self.processed_plot.setYRange(*self.original_plot.viewRange()[1], padding=0)
        
        def sync_right_to_left():
            if self.sync_zoom_btn.isChecked():
                self.original_plot.setXRange(*self.processed_plot.viewRange()[0], padding=0)
                self.original_plot.setYRange(*self.processed_plot.viewRange()[1], padding=0)
        
        # 连接视图变化信号
        self.original_plot.sigRangeChanged.connect(sync_left_to_right)
        self.processed_plot.sigRangeChanged.connect(sync_right_to_left)
    
    def set_title(self, original_title: str, processed_title: str):
        """设置标题"""
        self.original_plot.setTitle(original_title)
        self.processed_plot.setTitle(processed_title)