"""
生成字幕信息工具处理器

创建包含所有可能参数的字幕/文本配置的 JSON 字符串表示。
这是 add_captions 的辅助工具 - 生成单个字幕信息字符串，可以
收集到数组中并传递给 add_captions。

总参数数： 32 (4 必需 + 28 可选)
基于 pyJianYingDraft 库的 TextSegment 和 TextStyle。
支持完整的文本样式、定位、对齐和动画配置。
"""

import json
from typing import NamedTuple, Optional, Dict, Any
from runtime import Args


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """make_caption_info 工具的输入参数"""
    # 必需字段
    content: str                                # 文本内容/subtitle content
    start: int                                  # 开始时间（毫秒）
    end: int                                    # 结束时间（毫秒）
    
    # 可选位置和变换字段
    position_x: Optional[float] = 0.5           # X 位置（-1.0 到 1.0，默认 0.5 居中偏右）
    position_y: Optional[float] = -0.9          # Y 位置（-1.0 到 1.0，默认 -0.9 底部）
    scale: Optional[float] = 1.0                # 缩放（默认 1.0）
    rotation: Optional[float] = 0.0             # 旋转角度（默认 0.0）
    opacity: Optional[float] = 1.0              # 不透明度（0.0-1.0，默认 1.0）
    
    # Optional text style fields
    font_family: Optional[str] = "默认"         # 字体系列 (default "默认")
    font_size: Optional[int] = 48               # 字体大小 (default 48)
    font_weight: Optional[str] = "normal"       # Font weight: "normal", "bold"
    font_style: Optional[str] = "normal"        # Font style: "normal", "italic"
    color: Optional[str] = "#FFFFFF"            # Text color (default "#FFFFFF" white)
    
    # Optional text stroke/outline fields
    stroke_enabled: Optional[bool] = False      # Enable stroke (default False)
    stroke_color: Optional[str] = "#000000"     # 描边颜色 (default "#000000" black)
    stroke_width: Optional[int] = 2             # 描边宽度 (default 2)
    
    # Optional text shadow fields
    shadow_enabled: Optional[bool] = False      # 启用阴影 (default False)
    shadow_color: Optional[str] = "#000000"     # 阴影颜色 (default "#000000" black)
    shadow_offset_x: Optional[int] = 2          # Shadow X offset (default 2)
    shadow_offset_y: Optional[int] = 2          # Shadow Y offset (default 2)
    shadow_blur: Optional[int] = 4              # Shadow blur (default 4)
    
    # Optional text background fields
    background_enabled: Optional[bool] = False  # 启用背景 (default False)
    background_color: Optional[str] = "#000000" # 背景颜色 (default "#000000" black)
    background_opacity: Optional[float] = 0.5   # 背景不透明度 (0.0-1.0, default 0.5)
    
    # Optional alignment field
    alignment: Optional[str] = "center"         # Text alignment: "left", "center", "right"
    
    # 可选动画字段
    intro_animation: Optional[str] = None       # 入场动画类型 (e.g., "淡入")
    outro_animation: Optional[str] = None       # 出场动画类型 (e.g., "淡出")
    loop_animation: Optional[str] = None        # 循环动画类型


