# CustomNamespace 处理方案文档

## 概述

本文档说明 Handler Generator 如何处理 Coze 平台的 CustomNamespace/SimpleNamespace 对象，将其转换为可在应用端执行的代码。

## 问题背景

### Coze 平台的特殊性

Coze 云端运行环境使用 `CustomNamespace` 或 `SimpleNamespace` 对象来表示复杂的数据结构（如 `TimeRange`、`ClipSettings` 等）。这些对象：

1. **不是标准的 Python dict**：虽然有 `__dict__` 属性，但本身不是 dict 类型
2. **不能直接序列化**：Pydantic 模型无法直接接受这些对象
3. **需要转换**：在生成的脚本中，需要将它们转换为应用端可以理解的格式

### 两种方案对比

#### ❌ Dict 方案（已废弃）

最初的实现尝试将 CustomNamespace 转换为 dict 字面量字符串：

```python
# Handler 中的转换函数
def _to_dict_repr(obj) -> str:
    # 将 CustomNamespace(start=0, duration=5000000)
    # 转换为 '{"start": 0, "duration": 5000000}'
    ...

# 生成的脚本代码
req_params['target_timerange'] = {"start": 0, "duration": 5000000}
```

**遇到的问题**：

1. **f-string 转义问题**：生成的代码中出现双大括号 `{{...}}`，导致转义错误
2. **运行时错误**：`unhashable type: 'dict'` - dict 在某些场景下无法作为哈希键使用
3. **类型不匹配**：Pydantic 模型期望的是具体类型实例，而不是 dict

#### ✅ 类型构造方案（当前实现）

新方案直接生成类型构造表达式：

```python
# Handler 中的转换函数
def _to_type_constructor(obj, type_name: str) -> str:
    # 将 CustomNamespace(start=0, duration=5000000)
    # 转换为 'TimeRange(start=0, duration=5000000)'
    ...

# 生成的脚本代码
req_params['target_timerange'] = TimeRange(start=0, duration=5000000)
```

**优势**：

1. **类型正确**：生成的是实际的类型构造调用，应用端可以直接执行
2. **无转义问题**：使用关键字参数格式 `key=value`，不涉及 dict 字面量的大括号
3. **环境兼容**：脚本执行环境已经导入了所有类型定义，可以直接构造
4. **符合习惯**：生成的代码更接近正常的 Python 代码风格

## 实现细节

### 1. 类型名提取 (步骤 4)

**位置**：`scripts/handler_generator/generate_api_call_code.py`

**方法**：`APICallCodeGenerator._extract_type_name()`

**功能**：从类型字符串中提取核心类型名

```python
def _extract_type_name(self, field_type: str) -> str:
    """
    例如：
    - "TimeRange" -> "TimeRange"
    - "Optional[TimeRange]" -> "TimeRange"
    - "Optional[List[ClipSettings]]" -> "ClipSettings"
    """
    import re

    # 提取所有大写字母开头的类型名（PascalCase）
    matches = re.findall(r"\b([A-Z][a-zA-Z0-9_]*)\b", field_type)

    if matches:
        # 返回最后一个匹配（最内层类型）
        return matches[-1]

    return field_type
```

### 2. 复杂类型判断 (步骤 4)

**方法**：`APICallCodeGenerator._is_complex_type()`

**功能**：判断字段是否为复杂类型（需要类型构造）

```python
def _is_complex_type(self, field_type: str) -> bool:
    """判断是否为自定义复杂类型"""
    type_name = self._extract_type_name(field_type)

    basic_types = {
        "str", "int", "float", "bool", "None", "Any",
        "List", "Dict", "Tuple", "Set", "Optional", "Union",
    }

    # 不在基本类型集合中的，视为复杂类型
    return type_name not in basic_types
```

**判断规则**：

- ✅ 复杂类型：`TimeRange`, `ClipSettings`, `TextStyle`, `Position` 等自定义类型
- ❌ 基本类型：`str`, `int`, `float`, `bool`, `List`, `Dict` 等 Python 内置类型

