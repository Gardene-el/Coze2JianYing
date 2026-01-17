# Handler Generator 模块

这个包包含了 5 个核心步骤模块，用于从 API 端点自动生成 Coze handler。

## 核心特性

- ✅ **自动 API 扫描** - 智能识别所有 POST 端点
- ✅ **完整类型映射** - 从 Pydantic Schema 提取所有字段信息
- ✅ **可选参数处理** - 自动识别并正确处理可选字段
- ✅ **类型构造方案** - 将 CustomNamespace 转换为类型构造表达式
- ✅ **模块化设计** - 各脚本模块独立可测试

## 模块结构

### 数据模型

- **`api_endpoint_info.py`**: API 端点信息数据类，用于在各模块间传递数据

### 核心步骤模块

#### 步骤 1: `scan_api_endpoints.py`

**功能**: 扫描 `/app/api` 下所有 POST API 函数

- 使用 AST 解析识别 `@router.post` 装饰的函数
- 提取端点路径、请求/响应模型、路径参数等信息
- 支持异步函数识别

**主要类**: `APIScanner`

#### 步骤 6: `create_tool_scaffold.py`

**功能**: 在 `coze_plugin/raw_tools` 下创建对应工具文件夹和文件

- 创建工具目录结构
- 生成 handler.py 文件
- 生成 README.md 文档

**主要类**: `FolderCreator`

#### 步骤 3: `generate_io_models.py`

**功能**: 定义 Input/Output NamedTuple 类型

- 生成 Input 类（包含路径参数 + Request 模型字段）
- 提取 Output 字段信息
- 处理复杂类型简化

**主要类**: `InputOutputGenerator`

#### 步骤 5: `generate_handler_function.py`

**功能**: 生成 handler 函数

- 生成主 handler 函数框架
- 实现 UUID 生成逻辑
- 生成返回值结构
- 添加错误处理

**主要类**: `HandlerFunctionGenerator`

#### 步骤 4: `generate_api_call_code.py`

**功能**: 生成 API 调用记录代码

- 生成 request 对象构造代码
- 生成 API 调用代码字符串
- 生成写入 `/tmp/coze2jianying.py` 的逻辑
- 提取响应 ID

**主要类**: `APICallCodeGenerator`

### 兼容说明（旧文件名）

为保证历史脚本与文档可继续使用，旧的 `a_* / b_* / c_* / d_* / e_* / f_*` 文件仍保留为**转发模块**，
内部仅导入新的语义化模块。新开发请直接使用本节的步骤文件名。

### 辅助模块

#### `schema_extractor.py`

**功能**: 提取 Pydantic Schema 的字段信息

- 解析 Pydantic BaseModel 类定义
- 提取字段名、类型、默认值、描述
- 处理泛型类型（Optional, List 等）

**主要类**: `SchemaExtractor`

## 使用方法

### 单独使用各模块

```python
from handler_generator import (
    APIScanner,
    FolderCreator,
    InputOutputGenerator,
    HandlerFunctionGenerator,
    APICallCodeGenerator,
    SchemaExtractor,
)

# 步骤 1：扫描 API
scanner = APIScanner('/path/to/api')
endpoints = scanner.scan_all()

# 加载 Schema
schema_extractor = SchemaExtractor('/path/to/schemas.py')

# 步骤 3：生成 Input/Output
input_output_gen = InputOutputGenerator(schema_extractor)
input_class = input_output_gen.generate_input_class(endpoint)

# 步骤 4：生成 API 调用代码
api_call_gen = APICallCodeGenerator(schema_extractor)
api_call_code = api_call_gen.generate_api_call_code(endpoint, output_fields)

# 步骤 5：生成 handler 函数
handler_gen = HandlerFunctionGenerator()
handler_func = handler_gen.generate_handler_function(endpoint, output_fields, api_call_code)

# 步骤 6：创建文件
folder_creator = FolderCreator('/output/dir')
folder_creator.create_tool_folder(endpoint, handler_content, readme_content)
```

### 使用主脚本

```bash
# 使用主脚本自动执行所有步骤
python generate_handler_from_api.py
```

## 设计原则

1. **模块化**: 每个步骤模块负责单一职责，可独立测试和维护
2. **可组合**: 模块间通过清晰的接口组合使用
3. **可扩展**: 易于添加新功能或修改现有逻辑
4. **可测试**: 每个模块都可以独立编写单元测试

## 文件依赖关系

```
generate_handler_from_api.py (主程序)
    ├── scan_api_endpoints.py (步骤 1)
    │   └── api_endpoint_info.py
    ├── generate_io_models.py (步骤 3)
    │   ├── api_endpoint_info.py
    │   └── schema_extractor.py
    ├── generate_api_call_code.py (步骤 4)
    │   ├── api_endpoint_info.py
    │   └── schema_extractor.py
    ├── generate_handler_function.py (步骤 5)
    │   └── api_endpoint_info.py
    └── create_tool_scaffold.py (步骤 6)
        ├── api_endpoint_info.py
        └── schema_extractor.py
```

