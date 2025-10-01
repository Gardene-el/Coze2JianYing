# ADD_VIDEOS 和 MAKE_VIDEO_INFO 实现总结

## 实现概述

根据 Issue 的需求，参考 `add_images` 和 `make_image_info` 的设计过程（包括 PR #17、#25 和 Issue #16、#24），成功实现了 `add_videos` 和 `make_video_info` 工具。

## 实现的内容

### 1. 新增 `make_video_info` 工具 (`tools/make_video_info/`)

#### 功能
- 生成单个视频配置的 JSON 字符串表示
- 这是 `add_videos` 工具的辅助函数
- 用于在 Coze 工作流中动态构建视频配置

#### 支持的参数
**必需参数（3个）：**
- `video_url`: 视频 URL
- `start`: 开始时间（毫秒）
- `end`: 结束时间（毫秒）

**可选参数（24个）：**
- **素材范围**（视频特有）: `material_start`, `material_end`
- **速度控制**（视频特有）: `speed` (0.5-2.0), `reverse`
- **变换**: `position_x`, `position_y`, `scale_x`, `scale_y`, `rotation`, `opacity`
- **裁剪**: `crop_enabled`, `crop_left`, `crop_top`, `crop_right`, `crop_bottom`
- **效果**: `filter_type`, `filter_intensity`, `transition_type`, `transition_duration`
- **背景**: `background_blur`, `background_color`

#### 输出示例
```json
{"video_url":"https://example.com/video.mp4","start":0,"end":5000,"material_start":1000,"material_end":6000,"speed":1.5}
```

#### 关键特性
1. **参数优化**: 只输出非默认值，保持字符串紧凑
2. **完整验证**: 时间范围、速度范围、素材范围等全面验证
3. **视频特有功能**: material_range、speed、reverse
4. **中文支持**: 正确处理中文滤镜名称

### 2. 新增 `add_videos` 工具 (`tools/add_videos/`)

#### 功能
- 向现有草稿添加视频轨道和视频片段
- 每次调用创建一个新的视频轨道
- 支持多种输入格式

#### 支持的输入格式

**格式1: 数组对象（推荐用于静态配置）**
```json
[
  {
    "video_url": "https://example.com/video.mp4",
    "start": 0,
    "end": 5000,
    "speed": 1.5
  }
]
```

**格式2: 数组字符串（推荐用于动态配置）**
```json
[
  "{\"video_url\":\"https://example.com/video1.mp4\",\"start\":0,\"end\":5000}",
  "{\"video_url\":\"https://example.com/video2.mp4\",\"start\":5000,\"end\":10000,\"speed\":1.5}"
]
```

**格式3: JSON字符串**
```json
"[{\"video_url\":\"https://example.com/video.mp4\",\"start\":0,\"end\":5000}]"
```

#### 关键特性
1. **灵活输入解析**: 自动识别数组对象、数组字符串、JSON字符串
2. **完整数据结构**: 遵循 DraftConfig 的数据结构模式
3. **视频特有参数**: 正确处理 material_range、speed、reverse
4. **向后兼容**: 100% 兼容现有的输入格式

### 3. 完整的工作流示例

```python
# 步骤 1: 创建草稿
draft_result = create_draft(draft_name="视频项目", width=1920, height=1080)
draft_id = draft_result.draft_id

# 步骤 2: 使用 make_video_info 生成视频配置字符串
video1 = make_video_info(
    video_url="https://example.com/video1.mp4",
    start=0,
    end=5000,
    speed=1.5
)

video2 = make_video_info(
    video_url="https://example.com/video2.mp4",
    start=5000,
    end=10000,
    material_start=2000,
    material_end=7000
)

# 步骤 3: 收集到数组
video_infos_array = [
    video1.video_info_string,
    video2.video_info_string
]

# 步骤 4: 添加到草稿
add_videos(
    draft_id=draft_id,
    video_infos=video_infos_array
)
```

## 测试覆盖

### 新增测试文件

**1. `tests/test_make_video_info.py`**
- ✅ 基本功能测试（最小参数、完整参数、默认值排除）
- ✅ 视频特有功能测试（material_range、speed、reverse）
- ✅ 错误处理测试（缺少参数、无效时间范围、无效速度等）
- ✅ 中文字符支持测试
- **测试结果**: 3/3 测试套件通过

