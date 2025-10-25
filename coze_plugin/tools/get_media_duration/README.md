# Get Media Duration Tool

## 功能描述
这是一个专为 Coze 平台设计的插件工具函数，用于获取音频或视频文件的时长信息。该工具接收一组媒体文件的 URL 链接，分析每个文件的时长，并返回累积时间轴信息。

## 输入参数

### Input 类型定义
```python
class Input:
    links: List[str]  # 媒体文件 URL 链接数组，支持音频和视频格式
```

### 参数说明
- `links`: 字符串数组，包含要分析的媒体文件 URL 链接
  - 支持的格式：MP4, AVI, MOV, MP3, WAV, AAC 等常见音视频格式
  - 要求：每个 URL 必须是可访问的有效链接

## 输出结果

### Output 类型定义
```python
class Output:
    all_timelines: List[Dict[str, int]]  # 总时间轴信息
    timelines: List[Dict[str, int]]      # 各个文件的时间轴信息
```

### 返回值结构
```json
{
  "all_timelines": [{"start": 0, "end": 总时长毫秒数}],
  "timelines": [
    {"start": 0, "end": 第一个文件时长},
    {"start": 第一个文件时长, "end": 第一个文件时长+第二个文件时长},
    {"start": 前两个文件时长和, "end": 所有文件总时长}
  ]
}
```

## 使用示例

### 输入示例
```json
{
  "links": [
    "https://example.com/video1.mp4",
    "https://example.com/audio1.mp3",
    "https://example.com/video2.mov"
  ]
}
```

### 输出示例
```json
{
  "all_timelines": [{"start": 0, "end": 9824596}],
  "timelines": [
    {"start": 0, "end": 1234567},
    {"start": 1234567, "end": 5678901},
    {"start": 5678901, "end": 9824596}
  ]
}
```

### 代码使用示例
```python
from runtime import Args
from typings.get_media_duration.get_media_duration import Input, Output

# 创建输入数据
input_data = Input(links=[
    "https://example.com/video1.mp4",
    "https://example.com/video2.mp4"
])

# 创建参数对象
args = Args(input_data)

# 调用处理函数
result = handler(args)

# 输出结果
print(f"总时长: {result.all_timelines[0]['end']}ms")
print(f"文件数量: {len(result.timelines)}")
```

## 技术实现

### 核心依赖
- `requests`: 用于下载媒体文件
- `pymediainfo`: 用于分析媒体文件时长
- `tempfile`: 用于临时文件管理

### 处理流程
1. **URL 验证**: 验证输入的 URL 格式是否正确
2. **文件下载**: 将媒体文件下载到临时目录
3. **时长分析**: 使用 pymediainfo 分析文件时长
4. **时间轴计算**: 计算累积时间轴信息
5. **资源清理**: 自动清理下载的临时文件

### 错误处理
- **无效 URL**: 跳过无效的 URL，继续处理其他文件
- **下载失败**: 网络错误或文件不存在时跳过该文件
- **格式不支持**: 不支持的媒体格式将被跳过
- **分析失败**: 无法获取时长的文件将被跳过
- **访问权限**: 处理 403 Forbidden 错误，可能因为签名 URL 过期或需要特定认证

### CDN 和云存储支持
工具针对常见的 CDN 和云存储服务进行了优化：
- **字节跳动 CDN** (oceancloudapi.com, volccdn.com): 自动添加 Coze 平台 referer
- **火山引擎 TTS** (VolcanoUserVoice): 专门优化语音合成服务的签名 URL 处理
- **AWS CloudFront**: 优化请求头配置  
- **Google Cloud Storage**: 添加适当的 referer 策略
- **多重策略**: 如果一种请求方式失败，会自动尝试其他策略

### 火山引擎语音合成特殊处理
对于 Coze 平台的语音合成插件生成的 URL，工具提供专门的处理：
- **签名 URL 检测**: 自动识别火山引擎 TTS 服务的 URL
- **过期检查**: 检测签名 URL 是否已过期
- **特殊认证头**: 针对 TTS 服务优化的请求头配置
- **详细错误信息**: 提供 TTS 特定的错误说明和解决建议

## 注意事项

### Coze 平台限制
- **文件系统约束**: 使用 `/tmp` 目录存储临时文件，自动清理避免空间耗尽
- **网络访问**: 需要网络权限下载媒体文件
- **超时控制**: 每个文件下载超时时间为 30 秒

### 性能考虑
- **流式下载**: 使用流式下载避免内存占用过大
- **并发限制**: 当前版本为串行处理，避免过多并发网络请求
- **文件大小**: 建议单个文件不超过 100MB

### 安全性
- **URL 验证**: 验证 URL 格式，防止恶意链接
- **资源限制**: 自动清理临时文件，防止磁盘空间耗尽
- **错误隔离**: 单个文件处理失败不影响其他文件

## 故障排除

### 常见问题
1. **所有文件都无法处理**: 检查网络连接和 URL 有效性
2. **部分文件被跳过**: 检查文件格式是否支持
3. **时长信息不准确**: 某些编码格式可能导致时长检测不准确

### 调试信息
工具会通过 `args.logger` 输出详细的处理日志：
- URL 可访问性检查结果
- 文件下载进度和策略
- 时长分析结果
- 错误信息详情

### 常见问题解决

#### 403 Forbidden 错误
```
Error processing [URL]: Access denied to [URL]. This may be a signed URL that requires specific authentication or has expired.
```

**可能原因和解决方案：**
1. **签名 URL 过期**: 重新生成 URL 或检查过期时间
2. **缺少认证**: URL 需要特定的 referer 或 origin 头
3. **防盗链保护**: 媒体服务启用了防盗链，只允许特定域名访问
4. **会话过期**: 如果 URL 来自用户会话，可能需要重新登录

**火山引擎 TTS 特殊情况：**
```
Access denied to Volcano TTS URL: [URL]. This signed URL may have expired, require re-authentication, or need to be accessed from the original Coze session.
```
- TTS 签名 URL 通常有较短的有效期（通常几小时）
- 需要在生成 URL 后尽快使用
- 如果 URL 来自 Coze 工作流，确保及时调用本工具

#### 404 Not Found 错误
```
Media file not found at [URL]. Please verify the URL is correct and accessible.
```

**解决方案：**
- 检查 URL 是否正确
- 确认文件是否仍然存在于服务器上
- 验证 URL 中的路径和参数

#### 超时错误
```
Download timeout for [URL]. The file may be too large or the server is slow to respond.
```

**解决方案：**
- 检查网络连接
- 文件可能过大（建议 < 100MB）
- 服务器响应慢，可以重试

## 扩展说明
此工具是 CozeJianYingAssistent 项目的一部分，专门为 Coze 平台的剪映草稿生成工作流设计。时长信息将用于后续的视频编辑和时间轴规划。