# Add Videos Tool

## 功能描述

向现有草稿添加视频轨道和视频片段。每次调用会创建一个新的视频轨道，包含指定的所有视频。支持视频的位置、大小、速度、裁剪等完整参数设置。

## 输入参数

### Input 类型定义

```python
class Input(NamedTuple):
    draft_id: str                              # 现有草稿的UUID
    video_infos: Any                           # 视频信息：支持多种格式输入
```

### video_infos 输入格式

支持多种输入格式，自动识别和处理：

#### 格式1：数组对象（推荐用于静态配置）
```json
[
  {
    "video_url": "https://example.com/video.mp4",
    "start": 0,
    "end": 5000,
    "material_start": 1000,
    "material_end": 6000,
    "position_x": 0.0,
    "position_y": 0.0,
    "scale_x": 1.0,
    "scale_y": 1.0,
    "speed": 1.5,
    "filter_type": "暖冬",
    "filter_intensity": 0.8
  }
]
```

#### 格式2：数组字符串（推荐用于动态配置）
数组中每个元素是 JSON 字符串。通常与 `make_video_info` 工具配合使用：
```json
[
  "{\"video_url\":\"https://example.com/video1.mp4\",\"start\":0,\"end\":5000,\"speed\":1.5}",
  "{\"video_url\":\"https://example.com/video2.mp4\",\"start\":5000,\"end\":10000,\"material_start\":2000,\"material_end\":7000}"
]
```

#### 格式3：JSON字符串
整个数组作为一个 JSON 字符串：
```json
"[{\"video_url\":\"https://example.com/video.mp4\",\"start\":0,\"end\":5000,\"speed\":1.5}]"
```

#### 格式4：其他可迭代类型
工具还支持元组(tuple)等其他可迭代类型，会自动转换为列表处理。

#### 必需字段
- `video_url`: 视频的URL链接
- `start`: 开始时间（毫秒）
- `end`: 结束时间（毫秒）

#### 可选字段

**素材范围（视频特有）**：
- `material_start`: 素材开始时间（毫秒）- 用于裁剪源视频
- `material_end`: 素材结束时间（毫秒）- 用于裁剪源视频
- 注意：必须同时提供或同时不提供

**速度控制（视频特有）**：
- `speed`: 播放速度（0.5-2.0，默认1.0）
- `reverse`: 反向播放（布尔值，默认false）

**变换参数**：
- `position_x`, `position_y`: 位置坐标（浮点数）
- `scale_x`, `scale_y`: 缩放比例（默认1.0，**控制实际显示大小**）
- `rotation`: 旋转角度（默认0.0）
- `opacity`: 透明度（0.0-1.0，默认1.0）

**裁剪参数**：
- `crop_enabled`: 是否启用裁剪（默认false）
- `crop_left`, `crop_top`, `crop_right`, `crop_bottom`: 裁剪区域（0.0-1.0）

**效果参数**：
- `filter_type`: 滤镜类型
- `filter_intensity`: 滤镜强度（0.0-1.0，默认1.0）
- `transition_type`: 转场类型
- `transition_duration`: 转场时长（毫秒，默认500）

**背景参数**：
- `background_blur`: 背景模糊（默认false）
- `background_color`: 背景颜色

## 输出结果

### Output 类型定义

```python
class Output(NamedTuple):
    segment_ids: List[str]                 # 生成的片段UUID列表
    segment_infos: List[Dict[str, Any]]    # 片段信息列表
    success: bool                          # 操作是否成功
    message: str                           # 状态消息
```

### segment_infos 格式

```json
[
  {
    "id": "efde9038-64b8-40d2-bdab-fca68e6bf943",
    "start": 0,
    "end": 5000
  }
]
```

## 使用示例

### 基本用法

#### 方法1：使用数组格式（推荐用于静态配置）

```python
from tools.add_videos.handler import handler, Input
from runtime import Args

# 创建输入参数（数组格式）
input_data = Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    video_infos=[{
        "video_url": "https://example.com/video.mp4",
        "start": 0,
        "end": 5000
    }]
)

# 模拟Args对象
class MockArgs:
    def __init__(self, input_data):
        self.input = input_data

# 调用处理函数
result = handler(MockArgs(input_data))

print(f"成功: {result.success}")
print(f"片段数量: {len(result.segment_ids)}")
print(f"片段ID: {result.segment_ids}")
```

#### 方法2：使用数组字符串格式（推荐用于动态配置）

配合 `make_video_info` 工具使用：

