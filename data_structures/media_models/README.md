# Media Models

## 功能描述
媒体文件相关的数据模型定义，专为 Coze 平台插件工具设计。提供媒体文件处理、时长分析和时间轴计算的标准化数据结构。

## 主要数据模型

### MediaTimeline
```python
@dataclass
class MediaTimeline:
    start: int  # 开始时间（毫秒）
    end: int    # 结束时间（毫秒）
```
表示具有开始和结束时间的时间轴段，用于视频编辑和时间轴规划。

### MediaInfo
```python
@dataclass
class MediaInfo:
    url: str                    # 原始 URL
    duration_ms: int           # 时长（毫秒）
    file_size: Optional[int]   # 文件大小（字节）
    format: Optional[str]      # 媒体格式
    error: Optional[str]       # 错误信息
```
包含媒体文件的完整信息，包括 URL、时长、大小等元数据。

### MediaDurationResult
```python
@dataclass
class MediaDurationResult:
    all_timelines: List[Dict[str, int]]  # 总时间轴信息
    timelines: List[Dict[str, int]]      # 各文件时间轴
    processed_count: int                 # 成功处理的文件数
    failed_count: int                    # 失败的文件数
    total_duration_ms: int               # 总时长（毫秒）
```
媒体时长分析的完整结果，包含处理统计和时间轴数据。

## 输入输出模型

### MediaProcessingInput
```python
class MediaProcessingInput(NamedTuple):
    links: List[str]  # 媒体 URL 列表
```
媒体处理工具的标准输入格式。

### MediaProcessingOutput
```python
class MediaProcessingOutput(NamedTuple):
    all_timelines: List[Dict[str, int]]  # 总时间轴
    timelines: List[Dict[str, int]]      # 各文件时间轴
```
媒体处理工具的标准输出格式。

## 工具函数

### URL 验证
```python
validate_media_url(url: str) -> bool
is_supported_media_format(url: str) -> bool
```
验证媒体 URL 的有效性和格式支持。

### 时间轴计算
```python
calculate_cumulative_timelines(durations_ms: List[int]) -> List[MediaTimeline]
```
从时长列表计算累积时间轴。

### 格式化工具
```python
format_duration(duration_ms: int) -> str
```
将毫秒时长格式化为可读字符串。

## 使用示例

### 创建时间轴结果
```python
from data_structures.media_models.models import MediaDurationResult

# 从时长列表创建结果
durations = [1234567, 4444334, 4145695]  # 毫秒
result = MediaDurationResult.from_durations(durations)

print(f"总时长: {format_duration(result.total_duration_ms)}")
print(f"处理文件数: {result.processed_count}")
```

### URL 验证
```python
from data_structures.media_models.models import validate_media_url, is_supported_media_format

url = "https://example.com/video.mp4"
if validate_media_url(url) and is_supported_media_format(url):
    print("URL 有效且格式支持")
```

### 时间轴计算
```python
from data_structures.media_models.models import calculate_cumulative_timelines

durations = [5000, 3000, 2000]  # 毫秒
timelines = calculate_cumulative_timelines(durations)

for i, timeline in enumerate(timelines):
    print(f"文件 {i+1}: {timeline.start}ms - {timeline.end}ms")
```

## 兼容性说明

为了与现有工具兼容，提供了别名：
```python
Input = MediaProcessingInput
Output = MediaProcessingOutput
```

这样现有的工具函数可以直接使用 `Input` 和 `Output` 类型而无需修改。

## 设计原则

1. **Coze 平台兼容**: 遵循 Coze 平台的类型系统和约束
2. **链接资源处理**: 专门设计用于处理网页链接形式的媒体资源
3. **错误处理**: 内置错误信息和处理状态跟踪
4. **扩展性**: 支持未来添加更多媒体元数据字段
5. **标准化**: 为整个项目提供统一的数据结构标准