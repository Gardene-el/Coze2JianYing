# Coze OpenAPI 插件导入指南

## 概述

本指南介绍如何将 Coze2JianYing 的 FastAPI 服务导入到 Coze 平台作为"基于已有服务创建"的插件。

## 关键问题解答

### 1. FastAPI 与 OpenAPI 的兼容性

✅ **完全兼容**

FastAPI 内置了对 OpenAPI 标准的完整支持：

- **自动生成 OpenAPI 规范**: FastAPI 会自动为你的 API 生成 OpenAPI 3.1.0 兼容的规范文档
- **交互式文档**: 提供 Swagger UI (`/docs`) 和 ReDoc (`/redoc`) 两种交互式文档界面
- **标准兼容**: 生成的 OpenAPI 规范完全符合 OpenAPI 3.0/3.1 标准
- **可编程导出**: 可以通过 `app.openapi()` 方法获取完整的 OpenAPI schema

**兼容性对比**:

| 特性 | FastAPI 生成 | Coze 要求 | 兼容性 |
|------|-------------|----------|--------|
| OpenAPI 版本 | 3.1.0 | 3.0.1 | ✅ 向下兼容 |
| Schemas | 完整支持 | 支持 | ✅ |
| Examples | 支持 | 必需 | ✅ |
| Paths/Operations | 完整支持 | 支持 | ✅ |
| Components | 完整支持 | 支持 | ✅ |

### 2. 如何生成 Coze 兼容的 OpenAPI 文件

我们提供了专门的脚本 `scripts/generate_coze_openapi.py` 来生成 Coze 兼容的 OpenAPI 文件。

#### 生成步骤

1. **启动 API 服务** (如果需要公网访问)：

```bash
# 本地测试
python start_api.py

# 使用 ngrok 提供公网访问
# 在 GUI 的"本地服务"标签页中启动服务并启用 ngrok
```

2. **生成 OpenAPI 文件**：

```bash
# 生成本地版本
python scripts/generate_coze_openapi.py

# 生成带 ngrok URL 的版本
python scripts/generate_coze_openapi.py --server-url https://your-ngrok-url.ngrok-free.app

# 生成 JSON 格式
python scripts/generate_coze_openapi.py --format json --output coze_openapi.json
```

3. **验证生成的文件**：

```bash
# 查看生成的文件
cat coze_openapi.yaml
```

#### 脚本参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--server-url` | API 服务器 URL | `http://localhost:8000` |
| `--output` | 输出文件路径 | `coze_openapi.yaml` |
| `--format` | 输出格式 (yaml/json) | `yaml` |

### 3. Coze OpenAPI 格式说明

#### 必需的格式特点

Coze 平台要求的 OpenAPI 格式具有以下特点：

1. **OpenAPI 版本**: 3.0.1 (我们生成 3.0.1 兼容版本)

2. **完整的 Examples**: 必须在 `components/examples` 中为每个 operation 提供示例

```yaml
components:
  examples:
    create_draft:
      value:
        ReqExample:
          draft_name: "Coze剪映项目"
          width: 1920
          height: 1080
          fps: 30
        RespExample:
          draft_id: "de5a8d2c-1f72-47b7-83b4-d77429d6e759"
```

3. **简化的 operationId**: 使用简洁的操作 ID

```yaml
# ✅ 简化后
operationId: create_draft

# ❌ FastAPI 默认生成
operationId: create_draft_api_draft_create_post
```

4. **服务器 URL**: 必须指向可访问的 API 服务器

```yaml
servers:
  - url: https://your-ngrok-url.ngrok-free.app
```

#### 文件结构对比

**原始 FastAPI OpenAPI** (openapi.yaml):
```yaml
openapi: 3.1.0
info:
  title: Coze剪映草稿生成器 API
  description: 示例 API 接口，演示 FastAPI 的各种通讯方法
  version: 1.0.0
paths:
  /api/draft/create:
    post:
      operationId: create_draft_api_draft_create_post  # 冗长的 ID
      # ... 省略其他内容
components:
  schemas:
    # 包含所有 schema 定义
  # 缺少 examples 部分
```

**Coze 兼容版本** (coze_openapi.yaml):
```yaml
openapi: 3.0.1
info:
  title: Coze2JianYing - 基于已有服务创建
  description: 提供云端服务，生成对应视频
  version: v1
servers:
  - url: https://your-ngrok-url.ngrok-free.app
paths:
  /api/draft/create:
    post:
      operationId: create_draft  # 简化的 ID
      # ... 省略其他内容
components:
  examples:  # 新增完整的 examples
    create_draft:
      value:
        ReqExample: {...}
        RespExample: {...}
  schemas:
    # 包含所有 schema 定义
```

## 导入到 Coze 平台

### 前提条件

1. 已注册 Coze 账号并登录
2. API 服务已启动并可通过公网访问（推荐使用 ngrok）
3. 已生成 `coze_openapi.yaml` 文件

### 导入步骤

1. **访问 Coze 插件管理**

登录 Coze 平台，进入插件管理页面。

