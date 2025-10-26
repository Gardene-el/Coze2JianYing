# 素材管理器（MaterialManager）功能说明

## ✅ 回答你的问题

### Q: 在当前 pyJianYingDraft 的设计下，这样的 utils 函数可行吗？

**答案：完全可行！✅**

## 📋 设计方案

### 文件结构

```
草稿根目录/
└── 我的项目/                      # 草稿文件夹（草稿名称）
    ├── Assets/                    # 素材文件夹（MaterialManager 创建）
    │   ├── video1.mp4            # 从 URL 下载的视频
    │   ├── audio1.mp3            # 从 URL 下载的音频
    │   └── image1.jpg            # 从 URL 下载的图片
    ├── draft_content.json        # 草稿配置（pyJianYingDraft 生成）
    └── draft_meta_info.json      # 草稿元信息（pyJianYingDraft 生成）
```

### 核心逻辑

1. **自动创建 Assets 文件夹**

   ```python
   # MaterialManager 初始化时
   assets_path = draft_path / "Assets"
   assets_path.mkdir(parents=True, exist_ok=True)
   ```

2. **下载素材到 Assets**

   ```python
   # 下载到: {草稿文件夹}/Assets/{文件名}
   target_path = assets_path / filename
   ```

3. **创建 Material 对象**
   ```python
   # pyJianYingDraft 只需要本地路径
   video_material = draft.VideoMaterial(str(target_path))
   ```

## 🎯 为什么可行？

### 1. pyJianYingDraft 的设计支持

- **Material 只需要路径**：`VideoMaterial(path)` 只需要文件存在即可
- **不限制素材位置**：可以是任何本地路径
- **草稿文件夹结构灵活**：pyJianYingDraft 只关心 `draft_content.json`

### 2. 不干扰现有功能

- Assets 文件夹是额外的，不影响 pyJianYingDraft
- 剪映打开草稿时只读取 JSON 文件中的 Material 路径
- 只要文件存在，剪映就能正常加载

### 3. 便于管理

- 每个草稿有自己的 Assets 文件夹
- 素材与草稿在同一目录，便于备份和移动
- 避免素材散落在各处

## 📝 实现细节

### 已实现的文件

**`src/utils/material_manager.py`**

- `MaterialManager` 类 - 核心素材管理器
- `create_material_manager()` - 便捷创建函数

### 主要功能

```python
class MaterialManager:
    def __init__(self, draft_folder_path, draft_name):
        """
        初始化时自动创建 Assets 文件夹
        路径: {draft_folder_path}/{draft_name}/Assets/
        """

    def create_material(self, url) -> Material:
        """从URL下载并创建Material对象"""

    def create_video_material(self, url) -> VideoMaterial:
        """下载视频并创建VideoMaterial"""

    def create_audio_material(self, url) -> AudioMaterial:
        """下载音频并创建AudioMaterial"""

    def batch_create_materials(self, urls) -> Dict[str, Material]:
        """批量下载素材"""

    # ... 更多管理功能
```

## 🚀 使用示例

### 基本使用

```python
import pyJianYingDraft as draft
from src.utils.material_manager import create_material_manager

# 1. 创建草稿
draft_folder = draft.DraftFolder("C:/path/to/drafts")
script = draft_folder.create_draft("我的项目", 1920, 1080, allow_replace=True)

# 2. 创建素材管理器
# 此时会自动创建: C:/path/to/drafts/我的项目/Assets/
manager = create_material_manager(draft_folder, "我的项目")

# 3. 下载素材
video_url = "https://example.com/video.mp4"
video_material = manager.create_video_material(video_url)
# 文件下载到: C:/path/to/drafts/我的项目/Assets/video.mp4
# 返回: VideoMaterial("C:/path/to/drafts/我的项目/Assets/video.mp4")

# 4. 使用 Material 创建 Segment
from pyJianYingDraft import VideoSegment, Timerange
segment = VideoSegment(
    material=video_material,  # 使用下载的素材
    target_timerange=Timerange(0, 5000)
)

# 5. 添加到草稿
script.add_segment(segment)
script.save()
```

### 与 Converter 配合使用

