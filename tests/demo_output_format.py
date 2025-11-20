#!/usr/bin/env python3
"""
演示修复前后的 handler 输出格式差异

这个脚本展示了为什么 Coze 无法识别 NamedTuple 的原因，
以及使用 _asdict() 方法后的改进。
"""

import json
from typing import NamedTuple, Optional, Dict, Any


class Output(NamedTuple):
    """模拟 handler 的 Output 类型"""
    draft_id: str = ""
    success: bool = False
    message: str = ""
    error_code: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    details: Optional[Dict] = None


def show_old_format():
    """展示修复前的输出格式（NamedTuple 直接返回）"""
    print("=" * 60)
    print("修复前：直接返回 NamedTuple")
    print("=" * 60)
    
    # 模拟旧的 handler 返回
    output = Output(
        draft_id="7156f95b_a827_491e_9a6c_a7b2d338471e",
        success=True,
        message="操作成功",
        error_code=None,
        category=None,
        level=None,
        details=None
    )
    
    print(f"\nPython 对象: {output}")
    print(f"类型: {type(output)}")
    
    # 当 NamedTuple 被序列化时，它变成一个数组
    print(f"\n当序列化为 JSON 时，Coze 看到的是:")
    # NamedTuple 会被转换为列表
    as_list = list(output)
    print(json.dumps(as_list, ensure_ascii=False, indent=2))
    
    print(f"\n❌ 这是一个数组格式，Coze 无法识别各个字段的含义！")
    print()


def show_new_format():
    """展示修复后的输出格式（使用 _asdict() 转换）"""
    print("=" * 60)
    print("修复后：返回 Output._asdict()")
    print("=" * 60)
    
    # 模拟新的 handler 返回
    output = Output(
        draft_id="7156f95b_a827_491e_9a6c_a7b2d338471e",
        success=True,
        message="操作成功",
        error_code=None,
        category=None,
        level=None,
        details=None
    )
    
    # 使用 _asdict() 转换为字典
    output_dict = output._asdict()
    
    print(f"\nPython 对象: {output_dict}")
    print(f"类型: {type(output_dict)}")
    
    print(f"\n当序列化为 JSON 时，Coze 看到的是:")
    print(json.dumps(output_dict, ensure_ascii=False, indent=2))
    
    print(f"\n✅ 这是一个对象格式，Coze 可以正确识别每个字段！")
    print()


def show_comparison():
    """并排比较两种格式"""
    print("=" * 60)
    print("格式对比")
    print("=" * 60)
    
    output = Output(
        draft_id="7156f95b_a827_491e_9a6c_a7b2d338471e",
        success=True,
        message="操作成功"
    )
    
    print("\n修复前 (数组格式):")
    print("-" * 60)
    old_format = list(output)
    print(json.dumps(old_format, ensure_ascii=False))
    
    print("\n修复后 (对象格式):")
    print("-" * 60)
    new_format = output._asdict()
    print(json.dumps(new_format, ensure_ascii=False, indent=2))
    
    print("\n说明:")
    print("-" * 60)
    print("• 数组格式: Coze 只看到 [value1, value2, ...]，不知道哪个是 draft_id")
    print("• 对象格式: Coze 看到 {\"draft_id\": \"...\", \"success\": true, ...}")
    print("           可以通过键名访问每个字段")
    print()


def show_realistic_example():
    """展示一个更真实的例子"""
    print("=" * 60)
    print("真实使用场景示例")
    print("=" * 60)
    
    # 成功情况
    print("\n场景 1: 成功创建草稿")
    print("-" * 60)
    success_output = Output(
        draft_id="abc123_def456",
        success=True,
        message="草稿创建成功",
        details={"width": 1920, "height": 1080, "fps": 30}
    )._asdict()
    
    print(json.dumps(success_output, ensure_ascii=False, indent=2))
    
    # 错误情况
    print("\n场景 2: 创建失败")
    print("-" * 60)
    error_output = Output(
        success=False,
        message="调用 create_draft 时发生错误: 无效的参数",
        error_code="INVALID_PARAMS",
        category="validation_error"
    )._asdict()
    
    print(json.dumps(error_output, ensure_ascii=False, indent=2))
    
    print("\n✅ 两种情况下，Coze 都能正确解析字段!")
    print()


def main():
    """运行所有演示"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Handler 输出格式修复演示" + " " * 24 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    show_old_format()
    show_new_format()
    show_comparison()
    show_realistic_example()
    
    print("=" * 60)
    print("总结")
    print("=" * 60)
    print("\n修复方法:")
    print("  修复前: return Output(...)")
    print("  修复后: return Output(...)._asdict()")
    print("\n影响:")
    print("  • 返回类型从 Output (NamedTuple) 改为 Dict[str, Any]")
    print("  • Coze 现在可以正确识别和使用返回的字段")
    print("  • 保持了使用 Output 类型进行类型检查的优势")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
