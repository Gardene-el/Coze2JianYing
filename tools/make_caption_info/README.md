# Make Caption Info Tool

## 功能描述

生成单个字幕/文本配置的 JSON 字符串表示。这是 `add_captions` 工具的辅助函数，用于创建可以被组合成数组的字幕信息字符串。

### 使用场景

当你需要在 Coze 工作流中动态构建多个字幕配置时，可以：
1. 多次调用 `make_caption_info` 生成每个字幕的配置字符串
2. 将这些字符串收集到一个数组中
3. 将该数组作为 `caption_infos` 参数传递给 `add_captions` 工具

### 参数数量说明

总共 32 个参数：
- **4 个必需参数**: content, start, end（基本内容和时间范围）
- **28 个可选参数**: 包含位置变换、文本样式、描边、阴影、背景、对齐和动画等所有配置

这个工具覆盖了 pyJianYingDraft 中 TextSegment 和 TextStyle 支持的所有参数。

## 输入参数

### Input 类型定义

```python
class Input(NamedTuple):
    """Input parameters for make_caption_info tool"""
    # Required fields (4个必需参数)
    content: str                                # 文本内容/字幕内容
    start: int                                  # 开始时间（毫秒）
    end: int                                    # 结束时间（毫秒）
    
    # Optional position and transform fields (5个位置变换参数)
    position_x: Optional[float] = 0.5           # X位置 (0.0-1.0, 默认0.5居中)
    position_y: Optional[float] = 0.9           # Y位置 (0.0-1.0, 默认0.9底部)
    scale: Optional[float] = 1.0                # 缩放 (默认1.0)
    rotation: Optional[float] = 0.0             # 旋转角度 (默认0.0)
    opacity: Optional[float] = 1.0              # 透明度 (0.0-1.0, 默认1.0)
    
    # Optional text style fields (5个文本样式参数)
    font_family: Optional[str] = "默认"         # 字体 (默认"默认")
    font_size: Optional[int] = 48               # 字号 (默认48)
    font_weight: Optional[str] = "normal"       # 字重: "normal", "bold"
    font_style: Optional[str] = "normal"        # 字形: "normal", "italic"
    color: Optional[str] = "#FFFFFF"            # 文本颜色 (默认"#FFFFFF"白色)
    
    # Optional text stroke/outline fields (3个描边参数)
    stroke_enabled: Optional[bool] = False      # 启用描边 (默认False)
    stroke_color: Optional[str] = "#000000"     # 描边颜色 (默认"#000000"黑色)
    stroke_width: Optional[int] = 2             # 描边宽度 (默认2)
    
    # Optional text shadow fields (5个阴影参数)
    shadow_enabled: Optional[bool] = False      # 启用阴影 (默认False)
    shadow_color: Optional[str] = "#000000"     # 阴影颜色 (默认"#000000"黑色)
    shadow_offset_x: Optional[int] = 2          # 阴影X偏移 (默认2)
    shadow_offset_y: Optional[int] = 2          # 阴影Y偏移 (默认2)
    shadow_blur: Optional[int] = 4              # 阴影模糊 (默认4)
    
    # Optional text background fields (3个背景参数)
    background_enabled: Optional[bool] = False  # 启用背景 (默认False)
    background_color: Optional[str] = "#000000" # 背景颜色 (默认"#000000"黑色)
    background_opacity: Optional[float] = 0.5   # 背景透明度 (0.0-1.0, 默认0.5)
    
    # Optional alignment field (1个对齐参数)
    alignment: Optional[str] = "center"         # 文本对齐: "left", "center", "right"
    
    # Optional animation fields (3个动画参数)
    intro_animation: Optional[str] = None       # 入场动画类型 (如"淡入")
    outro_animation: Optional[str] = None       # 出场动画类型 (如"淡出")
    loop_animation: Optional[str] = None        # 循环动画类型
```

### 参数分类和作用

#### 必需参数 (4个)
这些参数必须提供：
- `content`: 字幕的文本内容
- `start`: 字幕显示的开始时间（毫秒）
- `end`: 字幕显示的结束时间（毫秒）

#### 位置和变换 (5个)
控制字幕在画面中的位置和显示效果：
- `position_x`, `position_y`: 归一化坐标 (0.0-1.0)，0.5表示居中
- `scale`: 整体缩放比例
- `rotation`: 旋转角度（度数）
- `opacity`: 透明度，1.0为完全不透明

#### 文本样式 (5个)
控制文字的基本外观：
- `font_family`: 字体名称
- `font_size`: 字号大小（像素）
- `font_weight`: 字重（粗细）
- `font_style`: 字形（斜体等）
- `color`: 文字颜色（十六进制）

#### 描边效果 (3个)
为文字添加轮廓：
- `stroke_enabled`: 是否启用描边
- `stroke_color`: 描边颜色
- `stroke_width`: 描边宽度

#### 阴影效果 (5个)
为文字添加阴影：
- `shadow_enabled`: 是否启用阴影
- `shadow_color`: 阴影颜色
- `shadow_offset_x`, `shadow_offset_y`: 阴影偏移
- `shadow_blur`: 阴影模糊程度

