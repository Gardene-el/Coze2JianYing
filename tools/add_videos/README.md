# add_videos - 添加视频轨道工具

## 功能描述
将视频内容添加到现有草稿中，通过创建新的视频轨道。每次调用此工具都会创建一个包含所有视频片段的新轨道。

## 输入参数

### Input 类型定义
```python
class Input(NamedTuple):
    draft_id: str                           # 要修改的草稿UUID
    video_urls: List[str]                   # 要添加的视频URL列表
    filters: Optional[List[str]] = None     # 每个视频的可选滤镜名称
    transitions: Optional[List[str]] = None # 视频间的可选转场类型
    volumes: Optional[List[float]] = None   # 每个视频的可选音量设置(0-2)
    start_time: int = 0                     # 时间轴上的开始时间(毫秒)
```

### 参数说明

- **draft_id**: 目标草稿的UUID字符串，必需参数
- **video_urls**: 视频文件URL列表，必需参数，至少包含一个有效URL
- **filters**: 可选滤镜列表，如果提供则长度必须与video_urls相同
- **transitions**: 可选转场效果列表，如果提供则长度必须与video_urls相同
- **volumes**: 可选音量设置列表(0.0-2.0)，如果提供则长度必须与video_urls相同
- **start_time**: 在时间轴上放置视频的起始时间(毫秒)，默认为0

## 输出结果

### Output 类型定义
```python
class Output(NamedTuple):
    success: bool = True          # 操作成功状态
    message: str = "视频轨道添加成功"  # 状态消息
    track_index: int = -1         # 创建的轨道索引
    total_duration: int = 0       # 添加视频的总时长(毫秒)
```

## 使用示例

### 基本用法
```json
{
  "tool": "add_videos",
  "input": {
    "draft_id": "uuid-of-draft",
    "video_urls": [
      "https://example.com/video1.mp4",
      "https://example.com/video2.mp4"
    ]
  }
}
```

### 带滤镜和转场效果
```json
{
  "tool": "add_videos",
  "input": {
    "draft_id": "uuid-of-draft", 
    "video_urls": [
      "https://example.com/intro.mp4",
      "https://example.com/main.mp4"
    ],
    "filters": ["暖冬", "电影"],
    "transitions": ["淡化", "切镜"],
    "volumes": [1.0, 0.8],
    "start_time": 2000
  }
}
```

### 在Coze工作流中使用
```json
{
  "step": 2,
  "name": "添加主要视频内容",
  "tool": "add_videos",
  "input": {
    "draft_id": "{{project_draft.draft_id}}",
    "video_urls": "{{user_input.video_list}}",
    "filters": "{{user_input.video_filters}}",
    "start_time": 0
  },
  "output_variable": "video_track_added"
}
```

## 注意事项

### 输入验证
- draft_id必须是有效的UUID格式
- video_urls不能为空，必须包含至少一个有效URL
- 如果提供可选参数(filters、transitions、volumes)，其长度必须与video_urls相同
- volumes值必须在0.0-2.0范围内
- start_time必须是非负整数

### 轨道管理
- 每次调用都会创建一个新的视频轨道
- 视频按顺序在时间轴上连续排列
- 如果指定start_time，所有视频将从该时间点开始放置
- 轨道索引从0开始，返回新创建轨道的索引

### 性能考虑
- 目前使用默认时长估算(10秒/视频)
- 在生产环境中应集成实际的视频分析功能
- 大量视频可能影响草稿加载时间

### 错误处理
- UUID格式验证失败会返回详细错误信息
- 草稿不存在会返回相应错误
- 参数验证失败会指出具体问题
- 文件系统错误会被捕获并报告

## 相关工具

- `create_draft`: 创建新草稿
- `add_audios`: 添加音频轨道
- `add_captions`: 添加字幕轨道
- `export_drafts`: 导出草稿数据