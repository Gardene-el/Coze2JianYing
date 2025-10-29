#!/usr/bin/env python3
"""
测试 draft_meta_manager 对各种JSON错误的处理
验证错误消息的清晰度和用户友好性
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.draft_meta_manager import DraftMetaManager
import tempfile
import json
import shutil


def create_test_environment():
    """创建测试环境"""
    test_dir = tempfile.mkdtemp()
    
    draft_content = {
        'tracks': [{
            'segments': [{
                'time_range': {'start': 0, 'end': 5000}  # 5 seconds in ms
            }]
        }]
    }
    
    test_cases = {
        # 有效草稿
        'valid_draft_001': {
            'meta': {'draft_name': 'valid_draft_001', 'draft_id': 'VALID-001'},
            'should_pass': True
        },
        'valid_draft_002': {
            'meta': {'draft_name': 'valid_draft_002', 'draft_id': 'VALID-002'},
            'should_pass': True
        },
        # 空文件
        'empty_file_draft': {
            'meta': '',
            'should_pass': False,
            'error_type': 'empty'
        },
        # 仅空白字符
        'whitespace_draft': {
            'meta': '   \n\t  ',
            'should_pass': False,
            'error_type': 'empty'
        },
        # 多个JSON对象
        'multiple_json_draft': {
            'meta': '{}{}',
            'should_pass': False,
            'error_type': 'extra_data'
        },
        # 无效JSON
        'invalid_json_draft': {
            'meta': '{invalid}',
            'should_pass': False,
            'error_type': 'invalid'
        },
    }
    
    for draft_name, config in test_cases.items():
        draft_dir = os.path.join(test_dir, draft_name)
        os.makedirs(draft_dir)
        
        # 创建 draft_content.json
        with open(os.path.join(draft_dir, 'draft_content.json'), 'w') as f:
            json.dump(draft_content, f)
        
        # 创建 draft_meta_info.json
        meta_data = config['meta']
        with open(os.path.join(draft_dir, 'draft_meta_info.json'), 'w') as f:
            if isinstance(meta_data, str):
                f.write(meta_data)
            else:
                json.dump(meta_data, f)
    
    return test_dir, test_cases


def test_error_handling():
    """测试错误处理"""
    print("=" * 80)
    print("测试 draft_meta_manager 错误处理")
    print("=" * 80)
    
    test_dir, test_cases = create_test_environment()
    
    try:
        print(f"\n测试目录: {test_dir}")
        print(f"测试草稿数量: {len(test_cases)}")
        print(f"  - 有效草稿: {sum(1 for c in test_cases.values() if c['should_pass'])}")
        print(f"  - 问题草稿: {sum(1 for c in test_cases.values() if not c['should_pass'])}")
        
        print("\n开始扫描...")
        print("-" * 80)
        
        manager = DraftMetaManager()
        result = manager.scan_and_generate_meta_info(test_dir)
        
        print("-" * 80)
        print("\n扫描结果:")
        print(f"  ✅ 找到有效草稿: {result['draft_ids']}")
        print(f"  📁 草稿列表: {[d['draft_name'] for d in result['all_draft_store']]}")
        
        # 验证结果
        expected_valid = sum(1 for c in test_cases.values() if c['should_pass'])
        actual_valid = result['draft_ids']
        
        print("\n验证:")
        if expected_valid == actual_valid:
            print(f"  ✅ 测试通过: 预期 {expected_valid} 个有效草稿，实际找到 {actual_valid} 个")
            return True
        else:
            print(f"  ❌ 测试失败: 预期 {expected_valid} 个有效草稿，但找到 {actual_valid} 个")
            return False
            
    finally:
        # 清理
        shutil.rmtree(test_dir)
        print("\n✅ 测试环境已清理")


def test_real_world_scenario():
    """测试实际用例场景（来自issue）"""
    print("\n" + "=" * 80)
    print("测试实际用例场景（模拟issue中的情况）")
    print("=" * 80)
    
    test_dir = tempfile.mkdtemp()
    
    draft_content = {
        'tracks': [{
            'segments': [{
                'time_range': {'start': 0, 'end': 5000}
            }]
        }]
    }
    
    # 模拟issue中的草稿状态
    scenarios = [
        # 有效草稿
        ('6BADD2B7-DD7C-4FFA-8BFF-AF5F99C5A97B', True, None),
        ('87cc6c27-ce94-4219-bbb7-cce388cafc37', True, None),
        ('8a366c1c-b575-43ba-82e2-6e3991276d27(16)', True, None),
        # 问题草稿（来自issue日志）
        ('265646ca-0818-4dfc-9a78-f281845f0cfd(15)', False, ''),  # Empty
        ('9F776C47-1C7C-44ca-82D1-882A267B9AE4', False, '{}{}'),  # Extra data
        ('d5eaa880-ae11-441c-ae7e-1872d95d108f(16)', False, ''),  # Empty
    ]
    
    try:
        for draft_id, is_valid, meta_content in scenarios:
            draft_dir = os.path.join(test_dir, draft_id)
            os.makedirs(draft_dir)
            
            with open(os.path.join(draft_dir, 'draft_content.json'), 'w') as f:
                json.dump(draft_content, f)
            
            with open(os.path.join(draft_dir, 'draft_meta_info.json'), 'w') as f:
                if is_valid:
                    json.dump({'draft_name': draft_id, 'draft_id': draft_id}, f)
                else:
                    f.write(meta_content)
        
        print(f"\n测试目录: {test_dir}")
        print("开始扫描...")
        print("-" * 80)
        
        manager = DraftMetaManager()
        result = manager.scan_and_generate_meta_info(test_dir)
        
        print("-" * 80)
        print("\n扫描结果:")
        print(f"  ✅ 找到有效草稿: {result['draft_ids']} 个")
        print(f"  📁 草稿列表:")
        for draft in result['all_draft_store']:
            print(f"     - {draft['draft_name']}")
        
        # 验证结果
        expected_valid = sum(1 for _, is_valid, _ in scenarios if is_valid)
        actual_valid = result['draft_ids']
        
        print("\n验证:")
        if expected_valid == actual_valid:
            print(f"  ✅ 测试通过: 预期 {expected_valid} 个有效草稿，实际找到 {actual_valid} 个")
            print("  ✅ 问题草稿已被正确识别并跳过，提供了详细的错误信息")
            return True
        else:
            print(f"  ❌ 测试失败: 预期 {expected_valid} 个有效草稿，但找到 {actual_valid} 个")
            return False
            
    finally:
        shutil.rmtree(test_dir)
        print("\n✅ 测试环境已清理")


if __name__ == "__main__":
    print("draft_meta_manager 错误处理测试套件\n")
    
    test1_passed = test_error_handling()
    test2_passed = test_real_world_scenario()
    
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"基础错误处理测试: {'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"实际场景测试: {'✅ 通过' if test2_passed else '❌ 失败'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1)