```python
from tools.make_video_info.handler import handler as make_video_info_handler
from tools.add_videos.handler import handler as add_videos_handler

# 步骤1: 使用 make_video_info 生成视频信息字符串
video1_result = make_video_info_handler(MockArgs(Input(
    video_url="https://example.com/video1.mp4",
    start=0,
    end=5000,
    speed=1.5
)))

video2_result = make_video_info_handler(MockArgs(Input(
    video_url="https://example.com/video2.mp4",
    start=5000,
    end=10000,
    material_start=2000,
    material_end=7000
)))

# 步骤2: 将字符串收集到数组中
video_infos_array = [
    video1_result.video_info_string,
    video2_result.video_info_string
]

# 步骤3: 传递数组字符串给 add_videos
result = add_videos_handler(MockArgs(Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    video_infos=video_infos_array  # 数组字符串格式
)))

print(f"成功添加 {len(result.segment_ids)} 个视频")
```

#### 方法3：使用JSON字符串格式

```python
# 创建输入参数（JSON字符串格式）
input_data = Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    video_infos='[{"video_url":"https://example.com/video.mp4","start":0,"end":5000,"speed":1.5}]'
)
```

### 复杂参数示例

#### 示例1：使用素材范围裁剪视频

```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "video_infos": [
        {
            "video_url": "https://example.com/video.mp4",
            "start": 0,
            "end": 10000,
            "material_start": 5000,
            "material_end": 15000
        }
    ]
}
```

说明：
- 在时间轴的 0-10 秒位置放置视频
- 使用源视频的 5-15 秒片段（裁剪了前5秒和15秒后的内容）

#### 示例2：调整播放速度

```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "video_infos": [
        {
            "video_url": "https://example.com/video.mp4",
            "start": 0,
            "end": 5000,
            "speed": 2.0
        }
    ]
}
```

说明：
- 视频以2倍速播放
- 如果源视频是10秒，2倍速后只需要5秒就能播放完

#### 示例3：反向播放

```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "video_infos": [
        {
            "video_url": "https://example.com/video.mp4",
            "start": 0,
            "end": 5000,
            "reverse": true,
            "speed": 0.5
        }
    ]
}
```

说明：
- 视频反向播放（倒放）
- 同时以0.5倍速播放（慢动作）

#### 示例4：完整参数配置

数组格式：
```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "video_infos": [
        {
            "video_url": "https://example.com/video.mp4",
            "start": 0,
            "end": 5000,
            "material_start": 1000,
            "material_end": 6000,
            "position_x": 0.1,
            "position_y": 0.1,
            "scale_x": 1.2,
            "scale_y": 1.2,
            "rotation": 15.0,
            "opacity": 0.9,
            "speed": 1.5,
            "filter_type": "暖冬",
            "filter_intensity": 0.8,
            "background_blur": true
        }
    ]
}
```

JSON字符串格式：
```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "video_infos": "[{\"video_url\":\"https://example.com/video.mp4\",\"start\":0,\"end\":5000,\"material_start\":1000,\"material_end\":6000,\"position_x\":0.1,\"position_y\":0.1,\"scale_x\":1.2,\"scale_y\":1.2,\"rotation\":15.0,\"opacity\":0.9,\"speed\":1.5,\"filter_type\":\"暖冬\",\"filter_intensity\":0.8,\"background_blur\":true}]"
}
```

## 注意事项

### 时间单位与时间轴说明

所有时间参数使用毫秒(ms)为单位。

**时间轴时间（start/end）**:
- 定义视频在最终项目时间轴上的位置
- 例如：`start=0, end=5000` 表示视频在时间轴的 0-5 秒位置

**素材时间（material_start/material_end）**:
- 定义使用源视频的哪个片段
- 例如：`material_start=10000, material_end=15000` 表示使用源视频的 10-15 秒部分
- 可以用于裁剪掉视频的开头、结尾或中间部分

**完整示例**:
```json
{
    "video_url": "https://example.com/30s_video.mp4",
    "start": 0,
    "end": 5000,
    "material_start": 10000,
    "material_end": 15000
}
```
这表示：
- 从 30 秒的源视频中取出 10-15 秒的片段（5秒）
- 将这 5 秒片段放在时间轴的 0-5 秒位置

### 速度控制说明

**speed 参数**:
- 取值范围：0.5 到 2.0
- 常用值：
  - 0.5: 慢动作（半速播放）
  - 1.0: 正常速度（默认）
  - 1.5: 1.5倍速
  - 2.0: 2倍速（快进）

**reverse 参数**:
- `false`（默认）: 正向播放
- `true`: 反向播放（倒放）

**组合使用**:
```json
{
    "speed": 0.5,
    "reverse": true
}
```
这表示以0.5倍速反向播放（倒放慢动作）

### 坐标系统
- 位置坐标使用浮点数，可以为负值或超过1.0
- (0,0) 通常表示屏幕中心或左上角（取决于剪映的坐标系）
- 缩放比例1.0表示原始大小

### 轨道管理
- 每次调用都会创建一个新的视频轨道
- 同一轨道内的视频按时间顺序排列
- 不同轨道的视频可以重叠显示（画中画效果）

### 错误处理
- 如果draft_id不存在，返回失败状态
- 如果video_infos格式无效，返回详细错误信息
- 如果视频URL无法访问，仍会创建片段（由草稿生成器处理）

