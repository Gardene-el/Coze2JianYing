"""
make_clip_settings 工具处理器

为 ClipSettings 类生成字典
图像调节设置（镜像 pyJianYingDraft.ClipSettings）
对应 pyJianYingDraft 的 ClipSettings 类，用于控制片段的变换属性

此工具接收 ClipSettings 的所有参数（可选，使用原始默认值），
并返回一个包含提供的参数的字典。
"""

import json
from typing import NamedTuple, Optional, Dict, Any, List
from runtime import Args


# Input 类型定义
class Input(NamedTuple):
    """make_clip_settings 工具的输入参数（可选，有默认值的参数使用原始默认值）"""
    alpha: Optional[float] = 1.0  # 透明度 (0.0-1.0)
    rotation: Optional[float] = 0.0  # 旋转角度（度）
    scale_x: Optional[float] = 1.0  # X 轴缩放比例
    scale_y: Optional[float] = 1.0  # Y 轴缩放比例
    transform_x: Optional[float] = 0.0  # X 轴位置偏移
    transform_y: Optional[float] = 0.0  # Y 轴位置偏移


# Output 类型定义
class Output(NamedTuple):
    """make_clip_settings 工具的输出"""
    result: Dict[str, Any]  # ClipSettings 字典（错误时为空字典）
    success: bool           # 操作成功状态
    message: str            # 状态消息


def handler(args: Args[Input]) -> Output:
    """
    创建 ClipSettings 字典的主处理函数
    
    Args:
        args: 包含所有 ClipSettings 参数的输入参数（使用原始默认值）
        
    Returns:
        包含 ClipSettings 字典的 Output
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating ClipSettings dict")
    
    try:
        # 构建结果字典，只包含提供的参数或有默认值的参数
        result = {}
        if args.input.alpha is not None:
            result['alpha'] = args.input.alpha
        else:
            result['alpha'] = 1.0
        if args.input.rotation is not None:
            result['rotation'] = args.input.rotation
        else:
            result['rotation'] = 0.0
        if args.input.scale_x is not None:
            result['scale_x'] = args.input.scale_x
        else:
            result['scale_x'] = 1.0
        if args.input.scale_y is not None:
            result['scale_y'] = args.input.scale_y
        else:
            result['scale_y'] = 1.0
        if args.input.transform_x is not None:
            result['transform_x'] = args.input.transform_x
        else:
            result['transform_x'] = 0.0
        if args.input.transform_y is not None:
            result['transform_y'] = args.input.transform_y
        else:
            result['transform_y'] = 0.0
        
        if logger:
            logger.info(f"Successfully created ClipSettings dict with {len(result)} fields")
        
        return Output(
            result=result,
            success=True,
            message="ClipSettings 字典创建成功"
        )
        
    except Exception as e:
        error_msg = f"创建 ClipSettings 字典时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            result={},
            success=False,
            message=error_msg
        )

