# Coze OpenAPI 生成器使用指南

## 概述

`scripts/generate_coze_openapi.py` 是一个自动化工具，用于从 FastAPI 应用生成符合 Coze 平台要求的 OpenAPI 3.0.1 规范文件。

## 快速开始

### 基本用法

```bash
# 生成默认 OpenAPI 文件（使用 localhost）
python scripts/generate_coze_openapi.py

# 使用自定义服务器 URL（推荐用于 Coze 导入）
python scripts/generate_coze_openapi.py --server-url https://your-domain.ngrok-free.app

# 生成 JSON 格式
python scripts/generate_coze_openapi.py --format json

# 指定输出文件名
python scripts/generate_coze_openapi.py --output my_api.yaml
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--server-url` | API 服务器 URL | `http://localhost:8000` |
| `--format` | 输出格式 (yaml/json) | `yaml` |
| `--output` | 输出文件名 | `coze_openapi.yaml` (或 .json) |

## 工作流程

### 1. 启动 API 服务

首先确保 API 服务正在运行：

```bash
# 方式一：直接启动
python start_api.py

# 方式二：使用 GUI 的"云端服务"标签页启动
python app/main.py
```

### 2. 配置 ngrok（可选但推荐）

如果要让 Coze 平台访问本地 API，需要使用 ngrok：

```bash
ngrok http 8000
```

记录 ngrok 提供的公网 URL（如 `https://abc123.ngrok-free.app`）。

### 3. 生成 OpenAPI 文件

```bash
python scripts/generate_coze_openapi.py --server-url https://abc123.ngrok-free.app
```

### 4. 导入到 Coze 平台

