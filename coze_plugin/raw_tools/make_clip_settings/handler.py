"""
make_clip_settings 工具处理器

为 ClipSettings 类生成 Object 对象
图像调节设置（镜像 pyJianYingDraft.ClipSettings）
对应 pyJianYingDraft 的 ClipSettings 类，用于控制片段的变换属性

此工具接收 ClipSettings 的所有参数（全部为可选），
并返回一个 Object（字典）表示。
"""

import json
from typing import NamedTuple, Optional, Dict, Any, List
from runtime import Args


# Input 类型定义
class Input(NamedTuple):
    """make_clip_settings 工具的输入参数（全部可选）"""
    alpha: Optional[float] = None  # 透明度 (0.0-1.0)
    rotation: Optional[float] = None  # 旋转角度（度）
    scale_x: Optional[float] = None  # X 轴缩放比例
    scale_y: Optional[float] = None  # Y 轴缩放比例
    transform_x: Optional[float] = None  # X 轴位置偏移
    transform_y: Optional[float] = None  # Y 轴位置偏移


# Output 类型定义
class Output(NamedTuple):
    """make_clip_settings 工具的输出"""
    result: Dict[str, Any]  # ClipSettings 对象的字典表示
    success: bool           # 操作成功状态
    message: str            # 状态消息


def handler(args: Args[Input]) -> Output:
    """
    创建 ClipSettings 对象的主处理函数
    
    Args:
        args: 包含所有 ClipSettings 参数的输入参数（全部可选）
        
    Returns:
        包含 ClipSettings 对象字典表示的 Output
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating ClipSettings object")
    
    try:
        # 构建结果字典，仅包含提供的非 None 参数
        result = {}
        
        if args.input.alpha is not None:
            result['alpha'] = args.input.alpha
        if args.input.rotation is not None:
            result['rotation'] = args.input.rotation
        if args.input.scale_x is not None:
            result['scale_x'] = args.input.scale_x
        if args.input.scale_y is not None:
            result['scale_y'] = args.input.scale_y
        if args.input.transform_x is not None:
            result['transform_x'] = args.input.transform_x
        if args.input.transform_y is not None:
            result['transform_y'] = args.input.transform_y
        
        if logger:
            logger.info(f"Successfully created ClipSettings object with {len(result)} fields")
        
        return Output(
            result=result,
            success=True,
            message="ClipSettings 对象创建成功"
        )
        
    except Exception as e:
        error_msg = f"创建 ClipSettings 对象时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            result={},
            success=False,
            message=error_msg
        )

