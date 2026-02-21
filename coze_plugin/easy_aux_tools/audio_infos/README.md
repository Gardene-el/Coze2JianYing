# audio_infos

## 功能描述

将音频 URL 列表与时间线合并，生成 `add_audios` 工具所需的 `audio_infos` JSON 字符串。

纯计算工具，无网络请求，无文件 I/O。

### 使用场景

1. 一批背景音乐文件，配合 `audio_timelines` 生成的时间线，构建 add_audios 输入
2. 统一为所有音频设置音量或效果

## 输入参数

```python
class Input(NamedTuple):
    mp3_urls: str                    # 音频 URL 数组，JSON 字符串，如 '["url1","url2"]'
    timelines: str                   # 时间线 JSON 字符串，来自 timelines/ 或 audio_timelines/
    audio_effect: Optional[str] = None   # 可选：统一音频效果名称
    volume: Optional[float] = None       # 可选：音量（0.0–2.0）
```

### 参数说明

| 参数           | 类型  | 必填 | 说明                                               |
| -------------- | ----- | ---- | -------------------------------------------------- |
| `mp3_urls`     | str   | ✅   | JSON 数组字符串，与 timelines 等长                 |
| `timelines`    | str   | ✅   | JSON 数组字符串，格式 `[{"start":…,"end":…},…]`    |
| `audio_effect` | str   | ❌   | 统一应用的音频效果名称                             |
| `volume`       | float | ❌   | 音量，范围 0.0–2.0，默认不设置（沿用素材原始音量） |

## 输出

```python
class Output(NamedTuple):
    audio_infos: str    # add_audios 所需的 JSON 字符串
    success: bool
    message: str
```

### 输出格式

```json
[
  { "audio_url": "https://…/a.mp3", "start": 0, "end": 5000000, "volume": 0.8 },
  {
    "audio_url": "https://…/b.mp3",
    "start": 5000000,
    "end": 9000000,
    "volume": 0.8
  }
]
```

## 工作流衔接

```
audio_timelines → audio_infos → add_audios
timelines       → audio_infos → add_audios
```