## 核心功能详解

### CustomNamespace 处理机制（类型构造方案）

**问题**: Coze 云端将复杂类型（如 `TimeRange`, `ClipSettings`）表示为 `CustomNamespace` 对象，应用端无法直接识别。

**解决方案**:

1. 步骤 4 识别复杂类型字段，提取类型名（如 `TimeRange`, `ClipSettings`）
2. 步骤 5 在每个 handler 中生成 `_to_type_constructor` 辅助函数
3. 运行时将 `CustomNamespace(start=0, duration=5000000)` 转换为 `TimeRange(start=0, duration=5000000)`
4. 生成的代码在应用端可以直接执行，构造正确的类型实例

**优势**:

- ✅ 类型正确：生成实际的类型构造调用，而非 dict
- ✅ 无转义问题：使用关键字参数格式，避免 f-string 大括号冲突
- ✅ 环境兼容：脚本执行环境已导入所有类型定义

**示例**:

```python
# Coze 云端输入
args.input.target_timerange = CustomNamespace(start=0, duration=5000000)

# 生成的脚本输出
req_params_xxx['target_timerange'] = TimeRange(start=0, duration=5000000)
```

详见: [`../../docs/handler_generator/CUSTOMNAMESPACE_HANDLING.md`](../../docs/handler_generator/CUSTOMNAMESPACE_HANDLING.md)

### 可选参数处理

**识别逻辑**:

- 类型包含 `Optional`
- 有默认值且不是 `...` 或 `Ellipsis`

**生成代码**:

```python
# 必需字段直接添加
req_params_xxx['material_url'] = "..."

# 可选字段加 None 检查
if {args.input.source_timerange} is not None:
    req_params_xxx['source_timerange'] = ...
```

### 类型感知格式化

**字符串类型** - 自动加引号:

```python
req_params_xxx['material_url'] = "{args.input.material_url}"
```

**数字/布尔类型** - 不加引号:

```python
req_params_xxx['speed'] = {args.input.speed}
```

**复杂类型** - 调用类型构造函数:

```python
req_params_xxx['target_timerange'] = {_to_type_constructor(args.input.target_timerange, 'TimeRange')}
```

## 测试

### 运行测试

```bash
# 测试类型构造方案
python scripts/test_type_constructor.py

# 测试类型名提取
python scripts/test_extract_type_name.py

# 测试可选参数处理
python scripts/test_optional_params.py
```

### 测试覆盖

- ✅ \_to_type_constructor 函数逻辑
- ✅ SimpleNamespace 对象转换为类型构造表达式
- ✅ 嵌套对象递归处理
- ✅ 类型名提取（从 Optional[TimeRange] 提取 TimeRange）
- ✅ 复杂类型判断（区分自定义类型和基本类型）
- ✅ 可选字段识别和 None 检查
- ✅ 字符串/数字类型格式化
- ✅ 生成的类型构造表达式可执行

## 扩展指南

### 添加新的代码生成逻辑

1. 在相应的脚本模块中添加新方法
2. 在主程序中调用新方法
3. 更新测试以验证新功能

### 支持新的 API 模式

1. 修改 `scan_api_endpoints.py` 中的 AST 解析逻辑
2. 更新 `api_endpoint_info.py` 添加新字段
3. 在步骤 3/4/5 中使用新字段

### 自定义生成模板

1. 修改步骤 5 的 `generate_handler_function` 方法
2. 调整返回值生成逻辑
3. 更新步骤 4 的 API 调用代码格式

### 添加新的复杂类型处理

1. 在步骤 4 的 `_extract_type_name` 中添加类型名提取逻辑（如果需要）
2. 在步骤 5 的 `_to_type_constructor` 中添加嵌套类型的智能推断规则
3. 添加测试用例验证类型构造表达式生成和执行

## 相关文档

- [`../../docs/handler_generator/CUSTOMNAMESPACE_HANDLING.md`](../../docs/handler_generator/CUSTOMNAMESPACE_HANDLING.md) - CustomNamespace 处理机制详解（类型构造方案）
- [`../test_type_constructor.py`](../test_type_constructor.py) - 类型构造方案测试
- [`../test_extract_type_name.py`](../test_extract_type_name.py) - 类型名提取测试
- [`../test_optional_params.py`](../test_optional_params.py) - 可选参数测试
- [`../test_customnamespace_handling.py`](../test_customnamespace_handling.py) - 旧的 dict 方案测试（已过时，仅供参考）
