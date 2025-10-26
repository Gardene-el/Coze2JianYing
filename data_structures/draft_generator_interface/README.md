# Draft Generator Interface

草稿生成器接口数据模型，定义了传递给草稿生成器的完整数据结构。

## ⚠️ 重要：pyJianYingDraft 段类型映射关系

### pyJianYingDraft 类层次结构

```
BaseSegment (基类)
├── MediaSegment (媒体片段基类 - 不是直接使用的段类型)
│   ├── AudioSegment (音频片段) ✅
│   └── VisualSegment (视觉片段基类 - 不是直接使用的段类型)
│       ├── VideoSegment (视频片段 - 也用于图片!) ✅
│       ├── TextSegment (文本/字幕片段) ✅
│       └── StickerSegment (贴纸片段) ✅
├── EffectSegment (特效片段) ✅
└── FilterSegment (滤镜片段) ✅
```

### 本模块的配置类映射

| 本模块配置类 | pyJianYingDraft 类 | 说明 |
|------------|-------------------|------|
| `VideoSegmentConfig` | `VideoSegment` | 视频片段 |
| `AudioSegmentConfig` | `AudioSegment` | 音频片段 |
| `ImageSegmentConfig` | `VideoSegment` | ⚠️ 图片在剪映中作为静态视频处理! |
| `TextSegmentConfig` | `TextSegment` | 文本/字幕片段 |
| `StickerSegmentConfig` | `StickerSegment` | 贴纸片段 |
| `EffectSegmentConfig` | `EffectSegment` | 特效片段（独立轨道）|
| `FilterSegmentConfig` | `FilterSegment` | 滤镜片段（独立轨道）|

### 媒体资源引用方式

各段配置类通过 `material_url` 字段直接引用网络资源URL。资源类型从段类型推断：
- `VideoSegmentConfig.material_url` → 视频文件URL
- `AudioSegmentConfig.material_url` → 音频文件URL
- `ImageSegmentConfig.material_url` → 图片文件URL（在 pyJianYingDraft 中作为 VideoMaterial 处理）
- `StickerSegmentConfig.resource_id` → 贴纸资源ID

在草稿生成器（pyJianYingDraftImporter）中，这些 URL 会被下载为本地文件，然后传递给 pyJianYingDraft 的 Material 类：
- `VideoMaterial(path)` - 用于视频和图片
- `AudioMaterial(path)` - 用于音频

## 功能描述

本模块定义了用于在Coze插件和草稿生成器之间传递数据的标准化数据结构。这些模型包含了pyJianYingDraft支持的所有参数配置选项，但使用URL而不是本地文件路径来引用媒体资源。

### 本接口的作用

Draft Generator Interface 是 **Coze2JianYing** 项目和 **pyJianYingDraftImporter** 项目之间的数据交换协议。它的设计目标是：

1. **在 Coze 工作流中收集和组织所有草稿参数** - 包括媒体资源URL、时间轴配置、效果参数等
2. **提供标准化的 JSON 格式** - 便于序列化传输和存储
3. **桥接 Coze 平台和剪映生态** - 将网络资源（URL）和剪映草稿（本地文件）连接起来

## 核心设计原则

### 1. URL-based资源管理
- 所有媒体资源（视频、音频、图片、贴纸）使用URL形式
- 适配Coze平台的网络资源传递模式
- 支持各种网络媒体格式和来源

### 2. 完整参数覆盖
- 包含pyJianYingDraft的所有可配置参数
- 支持视频、音频、图片、文本、贴纸、特效、滤镜等所有段类型
- 涵盖变换、滤镜、转场、动画等所有效果

### 3. UUID草稿管理
- 使用UUID作为草稿唯一标识符
- 支持多草稿批量导出
- 临时文件管理和清理

## 数据结构概览

### 基础配置类

#### ProjectSettings
项目基本配置，包含分辨率、帧率等。

```python
@dataclass
class ProjectSettings:
    name: str = "Coze剪映项目"
    width: int = 1920
    height: int = 1080
    fps: int = 30
```

#### TimeRange
时间范围定义，以毫秒为单位。

```python
@dataclass
class TimeRange:
    start: int = 0
    end: int = 0
    
    @property
    def duration(self) -> int:
        return self.end - self.start
```

### 轨道段配置类

**媒体资源引用方式**: 所有段配置类通过 `material_url` 字段直接引用网络资源URL。资源类型从段类型推断（VideoSegment → 视频，AudioSegment → 音频，等）。

#### VideoSegmentConfig
视频段配置，对应 `pyJianYingDraft.VideoSegment`：

