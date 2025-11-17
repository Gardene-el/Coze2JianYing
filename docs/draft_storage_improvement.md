# 草稿文件存储管理改进

## 改进概述

将三个标签页中分散的草稿文件夹路径设置统一到主窗口顶部的全局配置面板中，并添加了"传输到草稿文件夹"选项，实现了两种草稿存储方案的自动切换。

## 主要变更

### 1. 新增全局配置管理器

**文件**: `app/utils/draft_config_manager.py`

- **类**: `DraftConfigManager`（单例模式）
- **功能**:
  - 管理草稿文件夹路径
  - 管理是否传输到草稿文件夹的选项
  - 提供有效输出路径获取方法
  - 提供素材基础路径获取方法
  - 路径验证功能

**API**:
```python
from app.utils.draft_config_manager import get_draft_config_manager

config_mgr = get_draft_config_manager()

# 设置路径
config_mgr.draft_folder_path = "C:/Users/用户名/AppData/Local/JianyingPro/..."

# 设置传输选项
config_mgr.transfer_to_draft_folder = True

# 获取有效输出路径
output_path = config_mgr.get_effective_output_path()

# 获取素材基础路径
assets_path = config_mgr.get_assets_base_path()

# 验证路径
is_valid, msg = config_mgr.validate_draft_folder_path()
```

### 2. 新增草稿文件夹设置面板

**文件**: `app/gui/draft_folder_panel.py`

- **类**: `DraftFolderPanel`
- **功能**:
  - 显示草稿文件夹路径
  - 提供"选择文件夹"和"自动检测"按钮
  - 提供"传输到草稿文件夹"复选框
  - 显示两种存储方案的说明文字
  - 验证路径有效性

**UI 布局**:
```
┌─────────────────────────────────────────────────────────┐
│ 草稿文件夹设置                                           │
├─────────────────────────────────────────────────────────┤
│ 剪映草稿文件夹: [路径显示] [选择文件夹] [自动检测]      │
│ ☑ 传输草稿到指定文件夹                                  │
│ • 勾选：草稿直接保存在剪映文件夹，素材存储在            │
│         CozeJianYingAssistantAssets 文件夹              │
│ • 不勾选：草稿和素材保存在本地数据目录                  │
└─────────────────────────────────────────────────────────┘
```

### 3. 主窗口集成

**文件**: `app/gui/main_window.py`

**变更**:
- 导入 `DraftFolderPanel`
- 在标签页之前添加草稿文件夹设置面板

**新的窗口结构**:
```
┌─────────────────────────────────────────────┐
│ Coze剪映草稿生成器                           │
├─────────────────────────────────────────────┤
│ 草稿文件夹设置面板                           │  ← 新增
├─────────────────────────────────────────────┤
│ 标签页 1 | 标签页 2 | 标签页 3              │
│                                             │
│ 标签页内容区域                               │
│                                             │
├─────────────────────────────────────────────┤
│ 日志窗口                                     │
└─────────────────────────────────────────────┘
```

### 4. 标签页更新

移除了三个标签页各自的文件夹选择 UI，统一使用全局配置：

**文件**: 
- `app/gui/draft_generator_tab.py`
- `app/gui/cloud_service_tab.py`
- `app/gui/script_executor_tab.py`

**变更**:
- 移除 `output_folder` 实例变量
- 移除文件夹选择 UI（`folder_frame`、`folder_label`、`folder_entry`、`folder_btn`、`auto_detect_btn`）
- 移除 `_select_output_folder()` 和 `_auto_detect_folder()` 方法
- 导入并使用 `get_draft_config_manager()`
- 使用 `config_mgr.get_effective_output_path()` 获取输出路径

### 5. 草稿保存器更新

**文件**: `app/utils/draft_saver.py`

**变更**:
- 导入 `get_draft_config_manager`
- 在 `__init__` 方法中使用全局配置决定输出目录
- 在 `save_draft` 方法中根据传输选项决定素材存储位置

