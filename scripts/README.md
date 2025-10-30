# Scripts 目录

## 📦 概述

此目录包含项目的实用工具脚本，这些脚本可以独立运行，不依赖复杂的包管理结构。

## 🛠️ 可用脚本

### coze_json_formatter.py

**功能**: Coze JSON 格式化工具

将 Coze 输出的特殊格式（包含 output 字段的字符串 JSON）转换为标准 JSON 格式。

**使用方法**:

```bash
# 显示帮助信息
python scripts/coze_json_formatter.py --help

# 转换单个文件（自动生成输出文件名）
python scripts/coze_json_formatter.py coze_example_for_paste_context.json

# 指定输出文件名
python scripts/coze_json_formatter.py input.json output.json

# 批量转换当前目录下的所有匹配文件
python scripts/coze_json_formatter.py --batch

# 批量转换指定目录和模式
python scripts/coze_json_formatter.py --batch ./data "*coze*.json"
```

**作为 Python 模块使用**:

```python
import sys
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from coze_json_formatter import convert_coze_to_standard_format

# 转换文件
output_file = convert_coze_to_standard_format('input.json')
print(f"转换完成: {output_file}")
```

**主要功能**:
- ✅ 自动提取并解析 output 字段
- ✅ 格式验证
- ✅ 批量转换
- ✅ 智能命名
- ✅ 详细日志
- ✅ UTF-8 编码支持

### test_coze_json_formatter.py

**功能**: 测试 coze_json_formatter.py 的功能

**使用方法**:

```bash
python scripts/test_coze_json_formatter.py
```

**测试内容**:
- 单文件转换
- 提取 output 字段
- 自定义输出文件名
- 与 DraftGenerator 集成

## 📊 输入输出格式

### 输入格式（Coze 特殊格式）

```json
{
  "output": "{\"format_version\":\"1.0\",\"drafts\":[...]}"
}
```

- `output` 字段是一个字符串
- 字符串内容是转义的 JSON

### 输出格式（标准格式）

```json
{
  "format_version": "1.0",
  "export_type": "single_draft",
  "draft_count": 1,
  "drafts": [...]
}
```

- 标准的 JSON 对象
- 可直接用于剪映草稿生成器

## ⚠️ 注意事项

- 所有脚本使用 UTF-8 编码
- 支持中文和特殊字符
- 转换不会修改原始文件
- 批量转换时自动跳过已转换的文件
- 建议在项目根目录运行命令

## 🔧 添加新脚本

如需添加新的工具脚本：

1. 在 `scripts/` 目录下创建新的 Python 文件
2. 添加详细的文档字符串说明功能
3. 提供 `--help` 选项显示使用方法
4. 更新此 README 文件
5. 创建对应的测试脚本（可选）

## 📚 相关文档

- [项目主 README](../README.md)
- [Coze 输出转换器详细指南](../docs/draft_generator/COZE_OUTPUT_CONVERTER_GUIDE.md)
