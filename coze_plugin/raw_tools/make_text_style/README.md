# make_text_style

## 功能描述

为 `TextStyle` 类生成 Object 对象的辅助工具。

文本样式（镜像 pyJianYingDraft.TextStyle）
对应 pyJianYingDraft 的 TextStyle 类，用于控制文本的样式属性

此工具接收 TextStyle 的所有参数（全部为可选），并返回一个 Object（字典）表示。
该对象可以在 Coze 工作流中传递给需要 TextStyle 参数的其他工具。

## 输入参数

所有参数均为可选，仅在提供时才会包含在返回的对象中。

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| `font_size` | `float` | 字体大小 | `24.0` |
| `color` | `List[float]` | 文字颜色 RGB (0.0-1.0) | `...` |
| `bold` | `bool` | 是否加粗 | `False` |
| `italic` | `bool` | 是否斜体 | `False` |
| `underline` | `bool` | 是否下划线 | `False` |

## 输出结果

### Output 类型定义

```python
class Output(NamedTuple):
    result: Dict[str, Any]  # TextStyle 对象的字典表示
    success: bool           # 操作成功状态
    message: str            # 状态消息
```

## 使用示例

### 在 Coze 工作流中使用

```json
{
  "font_size": 0.5,
  "color": 0.5,
  "bold": true
}
```

### 返回示例

```json
{
  "result": {
  "font_size": 0.5,
  "color": 0.5,
  "bold": true
  },
  "success": true,
  "message": "TextStyle 对象创建成功"
}
```

## 使用场景

1. **在 create_video_segment 等工具中使用**: 生成 TextStyle 对象后，可以直接传递给需要此类型参数的 API 工具
2. **参数预处理**: 在调用主工具前，先构建好 TextStyle 对象，使工作流更清晰
3. **参数复用**: 创建一个 TextStyle 对象，可以在多个地方使用

## 注意事项

- 所有参数均为可选，未提供的参数不会出现在返回的对象中
- 返回的 `result` 字段是一个标准的 JSON 对象（字典）
- 可以在 Coze 工作流的后续步骤中直接使用此对象
