# Add Audios Tool

## 功能描述

向现有草稿添加音频轨道和音频片段。每次调用会创建一个新的音频轨道，包含指定的所有音频。支持音频的音量、淡入淡出、效果等完整参数设置。

## 输入参数

### Input 类型定义

```python
class Input(NamedTuple):
    draft_id: str                              # 现有草稿的UUID
    audio_infos: Any                           # 音频信息：支持多种格式输入
```

### audio_infos 输入格式

支持多种输入格式，自动识别和处理：

#### 格式1：数组对象（推荐用于静态配置）
```json
[
  {
    "audio_url": "https://example.com/bgm.mp3",
    "start": 0,
    "end": 30000,
    "volume": 0.7,
    "fade_in": 2000,
    "fade_out": 3000
  }
]
```

#### 格式2：数组字符串（推荐用于动态配置）
数组中每个元素是 JSON 字符串。通常与 `make_audio_info` 工具配合使用：
```json
[
  "{\"audio_url\":\"https://example.com/bgm.mp3\",\"start\":0,\"end\":30000,\"volume\":0.7}",
  "{\"audio_url\":\"https://example.com/narration.mp3\",\"start\":5000,\"end\":25000,\"volume\":0.9}"
]
```

#### 格式3：JSON字符串
整个数组作为一个 JSON 字符串：
```json
"[{\"audio_url\":\"https://example.com/bgm.mp3\",\"start\":0,\"end\":30000,\"volume\":0.7}]"
```

#### 格式4：其他可迭代类型
工具还支持元组(tuple)等其他可迭代类型，会自动转换为列表处理。

#### 必需字段
- `audio_url`: 音频的URL链接
- `start`: 开始时间（毫秒）
- `end`: 结束时间（毫秒）

#### 可选字段
- `volume`: 音量（0.0-2.0，默认1.0）
- `fade_in`: 淡入时长（毫秒，默认0）
- `fade_out`: 淡出时长（毫秒，默认0）
- `effect_type`: 音频效果类型（如"变声"、"混响"）
- `effect_intensity`: 效果强度（0.0-1.0，默认1.0）
- `speed`: 播放速度（0.5-2.0，默认1.0）
- `material_start`: 素材开始时间（毫秒，用于裁剪）
- `material_end`: 素材结束时间（毫秒，用于裁剪）

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
    "end": 30000
  }
]
```

## 使用示例

### 基本用法

#### 方法1：使用数组格式（推荐用于静态配置）

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
        "volume": 0.3,
        "fade_in": 2000,
        "fade_out": 3000
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

配合 `make_audio_info` 工具使用：

```python
from tools.make_audio_info.handler import handler as make_audio_info_handler
from tools.add_audios.handler import handler as add_audios_handler

# 步骤1: 使用 make_audio_info 生成音频信息字符串
audio1_result = make_audio_info_handler(MockArgs(Input(
    audio_url="https://example.com/bgm.mp3",
    start=0,
    end=30000,
    volume=0.3,
    fade_in=2000
)))

audio2_result = make_audio_info_handler(MockArgs(Input(
    audio_url="https://example.com/narration.mp3",
    start=5000,
    end=25000,
    volume=0.9
)))

# 步骤2: 将字符串收集到数组中
audio_infos_array = [
    audio1_result.audio_info_string,
    audio2_result.audio_info_string
]

# 步骤3: 传递数组字符串给 add_audios
result = add_audios_handler(MockArgs(Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    audio_infos=audio_infos_array  # 数组字符串格式
)))

