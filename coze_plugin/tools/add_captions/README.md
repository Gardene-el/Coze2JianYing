# Add Captions Tool

## 功能描述

向现有草稿添加文本/字幕轨道和字幕片段。每次调用会创建一个新的文本轨道，包含指定的所有字幕。支持字幕的完整文本样式、位置、动画等参数设置。

## 输入参数

### Input 类型定义

```python
class Input(NamedTuple):
    draft_id: str                              # 现有草稿的UUID
    caption_infos: Any                         # 字幕信息：支持多种格式输入
```

### caption_infos 输入格式

支持多种输入格式，自动识别和处理：

#### 格式1：数组对象（推荐用于静态配置）
```json
[
  {
    "content": "这是第一句字幕",
    "start": 0,
    "end": 3000,
    "font_size": 48,
    "color": "#FFFFFF",
    "position_x": 0.5,
    "position_y": -0.9
  },
  {
    "content": "这是第二句字幕",
    "start": 3000,
    "end": 6000,
    "font_size": 56,
    "color": "#FFD700",
    "stroke_enabled": true
  }
]
```

#### 格式2：数组字符串（推荐用于动态配置）
数组中每个元素是 JSON 字符串。通常与 `make_caption_info` 工具配合使用：
```json
[
  "{\"content\":\"第一句字幕\",\"start\":0,\"end\":3000}",
  "{\"content\":\"第二句字幕\",\"start\":3000,\"end\":6000,\"font_size\":56}"
]
```

#### 格式3：JSON字符串
整个数组作为一个 JSON 字符串：
```json
"[{\"content\":\"第一句字幕\",\"start\":0,\"end\":3000}]"
```

#### 格式4：其他可迭代类型
工具还支持元组(tuple)等其他可迭代类型，会自动转换为列表处理。

#### 必需字段
- `content`: 字幕的文本内容
- `start`: 开始时间（毫秒）
- `end`: 结束时间（毫秒）

#### 可选字段

**位置和变换 (5个)**:
- `position_x`, `position_y`: 位置坐标（-2.0到2.0，默认0.5, -0.9；0为中心，负值向下/左）
- `scale`: 缩放比例（默认1.0）
- `rotation`: 旋转角度（默认0.0）
- `opacity`: 透明度（0.0-1.0，默认1.0）

**文本样式 (5个)**:
- `font_family`: 字体名称（默认"默认"）
- `font_size`: 字号大小（默认48）
- `font_weight`: 字重（"normal"或"bold"，默认"normal"）
- `font_style`: 字形（"normal"或"italic"，默认"normal"）
- `color`: 文字颜色（十六进制，默认"#FFFFFF"）

**描边效果 (3个)**:
- `stroke_enabled`: 是否启用描边（默认false）
- `stroke_color`: 描边颜色（默认"#000000"）
- `stroke_width`: 描边宽度（默认2）

**阴影效果 (5个)**:
- `shadow_enabled`: 是否启用阴影（默认false）
- `shadow_color`: 阴影颜色（默认"#000000"）
- `shadow_offset_x`, `shadow_offset_y`: 阴影偏移（默认2, 2）
- `shadow_blur`: 阴影模糊（默认4）

**背景效果 (3个)**:
- `background_enabled`: 是否启用背景（默认false）
- `background_color`: 背景颜色（默认"#000000"）
- `background_opacity`: 背景透明度（0.0-1.0，默认0.5）

**对齐方式 (1个)**:
- `alignment`: 文本对齐（"left", "center", "right"，默认"center"）

**动画效果 (3个)**:
- `intro_animation`: 入场动画类型（如"淡入"）
- `outro_animation`: 出场动画类型（如"淡出"）
- `loop_animation`: 循环动画类型

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
    "end": 3000
  },
  {
    "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
    "start": 3000,
    "end": 6000
  }
]
```

## 使用示例

### 基本用法

#### 方法1：使用数组格式（推荐用于静态配置）

```python
from tools.add_captions.handler import handler, Input
from runtime import Args

# 创建输入参数（数组格式）
input_data = Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    caption_infos=[
        {
            "content": "欢迎观看本视频",
            "start": 0,
            "end": 3000
        },
        {
            "content": "精彩内容马上开始",
            "start": 3000,
            "end": 6000,
            "font_size": 56,
            "color": "#FFD700"
        }
    ]
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

配合 `make_caption_info` 工具使用：