- **变换属性**: 位置、缩放、旋转、透明度
- **裁剪设置**: 裁剪区域定义
- **效果滤镜**: 滤镜类型、强度、转场效果
- **速度控制**: 播放速度、倒放、变调控制
- **音频控制**: 音量、变调控制
- **背景填充**: 模糊背景、纯色背景
- **关键帧动画**: 位置、缩放、旋转、透明度动画

#### AudioSegmentConfig
音频段配置，对应 `pyJianYingDraft.AudioSegment`：

- **音频属性**: 音量、淡入淡出
- **音频效果**: 效果类型、强度
- **速度控制**: 播放速度、变调控制
- **音量动画**: 音量关键帧

#### ImageSegmentConfig
图片段配置，⚠️ **对应 `pyJianYingDraft.VideoSegment`**（图片作为静态视频处理）：

- **变换属性**: 位置、缩放、旋转、透明度
- **裁剪设置**: 裁剪区域定义
- **效果滤镜**: 滤镜类型、强度、转场效果
- **背景填充**: 模糊背景、纯色背景、适应模式
- **动画效果**: 入场、出场动画
- **关键帧动画**: 位置、缩放、旋转、透明度动画

注意：移除了不适用于静态图片的参数（material_range, speed, reverse, volume）

#### TextSegmentConfig
文本段配置，对应 `pyJianYingDraft.TextSegment`：

- **位置变换**: 位置、缩放、旋转、透明度
- **文本样式**: 字体、颜色、描边、阴影、背景
- **对齐方式**: 左对齐、居中、右对齐
- **动画效果**: 入场、出场、循环动画
- **关键帧动画**: 完整的动画支持

#### StickerSegmentConfig
贴纸段配置，对应 `pyJianYingDraft.StickerSegment`：

- **变换属性**: 位置、缩放、旋转、透明度
- **翻转选项**: 水平翻转、垂直翻转
- **资源引用**: resource_id（从模板中获取）
- **关键帧动画**: 位置、缩放、旋转、透明度动画

注意：贴纸没有 source_timerange（素材裁剪范围）

#### EffectSegmentConfig
特效段配置，对应 `pyJianYingDraft.EffectSegment`（独立特效轨道）：

- **特效类型**: 特效名称和参数
- **特效属性**: 强度、位置、缩放
- **自定义属性**: 灵活的特效参数支持

注意：EffectSegment 放置在独立轨道上，作用域为全局

#### FilterSegmentConfig
滤镜段配置，对应 `pyJianYingDraft.FilterSegment`（独立滤镜轨道）：

- **滤镜类型**: 滤镜名称
- **强度控制**: 0-1 范围（对应剪映中的 0-100）

注意：FilterSegment 放置在独立滤镜轨道上

## 使用示例

### 轨道和段类型映射关系

**重要**: 每种轨道类型只接受特定的段类型（对应 pyJianYingDraft 的设计）：

| 轨道类型 | 接受的段类型 | 说明 |
|---------|------------|------|
| `video` | VideoSegmentConfig, ImageSegmentConfig | 图片作为静态视频放在 video 轨道上 |
| `audio` | AudioSegmentConfig | 音频轨道 |
| `text` | TextSegmentConfig | 文本/字幕轨道 |
| `sticker` | StickerSegmentConfig | 贴纸轨道 |
| `effect` | EffectSegmentConfig | 特效轨道（独立轨道） |
| `filter` | FilterSegmentConfig | 滤镜轨道（独立轨道） |

### 创建基本草稿配置

```python
from data_structures.draft_generator_interface.models import (
    DraftConfig, ProjectSettings, TrackConfig,
    VideoSegmentConfig, AudioSegmentConfig, TimeRange
)

# 创建项目设置
project = ProjectSettings(
    name="我的Coze项目",
    width=1920,
    height=1080,
    fps=30
)

# 创建视频轨道（包含视频片段）
video_segment = VideoSegmentConfig(
    material_url="https://example.com/video1.mp4",
    time_range=TimeRange(start=0, end=30000),
    filter_type="暖冬",
    filter_intensity=0.8,
    transition_type="淡化",
    transition_duration=1000
)

video_track = TrackConfig(
    track_type="video",  # video 轨道
    segments=[video_segment]  # 只能包含 VideoSegmentConfig 或 ImageSegmentConfig
)

# 创建音频轨道（包含音频片段）
audio_segment = AudioSegmentConfig(
    material_url="https://example.com/audio1.mp3",
    time_range=TimeRange(start=0, end=30000),
    volume=0.8
)

audio_track = TrackConfig(
    track_type="audio",  # audio 轨道
    segments=[audio_segment]  # 只能包含 AudioSegmentConfig
)

# 创建完整草稿配置
# 注意: tracks 是一个列表，可以包含任意数量和类型的轨道
# 这里展示了 video 和 audio 两种轨道，实际使用时可以根据需要添加更多轨道
draft_config = DraftConfig(
    project=project,
    tracks=[video_track, audio_track]  # 可以添加更多轨道: text_track, sticker_track, etc.
)

# 转换为JSON字符串
json_data = json.dumps(draft_config.to_dict(), ensure_ascii=False, indent=2)
```

