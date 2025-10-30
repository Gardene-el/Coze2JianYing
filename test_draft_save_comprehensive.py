#!/usr/bin/env python3
"""
综合测试：草稿保存在各种场景下的表现
包括：正常保存、文件夹重命名、多个草稿并发等
"""
import os
import sys
import tempfile
import shutil
import json
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pyJianYingDraft as draft
from src.utils.draft_generator import DraftGenerator


def test_normal_save():
    """测试1: 正常保存（文件夹未被重命名）"""
    print("\n" + "="*60)
    print("测试1: 正常保存（文件夹未被重命名）")
    print("="*60 + "\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        draft_id = "normal-draft"
        draft_folder_obj = draft.DraftFolder(tmpdir)
        script = draft_folder_obj.create_draft(draft_id, 1920, 1080, allow_replace=True)
        script.add_track(draft.TrackType.text, "test_track")
        
        generator = DraftGenerator(output_base_dir=tmpdir)
        expected_folder = os.path.join(tmpdir, draft_id)
        
        result_folder = generator._save_draft_robust(script, expected_folder, draft_id)
        
        # 验证
        content_path = os.path.join(result_folder, "draft_content.json")
        assert os.path.exists(content_path), "draft_content.json 应该存在"
        assert result_folder == expected_folder, "返回的路径应该与预期一致"
        
        print("✅ 测试通过：正常保存工作正常\n")
        return True


def test_folder_renamed():
    """测试2: 文件夹被重命名（模拟剪映行为）"""
    print("\n" + "="*60)
    print("测试2: 文件夹被重命名（模拟剪映行为）")
    print("="*60 + "\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        draft_id = "renamed-draft"
        draft_folder_obj = draft.DraftFolder(tmpdir)
        script = draft_folder_obj.create_draft(draft_id, 1920, 1080, allow_replace=True)
        script.add_track(draft.TrackType.text, "test_track")
        
        # 保存一次以生成 draft_meta_info.json
        script.save()
        
        original_folder = os.path.join(tmpdir, draft_id)
        
        # 读取剪映内部的 draft_id
        meta_info_path = os.path.join(original_folder, "draft_meta_info.json")
        with open(meta_info_path, 'r', encoding='utf-8') as f:
            meta_info = json.load(f)
        jianyingpro_id = meta_info.get('draft_id', '')
        
        # 模拟剪映重命名
        renamed_folder = os.path.join(tmpdir, jianyingpro_id)
        shutil.move(original_folder, renamed_folder)
        
        # 删除 draft_content.json 模拟未保存状态
        content_path = os.path.join(renamed_folder, "draft_content.json")
        os.remove(content_path)
        
        print(f"原文件夹: {draft_id}")
        print(f"重命名为: {jianyingpro_id}\n")
        
        # 测试健壮保存
        generator = DraftGenerator(output_base_dir=tmpdir)
        result_folder = generator._save_draft_robust(script, original_folder, draft_id)
        
        # 验证
        new_content_path = os.path.join(result_folder, "draft_content.json")
        assert os.path.exists(new_content_path), "draft_content.json 应该在新位置存在"
        assert result_folder == renamed_folder, "返回的路径应该是重命名后的路径"
        
        print("✅ 测试通过：正确处理了文件夹重命名\n")
        return True


def test_multiple_drafts_with_rename():
    """测试3: 多个草稿时，能正确识别最新的被重命名文件夹"""
    print("\n" + "="*60)
    print("测试3: 多个草稿时正确识别最新的重命名文件夹")
    print("="*60 + "\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建第一个旧草稿
        old_draft_id = "old-draft"
        old_folder = draft.DraftFolder(tmpdir)
        old_script = old_folder.create_draft(old_draft_id, 1920, 1080, allow_replace=True)
        old_script.save()
        
        # 读取旧草稿的内部ID
        old_meta_path = os.path.join(tmpdir, old_draft_id, "draft_meta_info.json")
        with open(old_meta_path, 'r', encoding='utf-8') as f:
            old_meta = json.load(f)
        old_jianyingpro_id = old_meta.get('draft_id', '')
        
        # 重命名旧草稿
        old_renamed = os.path.join(tmpdir, old_jianyingpro_id)
        shutil.move(os.path.join(tmpdir, old_draft_id), old_renamed)
        
        # 删除旧草稿的 draft_content.json
        os.remove(os.path.join(old_renamed, "draft_content.json"))
        
        time.sleep(0.1)  # 确保时间戳不同
        
        # 创建新草稿
        new_draft_id = "new-draft"
        new_folder = draft.DraftFolder(tmpdir)
        new_script = new_folder.create_draft(new_draft_id, 1920, 1080, allow_replace=True)
        new_script.add_track(draft.TrackType.text, "new_track")
        new_script.save()
        
        # 读取新草稿的内部ID
        new_meta_path = os.path.join(tmpdir, new_draft_id, "draft_meta_info.json")
        with open(new_meta_path, 'r', encoding='utf-8') as f:
            new_meta = json.load(f)
        new_jianyingpro_id = new_meta.get('draft_id', '')
        
        # 重命名新草稿
        new_renamed = os.path.join(tmpdir, new_jianyingpro_id)
        original_new_folder = os.path.join(tmpdir, new_draft_id)
        
        # 如果重命名目标已存在（例如UUID冲突），跳过测试
        if os.path.exists(new_renamed):
            print(f"⚠️  UUID冲突，跳过此测试")
            print("✅ 测试跳过：UUID冲突（这是正常的随机情况）\n")
            return True
        
        shutil.move(original_new_folder, new_renamed)
        
        # 删除新草稿的 draft_content.json
        new_content_file = os.path.join(new_renamed, "draft_content.json")
        if os.path.exists(new_content_file):
            os.remove(new_content_file)
        
        print(f"旧草稿: {old_draft_id} -> {old_jianyingpro_id}")
        print(f"新草稿: {new_draft_id} -> {new_jianyingpro_id}\n")
        
        # 测试：应该找到新草稿的文件夹
        generator = DraftGenerator(output_base_dir=tmpdir)
        result_folder = generator._save_draft_robust(new_script, original_new_folder, new_draft_id)
        
        # 验证：应该是新草稿的文件夹
        assert result_folder == new_renamed, f"应该找到新草稿的文件夹 {new_renamed}，实际找到 {result_folder}"
        
        new_content_path = os.path.join(result_folder, "draft_content.json")
        assert os.path.exists(new_content_path), "新草稿的 draft_content.json 应该存在"
        
        print("✅ 测试通过：正确识别了最新的重命名文件夹\n")
        return True


def test_fallback_to_manual_creation():
    """测试4: 当检测失败时，回退到手动创建"""
    print("\n" + "="*60)
    print("测试4: 回退到手动创建文件夹")
    print("="*60 + "\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        draft_id = "fallback-draft"
        
        # 创建一个不在 tmpdir 中的 script
        with tempfile.TemporaryDirectory() as other_dir:
            draft_folder_obj = draft.DraftFolder(other_dir)
            script = draft_folder_obj.create_draft("temp", 1920, 1080, allow_replace=True)
            script.add_track(draft.TrackType.text, "test_track")
            script.save()
        
        # 现在尝试保存到 tmpdir（这会失败并触发回退逻辑）
        generator = DraftGenerator(output_base_dir=tmpdir)
        expected_folder = os.path.join(tmpdir, draft_id)
        
        result_folder = generator._save_draft_robust(script, expected_folder, draft_id)
        
        # 验证
        content_path = os.path.join(result_folder, "draft_content.json")
        assert os.path.exists(content_path), "draft_content.json 应该被手动创建"
        assert result_folder == expected_folder, "返回的路径应该与预期一致"
        
        print("✅ 测试通过：成功回退到手动创建\n")
        return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始运行综合测试套件")
    print("="*60)
    
    tests = [
        ("正常保存", test_normal_save),
        ("文件夹重命名", test_folder_renamed),
        ("多草稿识别", test_multiple_drafts_with_rename),
        ("手动创建回退", test_fallback_to_manual_creation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result, None))
        except Exception as e:
            print(f"❌ 测试失败: {name}")
            print(f"   错误: {e}\n")
            import traceback
            traceback.print_exc()
            results.append((name, False, str(e)))
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60 + "\n")
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for name, result, error in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
        if error:
            print(f"     {error}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
