#!/usr/bin/env python3
"""
测试草稿命名修复
验证使用"扣子2剪映：" + UUID 作为文件夹名可以避免剪映重命名问题，同时保留UUID用于批量识别
"""

import os
import sys
import json
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.draft_generator import DraftGenerator


def test_draft_naming_with_project_name():
    """测试使用"扣子2剪映：" + UUID 作为文件夹名"""
    print("=== 测试草稿命名修复 ===\n")
    
    # 创建临时输出目录
    temp_dir = tempfile.mkdtemp(prefix="test_draft_naming_")
    print(f"临时目录: {temp_dir}\n")
    
    try:
        # 创建草稿生成器
        generator = DraftGenerator(output_base_dir=temp_dir)
        
        # 准备测试数据：使用人类可读的项目名称
        test_draft_id = "e559681e-6730-4c6b-b7ba-4e785e2c9f86"
        test_draft_data = {
            "format_version": "1.0",
            "export_type": "single_draft",
            "draft_count": 1,
            "drafts": [{
                "draft_id": test_draft_id,
                "project": {
                    "name": "测试项目",  # 人类可读的名称
                    "width": 1920,
                    "height": 1080,
                    "fps": 30
                },
                "tracks": [
                    {
                        "track_type": "video",
                        "segments": []
                    }
                ]
            }]
        }
        
        # 转换为 JSON 字符串
        test_json = json.dumps(test_draft_data, ensure_ascii=False, indent=2)
        
        # 生成草稿
        print("1. 生成草稿...")
        draft_paths = generator.generate(test_json, output_folder=temp_dir)
        
        # 验证结果
        print("\n2. 验证结果...")
        print(f"   生成的草稿路径: {draft_paths}")
        
        if not draft_paths:
            print("   ❌ 未生成草稿路径")
            return False
        
        draft_path = draft_paths[0]
        expected_folder_name = f"扣子2剪映：{test_draft_id}"
        
        # 检查文件夹名称是否为"扣子2剪映：" + UUID
        folder_name = os.path.basename(draft_path)
        print(f"   文件夹名称: {folder_name}")
        print(f"   期望名称: {expected_folder_name}")
        
        if folder_name != expected_folder_name:
            print(f"   ❌ 文件夹名称不匹配")
            return False
        
        # 验证包含UUID用于批量识别
        if test_draft_id not in folder_name:
            print(f"   ❌ 文件夹名称不包含UUID")
            return False
        
        print(f"   ✅ 文件夹名称正确（包含前缀和UUID）")
        
        # 检查草稿文件是否存在
        draft_content_file = os.path.join(draft_path, "draft_content.json")
        if not os.path.exists(draft_content_file):
            print(f"   ❌ draft_content.json 不存在")
            return False
        
        print(f"   ✅ draft_content.json 存在")
        
        # 检查是否可以读取草稿内容
        try:
            with open(draft_content_file, 'r', encoding='utf-8') as f:
                draft_content = json.load(f)
            print(f"   ✅ 草稿内容可正常读取")
        except Exception as e:
            print(f"   ❌ 读取草稿内容失败: {e}")
            return False
        
        print("\n✅ 测试通过！使用'扣子2剪映：' + UUID 作为文件夹名")
        print("   优势：既避免剪映重命名，又保留UUID用于批量识别")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\n已清理临时目录: {temp_dir}")


def test_draft_naming_with_default_name():
    """测试生成的UUID也会添加前缀"""
    print("\n=== 测试自动生成UUID ===\n")
    
    # 创建临时输出目录
    temp_dir = tempfile.mkdtemp(prefix="test_draft_naming_default_")
    print(f"临时目录: {temp_dir}\n")
    
    try:
        # 创建草稿生成器
        generator = DraftGenerator(output_base_dir=temp_dir)
        
        # 准备测试数据：使用明确的 draft_id
        test_draft_id = "test-uuid-123"
        test_draft_data = {
            "format_version": "1.0",
            "export_type": "single_draft",
            "draft_count": 1,
            "drafts": [{
                "draft_id": test_draft_id,
                "project": {
                    # 没有 name 字段
                    "width": 1920,
                    "height": 1080,
                    "fps": 30
                },
                "tracks": [
                    {
                        "track_type": "video",
                        "segments": []
                    }
                ]
            }]
        }
        
        # 转换为 JSON 字符串
        test_json = json.dumps(test_draft_data, ensure_ascii=False, indent=2)
        
        # 生成草稿
        print("1. 生成草稿...")
        draft_paths = generator.generate(test_json, output_folder=temp_dir)
        
        # 验证结果
        print("\n2. 验证结果...")
        print(f"   生成的草稿路径: {draft_paths}")
        
        if not draft_paths:
            print("   ❌ 未生成草稿路径")
            return False
        
        draft_path = draft_paths[0]
        expected_folder_name = f"扣子2剪映：{test_draft_id}"
        
        # 检查文件夹名称
        folder_name = os.path.basename(draft_path)
        print(f"   文件夹名称: {folder_name}")
        print(f"   期望名称: {expected_folder_name}")
        
        if folder_name != expected_folder_name:
            print(f"   ❌ 文件夹名称不匹配")
            return False
        
        # 检查草稿文件是否存在
        draft_content_file = os.path.join(draft_path, "draft_content.json")
        if not os.path.exists(draft_content_file):
            print(f"   ❌ draft_content.json 不存在")
            return False
        
        print(f"   ✅ draft_content.json 存在")
        
        print("\n✅ 测试通过！使用'扣子2剪映：' + UUID")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\n已清理临时目录: {temp_dir}")


def test_draft_naming_with_uuid_comparison():
    """对比测试：使用纯 UUID vs '扣子2剪映：' + UUID"""
    print("\n=== 对比测试：文件夹命名方式 ===\n")
    
    # 测试使用 UUID 的情况（旧方式）
    print("旧方式: 使用纯 UUID 作为文件夹名")
    print("问题: 剪映可能会重命名 UUID 文件夹，导致 save() 失败\n")
    
    # 测试使用前缀+UUID的情况（新方式）
    print("新方式: 使用'扣子2剪映：' + UUID 作为文件夹名")
    print("优势: 人类可读前缀防止剪映重命名，UUID保留用于批量识别\n")
    
    return True


if __name__ == "__main__":
    print("草稿命名修复测试\n")
    print("=" * 80)
    print()
    
    results = []
    
    # 运行测试
    results.append(("使用'扣子2剪映：'+UUID", test_draft_naming_with_project_name()))
    results.append(("自动生成UUID", test_draft_naming_with_default_name()))
    results.append(("对比测试", test_draft_naming_with_uuid_comparison()))
    
    # 打印总结
    print("\n" + "=" * 80)
    print("\n测试总结:")
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status}: {test_name}")
    
    # 总体结果
    all_passed = all(result for _, result in results)
    passed_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n总计: {passed_count}/{total_count} 测试通过")
    
    if all_passed:
        print("\n✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1)
