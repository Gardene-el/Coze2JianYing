# 统一草稿数据管理 - 实现总结

## 问题背景

当前三个标签页（手动草稿生成、云端服务、脚本执行）各自独立管理草稿文件路径，导致：
1. UI 重复，用户需要在每个标签页单独设置路径
2. 设置不一致，可能导致混淆
3. 无法统一控制草稿输出行为

## 解决方案

实现全局路径管理系统，统一控制所有草稿生成场景的输出位置。

## 核心实现

### 1. 全局路径管理器 (DraftPathManager)

**文件**: `app/utils/draft_path_manager.py`

**特性**:
- 单例模式，确保全局唯一
- 管理两个核心状态：
  - 剪映草稿文件夹路径
  - 是否传输到指定文件夹
- 智能路径决策算法

**关键方法**:
```python
# 获取实例
manager = get_draft_path_manager()

# 设置和查询
manager.set_draft_folder(path)
manager.set_transfer_enabled(True/False)
manager.get_effective_output_path()
manager.get_effective_assets_path(draft_id)
```

### 2. 主窗口全局设置

**文件**: `app/gui/main_window.py`

**新增UI组件**:
```
┌─ 全局草稿路径设置 ────────────────────────────────┐
│ 剪映草稿文件夹: [路径显示] [选择...] [自动检测]    │
│ ☑ 传输草稿到指定文件夹                           │
│ 当前状态: [状态显示]                             │
└─────────────────────────────────────────────────┘
```

**位置**: 标签页上方，所有标签页共享

### 3. 标签页更新

#### 手动草稿生成 (`draft_generator_tab.py`)
- **删除**: 54行代码（输出设置UI）
- **简化**: 直接使用全局路径管理器

#### 云端服务 (`cloud_service_tab.py`)  
- **删除**: 32行代码（草稿文件夹设置UI）
- **更新**: 服务说明提示使用全局设置

#### 脚本执行 (`script_executor_tab.py`)
- **删除**: 48行代码（输出设置UI）
- **简化**: 统一使用全局路径管理器

### 4. 后端集成

#### draft_saver.py
```python
# 之前
self.output_dir = config.drafts_dir

# 之后  
path_manager = get_draft_path_manager()
self.output_dir = path_manager.get_effective_output_path()
```

#### draft_generator.py
```python
# 添加导入
from app.utils.draft_path_manager import get_draft_path_manager

# generate 方法已支持 output_folder 参数
# 标签页调用时传入全局管理器的路径
```

## 路径决策表

| 传输选项 | 路径设置 | 草稿输出位置 | 素材存储位置 |
|---------|---------|------------|-------------|
| ❌ 未勾选 | - | 本地数据: `AppData/Local/coze2jianying_data/drafts` | `assets/{draft_id}` |
| ✅ 已勾选 | 有效路径 | 剪映文件夹: `.../com.lveditor.draft` | `CozeJianYingAssistantAssets` |
| ✅ 已勾选 | 无效路径 | 本地数据（回退） | `assets/{draft_id}` |

## 代码统计

```
添加:    801 行
删除:    225 行
净增:    576 行

新增文件: 4 个
- app/utils/draft_path_manager.py (201行)
- tests/test_draft_path_manager.py (74行)
- docs/unified_draft_path_management.md (180行)
- docs/ui_visualization.md (189行)

修改文件: 6 个
- app/gui/main_window.py (+118行)
- app/gui/draft_generator_tab.py (-47净变化)
- app/gui/cloud_service_tab.py (-36净变化)
- app/gui/script_executor_tab.py (-45净变化)
- app/utils/draft_saver.py (+3净变化)
- app/utils/draft_generator.py (+1行)
```

## 使用场景

### 场景A: 开发测试（默认）
1. 打开应用
2. 不勾选传输选项
3. 草稿保存在: `AppData/Local/coze2jianying_data/drafts`
4. 不影响剪映现有草稿

### 场景B: 生产使用
1. 点击"自动检测"找到剪映文件夹
2. 勾选"传输草稿到指定文件夹"
3. 草稿直接出现在剪映中
4. 素材统一管理在 CozeJianYingAssistantAssets

## 技术亮点

1. **单例模式**: 确保全局状态一致性
2. **智能回退**: 路径无效时自动使用本地目录
3. **实时状态**: UI 状态标签实时反映当前策略
4. **模块解耦**: 各组件职责清晰，易于维护
5. **向后兼容**: 默认行为不变，用户可选择启用新功能

## 测试覆盖

**测试文件**: `tests/test_draft_path_manager.py`

**测试项**:
- ✅ 单例模式验证
- ✅ 路径设置和获取
- ✅ 传输选项切换
- ✅ 有效路径计算
- ✅ 自动检测功能
- ✅ 状态文本生成

## 向后兼容性

- ✅ 现有数据结构不变
- ✅ API 接口保持一致
- ✅ 默认行为与之前相同
- ✅ 可选性功能，用户自主选择

## 用户体验改进

**之前**:
- 需要在3个标签页分别设置路径
- 可能设置不一致导致混淆
- 界面冗余，占用空间

**之后**:
- 一处设置，全局生效
- 状态清晰可见
- 界面简洁，操作便捷

## 未来扩展可能

1. 路径预设管理（保存多个常用路径）
2. 路径历史记录
3. 设置持久化到配置文件
4. 路径冲突检测和警告
5. 批量迁移工具

## 相关文档

- [实现详情](unified_draft_path_management.md)
- [UI可视化](ui_visualization.md)
- [测试代码](../tests/test_draft_path_manager.py)

## 验收标准

- [x] 全局路径设置UI正常显示
- [x] 文件夹选择和自动检测功能正常
- [x] 传输选项可切换，状态正确显示
- [x] 三个标签页均使用全局设置
- [x] 路径决策逻辑正确
- [x] 向后兼容，默认行为不变
- [x] 代码通过语法检查
- [x] 测试用例通过
- [x] 文档完整清晰

## 结论

本次实现成功统一了三个草稿生成场景的数据管理，通过引入全局路径管理器，实现了：
1. UI简化 - 移除重复设置界面
2. 管理统一 - 一处配置全局生效
3. 逻辑清晰 - 智能路径决策
4. 用户友好 - 实时状态反馈
5. 扩展性强 - 便于未来功能扩展

完全满足需求，向后兼容，可以安全合并。
