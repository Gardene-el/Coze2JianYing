# 存储配置系统指南

## 概述

Coze2JianYing 使用集中式存储配置系统来管理所有数据存储路径，提供平台无关、用户可配置的存储解决方案。

## 核心特性

### 1. 平台无关

存储配置系统自动检测操作系统并使用合适的路径：

**Windows:**
- 剪映自动检测: `C:\Users\{用户名}\AppData\Local\JianyingPro\...` 或 `AppData\Roaming\...`
- 应用数据: `%LOCALAPPDATA%\Coze2JianYing\`
- 默认草稿: `%USERPROFILE%\JianyingProjects\`

**macOS:**
- 剪映自动检测: `~/Library/Containers/com.lemon.lvpro/...` 或 `~/Movies/JianyingPro/...`
- 应用数据: `~/Library/Application Support/Coze2JianYing/`
- 默认草稿: `~/JianyingProjects/`

**Linux:**
- 剪映: 不支持（剪映不支持 Linux）
- 应用数据: `~/.local/share/coze2jianying/`
- 默认草稿: `~/JianyingProjects/`

### 2. 自动检测

系统会自动检测剪映的安装位置：

```python
from app.core.storage_config import get_storage_config

config = get_storage_config()
jianying_path = config.detect_jianying_draft_folder()

if jianying_path:
    print(f"检测到剪映: {jianying_path}")
else:
    print("未检测到剪映，使用默认路径")
```

### 3. 配置持久化

所有配置自动保存到用户配置文件：

- **配置文件位置**: `~/.coze2jianying/storage_config.json`
- **格式**: JSON
- **自动保存**: 配置修改后自动保存

配置文件示例:

```json
{
  "drafts_base_dir": "/home/user/JianyingProjects",
  "state_base_dir": null,
  "assets_base_dir": null,
  "temp_dir": null,
  "auto_detect_jianying": true
}
```

## 存储路径说明

### 1. 草稿目录 (drafts_base_dir)

**用途**: 存放生成的剪映草稿项目

**默认位置**:
- 自动检测到剪映时: 剪映的草稿文件夹
- 未检测到时: `~/JianyingProjects/`

**目录结构**:
```
JianyingProjects/
├── 扣子2剪映：{uuid-1}/
│   ├── draft_content.json
│   ├── draft_info.json
│   └── draft_mate_info.json
├── 扣子2剪映：{uuid-2}/
└── CozeJianYingAssistantAssets/  # 统一素材文件夹
    ├── {uuid-1}/
    │   ├── video1.mp4
    │   └── audio1.mp3
    └── {uuid-2}/
        └── image1.jpg
```

### 2. 状态目录 (state_base_dir)

**用途**: 存放草稿状态和配置信息（用于 API 模式）

**默认位置**:
- Windows: `%LOCALAPPDATA%\Coze2JianYing\drafts\`
- macOS: `~/Library/Application Support/Coze2JianYing/drafts/`
- Linux: `~/.local/share/coze2jianying/drafts/`

**目录结构**:
```
state_base_dir/
├── {uuid-1}/
│   └── draft_config.json  # 草稿配置和状态
└── {uuid-2}/
    └── draft_config.json
```

### 3. 素材目录 (assets_base_dir)

**用途**: 存放下载的网络素材文件

**默认位置**: `{drafts_base_dir}/CozeJianYingAssistantAssets/`

**特点**:
- 所有项目共享统一的素材文件夹
- 按项目 UUID 分类存储
- 避免素材重复下载

### 4. 临时目录 (temp_dir)

**用途**: 存放临时文件和缓存

**默认位置**: `{系统临时目录}/coze2jianying/`

## 使用方法

### 1. 获取存储配置

```python
from app.core.storage_config import get_storage_config

# 获取全局配置实例（单例）
config = get_storage_config()

# 访问各类路径
drafts_dir = config.drafts_base_dir    # Path 对象
state_dir = config.state_base_dir      # Path 对象
assets_dir = config.assets_base_dir    # Path 对象
temp_dir = config.temp_dir             # Path 对象
```

### 2. 自定义存储路径

```python
from app.core.storage_config import get_storage_config

config = get_storage_config()

# 设置自定义草稿目录
config.set_drafts_dir("/path/to/custom/drafts")

# 设置自定义状态目录
config.set_state_dir("/path/to/custom/state")

# 设置自定义素材目录
config.set_assets_dir("/path/to/custom/assets")
```

### 3. 自动检测控制

```python
from app.core.storage_config import get_storage_config

config = get_storage_config()

# 启用自动检测（默认启用）
config.enable_auto_detect(True)

# 禁用自动检测
config.enable_auto_detect(False)
```

### 4. 重置为默认配置

```python
from app.core.storage_config import get_storage_config

config = get_storage_config()

# 重置所有配置为默认值
config.reset_to_defaults()
```

### 5. 查看配置摘要

```python
from app.core.storage_config import get_storage_config

config = get_storage_config()

# 获取配置摘要（用于显示）
summary = config.get_config_summary()

for key, value in summary.items():
    print(f"{key}: {value}")
```

输出示例:
```
草稿目录: /home/user/JianyingProjects
状态目录: /home/user/.local/share/coze2jianying/drafts
素材目录: /home/user/JianyingProjects/CozeJianYingAssistantAssets
临时目录: /tmp/coze2jianying
自动检测: 启用
配置文件: /home/user/.coze2jianying/storage_config.json
```

## 与组件集成

### DraftGenerator

DraftGenerator 自动使用存储配置:

```python
from app.utils.draft_generator import DraftGenerator

