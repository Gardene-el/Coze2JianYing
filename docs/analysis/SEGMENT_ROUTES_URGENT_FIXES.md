# segment_routes.py 紧急修复指南

## 问题概述

在重构 Schema 以避免共享 Request 的过程中，`segment_routes.py` 出现了多个严重错误，需要立即修复。

## 发现的严重问题

### 🔥 问题 1: add_video_keyframe 被错误地定义为 text 端点

**位置**：约第 1130-1200 行

**错误代码**：
```python
@router.post(
    "/text/{segment_id}/add_keyframe",  # ❌ 错误！应该是 /video/
    response_model=AddTextKeyframeResponse,  # ❌ 错误！
    status_code=status.HTTP_200_OK,
    summary="添加文本关键帧",  # ❌ 错误！
    description="向文本片段添加位置、缩放、旋转等视觉属性关键帧",
)
async def add_text_keyframe(segment_id: str, request: AddTextKeyframeRequest):  # ❌ 函数名错误！
    """..."""
    logger.info(f"为视频片段 {segment_id} 添加关键帧")  # 注意这里是"视频片段"
    
    # ...
    if segment["segment_type"] != "video":  # ❌ 检查的是 video 类型！
        logger.error(f"片段类型错误: 期望 video，实际 {segment['segment_type']}")
```

**问题分析**：
1. 装饰器路径是 `/text/` 但函数名是 `add_text_keyframe`
2. 函数体内检查的却是 `segment_type != "video"`
3. 日志也说的是"视频片段"
4. 这个函数**实际上是 add_video_keyframe 的实现**，但装饰器和函数名都错了

**正确的修复**：

这个函数应该：
1. 重命名为 `add_video_keyframe`
2. 路径改为 `/video/{segment_id}/add_keyframe`
3. Response Model 改为 `AddVideoKeyframeResponse`
4. 移动到 VideoSegment 操作端点区域（在 `add_video_background_filling` 之后）

```python
@router.post(
    "/video/{segment_id}/add_keyframe",
    response_model=AddVideoKeyframeResponse,
    status_code=status.HTTP_200_OK,
    summary="添加视频关键帧",
    description="向视频片段添加位置、缩放、旋转等视觉属性关键帧",
)
async def add_video_keyframe(segment_id: str, request: AddVideoKeyframeRequest):
    """
    对应 pyJianYingDraft 代码：
    ```python
    video_segment.add_keyframe(KeyframeProperty.position_x, "2s", 0.5)
    ```
    """
    logger.info(f"为视频片段 {segment_id} 添加关键帧")
    
    try:
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            return response_manager.format_not_found_error("segment", segment_id)
        
        if segment["segment_type"] != "video":
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "video", "actual": segment["segment_type"]},
            )
        
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_keyframe", operation_data
        )
        
        if not success:
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加关键帧失败"},
            )
        
        import uuid
        keyframe_id = str(uuid.uuid4())
        
        success_response = response_manager.success(message="视频关键帧添加成功")
        return {"keyframe_id": keyframe_id, **success_response}
        
    except Exception as e:
        logger.error(f"添加视频关键帧失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)
```

### 🔥 问题 2: add_sticker_keyframe 使用了旧的共享 Schema

**位置**：约第 1203-1274 行

**错误代码**：
```python
@router.post(
    "/sticker/{segment_id}/add_keyframe",
    response_model=AddKeyframeResponse,  # ❌ 旧 Schema
    status_code=status.HTTP_200_OK,
    summary="添加视觉属性关键帧",
    description="向贴纸片段添加视觉属性关键帧",
)
async def add_sticker_keyframe(segment_id: str, request: AddKeyframeRequest):  # ❌ 旧 Schema
```

