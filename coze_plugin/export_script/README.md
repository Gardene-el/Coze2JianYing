# Export Script Tool

导出 `/tmp/coze2jianying.py` 脚本文件的Coze工具函数。

## 功能描述

本工具用于从 `/tmp` 目录中读取 `coze2jianying.py` 脚本文件，将其内容作为字符串返回。支持可选的文件内容清空功能，可在导出后清空源文件。

## 核心特性

### 脚本文件导出
- **读取文件**: 从 `/tmp/coze2jianying.py` 读取完整的脚本内容
- **内容返回**: 将脚本内容作为字符串返回
- **文件信息**: 返回文件大小信息

### 可选的内容清空
- **清空选项**: 支持导出后清空文件内容
- **安全操作**: 仅在成功读取后才清空
- **状态报告**: 清空操作的详细状态反馈

### 完整的错误处理
- 文件不存在检测
- 文件权限验证
- 编码错误处理
- 详细的错误信息

## 输入参数

### Input 类型定义
```python
class Input(NamedTuple):
    clear_content: bool = False  # 是否在导出后清空文件内容
```

### 参数详细说明

#### clear_content (boolean)
- **描述**: 是否在成功导出后清空脚本文件的内容
- **默认值**: `false`
- **true**: 导出后将文件内容清空（写入空字符串）
- **false**: 保留文件内容不变

## 输出结果

### 返回值格式

返回 Dict[str, Any] 格式（确保 Coze 平台正确序列化为 JSON 对象）：

```python
{
    "script_content": str,  # 脚本文件内容
    "file_size": int,       # 文件大小（字符数）
    "success": bool,        # 操作是否成功
    "message": str          # 详细状态消息
}
```

### 输出字段说明

#### script_content (string)
- **描述**: 脚本文件的完整内容
- **格式**: UTF-8编码的文本字符串
- **用途**: Python脚本代码，可直接执行或分析
- **失败时**: 返回空字符串

#### file_size (integer)
- **描述**: 文件内容的大小（字符数）
- **范围**: 0 到文件的实际字符数
- **用途**: 用于判断文件是否为空或评估内容量
- **失败时**: 返回 0

#### success (boolean)
- **描述**: 操作是否成功完成
- **true**: 成功读取文件内容
- **false**: 读取失败（文件不存在、权限错误等）

#### message (string)
- **描述**: 详细的操作结果描述
- **成功示例**: "成功导出脚本文件，大小: 1234 字符; 文件内容已清空"
- **失败示例**: "脚本文件不存在: /tmp/coze2jianying.py"

## 使用示例

### 基本导出（保留文件内容）

#### 输入
```json
{
  "clear_content": false
}
```

#### 预期输出
```json
{
  "script_content": "#!/usr/bin/env python3\n# Coze to JianYing Script\n...",
  "file_size": 1234,
  "success": true,
  "message": "成功导出脚本文件，大小: 1234 字符"
}
```

### 导出并清空文件

#### 输入
```json
{
  "clear_content": true
}
```

#### 预期输出
```json
{
  "script_content": "#!/usr/bin/env python3\n# Coze to JianYing Script\n...",
  "file_size": 1234,
  "success": true,
  "message": "成功导出脚本文件，大小: 1234 字符; 文件内容已清空"
}
```

### 在Coze工作流中的使用

#### 基本导出
```json
{
  "tool": "export_script",
  "input": {
    "clear_content": false
  },
  "output_variable": "exported_script"
}
```

#### 导出后清理
```json
{
  "tool": "export_script",
  "input": {
    "clear_content": true
  },
  "output_variable": "exported_script"
}
```

#### 在工作流中访问导出内容
```json
{
  "tool": "some_next_tool",
  "input": {
    "script_content": "{{exported_script.script_content}}",
    "file_size": "{{exported_script.file_size}}"
  }
}
```

## 错误处理

### 常见错误情况

#### 文件不存在
```json
{
  "script_content": "",
  "file_size": 0,
  "success": false,
  "message": "脚本文件不存在: /tmp/coze2jianying.py"
}
```

**原因**: 
- 文件尚未创建
- 文件已被删除
- 路径错误

**解决方案**:
- 检查文件是否已生成
- 确认文件路径正确
- 在工作流中先创建文件再导出

#### 权限错误
```json
{
  "script_content": "",
  "file_size": 0,
  "success": false,
  "message": "无权限读取文件: /tmp/coze2jianying.py"
}
```

**原因**:
- 文件权限设置不正确
- 进程没有读取权限

**解决方案**:
- 检查文件权限
- 确保工具有足够的访问权限

#### 编码错误
```json
{
  "script_content": "",
  "file_size": 0,
  "success": false,
  "message": "文件编码错误，无法以UTF-8读取: /tmp/coze2jianying.py"
}
```

**原因**:
- 文件不是UTF-8编码
- 文件包含二进制内容

**解决方案**:
- 确保文件是UTF-8编码的文本文件
- 确认文件不是二进制文件

#### 清空文件失败
```json
{
  "script_content": "#!/usr/bin/env python3\n...",
  "file_size": 1234,
  "success": true,
  "message": "成功导出脚本文件，大小: 1234 字符; 清空文件失败: 无权限清空文件"
}
```

**说明**:
- 读取操作成功（success=true）
- 但清空操作失败
- 仍然返回完整的脚本内容
- 消息中包含清空失败的原因

