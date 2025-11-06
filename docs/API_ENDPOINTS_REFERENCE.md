# API 端点完整参考文档

本文档列出所有 API 端点，直接镜像 pyJianYingDraft 的原生 API 结构。

## 设计原则

1. **UUID 引用系统**：所有对象创建时返回 UUID，后续操作使用 UUID 引用
2. **两级层次结构**：`draft_id` 用于 Script/Draft 操作，`segment_id` 用于 Segment 操作
3. **类型区分路径**：`/segment/{type}/{id}/operation` 区分不同类型的 segment 操作
4. **自动素材下载**：API 接收 URL，后台自动下载后调用 pyJianYingDraft

## 1. Draft/Script 操作

### 1.1 创建草稿
```
POST /api/draft/create
```

**功能**：创建新的剪映草稿项目

**请求参数**：
```json
{
  "draft_name": "string",     // 项目名称
  "width": 1920,              // 视频宽度（像素）
  "height": 1080,             // 视频高度（像素）
  "fps": 30,                  // 帧率
  "allow_replace": true       // 是否允许替换同名草稿（可选）
}
```

**响应**：
```json
{
  "draft_id": "uuid-string",  // 草稿 UUID
  "success": true,
  "message": "草稿创建成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
script = draft_folder.create_draft("demo", 1920, 1080, allow_replace=True)
```

---

### 1.2 添加轨道
```
POST /api/draft/{draft_id}/add_track
```

**功能**：向草稿添加轨道

**路径参数**：
- `draft_id`: 草稿 UUID

**请求参数**：
```json
{
  "track_type": "audio",      // 轨道类型：audio/video/text/sticker/effect/filter
  "track_name": "string"      // 轨道名称（可选）
}
```

**响应**：
```json
{
  "success": true,
  "track_index": 0,           // 轨道索引
  "message": "轨道添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
script.add_track(draft.TrackType.audio)
```

---

### 1.3 添加片段到草稿
```
POST /api/draft/{draft_id}/add_segment
```

**功能**：将已创建的 segment 添加到草稿中

**路径参数**：
- `draft_id`: 草稿 UUID

**请求参数**：
```json
{
  "segment_id": "uuid-string", // Segment UUID
  "track_index": 0             // 目标轨道索引（可选，自动选择合适轨道）
}
```

**响应**：
```json
{
  "success": true,
  "message": "片段添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
script.add_segment(audio_segment)
```

---

### 1.4 添加全局特效
```
POST /api/draft/{draft_id}/add_effect
```

**功能**：向草稿添加全局特效

**路径参数**：
- `draft_id`: 草稿 UUID

**请求参数**：
```json
{
  "effect_type": "string",      // 特效类型（VideoSceneEffectType 或 VideoCharacterEffectType）
  "target_timerange": {
    "start": 0,                 // 开始时间（微秒）
    "duration": 5000000         // 持续时间（微秒）
  },
  "params": [0.5, 1.0]         // 特效参数列表（可选）
}
```

**响应**：
```json
{
  "success": true,
  "effect_id": "uuid-string",   // 特效 UUID
  "message": "特效添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
script.add_effect(VideoSceneEffectType.XXX, timerange, params)
```

---

### 1.5 添加全局滤镜
```
POST /api/draft/{draft_id}/add_filter
```

**功能**：向草稿添加全局滤镜

**路径参数**：
- `draft_id`: 草稿 UUID

**请求参数**：
```json
{
  "filter_type": "string",      // 滤镜类型（FilterType）
  "target_timerange": {
    "start": 0,
    "duration": 5000000
  },
  "intensity": 100.0           // 滤镜强度 0-100
}
```

**响应**：
```json
{
  "success": true,
  "filter_id": "uuid-string",
  "message": "滤镜添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
script.add_filter(FilterType.XXX, timerange, intensity)
```

---

### 1.6 保存草稿
```
POST /api/draft/{draft_id}/save
```

**功能**：保存并完成草稿编辑，生成剪映草稿文件

**路径参数**：
- `draft_id`: 草稿 UUID

**请求参数**：无

**响应**：
```json
{
  "success": true,
  "draft_path": "/path/to/draft/folder",  // 草稿文件夹路径
  "message": "草稿保存成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
script.save()
```

---

## 2. Segment 创建

