"""
添加字幕工具处理器

向现有草稿添加文本/字幕片段，创建新的文本轨道。
每次调用创建一个包含所有指定字幕的新轨道。
"""

import os
import json
import uuid
import time
from typing import NamedTuple, List, Dict, Any
from runtime import Args


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """add_captions 工具的输入参数"""
    draft_id: str                # 现有草稿的 UUID
    caption_infos: List[str]       # 包含caption信息的 JSON 字符串列表


class Output(NamedTuple):
    """add_captions 工具的输出"""
    segment_ids: List[str]       # 生成的片段 UUID 列表
    success: bool = True         # 操作成功状态
    message: str = "字幕添加成功"  # 状态消息


# 数据模型（为 Coze 工具独立性在此重复定义）
class TimeRange:
    """时间范围，单位：毫秒"""
    def __init__(self, start: int = 0, end: int = 0):
        self.start = start
        self.end = end
    
    @property
    def duration(self) -> int:
        return self.end - self.start


class TextStyle:
    """文本样式配置"""
    def __init__(self, **kwargs):
        self.font_family = kwargs.get('font_family', "默认")
        self.font_size = kwargs.get('font_size', 48)
        self.font_weight = kwargs.get('font_weight', "normal")
        self.font_style = kwargs.get('font_style', "normal")
        self.color = kwargs.get('color', "#FFFFFF")
        
        # 文本特效
        self.stroke_enabled = kwargs.get('stroke_enabled', False)
        self.stroke_color = kwargs.get('stroke_color', "#000000")
        self.stroke_width = kwargs.get('stroke_width', 2)
        
        self.shadow_enabled = kwargs.get('shadow_enabled', False)
        self.shadow_color = kwargs.get('shadow_color', "#000000")
        self.shadow_offset_x = kwargs.get('shadow_offset_x', 2)
        self.shadow_offset_y = kwargs.get('shadow_offset_y', 2)
        self.shadow_blur = kwargs.get('shadow_blur', 4)
        
        self.background_enabled = kwargs.get('background_enabled', False)
        self.background_color = kwargs.get('background_color', "#000000")
        self.background_opacity = kwargs.get('background_opacity', 0.5)


class TextSegmentConfig:
    """文本/字幕片段的配置"""
    def __init__(self, content: str, time_range: TimeRange, **kwargs):
        self.content = content
        self.time_range = time_range
        
        # Position and transform
        self.position_x = kwargs.get('position_x', 0.5)
        self.position_y = kwargs.get('position_y', -0.9)
        self.scale = kwargs.get('scale', 1.0)
        self.rotation = kwargs.get('rotation', 0.0)
        self.opacity = kwargs.get('opacity', 1.0)
        
        # Text styling
        self.style = TextStyle(**kwargs)
        
        # Alignment
        self.alignment = kwargs.get('alignment', 'center')
        
        # Animations
        self.intro_animation = kwargs.get('intro_animation')
        self.outro_animation = kwargs.get('outro_animation')
        self.loop_animation = kwargs.get('loop_animation')
        
        # Keyframes (empty by default)
        self.position_keyframes = []
        self.scale_keyframes = []
        self.rotation_keyframes = []
        self.opacity_keyframes = []


