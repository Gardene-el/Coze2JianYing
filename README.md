# 
<h1 align="center">
<a>开源的Coze剪映小助手：Coze2JianYing</a>
</h1>

## 项目概述

<p>
Coze2JianYing搭建了从Coze平台到剪映草稿的工作流，包含Coze插件与草稿生成软件。Coze2JianYing遵循 GPL-3.0 许可证，将所有源码<b>按原样</b>提供，此外也提供立即可用的服务形式。Coze2JianYing是一个个人项目，并主要依赖AI生成，难免存在许多粗陋之处，请多海涵，同时，欢迎质量监督。目前项目仍处于非常早期的阶段，当前仅确定支持对字幕，音效和图片进行最基本的添加和参数设置，不支持效果和关键帧。
</p>

### 完整工作流程

```
Coze平台│──生成素材和设置草稿的参数───▶Coze 插件（本项目提供）│──导出草稿的内容───▶草稿生成器（本项目提供）│──生成剪影草稿至草稿文件夹───▶剪映

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
- 📊 **数据结构完备** - 覆盖 pyJianYingDraft 的所有可配置参数
- 🖥️ **GUI 应用** - 草稿生成器提供友好的图形界面
- 📦 **可打包发布** - 支持打包为 Windows exe 可执行文件


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

## 许可证

本项目采用 GPL-3.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！
