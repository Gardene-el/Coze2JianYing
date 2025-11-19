# make_text_style

## 功能描述

为 `TextStyle` 类生成对象的辅助工具。

文本样式（镜像 pyJianYingDraft.TextStyle）
对应 pyJianYingDraft 的 TextStyle 类，用于控制文本的样式属性

此工具接收 TextStyle 的所有参数（可选，有默认值的使用原始默认值），并返回一个 `TextStyle` 类型的对象。
该对象可以在 Coze 工作流中传递给需要 TextStyle 参数的其他工具。

## 输入参数

参数均为可选，有默认值的参数会使用原始默认值。

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| `font_size` | `float` | 字体大小 | `24.0` |
| `color` | `List[float]` | 文字颜色 RGB (0.0-1.0) | `[1.0, 1.0, 1.0]` |
| `bold` | `bool` | 是否加粗 | `False` |
| `italic` | `bool` | 是否斜体 | `False` |
| `underline` | `bool` | 是否下划线 | `False` |

## 输出结果

返回一个 `TextStyle` 类型的对象。

### 主要返回值

- `result`: `TextStyle` 对象（成功时）或 `None`（失败时）

## 使用示例

### 在 Coze 工作流中使用

```json
{
  "font_size": 0.5,
  "color": 0.5,
  "bold": true
}
```

### 返回的对象结构

成功时返回 `TextStyle` 对象，包含以下字段：

```json
{
  "font_size": 0.5,
  "color": 0.5,
  "bold": true
}
```

## 使用场景

1. **在 create_video_segment 等工具中使用**: 生成 TextStyle 对象后，可以直接传递给需要此类型参数的 API 工具
2. **参数预处理**: 在调用主工具前，先构建好 TextStyle 对象，使工作流更清晰
3. **参数复用**: 创建一个 TextStyle 对象，可以在多个地方使用

## 注意事项

- 所有参数均为可选，未提供的参数将使用默认值（如果有）
- 返回的是 `TextStyle` 类型对象，不是字典
- 可以在 Coze 工作流的后续步骤中直接使用此对象
