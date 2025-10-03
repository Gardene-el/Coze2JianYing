# Draft Generator Interface 快速参考指南

本文档为 pyJianYingDraftImporter 项目开发者提供快速参考。

---

## 📋 核心转换清单

### 1. URL → 本地文件路径

```python
# 必须先下载
import requests

def download_media(url: str, filename: str) -> str:
    local_path = f"/tmp/downloads/{filename}"
    response = requests.get(url, stream=True)
    with open(local_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return local_path
```

### 2. 时间范围格式转换

```python
from pyJianYingDraft import Timerange

# Draft Generator Interface: {"start": 5000, "end": 15000}
# pyJianYingDraft: Timerange(start=5000, duration=10000)

def convert_timerange(time_range: dict) -> Timerange:
    start = time_range["start"]
    duration = time_range["end"] - time_range["start"]
    return Timerange(start=start, duration=duration)
```

### 3. 裁剪设置转换

```python
from pyJianYingDraft import CropSettings

# Draft Generator Interface: {left, top, right, bottom}
# pyJianYingDraft: 四角点坐标

def convert_crop(crop: dict) -> CropSettings:
    if not crop.get("enabled"):
        return None
    
    return CropSettings(
        upper_left_x=crop["left"],
        upper_left_y=crop["top"],
        upper_right_x=crop["right"],
        upper_right_y=crop["top"],
        lower_left_x=crop["left"],
        lower_left_y=crop["bottom"],
        lower_right_x=crop["right"],
        lower_right_y=crop["bottom"]
    )
```

### 4. 变换设置转换

```python
from pyJianYingDraft import ClipSettings

def convert_transform(transform: dict) -> ClipSettings:
    return ClipSettings(
        alpha=transform.get("opacity", 1.0),
        rotation=transform.get("rotation", 0.0),
        scale_x=transform.get("scale_x", 1.0),
        scale_y=transform.get("scale_y", 1.0),
        transform_x=transform.get("position_x", 0.0),
        transform_y=transform.get("position_y", 0.0)
    )
```

### 5. 滤镜强度转换

```python
# Draft Generator Interface: 0.0 - 1.0
# pyJianYingDraft: 0 - 100

intensity_100 = filter_intensity * 100
```

---

## 🗂️ 参数快速对照表

| Draft Generator | pyJianYingDraft | 转换 |
|----------------|-----------------|------|
| `material_url` | `VideoMaterial(path)` | 下载 URL |
| `time_range{start, end}` | `Timerange(start, duration)` | duration = end - start |
| `position_x/y` | `transform_x/y` | 直接对应 |
| `opacity` | `alpha` | 直接对应 |
| `crop{left, top, right, bottom}` | `CropSettings(四角点)` | 见上方转换函数 |
| `filter_intensity` (0-1) | `intensity` (0-100) | × 100 |

---

## 🔧 核心 API 调用流程

### 完整流程示例

```python
from pyJianYingDraft import DraftFolder, VideoMaterial, VideoSegment

# 1. 创建 DraftFolder
draft_folder = DraftFolder("/path/to/JianyingPro/Drafts")

# 2. 创建草稿
script_file = draft_folder.create_draft(
    draft_name="我的项目",
    width=1920,
    height=1080,
    fps=30,
    allow_replace=True
)

# 3. 下载并添加媒体素材
video_path = download_media(video_url, "video.mp4")
material = VideoMaterial(video_path, material_name="video.mp4")
script_file.add_material(material)

# 4. 创建视频段
video_segment = VideoSegment(
    material=material,
    target_timerange=Timerange(start=0, duration=30000),
    speed=1.0,
    volume=1.0,
    clip_settings=clip_settings
)

# 5. 添加段到脚本
script_file.add_segment(video_segment)

# 6. 添加滤镜（可选）
from pyJianYingDraft import FilterType
script_file.add_filter(
    filter_meta=FilterType.暖冬,
    t_range=Timerange(start=0, duration=30000),
    intensity=80.0
)

# 7. 保存草稿
script_file.save()
```

---

