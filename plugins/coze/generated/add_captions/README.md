# add\_captions

## 工具名称

`add_captions`

## 工具介绍

此工具对应 FastAPI 端点: \`\`

没有提供详细文档注释

**重要提示**：本工具仅生成 API 调用代码，需配合使用才能生效。

使用步骤：

1. 调用本工具后，会返回 `api_call` 字段，其中包含生成的 API 调用代码
2. 将返回的 `api_call` 字段的值作为 `write_script` 工具的输入参数，调用 [Coze2剪映 - 在Coze IDE 中创建 基础工具](https://www.coze.cn/store/plugin/7573974660006674486) 插件中的 `write_script` 工具
3. `write_script` 工具会将代码写入脚本文件，最终通过导出脚本来执行所有操作

## 输入参数

* **draft\_id** (string, required): 草稿 ID
* **captions** (str, required): 字幕信息列表，JSON字符串
* **text\_color** (str, optional): 文本颜色（十六进制）
* **border\_color** (Optional\[str], optional): 边框颜色（十六进制）
* **alignment** (int, optional): 文本对齐方式
* **alpha** (float, optional): 文本透明度
* **font** (Optional\[str], optional): 字体名称
* **font\_size** (int, optional): 字体大小
* **letter\_spacing** (Optional\[float], optional): 字间距
* **line\_spacing** (Optional\[float], optional): 行间距
* **scale\_x** (float, optional): 水平缩放
* **scale\_y** (float, optional): 垂直缩放
* **transform\_x** (float, optional): 水平位移
* **transform\_y** (float, optional): 垂直位移
* **style\_text** (bool, optional): 是否使用样式文本
* **underline** (bool, optional): 文字下划线开关
* **italic** (bool, optional): 文本斜体开关
* **bold** (bool, optional): 文本加粗开关
* **has\_shadow** (bool, optional): 是否启用文本阴影
* **shadow\_info** (Optional\[ShadowInfo], optional): 文本阴影参数

## 输出参数

* **segment\_ids** (List\[str]): 字幕片段ID列表
* **api\_call** (str): 生成的 API 调用代码

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