**正确的修复**：
```python
@router.post(
    "/sticker/{segment_id}/add_keyframe",
    response_model=AddStickerKeyframeResponse,  # ✅ 新 Schema
    status_code=status.HTTP_200_OK,
    summary="添加贴纸关键帧",
    description="向贴纸片段添加位置、缩放、旋转等视觉属性关键帧",
)
async def add_sticker_keyframe(segment_id: str, request: AddStickerKeyframeRequest):  # ✅ 新 Schema
    """
    对应 pyJianYingDraft 代码：
    ```python
    sticker_segment.add_keyframe(KeyframeProperty.position_x, "2s", 0.5)
    ```
    """
    logger.info(f"为贴纸片段 {segment_id} 添加关键帧")
    
    try:
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            return response_manager.format_not_found_error("segment", segment_id)
        
        if segment["segment_type"] != "sticker":
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "sticker", "actual": segment["segment_type"]},
            )
        
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_keyframe", operation_data
        )
        
        if not success:
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加关键帧失败"},
            )
        
        import uuid
        keyframe_id = str(uuid.uuid4())
        
        success_response = response_manager.success(message="贴纸关键帧添加成功")
        return {"keyframe_id": keyframe_id, **success_response}
        
    except Exception as e:
        logger.error(f"添加贴纸关键帧失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)
```

### 🔥 问题 3: add_text_keyframe 定义重复

**位置**：
- 第一次：约第 1138 行（实际是 add_video_keyframe 的错误实现）
- 第二次：约第 1479-1548 行（使用旧 Schema）

**问题分析**：
1. 第一个应该改为 `add_video_keyframe` 并移到 VideoSegment 区域
2. 第二个应该更新为使用新的 `AddTextKeyframeRequest`

**第二个 add_text_keyframe 的正确代码**：
```python
@router.post(
    "/text/{segment_id}/add_keyframe",
    response_model=AddTextKeyframeResponse,
    status_code=status.HTTP_200_OK,
    summary="添加文本关键帧",
    description="向文本片段添加位置、缩放、旋转等视觉属性关键帧",
)
async def add_text_keyframe(segment_id: str, request: AddTextKeyframeRequest):  # ✅ 新 Schema
    """
    对应 pyJianYingDraft 代码：
    ```python
    text_segment.add_keyframe(KeyframeProperty.position_x, "2s", 0.5)
    ```
    """
    logger.info(f"为文本片段 {segment_id} 添加关键帧")
    
    try:
        segment = segment_manager.get_segment(segment_id)
        if not segment:
            return response_manager.format_not_found_error("segment", segment_id)
        
        if segment["segment_type"] != "text":
            return response_manager.error(
                error_code=ErrorCode.SEGMENT_TYPE_MISMATCH,
                details={"expected": "text", "actual": segment["segment_type"]},
            )
        
        operation_data = request.dict()
        success = segment_manager.add_operation(
            segment_id, "add_keyframe", operation_data
        )
        
        if not success:
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": "添加关键帧失败"},
            )
        
        import uuid
        keyframe_id = str(uuid.uuid4())
        
        success_response = response_manager.success(message="文本关键帧添加成功")
        return {"keyframe_id": keyframe_id, **success_response}
        
    except Exception as e:
        logger.error(f"添加文本关键帧失败: {e}", exc_info=True)
        return response_manager.format_internal_error(e)
```

## 修复步骤建议

### 步骤 1: 修复 add_video_keyframe（最紧急）

1. 找到第一个 `add_text_keyframe` 函数（约 1138 行）
2. 将整个函数（包括装饰器）剪切
3. 粘贴到 VideoSegment 操作端点区域，在 `add_video_background_filling` 之后
4. 修改装饰器和函数签名如上所示

### 步骤 2: 修复 add_sticker_keyframe

1. 找到 `add_sticker_keyframe` 函数（约 1207 行）
2. 将 `AddKeyframeRequest` 改为 `AddStickerKeyframeRequest`
3. 将 `AddKeyframeResponse` 改为 `AddStickerKeyframeResponse`
4. 更新日志消息

### 步骤 3: 修复 add_text_keyframe

