"""
Make Effect Info Tool Handler

Creates a JSON string representation of effect configuration with all possible parameters.
This is a helper tool for add_effects - generates a single effect info string that can be
collected into an array and passed to add_effects.

Total parameters: 8 (3 required + 5 optional)
Based on EffectSegmentConfig from data_structures/draft_generator_interface/models.py
"""

import json
from typing import NamedTuple, Optional, Dict, Any, Dict, Any
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for make_effect_info tool"""
    # Required fields
    effect_type: str                            # Effect type name (e.g., "模糊", "锐化", "马赛克")
    start: int                                  # Start time in milliseconds
    end: int                                    # End time in milliseconds
    
    # Optional effect properties
    intensity: Optional[float] = 1.0            # Effect intensity (0.0-1.0, default 1.0)
    
    # Optional position (for localized effects)
    position_x: Optional[float] = None          # X position (for localized effects)
    position_y: Optional[float] = None          # Y position (for localized effects)
    scale: Optional[float] = 1.0                # Scale (default 1.0)
    
    # Optional custom properties
    properties: Optional[str] = None            # JSON string of custom effect properties


class Output(NamedTuple):
    """Output for make_effect_info tool"""
    effect_info_string: str   # JSON string representation of effect info
    success: bool             # Operation success status
    message: str              # Status message


def handler(args: Args[Input]) -> Output:
    """
    Main handler function for creating effect info string
    
    Args:
        args: Input arguments containing all effect parameters
        
    Returns:
        Dict containing the JSON string representation of effect info
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating effect info string for: {args.input.effect_type}")
    
    try:
        # Validate required parameters
        if not args.input.effect_type:
            return Output(
                effect_info_string="",
                success=False,
                message="缺少必需的 effect_type 参数"
            )
        
        if args.input.start is None:
            return Output(
                effect_info_string="",
                success=False,
                message="缺少必需的 start 参数"
            )
        
        if args.input.end is None:
            return Output(
                effect_info_string="",
                success=False,
                message="缺少必需的 end 参数"
            )
        
        # Validate time range
        if args.input.start < 0:
            return Output(
                effect_info_string="",
                success=False,
                message="start 时间不能为负数"
            )
        
        if args.input.end <= args.input.start:
            return Output(
                effect_info_string="",
                success=False,
                message="end 时间必须大于 start 时间"
            )
        
        # Build effect info dictionary with all parameters
        effect_info = {
            "effect_type": args.input.effect_type,
            "start": args.input.start,
            "end": args.input.end
        }
        
        # Add optional parameters only if they are not None or default values
        # This keeps the output clean and only includes specified parameters
        
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
                )
        
        # Convert to JSON string without extra whitespace for compact representation
        effect_info_string = json.dumps(effect_info, ensure_ascii=False, separators=(',', ':'))
        
        if logger:
            logger.info(f"Successfully created effect info string: {len(effect_info_string)} characters")
        
        return Output(
            effect_info_string=effect_info_string,
            success=True,
            message="特效信息字符串生成成功"
        )
        
    except Exception as e:
        error_msg = f"生成特效信息字符串时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            effect_info_string="",
            success=False,
            message=error_msg
        )
