# add_global_effect

## 工具名称
`add_global_effect`

## 工具介绍
此工具对应 FastAPI 端点: `/{draft_id}/add_effect`

没有提供详细文档注释

## 输入参数

| 参数名称 | 参数描述 | 参数类型 | 是否必填 |
|---------|---------|---------|---------|
| draft_id | 草稿ID | str | 是 |
| effect_type | 特效类型 | str | 是 |
| target_timerange | 时间范围 | TimeRange | 是 |
| params | 特效参数列表 | Optional[List[float]] | 否 |

## 输出参数

| 参数名称 | 参数描述 | 参数类型 | 是否必填 |
|---------|---------|---------|---------|
| api_call | 生成的 API 调用代码 | str | 是 |

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
