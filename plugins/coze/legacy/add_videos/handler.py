"""
添加视频工具处理器

向现有草稿添加视频片段，创建新的视频轨道。
每次调用创建一个包含所有指定视频的新轨道。
"""

import os
import json
import uuid
import time
from typing import NamedTuple, List, Dict, Any
from runtime import Args


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """add_videos 工具的输入参数"""
    draft_id: str                # 现有草稿的 UUID
    video_infos: List[str]       # 包含视频信息的 JSON 字符串列表


class Output(NamedTuple):
    """add_videos 工具的输出"""
    segment_ids: List[str]       # 生成的片段 UUID 列表
    success: bool = True         # 操作成功状态
    message: str = "视频添加成功"  # 状态消息


# 数据模型（为 Coze 工具独立性在此重复定义）
class TimeRange:
    """时间范围，单位：毫秒"""
    def __init__(self, start: int = 0, end: int = 0):
        self.start = start
        self.end = end
    
    @property
    def duration(self) -> int:
        return self.end - self.start


class VideoSegmentConfig:
    """视频片段的配置"""
    def __init__(self, material_url: str, time_range: TimeRange, **kwargs):
        self.material_url = material_url
        self.time_range = time_range
        
        # 素材范围（用于剪裁视频）
        material_start = kwargs.get('material_start')
        material_end = kwargs.get('material_end')
        if material_start is not None and material_end is not None:
            self.material_range = TimeRange(material_start, material_end)
        else:
            self.material_range = None
        
        # 变换属性
        self.position_x = kwargs.get('position_x', 0.0)
        self.position_y = kwargs.get('position_y', 0.0) 
        self.scale_x = kwargs.get('scale_x', 1.0)
        self.scale_y = kwargs.get('scale_y', 1.0)
        self.rotation = kwargs.get('rotation', 0.0)
        self.opacity = kwargs.get('opacity', 1.0)
        self.flip_horizontal = kwargs.get('flip_horizontal', False)
        self.flip_vertical = kwargs.get('flip_vertical', False)
        
        # 裁剪设置
        self.crop_enabled = kwargs.get('crop_enabled', False)
        self.crop_left = kwargs.get('crop_left', 0.0)
        self.crop_top = kwargs.get('crop_top', 0.0)
        self.crop_right = kwargs.get('crop_right', 1.0)
        self.crop_bottom = kwargs.get('crop_bottom', 1.0)
        
        # 特效
        self.filter_type = kwargs.get('filter_type')
        self.filter_intensity = kwargs.get('filter_intensity', 1.0)
        self.transition_type = kwargs.get('transition_type')
        self.transition_duration = kwargs.get('transition_duration', 500)
        
        # 速度控制
        self.speed = kwargs.get('speed', 1.0)
        self.reverse = kwargs.get('reverse', False)
        
        # 音频（视频的）
        self.volume = kwargs.get('volume', 1.0)
        self.change_pitch = kwargs.get('change_pitch', False)
        
        # 背景
        self.background_blur = kwargs.get('background_blur', False)
        self.background_color = kwargs.get('background_color')
        
        # 关键帧（默认为空）
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


def parse_video_infos(video_infos_input: List[str]) -> List[Dict[str, Any]]:
    """从输入格式解析 video_infos 并验证"""
    try:
        # 处理 JSON 字符串列表格式
        if isinstance(video_infos_input, list):
            # 字符串数组 - 将每个字符串解析为 JSON
            parsed_infos = []
            for i, info_str in enumerate(video_infos_input):
                try:
                    parsed_info = json.loads(info_str)
                    parsed_infos.append(parsed_info)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in video_infos[{i}]: {str(e)}")
            video_infos = parsed_infos
        else:
            raise ValueError(f"video_infos 必须是字符串列表，得到 {type(video_infos_input)}")
        
        # 确保是列表
        if not isinstance(video_infos, list):
            raise ValueError(f"video_infos 必须解析为列表，得到 {type(video_infos)}")
        
        # 处理每一项并进行健壮性检查
        result = []
        for i, info in enumerate(video_infos):
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
                            raise ValueError(f"video_infos[{i}] 无法转换为字典（类型：{type(info)}）")
            
            # 验证必需字段
            required_fields = ['video_url', 'start', 'end']
            for field in required_fields:
                if field not in converted_info:
                    raise ValueError(f"video_infos[{i}] 中缺少必需字段 '{field}'")
            
            # 将 video_url 映射到 material_url 以保持一致性
            converted_info['material_url'] = converted_info['video_url']
            
            result.append(converted_info)
        
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"video_infos 中的 JSON 格式无效：{str(e)}")
    except Exception as e:
        raise ValueError(f"解析 video_infos 时出错（类型：{type(video_infos_input)}）：{str(e)}")


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


