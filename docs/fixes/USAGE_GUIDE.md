# Handler Generator 使用指南（修复后版本）

## 概述

修复后的 handler generator 现在能够：
- ✅ 生成与原始 API schema 完全一致的类型定义
- ✅ 自动检测并导入所有自定义类型依赖
- ✅ 正确区分必需字段和可选字段
- ✅ 支持复杂的嵌套类型（如 `Optional[TimeRange]`, `List[ClipSettings]`）

## 快速开始

### 生成所有 handler 文件

```bash
cd Coze2JianYing
python scripts/generate_handler_from_api.py
```

这将扫描 `app/api/` 目录下的所有 POST API 端点，并在 `coze_plugin/raw_tools/` 目录下生成对应的 handler.py 文件。

## 生成的文件结构

每个工具会生成以下文件：

```
coze_plugin/raw_tools/
└── create_audio_segment/
    ├── handler.py      # 主处理器文件
    └── README.md       # 工具说明文档
```

## 生成的 handler.py 结构

### 标准模板

```python
"""
工具名称 工具处理器

自动从 API 端点生成: /endpoint/path
源文件: path/to/source.py
"""

import os
import json
import uuid
import time
from typing import NamedTuple, Dict, Any, Optional, List
from runtime import Args
from app.schemas.segment_schemas import CustomType1, CustomType2  # ✅ 自动导入

# Input 类型定义
class Input(NamedTuple):
    """工具名称 工具的输入参数"""
    required_field: str              # 必需字段
    another_required: TimeRange      # 必需字段（自定义类型）
    optional_field: Optional[str] = None  # 可选字段
    with_default: float = 1.0        # 有默认值的字段

# Output 类型定义
class Output(NamedTuple):
    """工具名称 工具的输出参数"""
    success: bool = False
    message: str = ""
    result_id: str = ""

def handler(args: Args[Input]) -> Output:
    """主处理函数"""
    # ... 实现代码
```

## 类型定义规则

### 1. 必需字段（Required Fields）

**原始 schema**:
```python
class CreateRequest(BaseModel):
    material_url: str = Field(...)  # Field(...) 表示必需
    target_timerange: TimeRange = Field(...)
```

**生成的 Input**:
```python
class Input(NamedTuple):
    material_url: str              # ✅ 无默认值 = 必需
    target_timerange: TimeRange    # ✅ 保持原类型
```

### 2. 可选字段（Optional Fields）

**原始 schema**:
```python
class CreateRequest(BaseModel):
    source_timerange: Optional[TimeRange] = Field(None)
    font_family: Optional[str] = Field("黑体")
```

**生成的 Input**:
```python
class Input(NamedTuple):
    source_timerange: Optional[TimeRange] = None  # ✅ 保持 Optional
    font_family: Optional[str] = "黑体"           # ✅ 保持默认值
```

### 3. 有默认值的非 Optional 字段

**原始 schema**:
```python
class CreateRequest(BaseModel):
    speed: float = Field(1.0)
    volume: float = Field(1.0)
```

**生成的 Input**:
```python
class Input(NamedTuple):
    speed: float = 1.0    # ✅ 不额外包装 Optional
    volume: float = 1.0   # ✅ 保持原类型
```

## 自定义类型自动导入

### 支持的自定义类型

生成器会自动检测并导入以下自定义类型：

- `TimeRange` - 时间范围
- `ClipSettings` - 图像调节设置
- `TextStyle` - 文本样式
- `Position` - 位置信息
- 以及 `app/schemas/segment_schemas.py` 中定义的所有其他类型

### 导入示例

**单个自定义类型**:
```python
from app.schemas.segment_schemas import TimeRange
```

**多个自定义类型**:
```python
from app.schemas.segment_schemas import ClipSettings, TimeRange
```

**复杂嵌套类型**:
```python
from app.schemas.segment_schemas import Position, TextStyle, TimeRange

class Input(NamedTuple):
    target_timerange: TimeRange                    # ✅ 直接使用
    text_style: Optional[TextStyle] = None        # ✅ 嵌套在 Optional 中
    position: Optional[Position] = None           # ✅ 自动识别
```

## 实际使用示例

### 示例 1: 创建音频段

