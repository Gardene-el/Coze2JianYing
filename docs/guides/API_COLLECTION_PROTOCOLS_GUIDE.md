# API 集合协议文件详解

本文档详细解释什么是 API 集合协议文件，以及如何在 Coze2JianYing 项目中使用它们。

## 📋 目录

- [什么是 API 集合协议文件](#什么是-api-集合协议文件)
- [Coze 支持的协议格式](#coze-支持的协议格式)
- [本项目的 API 架构](#本项目的-api-架构)
- [如何生成和使用](#如何生成和使用)
- [实际应用场景](#实际应用场景)
- [常见问题](#常见问题)

## 什么是 API 集合协议文件

### 核心概念

**API 集合协议文件**是一种标准化的格式，用于描述 Web API 的结构、端点、参数和响应格式。它们就像 API 的"说明书"或"蓝图"。

### 主要作用

1. **API 文档化** - 自动生成可读的 API 文档
2. **工具集成** - 导入到各种 API 测试和开发工具
3. **客户端生成** - 自动生成调用 API 的客户端代码
4. **服务发现** - 让第三方平台（如 Coze）了解你的 API 结构

### 类比理解

你可以把 API 集合协议文件想象成：
- **建筑设计图纸** - 描述了 API 这座"建筑"的结构
- **菜单** - 列出了 API 提供的所有"菜品"（端点）和"配料"（参数）
- **使用手册** - 告诉别人如何使用你的 API

## Coze 支持的协议格式

Coze 平台的"基于已有服务创建"插件模式支持三种主流的 API 集合协议格式：

### 1. OpenAPI (推荐) ⭐

#### 什么是 OpenAPI？

OpenAPI（前身为 Swagger）是目前最流行的 API 规范标准，由 Linux 基金会管理。

#### 特点

- **标准化程度最高** - 得到业界广泛支持
- **功能最完整** - 可以描述复杂的 API 结构
- **工具生态丰富** - 有大量工具支持
- **版本兼容性好** - OpenAPI 3.x 向后兼容

#### 格式示例

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "Coze2JianYing API",
    "version": "1.0.0"
  },
  "paths": {
    "/api/draft/create": {
      "post": {
        "summary": "创建草稿",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "draft_name": {"type": "string"},
                  "width": {"type": "integer"},
                  "height": {"type": "integer"}
                }
              }
            }
          }
        }
      }
    }
  }
}
```

#### 支持的格式

- **JSON** - 机器可读，文件较小
- **YAML** - 人类可读，更易编辑

### 2. Swagger

#### 什么是 Swagger？

Swagger 是 OpenAPI 的前身，Swagger 2.0 规范现在仍在广泛使用。

#### 区别

- **OpenAPI 3.x** - 新标准，功能更强
- **Swagger 2.0** - 旧标准，兼容性更好

#### 何时使用

- 某些旧系统或工具只支持 Swagger 2.0
- 需要与旧版 API 网关集成
- 某些企业内部标准要求使用 Swagger 2.0

### 3. Postman Collection

#### 什么是 Postman Collection？

Postman Collection 是 Postman 这个流行 API 测试工具的原生格式。

#### 特点

- **专为 API 测试设计** - 包含测试脚本和示例
- **易于分享** - Postman 用户可直接导入
- **支持环境变量** - 方便切换不同环境（开发、测试、生产）

#### 格式示例

```json
{
  "info": {
    "name": "Coze2JianYing API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "创建草稿",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/api/draft/create",
        "body": {
          "mode": "raw",
          "raw": "{\"draft_name\": \"测试\"}"
        }
      }
    }
  ]
}
```

## 本项目的 API 架构

### FastAPI 自动生成支持

Coze2JianYing 使用 **FastAPI** 框架构建 API 服务。FastAPI 的核心优势之一是：

✅ **自动生成 OpenAPI 规范** - 无需手动编写

FastAPI 通过分析你的代码结构、类型注解和文档字符串，自动生成完整的 OpenAPI 规范。

### API 架构概览

```
Coze2JianYing API
├── 草稿操作 API (/api/draft/*)
│   ├── POST /api/draft/create - 创建草稿
│   ├── POST /api/draft/{id}/add_track - 添加轨道
│   ├── POST /api/draft/{id}/add_segment - 添加片段
│   ├── POST /api/draft/{id}/save - 保存草稿
│   └── GET /api/draft/{id}/status - 查询状态
│
└── 片段管理 API (/api/segment/*)
    ├── POST /api/segment/audio/create - 创建音频片段
    ├── POST /api/segment/video/create - 创建视频片段
    ├── POST /api/segment/text/create - 创建文本片段
    ├── POST /api/segment/sticker/create - 创建贴纸片段
    ├── POST /api/segment/effect/create - 创建特效片段
    └── POST /api/segment/filter/create - 创建滤镜片段
```

### 为什么能提供这些文件

1. **FastAPI 内置支持** - FastAPI 原生支持 OpenAPI 3.1.0
2. **自动文档生成** - 代码即文档，无需额外维护
3. **格式转换工具** - 我们提供了转换脚本支持其他格式

## 如何生成和使用

### 步骤 1: 生成 API 规范文件

运行导出脚本：

```bash
cd Coze2JianYing
python scripts/export_api_specs.py
```

这会在 `api_specs/` 目录下生成以下文件：

```
api_specs/
├── openapi.json           # OpenAPI 3.1.0 (JSON)
├── openapi.yaml           # OpenAPI 3.1.0 (YAML)
├── swagger.json           # Swagger 2.0 (JSON)
├── postman_collection.json # Postman Collection v2.1
└── README.md              # 使用说明
```

### 步骤 2: 在 Coze 平台使用

#### 方法 A: 上传 OpenAPI 文件（推荐）

1. 登录 [Coze 平台](https://www.coze.cn/)
2. 进入"扣子空间" → "资源库"
3. 点击 "+ 资源" → 选择"插件"
4. 选择创建方式：**"云侧插件 - 基于已有服务创建"**
5. 点击"导入 OpenAPI 规范"
6. 上传 `api_specs/openapi.json` 文件
7. 系统自动解析并生成工具列表
8. 修改 Base URL 为你的服务地址
9. 测试工具
10. 发布插件

#### 方法 B: 手动配置

如果不上传文件，也可以手动配置：

1. 在插件配置页面填写 Base URL
2. 逐个添加工具（API 端点）
3. 为每个工具配置参数和响应格式

### 步骤 3: 配置服务地址

#### 本地部署

1. 启动 API 服务：
   ```bash
   python start_api.py
   ```

2. 使用内网穿透（如 ngrok）暴露到公网：
   ```bash
   ngrok http 8000
   ```

3. 在 Coze 插件配置中使用 ngrok 提供的 URL

#### 云端部署

1. 部署到云服务器或 Serverless 平台
2. 获取公网 URL（如 `https://your-domain.com`）
3. 在 Coze 插件配置中使用该 URL

### 步骤 4: 测试集成

在 Coze 插件配置页面测试每个工具：

1. 点击"测试工具"
2. 填入测试参数
3. 点击"执行"
4. 查看返回结果

## 实际应用场景

### 场景 1: 完全自动化的视频生成工作流

**流程**：

```
用户输入 
  ↓
Coze AI 生成内容
  ↓
Coze 调用 Coze2JianYing API（通过 OpenAPI 集成）
  ↓
API 生成剪映草稿
  ↓
用户在剪映中打开编辑
```

**优势**：
- 无需手动复制粘贴 JSON
- 实时反馈处理状态
- 可以在 Coze 工作流中实现条件判断和错误处理

### 场景 2: API 测试和调试

**使用 Postman**：

1. 导入 `postman_collection.json`
2. 配置环境变量（Base URL）
3. 逐个测试 API 端点
4. 保存测试结果和示例

**优势**：
- 可视化 API 测试
- 团队协作共享
- 自动化测试脚本

### 场景 3: 多语言客户端开发

**使用 OpenAPI Generator**：

```bash
# 生成 Python 客户端
openapi-generator generate -i api_specs/openapi.json -g python -o clients/python

# 生成 JavaScript 客户端
openapi-generator generate -i api_specs/openapi.json -g javascript -o clients/js

# 生成 Java 客户端
openapi-generator generate -i api_specs/openapi.json -g java -o clients/java
```

**优势**：
- 自动生成类型安全的客户端代码
- 支持 50+ 编程语言
- 减少手动编写代码的错误

## 常见问题

### Q1: 必须使用 OpenAPI 文件才能创建 Coze 插件吗？

**A**: 不是必须的。有两种方式：

1. **上传 OpenAPI 文件**（推荐）
   - 自动导入所有 API 端点
   - 减少手动配置工作
   - 保持接口定义一致

2. **手动配置**
   - 逐个添加工具
   - 手动填写参数
   - 更适合简单 API

### Q2: OpenAPI、Swagger、Postman Collection 有什么区别？

**A**: 

| 特性 | OpenAPI 3.x | Swagger 2.0 | Postman Collection |
|------|------------|-------------|-------------------|
| 标准化 | 最新标准 | 旧标准 | 专有格式 |
| 功能完整性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Coze 支持 | ✅ | ✅ | ✅ |
| 测试工具 | 多种 | 多种 | Postman |
| 生态系统 | 最丰富 | 丰富 | Postman 专属 |

**推荐**：优先使用 OpenAPI 3.x

### Q3: 我的 API 更新了，如何重新生成规范文件？

**A**: 

```bash
# 重新运行导出脚本
python scripts/export_api_specs.py

# 在 Coze 中更新插件配置
# 方法1: 重新上传新的 openapi.json
# 方法2: 手动修改工具配置
```

### Q4: 本地生成的 OpenAPI 文件，Base URL 是本地地址怎么办？

**A**: 

在 Coze 插件配置页面，可以修改 Base URL：

1. 进入插件编辑页面
2. 找到"服务地址"或"Base URL"配置
3. 修改为实际部署的地址
   - 本地 + ngrok: `https://abc123.ngrok.io`
   - 云端: `https://your-domain.com`

### Q5: 为什么需要内网穿透？

**A**: 

Coze 平台在云端运行，只能访问公网 URL。如果你的 API 服务在本地运行：

```
Coze 云端 ❌ → 本地 API (localhost:8000)
```

使用内网穿透后：

```
Coze 云端 ✅ → ngrok 公网 URL → 本地 API
```

**替代方案**：直接部署到云服务器或 Serverless 平台。

### Q6: API 需要认证，如何在 OpenAPI 中配置？

**A**: 

OpenAPI 文件支持多种认证方式：

```json
{
  "components": {
    "securitySchemes": {
      "bearerAuth": {
        "type": "http",
        "scheme": "bearer"
      }
    }
  },
  "security": [
    {"bearerAuth": []}
  ]
}
```

在 Coze 插件配置中：
1. 选择"认证方式"
2. 配置 Bearer Token 或 API Key
3. 测试认证是否生效

### Q7: 可以只导出部分 API 端点吗？

**A**: 

目前导出脚本会导出所有端点。如需自定义：

1. **方法 1**: 手动编辑生成的 `openapi.json`，删除不需要的路径
2. **方法 2**: 在 Coze 中导入后，只启用需要的工具
3. **方法 3**: 修改 `scripts/export_api_specs.py`，添加过滤逻辑

### Q8: Postman Collection 导入后无法使用？

**A**: 检查以下几点：

1. **Base URL 配置**
   - 在 Postman 中设置环境变量 `baseUrl`
   - 值为实际的服务地址

2. **服务是否运行**
   - 确认 API 服务正在运行
   - 测试 `GET /` 根路径是否可访问

3. **请求格式**
   - 检查 Content-Type 是否为 `application/json`
   - 检查请求体格式是否正确

## 进阶主题

### 自定义 OpenAPI 输出

修改 `app/api_main.py` 中的 FastAPI 配置：

```python
app = FastAPI(
    title="Coze剪映草稿生成器 API",
    description="详细描述...",
    version="1.0.0",
    servers=[
        {
            "url": "https://your-domain.com",
            "description": "生产环境"
        },
        {
            "url": "http://localhost:8000",
            "description": "开发环境"
        }
    ]
)
```

### 添加 API 示例

在路由函数中添加示例：

```python
@router.post(
    "/api/draft/create",
    response_model=CreateDraftResponse,
    responses={
        201: {
            "description": "成功创建草稿",
            "content": {
                "application/json": {
                    "example": {
                        "draft_id": "12345678-1234-1234-1234-123456789abc",
                        "success": True,
                        "message": "草稿创建成功"
                    }
                }
            }
        }
    }
)
async def create_draft(request: CreateDraftRequest):
    ...
```

### 集成 CI/CD

在 `.github/workflows/` 中添加自动生成规范文件的步骤：

```yaml
- name: Generate API Specs
  run: |
    python scripts/export_api_specs.py
    
- name: Upload API Specs
  uses: actions/upload-artifact@v3
  with:
    name: api-specs
    path: api_specs/
```

## 相关资源

### 官方文档

- [OpenAPI 规范](https://spec.openapis.org/oas/latest.html)
- [Swagger 文档](https://swagger.io/docs/)
- [Postman API 文档](https://learning.postman.com/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Coze 开发者文档](https://www.coze.cn/open/docs/)

### 工具推荐

- [Swagger Editor](https://editor.swagger.io/) - 在线编辑 OpenAPI
- [Postman](https://www.postman.com/) - API 测试工具
- [Insomnia](https://insomnia.rest/) - API 测试工具替代品
- [OpenAPI Generator](https://openapi-generator.tech/) - 客户端代码生成
- [Redoc](https://redoc.ly/) - 美观的 API 文档生成器

### 项目相关文档

- [API 快速开始](../../API_QUICKSTART.md)
- [Coze 集成指南](./COZE_INTEGRATION_GUIDE.md)
- [API 使用示例](../API_USAGE_EXAMPLES.md)
- [API 端点参考](../reference/API_ENDPOINTS_REFERENCE.md)

## 总结

**API 集合协议文件**是连接 Coze2JianYing API 和外部工具（特别是 Coze 平台）的桥梁。通过使用这些标准化格式：

✅ **简化集成** - 自动导入 API 配置，无需手动填写  
✅ **提高效率** - 减少配置错误，加快开发速度  
✅ **增强协作** - 团队成员可以轻松共享和测试 API  
✅ **支持自动化** - 可以生成客户端代码和测试脚本  

本项目通过 FastAPI 的强大功能和自定义导出脚本，**完全支持**生成和使用这些协议文件，让你可以轻松地将 Coze2JianYing API 集成到 Coze 工作流或其他工具中。

---

**快速开始**：

```bash
# 1. 生成 API 规范文件
python scripts/export_api_specs.py

# 2. 查看生成的文件
cd api_specs/
ls -lh

# 3. 在 Coze 中上传 openapi.json
# 访问 https://www.coze.cn/ → 创建插件 → 导入 OpenAPI 规范
```

**需要帮助？**

- 提交 [GitHub Issue](https://github.com/Gardene-el/Coze2JianYing/issues)
- 查看 [完整文档](../../README.md)
