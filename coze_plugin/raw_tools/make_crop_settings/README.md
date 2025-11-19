# make_crop_settings

## 功能描述

为 `CropSettings` 类生成对象的辅助工具。

裁剪设置（镜像 pyJianYingDraft.CropSettings）
对应 pyJianYingDraft 的 CropSettings 类，用于定义裁剪区域的四个角点坐标

此工具接收 CropSettings 的所有参数（可选，有默认值的使用原始默认值），并返回一个 `CropSettings` 类型的对象。
该对象可以在 Coze 工作流中传递给需要 CropSettings 参数的其他工具。

## 输入参数

参数均为可选，有默认值的参数会使用原始默认值。

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| `upper_left_x` | `float` | 左上角 X 坐标 (0.0-1.0) | `0.0` |
| `upper_left_y` | `float` | 左上角 Y 坐标 (0.0-1.0) | `0.0` |
| `upper_right_x` | `float` | 右上角 X 坐标 (0.0-1.0) | `1.0` |
| `upper_right_y` | `float` | 右上角 Y 坐标 (0.0-1.0) | `0.0` |
| `lower_left_x` | `float` | 左下角 X 坐标 (0.0-1.0) | `0.0` |
| `lower_left_y` | `float` | 左下角 Y 坐标 (0.0-1.0) | `1.0` |
| `lower_right_x` | `float` | 右下角 X 坐标 (0.0-1.0) | `1.0` |
| `lower_right_y` | `float` | 右下角 Y 坐标 (0.0-1.0) | `1.0` |

## 输出结果

返回一个包含 `CropSettings` 字段的字典。

### 主要返回值

- `result`: `CropSettings` 字典（成功时）或空字典（失败时）

## 使用示例

### 在 Coze 工作流中使用

```json
{
  "upper_left_x": 0.5,
  "upper_left_y": 0.5,
  "upper_right_x": 0.5
}
```

### 返回的字典结构

成功时返回包含以下字段的字典：

```json
{
  "upper_left_x": 0.5,
  "upper_left_y": 0.5,
  "upper_right_x": 0.5
}
```

## 使用场景

1. **在 create_video_segment 等工具中使用**: 生成 CropSettings 对象后，可以直接传递给需要此类型参数的 API 工具
2. **参数预处理**: 在调用主工具前，先构建好 CropSettings 对象，使工作流更清晰
3. **参数复用**: 创建一个 CropSettings 对象，可以在多个地方使用

## 注意事项

- 所有参数均为可选，未提供的参数将使用默认值（如果有）
- 返回的是字典类型，包含 `CropSettings` 的所有字段
- 可以在 Coze 工作流的后续步骤中直接使用此字典
