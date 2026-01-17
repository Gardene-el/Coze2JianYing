# API 到 Handler 生成器使用文档

## 概述

`generate_handler_from_api.py` 是一个模块化的自动化工具，用于从 FastAPI 端点生成 Coze 平台兼容的 handler.py 文件。该工具实现了 Issue #162 中提出的分步生成逻辑。

## 功能特点

- **模块化设计**: 各步骤模块分别实现在独立文件中，便于管理和维护
- **自动扫描**: 自动扫描 `/app/api` 目录下所有 POST API 端点
- **智能解析**: 解析 Pydantic schemas，提取请求和响应模型
- **完整生成**: 为每个 API 端点生成完整的 Coze handler.py 和 README.md
- **UUID 管理**: 自动生成 UUID 跟踪和管理逻辑
- **API 调用记录**: 生成代码将 API 调用记录到 `/tmp/coze2jianying.py`

## 目录结构

### 脚本模块结构

```
scripts/
├── generate_handler_from_api.py      # 主程序
└── handler_generator/                # 生成器模块包
    ├── __init__.py                   # 包初始化
    ├── README.md                     # 模块文档
    ├── api_endpoint_info.py          # 数据模型
    ├── scan_api_endpoints.py         # 步骤1：扫描API
    ├── generate_io_models.py         # 步骤3：生成Input/Output
    ├── generate_api_call_code.py     # 步骤4：生成API调用代码
    ├── generate_handler_function.py  # 步骤5：生成handler函数
    ├── create_tool_scaffold.py       # 步骤6：创建文件夹与文档
    └── schema_extractor.py           # 辅助：Schema提取器
```

### 生成的工具目录

```
coze_plugin/
└── raw_tools/          # 自动生成的 handler 工具
    ├── create_draft/   # 示例工具
    │   ├── handler.py  # Coze 工具处理器
    │   └── README.md   # 工具文档
    ├── add_track/
    │   ├── handler.py
    │   └── README.md
    └── ...
```

## 使用方法

### 基本使用

1. **运行生成器**:

   ```bash
   python scripts/generate_handler_from_api.py
   ```

2. **查看生成结果**:
   - 生成的工具位于 `coze_plugin/raw_tools/`
   - 每个工具包含 `handler.py` 和 `README.md`

### 验证生成的文件

运行测试脚本验证生成的 handler 语法正确性：

```bash
python scripts/test_generated_handlers.py
```

## 生成器逻辑说明

根据 Issue #162 中的分步逻辑实现，现已模块化为独立文件：

### 步骤 1: 扫描 API 端点 (`scan_api_endpoints.py`)

- 扫描 `/app/api` 下所有 `*_routes.py` 文件
- 识别使用 `@router.post` 装饰器的异步函数
- 提取端点路径、请求/响应模型、路径参数等信息
- **主要类**: `APIScanner`

### 步骤 6: 创建工具文件夹 (`create_tool_scaffold.py`)

- 在 `coze_plugin/raw_tools/` 下创建与函数名同名的文件夹
- 生成 `handler.py` 和 `README.md` 文件
- **主要类**: `FolderCreator`

### 步骤 3: 定义 Input/Output 类型 (`generate_io_models.py`)

- **Input**: 包含路径参数（draft_id/segment_id）+ Request 模型的所有字段
- **Output**: 返回 `Dict[str, Any]` 类型（确保 Coze 平台正确序列化）
- **主要类**: `InputOutputGenerator`

### 步骤 5: 定义 handler 函数 (`generate_handler_function.py`)

1. 接收 `Args[Input]` 类型参数
2. 调用 `ensure_coze2jianying_file()` 确保文件存在
3. 生成唯一 UUID
4. 执行 E 脚本逻辑
5. 返回 Output 类型数据，ID 字段使用生成的 UUID

- **主要类**: `HandlerFunctionGenerator`

### 步骤 4: 写入 API 调用记录 (`generate_api_call_code.py`)

