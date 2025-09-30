# Make Image Info Tool

## 功能描述

生成单个图片配置的 JSON 字符串表示。这是 `add_images` 工具的辅助函数，用于创建可以被组合成数组的图片信息字符串。

### 使用场景

当你需要在 Coze 工作流中动态构建多个图片配置时，可以：
1. 多次调用 `make_image_info` 生成每个图片的配置字符串
2. 将这些字符串收集到一个数组中
3. 将该数组作为 `image_infos` 参数传递给 `add_images` 工具

## 输入参数

### Input 类型定义

```python
class Input(NamedTuple):
    # 必需字段
    image_url: str                              # 图片URL
    start: int                                  # 开始时间（毫秒）
    end: int                                    # 结束时间（毫秒）
    
    # 可选：尺寸字段
    width: Optional[int] = None                 # 图片宽度
    height: Optional[int] = None                # 图片高度
    
    # 可选：变换字段
    position_x: Optional[float] = 0.0           # X位置（默认0.0）
    position_y: Optional[float] = 0.0           # Y位置（默认0.0）
    scale_x: Optional[float] = 1.0              # X缩放（默认1.0）
    scale_y: Optional[float] = 1.0              # Y缩放（默认1.0）
    rotation: Optional[float] = 0.0             # 旋转角度（默认0.0）
    opacity: Optional[float] = 1.0              # 透明度（0.0-1.0，默认1.0）
    
    # 可选：裁剪字段
    crop_enabled: Optional[bool] = False        # 启用裁剪（默认False）
    crop_left: Optional[float] = 0.0            # 裁剪左边（0.0-1.0）
    crop_top: Optional[float] = 0.0             # 裁剪顶部（0.0-1.0）
    crop_right: Optional[float] = 1.0           # 裁剪右边（0.0-1.0）
    crop_bottom: Optional[float] = 1.0          # 裁剪底部（0.0-1.0）
    
    # 可选：效果字段
    filter_type: Optional[str] = None           # 滤镜类型（如"暖冬"）
    filter_intensity: Optional[float] = 1.0     # 滤镜强度（0.0-1.0）
    transition_type: Optional[str] = None       # 转场类型
    transition_duration: Optional[int] = 500    # 转场时长（毫秒）
    
    # 可选：背景字段
    background_blur: Optional[bool] = False     # 背景模糊（默认False）
    background_color: Optional[str] = None      # 背景颜色
    fit_mode: Optional[str] = "fit"             # 适配模式："fit"、"fill"、"stretch"
    
    # 可选：动画字段
    in_animation: Optional[str] = None          # 入场动画类型（如"轻微放大"）
    in_animation_duration: Optional[int] = 500  # 入场动画时长（毫秒）
    outro_animation: Optional[str] = None       # 出场动画类型
    outro_animation_duration: Optional[int] = 500  # 出场动画时长（毫秒）
```

### 参数说明

#### 必需参数
- `image_url`: 图片的 URL 地址
- `start`: 图片在时间轴上的开始时间（毫秒）
- `end`: 图片在时间轴上的结束时间（毫秒）

#### 可选参数
所有其他参数都是可选的，只有在设置了非默认值时才会包含在输出字符串中。这样可以保持输出紧凑。

## 输出结果

### Output 类型定义

```python
class Output(NamedTuple):
    image_info_string: str                      # 图片信息的 JSON 字符串
    success: bool                               # 操作是否成功
    message: str                                # 状态消息
```

### 输出格式

输出是一个紧凑的 JSON 字符串，例如：

```json
"{\"image_url\":\"https://example.com/image.jpg\",\"start\":0,\"end\":3000,\"width\":1920,\"height\":1080}"
```

## 使用示例

### 示例 1: 基本用法

```python
from tools.make_image_info.handler import handler, Input
from runtime import Args

# 创建输入参数（仅必需字段）
input_data = Input(
    image_url="https://s.coze.cn/t/W9CvmtJHJWI/",
    start=0,
    end=3936000
)

# 模拟Args对象
class MockArgs:
    def __init__(self, input_data):
        self.input = input_data

# 调用处理函数
result = handler(MockArgs(input_data))

print(f"成功: {result.success}")
print(f"生成的字符串: {result.image_info_string}")
# 输出: {"image_url":"https://s.coze.cn/t/W9CvmtJHJWI/","start":0,"end":3936000}
```

