"""
生成视频信息工具处理器

创建包含所有可能参数的视频配置的 JSON 字符串表示。
这是 add_videos 的辅助工具 - 生成单个视频信息字符串，可以
收集到数组中并传递给 add_videos。

总参数数： 31 (3 必需 + 28 可选)
基于 pyJianYingDraft 库的 VideoSegment、ClipSettings 和 CropSettings。
"""

import json
from typing import NamedTuple, Optional, Dict, Any
from runtime import Args


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """make_video_info 工具的输入参数"""
    # 必需字段
    video_url: str                              # 视频 URL
    start: int                                  # 开始时间（毫秒）
    end: int                                    # 结束时间（毫秒）
    
    # 可选素材范围（用于剪裁视频）
    material_start: Optional[int] = None        # 素材开始时间（毫秒）
    material_end: Optional[int] = None          # 素材结束时间（毫秒）
    
    # 可选变换字段
    position_x: Optional[float] = 0.0           # X 位置（默认 0.0）
    position_y: Optional[float] = 0.0           # Y 位置（默认 0.0）
    scale_x: Optional[float] = 1.0              # X 缩放（默认 1.0）
    scale_y: Optional[float] = 1.0              # Y 缩放（默认 1.0）
    rotation: Optional[float] = 0.0             # 旋转角度（默认 0.0）
    opacity: Optional[float] = 1.0              # 不透明度（0.0-1.0，默认 1.0）
    flip_horizontal: Optional[bool] = False     # 水平翻转（默认 False）
    flip_vertical: Optional[bool] = False       # 垂直翻转（默认 False）
    
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
    
    # 可选速度控制字段
    speed: Optional[float] = 1.0                # 播放速度（0.5-2.0，默认 1.0）
    reverse: Optional[bool] = False             # 反向播放（默认 False）
    
    # 可选音频字段
    volume: Optional[float] = 1.0               # 音量级别（0.0-2.0，默认 1.0）
    change_pitch: Optional[bool] = False        # 速度变化时改变音高（默认 False）
    
    # 可选背景字段
    background_blur: Optional[bool] = False     # 背景模糊（默认 False）
    background_color: Optional[str] = None      # 背景颜色


class Output(NamedTuple):
    """make_video_info 工具的输出"""
    video_info_string: str    # 视频信息的 JSON 字符串表示
    success: bool             # Operation success status
    message: str              # Status message


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    创建视频信息字符串的主处理函数
    
    Args:
        args: 包含所有视频参数的输入参数
        
    Returns:
        Dict containing the 视频信息的 JSON 字符串表示
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating video info string for: {args.input.video_url}")
    
    try:
        # 验证必需参数
        if not args.input.video_url:
            return Output(
                video_info_string="",
                success=False,
                message="缺少必需的 video_url 参数"
            )._asdict()
        
        if args.input.start is None:
            return Output(
                video_info_string="",
                success=False,
                message="缺少必需的 start 参数"
            )._asdict()
        
        if args.input.end is None:
            return Output(
                video_info_string="",
                success=False,
                message="缺少必需的 end 参数"
            )._asdict()
        
        # 验证时间范围
        if args.input.start < 0:
            return Output(
                video_info_string="",
                success=False,
                message="start 时间不能为负数"
            )._asdict()
        
        if args.input.end <= args.input.start:
            return Output(
                video_info_string="",
                success=False,
                message="end 时间必须大于 start 时间"
            )._asdict()
        
        # 如果提供，验证素材范围
        if args.input.material_start is not None or args.input.material_end is not None:
            if args.input.material_start is None or args.input.material_end is None:
                return Output(
                    video_info_string="",
                    success=False,
                    message="material_start 和 material_end 必须同时提供"
                )._asdict()
            
            if args.input.material_start < 0:
                return Output(
                    video_info_string="",
                    success=False,
                    message="material_start 时间不能为负数"
                )._asdict()
            
            if args.input.material_end <= args.input.material_start:
                return Output(
                    video_info_string="",
                    success=False,
                    message="material_end 时间必须大于 material_start 时间"
                )._asdict()
        
        # 验证速度
        if args.input.speed is not None and (args.input.speed < 0.5 or args.input.speed > 2.0):
            return Output(
                video_info_string="",
                success=False,
                message="speed 必须在 0.5 到 2.0 之间"
            )._asdict()
        
        # 使用所有参数构建视频信息字典
        video_info = {
            "video_url": args.input.video_url,
            "start": args.input.start,
            "end": args.input.end
        }
        
        # 仅在非 None 或非默认值时添加可选参数
        # 这使输出保持清洁，仅包含指定的参数
        
        # 素材范围（仅在提供时添加）
        if args.input.material_start is not None and args.input.material_end is not None:
            video_info["material_start"] = args.input.material_start
            video_info["material_end"] = args.input.material_end
        
        # 变换（仅在非 None 且非默认值时添加）
        if args.input.position_x is not None and args.input.position_x != 0.0:
            video_info["position_x"] = args.input.position_x
        if args.input.position_y is not None and args.input.position_y != 0.0:
            video_info["position_y"] = args.input.position_y
        if args.input.scale_x is not None and args.input.scale_x != 1.0:
            video_info["scale_x"] = args.input.scale_x
        if args.input.scale_y is not None and args.input.scale_y != 1.0:
            video_info["scale_y"] = args.input.scale_y
        if args.input.rotation is not None and args.input.rotation != 0.0:
            video_info["rotation"] = args.input.rotation
        if args.input.opacity is not None and args.input.opacity != 1.0:
            video_info["opacity"] = args.input.opacity
        if args.input.flip_horizontal:
            video_info["flip_horizontal"] = args.input.flip_horizontal
        if args.input.flip_vertical:
            video_info["flip_vertical"] = args.input.flip_vertical
        
        # 裁剪
        if args.input.crop_enabled:
            video_info["crop_enabled"] = args.input.crop_enabled
            video_info["crop_left"] = args.input.crop_left
            video_info["crop_top"] = args.input.crop_top
            video_info["crop_right"] = args.input.crop_right
            video_info["crop_bottom"] = args.input.crop_bottom
        
        # 特效
        if args.input.filter_type is not None:
            video_info["filter_type"] = args.input.filter_type
            if args.input.filter_intensity != 1.0:
                video_info["filter_intensity"] = args.input.filter_intensity
        
        if args.input.transition_type is not None:
            video_info["transition_type"] = args.input.transition_type
            if args.input.transition_duration != 500:
                video_info["transition_duration"] = args.input.transition_duration
        
        # 速度控制
        if args.input.speed != 1.0:
            video_info["speed"] = args.input.speed
        if args.input.reverse:
            video_info["reverse"] = args.input.reverse
        
        # 音频
        if args.input.volume != 1.0:
            video_info["volume"] = args.input.volume
        if args.input.change_pitch:
            video_info["change_pitch"] = args.input.change_pitch
        
        # 背景
        if args.input.background_blur:
            video_info["background_blur"] = args.input.background_blur
        if args.input.background_color is not None:
            video_info["background_color"] = args.input.background_color
        
        # 转换为 JSON 字符串，不带额外空格以进行紧凑表示
        video_info_string = json.dumps(video_info, ensure_ascii=False, separators=(',', ':'))
        
        if logger:
            logger.info(f"Successfully created video info string: {len(video_info_string)} characters")
        
        return Output(
            video_info_string=video_info_string,
            success=True,
            message="视频信息字符串生成成功"
        )._asdict()
        
    except Exception as e:
        error_msg = f"生成视频信息字符串时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            video_info_string="",
            success=False,
            message=error_msg
        )._asdict()
