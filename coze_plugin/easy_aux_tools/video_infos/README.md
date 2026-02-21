# video_infos

## 功能描述

将视频 URL 列表与时间线合并，生成 `add_videos` 工具所需的 `video_infos` JSON 字符串。

自动计算每段视频的 `duration = end - start`，可附加遮罩、转场、音量等元数据。

纯计算工具，无网络请求，无文件 I/O。

## 输入参数

```python
class Input(NamedTuple):
    video_urls: str                         # 视频 URL 数组，JSON 字符串
    timelines: str                          # 时间线 JSON 字符串
    height: Optional[int] = None            # 视频高度（像素，遮罩/裁切参考用）
    width: Optional[int] = None             # 视频宽度（像素）
    mask: Optional[str] = None              # 遮罩类型：圆形/矩形/爱心/星形
    transition: Optional[str] = None        # 转场类型（统一应用）
    transition_duration: Optional[int] = None   # 转场时长（微秒）
    volume: Optional[float] = 1.0           # 音量（0.0–10.0，默认 1.0）
```

### 参数说明

| 参数         | 必填 | 说明                                                           |
| ------------ | ---- | -------------------------------------------------------------- |
| `video_urls` | ✅   | JSON 字符串，与 timelines 等长                                 |
| `timelines`  | ✅   | 来自 `timelines/` 工具的输出                                   |
| `mask`       | ❌   | 统一应用到所有视频的遮罩形状                                   |
| `transition` | ❌   | 统一转场类型；名称来自 `pyJianYingDraft.TransitionType` 成员名 |
| `volume`     | ❌   | 视频原声音量，默认 1.0（保持原音量）                           |

## 输出

```python
class Output(NamedTuple):
    video_infos: str    # add_videos 所需的 JSON 字符串
    success: bool
    message: str
```

### 输出格式

```json
[
  {
    "video_url": "https://…/1.mp4",
    "start": 0,
    "end": 5000000,
    "duration": 5000000,
    "volume": 1.0,
    "transition": "叠化"
  }
]
```

## 工作流衔接

```
timelines → video_infos → add_videos
```
