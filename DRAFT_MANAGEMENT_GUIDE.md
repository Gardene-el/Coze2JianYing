# Coze剪映草稿管理系统使用指南

本指南介绍如何使用基于UUID的草稿管理系统来创建和导出剪映草稿数据。

## 系统概述

### 核心设计理念

本系统解决了在Coze平台上使用剪映草稿生成时的关键挑战：

1. **避免变量索引干扰**: 使用UUID而不是Coze变量来管理草稿
2. **临时文件管理**: 在`/tmp`目录中安全存储和清理草稿数据
3. **完整参数支持**: 覆盖pyJianYingDraft的所有功能参数
4. **URL资源处理**: 适配Coze平台的网络资源模式

### 工作流程

```
用户输入 → create_draft → UUID → 添加内容工具 → export_drafts → 草稿生成器 → 剪映
```

## 快速开始

### 1. 创建基础草稿

```json
{
  "tool": "create_draft",
  "input": {
    "draft_name": "我的项目",
    "width": 1920,
    "height": 1080,
    "fps": 30
  },
  "output_variable": "my_draft"
}
```

**输出**:
```json
{
  "draft_id": "abc12345-def6-789a-bcde-f123456789ab",
  "success": true,
  "message": "草稿创建成功"
}
```

### 2. 添加内容到草稿

*注意: 这些工具还未实现，这里展示预期的接口*

```json
{
  "tool": "add_video_track",
  "input": {
    "draft_id": "{{my_draft.draft_id}}",
    "video_urls": ["https://example.com/video1.mp4"],
    "filters": ["暖冬"],
    "transitions": ["淡化"]
  }
}
```

### 3. 导出草稿数据

```json
{
  "tool": "export_drafts",
  "input": {
    "draft_ids": "{{my_draft.draft_id}}",
    "remove_temp_files": true
  },
  "output_variable": "exported_data"
}
```

**输出**:
```json
{
  "draft_data": "{完整的JSON数据字符串}",
  "exported_count": 1,
  "success": true,
  "message": "成功导出 1 个草稿; 临时文件已清理"
}
```

## 详细功能说明

### create_draft 工具

#### 支持的参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `draft_name` | string | "Coze剪映项目" | 项目名称 |
| `width` | integer | 1920 | 视频宽度(像素) |
| `height` | integer | 1080 | 视频高度(像素) |
| `fps` | integer | 30 | 帧率 |

#### 常用配置

**4K超清项目**:
```json
{
  "draft_name": "4K宣传片",
  "width": 3840,
  "height": 2160,
  "fps": 60
}
```

**移动端竖版视频**:
```json
{
  "draft_name": "抖音短视频",
  "width": 1080,
  "height": 1920,
  "fps": 30
}
```

**教程录屏**:
```json
{
  "draft_name": "操作教程",
  "width": 1920,
  "height": 1080,
  "fps": 24
}
```

### export_drafts 工具

#### 导出模式

**单个草稿导出**:
```json
{
  "draft_ids": "单个UUID字符串",
  "remove_temp_files": false
}
```

**批量草稿导出**:
```json
{
  "draft_ids": ["UUID1", "UUID2", "UUID3"],
  "remove_temp_files": true
}
```

#### 输出格式

导出的JSON数据包含以下结构：

```json
{
  "format_version": "1.0",
  "export_type": "single_draft | batch_draft",
  "draft_count": 1,
  "drafts": [
    {
      "draft_id": "UUID",
      "project": { /* 项目设置 */ },
      "media_resources": [ /* 媒体资源列表 */ ],
      "tracks": [ /* 轨道配置 */ ],
      "total_duration_ms": 30000,
      "created_timestamp": 1703123456.789,
      "status": "created"
    }
  ]
}
```

## 数据结构详解

### 媒体资源格式

```json
{
  "url": "https://example.com/video.mp4",
  "resource_type": "video|audio|image",
  "duration_ms": 30000,
  "file_size": 25600000,
  "format": "mp4",
  "width": 1920,
  "height": 1080,
  "filename": "video.mp4"
}
```

### 视频段配置