### 图片放在视频轨道上

**重要**: pyJianYingDraft 没有独立的 image 轨道，图片作为静态视频放在 video 轨道上。

```python
from data_structures.draft_generator_interface.models import (
    ImageSegmentConfig, TimeRange
)

# 创建图片段（注意：图片段也是放在 video 轨道上的）
image_segment = ImageSegmentConfig(
    material_url="https://example.com/logo.png",
    time_range=TimeRange(start=0, end=5000),
    position_x=0.5,
    position_y=0.5,
    scale_x=0.5,
    scale_y=0.5,
    fit_mode="fit"
)

# 可以在同一个 video 轨道上混合视频和图片段
mixed_video_track = TrackConfig(
    track_type="video",  # 注意：track_type 是 "video" 不是 "image"
    segments=[video_segment, image_segment]  # video 轨道可以包含视频和图片
)
```

### 添加文本字幕

```python
from data_structures.draft_generator_interface.models import (
    TextSegmentConfig, TextStyle, TimeRange
)

# 创建文本样式
text_style = TextStyle(
    font_family="思源黑体",
    font_size=48,
    color="#FFFFFF",
    stroke_enabled=True,
    stroke_color="#000000",
    stroke_width=2
)

# 创建文本段
text_segment = TextSegmentConfig(
    content="欢迎使用Coze剪映助手",
    time_range=TimeRange(start=5000, end=10000),
    position_x=0.5,
    position_y=-0.9,
    style=text_style,
    intro_animation="淡入",
    outro_animation="淡出"
)

# 添加到文本轨道
text_track = TrackConfig(
    track_type="text",
    segments=[text_segment]
)
```

### 添加关键帧动画

```python
from data_structures.draft_generator_interface.models import KeyframeProperty

# 为视频段添加位置动画
position_keyframes = [
    KeyframeProperty(time=0, value={"x": 0, "y": 0}),
    KeyframeProperty(time=5000, value={"x": 100, "y": 50}),
    KeyframeProperty(time=10000, value={"x": 0, "y": 0})
]

video_segment.position_keyframes = position_keyframes

# 添加缩放动画
scale_keyframes = [
    KeyframeProperty(time=0, value={"x": 1.0, "y": 1.0}),
    KeyframeProperty(time=2500, value={"x": 1.2, "y": 1.2}),
    KeyframeProperty(time=5000, value={"x": 1.0, "y": 1.0})
]

video_segment.scale_keyframes = scale_keyframes
```

## Coze工具接口

### CreateDraftInput/Output
用于create_draft工具的输入输出类型定义。

### ExportDraftsInput/Output
用于export_drafts工具的输入输出类型定义。

## 支持的参数列表

### 滤镜类型 (FilterType)
支持pyJianYingDraft中的所有滤镜，包括：
- 基础滤镜：暖冬、冷蓝、复古、胶片等
- 风格滤镜：ins暗、复古工业、赛博朋克等
- 调色滤镜：增色、去灰、美肌等

### 转场类型 (TransitionType)
支持所有转场效果，包括：
- 基础转场：淡化、推移、擦除等
- 特效转场：旋转、爆闪、故障等
- 创意转场：星光、水波、燃烧等

### 文本动画
支持丰富的文本动画效果：
- 入场动画：淡入、飞入、弹出等
- 出场动画：淡出、飞出、缩小等
- 循环动画：闪烁、摇摆、跳动等

## 扩展性设计

### 灵活的属性系统
- 特效配置支持自定义属性字典
- 关键帧系统支持任意属性动画
- 样式系统可扩展新的文本效果

### 版本兼容性
- 结构化设计便于向后兼容
- 可选字段支持渐进式功能添加
- JSON序列化保证跨平台兼容

## 注意事项

### URL资源处理
- 所有媒体资源必须是有效的HTTP/HTTPS URL
- 建议包含文件格式和时长信息
- 支持签名URL和临时链接

### 时间单位
- 所有时间相关参数使用毫秒(ms)为单位
- 时间轴从0开始计算
- 支持负值用于预加载或延迟

### 坐标系统
- 位置坐标使用归一化值(0.0-1.0)
- (0,0)为左上角，(1,1)为右下角
- 支持超出范围的值用于离屏动画

### 性能考虑
- 合理控制关键帧数量
- 避免过于复杂的嵌套配置
- 建议单个草稿总时长不超过10分钟

