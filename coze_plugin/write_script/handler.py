"""
写入脚本工具处理器

向 /tmp 目录的 coze2jianying.py 脚本文件追加写入内容。
参考 raw_tools 中各个 handler 函数的写入方式实现。
"""

import os
from typing import Any, Dict, NamedTuple

from runtime import Args


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """输入参数 for write_script tool"""

    content: str  # 要写入的内容


# Output 现在返回 Dict[str, Any] 而不是 NamedTuple
# 这确保了在 Coze 平台中正确的 JSON 对象序列化


def ensure_coze2jianying_file() -> str:
    """
    确保 /tmp 目录下存在 coze2jianying.py 文件

    Returns:
        coze2jianying.py 文件的完整路径
    """
    file_path = "/tmp/coze2jianying.py"

    if not os.path.exists(file_path):
        # 创建初始文件内容
        initial_content = """# Coze2JianYing API 调用记录
# 此文件由 Coze 工具自动生成和更新
# 记录所有通过 Coze 工具调用的 API 操作

import asyncio
from app.schemas.segment_schemas import *

# API 调用记录将追加在下方
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(initial_content)

    return file_path


def append_content_to_file(file_path: str, content: str):
    """
    将内容追加到 coze2jianying.py 文件

    Args:
        file_path: coze2jianying.py 文件路径
        content: 要追加的内容
    """
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write("\n" + content + "\n")


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    写入脚本文件的主处理函数

    Args:
        args: 包含 content 的输入参数

    Returns:
        Dict containing success status and message
    """
    logger = getattr(args, "logger", None)

    if logger:
        logger.info(f"写入脚本，内容长度: {len(args.input.content)} 字符")

    try:
        # 获取参数
        content = getattr(args.input, "content", None)
        if content is None or content == "":
            error_msg = "写入内容不能为空"
            if logger:
                logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
            }

        # 确保文件存在并追加内容
        coze_file = ensure_coze2jianying_file()
        append_content_to_file(coze_file, content)

        success_message = "成功追加内容到脚本文件"

        if logger:
            logger.info(success_message)

        return {
            "success": True,
            "message": success_message,
        }

    except Exception as e:
        error_msg = f"写入脚本时发生意外错误: {str(e)}"
        if logger:
            logger.error(error_msg)

        return {
            "success": False,
            "message": error_msg,
        }