#### 背景效果 (3个)
为文字添加背景色块：
- `background_enabled`: 是否启用背景
- `background_color`: 背景颜色
- `background_opacity`: 背景透明度

#### 对齐方式 (1个)
- `alignment`: 文字对齐方式（左对齐、居中、右对齐）

#### 动画效果 (3个)
为字幕添加动画：
- `intro_animation`: 入场动画
- `outro_animation`: 出场动画
- `loop_animation`: 循环播放的动画

## 输出结果

### Output 类型定义

```python
class Output(NamedTuple):
    caption_info_string: str                    # 字幕信息的JSON字符串
    success: bool = True                        # 操作成功状态
    message: str = "字幕信息字符串生成成功"       # 状态消息
```

### 输出特点

1. **紧凑格式**: 输出的 JSON 字符串不包含额外的空格和换行
2. **仅包含非默认值**: 只输出那些被明确设置且不等于默认值的参数
3. **UTF-8编码**: 正确处理中文字符

### 输出示例

#### 最小配置输出
```json
{"content":"这是一段字幕","start":0,"end":3000}
```

#### 完整配置输出
```json
{"content":"自定义样式字幕","start":0,"end":5000,"position_y":0.5,"font_family":"思源黑体","font_size":60,"color":"#FFD700","stroke_enabled":true,"stroke_color":"#000000","stroke_width":3}
```

## 使用示例

### 示例 1: 基本用法（最小参数）

```python
from tools.make_caption_info.handler import handler, Input
from runtime import Args

# 创建最简单的字幕配置
input_data = Input(
    content="这是一段字幕",
    start=0,
    end=3000
)

result = handler(Args(input_data))
print(result.caption_info_string)
# 输出: {"content":"这是一段字幕","start":0,"end":3000}
```

### 示例 2: 带自定义位置

```python
# 创建顶部居中的字幕
input_data = Input(
    content="标题字幕",
    start=0,
    end=5000,
    position_x=0.5,  # 水平居中
    position_y=0.1   # 顶部位置
)

result = handler(Args(input_data))
print(result.caption_info_string)
# 输出: {"content":"标题字幕","start":0,"end":5000,"position_y":0.1}
# 注意: position_x=0.5 是默认值，不会出现在输出中
```

### 示例 3: 带完整文本样式

```python
# 创建自定义样式的字幕
input_data = Input(
    content="自定义样式字幕",
    start=0,
    end=5000,
    font_family="思源黑体",
    font_size=60,
    font_weight="bold",
    color="#FFD700",          # 金色
    stroke_enabled=True,       # 启用描边
    stroke_color="#000000",    # 黑色描边
    stroke_width=3
)

result = handler(Args(input_data))
print(result.caption_info_string)
# 输出包含所有非默认样式参数
```

### 示例 4: 带阴影和背景

```python
# 创建带阴影和背景的字幕
input_data = Input(
    content="醒目字幕",
    start=1000,
    end=4000,
    shadow_enabled=True,
    shadow_color="#000000",
    shadow_offset_x=4,
    shadow_offset_y=4,
    shadow_blur=8,
    background_enabled=True,
    background_color="#000000",
    background_opacity=0.7
)

result = handler(Args(input_data))
# 输出包含阴影和背景配置
```

### 示例 5: 带动画效果

```python
# 创建带入场和出场动画的字幕
input_data = Input(
    content="动画字幕",
    start=2000,
    end=6000,
    intro_animation="淡入",
    outro_animation="淡出"
)

result = handler(Args(input_data))
print(result.caption_info_string)
# 输出: {"content":"动画字幕","start":2000,"end":6000,"intro_animation":"淡入","outro_animation":"淡出"}
```

### 示例 6: 与 add_captions 配合使用（完整工作流）

```python
from tools.make_caption_info.handler import handler as make_caption_info_handler
from tools.add_captions.handler import handler as add_captions_handler

# 步骤 1: 生成多个字幕配置字符串
caption1 = make_caption_info_handler(Args(Input(
    content="第一句字幕",
    start=0,
    end=3000
)))

caption2 = make_caption_info_handler(Args(Input(
    content="第二句字幕",
    start=3000,
    end=6000,
    font_size=56,
    color="#FFD700"
)))

caption3 = make_caption_info_handler(Args(Input(
    content="第三句字幕",
    start=6000,
    end=9000,
    position_y=0.5  # 屏幕中央
)))

# 步骤 2: 收集字符串到数组
caption_infos_array = [
    caption1.caption_info_string,
    caption2.caption_info_string,
    caption3.caption_info_string
]

# 步骤 3: 传递给 add_captions
result = add_captions_handler(Args(Input(
    draft_id="your-draft-uuid",
    caption_infos=caption_infos_array
)))

print(f"成功添加 {len(result.segment_ids)} 条字幕")
```

### 示例 7: 在 Coze 工作流中使用

在 Coze 工作流中，你可以这样组合使用：