1. 找到第二个 `add_text_keyframe` 函数（约 1483 行）
2. 将 `AddKeyframeRequest` 改为 `AddTextKeyframeRequest`
3. 确保没有其他 `add_text_keyframe` 定义

### 步骤 4: 验证文件结构

确保文件的端点按以下顺序组织：

```python
# ==================== Segment 创建端点 ====================
# create_audio_segment
# create_video_segment
# create_text_segment
# create_sticker_segment
# create_effect_segment
# create_filter_segment

# ==================== AudioSegment 操作端点 ====================
# add_audio_effect         → AddAudioEffectRequest
# add_audio_fade           → AddAudioFadeRequest
# add_audio_keyframe       → AddAudioKeyframeRequest

# ==================== VideoSegment 操作端点 ====================
# add_video_animation      → AddVideoAnimationRequest
# add_video_effect         → AddVideoEffectRequest
# add_video_fade           → AddVideoFadeRequest
# add_video_filter         → AddFilterRequest (Video 专用)
# add_video_mask           → AddMaskRequest
# add_video_transition     → AddTransitionRequest
# add_video_background_filling → AddBackgroundFillingRequest
# add_video_keyframe       → AddVideoKeyframeRequest  ← 应该在这里！

# ==================== StickerSegment 操作端点 ====================
# add_sticker_keyframe     → AddStickerKeyframeRequest

# ==================== TextSegment 操作端点 ====================
# add_text_animation       → AddTextAnimationRequest
# add_text_bubble          → AddBubbleRequest
# add_text_effect          → AddTextEffectRequest
# add_text_keyframe        → AddTextKeyframeRequest

# ==================== 查询端点 ====================
# get_segment_detail
```

## 测试计划

修复后需要测试：

1. **API 端点可访问性**：
   ```bash
   # 测试 video keyframe
   POST /api/segment/video/{id}/add_keyframe
   
   # 测试 sticker keyframe
   POST /api/segment/sticker/{id}/add_keyframe
   
   # 测试 text keyframe
   POST /api/segment/text/{id}/add_keyframe
   ```

2. **Schema 验证**：
   - 确保每个端点只接受对应的 Request Schema
   - 测试错误的 Schema 类型会被拒绝

3. **Segment 类型验证**：
   - 确保 video 端点验证 `segment_type == "video"`
   - 确保 sticker 端点验证 `segment_type == "sticker"`
   - 确保 text 端点验证 `segment_type == "text"`

## 关键要点总结

1. **函数名、装饰器路径、segment_type 检查必须一致**
   - `add_video_keyframe` → `/video/` → `segment_type == "video"`
   - `add_sticker_keyframe` → `/sticker/` → `segment_type == "sticker"`
   - `add_text_keyframe` → `/text/` → `segment_type == "text"`

2. **使用正确的 Request/Response Schema**
   - 不要使用共享的旧 Schema
   - 每个 Segment 类型有自己独立的 Schema

3. **日志消息要准确**
   - `logger.info(f"为视频片段 {segment_id} 添加关键帧")`
   - `logger.info(f"为贴纸片段 {segment_id} 添加关键帧")`
   - `logger.info(f"为文本片段 {segment_id} 添加关键帧")`

## 相关文件

- `app/schemas/segment_schemas.py` - Schema 定义（已完成）
- `app/api/segment_routes.py` - 需要紧急修复的文件
- `app/schemas/__init__.py` - 需要导出新 Schema
- `docs/analysis/SCHEMA_REFACTORING_PLAN.md` - 完整重构计划

## 修复优先级

🔥 **紧急**（立即修复）：
1. 修复 add_video_keyframe 的错误定义
2. 更新 add_sticker_keyframe 的 Schema
3. 修复 add_text_keyframe 的 Schema

⚠️ **重要**（后续执行）：
4. 更新 __init__.py 导出
5. 更新测试文件
6. 更新文档