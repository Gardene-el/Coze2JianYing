# Test Utils - 测试工具集# Test Utils - 测试工具集

## 📦 工具组织结构## 📦 工具组织结构

```

test_utils/test_utils/

├── __init__.py                          # 模块入口├── __init__.py                          # 模块入口

├── test_converter.py                    # 转换器测试脚本├── test_converter.py                    # 转换器测试脚本

├── converters/                          # 格式转换工具├── converters/                          # 格式转换工具

│   ├── __init__.py│   ├── __init__.py

│   └── coze_output_converter.py        # Coze输出格式转换器│   └── coze_output_converter.py        # Coze输出格式转换器

└── README.md                            # 本文档└── README.md                            # 本文档

```

## 🎯 工具分类## 🎯 工具分类

### 1. 格式转换工具 (converters/)### 1. 格式转换工具 (converters/)

用于不同格式之间的转换用于不同格式之间的转换

#### Coze 输出格式转换器#### Coze 输出格式转换器

- **文件**: `converters/coze_output_converter.py`- **文件**: `converters/coze_output_converter.py`

- **功能**: 将 Coze 特殊格式转为标准 JSON 格式- **功能**: 将 Coze 特殊格式转为标准 JSON 格式

- **详细文档**: [COZE_OUTPUT_CONVERTER_GUIDE.md](../docs/COZE_OUTPUT_CONVERTER_GUIDE.md)

### 2. 未来扩展

### 2. 未来扩展- 数据处理工具

- 数据处理工具 (data_processors/)- 测试辅助工具

- 测试辅助工具 (test_helpers/)- 其他实用工具

- 验证工具 (validators/)

- 其他实用工具## 🚀 Coze 转换器快速使用

## 🚀 Coze 转换器快速使用### 命令行使用

### 命令行使用```bash

# 转换单个文件（自动生成输出文件名）

````bashpython test_utils\converters\coze_output_converter.py coze_example_for_paste_context.json

# 转换单个文件（自动生成输出文件名）

python test_utils\converters\coze_output_converter.py coze_example_for_paste_context.json# 指定输出文件名

python test_utils\converters\coze_output_converter.py input.json output.json

# 指定输出文件名

python test_utils\converters\coze_output_converter.py input.json output.json# 批量转换

python test_utils\converters\coze_output_converter.py --batch

# 批量转换```

python test_utils\converters\coze_output_converter.py --batch

```### 作为 Python 模块使用



### 作为 Python 模块使用```python

# 方式 1: 从 converters 子模块导入

```pythonfrom test_utils.converters.coze_output_converter import convert_coze_to_standard_format

# 方式 1: 从 converters 子模块导入

from test_utils.converters.coze_output_converter import convert_coze_to_standard_format# 方式 2: 从 test_utils 顶层导入（推荐）

from test_utils import convert_coze_to_standard_format

# 方式 2: 从 test_utils 顶层导入（推荐）

from test_utils import convert_coze_to_standard_format# 转换文件

output_file = convert_coze_to_standard_format('coze_example_for_paste_context.json')

# 转换文件print(f"转换完成: {output_file}")

output_file = convert_coze_to_standard_format('coze_example_for_paste_context.json')```

print(f"转换完成: {output_file}")

```## 📊 格式说明



## 📊 格式说明### 输入格式（Coze 特殊格式）

```json

### 输入格式（Coze 特殊格式）{

```json  "output": "{\"format_version\":\"1.0\",\"drafts\":[...]}"

{}

  "output": "{\"format_version\":\"1.0\",\"drafts\":[...]}"```

}- `output` 字段是一个**字符串**

```- 字符串内容是转义的 JSON

- `output` 字段是一个**字符串**

- 字符串内容是转义的 JSON### 输出格式（标准格式）

```json

### 输出格式（标准格式）{

```json  "format_version": "1.0",

{  "export_type": "single_draft",

  "format_version": "1.0",  "draft_count": 1,

  "export_type": "single_draft",  "drafts": [...]

  "draft_count": 1,}

  "drafts": [...]```

}- 标准的 JSON 对象

```- 可直接用于剪映草稿生成器

- 标准的 JSON 对象

- 可直接用于剪映草稿生成器## ✅ 测试



## ✅ 测试运行测试脚本验证功能：



运行测试脚本验证功能：```bash

python test_utils\test_converter.py

