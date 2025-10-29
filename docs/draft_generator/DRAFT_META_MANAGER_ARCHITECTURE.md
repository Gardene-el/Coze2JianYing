# draft_meta_manager 架构和工作流程详解

## 概述

`draft_meta_manager` 是剪映草稿元信息管理器，负责扫描剪映草稿文件夹并生成 `root_meta_info.json` 文件。本文档详细说明其设计、架构和工作流程。

## 核心问题和修复历史

### 原始设计缺陷（已修复）

**问题发现**: 原始代码读取 `draft_meta_info.json` 但从未使用其内容。

```python
# 原始代码（错误）
draft_meta_path = os.path.join(draft_folder_path, "draft_meta_info.json")
with open(draft_meta_path, 'r', encoding='utf-8') as f:
    draft_meta = json.load(f)  # 读取但从未使用！
```

**影响**:
- 当 `draft_meta_info.json` 为空或损坏时导致 JSON 解析错误
- 无法处理新版剪映加密的 `draft_meta_info.json` 文件
- 所有 `draft_store` 字段都从其他来源生成，读取完全多余

**修复**: 移除对 `draft_meta_info.json` 内容的读取，只保留文件存在性检查。

## 架构设计

### 系统架构图

```
┌────────────────────────────────────────────────────────────────┐
│                     draft_meta_manager                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  scan_and_generate_meta_info(draft_root_path)            │  │
│  │                                                            │  │
│  │  输入: 草稿根目录路径                                     │  │
│  │  输出: root_meta_info 完整数据结构                        │  │
│  └────────────────┬───────────────────────────────────────────┘  │
│                   │                                              │
│                   ├─► 1. 验证目录存在性                         │
│                   ├─► 2. 扫描所有子文件夹                       │
│                   ├─► 3. 验证草稿文件夹结构                     │
│                   ├─► 4. 生成每个草稿的 draft_store 信息        │
│                   └─► 5. 汇总生成 root_meta_info                │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  _generate_draft_store_info(...)                          │  │
│  │                                                            │  │
│  │  为单个草稿生成完整的 draft_store 信息                    │  │
│  └────────────────┬───────────────────────────────────────────┘  │
│                   │                                              │
│                   ├─► 读取 draft_content.json                   │
│                   ├─► 计算草稿时长                              │
│                   ├─► 计算 Assets 文件夹大小                    │
│                   ├─► 查找草稿封面图片                          │
│                   ├─► 生成时间戳和 UUID                         │
│                   └─► 构建 draft_store 数据结构                 │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

### 数据流图

```
输入: 剪映草稿根目录
    │
    ├─► C:\Users\{user}\AppData\Local\JianyingPro\...
    │   └─ com.lveditor.draft\
    │       ├─ draft_uuid_1/
    │       │   ├─ draft_content.json ✓ (必需，读取)
    │       │   ├─ draft_meta_info.json ✓ (可选，仅检查存在性)
    │       │   └─ Assets/
    │       ├─ draft_uuid_2/
    │       └─ ...
    │
    ▼
扫描和验证
    │
    ├─► 检查每个文件夹
    ├─► 验证必需文件
    ├─► 提取草稿信息
    │
    ▼
生成 draft_store
    │
    ├─► 从 draft_content.json 读取轨道和时长
    ├─► 从文件系统计算 Assets 大小
    ├─► 查找封面图片
    ├─► 生成元数据（时间戳、UUID等）
    │
    ▼
输出: root_meta_info.json
    │
    └─► {
          "all_draft_store": [...],
          "draft_ids": 3,
          "root_path": "..."
        }
