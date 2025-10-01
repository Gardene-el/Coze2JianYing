# Make Video Info Tool

## 功能描述

生成单个视频配置的 JSON 字符串表示。这是 `add_videos` 工具的辅助函数，用于创建可以被组合成数组的视频信息字符串。

### 使用场景

当你需要在 Coze 工作流中动态构建多个视频配置时，可以：
1. 多次调用 `make_video_info` 生成每个视频的配置字符串
2. 将这些字符串收集到一个数组中
3. 将该数组作为 `video_infos` 参数传递给 `add_videos` 工具

### 参数数量说明

本工具共有 **29 个参数**：
- **3 个必需参数**: `video_url`, `start`, `end`
- **26 个可选参数**: 包括素材范围、变换、裁剪、效果、速度控制、音频、背景等设置

这些参数基于 `pyJianYingDraft` 库的功能设计，映射了剪映中视频片段的主要可配置属性。

## 输入参数

### Input 类型定义

```python
class Input(NamedTuple):
    # 必需字段
    video_url: str                              # 视频URL
    start: int                                  # 开始时间（毫秒）
    end: int                                    # 结束时间（毫秒）
    
    # 可选：素材范围（用于裁剪视频）
    material_start: Optional[int] = None        # 素材开始时间（毫秒）
    material_end: Optional[int] = None          # 素材结束时间（毫秒）
    
    # 可选：变换字段
    position_x: Optional[float] = 0.0           # X位置（默认0.0）
    position_y: Optional[float] = 0.0           # Y位置（默认0.0）
    scale_x: Optional[float] = 1.0              # X缩放（默认1.0）
    scale_y: Optional[float] = 1.0              # Y缩放（默认1.0）
    rotation: Optional[float] = 0.0             # 旋转角度（默认0.0）
    opacity: Optional[float] = 1.0              # 透明度（0.0-1.0，默认1.0）
    
    # 可选：裁剪字段
    crop_enabled: Optional[bool] = False        # 启用裁剪（默认False）
    crop_left: Optional[float] = 0.0            # 裁剪左边（0.0-1.0）
    crop_top: Optional[float] = 0.0             # 裁剪顶部（0.0-1.0）
    crop_right: Optional[float] = 1.0           # 裁剪右边（0.0-1.0）
    crop_bottom: Optional[float] = 1.0          # 裁剪底部（0.0-1.0）
    
    # 可选：效果字段
    filter_type: Optional[str] = None           # 滤镜类型（如"暖冬"）
    filter_intensity: Optional[float] = 1.0     # 滤镜强度（0.0-1.0）
    transition_type: Optional[str] = None       # 转场类型
    transition_duration: Optional[int] = 500    # 转场时长（毫秒）
    
    # 可选：速度控制字段
    speed: Optional[float] = 1.0                # 播放速度（0.5-2.0，默认1.0）
    reverse: Optional[bool] = False             # 反向播放（默认False）
    
    # 可选：音频字段
    volume: Optional[float] = 1.0               # 音量（0.0-2.0，默认1.0）
    change_pitch: Optional[bool] = False        # 变速时是否变调（默认False）
    
    # 可选：背景字段
    background_blur: Optional[bool] = False     # 背景模糊（默认False）
    background_color: Optional[str] = None      # 背景颜色
```

### 参数说明

#### 必需参数

- `video_url`: 视频的 URL 地址
- `start`: 视频在时间轴上的开始时间（毫秒）
- `end`: 视频在时间轴上的结束时间（毫秒）

**重要说明 - start/end 与 material_start/material_end 的区别**：

1. **start/end（时间轴位置）**：
   - 定义素材在时间轴上**何时播放**
   - 例如：`start=0, end=5000` 表示从时间轴的0秒到5秒位置播放此视频
   - 所有素材类型（视频、音频、图片、字幕）都需要

2. **material_start/material_end（素材裁剪）**：
   - 定义从源素材中**截取哪一段**来播放
   - 例如：`material_start=10000, material_end=15000` 表示使用源视频的第10-15秒
   - 只有视频和音频需要（图片和字幕无时长概念）

3. **时长不匹配的行为**：
   - 当 `(end - start) ≠ (material_end - material_start)` 时，视频会**自动调整播放速度**
   - 速度计算：`effective_speed = (material_end - material_start) / (end - start)`
   - 示例：10秒素材放入5秒时间轴 → 2倍速播放（快动作）
   - 示例：5秒素材放入10秒时间轴 → 0.5倍速播放（慢动作）
   - **建议**：通常应保持时长一致以正常速度播放

4. **不指定 material_* 时的默认行为**：
   - 自动使用素材开头的 `(end - start)` 毫秒
   - 正常速度播放（1x）
   - 这是最常见的用法

#### 视频特有参数（与图片工具的区别）

**素材范围（Material Range）**:
- `material_start` 和 `material_end`: 用于裁剪源视频的某个片段
- 例如：源视频 30 秒，只想使用其中的 5-15 秒部分
- 必须同时提供两个参数，否则会报错

