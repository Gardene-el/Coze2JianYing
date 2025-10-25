# 导出草稿完整参数列表

本文档列出通过 `export_drafts` 函数导出的所有参数。

## 概述

`export_drafts` 工具从 `/tmp/jianying_assistant/drafts/` 目录读取草稿配置文件（`draft_config.json`），并将其包装成标准化的 JSON 格式供草稿生成器使用。

## 导出 JSON 结构

### 顶层参数（由 export_drafts 添加）

这些参数由 `export_drafts` 工具在导出时添加，用于标识导出格式和内容：

| 参数名 | 类型 | 说明 | 可能的值 |
|--------|------|------|----------|
| `format_version` | string | 导出格式版本 | "1.0" |
| `export_type` | string | 导出类型 | "single_draft" 或 "batch_draft" |
| `draft_count` | number | 导出的草稿数量 | 正整数 |
| `drafts` | array | 草稿对象数组 | 见下文"草稿对象参数" |

### 草稿对象参数（来自 draft_config.json）

每个草稿对象包含以下参数，这些参数在创建草稿时初始化，并在后续操作中更新：

#### 顶层草稿参数

| 参数名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| `draft_id` | string | 草稿的唯一标识符（UUID 格式） | "123e4567-e89b-12d3-a456-426614174000" |
| `project` | object | 项目配置对象 | 见下文 |
| `media_resources` | array | 媒体资源列表（当前未使用，保留用于未来扩展） | [] |
| `tracks` | array | 轨道配置数组 | 见下文 |
| `created_timestamp` | number | 创建时间戳（Unix 时间，浮点数） | 1703123456.789 |
| `last_modified` | number | 最后修改时间戳（Unix 时间，浮点数） | 1703123456.789 |
| `status` | string | 草稿状态 | "created" |

#### project 对象参数

| 参数名 | 类型 | 说明 | 默认值 | 约束 |
|--------|------|------|--------|------|
| `name` | string | 项目名称 | "Coze剪映项目" | - |
| `width` | number | 视频宽度（像素） | 1920 | > 0 |
| `height` | number | 视频高度（像素） | 1080 | > 0 |
| `fps` | number | 帧率 | 30 | 1-120 |

#### tracks 数组元素参数

每个轨道对象包含以下参数：

| 参数名 | 类型 | 说明 | 可能的值 |
|--------|------|------|----------|
| `track_type` | string | 轨道类型 | "video", "audio", "text", "sticker", "effect", "filter" |
| `muted` | boolean | 是否静音（主要用于音频轨道） | true/false |
| `volume` | number | 音量（0.0-1.0，主要用于音频轨道） | 0.0-1.0 |
| `segments` | array | 段配置数组，内容取决于轨道类型 | 见下文 |

#### segments 数组元素参数

段的具体参数取决于段类型。以下是各种段类型的参数：

##### 视频段 (type: "video")

基础参数：
- `type`: "video"
- `material_url`: 视频文件 URL
- `time_range`: {start: number, end: number}
- `material_range`: {start: number, end: number} 或 null

变换参数（transform 对象）：
- `position_x`, `position_y`: 位置
- `scale_x`, `scale_y`: 缩放
- `rotation`: 旋转角度
- `opacity`: 不透明度

裁剪参数（crop 对象）：
- `enabled`: 是否启用裁剪
- `left`, `top`, `right`, `bottom`: 裁剪范围

特效参数（effects 对象）：
- `filter_type`: 滤镜类型
- `filter_intensity`: 滤镜强度
- `transition_type`: 转场类型
- `transition_duration`: 转场时长

速度参数（speed 对象）：
- `speed`: 播放速度
- `reverse`: 是否倒放

音频参数（audio 对象）：
- `volume`: 音量
- `change_pitch`: 是否保持音调

背景参数（background 对象）：
- `blur`: 背景模糊
- `color`: 背景颜色

关键帧参数（keyframes 对象）：
- `position`, `scale`, `rotation`, `opacity`: 各种关键帧数组

##### 音频段 (type: "audio")

基础参数：
- `type`: "audio"
- `material_url`: 音频文件 URL
- `time_range`: {start: number, end: number}
- `material_range`: {start: number, end: number} 或 null

音频参数（audio 对象）：
- `volume`: 音量
- `fade_in`: 淡入时长（毫秒）
- `fade_out`: 淡出时长（毫秒）
- `effect_type`: 音效类型
- `effect_intensity`: 音效强度
- `speed`: 播放速度
- `change_pitch`: 是否保持音调

关键帧参数（keyframes 对象）：
- `volume`: 音量关键帧数组

##### 图片段 (type: "image")

基础参数：
- `type`: "image"
- `material_url`: 图片文件 URL
- `time_range`: {start: number, end: number}

变换参数、裁剪参数、特效参数、背景参数、关键帧参数：与视频段类似

额外参数：
- `dimensions`: {width: number, height: number}
- `animations`: {intro, intro_duration, outro, outro_duration}

##### 文本段 (type: "text")