## 技术实现

### 文件路径
- **固定路径**: `/tmp/coze2jianying.py`
- **目录**: Coze平台的临时文件目录 `/tmp`
- **文件名**: `coze2jianying.py`

### 文件操作
```python
# 读取文件
with open("/tmp/coze2jianying.py", 'r', encoding='utf-8') as f:
    content = f.read()

# 清空文件（可选）
with open("/tmp/coze2jianying.py", 'w', encoding='utf-8') as f:
    f.write("")
```

### 错误处理流程
1. **存在性检查**: 检查文件是否存在
2. **类型检查**: 确认路径是文件而非目录
3. **读取文件**: 尝试以UTF-8编码读取
4. **捕获异常**: 处理权限、编码等错误
5. **清空操作**: 如果请求，清空文件内容
6. **状态返回**: 返回详细的操作状态

### 清空逻辑
- 仅在成功读取文件后执行
- 使用写模式打开文件
- 写入空字符串
- 独立的错误处理，不影响读取结果

## 使用场景

### 1. 脚本生成与导出工作流
```
生成工具 → 写入 /tmp/coze2jianying.py → export_script → 使用脚本内容
```

**应用**:
- 自动生成Python脚本
- 导出用于执行或分析
- 清理临时文件

### 2. 多次导出场景
```
第一次导出: clear_content=false（保留文件）
第二次导出: clear_content=false（再次读取）
最后导出:   clear_content=true（清理）
```

**应用**:
- 多个工作流需要同一脚本
- 最后一个工作流负责清理

### 3. 脚本验证工作流
```
生成脚本 → export_script → 验证工具 → 反馈
```

**应用**:
- 验证生成的脚本语法
- 检查脚本内容
- 安全审查

## 与其他工具的集成

### 与 create_draft 工具配合
```json
// 1. 创建草稿
{
  "tool": "create_draft",
  "output_variable": "draft"
}

// 2. 生成脚本（假设的工具）
{
  "tool": "generate_script",
  "input": {
    "draft_id": "{{draft.draft_id}}"
  },
  "output_variable": "script_generated"
}

// 3. 导出脚本
{
  "tool": "export_script",
  "input": {
    "clear_content": true
  },
  "output_variable": "exported_script"
}
```

### 与其他导出工具的区别

| 工具 | 导出内容 | 来源 | 清理选项 |
|------|---------|------|----------|
| export_drafts | 草稿JSON数据 | /tmp/jianying_assistant/drafts/ | remove_temp_files |
| export_script | Python脚本 | /tmp/coze2jianying.py | clear_content |

## 注意事项

### Coze平台限制
- **文件系统**: 依赖 `/tmp` 目录
- **文件大小**: 注意Coze变量大小限制
- **生命周期**: `/tmp` 文件可能被定期清理

### 性能考虑
- **文件大小**: 大文件读取可能耗时较长
- **编码处理**: UTF-8解码可能影响性能
- **清空操作**: 额外的I/O操作

### 数据安全
- **敏感信息**: 避免在脚本中包含密码、密钥等敏感数据
- **清理策略**: 使用 `clear_content=true` 及时清理临时文件
- **权限控制**: 确保文件权限设置正确

### 最佳实践

1. **检查文件存在**: 在导出前确认文件已生成
```json
// 添加条件判断
{
  "condition": "{{script_generated.success}}",
  "then": {
    "tool": "export_script"
  }
}
```

2. **错误处理**: 始终检查 `success` 字段
```python
if exported_script.success:
    # 使用 exported_script.script_content
else:
    # 处理错误: exported_script.message
```

3. **清理策略**: 最后一次使用时清空
```json
{
  "tool": "export_script",
  "input": {
    "clear_content": true  // 工作流结束前清理
  }
}
```

4. **文件大小检查**: 验证导出的内容
```python
if exported_script.file_size == 0:
    # 文件为空，可能有问题
```

### 故障排除

#### 问题: 文件不存在
**症状**: `"脚本文件不存在: /tmp/coze2jianying.py"`

**排查步骤**:
1. 检查上游工具是否成功创建文件
2. 确认文件路径拼写正确
3. 检查工作流执行顺序

#### 问题: 清空失败但读取成功
**症状**: `"成功导出...; 清空文件失败: ..."`

**说明**: 
- 这不是严重错误
- 脚本内容已成功导出
- 只是清理操作失败

**处理**:
- 可以忽略清空失败
- 或稍后手动清理
- 检查文件权限

#### 问题: 文件太大
**症状**: 导出成功但无法在Coze中使用

**解决方案**:
1. 优化脚本大小
2. 分段处理
3. 使用外部存储

## 技术规格

### 文件约束
- **路径**: 固定为 `/tmp/coze2jianying.py`
- **编码**: UTF-8
- **类型**: 纯文本Python脚本
- **大小**: 受Coze平台变量大小限制

### 操作约束
- **原子性**: 读取和清空是两个独立操作
- **并发**: 不支持并发访问（文件系统限制）
- **持久性**: 依赖 `/tmp` 目录生命周期

### 返回值约束
- **script_content**: 字符串，可能很大
- **file_size**: 整数，以字符数计
- **success**: 布尔值
- **message**: UTF-8字符串

这个工具提供了简单但完整的脚本导出功能，适合在Coze工作流中管理和传递Python脚本内容。通过 `clear_content` 选项，可以灵活控制临时文件的清理时机。