**速度控制（Speed Control）**:
- `speed`: 额外的播放速度调整，范围 0.5-2.0（0.5倍速到2倍速）
- `reverse`: 是否反向播放，布尔值
- **注意**：如果时长不匹配，最终速度 = 自动速度 × speed 参数

**音频控制（Audio Control）** ⭐ 新增:
- `volume`: 视频的音量，范围 0.0-2.0（默认1.0）
- `change_pitch`: 变速时是否改变音调（默认False）
  - False: 变速不变调（推荐，听起来自然）
  - True: 变速变调（快放音调变高，慢放音调变低）

#### 共享参数（与图片工具相同）

**变换参数**: `position_x`, `position_y`, `scale_x`, `scale_y`, `rotation`, `opacity`

**裁剪参数**: `crop_enabled`, `crop_left`, `crop_top`, `crop_right`, `crop_bottom`

**效果参数**: `filter_type`, `filter_intensity`, `transition_type`, `transition_duration`

**背景参数**: `background_blur`, `background_color`

#### 与图片工具的差异

视频工具**不包含**以下图片专有参数：
- `fit_mode` (适配模式) - 视频不需要
- `in_animation` / `intro_animation` (入场动画) - 视频不支持
- `outro_animation` (出场动画) - 视频不支持
- `in_animation_duration` / `outro_animation_duration` - 视频不支持
- `width` / `height` (尺寸) - 视频从源文件获取

#### 参数来源与 pyJianYingDraft 的关系

本工具的参数设计基于以下 `pyJianYingDraft` 库的组件：

1. **VideoSegment 参数**:
   - `material`: 映射为 `video_url`
   - `target_timerange`: 映射为 `start` 和 `end`
   - `source_timerange`: 映射为 `material_start` 和 `material_end`
   - `speed`: 直接对应
   - `reverse`: 通过 speed 参数的负值实现

2. **ClipSettings 参数**:
   - `alpha`: 映射为 `opacity`
   - `rotation`: 直接对应
   - `scale_x`, `scale_y`: 直接对应
   - `transform_x`, `transform_y`: 映射为 `position_x` 和 `position_y`

3. **CropSettings 参数**:
   - 简化为 `crop_enabled` 和四个边界参数

4. **效果参数**:
   - `filter_type`, `filter_intensity`: 滤镜设置
   - `transition_type`, `transition_duration`: 转场设置
   - `background_blur`, `background_color`: 背景设置

## 输出结果

### Output 类型定义

```python
class Output(NamedTuple):
    video_info_string: str                      # 视频信息的 JSON 字符串
    success: bool                               # 操作是否成功
    message: str                                # 状态消息
```

### 输出格式

输出是一个紧凑的 JSON 字符串，例如：

```json
"{\"video_url\":\"https://example.com/video.mp4\",\"start\":0,\"end\":5000}"
```

或带有可选参数：

```json
"{\"video_url\":\"https://example.com/video.mp4\",\"start\":0,\"end\":5000,\"material_start\":1000,\"material_end\":6000,\"speed\":1.5}"
```

## 使用示例

### 示例 1: 基本用法

```python
from tools.make_video_info.handler import handler, Input
from runtime import Args

# 创建输入参数（仅必需字段）
input_data = Input(
    video_url="https://example.com/video.mp4",
    start=0,
    end=5000
)

# 模拟Args对象
class MockArgs:
    def __init__(self, input_data):
        self.input = input_data

# 调用处理函数
result = handler(MockArgs(input_data))

print(f"成功: {result.success}")
print(f"生成的字符串: {result.video_info_string}")
# 输出: {"video_url":"https://example.com/video.mp4","start":0,"end":5000}
```

### 示例 2: 使用素材范围裁剪视频

```python
# 从 30 秒的视频中截取 5-15 秒的片段
input_data = Input(
    video_url="https://example.com/video.mp4",
    start=0,                    # 在时间轴上的位置
    end=10000,                  # 持续 10 秒
    material_start=5000,        # 从源视频的第 5 秒开始
    material_end=15000          # 到源视频的第 15 秒结束
)

result = handler(MockArgs(input_data))
print(result.video_info_string)
# 输出: {"video_url":"https://example.com/video.mp4","start":0,"end":10000,"material_start":5000,"material_end":15000}
```

### 示例 3: 带完整参数

```python
# 创建输入参数（包含可选字段）
input_data = Input(
    video_url="https://example.com/video.mp4",
    start=0,
    end=5000,
    material_start=2000,
    material_end=7000,
    position_x=0.1,
    position_y=0.1,
    scale_x=1.2,
    scale_y=1.2,
    speed=1.5,              # 1.5倍速播放
    filter_type="暖冬",
    filter_intensity=0.8,
    background_blur=True
)

result = handler(MockArgs(input_data))
print(result.video_info_string)
# 输出包含所有非默认值的参数
```

### 示例 4: 反向播放

```python
# 创建反向播放的视频
input_data = Input(
    video_url="https://example.com/video.mp4",
    start=0,
    end=5000,
    reverse=True,           # 反向播放
    speed=0.5               # 0.5倍速（慢动作）
)

result = handler(MockArgs(input_data))
print(result.video_info_string)
```

