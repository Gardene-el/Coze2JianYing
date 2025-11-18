# add_global_filter

## 工具名称
`add_global_filter`

## 工具介绍
此工具对应 FastAPI 端点: `/{draft_id}/add_filter`

没有提供详细文档注释

## 输入参数

| 参数名称 | 参数描述 | 参数类型 | 是否必填 |
|---------|---------|---------|---------|
| draft_id | 草稿ID | str | 是 |
| filter_type | 滤镜类型 | str | 是 |
| target_timerange | 时间范围 | TimeRange | 是 |
| intensity | 滤镜强度 0-100 | float | 否 |

## 输出参数

无输出参数

## 使用说明
此工具由脚本自动生成，用于在 Coze 平台中调用对应的 API 端点。

工具会：
1. 生成唯一的 UUID
2. 记录 API 调用到 `/tmp/coze2jianying.py` 文件
3. 返回包含 UUID 的响应

## 注意事项
- 此工具在 Coze 平台的沙盒环境中运行
- API 调用记录保存在 `/tmp/coze2jianying.py`
- UUID 用于关联和追踪不同的对象实例