```
1. [make_caption_info 节点1] → 生成第一条字幕配置字符串
   输入: content="欢迎观看", start=0, end=3000
   输出: caption_info_string

2. [make_caption_info 节点2] → 生成第二条字幕配置字符串
   输入: content="精彩内容开始", start=3000, end=6000, font_size=60
   输出: caption_info_string

3. [make_caption_info 节点3] → 生成第三条字幕配置字符串
   输入: content="敬请期待", start=6000, end=9000
   输出: caption_info_string

4. [数组节点] → 将多个字符串组合成数组
   输入: [节点1.caption_info_string, 节点2.caption_info_string, 节点3.caption_info_string]
   输出: caption_infos_array

5. [add_captions 节点] → 添加字幕到草稿
   输入: draft_id="...", caption_infos=caption_infos_array
   输出: segment_ids, segment_infos
```

## 参数验证规则

### 必需参数验证
- `content`: 不能为空字符串
- `start`: 必须 >= 0
- `end`: 必须 > start

### 数值范围验证
- `position_x`: 0.0 到 1.0
- `position_y`: 0.0 到 1.0
- `opacity`: 0.0 到 1.0
- `background_opacity`: 0.0 到 1.0

### 枚举值验证
- `alignment`: 必须是 "left", "center", "right" 之一
- `font_weight`: 必须是 "normal", "bold" 之一
- `font_style`: 必须是 "normal", "italic" 之一

### 错误消息
所有验证失败都会返回清晰的中文错误消息，例如：
- "缺少必需的 content 参数"
- "end 时间必须大于 start 时间"
- "position_x 必须在 0.0 到 1.0 之间"

## 注意事项

### 默认值优化
- 工具会自动排除默认值，使输出更紧凑
- 例如：如果 `position_x=0.5` (默认值)，则不会出现在输出中
- 这个优化减少了数据传输量，特别适合 Coze 工作流

### 中文支持
- 完全支持中文内容、字体名称和动画名称
- 使用 `ensure_ascii=False` 确保中文字符正确编码
- 例如：`{"content":"这是中文","font_family":"思源黑体","intro_animation":"淡入"}`

### 输出格式
- 输出是紧凑的 JSON 字符串（无额外空格）
- 可以直接收集到数组中传递给 `add_captions`
- 也可以手动解析为对象进行进一步处理

### 与其他参数的配合
- 描边、阴影、背景是独立的功能，可以任意组合
- 位置和对齐方式会相互影响最终显示效果
- 动画效果不影响静态样式的设置

## 与其他工具的关系

### make_caption_info → add_captions
这是主要的使用流程：
1. `make_caption_info` 生成单个字幕的配置字符串
2. 多个字符串组合成数组
3. `add_captions` 接收数组并添加字幕到草稿

### 替代方案
如果你的字幕配置是静态的，也可以：
- 直接使用数组对象格式传递给 `add_captions`
- 使用 JSON 字符串格式传递给 `add_captions`

`make_caption_info` 主要用于需要动态构建配置的场景。

## 常见使用场景

### 场景1: 简单字幕
适合普通的视频字幕，只需要设置内容和时间：
```python
Input(content="字幕内容", start=0, end=3000)
```

### 场景2: 标题字幕
适合视频开头的标题，使用更大的字号和不同位置：
```python
Input(
    content="视频标题",
    start=0,
    end=3000,
    font_size=72,
    position_y=0.3,
    font_weight="bold"
)
```

### 场景3: 醒目提示
适合重要信息提示，使用描边和背景增强可读性：
```python
Input(
    content="重要提示",
    start=5000,
    end=8000,
    stroke_enabled=True,
    stroke_width=3,
    background_enabled=True,
    background_opacity=0.8
)
```

### 场景4: 动态字幕
适合有视觉冲击力的场景，使用动画效果：
```python
Input(
    content="精彩内容",
    start=0,
    end=5000,
    intro_animation="淡入",
    outro_animation="淡出",
    font_size=60,
    color="#FFD700"
)
```

## 技术细节

### 参数映射
本工具的参数完全映射到 pyJianYingDraft 的 `TextSegment` 和 `TextStyle` 类：
- Transform properties → position_x, position_y, scale, rotation, opacity
- Text style → font_family, font_size, font_weight, font_style, color
- Stroke → stroke_enabled, stroke_color, stroke_width
- Shadow → shadow_enabled, shadow_color, shadow_offset_x/y, shadow_blur
- Background → background_enabled, background_color, background_opacity
- Layout → alignment
- Animations → intro_animation, outro_animation, loop_animation

### JSON 序列化
- 使用 `json.dumps()` 的 `ensure_ascii=False` 参数确保中文正确编码
- 使用 `separators=(',', ':')` 生成紧凑格式（无多余空格）
- 所有字符串使用 UTF-8 编码

### 向后兼容性
- 本工具生成的字符串格式与 `add_captions` 完全兼容
- 未来添加新参数不会破坏现有功能
- 默认值策略确保输出保持紧凑
