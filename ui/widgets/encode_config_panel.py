"""
编码配置面板
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLabel, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QGroupBox, QSlider
)
from PySide6.QtCore import Qt


class EncodeConfigPanel(QWidget):
    """编码配置面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 创建配置组
        config_group = QGroupBox("编码配置")
        config_layout = QFormLayout(config_group)
        
        # 编码器选择
        self.codec_combo = QComboBox()
        self.codec_combo.addItems(["H.264", "H.265/HEVC", "VP9", "AV1"])
        
        # 预设选择
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "ultrafast", "superfast", "veryfast", 
            "faster", "fast", "medium", 
            "slow", "slower", "veryslow"
        ])
        self.preset_combo.setCurrentText("medium")
        
        # CRF值
        self.crf_spinbox = QDoubleSpinBox()
        self.crf_spinbox.setRange(0, 51)
        self.crf_spinbox.setValue(23)
        self.crf_spinbox.setSingleStep(0.5)
        
        # 比特率
        self.bitrate_spinbox = QSpinBox()
        self.bitrate_spinbox.setRange(100, 100000)
        self.bitrate_spinbox.setValue(5000)
        self.bitrate_spinbox.setSuffix(" kbps")
        
        # 帧率
        self.framerate_spinbox = QDoubleSpinBox()
        self.framerate_spinbox.setRange(1, 120)
        self.framerate_spinbox.setValue(30)
        self.framerate_spinbox.setDecimals(2)
        
        # 分辨率
        res_layout = QHBoxLayout()
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(16, 7680)  # 支持8K
        self.width_spinbox.setValue(1920)
        self.width_spinbox.setSuffix(" px")
        
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(16, 4320)  # 支持8K
        self.height_spinbox.setValue(1080)
        self.height_spinbox.setSuffix(" px")
        
        res_layout.addWidget(QLabel("宽"))
        res_layout.addWidget(self.width_spinbox)
        res_layout.addWidget(QLabel("×"))
        res_layout.addWidget(QLabel("高"))
        res_layout.addWidget(self.height_spinbox)
        
        # 硬件加速
        self.hw_accel_checkbox = QCheckBox("启用硬件加速")
        
        # 添加到表单布局
        config_layout.addRow("编码器:", self.codec_combo)
        config_layout.addRow("预设:", self.preset_combo)
        config_layout.addRow("CRF值:", self.crf_spinbox)
        config_layout.addRow("比特率:", self.bitrate_spinbox)
        config_layout.addRow("帧率:", self.framerate_spinbox)
        config_layout.addRow("分辨率:", res_layout)
        config_layout.addRow("", self.hw_accel_checkbox)
        
        # 添加到主布局
        layout.addWidget(config_group)
        layout.addStretch()
    
    def _connect_signals(self):
        """连接信号"""
        pass
    
    def get_config(self):
        """获取当前配置"""
        return {
            'codec': self.codec_combo.currentText().lower().replace('.', ''),
            'preset': self.preset_combo.currentText(),
            'crf': self.crf_spinbox.value(),
            'bitrate': self.bitrate_spinbox.value(),
            'framerate': self.framerate_spinbox.value(),
            'resolution': (self.width_spinbox.value(), self.height_spinbox.value()),
            'hardware_acceleration': self.hw_accel_checkbox.isChecked()
        }
    
    def set_config(self, config: dict):
        """设置配置"""
        if 'codec' in config:
            codec_text = config['codec'].upper()
            if 'H264' in codec_text:
                codec_text = 'H.264'
            elif 'H265' in codec_text or 'HEVC' in codec_text:
                codec_text = 'H.265/HEVC'
            elif 'VP9' in codec_text:
                codec_text = 'VP9'
            elif 'AV1' in codec_text:
                codec_text = 'AV1'
            index = self.codec_combo.findText(codec_text)
            if index >= 0:
                self.codec_combo.setCurrentIndex(index)
        
        if 'preset' in config:
            index = self.preset_combo.findText(config['preset'])
            if index >= 0:
                self.preset_combo.setCurrentIndex(index)
        
        if 'crf' in config:
            self.crf_spinbox.setValue(config['crf'])
        
        if 'bitrate' in config:
            self.bitrate_spinbox.setValue(config['bitrate'])
        
        if 'framerate' in config:
            self.framerate_spinbox.setValue(config['framerate'])
        
        if 'resolution' in config and len(config['resolution']) >= 2:
            width, height = config['resolution']
            self.width_spinbox.setValue(width)
            self.height_spinbox.setValue(height)
        
        if 'hardware_acceleration' in config:
            self.hw_accel_checkbox.setChecked(config['hardware_acceleration'])