print(f"成功添加 {len(result.segment_ids)} 个音频")
```

#### 方法3：使用JSON字符串格式

```python
# 创建输入参数（JSON字符串格式）
input_data = Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    audio_infos='[{"audio_url":"https://example.com/bgm.mp3","start":0,"end":30000,"volume":0.7}]'
)
```

### 复杂参数示例

#### 背景音乐 + 旁白配置

```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "audio_infos": [
        {
            "audio_url": "https://example.com/background_music.mp3",
            "start": 0,
            "end": 45000,
            "volume": 0.3,
            "fade_in": 2000,
            "fade_out": 3000
        },
        {
            "audio_url": "https://example.com/narration.mp3",
            "start": 5000,
            "end": 40000,
            "volume": 1.0
        }
    ]
}
```

#### 使用音频效果和速度控制

```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "audio_infos": [
        {
            "audio_url": "https://example.com/voice.mp3",
            "start": 0,
            "end": 10000,
            "volume": 0.9,
            "effect_type": "变声",
            "effect_intensity": 0.8,
            "speed": 1.2
        }
    ]
}
```

#### 裁剪音频片段

```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "audio_infos": [
        {
            "audio_url": "https://example.com/long_music.mp3",
            "start": 0,
            "end": 20000,
            "material_start": 10000,
            "material_end": 30000,
            "volume": 0.5
        }
    ]
}
```

## 注意事项

### 时间单位
- 所有时间参数使用毫秒(ms)为单位
- `start` 和 `end` 定义音频在时间轴上的播放区间
- `fade_in` 和 `fade_out` 使用毫秒为单位

### 音量控制
- `volume` 范围为 0.0 到 2.0
- 1.0 表示原始音量
- 小于 1.0: 降低音量
- 大于 1.0: 增大音量（可能导致音质损失）

### 轨道管理
- 每次调用都会创建一个新的音频轨道
- 同一轨道内的音频按时间顺序排列
- 不同轨道的音频会被混合播放

### 素材裁剪
- `material_start` 和 `material_end` 用于从音频文件中截取特定部分
- 这两个参数必须同时提供
- 示例：从60秒的音频文件中截取10-30秒的部分

### 错误处理
- 如果draft_id不存在，返回失败状态
- 如果audio_infos格式无效，返回详细错误信息
- 如果音频URL无法访问，仍会创建片段（由草稿生成器处理）

### 性能考虑
- 大量音频可能影响处理性能
- 建议单次调用音频数量控制在20个以内
- 音频效果和速度调整会增加处理复杂度

## 与其他工具的集成

### 与 create_draft 配合使用
1. 使用 `create_draft` 创建基础草稿
2. 使用 `add_images` 添加图片轨道（可选）
3. 使用 `add_audios` 添加音频轨道
4. 使用 `export_drafts` 导出完整配置

### 与 get_media_duration 配合使用
1. 使用 `get_media_duration` 获取音频时长信息
2. 根据时长信息设置音频的 `start` 和 `end` 参数
3. 使用 `add_audios` 添加到草稿

### 典型工作流

```
1. create_draft → 创建草稿
2. add_images → 添加图片/视频轨道
3. make_audio_info (多次) → 生成音频配置字符串
4. add_audios → 添加音频轨道
5. export_drafts → 导出草稿配置
```

## 常见用例

### 用例1：背景音乐
```python
# 添加循环背景音乐，音量较低，带淡入淡出
audio_infos = [{
    "audio_url": "https://example.com/bgm.mp3",
    "start": 0,
    "end": 60000,
    "volume": 0.3,
    "fade_in": 2000,
    "fade_out": 3000
}]
```

### 用例2：旁白配音
```python
# 添加清晰的旁白，音量正常
audio_infos = [{
    "audio_url": "https://example.com/narration.mp3",
    "start": 5000,
    "end": 55000,
    "volume": 1.0
}]
```

### 用例3：音效
```python
# 添加短音效，无淡入淡出
audio_infos = [{
    "audio_url": "https://example.com/click.mp3",
    "start": 10000,
    "end": 10500,
    "volume": 0.8
}]
```

### 用例4：多层音频混合
```python
# 同时添加背景音乐、旁白和音效（创建三个不同轨道）
# 第一次调用 - 背景音乐
add_audios(draft_id, [{
    "audio_url": "https://example.com/bgm.mp3",
    "start": 0,
    "end": 60000,
    "volume": 0.3
}])

# 第二次调用 - 旁白
add_audios(draft_id, [{
    "audio_url": "https://example.com/narration.mp3",
    "start": 5000,
    "end": 55000,
    "volume": 1.0
}])

# 第三次调用 - 音效
add_audios(draft_id, [{
    "audio_url": "https://example.com/effect.mp3",
    "start": 10000,
    "end": 11000,
    "volume": 0.8
}])
```

## 数据结构参考

本工具生成的音频轨道遵循以下数据结构（与 `data_structures/draft_generator_interface/models.py` 中的 `AudioSegmentConfig` 保持一致）：

```json
{
  "track_type": "audio",
  "muted": false,
  "volume": 1.0,
  "segments": [
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
        "volume": 0.7,
        "fade_in": 2000,
        "fade_out": 3000,
        "effect_type": null,
        "effect_intensity": 1.0,
        "speed": 1.0
      },
      "keyframes": {
        "volume": []
      }
    }
  ]
}
```
