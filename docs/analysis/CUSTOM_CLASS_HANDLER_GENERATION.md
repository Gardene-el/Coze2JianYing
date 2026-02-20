# 自定义类 Handler 生成系统

## 概述

本文档描述了为 `general_schemas.py` 中的自定义类自动生成 Coze handler 工具的系统。

## 背景

在 Coze 工作流中，需要能够创建和传递自定义类对象（如 TimeRange、ClipSettings、TextStyle、CropSettings）。由于 Coze 平台的限制，不能直接在工作流中构造复杂的对象，因此需要专门的辅助工具来创建这些对象。

## 生成的工具

系统自动为以下自定义类生成了 handler 工具：

### 1. make_time_range

- **类**: TimeRange
- **参数**: start (int), duration (int)
- **用途**: 创建时间范围对象，用于指定媒体片段的时间区间

### 2. make_clip_settings

- **类**: ClipSettings
- **参数**: alpha, rotation, scale_x, scale_y, transform_x, transform_y
- **用途**: 创建图像调节设置对象，控制片段的变换属性

### 3. make_text_style

- **类**: TextStyle
- **参数**: font_size, color, bold, italic, underline
- **用途**: 创建文本样式对象，控制文本的样式属性

### 4. make_crop_settings

- **类**: CropSettings
- **参数**: upper_left_x, upper_left_y, upper_right_x, upper_right_y, lower_left_x, lower_left_y, lower_right_x, lower_right_y
- **用途**: 创建裁剪设置对象，定义裁剪区域的四个角点坐标

## 工具特点

每个生成的 handler 工具都具有以下特点：

1. **所有参数可选**: 所有输入参数都是可选的，用户可以只提供需要的参数
2. **返回字典对象**: 返回标准的 JSON 对象（字典），可以直接在 Coze 工作流中传递
3. **仅包含提供的参数**: 返回的对象只包含用户实际提供的参数，未提供的参数不会出现
4. **完整的文档**: 每个工具都有详细的 README.md 文档

## 使用示例

### 在 Coze 工作流中使用

```
步骤 1: 调用 make_time_range 工具
输入:
{
  "start": 0,
  "duration": 5000000
}

输出:
{
  "result": {
    "start": 0,
    "duration": 5000000
  },
  "success": true,
  "message": "TimeRange 对象创建成功"
}

步骤 2: 将 result 传递给其他工具
使用步骤1的 result 作为 target_timerange 参数传递给 create_video_segment 等工具
```

## 技术实现

### 附加流程模块

新增的 `generate_custom_class_handlers.py` 模块负责：

1. **扫描自定义类**: 从 `general_schemas.py` 识别目标自定义类
2. **提取字段信息**: 使用 SchemaExtractor 提取类的所有字段和类型
3. **生成 Input 类**: 将所有参数转换为可选参数
4. **生成 handler 函数**: 创建处理逻辑，仅包含非 None 参数
5. **生成文档**: 自动生成详细的 README.md

### 生成流程

```
general_schemas.py
    ↓
附加流程: CustomClassHandlerGenerator
    ↓
    ├── 扫描目标类 (TimeRange, ClipSettings, TextStyle, CropSettings)
    ├── 提取字段信息
    ├── 生成 handler.py
    └── 生成 README.md
    ↓
coze_plugin/raw_tools/make_*/
```

### 目录结构

```
coze_plugin/raw_tools/
├── make_time_range/
│   ├── handler.py
│   └── README.md
├── make_clip_settings/
│   ├── handler.py
│   └── README.md
├── make_text_style/
│   ├── handler.py
│   └── README.md
└── make_crop_settings/
    ├── handler.py
    └── README.md
```

## 如何重新生成

如果需要重新生成这些 handler（例如，在 general_schemas.py 中添加了新的自定义类），运行：

```bash
python scripts/generate_custom_class_handlers.py
```

## 与 API Handler 的区别

| 特性     | API Handler                  | 自定义类 Handler |
| -------- | ---------------------------- | ---------------- |
| 用途     | 调用后端 API 端点            | 构造对象         |
| 输入     | 必需和可选参数混合           | 全部可选参数     |
| 输出     | API 响应                     | 简单的字典对象   |
| 复杂度   | 包含 API 调用代码生成        | 简单的对象构造   |
| 文件追加 | 追加到 /tmp/coze2jianying.py | 不追加文件       |

## 测试

运行测试脚本验证生成的 handler：

```bash
python scripts/test_custom_class_handlers.py
```

测试覆盖：

- 验证 handler 文件结构正确
- 验证 Input/Output 类型定义
- 验证 handler 函数可调用
- 验证返回值格式正确

## 维护说明

### 添加新的自定义类

要为新的自定义类生成 handler：

1. 在 `general_schemas.py` 中定义新的 Pydantic 模型类
2. 在 `generate_custom_class_handlers.py` 的 `TARGET_CLASSES` 列表中添加类名
3. 运行生成脚本：`python scripts/generate_custom_class_handlers.py`

### 修改现有类

如果修改了现有自定义类的字段：

1. 更新 `general_schemas.py` 中的类定义
2. 重新运行生成脚本
3. 生成器会覆盖现有的 handler 文件

## 相关文件

- `scripts/handler_generator/generate_custom_class_handlers.py` - 附加流程模块
- `scripts/generate_custom_class_handlers.py` - 生成脚本主程序
- `scripts/test_custom_class_handlers.py` - 测试脚本
- `app/schemas/general_schemas.py` - 自定义类定义
- `coze_plugin/raw_tools/make_*/` - 生成的 handler 工具

## 注意事项

1. **Coze 平台限制**: 生成的 handler 使用 `from runtime import Args`，这个模块只在 Coze 平台上可用
2. **参数命名**: 所有参数名保持与原始类定义一致
3. **类型安全**: 使用 NamedTuple 提供类型提示，但在 Coze 中运行时不强制类型检查
4. **向后兼容**: 新生成的 handler 不会影响现有的工作流

## 未来改进

- [ ] 支持嵌套的自定义类（当一个类包含另一个自定义类作为字段时）
- [ ] 添加参数验证逻辑（如范围检查）
- [ ] 支持生成示例 JSON 数据用于测试
- [ ] 自动检测 general_schemas.py 中的新增类并提示生成
