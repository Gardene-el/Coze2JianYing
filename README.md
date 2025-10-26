# Coze2JianYing - Coze 到剪映完整工作流

一个基于 [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft) 构建的完整工作流项目，专为 Coze 平台设计，包含从 Coze 插件到剪映草稿生成的全流程。

## 项目概述

本项目整合了 **Coze 到剪映自动化视频生成工作流** 中的两个核心组件，在同一 GitHub 项目中管理两个强关联但相对独立的子项目。

### 完整工作流程

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────┐
│  Coze 工作流 │───▶│  Coze 插件       │───▶│ 草稿生成器       │───▶│    剪映     │
│ (AI内容生成) │    │ (coze_plugin/)   │    │ (src/)          │    │ (视频编辑)   │
│              │    │ 处理参数、导出JSON│    │ JSON转剪映草稿   │    │             │
└─────────────┘    └──────────────────┘    └─────────────────┘    └─────────────┘
```

### 项目组成

本项目包含两个主要子项目：

#### 1. **Coze 插件** (`coze_plugin/`)
- 处理 Coze 平台的参数和数据
- 基于 UUID 的草稿创建、管理和导出
- 网络资源处理和媒体时长分析
- 导出标准化 JSON 数据供草稿生成器使用

#### 2. **草稿生成器** (`src/`)  
- 从 JSON 数据生成剪映草稿文件
- GUI 界面和完整的日志系统
- 素材下载和管理
- 可打包为独立 exe 文件

## 特性

- 🎬 **完整的剪映草稿管理** - 基于 UUID 的草稿生成、存储和导出系统
- 🔗 **网络资源处理** - 支持 Coze 平台的网络链接资源模式
- ⏱️ **媒体时长分析** - 自动获取音视频文件时长和时间轴计算
- 📊 **数据结构完备** - 覆盖 pyJianYingDraft 的所有可配置参数
- 🛠️ **Coze 平台优化** - 遵循 Coze 平台的约束和开发规范
- 🐍 **纯 Python 实现** - 易于扩展和自定义
- 🔌 **模块化设计** - 两个子项目相对独立，易于维护
- 🖥️ **GUI 应用** - 草稿生成器提供友好的图形界面
- 📦 **可打包发布** - 支持打包为 Windows exe 可执行文件

> 📢 **项目架构更新**: 项目已完成重大架构调整，整合了 Coze 插件和草稿生成器两个子项目。详见 [草稿生成器架构文档](./docs/draft_generator/ARCHITECTURE_AND_WORKFLOW.md)。

## 安装

### 从源码安装

1. 克隆仓库：
```bash
git clone https://github.com/Gardene-el/Coze2JianYing.git
cd Coze2JianYing
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 安装项目：
```bash
pip install -e .
```

## 使用说明

### 使用 Coze 插件 (coze_plugin/)

#### 在 Coze 平台使用

参考 `coze_plugin/` 目录下的工具函数，将它们部署到 Coze 平台上：

1. **create_draft** - 创建剪映草稿
2. **export_drafts** - 导出草稿数据  
3. **get_media_duration** - 获取媒体时长

详细使用方法见 [Coze 插件 README](./coze_plugin/README.md)

#### Python 开发测试

```python
# 测试数据结构
from data_structures.draft_generator_interface.models import DraftConfig

# 运行测试
python coze_plugin/tests/test_basic.py
```

### 使用草稿生成器 (src/)

#### GUI 模式（推荐）

```bash
# 运行图形界面
python src/main.py
```

#### 打包为 exe

```bash
# 打包成 Windows 可执行文件
python build.py
```

生成的 exe 文件将位于 `dist/` 目录。

详细使用方法见 [草稿生成器文档](./docs/draft_generator/)

## 项目结构

```
Coze2JianYing/
├── coze_plugin/              # Coze 插件子项目
│   ├── tools/                # 工具函数（create_draft, export_drafts 等）
│   ├── examples/             # 使用示例
│   ├── tests/                # 测试文件
│   └── main.py               # 核心助手类
├── src/                      # 草稿生成器主代码
│   ├── gui/                  # GUI 界面
│   ├── utils/                # 工具模块
│   │   ├── draft_generator.py    # 核心生成器
│   │   ├── coze_parser.py        # Coze 输出解析
│   │   ├── converter.py          # 数据转换
│   │   └── material_manager.py   # 素材管理
│   └── main.py               # GUI 应用入口
├── test_utils/               # 测试和转换工具
│   └── converters/           # 格式转换器
├── data_structures/          # 数据结构定义
│   ├── draft_generator_interface/  # 草稿生成器接口
│   └── media_models/         # 媒体文件模型
├── docs/                     # 文档目录
│   ├── guides/               # 使用指南
│   └── draft_generator/      # 草稿生成器文档
├── resources/                # 应用资源文件
├── build.py                  # PyInstaller 打包脚本
├── requirements.txt          # 项目依赖
└── setup.py                  # 安装配置
```

## 依赖项目

本项目基于以下开源项目构建：

- [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft) - 轻量、灵活、易上手的Python剪映草稿生成及导出工具

## 开发

### 运行测试
```bash
# 运行所有测试
python -m pytest coze_plugin/tests/

# 运行特定测试
python coze_plugin/tests/test_basic.py
```

### 贡献指南
欢迎提交 Issue 和 Pull Request！提交前请确保：
- 代码通过所有测试
- 遵循项目的代码风格
- 更新相关文档

## 📚 文档

完整的项目文档位于 [docs/](./docs/) 目录：

- **[开发指南](./docs/guides/)** - 项目开发历程和使用指南
- **[功能更新记录](./docs/updates/)** - 各功能模块的实现总结
- **[技术分析](./docs/analysis/)** - 深入的技术分析和审计报告
- **[API 参考](./docs/reference/)** - 参数列表和快速查询指南

推荐阅读：
- [项目开发历程](./docs/guides/DEVELOPMENT_ROADMAP.md) - 了解项目如何发展
- [草稿管理指南](./docs/guides/DRAFT_MANAGEMENT_GUIDE.md) - 学习如何使用草稿系统

## 项目结构

```
Coze2JianYing/
├── coze_plugin/               # 🔌 Coze 插件子项目
│   ├── __init__.py            # 子项目初始化
│   ├── README.md              # 子项目说明文档
│   ├── main.py                # 核心助手类和主程序入口
│   ├── tools/                 # Coze 工具函数脚本
│   │   ├── create_draft/      # 创建草稿工具
│   │   ├── export_drafts/     # 导出草稿工具
│   │   ├── add_videos/        # 添加视频工具
│   │   ├── add_audios/        # 添加音频工具
│   │   ├── add_images/        # 添加图片工具
│   │   └── [更多工具...]
│   ├── examples/              # 工具使用示例和工作流演示
│   │   ├── coze_workflow_examples/
│   │   └── json_output_samples/
│   └── tests/                 # 测试文件目录
├── data_structures/           # 数据结构定义
│   ├── draft_generator_interface/  # 草稿生成器接口
│   └── media_models/          # 媒体文件模型
├── docs/                      # 📚 项目文档
│   ├── guides/                # 开发与使用指南
│   ├── updates/               # 功能更新记录
│   ├── analysis/              # 技术分析报告
│   └── reference/             # API 参考文档
├── requirements.txt           # 项目依赖
└── setup.py                  # 安装配置
```

## 许可证

本项目采用 GPL-3.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！
