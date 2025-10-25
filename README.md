# 开源的Coze剪映小助手

一个基于 [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft) 构建的剪映草稿生成工具，专为 Coze 平台设计。

## 项目概述

本项目是 **Coze 到剪映自动化视频生成工作流** 中的关键组件，提供了完整的 Coze 插件工具函数，用于处理剪映草稿的创建、管理和导出。

### 核心工作流程

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│  Coze 工作流 │───▶│ Coze插件     │───▶│ 草稿生成器   │───▶│    剪映     │
│ (AI内容生成) │    │ (本项目)     │    │ (JSON转换)   │    │ (视频编辑)   │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
```

## 特性

- 🎬 **完整的剪映草稿管理** - 基于 UUID 的草稿生成、存储和导出系统
- 🔗 **网络资源处理** - 支持 Coze 平台的网络链接资源模式
- ⏱️ **媒体时长分析** - 自动获取音视频文件时长和时间轴计算
- 📊 **数据结构完备** - 覆盖 pyJianYingDraft 的所有可配置参数
- 🛠️ **Coze 平台优化** - 遵循 Coze 平台的约束和开发规范
- 🐍 **纯 Python 实现** - 易于扩展和自定义

## 安装

### 从源码安装

1. 克隆仓库：
```bash
git clone https://github.com/Gardene-el/CozeJianYingAssistent.git
cd CozeJianYingAssistent
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 安装项目：
```bash
pip install -e .
```

## 核心功能

### 已实现的 Coze 工具函数

#### 1. create_draft - 创建剪映草稿
创建基础的剪映项目草稿，支持分辨率、帧率、质量等全面配置。

#### 2. export_drafts - 导出草稿数据  
将草稿导出为标准化 JSON 格式，支持单个和批量导出。

#### 3. get_media_duration - 获取媒体时长
分析音视频链接，计算时长和时间轴信息，支持累积时间轴计算。

### Coze 工作流示例

#### 创建草稿
```json
{
  "tool": "create_draft",
  "input": {
    "draft_name": "我的视频项目",
    "width": 1920,
    "height": 1080,
    "fps": 30
  }
}
```

#### 导出草稿
```json
{
  "tool": "export_drafts", 
  "input": {
    "draft_ids": "{{draft.draft_id}}",
    "remove_temp_files": true
  }
}
```

### Python 开发使用
```python
# 测试数据结构
from data_structures.draft_generator_interface.models import DraftConfig

# 运行测试
python tests/test_basic.py
```

## 依赖项目

本项目基于以下开源项目构建：

- [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft) - 轻量、灵活、易上手的Python剪映草稿生成及导出工具

## 开发

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python tests/test_basic.py
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
CozeJianYingAssistent/
├── coze_plugin/               # 🔌 Coze 插件子项目
│   ├── __init__.py            # 子项目初始化
│   ├── README.md              # 子项目说明文档
│   ├── coze_jianying_assistant/  # 核心助手模块
│   │   ├── __init__.py        # 包初始化文件
│   │   └── main.py            # 主程序入口
│   └── tools/                 # Coze 工具函数脚本
│       ├── create_draft/      # 创建草稿工具
│       ├── export_drafts/     # 导出草稿工具
│       ├── add_videos/        # 添加视频工具
│       ├── add_audios/        # 添加音频工具
│       ├── add_images/        # 添加图片工具
│       └── [更多工具...]
├── data_structures/           # 数据结构定义
│   ├── draft_generator_interface/  # 草稿生成器接口
│   └── media_models/          # 媒体文件模型
├── docs/                      # 📚 项目文档
│   ├── guides/                # 开发与使用指南
│   ├── updates/               # 功能更新记录
│   ├── analysis/              # 技术分析报告
│   └── reference/             # API 参考文档
├── examples/                  # 使用示例
│   ├── coze_workflow_examples/
│   └── json_output_samples/
├── tests/                     # 测试文件目录
├── requirements.txt           # 项目依赖
└── setup.py                  # 安装配置
```

## 许可证

本项目采用 GPL-3.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！
