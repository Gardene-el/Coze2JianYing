# 草稿生成 API 参考文档

本文档提供 Coze2JianYing 草稿生成 API 的详细技术参考。

## 📋 目录

- [概述](#概述)
- [认证](#认证)
- [端点列表](#端点列表)
- [数据模型](#数据模型)
- [错误处理](#错误处理)
- [限流和配额](#限流和配额)
- [代码示例](#代码示例)

## 概述

### Base URL

- **本地开发**: `http://127.0.0.1:8000`
- **生产环境**: `https://your-domain.com`

### API 版本

当前版本：`v1.0.0`

### 内容类型

所有请求和响应使用 JSON 格式：

```
Content-Type: application/json
```

### OpenAPI 规范

完整的 OpenAPI 3.0 规范可通过以下端点获取：

```
GET /openapi.json
```

交互式文档：
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## 认证

### 当前状态

当前版本的 API **不需要认证**，适合测试和开发环境。

### 未来计划

生产环境部署时，建议添加以下认证方式之一：

#### Bearer Token

```http
Authorization: Bearer YOUR_API_TOKEN
```

#### API Key

```http
X-API-Key: YOUR_API_KEY
```

## 端点列表

### 1. 生成草稿

创建剪映草稿文件。

**端点**: `POST /api/draft/generate`

**请求体**:

```json
{
  "content": "string",
  "output_folder": "string (optional)"
}
```

**成功响应** (201 Created):

```json
{
  "status": "success",
  "message": "成功生成 1 个草稿",
  "draft_count": 1,
  "drafts": [
    {
      "draft_id": "12345678-1234-1234-1234-123456789abc",
      "project_name": "项目名称",
      "folder_path": "C:/Users/.../com.lveditor.draft/12345678-..."
    }
  ],
  "timestamp": "2025-11-04T08:00:00"
}
```

**错误响应**:

- `400 Bad Request` - 无效的 JSON 格式
- `500 Internal Server Error` - 草稿生成失败

**示例请求**:

```bash
curl -X POST "http://127.0.0.1:8000/api/draft/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{\"draft_id\": \"test-123\", \"project_name\": \"测试\"}",
    "output_folder": null
  }'
```

---

### 2. 查询草稿状态

查询指定草稿的生成状态和信息。

**端点**: `GET /api/draft/status/{draft_id}`

**路径参数**:

- `draft_id` (string, required): 草稿的唯一标识符

**成功响应** (200 OK):

```json
{
  "draft_id": "12345678-1234-1234-1234-123456789abc",
  "status": "completed",
  "project_name": "项目名称",
  "folder_path": "C:/Users/.../com.lveditor.draft/12345678-...",
  "created_at": "2025-11-04T08:00:00",
  "error_message": null
}
```

**状态值**:

- `pending` - 待处理
- `processing` - 处理中
- `completed` - 已完成
- `failed` - 失败

**错误响应**:

- `404 Not Found` - 草稿不存在

**示例请求**:

```bash
curl "http://127.0.0.1:8000/api/draft/status/12345678-1234-1234-1234-123456789abc"
```

---

### 3. 列出草稿

获取所有已生成草稿的列表。

**端点**: `GET /api/draft/list`

**查询参数**:

- `skip` (integer, optional, default: 0): 跳过的记录数（分页）
- `limit` (integer, optional, default: 100): 返回的最大记录数

**成功响应** (200 OK):

```json
{
  "total": 10,
  "drafts": [
    {
      "draft_id": "12345678-1234-1234-1234-123456789abc",
      "project_name": "项目名称",
      "created_at": "2025-11-04T08:00:00",
      "folder_path": "C:/Users/.../com.lveditor.draft/12345678-..."
    }
  ]
}
```

**示例请求**:

```bash
curl "http://127.0.0.1:8000/api/draft/list?skip=0&limit=10"
```

---

### 4. 健康检查

检查 API 服务的健康状态。

**端点**: `GET /api/draft/health`

**成功响应** (200 OK):

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-04T08:00:00",
  "services": {
    "draft_generator": true,
    "material_downloader": true,
    "jianying_folder_detected": true
  }
}
```

**状态值**:

- `healthy` - 所有服务正常
- `degraded` - 部分服务异常

**示例请求**:

```bash
curl "http://127.0.0.1:8000/api/draft/health"
```

---

### 5. 清空草稿存储

清空内存中的草稿状态存储（仅用于测试）。

**端点**: `DELETE /api/draft/clear`

⚠️ **警告**: 此操作只清空内存中的状态记录，不会删除实际的草稿文件。

**成功响应** (200 OK):

```json
{
  "message": "草稿状态存储已清空",
  "status": "success"
}
```

**示例请求**:

```bash
curl -X DELETE "http://127.0.0.1:8000/api/draft/clear"
```

---

### 6. 根路径

API 服务的欢迎页面。

**端点**: `GET /`

**成功响应** (200 OK):

```json
{
  "message": "Welcome to Coze剪映草稿生成器 API",
  "docs": "/docs",
  "redoc": "/redoc",
  "version": "1.0.0",
  "timestamp": "2025-11-04T08:00:00"
}
```

## 数据模型

### DraftGenerateRequest

生成草稿的请求模型。

```typescript
{
  content: string;           // 必需：Coze 导出的 JSON 数据（字符串格式）
  output_folder?: string;    // 可选：输出文件夹路径
}
```

**content 字段格式**:

content 字段应包含符合 Draft Generator Interface 规范的 JSON 字符串。参考 `data_structures/draft_generator_interface/README.md` 了解详细格式。

**最小示例**:

```json
{
  "content": "{\"draft_id\": \"test-123\", \"project_name\": \"测试项目\", \"canvas\": {\"width\": 1920, \"height\": 1080, \"fps\": 30}, \"tracks\": []}"
}
```

### DraftGenerateResponse

草稿生成的响应模型。

```typescript
{
  status: string;            // 响应状态 ("success" | "error")
  message: string;           // 响应消息
  draft_count: number;       // 生成的草稿数量
  drafts: DraftInfo[];       // 生成的草稿列表
  timestamp: string;         // ISO 8601 格式的时间戳
}
```

### DraftInfo

单个草稿的信息。

```typescript
{
  draft_id: string;          // 草稿的唯一标识符（UUID）
  project_name: string;      // 项目名称
  folder_path: string;       // 草稿文件夹的完整路径
}
```

### DraftStatusResponse

草稿状态查询的响应模型。

```typescript
{
  draft_id: string;          // 草稿ID
  status: DraftStatus;       // 草稿状态
  project_name?: string;     // 项目名称（可选）
  folder_path?: string;      // 文件夹路径（可选）
  created_at?: string;       // 创建时间（ISO 8601）
  error_message?: string;    // 错误消息（可选）
}
```

### DraftStatus

草稿的状态枚举。

```typescript
enum DraftStatus {
  PENDING = "pending",       // 待处理
  PROCESSING = "processing", // 处理中
  COMPLETED = "completed",   // 已完成
  FAILED = "failed"          // 失败
}
```

### ErrorResponse

错误响应的标准格式。

```typescript
{
  error: string;             // 错误类型
  message: string;           // 错误消息
  detail?: string;           // 详细错误信息（可选）
  timestamp: string;         // ISO 8601 格式的时间戳
}
```

## 错误处理

### HTTP 状态码

API 使用标准的 HTTP 状态码：

- `200 OK` - 请求成功
- `201 Created` - 资源创建成功
- `400 Bad Request` - 请求参数错误
- `404 Not Found` - 资源不存在
- `500 Internal Server Error` - 服务器内部错误

### 错误响应格式

所有错误响应遵循统一格式：

```json
{
  "detail": "错误描述"
}
```

或更详细的格式：

```json
{
  "error": "InvalidJSON",
  "message": "无效的 JSON 格式",
  "detail": "Expecting value: line 1 column 1 (char 0)",
  "timestamp": "2025-11-04T08:00:00"
}
```

### 常见错误

#### 1. 无效的 JSON 格式

**状态码**: 400

**原因**: content 字段不是有效的 JSON 字符串

**解决方案**: 确保 content 是正确的 JSON 字符串

#### 2. 草稿生成失败

**状态码**: 500

**原因**: 草稿生成过程中发生错误（素材下载失败、文件写入失败等）

**解决方案**: 
- 检查网络连接
- 确认输出文件夹权限
- 查看服务日志获取详细信息

#### 3. 草稿不存在

**状态码**: 404

**原因**: 查询的草稿ID不存在

**解决方案**: 确认草稿ID正确

## 限流和配额

### 当前状态

当前版本**没有**限流限制。

### 生产环境建议

生产环境部署时，建议添加以下限制：

- **请求频率限制**: 每分钟最多 60 次请求
- **并发限制**: 同时最多处理 5 个草稿生成任务
- **内容大小限制**: content 字段最大 10MB

实现示例（使用 slowapi）：

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/draft/generate")
@limiter.limit("60/minute")
async def generate_draft(request: DraftGenerateRequest):
    ...
```

## 代码示例

### Python 客户端

```python
import requests
import json

# API 基础 URL
BASE_URL = "http://127.0.0.1:8000"

def generate_draft(draft_data: dict, output_folder: str = None):
    """生成草稿"""
    url = f"{BASE_URL}/api/draft/generate"
    
    # 准备请求数据
    payload = {
        "content": json.dumps(draft_data),
        "output_folder": output_folder
    }
    
    # 发送请求
    response = requests.post(url, json=payload)
    
    # 检查响应
    if response.status_code == 201:
        result = response.json()
        print(f"✅ 成功生成 {result['draft_count']} 个草稿")
        for draft in result['drafts']:
            print(f"  - {draft['project_name']}: {draft['folder_path']}")
        return result
    else:
        print(f"❌ 生成失败: {response.json()}")
        return None

def check_health():
    """检查服务健康状态"""
    url = f"{BASE_URL}/api/draft/health"
    response = requests.get(url)
    
    if response.status_code == 200:
        health = response.json()
        print(f"服务状态: {health['status']}")
        print(f"版本: {health['version']}")
        print("服务组件:")
        for service, status in health['services'].items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {service}")
        return health
    else:
        print("❌ 健康检查失败")
        return None

# 使用示例
if __name__ == "__main__":
    # 检查服务健康
    check_health()
    
    # 生成草稿
    draft_data = {
        "draft_id": "test-123",
        "project_name": "测试项目",
        "canvas": {"width": 1920, "height": 1080, "fps": 30},
        "tracks": []
    }
    
    generate_draft(draft_data)
```

### JavaScript/Node.js 客户端

```javascript
const axios = require('axios');

const BASE_URL = 'http://127.0.0.1:8000';

async function generateDraft(draftData, outputFolder = null) {
  try {
    const response = await axios.post(`${BASE_URL}/api/draft/generate`, {
      content: JSON.stringify(draftData),
      output_folder: outputFolder
    });
    
    const result = response.data;
    console.log(`✅ 成功生成 ${result.draft_count} 个草稿`);
    result.drafts.forEach(draft => {
      console.log(`  - ${draft.project_name}: ${draft.folder_path}`);
    });
    
    return result;
  } catch (error) {
    console.error('❌ 生成失败:', error.response?.data || error.message);
    return null;
  }
}

async function checkHealth() {
  try {
    const response = await axios.get(`${BASE_URL}/api/draft/health`);
    const health = response.data;
    
    console.log(`服务状态: ${health.status}`);
    console.log(`版本: ${health.version}`);
    console.log('服务组件:');
    Object.entries(health.services).forEach(([service, status]) => {
      const statusIcon = status ? '✅' : '❌';
      console.log(`  ${statusIcon} ${service}`);
    });
    
    return health;
  } catch (error) {
    console.error('❌ 健康检查失败:', error.message);
    return null;
  }
}

// 使用示例
(async () => {
  // 检查服务健康
  await checkHealth();
  
  // 生成草稿
  const draftData = {
    draft_id: 'test-123',
    project_name: '测试项目',
    canvas: { width: 1920, height: 1080, fps: 30 },
    tracks: []
  };
  
  await generateDraft(draftData);
})();
```

### cURL 示例

```bash
# 健康检查
curl "http://127.0.0.1:8000/api/draft/health"

# 生成草稿
curl -X POST "http://127.0.0.1:8000/api/draft/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{\"draft_id\": \"test-123\", \"project_name\": \"测试项目\", \"canvas\": {\"width\": 1920, \"height\": 1080, \"fps\": 30}, \"tracks\": []}",
    "output_folder": null
  }'

# 查询草稿状态
curl "http://127.0.0.1:8000/api/draft/status/test-123"

# 列出草稿
curl "http://127.0.0.1:8000/api/draft/list?skip=0&limit=10"
```

## 相关文档

- [Coze 集成指南](./COZE_INTEGRATION_GUIDE.md) - 详细的集成步骤和部署指南
- [API Gateway 调查报告](../analysis/COZE_API_GATEWAY_INVESTIGATION.md) - 技术调研和架构决策
- [Draft Generator Interface](../../data_structures/draft_generator_interface/README.md) - JSON 数据格式规范

---

**版本**: v1.0.0  
**最后更新**: 2025-11-04
