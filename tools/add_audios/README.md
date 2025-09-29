# Add Audios Tool

## 功能描述

向现有的草稿中添加音频片段，每次调用会创建一个包含所有指定音频的新音频轨道。该工具允许您在剪映草稿中添加背景音乐、音效、旁白等各种音频内容，支持丰富的音频处理参数设置。

### 核心特性
- 支持多种音频格式（MP3、WAV、AAC等）
- 灵活的音频时间轴控制
- 音量调节和淡入淡出效果
- 音频特效和速度控制
- 音频片段裁剪功能
- 动态音量关键帧支持

## 输入参数

### Input 类型定义

```python
class Input(NamedTuple):
    draft_id: str                              # 现有草稿的UUID
    audio_infos: Any                           # 音频信息：支持多种格式输入
```

### audio_infos 输入格式

支持多种输入格式，自动识别和处理：

#### 格式1：数组对象（推荐）
```json
[
  {
    "audio_url": "https://example.com/background_music.mp3",
    "start": 0,
    "end": 30000,
    "volume": 0.8,
    "fade_in": 1000,
    "fade_out": 2000,
    "effect_type": "reverb",
    "effect_intensity": 0.5,
    "speed": 1.0,
    "material_start": 0,
    "material_end": 30000
  }
]
```

#### 格式2：JSON字符串
```json
"[{\"audio_url\":\"https://example.com/music.mp3\",\"start\":0,\"end\":30000,\"volume\":0.8}]"
```

#### 格式3：其他可迭代类型
系统会自动尝试转换为标准的字典列表格式。

#### 必需字段
- `audio_url` (str): 音频文件的URL地址
- `start` (int): 音频在时间轴上的开始时间（毫秒）
- `end` (int): 音频在时间轴上的结束时间（毫秒）

#### 可选字段
- `volume` (float): 音量大小（0.0-2.0，默认1.0）
- `fade_in` (int): 淡入时长（毫秒，默认0）
- `fade_out` (int): 淡出时长（毫秒，默认0）
- `effect_type` (str): 音频特效类型（如"reverb"、"echo"等）
- `effect_intensity` (float): 特效强度（0.0-1.0，默认1.0）
- `speed` (float): 播放速度（0.5-2.0，默认1.0）
- `material_start` (int): 原音频素材的开始裁剪点（毫秒）
- `material_end` (int): 原音频素材的结束裁剪点（毫秒）

## 输出结果

### Output 类型定义

```python
class Output(NamedTuple):
    segment_ids: List[str]                     # 生成的音频片段UUID列表
    segment_infos: List[Dict[str, Any]]        # 片段信息列表（id, start, end）
    success: bool                              # 操作成功状态
    message: str                               # 状态消息
```

### 输出示例
```json
{
  "segment_ids": [
    "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "b2c3d4e5-f6g7-8901-bcde-f23456789012"
  ],
  "segment_infos": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "start": 0,
      "end": 30000
    },
    {
      "id": "b2c3d4e5-f6g7-8901-bcde-f23456789012",
      "start": 30000,
      "end": 60000
    }
  ],
  "success": true,
  "message": "成功添加 2 个音频片段"
}
```

## 使用示例

### 基本用法

#### 方法1：使用数组格式（推荐）

```python
from tools.add_audios.handler import handler, Input
from runtime import Args

# 创建输入参数（数组格式）
input_data = Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    audio_infos=[{
        "audio_url": "https://example.com/background_music.mp3",
        "start": 0,
        "end": 30000,
        "volume": 0.8,
        "fade_in": 1000,
        "fade_out": 2000
    }]
)

# 模拟Args对象
class MockArgs:
    def __init__(self, input_data):
        self.input = input_data

# 调用处理函数
result = handler(MockArgs(input_data))

print(f"成功: {result.success}")
print(f"音频片段数量: {len(result.segment_ids)}")
print(f"片段ID: {result.segment_ids}")
print(f"消息: {result.message}")
```

#### 方法2：使用JSON字符串格式

```python
input_data = Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    audio_infos='[{"audio_url":"https://example.com/music.mp3","start":0,"end":30000,"volume":0.8}]'
)

result = handler(MockArgs(input_data))
print(f"操作结果: {result.success}")
```

### 复杂参数示例

