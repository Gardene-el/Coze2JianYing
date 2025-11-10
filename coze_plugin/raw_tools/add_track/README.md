# add_track

## 功能描述
此工具对应 FastAPI 端点: `/{draft_id}/add_track`

源文件: `/home/runner/work/Coze2JianYing/Coze2JianYing/app/api/draft_routes.py`

## API 信息
- **函数名**: add_track
- **路径**: /{draft_id}/add_track
- **方法**: POST
- **Request Model**: AddTrackRequest
- **Response Model**: AddTrackResponse

## 路径参数
- `draft_id`: 草稿ID

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