```bash```

python test_utils\test_converter.py

```测试包括：

- ✅ 单文件转换

测试包括：- ✅ 提取 output 字段

- ✅ 单文件转换- ✅ 自定义输出文件名

- ✅ 提取 output 字段- ✅ 与 DraftGenerator 集成

- ✅ 格式验证

- ✅ 转换结果验证## 📚 完整文档



## 💡 使用示例查看详细文档：[docs/COZE_OUTPUT_CONVERTER_GUIDE.md](../docs/COZE_OUTPUT_CONVERTER_GUIDE.md)



### 完整工作流## 💡 示例



```bash### 完整工作流

# 1. 转换 Coze 输出

python test_utils\converters\coze_output_converter.py coze_example_for_paste_context.json```bash

# 1. 转换 Coze 输出

# 2. 使用转换后的文件生成草稿python test_utils\coze_output_converter.py coze_example_for_paste_context.json

python src\main.py

# 在 GUI 中选择 coze_example_for_paste_context_converted.json# 2. 使用转换后的文件生成草稿

```python src\main.py

# 在 GUI 中选择 coze_example_for_paste_context_converted.json

### 在代码中使用

# 或者使用命令行

```pythonpython -c "

from src.utils.draft_generator import DraftGeneratorfrom src.utils.draft_generator import DraftGenerator

from test_utils import convert_coze_to_standard_formatgenerator = DraftGenerator('./JianyingProjects')

generator.generate_from_file('coze_example_for_paste_context_converted.json')

# 1. 转换 Coze 输出"

converted_file = convert_coze_to_standard_format('coze_example_for_paste_context.json')```



# 2. 生成草稿## 🎯 主要功能

generator = DraftGenerator('./JianyingProjects')

generator.generate_from_file(converted_file)1. **自动解析** - 自动提取并解析 `output` 字段

```2. **格式验证** - 自动验证转换结果

3. **批量处理** - 支持批量转换多个文件

## 🔧 添加新工具4. **智能命名** - 自动生成输出文件名

5. **详细日志** - 显示详细的处理信息

### 创建新的工具分类

## ⚠️ 注意事项

1. 在 `test_utils/` 下创建新的子文件夹

   ```bash- 转换不会修改原始文件

   mkdir test_utils\processors- 输出文件使用 UTF-8 编码

   ```- 支持中文和特殊字符

- 批量转换时自动跳过已转换的文件

2. 创建 `__init__.py` 并导出主要函数
   ```python
   # test_utils/processors/__init__.py
   from .data_processor import process_data

   __all__ = ['process_data']
````

3. 在 `test_utils/__init__.py` 中导入新工具
   ```python
   from .processors import process_data
   ```

### 命名规范

- **文件夹名**: 小写+下划线（如 `converters`, `data_processors`）
- **文件名**: 描述性名称（如 `coze_output_converter.py`）
- **函数名**: 动词开头（如 `convert_coze_to_standard_format`）
- **测试文件**: `test_` 前缀（如 `test_converter.py`）

### 示例结构

```
test_utils/
├── converters/              # 格式转换工具
│   ├── __init__.py
│   └── coze_output_converter.py
├── processors/              # 数据处理工具
│   ├── __init__.py
│   └── data_processor.py
├── validators/              # 验证工具
│   ├── __init__.py
│   └── json_validator.py
└── test_helpers/            # 测试辅助工具
    ├── __init__.py
    └── mock_generator.py
```

## 🎯 Coze 转换器功能

1. **自动解析** - 自动提取并解析 `output` 字段
2. **格式验证** - 自动验证转换结果
3. **批量处理** - 支持批量转换多个文件
4. **智能命名** - 自动生成输出文件名
5. **详细日志** - 显示详细的处理信息
6. **错误处理** - 完善的异常处理机制

## ⚠️ 注意事项

- 转换不会修改原始文件
- 输出文件使用 UTF-8 编码
- 支持中文和特殊字符
- 批量转换时自动跳过已转换的文件
- 建议在项目根目录运行命令

## 📚 相关文档

- [Coze 转换器详细指南](../docs/COZE_OUTPUT_CONVERTER_GUIDE.md)
- [转换器总结文档](../CONVERTER_TOOL_SUMMARY.md)
- [架构和工作流](../docs/ARCHITECTURE_AND_WORKFLOW.md)