2. **创建新插件**

选择"基于已有服务创建"方式创建插件。

3. **上传 OpenAPI 文件**

- 选择上传 `coze_openapi.yaml` 文件
- 或者直接粘贴文件内容

4. **配置认证**（可选）

如果 API 需要认证，配置相应的认证方式：
- API Key
- OAuth 2.0
- Basic Auth

对于 Coze2JianYing，默认不需要认证。

5. **测试端点**

Coze 会自动识别 OpenAPI 中定义的端点，可以在平台上直接测试：
- `POST /api/draft/create` - 创建草稿
- `POST /api/segment/audio/create` - 创建音频片段
- `POST /api/segment/video/create` - 创建视频片段
- `POST /api/segment/audio/{segment_id}/add_effect` - 添加音频特效

6. **发布插件**

测试通过后，发布插件供 Bot 使用。

### 在 Coze Bot 中使用

1. **创建或编辑 Bot**

2. **添加插件**

在 Bot 配置中添加刚刚创建的插件。

3. **配置工作流**

在工作流中调用插件的各个端点：

```
开始 → 创建草稿 → 创建音频片段 → 保存草稿 → 结束
```

4. **测试工作流**

发送测试消息，验证工作流是否正常运行。

## API 端点说明

### 核心端点

#### 1. 创建草稿

```http
POST /api/draft/create
```

**请求体**:
```json
{
  "draft_name": "我的视频项目",
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "allow_replace": true
}
```

**响应**:
```json
{
  "draft_id": "uuid-string",
  "success": true,
  "message": "草稿创建成功"
}
```

#### 2. 创建音频片段

```http
POST /api/segment/audio/create
```

**请求体**:
```json
{
  "material_url": "https://example.com/audio.mp3",
  "target_timerange": {
    "start": 0,
    "duration": 5000000
  },
  "speed": 1.0,
  "volume": 0.6,
  "change_pitch": false
}
```

**响应**:
```json
{
  "segment_id": "uuid-string",
  "success": true,
  "message": "音频片段创建成功"
}
```

#### 3. 创建视频片段

```http
POST /api/segment/video/create
```

**请求体**:
```json
{
  "material_url": "https://example.com/video.mp4",
  "target_timerange": {
    "start": 0,
    "duration": 5000000
  },
  "speed": 1.0,
  "volume": 1.0,
  "change_pitch": false
}
```

#### 4. 添加音频特效

```http
POST /api/segment/audio/{segment_id}/add_effect
```

**请求体**:
```json
{
  "effect_type": "AudioSceneEffectType.音效增强_环绕声",
  "params": [0, 100]
}
```

## 常见问题

### Q1: 为什么需要使用 ngrok？

Coze 平台需要能够访问你的 API 服务。如果你的服务运行在本地，需要使用 ngrok 等工具将本地服务暴露到公网。

### Q2: OpenAPI 版本不匹配怎么办？

FastAPI 生成 OpenAPI 3.1.0，而 Coze 要求 3.0.1。我们的生成脚本会自动处理这个问题，生成 3.0.1 兼容的文件。

### Q3: 如何更新插件？

当 API 有新的端点或修改时：
1. 重新运行 `scripts/generate_coze_openapi.py`
2. 在 Coze 平台重新上传新的 OpenAPI 文件
3. 更新 Bot 配置

### Q4: 能否同时使用云侧插件和基于服务的插件？

可以。你可以：
- 使用云侧插件（Coze IDE）进行参数处理和 JSON 生成
- 使用基于服务的插件（本项目）进行草稿生成和素材管理

两者可以在同一个工作流中配合使用。

## 技术原理

### FastAPI 如何生成 OpenAPI

FastAPI 使用 Pydantic 模型自动生成 OpenAPI 规范：

1. **从类型注解提取**: 从函数签名和 Pydantic 模型提取参数类型
2. **从文档字符串生成描述**: 函数的 docstring 成为端点描述
3. **从 Pydantic 配置生成示例**: `Config.json_schema_extra` 中的 example 成为示例数据
4. **自动验证**: 所有请求和响应都会根据 schema 自动验证

### 生成脚本的工作原理

`scripts/generate_coze_openapi.py` 执行以下转换：

1. **提取原始 schema**: 调用 `app.openapi()` 获取 FastAPI 生成的完整 schema
2. **版本降级**: 将 OpenAPI 3.1.0 转换为 3.0.1
3. **简化 operationId**: 移除冗余的路径信息
4. **生成 examples**: 从 schema 定义中提取或构建示例数据
5. **格式化输出**: 生成符合 Coze 要求的 YAML/JSON 文件

## 参考资料

- [Coze 插件开发文档](https://www.coze.cn/open/docs/guides/import)
- [OpenAPI 规范](https://spec.openapis.org/oas/v3.0.1)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [本项目 API 文档](http://localhost:8000/docs) (启动服务后访问)

## 更新日志

- 2025-11-08: 创建初始文档
- 2025-11-08: 添加生成脚本和完整示例
