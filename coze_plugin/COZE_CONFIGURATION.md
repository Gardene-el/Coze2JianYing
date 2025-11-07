# Coze 插件配置说明

## 概述

Coze 插件工具现在支持通过环境变量配置文件存储路径，不再硬编码 `/tmp/jianying_assistant` 路径。

## 配置方式

### 环境变量

在 Coze 平台或运行环境中设置以下环境变量：

```bash
# Coze 专用草稿目录（最高优先级）
export JIANYING_COZE_DRAFTS_DIR=/custom/path/to/drafts

# Coze 专用数据根目录
export JIANYING_COZE_DATA_DIR=/custom/path/to/data

# 通用数据根目录（与应用共享）
export JIANYING_DATA_ROOT=/custom/path/to/data
```

### 配置优先级

1. `JIANYING_COZE_DRAFTS_DIR` - Coze 专用草稿目录
2. `JIANYING_DATA_ROOT` - 通用数据根目录（草稿在其下的 drafts 子目录）
3. `/tmp/jianying_assistant` - 默认路径（Coze 平台标准）

## 注意事项

### Coze 平台限制

- Coze 平台的 `/tmp` 目录限制为 512MB
- 如果数据量较大，建议配置外部存储路径
- 确保配置的路径有读写权限

### 向后兼容

- 如果不设置环境变量，工具将使用默认的 `/tmp/jianying_assistant` 路径
- 已有代码在不设置环境变量的情况下仍然正常工作

## 工具配置

### 已支持配置的工具

以下工具已更新为支持环境变量配置：

1. **create_draft** - 创建草稿工具
   - 使用 `get_coze_drafts_dir()` 获取草稿目录
   
2. **export_drafts** - 导出草稿工具
   - 使用 `get_coze_drafts_dir()` 查找和导出草稿

### 配置模块

`base_tools/coze_config.py` 提供了配置辅助函数：

- `get_coze_base_dir()` - 获取数据根目录
- `get_coze_drafts_dir()` - 获取草稿目录
- `ensure_dir_exists(path)` - 确保目录存在

## 使用示例

### 在 Coze 工具中使用配置

```python
# 导入配置模块
from base_tools.coze_config import get_coze_drafts_dir, ensure_dir_exists

# 使用配置的目录
drafts_dir = get_coze_drafts_dir()
draft_path = os.path.join(drafts_dir, draft_id)

# 确保目录存在
ensure_dir_exists(draft_path)
```

### 测试配置

```bash
# 设置自定义路径
export JIANYING_COZE_DRAFTS_DIR=/custom/drafts

# 运行 Coze 工具
# 工具将使用 /custom/drafts 作为草稿存储目录
```

## 部署建议

### 本地测试

```bash
# 使用临时目录
export JIANYING_COZE_DATA_DIR=/tmp/coze_test
```

### 生产环境

```bash
# 使用持久化存储
export JIANYING_COZE_DATA_DIR=/data/jianying_coze
# 或者只设置草稿目录
export JIANYING_COZE_DRAFTS_DIR=/data/jianying_coze/drafts
```

### Docker 部署

```yaml
# docker-compose.yml
services:
  coze-tools:
    environment:
      - JIANYING_COZE_DATA_DIR=/app/coze_data
    volumes:
      - coze-data:/app/coze_data
```

## 故障排查

### 问题1：找不到配置模块

**症状**：`ImportError: No module named 'coze_config'`

**解决方案**：
- 确保 `base_tools/coze_config.py` 文件存在
- 工具中已包含向后兼容代码，会自动降级到硬编码路径

### 问题2：权限问题

**症状**：无法创建目录或写入文件

**解决方案**：
- 检查环境变量指向的路径权限
- 使用有权限的目录
- Coze 平台上确保有 `/tmp` 目录的写权限

### 问题3：路径不存在

**症状**：工具报错找不到草稿

**解决方案**：
- 检查环境变量设置是否正确
- 确认草稿是否在配置的目录中创建
- 使用 `export_drafts` 工具的 `export_all=true` 参数列出所有草稿

## 迁移指南

### 从硬编码路径迁移

如果之前使用硬编码的 `/tmp/jianying_assistant`：

1. 数据已经存在于 `/tmp/jianying_assistant/drafts`
2. 不需要任何配置更改，工具会继续使用默认路径
3. 如需迁移，设置环境变量并手动复制数据：

```bash
# 设置新路径
export JIANYING_COZE_DRAFTS_DIR=/new/path/drafts

# 复制现有数据
cp -r /tmp/jianying_assistant/drafts/* /new/path/drafts/
```

## 相关文档

- [应用配置说明](../../docs/CONFIGURATION.md) - 主应用的配置系统
- [Coze 插件开发指南](https://www.coze.cn/open/docs/developer_guides) - Coze 官方文档
