# add_track

## 工具名称
`add_track`

## 工具介绍
此工具对应 FastAPI 端点: `/{draft_id}/add_track`

向草稿添加指定类型的轨道, 并可配置轨道名称、静音状态及图层位置 轨道创建完成后, 可通过添加片段来填充轨道内容

## 输入参数

| 参数名称 | 参数描述 | 参数类型 | 是否必填 |
|---------|---------|---------|---------|
| draft_id | 草稿ID | str | 是 |
| track_type | 轨道类型: audio/video/text/sticker/effect/filter | str | 是 |
| track_name | 轨道名称 | Optional[str] | 否 |

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
