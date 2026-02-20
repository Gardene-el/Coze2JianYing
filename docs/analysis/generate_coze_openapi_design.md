# Coze OpenAPI 生成器 - 技术设计文档

## 项目背景

### 问题描述

Issue #156 提出需要将 FastAPI 服务作为插件导入到 Coze 平台。主要挑战：

1. FastAPI 生成 OpenAPI 3.1.0，但 Coze 要求 3.0.1
2. Coze 需要特定的 schema 结构（内联，无 $ref）
3. Coze 的 YAML 解析器对某些字段敏感
4. 需要自动发现所有 API 端点

## 设计演进

### 迭代 1: 初始实现 (Commit 7238071, 90aa23d)

**目标**：创建基本的 OpenAPI 生成脚本

**实现**：
- 从 FastAPI 提取 OpenAPI schema
- 生成包含 components/schemas 的完整文件
- 手动添加 components/examples

**问题**：
- 生成的文件包含 Coze 不需要的 components 部分
- 只包含部分 API 端点
- 使用 $ref 引用，不符合 Coze 要求

### 迭代 2: OpenAPI 3.0.1 兼容性修复

#### 2a. exclusiveMinimum/exclusiveMaximum (Commit 2e155e9)

**错误信息**：
```
cannot unmarshal number into Go struct field 
Schema.components.schemas.properties.exclusiveMinimum of type bool
```

**原因分析**：
```yaml
# OpenAPI 3.1.0 (FastAPI)
width:
  type: integer
  exclusiveMinimum: 0    # 数值类型

# OpenAPI 3.0.1 (Coze 要求)
width:
  type: integer
  minimum: 0             # 数值限制
  exclusiveMinimum: true # 布尔标志
```

**解决方案**：
```python
def convert_schema_to_openapi_3_0(schema: Any) -> Any:
    if isinstance(schema, dict):
        # 处理 exclusiveMinimum
        if 'exclusiveMinimum' in schema:
            value = schema['exclusiveMinimum']
            if isinstance(value, (int, float)):
                converted['minimum'] = value
                converted['exclusiveMinimum'] = True
        
        # 处理 exclusiveMaximum
        if 'exclusiveMaximum' in schema:
            value = schema['exclusiveMaximum']
            if isinstance(value, (int, float)):
                converted['maximum'] = value
                converted['exclusiveMaximum'] = True
```

#### 2b. nullable 类型处理 (Commit c01f309)

**错误信息**：
```
cannot unmarshal bool into Go struct field 
Schema.components.schemas.properties.title of type string
```

**原因分析**：
```yaml
# OpenAPI 3.1.0
duration:
  anyOf:
    - type: string
    - type: 'null'       # 3.0.1 不支持

# OpenAPI 3.0.1
duration:
  type: string
  nullable: true         # 正确格式
```

**解决方案**：
```python
# 检测 anyOf: [type: X, type: 'null'] 模式
if 'anyOf' in schema:
    any_of_list = schema['anyOf']
    if len(any_of_list) == 2:
        non_null = None
        has_null = False
        
        for item in any_of_list:
            if item.get('type') == 'null':
                has_null = True
            else:
                non_null = item
        
        if has_null and non_null:
            # 转换为 nullable
            converted = convert_schema_to_openapi_3_0(non_null)
            converted['nullable'] = True
            return converted
```

#### 2c. YAML 锚点/别名问题 (Commit 480c640)

**错误信息**：
```
cannot unmarshal bool into Go struct field 
Schema.components.schemas.properties.title of type string
```

**原因分析**：

PyYAML 默认生成锚点和别名来避免重复：

```yaml
RespExample: &id001
  segment_id: "uuid..."
  success: true

# 后续引用
RespExample: *id001
```

Coze 的 Go YAML 解析器无法正确处理这些引用。

**解决方案**：

创建自定义 YAML Dumper：

```python
class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True  # 禁用所有锚点和别名

# 使用时
yaml.dump(openapi_spec, f, Dumper=NoAliasDumper, 
          allow_unicode=True, sort_keys=False)
```

### 迭代 3: 架构重新设计 (Commit e00d309)

**用户反馈**：
- 不应该生成 components/schemas
- 不应该生成 components/examples（Coze 测试后自动生成）
- 应该内联所有 schema（无 $ref）
- 应该自动扫描所有路由文件

**重新设计**：