基础参数：
- `type`: "text"
- `content`: 文本内容
- `time_range`: {start: number, end: number}

变换参数（transform 对象）：
- `position_x`, `position_y`: 位置（归一化 0-1）
- `scale`: 缩放
- `rotation`: 旋转角度
- `opacity`: 不透明度

样式参数（style 对象）：
- `font_family`: 字体
- `font_size`: 字号
- `font_weight`: 字重
- `font_style`: 字形
- `color`: 颜色
- `stroke`: 描边设置
- `shadow`: 阴影设置
- `background`: 背景设置

对齐和动画参数：
- `alignment`: 对齐方式
- `animations`: {intro, outro, loop}

关键帧参数（keyframes 对象）：与视频段类似

##### 特效段 (type: "effect")

参数：
- `type`: "effect"
- `effect_type`: 特效类型
- `time_range`: {start: number, end: number}
- `properties`: {intensity, position_x, position_y, scale, ...}

##### 滤镜段 (type: "filter")

参数：
- `type`: "filter"
- `filter_type`: 滤镜类型
- `time_range`: {start: number, end: number}
- `intensity`: 强度（0-1）

##### 贴纸段 (type: "sticker")

参数：
- `type`: "sticker"
- `resource_id`: 贴纸资源 ID
- `time_range`: {start: number, end: number}
- `transform`: 变换参数
- `flip`: {horizontal, vertical}
- `keyframes`: 关键帧参数

## 已移除的参数

### total_duration_ms

**状态**: ❌ 已移除

**原因**: 该参数不应出现在草稿配置中。时长信息应该从各个段的 `time_range` 计算得出，而不是作为独立参数存储。

**移除位置**:
- `coze_plugin/tools/create_draft/handler.py` - 初始草稿配置
- `data_structures/draft_generator_interface/models.py` - DraftConfig 类
- 所有测试文件和示例
- 相关文档

**注意**: `data_structures/media_models/models.py` 中的 `MediaDurationResult.total_duration_ms` 是不同的参数，用于媒体时长分析结果，已保留。

## 数据流程

```
create_draft 工具
  ↓ 创建初始 draft_config.json
  {draft_id, project, media_resources=[], tracks=[], 
   created_timestamp, last_modified, status}
  ↓
add_videos/add_audios/add_images/add_captions 等工具
  ↓ 更新 draft_config.json，添加 tracks
  {draft_id, project, media_resources, tracks=[...], 
   created_timestamp, last_modified, status}
  ↓
export_drafts 工具
  ↓ 读取并包装为标准格式
  {format_version, export_type, draft_count, 
   drafts=[{draft_config...}]}
  ↓
草稿生成器（外部项目）
```

## 示例：完整的导出 JSON

```json
{
  "format_version": "1.0",
  "export_type": "single_draft",
  "draft_count": 1,
  "drafts": [
    {
      "draft_id": "123e4567-e89b-12d3-a456-426614174000",
      "project": {
        "name": "示例项目",
        "width": 1920,
        "height": 1080,
        "fps": 30
      },
      "media_resources": [],
      "tracks": [
        {
          "track_type": "video",
          "muted": false,
          "volume": 1.0,
          "segments": [
            {
              "type": "video",
              "material_url": "https://example.com/video.mp4",
              "time_range": {"start": 0, "end": 30000},
              "material_range": null,
              "transform": {
                "position_x": 0.0,
                "position_y": 0.0,
                "scale_x": 1.0,
                "scale_y": 1.0,
                "rotation": 0.0,
                "opacity": 1.0
              },
              "crop": {
                "enabled": false,
                "left": 0.0,
                "top": 0.0,
                "right": 1.0,
                "bottom": 1.0
              },
              "effects": {
                "filter_type": null,
                "filter_intensity": 1.0,
                "transition_type": null,
                "transition_duration": 500
              },
              "speed": {
                "speed": 1.0,
                "reverse": false
              },
              "audio": {
                "volume": 1.0,
                "change_pitch": false
              },
              "background": {
                "blur": false,
                "color": null
              },
              "keyframes": {
                "position": [],
                "scale": [],
                "rotation": [],
                "opacity": []
              }
            }
          ]
        }
      ],
      "created_timestamp": 1703123456.789,
      "last_modified": 1703123456.789,
      "status": "created"
    }
  ]
}
```

## 参数验证

### 必需参数

以下参数在导出时必须存在：
- `draft_id`: 必须是有效的 UUID 格式
- `project`: 必须包含 name, width, height, fps
- `tracks`: 可以为空数组，但必须存在
- `created_timestamp`: 必须是有效的时间戳
- `last_modified`: 必须是有效的时间戳

### 可选参数

以下参数可以为空或使用默认值：
- `media_resources`: 当前未使用，可以为空数组
- `status`: 默认为 "created"
- 各段的特效、滤镜等参数：可以为 null 或使用默认值

## 版本历史

- **1.0** (当前版本):
  - 移除了 `total_duration_ms` 参数
  - 确立了标准的导出格式
  - 支持 video, audio, image, text, sticker, effect, filter 七种段类型
