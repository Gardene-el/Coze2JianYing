"""
添加图片工具处理器

向现有草稿添加图片片段，创建新的图片轨道。
每次调用创建一个包含所有指定图片的新轨道。
"""

import os
import json
import uuid
import time
from typing import NamedTuple, List, Dict, Any
from runtime import Args


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """add_images 工具的输入参数"""
    draft_id: str                # 现有草稿的 UUID
    image_infos: List[str]       # 包含image信息的 JSON 字符串列表


class Output(NamedTuple):
    """add_images 工具的输出"""
    segment_ids: List[str]       # 生成的片段 UUID 列表
    success: bool = True         # 操作成功状态
    message: str = "图片添加成功"  # 状态消息


# 数据模型（为 Coze 工具独立性在此重复定义）
class TimeRange:
    """时间范围，单位：毫秒"""
    def __init__(self, start: int = 0, end: int = 0):
        self.start = start
        self.end = end
    
    @property
    def duration(self) -> int:
        return self.end - self.start


class ImageSegmentConfig:
    """图片片段的配置"""
    def __init__(self, material_url: str, time_range: TimeRange, **kwargs):
        self.material_url = material_url
        self.time_range = time_range
        
        # Transform properties
        self.position_x = kwargs.get('position_x', 0.0)
        self.position_y = kwargs.get('position_y', 0.0) 
        self.scale_x = kwargs.get('scale_x', 1.0)
        self.scale_y = kwargs.get('scale_y', 1.0)
        self.rotation = kwargs.get('rotation', 0.0)
        self.opacity = kwargs.get('opacity', 1.0)
        
        # Image dimensions
        self.width = kwargs.get('width')
        self.height = kwargs.get('height')
        
        # Crop settings
        self.crop_enabled = kwargs.get('crop_enabled', False)
        self.crop_left = kwargs.get('crop_left', 0.0)
        self.crop_top = kwargs.get('crop_top', 0.0)
        self.crop_right = kwargs.get('crop_right', 1.0)
        self.crop_bottom = kwargs.get('crop_bottom', 1.0)
        
        # Effects
        self.filter_type = kwargs.get('filter_type')
        self.filter_intensity = kwargs.get('filter_intensity', 1.0)
        self.transition_type = kwargs.get('transition_type')
        self.transition_duration = kwargs.get('transition_duration', 500)
        
        # Background
        self.background_blur = kwargs.get('background_blur', False)
        self.background_color = kwargs.get('background_color')
        self.fit_mode = kwargs.get('fit_mode', 'fit')
        
        # Animations
        self.intro_animation = kwargs.get('in_animation')  # Maps to intro_animation
        self.intro_animation_duration = kwargs.get('in_animation_duration', 500)
        self.outro_animation = kwargs.get('outro_animation')
        self.outro_animation_duration = kwargs.get('outro_animation_duration', 500)
        
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


def parse_image_infos(image_infos_input: List[str]) -> List[Dict[str, Any]]:
    """从输入格式解析 image_infos 并验证"""
    try:
        # 处理 JSON 字符串列表格式
        if isinstance(image_infos_input, list):
            # 字符串数组 - 将每个字符串解析为 JSON
            parsed_infos = []
            for i, info_str in enumerate(image_infos_input):
                try:
                    parsed_info = json.loads(info_str)
                    parsed_infos.append(parsed_info)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in image_infos[{i}]: {str(e)}")
            images = parsed_infos
        else:
            raise ValueError(f"image_infos 必须是字符串列表，得到 {type(image_infos_input)}")
        
        # 确保是列表
        if not isinstance(images, list):
            raise ValueError(f"image_infos 必须解析为列表，得到 {type(images)}")
        
        # 处理每一项并进行健壮性检查
        result = []
        for i, info in enumerate(images):
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
                            raise ValueError(f"image_infos[{i}] 无法转换为字典（类型：{type(info)}）")

            # 验证必需字段
            required_fields = ['image_url', 'start', 'end']
            for field in required_fields:
                if field not in converted_info:
                    raise ValueError(f"{info_param}[{{i}}] 中缺少必需字段 '{{field}}'")
            
            # 将 image_url 映射到 material_url 以保持一致性
            converted_info['material_url'] = converted_info['image_url']

            result.append(converted_info)
        
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"image_infos 中的 JSON 格式无效：{str(e)}")
    except Exception as e:
        raise ValueError(f"解析 image_infos 时出错（类型：{type(image_infos_input)}）：{str(e)}")

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