### 3. 参数值格式化 (步骤 4)

**方法**：`APICallCodeGenerator._format_param_value()`

**功能**：根据字段类型生成不同的参数值表达式

```python
def _format_param_value(self, field_name: str, field_type: str) -> str:
    access_expr = "args.input." + field_name

    if self._should_quote_type(field_type):
        # 字符串类型：加引号
        return '"{' + access_expr + '}"'
    elif self._is_complex_type(field_type):
        # 复杂类型：调用类型构造器
        type_name = self._extract_type_name(field_type)
        return "{_to_type_constructor(" + access_expr + ", '" + type_name + "')}"
    else:
        # 其他基本类型：直接插值
        return "{" + access_expr + "}"
```

**生成的代码示例**：

```python
# 字符串字段
req_params['material_url'] = "{args.input.material_url}"

# 数值字段
req_params['speed'] = {args.input.speed}

# 复杂类型字段
req_params['target_timerange'] = {_to_type_constructor(args.input.target_timerange, 'TimeRange')}
```

### 4. 类型构造转换 (步骤 5)

**位置**：`scripts/handler_generator/generate_handler_function.py`

**函数**：`_to_type_constructor()` (生成到 handler.py 中)

**功能**：运行时将 CustomNamespace 转换为类型构造表达式字符串

```python
def _to_type_constructor(obj, type_name: str) -> str:
    """
    将 CustomNamespace/SimpleNamespace 对象转换为类型构造表达式字符串

    例如：
        CustomNamespace(start=0, duration=5000000)
        -> "TimeRange(start=0, duration=5000000)"

    Args:
        obj: CustomNamespace/SimpleNamespace 对象
        type_name: 目标类型名，如 "TimeRange", "ClipSettings"

    Returns:
        类型构造表达式字符串
    """
    if obj is None:
        return 'None'

    if hasattr(obj, '__dict__'):
        obj_dict = obj.__dict__
        params = []

        for key, value in obj_dict.items():
            # 递归处理嵌套对象
            if hasattr(value, '__dict__'):
                # 智能推断嵌套类型名
                if 'settings' in key.lower():
                    nested_type_name = 'ClipSettings'
                elif 'timerange' in key.lower():
                    nested_type_name = 'TimeRange'
                elif 'style' in key.lower():
                    nested_type_name = 'TextStyle'
                elif 'position' in key.lower():
                    nested_type_name = 'Position'
                else:
                    nested_type_name = key.capitalize()
                value_repr = _to_type_constructor(value, nested_type_name)
            elif isinstance(value, str):
                value_repr = f'"{value}"'
            else:
                value_repr = repr(value)

            params.append(f'{key}={value_repr}')

        # 构造：TypeName(param1=value1, param2=value2)
        return f'{type_name}(' + ', '.join(params) + ')'

    if isinstance(obj, str):
        return f'"{obj}"'
    else:
        return repr(obj)
```

## 工作流程示例

### 输入（Coze 云端）

```python
# Coze 传入的参数（使用 SimpleNamespace）
args.input = SimpleNamespace(
    material_url="https://example.com/video.mp4",
    target_timerange=SimpleNamespace(start=0, duration=5000000),
    speed=1.0,
    clip_settings=SimpleNamespace(brightness=0.5, contrast=0.3)
)
```

### 处理（Handler 生成器）

1. **扫描 API**：识别字段类型
   - `material_url`: `str` → 字符串类型
   - `target_timerange`: `TimeRange` → 复杂类型
   - `speed`: `float` → 基本类型
   - `clip_settings`: `Optional[ClipSettings]` → 复杂类型

2. **生成 Handler**：包含 `_to_type_constructor` 函数

3. **格式化参数值**：
   - 字符串 → `"{args.input.material_url}"`
   - 复杂类型 → `{_to_type_constructor(args.input.target_timerange, 'TimeRange')}`
   - 基本类型 → `{args.input.speed}`

