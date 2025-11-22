# Write Script Tool

向 `/tmp/coze2jianying.py` 脚本文件写入内容的 Coze 工具函数。

## 功能描述

本工具用于向 `/tmp` 目录中的 `coze2jianying.py` 脚本文件写入内容。支持追加（append）和覆盖（overwrite）两种写入模式，是 `export_script` 工具的互补工具。

## 核心特性

### 灵活的写入模式
- **追加模式（append）**: 在文件末尾追加新内容
- **覆盖模式（overwrite）**: 清空文件并写入新内容
- **自动换行**: 可选择是否在内容末尾添加换行符

### 自动文件管理
- **文件创建**: 如果文件不存在，自动创建
- **初始化内容**: 新建文件包含基本的 Python 文件头注释
- **文件大小跟踪**: 返回写入字节数和文件总大小

### 完整的错误处理
- 内容验证（不能为空）
- 模式验证（必须是 append 或 overwrite）
- 文件权限验证
- 详细的错误信息

## 输入参数

### Input 类型定义
```python
class Input(NamedTuple):
    content: str                # 要写入的内容
    mode: str = "append"        # 写入模式：append 或 overwrite
    add_newline: bool = True    # 是否在内容末尾添加换行符
```

### 参数详细说明

#### content (string, 必需)
- **描述**: 要写入到脚本文件的内容
- **格式**: 任意文本字符串，通常是 Python 代码
- **验证**: 不能为空或 None
- **示例**: 
  ```python
  "# 这是一条注释\nprint('Hello, World!')"
  ```

#### mode (string, 可选)
- **描述**: 写入模式
- **默认值**: `"append"`
- **可选值**:
  - `"append"`: 追加模式，在文件末尾添加内容
  - `"overwrite"`: 覆盖模式，清空文件后写入新内容
- **注意**: 使用 overwrite 会丢失文件中的所有现有内容

#### add_newline (boolean, 可选)
- **描述**: 是否在写入内容的末尾自动添加换行符
- **默认值**: `true`
- **true**: 如果内容不以换行符结尾，自动添加 `\n`
- **false**: 不添加换行符，保持内容原样
- **用途**: 确保每次写入的内容在独立的行上

## 输出结果

### 返回值格式

返回 Dict[str, Any] 格式（确保 Coze 平台正确序列化为 JSON 对象）：

```python
{
    "success": bool,           # 操作是否成功
    "message": str,            # 详细状态消息
    "bytes_written": int,      # 本次写入的字节数
    "total_file_size": int     # 文件的总大小（字节）
}
```

### 输出字段说明

#### success (boolean)
- **描述**: 操作是否成功完成
- **true**: 内容成功写入文件
- **false**: 写入失败（内容为空、权限错误、无效模式等）

#### message (string)
- **描述**: 详细的操作结果描述
- **成功示例**: "成功追加内容到脚本文件，写入: 128 字节，文件总大小: 1024 字节"
- **失败示例**: "写入内容不能为空"

#### bytes_written (integer)
- **描述**: 本次操作写入的字节数
- **范围**: 0 到实际写入的字节数
- **用途**: 评估写入的数据量
- **失败时**: 返回 0

#### total_file_size (integer)
- **描述**: 写入操作完成后文件的总大小（字节）
- **用途**: 监控文件大小，避免超过 Coze 平台限制
- **失败时**: 返回当前文件大小（如果文件存在）

## 使用示例

### 基本追加写入

#### 输入
```json
{
  "content": "# 新增的 API 调用\nresult = api_call()\n",
  "mode": "append",
  "add_newline": true
}
```

#### 预期输出
```json
{
  "success": true,
  "message": "成功追加内容到脚本文件，写入: 45 字节，文件总大小: 1024 字节",
  "bytes_written": 45,
  "total_file_size": 1024
}
```

### 覆盖写入（重置文件）

#### 输入
```json
{
  "content": "#!/usr/bin/env python3\n# 新的脚本开始\n",
  "mode": "overwrite",
  "add_newline": true
}
```

#### 预期输出
```json
{
  "success": true,
  "message": "成功覆盖写入内容到脚本文件，写入: 45 字节，文件总大小: 45 字节",
  "bytes_written": 45,
  "total_file_size": 45
}
```

### 不添加换行符

#### 输入
```json
{
  "content": "from datetime import datetime",
  "mode": "append",
  "add_newline": false
}
```

#### 预期输出
```json
{
  "success": true,
  "message": "成功追加内容到脚本文件，写入: 28 字节，文件总大小: 1052 字节",
  "bytes_written": 28,
  "total_file_size": 1052
}
```

### 在 Coze 工作流中的使用

