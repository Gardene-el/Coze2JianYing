# pyJianYingDraft Segment Type Mapping Corrections

This document summarizes the corrections made to the Draft Generator Interface to properly align with pyJianYingDraft's segment type hierarchy.

## Latest Update: Track-Segment Type Validation

**Track-Segment Relationship Fix**: After user feedback, additional issues were identified and fixed:

1. **Removed invalid "image" track_type** - pyJianYingDraft only has 6 track types (video, audio, text, sticker, effect, filter). Images go on video tracks, not separate image tracks.

2. **Added type validation** - TrackConfig now includes `__post_init__` validation to ensure:
   - Only valid track_types are used
   - Segments match their track_type (e.g., AudioSegmentConfig only on audio tracks)
   - VideoSegmentConfig and ImageSegmentConfig can both go on video tracks
   
3. **Clarified track usage in documentation**:
   - Each track type accepts only specific segment types (matches pyJianYingDraft's `Track[Seg_type]` generic design)
   - Examples now clearly explain that tracks list can contain any number/types of tracks
   - Added mapping table showing which segments go on which tracks

**Result**: TrackConfig now properly enforces the one-to-one (or one-to-few for video track) relationship between track types and segment types, matching pyJianYingDraft's design.

## Update (After Initial Correction)

**MediaResource Removal**: After the initial corrections, it was identified that `MediaResource` was redundant and unnecessary:
- Material URLs are already stored directly in segment configurations (`material_url` field)
- Resource types can be inferred from segment types (VideoSegment → video, AudioSegment → audio, etc.)
- Metadata (duration, format, etc.) was never actually used in the implementation
- This created data duplication (same URL stored twice)

**Result**: `MediaResource` class and `DraftConfig.media_resources` field have been completely removed. Segments now directly reference media URLs without intermediate abstraction.

## Original Issue Summary

**Problem**: The Draft Generator Interface had misconceptions about segment types in pyJianYingDraft:
1. MediaResource was incorrectly assumed to be a pyJianYingDraft class (later determined to be unnecessary altogether)
2. Missing segment configuration classes for StickerSegment and FilterSegment
3. Unclear that ImageSegment doesn't exist in pyJianYingDraft (images use VideoSegment)
4. Documentation didn't explain the segment hierarchy
5. Track-segment type relationship was not properly enforced (added later)

## pyJianYingDraft Segment Hierarchy (Correct Understanding)

```
BaseSegment (基类)
├── MediaSegment (媒体片段基类 - 不直接实例化)
│   ├── AudioSegment ✅ 可直接使用
│   └── VisualSegment (视觉片段基类 - 不直接实例化)
│       ├── VideoSegment ✅ 可直接使用 (也用于图片!)
│       ├── TextSegment ✅ 可直接使用
│       └── StickerSegment ✅ 可直接使用
├── EffectSegment ✅ 可直接使用 (独立轨道)
└── FilterSegment ✅ 可直接使用 (独立轨道)
```

### Key Facts

1. **Base Classes** (`MediaSegment`, `VisualSegment`): These are abstract base classes and are NOT directly instantiated
2. **Concrete Segment Types**: Only 6 types can be directly used:
   - `VideoSegment` (for both videos and images)
   - `AudioSegment`
   - `TextSegment`
   - `StickerSegment`
   - `EffectSegment` (independent track)
   - `FilterSegment` (independent track)

## Corrections Made

### 1. Added Missing Segment Configuration Classes

#### StickerSegmentConfig
```python
@dataclass
class StickerSegmentConfig:
    """Configuration for sticker segments
    
    对应 pyJianYingDraft.StickerSegment (继承自 VisualSegment -> MediaSegment -> BaseSegment)
    """
    resource_id: str
    time_range: TimeRange
    # Transform properties, flip options, keyframes...
```

#### FilterSegmentConfig
```python
@dataclass
class FilterSegmentConfig:
    """Configuration for filter segments
    
    对应 pyJianYingDraft.FilterSegment (继承自 BaseSegment)
    """
    filter_type: str
    time_range: TimeRange
    intensity: float = 1.0
```

### 2. Clarified MediaResource Nature

**Updated Documentation**:
```python
@dataclass
class MediaResource:
    """Represents a media resource with URL and metadata
    
    注意: 这不是 pyJianYingDraft 的类! 
    这是本项目为适配 Coze 平台的 URL-based 资源管理而创建的抽象类。
    在草稿生成器中，URL 会被下载为本地文件，然后传递给 pyJianYingDraft 的 Material 类:
    - VideoMaterial(path)
    - AudioMaterial(path)
    - 图片作为 VideoMaterial(path) 处理
    """
```

### 3. Clarified ImageSegmentConfig Mapping

**Updated Documentation**:
```python
@dataclass
class ImageSegmentConfig:
    """Configuration for an image segment
    
    ⚠️ 重要: 图片在 pyJianYingDraft 中没有独立的 ImageSegment 类!
    图片实际上是作为 VideoSegment 处理的（静态视频）。
    
    对应 pyJianYingDraft.VideoSegment:
    - material: VideoMaterial(图片本地路径) <- material_url 需下载
    - target_timerange: Timerange(start, duration) <- time_range (start, end)
    - source_timerange: None (图片没有素材裁剪范围)
    ...
    """
```

### 4. Updated Configuration Class Mappings

All segment configuration classes now have clear docstrings showing their mapping:

| 配置类 | pyJianYingDraft 类 | 说明 |
|--------|-------------------|------|
| `VideoSegmentConfig` | `VideoSegment` | 视频片段 |
| `AudioSegmentConfig` | `AudioSegment` | 音频片段 |
| `ImageSegmentConfig` | `VideoSegment` | ⚠️ 图片作为静态视频处理 |
| `TextSegmentConfig` | `TextSegment` | 文本/字幕片段 |
| `StickerSegmentConfig` | `StickerSegment` | 贴纸片段 |
| `EffectSegmentConfig` | `EffectSegment` | 特效片段（独立轨道）|
| `FilterSegmentConfig` | `FilterSegment` | 滤镜片段（独立轨道）|

## Documentation Updates

### 1. models.py
- Added comprehensive header documentation explaining the segment hierarchy
- Added detailed docstrings for each segment configuration class
- Clarified MediaResource's role as an abstraction, not a pyJianYingDraft class

### 2. README.md
- Added "⚠️ 重要：pyJianYingDraft 段类型映射关系" section at the top
- Added visual hierarchy diagram
- Added mapping table
- Added clarification about MediaResource
- Updated segment configuration descriptions

### 3. copilot-instructions.md
- Added new section "重要架构说明：pyJianYingDraft 段类型映射"
- Documented MediaResource's positioning
- Documented segment type hierarchy
- Added "常见误解和注意事项" section

## Testing

Created comprehensive tests to verify:
1. All 7 segment types can be created and serialized
2. Track types correctly handle their respective segment types
3. Serialization produces valid JSON with correct structure

Test results: ✅ All tests passed

## Benefits of These Corrections

1. **Clarity**: Developers now understand the exact correspondence between our configuration classes and pyJianYingDraft's classes
2. **Completeness**: All pyJianYingDraft segment types are now supported
3. **Correctness**: Misconceptions about MediaResource and ImageSegment are resolved
4. **Maintainability**: Clear documentation helps future development and debugging
5. **Integration**: Proper mapping ensures smooth integration with the future draft generator

## Files Changed

- `data_structures/draft_generator_interface/models.py`
- `data_structures/draft_generator_interface/README.md`
- `.github/copilot-instructions.md`

## Related Issues

This work addresses the issue: "详细查看阅读pyjianyingdraft的segment.py以修正MediaResource的谬误"
