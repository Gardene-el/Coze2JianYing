"""
Make Image Info Tool Handler

Creates a JSON string representation of image configuration with all possible parameters.
This is a helper tool for add_images - generates a single image info string that can be
collected into an array and passed to add_images.
"""

import json
from typing import NamedTuple, Optional
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for make_image_info tool"""
    # Required fields
    image_url: str                              # Image URL
    start: int                                  # Start time in milliseconds
    end: int                                    # End time in milliseconds
    
    # Optional dimension fields
    width: Optional[int] = None                 # Image width
    height: Optional[int] = None                # Image height
    
    # Optional transform fields
    position_x: Optional[float] = 0.0           # X position (default 0.0)
    position_y: Optional[float] = 0.0           # Y position (default 0.0)
    scale_x: Optional[float] = 1.0              # X scale (default 1.0)
    scale_y: Optional[float] = 1.0              # Y scale (default 1.0)
    rotation: Optional[float] = 0.0             # Rotation angle (default 0.0)
    opacity: Optional[float] = 1.0              # Opacity (0.0-1.0, default 1.0)
    
    # Optional crop fields
    crop_enabled: Optional[bool] = False        # Enable cropping (default False)
    crop_left: Optional[float] = 0.0            # Crop left (0.0-1.0)
    crop_top: Optional[float] = 0.0             # Crop top (0.0-1.0)
    crop_right: Optional[float] = 1.0           # Crop right (0.0-1.0)
    crop_bottom: Optional[float] = 1.0          # Crop bottom (0.0-1.0)
    
    # Optional effect fields
    filter_type: Optional[str] = None           # Filter type (e.g., "暖冬")
    filter_intensity: Optional[float] = 1.0     # Filter intensity (0.0-1.0)
    transition_type: Optional[str] = None       # Transition type
    transition_duration: Optional[int] = 500    # Transition duration in ms
    
    # Optional background fields
    background_blur: Optional[bool] = False     # Background blur (default False)
    background_color: Optional[str] = None      # Background color
    fit_mode: Optional[str] = "fit"             # Fit mode: "fit", "fill", "stretch"
    
    # Optional animation fields
    in_animation: Optional[str] = None          # Intro animation type (e.g., "轻微放大")
    in_animation_duration: Optional[int] = 500  # Intro animation duration in ms
    outro_animation: Optional[str] = None       # Outro animation type
    outro_animation_duration: Optional[int] = 500  # Outro animation duration in ms


class Output(NamedTuple):
    """Output for make_image_info tool"""
    image_info_string: str                      # JSON string representation of image info
    success: bool = True                        # Operation success status
    message: str = "图片信息字符串生成成功"       # Status message


def handler(args: Args[Input]) -> Output:
    """
    Main handler function for creating image info string
    
    Args:
        args: Input arguments containing all image parameters
        
    Returns:
        Output containing the JSON string representation of image info
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating image info string for: {args.input.image_url}")
    
    try:
        # Validate required parameters
        if not args.input.image_url:
            return Output(
                image_info_string="",
                success=False,
                message="缺少必需的 image_url 参数"
            )
        
        if args.input.start is None:
            return Output(
                image_info_string="",
                success=False,
                message="缺少必需的 start 参数"
            )
        
        if args.input.end is None:
            return Output(
                image_info_string="",
                success=False,
                message="缺少必需的 end 参数"
            )
        
        # Validate time range
        if args.input.start < 0:
            return Output(
                image_info_string="",
                success=False,
                message="start 时间不能为负数"
            )
        
        if args.input.end <= args.input.start:
            return Output(
                image_info_string="",
                success=False,
                message="end 时间必须大于 start 时间"
            )
        
        # Build image info dictionary with all parameters
        image_info = {
            "image_url": args.input.image_url,
            "start": args.input.start,
            "end": args.input.end
        }
        
        # Add optional parameters only if they are not None
        # This keeps the output clean and only includes specified parameters
        
        # Dimensions
        if args.input.width is not None:
            image_info["width"] = args.input.width
        if args.input.height is not None:
            image_info["height"] = args.input.height
        
        # Transform (only add if not default values)
        if args.input.position_x != 0.0:
            image_info["position_x"] = args.input.position_x
        if args.input.position_y != 0.0:
            image_info["position_y"] = args.input.position_y
        if args.input.scale_x != 1.0:
            image_info["scale_x"] = args.input.scale_x
        if args.input.scale_y != 1.0:
            image_info["scale_y"] = args.input.scale_y
        if args.input.rotation != 0.0:
            image_info["rotation"] = args.input.rotation
        if args.input.opacity != 1.0:
            image_info["opacity"] = args.input.opacity
        
        # Crop
        if args.input.crop_enabled:
            image_info["crop_enabled"] = args.input.crop_enabled
            image_info["crop_left"] = args.input.crop_left
            image_info["crop_top"] = args.input.crop_top
            image_info["crop_right"] = args.input.crop_right
            image_info["crop_bottom"] = args.input.crop_bottom
        
        # Effects
        if args.input.filter_type is not None:
            image_info["filter_type"] = args.input.filter_type
            if args.input.filter_intensity != 1.0:
                image_info["filter_intensity"] = args.input.filter_intensity
        
        if args.input.transition_type is not None:
            image_info["transition_type"] = args.input.transition_type
            if args.input.transition_duration != 500:
                image_info["transition_duration"] = args.input.transition_duration
        
        # Background
        if args.input.background_blur:
            image_info["background_blur"] = args.input.background_blur
        if args.input.background_color is not None:
            image_info["background_color"] = args.input.background_color
        if args.input.fit_mode != "fit":
            image_info["fit_mode"] = args.input.fit_mode
        
        # Animations
        if args.input.in_animation is not None:
            image_info["in_animation"] = args.input.in_animation
            if args.input.in_animation_duration != 500:
                image_info["in_animation_duration"] = args.input.in_animation_duration
        
        if args.input.outro_animation is not None:
            image_info["outro_animation"] = args.input.outro_animation
            if args.input.outro_animation_duration != 500:
                image_info["outro_animation_duration"] = args.input.outro_animation_duration
        
        # Convert to JSON string without extra whitespace for compact representation
        image_info_string = json.dumps(image_info, ensure_ascii=False, separators=(',', ':'))
        
        if logger:
            logger.info(f"Successfully created image info string: {len(image_info_string)} characters")
        
        return Output(
            image_info_string=image_info_string,
            success=True,
            message="图片信息字符串生成成功"
        )
        
    except Exception as e:
        error_msg = f"生成图片信息字符串时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            image_info_string="",
            success=False,
            message=error_msg
        )
