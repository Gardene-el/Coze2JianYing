# 统一草稿数据管理实现文档

## 概述

本次更新实现了统一的草稿数据管理系统，解决了三个标签页各自管理草稿文件路径的问题，提供了一个全局的路径设置面板，统一控制所有草稿生成场景的输出位置。

## 主要变更

### 1. 新增全局路径管理器 (`app/utils/draft_path_manager.py`)

新增了 `DraftPathManager` 类，作为单例模式管理全局草稿路径设置：

**核心功能：**
- 管理剪映草稿文件夹路径
- 控制是否传输草稿到指定文件夹
- 提供有效输出路径和素材路径的智能计算
- 支持自动检测剪映草稿文件夹

**关键方法：**
```python
# 获取全局实例
manager = get_draft_path_manager()

# 设置草稿文件夹
manager.set_draft_folder(path)

# 启用/禁用传输到指定文件夹
manager.set_transfer_enabled(True/False)

# 获取有效的输出路径（根据设置返回剪映文件夹或本地数据目录）
output_path = manager.get_effective_output_path()

# 获取有效的素材路径（根据设置返回对应位置）
assets_path = manager.get_effective_assets_path(draft_id)
```

**路径决策逻辑：**

| 传输选项 | 草稿文件夹设置 | 草稿输出位置 | 素材存储位置 |
|---------|--------------|------------|------------|
| 未勾选 | - | 本地数据目录 (`config.drafts_dir`) | 本地素材目录 (`config.assets_dir/{draft_id}`) |
| 已勾选 | 已设置且有效 | 剪映草稿文件夹 | `剪映草稿文件夹/../CozeJianYingAssistantAssets` |
| 已勾选 | 未设置或无效 | 本地数据目录（回退） | 本地素材目录（回退） |

### 2. 主窗口新增全局路径设置面板 (`app/gui/main_window.py`)

在标签页上方添加了 "全局草稿路径设置" 面板，包含：

**UI组件：**
- 剪映草稿文件夹路径显示和选择
- "选择文件夹..." 按钮
- "自动检测" 按钮
- "传输草稿到指定文件夹" 复选框
- 状态显示标签

**功能：**
- 所有标签页共享相同的路径设置
- 实时显示当前状态（使用本地数据或传输至剪映）
- 路径更改立即生效，无需重启应用

### 3. 三个标签页的更新

#### 手动草稿生成标签页 (`app/gui/draft_generator_tab.py`)
- **移除**：文件夹选择UI（"输出设置" LabelFrame）
- **使用**：全局路径管理器获取输出路径
- **行为**：生成草稿时从全局管理器获取有效路径

#### 云端服务标签页 (`app/gui/cloud_service_tab.py`)
- **移除**：文件夹选择UI（"草稿文件夹设置" LabelFrame）
- **更新**：服务说明增加提示"草稿输出路径由全局设置控制"
- **行为**：API服务生成草稿时使用全局路径配置

#### 脚本执行标签页 (`app/gui/script_executor_tab.py`)
- **移除**：文件夹选择UI（"输出设置" LabelFrame）
- **使用**：全局路径管理器
- **行为**：脚本执行时使用全局路径配置

### 4. 后端工具更新

#### 草稿保存器 (`app/utils/draft_saver.py`)
```python
def __init__(self, output_dir: str = None):
    # 如果没有指定输出目录，使用全局路径管理器的配置
    if output_dir is None:
        path_manager = get_draft_path_manager()
        self.output_dir = path_manager.get_effective_output_path()
```

**素材目录管理：**
```python
# 使用全局路径管理器的素材路径配置
path_manager = get_draft_path_manager()
temp_assets_dir = path_manager.get_effective_assets_path(draft_id)
```

#### 草稿生成器 (`app/utils/draft_generator.py`)
- 添加了 `draft_path_manager` 导入
- generate 方法已支持接受 output_folder 参数
- 标签页调用时传入全局管理器的路径

## 使用场景

### 场景1：本地数据存储（默认）
适合开发、测试，或者不想直接影响剪映草稿文件夹的情况。

**设置：**
- 不勾选 "传输草稿到指定文件夹"

**行为：**
- 草稿保存到：`C:\Users\<username>\AppData\Local\coze2jianying_data\drafts`
- 素材保存到：`C:\Users\<username>\AppData\Local\coze2jianying_data\assets\{draft_id}`

**优点：**
- 不影响剪映现有草稿
- 便于测试和调试
- 数据集中管理

### 场景2：直接传输到剪映（生产）
适合正式使用，草稿直接出现在剪映中。

**设置：**
1. 点击 "自动检测" 或 "选择文件夹..." 设置剪映草稿文件夹
2. 勾选 "传输草稿到指定文件夹"

**行为：**
- 草稿保存到：剪映草稿文件夹（如 `C:\Users\<username>\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft`）
- 素材保存到：`剪映草稿文件夹/../CozeJianYingAssistantAssets`

**优点：**
- 草稿立即可在剪映中使用
- 素材统一管理在剪映目录附近
- 符合手动草稿生成的传统行为

## 向后兼容性

本次更新完全向后兼容：
- 不影响现有数据结构
- API 接口保持不变
- 默认行为（使用本地数据目录）与之前一致
- 用户可以选择性启用新的传输功能

## 测试

新增测试文件 `tests/test_draft_path_manager.py`，验证：
- 路径管理器单例模式
- 路径设置和获取
- 传输选项切换
- 有效路径计算逻辑
- 自动检测功能

运行测试：
```bash
python tests/test_draft_path_manager.py
```

## 注意事项

1. **路径验证**：全局路径管理器会验证设置的路径是否存在且为有效目录
2. **自动回退**：如果启用传输但路径无效，自动回退到本地数据目录
3. **状态提示**：状态标签实时显示当前使用的路径策略
4. **素材管理**：传输模式下，素材存储在 `CozeJianYingAssistantAssets` 目录（与手动草稿生成一致）

## 未来扩展

可能的扩展方向：
- 支持多个草稿文件夹预设
- 添加历史路径记录
- 路径设置持久化到配置文件
- 提供路径冲突检测和警告

## 相关文件

- `app/utils/draft_path_manager.py` - 路径管理器核心实现
- `app/gui/main_window.py` - 全局路径设置UI
- `app/gui/draft_generator_tab.py` - 手动草稿生成标签页更新
- `app/gui/cloud_service_tab.py` - 云端服务标签页更新
- `app/gui/script_executor_tab.py` - 脚本执行标签页更新
- `app/utils/draft_saver.py` - 草稿保存器更新
- `app/utils/draft_generator.py` - 草稿生成器更新
- `tests/test_draft_path_manager.py` - 路径管理器测试
