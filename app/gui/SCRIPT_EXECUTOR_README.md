# 脚本执行器标签页

## 功能说明

脚本执行器标签页允许用户在 GUI 中直接执行脚本，无需手动配置 Python 环境。所有必要的 API 依赖项（Request 类、API 函数等）会自动注入到脚本的执行环境中。

## 主要特性

### 1. 自动依赖注入

脚本执行时会自动注入以下依赖项：

#### Request 类（用于构造请求）
- `CreateDraftRequest` - 创建草稿
- `AddTrackRequest` - 添加轨道
- `AddSegmentToDraftRequest` - 添加片段到草稿
- `CreateAudioSegmentRequest` - 创建音频片段
- `CreateVideoSegmentRequest` - 创建视频片段
- `CreateTextSegmentRequest` - 创建文本片段
- `AddFadeRequest` - 添加淡入淡出
- `AddAnimationRequest` - 添加动画
- 等等...

#### API 函数（用于调用 API）
- `create_draft` - 创建草稿
- `add_track` - 添加轨道
- `add_segment` - 添加片段
- `create_audio_segment` - 创建音频片段
- `create_video_segment` - 创建视频片段
- `save_draft` - 保存草稿
- 等等...

#### 辅助工具
- `asyncio` - 异步支持
- `CustomNamespace` - 用于构造时间范围等对象
- `print` - 标准输出函数

### 2. 异步代码支持

脚本执行器完全支持异步代码，包括顶层 `await` 语句。您可以直接编写：

```python
req = CreateDraftRequest(draft_name="test", width=1920, height=1080, fps=30)
resp = await create_draft(req)
draft_id = resp.draft_id
```

无需手动定义 `async def main()` 函数。

### 3. 输出捕获

脚本执行时的所有输出（`print` 语句、错误信息等）都会显示在"执行结果"区域。

## 使用方法

### 基本步骤

1. **输入脚本**：在"脚本内容"区域输入或粘贴您的脚本
2. **执行脚本**：点击"执行脚本"按钮
3. **查看结果**：在"执行结果"区域查看输出和执行状态

### 示例脚本

#### 简单示例

```python
# 创建草稿
req = CreateDraftRequest(draft_name="我的草稿", width=1920, height=1080, fps=30)
resp = await create_draft(req)
draft_id = resp.draft_id

print(f"草稿创建成功！ID: {draft_id}")
```

#### 完整示例

```python
# 1. 创建草稿
req_draft = CreateDraftRequest(draft_name="demo", width=1920, height=1080, fps=30)
resp_draft = await create_draft(req_draft)
draft_id = resp_draft.draft_id
print(f"✓ 创建草稿: {draft_id}")

# 2. 添加音频轨道
req_audio_track = AddTrackRequest(track_type="audio", track_name=None)
resp_audio_track = await add_track(draft_id, req_audio_track)
print("✓ 添加音频轨道")

# 3. 添加视频轨道
req_video_track = AddTrackRequest(track_type="video", track_name=None)
resp_video_track = await add_track(draft_id, req_video_track)
print("✓ 添加视频轨道")

# 4. 创建音频片段
req_audio = CreateAudioSegmentRequest(
    material_url="https://example.com/audio.mp3",
    target_timerange=CustomNamespace(start=0, duration=5000000),
    speed=1,
    volume=1
)
resp_audio = await create_audio_segment(req_audio)
segment_id = resp_audio.segment_id
print(f"✓ 创建音频片段: {segment_id}")

# 5. 添加片段到草稿
req_add = AddSegmentToDraftRequest(segment_id=segment_id, track_index=None)
resp_add = await add_segment(draft_id, req_add)
print("✓ 添加片段到草稿")

# 6. 保存草稿
resp_save = await save_draft(draft_id)
print("✓ 草稿保存成功！")
```

### 加载脚本文件

您可以点击"加载脚本..."按钮从文件系统加载脚本文件。支持的文件格式：
- Python 文件 (`.py`)
- 文本文件 (`.txt`)
- 所有文件 (`*.*`)

## 注意事项

### 字符串参数

在编写脚本时，请确保字符串参数使用引号：

✅ **正确**：
```python
CreateDraftRequest(draft_name="demo", ...)
AddTrackRequest(track_type="audio", ...)
```

❌ **错误**：
```python
CreateDraftRequest(draft_name=demo, ...)  # 缺少引号
AddTrackRequest(track_type=audio, ...)    # 缺少引号
```

### 时间范围对象

使用 `CustomNamespace` 构造时间范围：

```python
target_timerange=CustomNamespace(start=0, duration=5000000)
```

时间单位为微秒（1秒 = 1,000,000 微秒）。

### 异步调用

所有 API 函数都是异步的，需要使用 `await` 关键字：

```python
resp = await create_draft(req)  # ✅ 正确
resp = create_draft(req)        # ❌ 错误 - 会返回协程对象而不是结果
```

### 错误处理

如果脚本执行出错，错误信息会显示在"执行结果"区域。常见错误：
- **语法错误**：检查 Python 语法是否正确
- **未定义的名称**：检查是否拼写正确，或使用了未注入的类/函数
- **异步错误**：确保在异步函数调用前使用 `await`

## 技术细节

### 执行环境

脚本在独立的命名空间中执行，包含：
- 所有必要的 Request 类
- 所有必要的 API 函数
- Python 内置函数
- `asyncio` 模块
- `CustomNamespace` 用于构造对象

### 异步处理

- 脚本执行在后台线程中进行，不会阻塞 GUI
- 如果脚本包含顶层 `await`，会自动包装成异步函数
- 使用新的事件循环执行异步代码

### 输出捕获

- 标准输出（`stdout`）和标准错误（`stderr`）都会被捕获
- 执行完成后显示在"执行结果"区域
- 不同类型的消息使用不同颜色显示

## 故障排查

### 脚本不执行

- 确保点击了"执行脚本"按钮
- 检查脚本内容区域是否为空
- 查看状态栏显示的状态信息

### 执行失败

- 查看"执行结果"区域的错误信息
- 检查脚本语法是否正确
- 确保所有字符串参数都使用引号
- 确认异步调用使用了 `await` 关键字

### 无输出

- 确保脚本中有 `print` 语句
- 检查是否有运行时错误
- 查看主日志面板（底部）是否有错误信息

## 示例文件

项目根目录下的 `测试脚本_可执行版.py` 提供了一个完整的可执行示例。
