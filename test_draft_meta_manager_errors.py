#!/usr/bin/env python3
"""
测试 draft_meta_manager 的核心功能
验证系统能够正确处理各种 draft_meta_info.json 状态（包括加密文件）
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
        # 有效草稿 - draft_meta_info.json 内容不重要
        'valid_draft_001': {
            'meta': {'draft_name': 'valid_draft_001', 'draft_id': 'VALID-001'},
            'should_pass': True
        },
        'valid_draft_002': {
            'meta': {'draft_name': 'valid_draft_002', 'draft_id': 'VALID-002'},
            'should_pass': True
        },
        # 加密内容（模拟真实剪映草稿）
        'encrypted_draft': {
            'meta': 'BF46PyJE3d2UEKWxuiZaAjcjhZ1aTgrleb1G8gwJ71ed...',
            'should_pass': True,  # 现在应该通过，因为不读取内容
            'error_type': 'encrypted'
        },
        # 空文件 - 应该仍然通过，因为不读取内容
        'empty_file_draft': {
            'meta': '',
            'should_pass': True,  # 改为 True
            'error_type': 'empty'
        },
        # 任意文本 - 应该通过
        'arbitrary_text_draft': {
            'meta': 'This is not JSON at all!',
            'should_pass': True,
            'error_type': 'not_json'
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
    """测试系统对各种 draft_meta_info.json 状态的处理"""
    print("=" * 80)
    print("测试 draft_meta_manager 核心功能")
    print("=" * 80)
    
    test_dir, test_cases = create_test_environment()
    
    try:
        print(f"\n测试目录: {test_dir}")
        print(f"测试草稿数量: {len(test_cases)}")
        print(f"  - 应该通过: {sum(1 for c in test_cases.values() if c['should_pass'])}")
        print(f"  - 特殊情况测试: {sum(1 for c in test_cases.values() if not c['should_pass'])}")
        
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
            print(f"  ✅ 系统正确处理了加密和各种格式的 draft_meta_info.json")
            return True
        else:
            print(f"  ❌ 测试失败: 预期 {expected_valid} 个有效草稿，但找到 {actual_valid} 个")
            return False
            
    finally:
        # 清理
        shutil.rmtree(test_dir)
        print("\n✅ 测试环境已清理")


def test_real_world_scenario():
    """测试实际用例场景（包括加密的剪映草稿）"""
    print("\n" + "=" * 80)
    print("测试实际用例场景（加密的剪映草稿）")
    print("=" * 80)
    
    test_dir = tempfile.mkdtemp()
    
    draft_content = {
        'tracks': [{
            'segments': [{
                'time_range': {'start': 0, 'end': 5000}
            }]
        }]
    }
    
    # 模拟真实的剪映草稿，包括加密的 draft_meta_info.json
    scenarios = [
        # 有效草稿 - 加密的 draft_meta_info.json（真实剪映格式）
        ('6BADD2B7-DD7C-4FFA-8BFF-AF5F99C5A97B', True, 
         'BF46PyJE3d2UEKWxuiZaAjcjhZ1aTgrleb1G8gwJ71edGYEBFfd1QpSdtvrDa5Gc...'),
        ('87cc6c27-ce94-4219-bbb7-cce388cafc37', True,
         'BF46PyJE3d2UEKWxuiZaAjcjhZ1aTgrleb1G8gwJ71edGYEBFfd1QpSdtvrDa5Gc...'),
        ('8a366c1c-b575-43ba-82e2-6e3991276d27(16)', True,
         'BF46PyJE3d2UEKWxuiZaAjcjhZ1aTgrleb1G8gwJ71edGYEBFfd1QpSdtvrDa5Gc...'),
        # 以前会导致错误的草稿（空文件等）现在也应该通过
        ('265646ca-0818-4dfc-9a78-f281845f0cfd(15)', True, ''),  # Empty - 现在OK
        ('9F776C47-1C7C-44ca-82D1-882A267B9AE4', True, '{}{}'),  # Extra data - 现在OK
        ('d5eaa880-ae11-441c-ae7e-1872d95d108f(16)', True, ''),  # Empty - 现在OK
    ]
    
    try:
        for draft_id, is_valid, meta_content in scenarios:
            draft_dir = os.path.join(test_dir, draft_id)
            os.makedirs(draft_dir)
            
            with open(os.path.join(draft_dir, 'draft_content.json'), 'w') as f:
                json.dump(draft_content, f)
            
            # 写入各种格式的 draft_meta_info.json
            with open(os.path.join(draft_dir, 'draft_meta_info.json'), 'w') as f:
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
        
        # 验证结果 - 所有草稿都应该通过
        expected_valid = sum(1 for _, is_valid, _ in scenarios if is_valid)
        actual_valid = result['draft_ids']
        
        print("\n验证:")
        if expected_valid == actual_valid:
            print(f"  ✅ 测试通过: 预期 {expected_valid} 个有效草稿，实际找到 {actual_valid} 个")
            print(f"  ✅ 系统正确处理了加密的 draft_meta_info.json")
            print(f"  ✅ 以前会导致错误的草稿现在都能正常处理")
            return True
        else:
            print(f"  ❌ 测试失败: 预期 {expected_valid} 个有效草稿，但找到 {actual_valid} 个")
            return False
            
    finally:
        shutil.rmtree(test_dir)
        print("\n✅ 测试环境已清理")


if __name__ == "__main__":
    print("draft_meta_manager 核心功能测试套件\n")
    print("验证系统能够处理加密和各种格式的 draft_meta_info.json\n")
    
    test1_passed = test_error_handling()
    test2_passed = test_real_world_scenario()
    
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"核心功能测试: {'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"实际场景测试（加密文件）: {'✅ 通过' if test2_passed else '❌ 失败'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 所有测试通过！")
        print("✅ 系统不再读取 draft_meta_info.json 内容")
        print("✅ 可以正确处理加密的剪映草稿")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1)
