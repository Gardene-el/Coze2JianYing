# Handler 输出格式修复文档

## 问题描述

在修复之前，由 `scripts/handler_generator` 生成的 `coze_plugin/raw_tools` 中的所有 `create_**` 类 handler 函数返回的值为 NamedTuple 格式，导致 Coze 平台无法正确识别。

### 修复前的输出格式

```python
# Handler 代码
def handler(args: Args[Input]) -> Output:
    # ...
    return Output(
        draft_id="7156f95b_a827_491e_9a6c_a7b2d338471e",
        success=True,
        message="操作成功",
        error_code=None,
        category=None,
        level=None,
        details=None
    )
```

**Coze 端收到的数据（数组格式）：**
```json
["7156f95b_a827_491e_9a6c_a7b2d338471e", true, "操作成功", null, null, null, null]
```

❌ **问题**：Coze 平台无法识别这个数组格式，不知道哪个元素对应哪个字段。

## 解决方案

### 修复后的输出格式

```python
# Handler 代码
def handler(args: Args[Input]) -> Dict[str, Any]:
    # ...
    return Output(
        draft_id="7156f95b_a827_491e_9a6c_a7b2d338471e",
        success=True,
        message="操作成功",
        error_code=None,
        category=None,
        level=None,
        details=None
    )._asdict()  # 关键：调用 _asdict() 转换为字典
```

**Coze 端收到的数据（对象格式）：**
```json
{
  "draft_id": "7156f95b_a827_491e_9a6c_a7b2d338471e",
  "success": true,
  "message": "操作成功",
  "error_code": null,
  "category": null,
  "level": null,
  "details": null
}
```

✅ **成功**：Coze 平台可以正确识别和使用每个字段。

## 技术实现

### 1. 修改 handler 生成器

**文件**: `scripts/handler_generator/d_handler_function_generator.py`

**修改内容**：

1. 更改返回类型注解：
   ```python
   # 修改前
   def handler(args: Args[Input]) -> Output:
   
   # 修改后
   def handler(args: Args[Input]) -> Dict[str, Any]:
   ```

2. 在所有返回语句中添加 `._asdict()` 调用：
   ```python
   # 修改前
   return Output(draft_id=f"{generated_uuid}", success=True, message="操作成功")
   
   # 修改后
   return Output(draft_id=f"{generated_uuid}", success=True, message="操作成功")._asdict()
   ```

### 2. 重新生成所有 handler

运行生成脚本重新生成所有 28 个 handler：

```bash
python scripts/generate_handler_from_api.py
```

**受影响的 handler**：
- `create_draft`
- `create_audio_segment`
- `create_video_segment`
- `create_text_segment`
- `create_sticker_segment`
- `create_effect_segment`
- `create_filter_segment`
- `add_track`
- `add_segment`
- `add_global_effect`
- `add_global_filter`
- `save_draft`
- 以及其他 16 个 handler

总共：**28 个 handler 文件被更新**

## 优势

### 保持类型安全

虽然最终返回的是字典，但我们仍然保留了 `Output` NamedTuple 的定义和使用：

1. **类型检查**：在构造 Output 时，IDE 和类型检查器可以验证字段名称和类型
2. **代码可读性**：Output 的定义清晰地展示了返回值的结构
3. **向后兼容**：Output 类的定义保持不变，只是在返回时转换为字典

```python
# 仍然使用 Output 类型进行构造（获得类型检查）
output = Output(
    draft_id=generated_uuid,
    success=True,
    message="操作成功"
)

# 转换为字典后返回（Coze 兼容）
return output._asdict()
```

### Coze 平台兼容性

修复后，Coze 可以：
- 通过字段名访问返回值：`result.draft_id`, `result.success`, `result.message`
- 在工作流中正确传递和使用返回值
- 显示有意义的字段名而不是数组索引

## 测试

### 测试文件

1. **`tests/test_handler_output_format.py`** - 全面的单元测试
   - 测试 `_asdict()` 方法正确转换为字典
   - 测试 JSON 序列化
   - 测试 Coze 兼容格式
   - 测试错误情况

2. **`tests/demo_output_format.py`** - 演示脚本
   - 展示修复前后的输出差异
   - 并排比较两种格式
   - 提供真实使用场景示例

### 运行测试

```bash
# 运行单元测试
python tests/test_handler_output_format.py

# 运行演示脚本
python tests/demo_output_format.py
```

## 实际使用示例

### 成功情况

```json
{
  "draft_id": "abc123_def456",
  "success": true,
  "message": "草稿创建成功",
  "error_code": null,
  "category": null,
  "level": null,
  "details": {
    "width": 1920,
    "height": 1080,
    "fps": 30
  }
}
```

### 错误情况

```json
{
  "draft_id": "",
  "success": false,
  "message": "调用 create_draft 时发生错误: 无效的参数",
  "error_code": "INVALID_PARAMS",
  "category": "validation_error",
  "level": null,
  "details": null
}
```

## 注意事项

1. **向后兼容性**：这个修复不影响 Output 类型的定义，仅改变最终返回格式
2. **性能影响**：`._asdict()` 调用的性能开销可忽略不计
3. **维护性**：未来添加新 handler 时，生成器会自动应用这个修复

## 相关 Issue

- Issue: [修复handler生成模块中无法Output出需要的输出的问题](链接)
- PR: [Fix handler output format for Coze compatibility](链接)

## 参考资料

- [Python NamedTuple 文档](https://docs.python.org/3/library/typing.html#typing.NamedTuple)
- [Coze 工具开发指南](https://www.coze.cn/open/docs/developer_guides)
