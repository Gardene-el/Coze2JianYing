# Coze Plugin 子项目

这是一个专门为 Coze 平台设计的插件子项目，包含所有 Coze 工具函数和核心助手功能。

## 目录结构

```
coze_plugin/
├── __init__.py                 # 子项目初始化文件
├── README.md                   # 本文档
├── main.py                     # 核心助手类和主程序入口
├── tools/                     # Coze 工具函数集合
│   ├── create_draft/          # 创建草稿工具
│   ├── export_drafts/         # 导出草稿工具
│   ├── add_videos/            # 添加视频工具
│   ├── add_audios/            # 添加音频工具
│   ├── add_images/            # 添加图片工具
│   ├── add_captions/          # 添加字幕工具
│   ├── add_effects/           # 添加特效工具
│   ├── get_media_duration/    # 获取媒体时长工具
│   ├── make_video_info/       # 创建视频信息工具
│   ├── make_audio_info/       # 创建音频信息工具
│   ├── make_image_info/       # 创建图片信息工具
│   ├── make_caption_info/     # 创建字幕信息工具
│   └── make_effect_info/      # 创建特效信息工具
├── examples/                  # 工具使用示例和演示
│   ├── add_videos_demo.py     # 视频添加工具演示
│   ├── add_audios_demo.py     # 音频添加工具演示
│   ├── add_images_demo.py     # 图片添加工具演示
│   ├── add_captions_demo.py   # 字幕添加工具演示
│   ├── make_*_info_demo.py    # make 系列工具演示
│   ├── coze_workflow_examples/  # Coze 工作流示例
│   └── json_output_samples/   # JSON 输出示例
└── tests/                     # 测试文件集合
    ├── test_basic.py          # 基础功能测试
    ├── test_tools.py          # 工具函数集成测试
    ├── test_add_*.py          # add 系列工具测试
    └── test_make_*.py         # make 系列工具测试
```

## 模块说明

### main.py
核心助手模块，提供 `Coze2JianYing` 类和 `main()` 入口函数，封装剪映草稿的基础操作。

### tools/
包含所有 Coze 平台可调用的工具函数。每个工具都是独立的模块，包含：
- `handler.py` - 工具的主处理函数
- `README.md` - 工具的使用文档

### examples/
包含工具使用示例和工作流演示：
- `add_*_demo.py` - 各种 add 工具的完整使用演示
- `make_*_info_demo.py` - 各种 make 工具的参数配置演示
- `coze_workflow_examples/` - 在 Coze 工作流中的使用示例
- `json_output_samples/` - 标准 JSON 输出格式示例

### tests/
包含完整的测试套件：
- 基础功能测试 (`test_basic.py`)
- 工具集成测试 (`test_tools.py`)
- 各工具的单元测试 (`test_add_*.py`, `test_make_*.py`)
- 修复验证测试 (验证特定问题的修复)

## 作为子项目的角色

`coze_plugin` 是整个项目的一个独立子项目，专注于：
1. **Coze 平台集成** - 所有与 Coze 平台交互的工具和接口
2. **工具函数实现** - 实现符合 Coze 规范的 handler 函数
3. **核心功能封装** - 提供剪映草稿操作的核心功能
4. **示例和测试** - 完整的使用示例和测试覆盖

## 使用方式

### 作为子项目导入
```python
from coze_plugin import Coze2JianYing, main
```

### 单独使用工具
```python
from coze_plugin.tools.create_draft.handler import handler as create_draft
from coze_plugin.tools.export_drafts.handler import handler as export_drafts
```

## 开发指南

在 `coze_plugin` 子项目中开发时，请遵循：
1. 每个工具函数保持独立性
2. 遵循 Coze 平台的工具函数规范
3. 保持向后兼容性
4. 详细记录工具的使用方法
5. 为新功能添加测试和示例

### 运行测试
```bash
# 从项目根目录运行
python coze_plugin/tests/test_basic.py

# 运行所有测试
python -m pytest coze_plugin/tests/
```

### 查看示例
```bash
# 运行工具演示
python coze_plugin/examples/add_videos_demo.py

# 查看工作流示例
cat coze_plugin/examples/coze_workflow_examples/draft_management_example.py
```

## 相关文档

- [主项目 README](../README.md)
- [工具函数文档](./tools/)
- [开发指南](../docs/guides/)