#### 多音频轨道示例：
```python
input_data = Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    audio_infos=[
        {
            "audio_url": "https://example.com/background_music.mp3",
            "start": 0,
            "end": 60000,
            "volume": 0.6,
            "fade_in": 2000,
            "fade_out": 3000,
            "effect_type": "reverb",
            "effect_intensity": 0.3,
            "speed": 1.0
        },
        {
            "audio_url": "https://example.com/sound_effect.wav",
            "start": 10000,
            "end": 15000,
            "volume": 1.2,
            "effect_type": "echo",
            "effect_intensity": 0.7,
            "material_start": 5000,
            "material_end": 10000
        },
        {
            "audio_url": "https://example.com/narration.aac",
            "start": 20000,
            "end": 45000,
            "volume": 1.0,
            "fade_in": 500,
            "fade_out": 1000,
            "speed": 0.9
        }
    ]
)
```

#### JSON字符串格式：
```json
"[{\"audio_url\":\"https://example.com/music.mp3\",\"start\":0,\"end\":30000,\"volume\":0.8,\"fade_in\":1000,\"fade_out\":2000,\"effect_type\":\"reverb\",\"effect_intensity\":0.5}]"
```

## 注意事项

### 参数约束
- `start` 和 `end` 必须为非负整数，且 `end > start`
- `volume` 建议范围 0.0-2.0，超出范围可能导致音频失真
- `fade_in` 和 `fade_out` 不能超过音频片段的总时长
- `speed` 建议范围 0.5-2.0，极端值可能影响音频质量
- `effect_intensity` 范围 0.0-1.0

### 错误处理
- 如果draft_id不存在，返回失败状态
- 如果audio_infos格式无效，返回详细错误信息
- 如果音频URL无法访问，仍会创建片段（由草稿生成器处理）
- 参数验证失败时提供具体的错误描述

### 性能考虑
- 大量音频可能影响处理性能
- 建议单次调用音频数量控制在20个以内
- 长时间的音频文件可能影响处理速度
- 复杂的音频特效会增加渲染时间

### 音频格式支持
- 推荐格式：MP3、WAV、AAC、M4A
- 支持的采样率：8kHz - 192kHz
- 支持的比特率：根据格式而定
- 单声道和立体声均支持

## 与其他工具的集成

### 与 create_draft 的配合使用
```python
# 1. 首先创建草稿
from tools.create_draft.handler import handler as create_handler
draft_result = create_handler(draft_args)
draft_id = draft_result.draft_id

# 2. 然后添加音频
audio_result = handler(MockArgs(Input(
    draft_id=draft_id,
    audio_infos=[{"audio_url": "...", "start": 0, "end": 30000}]
)))
```

### 与 export_drafts 的配合使用
```python
# 添加音频后导出草稿
from tools.export_drafts.handler import handler as export_handler
export_result = export_handler(export_args)
```

### 与 get_media_duration 的配合使用
```python
# 获取音频时长后设置正确的时间范围
from tools.get_media_duration.handler import handler as duration_handler
duration_result = duration_handler(duration_args)
# 使用 duration_result 中的信息设置 start 和 end
```

## 数据结构说明

### 音频片段数据结构
每个音频片段在草稿中存储为以下结构：
```json
{
  "id": "uuid-string",
  "type": "audio",
  "material_url": "https://example.com/audio.mp3",
  "time_range": {
    "start": 0,
    "end": 30000
  },
  "material_range": {
    "start": 0,
    "end": 30000
  },
  "audio": {
    "volume": 1.0,
    "fade_in": 1000,
    "fade_out": 2000,
    "effect_type": "reverb",
    "effect_intensity": 0.5,
    "speed": 1.0
  },
  "keyframes": {
    "volume": []
  }
}
```

### 音频轨道结构
```json
{
  "track_type": "audio",
  "muted": false,
  "volume": 1.0,
  "segments": [...]
}
```

## 最佳实践

1. **音频时长规划**: 提前规划好各音频片段的时间分配
2. **音量平衡**: 注意不同音频间的音量平衡
3. **淡入淡出**: 适当使用淡入淡出避免突兀的音频切换
4. **特效使用**: 谨慎使用音频特效，避免过度处理
5. **性能优化**: 对于大型项目，分批次添加音频片段