```python
def resolve_refs(schema: Dict, root: Dict) -> Any:
    """递归解析所有 $ref 引用，完全内联"""
    if isinstance(schema, dict):
        if '$ref' in schema:
            # 解析引用路径
            ref_path = schema['$ref']
            parts = ref_path.split('/')
            
            # 从 root 中查找定义
            current = root
            for part in parts[1:]:  # 跳过 '#'
                current = current.get(part, {})
            
            # 递归解析引用的内容
            return resolve_refs(current, root)
        
        # 递归处理所有字段
        return {k: resolve_refs(v, root) for k, v in schema.items()}
    
    elif isinstance(schema, list):
        return [resolve_refs(item, root) for item in schema]
    
    return schema

def generate_coze_openapi(app, server_url: str) -> Dict:
    # 获取原始 schema
    openapi_schema = app.openapi()
    
    # 移除 components
    if 'components' in openapi_schema:
        components = openapi_schema.pop('components')
    else:
        components = {}
    
    # 处理所有 paths
    if 'paths' in openapi_schema:
        for path, path_item in openapi_schema['paths'].items():
            for method, operation in path_item.items():
                # 内联 requestBody schema
                if 'requestBody' in operation:
                    content = operation['requestBody'].get('content', {})
                    for media_type, media_schema in content.items():
                        if 'schema' in media_schema:
                            # 解析 $ref
                            resolved = resolve_refs(
                                media_schema['schema'], 
                                {'components': components}
                            )
                            # 转换为 3.0.1
                            media_schema['schema'] = convert_schema_to_openapi_3_0(resolved)
                
                # 内联 responses schema
                if 'responses' in operation:
                    for status, response in operation['responses'].items():
                        content = response.get('content', {})
                        for media_type, media_schema in content.items():
                            if 'schema' in media_schema:
                                resolved = resolve_refs(
                                    media_schema['schema'],
                                    {'components': components}
                                )
                                media_schema['schema'] = convert_schema_to_openapi_3_0(resolved)
    
    return openapi_schema
```

### 迭代 4: title 字段问题 (Commit 2074260)

**错误信息**：
```
cannot unmarshal bool into Go struct field 
Schema.paths.post.requestBody.content.schema.properties.properties.title of type string
```

**问题分析**：

错误路径 `schema.properties.properties.title` 揭示了问题：

1. 第一个 `properties` - OpenAPI 关键字
2. 第二个 `properties` - 实际字段名（`SegmentDetailResponse.properties: Dict[str, Any]`）
3. `title` - FastAPI 自动生成的字段

```python
# app/schemas/general_schemas.py
class SegmentDetailResponse(BaseModel):
    properties: Dict[str, Any] = Field(..., description="片段属性")
```

生成的 schema：

```yaml
schema:
  properties:          # OpenAPI 关键字
    properties:        # 字段名
      type: object
      title: Properties  # ❌ Coze 解析混乱
      additionalProperties: true
```

**用户测试发现**：

通过对比两个文件：
- `示例中导致报错的部分.txt` - 包含 title 字段，导致错误
- `示例中没有错误的部分.txt` - 同样包含 title 字段，但能正常工作

发现问题不是所有 title 字段，而是特定位置（如字段名为 `properties` 时）的 title 字段导致 Coze 解析器混淆。

**解决方案**：

最简单且彻底的方案 - 移除所有 title 字段：

```python
def convert_schema_to_openapi_3_0(schema: Any) -> Any:
    if isinstance(schema, dict):
        converted = {}
        
        for key, value in schema.items():
            # 跳过 title 字段（Coze 平台不支持）
            if key == 'title':
                continue
            
            # 处理其他字段
            converted[key] = convert_schema_to_openapi_3_0(value)
        
        return converted
```

**验证**：

```bash
grep "title:" coze_openapi.yaml
# 输出: title: Coze2JianYing - 基于已有服务创建

# 只有 info.title 保留（这是 OpenAPI 规范要求的）
# 所有 schema 中的 title 都被移除
```

## 最终架构

### 文件结构

```
scripts/
  ├── generate_coze_openapi.py    # 主生成脚本
  └── test_generate_coze_openapi.py  # 测试套件

docs/
  ├── generate_coze_openapi_guide.md  # 使用指南
  └── generate_coze_openapi_design.md # 本文档
```

### 核心函数

#### 1. convert_schema_to_openapi_3_0()

**职责**：转换 OpenAPI 3.1.0 到 3.0.1

**处理内容**：
- `exclusiveMinimum`/`exclusiveMaximum` 转换
- `anyOf` nullable 类型处理
- 移除 `title` 字段
- 递归处理嵌套结构

**复杂度**：O(n)，n 为 schema 节点数

#### 2. resolve_refs()

**职责**：解析并内联所有 $ref 引用

**算法**：
1. 检测 `$ref` 字段
2. 解析引用路径（如 `#/components/schemas/Model`）
3. 从 root schema 查找定义
4. 递归解析嵌套引用
5. 返回完全展开的 schema

**复杂度**：O(n * m)，n 为 schema 节点数，m 为平均引用深度

#### 3. generate_coze_openapi()

**职责**：主入口，生成完整 OpenAPI 文件

**流程**：
```
FastAPI app
    ↓
提取 OpenAPI schema (3.1.0)
    ↓
移除 components 部分
    ↓
遍历所有 paths
    ↓
解析 $ref (resolve_refs)
    ↓
转换为 3.0.1 (convert_schema_to_openapi_3_0)
    ↓
设置服务器 URL
    ↓
生成 YAML/JSON
```

#### 4. NoAliasDumper

**职责**：自定义 YAML 输出，禁用锚点/别名

