""""""

测试 Coze 输出转换器Coze 输出格式转换工具测试脚本



这个脚本用于测试 coze_output_converter.py 的功能演示如何使用 coze_output_converter.py 工具

""""""

import sys

import sysfrom pathlib import Path

from pathlib import Path

# 添加项目根目录到路径

# 添加项目根目录到 Python 路径project_root = Path(__file__).parent.parent

project_root = Path(__file__).parent.parentsys.path.insert(0, str(project_root))

sys.path.insert(0, str(project_root))

from test_utils.coze_output_converter import (

from test_utils.converters.coze_output_converter import (    convert_coze_to_standard_format,

    convert_coze_to_standard_format,    extract_output_from_coze_file,

    extract_output_from_coze_file,    validate_conversion

    validate_conversion)

)



def test_single_file_conversion():

def test_extract_output():    """测试单文件转换"""

    """测试提取 output 字段"""    print("="*60)

    print("\n=== 测试提取 output 字段 ===")    print("测试 1: 单文件转换")

        print("="*60)

    # 使用示例文件    

    input_file = project_root / "coze_example_for_paste_context.json"    input_file = "coze_example_for_paste_context.json"

        

    if not input_file.exists():    if not Path(input_file).exists():

        print(f"❌ 测试文件不存在: {input_file}")        print(f"❌ 文件不存在: {input_file}")

        return False        return False

        

    try:    try:

        extracted_data = extract_output_from_coze_file(str(input_file))        # 转换文件

        print(f"✅ 成功提取 output 字段")        output_file = convert_coze_to_standard_format(input_file)

        print(f"   提取的数据类型: {type(extracted_data)}")        

                # 验证结果

        # 检查是否有必需的字段        validate_conversion(input_file, output_file)

        if isinstance(extracted_data, dict):        

            if "materials" in extracted_data:        print(f"\n✅ 测试通过!")

                print(f"   包含 materials 字段")        print(f"转换后的文件: {output_file}")

            if "tracks" in extracted_data:        return True

                print(f"   包含 tracks 字段")        

            except Exception as e:

        return True        print(f"❌ 测试失败: {e}")

    except Exception as e:        import traceback

        print(f"❌ 提取失败: {e}")        traceback.print_exc()

        return False        return False





def test_convert():def test_extract_output():

    """测试完整转换"""    """测试提取 output 字段"""

    print("\n=== 测试完整转换 ===")    print("\n" + "="*60)

        print("测试 2: 提取 output 字段")

    input_file = project_root / "coze_example_for_paste_context.json"    print("="*60)

    output_file = project_root / "test_converted_output.json"    

        input_file = "coze_example_for_paste_context.json"

    if not input_file.exists():    

        print(f"❌ 测试文件不存在: {input_file}")    if not Path(input_file).exists():

        return False        print(f"❌ 文件不存在: {input_file}")

            return False

    try:    

        result = convert_coze_to_standard_format(    try:

            str(input_file),        # 提取并解析 output 字段

            str(output_file)        data = extract_output_from_coze_file(input_file)

        )        

                print(f"\n解析后的数据:")

        if result:        print(f"  - format_version: {data.get('format_version')}")

            print(f"✅ 转换成功")        print(f"  - export_type: {data.get('export_type')}")

            print(f"   输出文件: {output_file}")        print(f"  - draft_count: {data.get('draft_count')}")

                    print(f"  - drafts 数量: {len(data.get('drafts', []))}")

            # 验证转换结果        

            if validate_conversion(str(output_file)):        if len(data.get('drafts', [])) > 0:

                print(f"✅ 转换结果验证通过")            draft = data['drafts'][0]

                return True            print(f"\n第一个草稿:")

            else:            print(f"  - draft_id: {draft.get('draft_id')}")

                print(f"⚠️ 转换结果验证失败")            print(f"  - 项目名称: {draft.get('project', {}).get('name')}")

                return False            print(f"  - 轨道数量: {len(draft.get('tracks', []))}")

        else:        

            print(f"❌ 转换失败")        print(f"\n✅ 测试通过!")

            return False        return True

                    

    except Exception as e:    except Exception as e:

        print(f"❌ 转换失败: {e}")        print(f"❌ 测试失败: {e}")

        import traceback        import traceback

        traceback.print_exc()        traceback.print_exc()

        return False        return False





