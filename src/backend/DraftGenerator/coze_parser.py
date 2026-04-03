"""
Coze输出解析器
用于解析从Coze Draft Generator Interface粘贴的JSON内容
"""

import json
import hashlib
from typing import Dict, List, Any, Optional
from src.backend.utils.logger import logger


def parse_coze_output(input_source: str, is_file: bool = False) -> Dict[str, Any]:
    """
    解析Coze输出

    Args:
        input_source: 剪贴板文本或文件路径
        is_file: 是否为文件路径

    Returns:
        解析后的草稿数据字典

    Raises:
        ValueError: 如果解析失败
    """
    if is_file:
        return _parse_from_file(input_source)
    return _parse_from_text(input_source)


def normalize_draft_data(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    标准化解析的数据，转换为 DraftGenerator 期望的格式

    Args:
        parsed_data: parse_coze_output 返回的数据

    Returns:
        标准化后的数据字典（不修改原始数据）
    """
    normalized = parsed_data.copy()
    normalized['drafts'] = [dict(d) for d in parsed_data.get('drafts', [])]
    for draft in normalized['drafts']:
        _normalize_draft(draft)
    return normalized


def print_draft_summary(parsed_data: Dict[str, Any]) -> None:
    """打印解析摘要"""
    logger.info("=" * 60)
    logger.info("输入内容解析摘要")
    logger.info("=" * 60)
    logger.info(f"格式版本: {parsed_data.get('format_version', 'N/A')}")
    logger.info(f"导出类型: {parsed_data.get('export_type', '')}")
    drafts = parsed_data.get('drafts', [])
    logger.info(f"草稿数量: {len(drafts)}")
    logger.info("")

    for i, draft in enumerate(drafts, 1):
        info = _get_draft_info(draft)
        logger.info(f"草稿 {i}:")
        logger.info(f"  ID: {info['draft_id']}")
        logger.info(f"  项目名称: {info['project_name']}")
        logger.info(f"  分辨率: {info['resolution']}")
        logger.info(f"  帧率: {info['fps']} fps")
        logger.info(f"  轨道数量: {info['track_count']}")
        logger.info(f"  轨道类型: {info['track_stats']}")
        logger.info(f"  总片段数: {info['total_segments']}")
        logger.info(f"  状态: {info['status']}")
        logger.info("")

    logger.info("=" * 60)


# ========== 私有函数 ==========

def _parse_from_text(text: str) -> Dict[str, Any]:
    try:
        parsed_json = json.loads(text)
        logger.info("成功解析JSON内容")
        return _detect_and_parse_format(parsed_json)
    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        raise ValueError(f"无效的JSON格式: {e}")
    except Exception as e:
        logger.error(f"解析过程出错: {e}")
        raise ValueError(f"解析失败: {e}")


def _parse_from_file(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"成功读取文件: {file_path}")
        return _parse_from_text(content)
    except FileNotFoundError:
        logger.error(f"文件不存在: {file_path}")
        raise ValueError(f"文件不存在: {file_path}")
    except Exception as e:
        logger.error(f"读取文件失败: {e}")
        raise ValueError(f"读取文件失败: {e}")


def _detect_and_parse_format(parsed_json: Dict[str, Any]) -> Dict[str, Any]:
    if 'output' in parsed_json:
        logger.info("检测到Coze输出格式")
        return _parse_coze_output_format(parsed_json)
    elif 'drafts' in parsed_json and isinstance(parsed_json['drafts'], list):
        logger.info("检测到标准剪映草稿格式")
        return _parse_standard_draft_format(parsed_json)
    elif 'tracks' in parsed_json:
        logger.info("检测到单个草稿对象格式")
        return _parse_single_draft_format(parsed_json)
    else:
        logger.info("尝试智能推断格式")
        return _parse_unknown_format(parsed_json)


def _parse_coze_output_format(outer_json: Dict[str, Any]) -> Dict[str, Any]:
    raw_output = outer_json.get('output')
    if not raw_output:
        raise ValueError("output字段为空")
    inner_json = json.loads(raw_output)
    logger.info("成功解析Coze输出格式的内层JSON")
    return inner_json


def _parse_standard_draft_format(draft_data: Dict[str, Any]) -> Dict[str, Any]:
    drafts = draft_data['drafts']
    if not isinstance(drafts, list):
        raise ValueError("'drafts'字段必须是数组")
    if not drafts:
        raise ValueError("'drafts'数组为空")
    result = {
        'format_version': draft_data.get('format_version', '1.0'),
        'export_type': draft_data.get('export_type', 'single_draft' if len(drafts) == 1 else 'multiple_drafts'),
        'draft_count': draft_data.get('draft_count', len(drafts)),
        'drafts': drafts
    }
    logger.info(f"成功解析标准草稿格式，包含 {len(drafts)} 个草稿")
    return result


def _parse_single_draft_format(draft_object: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        'format_version': '1.0',
        'export_type': 'single_draft',
        'draft_count': 1,
        'drafts': [draft_object]
    }
    logger.info("成功解析单个草稿对象格式")
    return result


def _parse_unknown_format(data: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in data.items():
        if isinstance(value, list) and value:
            first_item = value[0]
            if isinstance(first_item, dict) and ('tracks' in first_item or 'project' in first_item):
                logger.info(f"在'{key}'字段中发现可能的草稿列表")
                return {
                    'format_version': '1.0',
                    'export_type': 'single_draft' if len(value) == 1 else 'multiple_drafts',
                    'draft_count': len(value),
                    'drafts': value
                }
    available_keys = list(data.keys())
    raise ValueError(
        f"无法识别的输入格式。\n"
        f"支持的格式:\n"
        f"1. Coze输出格式 (包含'output'字段)\n"
        f"2. 标准剪映草稿格式 (包含'drafts'数组)\n"
        f"3. 单个草稿对象 (包含'tracks'字段)\n"
        f"当前输入包含字段: {available_keys}"
    )


def _get_draft_info(draft_data: Dict[str, Any]) -> Dict[str, Any]:
    project = draft_data.get('project', {})
    tracks = draft_data.get('tracks', [])
    track_stats: Dict[str, int] = {}
    for track in tracks:
        track_type = track.get('track_type', 'unknown')
        track_stats[track_type] = track_stats.get(track_type, 0) + 1
    total_segments = sum(len(track.get('segments', [])) for track in tracks)
    return {
        'draft_id': draft_data.get('draft_id', ''),
        'project_name': project.get('name', ''),
        'resolution': f"{project.get('width', 0)}x{project.get('height', 0)}",
        'fps': project.get('fps', 30),
        'track_count': len(tracks),
        'track_stats': track_stats,
        'total_segments': total_segments,
        'status': draft_data.get('status', 'unknown')
    }


def _normalize_draft(draft: Dict[str, Any]) -> None:
    for track in draft.get('tracks', []):
        for segment in track.get('segments', []):
            if 'type' in segment:
                segment['segment_type'] = segment['type']
            time_range = segment.get('time_range', {})
            if 'start' in time_range and 'end' in time_range:
                segment['duration_ms'] = time_range['end'] - time_range['start']
            if 'material_url' in segment:
                material_url = segment['material_url']
                file_name = _generate_filename_from_url(
                    material_url, segment.get('segment_type', 'unknown')
                )
                segment['material'] = {'url': material_url, 'file_name': file_name}


def _generate_filename_from_url(url: str, segment_type: str) -> str:
    if not url:
        return f"material_{segment_type}"
    if 's.coze.cn/t/' in url:
        path_part = url.split('/t/')[-1].rstrip('/')
        if segment_type == 'image':
            return f"{path_part}.png"
        elif segment_type == 'video':
            return f"{path_part}.mp4"
    elif 'speech_' in url:
        speech_id = url.split('speech_')[1].split('_')[0]
        return f"speech_{speech_id}.mp3"
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    ext_map = {'audio': '.mp3', 'image': '.png', 'video': '.mp4', 'text': '.txt'}
    ext = ext_map.get(segment_type, '.bin')
    return f"material_{url_hash}{ext}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        try:
            parsed = parse_coze_output(sys.argv[1], is_file=True)
            print_draft_summary(parsed)
        except ValueError as e:
            print(f"解析失败: {e}")
