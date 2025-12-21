# MediaFlow

![License](https://img.shields.io/badge/license-MIT-blue.svg)

MediaFlow 是一个可视化照片和视频批处理工具，专为摄影师和内容创作者设计。它提供直观的图形界面，支持对图像（包括RAW文件）、视频或混合媒体进行批量操作。

## 功能特点

- 🖼️ **多格式支持**：支持各种图片和视频格式，包括专业RAW格式
- 📁 **文件夹管理**：轻松管理和浏览多个媒体文件夹
- 🔧 **插件化架构**：通过插件系统扩展处理功能
- 💻 **跨平台**：支持Windows、macOS和Linux操作系统
- 🌐 **可视化界面**：直观易用的图形用户界面

## 快速开始

### 环境要求

- Python 3.6+
- PyQt5

### 安装步骤

1. 克隆项目代码：
   ```bash
   git clone <repository-url>
   cd MediaFlow
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 运行应用：
   ```bash
   python main.py
   ```

## 使用指南

1. 启动应用后，使用“文件”菜单或工具栏中的“添加文件夹”按钮添加要处理的媒体文件夹
2. 在左侧文件浏览器中选择需要处理的文件
3. 在右侧处理面板中选择合适的处理选项
4. 点击“开始处理”执行批处理操作

## 插件开发

MediaFlow采用插件化架构，允许开发者轻松添加新的处理功能。

### 创建新插件

1. 在`plugins`目录下创建新的Python文件
2. 继承[BaseProcessor](file:///D:/PythonProject/MediaFlow/plugins/base_processor.py#L12-L69)基类
3. 实现必要的属性和方法：
   - [name](file:///D:/PythonProject/MediaFlow/plugins/extension_upper_processor.py#L23-L24)：处理器名称
   - [description](file:///D:/PythonProject/MediaFlow/plugins/extension_upper_processor.py#L26-L27)：处理器描述
   - [process](file:///D:/PythonProject/MediaFlow/plugins/extension_upper_processor.py#L29-L47)：单个文件处理逻辑

参考[ExtensionUpperProcessor](file:///D:/PythonProject/MediaFlow/plugins/extension_upper_processor.py#L12-L47)示例了解详细实现。

## 项目结构

```
MediaFlow/
├── core/              # 核心处理逻辑
├── plugins/           # 插件目录
├── ui/                # 用户界面
├── main.py            # 应用入口点
└── mediaflow_config.json  # 配置文件
```

## 许可证

本项目采用MIT许可证，详情请参阅[LICENSE](file:///D:/PythonProject/MediaFlow/LICENSE)文件。
