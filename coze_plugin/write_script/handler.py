"""
写入脚本工具处理器

向 /tmp 目录的 coze2jianying.py 脚本文件写入内容。
支持追加模式和覆盖模式。
"""

import os
from typing import Any, Dict, NamedTuple

from runtime import Args


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """输入参数 for write_script tool"""

    content: str  # 要写入的内容
    mode: str = "append"  # 写入模式：append（追加）或 overwrite（覆盖）
    add_newline: bool = True  # 是否在内容末尾添加换行符


# Output 现在返回 Dict[str, Any] 而不是 NamedTuple
# 这确保了在 Coze 平台中正确的 JSON 对象序列化


def ensure_script_file_exists(file_path: str) -> tuple[bool, str]:
    """
    确保脚本文件存在，如果不存在则创建

    Args:
        file_path: 脚本文件的完整路径

    Returns:
        Tuple of (success, error_message)
    """
    try:
        if not os.path.exists(file_path):
            # 创建初始文件内容
            initial_content = """#!/usr/bin/env python3
# Coze2JianYing 脚本文件
# 此文件由 Coze 工具自动生成和更新

"""
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(initial_content)
        return True, ""
    except PermissionError:
        return False, f"无权限创建文件: {file_path}"
    except Exception as e:
        return False, f"创建文件失败: {str(e)}"


def write_to_file(
    file_path: str, content: str, mode: str, add_newline: bool
) -> tuple[bool, str, int]:
    """
    写入内容到脚本文件

    Args:
        file_path: 脚本文件的完整路径
        content: 要写入的内容
        mode: 写入模式（append 或 overwrite）
        add_newline: 是否添加换行符

    Returns:
        Tuple of (success, error_message, bytes_written)
    """
    try:
        # 准备要写入的内容
        write_content = content
        if add_newline and not content.endswith("\n"):
            write_content += "\n"

        # 根据模式选择文件打开方式
        if mode == "overwrite":
            file_mode = "w"
        else:  # append
            file_mode = "a"

        # 写入文件
        with open(file_path, file_mode, encoding="utf-8") as f:
            f.write(write_content)

        bytes_written = len(write_content.encode("utf-8"))
        return True, "", bytes_written

    except PermissionError:
        return False, f"无权限写入文件: {file_path}", 0
    except Exception as e:
        return False, f"写入文件失败: {str(e)}", 0


def get_file_size(file_path: str) -> int:
    """
    获取文件大小

    Args:
        file_path: 文件路径

    Returns:
        文件大小（字节数），如果文件不存在返回 0
    """
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    except Exception:
        return 0


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    写入脚本文件的主处理函数

    Args:
        args: 包含 content, mode, add_newline 的输入参数

    Returns:
        Dict containing success status, message, bytes written, and total file size
    """
    logger = getattr(args, "logger", None)

    if logger:
        logger.info(f"Writing to script with parameters: mode={args.input.mode}")

    # 定义脚本文件路径
    script_file_path = "/tmp/coze2jianying.py"

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
                "bytes_written": 0,
                "total_file_size": get_file_size(script_file_path),
            }

        mode = getattr(args.input, "mode", None) or "append"
        add_newline = getattr(args.input, "add_newline", None)
        if add_newline is None:
            add_newline = True

        # 验证模式
        if mode not in ["append", "overwrite"]:
            error_msg = f"无效的写入模式: {mode}，必须是 'append' 或 'overwrite'"
            if logger:
                logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "bytes_written": 0,
                "total_file_size": get_file_size(script_file_path),
            }

        # 确保文件存在
        success, error_msg = ensure_script_file_exists(script_file_path)
        if not success:
            if logger:
                logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "bytes_written": 0,
                "total_file_size": 0,
            }

        # 写入内容
        success, error_msg, bytes_written = write_to_file(
            script_file_path, content, mode, add_newline
        )

        if not success:
            if logger:
                logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "bytes_written": 0,
                "total_file_size": get_file_size(script_file_path),
            }

        # 获取文件大小
        total_size = get_file_size(script_file_path)

        # 准备成功消息
        mode_text = "追加" if mode == "append" else "覆盖写入"
        success_message = (
            f"成功{mode_text}内容到脚本文件，"
            f"写入: {bytes_written} 字节，"
            f"文件总大小: {total_size} 字节"
        )

        if logger:
            logger.info(success_message)

        return {
            "success": True,
            "message": success_message,
            "bytes_written": bytes_written,
            "total_file_size": total_size,
        }

    except Exception as e:
        error_msg = f"写入脚本时发生意外错误: {str(e)}"
        if logger:
            logger.error(error_msg)

        return {
            "success": False,
            "message": error_msg,
            "bytes_written": 0,
            "total_file_size": get_file_size(script_file_path),
        }