### 示例 2: 带完整参数

```python
# 创建输入参数（包含可选字段）
input_data = Input(
    image_url="https://s.coze.cn/t/W9CvmtJHJWI/",
    start=0,
    end=3936000,
    width=1440,
    height=1080,
    in_animation="轻微放大",
    in_animation_duration=100000,
    position_x=0.1,
    position_y=0.1,
    scale_x=1.2,
    scale_y=1.2,
    filter_type="暖冬",
    filter_intensity=0.8
)

result = handler(MockArgs(input_data))
print(result.image_info_string)
# 输出: {"image_url":"https://s.coze.cn/t/W9CvmtJHJWI/","start":0,"end":3936000,"width":1440,"height":1080,"position_x":0.1,"position_y":0.1,"scale_x":1.2,"scale_y":1.2,"in_animation":"轻微放大","in_animation_duration":100000,"filter_type":"暖冬","filter_intensity":0.8}
```

### 示例 3: 与 add_images 配合使用（完整工作流）

这是本工具的主要使用场景：

```python
# 步骤 1: 使用 make_image_info 生成多个图片信息字符串
image1_info = make_image_info(
    image_url="https://example.com/image1.jpg",
    start=0,
    end=3000,
    width=1920,
    height=1080
)
# 返回: {"image_url":"https://example.com/image1.jpg","start":0,"end":3000,"width":1920,"height":1080}

image2_info = make_image_info(
    image_url="https://example.com/image2.jpg",
    start=3000,
    end=6000,
    in_animation="轻微放大",
    filter_type="暖冬"
)
# 返回: {"image_url":"https://example.com/image2.jpg","start":3000,"end":6000,"in_animation":"轻微放大","filter_type":"暖冬"}

# 步骤 2: 将字符串收集到数组中
image_infos_array = [
    image1_info.image_info_string,
    image2_info.image_info_string
]

# 步骤 3: 将数组字符串传递给 add_images
add_images(
    draft_id="your-draft-uuid",
    image_infos=image_infos_array  # 数组字符串格式！
)
```

### 示例 4: 在 Coze 工作流中使用

在 Coze 工作流中，你可以这样组合使用：

```
1. [make_image_info 节点1] → 生成第一张图片配置字符串
   输入: image_url="https://...", start=0, end=3000
   输出: image_info_string

2. [make_image_info 节点2] → 生成第二张图片配置字符串
   输入: image_url="https://...", start=3000, end=6000
   输出: image_info_string

3. [数组节点] → 将多个字符串组合成数组
   输入: [节点1.image_info_string, 节点2.image_info_string]
   输出: image_infos_array

4. [add_images 节点] → 添加图片到草稿
   输入: draft_id="...", image_infos=image_infos_array
   输出: segment_ids, segment_infos
```

## 注意事项

### 输出优化
- 工具只会在输出中包含非默认值的参数
- 这使得输出字符串保持紧凑，减少数据传输
- 例如：如果 `scale_x=1.0`（默认值），则不会包含在输出中

### 时间参数验证
- `start` 必须 >= 0
- `end` 必须 > `start`
- 时间单位为毫秒

### 与 add_images 的兼容性
- 输出的字符串格式完全兼容 `add_images` 的 `image_infos` 参数
- 可以使用数组字符串格式（新增）、数组对象格式或 JSON 字符串格式

### 参数命名约定
- 动画参数使用 `in_animation` 而不是 `intro_animation`
- 这与 `add_images` 工具的输入参数命名保持一致

## 错误处理

工具会验证以下情况：

1. **缺少必需参数**: 如果缺少 `image_url`、`start` 或 `end`，返回错误
2. **无效时间范围**: 如果 `start < 0` 或 `end <= start`，返回错误
3. **其他异常**: 任何意外错误都会被捕获并返回错误消息

## 与其他工具的关系

### make_image_info → add_images
这是主要的使用流程：
1. `make_image_info` 生成单个图片的配置字符串
2. 多个字符串组合成数组
3. `add_images` 接收数组并添加图片到草稿

### 替代方案
如果你的图片配置是静态的，也可以：
- 直接使用数组对象格式传递给 `add_images`
- 使用 JSON 字符串格式传递给 `add_images`

`make_image_info` 主要用于需要动态构建配置的场景。
