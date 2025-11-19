"""
make_clip_settings 工具处理器

为 ClipSettings 类生成对象
图像调节设置（镜像 pyJianYingDraft.ClipSettings）
对应 pyJianYingDraft 的 ClipSettings 类，用于控制片段的变换属性

此工具接收 ClipSettings 的所有参数（可选，使用原始默认值），
并返回一个包含 ClipSettings 数据的字典。

注意：handler 直接返回 Dict[str, Any]，而不是 NamedTuple，
以确保在 Coze 平台中正确的 JSON 对象序列化。
"""

import json
from typing import NamedTuple, Optional, Dict, Any, List
from runtime import Args


# ClipSettings 类型定义
class ClipSettings(NamedTuple):
    """图像调节设置（镜像 pyJianYingDraft.ClipSettings）
对应 pyJianYingDraft 的 ClipSettings 类，用于控制片段的变换属性"""
    alpha: float  # 透明度 (0.0-1.0)
    rotation: float  # 旋转角度（度）
    scale_x: float  # X 轴缩放比例
    scale_y: float  # Y 轴缩放比例
    transform_x: float  # X 轴位置偏移
    transform_y: float  # Y 轴位置偏移


# Input 类型定义
class Input(NamedTuple):
    """make_clip_settings 工具的输入参数（可选，有默认值的参数使用原始默认值）"""
    alpha: Optional[float] = 1.0  # 透明度 (0.0-1.0)
    rotation: Optional[float] = 0.0  # 旋转角度（度）
    scale_x: Optional[float] = 1.0  # X 轴缩放比例
    scale_y: Optional[float] = 1.0  # Y 轴缩放比例
    transform_x: Optional[float] = 0.0  # X 轴位置偏移
    transform_y: Optional[float] = 0.0  # Y 轴位置偏移


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    创建 ClipSettings 对象的主处理函数
    
    Args:
        args: 包含所有 ClipSettings 参数的输入参数（使用原始默认值）
        
    Returns:
        Dict[str, Any]: 包含 result、success、message 字段的字典
            - result: ClipSettings 对象的字典表示（参数不完整时为 None）
            - success: 操作是否成功
            - message: 状态消息
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating ClipSettings object")
    
    try:
        # 准备参数，使用提供的值或默认值
        alpha = args.input.alpha if args.input.alpha is not None else 1.0
        rotation = args.input.rotation if args.input.rotation is not None else 0.0
        scale_x = args.input.scale_x if args.input.scale_x is not None else 1.0
        scale_y = args.input.scale_y if args.input.scale_y is not None else 1.0
        transform_x = args.input.transform_x if args.input.transform_x is not None else 0.0
        transform_y = args.input.transform_y if args.input.transform_y is not None else 0.0
        
        # 创建 ClipSettings 对象
        obj = ClipSettings(alpha=alpha, rotation=rotation, scale_x=scale_x, scale_y=scale_y, transform_x=transform_x, transform_y=transform_y)
        
        # 转换为字典以确保正确的 JSON 序列化
        result_dict = obj._asdict()
        
        if logger:
            logger.info(f"Successfully created ClipSettings object")
        
        return {
            'result': result_dict,
            'success': True,
            'message': 'ClipSettings 对象创建成功'
        }
        
    except Exception as e:
        error_msg = f"创建 ClipSettings 对象时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return {
            'result': None,
            'success': False,
            'message': error_msg
        }

