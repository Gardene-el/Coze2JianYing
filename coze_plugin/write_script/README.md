# Write Script Tool

向 `/tmp/coze2jianying.py` 脚本文件追加写入内容的 Coze 工具函数。

## 功能描述

本工具用于向 `/tmp` 目录中的 `coze2jianying.py` 脚本文件追加内容。采用与 `raw_tools` 中各个 handler 函数相同的写入方式，是 `export_script` 工具的互补工具。

## 核心特性

### 简洁的追加写入
- **追加模式**: 始终在文件末尾追加新内容，与 raw_tools 保持一致
- **自动换行**: 自动在内容前后添加换行符，确保格式正确

### 智能内容格式化
- **转义字符处理**: 自动将 `\n` 转义字符转换为实际换行符
- **空行清理**: 移除开头和结尾的多余空行
- **空行压缩**: 将连续 3 个以上的空行压缩为 2 个空行
- **Coze 兼容**: 处理从 Coze 平台传递的转义字符串

### 自动文件管理
- **文件创建**: 如果文件不存在，自动创建
- **初始化内容**: 新建文件包含标准的 Python 文件头注释和导入语句
- **与 raw_tools 一致**: 使用相同的文件初始化模板

### 完整的错误处理
- 内容验证（不能为空）
- 文件权限验证
- 详细的错误信息

## 输入参数

### Input 类型定义
```python
class Input(NamedTuple):
    content: str  # 要追加的内容
```

### 参数详细说明

#### content (string, 必需)
- **描述**: 要追加到脚本文件的内容
- **格式**: 任意文本字符串，通常是 Python 代码或注释
- **验证**: 不能为空或 None
- **自动格式化**: 
  - 转义的 `\n` 会被转换为实际换行符
  - 多余的空行会被清理
  - 从 Coze 传递的转义字符串会被正确处理
- **示例**: 
  ```python
  # 直接使用换行符
  "# API 调用: create_draft\ndraft_id = 'abc123'"
  
  # 或使用转义字符串（从 Coze 传递）
  "\\n\\n# API 调用: create_draft\\n# 时间: 2025-11-22\\n\\ndraft_id = 'abc123'"
  # 上述两种方式都会被正确格式化
  ```

## 输出结果

### 返回值格式

返回 Dict[str, Any] 格式（确保 Coze 平台正确序列化为 JSON 对象）：

```python
{
    "success": bool,  # 操作是否成功
    "message": str,   # 详细状态消息
}
```

### 输出字段说明

#### success (boolean)
- **描述**: 操作是否成功完成
- **true**: 内容成功追加到文件
- **false**: 写入失败（内容为空、权限错误等）

#### message (string)
- **描述**: 详细的操作结果描述
- **成功示例**: "成功追加内容到脚本文件"
- **失败示例**: "写入内容不能为空"

## 使用示例

### 基本追加写入

#### 输入
```json
{
  "content": "# API 调用: create_draft\ndraft_id = 'abc123'"
}
```

#### 预期输出
```json
{
  "success": true,
  "message": "成功追加内容到脚本文件"
}
```

### 追加代码注释

#### 输入
```json
{
  "content": "# ===== 添加媒体资源 ====="
}
```

#### 预期输出
```json
{
  "success": true,
  "message": "成功追加内容到脚本文件"
}
```

### 在 Coze 工作流中的使用

#### 追加 API 调用代码
```json
{
  "tool": "write_script",
  "input": {
    "content": "# 创建草稿\ndraft_id = create_draft(name='我的项目')"
  },
  "output_variable": "append_result"
}
```

#### 添加分隔注释
```json
{
  "tool": "write_script",
  "input": {
    "content": "# ===== 添加媒体资源 ====="
  },
  "output_variable": "comment_result"
}
```

#### 工作流中检查结果
```json
{
  "condition": "{{append_result.success}}",
  "then": {
    "tool": "next_tool"
  },
  "else": {
    "tool": "error_handler",
    "input": {
      "error_message": "{{append_result.message}}"
    }
  }
}
```

## 错误处理

### 常见错误情况

#### 内容为空
```json
{
  "success": false,
  "message": "写入内容不能为空"
}
```

**原因**: 
- content 参数为空字符串
- content 参数为 null/None

**解决方案**:
- 确保 content 参数包含有效内容
- 检查内容来源是否正确

#### 权限错误
```json
{
  "success": false,
  "message": "写入脚本时发生意外错误: [Permission denied]"
}
```

**原因**:
- 文件权限设置不正确
- 进程没有写入权限

**解决方案**:
- 检查文件权限
- 确保工具有足够的访问权限

## 技术实现

### 文件路径
- **固定路径**: `/tmp/coze2jianying.py`
- **目录**: Coze 平台的临时文件目录 `/tmp`
- **文件名**: `coze2jianying.py`

### 内容格式化

在写入前，内容会经过格式化处理：

```python
def format_content(content: str) -> str:
    """
    格式化输入内容，处理转义字符
    
    - 将 \\n 转义字符转换为实际换行符
    - 移除开头和结尾的多余空行
    - 将连续3个以上的空行压缩为2个空行
    """
    formatted = content.replace('\\n', '\n')
    formatted = formatted.strip('\n')
    while '\n\n\n' in formatted:
        formatted = formatted.replace('\n\n\n', '\n\n')
    return formatted
```