## ⚠️ 常见陷阱

### 1. Timerange 参数顺序

```python
# ❌ 错误
Timerange(0, 30000)  # 这是 (start, duration) 不是 (start, end)!

# ✅ 正确
Timerange(start=0, duration=30000)
```

### 2. Material 必须先 add_material

```python
# ❌ 错误
segment = VideoSegment(material=video_path, ...)  # 可以用 path
script_file.add_segment(segment)  # 但会找不到 material!

# ✅ 正确
material = VideoMaterial(video_path)
script_file.add_material(material)  # 先添加 material
segment = VideoSegment(material=material, ...)
script_file.add_segment(segment)
```

### 3. 裁剪必须是四角点格式

```python
# ❌ 错误 - CropSettings 不接受 box 参数
crop = CropSettings(left=0.1, right=0.9, top=0.1, bottom=0.9)

# ✅ 正确 - 必须转换为四角点
crop = CropSettings(
    upper_left_x=0.1, upper_left_y=0.1,
    upper_right_x=0.9, upper_right_y=0.1,
    lower_left_x=0.1, lower_left_y=0.9,
    lower_right_x=0.9, lower_right_y=0.9
)
```

### 4. 滤镜强度范围

```python
# ❌ 错误 - pyJianYingDraft 期望 0-100
script_file.add_filter(filter_meta=FilterType.暖冬, intensity=0.8)

# ✅ 正确
script_file.add_filter(filter_meta=FilterType.暖冬, intensity=80.0)
```

---

## 📊 数据完整性检查清单

在处理 Draft Generator Interface JSON 时，确保：

- [ ] 所有 URL 都能成功下载
- [ ] 时间范围没有负值或 end < start
- [ ] 所有引用的 material_url 都在 media_resources 中
- [ ] 滤镜类型名称可以映射到 FilterType 枚举
- [ ] 特效类型名称可以映射到 EffectType 枚举
- [ ] 转场类型名称可以映射到 TransitionType 枚举
- [ ] 参数值在合理范围内（如 opacity 在 0-1）

---

## 🎯 快速测试代码

```python
def test_basic_draft():
    """快速测试草稿创建流程"""
    import tempfile
    from pyJianYingDraft import DraftFolder
    
    # 使用临时目录测试
    temp_dir = tempfile.mkdtemp()
    
    draft_folder = DraftFolder(temp_dir)
    script_file = draft_folder.create_draft(
        draft_name="test_draft",
        width=1920,
        height=1080,
        fps=30,
        allow_replace=True
    )
    
    script_file.save()
    print(f"✅ 测试成功！草稿已保存到: {temp_dir}/test_draft")
    
    return temp_dir

# 运行测试
test_basic_draft()
```

---

## 📚 延伸阅读

- **详细实现指南**: `data_structures/draft_generator_interface/README.md`
- **完整性分析**: `DRAFT_INTERFACE_ANALYSIS.md`
- **参数审计报告**: `AUDIT_REPORT.md`
- **pyJianYingDraft 文档**: https://github.com/GuanYixuan/pyJianYingDraft

---

## 🆘 疑难解答

### Q: 如何处理图片素材？

A: 图片不需要创建 Material 对象，直接在 VideoSegment 中使用本地路径即可：
```python
image_segment = VideoSegment(
    material="/path/to/image.jpg",  # 直接使用路径
    target_timerange=Timerange(start=0, duration=5000),
    ...
)
```

### Q: 音频的 fade_in/fade_out 如何实现？

A: pyJianYingDraft 的 AudioSegment 不直接支持 fade 参数。需要使用音量关键帧实现：
```python
# 这是一个需要深入研究的高级功能
# 建议先实现基础功能，fade 功能可以后续添加
```

### Q: 关键帧动画如何实现？

A: Draft Generator Interface 提供了关键帧数据结构，但 pyJianYingDraft 的关键帧 API 需要详细研究。建议参考 pyJianYingDraft 的示例代码和测试用例。

---

**最后更新**: 2024年  
**适用版本**: pyJianYingDraft >= 0.2.5