```python
from tools.make_caption_info.handler import handler as make_caption_info_handler
from tools.add_captions.handler import handler as add_captions_handler

# 步骤1: 使用 make_caption_info 生成字幕信息字符串
caption1_result = make_caption_info_handler(MockArgs(Input(
    content="欢迎观看本视频",
    start=0,
    end=3000
)))

caption2_result = make_caption_info_handler(MockArgs(Input(
    content="精彩内容马上开始",
    start=3000,
    end=6000,
    font_size=56,
    color="#FFD700"
)))

# 步骤2: 将字符串收集到数组中
caption_infos_array = [
    caption1_result.caption_info_string,
    caption2_result.caption_info_string
]

# 步骤3: 传递数组字符串给 add_captions
result = add_captions_handler(MockArgs(Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    caption_infos=caption_infos_array  # 数组字符串格式
)))

print(f"成功添加 {len(result.segment_ids)} 条字幕")
```

#### 方法3：使用JSON字符串格式

```python
# 创建输入参数（JSON字符串格式）
input_data = Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    caption_infos='[{"content":"欢迎观看","start":0,"end":3000}]'
)
```

### 复杂参数示例

#### 示例1: 带完整文本样式的字幕

数组格式：
```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "caption_infos": [
        {
            "content": "醒目标题",
            "start": 0,
            "end": 5000,
            "position_y": 0.3,
            "font_family": "思源黑体",
            "font_size": 72,
            "font_weight": "bold",
            "color": "#FFD700",
            "stroke_enabled": true,
            "stroke_color": "#000000",
            "stroke_width": 4
        }
    ]
}
```

#### 示例2: 带阴影和背景的字幕

```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "caption_infos": [
        {
            "content": "重要提示",
            "start": 3000,
            "end": 8000,
            "shadow_enabled": true,
            "shadow_color": "#000000",
            "shadow_offset_x": 4,
            "shadow_offset_y": 4,
            "shadow_blur": 8,
            "background_enabled": true,
            "background_color": "#FF0000",
            "background_opacity": 0.7
        }
    ]
}
```

#### 示例3: 带动画效果的字幕

```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "caption_infos": [
        {
            "content": "动态字幕",
            "start": 0,
            "end": 5000,
            "intro_animation": "淡入",
            "outro_animation": "淡出",
            "font_size": 60,
            "color": "#FFFFFF"
        }
    ]
}
```

### 完整工作流示例

```python
from tools.create_draft.handler import handler as create_draft_handler
from tools.make_caption_info.handler import handler as make_caption_info_handler
from tools.add_captions.handler import handler as add_captions_handler
from tools.export_drafts.handler import handler as export_handler

# 步骤1: 创建草稿
draft_result = create_draft_handler(MockArgs(Input(
    draft_name="字幕测试项目",
    width=1920,
    height=1080,
    fps=30
)))
draft_id = draft_result.draft_id
print(f"创建草稿: {draft_id}")

# 步骤2: 生成字幕配置
caption1 = make_caption_info_handler(MockArgs(Input(
    content="欢迎观看本视频",
    start=0,
    end=3000
)))

caption2 = make_caption_info_handler(MockArgs(Input(
    content="精彩内容马上开始",
    start=3000,
    end=6000,
    font_size=60,
    color="#FFD700"
)))

caption3 = make_caption_info_handler(MockArgs(Input(
    content="感谢观看",
    start=6000,
    end=9000,
    intro_animation="淡入",
    outro_animation="淡出"
)))

# 步骤3: 添加字幕到草稿
captions_result = add_captions_handler(MockArgs(Input(
    draft_id=draft_id,
    caption_infos=[
        caption1.caption_info_string,
        caption2.caption_info_string,
        caption3.caption_info_string
    ]
)))
print(f"添加了 {len(captions_result.segment_ids)} 条字幕")

# 步骤4: 导出草稿配置
export_result = export_handler(MockArgs(Input(
    draft_ids=draft_id
)))
print("草稿导出完成")
```

## 注意事项

### 时间单位
- 所有时间参数使用毫秒(ms)为单位
- `start` 和 `end` 定义字幕在时间轴上的显示区间
- 建议字幕时长不少于1秒（1000ms）以确保可读性

### 坐标系统
- 位置坐标使用归一化值（0.0-1.0）
- `position_x`: 0.0=左边缘, 0.5=水平居中, 1.0=右边缘
- `position_y`: 0.0=顶部, 0.5=垂直居中, 1.0=底部
- 默认位置 (0.5, 0.9) 表示水平居中、靠近底部

### 文本样式
- 描边、阴影、背景是独立功能，可以任意组合
- 启用描边/阴影/背景时，相关的颜色和参数才会生效
- 字体名称需要与剪映支持的字体匹配
- 颜色使用十六进制格式（如 "#FFFFFF", "#FFD700"）

### 轨道管理
- 每次调用都会创建一个新的文本轨道
- 同一轨道内的字幕按时间顺序排列
- 不同轨道的字幕可以重叠显示
- 如需多层字幕效果，可以多次调用 `add_captions`

