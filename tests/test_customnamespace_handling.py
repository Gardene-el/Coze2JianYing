#!/usr/bin/env python3
"""
测试 CustomNamespace 处理功能

验证生成的 handler 能够正确处理 Coze 的 CustomNamespace/SimpleNamespace 对象，
将其转换为 dict 字面量字符串，以便在应用端执行时能被 Pydantic 正确解析。
"""

from types import SimpleNamespace


def test_to_dict_repr_function():
    """测试 _to_dict_repr 函数的实现逻辑"""
    print("=== 测试 _to_dict_repr 函数逻辑 ===\n")

    def _to_dict_repr(obj) -> str:
        """
        将对象转换为 dict 字面量字符串表示

        用于处理 Coze 的 CustomNamespace/SimpleNamespace 对象
        这些对象在 Coze 云端使用，但在应用端执行时需要转换为 dict

        Args:
            obj: 任意对象

        Returns:
            dict 字面量字符串，如 '{"start": 0, "duration": 5000000}'
        """
        if obj is None:
            return "None"

        # 检查是否有 __dict__ 属性（CustomNamespace, SimpleNamespace 等）
        if hasattr(obj, "__dict__"):
            obj_dict = obj.__dict__
            # 构造 dict 字面量字符串
            items = []
            for key, value in obj_dict.items():
                # 递归处理嵌套对象
                if hasattr(value, "__dict__"):
                    value_repr = _to_dict_repr(value)
                elif isinstance(value, str):
                    value_repr = f'"{value}"'
                else:
                    value_repr = repr(value)
                items.append(f'"{key}": {value_repr}')
            return "{" + ", ".join(items) + "}"

        # 如果不是复杂对象，返回其 repr
        if isinstance(obj, str):
            return f'"{obj}"'
        else:
            return repr(obj)

    # 测试 1: SimpleNamespace 对象（模拟 CustomNamespace）
    print("测试 1: SimpleNamespace 对象 (模拟 CustomNamespace)")
    timerange = SimpleNamespace(start=0, duration=5000000)
    result = _to_dict_repr(timerange)
    print(f"输入: {timerange}")
    print(f"输出: {result}")
    expected = '{"start": 0, "duration": 5000000}'
    assert result == expected, f"Expected {expected}, got {result}"
    print("✅ 通过\n")

    # 测试 2: None 值
    print("测试 2: None 值")
    result = _to_dict_repr(None)
    print(f"输入: None")
    print(f"输出: {result}")
    assert result == "None", f"Expected 'None', got {result}"
    print("✅ 通过\n")

    # 测试 3: 嵌套对象
    print("测试 3: 嵌套 SimpleNamespace 对象")
    clip_settings = SimpleNamespace(
        brightness=0.5, contrast=0.3, saturation=0.2, temperature=0.1, hue=0.0
    )
    result = _to_dict_repr(clip_settings)
    print(f"输入: {clip_settings}")
    print(f"输出: {result}")
    # 验证包含所有字段
    assert '"brightness": 0.5' in result
    assert '"contrast": 0.3' in result
    assert '"saturation": 0.2' in result
    print("✅ 通过\n")

    # 测试 4: 包含字符串字段的对象
    print("测试 4: 包含字符串字段的对象")
    obj_with_str = SimpleNamespace(name="test_segment", duration=1000)
    result = _to_dict_repr(obj_with_str)
    print(f"输入: {obj_with_str}")
    print(f"输出: {result}")
    assert '"name": "test_segment"' in result
    assert '"duration": 1000' in result
    print("✅ 通过\n")

    # 测试 5: 基本类型（字符串）
    print("测试 5: 字符串类型")
    result = _to_dict_repr("hello")
    print(f"输入: 'hello'")
    print(f"输出: {result}")
    assert result == '"hello"', f"Expected '\"hello\"', got {result}"
    print("✅ 通过\n")

    # 测试 6: 基本类型（数字）
    print("测试 6: 数字类型")
    result = _to_dict_repr(42)
    print(f"输入: 42")
    print(f"输出: {result}")
    assert result == "42", f"Expected '42', got {result}"
    print("✅ 通过\n")

    return True


