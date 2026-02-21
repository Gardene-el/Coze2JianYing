#!/usr/bin/env python3
"""
测试空 CustomNamespace 对象的处理
验证 _is_meaningful_object 函数能够正确识别和过滤空对象
"""

from types import SimpleNamespace


def test_is_meaningful_object_function():
    """测试 _is_meaningful_object 函数的实现逻辑"""
    print("=== 测试 _is_meaningful_object 函数 ===\n")

    def _is_meaningful_object(obj) -> bool:
        """
        检查对象是否包含有意义的数据
        
        用于区分空的 CustomNamespace() 对象和包含有效数据的对象
        避免将空对象视为有效值，导致 Pydantic 验证失败
        
        Args:
            obj: 任意对象
            
        Returns:
            True 如果对象包含有意义的数据，False 如果对象为 None 或为空
        """
        # None 值不是有意义的对象
        if obj is None:
            return False
        
        # 检查是否有 __dict__ 属性（CustomNamespace, SimpleNamespace 等）
        if hasattr(obj, '__dict__'):
            obj_dict = obj.__dict__
            # 空字典意味着空对象
            if not obj_dict:
                return False
            # 检查是否所有值都是 None（也视为空对象）
            if all(v is None for v in obj_dict.values()):
                return False
            # 至少有一个非 None 值，视为有意义的对象
            return True
        
        # 对于基本类型（字符串、数字、布尔值等），非 None 即为有意义
        return True

    # 测试用例
    test_cases = [
        # (输入, 期望结果, 描述)
        (None, False, "None 值"),
        (SimpleNamespace(), False, "空的 SimpleNamespace"),
        (SimpleNamespace(start=0, duration=5000000), True, "有值的 TimeRange"),
        (SimpleNamespace(start=None, duration=None), False, "所有值为 None 的对象"),
        (SimpleNamespace(start=0, duration=None), True, "部分值有效的对象"),
        ("test_string", True, "字符串"),
        (123, True, "数字"),
        (0, True, "数字 0（仍然有意义）"),
        (False, True, "布尔值 False（仍然有意义）"),
        ([], True, "空列表（基本类型）"),
        ({}, True, "空字典（基本类型）"),
    ]

    all_passed = True
    for obj, expected, description in test_cases:
        result = _is_meaningful_object(obj)
        passed = (result == expected)
        status = "✅" if passed else "❌"
        
        print(f"{status} {description}")
        print(f"   输入: {obj}")
        print(f"   期望: {expected}, 实际: {result}")
        
        if not passed:
            all_passed = False
            print(f"   ⚠️  测试失败")
        print()

    return all_passed


