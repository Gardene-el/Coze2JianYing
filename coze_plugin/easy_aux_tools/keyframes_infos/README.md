# keyframes_infos

## 功能描述

根据关键帧类型、百分比偏移量和值，结合片段信息，
生成 `add_keyframes` 工具所需的关键帧配置 JSON 字符串。

百分比偏移自动换算为各片段内的绝对时间（微秒）；
位置类关键帧（PositionX/Y）自动按草稿分辨率归一化。

纯计算工具，无网络请求，无文件 I/O。

## 输入参数

```python
class Input(NamedTuple):
    ctype: str                      # 关键帧类型，见下表
    offsets: str                    # 百分比偏移，| 分隔，如 "0|50|100"
    values: str                     # 对应值，| 分隔，如 "0|1|0"
    segment_infos: str              # 片段信息 JSON 字符串
    height: Optional[int] = None    # 草稿高度（像素，KFTypePositionY 归一化用）
    width: Optional[int] = None     # 草稿宽度（像素，KFTypePositionX 归一化用）
```

### 关键帧类型 (ctype)

| ctype             | 含义     | 值范围   | 归一化        |
| ----------------- | -------- | -------- | ------------- |
| `KFTypePositionX` | 水平位移 | 像素     | 除以 `width`  |
| `KFTypePositionY` | 垂直位移 | 像素     | 除以 `height` |
| `KFTypeRotation`  | 旋转     | 度（°）  | 无            |
| `UNIFORM_SCALE`   | 等比缩放 | 1.0=原始 | 无            |
| `KFTypeAlpha`     | 透明度   | 0.0–1.0  | 无            |
| `KFTypeScaleX`    | X 轴缩放 | 1.0=原始 | 无            |
| `KFTypeScaleY`    | Y 轴缩放 | 1.0=原始 | 无            |

### segment_infos 格式

```json
[
  { "id": "片段UUID1", "start": 0, "end": 5000000 },
  { "id": "片段UUID2", "start": 5000000, "end": 10000000 }
]
```

通常来自 `add_images`、`add_videos`、`add_captions` 等工具的 `segment_infos` 输出字段。

## 输出

```python
class Output(NamedTuple):
    keyframes_infos: str    # add_keyframes 所需的 JSON 字符串
    success: bool
    message: str
```

### 输出格式

```json
[
  {
    "segment_id": "uuid1",
    "property": "UNIFORM_SCALE",
    "offset": 0,
    "value": 0.0
  },
  {
    "segment_id": "uuid1",
    "property": "UNIFORM_SCALE",
    "offset": 2500000,
    "value": 1.0
  },
  {
    "segment_id": "uuid1",
    "property": "UNIFORM_SCALE",
    "offset": 5000000,
    "value": 0.0
  }
]
```

## 示例：缩放动画

所有片段从 0 缩放到 1.0 再回到 0：

```
ctype   = "UNIFORM_SCALE"
offsets = "0|50|100"
values  = "0|1|0"
```

## 工作流衔接

```
add_images (segment_infos 输出) → keyframes_infos → add_keyframes
add_videos (segment_infos 输出) → keyframes_infos → add_keyframes
```
