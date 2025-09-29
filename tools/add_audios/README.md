# add_audios - 添加音频轨道工具

## 功能描述
将音频内容添加到现有草稿中，通过创建新的音频轨道。每次调用此工具都会创建一个包含所有音频片段的新轨道。

## 输入参数

### Input 类型定义
```python
class Input(NamedTuple):
    draft_id: str                           # 要修改的草稿UUID
    audio_urls: List[str]                   # 要添加的音频URL列表
    volumes: Optional[List[float]] = None   # 每个音频的可选音量设置(0-2)
    fade_ins: Optional[List[int]] = None    # 可选淡入时长(毫秒)
    fade_outs: Optional[List[int]] = None   # 可选淡出时长(毫秒)
    effects: Optional[List[str]] = None     # 可选音频效果类型
    start_time: int = 0                     # 时间轴上的开始时间(毫秒)
```

### 参数说明

- **draft_id**: 目标草稿的UUID字符串，必需参数
- **audio_urls**: 音频文件URL列表，必需参数，至少包含一个有效URL
- **volumes**: 可选音量设置列表(0.0-2.0)，如果提供则长度必须与audio_urls相同
- **fade_ins**: 可选淡入时长列表(毫秒)，如果提供则长度必须与audio_urls相同
- **fade_outs**: 可选淡出时长列表(毫秒)，如果提供则长度必须与audio_urls相同
- **effects**: 可选音频效果列表，如果提供则长度必须与audio_urls相同
- **start_time**: 在时间轴上放置音频的起始时间(毫秒)，默认为0

## 输出结果

### Output 类型定义
```python
class Output(NamedTuple):
    success: bool = True          # 操作成功状态
    message: str = "音频轨道添加成功"  # 状态消息
    track_index: int = -1         # 创建的轨道索引
    total_duration: int = 0       # 添加音频的总时长(毫秒)
```

## 使用示例

### 基本用法
```json
{
  "tool": "add_audios",
  "input": {
    "draft_id": "uuid-of-draft",
    "audio_urls": [
      "https://example.com/bgm.mp3",
      "https://example.com/sfx.wav"
    ]
  }
}
```

### 带音效和淡入淡出
```json
{
  "tool": "add_audios",
  "input": {
    "draft_id": "uuid-of-draft",
    "audio_urls": [
      "https://example.com/music.mp3",
      "https://example.com/voice.wav"
    ],
    "volumes": [0.6, 1.0],
    "fade_ins": [2000, 500],
    "fade_outs": [3000, 1000],
    "effects": ["回声", null],
    "start_time": 1000
  }
}
```

### 在Coze工作流中使用
```json
{
  "step": 3,
  "name": "添加背景音乐",
  "tool": "add_audios",
  "input": {
    "draft_id": "{{project_draft.draft_id}}",
    "audio_urls": "{{user_input.background_music}}",
    "volumes": [0.3],
    "fade_ins": [2000],
    "fade_outs": [2000]
  },
  "output_variable": "audio_track_added"
}
```

## 注意事项

### 输入验证
- draft_id必须是有效的UUID格式
- audio_urls不能为空，必须包含至少一个有效URL
- 如果提供可选参数，其长度必须与audio_urls相同
- volumes值必须在0.0-2.0范围内
- fade_ins和fade_outs必须是非负整数
- start_time必须是非负整数

### 轨道管理
- 每次调用都会创建一个新的音频轨道
- 音频按顺序在时间轴上连续排列
- 如果指定start_time，所有音频将从该时间点开始放置
- 轨道索引从0开始，返回新创建轨道的索引

### 音频效果支持
- 支持常见音频效果：回声、混响、降噪等
- 默认音频效果强度为1.0
- 支持淡入淡出效果，单位为毫秒
- 音量调节范围0.0(静音)到2.0(200%音量)

### 性能考虑
- 目前使用默认时长估算(30秒/音频)
- 在生产环境中应集成实际的音频分析功能
- 大量音频文件可能影响草稿加载时间

### 错误处理
- UUID格式验证失败会返回详细错误信息
- 草稿不存在会返回相应错误
- 参数验证失败会指出具体问题
- 文件系统错误会被捕获并报告

## 常见音频效果类型

- **回声**: 产生回音效果
- **混响**: 模拟房间混响
- **降噪**: 降低背景噪音
- **均衡器**: 调节音频频率
- **压缩**: 动态范围压缩
- **放大**: 音频增益

## 相关工具

- `create_draft`: 创建新草稿
- `add_videos`: 添加视频轨道
- `add_captions`: 添加字幕轨道
- `export_drafts`: 导出草稿数据