"""
Coze JSON 格式化工具

用于将 Coze 输出的特殊格式（包含 output 字段的字符串 JSON）
转换为标准的 JSON 格式，便于剪映草稿生成器使用。

功能：
- 从 Coze 输出文件中提取并解析 output 字段
- 将字符串形式的 JSON 转换为标准 JSON 对象
- 支持单文件转换和批量转换
- 提供格式验证功能

使用方式：
  命令行：
    python scripts/coze_json_formatter.py <input_file> [output_file]
    python scripts/coze_json_formatter.py --batch [directory] [pattern]
  
  Python 模块：
    from coze_json_formatter import convert_coze_to_standard_format
    output = convert_coze_to_standard_format('input.json')
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any


def extract_output_from_coze_file(input_file: str) -> Dict[str, Any]:
    """
    从 Coze 输出文件中提取并解析 output 字段
    
    Args:
        input_file: 输入文件路径（coze_example_for_paste_context.json 格式）
        
    Returns:
        解析后的 JSON 数据（标准格式）
        
    Raises:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON 解析失败
        KeyError: 缺少 output 字段
    """
    print(f"读取文件: {input_file}")
    
    # 读取原始文件
    with open(input_file, 'r', encoding='utf-8') as f:
        coze_data = json.load(f)
    
    # 检查是否有 output 字段
    if 'output' not in coze_data:
        raise KeyError("文件中未找到 'output' 字段")
    
    # 提取并解析 output 字段
    output_str = coze_data['output']
    print(f"output 字段长度: {len(output_str)} 字符")
    
    # 解析 output 字符串为 JSON
    output_data = json.loads(output_str)
    print(f"✅ 成功解析 output 字段")
    
    return output_data


def convert_coze_to_standard_format(input_file: str, output_file: str | None = None) -> str:
    """
    将 Coze 输出文件转换为标准格式
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径（可选，默认为 input_file_converted.json）
        
    Returns:
        输出文件路径
        
    Example:
        >>> convert_coze_to_standard_format('coze_example_for_paste_context.json')
        'coze_example_for_paste_context_converted.json'
    """
    # 提取并解析数据
    standard_data = extract_output_from_coze_file(input_file)
    
    # 确定输出文件路径
    if output_file is None:
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_converted.json")
    
    # 保存为格式化的 JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(standard_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存到: {output_file}")
    
    return output_file


def validate_conversion(input_file: str, output_file: str):
    """
    验证转换结果
    
    Args:
        input_file: 原始输入文件
        output_file: 转换后的输出文件
    """
    print("\n" + "="*60)
    print("验证转换结果")
    print("="*60)
    
    # 读取转换后的文件
    with open(output_file, 'r', encoding='utf-8') as f:
        converted_data = json.load(f)
    
    # 检查基本结构
    checks = [
        ('format_version', 'format_version' in converted_data),
        ('export_type', 'export_type' in converted_data),
        ('draft_count', 'draft_count' in converted_data),
        ('drafts', 'drafts' in converted_data),
    ]
    
    all_passed = True
    for field_name, check_result in checks:
        status = "✅" if check_result else "❌"
        print(f"{status} {field_name}: {'存在' if check_result else '缺失'}")
        if not check_result:
            all_passed = False
    
    if all_passed and len(converted_data.get('drafts', [])) > 0:
        draft = converted_data['drafts'][0]
        print(f"\n草稿信息:")
        print(f"  - draft_id: {draft.get('draft_id', '未知')}")
        print(f"  - 项目名称: {draft.get('project', {}).get('name', '未知')}")
        print(f"  - 分辨率: {draft.get('project', {}).get('width', 0)}x{draft.get('project', {}).get('height', 0)}")
        print(f"  - 轨道数量: {len(draft.get('tracks', []))}")
        
        # 统计每个轨道的片段数量
        for i, track in enumerate(draft.get('tracks', []), 1):
            track_type = track.get('track_type', '未知')
            segment_count = len(track.get('segments', []))
            print(f"    轨道 {i} ({track_type}): {segment_count} 个片段")
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ 验证通过! 转换成功!")
    else:
        print("❌ 验证失败，请检查输出文件")
    print("="*60)


def batch_convert(input_dir: str = ".", pattern: str = "*coze*.json", output_suffix: str = "_converted"):
    """
    批量转换目录中的所有 Coze 输出文件
    
    Args:
        input_dir: 输入目录
        pattern: 文件匹配模式
        output_suffix: 输出文件后缀
    """
    input_path = Path(input_dir)
    files = list(input_path.glob(pattern))
    
    if not files:
        print(f"在 {input_dir} 中未找到匹配 '{pattern}' 的文件")
        return
    
    print(f"找到 {len(files)} 个文件:")
    for f in files:
        print(f"  - {f.name}")
    
    print("\n开始批量转换...")
    
    success_count = 0
    for input_file in files:
        try:
            # 跳过已经转换过的文件
            if output_suffix in input_file.stem:
                print(f"⏭️  跳过已转换文件: {input_file.name}")
                continue
            
            print(f"\n处理: {input_file.name}")
            output_file = str(input_file.parent / f"{input_file.stem}{output_suffix}.json")
            convert_coze_to_standard_format(str(input_file), output_file)
            success_count += 1
        except Exception as e:
            print(f"❌ 转换失败: {e}")
    
    print(f"\n批量转换完成: {success_count}/{len(files)} 个文件转换成功")


def main():
    """命令行入口"""
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print("用法:")
        print("  python scripts/coze_json_formatter.py <input_file> [output_file]")
        print("  python scripts/coze_json_formatter.py --batch [directory] [pattern]")
        print("\n示例:")
        print("  python scripts/coze_json_formatter.py coze_example_for_paste_context.json")
        print("  python scripts/coze_json_formatter.py coze_example.json output.json")
        print("  python scripts/coze_json_formatter.py --batch . '*coze*.json'")
        print("\n说明:")
        print("  此工具用于将 Coze 输出格式（包含 output 字段的字符串 JSON）")
        print("  转换为标准 JSON 格式，供剪映草稿生成器使用。")
        return
    
    if sys.argv[1] == '--batch':
        # 批量转换模式
        input_dir = sys.argv[2] if len(sys.argv) > 2 else "."
        pattern = sys.argv[3] if len(sys.argv) > 3 else "*coze*.json"
        batch_convert(input_dir, pattern)
    else:
        # 单文件转换模式
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        try:
            result_file = convert_coze_to_standard_format(input_file, output_file)
            validate_conversion(input_file, result_file)
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
