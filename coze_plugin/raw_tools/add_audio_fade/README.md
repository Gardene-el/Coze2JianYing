# add_audio_fade

## 工具名称
`add_audio_fade`

## 工具介绍
此工具对应 FastAPI 端点: `/audio/{segment_id}/add_fade`

为音频片段添加淡入淡出效果, 可配置淡入淡出的时长 淡入淡出将应用于片段的开头和结尾部分

受限于Coze本身的运行状态，使用此函数后需使用插件名为"Coze2剪映 - 在Coze IDE 中创建 基础工具"的插件中的write_script工具，将当前工具函数的返回值api_call作为write_script工具的输入值，此函数才起效。

## 输入参数

| 参数名称 | 参数描述 | 参数类型 | 是否必填 |
|---------|---------|---------|---------|
| segment_id | 片段ID | str | 是 |
| in_duration | 淡入时长（字符串如 '1s' 或微秒数） | str | 是 |
| out_duration | 淡出时长 | str | 是 |

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
