# create\_audio\_segment

## 工具名称

`create_audio_segment`

## 工具介绍

此工具对应 FastAPI 端点: \`\`

没有提供详细文档注释

## 输入参数

* **material\_url** (str, optional): 音频素材 URL
* **target\_timerange** (TimeRange, required): 在轨道上的时间范围
* **source\_timerange** (Optional\[TimeRange], optional): 素材裁剪范围
* **speed** (float, optional): 播放速度
* **volume** (float, optional): 音量 0-2
* **change\_pitch** (bool, optional): 是否跟随变速改变音调

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