```json
{
  "type": "video",
  "material_url": "https://example.com/video.mp4",
  "time_range": {"start": 0, "end": 30000},
  "transform": {
    "position_x": 0.0,
    "position_y": 0.0,
    "scale_x": 1.0,
    "scale_y": 1.0,
    "rotation": 0.0,
    "opacity": 1.0
  },
  "effects": {
    "filter_type": "暖冬",
    "filter_intensity": 0.8,
    "transition_type": "淡化",
    "transition_duration": 1000
  },
  "keyframes": {
    "position": [],
    "scale": [],
    "rotation": [],
    "opacity": []
  }
}
```

### 文本段配置

```json
{
  "type": "text",
  "content": "标题文字",
  "time_range": {"start": 5000, "end": 10000},
  "style": {
    "font_family": "思源黑体",
    "font_size": 48,
    "color": "#FFFFFF",
    "stroke": {
      "enabled": true,
      "color": "#000000",
      "width": 2
    }
  },
  "animations": {
    "intro": "飞入",
    "outro": "飞出"
  }
}
```

## 支持的效果和参数

### 滤镜类型 (200+种)

- **基础调色**: 暖冬、冷蓝、清晰、增色、去灰等
- **复古风格**: 复古工业、胶片、老电影等
- **现代风格**: 赛博朋克、ins暗、抖音风等
- **专业调色**: 好莱坞、电影级、商业等

### 转场效果 (100+种)

- **基础转场**: 淡化、推移、擦除、旋转等
- **创意转场**: 星光、水波、燃烧、故障等
- **动感转场**: 爆闪、震动、弹跳、翻转等

### 文本动画

- **入场**: 飞入、淡入、弹出、缩放等
- **出场**: 飞出、淡出、消失、收缩等
- **循环**: 闪烁、摇摆、跳动、旋转等

## 最佳实践

### 1. 项目规划

- 确定目标平台和分辨率
- 选择合适的帧率和质量
- 预估项目总时长

### 2. 资源管理

- 使用稳定的网络链接
- 确保链接有效期足够长
- 提供准确的媒体元数据

### 3. 性能优化

- 单次操作避免创建过多草稿
- 及时导出和清理临时文件
- 合理使用批量导出功能

### 4. 错误处理

- 检查所有工具的`success`字段
- 处理部分成功的情况
- 保存重要的草稿ID用于重试

## 故障排除

### 常见问题

**Q: "参数验证失败"错误**
A: 检查分辨率、帧率、质量等参数是否在有效范围内

**Q: "草稿文件夹不存在"错误**
A: 确认draft_id正确，检查是否已被清理

**Q: "UUID格式错误"**
A: 确保传递的是有效的UUID字符串

**Q: 导出的JSON数据过大**
A: 考虑分批导出或减少复杂的配置

### 调试技巧

1. 使用简单参数测试基本功能
2. 检查`/tmp`目录中的文件结构
3. 验证JSON输出的格式正确性
4. 监控内存和存储使用情况

## 完整工作流示例

```json
{
  "workflow": "video_production",
  "steps": [
    {
      "name": "创建项目",
      "tool": "create_draft",
      "input": {
        "draft_name": "{{user.project_name}}",
        "width": 1920,
        "height": 1080
      },
      "output": "project"
    },
    {
      "name": "添加视频",
      "tool": "add_video_track",
      "input": {
        "draft_id": "{{project.draft_id}}",
        "video_urls": "{{user.video_list}}"
      }
    },
    {
      "name": "添加音频",
      "tool": "add_audio_track", 
      "input": {
        "draft_id": "{{project.draft_id}}",
        "audio_urls": "{{user.audio_list}}"
      }
    },
    {
      "name": "添加文字",
      "tool": "add_text_track",
      "input": {
        "draft_id": "{{project.draft_id}}",
        "texts": "{{user.subtitle_list}}"
      }
    },
    {
      "name": "导出数据",
      "tool": "export_drafts",
      "input": {
        "draft_ids": "{{project.draft_id}}",
        "remove_temp_files": true
      },
      "output": "final_draft"
    }
  ]
}
```

## 下一步开发

当前已实现的是草稿管理的基础架构。后续需要开发的工具包括：

- `add_video_track` - 添加视频轨道
- `add_audio_track` - 添加音频轨道  
- `add_text_track` - 添加文本轨道
- `add_effects` - 添加特效
- `modify_timeline` - 修改时间轴

这些工具都将使用相同的UUID系统，确保整个工作流的一致性和可靠性。

---

通过这个草稿管理系统，你可以在Coze平台上高效地创建和管理剪映草稿，最终生成专业的视频内容。