# Add Images Tool

## 功能描述

向现有草稿添加图片轨道和图片片段。每次调用会创建一个新的图片轨道，包含指定的所有图片。支持图片的位置、大小、动画等完整参数设置。

## 输入参数

### Input 类型定义

```python
class Input(NamedTuple):
    draft_id: str                              # 现有草稿的UUID
    image_infos: Any                           # 图片信息：支持多种格式输入
```

### image_infos 输入格式

支持多种输入格式，自动识别和处理：

#### 格式1：数组对象（推荐用于静态配置）
```json
[
  {
    "image_url": "https://s.coze.cn/t/W9CvmtJHJWI/",
    "start": 0,
    "end": 3936000,
    "width": 1440,
    "height": 1080,
    "in_animation": "轻微放大",
    "in_animation_duration": 100000,
    "position_x": 0.0,
    "position_y": 0.0,
    "scale_x": 1.0,
    "scale_y": 1.0,
    "rotation": 0.0,
    "opacity": 1.0,
    "filter_type": "暖冬",
    "filter_intensity": 0.8
  }
]
```

#### 格式2：数组字符串（推荐用于动态配置）
数组中每个元素是 JSON 字符串。通常与 `make_image_info` 工具配合使用：
```json
[
  "{\"image_url\":\"https://s.coze.cn/t/W9CvmtJHJWI/\",\"start\":0,\"end\":3936000,\"width\":1440,\"height\":1080}",
  "{\"image_url\":\"https://example.com/image2.jpg\",\"start\":3936000,\"end\":7872000,\"in_animation\":\"轻微放大\"}"
]
```

#### 格式3：JSON字符串
整个数组作为一个 JSON 字符串：
```json
"[{\"image_url\":\"https://s.coze.cn/t/W9CvmtJHJWI/\",\"start\":0,\"end\":3936000,\"width\":1440,\"height\":1080}]"
```

#### 格式4：其他可迭代类型
工具还支持元组(tuple)等其他可迭代类型，会自动转换为列表处理。

#### 必需字段
- `image_url`: 图片的URL链接
- `start`: 开始时间（毫秒）
- `end`: 结束时间（毫秒）

#### 可选字段
- `width`, `height`: 图片尺寸（**元数据字段**，不影响实际显示，可省略）
- `position_x`, `position_y`: 位置坐标（浮点数）
- `scale_x`, `scale_y`: 缩放比例（默认1.0，**控制实际显示大小**）
- `rotation`: 旋转角度（默认0.0）
- `opacity`: 透明度（0.0-1.0，默认1.0）
- `in_animation`: 入场动画类型（如"轻微放大"）
- `in_animation_duration`: 入场动画时长（毫秒，默认500）
- `outro_animation`: 出场动画类型
- `outro_animation_duration`: 出场动画时长（毫秒，默认500）
- `filter_type`: 滤镜类型
- `filter_intensity`: 滤镜强度（0.0-1.0，默认1.0）
- `crop_enabled`: 是否启用裁剪（默认false）
- `crop_left`, `crop_top`, `crop_right`, `crop_bottom`: 裁剪区域（0.0-1.0）
- `background_blur`: 背景模糊（默认false）
- `background_color`: 背景颜色
- `fit_mode`: 适配模式（"fit", "fill", "stretch"，默认"fit"，**控制适配方式**）

**关于尺寸参数**: `width` 和 `height` 是可选的元数据字段，用于记录图片原始尺寸信息。它们不会影响图片的实际显示效果。实际显示由 `scale_x/scale_y`（缩放）和 `fit_mode`（适配模式）控制。

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
    "end": 3936000
  }
]
```

## 使用示例

### 基本用法

#### 方法1：使用数组格式（推荐用于静态配置）

```python
from tools.add_images.handler import handler, Input
from runtime import Args

