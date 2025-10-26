# Coze 输出格式转换工具

这个工具用于将 Coze 输出的特殊格式（包含 `output` 字段的字符串 JSON）转换为标准的 `sample.json` 格式。

## 📁 文件位置

- **工具文件**: `test_utils/coze_output_converter.py`
- **测试模块**: `test_utils/__init__.py`

## 🎯 功能

### 1. 单文件转换

将单个 Coze 输出文件转换为标准格式。

### 2. 批量转换

批量处理目录中的所有 Coze 输出文件。

### 3. 自动验证

转换后自动验证文件结构是否正确。

## 📖 使用方法

### 方法 1: 命令行使用

#### 转换单个文件

```bash
# 自动生成输出文件名（添加 _converted 后缀）
python test_utils\coze_output_converter.py coze_example_for_paste_context.json

# 指定输出文件名
python test_utils\coze_output_converter.py input.json output.json
```

#### 批量转换

```bash
# 转换当前目录下所有包含 'coze' 的 JSON 文件
python test_utils\coze_output_converter.py --batch

# 指定目录和匹配模式
python test_utils\coze_output_converter.py --batch . "*coze*.json"
python test_utils\coze_output_converter.py --batch ./data "*.json"
```

### 方法 2: 作为 Python 模块使用

```python
import sys
sys.path.append('.')

from test_utils.coze_output_converter import (
    convert_coze_to_standard_format,
    extract_output_from_coze_file,
    validate_conversion,
    batch_convert
)

# 转换单个文件
output_file = convert_coze_to_standard_format(
    'coze_example_for_paste_context.json',
    'output.json'
)

# 提取 output 字段（不保存文件）
data = extract_output_from_coze_file('coze_example.json')

# 验证转换结果
validate_conversion('input.json', 'output.json')

# 批量转换
batch_convert(input_dir='.', pattern='*coze*.json')
```

## 📊 输入输出格式

### 输入格式（Coze 输出）

```json
{
  "output": "{\"format_version\":\"1.0\",\"export_type\":\"single_draft\",\"drafts\":[...]}"
}
```

特点：

- 包含一个 `output` 字段
- `output` 字段的值是一个**字符串**（转义的 JSON）
- 需要两次解析才能得到实际数据

### 输出格式（标准格式）

```json
{
  "format_version": "1.0",
  "export_type": "single_draft",
  "draft_count": 1,
  "drafts": [
    {
      "draft_id": "...",
      "project": {...},
      "tracks": [...]
    }
  ]
}
```

特点：

- 直接是标准的 JSON 对象
- 可以直接被剪映草稿生成器使用
- 格式清晰，易于阅读和编辑

## ✅ 功能特性

### 1. 智能文件名生成

- 如果不指定输出文件名，自动添加 `_converted` 后缀
- 例如：`coze_example.json` → `coze_example_converted.json`

### 2. 自动验证

转换后自动检查：

- ✅ 基本字段是否存在（format_version, export_type, draft_count, drafts）
- ✅ 草稿信息（ID、项目名称、分辨率）
- ✅ 轨道统计（轨道类型、片段数量）

### 3. 批量处理

- 自动跳过已转换的文件
- 显示处理进度
- 统计成功/失败数量

### 4. 详细日志

- 显示文件大小
- 显示转换进度
- 显示验证结果

## 📝 使用示例

### 示例 1: 转换单个文件

```bash
$ python test_utils\coze_output_converter.py coze_example_for_paste_context.json

读取文件: coze_example_for_paste_context.json
output 字段长度: 12986 字符
✅ 成功解析 output 字段
✅ 已保存到: coze_example_for_paste_context_converted.json

============================================================
验证转换结果
============================================================
✅ format_version: 存在
✅ export_type: 存在
✅ draft_count: 存在
✅ drafts: 存在

草稿信息:
  - draft_id: f7a9d782-9d4f-407c-aede-9a889dc52d3e
  - 项目名称: Coze剪映项目
  - 分辨率: 1440x1080
  - 轨道数量: 2
    轨道 1 (audio): 5 个片段
    轨道 2 (text): 5 个片段

============================================================
✅ 验证通过! 转换成功!
============================================================
```

### 示例 2: 批量转换

```bash
$ python test_utils\coze_output_converter.py --batch

找到 3 个文件:
  - coze_example1.json
  - coze_example2.json
  - coze_example3.json

开始批量转换...

处理: coze_example1.json
读取文件: coze_example1.json
✅ 已保存到: coze_example1_converted.json

处理: coze_example2.json
读取文件: coze_example2.json
✅ 已保存到: coze_example2_converted.json

处理: coze_example3.json
读取文件: coze_example3.json
✅ 已保存到: coze_example3_converted.json

批量转换完成: 3/3 个文件转换成功
```

## 🔧 错误处理

### 常见错误

#### 1. 文件不存在

```
❌ 转换失败: [Errno 2] No such file or directory: 'input.json'
```

**解决方案**: 检查文件路径是否正确

#### 2. 缺少 output 字段

```
❌ 转换失败: 文件中未找到 'output' 字段
```

**解决方案**: 确认输入文件是 Coze 输出格式（包含 output 字段）

#### 3. JSON 解析失败

```
❌ 转换失败: Expecting value: line 1 column 1 (char 0)
```

**解决方案**: 检查文件内容是否是有效的 JSON 格式

## 🎨 与剪映草稿生成器集成

转换后的文件可以直接用于剪映草稿生成器：

```python
from src.utils.draft_generator import DraftGenerator

# 转换文件
from test_utils.coze_output_converter import convert_coze_to_standard_format
converted_file = convert_coze_to_standard_format('coze_example.json')

# 生成草稿
generator = DraftGenerator(output_base_dir="./JianyingProjects")
draft_paths = generator.generate_from_file(converted_file)
```

## 📚 相关文档

- [多格式输入指南](../docs/MULTI_FORMAT_INPUT_GUIDE.md)
- [Coze 转换指南](../docs/COZE_CONVERSION_GUIDE.md)
- [素材管理器指南](../docs/MATERIAL_MANAGER_GUIDE.md)

## 💡 提示

1. **保留原文件**: 转换不会修改原始文件，始终生成新文件
2. **格式化输出**: 输出文件会自动格式化（缩进 2 空格），便于阅读
3. **自动跳过**: 批量转换时会自动跳过已转换的文件（包含 `_converted` 的文件）
4. **UTF-8 编码**: 支持中文和特殊字符，使用 UTF-8 编码

## 🐛 问题排查

如果转换失败，可以尝试：

1. **检查文件格式**: 确认是否是 Coze 输出格式

   ```python
   import json
   with open('input.json') as f:
       data = json.load(f)
   print('output' in data)  # 应该输出 True
   ```

2. **手动解析 output 字段**:

   ```python
   from test_utils.coze_output_converter import extract_output_from_coze_file
   try:
       data = extract_output_from_coze_file('input.json')
       print("✅ 解析成功")
   except Exception as e:
       print(f"❌ 解析失败: {e}")
   ```

3. **查看详细错误信息**: 脚本会自动打印 traceback

## 📞 支持

如有问题，请查看：

- 工具代码: `test_utils/coze_output_converter.py`
- 项目文档: `docs/` 目录
- 示例文件: `sample.json`, `coze_example_for_paste_context.json`