def create_video_track_with_segments(video_infos: List[Dict[str, Any]]) -> tuple[List[str], Dict[str, Any]]:
    """
    创建包含片段的视频轨道，遵循数据结构模式
    
    返回值:
        tuple: (segment_ids, track_dict)
    """
    segment_ids = []
    segments = []
    
    for info in video_infos:
        segment_id = str(uuid.uuid4())
        segment_ids.append(segment_id)
        
        # 遵循正确的数据结构格式创建片段
        # 仅包含 info 中存在的字段（来自 make_video_info 的非默认值）
        segment = {
            "id": segment_id,
            "type": "video",
            "material_url": info['material_url'],
            "time_range": {
                "start": info['start'],
                "end": info['end']
            }
        }
        
        # 如果提供了 material_range，则添加（用于剪裁视频）
        if 'material_start' in info and 'material_end' in info:
            segment["material_range"] = {
                "start": info['material_start'],
                "end": info['material_end']
            }
        
        # 构建 transform 字典，仅包含 info 中存在的字段
        transform = {}
        if 'position_x' in info:
            transform['position_x'] = info['position_x']
        if 'position_y' in info:
            transform['position_y'] = info['position_y']
        if 'scale_x' in info:
            transform['scale_x'] = info['scale_x']
        if 'scale_y' in info:
            transform['scale_y'] = info['scale_y']
        if 'rotation' in info:
            transform['rotation'] = info['rotation']
        if 'opacity' in info:
            transform['opacity'] = info['opacity']
        if transform:
            segment["transform"] = transform
        
        # 裁剪 - 仅在启用时添加
        if info.get('crop_enabled'):
            segment["crop"] = {
                "enabled": True,
                "left": info.get('crop_left', 0.0),
                "top": info.get('crop_top', 0.0),
                "right": info.get('crop_right', 1.0),
                "bottom": info.get('crop_bottom', 1.0)
            }
        
        # 特效 - 仅在指定了滤镜或转场时添加
        effects = {}
        if 'filter_type' in info:
            effects['filter_type'] = info['filter_type']
            if 'filter_intensity' in info:
                effects['filter_intensity'] = info['filter_intensity']
        if 'transition_type' in info:
            effects['transition_type'] = info['transition_type']
            if 'transition_duration' in info:
                effects['transition_duration'] = info['transition_duration']
        if effects:
            segment["effects"] = effects
        
        # 速度 - 仅在非默认值时添加
        speed = {}
        if 'speed' in info:
            speed['speed'] = info['speed']
        if 'reverse' in info:
            speed['reverse'] = info['reverse']
        if speed:
            segment["speed"] = speed
        
        # 背景 - 仅在指定了任何背景属性时添加
        background = {}
        if 'background_blur' in info:
            background['blur'] = info['background_blur']
        if 'background_color' in info:
            background['color'] = info['background_color']
        if background:
            segment["background"] = background
        
        segments.append(segment)
    
    # 遵循正确的 TrackConfig 格式创建轨道
    track = {
        "track_type": "video",
        "segments": segments
    }
    
    return segment_ids, track


def handler(args: Args[Input]) -> Output:
    """
    向草稿添加视频的主处理函数
    
    参数:
        args: 包含 draft_id 和 video_infos 的输入参数
        
    返回值:
        包含 segment_ids 的输出
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"向草稿添加视频: {args.input.draft_id}")
    
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
        
        if args.input.video_infos is None:
            return Output(
                segment_ids=[],
                success=False,
                message="缺少必需的 video_infos 参数"
            )
        
        # 解析视频信息并进行详细日志记录
        try:
            if logger:
                logger.info(f"即将解析 video_infos: type={type(args.input.video_infos)}, value={repr(args.input.video_infos)[:500]}...")
            
            video_infos = parse_video_infos(args.input.video_infos)
            
            if logger:
                logger.info(f"成功解析 {len(video_infos)} 个视频信息")
                
        except ValueError as e:
            if logger:
                logger.error(f"解析 video_infos 失败: {str(e)}")
            return Output(
                segment_ids=[],
                success=False,
                message=f"解析 video_infos 失败: {str(e)}"
            )
        
        if not video_infos:
            return Output(
                segment_ids=[],
                success=False,
                message="video_infos 不能为空"
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
        
        # 使用正确的数据结构模式创建带有片段的视频轨道
        segment_ids, video_track = create_video_track_with_segments(video_infos)
        
        # 将轨道添加到草稿配置
        if "tracks" not in draft_config:
            draft_config["tracks"] = []
        
        draft_config["tracks"].append(video_track)
        
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
            logger.info(f"成功向草稿 {args.input.draft_id} 添加了 {len(video_infos)} 个视频")
        
        return Output(
            segment_ids=segment_ids,
            success=True,
            message=f"成功添加 {len(video_infos)} 个视频到草稿"
        )
        
    except Exception as e:
        error_msg = f"添加视频时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            segment_ids=[],
            success=False,
            message=error_msg
        )
