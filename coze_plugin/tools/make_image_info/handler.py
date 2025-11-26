"""
生成图片信息工具处理器

创建包含所有可能参数的图片配置的 JSON 字符串表示。
这是 add_images 的辅助工具 - 生成单个图片信息字符串，可以
收集到数组中并传递给 add_images。

总参数数： 25 (3 必需 + 22 可选)
基于 pyJianYingDraft 库的 VideoSegment、ClipSettings 和 CropSettings。
Note: width/height removed as they are non-functional metadata fields.
Note: flip_horizontal/flip_vertical removed as they don't apply to static images per draft_generator_interface specification.
"""

import json
from typing import NamedTuple, Optional, Dict, Any
from runtime import Args


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """make_image_info 工具的输入参数"""
    # 必需字段
    image_url: str                              # 图片 URL
    start: int                                  # 开始时间（毫秒）
    end: int                                    # 结束时间（毫秒）
    
    # 可选变换字段
    position_x: Optional[float] = 0.0           # X 位置（默认 0.0）
    position_y: Optional[float] = 0.0           # Y 位置（默认 0.0）
    scale_x: Optional[float] = 1.0              # X 缩放（默认 1.0）
    scale_y: Optional[float] = 1.0              # Y 缩放（默认 1.0）
    rotation: Optional[float] = 0.0             # 旋转角度（默认 0.0）
    opacity: Optional[float] = 1.0              # 不透明度（0.0-1.0，默认 1.0）
    
    # 可选裁剪字段
    crop_enabled: Optional[bool] = False        # 启用裁剪（默认 False）
    crop_left: Optional[float] = 0.0            # 裁剪左侧（0.0-1.0）
    crop_top: Optional[float] = 0.0             # 裁剪顶部（0.0-1.0）
    crop_right: Optional[float] = 1.0           # 裁剪右侧（0.0-1.0）
    crop_bottom: Optional[float] = 1.0          # 裁剪底部（0.0-1.0）
    
    # 可选特效字段
    filter_type: Optional[str] = None           # 滤镜类型（例如"暖冬"）
    filter_intensity: Optional[float] = 1.0     # 滤镜强度（0.0-1.0）
    transition_type: Optional[str] = None       # 转场类型
    transition_duration: Optional[int] = 500    # 转场时长（毫秒）
    
    # 可选背景字段
    background_blur: Optional[bool] = False     # 背景模糊（默认 False）
    background_color: Optional[str] = None      # 背景颜色
    fit_mode: Optional[str] = "fit"             # 适配模式: "fit", "fill", "stretch"
    
    # 可选动画字段
    in_animation: Optional[str] = None          # 入场动画类型 (e.g., "轻微放大")
    in_animation_duration: Optional[int] = 500  # 入场动画时长 in ms
    outro_animation: Optional[str] = None       # 出场动画类型
    outro_animation_duration: Optional[int] = 500  # 出场动画时长 in ms


class Output(NamedTuple):
    """make_image_info 工具的输出"""
    image_info_string: str    # 图片信息的 JSON 字符串表示
    success: bool             # Operation success status
    message: str              # Status message


def handler(args: Args[Input]) -> Output:
    """
    创建图片信息字符串的主处理函数
    
    Args:
        args: 包含所有图片参数的输入参数
        
    Returns:
        Dict containing the 图片信息的 JSON 字符串表示
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating image info string for: {args.input.image_url}")
    
    try:
        # 验证必需参数
        if not args.input.image_url:
            return Output(
                image_info_string="",
                success=False,
                message="缺少必需的 image_url 参数"
            )._asdict()
        
        if args.input.start is None:
            return Output(
                image_info_string="",
                success=False,
                message="缺少必需的 start 参数"
            )._asdict()
        
        if args.input.end is None:
            return Output(
                image_info_string="",
                success=False,
                message="缺少必需的 end 参数"
            )._asdict()
        
        # 验证时间范围
        if args.input.start < 0:
            return Output(
                image_info_string="",
                success=False,
                message="start 时间不能为负数"
            )._asdict()
        
        if args.input.end <= args.input.start:
            return Output(
                image_info_string="",
                success=False,
                message="end 时间必须大于 start 时间"
            )._asdict()
        
        # 使用所有参数构建图片信息字典
        image_info = {
            "image_url": args.input.image_url,
            "start": args.input.start,
            "end": args.input.end
        }
        
        # Add 可选 parameters only if they are not None
        # 这使输出保持清洁，仅包含指定的参数
        
        # 变换（仅在非 None 且非默认值时添加）
        if args.input.position_x is not None and args.input.position_x != 0.0:
            image_info["position_x"] = args.input.position_x
        if args.input.position_y is not None and args.input.position_y != 0.0:
            image_info["position_y"] = args.input.position_y
        if args.input.scale_x is not None and args.input.scale_x != 1.0:
            image_info["scale_x"] = args.input.scale_x
        if args.input.scale_y is not None and args.input.scale_y != 1.0:
            image_info["scale_y"] = args.input.scale_y
        if args.input.rotation is not None and args.input.rotation != 0.0:
            image_info["rotation"] = args.input.rotation
        if args.input.opacity is not None and args.input.opacity != 1.0:
            image_info["opacity"] = args.input.opacity
        
        # 裁剪
        if args.input.crop_enabled:
            image_info["crop_enabled"] = args.input.crop_enabled
            image_info["crop_left"] = args.input.crop_left
            image_info["crop_top"] = args.input.crop_top
            image_info["crop_right"] = args.input.crop_right
            image_info["crop_bottom"] = args.input.crop_bottom
        
        # 特效
        if args.input.filter_type is not None:
            image_info["filter_type"] = args.input.filter_type
            if args.input.filter_intensity != 1.0:
                image_info["filter_intensity"] = args.input.filter_intensity
        
        if args.input.transition_type is not None:
            image_info["transition_type"] = args.input.transition_type
            if args.input.transition_duration != 500:
                image_info["transition_duration"] = args.input.transition_duration
        
        # 背景 (only add if not None and not default values)
        if args.input.background_blur:
            image_info["background_blur"] = args.input.background_blur
        if args.input.background_color is not None:
            image_info["background_color"] = args.input.background_color
        if args.input.fit_mode is not None and args.input.fit_mode != "fit":
            image_info["fit_mode"] = args.input.fit_mode
        
        # 动画
        if args.input.in_animation is not None:
            image_info["in_animation"] = args.input.in_animation
            if args.input.in_animation_duration != 500:
                image_info["in_animation_duration"] = args.input.in_animation_duration
        
        if args.input.outro_animation is not None:
            image_info["outro_animation"] = args.input.outro_animation
            if args.input.outro_animation_duration != 500:
                image_info["outro_animation_duration"] = args.input.outro_animation_duration
        
        # 转换为 JSON 字符串，不带额外空格以进行紧凑表示
        image_info_string = json.dumps(image_info, ensure_ascii=False, separators=(',', ':'))
        
        if logger:
            logger.info(f"Successfully created image info string: {len(image_info_string)} characters")
        
        return Output(
            image_info_string=image_info_string,
            success=True,
            message="图片信息字符串生成成功"
        )._asdict()
        
    except Exception as e:
        error_msg = f"生成图片信息字符串时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            image_info_string="",
            success=False,
            message=error_msg
        )._asdict()