**2. `tests/test_add_videos.py`**
- ✅ 基本功能测试（添加视频、验证配置）
- ✅ 数组字符串格式测试（新格式支持、向后兼容）
- ✅ 视频特有参数测试（material_range、speed、reverse、效果）
- ✅ 集成测试（make_video_info → add_videos 完整流程）
- ✅ 错误处理测试（无效 UUID、缺少字段等）
- **测试结果**: 5/5 测试套件通过

### 示例文件

**1. `examples/make_video_info_demo.py`**
- 演示 6 个场景：基本用法、视频特有功能、完整配置、工作流、错误处理、与图片工具对比

**2. `examples/add_videos_demo.py`**
- 演示 8 个场景：输入格式、视频裁剪、速度控制、画中画、效果、完整工作流、多轨道、错误处理

## 视频工具与图片工具的差异

### 视频特有功能 (Images不支持)

| 功能 | 说明 | 参数 |
|------|------|------|
| 素材范围 | 裁剪源视频的特定片段 | `material_start`, `material_end` |
| 速度控制 | 调整播放速度 | `speed` (0.5-2.0) |
| 反向播放 | 倒放视频 | `reverse` (boolean) |

### 图片特有功能 (Videos不支持)

| 功能 | 说明 | 参数 |
|------|------|------|
| 入场动画 | 图片出现时的动画效果 | `in_animation`, `in_animation_duration` |
| 出场动画 | 图片消失时的动画效果 | `outro_animation`, `outro_animation_duration` |
| 适配模式 | 控制图片如何适配画布 | `fit_mode` ("fit", "fill", "stretch") |

### 共享功能

| 功能类别 | 参数 |
|---------|------|
| 变换 | `position_x`, `position_y`, `scale_x`, `scale_y`, `rotation`, `opacity` |
| 裁剪 | `crop_enabled`, `crop_left`, `crop_top`, `crop_right`, `crop_bottom` |
| 效果 | `filter_type`, `filter_intensity`, `transition_type`, `transition_duration` |
| 背景 | `background_blur`, `background_color` |

## 文档更新

### 新增文档
1. **`tools/make_video_info/README.md`** - 完整的工具文档（300+ 行）
   - 功能描述和使用场景
   - 完整的参数说明
   - 多个使用示例
   - 与图片工具的对比
   - 错误处理说明

2. **`tools/add_videos/README.md`** - 完整的工具文档（400+ 行）
   - 功能描述
   - 输入格式说明（支持 3 种格式）
   - 完整的参数列表
   - 多个使用示例（基本用法、裁剪、速度控制、画中画等）
   - 最佳实践
   - 常见问题解答

3. **`ADD_VIDEOS_UPDATE.md`** - 本文档，实现总结

## 向后兼容性

✅ **100% 向后兼容**
- 所有原有的 add_images 和 make_image_info 功能继续正常工作
- 数据结构与现有工具保持一致
- 测试验证了所有现有工具仍然正常运行

## 在 Coze 工作流中的应用

### 适用场景

**动态配置场景** (推荐使用 make_video_info + add_videos):
```
1. [make_video_info 节点1] → 生成视频1配置
2. [make_video_info 节点2] → 生成视频2配置
3. [数组收集节点] → 组合成数组
4. [add_videos 节点] → 添加到草稿
```

**静态配置场景** (直接使用 add_videos):
```
1. [add_videos 节点] → 直接传入数组对象
```

## 关键技术点

### 1. 灵活的输入解析
通过检查数组第一个元素的类型来区分数组字符串和数组对象：
```python
if isinstance(video_infos_input, list):
    if video_infos_input and isinstance(video_infos_input[0], str):
        # 数组字符串格式
        parsed_infos = [json.loads(s) for s in video_infos_input]
    else:
        # 数组对象格式
        video_infos = video_infos_input
```

### 2. 视频特有参数处理
正确处理 `material_range`、`speed` 和 `reverse`：
```python
# 在创建片段时
segment = {
    "material_range": {
        "start": info['material_start'],
        "end": info['material_end']
    } if 'material_start' in info else None,
    "speed": {
        "speed": info.get('speed', 1.0),
        "reverse": info.get('reverse', False)
    }
}
```

### 3. 参数优化
只输出非默认值，保持 JSON 字符串紧凑：
```python
if args.input.speed != 1.0:
    video_info["speed"] = args.input.speed
if args.input.reverse:
    video_info["reverse"] = args.input.reverse
```

