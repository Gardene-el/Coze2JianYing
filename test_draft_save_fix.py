#!/usr/bin/env python3
"""
测试草稿保存修复 - 模拟剪映重命名文件夹的情况
"""
import os
import sys
import tempfile
import shutil
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.draft_generator import DraftGenerator


def test_draft_save_with_folder_rename():
    """测试草稿保存在文件夹被重命名后是否能正常工作"""
    print("=== 测试草稿保存（模拟剪映重命名文件夹）===\n")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"测试目录: {tmpdir}\n")
        
        # 准备测试数据 - 一个简单的草稿配置
        test_data = {
            "drafts": [
                {
                    "draft_id": "test-draft-12345",
                    "project": {
                        "width": 1920,
                        "height": 1080,
                        "fps": 30
                    },
                    "tracks": [
                        {
                            "track_type": "text",
                            "segments": [
                                {
                                    "type": "text",
                                    "content": "测试文本",
                                    "target_timerange": {
                                        "start": 0,
                                        "duration": 3000000
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # 初始化 DraftGenerator
        generator = DraftGenerator(output_base_dir=tmpdir)
        
        # 生成草稿（不模拟重命名）
        print("步骤1: 正常生成草稿")
        try:
            draft_paths = generator._convert_drafts(test_data)
            print(f"✅ 草稿生成成功: {draft_paths[0]}\n")
            
            # 检查文件是否存在
            draft_content_path = os.path.join(draft_paths[0], "draft_content.json")
            if os.path.exists(draft_content_path):
                print(f"✅ draft_content.json 已创建\n")
            else:
                print(f"❌ draft_content.json 未找到\n")
                
        except Exception as e:
            print(f"❌ 草稿生成失败: {e}\n")
            import traceback
            traceback.print_exc()
            return False
        
        # 测试2: 模拟剪映重命名文件夹的情况
        print("\n" + "="*60)
        print("步骤2: 模拟剪映重命名文件夹")
        print("="*60 + "\n")
        
        with tempfile.TemporaryDirectory() as tmpdir2:
            print(f"测试目录: {tmpdir2}\n")
            
            # 初始化新的 DraftGenerator
            generator2 = DraftGenerator(output_base_dir=tmpdir2)
            
            # 准备草稿数据
            draft_id = "my-draft-id"
            original_folder = os.path.join(tmpdir2, draft_id)
            
            print(f"预期草稿文件夹: {original_folder}")
            
            # 开始转换
            test_data2 = {
                "drafts": [
                    {
                        "draft_id": draft_id,
                        "project": {
                            "width": 1920,
                            "height": 1080,
                            "fps": 30
                        },
                        "tracks": [
                            {
                                "track_type": "text",
                                "segments": [
                                    {
                                        "type": "text",
                                        "text": "测试剪映重命名",
                                        "target_timerange": {
                                            "start": 0,
                                            "duration": 5000000
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            
            # 手动创建草稿并模拟重命名
            import pyJianYingDraft as draft
            
            draft_folder_obj = draft.DraftFolder(tmpdir2)
            script = draft_folder_obj.create_draft(draft_id, 1920, 1080, allow_replace=True)
            
            # 保存一次以生成 draft_meta_info.json
            script.save()
            
            # 读取 draft_meta_info.json 中的 draft_id
            meta_info_path = os.path.join(original_folder, "draft_meta_info.json")
            with open(meta_info_path, 'r', encoding='utf-8') as f:
                meta_info = json.load(f)
            
            jianyingpro_draft_id = meta_info.get('draft_id', '')
            print(f"剪映内部 draft_id: {jianyingpro_draft_id}")
            
            # 模拟剪映重命名文件夹
            renamed_folder = os.path.join(tmpdir2, jianyingpro_draft_id)
            print(f"模拟重命名为: {renamed_folder}\n")
            shutil.move(original_folder, renamed_folder)
            
            # 删除 draft_content.json 以模拟还未保存的状态
            content_path = os.path.join(renamed_folder, "draft_content.json")
            if os.path.exists(content_path):
                os.remove(content_path)
                print("已删除 draft_content.json (模拟未保存状态)\n")
            
            # 现在测试我们的健壮保存方法
            print("测试健壮保存方法...")
            try:
                # 添加一些内容到 script
                script.add_track(draft.TrackType.text, "test_track")
                
                # 使用健壮保存方法
                actual_folder = generator2._save_draft_robust(script, original_folder, draft_id)
                
                print(f"\n✅ 保存成功!")
                print(f"实际保存路径: {actual_folder}")
                
                # 验证文件是否存在
                final_content_path = os.path.join(actual_folder, "draft_content.json")
                if os.path.exists(final_content_path):
                    print(f"✅ draft_content.json 已成功创建在重命名后的文件夹中\n")
                    
                    # 读取并验证内容
                    with open(final_content_path, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                    print(f"✅ draft_content.json 内容有效 (包含 {len(content)} 个键)\n")
                    return True
                else:
                    print(f"❌ draft_content.json 未找到\n")
                    return False
                    
            except Exception as e:
                print(f"❌ 健壮保存失败: {e}\n")
                import traceback
                traceback.print_exc()
                return False


if __name__ == "__main__":
    success = test_draft_save_with_folder_rename()
    
    print("\n" + "="*60)
    if success:
        print("✅ 所有测试通过!")
    else:
        print("❌ 测试失败")
    print("="*60)
    
    sys.exit(0 if success else 1)
