"""
添加特效工具处理器

向现有草稿添加特效片段，创建新的特效轨道。
每次调用创建一个包含所有指定特效的新轨道。
"""

import os
import json
import uuid
import time
from typing import NamedTuple, List, Dict, Any
from runtime import Args


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """add_effects 工具的输入参数"""
    draft_id: str                # 现有草稿的 UUID
    effect_infos: List[str]       # 包含effect信息的 JSON 字符串列表


class Output(NamedTuple):
    """add_effects 工具的输出"""
    segment_ids: List[str]       # 生成的片段 UUID 列表
    success: bool = True         # 操作成功状态
    message: str = "特效添加成功"  # 状态消息


# 数据模型（为 Coze 工具独立性在此重复定义）
class TimeRange:
    """时间范围，单位：毫秒"""
    def __init__(self, start: int = 0, end: int = 0):
        self.start = start
        self.end = end
    
    @property
    def duration(self) -> int:
        return self.end - self.start


class EffectSegmentConfig:
    """特效片段的配置"""
    def __init__(self, effect_type: str, time_range: TimeRange, **kwargs):
        self.effect_type = effect_type
        self.time_range = time_range
        
        # Effect properties
        self.intensity = kwargs.get('intensity', 1.0)
        self.properties = kwargs.get('properties', {})
        
        # Position (for localized effects)
        self.position_x = kwargs.get('position_x')
        self.position_y = kwargs.get('position_y')
        self.scale = kwargs.get('scale', 1.0)


def validate_uuid_format(uuid_str: str) -> bool:
    """验证 UUID 字符串格式"""
    try:
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def parse_effect_infos(effect_infos_input: List[str]) -> List[Dict[str, Any]]:
    """从输入格式解析 effect_infos 并验证"""
    try:
        # 处理 JSON 字符串列表格式
        if isinstance(effect_infos_input, list):
            # 字符串数组 - 将每个字符串解析为 JSON
            parsed_infos = []
            for i, info_str in enumerate(effect_infos_input):
                try:
                    parsed_info = json.loads(info_str)
                    parsed_infos.append(parsed_info)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in effect_infos[{i}]: {str(e)}")
            effects = parsed_infos
        else:
            raise ValueError(f"effect_infos 必须是字符串列表，得到 {type(effect_infos_input)}")
        
        # 确保是列表
        if not isinstance(effects, list):
            raise ValueError(f"effect_infos 必须解析为列表，得到 {type(effects)}")
        
        # 处理每一项并进行健壮性检查
        result = []
        for i, info in enumerate(effects):
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
                            raise ValueError(f"effect_infos[{i}] 无法转换为字典（类型：{type(info)}）")

            # 验证必需字段
            required_fields = ['effect_type', 'start', 'end']
            for field in required_fields:
                if field not in converted_info:
                    raise ValueError(f"{info_param}[{{i}}] 中缺少必需字段 '{{field}}'")

            result.append(converted_info)
        
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"effect_infos 中的 JSON 格式无效：{str(e)}")
    except Exception as e:
        raise ValueError(f"解析 effect_infos 时出错（类型：{type(effect_infos_input)}）：{str(e)}")

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


def create_effect_track_with_segments(effect_infos: List[Dict[str, Any]]) -> tuple[List[str], Dict[str, Any]]:
    """
    创建包含片段的特效轨道，遵循数据结构模式
    
    返回值:
        tuple: (segment_ids, track_dict)
    """
    segment_ids = []
    segments = []
    
    for info in effect_infos:
        segment_id = str(uuid.uuid4())
        segment_ids.append(segment_id)
        
        # 创建要返回的片段信息
        segment_infos.append({
            "id": segment_id,
            "start": info['start'],
            "end": info['end']
        })
        
        # 遵循正确的数据结构格式创建片段
        # 这匹配 DraftConfig 的 _serialize_effect_segment 格式
        segment = {
            "id": segment_id,
            "type": "effect",
            "effect_type": info['effect_type'],
            "time_range": {
                "start": info['start'],
                "end": info['end']
            },
            "properties": {
                "intensity": info.get('intensity', 1.0),
                "position_x": info.get('position_x'),
                "position_y": info.get('position_y'),
                "scale": info.get('scale', 1.0)
            }
        }
        
        # 如果提供了自定义属性则添加
        if 'properties' in info and info['properties']:
            segment["properties"].update(info['properties'])
        
        segments.append(segment)
    
    # 遵循正确的 TrackConfig 格式创建轨道
    track = {
        "track_type": "effect",
        "muted": False,
        "volume": 1.0,
        "segments": segments
    }
    
    return segment_ids, segment_infos, track


def handler(args: Args[Input]) -> Output:
    """
    向草稿添加特效的主处理函数
    
    参数:
        args: 包含 draft_id 和 effect_infos 的输入参数
        
    返回值:
        包含 segment_ids 的输出
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Adding effects to draft: {args.input.draft_id}")
    
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
        
        if args.input.effect_infos is None:
            return Output(
                segment_ids=[],                success=False,
                message="缺少必需的 effect_infos 参数"
            )
        
        # 解析特效信息并进行详细日志记录
        try:
            if logger:
                logger.info(f"About to parse effect_infos: type={type(args.input.effect_infos)}, value={repr(args.input.effect_infos)[:500]}...")
            
            effect_infos = parse_effect_infos(args.input.effect_infos)
            
            if logger:
                logger.info(f"Successfully parsed {len(effect_infos)} effect infos")
                
        except ValueError as e:
            if logger:
                logger.error(f"Failed to parse effect_infos: {str(e)}")
            return Output(
                segment_ids=[],                success=False,
                message=f"解析 effect_infos 失败: {str(e)}"
            )
        
        if not effect_infos:
            return Output(
                segment_ids=[],                success=False,
                message="effect_infos 不能为空"
            )
        
        # 加载现有草稿配置
        try:
            draft_config = load_draft_config(args.input.draft_id)
        except (FileNotFoundError, Exception) as e:
            return Output(
                segment_ids=[],                success=False,
                message=f"加载草稿配置失败: {str(e)}"
            )
        
        # 使用正确的数据结构模式创建带片段的特效轨道
        segment_ids, effect_track = create_effect_track_with_segments(effect_infos)
        
        # 将轨道添加到草稿配置
        if "tracks" not in draft_config:
            draft_config["tracks"] = []
        
        draft_config["tracks"].append(effect_track)
        
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
            logger.info(f"Successfully added {len(effect_infos)} effects to draft {args.input.draft_id}")
        
        return Output(
            segment_ids=segment_ids,            success=True,
            message=f"成功添加 {len(effect_infos)} 个特效到草稿"
        )
        
    except Exception as e:
        error_msg = f"添加特效时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            segment_ids=[],            success=False,
            message=error_msg
        )
