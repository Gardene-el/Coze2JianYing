# imgs_infos

## 功能描述

将图片 URL 列表与时间线合并，生成 `add_images` 工具所需的 `image_infos` JSON 字符串。

动画参数支持两种格式：

- **单值**：所有图片使用相同动画，如 `"渐入"`
- **管道分隔多值**：每张图片使用不同动画，如 `"渐入|浮入|旋转入"`

纯计算工具，无网络请求，无文件 I/O。

## 输入参数

```python
class Input(NamedTuple):
    imgs: str                               # 图片 URL 数组，JSON 字符串
    timelines: str                          # 时间线 JSON 字符串
    height: Optional[int] = None            # 图片高度（像素）
    width: Optional[int] = None             # 图片宽度（像素）
    in_animation: Optional[str] = None     # 入场动画（单值或 | 分隔）
    in_animation_duration: Optional[int] = None   # 入场动画时长（微秒）
    loop_animation: Optional[str] = None   # 循环动画
    loop_animation_duration: Optional[int] = None
    out_animation: Optional[str] = None    # 出场动画
    out_animation_duration: Optional[int] = None
    transition: Optional[str] = None       # 转场类型（单值或 | 分隔）
    transition_duration: Optional[int] = None
```

### 参数说明

| 参数           | 必填 | 说明                                                   |
| -------------- | ---- | ------------------------------------------------------ |
| `imgs`         | ✅   | JSON 字符串，如 `'["url1","url2"]'`，与 timelines 等长 |
| `timelines`    | ✅   | JSON 字符串，格式 `[{"start":…,"end":…},…]`            |
| `in_animation` | ❌   | 单值（所有图片相同）或管道分隔多值（每张图片不同）     |
| `transition`   | ❌   | 转场类型，同上支持单值和管道分隔                       |

### 动画多值示例

`in_animation="渐入|浮入|旋转入"` 时：

- 第 1 张图片使用 `渐入`
- 第 2 张图片使用 `浮入`
- 第 3 张图片使用 `旋转入`
- 第 4 张及后续：无入场动画（超出列表范围）

若使用单值 `in_animation="渐入"`，所有图片都应用 `渐入`。

## 输出

```python
class Output(NamedTuple):
    image_infos: str    # add_images 所需的 JSON 字符串
    success: bool
    message: str
```

### 输出格式

```json
[
  {
    "image_url": "https://…/1.jpg",
    "start": 0,
    "end": 3000000,
    "in_animation": "渐入",
    "in_animation_duration": 500000
  }
]
```

## 工作流衔接

```
timelines → imgs_infos → add_images
```
