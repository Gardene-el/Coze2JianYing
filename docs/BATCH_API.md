# 批量片段 API 文档

批量操作 API 提供了与 Coze 插件工具接口保持一致的批量片段处理功能。

## API 端点列表

所有端点都使用 `POST` 方法，基础路径为 `/api/batch/`。

### 1. 批量添加音频 (`/add_audios`)

批量添加音频片段到草稿，创建新的音频轨道。

**请求示例:**
```json
{
  "draft_id": "12345678-1234-1234-1234-123456789012",
  "audio_infos": [
    "{\"audio_url\": \"https://example.com/audio1.mp3\", \"start\": 0, \"end\": 5000, \"volume\": 0.8}",
    "{\"audio_url\": \"https://example.com/audio2.mp3\", \"start\": 5000, \"end\": 10000}"
  ]
}
```

**响应示例:**
```json
{
  "success": true,
  "message": "成功添加 2 个音频片段",
  "error_code": "",
  "segment_ids": [
    "uuid-1",
    "uuid-2"
  ]
}
```

**音频信息字段:**
- `audio_url` (必需): 音频文件 URL
- `start` (必需): 开始时间（毫秒）
- `end` (必需): 结束时间（毫秒）
- `volume` (可选): 音量 (0.0-1.0)
- `fade_in` (可选): 淡入时长（毫秒）
- `fade_out` (可选): 淡出时长（毫秒）
- `speed` (可选): 播放速度
- `change_pitch` (可选): 是否跟随变速改变音调

---

### 2. 批量添加字幕 (`/add_captions`)

批量添加字幕片段到草稿，创建新的文本轨道。

**请求示例:**
```json
{
  "draft_id": "12345678-1234-1234-1234-123456789012",
  "caption_infos": [
    "{\"content\": \"第一句字幕\", \"start\": 0, \"end\": 3000, \"font_size\": 48}",
    "{\"content\": \"第二句字幕\", \"start\": 3000, \"end\": 6000}"
  ]
}
```

