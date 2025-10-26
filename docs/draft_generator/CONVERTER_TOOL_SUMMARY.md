# Coze 输出格式转换工具 - 创建总结

## ✅ 完成内容

### 1. 核心工具文件

**文件**: `test_utils/coze_output_converter.py`

功能：

- ✅ 从 Coze 输出文件中提取 `output` 字段
- ✅ 解析字符串格式的 JSON 为标准 JSON 对象
- ✅ 保存为格式化的标准 JSON 文件
- ✅ 自动验证转换结果
- ✅ 支持单文件和批量转换
- ✅ 命令行接口

### 2. 测试脚本

**文件**: `test_utils/test_converter.py`

测试内容：

- ✅ 单文件转换功能
- ✅ 提取 output 字段功能
- ✅ 自定义输出文件名
- ✅ 与 DraftGenerator 集成测试
- ✅ 所有测试通过

### 3. 文档

**文件**:

- `docs/COZE_OUTPUT_CONVERTER_GUIDE.md` - 完整使用指南
- `test_utils/README.md` - 快速开始指南
- 更新了主 `README.md`

### 4. 模块结构

```
test_utils/
├── __init__.py                 # 模块初始化
├── coze_output_converter.py    # 核心转换工具
├── test_converter.py            # 测试脚本
└── README.md                    # 快速指南
```

---

## 📊 功能对比

### 输入格式（Coze 特殊格式）

```json
{
  "output": "{\"format_version\":\"1.0\",\"export_type\":\"single_draft\",\"drafts\":[...]}"
}
```

**特点**：

- `output` 是一个**字符串**
- 包含转义的 JSON 内容
- 需要两次解析

### 输出格式（标准格式）

```json
{
  "format_version": "1.0",
  "export_type": "single_draft",
  "draft_count": 1,
  "drafts": [
    {
      "draft_id": "f7a9d782-9d4f-407c-aede-9a889dc52d3e",
      "project": {...},
      "tracks": [...]
    }
  ]
}
```

**特点**：

- 标准的 JSON 对象
- 可直接使用
- 格式清晰

---

## 🚀 使用方式

### 命令行使用

```bash
# 1. 转换单个文件（自动命名）
python test_utils\coze_output_converter.py coze_example_for_paste_context.json
# 输出: coze_example_for_paste_context_converted.json

# 2. 指定输出文件名
python test_utils\coze_output_converter.py input.json output.json

# 3. 批量转换当前目录
python test_utils\coze_output_converter.py --batch

# 4. 批量转换指定目录和模式
python test_utils\coze_output_converter.py --batch ./data "*coze*.json"
```

### Python 模块使用

```python
from test_utils.coze_output_converter import convert_coze_to_standard_format

# 转换文件
output_file = convert_coze_to_standard_format(
    'coze_example_for_paste_context.json',
    'output.json'
)
```

### 与 DraftGenerator 集成

```python
from test_utils.coze_output_converter import convert_coze_to_standard_format
from src.utils.draft_generator import DraftGenerator

# 1. 转换格式
converted_file = convert_coze_to_standard_format('coze_input.json')

# 2. 生成草稿
generator = DraftGenerator('./JianyingProjects')
draft_paths = generator.generate_from_file(converted_file)
```

---

## ✅ 测试结果

```
============================================================
Coze 输出格式转换工具测试
============================================================

测试总结
============================================================
单文件转换: ✅ 通过
提取 output 字段: ✅ 通过
自定义输出文件名: ✅ 通过
与 DraftGenerator 集成: ✅ 通过

============================================================
✅ 所有测试通过!
============================================================
```

### 测试详情

1. **单文件转换测试**

   - ✅ 成功读取 Coze 输出文件
   - ✅ 成功提取并解析 output 字段
   - ✅ 成功保存为标准格式
   - ✅ 验证通过所有字段

2. **提取 output 字段测试**

   - ✅ 正确提取 format_version
   - ✅ 正确提取 export_type
   - ✅ 正确提取 draft_count
   - ✅ 正确提取 drafts 数组

3. **自定义输出文件名测试**

   - ✅ 支持自定义输出路径
   - ✅ 文件正确创建

4. **与 DraftGenerator 集成测试**
   - ✅ 转换后文件可被 DraftGenerator 识别
   - ✅ 成功生成草稿
   - ✅ 素材文件夹正确创建
   - ✅ 5 个音频素材成功下载

---

## 🎯 主要特性

### 1. 自动化处理

