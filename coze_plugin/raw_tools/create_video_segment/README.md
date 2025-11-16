# create_video_segment

## 工具名称
`create_video_segment`

## 工具介绍
此工具对应 FastAPI 端点: `/video/create`

创建视频片段, 并指定其时间信息、音量、播放速度及图像调节设置 片段创建完成后, 可通过`ScriptFile.add_segment`方法将其添加到轨道中

## 输入参数

| 参数名称 | 参数描述 | 参数类型 | 是否必填 |
|---------|---------|---------|---------|
| material_url | 视频素材 URL | str | 是 |
| target_timerange | 在轨道上的时间范围 | TimeRange | 是 |
| source_timerange | 素材裁剪范围 | Optional[TimeRange] | 否 |
| speed | 播放速度 | float | 否 |
| volume | 音量 0-2 | float | 否 |
| change_pitch | 是否跟随变速改变音调 | bool | 否 |
| clip_settings | 图像调节设置 | Optional[ClipSettings] | 否 |

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
