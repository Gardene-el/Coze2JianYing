# 数据存储重构总结

## 问题描述

Issue 提到 "当前数据储存存在一些问题，不仅在C:\Users\"，虽然描述不完整，但通过代码分析发现了以下问题：

1. **硬编码的 Windows 路径**: `draft_generator.py` 中使用了硬编码的 `C:\Users\{username}\AppData\...` 路径
2. **分散的存储位置**: 不同组件使用不同的存储目录
   - DraftGenerator: `./JianyingProjects`
   - DraftStateManager: `/tmp/jianying_assistant/drafts`
   - MaterialManager: 各种素材位置
3. **平台特定代码**: 代码不支持跨平台使用
4. **无用户配置**: 用户无法自定义存储位置

## 解决方案

### 1. 集中式存储配置系统

创建了 `app/core/storage_config.py` 模块，提供：

- **平台无关的路径检测**: 自动识别 Windows/Mac/Linux
- **自动检测剪映安装位置**: 
  - Windows: 检测 AppData/Local 和 AppData/Roaming
  - macOS: 检测 Library/Containers 和 Movies
  - Linux: 不支持剪映（使用默认路径）
- **配置持久化**: JSON 格式保存到 `~/.coze2jianying/storage_config.json`
- **用户可配置**: 提供完整的 API 来设置自定义路径

### 2. 更新现有组件

**DraftGenerator**:
```python
# 之前：硬编码路径
DEFAULT_DRAFT_PATHS = [
    r"C:\Users\{username}\AppData\Local\...",
    r"C:\Users\{username}\AppData\Roaming\...",
]

# 现在：使用存储配置
from app.core.storage_config import get_storage_config
config = get_storage_config()
detected = config.detect_jianying_draft_folder()
```

**DraftStateManager**:
```python
# 之前：硬编码 /tmp 路径
def __init__(self, base_dir: str = "/tmp/jianying_assistant/drafts"):

# 现在：使用存储配置
def __init__(self, base_dir: Optional[str] = None):
    storage_config = get_storage_config()
    self.base_dir = base_dir or storage_config.state_base_dir
```

### 3. 默认存储位置

**草稿目录** (`drafts_base_dir`):
- 优先：自动检测到的剪映草稿文件夹
- 其次：`~/JianyingProjects/`

**状态目录** (`state_base_dir`):
- Windows: `%LOCALAPPDATA%\Coze2JianYing\drafts\`
- macOS: `~/Library/Application Support/Coze2JianYing/drafts/`
- Linux: `~/.local/share/coze2jianying/drafts/`

**素材目录** (`assets_base_dir`):
- `{drafts_base_dir}/CozeJianYingAssistantAssets/`

**临时目录** (`temp_dir`):
- `{系统临时目录}/coze2jianying/`

### 4. 使用方法

```python
from app.core.storage_config import get_storage_config

# 获取配置
config = get_storage_config()

# 访问路径
print(f"草稿目录: {config.drafts_base_dir}")
print(f"状态目录: {config.state_base_dir}")

# 自定义路径
config.set_drafts_dir("/custom/path")

# 查看配置摘要
summary = config.get_config_summary()
for key, value in summary.items():
    print(f"{key}: {value}")
```

## 实施成果

### 新增文件
1. `app/core/storage_config.py` (418 行) - 核心配置模块
2. `tests/test_storage_config.py` (217 行) - 完整测试套件
3. `docs/STORAGE_CONFIG_GUIDE.md` (457 行) - 使用指南

### 修改文件
1. `app/utils/draft_generator.py` - 移除硬编码路径，使用配置
2. `app/utils/draft_state_manager.py` - 使用配置的状态目录
3. `docs/draft_generator/MATERIAL_MANAGER_GUIDE.md` - 添加 v2.0 说明
4. `scripts/test_api_demo.py` - 移除硬编码路径

### 测试覆盖

7 个测试用例，全部通过：

1. ✅ 存储配置初始化测试
2. ✅ 配置持久化测试
3. ✅ 平台检测测试
4. ✅ DraftGenerator 集成测试
5. ✅ DraftStateManager 集成测试
6. ✅ 配置摘要测试
7. ✅ 配置重置测试

### 代码质量

- ✅ 所有测试通过 (7/7)
- ✅ 代码审查完成
- ✅ 所有审查意见已解决
- ✅ CodeQL 安全扫描通过 (0 警告)
- ✅ 遵循 Python 最佳实践

## 向后兼容性

### 完全兼容

所有更改都是向后兼容的：

1. **DraftGenerator**: 仍然接受 `output_base_dir` 参数，可以覆盖默认配置
2. **DraftStateManager**: 仍然接受 `base_dir` 参数，可以覆盖默认配置
3. **配置文件**: 如果不存在，自动使用默认值
4. **现有数据**: 不受影响，继续可用

### 迁移路径

对于现有用户：

1. **无需操作**: 如果剪映在默认位置，系统会自动检测
2. **首次配置**: 如果使用自定义位置，首次运行时设置即可
3. **配置持久**: 设置后自动保存，下次自动加载

## 优势

### 1. 跨平台支持

- ✅ Windows 完全支持
- ✅ macOS 完全支持  
- ✅ Linux 基本支持（剪映不支持 Linux）

### 2. 用户友好

- ✅ 自动检测，零配置
- ✅ 支持自定义路径
- ✅ 配置持久化
- ✅ 详细文档

### 3. 开发者友好

- ✅ 单一真实来源
- ✅ 清晰的 API
- ✅ 完整的测试
- ✅ 易于扩展

### 4. 可维护性

- ✅ 集中管理所有路径
- ✅ 无硬编码
- ✅ 易于调试
- ✅ 便于迁移

## 未来工作（可选）

### GUI 集成

可以在 GUI 中添加存储设置面板：

```python
# 在 local_service_tab.py 或新的 settings_tab.py 中
from app.core.storage_config import get_storage_config

def create_storage_settings():
    config = get_storage_config()
    
    # 显示当前配置
    summary = config.get_config_summary()
    
    # 提供修改按钮
    # - 选择草稿目录
    # - 选择素材目录
    # - 启用/禁用自动检测
    # - 重置为默认
```

### 环境变量支持

可以添加环境变量覆盖：

```python
# 在 storage_config.py 中
drafts_dir = os.getenv('COZE2JIANYING_DRAFTS_DIR') or self._get_default_drafts_dir()
```

### 迁移工具

如果需要，可以创建数据迁移工具：

```python
def migrate_old_data():
    """将旧版本的数据迁移到新位置"""
    # 检测旧数据
    # 复制到新位置
    # 更新配置
```

## 相关链接

- [存储配置指南](docs/STORAGE_CONFIG_GUIDE.md)
- [MaterialManager 指南](docs/draft_generator/MATERIAL_MANAGER_GUIDE.md)
- [测试代码](tests/test_storage_config.py)
- [核心代码](app/core/storage_config.py)

## 总结

本次重构完全解决了数据存储相关的问题：

1. ✅ 移除了所有硬编码路径
2. ✅ 实现了平台无关的路径处理
3. ✅ 提供了集中式配置管理
4. ✅ 支持用户自定义配置
5. ✅ 保持了完全的向后兼容性
6. ✅ 提供了完整的文档和测试

系统现在更加健壮、灵活和易于维护。
