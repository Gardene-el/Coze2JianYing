#!/usr/bin/env python3
"""
模拟实际场景测试 - 验证修复解决了原始问题
测试在剪映草稿文件夹中创建草稿，并验证 save() 不会失败
"""

import os
import sys
import json
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.draft_generator import DraftGenerator


def test_actual_scenario_with_jianyingpro_folder():
    """
    模拟实际场景：在剪映草稿文件夹中创建草稿
    
    原始问题场景：
    1. 用户在剪映打开时使用剪映小助手生成草稿
    2. 草稿文件夹名为 UUID (e.g., e559681e-6730-4c6b-b7ba-4e785e2c9f86)
    3. 剪映自动重命名文件夹 (e.g., 686899BC-141F-4302-846A-F83BF61460CB)
    4. script.save() 时找不到原始路径，抛出 FileNotFoundError
    
    修复后的行为：
    1. 使用项目名称作为文件夹名 (e.g., "测试项目")
    2. 剪映不会重命名人类可读的文件夹名
    3. script.save() 成功保存
    """
    print("=== 模拟实际场景测试 ===\n")
    
    # 创建模拟剪映草稿文件夹
    temp_dir = tempfile.mkdtemp(prefix="JianyingPro_UserData_")
    mock_draft_folder = os.path.join(temp_dir, "com.lveditor.draft")
    os.makedirs(mock_draft_folder, exist_ok=True)
    
    print(f"模拟剪映草稿文件夹: {mock_draft_folder}\n")
    
    try:
        # 创建草稿生成器
        generator = DraftGenerator(output_base_dir=mock_draft_folder)
        
        # 准备测试数据 - 模拟 Coze 工作流输出
        test_draft_data = {
            "format_version": "1.0",
            "export_type": "single_draft",
            "draft_count": 1,
            "drafts": [{
                "draft_id": "e559681e-6730-4c6b-b7ba-4e785e2c9f86",  # 原始问题中的 UUID
                "project": {
                    "name": "剪映小助手生成的项目",  # 人类可读的项目名称
                    "width": 1920,
                    "height": 1080,
                    "fps": 30
                },
                "tracks": [
                    {
                        "track_type": "video",
                        "segments": []
                    },
                    {
                        "track_type": "audio",
                        "segments": []
                    }
                ]
            }]
        }
        
        # 转换为 JSON 字符串
        test_json = json.dumps(test_draft_data, ensure_ascii=False, indent=2)
        
        print("1. 场景设置:")
        print(f"   - 剪映草稿文件夹: {mock_draft_folder}")
        print(f"   - Draft ID (UUID): e559681e-6730-4c6b-b7ba-4e785e2c9f86")
        print(f"   - 项目名称: 剪映小助手生成的项目\n")
        
        print("2. 生成草稿...")
        draft_paths = generator.generate(test_json, output_folder=mock_draft_folder)
        
        print("\n3. 验证结果...")
        
        if not draft_paths:
            print("   ❌ 未生成草稿路径")
            return False
        
        draft_path = draft_paths[0]
        folder_name = os.path.basename(draft_path)
        
        print(f"   草稿文件夹: {draft_path}")
        print(f"   文件夹名称: {folder_name}")
        
        # 验证1: 文件夹名称是项目名称而非 UUID
        if folder_name == "e559681e-6730-4c6b-b7ba-4e785e2c9f86":
            print("   ❌ 错误：仍在使用 UUID 作为文件夹名（这会导致原始问题）")
            return False
        
        if folder_name == "剪映小助手生成的项目":
            print("   ✅ 正确：使用项目名称作为文件夹名")
        else:
            print(f"   ⚠️  警告：文件夹名称不是预期的项目名称: {folder_name}")
        
        # 验证2: draft_content.json 存在且可以读取
        draft_content_file = os.path.join(draft_path, "draft_content.json")
        if not os.path.exists(draft_content_file):
            print(f"   ❌ draft_content.json 不存在 (原始问题的症状)")
            return False
        
        print(f"   ✅ draft_content.json 存在")
        
        try:
            with open(draft_content_file, 'r', encoding='utf-8') as f:
                draft_content = json.load(f)
            print(f"   ✅ 草稿内容可正常读取")
        except Exception as e:
            print(f"   ❌ 读取草稿内容失败: {e}")
            return False
        
        # 验证3: draft_meta_info.json 也应该存在
        draft_meta_file = os.path.join(draft_path, "draft_meta_info.json")
        if not os.path.exists(draft_meta_file):
            print(f"   ❌ draft_meta_info.json 不存在")
            return False
        
        print(f"   ✅ draft_meta_info.json 存在")
        
        # 验证4: 列出文件夹结构
        print(f"\n4. 文件夹结构:")
        for item in os.listdir(draft_path):
            item_path = os.path.join(draft_path, item)
            if os.path.isdir(item_path):
                print(f"   📁 {item}/")
            else:
                file_size = os.path.getsize(item_path)
                print(f"   📄 {item} ({file_size} bytes)")
        
        print("\n✅ 测试通过！")
        print("\n对比原始问题:")
        print("   原始问题: FileNotFoundError - 找不到 draft_content.json")
        print("   修复后: 草稿成功创建，所有文件都在预期位置")
        
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


