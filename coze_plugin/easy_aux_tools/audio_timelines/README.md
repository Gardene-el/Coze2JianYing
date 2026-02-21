# audio_timelines

## 功能描述

接收各段音频的时长列表，按顺序累加生成首尾相接的时间线 JSON 字符串。

通常与 `get_media_duration` 工具配合：先获取每个音频文件的时长，再传入本工具生成时间线。

### 使用场景

1. 多首背景音乐顺序播放，每首时长不同
2. 配音文件按实际时长排列时间线
3. 生成的时间线再传给 `audio_infos` 使用

## 输入参数

```python
class Input(NamedTuple):
    durations_us: str   # 各段时长（微秒），英文逗号分隔，如 "5000000,4000000,6000000"
    start: int = 0      # 起始偏移（微秒，默认 0）
```

### 参数说明

| 参数           | 类型 | 必填 | 说明                                 |
| -------------- | ---- | ---- | ------------------------------------ |
| `durations_us` | str  | ✅   | 逗号分隔的时长列表，每个值为微秒整数 |
| `start`        | int  | ❌   | 起始偏移，默认 0                     |

## 输出

```python
class Output(NamedTuple):
    timelines: str      # JSON 字符串：[{"start":…,"end":…},…]
    all_timelines: str  # 同 timelines（兼容字段）
    success: bool
    message: str
```

## 示例

输入：`durations_us="5000000,4000000,6000000"`

输出 `timelines`：

```json
[
  { "start": 0, "end": 5000000 },
  { "start": 5000000, "end": 9000000 },
  { "start": 9000000, "end": 15000000 }
]
```

## 工作流衔接

```
get_media_duration (×N) → 收集 durations → audio_timelines → audio_infos → add_audios
```
