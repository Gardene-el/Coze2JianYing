# Windows 专用存储系统实现说明

## 概述

根据用户需求，实现了 Windows 专用的统一存储系统，将所有数据集中存储在 `C:\Users\{username}\AppData\Local\coze2jianying\` 目录下。

## 目录结构

```
C:\Users\{username}\AppData\Local\coze2jianying\
├── cache\      # 临时数据（替代 /tmp/jianying_assistant/drafts）
├── drafts\     # 生成的草稿（替代 Temp\jianying_draft_*）
└── assets\     # 下载的素材（替代 Temp\jianying_assets_*）
```

## 实现的功能

### 1. 统一存储配置 (`app/core/storage_config.py`)

**功能：**
- 提供三个标准目录的访问接口
- 自动创建必要的目录结构
- 使用 `LOCALAPPDATA` 环境变量定位基础目录

**使用方法：**
```python
from app.core.storage_config import get_storage_config

config = get_storage_config()

# 获取三个目录
cache_dir = config.get_cache_dir()      # C:\Users\{username}\AppData\Local\coze2jianying\cache
drafts_dir = config.get_drafts_dir()    # C:\Users\{username}\AppData\Local\coze2jianying\drafts
assets_dir = config.get_assets_dir()    # C:\Users\{username}\AppData\Local\coze2jianying\assets

# 查看配置摘要
summary = config.get_summary()
```

### 2. DraftStateManager 集成

**更新内容：**
- 默认使用 `cache` 目录存储草稿状态
- 保持向后兼容，仍支持自定义 `base_dir` 参数

**使用方法：**
```python
from app.utils.draft_state_manager import get_draft_state_manager

# 使用默认的 cache 目录
manager = get_draft_state_manager()

# 或者使用自定义目录
manager = get_draft_state_manager(base_dir="custom/path")
```

### 3. DraftSaver 集成

**更新内容：**
- 默认使用 `drafts` 目录保存草稿
- 默认使用 `assets` 目录存储下载的素材
- 新增 `jianying_draft_path` 参数，支持自动复制到剪映目录

**使用方法：**
```python
from app.utils.draft_saver import get_draft_saver

# 基本使用（保存到 drafts 目录）
saver = get_draft_saver()
draft_path = saver.save_draft(draft_id)

# 自动复制到剪映目录
saver = get_draft_saver(
    jianying_draft_path=r"C:\Users\{username}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft"
)
draft_path = saver.save_draft(draft_id)
# 草稿会先保存到 drafts 目录，然后自动复制到剪映目录
```

## 关键改进

### 1. 不再使用系统临时目录

**之前：**
- 草稿状态：`/tmp/jianying_assistant/drafts/`
- 生成的草稿：`C:\Users\...\Temp\jianying_draft_qzbyj_59\`
- 下载的素材：`C:\Users\...\Temp\jianying_assets_imjwqr82\`

**现在：**
- 草稿状态：`C:\Users\{username}\AppData\Local\coze2jianying\cache\`
- 生成的草稿：`C:\Users\{username}\AppData\Local\coze2jianying\drafts\`
- 下载的素材：`C:\Users\{username}\AppData\Local\coze2jianying\assets\`

### 2. 数据持久化

- 所有数据保存在固定位置，不会被系统清理
- 素材下载后可重复使用，避免重复下载
- 便于用户备份和管理

### 3. 自动复制功能

- 草稿生成后可自动复制到剪映目录
- 保持本地副本在 `drafts` 目录，方便管理
- 复制失败不影响本地草稿保存

## 测试

新增测试文件 `tests/test_windows_storage.py`，包含 3 个测试用例：

1. **存储配置测试** - 验证三个目录正确创建和初始化
2. **DraftStateManager 集成测试** - 验证使用 cache 目录
3. **DraftSaver 集成测试** - 验证使用 drafts 和 assets 目录

所有测试通过 ✅

## 向后兼容性

所有修改保持向后兼容：

- `DraftStateManager`: 仍支持自定义 `base_dir` 参数
- `DraftSaver`: 仍支持自定义 `output_dir` 参数
- `get_draft_saver`: 函数签名扩展，但保持原有参数

## 文件变更

**新增：**
- `app/core/storage_config.py` (118 行) - Windows 专用存储配置
- `tests/test_windows_storage.py` (128 行) - 存储系统测试

**修改：**
- `app/utils/draft_state_manager.py` - 集成存储配置
- `app/utils/draft_saver.py` - 集成存储配置，添加自动复制功能
- `.gitignore` - 排除 Windows 存储目录

**未修改：**
- `app/utils/draft_generator.py` - 保持原状

**总计：** +358 行, -22 行

## 使用建议

### 1. 开发环境

```python
# 直接使用默认配置
from app.utils.draft_saver import get_draft_saver

saver = get_draft_saver()
draft_path = saver.save_draft(draft_id)
# 草稿保存在: C:\Users\{username}\AppData\Local\coze2jianying\drafts\
```

### 2. 生产环境（自动复制到剪映）

```python
from app.utils.draft_saver import get_draft_saver

# 检测剪映路径
jianying_path = r"C:\Users\{username}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft"

saver = get_draft_saver(jianying_draft_path=jianying_path)
draft_path = saver.save_draft(draft_id)
# 草稿保存在 drafts 目录，同时复制到剪映目录
```

### 3. 清理数据

```python
from app.core.storage_config import get_storage_config
import shutil

config = get_storage_config()

# 清理缓存
shutil.rmtree(config.get_cache_dir())
config.get_cache_dir().mkdir()

# 清理旧草稿（保留最近的）
# ... 自定义清理逻辑
```

## 注意事项

1. **Windows 专用**: 此实现仅支持 Windows 平台
2. **权限要求**: 需要有 `AppData\Local` 目录的写入权限
3. **磁盘空间**: 素材会持久化存储，注意磁盘空间管理
4. **自动复制**: 复制失败不会影响本地草稿保存，会记录错误日志

## 相关文档

- 存储配置源码：`app/core/storage_config.py`
- 测试文件：`tests/test_windows_storage.py`
- 使用示例：参见 `app/utils/draft_saver.py` 中的 docstring
