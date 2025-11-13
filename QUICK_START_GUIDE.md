# CustomNamespace 处理修复 - 快速开始指南

## 📋 修复概述

本次修复解决了 Handler Generator 在处理 Coze 平台 CustomNamespace 对象时的关键问题，从"dict 字面量方案"升级为"类型构造方案"。

## ❌ 旧方案的问题

```python
# 旧方案生成的代码（有问题）
req_params['target_timerange'] = {"start": 0, "duration": 5000000}

# 问题：
# 1. f-string 转义导致双大括号 {{"start": 0}}
# 2. 运行时错误: unhashable type: 'dict'
# 3. dict 类型与 TimeRange 类型不匹配
```

## ✅ 新方案的优势

```python
# 新方案生成的代码（正确）
req_params['target_timerange'] = TimeRange(start=0, duration=5000000)

# 优势：
# 1. 无转义问题（关键字参数格式）
# 2. 类型正确（TimeRange 实例）
# 3. 可直接执行（应用端已导入类型）
```

## 🚀 快速开始

### 1. 验证修复

运行测试确认新方案工作正常：

```bash
# 测试类型构造方案
python scripts/test_type_constructor.py

# 测试类型名提取
python scripts/test_extract_type_name.py
```

**期望结果**：所有测试通过 ✅

### 2. 重新生成 Handler

使用新方案重新生成所有 handler 文件：

```bash
python scripts/generate_handler_from_api.py
```

这会更新 `coze_plugin/raw_tools/` 目录下的所有 handler 文件。

### 3. 验证生成的代码

检查生成的 handler 文件中的 `_to_type_constructor` 函数：

```python
# 在任意 handler.py 中应该看到：
def _to_type_constructor(obj, type_name: str) -> str:
    """将 CustomNamespace 转换为类型构造表达式"""
    # ... 实现代码
```

## 📚 核心变更

### E 脚本 (e_api_call_code_generator.py)

**新增功能**：
- `_extract_type_name()` - 从类型字符串提取核心类型名
- 重构 `_is_complex_type()` - 更准确的类型判断
- 修改 `_format_param_value()` - 生成类型构造调用

**示例**：
```python
# Optional[TimeRange] -> "TimeRange"
type_name = self._extract_type_name("Optional[TimeRange]")

# 生成: {_to_type_constructor(args.input.field, 'TimeRange')}
formatted = self._format_param_value("field", "Optional[TimeRange]")
```

### D 脚本 (d_handler_function_generator.py)

**核心变更**：
- 移除 `_to_dict_repr()` ❌
- 新增 `_to_type_constructor()` ✅

**功能对比**：
```python
# 旧函数
_to_dict_repr(obj) -> '{"start": 0, "duration": 5000000}'

# 新函数
_to_type_constructor(obj, 'TimeRange') -> 'TimeRange(start=0, duration=5000000)'
```

## 🧪 测试覆盖

### test_type_constructor.py
- ✅ _to_type_constructor 函数逻辑
- ✅ 生成代码输出格式
- ✅ 类型构造表达式可执行性
- ✅ 确保不生成 dict 字面量

### test_extract_type_name.py
- ✅ 类型名提取（14 个测试用例）
- ✅ 复杂类型判断（16 个测试用例）
- ✅ 参数值格式化（7 个测试用例）

## 📖 完整文档

### 技术细节
- **详细文档**: `docs/handler_generator/CUSTOMNAMESPACE_HANDLING.md`
- **版本记录**: `scripts/handler_generator/CHANGELOG.md`
- **修复总结**: `CUSTOMNAMESPACE_FIX_SUMMARY.md`

### 模块文档
- **Handler Generator**: `scripts/handler_generator/README.md`

## 🔍 工作流程示例

### 输入（Coze 云端）
```python
args.input = SimpleNamespace(
    material_url="https://example.com/video.mp4",
    target_timerange=SimpleNamespace(start=0, duration=5000000),
    clip_settings=SimpleNamespace(brightness=0.5)
)
```

### 处理（Handler 运行时）
```python
# Handler 调用 _to_type_constructor
timerange_expr = _to_type_constructor(
    args.input.target_timerange, 
    'TimeRange'
)
# 返回: "TimeRange(start=0, duration=5000000)"
```

### 输出（生成的脚本）
```python
# /tmp/coze2jianying.py
req_params_abc123 = {}
req_params_abc123['material_url'] = "https://example.com/video.mp4"
req_params_abc123['target_timerange'] = TimeRange(start=0, duration=5000000)
req_params_abc123['clip_settings'] = ClipSettings(brightness=0.5)

req_abc123 = CreateVideoSegmentRequest(**req_params_abc123)
resp_abc123 = await create_video_segment(req_abc123)
```

### 执行（应用端）
```python
# 应用端已导入类型定义
from app.schemas.segment_schemas import TimeRange, ClipSettings

# 直接执行脚本，所有类型构造都能正确执行
exec(script_content)  # ✅ 成功
```

## ⚙️ 类型推断规则

对于嵌套对象，通过字段名智能推断类型：

| 字段名模式 | 推断类型 |
|-----------|---------|
| `*_settings` | `ClipSettings` |
| `*_timerange` | `TimeRange` |
| `*_style` | `TextStyle` |
| `*_position` | `Position` |
| 其他 | 首字母大写的字段名 |

## 🔧 故障排查

### 问题：生成的 handler 仍然使用旧方案

**解决**：重新运行生成器
```bash
python scripts/generate_handler_from_api.py
```

### 问题：测试失败

**解决**：
1. 检查 Python 版本（需要 3.7+）
2. 确认项目依赖已安装：`pip install -r requirements.txt`
3. 查看测试输出的详细错误信息

### 问题：类型名提取不正确

**解决**：
- 检查类型字符串格式（应该是 PascalCase）
- 查看 `_extract_type_name()` 的正则表达式逻辑
- 如果是新类型，可能需要添加到智能推断规则

## ✅ 验证清单

完成修复后，请确认：

- [ ] 测试全部通过 (test_type_constructor.py)
- [ ] 测试全部通过 (test_extract_type_name.py)
- [ ] 重新生成了 handler 文件
- [ ] 检查生成的代码包含 `_to_type_constructor`
- [ ] 阅读了 CUSTOMNAMESPACE_HANDLING.md 文档
- [ ] 理解了新旧方案的区别

## 📞 支持

如有问题，请参考：
- 详细文档：`docs/handler_generator/CUSTOMNAMESPACE_HANDLING.md`
- 修复总结：`CUSTOMNAMESPACE_FIX_SUMMARY.md`
- 文件清单：`FILES_CHANGED.md`

## 🎯 总结

本次修复：
- ✅ 解决了 f-string 转义问题
- ✅ 修复了运行时类型错误
- ✅ 生成更符合预期的代码
- ✅ 保持向后兼容性
- ✅ 提供完整的测试覆盖
- ✅ 更新了相关文档

新方案更加健壮、可靠，生成的代码可以在应用端直接执行！