1. 登录 [Coze 平台](https://www.coze.cn)
2. 创建插件 → "基于已有服务创建"
3. 上传生成的 `coze_openapi.yaml` 文件
4. Coze 会自动识别所有 API 端点
5. 测试 API 后，Coze 自动生成示例

## 生成文件说明

### 生成的文件结构

```yaml
openapi: 3.0.1
info:
  title: Coze2JianYing - 基于已有服务创建
  description: 提供云端服务，生成对应视频
  version: v1
servers:
  - url: https://your-domain.ngrok-free.app
paths:
  /api/draft/create:
    post:
      operationId: create_draft
      summary: 创建草稿
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                draft_name:
                  type: string
                  description: 项目名称
                  default: Coze剪映项目
                # ... 所有字段完全内联展开
      responses:
        "200":
          content:
            application/json:
              schema:
                type: object
                properties:
                  draft_id:
                    type: string
  # ... 更多端点
```

### 关键特性

1. **无 components/schemas 部分** - 所有 schema 完全内联
2. **无 components/examples 部分** - 等待 Coze 测试后自动生成
3. **30+ 端点自动发现** - 扫描所有 API 路由
4. **OpenAPI 3.0.1 完全兼容** - 转换所有不兼容的字段

## 技术细节

### OpenAPI 3.1.0 → 3.0.1 转换

脚本自动处理以下转换：

#### 1. exclusiveMinimum/exclusiveMaximum

```yaml
# OpenAPI 3.1.0 (FastAPI 生成)
width:
  type: integer
  exclusiveMinimum: 0    # ❌ 数值

# OpenAPI 3.0.1 (脚本转换后)
width:
  type: integer
  minimum: 0             # ✓ 数值
  exclusiveMinimum: true # ✓ 布尔值
```

#### 2. 可空类型处理

```yaml
# OpenAPI 3.1.0
duration:
  anyOf:
    - type: string
    - type: 'null'       # ❌ 3.0.1 不支持

# OpenAPI 3.0.1
duration:
  type: string
  nullable: true         # ✓ 正确格式
```

#### 3. title 字段移除

```yaml
# OpenAPI 3.1.0
material_url:
  type: string
  title: Material Url    # ❌ Coze 解析错误
  description: 音频素材 URL

# OpenAPI 3.0.1
material_url:
  type: string
  description: 音频素材 URL  # ✓ 移除 title
```

#### 4. YAML 锚点/别名

脚本使用自定义 `NoAliasDumper` 禁用 YAML 锚点和别名：

```yaml
# 不会生成这种格式（Coze 不支持）
RespExample: &id001
  segment_id: "..."
  
# 而是完全展开每个对象
```

### 函数说明

#### `convert_schema_to_openapi_3_0(schema: Any) -> Any`

递归转换 schema 对象，处理所有 OpenAPI 3.1.0 到 3.0.1 的不兼容问题。

**处理内容：**
- `exclusiveMinimum`/`exclusiveMaximum` 数值 → 布尔值
- `anyOf: [type: X, type: 'null']` → `type: X, nullable: true`
- 移除所有 `title` 字段
- 递归处理嵌套对象和数组

#### `resolve_refs(schema: Dict, root: Dict) -> Any`

解析并内联所有 `$ref` 引用，确保没有 schema 引用。

**处理内容：**
- 识别 `$ref: "#/components/schemas/Model"` 引用
- 从 root schema 中查找对应定义
- 递归解析嵌套引用
- 返回完全展开的 schema

#### `generate_coze_openapi(app, server_url: str) -> Dict`

主函数，生成完整的 Coze 兼容 OpenAPI 规范。

**处理流程：**
1. 从 FastAPI app 提取原始 OpenAPI schema
2. 移除 `components/schemas` 和 `components/examples` 部分
3. 遍历所有 paths 和 operations
4. 解析并内联所有 schema 引用
5. 转换为 OpenAPI 3.0.1 格式
6. 设置服务器 URL

#### `class NoAliasDumper(yaml.SafeDumper)`

自定义 YAML dumper，禁用锚点和别名。

```python
class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True  # 总是禁用别名
```

### 自动发现端点

脚本从以下文件自动扫描所有 API 端点：

- `app/api/new_draft_routes.py` - 草稿相关 API
- `app/api/segment_routes.py` - 片段相关 API

共计 30+ 个端点被自动发现和处理。

## 常见问题

### Q1: 生成的文件导入 Coze 时报错？

**A:** 重新生成文件，确保使用最新版本的脚本。常见错误已被修复：
- `exclusiveMinimum` 类型错误 ✅
- `type: 'null'` 不支持 ✅
- YAML 锚点解析错误 ✅
- `title` 字段解析错误 ✅

### Q2: 如何验证生成的文件？

```bash
# 检查只有 info.title 存在（schema 中无 title）
grep "title:" coze_openapi.yaml

# 应该只看到一行：
# title: Coze2JianYing - 基于已有服务创建

# 检查无 YAML 锚点/别名
grep -E "&id|\\*id" coze_openapi.yaml
# 应该无输出
```

### Q3: 需要修改 API 代码吗？

**A:** 不需要。脚本直接从运行中的 FastAPI 应用提取 schema，无需修改任何 API 代码。

### Q4: 支持哪些 HTTP 方法？

**A:** 支持所有 FastAPI 支持的方法：GET, POST, PUT, DELETE, PATCH 等。

### Q5: 如何添加新的 API 端点？

只需在 `app/api/` 中的路由文件中添加新端点，重新运行生成脚本即可自动包含。

## 测试

运行测试套件：

```bash
python scripts/test_generate_coze_openapi.py
```

测试包含：
- YAML 格式生成测试
- JSON 格式生成测试
- Schema 结构验证
- 服务器 URL 自定义测试
- OpenAPI 3.0.1 兼容性测试

## 故障排除

### 问题：脚本运行失败

```bash
# 确保在项目根目录
cd /path/to/Coze2JianYing

# 确保依赖已安装
pip install -r requirements.txt

# 确保 API 服务已启动
python start_api.py
```

### 问题：ngrok URL 不工作

1. 确认 ngrok 正在运行且转发到正确端口（8000）
2. 确认 URL 格式正确（包含 `https://`）
3. 测试 URL 是否可访问：`curl https://your-url.ngrok-free.app/docs`

### 问题：Coze 导入后 API 调用失败

1. 确认 ngrok 仍在运行
2. 确认本地 API 服务正常
3. 检查 Coze 的错误日志
4. 验证 API 认证配置（如果有）

## 更新日志

### v1.0 (Commit 2074260)
- ✅ 初始版本发布
- ✅ OpenAPI 3.0.1 完全兼容
- ✅ 移除 components 部分
- ✅ 内联所有 schema
- ✅ 自动发现所有端点
- ✅ 修复所有已知解析错误

## 相关资源

- [Coze 平台文档](https://www.coze.cn/open/docs/guides/import)
- [OpenAPI 3.0.1 规范](https://spec.openapis.org/oas/v3.0.1)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [ngrok 文档](https://ngrok.com/docs)
