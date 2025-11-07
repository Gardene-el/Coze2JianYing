# MaterialManager 使用文档

> **📌 注意**: 从 v2.0 开始，Coze2JianYing 使用集中式存储配置系统。
> MaterialManager 现在使用 `{drafts_base_dir}/CozeJianYingAssistantAssets/` 作为统一的素材存储位置。
> 详见 [存储配置指南](../STORAGE_CONFIG_GUIDE.md)。

## 📋 概述

`MaterialManager` 是专门用于管理剪映草稿素材的工具类，主要功能：

1. ✅ **自动创建 Assets 文件夹** - 在草稿目录下创建独立的素材存储空间
2. ✅ **下载网络素材** - 从 URL 下载视频/音频/图片到本地
3. ✅ **创建 Material 对象** - 自动识别类型并创建对应的 pyJianYingDraft Material
4. ✅ **素材缓存机制** - 避免重复下载同一 URL 的素材
5. ✅ **批量处理** - 支持批量下载多个素材
6. ✅ **素材管理** - 查看、统计、清理素材

## 🗂️ 新版存储结构

**v2.0 新特性：统一素材文件夹**

```
{drafts_base_dir}/                          # 草稿根目录（可配置）
├── 扣子2剪映：{uuid-1}/                    # 项目1
│   ├── draft_content.json
│   └── draft_meta_info.json
├── 扣子2剪映：{uuid-2}/                    # 项目2
│   ├── draft_content.json
│   └── draft_meta_info.json
└── CozeJianYingAssistantAssets/           # 统一素材文件夹 ✨
    ├── {uuid-1}/                          # 项目1的素材
    │   ├── video1.mp4
    │   └── audio1.mp3
    └── {uuid-2}/                          # 项目2的素材
        └── image1.jpg
```

**优势:**
- ✅ 所有项目共享统一素材文件夹
- ✅ 按项目 UUID 隔离，避免冲突
- ✅ 便于统一管理和备份
- ✅ 减少磁盘空间占用（避免重复）

## 🎯 核心问题解答

### Q: 在 pyJianYingDraft 的设计下，这样的方案可行吗？

**答：完全可行！✅**

理由：

1. **pyJianYingDraft 的草稿结构支持自定义文件夹**

   ```
   草稿根目录/
   └── 我的项目/              # 草稿文件夹
       ├── draft_content.json    # pyJianYingDraft 生成
       ├── draft_meta_info.json  # pyJianYingDraft 生成
       └── Assets/               # 我们创建的素材文件夹 ✅
           ├── video1.mp4
           ├── audio1.mp3
           └── image1.jpg
   ```

2. **Material 对象只需要本地路径**

   ```python
   # pyJianYingDraft 的 VideoMaterial 只需要文件路径
   video_material = draft.VideoMaterial("C:/path/to/草稿/Assets/video.mp4")
   ```

3. **Assets 文件夹不会干扰 pyJianYingDraft 的工作**

   - pyJianYingDraft 只关心 `draft_content.json` 和 `draft_meta_info.json`
   - Assets 文件夹是额外的，不影响草稿的读取和保存

4. **剪映本身也支持素材文件夹**
   - 剪映打开草稿时会读取 Material 路径指向的文件
   - 只要文件存在，剪映就能正常加载

## 📦 安装依赖

```bash
# 安装 requests 用于下载
pip install requests

# 或者安装所有依赖
pip install -r requirements.txt
```

## 🚀 快速开始

### 基本使用

```python
import pyJianYingDraft as draft
from src.utils.material_manager import create_material_manager

# 1. 创建草稿
draft_folder = draft.DraftFolder("C:/path/to/JianyingPro/草稿文件夹")
script = draft_folder.create_draft("我的项目", 1920, 1080, allow_replace=True)

# 2. 创建素材管理器（自动创建 Assets 文件夹）
manager = create_material_manager(draft_folder, "我的项目")

# 3. 下载素材并创建 Material 对象
video_url = "https://example.com/video.mp4"
video_material = manager.create_video_material(video_url)

# 4. 创建视频片段并添加到草稿
from pyJianYingDraft import VideoSegment, Timerange
segment = VideoSegment(
    material=video_material,
    target_timerange=Timerange(0, 5000)
)
script.add_segment(segment)

# 5. 保存
script.save()
```

