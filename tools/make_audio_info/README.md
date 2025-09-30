# Make Audio Info Tool

## 功能描述

生成单个音频配置的 JSON 字符串表示。这是 `add_audios` 工具的辅助函数，用于创建可以被组合成数组的音频信息字符串。

### 使用场景

当你需要在 Coze 工作流中动态构建多个音频配置时，可以：
1. 多次调用 `make_audio_info` 生成每个音频的配置字符串
2. 将这些字符串收集到一个数组中
3. 将该数组作为 `audio_infos` 参数传递给 `add_audios` 工具

### 参数数量说明

本工具共有 **10 个参数**：
- **3 个必需参数**: `audio_url`, `start`, `end`
- **7 个可选参数**: `volume`, `fade_in`, `fade_out`, `effect_type`, `effect_intensity`, `speed`, `material_start/material_end`

这些参数基于 `pyJianYingDraft` 库的 AudioSegmentConfig 设计，映射了剪映中音频片段的主要可配置属性。

## 输入参数

### Input 类型定义

```python
class Input(NamedTuple):
    # 必需字段
    audio_url: str                              # 音频URL
    start: int                                  # 开始时间（毫秒）
    end: int                                    # 结束时间（毫秒）
    
    # 可选：音频属性
    volume: Optional[float] = 1.0               # 音量（0.0-2.0，默认1.0）
    fade_in: Optional[int] = 0                  # 淡入时长（毫秒）
    fade_out: Optional[int] = 0                 # 淡出时长（毫秒）
    
    # 可选：音频效果
    effect_type: Optional[str] = None           # 音频效果类型（如"变声"、"混响"）
    effect_intensity: Optional[float] = 1.0     # 效果强度（0.0-1.0）
    
    # 可选：速度控制
    speed: Optional[float] = 1.0                # 播放速度（0.5-2.0，默认1.0）
    
    # 可选：素材范围（裁剪音频）
    material_start: Optional[int] = None        # 素材开始时间（毫秒）
    material_end: Optional[int] = None          # 素材结束时间（毫秒）
```

### 参数说明

#### 必需参数
- `audio_url`: 音频的 URL 地址
- `start`: 音频在时间轴上的开始时间（毫秒）
- `end`: 音频在时间轴上的结束时间（毫秒）

#### 可选参数

**音频属性**:
- `volume`: 音量级别，范围 0.0-2.0，默认 1.0（原始音量）
- `fade_in`: 淡入效果持续时间（毫秒），默认 0（无淡入）
- `fade_out`: 淡出效果持续时间（毫秒），默认 0（无淡出）

**音频效果**:
- `effect_type`: 音频效果类型，如 "变声"、"混响"、"回声" 等
- `effect_intensity`: 效果强度，范围 0.0-1.0，默认 1.0

**速度控制**:
- `speed`: 播放速度，范围 0.5-2.0，默认 1.0（原速）
  - 小于 1.0: 慢速播放
  - 大于 1.0: 快速播放

**素材范围**（裁剪音频）:
- `material_start` 和 `material_end`: 用于裁剪音频文件的特定部分
- 这两个参数必须同时提供
- 示例：如果音频文件是 60 秒，你可以只使用其中 10-30 秒的部分

#### 参数来源与 pyJianYingDraft 的关系

本工具的参数设计基于 `pyJianYingDraft` 库的 `AudioSegmentConfig` 类：

1. **基本参数**:
   - `material_url` → `audio_url`
   - `time_range` → `start/end`
   - `material_range` → `material_start/material_end`

2. **音频属性**:
   - `volume`: 音量控制
   - `fade_in`: 淡入时长
   - `fade_out`: 淡出时长

3. **音频效果**:
   - `effect_type`: 效果类型
   - `effect_intensity`: 效果强度

4. **速度控制**:
   - `speed`: 播放速度

## 输出结果

### Output 类型定义

```python
class Output(NamedTuple):
    audio_info_string: str                      # 音频信息的 JSON 字符串
    success: bool                               # 操作是否成功
    message: str                                # 状态消息
```

### 输出格式

输出是一个紧凑的 JSON 字符串，例如：

```json
"{\"audio_url\":\"https://example.com/audio.mp3\",\"start\":0,\"end\":5000}"
```

或带有可选参数：

```json
"{\"audio_url\":\"https://example.com/audio.mp3\",\"start\":0,\"end\":5000,\"volume\":0.8,\"fade_in\":1000,\"fade_out\":1000}"
```

## 使用示例

### 示例 1: 基本用法

```python
from tools.make_audio_info.handler import handler, Input
from runtime import Args

# 创建输入参数（仅必需字段）
input_data = Input(
    audio_url="https://example.com/background_music.mp3",
    start=0,
    end=30000  # 30秒
)

# 模拟Args对象
class MockArgs:
    def __init__(self, input_data):
        self.input = input_data

# 调用处理函数
result = handler(MockArgs(input_data))

print(f"成功: {result.success}")
print(f"生成的字符串: {result.audio_info_string}")
# 输出: {"audio_url":"https://example.com/background_music.mp3","start":0,"end":30000}
```

### 示例 2: 带淡入淡出效果

```python
# 创建输入参数（包含淡入淡出）
input_data = Input(
    audio_url="https://example.com/background_music.mp3",
    start=0,
    end=30000,
    volume=0.7,
    fade_in=2000,   # 2秒淡入
    fade_out=3000   # 3秒淡出
)

result = handler(MockArgs(input_data))
print(result.audio_info_string)
# 输出: {"audio_url":"https://example.com/background_music.mp3","start":0,"end":30000,"volume":0.7,"fade_in":2000,"fade_out":3000}
```

