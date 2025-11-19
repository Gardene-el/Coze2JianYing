"""
make_text_style 工具处理器

为 TextStyle 类生成 Object 对象
文本样式（镜像 pyJianYingDraft.TextStyle）
对应 pyJianYingDraft 的 TextStyle 类，用于控制文本的样式属性

此工具接收 TextStyle 的所有参数（全部为可选），
并返回一个 Object（字典）表示。
"""

import json
from typing import NamedTuple, Optional, Dict, Any, List
from runtime import Args


# Input 类型定义
class Input(NamedTuple):
    """make_text_style 工具的输入参数（全部可选）"""
    font_size: Optional[float] = None  # 字体大小
    color: Optional[List[float]] = None  # 文字颜色 RGB (0.0-1.0)
    bold: Optional[bool] = None  # 是否加粗
    italic: Optional[bool] = None  # 是否斜体
    underline: Optional[bool] = None  # 是否下划线


# Output 类型定义
class Output(NamedTuple):
    """make_text_style 工具的输出"""
    result: Dict[str, Any]  # TextStyle 对象的字典表示
    success: bool           # 操作成功状态
    message: str            # 状态消息


def handler(args: Args[Input]) -> Output:
    """
    创建 TextStyle 对象的主处理函数
    
    Args:
        args: 包含所有 TextStyle 参数的输入参数（全部可选）
        
    Returns:
        包含 TextStyle 对象字典表示的 Output
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating TextStyle object")
    
    try:
        # 构建结果字典，仅包含提供的非 None 参数
        result = {}
        
        if args.input.font_size is not None:
            result['font_size'] = args.input.font_size
        if args.input.color is not None:
            result['color'] = args.input.color
        if args.input.bold is not None:
            result['bold'] = args.input.bold
        if args.input.italic is not None:
            result['italic'] = args.input.italic
        if args.input.underline is not None:
            result['underline'] = args.input.underline
        
        if logger:
            logger.info(f"Successfully created TextStyle object with {len(result)} fields")
        
        return Output(
            result=result,
            success=True,
            message="TextStyle 对象创建成功"
        )
        
    except Exception as e:
        error_msg = f"创建 TextStyle 对象时发生错误: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return Output(
            result={},
            success=False,
            message=error_msg
        )

