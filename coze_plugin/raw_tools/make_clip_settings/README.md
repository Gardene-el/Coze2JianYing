# make_clip_settings

## 功能描述

为 `ClipSettings` 类生成 Object 对象的辅助工具。

图像调节设置（镜像 pyJianYingDraft.ClipSettings）
对应 pyJianYingDraft 的 ClipSettings 类，用于控制片段的变换属性

此工具接收 ClipSettings 的所有参数（全部为可选），并返回一个 Object（字典）表示。
该对象可以在 Coze 工作流中传递给需要 ClipSettings 参数的其他工具。

## 输入参数

所有参数均为可选，仅在提供时才会包含在返回的对象中。

| 参数名 | 类型 | 描述 | 默认值 |
|--------|------|------|--------|
| `alpha` | `float` | 透明度 (0.0-1.0) | `1.0` |
| `rotation` | `float` | 旋转角度（度） | `0.0` |
| `scale_x` | `float` | X 轴缩放比例 | `1.0` |
| `scale_y` | `float` | Y 轴缩放比例 | `1.0` |
| `transform_x` | `float` | X 轴位置偏移 | `0.0` |
| `transform_y` | `float` | Y 轴位置偏移 | `0.0` |

## 输出结果

### Output 类型定义

```python
class Output(NamedTuple):
    result: Dict[str, Any]  # ClipSettings 对象的字典表示
    success: bool           # 操作成功状态
    message: str            # 状态消息
```

## 使用示例

### 在 Coze 工作流中使用

```json
{
  "alpha": 0.5,
  "rotation": 0.5,
  "scale_x": 0.5
}
```

### 返回示例

```json
{
  "result": {
  "alpha": 0.5,
  "rotation": 0.5,
  "scale_x": 0.5
  },
  "success": true,
  "message": "ClipSettings 对象创建成功"
}
```

## 使用场景

1. **在 create_video_segment 等工具中使用**: 生成 ClipSettings 对象后，可以直接传递给需要此类型参数的 API 工具
2. **参数预处理**: 在调用主工具前，先构建好 ClipSettings 对象，使工作流更清晰
3. **参数复用**: 创建一个 ClipSettings 对象，可以在多个地方使用

## 注意事项

- 所有参数均为可选，未提供的参数不会出现在返回的对象中
- 返回的 `result` 字段是一个标准的 JSON 对象（字典）
- 可以在 Coze 工作流的后续步骤中直接使用此对象
