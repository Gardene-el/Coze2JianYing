#!/usr/bin/env python3
"""
测试生成的自定义类 handler
验证生成的 handler 文件是否能正确工作
"""

import sys
from pathlib import Path
from typing import NamedTuple, Generic, TypeVar
from unittest.mock import MagicMock

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 模拟 Coze 运行时的 Args 类（使用泛型）
T = TypeVar('T')

class Args(Generic[T]):
    def __init__(self, input_tuple):
        self.input = input_tuple
        self.logger = None

# 模拟 runtime 模块（仅在 Coze 环境中可用）
runtime_module = MagicMock()
runtime_module.Args = Args
sys.modules['runtime'] = runtime_module


def test_make_time_range():
    """测试 make_time_range handler"""
    print("\n测试 make_time_range:")
    print("-" * 50)
    
    # 导入 handler
    handler_path = project_root / "coze_plugin" / "raw_tools" / "make_time_range"
    sys.path.insert(0, str(handler_path))
    
    try:
        from handler import handler, Input, Output
        
        # 测试用例 1: 提供所有参数
        print("测试用例 1: 提供所有参数")
        test_input = Input(start=0, duration=5000000)
        args = Args(test_input)
        result = handler(args)
        
        assert result.success == True, "应该成功"
        assert result.result.get('start') == 0, "start 应该为 0"
        assert result.result.get('duration') == 5000000, "duration 应该为 5000000"
        print(f"✓ 通过: {result.result}")
        
        # 测试用例 2: 仅提供部分参数
        print("测试用例 2: 仅提供部分参数")
        test_input = Input(start=1000000, duration=None)
        args = Args(test_input)
        result = handler(args)
        
        assert result.success == True, "应该成功"
        assert result.result.get('start') == 1000000, "start 应该为 1000000"
        assert 'duration' not in result.result, "duration 不应该在结果中"
        print(f"✓ 通过: {result.result}")
        
        # 测试用例 3: 不提供任何参数
        print("测试用例 3: 不提供任何参数")
        test_input = Input(start=None, duration=None)
        args = Args(test_input)
        result = handler(args)
        
        assert result.success == True, "应该成功"
        assert len(result.result) == 0, "结果应该为空字典"
        print(f"✓ 通过: {result.result}")
        
        print("✓ make_time_range 所有测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        sys.path.remove(str(handler_path))


def test_make_clip_settings():
    """测试 make_clip_settings handler"""
    print("\n测试 make_clip_settings:")
    print("-" * 50)
    
    # 导入 handler
    handler_path = project_root / "coze_plugin" / "raw_tools" / "make_clip_settings"
    sys.path.insert(0, str(handler_path))
    
    try:
        from handler import handler, Input, Output
        
        # 验证基本结构
        print("验证 handler 文件结构...")
        assert hasattr(Input, '_fields'), "Input 应该是 NamedTuple"
        assert hasattr(Output, '_fields'), "Output 应该是 NamedTuple"
        assert callable(handler), "handler 应该是可调用的"
        print(f"✓ Input 字段: {Input._fields}")
        print(f"✓ Output 字段: {Output._fields}")
        
        # 简单测试：使用默认值
        print("测试用例: 使用默认值")
        test_input = Input()
        args = Args(test_input)
        result = handler(args)
        
        assert result.success == True, "应该成功"
        assert isinstance(result.result, dict), "result 应该是字典"
        print(f"✓ 通过: 返回空字典 {result.result}")
        
        print("✓ make_clip_settings 基本测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        sys.path.remove(str(handler_path))


def test_make_text_style():
    """测试 make_text_style handler"""
    print("\n测试 make_text_style:")
    print("-" * 50)
    
    # 导入 handler
    handler_path = project_root / "coze_plugin" / "raw_tools" / "make_text_style"
    sys.path.insert(0, str(handler_path))
    
    try:
        from handler import handler, Input, Output
        
        # 验证基本结构
        print("验证 handler 文件结构...")
        assert hasattr(Input, '_fields'), "Input 应该是 NamedTuple"
        assert hasattr(Output, '_fields'), "Output 应该是 NamedTuple"
        assert callable(handler), "handler 应该是可调用的"
        print(f"✓ Input 字段: {Input._fields}")
        print(f"✓ Output 字段: {Output._fields}")
        
        # 简单测试：使用默认值
        print("测试用例: 使用默认值")
        test_input = Input()
        args = Args(test_input)
        result = handler(args)
        
        assert result.success == True, "应该成功"
        assert isinstance(result.result, dict), "result 应该是字典"
        print(f"✓ 通过: 返回空字典 {result.result}")
        
        print("✓ make_text_style 基本测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        sys.path.remove(str(handler_path))


def test_make_crop_settings():
    """测试 make_crop_settings handler"""
    print("\n测试 make_crop_settings:")
    print("-" * 50)
    
    # 导入 handler
    handler_path = project_root / "coze_plugin" / "raw_tools" / "make_crop_settings"
    sys.path.insert(0, str(handler_path))
    
    try:
        from handler import handler, Input, Output
        
        # 验证基本结构
        print("验证 handler 文件结构...")
        assert hasattr(Input, '_fields'), "Input 应该是 NamedTuple"
        assert hasattr(Output, '_fields'), "Output 应该是 NamedTuple"
        assert callable(handler), "handler 应该是可调用的"
        print(f"✓ Input 字段: {Input._fields}")
        print(f"✓ Output 字段: {Output._fields}")
        
        # 简单测试：使用默认值
        print("测试用例: 使用默认值")
        test_input = Input()
        args = Args(test_input)
        result = handler(args)
        
        assert result.success == True, "应该成功"
        assert isinstance(result.result, dict), "result 应该是字典"
        print(f"✓ 通过: 返回空字典 {result.result}")
        
        print("✓ make_crop_settings 基本测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        sys.path.remove(str(handler_path))


def main():
    """主测试函数"""
    print("=" * 60)
    print("测试生成的自定义类 Handler")
    print("=" * 60)
    
    results = []
    results.append(("make_time_range", test_make_time_range()))
    results.append(("make_clip_settings", test_make_clip_settings()))
    results.append(("make_text_style", test_make_text_style()))
    results.append(("make_crop_settings", test_make_crop_settings()))
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name:25s} {status}")
    
    all_passed = all(passed for _, passed in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("所有测试通过！✓")
        return 0
    else:
        print("部分测试失败！✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