### 2.1 创建 AudioSegment
```
POST /api/segment/audio/create
```

**功能**：创建音频片段

**请求参数**：
```json
{
  "material_url": "https://example.com/audio.mp3",  // 音频素材 URL
  "target_timerange": {
    "start": 0,                 // 在轨道上的起始位置（微秒）
    "duration": 5000000         // 持续时长（微秒）
  },
  "source_timerange": {         // 素材裁剪范围（可选）
    "start": 0,
    "duration": 5000000
  },
  "speed": 1.0,                 // 播放速度（可选，默认 1.0）
  "volume": 1.0,                // 音量 0-2（可选，默认 1.0）
  "change_pitch": false         // 是否跟随变速改变音调（可选）
}
```

**响应**：
```json
{
  "segment_id": "uuid-string",  // Segment UUID
  "success": true,
  "message": "音频片段创建成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
audio_segment = draft.AudioSegment(
    "audio.mp3",
    trange("0s", "5s"),
    volume=0.6
)
```

---

### 2.2 创建 VideoSegment
```
POST /api/segment/video/create
```

**功能**：创建视频片段

**请求参数**：
```json
{
  "material_url": "https://example.com/video.mp4",
  "target_timerange": {
    "start": 0,
    "duration": 5000000
  },
  "source_timerange": {         // 可选
    "start": 0,
    "duration": 5000000
  },
  "speed": 1.0,                 // 可选
  "volume": 1.0,                // 可选
  "change_pitch": false,        // 可选
  "clip_settings": {            // 图像调节设置（可选）
    "brightness": 0.0,
    "contrast": 0.0,
    "saturation": 0.0,
    "temperature": 0.0,
    "hue": 0.0
  }
}
```

**响应**：
```json
{
  "segment_id": "uuid-string",
  "success": true,
  "message": "视频片段创建成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
video_segment = draft.VideoSegment(
    VideoMaterial("video.mp4"),
    trange("0s", "5s")
)
```

---

### 2.3 创建 TextSegment
```
POST /api/segment/text/create
```

**功能**：创建文本片段

**请求参数**：
```json
{
  "text_content": "Hello World", // 文本内容
  "target_timerange": {
    "start": 0,
    "duration": 3000000
  },
  "font_family": "黑体",         // 字体名称（可选）
  "font_size": 24.0,            // 字体大小（可选）
  "color": "#FFFFFF",           // 文字颜色（可选）
  "text_style": {               // 文本样式（可选）
    "bold": false,
    "italic": false,
    "underline": false
  },
  "position": {                 // 位置（可选）
    "x": 0.0,
    "y": 0.0
  }
}
```

**响应**：
```json
{
  "segment_id": "uuid-string",
  "success": true,
  "message": "文本片段创建成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
text_segment = draft.TextSegment(
    "Hello World",
    trange("0s", "3s")
)
```

---

### 2.4 创建 StickerSegment
```
POST /api/segment/sticker/create
```

**功能**：创建贴纸片段

**请求参数**：
```json
{
  "material_url": "https://example.com/sticker.png",
  "target_timerange": {
    "start": 0,
    "duration": 3000000
  },
  "position": {                 // 可选
    "x": 0.0,
    "y": 0.0
  },
  "scale": 1.0                  // 可选
}
```

**响应**：
```json
{
  "segment_id": "uuid-string",
  "success": true,
  "message": "贴纸片段创建成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
sticker_segment = draft.StickerSegment(
    material,
    trange("0s", "3s")
)
```

---

## 3. AudioSegment 操作

### 3.1 添加音频特效
```
POST /api/segment/audio/{segment_id}/add_effect
```

**路径参数**：
- `segment_id`: AudioSegment UUID

**请求参数**：
```json
{
  "effect_type": "string",      // AudioSceneEffectType/ToneEffectType/SpeechToSongType
  "params": [0.5, 1.0]         // 特效参数列表（可选，范围 0-100）
}
```

**响应**：
```json
{
  "success": true,
  "effect_id": "uuid-string",
  "message": "音频特效添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
audio_segment.add_effect(AudioSceneEffectType.XXX, params)
```

---

### 3.2 添加淡入淡出
```
POST /api/segment/audio/{segment_id}/add_fade
```

**路径参数**：
- `segment_id`: AudioSegment UUID

