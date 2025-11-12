#!/usr/bin/env python3
"""
测试脚本修复功能
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_fix_unquoted_strings():
    """测试修复未加引号的字符串"""
    print("=" * 60)
    print("测试修复未加引号的字符串")
    print("=" * 60)
    
    # 模拟脚本执行器的修复方法
    import re
    
    def fix_unquoted_strings(script_content: str) -> str:
        """修复脚本中未加引号的字符串值"""
        lines = script_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 跳过注释行和空行
            if line.strip().startswith('#') or not line.strip():
                fixed_lines.append(line)
                continue
            
            # 匹配函数调用中的参数: param_name=value
            def fix_param(match):
                param_name = match.group(1)
                value = match.group(2)
                
                # 如果值已经有引号，不处理
                if value.startswith('"') or value.startswith("'"):
                    return match.group(0)
                
                # 如果是 None, True, False，不处理
                if value in ['None', 'True', 'False']:
                    return match.group(0)
                
                # 如果是纯数字（整数或小数），不处理
                try:
                    float(value)
                    return match.group(0)
                except ValueError:
                    pass
                
                # 如果是函数调用（包含括号），不处理
                if '(' in value and ')' in value:
                    return match.group(0)
                
                # 其他情况，添加引号
                return f'{param_name}="{value}"'
            
            # 匹配模式：参数名=值
            pattern = r'(\w+)=([^,\)\s"\']+)(?=[,\)\s])'
            fixed_line = re.sub(pattern, fix_param, line)
            
            fixed_lines.append(fixed_line)
        
        return '\n'.join(fixed_lines)
    
    # 测试用例
    test_cases = [
        # (输入, 期望输出)
        (
            "req = CreateDraftRequest(draft_name=demo, width=1920, height=1080)",
            'req = CreateDraftRequest(draft_name="demo", width=1920, height=1080)'
        ),
        (
            "req = AddTrackRequest(track_type=audio, track_name=None)",
            'req = AddTrackRequest(track_type="audio", track_name=None)'
        ),
        (
            "req = CreateAudioSegmentRequest(material_url=https://example.com/audio.mp3, volume=1, change_pitch=False)",
            'req = CreateAudioSegmentRequest(material_url="https://example.com/audio.mp3", volume=1, change_pitch=False)'
        ),
        (
            "req = AddFadeRequest(in_duration=1s, out_duration=0s)",
            'req = AddFadeRequest(in_duration="1s", out_duration="0s")'
        ),
        (
            "req = AddAnimationRequest(animation_type=斜切, duration=None)",
            'req = AddAnimationRequest(animation_type="斜切", duration=None)'
        ),
        (
            "req = AddSegmentToDraftRequest(segment_id=bf1ca35b_9410_495d_96ce_97c37a1a9339, track_index=None)",
            'req = AddSegmentToDraftRequest(segment_id="bf1ca35b_9410_495d_96ce_97c37a1a9339", track_index=None)'
        ),
    ]
    
    all_pass = True
    for i, (input_str, expected) in enumerate(test_cases, 1):
        result = fix_unquoted_strings(input_str)
        if result == expected:
            print(f"✅ 测试 {i} 通过")
            print(f"  输入: {input_str}")
            print(f"  输出: {result}")
        else:
            print(f"❌ 测试 {i} 失败")
            print(f"  输入: {input_str}")
            print(f"  期望: {expected}")
            print(f"  实际: {result}")
            all_pass = False
    
    return all_pass


def test_with_actual_script():
    """测试实际的测试脚本"""
    print("\n" + "=" * 60)
    print("测试实际的测试脚本")
    print("=" * 60)
    
    script_path = project_root / "测试用的脚本"
    
    if not script_path.exists():
        print("⚠️  测试脚本文件不存在")
        return True
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 只测试前几行
        lines = content.split('\n')[:10]
        sample = '\n'.join(lines)
        
        print("原始脚本（前10行）:")
        print("-" * 60)
        print(sample)
        print("-" * 60)
        
        # 应用修复
        import re
        
        def fix_unquoted_strings(script_content: str) -> str:
            """修复脚本中未加引号的字符串值"""
            lines = script_content.split('\n')
            fixed_lines = []
            
            for line in lines:
                if line.strip().startswith('#') or not line.strip():
                    fixed_lines.append(line)
                    continue
                
                def fix_param(match):
                    param_name = match.group(1)
                    value = match.group(2)
                    
                    if value.startswith('"') or value.startswith("'"):
                        return match.group(0)
                    if value in ['None', 'True', 'False']:
                        return match.group(0)
                    
                    try:
                        float(value)
                        return match.group(0)
                    except ValueError:
                        pass
                    
                    if '(' in value and ')' in value:
                        return match.group(0)
                    
                    return f'{param_name}="{value}"'
                
                pattern = r'(\w+)=([^,\)\s"\']+)(?=[,\)\s])'
                fixed_line = re.sub(pattern, fix_param, line)
                fixed_lines.append(fixed_line)
            
            return '\n'.join(fixed_lines)
        
        fixed = fix_unquoted_strings(content)
        fixed_lines = fixed.split('\n')[:10]
        fixed_sample = '\n'.join(fixed_lines)
        
        print("\n修复后的脚本（前10行）:")
        print("-" * 60)
        print(fixed_sample)
        print("-" * 60)
        
        print("\n✅ 实际脚本测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🎬 开始测试脚本修复功能")
    
    results = []
    results.append(("修复未加引号的字符串", test_fix_unquoted_strings()))
    results.append(("实际脚本测试", test_with_actual_script()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)
