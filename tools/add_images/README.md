# add_images - 添加图片轨道工具

## 功能描述
将图片内容添加到现有草稿中，通过创建新的视频轨道。图片被处理为具有指定时长的视频片段。每次调用此工具都会创建一个包含所有图片片段的新轨道。

## 输入参数

### Input 类型定义
```python
class Input(NamedTuple):
    draft_id: str                               # 要修改的草稿UUID
    image_urls: List[str]                       # 要添加的图片URL列表
    durations: Optional[List[int]] = None       # 每个图片的可选显示时长(毫秒)
    transitions: Optional[List[str]] = None     # 图片间的可选转场类型
    positions_x: Optional[List[float]] = None   # 可选水平位置(-1到1)
    positions_y: Optional[List[float]] = None   # 可选垂直位置(-1到1)
    scales: Optional[List[float]] = None        # 可选缩放因子
    start_time: int = 0                         # 时间轴上的开始时间(毫秒)
```

### 参数说明

- **draft_id**: 目标草稿的UUID字符串，必需参数
- **image_urls**: 图片文件URL列表，必需参数，至少包含一个有效URL
- **durations**: 可选显示时长列表(毫秒)，默认每张图片3秒，如果提供则长度必须与image_urls相同
- **transitions**: 可选转场效果列表，如果提供则长度必须与image_urls相同
- **positions_x**: 可选水平位置列表(-1到1)，如果提供则长度必须与image_urls相同
- **positions_y**: 可选垂直位置列表(-1到1)，如果提供则长度必须与image_urls相同
- **scales**: 可选缩放因子列表(>0)，如果提供则长度必须与image_urls相同
- **start_time**: 在时间轴上放置图片的起始时间(毫秒)，默认为0

## 输出结果

### Output 类型定义
```python
class Output(NamedTuple):
    success: bool = True          # 操作成功状态
    message: str = "图片轨道添加成功"  # 状态消息
    track_index: int = -1         # 创建的轨道索引
    total_duration: int = 0       # 添加图片的总时长(毫秒)
```

## 使用示例

### 基本用法
```json
{
  "tool": "add_images",
  "input": {
    "draft_id": "uuid-of-draft",
    "image_urls": [
      "https://example.com/photo1.jpg",
      "https://example.com/photo2.png"
    ]
  }
}
```

### 自定义时长和转场
```json
{
  "tool": "add_images",
  "input": {
    "draft_id": "uuid-of-draft",
    "image_urls": [
      "https://example.com/intro.jpg",
      "https://example.com/main.jpg",
      "https://example.com/end.jpg"
    ],
    "durations": [2000, 5000, 3000],
    "transitions": ["淡化", "切镜", "滑动"],
    "start_time": 1000
  }
}
```

### 带位置和缩放效果
```json
{
  "tool": "add_images",
  "input": {
    "draft_id": "uuid-of-draft",
    "image_urls": [
      "https://example.com/logo.png",
      "https://example.com/background.jpg"
    ],
    "durations": [4000, 6000],
    "positions_x": [0.8, 0.0],
    "positions_y": [-0.8, 0.0],
    "scales": [0.3, 1.2],
    "transitions": ["淡入", "缩放"]
  }
}
```

### 在Coze工作流中使用
```json
{
  "step": 2,
  "name": "添加产品图片",
  "tool": "add_images",
  "input": {
    "draft_id": "{{project_draft.draft_id}}",
    "image_urls": "{{user_input.product_images}}",
    "durations": "{{user_input.image_durations}}",
    "transitions": ["淡化", "切镜"]
  },
  "output_variable": "images_added"
}
```

## 注意事项

### 输入验证
- draft_id必须是有效的UUID格式
- image_urls不能为空，必须包含至少一个有效URL
- 如果提供可选参数，其长度必须与image_urls相同
- durations必须是正整数(毫秒)
- positions_x和positions_y必须在-1到1范围内
- scales必须是大于0的数值
- start_time必须是非负整数

### 图片处理原理
- 图片被视为静态视频片段处理
- 每张图片创建一个视频段(VideoSegment)
- 默认显示时长为3秒(3000毫秒)
- 支持常见图片格式：JPG、PNG、GIF、WEBP等

### 位置和变换
- **位置坐标系**: 
  - position_x: -1(左边界) 到 1(右边界)，0为中心
  - position_y: -1(上边界) 到 1(下边界)，0为中心
- **缩放系数**: 
  - 1.0为原始大小
  - <1.0为缩小，>1.0为放大
  - 支持非等比缩放(scale_x, scale_y独立)

### 转场效果支持
- **淡化**: 图片间平滑淡入淡出
- **切镜**: 直接切换
- **滑动**: 滑动切换效果
- **缩放**: 缩放转场效果
- **旋转**: 旋转切换效果

### 轨道管理
- 每次调用创建新的视频轨道(用于图片)
- 图片按顺序在时间轴上连续排列
- 轨道索引从0开始计数
- 自动更新草稿总时长

### 性能考虑
- 图片作为视频处理，占用视频轨道资源
- 大尺寸图片可能影响渲染性能
- 建议优化图片分辨率匹配项目设置
- 过多图片可能增加草稿文件大小

### 常见使用场景
- **幻灯片演示**: 产品介绍、教程展示
- **照片集锦**: 旅行记录、活动回顾
- **Logo展示**: 品牌标识、水印添加
- **背景图片**: 静态背景、装饰元素

### 错误处理
- UUID格式验证失败会返回详细错误信息
- 草稿不存在会返回相应错误
- 参数验证失败会指出具体问题
- 图片URL无效会在媒体资源中标记

## 相关工具

- `create_draft`: 创建新草稿
- `add_videos`: 添加视频轨道
- `add_audios`: 添加音频轨道
- `add_captions`: 添加字幕轨道
- `add_effects`: 添加特效轨道
- `export_drafts`: 导出草稿数据