**请求参数**：
```json
{
  "in_duration": "1s",          // 淡入时长（字符串或微秒数）
  "out_duration": "0s"          // 淡出时长
}
```

**响应**：
```json
{
  "success": true,
  "message": "淡入淡出添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
audio_segment.add_fade("1s", "0s")
```

---

### 3.3 添加音量关键帧
```
POST /api/segment/audio/{segment_id}/add_keyframe
```

**路径参数**：
- `segment_id`: AudioSegment UUID

**请求参数**：
```json
{
  "time_offset": 2000000,       // 时间偏移量（微秒）或字符串 "2s"
  "volume": 0.8                 // 音量值 0-2
}
```

**响应**：
```json
{
  "success": true,
  "keyframe_id": "uuid-string",
  "message": "关键帧添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
audio_segment.add_keyframe("2s", 0.8)
```

---

## 4. VideoSegment 操作

### 4.1 添加动画
```
POST /api/segment/video/{segment_id}/add_animation
```

**路径参数**：
- `segment_id`: VideoSegment UUID

**请求参数**：
```json
{
  "animation_type": "string",   // IntroType/OutroType/GroupAnimationType
  "duration": "1s"              // 动画时长（可选）
}
```

**响应**：
```json
{
  "success": true,
  "animation_id": "uuid-string",
  "message": "动画添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
video_segment.add_animation(IntroType.XXX, duration="1s")
```

---

### 4.2 添加视频特效
```
POST /api/segment/video/{segment_id}/add_effect
```

**路径参数**：
- `segment_id`: VideoSegment UUID

**请求参数**：
```json
{
  "effect_type": "string",      // VideoSceneEffectType 或 VideoCharacterEffectType
  "params": [0.5, 1.0],        // 特效参数（可选）
  "apply_target_type": 0       // 应用目标类型：0=片段，1=画面，2=全局（可选）
}
```

**响应**：
```json
{
  "success": true,
  "effect_id": "uuid-string",
  "message": "视频特效添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
video_segment.add_effect(VideoSceneEffectType.XXX, params)
```

---

### 4.3 添加淡入淡出
```
POST /api/segment/video/{segment_id}/add_fade
```

**路径参数**：
- `segment_id`: VideoSegment UUID

**请求参数**：
```json
{
  "in_duration": "1s",
  "out_duration": "0s"
}
```

**响应**：
```json
{
  "success": true,
  "message": "淡入淡出添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
video_segment.add_fade("1s", "0s")
```

---

### 4.4 添加滤镜
```
POST /api/segment/video/{segment_id}/add_filter
```

**路径参数**：
- `segment_id`: VideoSegment UUID

**请求参数**：
```json
{
  "filter_type": "string",      // FilterType
  "intensity": 100.0           // 滤镜强度 0-100（可选，默认 100）
}
```

**响应**：
```json
{
  "success": true,
  "filter_id": "uuid-string",
  "message": "滤镜添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
video_segment.add_filter(FilterType.XXX, intensity=100.0)
```

---

### 4.5 添加蒙版
```
POST /api/segment/video/{segment_id}/add_mask
```

**路径参数**：
- `segment_id`: VideoSegment UUID

**请求参数**：
```json
{
  "mask_type": "string",        // MaskType
  "center_x": 0.0,             // 蒙版中心 X 坐标（可选）
  "center_y": 0.0,             // 蒙版中心 Y 坐标（可选）
  "size": 0.5,                 // 蒙版大小（可选）
  "feather": 0.0,              // 羽化程度 0-1（可选）
  "invert": false,             // 是否反转（可选）
  "rotation": 0.0              // 旋转角度（可选）
}
```

**响应**：
```json
{
  "success": true,
  "mask_id": "uuid-string",
  "message": "蒙版添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
video_segment.add_mask(MaskType.XXX, center_x=0.0, center_y=0.0, size=0.5)
```

---

### 4.6 添加转场
```
POST /api/segment/video/{segment_id}/add_transition
```

**路径参数**：
- `segment_id`: VideoSegment UUID

**请求参数**：
```json
{
  "transition_type": "string",  // TransitionType
  "duration": "1s"             // 转场时长（可选）
}
```

**响应**：
```json
{
  "success": true,
  "transition_id": "uuid-string",
  "message": "转场添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
video_segment.add_transition(TransitionType.XXX, duration="1s")
```

---

