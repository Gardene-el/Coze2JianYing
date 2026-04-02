# create\_text\_segment

## 工具名称

`create_text_segment`

## 工具介绍

此工具对应 FastAPI 端点: \`\`

没有提供详细文档注释

## 输入参数

* **text\_content** (str, optional): 文本内容
* **target\_timerange** (TimeRange, required): 在轨道上的时间范围
* **font\_family** (Optional\[str], optional): 字体名称
* **text\_style** (Optional\[TextStyle], optional): 文本样式（字体大小、颜色、加粗等）
* **text\_border** (Optional\[TextBorder], optional): 文本描边，None 表示无描边
* **text\_shadow** (Optional\[TextShadow], optional): 文本阴影，None 表示无阴影
* **text\_background** (Optional\[TextBackground], optional): 文本背景，None 表示无背景
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