这个数据结构设计为Coze工作流和草稿生成器之间提供了完整、标准化的数据交换接口，确保了剪映草稿生成的完整性和准确性。

---

## 使用 Draft Generator Interface 生成剪映草稿

本节详细说明如何使用 Draft Generator Interface 的数据结构配合 pyJianYingDraft 库生成实际的剪映草稿文件。

### 整体流程概述

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Draft Generator Interface                        │
│                   (JSON 数据 - 本项目输出)                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  pyJianYingDraftImporter 项目                        │
│  1. 解析 JSON 数据                                                  │
│  2. 下载 URL 资源到本地                                             │
│  3. 调用 pyJianYingDraft 生成草稿                                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     剪映草稿文件                                     │
│          (可直接在剪映应用中打开编辑)                                │
└─────────────────────────────────────────────────────────────────────┘
```

### 核心数据映射关系

#### 1. 项目配置映射

Draft Generator Interface → pyJianYingDraft

```python
# Draft Generator Interface (JSON)
{
  "project": {
    "name": "Coze剪映项目",
    "width": 1920,
    "height": 1080,
    "fps": 30
  }
}

# pyJianYingDraft 调用
from pyJianYingDraft import DraftFolder

draft_folder = DraftFolder("/path/to/JianyingPro Drafts")
script_file = draft_folder.create_draft(
    draft_name=project["name"],
    width=project["width"],
    height=project["height"],
    fps=project["fps"]
)
```

#### 2. 媒体资源映射

**关键差异**: Draft Generator Interface 使用 URL，pyJianYingDraft 需要本地文件路径

```python
# Draft Generator Interface (JSON)
{
  "media_resources": [
    {
      "url": "https://example.com/video.mp4",
      "resource_type": "video",
      "duration_ms": 30000,
      "filename": "video.mp4"
    }
  ]
}

# pyJianYingDraftImporter 必须先下载
import requests
from pyJianYingDraft import VideoMaterial

# 步骤 1: 下载 URL 到本地
local_path = download_media(resource["url"], resource["filename"])
# 例如: local_path = "/tmp/downloads/video.mp4"

# 步骤 2: 创建 Material 对象
if resource["resource_type"] == "video":
    material = VideoMaterial(local_path, material_name=resource["filename"])
elif resource["resource_type"] == "audio":
    material = AudioMaterial(local_path, material_name=resource["filename"])
# 注意: 图片不需要 Material 对象，直接在 VideoSegment 中使用路径即可

# 步骤 3: 添加到 ScriptFile
script_file.add_material(material)
```

#### 3. 时间范围映射

**关键差异**: Draft Generator Interface 使用 (start, end)，pyJianYingDraft 使用 (start, duration)

```python
# Draft Generator Interface (JSON)
{
  "time_range": {
    "start": 5000,    # 开始时间 (ms)
    "end": 15000      # 结束时间 (ms)
  }
}

# pyJianYingDraft 调用
from pyJianYingDraft import Timerange

# 必须转换: duration = end - start
start_ms = time_range["start"]
end_ms = time_range["end"]
duration_ms = end_ms - start_ms

timerange = Timerange(start=start_ms, duration=duration_ms)
```

#### 4. 视频段映射

```python
# Draft Generator Interface (JSON)
{
  "type": "video",
  "material_url": "https://example.com/video.mp4",
  "time_range": {"start": 0, "end": 30000},
  "material_range": {"start": 5000, "end": 25000},  # 可选
  "transform": {
    "position_x": 0.0,
    "position_y": 0.0,
    "scale_x": 1.0,
    "scale_y": 1.0,
    "rotation": 0.0,
    "opacity": 1.0
  },
  "crop": {
    "enabled": true,
    "left": 0.1,
    "top": 0.1,
    "right": 0.9,
    "bottom": 0.9
  },
  "speed": {
    "speed": 1.0,
    "reverse": false
  }
}

# pyJianYingDraft 调用
from pyJianYingDraft import VideoSegment, ClipSettings, CropSettings, Timerange

# 1. 准备 target_timerange (时间轴位置)
target_timerange = Timerange(
    start=segment["time_range"]["start"],
    duration=segment["time_range"]["end"] - segment["time_range"]["start"]
)

# 2. 准备 source_timerange (素材裁剪，可选)
source_timerange = None
if segment["material_range"]:
    source_timerange = Timerange(
        start=segment["material_range"]["start"],
        duration=segment["material_range"]["end"] - segment["material_range"]["start"]
    )

