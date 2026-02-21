#!/usr/bin/env python3
"""
测试类型构造方案

验证生成的 handler 能够正确处理 Coze 的 CustomNamespace/SimpleNamespace 对象，
将其转换为类型构造表达式（如 TimeRange(start=0, duration=5000000)），
而不是 dict 字面量。
"""

from types import SimpleNamespace


def test_to_type_constructor_function():
    """测试 _to_type_constructor 函数的实现逻辑"""
    print("=== 测试 _to_type_constructor 函数逻辑 ===\n")

    def _to_type_constructor(obj, type_name: str) -> str:
        """
        将 CustomNamespace/SimpleNamespace 对象转换为类型构造表达式字符串

        用于处理 Coze 的 CustomNamespace/SimpleNamespace 对象
        这些对象在 Coze 云端使用，在应用端执行时需要转换为对应类型的构造调用

        例如：
            CustomNamespace(start=0, duration=5000000)
            -> "TimeRange(start=0, duration=5000000)"

        Args:
            obj: CustomNamespace/SimpleNamespace 对象
            type_name: 目标类型名，如 "TimeRange", "ClipSettings"

        Returns:
            类型构造表达式字符串，如 "TimeRange(start=0, duration=5000000)"
        """
        if obj is None:
            return "None"

        # 检查是否有 __dict__ 属性（CustomNamespace, SimpleNamespace 等）
        if hasattr(obj, "__dict__"):
            obj_dict = obj.__dict__
            # 构造类型构造调用的参数列表
            params = []
            for key, value in obj_dict.items():
                # 递归处理嵌套对象
                if hasattr(value, "__dict__"):
                    # 嵌套对象：尝试推断其类型名（使用首字母大写的 key）
                    nested_type_name = key.capitalize() if key else "Object"
                    # 如果 key 本身就是类型相关的，使用更智能的命名
                    if "settings" in key.lower():
                        nested_type_name = "ClipSettings"
                    elif "timerange" in key.lower():
                        nested_type_name = "TimeRange"
                    elif "style" in key.lower():
                        nested_type_name = "TextStyle"
                    elif "position" in key.lower():
                        nested_type_name = "Position"
                    value_repr = _to_type_constructor(value, nested_type_name)
                elif isinstance(value, str):
                    # 字符串值：加引号
                    value_repr = f'"{value}"'
                else:
                    # 其他类型：直接使用 repr
                    value_repr = repr(value)
                params.append(f"{key}={value_repr}")

            # 构造类型构造表达式：TypeName(param1=value1, param2=value2)
            return f"{type_name}(" + ", ".join(params) + ")"

        # 如果不是复杂对象，返回其 repr
        if isinstance(obj, str):
            return f'"{obj}"'
        else:
            return repr(obj)

    # 测试 1: SimpleNamespace 对象（模拟 TimeRange）
    print("测试 1: SimpleNamespace 对象 (模拟 TimeRange)")
    timerange = SimpleNamespace(start=0, duration=5000000)
    result = _to_type_constructor(timerange, "TimeRange")
    print(f"输入: {timerange}")
    print(f"输出: {result}")
    expected = "TimeRange(start=0, duration=5000000)"
    assert result == expected, f"Expected {expected}, got {result}"
    print("✅ 通过\n")

    # 测试 2: None 值
    print("测试 2: None 值")
    result = _to_type_constructor(None, "TimeRange")
    print(f"输入: None")
    print(f"输出: {result}")
    assert result == "None", f"Expected 'None', got {result}"
    print("✅ 通过\n")

    # 测试 3: ClipSettings 对象
    print("测试 3: SimpleNamespace 对象 (模拟 ClipSettings)")
    clip_settings = SimpleNamespace(
        brightness=0.5, contrast=0.3, saturation=0.2, temperature=0.1, hue=0.0
    )
    result = _to_type_constructor(clip_settings, "ClipSettings")
    print(f"输入: {clip_settings}")
    print(f"输出: {result}")
    # 验证格式
    assert result.startswith("ClipSettings("), "应该以 ClipSettings( 开头"
    assert result.endswith(")"), "应该以 ) 结尾"
    assert "brightness=0.5" in result, "应该包含 brightness=0.5"
    assert "contrast=0.3" in result, "应该包含 contrast=0.3"
    # 不应该有 dict 字面量格式的引号键
    assert '"brightness"' not in result, "不应该有引号包裹的键名"
    print("✅ 通过\n")

    # 测试 4: 包含字符串字段的对象
    print("测试 4: 包含字符串字段的对象")
    obj_with_str = SimpleNamespace(name="test_segment", duration=1000)
    result = _to_type_constructor(obj_with_str, "CustomType")
    print(f"输入: {obj_with_str}")
    print(f"输出: {result}")
    assert 'name="test_segment"' in result, '应该包含 name="test_segment"'
    assert "duration=1000" in result, "应该包含 duration=1000"
    assert result.startswith("CustomType("), "应该以类型名开头"
    print("✅ 通过\n")

    # 测试 5: 嵌套对象（TimeRange 嵌套在 Request 中）
    print("测试 5: 嵌套对象")
    nested_obj = SimpleNamespace(
        material_url="https://example.com/video.mp4",
        target_timerange=SimpleNamespace(start=0, duration=5000000),
        speed=1.0,
    )
    result = _to_type_constructor(nested_obj, "CreateVideoSegmentRequest")
    print(f"输入: {nested_obj}")
    print(f"输出: {result}")
    # 验证嵌套对象也被正确处理
    assert "target_timerange=TimeRange(" in result, (
        "嵌套的 timerange 应该被识别为 TimeRange 类型"
    )
    assert "start=0" in result, "应该包含嵌套对象的字段"
    assert "duration=5000000" in result, "应该包含嵌套对象的字段"
    print("✅ 通过\n")

    return True


