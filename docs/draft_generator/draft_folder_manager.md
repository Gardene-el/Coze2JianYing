# 草稿文件夹管理器

## 概述

`draft_folder_manager.py` 模块提供了统一的草稿文件夹路径管理功能，用于在三个标签页之间共享代码，实现：

1. 草稿文件夹路径的选择和存储
2. 自动检测剪映草稿文件夹
3. 管理是否传输草稿到指定文件夹的选项

## 核心组件

### DraftFolderManager

草稿文件夹管理器类，负责管理文件夹路径和配置。

**属性**:
- `folder_path`: 草稿文件夹路径（可读写）
- `enable_transfer`: 是否启用传输到草稿文件夹（可读写，默认为 True）

**方法**:
- `detect_default_folder()`: 自动检测剪映草稿文件夹
- `get_output_folder(fallback_folder)`: 获取最终的输出文件夹路径
  - 如果启用传输：返回设置的文件夹路径或自动检测的路径
  - 如果未启用传输：返回 fallback_folder
- `validate_folder(folder_path)`: 验证文件夹路径是否有效

### DraftFolderWidget

可复用的草稿文件夹选择 UI 组件。

**UI 元素**:
- 勾选框："传输草稿到指定文件夹"
- 文件夹路径显示框
- "选择文件夹..." 按钮
- "自动检测" 按钮

**特性**:
- 根据勾选状态自动启用/禁用文件夹选择组件
- 支持回调函数通知路径和传输选项变化

## 使用示例

### 在标签页中使用

```python
from app.utils.draft_folder_manager import DraftFolderManager, DraftFolderWidget

class MyTab(BaseTab):
    def __init__(self, parent):
        # 创建管理器实例
        self.folder_manager = DraftFolderManager()
        
        # 在 _create_widgets 中创建 UI 组件
        self.folder_widget = DraftFolderWidget(
            parent=self.frame,
            manager=self.folder_manager,
            on_folder_changed=self._on_folder_changed,
            on_transfer_changed=self._on_transfer_changed
        )
        
    def _create_widgets(self):
        # ... 其他组件 ...
        pass
        
    def _setup_layout(self):
        # 将组件放置到布局中
        self.folder_widget.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
    def _on_folder_changed(self, folder: str):
        """文件夹路径改变时的回调"""
        self.status_var.set(f"输出文件夹: {folder}")
    
    def _on_transfer_changed(self, enabled: bool):
        """传输选项改变时的回调"""
        self.logger.info(f"传输草稿到文件夹: {'启用' if enabled else '禁用'}")
    
    def generate_draft(self):
        # 获取输出文件夹
        from app.config import get_config
        config = get_config()
        fallback_folder = config.drafts_dir
        
        output_folder = self.folder_manager.get_output_folder(fallback_folder)
        
        if output_folder is None:
            # 处理未配置的情况
            messagebox.showerror("错误", "请选择草稿文件夹")
            return
        
        # 验证文件夹
        is_valid, error_msg = self.folder_manager.validate_folder(output_folder)
        if not is_valid:
            messagebox.showerror("错误", error_msg)
            return
        
        # 使用 output_folder 生成草稿
        # ...
```

## 传输选项逻辑

**勾选"传输草稿到指定文件夹"时**:
- 使用用户选择的草稿文件夹路径
- 如果未选择，尝试自动检测剪映草稿文件夹
- 如果检测失败，返回 None，需要用户手动选择

**未勾选时**:
- 使用备用文件夹（由 `app.config` 的 `drafts_dir` 提供）
- 备用文件夹通常是临时目录或应用数据目录

## 代码复用效果

使用共享模块后，三个标签页的重复代码从约 100 行减少到约 10 行：

**之前** (每个标签页):
```python
# 约 40 行的文件夹选择 UI 代码
# 约 30 行的文件夹选择和检测逻辑
# 约 30 行的验证和错误处理代码
```

**之后** (每个标签页):
```python
# 创建管理器
self.folder_manager = DraftFolderManager()

# 创建 UI 组件
self.folder_widget = DraftFolderWidget(...)

# 放置到布局
self.folder_widget.grid(...)

# 2 个简单的回调函数（约 10 行）
```

## 优势

1. **代码复用**: 消除了三个标签页之间的重复代码
2. **统一行为**: 所有标签页的文件夹选择行为完全一致
3. **易于维护**: 只需在一处修改即可影响所有标签页
4. **新功能**: 添加了"是否传输"的控制选项
5. **向后兼容**: 保持了原有的所有功能和 API

## 测试

运行测试：
```bash
python tests/test_draft_folder_manager.py
```

测试覆盖：
- 模块导入和语法检查
- 核心逻辑测试（初始化、路径设置、传输选项、文件夹验证）
