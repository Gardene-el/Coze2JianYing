# 素材路径修改 - 更新说明

## 📋 修改概述

**日期**: 2025-10-16  
**版本**: v1.1.0  
**修改人**: GitHub Copilot

### 主要变更

将素材下载位置从项目文件夹内的 `Assets` 目录改为剪映草稿根目录下的 `CozeJianYingAssistantAssets/{项目ID}/` 统一管理目录。

---

## 🎯 修改动机

### 之前的问题

- 素材分散在各个项目文件夹中，不便于统一管理
- 项目文件夹包含了草稿文件和素材文件，结构混乱
- 难以批量清理或管理素材

### 改进后的优势

1. **统一管理**: 所有素材集中存放，便于管理和清理
2. **清晰分隔**: 草稿文件和素材文件分开，结构更清晰
3. **易于识别**: 通过文件夹名称快速识别是 Coze 助手创建的素材
4. **向后兼容**: 保留旧的路径逻辑，不影响现有代码

---

## 📁 目录结构对比

### 旧结构

```
剪映草稿文件夹/
└── 项目名称/
    ├── draft_content.json       # 草稿内容
    ├── draft_meta_info.json     # 草稿元信息
    └── Assets/                  # 素材（在项目内）
        ├── material_xxx.png
        └── material_yyy.mp3
```

### 新结构

```
剪映草稿文件夹/
├── 项目ID/                      # 草稿文件夹
│   ├── draft_content.json
│   └── draft_meta_info.json
└── CozeJianYingAssistantAssets/ # 素材统一管理文件夹（新增）
    └── 项目ID/                  # 每个项目的素材独立存放
        ├── material_xxx.png
        └── material_yyy.mp3
```

---

## 🔧 技术实现

### 修改的文件

#### 1. `src/utils/material_manager.py`

**变更**: 修改 `MaterialManager` 类和 `create_material_manager` 函数

```python
# 新增 project_id 参数
def __init__(self, draft_folder_path: str, draft_name: str, project_id: Optional[str] = None):
    # 新路径逻辑
    if project_id:
        # {draft_folder_path}/CozeJianYingAssistantAssets/{project_id}/
        self.assets_base_path = self.draft_folder_path / "CozeJianYingAssistantAssets"
        self.assets_path = self.assets_base_path / project_id
    else:
        # 旧路径（向后兼容）
        self.assets_path = self.draft_path / "Assets"
```

#### 2. `src/utils/draft_generator.py`

**变更**: 在创建 `MaterialManager` 时传入 `project_id`

```python
material_manager = create_material_manager(
    draft_folder=draft_folder_obj,
    draft_name=draft_id,
    project_id=draft_id  # 传入项目ID
)
```

---

## ✅ 测试验证

### 测试 1: 路径逻辑测试 (`test_new_assets_path.py`)

- ✅ 新路径逻辑正确
- ✅ 旧路径逻辑正确（向后兼容）
- ✅ 工厂函数正确
- ✅ 文件夹结构正确

### 测试 2: 真实数据测试 (`test_real_coze_assets_path.py`)

- ✅ 使用真实 Coze 数据生成草稿
- ✅ 素材成功下载到新位置（10 个图片，约 8MB）
- ✅ 草稿文件正确生成
- ✅ 目录结构符合预期

### 测试 3: 快速验证 (`quick_verify.py`)

- ✅ 基本功能正常
- ✅ 素材文件夹创建在正确位置
- ✅ 草稿文件正确生成

---

## 📝 使用说明

### 正常使用（自动使用新路径）

```python
from src.utils.draft_generator import DraftGenerator

# 创建生成器
generator = DraftGenerator(output_base_dir="./JianyingProjects")

# 生成草稿（自动使用新的素材路径）
draft_paths = generator.generate_from_file('coze_output.json')

# 素材将下载到:
# ./JianyingProjects/CozeJianYingAssistantAssets/{项目ID}/
```

### 手动使用 MaterialManager

```python
import pyJianYingDraft as draft
from src.utils.material_manager import create_material_manager

# 新方式（推荐）- 使用项目ID
project_id = "6a65b7a9-5e3b-45f1-9c9b-583d8a5fd1f6"
draft_folder = draft.DraftFolder("C:/path/to/drafts")
manager = create_material_manager(draft_folder, "项目名称", project_id)
# 素材路径: C:/path/to/drafts/CozeJianYingAssistantAssets/{project_id}/

# 旧方式（兼容）- 不使用项目ID
manager = create_material_manager(draft_folder, "项目名称")
# 素材路径: C:/path/to/drafts/项目名称/Assets/
```

---

## ⚠️ 注意事项

### 1. 向后兼容性

- 所有旧的测试代码仍然可以正常运行
- 不传 `project_id` 参数时，使用旧的路径逻辑
- GUI 程序自动使用新路径，无需修改

### 2. 文件夹管理

- 素材和草稿文件现在是分开的
- 移动或复制草稿时，需要同时处理两个文件夹：
  - 草稿文件夹: `{项目ID}/`
  - 素材文件夹: `CozeJianYingAssistantAssets/{项目ID}/`

### 3. 路径引用

- pyJianYingDraft 库会自动处理素材的绝对路径引用
- draft_content.json 中的素材路径会正确指向新位置
- 剪映软件可以正常识别和使用这些素材

---

## 🚀 后续优化建议

### 1. 素材清理功能

添加工具函数清理不再使用的素材：

```python
def clean_unused_assets(draft_folder_path: str):
    """清理 CozeJianYingAssistantAssets 中不再被引用的素材"""
    pass
```

### 2. 素材共享功能

如果多个项目使用相同的素材 URL，可以共享同一份文件：

```python
# 使用 URL hash 作为文件名，多个项目可以引用同一个文件
def get_shared_material_path(url: str) -> str:
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return f"CozeJianYingAssistantAssets/shared/{url_hash}.ext"
```

### 3. 素材统计功能

```python
def get_assets_statistics(draft_folder_path: str) -> dict:
    """获取素材文件夹统计信息"""
    return {
        "total_size": "...",
        "file_count": "...",
        "project_count": "...",
    }
```

---

## 📚 相关文档

- [素材管理器使用指南](MATERIAL_MANAGER_GUIDE.md)
- [Coze 转换指南](COZE_CONVERSION_GUIDE.md)
- [架构和工作流](ARCHITECTURE_AND_WORKFLOW.md)

---

## 🔍 排查问题

### 问题 1: 找不到素材文件

**症状**: 剪映打开草稿时提示找不到素材

**解决方案**:

1. 检查 `CozeJianYingAssistantAssets/{项目ID}/` 文件夹是否存在
2. 检查素材文件是否已下载
3. 查看 draft_content.json 中的素材路径是否正确

### 问题 2: 素材文件夹为空

**症状**: `CozeJianYingAssistantAssets/{项目ID}/` 文件夹存在但为空

**可能原因**:

1. Coze 输出中没有需要下载的素材 URL
2. 素材下载失败（URL 过期、网络问题等）
3. 只有文本轨道，没有音视频素材

**解决方案**: 查看日志文件确认具体原因

---

## 📞 支持

如有问题，请查看：

- 日志文件: `logs/app.log`
- 测试文件: `test_new_assets_path.py`, `test_real_coze_assets_path.py`
- 文档: `docs/ASSETS_PATH_CHANGE.md`