### 示例 5: 与 add_videos 配合使用（完整工作流）

这是本工具的主要使用场景：

```python
# 步骤 1: 使用 make_video_info 生成多个视频信息字符串
video1_info = make_video_info(
    video_url="https://example.com/video1.mp4",
    start=0,
    end=5000,
    scale_x=1.2
)
# 返回: {"video_url":"https://example.com/video1.mp4","start":0,"end":5000,"scale_x":1.2}

video2_info = make_video_info(
    video_url="https://example.com/video2.mp4",
    start=5000,
    end=10000,
    speed=1.5,
    filter_type="暖冬"
)
# 返回: {"video_url":"https://example.com/video2.mp4","start":5000,"end":10000,"speed":1.5,"filter_type":"暖冬"}

# 步骤 2: 将字符串收集到数组中
video_infos_array = [
    video1_info.video_info_string,
    video2_info.video_info_string
]

# 步骤 3: 将数组字符串传递给 add_videos
add_videos(
    draft_id="your-draft-uuid",
    video_infos=video_infos_array  # 数组字符串格式！
)
```

### 示例 6: 在 Coze 工作流中使用

在 Coze 工作流中，你可以这样组合使用：

```
1. [make_video_info 节点1] → 生成第一个视频配置字符串
   输入: video_url="https://...", start=0, end=5000
   输出: video_info_string

2. [make_video_info 节点2] → 生成第二个视频配置字符串
   输入: video_url="https://...", start=5000, end=10000, speed=1.5
   输出: video_info_string

3. [数组节点] → 将多个字符串组合成数组
   输入: [节点1.video_info_string, 节点2.video_info_string]
   输出: video_infos_array

4. [add_videos 节点] → 添加视频到草稿
   输入: draft_id="...", video_infos=video_infos_array
   输出: segment_ids, segment_infos
```

## 注意事项

### 输出优化
- 工具只会在输出中包含非默认值的参数
- 这使得输出字符串保持紧凑，减少数据传输
- 例如：如果 `scale_x=1.0`（默认值），则不会包含在输出中

### 时间参数说明

**时间轴时间（start/end）**:
- 定义视频在最终项目时间轴上的位置
- 例如：`start=0, end=5000` 表示视频在时间轴的 0-5 秒位置

**素材时间（material_start/material_end）**:
- 定义使用源视频的哪个片段
- 例如：`material_start=10000, material_end=15000` 表示使用源视频的 10-15 秒部分
- 必须同时提供或同时不提供

### 时间参数验证
- `start` 必须 >= 0
- `end` 必须 > `start`
- `material_start` 必须 >= 0（如果提供）
- `material_end` 必须 > `material_start`（如果提供）
- `material_start` 和 `material_end` 必须同时提供
- 时间单位为毫秒

### 速度参数验证
- `speed` 必须在 0.5 到 2.0 之间
- 常用值：0.5（慢动作）、1.0（正常速度）、1.5（快速）、2.0（2倍速）

### 与 add_videos 的兼容性
- 输出的字符串格式完全兼容 `add_videos` 的 `video_infos` 参数
- 可以使用数组字符串格式（推荐）、数组对象格式或 JSON 字符串格式

## 错误处理

工具会验证以下情况：

1. **缺少必需参数**: 如果缺少 `video_url`、`start` 或 `end`，返回错误
2. **无效时间范围**: 如果 `start < 0` 或 `end <= start`，返回错误
3. **无效素材范围**: 如果只提供了 `material_start` 或 `material_end` 之一，返回错误
4. **无效素材时间**: 如果 `material_start < 0` 或 `material_end <= material_start`，返回错误
5. **无效速度值**: 如果 `speed < 0.5` 或 `speed > 2.0`，返回错误
6. **其他异常**: 任何意外错误都会被捕获并返回错误消息

## 与其他工具的关系

### make_video_info → add_videos
这是主要的使用流程：
1. `make_video_info` 生成单个视频的配置字符串
2. 多个字符串组合成数组
3. `add_videos` 接收数组并添加视频到草稿

### 与 make_image_info 和 make_audio_info 的比较

| 特性 | make_video_info | make_image_info | make_audio_info |
|------|----------------|-----------------|-----------------|
| 素材范围 | ✅ 支持 | ❌ 不支持 | ✅ 支持 |
| 速度控制 | ✅ 支持 | ❌ 不支持 | ✅ 支持 |
| 反向播放 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 |
| 入场/出场动画 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 |
| 适配模式 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 |
| 裁剪 | ✅ 支持 | ✅ 支持 | ❌ 不支持 |
| 滤镜 | ✅ 支持 | ✅ 支持 | ❌ 不支持（音效） |

### 替代方案
如果你的视频配置是静态的，也可以：
- 直接使用数组对象格式传递给 `add_videos`
- 使用 JSON 字符串格式传递给 `add_videos`

`make_video_info` 主要用于需要动态构建配置的场景。
