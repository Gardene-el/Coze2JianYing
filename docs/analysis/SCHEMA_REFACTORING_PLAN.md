# Schema 重构计划文档

## 重构目标

避免因参数结构相同而共享 Request Schema 的设计，确保每个 Segment 类型的操作都有独立的 Request/Response Schema。

## 重构原则

1. **语义清晰性**：不同的 Segment 类型应该有不同的 Request Schema
2. **未来扩展性**：参数差异不会导致 breaking change
3. **类型安全**：在 Schema 层面明确 effect_type 等参数的取值范围
4. **维护性**：代码意图更明确，减少开发者困惑

## 已完成的重构

### 1. AddEffectRequest 拆分 ✅

**原共享 Schema**：
```python
class AddEffectRequest(BaseModel):
    """添加特效请求（用于 AudioSegment/VideoSegment）"""
    effect_type: str
    params: Optional[List[float]]
```

**拆分后**：
```python
class AddAudioEffectRequest(BaseModel):
    """添加音频特效请求（用于 AudioSegment）"""
    effect_type: str  # AudioSceneEffectType | ToneEffectType | SpeechToSongType
    params: Optional[List[float]]

class AddVideoEffectRequest(BaseModel):
    """添加视频特效请求（用于 VideoSegment）"""
    effect_type: str  # VideoSceneEffectType | VideoCharacterEffectType
    params: Optional[List[float]]
```

**对应 Response**：
- `AddAudioEffectResponse`
- `AddVideoEffectResponse`

### 2. AddFadeRequest 拆分 ✅

**原共享 Schema**：
```python
class AddFadeRequest(BaseModel):
    """添加淡入淡出请求（用于 AudioSegment/VideoSegment）"""
    in_duration: str
    out_duration: str
```

**拆分后**：
```python
class AddAudioFadeRequest(BaseModel):
    """添加音频淡入淡出请求（用于 AudioSegment）"""
    in_duration: str
    out_duration: str

class AddVideoFadeRequest(BaseModel):
    """添加视频淡入淡出请求（用于 VideoSegment）"""
    in_duration: str
    out_duration: str
```

**对应 Response**：
- `AddAudioFadeResponse`
- `AddVideoFadeResponse`

### 3. AddKeyframeRequest 拆分 ✅

**原共享 Schema**：
```python
class AddKeyframeRequest(BaseModel):
    """添加关键帧请求"""
    time_offset: Any
    value: float
    property: Optional[str]  # VideoSegment 需要
```

**拆分后**：
```python
class AddAudioKeyframeRequest(BaseModel):
    """添加音频关键帧请求（用于 AudioSegment）"""
    time_offset: Any
    value: float  # 音量值 0-2

class AddVideoKeyframeRequest(BaseModel):
    """添加视频关键帧请求（用于 VideoSegment）"""
    time_offset: Any
    value: float
    property: str  # 必需！position_x, position_y, scale, rotation, opacity 等

class AddTextKeyframeRequest(BaseModel):
    """添加文本关键帧请求（用于 TextSegment）"""
    time_offset: Any
    value: float
    property: str  # position_x, position_y, scale, rotation, opacity 等

class AddStickerKeyframeRequest(BaseModel):
    """添加贴纸关键帧请求（用于 StickerSegment）"""
    time_offset: Any
    value: float
    property: str  # position_x, position_y, scale, rotation, opacity 等
```

**对应 Response**：
- `AddAudioKeyframeResponse`
- `AddVideoKeyframeResponse`
- `AddTextKeyframeResponse`
- `AddStickerKeyframeResponse`

### 4. AddAnimationRequest 拆分 ✅

**原共享 Schema**：
```python
class AddAnimationRequest(BaseModel):
    """添加动画请求（用于 VideoSegment/TextSegment）"""
    animation_type: str
    duration: Optional[str]
```

**拆分后**：
```python
class AddVideoAnimationRequest(BaseModel):
    """添加视频动画请求（用于 VideoSegment）"""
    animation_type: str  # IntroType | OutroType | GroupAnimationType
    duration: Optional[str]

class AddTextAnimationRequest(BaseModel):
    """添加文本动画请求（用于 TextSegment）"""
    animation_type: str  # TextAnimationType
    duration: Optional[str]
```

**对应 Response**：
- `AddVideoAnimationResponse`
- `AddTextAnimationResponse`

## 需要更新的文件

### 1. Schema 定义文件 ✅
- `app/schemas/general_schemas.py` - 已完成拆分

### 2. API 路由文件 ⚠️ 部分完成
- `app/api/segment_routes.py` - 已更新 imports 和部分函数签名
- **需要继续修复**：
  - `add_video_keyframe` 函数位置错误（在文本段落中）
  - `add_sticker_keyframe` 仍使用 `AddKeyframeRequest`
  - `add_text_keyframe` 重复定义（两处）

