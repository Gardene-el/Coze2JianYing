# timelines

## 功能描述

将总时长分割为 N 段时间线，返回 `[{"start":…,"end":…},…]` 格式的 JSON 字符串。

支持两种分割模式：

- **平均分割**（默认）：每段时长相同，最后一段补足余量
- **随机分割**：生成随机长度的 N 段，总和等于 `duration`

### 使用场景

1. 将一段背景音乐时长均分给 N 张图片
2. 生成随机节奏的视频切换时间线
3. 配合 `audio_infos`、`imgs_infos`、`video_infos` 等工具使用

## 输入参数

```python
class Input(NamedTuple):
    duration: int       # 总时长（微秒）
    num: int            # 分割段数
    start: int = 0      # 起始偏移（微秒，默认 0）
    split_type: int = 0 # 0=平均分割，1=随机分割
```

### 参数说明

| 参数         | 类型 | 必填 | 说明                                      |
| ------------ | ---- | ---- | ----------------------------------------- |
| `duration`   | int  | ✅   | 总时长，单位微秒（1 秒 = 1,000,000 微秒） |
| `num`        | int  | ✅   | 分割成几段                                |
| `start`      | int  | ❌   | 整个时间线的起始偏移，默认 0              |
| `split_type` | int  | ❌   | 0=平均（默认），1=随机                    |

## 输出

```python
class Output(NamedTuple):
    timelines: str      # JSON 字符串：[{"start":…,"end":…},…]
    all_timelines: str  # 同 timelines（兼容字段）
    success: bool
    message: str
```

## 示例

输入：`duration=15000000, num=3`

输出 `timelines`：

```json
[
  { "start": 0, "end": 5000000 },
  { "start": 5000000, "end": 10000000 },
  { "start": 10000000, "end": 15000000 }
]
```

## 工作流衔接

```
timelines → video_infos → add_videos
timelines → imgs_infos  → add_images
timelines → effect_infos → add_effects
```