### 示例 3: 使用音频效果和速度控制

```python
# 创建输入参数（包含效果和速度）
input_data = Input(
    audio_url="https://example.com/voice.mp3",
    start=0,
    end=10000,
    effect_type="变声",
    effect_intensity=0.8,
    speed=1.2  # 加速20%
)

result = handler(MockArgs(input_data))
print(result.audio_info_string)
# 输出: {"audio_url":"https://example.com/voice.mp3","start":0,"end":10000,"effect_type":"变声","effect_intensity":0.8,"speed":1.2}
```

### 示例 4: 裁剪音频片段

```python
# 使用音频文件的特定部分（10秒-30秒）
input_data = Input(
    audio_url="https://example.com/long_audio.mp3",
    start=0,
    end=20000,  # 在时间轴上显示20秒
    material_start=10000,  # 从音频文件的第10秒开始
    material_end=30000     # 到音频文件的第30秒结束
)

result = handler(MockArgs(input_data))
print(result.audio_info_string)
# 输出: {"audio_url":"https://example.com/long_audio.mp3","start":0,"end":20000,"material_start":10000,"material_end":30000}
```

### 示例 5: 与 add_audios 配合使用（完整工作流）

这是本工具的主要使用场景：

```python
# 步骤 1: 使用 make_audio_info 生成多个音频信息字符串
audio1_info = make_audio_info(
    audio_url="https://example.com/bgm.mp3",
    start=0,
    end=30000,
    volume=0.3,
    fade_in=2000
)
# 返回: {"audio_url":"https://example.com/bgm.mp3","start":0,"end":30000,"volume":0.3,"fade_in":2000}

audio2_info = make_audio_info(
    audio_url="https://example.com/narration.mp3",
    start=5000,
    end=25000,
    volume=0.9
)
# 返回: {"audio_url":"https://example.com/narration.mp3","start":5000,"end":25000,"volume":0.9}

# 步骤 2: 将字符串收集到数组中
audio_infos_array = [
    audio1_info.audio_info_string,
    audio2_info.audio_info_string
]

# 步骤 3: 将数组字符串传递给 add_audios
add_audios(
    draft_id="your-draft-uuid",
    audio_infos=audio_infos_array  # 数组字符串格式！
)
```

### 示例 6: 在 Coze 工作流中使用

在 Coze 工作流中，你可以这样组合使用：

```
1. [make_audio_info 节点1] → 生成背景音乐配置字符串
   输入: audio_url="https://...", start=0, end=30000, volume=0.3
   输出: audio_info_string

2. [make_audio_info 节点2] → 生成旁白配置字符串
   输入: audio_url="https://...", start=5000, end=25000
   输出: audio_info_string

3. [数组节点] → 将多个字符串组合成数组
   输入: [节点1.audio_info_string, 节点2.audio_info_string]
   输出: audio_infos_array

4. [add_audios 节点] → 添加音频到草稿
   输入: draft_id="...", audio_infos=audio_infos_array
   输出: segment_ids, segment_infos
```

## 注意事项

### 输出优化
- 工具只会在输出中包含非默认值的参数
- 这使得输出字符串保持紧凑，减少数据传输
- 例如：如果 `volume=1.0`（默认值），则不会包含在输出中

### 时间参数验证
- `start` 必须 >= 0
- `end` 必须 > `start`
- 时间单位为毫秒
- `material_start` 和 `material_end` 必须同时提供

### 参数范围验证
- `volume`: 0.0 到 2.0
- `speed`: 0.5 到 2.0
- `fade_in`, `fade_out`: >= 0
- `effect_intensity`: 0.0 到 1.0

### 与 add_audios 的兼容性
- 输出的字符串格式完全兼容 `add_audios` 的 `audio_infos` 参数
- 可以使用数组字符串格式（推荐）、数组对象格式或 JSON 字符串格式

## 错误处理

工具会验证以下情况：

1. **缺少必需参数**: 如果缺少 `audio_url`、`start` 或 `end`，返回错误
2. **无效时间范围**: 如果 `start < 0` 或 `end <= start`，返回错误
3. **参数范围错误**: 如果 `volume`、`speed` 等超出有效范围，返回错误
4. **素材范围不完整**: 如果只提供 `material_start` 或 `material_end` 其中一个，返回错误
5. **其他异常**: 任何意外错误都会被捕获并返回错误消息

## 与其他工具的关系

### make_audio_info → add_audios
这是主要的使用流程：
1. `make_audio_info` 生成单个音频的配置字符串
2. 多个字符串组合成数组
3. `add_audios` 接收数组并添加音频到草稿

### 替代方案
如果你的音频配置是静态的，也可以：
- 直接使用数组对象格式传递给 `add_audios`
- 使用 JSON 字符串格式传递给 `add_audios`

`make_audio_info` 主要用于需要动态构建配置的场景。

## 音频效果类型参考

常见的音频效果类型（基于剪映功能）：
- `"变声"` - 变声效果
- `"混响"` - 混响效果
- `"回声"` - 回声效果
- `"立体声"` - 立体声增强
- `"均衡器"` - 音频均衡

**注意**: 具体支持的效果类型取决于剪映版本和 pyJianYingDraft 库的实现。