### 性能考虑
- 大量视频可能影响处理性能
- 建议单次调用视频数量控制在20个以内
- 过长的视频或过多的效果可能影响播放流畅度

## 与其他工具的集成

### 与 create_draft 配合使用
1. 使用 `create_draft` 创建基础草稿
2. 使用 `add_videos` 添加视频轨道
3. 使用 `add_audios` 添加音频轨道
4. 使用 `add_images` 添加图片轨道
5. 使用 `export_drafts` 导出完整配置

### 与 get_media_duration 配合使用
1. 使用 `get_media_duration` 获取视频时长信息
2. 根据时长信息设置视频的 `start`、`end`、`material_start`、`material_end` 参数
3. 使用 `add_videos` 添加到草稿

### 与 make_video_info 的工作流

这是推荐的动态配置方式：

```
1. [make_video_info 节点1] → 生成第一个视频配置
2. [make_video_info 节点2] → 生成第二个视频配置
3. [数组收集节点] → 组合成数组
4. [add_videos 节点] → 添加到草稿
```

## 与 add_images 和 add_audios 的比较

| 特性 | add_videos | add_images | add_audios |
|------|-----------|------------|------------|
| 素材范围 | ✅ 支持 | ❌ 不支持 | ✅ 支持 |
| 速度控制 | ✅ 支持 | ❌ 不支持 | ✅ 支持 |
| 反向播放 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 |
| 入场/出场动画 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 |
| 适配模式 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 |
| 裁剪 | ✅ 支持 | ✅ 支持 | ❌ 不支持 |
| 滤镜 | ✅ 支持 | ✅ 支持 | ❌ 不支持（音效） |
| 变换参数 | ✅ 支持 | ✅ 支持 | ❌ 不支持 |

## 最佳实践

### 1. 使用素材范围优化视频

```python
# 不推荐：使用整个30秒视频
video_infos = [{
    "video_url": "https://example.com/30s_video.mp4",
    "start": 0,
    "end": 30000
}]

# 推荐：只使用需要的片段
video_infos = [{
    "video_url": "https://example.com/30s_video.mp4",
    "start": 0,
    "end": 5000,
    "material_start": 10000,  # 从第10秒开始
    "material_end": 15000     # 到第15秒结束
}]
```

### 2. 合理使用速度控制

```python
# 快速浏览场景 - 使用快进
video_infos = [{
    "video_url": "https://example.com/long_video.mp4",
    "start": 0,
    "end": 5000,
    "speed": 2.0  # 2倍速
}]

# 强调重要时刻 - 使用慢动作
video_infos = [{
    "video_url": "https://example.com/highlight.mp4",
    "start": 0,
    "end": 10000,
    "speed": 0.5  # 慢动作
}]
```

### 3. 创建画中画效果

通过多次调用 `add_videos` 创建多个视频轨道：

```python
# 第一次调用 - 主视频（全屏）
add_videos(
    draft_id=draft_id,
    video_infos=[{
        "video_url": "https://example.com/main.mp4",
        "start": 0,
        "end": 10000
    }]
)

# 第二次调用 - 小窗口视频（右上角）
add_videos(
    draft_id=draft_id,
    video_infos=[{
        "video_url": "https://example.com/pip.mp4",
        "start": 2000,
        "end": 8000,
        "scale_x": 0.3,
        "scale_y": 0.3,
        "position_x": 0.6,
        "position_y": -0.6
    }]
)
```

## 常见问题

### Q: material_start 和 start 的区别是什么？

A: 
- `start/end`: 视频在**最终项目时间轴**上的位置
- `material_start/material_end`: 使用**源视频文件**的哪个片段

例如：
```json
{
    "start": 0,
    "end": 5000,
    "material_start": 10000,
    "material_end": 15000
}
```
表示从源视频的10-15秒（5秒）放在最终项目的0-5秒位置。

### Q: 如何实现视频循环播放？

A: 可以多次添加同一视频的不同时间段：

```python
video_infos = [
    {"video_url": "url", "start": 0, "end": 3000},
    {"video_url": "url", "start": 3000, "end": 6000},
    {"video_url": "url", "start": 6000, "end": 9000}
]
```

### Q: speed 和 material_range 如何配合使用？

A: 
- `material_range` 先裁剪源视频
- `speed` 然后调整播放速度

例如：
```json
{
    "material_start": 0,
    "material_end": 10000,  // 取源视频的10秒
    "speed": 2.0,           // 2倍速播放
    "start": 0,
    "end": 5000             // 在时间轴上占5秒（10秒÷2倍速）
}
```

### Q: 可以同时使用 speed 和 reverse 吗？

A: 可以。两个参数独立工作：
```json
{
    "speed": 0.5,    // 0.5倍速（慢动作）
    "reverse": true  // 反向播放
}
```
这会产生慢动作倒放的效果。
