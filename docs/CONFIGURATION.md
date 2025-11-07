# 应用配置说明

## 概述

本应用**仅在 Windows 系统上运行**。所有数据存储在统一的位置：

**`C:\Users\<username>\AppData\Local\coze2jianying_data\`**

## 目录结构

```
C:\Users\<username>\AppData\Local\coze2jianying_data\
├── cache\      # 缓存文件（替代 C:\tmp\jianying_assistant）
├── drafts\     # 草稿文件（替代 Temp\jianying_draft_*）
├── assets\     # 素材文件（替代 Temp\jianying_assets_*）
└── logs\       # 日志文件
```

## 配置方式

### 使用默认路径（推荐）

无需任何配置，应用会自动使用上述默认路径。

### 自定义路径（可选）

通过环境变量自定义存储位置：

```bash
# 设置自定义数据根目录
set JIANYING_DATA_ROOT=D:\MyData\coze2jianying

# 或单独设置各个目录
set JIANYING_CACHE_DIR=D:\MyData\cache
set JIANYING_DRAFTS_DIR=D:\MyData\drafts
set JIANYING_ASSETS_DIR=D:\MyData\assets
```

## 目录说明

### cache 目录
- **用途**: 存储缓存数据和临时处理文件
- **替代**: `C:\tmp\jianying_assistant`
- **内容**: draft state manager 的状态文件

### drafts 目录
- **用途**: 存储草稿文件
- **替代**: `C:\Users\<username>\AppData\Local\Temp\jianying_draft_*`
- **内容**: 生成的剪映草稿项目

### assets 目录
- **用途**: 存储素材文件
- **替代**: `C:\Users\<username>\AppData\Local\Temp\jianying_assets_*`
- **内容**: 下载的媒体文件和素材缓存

## 查看当前配置

### 通过 Python
```python
from app.config import get_config

config = get_config()
print(config.to_dict())
```

## 注意事项

1. **仅支持 Windows**: 本应用设计为仅在 Windows 系统运行
2. **自动创建目录**: 首次运行时会自动创建所需目录
3. **权限要求**: 需要有权限在 `%LOCALAPPDATA%` 创建目录
4. **磁盘空间**: 确保有足够的磁盘空间存储素材和草稿

## 故障排查

### 问题1: 无法创建目录

**症状**: 应用报错无法创建 `coze2jianying_data` 目录

**解决方案**:
1. 检查 Windows 用户权限
2. 确认 `%LOCALAPPDATA%` 环境变量存在
3. 尝试手动创建目录
4. 使用环境变量指定其他位置

### 问题2: 磁盘空间不足

**症状**: 提示磁盘空间不足

**解决方案**:
1. 清理不需要的草稿文件
2. 清空 cache 目录
3. 使用环境变量将数据移至其他磁盘

## 环境变量参考

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `JIANYING_DATA_ROOT` | 数据根目录 | `%LOCALAPPDATA%\coze2jianying_data` |
| `JIANYING_CACHE_DIR` | 缓存目录 | `{data_root}\cache` |
| `JIANYING_DRAFTS_DIR` | 草稿目录 | `{data_root}\drafts` |
| `JIANYING_ASSETS_DIR` | 素材目录 | `{data_root}\assets` |

## 迁移指南

### 从旧版本迁移

如果之前使用的是其他路径，可以手动迁移数据：

```cmd
REM 1. 复制旧数据到新位置
xcopy /E /I C:\tmp\jianying_assistant "%LOCALAPPDATA%\coze2jianying_data\cache"
xcopy /E /I "%TEMP%\jianying_draft_*" "%LOCALAPPDATA%\coze2jianying_data\drafts"
xcopy /E /I "%TEMP%\jianying_assets_*" "%LOCALAPPDATA%\coze2jianying_data\assets"

REM 2. 启动应用，验证数据正确
```
