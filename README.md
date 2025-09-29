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

#### 草稿管理工具

#### 1. create_draft - 创建剪映草稿
创建基础的剪映项目草稿，支持分辨率、帧率、质量等全面配置。

#### 2. export_drafts - 导出草稿数据  
将草稿导出为标准化 JSON 格式，支持单个和批量导出。

#### 3. get_media_duration - 获取媒体时长
分析音视频链接，计算时长和时间轴信息，支持累积时间轴计算。

#### 内容添加工具

#### 4. add_videos - 添加视频轨道
将视频内容添加到草稿，创建新的视频轨道，支持滤镜、转场、音量控制。

#### 5. add_audios - 添加音频轨道
将音频内容添加到草稿，创建新的音频轨道，支持音量、淡入淡出、音效处理。

#### 6. add_captions - 添加字幕轨道
将文本字幕添加到草稿，创建新的文本轨道，支持字体、颜色、位置定制。

#### 7. add_images - 添加图片轨道
将图片内容添加到草稿，创建新的视频轨道，支持时长、位置、缩放、转场。

#### 8. add_effects - 添加特效轨道
将视觉特效添加到草稿，创建新的特效轨道，支持光效、粒子、动态效果。

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

#### 添加视频内容
```json
{
  "tool": "add_videos",
  "input": {
    "draft_id": "{{draft.draft_id}}",
    "video_urls": ["https://example.com/video1.mp4"],
    "filters": ["暖冬"],
    "transitions": ["淡化"]
  }
}
```

#### 添加字幕
```json
{
  "tool": "add_captions",
  "input": {
    "draft_id": "{{draft.draft_id}}",
    "captions": [
      {
        "text": "欢迎使用Coze剪映助手",
        "start_time": 0,
        "end_time": 3000
      }
    ]
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

## 项目结构

```
CozeJianYingAssistent/
├── coze_jianying_assistant/    # 主包目录
│   ├── __init__.py            # 包初始化文件
│   └── main.py                # 主程序入口
├── tools/                     # Coze 工具函数脚本
│   ├── create_draft/          # 创建草稿工具
│   │   ├── handler.py
│   │   └── README.md
│   ├── export_drafts/         # 导出草稿工具
│   │   ├── handler.py
│   │   └── README.md
│   ├── get_media_duration/    # 媒体时长工具
│   │   ├── handler.py
│   │   └── README.md
│   ├── add_videos/            # 添加视频轨道工具
│   │   ├── handler.py
│   │   └── README.md
│   ├── add_audios/            # 添加音频轨道工具
│   │   ├── handler.py
│   │   └── README.md
│   ├── add_captions/          # 添加字幕轨道工具
│   │   ├── handler.py
│   │   └── README.md
│   ├── add_images/            # 添加图片轨道工具
│   │   ├── handler.py
│   │   └── README.md
│   └── add_effects/           # 添加特效轨道工具
│       ├── handler.py
│       └── README.md
├── data_structures/           # 数据结构定义
│   ├── draft_generator_interface/  # 草稿生成器接口
│   │   ├── models.py
│   │   └── README.md
│   └── media_models/          # 媒体文件模型
│       ├── models.py
│       └── README.md
├── examples/                  # 使用示例
│   ├── coze_workflow_examples/
│   └── json_output_samples/
├── tests/                     # 测试文件目录
│   ├── test_basic.py         # 基础功能测试
│   ├── test_tools.py         # 工具函数测试
│   └── [其他测试文件...]
├── requirements.txt           # 项目依赖
├── setup.py                  # 安装配置
├── DRAFT_MANAGEMENT_GUIDE.md # 草稿管理指南
└── README.md                 # 项目说明
```

## 许可证

本项目采用 GPL-3.0 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！
