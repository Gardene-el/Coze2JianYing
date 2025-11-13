# Handler Generator Changelog

## [2024-12] - 类型构造方案实现

### 重大变更

#### CustomNamespace 处理方案重构

**问题**: 原有的 dict 方案存在以下问题：
- f-string 转义导致双大括号问题
- 运行时 `unhashable type: 'dict'` 错误
- dict 类型与 Pydantic 模型期望的类型不匹配

**解决方案**: 实现类型构造方案
- 将 CustomNamespace 转换为类型构造表达式（如 `TimeRange(start=0, duration=5000000)`）
- 生成的代码可在应用端直接执行，构造正确的类型实例
- 避免 f-string 转义问题，使用关键字参数格式

### 新增功能

#### E 脚本 (`e_api_call_code_generator.py`)

**新增方法**:
- `_extract_type_name(field_type: str) -> str`
  - 从类型字符串中提取核心类型名
  - 支持 Optional, List, Dict 等泛型包装
  - 例如: `Optional[TimeRange]` -> `TimeRange`

**修改方法**:
- `_is_complex_type(field_type: str) -> bool`
  - 重构判断逻辑，使用 `_extract_type_name` 提取类型名
  - 更准确地区分自定义类型和基本类型
  
- `_format_param_value(field_name: str, field_type: str) -> str`
  - 复杂类型改为调用 `_to_type_constructor(obj, type_name)`
  - 传递类型名作为第二个参数

#### D 脚本 (`d_handler_function_generator.py`)

**重写辅助函数**:
- `_to_dict_repr(obj) -> str` ❌ 已移除
- `_to_type_constructor(obj, type_name: str) -> str` ✅ 新增
  - 将 CustomNamespace 转换为类型构造表达式字符串
  - 支持嵌套对象递归处理
  - 智能推断嵌套类型名（settings -> ClipSettings, timerange -> TimeRange）
  - 返回格式: `TypeName(param1=value1, param2=value2)`

### 测试

**新增测试文件**:
- `scripts/test_type_constructor.py`
  - 测试 `_to_type_constructor` 函数逻辑
  - 验证生成代码输出格式
  - 确保类型构造表达式可执行
  - 确认不再生成 dict 字面量

- `scripts/test_extract_type_name.py`
  - 测试类型名提取的正确性
  - 验证复杂类型判断
  - 测试参数值格式化输出

**已过时**:
- `scripts/test_customnamespace_handling.py` - 旧的 dict 方案测试，保留供参考

### 文档

**新增**:
- `docs/handler_generator/CUSTOMNAMESPACE_HANDLING.md`
  - 详细说明类型构造方案的实现
  - 包含两种方案的对比
  - 提供完整的工作流程示例
  - 说明向后兼容性

**更新**:
- `scripts/handler_generator/README.md`
  - 更新 CustomNamespace 处理部分
  - 更新测试运行命令
  - 添加类型构造方案说明

### 示例对比

#### 旧方案（dict 字面量）❌
```python
# 生成的代码
req_params_xxx['target_timerange'] = {"start": 0, "duration": 5000000}
req_params_xxx['clip_settings'] = {"brightness": 0.5, "contrast": 0.3}
```

**问题**:
- 双大括号转义: `{{"start": 0}}`
- 类型错误: dict 而非 TimeRange 实例
- 运行时错误: `unhashable type: 'dict'`

#### 新方案（类型构造）✅
```python
# 生成的代码
req_params_xxx['target_timerange'] = TimeRange(start=0, duration=5000000)
req_params_xxx['clip_settings'] = ClipSettings(brightness=0.5, contrast=0.3)
```

**优势**:
- 无转义问题
- 类型正确
- 可直接执行

### 向后兼容性

- ✅ 完全兼容：只修改生成器内部逻辑
- ✅ API 不变：对外接口保持不变
- ✅ 现有测试通过：不影响其他功能

### 重新生成说明

如需使用新方案，重新运行生成器：
```bash
python scripts/generate_handler_from_api.py
```

### 技术细节

**类型名提取算法**:
```python
# 使用正则表达式匹配 PascalCase 类型名
matches = re.findall(r"\b([A-Z][a-zA-Z0-9_]*)\b", field_type)
# 返回最后一个匹配（最内层类型）
return matches[-1] if matches else field_type
```

**嵌套类型推断规则**:
- `*_settings` -> `ClipSettings`
- `*_timerange` -> `TimeRange`
- `*_style` -> `TextStyle`
- `*_position` -> `Position`
- 其他: 首字母大写的字段名

### 相关 Issue/PR

- 原始问题: CustomNamespace 导致 Pydantic 验证失败
- dict 方案问题: 双大括号转义和运行时错误
- 解决方案: 类型构造方案实现

---

## 历史版本

### [2024-12] - 初始实现

**实现的核心功能**:
- A-E 脚本模块架构
- API 扫描和解析
- Input/Output 类型生成
- Handler 函数生成
- API 调用代码生成
- 可选参数处理
- 初始 CustomNamespace 处理（dict 方案）

**测试**:
- `test_optional_params.py` - 可选参数测试
- `test_customnamespace_handling.py` - dict 方案测试

**文档**:
- `README.md` - 模块架构和使用说明