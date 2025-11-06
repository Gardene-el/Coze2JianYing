# Assets 目录说明

## 📋 概述

本目录包含用于测试 Coze2JianYing API 的素材文件。

## 📂 文件列表

| 文件名 | 类型 | 大小 | 说明 |
|--------|------|------|------|
| `video.mp4` | 视频 | ~3.0 MB | 测试视频素材 |
| `audio.mp3` | 音频 | ~128 KB | 测试音频素材 |
| `sticker.gif` | 贴纸 | ~82 KB | 测试贴纸素材（GIF 动画）|
| `subtitles.srt` | 字幕 | 239 字节 | 测试字幕文件（SRT 格式）|

## 📜 素材来源

本目录中的所有素材文件均**复制自** [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft) 项目。

### 源仓库信息

- **项目名称**: pyJianYingDraft
- **项目地址**: https://github.com/GuanYixuan/pyJianYingDraft
- **源文件路径**: `readme_assets/tutorial/`
- **复制时的 Commit 版本**: `30f9695` (Feat: Support setting `maintrack_adsorb`)
- **复制日期**: 2024-11-06

### Commit 详情

```
commit 30f9695
Author: GuanYixuan
Date: [见原仓库]
Message: Feat: Support setting `maintrack_adsorb`
```

完整的 commit 信息可在原仓库查看：
https://github.com/GuanYixuan/pyJianYingDraft/commit/30f9695

## 📖 用途说明

这些素材文件的主要用途是：

### 1. API 测试
用于测试 Coze2JianYing 项目的 API 接口功能，包括：
- 视频片段添加和处理
- 音频轨道管理
- 贴纸元素集成
- 字幕文件导入
- 素材下载和管理功能

### 2. 功能演示
作为示例素材，用于演示：
- 草稿生成流程
- 素材管理系统
- 各种媒体类型的处理能力
- API 端点的使用方法

### 3. 开发测试
供开发者在开发过程中使用：
- 单元测试
- 集成测试
- 功能验证
- 性能测试

## ⚖️ 版权说明

### 素材版权

本目录中的素材文件版权归 [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft) 项目所有者所有。

这些文件仅用于：
- **测试目的** - 验证 Coze2JianYing 项目功能
- **开发目的** - 辅助开发和调试
- **演示目的** - 展示项目功能

### 使用限制

⚠️ **重要提示**：

1. **非商业用途**：本目录中的素材仅供测试和开发使用，不得用于商业用途
2. **禁止再分发**：除非获得原作者明确授权，不得单独分发这些素材文件
3. **归属声明**：使用这些素材时应注明来源于 pyJianYingDraft 项目
4. **遵循原项目许可**：使用这些文件必须遵守 pyJianYingDraft 项目的许可证条款

### pyJianYingDraft 项目许可

pyJianYingDraft 项目采用的许可证请参考其原仓库：
https://github.com/GuanYixuan/pyJianYingDraft/blob/main/LICENSE

## 🔗 相关链接

- **pyJianYingDraft 项目**: https://github.com/GuanYixuan/pyJianYingDraft
- **原始素材路径**: https://github.com/GuanYixuan/pyJianYingDraft/tree/main/readme_assets/tutorial
- **Coze2JianYing 项目**: https://github.com/Gardene-el/Coze2JianYing

## 📝 使用示例

### API 测试示例

```python
import requests

# 测试添加视频
response = requests.post(
    "http://localhost:8000/api/draft/{draft_id}/add-videos",
    json={
        "draft_id": "your-draft-id",
        "videos": [{
            "material_url": "file:///path/to/Assets/video.mp4",
            "time_range": {"start": 0, "end": 5000}
        }]
    }
)

# 测试添加音频
response = requests.post(
    "http://localhost:8000/api/draft/{draft_id}/add-audios",
    json={
        "draft_id": "your-draft-id",
        "audios": [{
            "material_url": "file:///path/to/Assets/audio.mp3",
            "time_range": {"start": 0, "end": 3000}
        }]
    }
)
```

### 本地文件路径使用

在测试时，可以使用以下方式引用本地素材：

```python
import os
from pathlib import Path

# 获取 Assets 目录的绝对路径
assets_dir = Path(__file__).parent.parent / "Assets"

# 构建文件 URL
video_url = f"file://{assets_dir}/video.mp4"
audio_url = f"file://{assets_dir}/audio.mp3"
sticker_url = f"file://{assets_dir}/sticker.gif"
subtitle_path = str(assets_dir / "subtitles.srt")
```

## 🔄 更新说明

如果需要更新素材文件到 pyJianYingDraft 的最新版本：

1. 访问原仓库获取最新文件：
   ```bash
   git clone https://github.com/GuanYixuan/pyJianYingDraft.git
   cd pyJianYingDraft
   git log -1  # 获取最新 commit hash
   ```

2. 复制新文件到本目录：
   ```bash
   cp -r readme_assets/tutorial/* /path/to/Coze2JianYing/Assets/
   ```

3. 更新本 README 文件中的 commit 版本号和日期

## ⚠️ 注意事项

1. **文件大小**: 素材文件总大小约 3.2 MB，请确保有足够的存储空间
2. **Git LFS**: 如果项目使用 Git LFS，大文件会被正确处理
3. **文件路径**: 在代码中引用这些文件时，请使用相对路径或配置化的绝对路径
4. **文件完整性**: 不要修改这些文件的内容，以保持与原始素材的一致性

## 🙏 致谢

感谢 [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft) 项目提供的优质素材文件，使得我们能够更好地测试和开发 Coze2JianYing 项目。

---

**最后更新**: 2024-11-06  
**维护者**: Coze2JianYing 项目团队