#### 初始化脚本文件
```json
{
  "tool": "write_script",
  "input": {
    "content": "#!/usr/bin/env python3\n# Coze 生成的脚本\n\nimport asyncio\nfrom app.schemas.segment_schemas import *\n\n",
    "mode": "overwrite",
    "add_newline": true
  },
  "output_variable": "init_result"
}
```

#### 追加 API 调用代码
```json
{
  "tool": "write_script",
  "input": {
    "content": "# 创建草稿\ndraft_id = create_draft(name='我的项目')\n",
    "mode": "append",
    "add_newline": true
  },
  "output_variable": "append_result"
}
```

#### 添加注释
```json
{
  "tool": "write_script",
  "input": {
    "content": "# ===== 添加媒体资源 =====\n",
    "mode": "append",
    "add_newline": true
  },
  "output_variable": "comment_result"
}
```

#### 工作流中检查结果
```json
{
  "condition": "{{append_result.success}}",
  "then": {
    "tool": "next_tool",
    "input": {
      "file_size": "{{append_result.total_file_size}}"
    }
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
  "message": "写入内容不能为空",
  "bytes_written": 0,
  "total_file_size": 1024
}
```

**原因**: 
- content 参数为空字符串
- content 参数为 null/None

**解决方案**:
- 确保 content 参数包含有效内容
- 检查内容来源是否正确

#### 无效的写入模式
```json
{
  "success": false,
  "message": "无效的写入模式: invalid，必须是 'append' 或 'overwrite'",
  "bytes_written": 0,
  "total_file_size": 1024
}
```

**原因**:
- mode 参数不是 "append" 或 "overwrite"
- mode 参数拼写错误

**解决方案**:
- 使用正确的模式值："append" 或 "overwrite"
- 检查参数拼写

#### 权限错误
```json
{
  "success": false,
  "message": "无权限写入文件: /tmp/coze2jianying.py",
  "bytes_written": 0,
  "total_file_size": 1024
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

### 文件操作

#### 追加模式
```python
# 以追加模式打开文件
with open("/tmp/coze2jianying.py", 'a', encoding='utf-8') as f:
    f.write(content + "\n")  # 如果 add_newline=True
```

#### 覆盖模式
```python
# 以写入模式打开文件（清空现有内容）
with open("/tmp/coze2jianying.py", 'w', encoding='utf-8') as f:
    f.write(content + "\n")  # 如果 add_newline=True
```

### 文件初始化
当文件不存在时，自动创建并写入初始内容：
```python
#!/usr/bin/env python3
# Coze2JianYing 脚本文件
# 此文件由 Coze 工具自动生成和更新

```

### 错误处理流程
1. **参数验证**: 检查 content 不为空，mode 有效
2. **文件存在性**: 如果文件不存在，创建新文件
3. **权限检查**: 尝试打开文件进行写入
4. **写入操作**: 根据模式写入内容
5. **大小计算**: 计算写入字节数和总文件大小
6. **状态返回**: 返回详细的操作状态

## 使用场景

### 1. 脚本生成工作流
```
初始化脚本 (overwrite) → 添加 imports → 添加函数 (append) → 添加主逻辑 (append)
```

**应用**:
- 分步骤构建复杂的 Python 脚本
- 每个工具负责添加特定部分
- 最后使用 export_script 导出

### 2. 逐步构建 API 调用序列
```
write_script (init) → create_draft → write_script (append) → add_videos → write_script (append)
```

**应用**:
- 记录每个 API 调用
- 构建可重放的操作序列
- 支持脚本调试和分析

### 3. 添加注释和分隔符
```
write_script (comment) → 业务操作 → write_script (separator) → 下一组操作
```

**应用**:
- 提高脚本可读性
- 组织代码结构
- 便于后续维护

### 4. 重置和重新开始
```
write_script (overwrite, "") → 清空文件 → 重新开始新的工作流
```

**应用**:
- 清理旧的脚本内容
- 开始全新的操作序列
- 避免旧内容干扰

## 与其他工具的集成

### 与 export_script 配合使用

#### 写入 → 导出工作流
```json
// 1. 初始化脚本
{
  "tool": "write_script",
  "input": {
    "content": "#!/usr/bin/env python3\nimport asyncio\n",
    "mode": "overwrite"
  }
}