# 使用默认配置（从 storage_config）
generator = DraftGenerator()

# 或指定自定义路径（覆盖配置）
generator = DraftGenerator(output_base_dir="/custom/path")
```

### DraftStateManager

DraftStateManager 自动使用存储配置:

```python
from app.utils.draft_state_manager import get_draft_state_manager

# 使用默认配置（从 storage_config）
manager = get_draft_state_manager()

# 或指定自定义路径（覆盖配置）
manager = get_draft_state_manager(base_dir="/custom/path")
```

### MaterialManager

MaterialManager 使用草稿目录下的统一素材文件夹:

```python
from app.utils.material_manager import create_material_manager
import pyJianYingDraft as draft

# MaterialManager 自动使用 {drafts_base_dir}/CozeJianYingAssistantAssets/
draft_folder = draft.DraftFolder(drafts_base_dir)
manager = create_material_manager(
    draft_folder=draft_folder,
    draft_name="项目名称",
    project_id="uuid"
)
```

## 环境变量支持

虽然配置主要通过文件管理，但某些路径可以通过环境变量覆盖:

```bash
# 设置自定义草稿目录（未来支持）
export COZE2JIANYING_DRAFTS_DIR="/custom/drafts"

# 设置自定义配置文件位置（未来支持）
export COZE2JIANYING_CONFIG_FILE="/custom/config.json"
```

## 迁移指南

### 从旧版本迁移

如果您已经使用旧版本生成了草稿，无需担心：

1. **自动检测**: 如果您的草稿在剪映默认位置，新版本会自动检测
2. **手动设置**: 如果使用自定义位置，首次运行时设置正确的路径即可
3. **配置持久化**: 设置后会自动保存，下次启动时自动加载

### 素材文件迁移

新版本使用统一的素材文件夹 `CozeJianYingAssistantAssets/`：

```bash
# 旧版本结构
JianyingProjects/
├── 项目1/
│   └── Assets/  # 素材分散在各项目中
└── 项目2/
    └── Assets/

# 新版本结构
JianyingProjects/
├── 项目1/
├── 项目2/
└── CozeJianYingAssistantAssets/  # 统一素材文件夹
    ├── uuid-1/
    └── uuid-2/
```

**迁移建议**: 旧项目的素材保持原样，新生成的项目使用新结构即可。

## 最佳实践

### 1. 使用默认配置

对于大多数用户，默认配置已经足够：

- ✅ 自动检测剪映位置
- ✅ 使用系统标准路径
- ✅ 配置自动持久化

### 2. 自定义配置

如果您有特殊需求：

```python
from app.core.storage_config import get_storage_config

config = get_storage_config()

# 例如：使用外部硬盘存储素材
config.set_assets_dir("/Volumes/ExternalDrive/JianyingAssets")

# 例如：使用网络共享文件夹
config.set_drafts_dir("//NAS/JianyingProjects")
```

### 3. 多用户环境

每个用户有独立的配置文件：

- 配置文件位于用户主目录: `~/.coze2jianying/`
- 不同用户之间互不干扰
- 支持多用户共享服务器部署

### 4. 备份重要数据

建议定期备份：

- ✅ 草稿目录: 包含所有生成的项目
- ✅ 素材目录: 包含所有下载的素材
- ⚠️ 状态目录: 可选（主要用于 API 模式）
- ❌ 临时目录: 无需备份

## 故障排除

### 问题1: 无法检测到剪映

**症状**: 自动检测返回 None

**解决方案**:
1. 确认剪映已正确安装
2. 检查是否使用了非标准安装路径
3. 手动设置草稿目录:
   ```python
   config.set_drafts_dir("/path/to/jianying/drafts")
   ```

### 问题2: 配置无法保存

**症状**: 配置修改后重启丢失

**解决方案**:
1. 检查配置文件路径的写入权限
2. 查看日志中的错误信息
3. 尝试手动创建配置目录:
   ```bash
   mkdir -p ~/.coze2jianying
   ```

### 问题3: 路径冲突

**症状**: 多个组件使用不同的路径

**解决方案**:
1. 重置全局配置:
   ```python
   from app.core.storage_config import reset_storage_config
   reset_storage_config()
   ```
2. 重新初始化组件

## 开发者参考

### 添加新的存储路径

如果需要添加新的存储路径类型:

```python
# 1. 在 StorageConfig 的 DEFAULT_CONFIG 中添加
DEFAULT_CONFIG = {
    # ...
    "new_path_type": None,
}

# 2. 在 _init_paths() 中初始化
def _init_paths(self):
    # ...
    self._new_path = self._get_default_new_path()

# 3. 添加属性访问器
@property
def new_path(self) -> Path:
    return self._new_path

# 4. 添加设置方法
def set_new_path(self, path: str) -> bool:
    # ...
```

### 单元测试

参考 `tests/test_storage_config.py` 编写测试:

```python
def test_new_feature():
    with tempfile.TemporaryDirectory() as tmpdir:
        config = StorageConfig(config_file=Path(tmpdir) / "test.json")
        # 测试代码
```

## 相关文档

- [MaterialManager 指南](../draft_generator/MATERIAL_MANAGER_GUIDE.md)
- [API 使用指南](../../API_QUICKSTART.md)
- [开发路线图](../guides/DEVELOPMENT_ROADMAP.md)

## 更新日志

### v2.0 (2025-11)
- ✅ 实现集中式存储配置
- ✅ 平台无关的路径检测
- ✅ 配置持久化
- ✅ 与现有组件集成
- ✅ 完整测试套件