def test_generated_code_output():
    """测试生成的代码输出格式"""
    print("=== 测试生成的代码输出格式 ===\n")

    from types import SimpleNamespace

    def _to_type_constructor(obj, type_name: str) -> str:
        if obj is None:
            return "None"
        if hasattr(obj, "__dict__"):
            obj_dict = obj.__dict__
            params = []
            for key, value in obj_dict.items():
                if hasattr(value, "__dict__"):
                    nested_type_name = key.capitalize() if key else "Object"
                    if "settings" in key.lower():
                        nested_type_name = "ClipSettings"
                    elif "timerange" in key.lower():
                        nested_type_name = "TimeRange"
                    elif "style" in key.lower():
                        nested_type_name = "TextStyle"
                    elif "position" in key.lower():
                        nested_type_name = "Position"
                    value_repr = _to_type_constructor(value, nested_type_name)
                elif isinstance(value, str):
                    value_repr = f'"{value}"'
                else:
                    value_repr = repr(value)
                params.append(f"{key}={value_repr}")
            return f"{type_name}(" + ", ".join(params) + ")"
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
        f"req_params_{generated_uuid}['target_timerange'] = {_to_type_constructor(mock_input.target_timerange, 'TimeRange')}"
    )

    if mock_input.source_timerange is not None:
        api_call_lines.append(
            f"req_params_{generated_uuid}['source_timerange'] = {_to_type_constructor(mock_input.source_timerange, 'TimeRange')}"
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
            f"req_params_{generated_uuid}['clip_settings'] = {_to_type_constructor(mock_input.clip_settings, 'ClipSettings')}"
        )

    for line in api_call_lines:
        print(line)

    print("\n验证输出:\n")

    # 验证 1: target_timerange 应该是类型构造表达式
    target_line = api_call_lines[2]
    print(f"✅ target_timerange: {target_line}")
    assert "CustomNamespace" not in target_line, "不应该包含 CustomNamespace"
    assert "SimpleNamespace" not in target_line, "不应该包含 SimpleNamespace"
    assert "TimeRange(start=0, duration=5000000)" in target_line, "应该是类型构造表达式"
    assert "{" not in target_line.split("=")[1], "不应该有大括号（dict 字面量）"

    # 验证 2: clip_settings 也应该是类型构造表达式
    clip_line = api_call_lines[-1]
    print(f"✅ clip_settings: {clip_line}")
    assert "CustomNamespace" not in clip_line, "不应该包含 CustomNamespace"
    assert "SimpleNamespace" not in clip_line, "不应该包含 SimpleNamespace"
    assert "ClipSettings(" in clip_line, "应该是 ClipSettings 构造调用"
    assert "brightness=" in clip_line, "应该使用关键字参数格式"

    # 验证 3: None 值的字段应该被省略
    source_timerange_present = any(
        "source_timerange" in line for line in api_call_lines
    )
    print(f"✅ source_timerange (None) 被省略: {not source_timerange_present}")
    assert not source_timerange_present, "None 值的 source_timerange 应该被省略"

    print("\n✅ 所有验证通过\n")
    return True


