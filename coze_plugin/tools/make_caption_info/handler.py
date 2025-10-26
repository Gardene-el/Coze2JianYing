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
from typing import NamedTuple, Optional, Dict, Any
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for make_caption_info tool"""
    # Required fields
    content: str                                # Text content/subtitle content
    start: int                                  # Start time in milliseconds
    end: int                                    # End time in milliseconds
    
    # Optional position and transform fields
    position_x: Optional[float] = 0.5           # X position (-1.0 to 1.0, default 0.5 center-right)
    position_y: Optional[float] = -0.9          # Y position (-1.0 to 1.0, default -0.9 bottom)
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



def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    Main handler function for creating caption info string
    
    Args:
        args: Input arguments containing all caption parameters
        
    Returns:
        Dict containing the JSON string representation of caption info
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating caption info string for content: {args.input.content[:50]}...")
    
    try:
        # Validate required parameters
        if not args.input.content:
            return {
                "caption_info_string": "",
                "success": False,
                "message": "缺少必需的 content 参数"
            }
        
        if args.input.start is None:
            return {
                "caption_info_string": "",
                "success": False,
                "message": "缺少必需的 start 参数"
            }
        
        if args.input.end is None:
            return {
                "caption_info_string": "",
                "success": False,
                "message": "缺少必需的 end 参数"
            }
        
        # Validate time range
        if args.input.start < 0:
            return {
                "caption_info_string": "",
                "success": False,
                "message": "start 时间不能为负数"
            }
        
        if args.input.end <= args.input.start:
            return {
                "caption_info_string": "",
                "success": False,
                "message": "end 时间必须大于 start 时间"
            }
        
        # Validate numeric ranges (handle None values with defaults)
        position_x = args.input.position_x if args.input.position_x is not None else 0.5
        position_y = args.input.position_y if args.input.position_y is not None else -0.9
        opacity = args.input.opacity if args.input.opacity is not None else 1.0
        background_opacity = args.input.background_opacity if args.input.background_opacity is not None else 0.5
        
        if not (-1.0 <= position_x <= 1.0):
            return {
                "caption_info_string": "",
                "success": False,
                "message": "position_x 必须在 -1.0 到 1.0 之间"
            }
        
        if not (-1.0 <= position_y <= 1.0):
            return {
                "caption_info_string": "",
                "success": False,
                "message": "position_y 必须在 -1.0 到 1.0 之间"
            }
        
        if not (0.0 <= opacity <= 1.0):
            return {
                "caption_info_string": "",
                "success": False,
                "message": "opacity 必须在 0.0 到 1.0 之间"
            }
        
        if not (0.0 <= background_opacity <= 1.0):
            return {
                "caption_info_string": "",
                "success": False,
                "message": "background_opacity 必须在 0.0 到 1.0 之间"
            }
        
        # Validate text alignment (handle None with default)
        alignment = args.input.alignment if args.input.alignment is not None else "center"
        valid_alignments = ["left", "center", "right"]
        if alignment not in valid_alignments:
            return {
                "caption_info_string": "",
                "success": False,
                "message": f"alignment 必须是以下值之一: {', '.join(valid_alignments)}"
            }
        
        # Validate font weight and style (handle None with defaults)
        font_weight = args.input.font_weight if args.input.font_weight is not None else "normal"
        valid_weights = ["normal", "bold"]
        if font_weight not in valid_weights:
            return {
                "caption_info_string": "",
                "success": False,
                "message": f"font_weight 必须是以下值之一: {', '.join(valid_weights)}"
            }
        
        font_style = args.input.font_style if args.input.font_style is not None else "normal"
        valid_styles = ["normal", "italic"]
        if font_style not in valid_styles:
            return {
                "caption_info_string": "",
                "success": False,
                "message": f"font_style 必须是以下值之一: {', '.join(valid_styles)}"
            }
        
        # Build caption info dictionary with all parameters
        caption_info = {
            "content": args.input.content,
            "start": args.input.start,
            "end": args.input.end
        }
        
        # Add optional parameters only if they are not default values
        # This keeps the output clean and only includes specified parameters
        # Use getattr with defaults to handle None values from Coze
        
        # Position and transform (only add if not default values)
        position_x_val = args.input.position_x if args.input.position_x is not None else 0.5
        if position_x_val != 0.5:
            caption_info["position_x"] = position_x_val
            
        position_y_val = args.input.position_y if args.input.position_y is not None else -0.9
        if position_y_val != -0.9:
            caption_info["position_y"] = position_y_val
            
        scale_val = args.input.scale if args.input.scale is not None else 1.0
        if scale_val != 1.0:
            caption_info["scale"] = scale_val
            
        rotation_val = args.input.rotation if args.input.rotation is not None else 0.0
        if rotation_val != 0.0:
            caption_info["rotation"] = rotation_val
            
        opacity_val = args.input.opacity if args.input.opacity is not None else 1.0
        if opacity_val != 1.0:
            caption_info["opacity"] = opacity_val
        
        # Text style (only add if not default values)
        font_family_val = args.input.font_family if args.input.font_family is not None else "默认"
        if font_family_val != "默认":
            caption_info["font_family"] = font_family_val
            
        font_size_val = args.input.font_size if args.input.font_size is not None else 48
        if font_size_val != 48:
            caption_info["font_size"] = font_size_val
            
        font_weight_val = args.input.font_weight if args.input.font_weight is not None else "normal"
        if font_weight_val != "normal":
            caption_info["font_weight"] = font_weight_val
            
        font_style_val = args.input.font_style if args.input.font_style is not None else "normal"
        if font_style_val != "normal":
            caption_info["font_style"] = font_style_val
            
        color_val = args.input.color if args.input.color is not None else "#FFFFFF"
        if color_val != "#FFFFFF":
            caption_info["color"] = color_val
        
        # Stroke/outline
        stroke_enabled_val = args.input.stroke_enabled if args.input.stroke_enabled is not None else False
        if stroke_enabled_val:
            caption_info["stroke_enabled"] = stroke_enabled_val
            
            stroke_color_val = args.input.stroke_color if args.input.stroke_color is not None else "#000000"
            if stroke_color_val != "#000000":
                caption_info["stroke_color"] = stroke_color_val
                
            stroke_width_val = args.input.stroke_width if args.input.stroke_width is not None else 2
            if stroke_width_val != 2:
                caption_info["stroke_width"] = stroke_width_val
        
        # Shadow
        shadow_enabled_val = args.input.shadow_enabled if args.input.shadow_enabled is not None else False
        if shadow_enabled_val:
            caption_info["shadow_enabled"] = shadow_enabled_val
            
            shadow_color_val = args.input.shadow_color if args.input.shadow_color is not None else "#000000"
            if shadow_color_val != "#000000":
                caption_info["shadow_color"] = shadow_color_val
                
            shadow_offset_x_val = args.input.shadow_offset_x if args.input.shadow_offset_x is not None else 2
            if shadow_offset_x_val != 2:
                caption_info["shadow_offset_x"] = shadow_offset_x_val
                
            shadow_offset_y_val = args.input.shadow_offset_y if args.input.shadow_offset_y is not None else 2
            if shadow_offset_y_val != 2:
                caption_info["shadow_offset_y"] = shadow_offset_y_val
                
            shadow_blur_val = args.input.shadow_blur if args.input.shadow_blur is not None else 4
            if shadow_blur_val != 4:
                caption_info["shadow_blur"] = shadow_blur_val
        
        # Background
        background_enabled_val = args.input.background_enabled if args.input.background_enabled is not None else False
        if background_enabled_val:
            caption_info["background_enabled"] = background_enabled_val
            
            background_color_val = args.input.background_color if args.input.background_color is not None else "#000000"
            if background_color_val != "#000000":
                caption_info["background_color"] = background_color_val
                
            background_opacity_val = args.input.background_opacity if args.input.background_opacity is not None else 0.5
            if background_opacity_val != 0.5:
                caption_info["background_opacity"] = background_opacity_val
        
        # Alignment
        alignment_val = args.input.alignment if args.input.alignment is not None else "center"
        if alignment_val != "center":
            caption_info["alignment"] = alignment_val
        
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
        
        return {
            "caption_info_string": caption_info_string,
            "success": True,
            "message": "字幕信息字符串生成成功"
            }
        
    except Exception as e:
        error_msg = f"生成字幕信息字符串时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return {
            "caption_info_string": "",
            "success": False,
            "message": error_msg
            }
