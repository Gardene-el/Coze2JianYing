# API 响应标准化文档

## 概述

为了更好地适应 Coze 插件的测试需求，我们对 API 响应进行了标准化处理。**关键特性是所有 API 响应都返回 `success=True`**，即使发生错误也是如此。错误信息通过结构化的错误代码和消息字段传递。

## 为什么需要这个改变？

### Coze 插件测试要求

Coze 平台在插件上线前需要进行测试，这些测试要求：
1. **服务端必须返回 `success=true` 才能通过测试**
2. 当前的 API 抛出 HTTP 异常会导致测试失败
3. API 之间相互耦合，难以进行单元测试

### 解决方案

引入 `APIResponseManager` 类来统一管理所有 API 响应：
- ✅ **所有响应都返回 `success=true`**（便于 Coze 测试通过）
- ✅ **结构化的错误代码和分类**（便于识别和处理错误）
- ✅ **详细的错误信息**（便于调试和问题排查）
- ✅ **易于维护和扩展**（集中管理错误消息和代码）

## 响应格式

### 成功响应示例

```json
{
  "draft_id": "12345678-1234-1234-1234-123456789abc",
  "success": true,
  "error_code": "SUCCESS",
  "category": "success",
  "level": "info",
  "message": "草稿创建成功",
  "timestamp": "2025-11-17T05:30:00.000000"
}
```

### 错误响应示例

**关键：即使是错误，`success` 也是 `true`！**

```json
{
  "draft_id": "",
  "success": true,
  "error_code": "DRAFT_NOT_FOUND",
  "category": "not_found",
  "level": "error",
  "message": "草稿不存在: abc-123",
  "timestamp": "2025-11-17T05:30:00.000000",
  "details": {
    "draft_id": "abc-123"
  }
}
```

## 响应字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `success` | boolean | ✅ | **始终为 `true`**，即使发生错误 |
| `error_code` | string | ✅ | 错误代码（成功时为 "SUCCESS"） |
| `category` | string | ✅ | 错误类别（如 "success", "not_found", "validation_error"） |
| `level` | string | ✅ | 响应级别（"info", "warning", "error", "critical"） |
| `message` | string | ✅ | 人类可读的消息 |
| `timestamp` | string | ✅ | ISO 格式的时间戳 |
| `details` | object | ❌ | 额外的错误详情（仅在有详细信息时存在） |
| `data` | object | ❌ | 响应数据（成功时可能存在） |

## 错误代码分类

### 成功状态
- `SUCCESS` - 操作成功

### 客户端错误（4xx 系列概念）
- `VALIDATION_ERROR` - 参数验证错误
- `NOT_FOUND` - 资源不存在
- `ALREADY_EXISTS` - 资源已存在
- `INVALID_STATE` - 状态无效
- `TYPE_MISMATCH` - 类型不匹配

### 服务端错误（5xx 系列概念）
- `INTERNAL_ERROR` - 内部错误
- `DATABASE_ERROR` - 数据库错误
- `FILE_SYSTEM_ERROR` - 文件系统错误
- `EXTERNAL_SERVICE_ERROR` - 外部服务错误

### 业务逻辑错误
- `OPERATION_FAILED` - 操作失败
- `DEPENDENCY_ERROR` - 依赖错误
- `RESOURCE_CONFLICT` - 资源冲突

## 具体错误代码

### 草稿相关
- `DRAFT_NOT_FOUND` - 草稿不存在
- `DRAFT_ALREADY_EXISTS` - 草稿已存在
- `DRAFT_CREATE_FAILED` - 草稿创建失败
- `DRAFT_UPDATE_FAILED` - 草稿更新失败
- `DRAFT_SAVE_FAILED` - 草稿保存失败
- `DRAFT_INVALID_STATE` - 草稿状态无效

### 片段相关
- `SEGMENT_NOT_FOUND` - 片段不存在
- `SEGMENT_CREATE_FAILED` - 片段创建失败
- `SEGMENT_TYPE_MISMATCH` - 片段类型不匹配
- `SEGMENT_INVALID_CONFIG` - 片段配置无效