### 4. 完整的参数验证
- 时间范围验证（start >= 0, end > start）
- 素材范围验证（material_start >= 0, material_end > material_start）
- 速度范围验证（0.5 <= speed <= 2.0）
- 素材范围配对验证（material_start 和 material_end 必须同时提供）

### 5. 中文支持
正确处理中文字符（滤镜名称、转场类型等）：
```python
video_info_string = json.dumps(video_info, ensure_ascii=False, separators=(',', ':'))
```

## 文件变更清单

### 新增文件
- `tools/make_video_info/handler.py` (235 行)
- `tools/make_video_info/README.md` (300+ 行)
- `tools/add_videos/handler.py` (450 行)
- `tools/add_videos/README.md` (400+ 行)
- `tests/test_make_video_info.py` (300 行)
- `tests/test_add_videos.py` (400 行)
- `examples/make_video_info_demo.py` (300 行)
- `examples/add_videos_demo.py` (400 行)
- `ADD_VIDEOS_UPDATE.md` (本文档)

### 总代码量
- 工具代码: ~700 行
- 测试代码: ~700 行
- 示例代码: ~700 行
- 文档: ~1000 行
- **总计: ~3100 行**

## 使用建议

### 何时使用 make_video_info + add_videos
✅ 推荐场景：
- Coze 工作流中需要动态生成视频配置
- 需要在多个节点之间传递视频信息
- 每个视频的配置来自不同的数据源
- 需要对每个视频进行独立的参数处理

### 何时直接使用 add_videos
✅ 推荐场景：
- 静态配置，视频信息固定
- 在 Python 代码中直接构建配置
- 不需要序列化传递的场景
- 快速测试和原型开发

### 视频编辑最佳实践

**1. 使用 material_range 优化视频**
```python
# 只使用需要的片段，而不是整个视频
{
    "video_url": "https://example.com/30s_video.mp4",
    "start": 0,
    "end": 5000,
    "material_start": 10000,  # 从源视频的第 10 秒开始
    "material_end": 15000     # 到第 15 秒结束
}
```

**2. 合理使用速度控制**
```python
# 快速浏览 - 2倍速
{"speed": 2.0}

# 强调重要时刻 - 慢动作
{"speed": 0.5}

# 创意倒放效果
{"speed": 0.5, "reverse": True}
```

**3. 创建画中画效果**
```python
# 第一次调用 - 主视频（全屏）
add_videos(draft_id, [{
    "video_url": "main.mp4",
    "start": 0,
    "end": 10000
}])

# 第二次调用 - 小窗口视频
add_videos(draft_id, [{
    "video_url": "pip.mp4",
    "start": 2000,
    "end": 8000,
    "scale_x": 0.3,
    "scale_y": 0.3,
    "position_x": 0.6,
    "position_y": -0.6
}])
```

## 与其他工具的集成

### 完整的视频制作流程

```python
# 1. 创建项目
draft = create_draft(name="视频项目", width=1920, height=1080)

# 2. 添加视频轨道
add_videos(draft.draft_id, video_infos)

# 3. 添加音频轨道
add_audios(draft.draft_id, audio_infos)

# 4. 添加图片/字幕轨道
add_images(draft.draft_id, image_infos)

# 5. 导出配置
export_drafts(draft_ids=[draft.draft_id])
```

## 性能考虑

- 建议单次调用视频数量控制在 20 个以内
- 过长的视频或过多的效果可能影响播放流畅度
- material_range 可以减少需要处理的视频数据量

## 参考资料

### 设计参考
- PR #17: https://github.com/Gardene-el/CozeJianYingAssistent/pull/17
- PR #25: https://github.com/Gardene-el/CozeJianYingAssistent/pull/25
- Issue #16: https://github.com/Gardene-el/CozeJianYingAssistent/issues/16
- Issue #24: https://github.com/Gardene-el/CozeJianYingAssistent/issues/24

### 技术文档
- `data_structures/draft_generator_interface/models.py` - VideoSegmentConfig 定义
- `tools/add_images/` - 图片工具参考实现
- `tools/make_image_info/` - 图片配置工具参考实现
- `MAKE_IMAGE_INFO_UPDATE.md` - 图片工具实现总结

## 总结

成功实现了功能完整、文档齐全、测试充分的 `add_videos` 和 `make_video_info` 工具，完全遵循了项目现有的设计模式和最佳实践。所有测试通过，向后兼容性得到保证，为 Coze 平台提供了强大的视频处理能力。
