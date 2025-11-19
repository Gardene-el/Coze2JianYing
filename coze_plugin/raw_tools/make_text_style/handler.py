"""
make_text_style 工具处理器

为 TextStyle 类生成字典
文本样式（镜像 pyJianYingDraft.TextStyle）
对应 pyJianYingDraft 的 TextStyle 类，用于控制文本的样式属性

此工具接收 TextStyle 的所有参数（可选，使用原始默认值），
并返回一个包含提供的参数的字典。
"""

import json
from typing import NamedTuple, Optional, Dict, Any, List
from runtime import Args


# Input 类型定义
class Input(NamedTuple):
    """make_text_style 工具的输入参数（可选，有默认值的参数使用原始默认值）"""
    font_size: Optional[float] = 24.0  # 字体大小
    color: Optional[List[float]] = [1.0, 1.0, 1.0]  # 文字颜色 RGB (0.0-1.0)
    bold: Optional[bool] = False  # 是否加粗
    italic: Optional[bool] = False  # 是否斜体
    underline: Optional[bool] = False  # 是否下划线


# Output 类型定义
class Output(NamedTuple):
    """make_text_style 工具的输出"""
    result: Dict[str, Any]  # TextStyle 字典（错误时为空字典）
    success: bool           # 操作成功状态
    message: str            # 状态消息


def handler(args: Args[Input]) -> Output:
    """
    创建 TextStyle 字典的主处理函数
    
    Args:
        args: 包含所有 TextStyle 参数的输入参数（使用原始默认值）
        
    Returns:
        包含 TextStyle 字典的 Output
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating TextStyle dict")
    
    try:
        # 构建结果字典，只包含提供的参数或有默认值的参数
        result = {}
        if args.input.font_size is not None:
            result['font_size'] = args.input.font_size
        else:
            result['font_size'] = 24.0
        if args.input.color is not None:
            result['color'] = args.input.color
        else:
            result['color'] = [1.0, 1.0, 1.0]
        if args.input.bold is not None:
            result['bold'] = args.input.bold
        else:
            result['bold'] = False
        if args.input.italic is not None:
            result['italic'] = args.input.italic
        else:
            result['italic'] = False
        if args.input.underline is not None:
            result['underline'] = args.input.underline
        else:
            result['underline'] = False
        
        if logger:
            logger.info(f"Successfully created TextStyle dict with {len(result)} fields")
        
        return Output(
            result=result,
            success=True,
            message="TextStyle 字典创建成功"
        )
        
    except Exception as e:
        error_msg = f"创建 TextStyle 字典时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            result={},
            success=False,
            message=error_msg
        )

