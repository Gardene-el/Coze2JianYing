# caption_infos

## 功能描述

将文本列表与时间线合并，生成 `add_captions` 工具所需的 `captions` JSON 字符串。

支持两种关键词指定方式：

1. **内联语法**：在文本中使用 `"正文||关键词"` 格式
2. **keywords 参数**：通过独立 JSON 数组按索引为每条字幕指定关键词（优先级更高）

纯计算工具，无网络请求，无文件 I/O。

## 输入参数

```python
class Input(NamedTuple):
    texts: str                              # 文本数组，JSON 字符串，如 '["大家好","欢迎观看"]'
    timelines: str                          # 时间线 JSON 字符串
    font_size: Optional[int] = None         # 统一字体大小
    keyword_color: Optional[str] = None     # 关键词颜色（十六进制，如 "#ff7100"）
    keyword_font_size: Optional[int] = None # 关键词字体大小
    keywords: Optional[str] = None         # 关键词数组，JSON 字符串，如 '["kw1","kw2"]'
    in_animation: Optional[str] = None
    in_animation_duration: Optional[int] = None
    loop_animation: Optional[str] = None
    loop_animation_duration: Optional[int] = None
    out_animation: Optional[str] = None
    out_animation_duration: Optional[int] = None
    transition: Optional[str] = None
    transition_duration: Optional[int] = None
```

### 关键词说明

**方式 1 — 内联语法**（在文本中使用 `||` 分隔关键词）：

```json
["今天天气||天气", "股市上涨||上涨"]
```

解析结果：

- text=`"今天天气"`，keyword=`"天气"`
- text=`"股市上涨"`，keyword=`"上涨"`

**方式 2 — keywords 参数**（JSON 字符串数组）：

```
keywords='["天气", "上涨"]'
```

`keywords` 参数优先级高于内联语法。

## 输出

```python
class Output(NamedTuple):
    captions: str   # add_captions 所需的 JSON 字符串
    success: bool
    message: str
```

### 输出格式

```json
[
  {
    "start": 0,
    "end": 3000000,
    "text": "今天天气",
    "keyword": "天气",
    "keyword_color": "#ff7100",
    "font_size": 20,
    "in_animation": "渐入",
    "in_animation_duration": 500000
  }
]
```

## 工作流衔接

```
timelines → caption_infos → add_captions
```
