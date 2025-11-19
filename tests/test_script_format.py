#!/usr/bin/env python3
"""
测试脚本格式化功能（新增的格式化输入按钮）
"""
import json
import re
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def decode_escaped_string(s: str) -> str:
    """解码包含literal escape序列的字符串"""
    replacements = [
        (r'\n', '\n'),
        (r'\t', '\t'),
        (r'\r', '\r'),
        (r'\"', '"'),
        (r"\'", "'"),
    ]
    
    result = s
    for escaped, unescaped in replacements:
        result = result.replace(escaped, unescaped)
    
    return result


def fix_script_issues(script: str) -> str:
    """修复脚本中的常见问题"""
    lines = script.split('\n')
    fixed_lines = []
    draft_id_var = None
    
    for line in lines:
        # 问题1: 修复draft_变量引用
        if 'draft_id' in line and '=' in line and 'resp_' in line:
            match = re.search(r'(draft_[\w]+)\s*=\s*resp_[\w]+\.draft_id', line)
            if match:
                draft_id_var = match.group(1)
        
        if draft_id_var and re.search(r'\bdraft_\b(?![\w])', line):
            line = re.sub(r'\bdraft_\b(?![\w])', draft_id_var, line)
        
        # 问题2: 修复TimeRange
        if ('target_timerange' in line or 'timerange' in line) and '= "' in line and ('{' in line or '\\{' in line):
            patterns = [
                r'= "(\\?\{[^}]+\\?\})"',
            ]
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    json_str = match.group(1)
                    json_str = json_str.replace('\\"', '"').replace('\\{', '{').replace('\\}', '}')
                    try:
                        data = json.loads(json_str)
                        params = ', '.join([f"{k}={v}" for k, v in data.items()])
                        line = re.sub(r'= ".*"', f'= TimeRange({params})', line)
                        break
                    except:
                        pass
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def extract_script_from_input(content: str) -> str:
    """从输入内容中提取脚本"""
    content = content.strip()
    
    # 方式1: 尝试作为JSON解析
    try:
        data = json.loads(content)
        if isinstance(data, dict) and "output" in data:
            script_content = data["output"]
            script_content = decode_escaped_string(script_content)
            script_content = fix_script_issues(script_content)
            return script_content
    except json.JSONDecodeError:
        pass
    
    # 方式2: 检查是否包含literal \n
    if r'\n' in content or '\\n' in content:
        script_content = decode_escaped_string(content)
        script_content = fix_script_issues(script_content)
        return script_content
    
    # 方式3: 已经是正常格式的脚本
    return content


