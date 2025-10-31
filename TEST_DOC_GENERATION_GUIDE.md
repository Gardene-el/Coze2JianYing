# 文档生成工具测试指南

本文件提供了使用文档生成脚本的测试指南和示例。

## 快速测试

运行测试脚本以验证文档生成功能：

```bash
python test_doc_generation.py
```

测试内容包括：
1. 工具名称提取
2. 模块文档字符串提取
3. 输入参数解析
4. 完整文档生成
5. 文件写入和读取

## 使用示例

### 示例 1: 为单个工具生成文档

```bash
# 为 create_draft 工具生成文档
python scripts/generate_tool_doc.py coze_plugin/tools/create_draft/handler.py

# 查看生成的文档
cat coze_plugin/tools/create_draft/create_draft_generated.md
```

### 示例 2: 为所有工具生成文档

```bash
# 扫描并生成所有工具的文档
python scripts/scan_and_generate_docs.py

# 文档将生成在各工具的目录中，文件名为 {tool_name}_generated.md
```

### 示例 3: 将文档输出到指定目录

```bash
# 将所有文档生成到 /tmp/docs 目录
python scripts/scan_and_generate_docs.py coze_plugin/tools /tmp/docs

# 查看生成的文档
ls -la /tmp/docs/
```

## 生成的文档格式

文档按照以下格式生成：

```markdown
# 工具函数 Tool Name

工具名称：tool_name
工具描述：[从 handler.py 模块文档字符串提取的描述]

## 输入参数

\`\`\`python
class Input(NamedTuple):
    param1: type = default_value  # 参数注释（如果有）
    param2: type = default_value  # 参数注释（如果有）
\`\`\`
```

### 示例：create_draft 工具的文档

```markdown
# 工具函数 Create Draft

工具名称：create_draft
工具描述：Create Draft Tool Handler
Creates a new draft with basic project settings and returns a UUID for future reference.
The draft data is stored in /tmp directory with UUID as folder name.

## 输入参数

\`\`\`python
class Input(NamedTuple):
    draft_name: str = 'Coze剪映项目'
    width: int = 1920
    height: int = 1080
    fps: int = 30
\`\`\`
```

## 测试验证

### 1. 运行完整测试

```bash
python test_doc_generation.py
```

预期输出：
```
🧪 Testing Documentation Generation Scripts
================================================================================
...
🎉 All tests passed!
```

### 2. 手动验证单个工具

```bash
# 生成文档到临时文件
python scripts/generate_tool_doc.py coze_plugin/tools/create_draft/handler.py /tmp/test.md

# 查看生成的文档
cat /tmp/test.md

# 检查文档内容
grep "工具函数 Create Draft" /tmp/test.md
grep "工具名称：create_draft" /tmp/test.md
grep "class Input(NamedTuple):" /tmp/test.md
```

### 3. 批量生成测试

```bash
# 生成到临时目录以避免修改项目文件
python scripts/scan_and_generate_docs.py coze_plugin/tools /tmp/test_docs

# 检查生成的文件数量
ls /tmp/test_docs/*.md | wc -l

# 预期：13 个文档文件（对应 13 个工具）
```

## 注意事项

1. **不修改原文件**: 脚本只读取 handler.py，不会修改任何现有文件
2. **UTF-8 编码**: 所有文件使用 UTF-8 编码，支持中文和特殊字符
3. **独立运行**: 脚本可以独立运行，不依赖复杂的包管理
4. **安全测试**: 使用 /tmp 目录进行测试，避免污染项目文件

## 故障排除

### 问题：找不到 handler.py 文件

确保从项目根目录运行命令：
```bash
cd /path/to/Coze2JianYing
python scripts/generate_tool_doc.py coze_plugin/tools/create_draft/handler.py
```

### 问题：无法导入 generate_tool_doc 模块

检查 Python 路径：
```python
import sys
from pathlib import Path
script_dir = Path(__file__).parent / 'scripts'
sys.path.insert(0, str(script_dir))
```

### 问题：生成的文档格式不正确

检查 handler.py 文件格式：
1. 确保有模块级别的文档字符串（用 """ """ 包围）
2. 确保有 `class Input(NamedTuple):` 定义
3. 参数使用类型注解格式：`param_name: type = default_value`

## 相关文档

- [Scripts 目录 README](scripts/README.md)
- [Coze 插件开发指南](coze_plugin/README.md)
- [项目主 README](README.md)
