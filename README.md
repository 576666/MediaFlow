# MediaFlow - 高性能媒体批处理工具

![License](https://img.shields.io/badge/license-MIT-blue.svg)

MediaFlow 是一个现代化的高性能照片和视频批处理工具，专为摄影师和内容创作者设计。它提供直观的图形界面，支持对图像（包括RAW文件）、视频或混合媒体进行批量操作。

## ✨ 功能特点

- 🚀 **高性能渲染**：使用PyQtGraph实现GPU加速的实时图像/视频渲染
- 📁 **文件夹管理**：轻松管理和浏览多个媒体文件夹
- 🔧 **插件化架构**：通过插件系统扩展处理功能
- ⚡ **异步处理**：非阻塞任务队列，确保UI流畅响应
- 💻 **跨平台**：支持Windows、macOS和Linux操作系统
- 🌐 **现代化UI**：基于PySide6的现代化图形用户界面
- 📊 **质量分析**：内置PSNR、SSIM等质量评估指标
- 🎛️ **硬件加速**：支持NVIDIA NVENC等硬件编码加速

## 🛠️ 技术栈

- **GUI框架**：PySide6 (Qt6)
- **高性能渲染**：PyQtGraph
- **图表可视化**：Matplotlib
- **视频编解码**：FFmpeg-python + PyNvVideoCodec (可选)
- **图像处理**：OpenCV-Python + Pillow
- **架构模式**：MVVM (Model-View-ViewModel)

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py
```

## 🏗️ 项目架构

```
MediaFlow/
├── core/                  # 核心处理逻辑
│   ├── engine/            # 引擎相关 (视频、编解码、质量分析)
│   ├── models/            # 数据模型 (任务、配置、质量指标)
│   └── services/          # 服务 (任务队列、插件管理器)
├── plugins/               # 插件系统
│   ├── base_processor.py  # 处理器基类
│   ├── video_compressors/ # 视频压缩插件
│   ├── image_processors/  # 图像处理插件
│   ├── batch_operations/  # 批量操作插件
│   └── analyzers/         # 分析插件
├── ui/                    # 用户界面
│   ├── widgets/           # 自定义控件 (对比、图表、进度等)
│   ├── windows/           # 窗口模块 (主窗口、预览窗口等)
│   └── viewmodels/        # 视图模型 (MVVM中的ViewModel)
├── config/                # 配置管理
├── main.py                # 应用入口点
└── mediaflow_config.json  # 配置文件
```

## 🎯 核心功能

### 1. 预览-批量工作流
- **5秒预览**：快速预览处理效果，无需等待完整处理
- **实时对比**：左右分屏实时对比原始和处理后视频
- **质量分析**：PSNR、SSIM等质量指标实时显示

### 2. 任务管理系统
- **优先级队列**：支持任务优先级管理
- **进度反馈**：实时任务进度和状态更新
- **并发处理**：多任务并行处理，充分利用CPU资源

### 3. 插件系统
- **热插拔**：支持运行时加载/卸载插件
- **标准化接口**：统一的处理器接口，易于扩展
- **配置面板**：每个插件自带配置UI

## 🎨 界面特色

- **现代化设计**：采用现代化UI设计理念
- **响应式布局**：适应不同屏幕尺寸
- **暗色主题**：减少视觉疲劳，适合长时间使用
- **直观操作**：符合用户习惯的操作流程

## 🔌 插件开发

创建新插件只需继承BaseProcessor类并实现相应方法：

```python
from plugins.base_processor import BaseProcessor

class MyCustomProcessor(BaseProcessor):
    @property
    def name(self) -> str:
        return "我的处理器"
    
    @property
    def description(self) -> str:
        return "处理器描述"
    
    def process_task(self, task):
        # 实现处理逻辑
        pass
```

## 🔧 配置选项

应用支持丰富的配置选项，可通过`mediaflow_config.json`进行自定义：
- 硬件加速设置
- 任务并发数量
- 缓存大小
- UI主题和布局

## 📈 性能优化

- **GPU加速**：利用GPU进行图像渲染和视频处理
- **内存管理**：智能内存池，避免内存泄漏
- **并行处理**：多线程任务执行
- **缓存机制**：智能缓存，减少重复计算

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件