class Output(NamedTuple):
    """make_caption_info 工具的输出"""
    caption_info_string: str  # 字幕信息的 JSON 字符串表示
    success: bool             # Operation success status
    message: str              # Status message


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    创建字幕信息字符串的主处理函数
    
    Args:
        args: 包含所有字幕参数的输入参数
        
    Returns:
        Dict containing the 字幕信息的 JSON 字符串表示
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating caption info string for content: {args.input.content[:50]}...")
    
    try:
        # 验证必需参数
        if not args.input.content:
            return Output(
                caption_info_string="",
                success=False,
                message="缺少必需的 content 参数"
            )._asdict()
        
        if args.input.start is None:
            return Output(
                caption_info_string="",
                success=False,
                message="缺少必需的 start 参数"
            )._asdict()
        
        if args.input.end is None:
            return Output(
                caption_info_string="",
                success=False,
                message="缺少必需的 end 参数"
            )._asdict()
        
        # 验证时间范围
        if args.input.start < 0:
            return Output(
                caption_info_string="",
                success=False,
                message="start 时间不能为负数"
            )._asdict()
        
        if args.input.end <= args.input.start:
            return Output(
                caption_info_string="",
                success=False,
                message="end 时间必须大于 start 时间"
            )._asdict()
        
        # Validate numeric ranges (handle None values with defaults)
        position_x = args.input.position_x if args.input.position_x is not None else 0.5
        position_y = args.input.position_y if args.input.position_y is not None else -0.9
        opacity = args.input.opacity if args.input.opacity is not None else 1.0
        background_opacity = args.input.background_opacity if args.input.background_opacity is not None else 0.5
        
        if not (-1.0 <= position_x <= 1.0):
            return Output(
                caption_info_string="",
                success=False,
                message="position_x 必须在 -1.0 到 1.0 之间"
            )._asdict()
        
        if not (-1.0 <= position_y <= 1.0):
            return Output(
                caption_info_string="",
                success=False,
                message="position_y 必须在 -1.0 到 1.0 之间"
            )._asdict()
        
        if not (0.0 <= opacity <= 1.0):
            return Output(
                caption_info_string="",
                success=False,
                message="opacity 必须在 0.0 到 1.0 之间"
            )._asdict()
        
        if not (0.0 <= background_opacity <= 1.0):
            return Output(
                caption_info_string="",
                success=False,
                message="background_opacity 必须在 0.0 到 1.0 之间"
            )._asdict()
        
        # Validate text alignment (handle None with default)
        alignment = args.input.alignment if args.input.alignment is not None else "center"
        valid_alignments = ["left", "center", "right"]
        if alignment not in valid_alignments:
            return Output(
                caption_info_string="",
                success=False,
                message=f"alignment 必须是以下值之一: {', '.join(valid_alignments)}"
            )._asdict()
        
        # Validate font weight and style (handle None with defaults)
        font_weight = args.input.font_weight if args.input.font_weight is not None else "normal"
        valid_weights = ["normal", "bold"]
        if font_weight not in valid_weights:
            return Output(
                caption_info_string="",
                success=False,
                message=f"font_weight 必须是以下值之一: {', '.join(valid_weights)}"
            )._asdict()
        
        font_style = args.input.font_style if args.input.font_style is not None else "normal"
        valid_styles = ["normal", "italic"]
        if font_style not in valid_styles:
            return Output(
                caption_info_string="",
                success=False,
                message=f"font_style 必须是以下值之一: {', '.join(valid_styles)}"
            )._asdict()
        
        # 使用所有参数构建字幕信息字典
        caption_info = {
            "content": args.input.content,
            "start": args.input.start,
            "end": args.input.end
        }
        
        # Add 可选 parameters only if they are not default values
        # 这使输出保持清洁，仅包含指定的参数
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
        
        # 背景
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
        
        # 动画
        if args.input.intro_animation is not None:
            caption_info["intro_animation"] = args.input.intro_animation
        if args.input.outro_animation is not None:
            caption_info["outro_animation"] = args.input.outro_animation
        if args.input.loop_animation is not None:
            caption_info["loop_animation"] = args.input.loop_animation
        
        # 转换为 JSON 字符串，不带额外空格以进行紧凑表示
        caption_info_string = json.dumps(caption_info, ensure_ascii=False, separators=(',', ':'))
        
        if logger:
            logger.info(f"Successfully created caption info string: {len(caption_info_string)} characters")
        
        return Output(
            caption_info_string=caption_info_string,
            success=True,
            message="字幕信息字符串生成成功"
        )._asdict()
        
    except Exception as e:
        error_msg = f"生成字幕信息字符串时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            caption_info_string="",
            success=False,
            message=error_msg
        )._asdict()
