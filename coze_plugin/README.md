# Coze Plugin 子项目

这是一个专门为 Coze 平台设计的插件子项目，包含所有 Coze 工具函数。

## 目录结构

```
coze_plugin/
├── README.md                   # 本文档
├── tools/                     # 手工编写的 Coze 工具函数集合
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
├── raw_tools/                 # 自动生成的工具函数集合（由 scripts/generate_handler_from_api.py 生成）
│   ├── create_draft/          # 创建草稿工具
│   ├── add_track/             # 添加轨道工具
│   ├── add_segment/           # 添加段工具
│   ├── create_*_segment/      # 创建各类段工具（audio, video, text, sticker, effect, filter）
│   ├── add_*_effect/          # 添加各类效果工具（audio, video）
│   ├── add_*_fade/            # 添加淡入淡出工具（audio, video）
│   ├── add_*_keyframe/        # 添加关键帧工具（audio, video, text, sticker）
│   ├── add_*_animation/       # 添加动画工具（video, text）
│   └── ... (共 28 个工具)
├── export_script/             # 导出脚本工具
│   ├── handler.py            # 导出 /tmp/coze2jianying.py 的工具
│   └── README.md             # 工具文档
└── write_script/              # 写入脚本工具
    ├── handler.py            # 向 /tmp/coze2jianying.py 写入内容的工具
    └── README.md             # 工具文档
```

## 模块说明

### tools/
包含手工编写的 Coze 平台可调用的工具函数。每个工具都是独立的模块，包含：
- `handler.py` - 工具的主处理函数
- `README.md` - 工具的使用文档

这些工具提供了高级的剪映草稿操作接口。

### raw_tools/
包含从 API 端点自动生成的 Coze 工具函数。这些工具由 `scripts/generate_handler_from_api.py` 脚本自动生成，提供了更底层的 API 访问能力。

每个工具都包含：
- `handler.py` - 自动生成的处理函数
- `README.md` - 自动生成的文档

### export_script/
提供脚本导出功能的工具，用于实验性的脚本生成方案。从 `/tmp/coze2jianying.py` 读取脚本内容。

### write_script/
提供脚本写入功能的工具，用于向 `/tmp/coze2jianying.py` 追加内容。采用与 `raw_tools` 相同的实现方式，与 `export_script` 配合使用实现完整的脚本生成和导出流程。

## 作为子项目的角色

`coze_plugin` 是整个项目的一个独立子项目，专注于：
1. **Coze 平台集成** - 所有与 Coze 平台交互的工具和接口
2. **工具函数实现** - 实现符合 Coze 规范的 handler 函数
3. **核心功能封装** - 提供剪映草稿操作的核心功能
4. **测试覆盖** - 完整的测试套件确保功能稳定性

## 使用方式

### 在 Coze 平台使用
每个工具都设计为可在 Coze 平台上独立部署和使用。将工具目录下的 `handler.py` 内容复制到 Coze IDE 中即可。

### 单独使用工具
```python
# 导入具体工具的 handler 函数
from coze_plugin.tools.create_draft.handler import handler as create_draft
from coze_plugin.tools.export_drafts.handler import handler as export_drafts
```

## 开发指南

在 `coze_plugin` 子项目中开发时，请遵循：
1. 每个工具函数保持独立性
2. 遵循 Coze 平台的工具函数规范
3. 保持向后兼容性
4. 详细记录工具的使用方法
5. 为新功能添加测试

### 运行测试
```bash
# 从项目根目录运行单个测试
python coze_plugin/tests/test_basic.py

# 运行所有测试
python -m pytest coze_plugin/tests/
```

### 生成 raw_tools
```bash
# 从 API 端点自动生成工具
python scripts/generate_handler_from_api.py
```

## GitHub Releases

从每个 GitHub Release 中，您可以下载：
- **CozeJianYingDraftGenerator.exe** - 草稿生成器应用程序
- **coze_plugin.zip** - 包含所有 Coze 工具函数的压缩包

下载 `coze_plugin.zip` 后解压，即可获得所有可在 Coze 平台上部署的工具函数。

## 相关文档

- [主项目 README](../README.md)
- [工具函数文档](./tools/)
- [开发指南](../docs/guides/)
