# API 响应标准（capcut 风格）

## 统一契约

- 成功：

```json
{"code":0,"message":"成功","data":{...}}
```

- 失败：

```json
{"code":<非0>,"message":"错误说明"}
```

- HTTP 状态码：**始终返回 200**（包括参数校验错误、业务异常、未知异常）。

## 中间件行为

统一由 [app/backend/middlewares/response.py](app/backend/middlewares/response.py) 处理：

1. 解析语言（`Accept-Language`，默认中文）。
2. 422 参数校验错误格式化为统一失败结构。
3. 非 200 响应统一改写为失败结构并返回 200。
4. 200 的 JSON 业务数据自动补壳为 `code/message/data`。
5. 已经是标准响应（存在 `code` + `message`）时直接透传。
6. 捕获未处理异常并映射错误码。

## 路由与服务约定

- 路由层/服务层**不再拼响应壳**。
- 路由只返回业务字段（例如 `{ "draft_id": "..." }`）或抛异常。
- 错误码映射在中间件内维护，不分散在 `api_main.py` 或各路由。

## 迁移影响

- 客户端请统一按 `code/message/data` 解析。
- 历史字段 `success/error_code/category/level/timestamp` 已废弃。
- 旧工具 `response_builder.py` 与旧中间件 `coze_response.py` 已移除。

## 快速示例

### 成功

```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "draft_id": "12345678-1234-1234-1234-123456789abc"
  }
}
```

### 失败

```json
{
  "code": 1001,
  "message": "草稿不存在: not-exists"
}
```
