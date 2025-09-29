# add_images - 添加图片轨道工具

## 功能描述
将图片内容添加到现有草稿中，通过创建新的视频轨道。图片被处理为具有指定时长的视频片段。每次调用此工具都会创建一个包含所有图片片段的新轨道。

## 输入参数

### Input 类型定义
```python
class Input(NamedTuple):
    draft_id: str                               # 要修改的草稿UUID
    image_infos: str                            # JSON字符串，包含图片信息数组
```

### 图片信息格式
`image_infos` 参数是一个JSON字符串，包含图片信息对象数组，每个对象格式如下：

```json
{
  "image_url": "https://example.com/image.jpg",  # 必需：图片URL
  "start": 0,                                    # 必需：开始时间(毫秒)
  "end": 3000,                                   # 必需：结束时间(毫秒)
  "width": 1440,                                 # 可选：图片宽度
  "height": 1080,                                # 可选：图片高度
  "in_animation": "轻微放大",                      # 可选：入场动画
  "in_animation_duration": 100000                # 可选：入场动画时长(毫秒)
}
```

### 参数说明

- **draft_id**: 目标草稿的UUID字符串，必需参数
- **image_infos**: JSON字符串，包含图片信息数组，必需参数
  - **image_url**: 图片文件URL，必需字段
  - **start**: 图片在时间轴上的开始时间(毫秒)，必需字段
  - **end**: 图片在时间轴上的结束时间(毫秒)，必需字段，必须大于start
  - **width**: 图片宽度(像素)，可选字段
  - **height**: 图片高度(像素)，可选字段
  - **in_animation**: 入场动画名称，可选字段
  - **in_animation_duration**: 入场动画时长(毫秒)，可选字段

## 输出结果

### Output 类型定义
```python
class Output(NamedTuple):
    segment_ids: List[str]                      # 生成的片段UUID列表
    segment_infos: List[dict]                   # 片段信息列表，包含id、start、end
```

## 使用示例

### 基本用法
```json
{
  "tool": "add_images",
  "input": {
    "draft_id": "uuid-of-draft",
    "image_infos": "[{\"image_url\":\"https://example.com/photo1.jpg\",\"start\":0,\"end\":3000},{\"image_url\":\"https://example.com/photo2.png\",\"start\":3000,\"end\":6000}]"
  }
}
```

### 带动画和尺寸信息
```json
{
  "tool": "add_images",
  "input": {
    "draft_id": "uuid-of-draft",
    "image_infos": "[{\"image_url\":\"https://example.com/image1.jpg\",\"start\":0,\"end\":3936000,\"width\":1440,\"height\":1080},{\"image_url\":\"https://example.com/image2.jpg\",\"start\":3936000,\"end\":7176000,\"width\":1440,\"height\":1080,\"in_animation\":\"轻微放大\",\"in_animation_duration\":100000}]"
  }
}
```

### 复杂示例（用户提供的格式）
```json
{
  "tool": "add_images",
  "input": {
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "image_infos": "[{\"image_url\":\"https://s.coze.cn/t/W9CvmtJHJWI/\",\"start\":0,\"end\":3936000,\"width\":1440,\"height\":1080},{\"image_url\":\"https://s.coze.cn/t/iGLRGx6JvZ0/\",\"start\":3936000,\"end\":7176000,\"width\":1440,\"height\":1080,\"in_animation\":\"轻微放大\",\"in_animation_duration\":100000},{\"image_url\":\"https://s.coze.cn/t/amCMhpjzEC8/\",\"start\":7176000,\"end\":11688000,\"width\":1440,\"height\":1080}]"
  }
}
```

### 预期输出格式
```json
{
  "segment_ids": [
    "efde9038-64b8-40d2-bdab-fca68e6bf943",
    "7dc6650c-cacf-420a-ae88-be38f51b5bdc",
    "1a5ddb57-621b-40c5-b369-7b6af822b39d"
  ],
  "segment_infos": [
    {
      "end": 3936000,
      "id": "efde9038-64b8-40d2-bdab-fca68e6bf943",
      "start": 0
    },
    {
      "end": 7176000,
      "id": "7dc6650c-cacf-420a-ae88-be38f51b5bdc",
      "start": 3936000
    },
    {
      "end": 11688000,
      "id": "1a5ddb57-621b-40c5-b369-7b6af822b39d",
      "start": 7176000
    }
  ]
}

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