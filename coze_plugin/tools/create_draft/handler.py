"""
创建草稿工具处理器

创建具有基本项目设置的新草稿并返回 UUID 以供将来参考。
草稿数据存储在可配置的目录中（默认 /tmp），以 UUID 作为文件夹名称。

环境变量配置：
- JIANYING_COZE_DRAFTS_DIR: 指定草稿存储目录
- JIANYING_COZE_DATA_DIR: 指定数据根目录
- JIANYING_DATA_ROOT: 通用数据根目录
"""

import os
import json
import uuid
import time
from typing import NamedTuple, Dict, Any
from runtime import Args

# 导入 Coze 配置辅助模块
import sys
from pathlib import Path
# 添加 base_tools 到路径以导入 coze_config
base_tools_path = Path(__file__).parent.parent / "base_tools"
if str(base_tools_path) not in sys.path:
    sys.path.insert(0, str(base_tools_path))

try:
    from coze_config import get_coze_drafts_dir, ensure_dir_exists
except ImportError:
    # 如果导入失败，使用硬编码的默认值（向后兼容）
    def get_coze_drafts_dir():
        return os.path.join("/tmp", "jianying_assistant", "drafts")
    
    def ensure_dir_exists(path):
        os.makedirs(path, exist_ok=True)
        return path


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """create_draft 工具的输入参数"""
    draft_name: str = "Coze剪映项目"
    width: int = 1920
    height: int = 1080
    fps: int = 30


# Output 现在返回 Dict[str, Any] 而不是 NamedTuple
# 这确保了在 Coze 平台中正确的 JSON 对象序列化


def validate_input_parameters(input_data: Input) -> tuple[bool, str]:
    """
    验证 create_draft 的输入参数
    
    Args:
        input_data: 输入参数
        
    Returns:
        元组 (is_valid, error_message)
    """
    # 验证尺寸（处理 None 值）
    width = getattr(input_data, 'width', None) or 1920
    height = getattr(input_data, 'height', None) or 1080
    if width <= 0 or height <= 0:
        return False, f"Invalid dimensions: {width}x{height}"
    
    # 验证 fps（处理 None 值）
    fps = getattr(input_data, 'fps', None) or 30
    if fps <= 0 or fps > 120:
        return False, f"Invalid fps: {fps}"
    
    return True, ""


def create_draft_folder(draft_id: str) -> str:
    """
    创建草稿文件夹
    
    使用可配置的目录路径（通过环境变量）
    默认：/tmp/jianying_assistant/drafts/
    
    Args:
        draft_id: UUID string for the draft
        
    Returns:
        Path to created draft folder
        
    Raises:
        Exception: If folder creation fails
    """
    # 获取配置的草稿目录
    base_dir = get_coze_drafts_dir()
    draft_folder = os.path.join(base_dir, draft_id)
    
    try:
        # Create the full directory structure including parents
        ensure_dir_exists(draft_folder)
        return draft_folder
    except Exception as e:
        raise Exception(f"Failed to create draft folder: {str(e)}")


def create_initial_draft_config(input_data: Input, draft_id: str, draft_folder: str) -> None:
    """
    Create initial draft configuration file
    
    Args:
        input_data: 输入参数
        draft_id: UUID string for the draft
        draft_folder: Path to draft folder
        
    Raises:
        Exception: If config creation fails
    """
    timestamp = time.time()
    
    # Handle None values and provide defaults
    draft_name = getattr(input_data, 'draft_name', None) or "Coze剪映项目"
    width = getattr(input_data, 'width', None) or 1920
    height = getattr(input_data, 'height', None) or 1080
    fps = getattr(input_data, 'fps', None) or 30
    
    # Create initial draft configuration
    draft_config = {
        "draft_id": draft_id,
        "project": {
            "name": draft_name,
            "width": width,
            "height": height,
            "fps": fps
        },
        "media_resources": [],
        "tracks": [],
        "created_timestamp": timestamp,
        "last_modified": timestamp,
        "status": "created"
    }
    
    # Save configuration to file
    config_file = os.path.join(draft_folder, "draft_config.json")
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(draft_config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise Exception(f"Failed to save draft config: {str(e)}")


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    创建草稿的主处理函数
    
    Args:
        args: Input arguments containing project settings
        
    Returns:
        Dict containing draft_id, success status, and message
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Creating new draft with parameters: {args.input}")
    
    try:
        # Log the actual received parameters for debugging
        if logger:
            logger.info(f"Received parameters - width: {getattr(args.input, 'width', None)}, "
                       f"height: {getattr(args.input, 'height', None)}, "
                       f"fps: {getattr(args.input, 'fps', None)}, "
                       f"draft_name: {getattr(args.input, 'draft_name', None)}")
        
        # 验证输入 parameters
        is_valid, error_msg = validate_input_parameters(args.input)
        if not is_valid:
            if logger:
                logger.error(f"Input validation failed: {error_msg}")
            return {
                "draft_id": "",
                "success": False,
                "message": f"参数验证失败: {error_msg}"
            }
        
        # Generate unique draft ID
        draft_id = str(uuid.uuid4())
        
        if logger:
            logger.info(f"Generated draft ID: {draft_id}")
        
        # Create draft folder
        try:
            draft_folder = create_draft_folder(draft_id)
            if logger:
                logger.info(f"Created draft folder: {draft_folder}")
        except Exception as e:
            if logger:
                logger.error(f"Failed to create draft folder: {str(e)}")
            return {
                "draft_id": "",
                "success": False,
                "message": f"创建草稿文件夹失败: {str(e)}"
            }
        
        # Create initial draft configuration
        try:
            create_initial_draft_config(args.input, draft_id, draft_folder)
            if logger:
                logger.info(f"Created initial draft configuration")
        except Exception as e:
            if logger:
                logger.error(f"Failed to create draft config: {str(e)}")
            return {
                "draft_id": "",
                "success": False,
                "message": f"创建草稿配置失败: {str(e)}"
            }
        
        if logger:
            logger.info(f"Draft created successfully with ID: {draft_id}")
        
        return {
            "draft_id": draft_id,
            "success": True,
            "message": f"草稿创建成功，ID: {draft_id}"
        }
        
    except Exception as e:
        error_msg = f"Unexpected error in create_draft handler: {str(e)}"
        if logger:
            logger.error(error_msg)
            logger.error(f"Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return {
            "draft_id": "",
            "success": False,
            "message": f"创建草稿时发生意外错误: {str(e)}"
        }