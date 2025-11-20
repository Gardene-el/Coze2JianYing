#!/usr/bin/env python3
"""
测试 add_* 函数 handler 中的 ID 提取功能
验证所有返回 ID 的函数都正确生成了 ID 提取代码
"""

import ast
from pathlib import Path
from typing import Dict, List, Tuple


def extract_id_extraction_code(handler_path: Path) -> List[str]:
    """
    从 handler.py 中提取 ID 提取代码
    例如：effect_{generated_uuid} = resp_{generated_uuid}.effect_id
    
    Returns:
        提取到的 ID 变量名列表（如 ['effect']）
    """
    try:
        with open(handler_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找所有形如 "xxx_{generated_uuid} = resp_{generated_uuid}.xxx_id" 的行
        # 这些行在 f-string 内部，作为字符串的一部分
        extracted_ids = []
        
        # 搜索模式：{id_type}_{generated_uuid} = resp_{generated_uuid}.{id_field}
        import re
        # 匹配形如 "effect_{generated_uuid} = resp_{generated_uuid}.effect_id" 的行
        pattern = r'(\w+)_\{generated_uuid\}\s*=\s*resp_\{generated_uuid\}\.(\w+)_id'
        matches = re.findall(pattern, content)
        
        for match in matches:
            id_type = match[0]  # 例如 'effect', 'keyframe', 'draft' 等
            id_field = match[1]  # 例如 'effect', 'keyframe', 'draft' 等
            # 验证它们是匹配的（effect_{uuid} = resp_{uuid}.effect_id）
            if id_type == id_field:
                extracted_ids.append(id_type)
        
        return extracted_ids
    
    except Exception as e:
        print(f"错误: 无法解析 {handler_path}: {e}")
        return []


def get_expected_id_for_function(func_name: str) -> str | None:
    """
    根据函数名返回期望提取的 ID 类型
    
    Returns:
        期望的 ID 类型（如 'effect', 'keyframe'），如果不应该提取 ID 则返回 None
    """
    # 定义哪些函数应该提取哪种 ID
    id_mapping = {
        # create 函数
        'create_draft': 'draft',
        'create_audio_segment': 'segment',
        'create_video_segment': 'segment',
        'create_text_segment': 'segment',
        'create_sticker_segment': 'segment',
        'create_effect_segment': 'segment',
        'create_filter_segment': 'segment',
        
        # add_* 函数返回特定的 ID
        'add_audio_effect': 'effect',
        'add_audio_keyframe': 'keyframe',
        'add_video_animation': 'animation',
        'add_video_effect': 'effect',
        'add_video_filter': 'filter',
        'add_video_keyframe': 'keyframe',
        'add_video_mask': 'mask',
        'add_video_transition': 'transition',
        'add_sticker_keyframe': 'keyframe',
        'add_text_animation': 'animation',
        'add_text_bubble': 'bubble',
        'add_text_effect': 'effect',
        'add_text_keyframe': 'keyframe',
        'add_global_effect': 'effect',
        'add_global_filter': 'filter',
        
        # 以下函数不返回可引用的 ID
        'add_track': None,  # 返回 track_index 而不是 track_id
        'add_segment': None,  # 用于将现有 segment 添加到 track
        'add_audio_fade': None,  # 不返回 ID，直接修改 segment
        'add_video_fade': None,  # 不返回 ID，直接修改 segment
        'add_video_background_filling': None,  # 不返回 ID，直接修改 segment
        'save_draft': None,  # 保存操作，不返回新 ID
    }
    
    return id_mapping.get(func_name)


def test_id_extraction(raw_tools_dir: Path) -> Dict:
    """
    测试所有 add_* 和 create_* 函数的 ID 提取
    
    Returns:
        测试结果字典
    """
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    # 遍历所有工具目录
    tool_dirs = [d for d in raw_tools_dir.iterdir() if d.is_dir()]
    
    for tool_dir in sorted(tool_dirs):
        tool_name = tool_dir.name
        handler_path = tool_dir / 'handler.py'
        
        # 跳过 make_* 工具（它们是辅助工具，不需要 ID 提取）
        if tool_name.startswith('make_'):
            continue
        
        # 检查 handler.py 是否存在
        if not handler_path.exists():
            continue
        
        results['total'] += 1
        
        # 获取期望的 ID 类型
        expected_id = get_expected_id_for_function(tool_name)
        
        # 提取实际的 ID
        extracted_ids = extract_id_extraction_code(handler_path)
        
        print(f"\n测试工具: {tool_name}")
        print(f"  期望 ID: {expected_id}")
        print(f"  实际 ID: {extracted_ids}")
        
        # 验证结果
        if expected_id is None:
            # 不应该有 ID 提取
            if len(extracted_ids) == 0:
                results['passed'] += 1
                results['details'].append({
                    'tool': tool_name,
                    'status': 'passed',
                    'expected': None,
                    'actual': extracted_ids
                })
                print(f"  ✅ 正确：不需要提取 ID")
            else:
                results['failed'] += 1
                results['details'].append({
                    'tool': tool_name,
                    'status': 'failed',
                    'expected': None,
                    'actual': extracted_ids,
                    'reason': f'不应该提取 ID，但提取了: {extracted_ids}'
                })
                print(f"  ❌ 错误：不应该提取 ID，但提取了: {extracted_ids}")
        else:
            # 应该有 ID 提取
            if expected_id in extracted_ids:
                results['passed'] += 1
                results['details'].append({
                    'tool': tool_name,
                    'status': 'passed',
                    'expected': expected_id,
                    'actual': extracted_ids
                })
                print(f"  ✅ 正确：成功提取 {expected_id}_id")
            else:
                results['failed'] += 1
                results['details'].append({
                    'tool': tool_name,
                    'status': 'failed',
                    'expected': expected_id,
                    'actual': extracted_ids,
                    'reason': f'期望提取 {expected_id}_id，但实际提取了: {extracted_ids}'
                })
                print(f"  ❌ 错误：期望提取 {expected_id}_id，但实际提取了: {extracted_ids}")
    
    return results


def print_summary(results: Dict):
    """打印测试总结"""
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总计: {results['total']} 个工具")
    print(f"通过: {results['passed']} 个")
    print(f"失败: {results['failed']} 个")
    
    if results['total'] > 0:
        print(f"成功率: {results['passed']/results['total']*100:.1f}%")
    
    if results['failed'] > 0:
        print("\n失败的工具:")
        for detail in results['details']:
            if detail['status'] == 'failed':
                reason = detail.get('reason', '未知错误')
                print(f"  - {detail['tool']}: {reason}")
    
    print("=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("测试 add_* 函数的 ID 提取功能")
    print("=" * 60)
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    raw_tools_dir = project_root / 'coze_plugin' / 'raw_tools'
    
    print(f"\n项目根目录: {project_root}")
    print(f"Raw Tools 目录: {raw_tools_dir}")
    
    # 检查目录是否存在
    if not raw_tools_dir.exists():
        print(f"\n错误: {raw_tools_dir} 目录不存在")
        print("请先运行 generate_handler_from_api.py 生成 handler 文件")
        return 1
    
    # 运行测试
    results = test_id_extraction(raw_tools_dir)
    
    # 打印总结
    print_summary(results)
    
    # 返回适当的退出代码
    return 0 if results['failed'] == 0 else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