### 4.7 添加背景填充
```
POST /api/segment/video/{segment_id}/add_background_filling
```

**路径参数**：
- `segment_id`: VideoSegment UUID

**请求参数**：
```json
{
  "fill_type": "blur",          // "blur" 或 "color"
  "blur": 0.0625,              // 模糊程度（fill_type=blur 时）
  "color": "#00000000"         // 填充颜色（fill_type=color 时）
}
```

**响应**：
```json
{
  "success": true,
  "message": "背景填充添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
video_segment.add_background_filling("blur", blur=0.0625)
```

---

### 4.8 添加视觉属性关键帧
```
POST /api/segment/video/{segment_id}/add_keyframe
```

**路径参数**：
- `segment_id`: VideoSegment UUID

**请求参数**：
```json
{
  "property": "position_x",     // KeyframeProperty: position_x/position_y/scale_x/scale_y/rotation/alpha
  "time_offset": "2s",         // 时间偏移量（微秒或字符串）
  "value": 0.5                 // 属性值
}
```

**响应**：
```json
{
  "success": true,
  "keyframe_id": "uuid-string",
  "message": "关键帧添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
video_segment.add_keyframe(KeyframeProperty.position_x, "2s", 0.5)
```

---

## 5. StickerSegment 操作

### 5.1 添加视觉属性关键帧
```
POST /api/segment/sticker/{segment_id}/add_keyframe
```

**路径参数**：
- `segment_id`: StickerSegment UUID

**请求参数**：
```json
{
  "property": "position_x",     // KeyframeProperty
  "time_offset": "2s",
  "value": 0.5
}
```

**响应**：
```json
{
  "success": true,
  "keyframe_id": "uuid-string",
  "message": "关键帧添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
sticker_segment.add_keyframe(KeyframeProperty.position_x, "2s", 0.5)
```

---

## 6. TextSegment 操作

### 6.1 添加文字动画
```
POST /api/segment/text/{segment_id}/add_animation
```

**路径参数**：
- `segment_id`: TextSegment UUID

**请求参数**：
```json
{
  "animation_type": "string",   // TextIntro/TextOutro/TextLoopAnim
  "duration": "1s"             // 可选
}
```

**响应**：
```json
{
  "success": true,
  "animation_id": "uuid-string",
  "message": "文字动画添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
text_segment.add_animation(TextIntro.XXX, duration="1s")
```

---

### 6.2 添加气泡
```
POST /api/segment/text/{segment_id}/add_bubble
```

**路径参数**：
- `segment_id`: TextSegment UUID

**请求参数**：
```json
{
  "effect_id": "string",        // 气泡特效 ID
  "resource_id": "string"       // 资源 ID
}
```

**响应**：
```json
{
  "success": true,
  "bubble_id": "uuid-string",
  "message": "气泡添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
text_segment.add_bubble(effect_id, resource_id)
```

---

### 6.3 添加花字特效
```
POST /api/segment/text/{segment_id}/add_effect
```

**路径参数**：
- `segment_id`: TextSegment UUID

**请求参数**：
```json
{
  "effect_id": "string"         // 花字特效 ID
}
```

**响应**：
```json
{
  "success": true,
  "effect_id": "uuid-string",
  "message": "花字特效添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
text_segment.add_effect("7296357486490144036")
```

---

### 6.4 添加视觉属性关键帧
```
POST /api/segment/text/{segment_id}/add_keyframe
```

**路径参数**：
- `segment_id`: TextSegment UUID

**请求参数**：
```json
{
  "property": "position_x",     // KeyframeProperty
  "time_offset": "2s",
  "value": 0.5
}
```

**响应**：
```json
{
  "success": true,
  "keyframe_id": "uuid-string",
  "message": "关键帧添加成功"
}
```

**对应 pyJianYingDraft 代码**：
```python
text_segment.add_keyframe(KeyframeProperty.position_x, "2s", 0.5)
```

---

## 7. 辅助端点

### 7.1 查询草稿状态
```
GET /api/draft/{draft_id}/status
```

**路径参数**：
- `draft_id`: 草稿 UUID