# 3. 准备 ClipSettings (变换属性)
clip_settings = ClipSettings(
    alpha=segment["transform"]["opacity"],
    rotation=segment["transform"]["rotation"],
    scale_x=segment["transform"]["scale_x"],
    scale_y=segment["transform"]["scale_y"],
    transform_x=segment["transform"]["position_x"],
    transform_y=segment["transform"]["position_y"]
)

# 4. 准备 CropSettings (裁剪设置)
crop_settings = None
if segment["crop"]["enabled"]:
    # 转换: 从简单的 left/top/right/bottom 到四个角点
    left = segment["crop"]["left"]
    top = segment["crop"]["top"]
    right = segment["crop"]["right"]
    bottom = segment["crop"]["bottom"]
    
    crop_settings = CropSettings(
        upper_left_x=left,
        upper_left_y=top,
        upper_right_x=right,
        upper_right_y=top,
        lower_left_x=left,
        lower_left_y=bottom,
        lower_right_x=right,
        lower_right_y=bottom
    )

# 5. 查找对应的 Material
# 通过 material_url 匹配之前下载和创建的 material
material = find_material_by_url(segment["material_url"])

# 6. 创建 VideoSegment
video_segment = VideoSegment(
    material=material,
    target_timerange=target_timerange,
    source_timerange=source_timerange,
    speed=segment["speed"]["speed"],
    clip_settings=clip_settings
)

# 7. 添加到 ScriptFile (自动添加到视频轨道)
script_file.add_segment(video_segment)
```

#### 5. 音频段映射

```python
# Draft Generator Interface (JSON)
{
  "type": "audio",
  "material_url": "https://example.com/audio.mp3",
  "time_range": {"start": 0, "end": 30000},
  "audio": {
    "volume": 0.8,
    "fade_in": 1000,
    "fade_out": 1000,
    "speed": 1.0
  }
}

# pyJianYingDraft 调用
from pyJianYingDraft import AudioSegment, Timerange

# 1. 准备 timerange
target_timerange = Timerange(
    start=segment["time_range"]["start"],
    duration=segment["time_range"]["end"] - segment["time_range"]["start"]
)

# 2. 查找 material
material = find_material_by_url(segment["material_url"])

# 3. 创建 AudioSegment
audio_segment = AudioSegment(
    material=material,
    target_timerange=target_timerange,
    volume=segment["audio"]["volume"],
    speed=segment["audio"]["speed"]
)

# 注意: fade_in/fade_out 在 pyJianYingDraft 中需要通过特殊方式处理
# 可能需要使用 volume_keyframes 或其他机制实现

# 4. 添加到 ScriptFile (自动添加到音频轨道)
script_file.add_segment(audio_segment)
```

#### 6. 文本段映射

```python
# Draft Generator Interface (JSON)
{
  "type": "text",
  "content": "欢迎使用Coze剪映助手",
  "time_range": {"start": 5000, "end": 10000},
  "transform": {
    "position_x": 0.5,
    "position_y": -0.9,
    "scale": 1.0,
    "rotation": 0.0,
    "opacity": 1.0
  },
  "style": {
    "font_family": "思源黑体",
    "font_size": 48,
    "color": "#FFFFFF",
    "stroke": {
      "enabled": true,
      "color": "#000000",
      "width": 2
    }
  },
  "animations": {
    "intro": "淡入",
    "outro": "淡出"
  }
}

# pyJianYingDraft 调用
from pyJianYingDraft import TextSegment, TextStyle, ClipSettings, Timerange
from pyJianYingDraft import TextBorder, TextIntro, TextOutro

# 1. 准备 timerange
timerange = Timerange(
    start=segment["time_range"]["start"],
    duration=segment["time_range"]["end"] - segment["time_range"]["start"]
)

# 2. 准备 ClipSettings (位置、缩放、旋转、透明度)
clip_settings = ClipSettings(
    alpha=segment["transform"]["opacity"],
    rotation=segment["transform"]["rotation"],
    scale_x=segment["transform"]["scale"],
    scale_y=segment["transform"]["scale"],
    transform_x=segment["transform"]["position_x"],
    transform_y=segment["transform"]["position_y"]
)

# 3. 准备 TextStyle (字体和颜色)
text_style = TextStyle(
    size=segment["style"]["font_size"],
    color=segment["style"]["color"]
)

# 4. 准备 TextBorder (描边)
border = None
if segment["style"]["stroke"]["enabled"]:
    border = TextBorder(
        width=segment["style"]["stroke"]["width"],
        color=segment["style"]["stroke"]["color"]
    )

# 5. 创建 TextSegment
text_segment = TextSegment(
    text=segment["content"],
    timerange=timerange,
    style=text_style,
    clip_settings=clip_settings,
    border=border
)

# 注意: 动画效果 (intro/outro) 需要通过特殊的 API 设置
# 或在创建后修改 TextSegment 的相关属性