**实现**：
```python
class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True
```

### 数据流

```
FastAPI Application
    ↓
app.openapi()
    ↓
OpenAPI 3.1.0 Schema
    ├── components
    │   ├── schemas (被移除)
    │   └── examples (被移除)
    └── paths
        └── /api/endpoint
            └── post
                ├── requestBody
                │   └── schema (含 $ref) → resolve_refs() → convert_schema_to_openapi_3_0()
                └── responses
                    └── 200
                        └── schema (含 $ref) → resolve_refs() → convert_schema_to_openapi_3_0()
    ↓
OpenAPI 3.0.1 Schema (Coze 兼容)
    ├── info
    ├── servers
    └── paths (所有 schema 内联)
    ↓
YAML/JSON 输出 (NoAliasDumper)
    ↓
coze_openapi.yaml
```

## 兼容性保证

### OpenAPI 3.0.1 规范

| 特性 | OpenAPI 3.1.0 | OpenAPI 3.0.1 | 转换逻辑 |
|------|---------------|---------------|----------|
| exclusiveMinimum | 数值 | 布尔值 + minimum | ✅ 自动转换 |
| exclusiveMaximum | 数值 | 布尔值 + maximum | ✅ 自动转换 |
| nullable | anyOf + type: null | nullable: true | ✅ 自动转换 |
| title | 支持 | 支持但 Coze 不支持 | ✅ 移除 |
| $ref | 支持 | 支持但 Coze 要求内联 | ✅ 解析并内联 |

### Coze 平台要求

| 要求 | 实现 | 状态 |
|------|------|------|
| OpenAPI 3.0.1 | 完全转换 | ✅ |
| 无 components/schemas | 不生成 | ✅ |
| 无 components/examples | 不生成 | ✅ |
| Schema 内联 | resolve_refs() | ✅ |
| 无 YAML 锚点 | NoAliasDumper | ✅ |
| 无 title 字段 | 过滤移除 | ✅ |

## 测试策略

### 单元测试

```python
def test_convert_exclusive_minimum():
    """测试 exclusiveMinimum 转换"""
    schema = {
        'type': 'integer',
        'exclusiveMinimum': 0
    }
    result = convert_schema_to_openapi_3_0(schema)
    assert result['minimum'] == 0
    assert result['exclusiveMinimum'] is True
    assert 'exclusiveMinimum' not in result or isinstance(result['exclusiveMinimum'], bool)

def test_convert_nullable():
    """测试 nullable 转换"""
    schema = {
        'anyOf': [
            {'type': 'string'},
            {'type': 'null'}
        ]
    }
    result = convert_schema_to_openapi_3_0(schema)
    assert result['type'] == 'string'
    assert result['nullable'] is True

def test_remove_title():
    """测试 title 移除"""
    schema = {
        'type': 'string',
        'title': 'Test Title',
        'description': 'Test description'
    }
    result = convert_schema_to_openapi_3_0(schema)
    assert 'title' not in result
    assert result['description'] == 'Test description'
```

### 集成测试

```python
def test_generate_yaml():
    """测试 YAML 生成"""
    # 运行生成脚本
    result = subprocess.run([
        'python', 'scripts/generate_coze_openapi.py',
        '--format', 'yaml'
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    assert os.path.exists('coze_openapi.yaml')
    
    # 验证内容
    with open('coze_openapi.yaml') as f:
        data = yaml.safe_load(f)
    
    assert data['openapi'] == '3.0.1'
    assert 'components' not in data or 'schemas' not in data.get('components', {})
```

## 性能考虑

### 时间复杂度

- schema 转换：O(n)，n 为 schema 节点总数
- $ref 解析：O(n * m)，m 为平均引用深度
- 总体：O(n * m)，通常 m << n，接近线性

### 空间复杂度

- 原始 schema：O(n)
- 内联后 schema：O(n * k)，k 为平均引用次数
- 通常 k ≈ 1-3，空间增长可接受

### 实际性能

- 30 个端点生成时间：< 1 秒
- 生成文件大小：~60KB (YAML), ~90KB (JSON)

## 已知限制

1. **循环引用**：不支持（FastAPI 通常不会生成）
2. **自定义 schema 扩展**：可能丢失非标准字段
3. **复杂 anyOf/oneOf**：只处理简单的 nullable 模式

## 未来改进

1. **缓存机制**：缓存已解析的 $ref，提高性能
2. **增量更新**：只更新变化的端点
3. **验证工具**：在生成后自动验证 OpenAPI 规范
4. **CLI 增强**：支持更多选项（如排除特定端点）

## 参考资源

- [OpenAPI 3.0.1 规范](https://spec.openapis.org/oas/v3.0.1)
- [OpenAPI 3.1.0 规范](https://spec.openapis.org/oas/v3.1.0)
- [Coze 平台文档](https://www.coze.cn/open/docs/guides/import)
- [FastAPI OpenAPI 文档](https://fastapi.tiangolo.com/advanced/extending-openapi/)