```python
# coze_plugin/raw_tools/create_audio_segment/handler.py

from runtime import Args
from app.schemas.segment_schemas import TimeRange  # ✅ 自动导入

class Input(NamedTuple):
    """create_audio_segment 工具的输入参数"""
    material_url: str                              # 必需：音频 URL
    target_timerange: TimeRange                    # 必需：时间范围
    source_timerange: Optional[TimeRange] = None  # 可选：裁剪范围
    speed: float = 1.0                            # 可选：播放速度
    volume: float = 1.0                           # 可选：音量
    change_pitch: bool = False                    # 可选：是否变调

def handler(args: Args[Input]) -> Output:
    # 访问参数
    url = args.input.material_url
    timerange = args.input.target_timerange
    speed = args.input.speed

    # ... 处理逻辑
```

### 示例 2: 创建文本段

```python
# coze_plugin/raw_tools/create_text_segment/handler.py

from runtime import Args
from app.schemas.segment_schemas import Position, TextStyle, TimeRange  # ✅ 多个导入

class Input(NamedTuple):
    """create_text_segment 工具的输入参数"""
    text_content: str                             # 必需：文本内容
    target_timerange: TimeRange                   # 必需：时间范围
    font_family: Optional[str] = "黑体"           # 可选：字体
    font_size: Optional[float] = 24.0            # 可选：字号
    color: Optional[str] = "#FFFFFF"             # 可选：颜色
    text_style: Optional[TextStyle] = None       # 可选：文本样式
    position: Optional[Position] = None          # 可选：位置

def handler(args: Args[Input]) -> Output:
    # 使用自定义类型
    if args.input.text_style:
        # TextStyle 已正确导入，可以直接使用
        pass

    if args.input.position:
        # Position 已正确导入，可以直接使用
        pass

    # ... 处理逻辑
```

## 验证生成的代码

### 语法检查

```bash
# 检查单个文件
python -m py_compile coze_plugin/raw_tools/create_audio_segment/handler.py

# 检查所有生成的文件
python -m py_compile coze_plugin/raw_tools/*/handler.py
```

### 类型检查（可选）

如果安装了 mypy:
```bash
mypy coze_plugin/raw_tools/create_audio_segment/handler.py
```

## 常见问题

### Q1: 为什么有些字段没有默认值？

**A**: 这些是必需字段。在原始 API schema 中使用了 `Field(...)`，表示该字段是必需的。

```python
# 原始定义
material_url: str = Field(...)  # ... 表示必需

# 生成的 Input
material_url: str  # 无默认值 = 必需字段
```

### Q2: 自定义类型是从哪里导入的？

**A**: 所有自定义类型都从 `app.schemas.segment_schemas` 模块导入。这个模块包含了所有剪映草稿相关的数据模型。

### Q3: 如果需要修改生成的 handler，应该修改哪里？

**A**: 有两种情况：

1. **修改 API 定义本身**: 修改 `app/api/` 下的路由文件和 `app/schemas/segment_schemas.py`，然后重新运行生成器

2. **只修改生成逻辑**: 修改 `scripts/handler_generator/` 下的生成器脚本

### Q4: 生成器会覆盖已有的 handler 文件吗？

**A**: 是的。生成器会覆盖 `coze_plugin/raw_tools/` 下的所有文件。如
果需要自定义修改，建议：
- 将自定义代码放在其他目录
- 或者在 handler 文件中添加注释标记，然后修改生成器跳过这些文件

## 技术细节

### 类型提取机制

生成器使用 Python AST（抽象语法树）解析 schema 文件：

1. **识别字段类型**: 递归解析类型注解，支持嵌套泛型
2. **提取默认值**: 从 `Field()` 调用中提取默认值
3. **检测自定义类型**: 使用正则表达式匹配非基本类型
4. **生成导入语句**: 自动生成所需的 import 语句

### 默认值规则

| 原始定义 | 提取的默认值 | 生成的代码 |
|---------|-------------|-----------|
| `Field(...)` | `"Ellipsis"` | 无默认值（必需） |
| `Field(None)` | `"None"` | `= None` |
| `Field(1.0)` | `"1.0"` | `= 1.0` |
| `Field("text")` | `'"text"'` | `= "text"` |
| `Field(True)` | `"True"` | `= True` |

## 相关文档

- [完整修复报告](./handler_generator_fix_report.md) - 详细的技术分析
- [修复总结](./SUMMARY.md) - 快速概览

## 反馈和问题

如果在使用过程中发现问题，请：
1. 检查生成的代码语法
2. 验证原始 API schema 定义
3. 查看生成器的日志输出
4. 提交 Issue
 并附带详细信息

---

**生成器版本**: 修复后版本
**最后更新**: 2024年
**状态**: ✅ 已验证通过