```python
from src.utils.material_manager import create_material_manager
from src.utils.converter import DraftInterfaceConverter

# Draft Interface 配置
draft_config = {
    "tracks": [{
        "track_type": "video",
        "segments": [{
            "type": "video",
            "material_url": "https://example.com/video.mp4",
            "time_range": {"start": 0, "end": 5000},
            "transform": {...}
        }]
    }]
}

# 1. 创建草稿和管理器
draft_folder = draft.DraftFolder(output_folder)
script = draft_folder.create_draft("项目", 1920, 1080, allow_replace=True)
manager = create_material_manager(draft_folder, "项目")

# 2. 收集所有URL并批量下载
urls = [seg["material_url"] for track in draft_config["tracks"]
        for seg in track["segments"] if "material_url" in seg]
material_map = manager.batch_create_materials(urls)

# 3. 使用转换器转换
converter = DraftInterfaceConverter()
script = converter.convert_draft_config_to_script(
    draft_config,
    script,
    material_map  # URL → Material 映射
)

# 4. 保存
script.save()
```

## ✨ 关键特性

### 1. 自动创建文件夹 ✅

```python
# 初始化时自动创建，无需手动
manager = MaterialManager(draft_folder_path, draft_name)
# → Assets/ 文件夹已创建
```

### 2. 智能类型识别 ✅

```python
# 根据文件扩展名自动识别
material = manager.create_material(url)
# .mp4 → VideoMaterial
# .mp3 → AudioMaterial
# .jpg → VideoMaterial (图片作为静态视频)
```

### 3. 缓存机制 ✅

```python
# 同一URL只下载一次
material1 = manager.create_material(url)  # 下载
material2 = manager.create_material(url)  # 从缓存返回
```

### 4. 批量处理 ✅

```python
# 批量下载多个素材
urls = [url1, url2, url3]
materials = manager.batch_create_materials(urls)
# 返回: {url1: material1, url2: material2, url3: material3}
```

### 5. 素材管理 ✅

```python
# 查看已下载的素材
files = manager.list_downloaded_materials()

# 查看文件夹大小
size = manager.get_assets_folder_size()  # MB

# 清除缓存
manager.clear_cache()
```

## 🔍 技术细节

### 为什么可行？

1. **pyJianYingDraft 的 Material 设计**

   ```python
   # Material 只需要一个路径参数
   class VideoMaterial:
       def __init__(self, path: str):
           self.path = path
   ```

2. **草稿文件夹的灵活性**

   ```
   草稿文件夹/
   ├── draft_content.json    # pyJianYingDraft 管理
   ├── draft_meta_info.json  # pyJianYingDraft 管理
   └── Assets/               # 我们添加的，不冲突 ✅
   ```

3. **剪映的素材加载机制**
   - 剪映读取 `draft_content.json` 中的 Material 路径
   - 只要路径指向的文件存在，就能加载
   - 不关心文件在哪个文件夹

### 路径处理

```python
# 绝对路径示例
draft_folder_path = "C:/Users/你的用户名/.../com.lveditor.draft"
draft_name = "我的项目"
assets_path = "C:/Users/你的用户名/.../com.lveditor.draft/我的项目/Assets"

# Material 使用绝对路径
video_material = VideoMaterial(
    "C:/Users/你的用户名/.../com.lveditor.draft/我的项目/Assets/video.mp4"
)
```

## 📊 数据流程

```
1. 用户提供 URL
   ↓
2. MaterialManager.create_material(url)
   ↓
3. 下载到 {草稿文件夹}/Assets/{文件名}
   ↓
4. 创建 Material 对象（指向本地路径）
   ↓
5. Converter 使用 Material 创建 Segment
   ↓
6. Segment 添加到 Script
   ↓
7. 保存草稿（draft_content.json 包含 Material 路径）
   ↓
8. 剪映打开草稿，加载素材 ✅
```

## 🎓 总结

### ✅ 完全可行的原因

1. **符合 pyJianYingDraft 设计** - Material 只需要路径
2. **不干扰现有机制** - Assets 是额外添加的
3. **便于管理** - 素材与草稿在同一位置
4. **灵活扩展** - 支持各种素材类型和管理功能

### 📦 文件清单

- `src/utils/material_manager.py` - 素材管理器实现
- `docs/MATERIAL_MANAGER_GUIDE.md` - 完整使用文档
- `test_material_manager.py` - 使用示例和测试

### 🔗 相关文档

- 完整使用指南: `docs/MATERIAL_MANAGER_GUIDE.md`
- 数据结构集成: `INTEGRATION_SUMMARY.md`
- 转换器文档: `src/data_structures/draft_generator_interface/README.md`

---

**结论：在 pyJianYingDraft 的设计下，MaterialManager 的方案完全可行且推荐使用！✅**
