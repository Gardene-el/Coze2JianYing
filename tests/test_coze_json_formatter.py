"""
Coze JSON格式化工具测试脚本

演示如何使用 coze_json_formatter.py 工具
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入 scripts 目录中的模块
sys.path.insert(0, str(project_root / "scripts"))
from coze_json_formatter import (
    convert_coze_to_standard_format,
    extract_output_from_coze_file,
    validate_conversion
)


def test_single_file_conversion():
    """测试单文件转换"""
    print("="*60)
    print("测试 1: 单文件转换")
    print("="*60)
    
    input_file = "coze_example_for_paste_context.json"
    
    if not Path(input_file).exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    try:
        # 转换文件
        output_file = convert_coze_to_standard_format(input_file)
        
        # 验证结果
        validate_conversion(input_file, output_file)
        
        print(f"\n✅ 测试通过!")
        print(f"转换后的文件: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extract_output():
    """测试提取 output 字段"""
    print("\n" + "="*60)
    print("测试 2: 提取 output 字段")
    print("="*60)
    
    input_file = "coze_example_for_paste_context.json"
    
    if not Path(input_file).exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    try:
        # 提取并解析 output 字段
        data = extract_output_from_coze_file(input_file)
        
        print(f"\n解析后的数据:")
        print(f"  - format_version: {data.get('format_version')}")
        print(f"  - export_type: {data.get('export_type')}")
        print(f"  - draft_count: {data.get('draft_count')}")
        print(f"  - drafts 数量: {len(data.get('drafts', []))}")
        
        if len(data.get('drafts', [])) > 0:
            draft = data['drafts'][0]
            print(f"\n第一个草稿:")
            print(f"  - draft_id: {draft.get('draft_id')}")
            print(f"  - 项目名称: {draft.get('project', {}).get('name')}")
            print(f"  - 轨道数量: {len(draft.get('tracks', []))}")
        
        print(f"\n✅ 测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_draft_generator():
    """测试与 DraftGenerator 集成"""
    print("\n" + "="*60)
    print("测试 3: 与 DraftGenerator 集成")
    print("="*60)
    
    input_file = "coze_example_for_paste_context.json"
    
    if not Path(input_file).exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    try:
        # 1. 转换文件
        print("\n步骤 1: 转换文件格式")
        converted_file = convert_coze_to_standard_format(input_file)
        print(f"✅ 转换完成: {converted_file}")
        
        # 2. 使用 DraftGenerator 生成草稿
        print("\n步骤 2: 使用 DraftGenerator 生成草稿")
        from src.backend.DraftGenerator.draft_generator import DraftGenerator
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = DraftGenerator(output_base_dir=temp_dir)
            draft_paths = generator.generate_from_file(converted_file)
            
            if draft_paths:
                print(f"✅ 草稿生成成功!")
                print(f"草稿路径: {draft_paths[0]}")
                
                # 检查素材文件夹
                project_id = Path(draft_paths[0]).name
                assets_path = Path(temp_dir) / "CozeJianYingAssistantAssets" / project_id
                
                print(f"\n素材管理:")
                print(f"  - 素材路径: {assets_path}")
                print(f"  - 路径存在: {assets_path.exists()}")
                
                if assets_path.exists():
                    materials = list(assets_path.iterdir())
                    print(f"  - 素材数量: {len(materials)}")
                
                print(f"\n✅ 集成测试通过!")
                return True
            else:
                print("❌ 草稿生成失败")
                return False
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_output_name():
    """测试自定义输出文件名"""
    print("\n" + "="*60)
    print("测试 4: 自定义输出文件名")
    print("="*60)
    
    input_file = "coze_example_for_paste_context.json"
    output_file = "custom_output.json"
    
    if not Path(input_file).exists():
        print(f"❌ 文件不存在: {input_file}")
        return False
    
    try:
        # 使用自定义输出文件名
        result_file = convert_coze_to_standard_format(input_file, output_file)
        
        if Path(result_file).exists():
            print(f"✅ 文件已创建: {result_file}")
            print(f"✅ 测试通过!")
            
            # 清理测试文件
            Path(result_file).unlink()
            print(f"🧹 已清理测试文件")
            
            return True
        else:
            print(f"❌ 文件未创建")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("Coze JSON格式化工具测试")
    print("="*60)
    
    # 切换到项目根目录
    import os
    os.chdir(project_root)
    
    results = []
    
    # 运行测试
    results.append(("单文件转换", test_single_file_conversion()))
    results.append(("提取 output 字段", test_extract_output()))
    results.append(("自定义输出文件名", test_custom_output_name()))
    results.append(("与 DraftGenerator 集成", test_with_draft_generator()))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ 所有测试通过!")
    else:
        print("❌ 部分测试失败")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
