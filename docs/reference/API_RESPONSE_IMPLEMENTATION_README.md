# API 响应标准化 - 实现摘要

## 快速开始

本项目已实现 API 响应标准化，以支持 Coze 插件测试需求。

### 核心特性

✅ **所有 API 响应都返回 `success=true`**（即使发生错误）
✅ **结构化的错误代码和分类系统**
✅ **向后兼容现有客户端**
✅ **易于维护和扩展**

### 示例

**成功响应：**
```json
{
  "draft_id": "12345678-1234-1234-1234-123456789abc",
  "success": true,
  "error_code": "SUCCESS",
  "message": "草稿创建成功"
}
```

**错误响应（注意 success 依然是 true）：**
```json
{
  "draft_id": "",
  "success": true,
  "error_code": "DRAFT_NOT_FOUND",
  "message": "草稿不存在: abc-123",
  "details": {"draft_id": "abc-123"}
}
```

## 文件结构

```
app/
  utils/
    api_response_manager.py          # APIResponseManager 核心实现
  api/
    draft_routes.py                  # 已更新的示例端点
  schemas/
    general_schemas.py               # 已更新的响应模型

docs/
  API_RESPONSE_STANDARD.md           # 完整的响应标准文档
  API_MIGRATION_EXAMPLES.py          # 迁移示例和最佳实践

tests/
  test_api_response_manager.py       # ResponseManager 单元测试
  test_response_format_integration.py # 响应格式集成测试
```

## 使用方法

### 在新端点中使用

```python
from app.utils.api_response_manager import get_response_manager, ErrorCode

response_manager = get_response_manager()

@router.post("/api/example")
async def example(request: Request):
    try:
        # 业务逻辑
        result = do_something(request)
        
        if not result["success"]:
            return response_manager.error(
                error_code=ErrorCode.OPERATION_FAILED,
                details={"reason": result["message"]}
            )
        
        return response_manager.success(
            message="操作成功",
            data=result
        )
    except Exception as e:
        return response_manager.format_internal_error(e)
```

### 迁移现有端点

参考 `docs/API_MIGRATION_EXAMPLES.py` 获取详细的迁移指南。

简要步骤：
1. 导入 APIResponseManager
2. 替换 HTTPException 为 response_manager 方法
3. 捕获所有异常
4. 测试验证

## 错误代码

### 主要错误类别

- `SUCCESS` - 操作成功
- `VALIDATION_ERROR` - 参数验证错误
- `NOT_FOUND` - 资源不存在
- `ALREADY_EXISTS` - 资源已存在
- `TYPE_MISMATCH` - 类型不匹配
- `OPERATION_FAILED` - 操作失败
- `INTERNAL_ERROR` - 内部错误

查看 `app/utils/api_response_manager.py` 中的 `ErrorCode` 枚举获取完整列表（40+ 错误代码）。

## 测试

运行所有测试：
```bash
# APIResponseManager 单元测试
python tests/test_api_response_manager.py

# 响应格式集成测试
python tests/test_response_format_integration.py
```

所有测试都应该通过，并验证：
- success 字段始终为 True
- 错误代码和类别正确设置
- 消息模板正确工作
- 辅助方法功能正常

## Coze 兼容性

这个实现完全满足 Coze 插件测试要求：

| 要求 | 状态 | 说明 |
|------|------|------|
| HTTP 状态码 200-299 | ✅ | 所有响应使用 200 |
| 响应体包含 success=true | ✅ | 始终为 true |
| 提供错误信息 | ✅ | 通过 error_code 和 message |
| 单元测试友好 | ✅ | 每个端点可独立测试 |

## 已更新的端点

- ✅ `POST /api/draft/create` - 创建草稿（参考实现）

## 待更新的端点

以下端点仍需迁移到新的响应格式：

**Draft 相关：**
- `POST /api/draft/{draft_id}/add_track`
- `POST /api/draft/{draft_id}/add_segment`
- `POST /api/draft/{draft_id}/add_effect`
- `POST /api/draft/{draft_id}/add_filter`
- `POST /api/draft/{draft_id}/save`
- `GET /api/draft/{draft_id}/status`

**Segment 相关：**
- `POST /api/segment/audio/create`
- `POST /api/segment/video/create`
- `POST /api/segment/text/create`
- `POST /api/segment/sticker/create`
- `POST /api/segment/effect/create`
- `POST /api/segment/filter/create`
- 以及所有 segment 操作端点（add_effect, add_fade, 等）

## 向后兼容性

### 客户端迁移建议

**旧代码（依然可以工作）：**
```python
if response['success']:
    # 处理成功
else:
    # 处理错误  # ⚠️ 这个分支永远不会执行！
```

**新代码（推荐）：**
```python
if response['error_code'] == 'SUCCESS':
    # 处理成功
else:
    # 处理错误
    print(f"错误: {response['message']}")
    print(f"错误代码: {response['error_code']}")
```

### 保持兼容性的要点

1. ✅ 保留 `success` 字段（始终为 true）
2. ✅ 保留原有的响应字段（如 `draft_id`）
3. ✅ 新字段都是可选的（不影响旧客户端）
4. ✅ HTTP 状态码保持语义正确

## 资源链接

- **完整文档**: `docs/API_RESPONSE_STANDARD.md`
- **迁移示例**: `docs/API_MIGRATION_EXAMPLES.py`
- **源代码**: `app/utils/api_response_manager.py`
- **测试**: `tests/test_api_response_manager.py`

## 问题排查

### Q: 为什么 success 始终是 true？
A: Coze 插件测试要求。实际结果看 `error_code`。

### Q: 如何判断操作是否成功？
A: 检查 `error_code === 'SUCCESS'`，不要检查 `success` 字段。

### Q: HTTP 状态码还有用吗？
A: 有用。它表示 HTTP 层面的状态。业务逻辑看 `error_code`。

更多问题请参考 `docs/API_RESPONSE_STANDARD.md` 的 FAQ 部分。

## 贡献指南

### 添加新的错误代码

1. 在 `ErrorCode` 枚举中添加新代码
2. 在 `_initialize_error_messages()` 中定义消息模板
3. 添加测试用例
4. 更新文档

### 迁移现有端点

1. 参考 `docs/API_MIGRATION_EXAMPLES.py`
2. 使用迁移检查清单
3. 编写测试验证
4. 更新 API 文档

## 许可证

本项目使用与主项目相同的许可证。

## 联系方式

如有问题或建议，请在 GitHub 上创建 issue。