生成的代码会追加以下内容到 `/tmp/coze2jianying.py`：

1. 创建 request 对象: `req_{uuid} = RequestModel(...)`
2. 调用 API 函数: `resp_{uuid} = await api_function(...)`
3. 提取结果ID: `draft_id_{uuid} = resp_{uuid}.draft_id`

- **主要类**: `APICallCodeGenerator`

### 辅助模块: Schema 提取器 (`schema_extractor.py`)

- 解析 Pydantic BaseModel 类定义
- 提取字段名、类型、默认值、描述
- 供步骤 3/4/5 使用
- **主要类**: `SchemaExtractor`

## 模块化设计优势

1. **易于维护**: 每个脚本职责单一，修改某个功能只需编辑对应文件
2. **易于测试**: 可以为每个模块编写独立的单元测试
3. **易于扩展**: 添加新功能时不影响其他模块
4. **易于理解**: 模块边界清晰，符合分步生成的设计思路

## 生成的 Handler 结构

每个生成的 `handler.py` 包含以下部分：

### 1. 导入和类型定义

```python
from typing import NamedTuple, Dict, Any, Optional, List
from runtime import Args

class Input(NamedTuple):
    """工具的输入参数"""
    # 自动生成的字段...
```

### 2. 辅助函数

```python
def ensure_coze2jianying_file() -> str:
    """确保 /tmp/coze2jianying.py 文件存在"""
    # ...

def append_api_call_to_file(file_path: str, api_call_code: str):
    """追加 API 调用代码到文件"""
    # ...
```

### 3. Handler 函数

```python
def handler(args: Args[Input]) -> Dict[str, Any]:
    """主处理函数"""
    try:
        # 生成 UUID
        generated_uuid = str(uuid.uuid4())

        # 生成 API 调用代码
        api_call = f"""..."""

        # 写入文件
        coze_file = ensure_coze2jianying_file()
        append_api_call_to_file(coze_file, api_call)

        # 返回结果
        return {...}
    except Exception as e:
        return {"success": False, "message": str(e)}
```

## 生成的 README 结构

每个 README.md 包含：

1. **功能描述**: API 端点的路径和用途
2. **API 信息**: 函数名、HTTP 方法、模型信息
3. **路径参数**: draft_id、segment_id 等
4. **使用说明**: 工具的基本使用方法
5. **注意事项**: 沙盒环境、文件路径等重要提示

## 当前生成结果

运行 `generate_handler_from_api.py` 会生成 **28 个工具**：

### Draft 操作工具 (6个)

- `create_draft` - 创建草稿
- `add_track` - 添加轨道
- `add_segment` - 添加片段到草稿
- `add_global_effect` - 添加全局特效
- `add_global_filter` - 添加全局滤镜
- `save_draft` - 保存草稿

### Segment 创建工具 (6个)

- `create_audio_segment` - 创建音频片段
- `create_video_segment` - 创建视频片段
- `create_text_segment` - 创建文本片段
- `create_sticker_segment` - 创建贴纸片段
- `create_effect_segment` - 创建特效片段
- `create_filter_segment` - 创建滤镜片段

### 音频片段操作工具 (3个)

- `add_audio_effect` - 添加音频特效
- `add_audio_fade` - 添加音频淡入淡出
- `add_audio_keyframe` - 添加音量关键帧

### 视频片段操作工具 (7个)

- `add_video_animation` - 添加视频动画
- `add_video_effect` - 添加视频特效
- `add_video_fade` - 添加视频淡入淡出
- `add_video_filter` - 添加视频滤镜
- `add_video_mask` - 添加视频蒙版
- `add_video_transition` - 添加视频转场
- `add_video_background_filling` - 添加背景填充
- `add_video_keyframe` - 添加视觉属性关键帧

### 其他片段操作工具 (6个)

