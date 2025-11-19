# make_clip_settings

## 功能描述

为 `ClipSettings` 类生成对象的辅助工具。

图像调节设置（镜像 pyJianYingDraft.ClipSettings）
对应 pyJianYingDraft 的 ClipSettings 类，用于控制片段的变换属性

此工具接收 ClipSettings 的所有参数（可选，有默认值的使用原始默认值），并返回一个 `ClipSettings` 类型的对象。
该对象可以在 Coze 工作流中传递给需要 ClipSettings 参数的其他工具。

## 输入参数

参数均为可选，有默认值的参数会使用原始默认值。

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| `alpha` | `float` | 透明度 (0.0-1.0) | `1.0` |
| `rotation` | `float` | 旋转角度（度） | `0.0` |
| `scale_x` | `float` | X 轴缩放比例 | `1.0` |
| `scale_y` | `float` | Y 轴缩放比例 | `1.0` |
| `transform_x` | `float` | X 轴位置偏移 | `0.0` |
| `transform_y` | `float` | Y 轴位置偏移 | `0.0` |

## 输出结果

返回一个 `ClipSettings` 类型的对象。

### 主要返回值

- `result`: `ClipSettings` 对象（成功时）或 `None`（失败时）

## 使用示例

### 在 Coze 工作流中使用

```json
{
  "alpha": 0.5,
  "rotation": 0.5,
  "scale_x": 0.5
}
```

### 返回的对象结构

成功时返回 `ClipSettings` 对象，包含以下字段：

```json
{
  "alpha": 0.5,
  "rotation": 0.5,
  "scale_x": 0.5
}
```

## 使用场景

1. **在 create_video_segment 等工具中使用**: 生成 ClipSettings 对象后，可以直接传递给需要此类型参数的 API 工具
2. **参数预处理**: 在调用主工具前，先构建好 ClipSettings 对象，使工作流更清晰
3. **参数复用**: 创建一个 ClipSettings 对象，可以在多个地方使用

## 注意事项

- 所有参数均为可选，未提供的参数将使用默认值（如果有）
- 返回的是 `ClipSettings` 类型对象，不是字典
- 可以在 Coze 工作流的后续步骤中直接使用此对象
