# create\_sticker\_segment

## 工具名称

`create_sticker_segment`

## 工具介绍

此工具对应 FastAPI 端点: \`\`

没有提供详细文档注释

## 输入参数

* **sticker\_id** (str, required): 贴纸资源 ID（纯数字字符串，可从贴纸查询页面获取）
* **target\_timerange** (TimeRange, required): 在轨道上的时间范围
* **clip\_settings** (Optional\[ClipSettings], optional): 图像调节设置（位置、缩放、旋转、透明度）

## 输出参数

* **segment\_id** (str): Segment UUID

## 使用说明

此工具由脚本自动生成，用于在 Coze 平台中调用对应的 API 端点。

工具会：

1. 生成唯一的 UUID
2. 记录 API 调用到 `/tmp/coze2jianying.py` 文件
3. 返回包含 UUID 的响应

## 注意事项

* 此工具在 Coze 平台的沙盒环境中运行
* API 调用记录保存在 `/tmp/coze2jianying.py`
* UUID 用于关联和追踪不同的对象实例