**格式化示例**:

输入（Coze 传递的转义字符串）:
```
\n\n# API 调用: create_draft\n# 时间: 2025-11-22\n\ndraft_id = 'abc123'\n\n\n\n
```

输出（格式化后）:
```python
# API 调用: create_draft
# 时间: 2025-11-22

draft_id = 'abc123'
```

### 文件操作

采用与 `raw_tools` 相同的实现方式：

```python
def ensure_coze2jianying_file() -> str:
    """确保文件存在，不存在则创建"""
    file_path = "/tmp/coze2jianying.py"
    if not os.path.exists(file_path):
        # 创建初始文件内容（与 raw_tools 一致）
        initial_content = """# Coze2JianYing API 调用记录
# 此文件由 Coze 工具自动生成和更新
# 记录所有通过 Coze 工具调用的 API 操作

import asyncio
from app.schemas.segment_schemas import *

# API 调用记录将追加在下方
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)
    return file_path

def append_content_to_file(file_path: str, content: str):
    """追加内容到文件"""
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n" + content + "\n")
```

### 错误处理流程
1. **参数验证**: 检查 content 不为空
2. **文件准备**: 确保文件存在（不存在则创建）
3. **内容追加**: 追加内容到文件末尾
4. **状态返回**: 返回操作状态

## 使用场景

### 1. 添加自定义代码或注释
```
write_script → 添加注释 → write_script → 添加代码
```

**应用**:
- 分步骤构建复杂的 Python 脚本
- 每个工具负责添加特定部分
- 最后使用 export_script 导出

### 2. 添加注释和分隔符
```
write_script → 添加分隔注释 → 业务操作 → write_script → 下一组操作
```

**应用**:
- 提高脚本可读性
- 组织代码结构
- 便于后续维护

## 与其他工具的集成

### 与 export_script 配合使用

#### 写入 → 导出工作流
```json
// 1. 追加注释
{
  "tool": "write_script",
  "input": {
    "content": "# ===== 创建草稿 ====="
  }
}

// 2. 追加业务逻辑
{
  "tool": "write_script",
  "input": {
    "content": "draft_id = create_draft(name='我的项目')"
  }
}

// 3. 导出脚本
{
  "tool": "export_script",
  "input": {
    "clear_content": true
  },
  "output_variable": "final_script"
}
```

### 与 raw_tools 的关系

| 工具类型 | 写入方式 | 内容来源 | 灵活性 |
|---------|---------|---------|--------|
| write_script | 手动控制 | 用户提供 | 高（任意内容）|
| raw_tools | 自动生成 | API 调用 | 低（固定格式）|

**write_script** 提供了手动控制的灵活性，适合：
- 添加自定义注释
- 插入调试代码或辅助代码
- 组织脚本结构

**raw_tools** 自动生成标准化的 API 调用代码，适合：
- 记录 API 调用序列
- 生成可重放的操作
- 保持代码格式一致

两者使用相同的底层实现（`ensure_coze2jianying_file` 和 `append_content_to_file`），保证了一致性。

## 注意事项

### Coze 平台限制
- **文件系统**: 依赖 `/tmp` 目录
- **文件大小**: 注意 Coze 平台的文件大小限制（512MB）
- **生命周期**: `/tmp` 文件可能被定期清理

### 最佳实践

1. **添加注释分隔**: 使用注释组织代码结构
```json
{
  "tool": "write_script",
  "input": {
    "content": "# ===== 第一步：初始化 ====="
  }
}
```

2. **错误处理**: 始终检查 success 字段
```python
if not write_result.success:
    logger.error(f"写入失败: {write_result.message}")
```

3. **最后清理**: 工作流结束时导出并清空
```json
{
  "tool": "export_script",
  "input": {
    "clear_content": true  // 导出后清理
  }
}
```

## 技术规格

### 文件约束
- **路径**: 固定为 `/tmp/coze2jianying.py`
- **编码**: UTF-8
- **类型**: 纯文本 Python 脚本
- **大小**: 受 Coze 平台限制（建议 < 10MB）

### 操作约束
- **追加模式**: 始终追加内容到文件末尾
- **并发**: 不建议并发写入同一文件
- **持久性**: 依赖 `/tmp` 目录生命周期

### 返回值约束
- **success**: 布尔值
- **message**: UTF-8 字符串

## 工作流示例

### 完整的脚本生成流程

```json
{
  "workflow": "generate_script_with_comments",
  "steps": [
    {
      "step": 1,
      "tool": "write_script",
      "input": {
        "content": "# ===== 创建草稿 ====="
      }
    },
    {
      "step": 2,
      "tool": "write_script",
      "input": {
        "content": "draft_id = '{{uuid}}'\nprint(f'创建草稿: {draft_id}')"
      }
    },
    {
      "step": 3,
      "tool": "write_script",
      "input": {
        "content": "# ===== 添加媒体资源 ====="
      }
    },
    {
      "step": 4,
      "tool": "export_script",
      "input": {
        "clear_content": true
      },
      "output_variable": "final_script"
    }
  ]
}
```

这个工具采用与 `raw_tools` 相同的实现方式，提供简洁的内容追加功能。与 `export_script` 配合使用，可以实现完整的脚本生成、修改和导出流程。
