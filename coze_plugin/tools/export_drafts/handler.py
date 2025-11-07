"""
导出草稿工具处理器

从 /tmp 存储导出草稿数据以供草稿生成器使用。
支持单个草稿或批量导出，可选择清理临时文件。
"""

import os
import json
import shutil
from typing import NamedTuple, Union, List, Dict, Any
from runtime import Args


# Input/Output 类型定义（每个 Coze 工具都需要）
class Input(NamedTuple):
    """输入参数 for export_drafts tool"""
    draft_ids: Union[str, List[str], None] = None  # 单个 UUID 字符串、UUID 列表或 None（用于 export_all）
    remove_temp_files: bool = False   # 是否在导出后删除临时文件
    export_all: bool = False          # 是否导出目录中的所有草稿


# Output 现在返回 Dict[str, Any] 而不是 NamedTuple
# 这确保了在 Coze 平台中正确的 JSON 对象序列化


def validate_uuid_format(uuid_str: str) -> bool:
    """
    验证 UUID 字符串格式
    
    Args:
        uuid_str: 要验证的 UUID 字符串
        
    Returns:
        如果是有效的 UUID 格式则为 True
    """
    try:
        import uuid
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def normalize_draft_ids(draft_ids: Union[str, List[str], None]) -> List[str]:
    """
    将 draft_ids 输入规范化为列表格式
    
    Args:
        draft_ids: 单个 UUID 字符串、UUID 列表或 None
        
    Returns:
        UUID 字符串列表
    """
    if draft_ids is None:
        return []
    elif isinstance(draft_ids, str):
        return [draft_ids]
    elif isinstance(draft_ids, list):
        return draft_ids
    else:
        return []


def load_draft_config(draft_id: str) -> tuple[bool, dict, str]:
    """
    从文件加载草稿配置
    
    Args:
        draft_id: UUID string for the draft
        
    Returns:
        Tuple of (success, config_dict, error_message)
    """
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    config_file = os.path.join(draft_folder, "draft_config.json")
    
    # Check if draft folder exists
    if not os.path.exists(draft_folder):
        return False, {}, f"草稿文件夹不存在: {draft_id}"
    
    # Check if config file exists
    if not os.path.exists(config_file):
        return False, {}, f"草稿配置文件不存在: {draft_id}"
    
    # Load configuration
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return True, config, ""
    except json.JSONDecodeError as e:
        return False, {}, f"草稿配置文件格式错误: {str(e)}"
    except Exception as e:
        return False, {}, f"读取草稿配置失败: {str(e)}"


def create_draft_generator_data(draft_configs: List[dict]) -> dict:
    """
    Create data structure for draft generator
    
    Args:
        draft_configs: List of draft configuration dictionaries
        
    Returns:
        Combined data structure for draft generator
    """
    if len(draft_configs) == 1:
        # Single draft export
        config = draft_configs[0]
        return {
            "format_version": "1.0",
            "export_type": "single_draft",
            "draft_count": 1,
            "drafts": [config]
        }
    else:
        # Multiple drafts export
        return {
            "format_version": "1.0",
            "export_type": "batch_draft",
            "draft_count": len(draft_configs),
            "drafts": draft_configs
        }


def discover_all_drafts() -> List[str]:
    """
    Discover all draft IDs in the drafts directory
    
    Returns:
        List of draft UUID strings found in the directory
    """
    drafts_dir = os.path.join("/tmp", "jianying_assistant", "drafts")
    
    if not os.path.exists(drafts_dir):
        return []
    
    draft_ids = []
    try:
        # List all directories in the drafts folder
        for item in os.listdir(drafts_dir):
            item_path = os.path.join(drafts_dir, item)
            # Check if it's a directory and has a valid UUID format
            if os.path.isdir(item_path) and validate_uuid_format(item):
                # Check if it has a draft_config.json file
                config_file = os.path.join(item_path, "draft_config.json")
                if os.path.exists(config_file):
                    draft_ids.append(item)
    except Exception:
        # Return empty list if there's any error accessing the directory
        return []
    
    return draft_ids


def cleanup_draft_files(draft_id: str) -> tuple[bool, str]:
    """
    Remove draft files from /tmp/jianying_assistant/drafts/ directory
    
    Args:
        draft_id: UUID string for the draft
        
    Returns:
        Tuple of (success, error_message)
    """
    draft_folder = os.path.join("/tmp", "jianying_assistant", "drafts", draft_id)
    
    if not os.path.exists(draft_folder):
        return True, ""  # Already doesn't exist
    
    try:
        shutil.rmtree(draft_folder)
        return True, ""
    except Exception as e:
        return False, f"删除草稿文件失败: {str(e)}"