- `add_sticker_keyframe` - 添加贴纸关键帧
- `add_text_animation` - 添加文字动画
- `add_text_bubble` - 添加文字气泡
- `add_text_effect` - 添加花字特效
- `add_text_keyframe` - 添加文本关键帧

## 测试验证

运行测试脚本进行验证：

```bash
$ python scripts/test_generated_handlers.py

============================================================
测试总结
============================================================
总计: 28 个工具
通过: 28 个
失败: 0 个
成功率: 100.0%
============================================================
```

测试内容包括：

1. **Python 语法检查** - 使用 AST 解析验证语法正确性
2. **结构完整性检查** - 验证包含必需的类和函数
3. **文档完整性检查** - 验证 README.md 存在且非空

## 注意事项

1. **生成目录**:
   - 生成的工具保存在 `coze_plugin/raw_tools/`
   - 每次运行前可以清空该目录避免冲突

2. **依赖要求**:
   - 需要正确的 FastAPI 路由文件在 `app/api/`
   - 需要 Pydantic schemas 文件在 `app/schemas/segment_schemas.py`

3. **Coze 平台限制**:
   - 生成的 handler 假设在 Coze 沙盒环境中运行
   - `/tmp` 目录限制为 512MB
   - 工具函数必须导出名为 `handler` 的入口函数

4. **手动调整**:
   - 生成的代码是基础框架，可能需要手动调整以满足特定需求
   - 复杂的业务逻辑需要在生成后手动添加

## 脚本逻辑分析

根据 Issue #162 中的 A-E 脚本描述，本实现完全符合预期逻辑：

### ✅ A 脚本逻辑

- 扫描 `/app/api` 下所有 POST API 函数
- 对每个函数执行 B 脚本

### ✅ B 脚本逻辑

- 在 `coze_plugin/raw_tools` 下创建同名文件夹
- 创建 `handler.py` 和 `README.md`
- handler.py 内容由 C 脚本生成

### ✅ C 脚本逻辑

- 定义 `Input(NamedTuple)` 包含:
  - 路径参数 (draft_id/segment_id)
  - Request 模型的所有字段
- 定义 `Output` 返回类型 (Dict)
- 使用 D 脚本定义 handler 函数

### ✅ D 脚本逻辑

- Handler 函数接收 `Args[Input]` 参数
- 检查/创建 `/tmp/coze2jianying.py`
- 生成 UUID 变量
- 执行 E 脚本
- 返回 Output，ID 字段使用 UUID

### ✅ E 脚本逻辑

- 使用 Input 参数构造 request 对象
- 生成 API 调用代码字符串
- 追加到 `coze2jianying.py` 文件
- 如果有 ID 返回，提取并保存

## 常见问题

### Q: 为什么使用 Dict[str, Any] 而不是 NamedTuple 作为 Output？

A: Coze 平台需要正确的 JSON 序列化。Dict 类型确保返回值可以被正确序列化为 JSON 对象。

### Q: 生成的 handler 可以直接在 Coze 中使用吗？

A: 生成的代码是基础框架，包含了正确的结构和逻辑。但可能需要根据具体的 API 行为进行微调。

### Q: 如何处理复杂的嵌套类型？

A: 生成器会将复杂类型简化为 `Any`、`Optional[Any]` 或 `List[Any]`，在使用时需要确保类型兼容。

### Q: 生成的文件可以提交到版本控制吗？

A: 这取决于项目需求。建议将 `raw_tools/` 目录添加到 `.gitignore`，因为这些文件是自动生成的。

## 开发和调试

如果需要修改生成逻辑：

1. 编辑 `scripts/generate_handler_from_api.py`
2. 清空 `coze_plugin/raw_tools/` 目录
3. 运行生成器重新生成
4. 运行测试脚本验证

## 贡献

如果发现生成器的 bug 或有改进建议：

1. 在 Issue #162 中描述问题
2. 提供具体的 API 端点示例
3. 说明期望的生成结果
