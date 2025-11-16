# add_video_mask

## 工具名称
`add_video_mask`

## 工具介绍
此工具对应 FastAPI 端点: `/video/{segment_id}/add_mask`

为视频片段添加滤镜效果, 可配置滤镜类型及强度 滤镜将应用于整个片段或指定时间段

## 输入参数

| 参数名称 | 参数描述 | 参数类型 | 是否必填 |
|---------|---------|---------|---------|
| segment_id | 片段ID | str | 是 |
| mask_type | 蒙版类型 | str | 是 |
| center_x | 蒙版中心 X 坐标 | Optional[float] | 否 |
| center_y | 蒙版中心 Y 坐标 | Optional[float] | 否 |
| size | 蒙版大小 | Optional[float] | 否 |
| feather | 羽化程度 0-1 | Optional[float] | 否 |
| invert | 是否反转 | Optional[bool] | 否 |
| rotation | 旋转角度 | Optional[float] | 否 |

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