def test_generated_code_with_empty_objects():
    """测试生成的代码如何处理空对象"""
    print("=== 测试生成代码处理空对象 ===\n")

    def _is_meaningful_object(obj) -> bool:
        if obj is None:
            return False
        if hasattr(obj, '__dict__'):
            obj_dict = obj.__dict__
            if not obj_dict:
                return False
            if all(v is None for v in obj_dict.values()):
                return False
            return True
        return True

    def _to_type_constructor(obj, type_name: str) -> str:
        if obj is None:
            return 'None'
        if hasattr(obj, '__dict__'):
            obj_dict = obj.__dict__
            params = []
            for key, value in obj_dict.items():
                if isinstance(value, str):
                    value_repr = f'"{value}"'
                else:
                    value_repr = repr(value)
                params.append(f'{key}={value_repr}')
            return f'{type_name}(' + ', '.join(params) + ')'
        if isinstance(obj, str):
            return f'"{obj}"'
        else:
            return repr(obj)

    # 模拟 Coze 传入的参数（包含空对象）
    class MockInput:
        def __init__(self):
            self.material_url = "https://example.com/audio.mp3"
            self.target_timerange = SimpleNamespace(start=0, duration=5000000)
            self.source_timerange = SimpleNamespace()  # 空对象！
            self.speed = 1.0
            self.volume = 0.6
            self.change_pitch = True

    mock_input = MockInput()
    generated_uuid = "test_uuid_123"

    print("模拟生成的 API 调用代码:\n")

    # 生成代码（使用修复后的逻辑）
    code_lines = []
    code_lines.append(f"req_params_{generated_uuid} = {{}}")
    code_lines.append(f"req_params_{generated_uuid}['material_url'] = \"{mock_input.material_url}\"")
    code_lines.append(f"req_params_{generated_uuid}['target_timerange'] = {_to_type_constructor(mock_input.target_timerange, 'TimeRange')}")
    
    # 关键测试：空的 source_timerange 应该被过滤掉
    if _is_meaningful_object(mock_input.source_timerange):
        code_lines.append(f"req_params_{generated_uuid}['source_timerange'] = {_to_type_constructor(mock_input.source_timerange, 'TimeRange')}")
    else:
        code_lines.append("# source_timerange 为空，已跳过")
    
    if mock_input.speed is not None:
        code_lines.append(f"req_params_{generated_uuid}['speed'] = {mock_input.speed}")
    
    if mock_input.volume is not None:
        code_lines.append(f"req_params_{generated_uuid}['volume'] = {mock_input.volume}")
    
    if mock_input.change_pitch is not None:
        code_lines.append(f"req_params_{generated_uuid}['change_pitch'] = {mock_input.change_pitch}")

    for line in code_lines:
        print(line)

    print("\n验证结果:\n")

    # 验证 1: source_timerange 应该被跳过
    source_included = any("['source_timerange']" in line for line in code_lines)
    if not source_included:
        print("✅ 空的 source_timerange 被正确跳过")
    else:
        print("❌ 空的 source_timerange 没有被跳过")
        return False

    # 验证 2: 有效的 target_timerange 应该被包含
    target_included = any("['target_timerange']" in line for line in code_lines)
    if target_included:
        print("✅ 有效的 target_timerange 被正确包含")
    else:
        print("❌ 有效的 target_timerange 没有被包含")
        return False

    # 验证 3: 其他参数应该正常包含
    if "['speed']" in '\n'.join(code_lines) and "['volume']" in '\n'.join(code_lines):
        print("✅ 其他参数被正常包含")
    else:
        print("❌ 其他参数没有被正常包含")
        return False

    print("\n✅ 所有验证通过\n")
    return True


def test_coze_runtime_simulation():
    """模拟 Coze 运行时行为"""
    print("=== 模拟 Coze 运行时行为 ===\n")

    def _is_meaningful_object(obj) -> bool:
        if obj is None:
            return False
        if hasattr(obj, '__dict__'):
            obj_dict = obj.__dict__
            if not obj_dict:
                return False
            if all(v is None for v in obj_dict.values()):
                return False
            return True
        return True

    # 模拟不同场景
    scenarios = [
        ("空 SimpleNamespace", SimpleNamespace(), False),
        ("有值的 TimeRange", SimpleNamespace(start=0, duration=5000000), True),
        ("所有值为 None", SimpleNamespace(start=None, duration=None), False),
        ("部分值为 None", SimpleNamespace(brightness=0.5, contrast=None), True),
        ("None", None, False),
    ]

    print("测试不同场景:\n")
    all_passed = True
    for name, obj, expected in scenarios:
        result = _is_meaningful_object(obj)
        passed = (result == expected)
        status = "✅" if passed else "❌"
        
        print(f"{status} {name}: {result} (期望: {expected})")
        
        if not passed:
            all_passed = False

    print()
    return all_passed


def main():
    """运行所有测试"""
    print("=" * 60)
    print("空 CustomNamespace 对象处理测试")
    print("=" * 60)
    print()

    results = []

    try:
        results.append(("_is_meaningful_object 函数", test_is_meaningful_object_function()))
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(("_is_meaningful_object 函数", False))

    try:
        results.append(("生成代码处理空对象", test_generated_code_with_empty_objects()))
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(("生成代码处理空对象", False))

    try:
        results.append(("Coze 运行时模拟", test_coze_runtime_simulation()))
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Coze 运行时模拟", False))

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