# 6. 添加到 ScriptFile (自动添加到文本轨道)
script_file.add_segment(text_segment)
```

#### 7. 特效段映射

```python
# Draft Generator Interface (JSON)
{
  "type": "effect",
  "effect_type": "模糊",
  "time_range": {"start": 10000, "end": 15000},
  "properties": {
    "intensity": 0.8,
    "position_x": 0.5,
    "position_y": 0.5
  }
}

# pyJianYingDraft 调用
from pyJianYingDraft import Timerange
from pyJianYingDraft.metadata import VideoSceneEffectType

# 1. 准备 timerange
timerange = Timerange(
    start=segment["time_range"]["start"],
    duration=segment["time_range"]["end"] - segment["time_range"]["start"]
)

# 2. 查找特效类型
# 需要将中文名称映射到 VideoSceneEffectType 枚举
effect_type = VideoSceneEffectType.from_name(segment["effect_type"])

# 3. 准备特效参数
params = [segment["properties"].get("intensity")]

# 4. 添加特效到 ScriptFile
script_file.add_effect(
    effect=effect_type,
    t_range=timerange,
    params=params
)
```

#### 8. 滤镜映射

```python
# Draft Generator Interface (JSON) - 滤镜在 VideoSegment 的 effects 中
{
  "effects": {
    "filter_type": "暖冬",
    "filter_intensity": 0.8
  }
}

# pyJianYingDraft 调用
from pyJianYingDraft import FilterType, Timerange

# 1. 查找滤镜类型
filter_type = FilterType.from_name(segment["effects"]["filter_type"])

# 2. 准备 timerange (与视频段相同)
timerange = Timerange(
    start=segment["time_range"]["start"],
    duration=segment["time_range"]["end"] - segment["time_range"]["start"]
)

# 3. 添加滤镜
script_file.add_filter(
    filter_meta=filter_type,
    t_range=timerange,
    intensity=segment["effects"]["filter_intensity"] * 100.0  # 转换为 0-100
)
```

### 完整示例代码

以下是一个完整的转换流程示例：

```python
#!/usr/bin/env python3
"""
使用 Draft Generator Interface 数据生成剪映草稿的完整示例
"""

import json
import requests
import tempfile
import os
from pathlib import Path
from pyJianYingDraft import (
    DraftFolder, VideoMaterial, AudioMaterial, VideoSegment, AudioSegment,
    TextSegment, Timerange, ClipSettings, CropSettings, TextStyle
)