```

## 详细工作流程

### 1. 扫描阶段

```python
def scan_and_generate_meta_info(draft_root_path: str) -> Dict[str, Any]:
```

**步骤**:
1. **验证根目录**: 检查 `draft_root_path` 是否存在
2. **遍历子文件夹**: 使用 `os.listdir()` 获取所有项目
3. **过滤文件夹**: 跳过文件，只处理目录
4. **验证草稿结构**: 检查必需文件是否存在：
   - `draft_content.json` (必需)
   - `draft_meta_info.json` (可选，仅验证存在性)

**关键点**:
- `draft_meta_info.json` 的**存在性**用于验证草稿完整性
- **不读取** `draft_meta_info.json` 的内容
- 支持加密的 `draft_meta_info.json`

### 2. 草稿信息生成

```python
def _generate_draft_store_info(
    draft_folder_name: str,
    draft_folder_path: str,
    draft_root_path: str
) -> Optional[Dict[str, Any]]:
```

**数据来源**:

| 字段 | 来源 | 说明 |
|------|------|------|
| `tm_duration` | `draft_content.json` | 从轨道中计算最大结束时间 |
| `draft_timeline_materials_size` | `Assets/` 文件夹 | 递归计算所有素材文件大小 |
| `draft_cover` | 文件系统搜索 | 查找封面图片文件 |
| `draft_fold_path` | 函数参数 | 草稿文件夹路径 |
| `draft_json_file` | 函数参数 | `draft_content.json` 路径 |
| `draft_name` | 函数参数 | 文件夹名称 |
| `tm_draft_create` | `time.time()` | 当前时间戳（微秒）|
| `draft_id` | `uuid.uuid4()` | 新生成的 UUID |
| 其他字段 | 硬编码 | 默认值或模拟值 |

**重要**: 完全不依赖 `draft_meta_info.json` 的内容！

### 3. 时长计算

```python
def _calculate_draft_duration(draft_content_path: str) -> int:
```

**算法**:
1. 读取 `draft_content.json`
2. 遍历所有 `tracks`
3. 检查每个 `segment` 的 `time_range.end`
4. 返回最大的结束时间（毫秒转微秒）

```python
# 示例数据
{
  "tracks": [
    {
      "segments": [
        {
          "time_range": {
            "start": 0,
            "end": 5000  # 毫秒
          }
        }
      ]
    }
  ]
}

# 计算结果: 5000 * 1000 = 5000000 微秒
```

### 4. Assets 大小计算

```python
def _calculate_assets_size(draft_folder_path: str) -> int:
```

**步骤**:
1. 检查 `Assets/` 文件夹是否存在
2. 使用 `os.walk()` 递归遍历
3. 累加所有文件大小
4. 返回总字节数

### 5. 封面查找

```python
def _find_draft_cover(draft_folder_path: str) -> Optional[str]:
```

**查找策略**:
- 文件名模式: `draft_cover`, `cover`, `thumbnail`
- 支持扩展名: `.jpg`, `.jpeg`, `.png`, `.bmp`
- 返回第一个匹配的文件路径

## 数据结构

### root_meta_info 结构

```json
{
  "all_draft_store": [
    {
      "cloud_draft_cover": false,
      "cloud_draft_sync": false,
      "draft_cloud_last_action_download": false,
      "draft_cloud_purchase_info": "",
      "draft_cloud_template_id": "",
      "draft_cloud_tutorial_info": "",
      "draft_cloud_videocut_purchase_info": "",
      "draft_cover": "/path/to/cover.jpg",
      "draft_fold_path": "/path/to/draft/folder",
      "draft_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
      "draft_is_ai_shorts": false,
      "draft_is_cloud_temp_draft": false,
      "draft_is_invisible": false,
      "draft_is_web_article_video": false,
      "draft_json_file": "/path/to/draft_content.json",
      "draft_name": "draft_folder_name",
      "draft_new_version": "",
      "draft_root_path": "/root/path",
      "draft_timeline_materials_size": 1234567,
      "draft_type": "",
      "draft_web_article_video_enter_from": "",
      "streaming_edit_draft_ready": true,
      "tm_draft_cloud_completed": "1234567890123456",
      "tm_draft_cloud_entry_id": 1234567890,
      "tm_draft_cloud_modified": 1234567890123456,
      "tm_draft_cloud_parent_entry_id": -1,
      "tm_draft_cloud_space_id": 0,
      "tm_draft_cloud_user_id": 0,
      "tm_draft_create": 1234567890123456,
      "tm_draft_modified": 1234567890123456,
      "tm_draft_removed": 0,
      "tm_duration": 5000000
    }
  ],
  "draft_ids": 1,
  "root_path": "/root/path"
}
```

## 错误处理

### 处理策略

1. **文件夹层面**: 跳过无效文件夹，继续处理其他草稿
2. **单个草稿层面**: 记录错误，返回 `None`，不影响其他草稿
3. **聚合报告**: 扫描完成后汇总失败的草稿列表

### 典型错误场景

| 场景 | 处理方式 | 用户提示 |
|------|----------|----------|
| 根目录不存在 | 抛出 `FileNotFoundError` | 明确错误消息 |
| draft_content.json 损坏 | 跳过该草稿，记录错误 | 列出失败的草稿 |
| Assets 文件夹不存在 | 返回大小 0 | 无（正常情况）|
| 封面不存在 | 返回空字符串 | 无（正常情况）|

## 与剪映的兼容性

### 文件格式支持

| 文件 | 格式 | 读取方式 | 支持加密 |
|------|------|----------|----------|
| `draft_content.json` | JSON | 完整读取和解析 | ❌ 不支持 |
| `draft_meta_info.json` | 任意 | 仅检查存在 | ✅ 支持 |

### 版本兼容性

- ✅ **旧版剪映**: draft_meta_info.json 为明文 JSON
- ✅ **新版剪映**: draft_meta_info.json 为加密格式
- ✅ **混合环境**: 可以同时处理加密和非加密草稿

## 性能考虑

### 时间复杂度

- **文件夹扫描**: O(n) - n 为草稿数量
- **Assets 大小计算**: O(m) - m 为素材文件数量
- **总体复杂度**: O(n × m)

### 优化建议

1. **并行处理**: 可以使用多线程处理多个草稿
2. **缓存机制**: 缓存已计算的 Assets 大小
3. **增量更新**: 只处理变更的草稿

## 使用示例

### 基本使用

```python
from src.utils.draft_meta_manager import create_draft_meta_manager