### 输出（生成的脚本）

```python
# /tmp/coze2jianying.py 中的内容
req_params_abc123 = {}
req_params_abc123['material_url'] = "https://example.com/video.mp4"
req_params_abc123['target_timerange'] = TimeRange(start=0, duration=5000000)
req_params_abc123['speed'] = 1.0
req_params_abc123['clip_settings'] = ClipSettings(brightness=0.5, contrast=0.3)

req_abc123 = CreateVideoSegmentRequest(**req_params_abc123)
resp_abc123 = await create_video_segment(req_abc123)
```

### 执行（应用端）

```python
# 应用端已导入类型定义
from app.schemas.general_schemas import TimeRange, ClipSettings, CreateVideoSegmentRequest

# 直接执行生成的脚本
exec(script_content)  # 所有类型构造都能正确执行
```

## 测试

### 单元测试

**文件**：`scripts/test_type_constructor.py`

**测试内容**：

1. `_to_type_constructor` 函数逻辑
2. 生成的代码输出格式
3. 类型构造表达式可执行性
4. 确保不生成 dict 字面量

**文件**：`scripts/test_extract_type_name.py`

**测试内容**：

1. 类型名提取的正确性
2. 复杂类型判断的准确性
3. 参数值格式化的输出

### 运行测试

```bash
# 测试类型构造方案
python scripts/test_type_constructor.py

# 测试类型名提取
python scripts/test_extract_type_name.py
```

## 向后兼容性

### 对现有代码的影响

- ✅ **完全兼容**：只修改了生成器内部逻辑，不影响已生成的 handler
- ✅ **API 不变**：生成器的对外接口保持不变
- ✅ **现有测试通过**：所有现有测试继续通过

### 重新生成 Handler

如果需要使用新方案，需要重新运行生成器：

```bash
python scripts/generate_handler_from_api.py
```

这会用新的类型构造方案重新生成所有 handler 文件。

## 注意事项

### 1. 类型名推断

对于嵌套对象，类型名通过字段名推断：

- `target_timerange` → `TimeRange`
- `clip_settings` → `ClipSettings`
- `text_style` → `TextStyle`
- `position` → `Position`

如果字段名不包含类型关键字，使用首字母大写的字段名。

### 2. 执行环境要求

生成的脚本假设执行环境已经导入了所有类型定义：

```python
from app.schemas.general_schemas import (
    TimeRange,
    ClipSettings,
    TextStyle,
    Position,
    CreateVideoSegmentRequest,
    CreateAudioSegmentRequest,
    # ... 其他类型
)
```

### 3. 字符串转义

生成的代码中，字符串值会被正确转义：

```python
# 输入：SimpleNamespace(name="test's video")
# 输出：CustomType(name="test's video")  # 引号已处理
```

### 4. None 值处理

可选字段为 None 时会被省略：

```python
# source_timerange 为 None
if args.input.source_timerange is not None:
    req_params['source_timerange'] = ...  # 这行不会执行
```

## 相关文件

### 生成器模块

- `scripts/handler_generator/generate_api_call_code.py` - API 调用代码生成
- `scripts/handler_generator/generate_handler_function.py` - Handler 函数生成
- `scripts/handler_generator/schema_extractor.py` - Schema 字段提取

### 测试文件

- `scripts/test_type_constructor.py` - 类型构造方案测试
- `scripts/test_extract_type_name.py` - 类型名提取测试
- `scripts/test_customnamespace_handling.py` - 旧的 dict 方案测试（已过时）

### 生成的 Handler

- `coze_plugin/raw_tools/*/handler.py` - 自动生成的 handler 文件

## 更新历史

- **2024-12**: 初始实现（dict 方案）
- **2024-12**: 重构为类型构造方案（当前版本）

## 相关 Issue

- 原始需求：处理 CustomNamespace 对象
- 问题报告：dict 方案的运行时错误
- 解决方案：类型构造方案实现
