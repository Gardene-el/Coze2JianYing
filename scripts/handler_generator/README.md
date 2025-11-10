# Handler Generator 模块

这个包包含了 5 个脚本模块 (A-E)，用于从 API 端点自动生成 Coze handler。

## 模块结构

### 数据模型
- **`api_endpoint_info.py`**: API 端点信息数据类，用于在各模块间传递数据

### A-E 脚本模块

#### A 脚本: `a_api_scanner.py`
**功能**: 扫描 `/app/api` 下所有 POST API 函数

- 使用 AST 解析识别 `@router.post` 装饰的函数
- 提取端点路径、请求/响应模型、路径参数等信息
- 支持异步函数识别

**主要类**: `APIScanner`

#### B 脚本: `b_folder_creator.py`
**功能**: 在 `coze_plugin/raw_tools` 下创建对应工具文件夹和文件

- 创建工具目录结构
- 生成 handler.py 文件
- 生成 README.md 文档

**主要类**: `FolderCreator`

#### C 脚本: `c_input_output_generator.py`
**功能**: 定义 Input/Output NamedTuple 类型

- 生成 Input 类（包含路径参数 + Request 模型字段）
- 提取 Output 字段信息
- 处理复杂类型简化

**主要类**: `InputOutputGenerator`

#### D 脚本: `d_handler_function_generator.py`
**功能**: 生成 handler 函数

- 生成主 handler 函数框架
- 实现 UUID 生成逻辑
- 生成返回值结构
- 添加错误处理

**主要类**: `HandlerFunctionGenerator`

#### E 脚本: `e_api_call_code_generator.py`
**功能**: 生成 API 调用记录代码

- 生成 request 对象构造代码
- 生成 API 调用代码字符串
- 生成写入 `/tmp/coze2jianying.py` 的逻辑
- 提取响应 ID

**主要类**: `APICallCodeGenerator`

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

# A 脚本：扫描 API
scanner = APIScanner('/path/to/api')
endpoints = scanner.scan_all()

# 加载 Schema
schema_extractor = SchemaExtractor('/path/to/schemas.py')

# C 脚本：生成 Input/Output
input_output_gen = InputOutputGenerator(schema_extractor)
input_class = input_output_gen.generate_input_class(endpoint)

# E 脚本：生成 API 调用代码
api_call_gen = APICallCodeGenerator(schema_extractor)
api_call_code = api_call_gen.generate_api_call_code(endpoint, output_fields)

# D 脚本：生成 handler 函数
handler_gen = HandlerFunctionGenerator()
handler_func = handler_gen.generate_handler_function(endpoint, output_fields, api_call_code)

# B 脚本：创建文件
folder_creator = FolderCreator('/output/dir')
folder_creator.create_tool_folder(endpoint, handler_content, readme_content)
```

### 使用主脚本

```bash
# 使用主脚本自动执行所有步骤
python generate_handler_from_api.py
```

## 设计原则

1. **模块化**: 每个脚本负责单一职责，可独立测试和维护
2. **可组合**: 模块间通过清晰的接口组合使用
3. **可扩展**: 易于添加新功能或修改现有逻辑
4. **可测试**: 每个模块都可以独立编写单元测试

## 文件依赖关系

```
generate_handler_from_api.py (主程序)
    ├── a_api_scanner.py (A脚本)
    │   └── api_endpoint_info.py
    ├── b_folder_creator.py (B脚本)
    │   └── api_endpoint_info.py
    ├── c_input_output_generator.py (C脚本)
    │   ├── api_endpoint_info.py
    │   └── schema_extractor.py
    ├── d_handler_function_generator.py (D脚本)
    │   └── api_endpoint_info.py
    └── e_api_call_code_generator.py (E脚本)
        ├── api_endpoint_info.py
        └── schema_extractor.py
```

## 扩展指南

### 添加新的代码生成逻辑

1. 在相应的脚本模块中添加新方法
2. 在主程序中调用新方法
3. 更新测试以验证新功能

### 支持新的 API 模式

1. 修改 `a_api_scanner.py` 中的 AST 解析逻辑
2. 更新 `api_endpoint_info.py` 添加新字段
3. 在 C/D/E 脚本中使用新字段

### 自定义生成模板

1. 修改 D 脚本的 `generate_handler_function` 方法
2. 调整返回值生成逻辑
3. 更新 E 脚本的 API 调用代码格式