### 3. Schema __init__.py 文件 🔄 待更新
- `app/schemas/__init__.py` - 需要导出新的 Schema

### 4. GUI 脚本执行器 🔄 待更新
- `app/gui/script_executor_tab.py` - 需要更新 imports

### 5. 测试文件 🔄 待更新
- `tests/test_script_executor.py`
- `tests/test_script_executor_integration.py`

### 6. Coze 插件工具 🔄 待更新
- `coze_plugin/raw_tools/add_audio_effect/handler.py`
- `coze_plugin/raw_tools/add_video_effect/handler.py`
- 其他相关工具

### 7. 文档文件 🔄 待更新
- `docs/API_ENDPOINTS_REFERENCE.md`
- `docs/draft_generator/SCRIPT_EXECUTOR_TAB.md`
- 其他相关文档

## segment_routes.py 需要修复的问题

### 问题 1: add_video_keyframe 函数位置错误

**当前位置**：在 `add_video_background_filling` 之后，但装饰器写的是 `/text/{segment_id}/add_keyframe`

**错误代码**：
```python
@router.post(
    "/text/{segment_id}/add_keyframe",  # ❌ 错误！应该是 /video/
    response_model=AddTextKeyframeResponse,  # ❌ 错误！应该是 AddVideoKeyframeResponse
    status_code=status.HTTP_200_OK,
    summary="添加文本关键帧",  # ❌ 错误！应该是视频关键帧
    description="向文本片段添加位置、缩放、旋转等视觉属性关键帧",
)
async def add_video_keyframe(segment_id: str, request: AddTextKeyframeRequest):  # ❌ 错误！
```

**应该是**：
```python
@router.post(
    "/video/{segment_id}/add_keyframe",
    response_model=AddVideoKeyframeResponse,
    status_code=status.HTTP_200_OK,
    summary="添加视频关键帧",
    description="向视频片段添加位置、缩放、旋转等视觉属性关键帧",
)
async def add_video_keyframe(segment_id: str, request: AddVideoKeyframeRequest):
    # 验证 segment_type == "video"
    # ...
```

**建议位置**：在 `add_video_background_filling` 之后，VideoSegment 操作端点区域内

### 问题 2: add_sticker_keyframe 仍使用旧 Schema

**当前代码**：
```python
async def add_sticker_keyframe(segment_id: str, request: AddKeyframeRequest):  # ❌
```

**应该改为**：
```python
@router.post(
    "/sticker/{segment_id}/add_keyframe",
    response_model=AddStickerKeyframeResponse,
    status_code=status.HTTP_200_OK,
    summary="添加贴纸关键帧",
    description="向贴纸片段添加位置、缩放、旋转等视觉属性关键帧",
)
async def add_sticker_keyframe(segment_id: str, request: AddStickerKeyframeRequest):
    # ...
```

### 问题 3: add_text_keyframe 重复定义

文件中有**两个** `add_text_keyframe` 函数定义：

1. 第一个（行 1140 附近）：装饰器错误，实际是 `add_video_keyframe`
2. 第二个（行 1487 附近）：使用旧的 `AddKeyframeRequest`

**应该只保留一个**，使用 `AddTextKeyframeRequest`

## 完整的 API 端点对照表

| Segment 类型 | 操作 | API 端点 | Request Schema | Response Schema |
|-------------|------|---------|----------------|-----------------|
| **Audio** | 添加特效 | `/audio/{id}/add_effect` | `AddAudioEffectRequest` | `AddAudioEffectResponse` |
| | 添加淡入淡出 | `/audio/{id}/add_fade` | `AddAudioFadeRequest` | `AddAudioFadeResponse` |
| | 添加关键帧 | `/audio/{id}/add_keyframe` | `AddAudioKeyframeRequest` | `AddAudioKeyframeResponse` |
| **Video** | 添加动画 | `/video/{id}/add_animation` | `AddVideoAnimationRequest` | `AddVideoAnimationResponse` |
| | 添加特效 | `/video/{id}/add_effect` | `AddVideoEffectRequest` | `AddVideoEffectResponse` |
| | 添加淡入淡出 | `/video/{id}/add_fade` | `AddVideoFadeRequest` | `AddVideoFadeResponse` |
| | 添加滤镜 | `/video/{id}/add_filter` | `AddFilterRequest` | `AddFilterResponse` |
| | 添加蒙版 | `/video/{id}/add_mask` | `AddMaskRequest` | `AddMaskResponse` |
| | 添加转场 | `/video/{id}/add_transition` | `AddTransitionRequest` | `AddTransitionResponse` |
| | 添加背景填充 | `/video/{id}/add_background_filling` | `AddBackgroundFillingRequest` | `AddBackgroundFillingResponse` |
| | 添加关键帧 | `/video/{id}/add_keyframe` | `AddVideoKeyframeRequest` | `AddVideoKeyframeResponse` |
| **Text** | 添加动画 | `/text/{id}/add_animation` | `AddTextAnimationRequest` | `AddTextAnimationResponse` |
| | 添加气泡 | `/text/{id}/add_bubble` | `AddBubbleRequest` | `AddBubbleResponse` |
| | 添加花字特效 | `/text/{id}/add_effect` | `AddTextEffectRequest` | `AddTextEffectResponse` |
| | 添加关键帧 | `/text/{id}/add_keyframe` | `AddTextKeyframeRequest` | `AddTextKeyframeResponse` |
| **Sticker** | 添加关键帧 | `/sticker/{id}/add_keyframe` | `AddStickerKeyframeRequest` | `AddStickerKeyframeResponse` |