def test_json_format():
    """测试JSON格式输入"""
    print("=" * 60)
    print("测试1: JSON格式输入")
    print("=" * 60)
    
    # 模拟从Coze复制的JSON（使用Python字符串字面量）
    json_str = r'''{
  "output": "\n\n# API 调用: create_draft\n\ndraft_abc123 = resp_abc123.draft_id\n\nresp = await add_track(draft_, req)\n\nreq['timerange'] = \"{\\\"duration\\\":5000000,\\\"start\\\":0}\""
}'''
    
    try:
        result = extract_script_from_input(json_str)
        
        # 验证
        assert result.count('\n') > 3, "应该有多行"
        assert "draft_abc123" in result, "应该保留draft_id变量"
        assert re.search(r'\(draft_,', result) is None, "draft_不应该存在"
        assert "TimeRange(duration=5000000, start=0)" in result, "TimeRange应该被修复"
        
        print("✅ JSON格式处理成功")
        print(f"输入长度: {len(json_str)}")
        print(f"输出长度: {len(result)}")
        print(f"输出行数: {result.count(chr(10)) + 1}")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_literal_escape():
    """测试literal escape序列"""
    print("\n" + "=" * 60)
    print("测试2: Literal Escape序列")
    print("=" * 60)
    
    # 模拟用户直接复制的字符串
    literal_input = r'\n\n# API 调用: create_draft\n\ndraft_xyz = resp_xyz.draft_id\n\nresp = await add_track(draft_, req)\n'
    
    try:
        result = extract_script_from_input(literal_input)
        
        # 验证
        assert result.startswith('\n'), "应该以换行符开始"
        assert "# API 调用:" in result, "应该包含注释"
        assert "draft_xyz" in result, "应该保留变量名"
        assert "draft_," not in result, "draft_不应该存在"
        
        print("✅ Literal escape处理成功")
        print(f"输入: {repr(literal_input[:50])}")
        print(f"输出前3行: {repr(result[:50])}")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_draft_variable_fix():
    """测试draft_变量修复"""
    print("\n" + "=" * 60)
    print("测试3: draft_变量修复")
    print("=" * 60)
    
    script = """
draft_myid = resp_myid.draft_id

resp1 = await add_track(draft_, req1)
resp2 = await add_track(draft_, req2)
resp3 = await save_draft(draft_)
"""
    
    try:
        result = fix_script_issues(script)
        
        # 验证
        draft_underscore_count = len(re.findall(r'\(draft_[,\)]', result))
        assert draft_underscore_count == 0, f"不应该有draft_引用，找到{draft_underscore_count}个"
        assert result.count("draft_myid") >= 4, "应该有多处替换为draft_myid"
        
        print("✅ draft_变量修复成功")
        print(f"替换次数: {result.count('draft_myid') - 1}")  # -1 因为定义算一次
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_timerange_fix():
    """测试TimeRange JSON字符串修复"""
    print("\n" + "=" * 60)
    print("测试4: TimeRange JSON修复")
    print("=" * 60)
    
    test_cases = [
        ('req["timerange"] = "{\\"duration\\":4200000,\\"start\\":0}"', "转义的JSON"),
        ('req["timerange"] = "{"duration":5000000,"start":0}"', "非转义的JSON"),
        ('req_params[\'target_timerange\'] = "{\\"duration\\":3000000,\\"start\\":1000}"', "带参数的JSON"),
    ]
    
    passed = 0
    for test_input, description in test_cases:
        try:
            result = fix_script_issues(test_input)
            assert "TimeRange(" in result, f"{description}: 应该包含TimeRange"
            assert '"{' not in result, f"{description}: 不应该有JSON字符串"
            print(f"✅ {description}: {result.strip()}")
            passed += 1
        except Exception as e:
            print(f"❌ {description}: {e}")
    
    if passed == len(test_cases):
        print(f"✅ 所有TimeRange测试通过 ({passed}/{len(test_cases)})")
        return True
    else:
        print(f"❌ 部分TimeRange测试失败 ({passed}/{len(test_cases)})")
        return False


def test_issue_example():
    """测试GitHub issue中的实际示例"""
    print("\n" + "=" * 60)
    print("测试5: GitHub Issue实际示例")
    print("=" * 60)
    
    # 从issue中截取的实际问题片段
    issue_script = r'\n\n# API 调用: create_draft\n\ndraft_af21f036 = resp_af21f036.draft_id\n\nresp_e6fbe1a4 = await add_track(draft_, req_e6fbe1a4)\n\nreq_params_599961a7[\'target_timerange\'] = "{\"duration\":4200000,\"start\":0}"'
    
    try:
        result = extract_script_from_input(issue_script)
        
        # 验证所有问题都被修复
        checks = {
            "有换行符": result.count('\n') > 3,
            "draft_被替换": "draft_af21f036" in result and "draft_," not in result,
            "TimeRange被修复": "TimeRange(duration=4200000, start=0)" in result,
            "没有literal \\n": r'\n' not in result,
        }
        
        print("验证结果:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
        
        if all(checks.values()):
            print("✅ GitHub issue示例修复成功")
            return True
        else:
            print("❌ 部分检查失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🎬 开始测试脚本格式化功能")
    print("这些测试验证新增的'格式化输入'按钮功能\n")
    
    results = []
    
    # 运行所有测试
    results.append(("JSON格式输入", test_json_format()))
    results.append(("Literal Escape序列", test_literal_escape()))
    results.append(("draft_变量修复", test_draft_variable_fix()))
    results.append(("TimeRange JSON修复", test_timerange_fix()))
    results.append(("GitHub Issue示例", test_issue_example()))
    
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
        print("🎉 所有格式化功能测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)