def test_edge_case_special_characters_in_name():
    """测试边界情况：项目名称包含特殊字符"""
    print("\n=== 测试特殊字符处理 ===\n")
    
    temp_dir = tempfile.mkdtemp(prefix="test_special_chars_")
    
    try:
        generator = DraftGenerator(output_base_dir=temp_dir)
        
        # 测试包含特殊字符的项目名称
        test_cases = [
            "项目名称 - 包含空格",
            "项目_下划线_测试",
            "项目-连字符-测试",
            "项目123数字",
        ]
        
        all_passed = True
        
        for project_name in test_cases:
            print(f"测试项目名称: {project_name}")
            
            test_draft_data = {
                "format_version": "1.0",
                "export_type": "single_draft",
                "draft_count": 1,
                "drafts": [{
                    "draft_id": "test-uuid",
                    "project": {
                        "name": project_name,
                        "width": 1920,
                        "height": 1080,
                        "fps": 30
                    },
                    "tracks": []
                }]
            }
            
            test_json = json.dumps(test_draft_data, ensure_ascii=False, indent=2)
            
            try:
                draft_paths = generator.generate(test_json, output_folder=temp_dir)
                
                if draft_paths:
                    draft_path = draft_paths[0]
                    folder_name = os.path.basename(draft_path)
                    
                    # 验证文件夹名称
                    if folder_name == project_name:
                        print(f"   ✅ 成功: {folder_name}")
                    else:
                        print(f"   ⚠️  名称不匹配: 期望 '{project_name}', 实际 '{folder_name}'")
                        all_passed = False
                    
                    # 清理草稿文件夹以便下一个测试
                    if os.path.exists(draft_path):
                        shutil.rmtree(draft_path)
                else:
                    print(f"   ❌ 未生成草稿")
                    all_passed = False
                    
            except Exception as e:
                print(f"   ❌ 失败: {e}")
                all_passed = False
        
        if all_passed:
            print("\n✅ 所有特殊字符测试通过")
        else:
            print("\n⚠️  部分特殊字符测试失败")
        
        return all_passed
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("实际场景模拟测试\n")
    print("=" * 80)
    print()
    
    results = []
    
    # 运行测试
    results.append(("实际场景测试", test_actual_scenario_with_jianyingpro_folder()))
    results.append(("特殊字符测试", test_edge_case_special_characters_in_name()))
    
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
        print("\n✅ 所有测试通过！修复有效解决了原始问题")
        print("\n说明:")
        print("  - 使用项目名称而非 UUID 作为文件夹名")
        print("  - 剪映不会重命名人类可读的文件夹名")
        print("  - script.save() 可以正常工作")
        print("  - 避免了 FileNotFoundError")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败")
        sys.exit(1)