## 下一步行动计划

### 高优先级（立即执行）

1. **修复 segment_routes.py 中的错误** 🔥
   - [ ] 修正 `add_video_keyframe` 函数的装饰器和位置
   - [ ] 更新 `add_sticker_keyframe` 使用 `AddStickerKeyframeRequest`
   - [ ] 删除重复的 `add_text_keyframe` 定义，保留正确的版本

2. **更新 app/schemas/__init__.py** 📦
   - [ ] 导出所有新的 Request/Response Schema
   - [ ] 移除旧的共享 Schema（如果存在）

### 中优先级（后续执行）

3. **更新 GUI 和测试文件** 🧪
   - [ ] `app/gui/script_executor_tab.py`
   - [ ] `tests/test_script_executor.py`
   - [ ] `tests/test_script_executor_integration.py`

4. **更新 Coze 插件工具** 🔌
   - [ ] 所有受影响的 handler 文件
   - [ ] 对应的 README 文档

### 低优先级（文档更新）

5. **更新项目文档** 📚
   - [ ] `docs/API_ENDPOINTS_REFERENCE.md`
   - [ ] `docs/draft_generator/SCRIPT_EXECUTOR_TAB.md`
   - [ ] 其他相关文档

## 向后兼容性考虑

### Breaking Changes

这次重构是一个 **Breaking Change**，因为：

1. 所有共享的 Request Schema 名称都变了
2. API 调用方需要更新代码以使用新的 Schema

### 迁移指南

**旧代码**：
```python
from src.schemas.general_schemas import AddEffectRequest

# Audio
request = AddEffectRequest(effect_type="...", params=[...])
await add_audio_effect(segment_id, request)

# Video
request = AddEffectRequest(effect_type="...", params=[...])
await add_video_effect(segment_id, request)
```

**新代码**：
```python
from src.schemas.general_schemas import (
    AddAudioEffectRequest,
    AddVideoEffectRequest
)

# Audio
request = AddAudioEffectRequest(effect_type="...", params=[...])
await add_audio_effect(segment_id, request)

# Video
request = AddVideoEffectRequest(effect_type="...", params=[...])
await add_video_effect(segment_id, request)
```

### Deprecation 策略（可选）

如果需要保持向后兼容：

1. 保留旧的 Schema 作为 alias
2. 添加 deprecation warning
3. 在未来版本中移除

```python
# 向后兼容 alias（带弃用警告）
import warnings

class AddEffectRequest(AddAudioEffectRequest):
    """
    @deprecated: 使用 AddAudioEffectRequest 或 AddVideoEffectRequest
    """
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "AddEffectRequest is deprecated. "
            "Use AddAudioEffectRequest or AddVideoEffectRequest instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)
```

## 测试计划

### 单元测试

- [ ] 测试所有新 Schema 的验证逻辑
- [ ] 测试 API 端点接受正确的 Request Schema
- [ ] 测试错误的 Schema 类型会被拒绝

### 集成测试

- [ ] 端到端测试所有 Segment 操作
- [ ] 测试 Script Executor 与新 Schema 的兼容性
- [ ] 测试 Coze 插件工具的生成和执行

### 回归测试

- [ ] 运行现有的所有测试套件
- [ ] 确保没有意外的 breaking changes

## 参考文档

- [AddEffectRequest 设计分析报告](./AddEffectRequest_DESIGN_ANALYSIS.md)
- [API 端点参考文档](../API_ENDPOINTS_REFERENCE.md)
- [pyJianYingDraft 文档](https://github.com/GuanYixuan/pyJianYingDraft)

## 变更历史

- 2024-XX-XX: 创建重构计划文档
- 2024-XX-XX: 完成 general_schemas.py 的 Schema 拆分
- 2024-XX-XX: 部分更新 segment_routes.py（待完成）