# 创建管理器实例
manager = create_draft_meta_manager()

# 扫描草稿文件夹
draft_root = r"C:\Users\user\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft"
meta_info = manager.scan_and_generate_meta_info(draft_root)

# 保存 root_meta_info.json
output_path = os.path.join(draft_root, "root_meta_info.json")
manager.save_root_meta_info(meta_info, output_path)

print(f"找到 {meta_info['draft_ids']} 个草稿")
```

### 在 draft_generator 中的集成

```python
class DraftGenerator:
    def _generate_root_meta_info(self):
        """生成 root_meta_info.json"""
        meta_manager = create_draft_meta_manager()
        root_meta_info = meta_manager.scan_and_generate_meta_info(
            self.output_base_dir
        )
        meta_info_path = os.path.join(
            self.output_base_dir, 
            "root_meta_info.json"
        )
        meta_manager.save_root_meta_info(root_meta_info, meta_info_path)
```

## 设计原则

### 1. 单一职责
- 只负责扫描和生成元信息
- 不负责创建或修改草稿内容

### 2. 最小依赖
- 只读取必需的 `draft_content.json`
- 不依赖可能加密或损坏的 `draft_meta_info.json`

### 3. 错误隔离
- 单个草稿错误不影响其他草稿处理
- 提供详细的错误报告

### 4. 向后兼容
- 支持旧版和新版剪映格式
- 优雅处理缺失或损坏的文件

## 未来改进方向

1. **性能优化**: 并行处理多个草稿
2. **增量更新**: 只处理变更的草稿
3. **缓存机制**: 减少重复计算
4. **更多元数据**: 从 draft_content.json 提取更多信息
5. **解密支持**: 如果获得解密方法，可选择性读取加密内容

## 总结

`draft_meta_manager` 的核心设计理念是：
- ✅ 从可靠的来源（draft_content.json、文件系统）获取信息
- ✅ 避免依赖不可靠的来源（可能加密或损坏的 draft_meta_info.json）
- ✅ 优雅处理各种异常情况
- ✅ 提供清晰的错误报告和用户指导

这种设计使系统能够稳定处理各种剪映版本和草稿状态，包括加密的草稿文件。
