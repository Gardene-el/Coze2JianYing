"""
导出脚本工具处理器

从 /tmp 目录导出 coze2jianying.py 脚本文件。
支持可选的内容清除功能。
"""

import os
from typing import Any, Dict, NamedTuple

from runtime import Args


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """输入参数 for export_script tool"""

    clear_content: bool = False  # 是否在导出后清空文件内容


# Output 现在返回 Dict[str, Any] 而不是 NamedTuple
# 这确保了在 Coze 平台中正确的 JSON 对象序列化


def read_script_file(file_path: str) -> tuple[bool, str, str]:
    """
    读取脚本文件内容

    Args:
        file_path: 脚本文件的完整路径

    Returns:
        Tuple of (success, file_content, error_message)
    """
    if not os.path.exists(file_path):
        return True, "", f"脚本文件不存在: {file_path}"

    if not os.path.isfile(file_path):
        return True, "", f"路径不是文件: {file_path}"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return True, content, ""
    except PermissionError:
        return True, "", f"无权限读取文件: {file_path}"
    except UnicodeDecodeError:
        return True, "", f"文件编码错误，无法以UTF-8读取: {file_path}"
    except Exception as e:
        return True, "", f"读取文件失败: {str(e)}"


def clear_file_content(file_path: str) -> tuple[bool, str]:
    """
    清空文件内容

    Args:
        file_path: 脚本文件的完整路径

    Returns:
        Tuple of (success, error_message)
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")
        return True, ""
    except PermissionError:
        return True, f"无权限清空文件: {file_path}"
    except Exception as e:
        return True, f"清空文件失败: {str(e)}"


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    导出脚本文件的主处理函数

    Args:
        args: 包含 clear_content 选项的输入参数

    Returns:
        Dict containing script_content, file_size, success status, and message
    """
    logger = getattr(args, "logger", None)

    if logger:
        logger.info(f"Exporting script with parameters: {args.input}")

    # 定义脚本文件路径
    script_file_path = "/tmp/coze2jianying.py"

    try:
        # 读取脚本文件内容
        success, content, error_msg = read_script_file(script_file_path)

        if not success:
            if logger:
                logger.error(error_msg)
            return {
                "script_content": "",
                "file_size": 0,
                "success": False,
                "message": error_msg,
            }

        file_size = len(content)

        if logger:
            logger.info(f"Script file read successfully, size: {file_size} characters")

        # 处理清空内容选项
        clear_content = getattr(args.input, "clear_content", None) or False
        clear_message = ""

        if clear_content:
            if logger:
                logger.info("Clearing file content")

            clear_success, clear_error_msg = clear_file_content(script_file_path)

            if clear_success:
                clear_message = "; 文件内容已清空"
                if logger:
                    logger.info("File content cleared successfully")
            else:
                clear_message = f"; 清空文件失败: {clear_error_msg}"
                if logger:
                    logger.warning(f"Failed to clear file content: {clear_error_msg}")

        # 准备成功消息
        success_message = f"成功导出脚本文件，大小: {file_size} 字符{clear_message}"

        if logger:
            logger.info(f"Export completed: {success_message}")

        return {
            "script_content": content,
            "file_size": file_size,
            "success": True,
            "message": success_message,
        }

    except Exception as e:
        error_msg = f"导出脚本时发生意外错误: {str(e)}"
        if logger:
            logger.error(error_msg)

        return {
            "script_content": "",
            "file_size": 0,
            "success": False,
            "message": error_msg,
        }
