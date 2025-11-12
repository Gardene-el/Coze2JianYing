# 快速开始：脚本执行器使用指南

## 打开脚本执行器

1. 启动 Coze2JianYing 应用程序
2. 在主窗口中找到"脚本执行器"标签页
3. 点击切换到该标签页

## 第一个脚本：创建草稿

### 步骤 1：输入脚本

在"脚本内容"区域输入以下代码：

```python
# 创建一个简单的草稿
req = CreateDraftRequest(
    draft_name="我的第一个草稿",
    width=1920,
    height=1080,
    fps=30
)

resp = await create_draft(req)
draft_id = resp.draft_id

print(f"✓ 草稿创建成功！")
print(f"草稿 ID: {draft_id}")
```

### 步骤 2：执行脚本

1. 点击"执行脚本"按钮
2. 等待脚本执行完成
3. 查看"执行结果"区域的输出

### 预期输出

```
============================================================
开始执行脚本...
============================================================

============================================================
✓ 脚本执行完成
============================================================

--- 标准输出 ---
✓ 草稿创建成功！
草稿 ID: [UUID]

--- 执行结果 ---
draft_id = [UUID]
req = CreateDraftRequest(draft_name='我的第一个草稿', ...)
resp = CreateDraftResponse(draft_id='[UUID]', ...)
```

## 完整示例：创建带音频的草稿

```python
# 1. 创建草稿
print("步骤 1: 创建草稿")
req_draft = CreateDraftRequest(
    draft_name="音频演示",
    width=1920,
    height=1080,
    fps=30
)
resp_draft = await create_draft(req_draft)
draft_id = resp_draft.draft_id
print(f"✓ 草稿 ID: {draft_id}")

# 2. 添加音频轨道
print("\n步骤 2: 添加音频轨道")
req_track = AddTrackRequest(
    track_type="audio",
    track_name=None
)
resp_track = await add_track(draft_id, req_track)
print("✓ 音频轨道已添加")

# 3. 创建音频片段
print("\n步骤 3: 创建音频片段")
req_segment = CreateAudioSegmentRequest(
    material_url="https://gardene-el.github.io/Coze2JianYing/assets/audio.mp3",
    target_timerange=CustomNamespace(start=0, duration=5000000),
    speed=1,
    volume=1,
    change_pitch=False
)
resp_segment = await create_audio_segment(req_segment)
segment_id = resp_segment.segment_id
print(f"✓ 片段 ID: {segment_id}")

# 4. 添加片段到草稿
print("\n步骤 4: 添加片段到草稿")
req_add = AddSegmentToDraftRequest(
    segment_id=segment_id,
    track_index=None
)
resp_add = await add_segment(draft_id, req_add)
print("✓ 片段已添加到草稿")

# 5. 保存草稿
print("\n步骤 5: 保存草稿")
resp_save = await save_draft(draft_id)
print("✓ 草稿保存成功！")

print(f"\n完成！草稿已创建: {draft_id}")
```

## 常见问题

### Q: 脚本执行失败，提示"NameError"

**A:** 检查是否所有字符串参数都使用了引号。

错误示例：
```python
CreateDraftRequest(draft_name=demo, ...)  # 错误！
```

正确示例：
```python
CreateDraftRequest(draft_name="demo", ...)  # 正确
```

### Q: 脚本执行后没有输出

**A:** 确保脚本中包含 `print()` 语句。API 调用不会自动输出结果。

### Q: 如何使用时间范围？

**A:** 使用 `CustomNamespace` 构造时间范围对象：

```python
target_timerange=CustomNamespace(start=0, duration=5000000)
```

时间单位是微秒：
- 1 秒 = 1,000,000 微秒
- 5 秒 = 5,000,000 微秒

### Q: 如何加载外部脚本文件？

**A:** 
1. 点击"加载脚本..."按钮
2. 选择脚本文件
3. 文件内容会自动加载到脚本区域
4. 点击"执行脚本"按钮运行

### Q: 可以保存脚本吗？

**A:** 目前不支持从 GUI 保存脚本，但您可以：
1. 手动复制脚本内容
2. 保存到文本文件
3. 下次使用"加载脚本..."按钮加载

## 提示和技巧

### 1. 使用注释组织代码

```python
# ========== 第一步：初始化 ==========
req = CreateDraftRequest(...)
resp = await create_draft(req)

# ========== 第二步：添加内容 ==========
# 添加轨道
await add_track(...)

# 添加片段
await create_audio_segment(...)
```

### 2. 添加调试输出

```python
print(f"当前 draft_id: {draft_id}")
print(f"当前 segment_id: {segment_id}")
```

### 3. 错误处理（可选）

虽然脚本执行器会自动捕获错误，您也可以添加自己的错误处理：

```python
try:
    resp = await create_draft(req)
    print("✓ 成功")
except Exception as e:
    print(f"✗ 失败: {e}")
```

### 4. 使用变量简化代码

```python
# 定义常量
DRAFT_NAME = "我的草稿"
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

# 使用常量
req = CreateDraftRequest(
    draft_name=DRAFT_NAME,
    width=VIDEO_WIDTH,
    height=VIDEO_HEIGHT,
    fps=FPS
)
```

## 下一步

- 查看 `app/gui/SCRIPT_EXECUTOR_README.md` 了解完整功能说明
- 查看 `测试脚本_可执行版.py` 了解更多示例
- 查看 `SCRIPT_EXECUTOR_IMPLEMENTATION.md` 了解技术实现细节

## 需要帮助？

如果遇到问题：
1. 检查"执行结果"区域的错误信息
2. 查看主日志面板（窗口底部）
3. 参考完整文档 `SCRIPT_EXECUTOR_README.md`
