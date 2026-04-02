# create\_draft

## 工具名称

`create_draft`

## 工具介绍

此工具对应 FastAPI 端点: \`\`

没有提供详细文档注释

## 输入参数

* **width** (int, optional): 视频宽度（像素）
* **height** (int, optional): 视频高度（像素）

## 输出参数

* **draft\_id** (str): 草稿 UUID

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