def create_image_track_with_segments(image_infos: List[Dict[str, Any]]) -> tuple[List[str], Dict[str, Any]]:
    """
    创建包含片段的图片轨道，遵循数据结构模式
    
    返回值:
        tuple: (segment_ids, track_dict)
    """
    segment_ids = []
    segments = []
    
    for info in image_infos:
        segment_id = str(uuid.uuid4())
        segment_ids.append(segment_id)
        
        # 创建要返回的片段信息
        segment_infos.append({
            "id": segment_id,
            "start": info['start'],
            "end": info['end']
        })
        
        # 遵循正确的数据结构格式创建片段
        # 仅包含 info 中存在的字段（来自 make_image_info 的非默认值）
        segment = {
            "id": segment_id,
            "type": "image",
            "material_url": info['material_url'],
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
        
        # Crop - only add if enabled
        if info.get('crop_enabled'):
            segment["crop"] = {
                "enabled": True,
                "left": info.get('crop_left', 0.0),
                "top": info.get('crop_top', 0.0),
                "right": info.get('crop_right', 1.0),
                "bottom": info.get('crop_bottom', 1.0)
            }
        
        # Effects - only add if filter or transition specified
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
        
        # Background - only add if any background properties specified
        background = {}
        if 'background_blur' in info:
            background['blur'] = info['background_blur']
        if 'background_color' in info:
            background['color'] = info['background_color']
        if 'fit_mode' in info:
            background['fit_mode'] = info['fit_mode']
        if background:
            segment["background"] = background
        
        # 动画 - 仅在指定了任何动画时添加
        animations = {}
        if 'in_animation' in info:  # Map in_animation to intro
            animations['intro'] = info['in_animation']
            if 'in_animation_duration' in info:
                animations['intro_duration'] = info['in_animation_duration']
        if 'outro_animation' in info:
            animations['outro'] = info['outro_animation']
            if 'outro_animation_duration' in info:
                animations['outro_duration'] = info['outro_animation_duration']
        if animations:
            segment["animations"] = animations
        
        segments.append(segment)
    
    # 遵循正确的 TrackConfig 格式创建轨道
    # Note: Images are placed on video tracks (no separate image track type)
    track = {
        "track_type": "video",
        "segments": segments
    }
    
    return segment_ids, segment_infos, track


def handler(args: Args[Input]) -> Output:
    """
    向草稿添加图片的主处理函数
    
    参数:
        args: 包含 draft_id 和 image_infos 的输入参数
        
    返回值:
        包含 segment_ids 的输出
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Adding images to draft: {args.input.draft_id}")
    
    try:
        # 验证输入参数
        if not args.input.draft_id:
            return Output(
                segment_ids=[],                success=False,
                message="缺少必需的 draft_id 参数"
            )
        
        if not validate_uuid_format(args.input.draft_id):
            return Output(
                segment_ids=[],                success=False,
                message="无效的 draft_id 格式"
            )
        
        if args.input.image_infos is None:
            return Output(
                segment_ids=[],                success=False,
                message="缺少必需的 image_infos 参数"
            )
        
        # 解析图片信息并进行详细日志记录
        try:
            if logger:
                logger.info(f"About to parse image_infos: type={type(args.input.image_infos)}, value={repr(args.input.image_infos)[:500]}...")
            
            image_infos = parse_image_infos(args.input.image_infos)
            
            if logger:
                logger.info(f"Successfully parsed {len(image_infos)} image infos")
                
        except ValueError as e:
            if logger:
                logger.error(f"Failed to parse image_infos: {str(e)}")
            return Output(
                segment_ids=[],                success=False,
                message=f"解析 image_infos 失败: {str(e)}"
            )
        
        if not image_infos:
            return Output(
                segment_ids=[],                success=False,
                message="image_infos 不能为空"
            )
        
        # 加载现有草稿配置
        try:
            draft_config = load_draft_config(args.input.draft_id)
        except (FileNotFoundError, Exception) as e:
            return Output(
                segment_ids=[],                success=False,
                message=f"加载草稿配置失败: {str(e)}"
            )
        
        # 使用正确的数据结构模式创建带片段的图片轨道
        segment_ids, image_track = create_image_track_with_segments(image_infos)
        
        # 将轨道添加到草稿配置
        if "tracks" not in draft_config:
            draft_config["tracks"] = []
        
        draft_config["tracks"].append(image_track)
        
        # 更新时间戳
        draft_config["last_modified"] = time.time()
        
        # 保存更新后的配置
        try:
            save_draft_config(args.input.draft_id, draft_config)
        except Exception as e:
            return Output(
                segment_ids=[],                success=False,
                message=f"保存草稿配置失败: {str(e)}"
            )
        
        if logger:
            logger.info(f"Successfully added {len(image_infos)} images to draft {args.input.draft_id}")
        
        return Output(
            segment_ids=segment_ids,            success=True,
            message=f"成功添加 {len(image_infos)} 张图片到草稿"
        )
        
    except Exception as e:
        error_msg = f"添加图片时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            segment_ids=[],            success=False,
            message=error_msg
        )