### 轨道相关
- `TRACK_NOT_FOUND` - 轨道不存在
- `TRACK_INDEX_INVALID` - 轨道索引无效
- `TRACK_TYPE_MISMATCH` - 轨道类型不匹配
- `TRACK_OPERATION_FAILED` - 轨道操作失败

### 素材相关
- `MATERIAL_DOWNLOAD_FAILED` - 素材下载失败
- `MATERIAL_INVALID_URL` - 素材 URL 无效
- `MATERIAL_NOT_FOUND` - 素材不存在

### 参数验证相关
- `INVALID_PARAMETER` - 参数无效
- `MISSING_REQUIRED_PARAMETER` - 缺少必需参数
- `PARAMETER_OUT_OF_RANGE` - 参数超出范围

## 使用 APIResponseManager

### 在路由处理器中使用

```python
from app.utils.api_response_manager import get_response_manager, ErrorCode

router = APIRouter()
response_manager = get_response_manager()

@router.post("/api/draft/create")
async def create_draft(request: CreateDraftRequest):
    try:
        # 尝试创建草稿
        result = draft_manager.create_draft(...)
        
        if not result["success"]:
            # 创建失败，返回错误响应（依然 success=True）
            return response_manager.error(
                error_code=ErrorCode.DRAFT_CREATE_FAILED,
                details={"reason": result["message"]}
            )
        
        # 创建成功
        return response_manager.success(
            message="草稿创建成功",
            data={"draft_id": result["draft_id"]}
        )
        
    except Exception as e:
        # 捕获所有异常，返回内部错误（依然 success=True）
        return response_manager.format_internal_error(e)
```

### 辅助方法

```python
# 资源不存在
response_manager.format_not_found_error("draft", draft_id)

# 参数验证错误
response_manager.format_validation_error("volume", 3.0, "音量必须在 0-2 之间")

# 操作失败
response_manager.format_operation_error("保存草稿", "权限不足")

# 包装数据
response_manager.wrap_data({"draft_id": "123"}, "草稿创建成功")
```

## HTTP 状态码

虽然响应体中的 `success` 始终为 `true`，但我们仍然保持正确的 HTTP 状态码以符合 REST 最佳实践：

- `200 OK` - 操作成功（即使业务逻辑有错误）
- `201 Created` - 资源创建成功
- `400 Bad Request` - 请求格式错误（Pydantic 验证失败）
- `404 Not Found` - 端点不存在
- `422 Unprocessable Entity` - 请求格式正确但语义错误

**注意**：即使 HTTP 状态码是 200，响应体中的 `error_code` 仍然可能指示错误。

## Coze 插件测试兼容性

这个响应格式完全兼容 Coze 插件测试要求：

✅ **HTTP 状态码在 200-299 范围**（成功响应）
✅ **响应体包含 `success: true` 字段**（必需）
✅ **提供详细的错误代码和消息**（便于调试）
✅ **结构化的错误分类**（便于错误处理）

## 客户端处理建议

### JavaScript/TypeScript 客户端

```javascript
const response = await fetch('/api/draft/create', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ draft_name: '测试', width: 1920, height: 1080, fps: 30 })
});

const data = await response.json();

// 始终检查 error_code 而不是 success 字段
if (data.error_code === 'SUCCESS') {
  console.log('操作成功:', data.message);
  console.log('草稿 ID:', data.draft_id);
} else {
  console.error('操作失败:', data.message);
  console.error('错误代码:', data.error_code);
  console.error('错误类别:', data.category);
  if (data.details) {
    console.error('详细信息:', data.details);
  }
}
```

### Python 客户端

```python
import requests

response = requests.post(
    'http://localhost:8000/api/draft/create',
    json={'draft_name': '测试', 'width': 1920, 'height': 1080, 'fps': 30}
)

data = response.json()

# 始终检查 error_code 而不是 success 字段
if data['error_code'] == 'SUCCESS':
    print(f"操作成功: {data['message']}")
    print(f"草稿 ID: {data['draft_id']}")
else:
    print(f"操作失败: {data['message']}")
    print(f"错误代码: {data['error_code']}")
    print(f"错误类别: {data['category']}")
    if 'details' in data:
        print(f"详细信息: {data['details']}")
```

