# 修复：add_* 函数 handler 中的 ID 提取问题

## 问题描述

在 handler 生成模块中，`add_*` 类函数（如 `add_video_effect`、`add_video_keyframe` 等）的 handler 没有从 API 响应中提取和保存返回的 ID 值。这导致这些函数返回的对象 ID（如 `effect_id`、`keyframe_id` 等）无法被后续的 API 调用引用。

## 问题影响

当用户在 Coze 工作流中调用 `add_*` 函数后，虽然操作成功执行，但返回的 ID 被丢弃了。如果用户需要在后续步骤中引用这些创建的对象（例如修改某个特效或关键帧），就无法做到，因为没有保存这些对象的 ID。

## 根本原因

在 `scripts/handler_generator/e_api_call_code_generator.py` 中，`generate_api_call_code` 方法只硬编码处理了 `draft_id` 和 `segment_id` 两种 ID 类型，没有考虑其他类型的 ID（如 `effect_id`、`keyframe_id`、`animation_id` 等）。

### 修复前的代码逻辑

```python
# 检查 output 是否包含 draft_id 或 segment_id
# 如果是 create 类型的函数，需要保存创建的对象ID以便后续引用
has_output_draft_id = any(f["name"] == "draft_id" for f in output_fields)
has_output_segment_id = any(f["name"] == "segment_id" for f in output_fields)

if has_output_draft_id:
    api_call_code += "\ndraft_{generated_uuid} = resp_{generated_uuid}.draft_id\n"

if has_output_segment_id:
    api_call_code += "\nsegment_{generated_uuid} = resp_{generated_uuid}.segment_id\n"
```

这种硬编码方式只处理了两种特定的 ID 类型，忽略了所有其他 ID 类型。

## 解决方案

将硬编码的 ID 检查改为循环遍历所有可能的 ID 字段类型，对每个 ID 字段自动生成提取代码。

### 修复后的代码逻辑

```python
# 检查 output 中所有的 ID 字段并保存
# 这些 ID 可以在后续的 API 调用中被引用
# 支持的 ID 类型：draft_id, segment_id, effect_id, keyframe_id, animation_id, 
# filter_id, mask_id, transition_id, bubble_id 等
id_fields_to_extract = [
    "draft_id",
    "segment_id", 
    "effect_id",
    "keyframe_id",
    "animation_id",
    "filter_id",
    "mask_id",
    "transition_id",
    "bubble_id",
    "track_id",
]

for id_field in id_fields_to_extract:
    has_output_id = any(f["name"] == id_field for f in output_fields)
    if has_output_id:
        # 保存为 {type}_{uuid} 格式
        # 例如：effect_{uuid}, keyframe_{uuid} 等
        # 这样后续函数可以通过这个变量名引用创建的对象
        id_type = id_field.replace("_id", "")  # draft_id -> draft, effect_id -> effect
        api_call_code += "\n"
        api_call_code += f"{id_type}_{{generated_uuid}} = resp_{{generated_uuid}}.{id_field}\n"
```

## 修复效果

### 支持的 ID 类型

修复后，以下所有 ID 类型都能正确提取：

| ID 字段名 | 变量名格式 | 适用函数示例 |
|----------|-----------|------------|
| `draft_id` | `draft_{uuid}` | `create_draft` |
| `segment_id` | `segment_{uuid}` | `create_video_segment`, `create_audio_segment` 等 |
| `effect_id` | `effect_{uuid}` | `add_video_effect`, `add_audio_effect`, `add_text_effect`, `add_global_effect` |
| `keyframe_id` | `keyframe_{uuid}` | `add_video_keyframe`, `add_audio_keyframe`, `add_text_keyframe`, `add_sticker_keyframe` |
| `animation_id` | `animation_{uuid}` | `add_video_animation`, `add_text_animation` |
| `filter_id` | `filter_{uuid}` | `add_video_filter`, `add_global_filter` |
| `mask_id` | `mask_{uuid}` | `add_video_mask` |
| `transition_id` | `transition_{uuid}` | `add_video_transition` |
| `bubble_id` | `bubble_{uuid}` | `add_text_bubble` |
| `track_id` | `track_{uuid}` | (预留，当前 API 未使用) |

### 修复前后对比示例

#### 示例 1: add_video_effect

**修复前：**
```python
resp_{generated_uuid} = await add_video_effect(segment_{args.input.segment_id}, req_{generated_uuid})
"""
```