def validate_uuid_format(uuid_str: str) -> bool:
    """验证 UUID 字符串格式"""
    try:
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def parse_caption_infos(caption_infos_input: List[str]) -> List[Dict[str, Any]]:
    """从输入格式解析 caption_infos 并验证"""
    try:
        # 处理 JSON 字符串列表格式
        if isinstance(caption_infos_input, list):
            # 字符串数组 - 将每个字符串解析为 JSON
            parsed_infos = []
            for i, info_str in enumerate(caption_infos_input):
                try:
                    parsed_info = json.loads(info_str)
                    parsed_infos.append(parsed_info)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in caption_infos[{i}]: {str(e)}")
            captions = parsed_infos
        else:
            raise ValueError(f"caption_infos 必须是字符串列表，得到 {type(caption_infos_input)}")
        
        # 确保是列表
        if not isinstance(captions, list):
            raise ValueError(f"caption_infos 必须解析为列表，得到 {type(captions)}")
        
        # 处理每一项并进行健壮性检查
        result = []
        for i, info in enumerate(captions):
            # 转换为纯字典 - 处理各种对象类型
            if isinstance(info, dict):
                # 已经是纯字典
                converted_info = dict(info)  # 为安全起见制作副本
            else:
                # 尝试各种转换策略
                converted_info = {}
                
                # 策略 1：尝试像字典一样访问
                try:
                    if hasattr(info, 'keys') and hasattr(info, '__getitem__'):
                        for key in info.keys():
                            converted_info[key] = info[key]
                    else:
                        raise TypeError("Not dict-like")
                except Exception:
                    # 策略 2：尝试 vars() 获取对象属性
                    try:
                        converted_info = vars(info)
                    except Exception:
                        # 策略 3：尝试 dir() 和 getattr
                        try:
                            for attr in dir(info):
                                if not attr.startswith('_'):
                                    converted_info[attr] = getattr(info, attr)
                        except Exception:
                            raise ValueError(f"caption_infos[{i}] 无法转换为字典（类型：{type(info)}）")

            # 验证必需字段
            required_fields = ['content', 'start', 'end']
            for field in required_fields:
                if field not in converted_info:
                    raise ValueError(f"{info_param}[{{i}}] 中缺少必需字段 '{{field}}'")

            result.append(converted_info)
        
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"caption_infos 中的 JSON 格式无效：{str(e)}")
    except Exception as e:
        raise ValueError(f"解析 caption_infos 时出错（类型：{type(caption_infos_input)}）：{str(e)}")

def load_draft_config(draft_id: str) -> Dict[str, Any]:
    """加载现有草稿配置"""
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    if not os.path.exists(draft_folder):
        raise FileNotFoundError(f"Draft with ID {draft_id} not found")
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Draft config file not found for ID {draft_id}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Failed to load draft config: {str(e)}")


def save_draft_config(draft_id: str, config: Dict[str, Any]) -> None:
    """保存更新后的草稿配置"""
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise Exception(f"Failed to save draft config: {str(e)}")


def create_text_track_with_segments(caption_infos: List[Dict[str, Any]]) -> tuple[List[str], Dict[str, Any]]:
    """
    创建包含片段的文本轨道，遵循数据结构模式
    
    返回值:
        tuple: (segment_ids, track_dict)
    """
    segment_ids = []
    segments = []
    
    for info in caption_infos:
        segment_id = str(uuid.uuid4())
        segment_ids.append(segment_id)
        
        # 创建要返回的片段信息
        segment_infos.append({
            "id": segment_id,
            "start": info['start'],
            "end": info['end']
        })
        
        # 遵循正确的数据结构格式创建片段
        # 仅包含 info 中存在的字段（来自 make_caption_info 的非默认值）
        segment = {
            "id": segment_id,
            "type": "text",
            "content": info['content'],
            "time_range": {
                "start": info['start'],
                "end": info['end']
            }
        }
        
        # 构建变换字典，仅包含 info 中存在的字段
        transform = {}
        if 'position_x' in info:
            transform['position_x'] = info['position_x']
        if 'position_y' in info:
            transform['position_y'] = info['position_y']
        if 'scale' in info:
            transform['scale'] = info['scale']
        if 'rotation' in info:
            transform['rotation'] = info['rotation']
        if 'opacity' in info:
            transform['opacity'] = info['opacity']
        if transform:
            segment["transform"] = transform
        
        # 构建样式字典，仅包含 info 中存在的字段
        style = {}
        if 'font_family' in info:
            style['font_family'] = info['font_family']
        if 'font_size' in info:
            style['font_size'] = info['font_size']
        if 'font_weight' in info:
            style['font_weight'] = info['font_weight']
        if 'font_style' in info:
            style['font_style'] = info['font_style']
        if 'color' in info:
            style['color'] = info['color']
        
        # 描边 - 仅在启用时添加
        if info.get('stroke_enabled'):
            stroke = {'enabled': True}
            if 'stroke_color' in info:
                stroke['color'] = info['stroke_color']
            if 'stroke_width' in info:
                stroke['width'] = info['stroke_width']
            style['stroke'] = stroke
        
        # 阴影 - 仅在启用时添加
        if info.get('shadow_enabled'):
            shadow = {'enabled': True}
            if 'shadow_color' in info:
                shadow['color'] = info['shadow_color']
            if 'shadow_offset_x' in info:
                shadow['offset_x'] = info['shadow_offset_x']
            if 'shadow_offset_y' in info:
                shadow['offset_y'] = info['shadow_offset_y']
            if 'shadow_blur' in info:
                shadow['blur'] = info['shadow_blur']
            style['shadow'] = shadow
        
        # 背景 - 仅在启用时添加
        if info.get('background_enabled'):
            background = {'enabled': True}
            if 'background_color' in info:
                background['color'] = info['background_color']
            if 'background_opacity' in info:
                background['opacity'] = info['background_opacity']
            style['background'] = background
        
        if style:
            segment["style"] = style
        
        # 对齐 - 仅在非默认值时添加
        if 'alignment' in info:
            segment["alignment"] = info['alignment']
        
        # 动画 - 仅在指定了任何动画时添加
        animations = {}
        if 'intro_animation' in info:
            animations['intro'] = info['intro_animation']
        if 'outro_animation' in info:
            animations['outro'] = info['outro_animation']
        if 'loop_animation' in info:
            animations['loop'] = info['loop_animation']
        if animations:
            segment["animations"] = animations
        
        segments.append(segment)
    
    # 遵循正确的 TrackConfig 格式创建轨道
    track = {
        "track_type": "text",
        "segments": segments
    }
    
    return segment_ids, segment_infos, track