class DraftImporter:
    """从 Draft Generator Interface JSON 生成剪映草稿"""
    
    def __init__(self, draft_folder_path: str):
        """
        初始化导入器
        
        Args:
            draft_folder_path: 剪映草稿文件夹路径，例如:
                - Windows: "C:/Users/YourName/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft"
                - macOS: "~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
        """
        self.draft_folder = DraftFolder(draft_folder_path)
        self.temp_dir = tempfile.mkdtemp(prefix="jianying_import_")
        self.materials = {}  # URL -> Material 对象的映射
        
    def download_media(self, url: str, filename: str) -> str:
        """
        下载媒体资源到本地
        
        Args:
            url: 媒体资源的 URL
            filename: 文件名
            
        Returns:
            本地文件路径
        """
        local_path = os.path.join(self.temp_dir, filename)
        
        # 如果已经下载过，直接返回
        if os.path.exists(local_path):
            return local_path
        
        print(f"下载资源: {url} -> {local_path}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return local_path
    
    def process_media_resources(self, media_resources: list, script_file):
        """
        处理媒体资源：下载并创建 Material 对象
        
        Args:
            media_resources: Draft Generator Interface 的 media_resources 数组
            script_file: pyJianYingDraft 的 ScriptFile 对象
        """
        for resource in media_resources:
            url = resource["url"]
            filename = resource.get("filename", url.split("/")[-1])
            resource_type = resource["resource_type"]
            
            # 下载到本地
            local_path = self.download_media(url, filename)
            
            # 创建 Material 对象
            if resource_type == "video":
                material = VideoMaterial(local_path, material_name=filename)
                script_file.add_material(material)
                self.materials[url] = material
            elif resource_type == "audio":
                material = AudioMaterial(local_path, material_name=filename)
                script_file.add_material(material)
                self.materials[url] = material
            # 图片不需要 Material 对象
    
    def convert_timerange(self, time_range_dict: dict) -> Timerange:
        """
        转换时间范围格式
        
        Args:
            time_range_dict: {"start": ms, "end": ms}
            
        Returns:
            Timerange 对象 (start, duration)
        """
        start = time_range_dict["start"]
        end = time_range_dict["end"]
        duration = end - start
        return Timerange(start=start, duration=duration)
    
    def convert_crop_settings(self, crop_dict: dict) -> CropSettings:
        """
        转换裁剪设置格式
        
        Args:
            crop_dict: {"enabled": bool, "left": float, "top": float, 
                        "right": float, "bottom": float}
            
        Returns:
            CropSettings 对象或 None
        """
        if not crop_dict.get("enabled"):
            return None
        
        left = crop_dict["left"]
        top = crop_dict["top"]
        right = crop_dict["right"]
        bottom = crop_dict["bottom"]
        
        return CropSettings(
            upper_left_x=left,
            upper_left_y=top,
            upper_right_x=right,
            upper_right_y=top,
            lower_left_x=left,
            lower_left_y=bottom,
            lower_right_x=right,
            lower_right_y=bottom
        )
    
    def convert_clip_settings(self, transform_dict: dict) -> ClipSettings:
        """
        转换变换设置格式
        
        Args:
            transform_dict: {"position_x": float, "position_y": float, 
                            "scale_x": float, "scale_y": float, 
                            "rotation": float, "opacity": float}
            
        Returns:
            ClipSettings 对象
        """
        return ClipSettings(
            alpha=transform_dict.get("opacity", 1.0),
            rotation=transform_dict.get("rotation", 0.0),
            scale_x=transform_dict.get("scale_x", 1.0),
            scale_y=transform_dict.get("scale_y", 1.0),
            transform_x=transform_dict.get("position_x", 0.0),
            transform_y=transform_dict.get("position_y", 0.0)
        )
    
    def process_video_segment(self, segment: dict, script_file):
        """处理视频段"""
        # 1. 准备时间范围
        target_timerange = self.convert_timerange(segment["time_range"])
        
        source_timerange = None
        if segment.get("material_range"):
            source_timerange = self.convert_timerange(segment["material_range"])
        
        # 2. 准备变换设置
        clip_settings = self.convert_clip_settings(segment["transform"])
        
        # 3. 查找 material
        material = self.materials[segment["material_url"]]
        
        # 4. 创建视频段
        video_segment = VideoSegment(
            material=material,
            target_timerange=target_timerange,
            source_timerange=source_timerange,
            speed=segment["speed"]["speed"],
            clip_settings=clip_settings
        )
        
        # 5. 添加到脚本
        script_file.add_segment(video_segment)
    
    def process_audio_segment(self, segment: dict, script_file):
        """处理音频段"""
        # 1. 准备时间范围
        target_timerange = self.convert_timerange(segment["time_range"])
        
        source_timerange = None
        if segment.get("material_range"):
            source_timerange = self.convert_timerange(segment["material_range"])
        
        # 2. 查找 material
        material = self.materials[segment["material_url"]]
        
        # 3. 创建音频段
        audio_segment = AudioSegment(
            material=material,
            target_timerange=target_timerange,
            source_timerange=source_timerange,
            volume=segment["audio"]["volume"],
            speed=segment["audio"]["speed"]
        )
        
        # 4. 添加到脚本
        script_file.add_segment(audio_segment)
    
    def process_text_segment(self, segment: dict, script_file):
        """处理文本段"""
        # 1. 准备时间范围
        timerange = self.convert_timerange(segment["time_range"])
        
        # 2. 准备变换设置
        clip_settings = ClipSettings(
            alpha=segment["transform"]["opacity"],
            rotation=segment["transform"]["rotation"],
            scale_x=segment["transform"]["scale"],
            scale_y=segment["transform"]["scale"],
            transform_x=segment["transform"]["position_x"],
            transform_y=segment["transform"]["position_y"]
        )
        
        # 3. 准备文本样式
        text_style = TextStyle(
            size=segment["style"]["font_size"],
            color=segment["style"]["color"]
        )
        
        # 4. 创建文本段
        text_segment = TextSegment(
            text=segment["content"],
            timerange=timerange,
            style=text_style,
            clip_settings=clip_settings
        )
        
        # 5. 添加到脚本
        script_file.add_segment(text_segment)
    
    def import_draft(self, json_data: dict) -> str:
        """
        从 Draft Generator Interface JSON 导入草稿
        
        Args:
            json_data: 完整的 Draft Generator Interface JSON 数据
            
        Returns:
            草稿名称
        """
        # 1. 提取项目配置
        project = json_data["project"]
        draft_name = project["name"]
        
        print(f"创建草稿: {draft_name}")
        
        # 2. 创建草稿
        script_file = self.draft_folder.create_draft(
            draft_name=draft_name,
            width=project["width"],
            height=project["height"],
            fps=project["fps"],
            allow_replace=True
        )
        
        # 3. 处理媒体资源
        print("处理媒体资源...")
        self.process_media_resources(json_data["media_resources"], script_file)
        
        # 4. 处理轨道和段
        print("处理轨道...")
        for track in json_data["tracks"]:
            track_type = track["track_type"]
            print(f"  处理 {track_type} 轨道，共 {len(track['segments'])} 个段")
            
            for segment in track["segments"]:
                segment_type = segment["type"]
                
                if segment_type == "video":
                    self.process_video_segment(segment, script_file)
                elif segment_type == "audio":
                    self.process_audio_segment(segment, script_file)
                elif segment_type == "text":
                    self.process_text_segment(segment, script_file)
                # 其他类型...
        
        # 5. 保存草稿
        print("保存草稿...")
        script_file.save()
        
        print(f"✅ 草稿创建成功: {draft_name}")
        return draft_name


def main():
    """使用示例"""
    # 1. 加载 Draft Generator Interface JSON 数据
    with open("draft_export.json", "r", encoding="utf-8") as f:
        draft_data = json.load(f)
    
    # 2. 指定剪映草稿文件夹路径
    # Windows 示例
    # draft_folder_path = r"C:\Users\YourName\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft"
    # macOS 示例
    draft_folder_path = os.path.expanduser(
        "~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"
    )
    
    # 3. 创建导入器并导入
    importer = DraftImporter(draft_folder_path)
    
    # 如果是批量导出的 JSON，遍历所有草稿
    if draft_data.get("export_type") == "batch":
        for draft in draft_data["drafts"]:
            importer.import_draft(draft)
    else:
        # 单个草稿
        draft = draft_data["drafts"][0] if "drafts" in draft_data else draft_data
        importer.import_draft(draft)


if __name__ == "__main__":
    main()
```

### 关键映射说明总结

#### 必须转换的参数

1. **时间范围**: `(start, end)` → `Timerange(start, duration)` 其中 `duration = end - start`
2. **裁剪设置**: `{left, top, right, bottom}` → `CropSettings` 四角点格式
3. **URL资源**: 必须先下载到本地文件路径
4. **滤镜强度**: `0.0-1.0` → `0-100`

#### 参数对应表

| Draft Generator Interface | pyJianYingDraft | 说明 |
|--------------------------|-----------------|------|
| `position_x` / `position_y` | `transform_x` / `transform_y` | 位置坐标 |
| `opacity` | `alpha` | 透明度 |
| `scale_x` / `scale_y` | `scale_x` / `scale_y` | 缩放 |
| `rotation` | `rotation` | 旋转角度 |
| `time_range.start` / `end` | `Timerange(start, duration)` | 时间范围 |
| `material_url` (URL) | `VideoMaterial(path)` (本地路径) | 媒体素材 |
| `filter_intensity` (0-1) | `intensity` (0-100) | 滤镜强度 |

### 数据完整性分析

Draft Generator Interface 当前提供了以下完整的参数支持：

✅ **项目配置**
- 分辨率 (width, height)
- 帧率 (fps)

✅ **视频段参数**
- 基础: material, time_range, material_range
- 变换: position, scale, rotation, opacity
- 裁剪: crop settings
- 效果: filter, transition
- 速度: speed, reverse
- 背景: blur, color
- 关键帧动画: position, scale, rotation, opacity

✅ **音频段参数**
- 基础: material, time_range, material_range
- 音频属性: volume, fade_in, fade_out
- 效果: effect_type, intensity
- 速度: speed
- 关键帧: volume

✅ **图片段参数**
- 与视频段类似，额外支持：
  - 适配模式: fit_mode
  - 动画: intro_animation, outro_animation

✅ **文本段参数**
- 内容: text content
- 位置和变换: 完整支持
- 样式: font, size, color, stroke, shadow, background
- 对齐: alignment
- 动画: intro, outro, loop

✅ **特效段参数**
- 特效类型: effect_type
- 时间范围: time_range
- 属性: intensity, position, scale, custom properties

### 潜在的改进空间

虽然 Draft Generator Interface 已经相当完整，但在以下方面还可以增强：

1. **关键帧系统的细化** - 当前支持基本关键帧，可以添加更多缓动函数选项
2. **转场效果的参数** - 当前仅支持类型和时长，某些转场可能有额外参数
3. **音频淡入淡出** - pyJianYingDraft 中的实现方式需要进一步研究
4. **文本动画类型** - 需要建立完整的动画类型枚举映射
5. **镜像翻转参数** - `flip_horizontal/vertical` 参数可考虑添加

**结论**: Draft Generator Interface 设计合理、参数完整，能够满足从 Coze 工作流到剪映草稿生成的需求。配合 pyJianYingDraftImporter 项目进行 URL 下载和格式转换，可以实现完整的自动化视频生成流程。