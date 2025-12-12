# add_video_fade

## 工具名称
`add_video_fade`

## 工具介绍
此工具对应 FastAPI 端点: `/video/{segment_id}/add_fade`

VideoSegment 没有 add_fade 方法

**重要提示**：本工具仅生成 API 调用代码，需配合使用才能生效。

使用步骤：
1. 调用本工具后，会返回 `api_call` 字段，其中包含生成的 API 调用代码
2. 将返回的 `api_call` 字段的值作为 `write_script` 工具的输入参数，调用 [Coze2剪映 - 在Coze IDE 中创建 基础工具](https://www.coze.cn/store/plugin/7573974660006674486) 插件中的 `write_script` 工具
3. `write_script` 工具会将代码写入脚本文件，最终通过导出脚本来执行所有操作

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
