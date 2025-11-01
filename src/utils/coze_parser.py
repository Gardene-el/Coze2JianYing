"""
Coze输出解析器
用于解析从Coze Draft Generator Interface粘贴的JSON内容
"""

import json
from typing import Dict, List, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class CozeOutputParser:
    """解析Coze输出的工具类"""
    
    def __init__(self):
        """初始化解析器"""
        self.parsed_data: Optional[Dict[str, Any]] = None
        self.raw_output: Optional[str] = None
    
    def parse_from_clipboard(self, clipboard_text: str) -> Dict[str, Any]:
        """
        从剪贴板文本解析多种格式的输入内容
        支持格式:
        1. Coze输出格式 (包含output字段)
        2. 标准剪映草稿格式 (包含drafts数组)
        3. 其他自定义格式
        
        Args:
            clipboard_text: 从剪贴板粘贴的文本内容
            
        Returns:
            解析后的草稿数据字典
            
        Raises:
            ValueError: 如果解析失败
        """
        try:
            # 第一层解析:获取外层JSON
            parsed_json = json.loads(clipboard_text)
            logger.info("成功解析JSON内容")
            
            # 智能识别输入格式
            result = self._detect_and_parse_format(parsed_json, clipboard_text)
            
            self.parsed_data = result
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            raise ValueError(f"无效的JSON格式: {e}")
        except Exception as e:
            logger.error(f"解析过程出错: {e}")
            raise ValueError(f"解析失败: {e}")
    
    def _detect_and_parse_format(self, parsed_json: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """
        检测并解析输入格式
        
        Args:
            parsed_json: 已解析的JSON对象
            original_text: 原始文本内容
            
        Returns:
            标准化后的草稿数据字典
        """
        # 格式1: Coze输出格式 (包含output字段)
        if 'output' in parsed_json:
            logger.info("检测到Coze输出格式")
            return self._parse_coze_output_format(parsed_json)
        
        # 格式2: 标准剪映草稿格式 (包含drafts数组)
        elif 'drafts' in parsed_json and isinstance(parsed_json['drafts'], list):
            logger.info("检测到标准剪映草稿格式")
            return self._parse_standard_draft_format(parsed_json)
        
        # 格式3: 单个草稿对象 (包含tracks等字段)
        elif 'tracks' in parsed_json:
            logger.info("检测到单个草稿对象格式")
            return self._parse_single_draft_format(parsed_json)
        
        # 格式4: 其他可能的格式，尝试智能推断
        else:
            logger.info("尝试智能推断格式")
            return self._parse_unknown_format(parsed_json)
    
    def _parse_coze_output_format(self, outer_json: Dict[str, Any]) -> Dict[str, Any]:
        """解析Coze输出格式"""
        if 'output' not in outer_json:
            raise ValueError("JSON中缺少'output'字段")
        
        self.raw_output = outer_json['output']
        if not self.raw_output:
            raise ValueError("output字段为空")
        
        inner_json = json.loads(self.raw_output)
        logger.info("成功解析Coze输出格式的内层JSON")
        return inner_json
    
    def _parse_standard_draft_format(self, draft_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析标准剪映草稿格式"""
        # 验证必要字段
        if 'drafts' not in draft_data:
            raise ValueError("标准草稿格式中缺少'drafts'字段")
        
        drafts = draft_data['drafts']
        if not isinstance(drafts, list):
            raise ValueError("'drafts'字段必须是数组")
        
        if not drafts:
            raise ValueError("'drafts'数组为空")
        
        # 标准化格式，确保包含必要的元信息
        result = {
            'format_version': draft_data.get('format_version', '1.0'),
            'export_type': draft_data.get('export_type', 'single_draft' if len(drafts) == 1 else 'multiple_drafts'),
            'draft_count': draft_data.get('draft_count', len(drafts)),
            'drafts': drafts
        }
        
        logger.info(f"成功解析标准草稿格式，包含 {len(drafts)} 个草稿")
        return result
    
    def _parse_single_draft_format(self, draft_object: Dict[str, Any]) -> Dict[str, Any]:
        """解析单个草稿对象格式"""
        # 将单个草稿对象包装成标准格式
        result = {
            'format_version': '1.0',
            'export_type': 'single_draft',
            'draft_count': 1,
            'drafts': [draft_object]
        }
        
        logger.info("成功解析单个草稿对象格式")
        return result
    
    def _parse_unknown_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """尝试解析未知格式"""
        # 检查是否可能是草稿列表的变体
        for key, value in data.items():
            if isinstance(value, list) and value:
                # 检查列表中的元素是否像草稿对象
                first_item = value[0]
                if isinstance(first_item, dict) and ('tracks' in first_item or 'project' in first_item):
                    logger.info(f"在'{key}'字段中发现可能的草稿列表")
                    result = {
                        'format_version': '1.0',
                        'export_type': 'single_draft' if len(value) == 1 else 'multiple_drafts',
                        'draft_count': len(value),
                        'drafts': value
                    }
                    return result
        
        # 如果都不匹配，抛出错误
        available_keys = list(data.keys())
        raise ValueError(f"无法识别的输入格式。\n"
                        f"支持的格式:\n"
                        f"1. Coze输出格式 (包含'output'字段)\n"
                        f"2. 标准剪映草稿格式 (包含'drafts'数组)\n"
                        f"3. 单个草稿对象 (包含'tracks'字段)\n"
                        f"当前输入包含字段: {available_keys}")
    
    def parse_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        从文件解析Coze输出
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            解析后的草稿数据字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"成功读取文件: {file_path}")
            return self.parse_from_clipboard(content)
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
            raise ValueError(f"文件不存在: {file_path}")
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            raise ValueError(f"读取文件失败: {e}")
    
    def get_draft_count(self) -> int:
        """获取草稿数量"""
        if not self.parsed_data:
            return 0
        return self.parsed_data.get('draft_count', 0)
    
    def get_export_type(self) -> str:
        """获取导出类型 (single_draft 或 multiple_drafts)"""
        if not self.parsed_data:
            return ""
        return self.parsed_data.get('export_type', "")
    
    def get_drafts(self) -> List[Dict[str, Any]]:
        """
        获取所有草稿列表
        
        Returns:
            草稿字典列表
        """
        if not self.parsed_data:
            return []
        return self.parsed_data.get('drafts', [])
    
    def get_draft_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """
        根据索引获取特定草稿
        
        Args:
            index: 草稿索引(从0开始)
            
        Returns:
            草稿字典,如果索引无效则返回None
        """
        drafts = self.get_drafts()
        if 0 <= index < len(drafts):
            return drafts[index]
        return None
    
    def get_draft_info(self, draft: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取草稿基本信息
        
        Args:
            draft: 草稿字典,如果为None则使用第一个草稿
            
        Returns:
            包含草稿基本信息的字典
        """
        if draft is None:
            draft = self.get_draft_by_index(0)
        
        if not draft:
            return {}
        
        project = draft.get('project', {})
        tracks = draft.get('tracks', [])
        
        # 统计各类型轨道数量
        track_stats = {}
        for track in tracks:
            track_type = track.get('track_type', 'unknown')
            track_stats[track_type] = track_stats.get(track_type, 0) + 1
        
        # 统计总段数
        total_segments = sum(len(track.get('segments', [])) for track in tracks)
        
        return {
            'draft_id': draft.get('draft_id', ''),
            'project_name': project.get('name', ''),
            'resolution': f"{project.get('width', 0)}x{project.get('height', 0)}",
            'fps': project.get('fps', 30),
            'track_count': len(tracks),
            'track_stats': track_stats,
            'total_segments': total_segments,
            'status': draft.get('status', 'unknown')
        }
    
    def normalize_data(self) -> Dict[str, Any]:
        """
        标准化解析的数据，转换为DraftGenerator期望的格式
        
        Returns:
            标准化后的数据字典
        """
        if not self.parsed_data:
            return {}
        
        normalized = self.parsed_data.copy()
        
        # 标准化每个草稿的数据
        for draft in normalized.get('drafts', []):
            self._normalize_draft(draft)
        
        return normalized
    
    def _normalize_draft(self, draft: Dict[str, Any]):
        """标准化单个草稿的数据结构"""
        tracks = draft.get('tracks', [])
        
        for track in tracks:
            segments = track.get('segments', [])
            
            for segment in segments:
                # 1. 统一字段名: type -> segment_type
                if 'type' in segment:
                    segment['segment_type'] = segment['type']
                
                # 2. 计算duration_ms
                time_range = segment.get('time_range', {})
                if 'start' in time_range and 'end' in time_range:
                    duration_ms = time_range['end'] - time_range['start']
                    segment['duration_ms'] = duration_ms
                
                # 3. 标准化material结构
                if 'material_url' in segment:
                    material_url = segment['material_url']
                    # 从URL生成文件名
                    file_name = self._generate_filename_from_url(material_url, segment.get('segment_type', 'unknown'))
                    segment['material'] = {
                        'url': material_url,
                        'file_name': file_name
                    }
                
                # 注意：content字段应保持为字符串，不要转换为对象！
                # pyJianYingDraft的TextSegment期望text参数是字符串
    
    def _generate_filename_from_url(self, url: str, segment_type: str) -> str:
        """从URL生成文件名"""
        if not url:
            return f"material_{segment_type}"
        
        # 提取URL中的标识符
        if 's.coze.cn/t/' in url:
            # Coze图片URL: https://s.coze.cn/t/Wf_iCf1jiKE/
            path_part = url.split('/t/')[-1].rstrip('/')
            if segment_type == 'image':
                return f"{path_part}.png"
            elif segment_type == 'video':
                return f"{path_part}.mp4"
        elif 'speech_' in url:
            # 音频URL中通常包含speech_标识
            if 'speech_' in url:
                speech_id = url.split('speech_')[1].split('_')[0]
                return f"speech_{speech_id}.mp3"
        
        # 默认文件名
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        ext_map = {
            'audio': '.mp3',
            'image': '.png', 
            'video': '.mp4',
            'text': '.txt'
        }
        ext = ext_map.get(segment_type, '.bin')
        return f"material_{url_hash}{ext}"
    
    def get_normalized_data(self) -> Dict[str, Any]:
        """
        获取标准化后的数据
        
        Returns:
            标准化后的数据字典，可直接用于DraftGenerator
        """
        return self.normalize_data()

    def print_summary(self):
        """打印解析摘要"""
        if not self.parsed_data:
            logger.warning("没有解析的数据")
            return
        
        logger.info("=" * 60)
        logger.info("输入内容解析摘要")
        logger.info("=" * 60)
        logger.info(f"格式版本: {self.parsed_data.get('format_version', 'N/A')}")
        logger.info(f"导出类型: {self.get_export_type()}")
        logger.info(f"草稿数量: {self.get_draft_count()}")
        logger.info("")
        
        for i, draft in enumerate(self.get_drafts(), 1):
            info = self.get_draft_info(draft)
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


def parse_coze_output(input_source: str, is_file: bool = False) -> Dict[str, Any]:
    """
    便捷函数:解析Coze输出
    
    Args:
        input_source: 输入源(剪贴板文本或文件路径)
        is_file: 是否为文件路径
        
    Returns:
        解析后的草稿数据字典
        
    Example:
        # 从剪贴板
        data = parse_coze_output(clipboard_text)
        
        # 从文件
        data = parse_coze_output('coze_example.json', is_file=True)
    """
    parser = CozeOutputParser()
    
    if is_file:
        return parser.parse_from_file(input_source)
    else:
        return parser.parse_from_clipboard(input_source)


# 示例用法
if __name__ == "__main__":
    # 测试解析
    parser = CozeOutputParser()
    
    # 从文件解析
    try:
        data = parser.parse_from_file('coze_example_for_paste_context.json')
        parser.print_summary()
        
        # 获取第一个草稿
        first_draft = parser.get_draft_by_index(0)
        if first_draft:
            print("\n第一个草稿的轨道信息:")
            for track in first_draft.get('tracks', []):
                track_type = track.get('track_type')
                segments_count = len(track.get('segments', []))
                print(f"  {track_type}: {segments_count} 个片段")
                
    except ValueError as e:
        print(f"解析失败: {e}")