def handler(args: Args[Input]) -> Output:
    """
    向草稿添加字幕的主处理函数
    
    参数:
        args: 包含 draft_id 和 caption_infos 的输入参数
        
    返回值:
        包含 segment_ids 的输出
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Adding captions to draft: {args.input.draft_id}")
    
    try:
        # 验证输入参数
        if not args.input.draft_id:
            return Output(
                segment_ids=[],
                success=False,
                message="缺少必需的 draft_id 参数"
            )
        
        if not validate_uuid_format(args.input.draft_id):
            return Output(
                segment_ids=[],
                success=False,
                message="无效的 draft_id 格式"
            )
        
        if args.input.caption_infos is None:
            return Output(
                segment_ids=[],
                success=False,
                message="缺少必需的 caption_infos 参数"
            )
        
        # 解析字幕信息并进行详细日志记录
        try:
            if logger:
                logger.info(f"About to parse caption_infos: type={type(args.input.caption_infos)}, value={repr(args.input.caption_infos)[:500]}...")
            
            caption_infos = parse_caption_infos(args.input.caption_infos)
            
            if logger:
                logger.info(f"Successfully parsed {len(caption_infos)} caption infos")
                
        except ValueError as e:
            if logger:
                logger.error(f"Failed to parse caption_infos: {str(e)}")
            return Output(
                segment_ids=[],
                success=False,
                message=f"解析 caption_infos 失败: {str(e)}"
            )
        
        if not caption_infos:
            return Output(
                segment_ids=[],
                success=False,
                message="caption_infos 不能为空"
            )
        
        # 加载现有草稿配置
        try:
            draft_config = load_draft_config(args.input.draft_id)
        except (FileNotFoundError, Exception) as e:
            return Output(
                segment_ids=[],
                success=False,
                message=f"加载草稿配置失败: {str(e)}"
            )
        
        # 使用正确的数据结构模式创建带片段的文本轨道
        segment_ids, segment_infos, text_track = create_text_track_with_segments(caption_infos)
        
        # 将轨道添加到草稿配置
        if "tracks" not in draft_config:
            draft_config["tracks"] = []
        
        draft_config["tracks"].append(text_track)
        
        # 更新时间戳
        draft_config["last_modified"] = time.time()
        
        # 保存更新后的配置
        try:
            save_draft_config(args.input.draft_id, draft_config)
        except Exception as e:
            return Output(
                segment_ids=[],
                success=False,
                message=f"保存草稿配置失败: {str(e)}"
            )
        
        if logger:
            logger.info(f"Successfully added {len(caption_infos)} captions to draft {args.input.draft_id}")
        
        return Output(
            segment_ids=segment_ids,            success=True,
            message=f"成功添加 {len(caption_infos)} 条字幕到草稿"
        )
        
    except Exception as e:
        error_msg = f"添加字幕时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            segment_ids=[],
                success=False,
            message=error_msg
        )