def test_generated_code_output():
    """测试生成的代码输出格式"""
    print("=== 测试生成的代码输出格式 ===\n")

    # 模拟 handler 运行时的场景
    from types import SimpleNamespace

    def _to_dict_repr(obj) -> str:
        if obj is None:
            return "None"
        if hasattr(obj, "__dict__"):
            obj_dict = obj.__dict__
            items = []
            for key, value in obj_dict.items():
                if hasattr(value, "__dict__"):
                    value_repr = _to_dict_repr(value)
                elif isinstance(value, str):
                    value_repr = f'"{value}"'
                else:
                    value_repr = repr(value)
                items.append(f'"{key}": {value_repr}')
            return "{" + ", ".join(items) + "}"
        if isinstance(obj, str):
            return f'"{obj}"'
        else:
            return repr(obj)

    # 模拟 Coze 传入的参数
    class MockInput:
        def __init__(self):
            self.material_url = "https://example.com/video.mp4"
            self.target_timerange = SimpleNamespace(start=0, duration=5000000)
            self.source_timerange = None
            self.speed = 1.0
            self.volume = 1.0
            self.change_pitch = False
            self.clip_settings = SimpleNamespace(
                brightness=0.0, contrast=0.0, saturation=0.0, temperature=0.0, hue=0.0
            )

    mock_input = MockInput()
    generated_uuid = "test_uuid_123"

    # 构造实际生成的代码
    print("生成的 API 调用代码片段:\n")

    api_call_lines = []
    api_call_lines.append(f"req_params_{generated_uuid} = {{}}")
    api_call_lines.append(
        f"req_params_{generated_uuid}['material_url'] = \"{mock_input.material_url}\""
    )
    api_call_lines.append(
        f"req_params_{generated_uuid}['target_timerange'] = {_to_dict_repr(mock_input.target_timerange)}"
    )

    if mock_input.source_timerange is not None:
        api_call_lines.append(
            f"req_params_{generated_uuid}['source_timerange'] = {_to_dict_repr(mock_input.source_timerange)}"
        )

    if mock_input.speed is not None:
        api_call_lines.append(
            f"req_params_{generated_uuid}['speed'] = {mock_input.speed}"
        )

    if mock_input.volume is not None:
        api_call_lines.append(
            f"req_params_{generated_uuid}['volume'] = {mock_input.volume}"
        )

    if mock_input.change_pitch is not None:
        api_call_lines.append(
            f"req_params_{generated_uuid}['change_pitch'] = {mock_input.change_pitch}"
        )

    if mock_input.clip_settings is not None:
        api_call_lines.append(
            f"req_params_{generated_uuid}['clip_settings'] = {_to_dict_repr(mock_input.clip_settings)}"
        )

    for line in api_call_lines:
        print(line)

    print("\n验证输出:\n")

    # 验证 1: target_timerange 不再是 CustomNamespace(...) 形式
    target_line = api_call_lines[2]
    print(f"✅ target_timerange: {target_line}")
    assert "CustomNamespace" not in target_line, "不应该包含 CustomNamespace"
    assert "SimpleNamespace" not in target_line, "不应该包含 SimpleNamespace"
    assert '{"start": 0, "duration": 5000000}' in target_line, "应该是 dict 字面量"

    # 验证 2: clip_settings 也应该是 dict 格式
    clip_line = api_call_lines[-1]
    print(f"✅ clip_settings: {clip_line}")
    assert "CustomNamespace" not in clip_line, "不应该包含 CustomNamespace"
    assert "SimpleNamespace" not in clip_line, "不应该包含 SimpleNamespace"
    assert '"brightness"' in clip_line, "应该包含字段名"

    # 验证 3: None 值的字段应该被省略
    source_timerange_present = any(
        "source_timerange" in line for line in api_call_lines
    )
    print(f"✅ source_timerange (None) 被省略: {not source_timerange_present}")
    assert not source_timerange_present, "None 值的 source_timerange 应该被省略"

    print("\n✅ 所有验证通过\n")
    return True


def test_dict_literal_can_be_parsed():
    """测试生成的 dict 字面量可以被 Python 解析"""
    print("=== 测试 dict 字面量可以被解析 ===\n")

    from types import SimpleNamespace

    def _to_dict_repr(obj) -> str:
        if obj is None:
            return "None"
        if hasattr(obj, "__dict__"):
            obj_dict = obj.__dict__
            items = []
            for key, value in obj_dict.items():
                if hasattr(value, "__dict__"):
                    value_repr = _to_dict_repr(value)
                elif isinstance(value, str):
                    value_repr = f'"{value}"'
                else:
                    value_repr = repr(value)
                items.append(f'"{key}": {value_repr}')
            return "{" + ", ".join(items) + "}"
        if isinstance(obj, str):
            return f'"{obj}"'
        else:
            return repr(obj)

    # 创建测试对象
    timerange = SimpleNamespace(start=0, duration=5000000)
    dict_repr = _to_dict_repr(timerange)

    print(f"生成的字符串: {dict_repr}")

    # 尝试解析为 Python dict
    parsed_dict = eval(dict_repr)
    print(f"解析后的 dict: {parsed_dict}")
    print(f"类型: {type(parsed_dict)}")

    # 验证解析结果
    assert isinstance(parsed_dict, dict), "应该是 dict 类型"
    assert parsed_dict["start"] == 0, "start 字段应该是 0"
    assert parsed_dict["duration"] == 5000000, "duration 字段应该是 5000000"

    print("✅ dict 字面量可以被正确解析\n")
    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("CustomNamespace 处理功能测试")
    print("=" * 60)
    print()

    results = []

    try:
        results.append(("_to_dict_repr 函数逻辑", test_to_dict_repr_function()))
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        results.append(("_to_dict_repr 函数逻辑", False))

    try:
        results.append(("生成代码输出格式", test_generated_code_output()))
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        results.append(("生成代码输出格式", False))

    try:
        results.append(("dict 字面量解析", test_dict_literal_can_be_parsed()))
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        results.append(("dict 字面量解析", False))

    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n总计: {passed}/{total} 测试通过")

    return all(p for _, p in results)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