# 创建输入参数（数组格式）
input_data = Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    image_infos=[{
        "image_url": "https://s.coze.cn/t/W9CvmtJHJWI/",
        "start": 0,
        "end": 3936000,
        "width": 1440,
        "height": 1080
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

配合 `make_image_info` 工具使用：

```python
from tools.make_image_info.handler import handler as make_image_info_handler
from tools.add_images.handler import handler as add_images_handler

# 步骤1: 使用 make_image_info 生成图片信息字符串
image1_result = make_image_info_handler(MockArgs(Input(
    image_url="https://s.coze.cn/t/W9CvmtJHJWI/",
    start=0,
    end=3936000,
    width=1440,
    height=1080
)))

image2_result = make_image_info_handler(MockArgs(Input(
    image_url="https://example.com/image2.jpg",
    start=3936000,
    end=7872000,
    in_animation="轻微放大"
)))

# 步骤2: 将字符串收集到数组中
image_infos_array = [
    image1_result.image_info_string,
    image2_result.image_info_string
]

# 步骤3: 传递数组字符串给 add_images
result = add_images_handler(MockArgs(Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    image_infos=image_infos_array  # 数组字符串格式
)))

print(f"成功添加 {len(result.segment_ids)} 张图片")
```

#### 方法3：使用JSON字符串格式

```python
# 创建输入参数（JSON字符串格式）
input_data = Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    image_infos='[{"image_url":"https://s.coze.cn/t/W9CvmtJHJWI/","start":0,"end":3936000,"width":1440,"height":1080}]'
)
```

### 复杂参数示例

#### 数组格式：
```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "image_infos": [
        {
            "image_url": "https://s.coze.cn/t/W9CvmtJHJWI/",
            "start": 0,
            "end": 3936000,
            "width": 1440,
            "height": 1080,
            "in_animation": "轻微放大",
            "in_animation_duration": 100000,
            "position_x": 0.1,
            "position_y": 0.1,
            "scale_x": 1.2,
            "scale_y": 1.2,
            "filter_type": "暖冬",
            "filter_intensity": 0.8
        }
    ]
}
```

#### JSON字符串格式：
```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "image_infos": "[{\"image_url\":\"https://s.coze.cn/t/W9CvmtJHJWI/\",\"start\":0,\"end\":3936000,\"width\":1440,\"height\":1080,\"in_animation\":\"轻微放大\",\"in_animation_duration\":100000,\"position_x\":0.1,\"position_y\":0.1,\"scale_x\":1.2,\"scale_y\":1.2,\"filter_type\":\"暖冬\",\"filter_intensity\":0.8}]"
}
```

## 注意事项

### 时间单位
- 所有时间参数使用毫秒(ms)为单位
- `start` 和 `end` 定义图片在时间轴上的显示区间
- 动画时长也使用毫秒为单位

### 坐标系统
- 位置坐标使用浮点数，可以为负值或超过1.0
- (0,0) 通常表示屏幕中心或左上角（取决于剪映的坐标系）
- 缩放比例1.0表示原始大小

### 轨道管理
- 每次调用都会创建一个新的图片轨道
- 同一轨道内的图片按时间顺序排列
- 不同轨道的图片可以重叠显示

### 错误处理
- 如果draft_id不存在，返回失败状态
- 如果image_infos格式无效，返回详细错误信息
- 如果图片URL无法访问，仍会创建片段（由草稿生成器处理）

### 性能考虑
- 大量图片可能影响处理性能
- 建议单次调用图片数量控制在50张以内
- 过长的动画时长可能影响播放流畅度

## 与其他工具的集成

### 与 create_draft 配合使用
1. 使用 `create_draft` 创建基础草稿
2. 使用 `add_images` 添加图片轨道
3. 使用 `export_drafts` 导出完整配置

### 与 get_media_duration 配合使用
1. 使用 `get_media_duration` 获取图片时长信息
2. 根据时长信息设置图片的 `start` 和 `end` 参数
3. 使用 `add_images` 添加到草稿