**响应**：
```json
{
  "draft_id": "uuid-string",
  "draft_name": "string",
  "tracks": [
    {
      "track_type": "audio",
      "track_index": 0,
      "segment_count": 2
    }
  ],
  "segments": [
    {
      "segment_id": "uuid-string",
      "segment_type": "audio",
      "material_url": "https://...",
      "download_status": "completed"
    }
  ],
  "download_status": {
    "total": 5,
    "completed": 5,
    "pending": 0,
    "failed": 0
  }
}
```

---

### 7.2 查询 Segment 详情
```
GET /api/segment/{segment_type}/{segment_id}
```

**路径参数**：
- `segment_type`: audio/video/text/sticker
- `segment_id`: Segment UUID

**响应**：
```json
{
  "segment_id": "uuid-string",
  "segment_type": "audio",
  "material_url": "https://...",
  "download_status": "completed",
  "local_path": "/path/to/material",
  "properties": {
    "volume": 1.0,
    "speed": 1.0,
    "effects": [],
    "keyframes": []
  }
}
```

---

## 完整工作流示例

```python
import requests

API_BASE = "http://localhost:8000/api"

# 1. 创建草稿
draft = requests.post(f"{API_BASE}/draft/create", json={
    "draft_name": "我的视频",
    "width": 1920,
    "height": 1080,
    "fps": 30
}).json()
draft_id = draft["draft_id"]

# 2. 添加轨道
requests.post(f"{API_BASE}/draft/{draft_id}/add_track", json={"track_type": "audio"})
requests.post(f"{API_BASE}/draft/{draft_id}/add_track", json={"track_type": "video"})
requests.post(f"{API_BASE}/draft/{draft_id}/add_track", json={"track_type": "text"})

# 3. 创建音频片段
audio_seg = requests.post(f"{API_BASE}/segment/audio/create", json={
    "material_url": "https://example.com/audio.mp3",
    "target_timerange": {"start": 0, "duration": 5000000},
    "volume": 0.6
}).json()
audio_seg_id = audio_seg["segment_id"]

# 4. 为音频添加淡入淡出
requests.post(f"{API_BASE}/segment/audio/{audio_seg_id}/add_fade", json={
    "in_duration": "1s",
    "out_duration": "0s"
})

# 5. 创建视频片段
video_seg = requests.post(f"{API_BASE}/segment/video/create", json={
    "material_url": "https://example.com/video.mp4",
    "target_timerange": {"start": 0, "duration": 5000000}
}).json()
video_seg_id = video_seg["segment_id"]

# 6. 为视频添加关键帧
requests.post(f"{API_BASE}/segment/video/{video_seg_id}/add_keyframe", json={
    "property": "position_x",
    "time_offset": "2s",
    "value": 0.5
})

# 7. 创建文本片段
text_seg = requests.post(f"{API_BASE}/segment/text/create", json={
    "text_content": "Hello World",
    "target_timerange": {"start": 0, "duration": 3000000}
}).json()
text_seg_id = text_seg["segment_id"]

# 8. 添加片段到草稿
requests.post(f"{API_BASE}/draft/{draft_id}/add_segment", json={"segment_id": audio_seg_id})
requests.post(f"{API_BASE}/draft/{draft_id}/add_segment", json={"segment_id": video_seg_id})
requests.post(f"{API_BASE}/draft/{draft_id}/add_segment", json={"segment_id": text_seg_id})

# 9. 保存草稿
result = requests.post(f"{API_BASE}/draft/{draft_id}/save").json()
print(f"草稿已保存到: {result['draft_path']}")
```

---

## 注意事项

1. **时间单位**：所有时间参数以微秒为单位，或使用字符串格式（如 "1s", "500ms"）
2. **素材下载**：传入 `material_url` 后，后台会自动下载素材到本地，然后调用 pyJianYingDraft
3. **UUID 管理**：所有创建操作返回 UUID，后续操作必须使用相应的 UUID 引用对象
4. **类型区分**：不同类型的 segment 有不同的操作端点，通过路径中的 `{segment_type}` 区分
5. **错误处理**：所有端点在出错时返回标准 HTTP 错误码和错误信息

---

## API 端点总数统计

- **Draft 操作**：6 个端点
- **Segment 创建**：4 个端点
- **AudioSegment 操作**：3 个端点
- **VideoSegment 操作**：8 个端点
- **StickerSegment 操作**：1 个端点
- **TextSegment 操作**：4 个端点
- **辅助端点**：2 个端点

**总计**：28 个核心 API 端点