**修复后：**
```python
resp_{generated_uuid} = await add_video_effect(segment_{args.input.segment_id}, req_{generated_uuid})

effect_{generated_uuid} = resp_{generated_uuid}.effect_id
"""
```

#### 示例 2: add_video_keyframe

**修复前：**
```python
resp_{generated_uuid} = await add_video_keyframe(segment_{args.input.segment_id}, req_{generated_uuid})
"""
```

**修复后：**
```python
resp_{generated_uuid} = await add_video_keyframe(segment_{args.input.segment_id}, req_{generated_uuid})

keyframe_{generated_uuid} = resp_{generated_uuid}.keyframe_id
"""
```

## 影响范围

### 修改的文件

1. **核心修复：**
   - `scripts/handler_generator/e_api_call_code_generator.py` - 修复了 ID 提取逻辑

2. **重新生成的 handler 文件（15 个）：**
   - `coze_plugin/raw_tools/add_audio_effect/handler.py`
   - `coze_plugin/raw_tools/add_audio_keyframe/handler.py`
   - `coze_plugin/raw_tools/add_global_effect/handler.py`
   - `coze_plugin/raw_tools/add_global_filter/handler.py`
   - `coze_plugin/raw_tools/add_sticker_keyframe/handler.py`
   - `coze_plugin/raw_tools/add_text_animation/handler.py`
   - `coze_plugin/raw_tools/add_text_bubble/handler.py`
   - `coze_plugin/raw_tools/add_text_effect/handler.py`
   - `coze_plugin/raw_tools/add_text_keyframe/handler.py`
   - `coze_plugin/raw_tools/add_video_animation/handler.py`
   - `coze_plugin/raw_tools/add_video_effect/handler.py`
   - `coze_plugin/raw_tools/add_video_filter/handler.py`
   - `coze_plugin/raw_tools/add_video_keyframe/handler.py`
   - `coze_plugin/raw_tools/add_video_mask/handler.py`
   - `coze_plugin/raw_tools/add_video_transition/handler.py`

3. **新增测试：**
   - `scripts/test_id_extraction.py` - 专门测试 ID 提取功能的测试脚本

### 不受影响的函数

以下函数不返回可引用的 ID，因此不受此修复影响（它们正确地不提取任何 ID）：

- `add_track` - 返回 `track_index`（不是 ID）
- `add_segment` - 用于将现有 segment 添加到 track，不创建新对象
- `add_audio_fade` / `add_video_fade` - 直接修改 segment，不返回新 ID
- `add_video_background_filling` - 直接修改 segment，不返回新 ID
- `save_draft` - 保存操作，不返回新 ID

## 测试验证

### 测试结果

创建了专门的测试脚本 `scripts/test_id_extraction.py` 来验证所有函数的 ID 提取行为。

**测试结果：** ✅ 28/28 通过 (100% 成功率)

测试验证了：
1. 所有应该提取 ID 的函数都正确提取了相应的 ID
2. 所有不应该提取 ID 的函数都正确地没有提取任何 ID
3. 提取的 ID 类型与函数返回的 ID 类型匹配

### 运行测试

```bash
# 验证 ID 提取功能
python scripts/test_id_extraction.py

# 验证生成的 handler 结构完整性
python scripts/test_generated_handlers.py
```

## 向后兼容性

✅ 完全向后兼容

- 原有的 `draft_id` 和 `segment_id` 提取逻辑保持不变
- 所有现有的 handler 文件功能保持一致
- 只是新增了对其他 ID 类型的提取支持

## 未来扩展

如果将来需要支持新的 ID 类型，只需在 `id_fields_to_extract` 列表中添加新的 ID 字段名即可：

```python
id_fields_to_extract = [
    "draft_id",
    "segment_id",
    # ... 现有的 ID 类型 ...
    "new_id_type",  # 添加新的 ID 类型
]
```

然后重新运行 `scripts/generate_handler_from_api.py` 即可自动生成支持新 ID 类型的 handler。

## 总结

这次修复通过将硬编码的 ID 检查改为通用的循环遍历机制，解决了 `add_*` 函数无法保存返回 ID 的问题。修复后：

- ✅ 所有返回 ID 的函数都能正确提取和保存 ID
- ✅ 后续的 API 调用可以引用这些 ID
- ✅ 完全向后兼容
- ✅ 易于扩展支持新的 ID 类型
- ✅ 100% 测试通过

## 相关文件

- **核心修复代码：** `scripts/handler_generator/e_api_call_code_generator.py`
- **测试脚本：** `scripts/test_id_extraction.py`
- **生成脚本：** `scripts/generate_handler_from_api.py`