**字幕信息字段:**
- `content` (必需): 字幕文本内容
- `start` (必需): 开始时间（毫秒）
- `end` (必需): 结束时间（毫秒）
- `position_x` (可选): X 位置 (0.0-1.0)
- `position_y` (可选): Y 位置 (0.0-1.0)
- `font_family` (可选): 字体
- `font_size` (可选): 字体大小
- `color` (可选): 颜色 (#RRGGBB)
- `stroke_enabled` (可选): 是否启用描边
- `shadow_enabled` (可选): 是否启用阴影

---

### 3. 批量添加特效 (`/add_effects`)

批量添加特效片段到草稿，创建新的特效轨道。

**请求示例:**
```json
{
  "draft_id": "12345678-1234-1234-1234-123456789012",
  "effect_infos": [
    "{\"effect_type\": \"blur\", \"start\": 0, \"end\": 2000, \"params\": [50.0]}",
    "{\"effect_type\": \"glow\", \"start\": 2000, \"end\": 4000}"
  ]
}
```

**特效信息字段:**
- `effect_type` (必需): 特效类型
- `start` (必需): 开始时间（毫秒）
- `end` (必需): 结束时间（毫秒）
- `params` (可选): 特效参数列表

---

### 4. 批量添加图片 (`/add_images`)

批量添加图片片段到草稿，创建新的视频轨道（图片作为静态视频）。

**请求示例:**
```json
{
  "draft_id": "12345678-1234-1234-1234-123456789012",
  "image_infos": [
    "{\"image_url\": \"https://example.com/img1.jpg\", \"start\": 0, \"end\": 3000}",
    "{\"image_url\": \"https://example.com/img2.jpg\", \"start\": 3000, \"end\": 6000}"
  ]
}
```

**图片信息字段:**
- `image_url` (必需): 图片文件 URL
- `start` (必需): 开始时间（毫秒）
- `end` (必需): 结束时间（毫秒）
- `position_x` (可选): X 位置
- `position_y` (可选): Y 位置
- `scale_x` (可选): X 缩放
- `scale_y` (可选): Y 缩放
- `rotation` (可选): 旋转角度
- `opacity` (可选): 不透明度 (0.0-1.0)

---

### 5. 批量添加视频 (`/add_videos`)

批量添加视频片段到草稿，创建新的视频轨道。

**请求示例:**
```json
{
  "draft_id": "12345678-1234-1234-1234-123456789012",
  "video_infos": [
    "{\"video_url\": \"https://example.com/video1.mp4\", \"start\": 0, \"end\": 10000}",
    "{\"video_url\": \"https://example.com/video2.mp4\", \"start\": 10000, \"end\": 20000}"
  ]
}
```

**视频信息字段:**
- `video_url` (必需): 视频文件 URL
- `start` (必需): 开始时间（毫秒）
- `end` (必需): 结束时间（毫秒）
- `material_start` (可选): 素材起始时间（毫秒）
- `material_end` (可选): 素材结束时间（毫秒）
- `position_x`, `position_y` (可选): 位置
- `scale_x`, `scale_y` (可选): 缩放
- `rotation` (可选): 旋转角度
- `opacity` (可选): 不透明度
- `speed` (可选): 播放速度
- `filter_type` (可选): 滤镜类型
- `transition_type` (可选): 转场类型

---

### 6. 添加贴纸 (`/add_sticker`)

添加贴纸片段到草稿的贴纸轨道。

**请求示例:**
```json
{
  "draft_id": "12345678-1234-1234-1234-123456789012",
  "sticker_info": "{\"sticker_url\": \"https://example.com/sticker.png\", \"start\": 0, \"end\": 5000}"
}
```

**贴纸信息字段:**
- `sticker_url` (必需): 贴纸文件 URL
- `start` (必需): 开始时间（毫秒）
- `end` (必需): 结束时间（毫秒）
- `position_x` (可选): X 位置
- `position_y` (可选): Y 位置
- `scale` (可选): 缩放
- `rotation` (可选): 旋转角度

---

### 7. 添加关键帧 (`/add_keyframes`)

向片段添加关键帧，用于精确控制属性随时间变化。

**请求示例:**
```json
{
  "segment_id": "12345678-1234-1234-1234-123456789012",
  "keyframe_infos": [
    {
      "property": "position_x",
      "time_offset": 0,
      "value": 0.0
    },
    {
      "property": "position_x",
      "time_offset": 2000,
      "value": 0.5
    }
  ]
}
```

**关键帧信息字段:**
- `property` (必需): 属性名称（position_x, position_y, scale, rotation, opacity 等）
- `time_offset` (必需): 时间偏移量（毫秒）
- `value` (必需): 属性值

---

### 8. 添加蒙版 (`/add_masks`)

向视频片段添加蒙版效果。

**请求示例:**
```json
{
  "segment_id": "12345678-1234-1234-1234-123456789012",
  "mask_info": {
    "mask_type": "circle",
    "center_x": 0.5,
    "center_y": 0.5,
    "size": 0.5,
    "feather": 10.0
  }
}
```

**蒙版信息字段:**
- `mask_type` (必需): 蒙版类型（circle, rectangle, heart 等）
- `center_x` (可选): 中心点 X 坐标
- `center_y` (可选): 中心点 Y 坐标
- `size` (可选): 主要尺寸
- `rotation` (可选): 旋转角度
- `feather` (可选): 羽化程度
- `invert` (可选): 是否反转蒙版

---

## 统一响应格式

所有 API 都返回统一的响应格式：

```json
{
  "success": true,
  "message": "操作结果消息",
  "error_code": "错误代码（成功时为空）",
  "segment_ids": ["生成的片段 UUID 列表"],
  "details": {}
}
```

### 错误处理

当操作失败时，`success` 仍为 `true`（为了与 Coze 插件保持一致），但会包含错误信息：

```json
{
  "success": true,
  "message": "操作失败的原因",
  "error_code": "DRAFT_NOT_FOUND",
  "segment_ids": [],
  "details": {
    "resource_id": "draft-id",
    "reason": "详细错误原因"
  }
}
```

## 与 Coze 插件工具的兼容性

这些 API 端点的设计与 Coze 插件工具接口保持完全一致：

1. **命名一致**: API 端点名称与 Coze 工具函数名称相同
2. **参数格式**: 接受相同的参数结构（JSON 字符串列表）
3. **响应格式**: 返回相同的响应结构
4. **行为一致**: 实现相同的业务逻辑（批量创建轨道和片段）

## 使用场景

### 场景 1: Coze 工作流直接调用

Coze 工作流可以直接调用这些 API 端点，通过 API 方式而非手动粘贴来传输数据。

### 场景 2: 批量处理

需要一次性添加多个片段时，使用批量 API 比单独创建片段更高效。

### 场景 3: 自动化脚本

编写自动化脚本时，可以使用这些 API 批量处理媒体资源。

## 注意事项

1. **JSON 字符串格式**: `audio_infos`, `caption_infos` 等字段接受 JSON 字符串列表，需要对每个对象进行 JSON 编码
2. **时间单位**: 所有时间参数使用毫秒为单位
3. **URL 格式**: 所有素材 URL 应该是可访问的完整 HTTP/HTTPS 地址
4. **UUID 格式**: draft_id 和 segment_id 必须是有效的 UUID 格式
5. **轨道创建**: 每次批量添加都会创建一个新轨道，而不是添加到现有轨道