def test_type_constructor_can_be_executed():
    """测试生成的类型构造表达式可以被执行"""
    print("=== 测试类型构造表达式可以被执行 ===\n")

    from types import SimpleNamespace

    def _to_type_constructor(obj, type_name: str) -> str:
        if obj is None:
            return "None"
        if hasattr(obj, "__dict__"):
            obj_dict = obj.__dict__
            params = []
            for key, value in obj_dict.items():
                if hasattr(value, "__dict__"):
                    nested_type_name = key.capitalize() if key else "Object"
                    if "settings" in key.lower():
                        nested_type_name = "ClipSettings"
                    elif "timerange" in key.lower():
                        nested_type_name = "TimeRange"
                    value_repr = _to_type_constructor(value, nested_type_name)
                elif isinstance(value, str):
                    value_repr = f'"{value}"'
                else:
                    value_repr = repr(value)
                params.append(f"{key}={value_repr}")
            return f"{type_name}(" + ", ".join(params) + ")"
        if isinstance(obj, str):
            return f'"{obj}"'
        else:
            return repr(obj)

    # 创建测试对象
    timerange = SimpleNamespace(start=0, duration=5000000)
    type_constructor = _to_type_constructor(timerange, "TimeRange")

    print(f"生成的类型构造表达式: {type_constructor}")

    # 模拟在执行环境中有 TimeRange 类定义
    # 这里我们用 lambda 模拟类构造器
    TimeRange = lambda start, duration: {"start": start, "duration": duration}

    # 尝试执行生成的表达式
    try:
        result = eval(type_constructor)
        print(f"执行结果: {result}")
        print(f"类型: {type(result)}")

        # 验证结果
        assert result["start"] == 0, "start 字段应该是 0"
        assert result["duration"] == 5000000, "duration 字段应该是 5000000"

        print("✅ 类型构造表达式可以被正确执行\n")
        return True
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_no_dict_literal_format():
    """测试确保不再生成 dict 字面量格式"""
    print("=== 测试确保不生成 dict 字面量格式 ===\n")

    from types import SimpleNamespace

    def _to_type_constructor(obj, type_name: str) -> str:
        if obj is None:
            return "None"
        if hasattr(obj, "__dict__"):
            obj_dict = obj.__dict__
            params = []
            for key, value in obj_dict.items():
                if hasattr(value, "__dict__"):
                    nested_type_name = key.capitalize() if key else "Object"
                    if "settings" in key.lower():
                        nested_type_name = "ClipSettings"
                    elif "timerange" in key.lower():
                        nested_type_name = "TimeRange"
                    value_repr = _to_type_constructor(value, nested_type_name)
                elif isinstance(value, str):
                    value_repr = f'"{value}"'
                else:
                    value_repr = repr(value)
                params.append(f"{key}={value_repr}")
            return f"{type_name}(" + ", ".join(params) + ")"
        if isinstance(obj, str):
            return f'"{obj}"'
        else:
            return repr(obj)

    # 测试各种对象
    test_cases = [
        (SimpleNamespace(start=0, duration=5000000), "TimeRange"),
        (SimpleNamespace(brightness=0.5, contrast=0.3), "ClipSettings"),
        (SimpleNamespace(x=100, y=200), "Position"),
    ]

    for obj, type_name in test_cases:
        result = _to_type_constructor(obj, type_name)
        print(f"类型: {type_name}")
        print(f"输出: {result}")

        # 验证不是 dict 字面量格式
        assert not result.startswith("{"), f"{type_name} 输出不应该以 {{ 开头"
        assert result.startswith(f"{type_name}("), f"应该以 {type_name}( 开头"
        assert result.endswith(")"), f"应该以 ) 结尾"

        # 验证使用关键字参数格式（key=value），而不是 dict 格式（"key": value）
        if obj.__dict__:
            first_key = list(obj.__dict__.keys())[0]
            assert f"{first_key}=" in result, f"应该使用关键字参数格式 {first_key}="
            assert f'"{first_key}":' not in result, f"不应该使用 dict 字面量格式"

        print("✅ 通过\n")

    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("类型构造方案测试")
    print("=" * 60)
    print()

    results = []

    try:
        results.append(
            ("_to_type_constructor 函数逻辑", test_to_type_constructor_function())
        )
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        results.append(("_to_type_constructor 函数逻辑", False))

    try:
        results.append(("生成代码输出格式", test_generated_code_output()))
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        results.append(("生成代码输出格式", False))

    try:
        results.append(("类型构造表达式执行", test_type_constructor_can_be_executed()))
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        results.append(("类型构造表达式执行", False))

    try:
        results.append(("不生成 dict 字面量", test_no_dict_literal_format()))
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        results.append(("不生成 dict 字面量", False))

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
