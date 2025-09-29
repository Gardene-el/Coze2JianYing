# Draft Generator Interface

草稿生成器接口数据模型，定义了传递给草稿生成器的完整数据结构。

## 功能描述

本模块定义了用于在Coze插件和草稿生成器之间传递数据的标准化数据结构。这些模型包含了pyJianYingDraft支持的所有参数配置选项，但使用URL而不是本地文件路径来引用媒体资源。

## 核心设计原则

### 1. URL-based资源管理
- 所有媒体资源（视频、音频、图片）使用URL形式
- 适配Coze平台的网络资源传递模式
- 支持各种网络媒体格式和来源

### 2. 完整参数覆盖
- 包含pyJianYingDraft的所有可配置参数
- 支持视频、音频、文本、特效等所有轨道类型
- 涵盖变换、滤镜、转场、动画等所有效果

### 3. UUID草稿管理
- 使用UUID作为草稿唯一标识符
- 支持多草稿批量导出
- 临时文件管理和清理

## 数据结构概览

### 基础配置类

#### ProjectSettings
项目基本配置，包含分辨率、帧率、质量设置等。

```python
@dataclass
class ProjectSettings:
    name: str = "Coze剪映项目"
    width: int = 1920
    height: int = 1080
    fps: int = 30
    video_quality: VideoQuality = VideoQuality.FHD_1080P
    audio_quality: AudioQuality = AudioQuality.HIGH_320K
    background_color: str = "#000000"
```

#### MediaResource
媒体资源描述，包含URL和元数据信息。

```python
@dataclass
class MediaResource:
    url: str
    resource_type: str  # "video", "audio", "image"
    duration_ms: Optional[int] = None
    file_size: Optional[int] = None
    format: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    filename: Optional[str] = None
```

### 轨道段配置类

#### VideoSegmentConfig
视频段配置，包含所有视频相关的参数：

- **变换属性**: 位置、缩放、旋转、透明度
- **裁剪设置**: 裁剪区域定义
- **效果滤镜**: 滤镜类型、强度、转场效果
- **速度控制**: 播放速度、倒放
- **背景填充**: 模糊背景、纯色背景
- **关键帧动画**: 位置、缩放、旋转、透明度动画

#### AudioSegmentConfig
音频段配置，包含音频相关参数：

- **音频属性**: 音量、淡入淡出
- **音频效果**: 效果类型、强度
- **速度控制**: 播放速度
- **音量动画**: 音量关键帧

#### TextSegmentConfig
文本段配置，包含字幕和文本相关参数：

- **位置变换**: 位置、缩放、旋转、透明度
- **文本样式**: 字体、颜色、描边、阴影、背景
- **对齐方式**: 左对齐、居中、右对齐
- **动画效果**: 入场、出场、循环动画
- **关键帧动画**: 完整的动画支持

#### EffectSegmentConfig
特效段配置，支持各种视觉特效：

- **特效类型**: 特效名称和参数
- **特效属性**: 强度、位置、缩放
- **自定义属性**: 灵活的特效参数支持

## 使用示例

### 创建基本草稿配置

```python
from data_structures.draft_generator_interface.models import (
    DraftConfig, ProjectSettings, MediaResource, TrackConfig,
    VideoSegmentConfig, TimeRange
)

# 创建项目设置
project = ProjectSettings(
    name="我的Coze项目",
    width=1920,
    height=1080,
    fps=30
)

# 添加媒体资源
media_resources = [
    MediaResource(
        url="https://example.com/video1.mp4",
        resource_type="video",
        duration_ms=30000
    ),
    MediaResource(
        url="https://example.com/audio1.mp3",
        resource_type="audio",
        duration_ms=45000
    )
]

# 创建视频轨道
video_segment = VideoSegmentConfig(
    material_url="https://example.com/video1.mp4",
    time_range=TimeRange(start=0, end=30000),
    filter_type="暖冬",
    filter_intensity=0.8,
    transition_type="淡化",
    transition_duration=1000
)

video_track = TrackConfig(
    track_type="video",
    segments=[video_segment]
)

# 创建完整草稿配置
draft_config = DraftConfig(
    project=project,
    media_resources=media_resources,
    tracks=[video_track],
    total_duration_ms=30000
)

# 转换为JSON字符串
json_data = json.dumps(draft_config.to_dict(), ensure_ascii=False, indent=2)
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
    position_y=0.9,
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