"""
Make Caption Info Tool Handler

Creates a JSON string representation of caption/text configuration with all possible parameters.
This is a helper tool for add_captions - generates a single caption info string that can be
collected into an array and passed to add_captions.

Total parameters: 32 (4 required + 28 optional)
Based on pyJianYingDraft library's TextSegment and TextStyle.
Supports complete text styling, positioning, alignment, and animation configuration.
"""

import json
from typing import NamedTuple, Optional
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for make_caption_info tool"""
    # Required fields
    content: str                                # Text content/subtitle content
    start: int                                  # Start time in milliseconds
    end: int                                    # End time in milliseconds
    
    # Optional position and transform fields
    position_x: Optional[float] = 0.5           # X position (0.0-1.0, default 0.5 center)
    position_y: Optional[float] = 0.9           # Y position (0.0-1.0, default 0.9 bottom)
    scale: Optional[float] = 1.0                # Scale (default 1.0)
    rotation: Optional[float] = 0.0             # Rotation angle (default 0.0)
    opacity: Optional[float] = 1.0              # Opacity (0.0-1.0, default 1.0)
    
    # Optional text style fields
    font_family: Optional[str] = "默认"         # Font family (default "默认")
    font_size: Optional[int] = 48               # Font size (default 48)
    font_weight: Optional[str] = "normal"       # Font weight: "normal", "bold"
    font_style: Optional[str] = "normal"        # Font style: "normal", "italic"
    color: Optional[str] = "#FFFFFF"            # Text color (default "#FFFFFF" white)
    
    # Optional text stroke/outline fields
    stroke_enabled: Optional[bool] = False      # Enable stroke (default False)
    stroke_color: Optional[str] = "#000000"     # Stroke color (default "#000000" black)
    stroke_width: Optional[int] = 2             # Stroke width (default 2)
    
    # Optional text shadow fields
    shadow_enabled: Optional[bool] = False      # Enable shadow (default False)
    shadow_color: Optional[str] = "#000000"     # Shadow color (default "#000000" black)
    shadow_offset_x: Optional[int] = 2          # Shadow X offset (default 2)
    shadow_offset_y: Optional[int] = 2          # Shadow Y offset (default 2)
    shadow_blur: Optional[int] = 4              # Shadow blur (default 4)
    
    # Optional text background fields
    background_enabled: Optional[bool] = False  # Enable background (default False)
    background_color: Optional[str] = "#000000" # Background color (default "#000000" black)
    background_opacity: Optional[float] = 0.5   # Background opacity (0.0-1.0, default 0.5)
    
    # Optional alignment field
    alignment: Optional[str] = "center"         # Text alignment: "left", "center", "right"
    
    # Optional animation fields
    intro_animation: Optional[str] = None       # Intro animation type (e.g., "淡入")
    outro_animation: Optional[str] = None       # Outro animation type (e.g., "淡出")
    loop_animation: Optional[str] = None        # Loop animation type


class Output(NamedTuple):
    """Output for make_caption_info tool"""
    caption_info_string: str                    # JSON string representation of caption info
    success: bool = True                        # Operation success status
    message: str = "字幕信息字符串生成成功"       # Status message


def handler(args: Args[Input]) -> Output:
    """
    Main handler function for creating caption info string
    
    Args:
        args: Input arguments containing all caption parameters
        
    Returns:
        Output containing the JSON string representation of caption info
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating caption info string for content: {args.input.content[:50]}...")
    
    try:
        # Validate required parameters
        if not args.input.content:
            return Output(
                caption_info_string="",
                success=False,
                message="缺少必需的 content 参数"
            )
        
        if args.input.start is None:
            return Output(
                caption_info_string="",
                success=False,
                message="缺少必需的 start 参数"
            )
        
        if args.input.end is None:
            return Output(
                caption_info_string="",
                success=False,
                message="缺少必需的 end 参数"
            )
        
        # Validate time range
        if args.input.start < 0:
            return Output(
                caption_info_string="",
                success=False,
                message="start 时间不能为负数"
            )
        
        if args.input.end <= args.input.start:
            return Output(
                caption_info_string="",
                success=False,
                message="end 时间必须大于 start 时间"
            )
        
        # Validate numeric ranges
        if not (0.0 <= args.input.position_x <= 1.0):
            return Output(
                caption_info_string="",
                success=False,
                message="position_x 必须在 0.0 到 1.0 之间"
            )
        
        if not (0.0 <= args.input.position_y <= 1.0):
            return Output(
                caption_info_string="",
                success=False,
                message="position_y 必须在 0.0 到 1.0 之间"
            )
        
        if not (0.0 <= args.input.opacity <= 1.0):
            return Output(
                caption_info_string="",
                success=False,
                message="opacity 必须在 0.0 到 1.0 之间"
            )
        
        if not (0.0 <= args.input.background_opacity <= 1.0):
            return Output(
                caption_info_string="",
                success=False,
                message="background_opacity 必须在 0.0 到 1.0 之间"
            )
        
        # Validate text alignment
        valid_alignments = ["left", "center", "right"]
        if args.input.alignment not in valid_alignments:
            return Output(
                caption_info_string="",
                success=False,
                message=f"alignment 必须是以下值之一: {', '.join(valid_alignments)}"
            )
        
        # Validate font weight and style
        valid_weights = ["normal", "bold"]
        if args.input.font_weight not in valid_weights:
            return Output(
                caption_info_string="",
                success=False,
                message=f"font_weight 必须是以下值之一: {', '.join(valid_weights)}"
            )
        
        valid_styles = ["normal", "italic"]
        if args.input.font_style not in valid_styles:
            return Output(
                caption_info_string="",
                success=False,
                message=f"font_style 必须是以下值之一: {', '.join(valid_styles)}"
            )
        
        # Build caption info dictionary with all parameters
        caption_info = {
            "content": args.input.content,
            "start": args.input.start,
            "end": args.input.end
        }
        
        # Add optional parameters only if they are not default values
        # This keeps the output clean and only includes specified parameters
        
        # Position and transform (only add if not default values)
        if args.input.position_x != 0.5:
            caption_info["position_x"] = args.input.position_x
        if args.input.position_y != 0.9:
            caption_info["position_y"] = args.input.position_y
        if args.input.scale != 1.0:
            caption_info["scale"] = args.input.scale
        if args.input.rotation != 0.0:
            caption_info["rotation"] = args.input.rotation
        if args.input.opacity != 1.0:
            caption_info["opacity"] = args.input.opacity
        
        # Text style (only add if not default values)
        if args.input.font_family != "默认":
            caption_info["font_family"] = args.input.font_family
        if args.input.font_size != 48:
            caption_info["font_size"] = args.input.font_size
        if args.input.font_weight != "normal":
            caption_info["font_weight"] = args.input.font_weight
        if args.input.font_style != "normal":
            caption_info["font_style"] = args.input.font_style
        if args.input.color != "#FFFFFF":
            caption_info["color"] = args.input.color
        
        # Stroke/outline
        if args.input.stroke_enabled:
            caption_info["stroke_enabled"] = args.input.stroke_enabled
            if args.input.stroke_color != "#000000":
                caption_info["stroke_color"] = args.input.stroke_color
            if args.input.stroke_width != 2:
                caption_info["stroke_width"] = args.input.stroke_width
        
        # Shadow
        if args.input.shadow_enabled:
            caption_info["shadow_enabled"] = args.input.shadow_enabled
            if args.input.shadow_color != "#000000":
                caption_info["shadow_color"] = args.input.shadow_color
            if args.input.shadow_offset_x != 2:
                caption_info["shadow_offset_x"] = args.input.shadow_offset_x
            if args.input.shadow_offset_y != 2:
                caption_info["shadow_offset_y"] = args.input.shadow_offset_y
            if args.input.shadow_blur != 4:
                caption_info["shadow_blur"] = args.input.shadow_blur
        
        # Background
        if args.input.background_enabled:
            caption_info["background_enabled"] = args.input.background_enabled
            if args.input.background_color != "#000000":
                caption_info["background_color"] = args.input.background_color
            if args.input.background_opacity != 0.5:
                caption_info["background_opacity"] = args.input.background_opacity
        
        # Alignment
        if args.input.alignment != "center":
            caption_info["alignment"] = args.input.alignment
        
        # Animations
        if args.input.intro_animation is not None:
            caption_info["intro_animation"] = args.input.intro_animation
        if args.input.outro_animation is not None:
            caption_info["outro_animation"] = args.input.outro_animation
        if args.input.loop_animation is not None:
            caption_info["loop_animation"] = args.input.loop_animation
        
        # Convert to JSON string without extra whitespace for compact representation
        caption_info_string = json.dumps(caption_info, ensure_ascii=False, separators=(',', ':'))
        
        if logger:
            logger.info(f"Successfully created caption info string: {len(caption_info_string)} characters")
        
        return Output(
            caption_info_string=caption_info_string,
            success=True,
            message="字幕信息字符串生成成功"
        )
        
    except Exception as e:
        error_msg = f"生成字幕信息字符串时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            caption_info_string="",
            success=False,
            message=error_msg
        )