### 错误处理
- 如果draft_id不存在，返回失败状态
- 如果caption_infos格式无效，返回详细错误信息
- 缺少必需字段（content, start, end）会导致验证失败
- 时间范围验证：end 必须 > start，start 必须 >= 0

### 性能考虑
- 大量字幕可能影响处理性能
- 建议单次调用字幕数量控制在100条以内
- 过于复杂的样式组合可能影响播放流畅度
- 动画效果会增加渲染负担

### 字幕可读性建议
- 字号建议：48-72（标准字幕使用48，标题使用72）
- 对比度：确保文字颜色与背景有足够对比度
- 描边：在复杂背景上建议启用描边增强可读性
- 时长：每条字幕建议显示2-5秒
- 位置：底部字幕使用 position_y=-0.9（默认），标题使用 0.3-0.5

## 与其他工具的集成

### 与 create_draft 配合使用
1. 使用 `create_draft` 创建基础草稿
2. 使用 `add_captions` 添加字幕轨道
3. 使用 `add_videos`/`add_images` 添加视觉内容
4. 使用 `export_drafts` 导出完整配置

### 与 make_caption_info 配合使用
1. 使用 `make_caption_info` 动态生成字幕配置字符串
2. 收集多个字符串到数组
3. 使用 `add_captions` 添加到草稿

### 与 get_media_duration 配合使用
1. 使用 `get_media_duration` 获取视频/音频时长
2. 根据时长信息规划字幕的时间轴
3. 使用 `add_captions` 添加对应时间点的字幕

## 常见使用场景

### 场景1: 简单视频字幕
适合普通视频的字幕添加：
```python
caption_infos=[
    {"content": "第一句话", "start": 0, "end": 3000},
    {"content": "第二句话", "start": 3000, "end": 6000}
]
```

### 场景2: 标题字幕
适合视频开头的标题展示：
```python
caption_infos=[{
    "content": "视频标题",
    "start": 0,
    "end": 3000,
    "position_y": 0.3,
    "font_size": 72,
    "font_weight": "bold",
    "intro_animation": "淡入",
    "outro_animation": "淡出"
}]
```

### 场景3: 多语言字幕
可以创建多个轨道显示不同语言：
```python
# 第一次调用：添加中文字幕
add_captions(draft_id, chinese_captions)

# 第二次调用：添加英文字幕（不同position_y避免重叠）
add_captions(draft_id, english_captions_with_different_position)
```

### 场景4: 强调字幕
适合需要突出显示的重要信息：
```python
caption_infos=[{
    "content": "重要提示",
    "start": 5000,
    "end": 8000,
    "font_size": 60,
    "color": "#FF0000",
    "stroke_enabled": true,
    "stroke_width": 4,
    "background_enabled": true,
    "background_opacity": 0.8
}]
```

## 技术细节

### 参数映射
本工具的参数完全映射到 pyJianYingDraft 的 `TextSegment` 和 `TextStyle` 类：
- content, time_range → 基本内容和时间
- position_x, position_y, scale, rotation, opacity → 变换属性
- font_family, font_size, font_weight, font_style, color → 文本样式
- stroke_* → 描边效果
- shadow_* → 阴影效果
- background_* → 背景效果
- alignment → 对齐方式
- *_animation → 动画效果

### 数据结构
工具内部创建的文本片段结构：
```json
{
  "id": "uuid",
  "type": "text",
  "content": "字幕内容",
  "time_range": {"start": 0, "end": 3000},
  "transform": {
    "position_x": 0.5,
    "position_y": -0.9,
    "scale": 1.0,
    "rotation": 0.0,
    "opacity": 1.0
  },
  "style": {
    "font_family": "默认",
    "font_size": 48,
    "color": "#FFFFFF",
    "stroke": {"enabled": false, "color": "#000000", "width": 2},
    "shadow": {"enabled": false, ...},
    "background": {"enabled": false, ...}
  },
  "alignment": "center",
  "animations": {
    "intro": null,
    "outro": null,
    "loop": null
  }
}
```

### 向后兼容性
- 所有原有的输入格式继续正常工作
- 数组对象格式（推荐用于静态配置）
- JSON 字符串格式
- 新增的数组字符串格式不影响现有功能
- 未来添加新参数不会破坏现有功能

## 与图片/音频工具的对比

### 相同点
- 支持相同的三种输入格式（数组对象、数组字符串、JSON字符串）
- 都有对应的 `make_*_info` 辅助工具
- 都使用 UUID 管理草稿
- 都支持轨道和片段的完整配置

### 不同点
- **图片**: 25个参数，包含视觉变换、裁剪、滤镜、背景模糊等
- **音频**: 10个参数，专注于音量、淡入淡出、速度、音效
- **字幕**: 32个参数，包含完整的文本样式、描边、阴影、背景、对齐和动画

字幕工具参数最多，因为需要支持复杂的文本渲染效果。
