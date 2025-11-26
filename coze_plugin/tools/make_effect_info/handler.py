"""
生成特效信息工具处理器

创建包含所有可能参数的特效配置的 JSON 字符串表示。
这是 add_effects 的辅助工具 - 生成单个特效信息字符串，可以
收集到数组中并传递给 add_effects。

总参数数： 8 (3 必需 + 5 可选)
Based on EffectSegmentConfig from data_structures/draft_generator_interface/models.py
"""

import json
from typing import NamedTuple, Optional, Dict, Any, Dict, Any
from runtime import Args


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """make_effect_info 工具的输入参数"""
    # 必需字段
    effect_type: str                            # 特效类型 name (e.g., "模糊", "锐化", "马赛克")
    start: int                                  # 开始时间（毫秒）
    end: int                                    # 结束时间（毫秒）
    
    # 可选特效属性
    intensity: Optional[float] = 1.0            # 特效强度 (0.0-1.0, default 1.0)
    
    # Optional position (for localized effects)
    position_x: Optional[float] = None          # X position (for localized effects)
    position_y: Optional[float] = None          # Y position (for localized effects)
    scale: Optional[float] = 1.0                # 缩放（默认 1.0）
    
    # Optional custom properties
    properties: Optional[str] = None            # JSON string of custom effect properties


class Output(NamedTuple):
    """make_effect_info 工具的输出"""
    effect_info_string: str   # 特效信息的 JSON 字符串表示
    success: bool             # Operation success status
    message: str              # Status message


def handler(args: Args[Input]) -> Output:
    """
    创建特效信息字符串的主处理函数
    
    Args:
        args: 包含所有特效参数的输入参数
        
    Returns:
        Dict containing the 特效信息的 JSON 字符串表示
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating effect info string for: {args.input.effect_type}")
    
    try:
        # 验证必需参数
        if not args.input.effect_type:
            return Output(
                effect_info_string="",
                success=False,
                message="缺少必需的 effect_type 参数"
            )._asdict()
        
        if args.input.start is None:
            return Output(
                effect_info_string="",
                success=False,
                message="缺少必需的 start 参数"
            )._asdict()
        
        if args.input.end is None:
            return Output(
                effect_info_string="",
                success=False,
                message="缺少必需的 end 参数"
            )._asdict()
        
        # 验证时间范围
        if args.input.start < 0:
            return Output(
                effect_info_string="",
                success=False,
                message="start 时间不能为负数"
            )._asdict()
        
        if args.input.end <= args.input.start:
            return Output(
                effect_info_string="",
                success=False,
                message="end 时间必须大于 start 时间"
            )._asdict()
        
        # 使用所有参数构建特效信息字典
        effect_info = {
            "effect_type": args.input.effect_type,
            "start": args.input.start,
            "end": args.input.end
        }
        
        # Add 可选 parameters only if they are not None or default values
        # 这使输出保持清洁，仅包含指定的参数
        
        # Intensity (only add if not default)
        if args.input.intensity != 1.0:
            effect_info["intensity"] = args.input.intensity
        
        # Position (only add if specified)
        if args.input.position_x is not None:
            effect_info["position_x"] = args.input.position_x
        if args.input.position_y is not None:
            effect_info["position_y"] = args.input.position_y
        
        # Scale (only add if not default)
        if args.input.scale != 1.0:
            effect_info["scale"] = args.input.scale
        
        # Custom properties (parse and add if provided)
        if args.input.properties is not None:
            try:
                properties_dict = json.loads(args.input.properties)
                if properties_dict:  # Only add if not empty
                    effect_info["properties"] = properties_dict
            except json.JSONDecodeError as e:
                return Output(
                    effect_info_string="",
                    success=False,
                    message=f"properties 参数必须是有效的 JSON 字符串: {str(e)}"
                )._asdict()
        
        # 转换为 JSON 字符串，不带额外空格以进行紧凑表示
        effect_info_string = json.dumps(effect_info, ensure_ascii=False, separators=(',', ':'))
        
        if logger:
            logger.info(f"Successfully created effect info string: {len(effect_info_string)} characters")
        
        return Output(
            effect_info_string=effect_info_string,
            success=True,
            message="特效信息字符串生成成功"
        )._asdict()
        
    except Exception as e:
        error_msg = f"生成特效信息字符串时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            effect_info_string="",
            success=False,
            message=error_msg
        )._asdict()
