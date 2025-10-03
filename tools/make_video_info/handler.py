"""
Make Video Info Tool Handler

Creates a JSON string representation of video configuration with all possible parameters.
This is a helper tool for add_videos - generates a single video info string that can be
collected into an array and passed to add_videos.

Total parameters: 31 (3 required + 28 optional)
Based on pyJianYingDraft library's VideoSegment, ClipSettings, and CropSettings.
"""

import json
from typing import NamedTuple, Optional, Dict, Any
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for make_video_info tool"""
    # Required fields
    video_url: str                              # Video URL
    start: int                                  # Start time in milliseconds
    end: int                                    # End time in milliseconds
    
    # Optional material range (for trimming video)
    material_start: Optional[int] = None        # Material start time in milliseconds
    material_end: Optional[int] = None          # Material end time in milliseconds
    
    # Optional transform fields
    position_x: Optional[float] = 0.0           # X position (default 0.0)
    position_y: Optional[float] = 0.0           # Y position (default 0.0)
    scale_x: Optional[float] = 1.0              # X scale (default 1.0)
    scale_y: Optional[float] = 1.0              # Y scale (default 1.0)
    rotation: Optional[float] = 0.0             # Rotation angle (default 0.0)
    opacity: Optional[float] = 1.0              # Opacity (0.0-1.0, default 1.0)
    flip_horizontal: Optional[bool] = False     # Flip horizontally (default False)
    flip_vertical: Optional[bool] = False       # Flip vertically (default False)
    
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
    
    # Optional speed control fields
    speed: Optional[float] = 1.0                # Playback speed (0.5-2.0, default 1.0)
    reverse: Optional[bool] = False             # Reverse playback (default False)
    
    # Optional audio fields
    volume: Optional[float] = 1.0               # Volume level (0.0-2.0, default 1.0)
    change_pitch: Optional[bool] = False        # Change pitch when speed changes (default False)
    
    # Optional background fields
    background_blur: Optional[bool] = False     # Background blur (default False)
    background_color: Optional[str] = None      # Background color


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    Main handler function for creating video info string
    
    Args:
        args: Input arguments containing all video parameters
        
    Returns:
        Dict containing the JSON string representation of video info
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating video info string for: {args.input.video_url}")
    
    try:
        # Validate required parameters
        if not args.input.video_url:
            return {
                "video_info_string": "",
                "success": False,
                "message": "缺少必需的 video_url 参数"
            }
        
        if args.input.start is None:
            return {
                "video_info_string": "",
                "success": False,
                "message": "缺少必需的 start 参数"
            }
        
        if args.input.end is None:
            return {
                "video_info_string": "",
                "success": False,
                "message": "缺少必需的 end 参数"
            }
        
        # Validate time range
        if args.input.start < 0:
            return {
                "video_info_string": "",
                "success": False,
                "message": "start 时间不能为负数"
            }
        
        if args.input.end <= args.input.start:
            return {
                "video_info_string": "",
                "success": False,
                "message": "end 时间必须大于 start 时间"
            }
        
        # Validate material range if provided
        if args.input.material_start is not None or args.input.material_end is not None:
            if args.input.material_start is None or args.input.material_end is None:
                return {
                    "video_info_string": "",
                    "success": False,
                    "message": "material_start 和 material_end 必须同时提供"
                }
            
            if args.input.material_start < 0:
                return {
                    "video_info_string": "",
                    "success": False,
                    "message": "material_start 时间不能为负数"
                }
            
            if args.input.material_end <= args.input.material_start:
                return {
                    "video_info_string": "",
                    "success": False,
                    "message": "material_end 时间必须大于 material_start 时间"
                }
        
        # Validate speed
        if args.input.speed is not None and (args.input.speed < 0.5 or args.input.speed > 2.0):
            return {
                "video_info_string": "",
                "success": False,
                "message": "speed 必须在 0.5 到 2.0 之间"
            }
        
        # Build video info dictionary with all parameters
        video_info = {
            "video_url": args.input.video_url,
            "start": args.input.start,
            "end": args.input.end
        }
        
        # Add optional parameters only if they are not None or not default values
        # This keeps the output clean and only includes specified parameters
        
        # Material range (only add if provided)
        if args.input.material_start is not None and args.input.material_end is not None:
            video_info["material_start"] = args.input.material_start
            video_info["material_end"] = args.input.material_end
        
        # Transform (only add if not default values)
        if args.input.position_x != 0.0:
            video_info["position_x"] = args.input.position_x
        if args.input.position_y != 0.0:
            video_info["position_y"] = args.input.position_y
        if args.input.scale_x != 1.0:
            video_info["scale_x"] = args.input.scale_x
        if args.input.scale_y != 1.0:
            video_info["scale_y"] = args.input.scale_y
        if args.input.rotation != 0.0:
            video_info["rotation"] = args.input.rotation
        if args.input.opacity != 1.0:
            video_info["opacity"] = args.input.opacity
        if args.input.flip_horizontal:
            video_info["flip_horizontal"] = args.input.flip_horizontal
        if args.input.flip_vertical:
            video_info["flip_vertical"] = args.input.flip_vertical
        
        # Crop
        if args.input.crop_enabled:
            video_info["crop_enabled"] = args.input.crop_enabled
            video_info["crop_left"] = args.input.crop_left
            video_info["crop_top"] = args.input.crop_top
            video_info["crop_right"] = args.input.crop_right
            video_info["crop_bottom"] = args.input.crop_bottom
        
        # Effects
        if args.input.filter_type is not None:
            video_info["filter_type"] = args.input.filter_type
            if args.input.filter_intensity != 1.0:
                video_info["filter_intensity"] = args.input.filter_intensity
        
        if args.input.transition_type is not None:
            video_info["transition_type"] = args.input.transition_type
            if args.input.transition_duration != 500:
                video_info["transition_duration"] = args.input.transition_duration
        
        # Speed control
        if args.input.speed != 1.0:
            video_info["speed"] = args.input.speed
        if args.input.reverse:
            video_info["reverse"] = args.input.reverse
        
        # Audio
        if args.input.volume != 1.0:
            video_info["volume"] = args.input.volume
        if args.input.change_pitch:
            video_info["change_pitch"] = args.input.change_pitch
        
        # Background
        if args.input.background_blur:
            video_info["background_blur"] = args.input.background_blur
        if args.input.background_color is not None:
            video_info["background_color"] = args.input.background_color
        
        # Convert to JSON string without extra whitespace for compact representation
        video_info_string = json.dumps(video_info, ensure_ascii=False, separators=(',', ':'))
        
        if logger:
            logger.info(f"Successfully created video info string: {len(video_info_string)} characters")
        
        return {
            "video_info_string": video_info_string,
            "success": True,
            "message": "视频信息字符串生成成功"
        }
        
    except Exception as e:
        error_msg = f"生成视频信息字符串时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return {
            "video_info_string": "",
            "success": False,
            "message": error_msg
        }
