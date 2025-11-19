"""
make_text_style 工具处理器

为 TextStyle 类生成对象
文本样式（镜像 pyJianYingDraft.TextStyle）
对应 pyJianYingDraft 的 TextStyle 类，用于控制文本的样式属性

此工具接收 TextStyle 的所有参数（可选，使用原始默认值），
并返回一个 TextStyle 对象。
"""

import json
from typing import NamedTuple, Optional, Dict, Any, List
from runtime import Args


# TextStyle 类型定义
class TextStyle(NamedTuple):
    """文本样式（镜像 pyJianYingDraft.TextStyle）
对应 pyJianYingDraft 的 TextStyle 类，用于控制文本的样式属性"""
    font_size: float  # 字体大小
    color: List[float]  # 文字颜色 RGB (0.0-1.0)
    bold: bool  # 是否加粗
    italic: bool  # 是否斜体
    underline: bool  # 是否下划线


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
    result: Optional[TextStyle]  # TextStyle 对象（错误时为 None）
    success: bool           # 操作成功状态
    message: str            # 状态消息


def handler(args: Args[Input]) -> Output:
    """
    创建 TextStyle 对象的主处理函数
    
    Args:
        args: 包含所有 TextStyle 参数的输入参数（使用原始默认值）
        
    Returns:
        包含 TextStyle 对象的 Output
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating TextStyle object")
    
    try:
        # 准备参数，使用提供的值或默认值
        font_size = args.input.font_size if args.input.font_size is not None else 24.0
        color = args.input.color if args.input.color is not None else [1.0, 1.0, 1.0]
        bold = args.input.bold if args.input.bold is not None else False
        italic = args.input.italic if args.input.italic is not None else False
        underline = args.input.underline if args.input.underline is not None else False
        
        # 创建 TextStyle 对象
        result = TextStyle(font_size=font_size, color=color, bold=bold, italic=italic, underline=underline)
        
        if logger:
            logger.info(f"Successfully created TextStyle object")
        
        return Output(
            result=result,
            success=True,
            message="TextStyle 对象创建成功"
        )
        
    except ValueError as e:
        # 参数验证错误
        error_msg = f"参数错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        # 返回 None 作为错误情况（Output 中 result 改为 Optional）
        return Output(
            result=None,
            success=False,
            message=error_msg
        )
    except Exception as e:
        error_msg = f"创建 TextStyle 对象时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            result=None,
            success=False,
            message=error_msg
        )