- 自动提取 output 字段
- 自动解析嵌套的 JSON
- 自动格式化输出

### 2. 智能命名

- 默认添加 `_converted` 后缀
- 支持自定义输出文件名
- 批量处理时自动跳过已转换文件

### 3. 完整验证

- 验证基本字段结构
- 显示草稿详细信息
- 统计轨道和片段数量

### 4. 批量处理

- 支持批量转换多个文件
- 可自定义匹配模式
- 显示处理进度和统计

### 5. 详细日志

- 显示文件大小
- 显示解析进度
- 显示验证结果

---

## 📚 文档结构

```
docs/
└── COZE_OUTPUT_CONVERTER_GUIDE.md  # 完整使用指南
    ├── 功能介绍
    ├── 使用方法
    ├── 输入输出格式
    ├── 功能特性
    ├── 使用示例
    ├── 错误处理
    ├── 集成方式
    └── 问题排查

test_utils/
└── README.md                        # 快速开始指南
    ├── 工具位置
    ├── 快速使用
    ├── 格式说明
    ├── 测试说明
    ├── 完整工作流
    └── 主要功能
```

---

## 💡 使用场景

### 场景 1: 开发测试

```bash
# 转换测试数据
python test_utils\coze_output_converter.py test_data.json

# 使用转换后的数据进行测试
python test_utils\test_converter.py
```

### 场景 2: 生产使用

```bash
# 批量转换所有 Coze 输出
python test_utils\coze_output_converter.py --batch ./coze_outputs

# 生成草稿
python src\main.py
# 在 GUI 中选择转换后的文件
```

### 场景 3: 自动化流程

```python
import os
from test_utils.coze_output_converter import convert_coze_to_standard_format
from src.utils.draft_generator import DraftGenerator

# 自动化处理流程
input_dir = "./coze_outputs"
output_dir = "./JianyingProjects"

for file in os.listdir(input_dir):
    if file.endswith('.json') and 'coze' in file:
        # 转换格式
        input_path = os.path.join(input_dir, file)
        converted_file = convert_coze_to_standard_format(input_path)

        # 生成草稿
        generator = DraftGenerator(output_dir)
        generator.generate_from_file(converted_file)
```

---

## 🔧 技术实现

### 核心函数

1. **extract_output_from_coze_file(input_file)**

   - 读取 JSON 文件
   - 提取 output 字段
   - 解析字符串为 JSON
   - 返回标准格式数据

2. **convert_coze_to_standard_format(input_file, output_file)**

   - 调用 extract_output_from_coze_file
   - 保存为格式化的 JSON
   - 自动生成输出文件名
   - 返回输出文件路径

3. **validate_conversion(input_file, output_file)**

   - 验证基本字段
   - 显示草稿信息
   - 统计轨道和片段

4. **batch_convert(input_dir, pattern, output_suffix)**
   - 批量处理多个文件
   - 匹配文件模式
   - 显示处理进度

---

## ⚠️ 注意事项

1. **文件编码**: 使用 UTF-8 编码，支持中文
2. **文件安全**: 不会修改原始文件，总是创建新文件
3. **格式验证**: 自动验证转换结果，确保格式正确
4. **错误处理**: 完整的错误处理和日志输出
5. **向后兼容**: 不影响现有的工作流程

---

## 🎉 总结

### 创建的内容

- ✅ 核心转换工具（200+ 行代码）
- ✅ 完整测试脚本（150+ 行代码）
- ✅ 详细使用文档（300+ 行文档）
- ✅ 快速开始指南
- ✅ 更新主 README

### 功能特性

- ✅ 单文件转换
- ✅ 批量转换
- ✅ 自动验证
- ✅ 智能命名
- ✅ 详细日志
- ✅ 命令行接口
- ✅ Python 模块接口

### 测试状态

- ✅ 所有测试通过
- ✅ 与 DraftGenerator 集成正常
- ✅ 素材下载正常（5 个音频文件）

---

## 📞 使用帮助

```bash
# 查看帮助
python test_utils\coze_output_converter.py

# 输出:
用法:
  python coze_output_converter.py <input_file> [output_file]
  python coze_output_converter.py --batch [directory] [pattern]

示例:
  python coze_output_converter.py coze_example_for_paste_context.json
  python coze_output_converter.py coze_example.json output.json
  python coze_output_converter.py --batch . '*coze*.json'
```

---

**工具已完成并通过所有测试，可以正常使用！** 🎉
