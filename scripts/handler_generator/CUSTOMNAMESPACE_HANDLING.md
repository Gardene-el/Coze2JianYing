# CustomNamespace 处理机制

## 问题背景

在 Coze 云端环境中，复杂类型的参数（如 `TimeRange`, `ClipSettings` 等 NamedTuple）会被表示为 `CustomNamespace` 对象。例如：

```python
# Coze 云端传入的参数
args.input.target_timerange = CustomNamespace(start=0, duration=5000000)
```

当这些参数被直接插值到 f-string 中生成脚本代码时，会输出其 `repr()` 形式：

```python
req_params_xxx['target_timerange'] = CustomNamespace(start=0, duration=5000000)
```

这会导致问题：
1. **应用端无法识别 CustomNamespace** - `CustomNamespace` 是 Coze 平台的专有类型，在应用端执行脚本时不存在
2. **Pydantic 验证失败** - Pydantic 期望的是 dict 或模型实例，而不是 CustomNamespace 对象

## 解决方案

### 核心思路

在 **handler 函数运行时**（Coze 云端），将 `CustomNamespace` 对象转换为 **dict 字面量字符串**，然后写入脚本文件。这样应用端执行脚本时，读取到的是标准的 Python dict，可以被 Pydantic 正确解析。

### 实现架构

#### 1. 辅助函数 `_to_dict_repr`

在生成的每个 handler.py 文件中，包含一个辅助函数：

```python
def _to_dict_repr(obj) -> str:
    """
    将对象转换为 dict 字面量字符串表示
    
    处理 Coze 的 CustomNamespace/SimpleNamespace 对象
    """
    if obj is None:
        return 'None'
    
    # 检查是否有 __dict__ 属性
    if hasattr(obj, '__dict__'):
        obj_dict = obj.__dict__
        items = []
        for key, value in obj_dict.items():
            # 递归处理嵌套对象
            if hasattr(value, '__dict__'):
                value_repr = _to_dict_repr(value)
            elif isinstance(value, str):
                value_repr = f'"{value}"'
            else:
                value_repr = repr(value)
            items.append(f'"{key}": {value_repr}')
        return '{{' + ', '.join(items) + '}}'
    
    if isinstance(obj, str):
        return f'"{obj}"'
    else:
        return repr(obj)
```

#### 2. E 脚本：识别复杂类型

在 `e_api_call_code_generator.py` 中添加类型判断逻辑：

```python
def _is_complex_type(self, field_type: str) -> bool:
    """判断字段类型是否为复杂类型（需要转换为 dict）"""
    # 去除 Optional 包装
    field_type = field_type.strip().replace("Optional[", "").rstrip("]")
    
    # 基本类型不是复杂类型
    basic_types = ["str", "int", "float", "bool", "None"]
    if field_type in basic_types:
        return False
    
    # List, Dict, Tuple 等泛型类型也不算
    if field_type.startswith(("List[", "Dict[", "Tuple[", "Set[")):
        return False
    
    # 其他类型（如 TimeRange, ClipSettings）视为复杂类型
    return True
```

#### 3. 格式化参数值

在 `_format_param_value` 方法中，对复杂类型调用 `_to_dict_repr`：

```python
def _format_param_value(self, field_name: str, field_type: str) -> str:
    access_expr = "args.input." + field_name
    
    if self._should_quote_type(field_type):
        # 字符串类型：需要引号
        return '"{' + access_expr + '}"'
    elif self._is_complex_type(field_type):
        # 复杂类型：调用 _to_dict_repr 转换
        return "{_to_dict_repr(" + access_expr + ")}"
    else:
        # 基本类型：直接插值
        return "{" + access_expr + "}"
```

#### 4. D 脚本：生成辅助函数

在 `d_handler_function_generator.py` 中，将 `_to_dict_repr` 函数定义作为字符串生成，并插入到 handler 函数之前。

## 工作流程

### 生成阶段（开发端）

```
generate_handler_from_api.py 运行
    ↓
D 脚本生成 _to_dict_repr 函数源码
    ↓
E 脚本识别复杂类型字段
    ↓
生成调用 _to_dict_repr 的代码
    ↓
输出 handler.py 文件
```

### 运行阶段（Coze 云端）

```
handler 函数被调用
    ↓
args.input.target_timerange = CustomNamespace(start=0, duration=5000000)
    ↓
f-string 插值：{_to_dict_repr(args.input.target_timerange)}
    ↓
_to_dict_repr 返回：'{"start": 0, "duration": 5000000}'
    ↓
写入脚本：req_params_xxx['target_timerange'] = {"start": 0, "duration": 5000000}
```

### 执行阶段（应用端）

```
执行脚本 coze2jianying.py
    ↓
解析：{"start": 0, "duration": 5000000}
    ↓
创建：CreateVideoSegmentRequest(**{"target_timerange": {"start": 0, "duration": 5000000}})
    ↓
Pydantic 验证通过 ✓
```

## 转换示例

### 输入（Coze 云端）

```python
args.input.target_timerange = CustomNamespace(start=0, duration=5000000)
args.input.clip_settings = CustomNamespace(
    brightness=0.5,
    contrast=0.3,
    saturation=0.2,
    temperature=0.1,
    hue=0.0
)
```

### 生成的脚本代码

```python
req_params_5e7474fa['target_timerange'] = {"start": 0, "duration": 5000000}
req_params_5e7474fa['clip_settings'] = {"brightness": 0.5, "contrast": 0.3, "saturation": 0.2, "temperature": 0.1, "hue": 0.0}
```

### 应用端解析

```python
# Python 直接将字符串解析为 dict
target_timerange = {"start": 0, "duration": 5000000}  # ✓ 正确的 dict

# Pydantic 可以接受 dict 并转换为模型
CreateVideoSegmentRequest(target_timerange=target_timerange)  # ✓ 验证通过
```

## 处理的类型

当前实现处理以下复杂类型：

- `TimeRange` - 时间范围
- `ClipSettings` - 图像调节设置
- `AnimationKeyframe` - 动画关键帧
- `AudioFadeConfig` - 音频淡入淡出配置
- `TextStyle` - 文本样式
- 以及其他所有自定义 NamedTuple 和 dataclass

## 测试覆盖

参见 `scripts/test_customnamespace_handling.py`，包含以下测试：

1. **_to_dict_repr 函数逻辑测试**
   - SimpleNamespace 对象转换
   - None 值处理
   - 嵌套对象递归转换
   - 字符串字段正确加引号
   - 基本类型正确处理

2. **生成代码输出格式测试**
   - 验证不包含 CustomNamespace 字符串
   - 验证是 dict 字面量格式
   - 验证 None 值字段被省略

3. **dict 字面量解析测试**
   - 生成的字符串可以被 Python 解析为 dict
   - dict 包含正确的键值对

## 注意事项

1. **递归处理** - `_to_dict_repr` 支持嵌套对象的递归转换

2. **字符串转义** - 字符串值会被正确加上引号，避免解析错误

3. **向后兼容** - 这个机制对基本类型（str, int, float, bool）无影响，保持原有行为

4. **Coze 平台特性** - `CustomNamespace` 是 Coze 平台的实现细节，`SimpleNamespace` 用于本地测试模拟

## 修改的文件

- `scripts/handler_generator/d_handler_function_generator.py` - 生成 `_to_dict_repr` 函数
- `scripts/handler_generator/e_api_call_code_generator.py` - 识别复杂类型并调用转换函数
- `scripts/test_customnamespace_handling.py` - 测试脚本

## 相关讨论

参见 GitHub Issue: "Handler 生成器省略 None 参数" 会话线程