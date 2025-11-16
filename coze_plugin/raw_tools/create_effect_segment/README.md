# create_effect_segment

## 工具名称
`create_effect_segment`

## 工具介绍
此工具对应 FastAPI 端点: `/effect/create`

创建特效片段, 并指定其时间信息及特效参数 片段创建完成后, 可通过`ScriptFile.add_segment`方法将其添加到轨道中

## 输入参数

| 参数名称 | 参数描述 | 参数类型 | 是否必填 |
|---------|---------|---------|---------|
| effect_type | 特效类型（VideoSceneEffectType 或 VideoCharacterEffectType） | str | 是 |
| target_timerange | 在轨道上的时间范围 | TimeRange | 是 |
| params | 特效参数列表（范围 0-100） | Optional[List[float]] | 否 |

## 输出参数

| 参数名称 | 参数描述 | 参数类型 | 是否必填 |
|---------|---------|---------|---------|
| segment_id | 返回创建的片段ID | str | 是 |

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