// 2. 追加业务逻辑
{
  "tool": "write_script",
  "input": {
    "content": "# 创建草稿\nresult = create_draft()\n",
    "mode": "append"
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

### 与 raw_tools 的区别

| 工具类型 | 写入方式 | 内容来源 | 灵活性 |
|---------|---------|---------|--------|
| write_script | 手动控制 | 用户提供 | 高（任意内容）|
| raw_tools | 自动生成 | API 调用 | 低（固定格式）|

**write_script** 提供了手动控制的灵活性，适合：
- 添加自定义注释
- 插入调试代码
- 修改脚本结构
- 初始化文件内容

**raw_tools** 自动生成标准化的 API 调用代码，适合：
- 记录 API 调用序列
- 生成可重放的操作
- 保持代码格式一致

## 注意事项

### Coze 平台限制
- **文件系统**: 依赖 `/tmp` 目录
- **文件大小**: 注意 Coze 平台的文件大小限制（512MB）
- **生命周期**: `/tmp` 文件可能被定期清理

### 性能考虑
- **频繁写入**: 过多的追加操作可能影响性能
- **大文件**: 文件过大会增加读写时间
- **编码**: 使用 UTF-8 编码处理文本

### 数据安全
- **覆盖模式**: 使用 overwrite 会永久丢失原有内容
- **敏感信息**: 避免写入密码、密钥等敏感数据
- **内容验证**: 确保写入的内容格式正确

### 最佳实践

1. **初始化文件**: 工作流开始时使用 overwrite 清空旧内容
```json
{
  "tool": "write_script",
  "input": {
    "content": "#!/usr/bin/env python3\n# 新的脚本\n",
    "mode": "overwrite"
  }
}
```

2. **添加注释分隔**: 使用注释组织代码结构
```json
{
  "tool": "write_script",
  "input": {
    "content": "# ===== 第一步：初始化 =====\n",
    "mode": "append"
  }
}
```

3. **检查文件大小**: 定期监控文件大小
```python
if write_result.total_file_size > 1000000:  # 1MB
    # 文件过大，考虑优化或分割
```

4. **错误处理**: 始终检查 success 字段
```python
if not write_result.success:
    logger.error(f"写入失败: {write_result.message}")
    # 采取补救措施
```

5. **最后清理**: 工作流结束时导出并清空
```json
{
  "tool": "export_script",
  "input": {
    "clear_content": true  // 导出后清理
  }
}
```

### 故障排除

#### 问题: 内容没有写入
**症状**: success=true 但文件内容未变化

**排查步骤**:
1. 检查 bytes_written 是否大于 0
2. 验证 mode 是否正确
3. 确认文件路径是否正确
4. 检查是否有其他工具覆盖了内容

#### 问题: 文件内容被意外清空
**症状**: 原有内容丢失

**原因**: 
- 错误使用了 overwrite 模式
- 其他工具清空了文件

**预防**:
- 谨慎使用 overwrite 模式
- 在重要操作前导出备份

#### 问题: 换行符问题
**症状**: 内容连在一起或有多余空行

**解决方案**:
- 使用 add_newline=true 确保每次追加独立一行
- 在 content 中明确控制换行符
- 测试内容格式是否正确

## 技术规格

### 文件约束
- **路径**: 固定为 `/tmp/coze2jianying.py`
- **编码**: UTF-8
- **类型**: 纯文本 Python 脚本
- **大小**: 受 Coze 平台限制（建议 < 10MB）

### 操作约束
- **原子性**: 每次写入是原子操作
- **并发**: 不建议并发写入同一文件
- **持久性**: 依赖 `/tmp` 目录生命周期

### 返回值约束
- **success**: 布尔值
- **message**: UTF-8 字符串
- **bytes_written**: 非负整数
- **total_file_size**: 非负整数

## 工作流示例

### 完整的脚本生成流程

```json
{
  "workflow": "generate_complete_script",
  "steps": [
    {
      "step": 1,
      "description": "初始化脚本文件",
      "tool": "write_script",
      "input": {
        "content": "#!/usr/bin/env python3\n# Coze 自动生成的剪映脚本\n\nimport asyncio\nfrom app.schemas.segment_schemas import *\n\n",
        "mode": "overwrite"
      }
    },
    {
      "step": 2,
      "description": "添加创建草稿代码",
      "tool": "write_script",
      "input": {
        "content": "# 创建新草稿\ndraft_id = '{{uuid}}'\nprint(f'创建草稿: {draft_id}')\n",
        "mode": "append"
      }
    },
    {
      "step": 3,
      "description": "添加分隔注释",
      "tool": "write_script",
      "input": {
        "content": "\n# ===== 添加媒体资源 =====\n",
        "mode": "append"
      }
    },
    {
      "step": 4,
      "description": "添加视频代码",
      "tool": "write_script",
      "input": {
        "content": "# 添加视频\nvideo_url = '{{video_url}}'\nadd_video(draft_id, video_url)\n",
        "mode": "append"
      }
    },
    {
      "step": 5,
      "description": "导出并清理",
      "tool": "export_script",
      "input": {
        "clear_content": true
      },
      "output_variable": "final_script"
    }
  ]
}
```

这个工具提供了灵活的脚本内容写入功能，是构建完整 Coze 工作流的重要组成部分。通过与 `export_script` 配合使用，可以实现完整的脚本生成、修改和导出流程。