def handler(args: Args[Input]) -> Dict[str, Any]:
    """
    导出草稿的主处理函数
    
    Args:
        args: 包含 draft_ids 和选项的输入参数
        
    Returns:
        Dict containing draft_data, exported_count, success status, and message
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Exporting drafts with parameters: {args.input}")
    
    try:
        # 处理 export_all 模式
        export_all = getattr(args.input, 'export_all', None) or False
        
        if export_all:
            # Discover all drafts in the directory
            draft_ids = discover_all_drafts()
            if logger:
                logger.info(f"Export all mode: discovered {len(draft_ids)} drafts")
        else:
            # Normalize and validate input
            draft_ids = normalize_draft_ids(args.input.draft_ids)
        
        if not draft_ids:
            if export_all:
                message = "未找到任何草稿文件"
            else:
                message = "未提供草稿ID"
            
            if logger:
                logger.error(message)
            return {
                "draft_data": "",
                "exported_count": 0,
                "success": False,
                "message": message
            }
        
        # Validate UUID formats (only if not from export_all discovery)
        if not export_all:
            invalid_uuids = []
            for draft_id in draft_ids:
                if not validate_uuid_format(draft_id):
                    invalid_uuids.append(draft_id)
            
            if invalid_uuids:
                if logger:
                    logger.error(f"Invalid UUID formats: {invalid_uuids}")
                return {
                    "draft_data": "",
                    "exported_count": 0,
                    "success": False,
                    "message": f"无效的UUID格式: {', '.join(invalid_uuids)}"
                }
        
        if logger:
            logger.info(f"Processing {len(draft_ids)} draft(s): {draft_ids}")
        
        # Load draft configurations
        loaded_configs = []
        failed_drafts = []
        
        for draft_id in draft_ids:
            success, config, error_msg = load_draft_config(draft_id)
            
            if success:
                loaded_configs.append(config)
                if logger:
                    logger.info(f"Loaded draft config: {draft_id}")
            else:
                failed_drafts.append(f"{draft_id}: {error_msg}")
                if logger:
                    logger.error(f"Failed to load draft {draft_id}: {error_msg}")
        
        # Check if any drafts were loaded successfully
        if not loaded_configs:
            error_message = f"无法加载任何草稿配置: {'; '.join(failed_drafts)}"
            if logger:
                logger.error(error_message)
            return {
                "draft_data": "",
                "exported_count": 0,
                "success": False,
                "message": error_message
            }
        
        # Create draft generator data structure
        try:
            draft_generator_data = create_draft_generator_data(loaded_configs)
            draft_json_string = json.dumps(draft_generator_data, ensure_ascii=False, indent=2)
            
            if logger:
                logger.info(f"Created draft generator data, size: {len(draft_json_string)} characters")
                
        except Exception as e:
            if logger:
                logger.error(f"Failed to create draft generator data: {str(e)}")
            return {
                "draft_data": "",
                "exported_count": 0,
                "success": False,
                "message": f"创建草稿数据失败: {str(e)}"
            }
        
        # Handle cleanup if requested
        cleanup_failures = []
        if args.input.remove_temp_files:
            if logger:
                logger.info("Cleaning up temporary files")
            
            for draft_id in draft_ids:
                if draft_id in [config['draft_id'] for config in loaded_configs]:
                    # Only clean up successfully loaded drafts
                    success, error_msg = cleanup_draft_files(draft_id)
                    if not success:
                        cleanup_failures.append(f"{draft_id}: {error_msg}")
                        if logger:
                            logger.warning(f"Failed to cleanup draft {draft_id}: {error_msg}")
                    else:
                        if logger:
                            logger.info(f"Cleaned up draft: {draft_id}")
        
        # Prepare success message
        exported_count = len(loaded_configs)
        total_requested = len(draft_ids)
        
        message_parts = [f"成功导出 {exported_count} 个草稿"]
        
        if failed_drafts:
            message_parts.append(f"失败 {len(failed_drafts)} 个: {'; '.join(failed_drafts)}")
        
        if cleanup_failures:
            message_parts.append(f"清理失败: {'; '.join(cleanup_failures)}")
        elif args.input.remove_temp_files and exported_count > 0:
            message_parts.append("临时文件已清理")
        
        success_message = "; ".join(message_parts)
        
        if logger:
            logger.info(f"Export completed: {success_message}")
        
        return {
            "draft_data": draft_json_string,
            "exported_count": exported_count,
            "success": True,
            "message": success_message
        }
        
    except Exception as e:
        error_msg = f"Unexpected error in export_drafts handler: {str(e)}"
        if logger:
            logger.error(error_msg)
        
        return {
            "draft_data": "",
            "exported_count": 0,
            "success": False,
            "message": f"导出草稿时发生意外错误: {str(e)}"
        }