## 迁移指南

### 对于现有 API 端点

1. 导入 APIResponseManager：
   ```python
   from app.utils.api_response_manager import get_response_manager, ErrorCode
   ```

2. 创建响应管理器实例：
   ```python
   response_manager = get_response_manager()
   ```

3. 替换 HTTPException：
   ```python
   # 旧方式
   raise HTTPException(status_code=404, detail="草稿不存在")
   
   # 新方式
   return response_manager.error(
       error_code=ErrorCode.DRAFT_NOT_FOUND,
       details={"draft_id": draft_id}
   )
   ```

4. 替换成功响应：
   ```python
   # 旧方式
   return {"success": True, "draft_id": draft_id, "message": "创建成功"}
   
   # 新方式
   return response_manager.success(
       message="草稿创建成功",
       data={"draft_id": draft_id}
   )
   ```

### 对于现有客户端

- **重要**：不要依赖 `success` 字段判断操作是否成功
- **应该**：检查 `error_code` 字段（`SUCCESS` 表示成功）
- **可选**：检查 HTTP 状态码（200-299 表示请求成功）

## 向后兼容性

为了保持向后兼容：
1. 所有响应都包含 `success` 字段（始终为 `true`）
2. 保留原有的响应字段（如 `draft_id`、`message` 等）
3. 新增的字段都是可选的（`error_code`、`category`、`level`、`details`）

旧客户端可以继续使用 `success` 字段，但建议迁移到使用 `error_code`。

## 最佳实践

1. ✅ **总是使用 `error_code` 判断操作结果**，不要依赖 `success` 字段
2. ✅ **记录 `category` 和 `level`** 用于监控和告警
3. ✅ **提取 `details`** 用于详细的错误诊断
4. ✅ **向用户展示 `message`** 字段，它是人类可读的
5. ✅ **在客户端缓存 `timestamp`** 用于调试和日志关联

## 常见问题

### Q: 为什么 `success` 始终是 `true`？
A: 这是 Coze 插件测试的要求。Coze 平台需要 `success=true` 来通过测试。实际的操作结果通过 `error_code` 字段判断。

### Q: 如何判断操作是否真正成功？
A: 检查 `error_code` 字段。如果是 `"SUCCESS"`，操作成功；否则操作失败。

### Q: HTTP 状态码还有意义吗？
A: 有。HTTP 状态码仍然遵循 REST 最佳实践，用于表示 HTTP 层面的状态。但业务逻辑的成功与否应该看 `error_code`。

### Q: 旧客户端会受影响吗？
A: 不会。新的字段都是可选的，旧客户端可以继续使用 `success` 字段。但建议迁移到使用 `error_code`。

### Q: 如何添加新的错误代码？
A: 在 `app/utils/api_response_manager.py` 的 `ErrorCode` 枚举中添加新代码，并在 `_initialize_error_messages()` 方法中定义其消息模板和类别。

## 示例场景

### 场景 1：创建草稿成功
```json
{
  "draft_id": "abc-123",
  "success": true,
  "error_code": "SUCCESS",
  "category": "success",
  "level": "info",
  "message": "草稿创建成功"
}
```

### 场景 2：草稿不存在
```json
{
  "draft_id": "",
  "success": true,
  "error_code": "DRAFT_NOT_FOUND",
  "category": "not_found",
  "level": "error",
  "message": "草稿不存在: xyz-789",
  "details": {"draft_id": "xyz-789"}
}
```

### 场景 3：参数验证失败
```json
{
  "draft_id": "",
  "success": true,
  "error_code": "INVALID_PARAMETER",
  "category": "validation_error",
  "level": "error",
  "message": "参数无效: fps - 帧率必须在 1-120 之间",
  "details": {"parameter": "fps", "reason": "帧率必须在 1-120 之间"}
}
```

### 场景 4：内部错误
```json
{
  "draft_id": "",
  "success": true,
  "error_code": "INTERNAL_ERROR",
  "category": "internal_error",
  "level": "critical",
  "message": "内部错误: 连接数据库失败",
  "details": {
    "error": "连接数据库失败",
    "error_type": "ConnectionError"
  }
}
```