**存储逻辑**:
```python
if self.draft_config_manager.transfer_to_draft_folder and self.draft_config_manager.draft_folder_path:
    # 使用手动草稿生成方案：CozeJianYingAssistantAssets/{draft_id}
    temp_assets_dir = os.path.join(
        self.draft_config_manager.draft_folder_path, 
        "CozeJianYingAssistantAssets", 
        draft_id
    )
else:
    # 使用云端服务/脚本执行方案：本地数据/assets/{draft_id}
    temp_assets_dir = os.path.join(app_config.assets_dir, draft_id)
```

## 两种存储方案

### 方案一：传输到草稿文件夹（勾选时）

**适用场景**: 手动草稿生成

**存储位置**:
- 草稿文件：`{指定的剪映草稿文件夹}/{草稿名称}/`
- 素材文件：`{指定的剪映草稿文件夹}/CozeJianYingAssistantAssets/{draft_id}/`

**特点**:
- 草稿直接保存到剪映的草稿文件夹，剪映可以直接打开
- 素材集中存储在 CozeJianYingAssistantAssets 文件夹中
- 适合直接在剪映中编辑的场景

### 方案二：本地数据目录（不勾选时）

**适用场景**: 云端服务、脚本执行

**存储位置**:
- 草稿文件：`%LOCALAPPDATA%/coze2jianying_data/drafts/{草稿名称}/`
- 素材文件：`%LOCALAPPDATA%/coze2jianying_data/assets/{draft_id}/`

**特点**:
- 草稿和素材都存储在应用的本地数据目录
- 不直接显示在剪映的草稿列表中
- 需要手动导入到剪映
- 适合批量生成或临时预览的场景

## 测试

### 单元测试

**文件**: `tests/test_draft_config_manager_unit.py`

运行测试:
```bash
python tests/test_draft_config_manager_unit.py
```

测试覆盖:
- 单例模式
- 默认值
- 路径设置和获取
- 传输选项
- 有效输出路径（两种模式）
- 路径验证
- 素材基础路径（两种模式）
- 重置功能

## 向后兼容性

所有变更保持向后兼容：

1. **DraftSaver**:
   - 仍然支持显式传入 `output_dir` 参数
   - 如果未传入，则使用全局配置

2. **DraftGenerator**:
   - `generate()` 方法仍然支持 `output_folder` 参数
   - 如果未传入，则使用初始化时的 `output_base_dir`

3. **标签页**:
   - 保持原有功能不变
   - 只是移除了 UI 中的文件夹选择部分

## 使用示例

### 场景1：手动粘贴 JSON 生成草稿

1. 在主窗口顶部设置草稿文件夹路径
2. 勾选"传输草稿到指定文件夹"
3. 在"手动草稿生成"标签页粘贴 JSON
4. 点击"生成草稿"
5. 草稿和素材保存在指定的剪映文件夹中

### 场景2：云端服务 API 调用

1. 在主窗口顶部不勾选"传输草稿到指定文件夹"
2. 在"云端服务"标签页启动服务
3. Coze 通过 API 调用服务
4. 草稿和素材保存在本地数据目录

### 场景3：切换存储方案

用户可以随时在主窗口顶部切换存储方案：
- 勾选/取消勾选"传输草稿到指定文件夹"
- 后续的草稿生成将使用新的存储方案

## 注意事项

1. **路径验证**: 勾选"传输到草稿文件夹"时，系统会验证路径是否有效
2. **自动创建**: 输出目录和素材目录会自动创建
3. **全局生效**: 配置对所有标签页立即生效
4. **单例模式**: 配置管理器使用单例模式，确保全局唯一

## 未来改进

1. 支持配置持久化（保存到配置文件）
2. 支持多个草稿文件夹配置切换
3. 添加草稿文件夹历史记录
4. 提供素材清理功能