## 🔧 API 参考

### 创建管理器

```python
# 方法1: 从 DraftFolder 创建（推荐）
manager = create_material_manager(draft_folder, "草稿名称")

# 方法2: 直接创建
manager = MaterialManager(
    draft_folder_path="C:/path/to/drafts",
    draft_name="我的项目"
)
```

### 下载和创建素材

```python
# 自动识别类型
material = manager.create_material(url)

# 指定类型
video_material = manager.create_video_material(video_url)
audio_material = manager.create_audio_material(audio_url)

# 批量下载
urls = [url1, url2, url3]
material_map = manager.batch_create_materials(urls)
# 返回: {url1: material1, url2: material2, ...}
```

### 素材管理

```python
# 列出已下载的素材
files = manager.list_downloaded_materials()
# 返回: ['video1.mp4', 'audio1.mp3', ...]

# 查看 Assets 文件夹大小
size_mb = manager.get_assets_folder_size()
# 返回: 125.8 (MB)

# 查看素材信息
info = manager.get_material_info(url)
# 返回: {"url": "...", "type": "video", "local_path": "...", "cached": True}

# 清除缓存（不删除文件）
manager.clear_cache()
```

## 💡 完整工作流示例

### 场景：从 Draft Interface 配置生成草稿

```python
import pyJianYingDraft as draft
from src.utils.material_manager import create_material_manager
from src.utils.converter import DraftInterfaceConverter

# 1. Draft Interface 配置（来自外部系统）
draft_config = {
    "tracks": [
        {
            "track_type": "video",
            "segments": [
                {
                    "type": "video",
                    "material_url": "https://example.com/video1.mp4",
                    "time_range": {"start": 0, "end": 5000},
                    "transform": {
                        "position_x": 0.0,
                        "position_y": 0.0,
                        "scale_x": 1.0,
                        "scale_y": 1.0,
                        "rotation": 0.0,
                        "opacity": 1.0
                    }
                }
            ]
        },
        {
            "track_type": "audio",
            "segments": [
                {
                    "type": "audio",
                    "material_url": "https://example.com/bgm.mp3",
                    "time_range": {"start": 0, "end": 10000},
                    "audio": {"volume": 0.8}
                }
            ]
        }
    ]
}

# 2. 创建草稿和素材管理器
output_folder = "C:/Users/你的用户名/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft"
draft_folder = draft.DraftFolder(output_folder)
script = draft_folder.create_draft("我的项目", 1920, 1080, allow_replace=True)
manager = create_material_manager(draft_folder, "我的项目")

# 3. 收集所有需要下载的URL
urls_to_download = []
for track in draft_config["tracks"]:
    for segment in track["segments"]:
        if "material_url" in segment:
            urls_to_download.append(segment["material_url"])

print(f"需要下载 {len(urls_to_download)} 个素材")

# 4. 批量下载素材
material_map = manager.batch_create_materials(urls_to_download)
print(f"下载完成: {len(material_map)}/{len(urls_to_download)}")

# 5. 使用转换器转换草稿
converter = DraftInterfaceConverter()
script = converter.convert_draft_config_to_script(
    draft_config,
    script,
    material_map  # URL到Material的映射
)

# 6. 保存草稿
script.save()
print("✅ 草稿生成完成!")

# 7. 查看结果
print(f"\n📊 素材统计:")
print(f"  已下载文件: {manager.list_downloaded_materials()}")
print(f"  Assets大小: {manager.get_assets_folder_size():.2f} MB")
```

## 📂 文件结构

