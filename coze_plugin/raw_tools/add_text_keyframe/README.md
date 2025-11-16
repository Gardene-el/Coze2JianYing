# add_text_keyframe

## 工具名称
`add_text_keyframe`

## 工具介绍
此工具对应 FastAPI 端点: `/text/{segment_id}/add_keyframe`

为文本片段添加文本特效, 可配置特效类型及参数 特效将应用于整个文本或指定部分

## 输入参数

| 参数名称 | 参数描述 | 参数类型 | 是否必填 |
|---------|---------|---------|---------|
| segment_id | 片段ID | str | 是 |
| time_offset | 时间偏移量（微秒或字符串如 '2s'） | Any | 是 |
| value | 关键帧值 | float | 是 |
| property | 属性名称（VideoSegment 需要） | Optional[str] | 否 |

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