def test_validate():def test_with_draft_generator():

    """测试验证功能"""    """测试与 DraftGenerator 集成"""

    print("\n=== 测试验证功能 ===")    print("\n" + "="*60)

        print("测试 3: 与 DraftGenerator 集成")

    # 测试标准格式文件    print("="*60)

    sample_file = project_root / "sample.json"    

        input_file = "coze_example_for_paste_context.json"

    if sample_file.exists():    

        if validate_conversion(str(sample_file)):    if not Path(input_file).exists():

            print(f"✅ sample.json 验证通过")        print(f"❌ 文件不存在: {input_file}")

        else:        return False

            print(f"⚠️ sample.json 验证失败")    

    else:    try:

        print(f"⚠️ sample.json 不存在")        # 1. 转换文件

            print("\n步骤 1: 转换文件格式")

    # 测试 Coze 格式文件(应该失败)        converted_file = convert_coze_to_standard_format(input_file)

    coze_file = project_root / "coze_example_for_paste_context.json"        print(f"✅ 转换完成: {converted_file}")

            

    if coze_file.exists():        # 2. 使用 DraftGenerator 生成草稿

        if not validate_conversion(str(coze_file)):        print("\n步骤 2: 使用 DraftGenerator 生成草稿")

            print(f"✅ Coze 格式文件正确被识别为非标准格式")        from src.utils.draft_generator import DraftGenerator

        else:        import tempfile

            print(f"⚠️ Coze 格式文件被错误识别为标准格式")        

            with tempfile.TemporaryDirectory() as temp_dir:

    return True            generator = DraftGenerator(output_base_dir=temp_dir)

            draft_paths = generator.generate_from_file(converted_file)

            

def main():            if draft_paths:

    """运行所有测试"""                print(f"✅ 草稿生成成功!")

    print("=" * 60)                print(f"草稿路径: {draft_paths[0]}")

    print("开始测试 Coze 输出转换器")                

    print("=" * 60)                # 检查素材文件夹

                    project_id = Path(draft_paths[0]).name

    results = []                assets_path = Path(temp_dir) / "CozeJianYingAssistantAssets" / project_id

                    

    # 运行测试                print(f"\n素材管理:")

    results.append(("提取 output 字段", test_extract_output()))                print(f"  - 素材路径: {assets_path}")

    results.append(("完整转换", test_convert()))                print(f"  - 路径存在: {assets_path.exists()}")

    results.append(("验证功能", test_validate()))                

                    if assets_path.exists():

    # 显示总结                    materials = list(assets_path.iterdir())

    print("\n" + "=" * 60)                    print(f"  - 素材数量: {len(materials)}")

    print("测试总结")                

    print("=" * 60)                print(f"\n✅ 集成测试通过!")

                    return True

    for test_name, result in results:            else:

        status = "✅ 通过" if result else "❌ 失败"                print("❌ 草稿生成失败")

        print(f"{status} - {test_name}")                return False

                    

    # 总体结果    except Exception as e:

    total = len(results)        print(f"❌ 测试失败: {e}")

    passed = sum(1 for _, result in results if result)        import traceback

            traceback.print_exc()

    print(f"\n总计: {passed}/{total} 测试通过")        return False

    

    if passed == total:

        print("\n🎉 所有测试通过!")def test_custom_output_name():

        return 0    """测试自定义输出文件名"""

    else:    print("\n" + "="*60)

        print(f"\n⚠️ {total - passed} 个测试失败")    print("测试 4: 自定义输出文件名")

        return 1    print("="*60)

    

    input_file = "coze_example_for_paste_context.json"

if __name__ == "__main__":    output_file = "custom_output.json"

    sys.exit(main())    

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
    print("Coze 输出格式转换工具测试")
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