```
C:/Users/你的用户名/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft/
└── 我的项目/                        # 草稿文件夹
    ├── Assets/                      # 素材文件夹（MaterialManager 创建）
    │   ├── video1.mp4              # 从 URL1 下载
    │   ├── video2.mp4              # 从 URL2 下载
    │   ├── bgm.mp3                 # 从 URL3 下载
    │   └── cover.jpg               # 从 URL4 下载
    ├── draft_content.json          # 草稿内容（pyJianYingDraft 创建）
    └── draft_meta_info.json        # 草稿元信息（pyJianYingDraft 创建）
```

## ⚙️ 高级特性

### 1. 自定义文件名

```python
# 下载时指定文件名
material = manager.create_material(
    url="https://example.com/abc123",
    filename="my_custom_name.mp4"
)
```

### 2. 强制重新下载

```python
# 即使文件已存在也重新下载
material = manager.create_material(
    url=video_url,
    force_download=True
)
```

### 3. 错误处理

```python
try:
    material = manager.create_video_material(url)
except requests.RequestException as e:
    print(f"下载失败: {e}")
except ValueError as e:
    print(f"格式错误: {e}")
```

### 4. 素材类型支持

| 类别 | 支持的格式                                      | Material 类型      |
| ---- | ----------------------------------------------- | ------------------ |
| 视频 | .mp4, .mov, .avi, .mkv, .flv, .wmv, .webm, .m4v | `VideoMaterial`    |
| 音频 | .mp3, .wav, .aac, .flac, .ogg, .m4a, .wma       | `AudioMaterial`    |
| 图片 | .jpg, .jpeg, .png, .gif, .bmp, .webp            | `VideoMaterial` ⚠️ |

⚠️ **注意**：图片在 pyJianYingDraft 中也是作为 `VideoMaterial` 处理的（静态视频）

## 🎨 与其他模块的配合

### MaterialManager + Converter

```python
from src.utils.material_manager import create_material_manager
from src.utils.converter import DraftInterfaceConverter

# 创建管理器和转换器
manager = create_material_manager(draft_folder, "项目名")
converter = DraftInterfaceConverter()

# Draft Interface 配置
segment_config = {
    "material_url": "https://example.com/video.mp4",
    "time_range": {"start": 0, "end": 5000},
    "transform": {...}
}

# 下载并转换
video_material = manager.create_video_material(segment_config["material_url"])
video_segment = converter.convert_video_segment_config(segment_config, video_material)

# 添加到草稿
script.add_segment(video_segment)
```

## 🐛 常见问题

### Q1: Assets 文件夹会被剪映删除吗？

**答：不会。** 剪映只管理 `draft_content.json` 等文件，不会删除其他文件夹。

### Q2: 素材路径会随草稿移动吗？

**答：不会自动移动。** 如果移动草稿文件夹，需要重新下载素材或手动调整路径。

**建议：** 使用相对路径或者在 Assets 文件夹中统一管理素材。

### Q3: 可以使用本地文件吗？

**答：可以！** 直接创建 Material：

```python
# 不通过 MaterialManager
video_material = draft.VideoMaterial("C:/本地视频.mp4")

# 或者复制到 Assets 文件夹
import shutil
assets_path = manager.assets_path / "my_video.mp4"
shutil.copy("C:/本地视频.mp4", assets_path)
video_material = draft.VideoMaterial(str(assets_path))
```

### Q4: 下载大文件会超时吗？

**答：可能会。** 当前默认超时 30 秒，可以修改：

```python
# 在 material_manager.py 的 download_material 方法中
response = requests.get(url, stream=True, timeout=30)  # 修改这里
```

## 📊 性能建议

1. **批量下载** - 使用 `batch_create_materials()` 批量处理
2. **利用缓存** - 同一 URL 只会下载一次
3. **异步下载** - 大量素材时考虑使用异步（需要自己实现）

## 📝 总结

✅ **MaterialManager 在 pyJianYingDraft 的设计下完全可行！**

核心优势：

1. 素材统一管理在 Assets 文件夹
2. 不干扰 pyJianYingDraft 的正常工作
3. 与 Converter 完美配合
4. 支持完整的素材生命周期管理

使用流程：

```
URL → MaterialManager.download → Assets/ → Material → Converter → Segment → Script
```
