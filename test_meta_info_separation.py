#!/usr/bin/env python3
"""
测试 draft_meta_manager 分离功能
验证元信息生成可以独立于草稿生成流程单独触发
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.draft_generator import DraftGenerator
from app.utils.draft_meta_manager import DraftMetaManager
import tempfile
import json
import shutil


def test_meta_info_generation_separated():
    """测试元信息生成已从草稿生成流程中分离"""
    print("=== 测试元信息生成分离功能 ===")
    
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp()
    print(f"创建测试目录: {test_dir}")
    
    try:
        # 创建模拟的草稿文件夹结构
        draft_id = "test_draft_001"
        draft_path = os.path.join(test_dir, draft_id)
        os.makedirs(draft_path)
        
        # 创建 draft_content.json
        draft_content = {
            'tracks': [{
                'segments': [{
                    'time_range': {'start': 0, 'end': 5000}  # 5秒
                }]
            }]
        }
        with open(os.path.join(draft_path, 'draft_content.json'), 'w', encoding='utf-8') as f:
            json.dump(draft_content, f)
        
        # 创建 draft_meta_info.json（必须存在但内容不重要）
        with open(os.path.join(draft_path, 'draft_meta_info.json'), 'w', encoding='utf-8') as f:
            json.dump({'draft_name': draft_id}, f)
        
        print(f"✅ 创建模拟草稿: {draft_id}")
        
        # 测试1: 验证 DraftGenerator 有公共方法 generate_root_meta_info
        print("\n测试1: 验证 DraftGenerator 有公共方法 generate_root_meta_info")
        generator = DraftGenerator(output_base_dir=test_dir)
        assert hasattr(generator, 'generate_root_meta_info'), "DraftGenerator 应该有 generate_root_meta_info 方法"
        assert callable(generator.generate_root_meta_info), "generate_root_meta_info 应该是可调用的"
        print("✅ generate_root_meta_info 方法存在")
        
        # 测试2: 调用独立的元信息生成方法
        print("\n测试2: 调用独立的元信息生成方法")
        meta_info_path = generator.generate_root_meta_info(test_dir)
        assert os.path.exists(meta_info_path), f"元信息文件应该生成: {meta_info_path}"
        print(f"✅ 元信息文件生成成功: {meta_info_path}")
        
        # 测试3: 验证生成的元信息文件内容
        print("\n测试3: 验证生成的元信息文件内容")
        with open(meta_info_path, 'r', encoding='utf-8') as f:
            meta_info = json.load(f)
        
        assert 'all_draft_store' in meta_info, "元信息应包含 all_draft_store"
        assert 'draft_ids' in meta_info, "元信息应包含 draft_ids"
        assert 'root_path' in meta_info, "元信息应包含 root_path"
        assert meta_info['draft_ids'] == 1, f"应该有1个草稿，实际: {meta_info['draft_ids']}"
        print(f"✅ 元信息内容正确，包含 {meta_info['draft_ids']} 个草稿")
        
        # 测试4: 验证可以指定不同的文件夹路径
        print("\n测试4: 验证可以指定不同的文件夹路径")
        test_dir2 = tempfile.mkdtemp()
        draft_path2 = os.path.join(test_dir2, "test_draft_002")
        os.makedirs(draft_path2)
        with open(os.path.join(draft_path2, 'draft_content.json'), 'w', encoding='utf-8') as f:
            json.dump(draft_content, f)
        with open(os.path.join(draft_path2, 'draft_meta_info.json'), 'w', encoding='utf-8') as f:
            json.dump({'draft_name': 'test_draft_002'}, f)
        
        meta_info_path2 = generator.generate_root_meta_info(test_dir2)
        assert os.path.exists(meta_info_path2), "应该在指定文件夹生成元信息文件"
        assert os.path.dirname(meta_info_path2) == test_dir2, "元信息文件应该在指定的文件夹中"
        print(f"✅ 可以指定不同的文件夹: {meta_info_path2}")
        
        # 清理第二个测试目录
        shutil.rmtree(test_dir2, ignore_errors=True)
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！元信息生成已成功分离")
        print("="*60)
        return True
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理测试目录
        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"\n清理测试目录: {test_dir}")


if __name__ == "__main__":
    success = test_meta_info_generation_separated()
    sys.exit(0 if success else 1)
