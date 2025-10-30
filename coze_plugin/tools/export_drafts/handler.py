"""
Export Drafts Tool Handler

Exports draft data from /tmp storage for use by the draft generator.
Supports single draft or batch export, with optional cleanup of temporary files.
"""

import os
import json
import shutil
from typing import NamedTuple, Union, List, Dict, Any
from runtime import Args


# Input/Output type definitions (required for each Coze tool)
class Input(NamedTuple):
    """Input parameters for export_drafts tool"""
    draft_ids: Union[str, List[str], None] = None  # Single UUID string, list of UUIDs, or None for export_all
    remove_temp_files: bool = False   # Whether to remove temp files after export
    export_all: bool = False          # Whether to export all drafts in the directory


# Output is now returned as Dict[str, Any] instead of NamedTuple
# This ensures proper JSON object serialization in Coze platform


def validate_uuid_format(uuid_str: str) -> bool:
    """
    Validate UUID string format
    
    Args:
        uuid_str: UUID string to validate
        
    Returns:
        True if valid UUID format
    """
    try:
        import uuid
        uuid.UUID(uuid_str)
        return True
    except (ValueError, TypeError):
        return False


def normalize_draft_ids(draft_ids: Union[str, List[str], None]) -> List[str]:
    """
    Normalize draft_ids input to list format
    
    Args:
        draft_ids: Single UUID string, list of UUIDs, or None
        
    Returns:
        List of UUID strings
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
    Load draft configuration from file
    
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


def strip_default_values(data: dict, segment_type: str = None) -> dict:
    """
    Remove default values from serialized data to reduce size
    
    Args:
        data: Dictionary containing serialized data
        segment_type: Type of segment ('image', 'audio', 'text', 'video', etc.)
    
    Returns:
        Dictionary with default values stripped
    """
    if not isinstance(data, dict):
        return data
    
    # Define defaults for different field groups
    transform_defaults = {
        "position_x": {0.0, 0.5},  # 0.0 for most, 0.5 for text
        "position_y": {0.0, -0.9},  # 0.0 for most, -0.9 for text
        "scale_x": 1.0,
        "scale_y": 1.0,
        "scale": 1.0,
        "rotation": 0.0,
        "opacity": 1.0
    }
    
    crop_defaults = {
        "enabled": False,
        "left": 0.0,
        "top": 0.0,
        "right": 1.0,
        "bottom": 1.0
    }
    
    audio_defaults = {
        "volume": 1.0,
        "fade_in": 0,
        "fade_out": 0,
        "effect_type": None,
        "effect_intensity": 1.0,
        "speed": 1.0,
        "change_pitch": False
    }
    
    effects_defaults = {
        "filter_type": None,
        "filter_intensity": 1.0,
        "transition_type": None,
        "transition_duration": 500
    }
    
    background_defaults = {
        "blur": False,
        "color": None,
        "fit_mode": "fit"
    }
    
    animations_defaults = {
        "intro": None,
        "intro_duration": 500,
        "outro": None,
        "outro_duration": 500,
        "loop": None
    }
    
    speed_defaults = {
        "speed": 1.0,
        "reverse": False
    }
    
    dimensions_defaults = {
        "width": None,
        "height": None
    }
    
    flip_defaults = {
        "horizontal": False,
        "vertical": False
    }
    
    style_defaults = {
        "font_family": "默认",
        "font_size": 48,
        "font_weight": "normal",
        "font_style": "normal",
        "color": "#FFFFFF",
        "alignment": "center"
    }
    
    style_stroke_defaults = {
        "enabled": False,
        "color": "#000000",
        "width": 2
    }
    
    style_shadow_defaults = {
        "enabled": False,
        "color": "#000000",
        "offset_x": 2,
        "offset_y": 2,
        "blur": 4
    }
    
    style_background_defaults = {
        "enabled": False,
        "color": "#000000",
        "opacity": 0.5
    }
    
    # Check if a field group is all defaults
    def is_all_defaults(group: dict, defaults: dict) -> bool:
        if not group:
            return True
        for key, value in group.items():
            default = defaults.get(key)
            if isinstance(default, set):
                if value not in default:
                    return False
            elif value != default:
                return False
        return True
    
    # Check if value is empty (None or empty list)
    def is_empty(value):
        return value is None or (isinstance(value, list) and len(value) == 0)
    
    result = {}
    
    for key, value in data.items():
        # Always keep base fields
        if key in ["type", "material_url", "content", "resource_id", "effect_type", "filter_type", "time_range", "draft_id", "project", "tracks", "created_timestamp", "last_modified", "status"]:
            result[key] = value
            continue
        
        # Handle nested objects
        if key == "transform" and isinstance(value, dict):
            if not is_all_defaults(value, transform_defaults):
                result[key] = value
        elif key == "crop" and isinstance(value, dict):
            if not is_all_defaults(value, crop_defaults):
                result[key] = value
        elif key == "audio" and isinstance(value, dict):
            if not is_all_defaults(value, audio_defaults):
                result[key] = value
        elif key == "effects" and isinstance(value, dict):
            if not is_all_defaults(value, effects_defaults):
                result[key] = value
        elif key == "background" and isinstance(value, dict):
            if not is_all_defaults(value, background_defaults):
                result[key] = value
        elif key == "animations" and isinstance(value, dict):
            if not is_all_defaults(value, animations_defaults):
                result[key] = value
        elif key == "speed" and isinstance(value, dict):
            if not is_all_defaults(value, speed_defaults):
                result[key] = value
        elif key == "dimensions" and isinstance(value, dict):
            if not is_all_defaults(value, dimensions_defaults):
                result[key] = value
        elif key == "flip" and isinstance(value, dict):
            if not is_all_defaults(value, flip_defaults):
                result[key] = value
        elif key == "style" and isinstance(value, dict):
            # Style is more complex - check sub-groups
            style_result = {}
            for style_key, style_value in value.items():
                if style_key == "stroke" and isinstance(style_value, dict):
                    if not is_all_defaults(style_value, style_stroke_defaults):
                        style_result[style_key] = style_value
                elif style_key == "shadow" and isinstance(style_value, dict):
                    if not is_all_defaults(style_value, style_shadow_defaults):
                        style_result[style_key] = style_value
                elif style_key == "background" and isinstance(style_value, dict):
                    if not is_all_defaults(style_value, style_background_defaults):
                        style_result[style_key] = style_value
                else:
                    default_val = style_defaults.get(style_key)
                    if style_value != default_val:
                        style_result[style_key] = style_value
            if style_result:
                result[key] = style_result
        elif key == "keyframes" and isinstance(value, dict):
            # Only include keyframes if they're not all empty
            non_empty_keyframes = {k: v for k, v in value.items() if not is_empty(v)}
            if non_empty_keyframes:
                result[key] = non_empty_keyframes
        elif key == "properties" and isinstance(value, dict):
            # Include properties if not all defaults
            props_defaults = {"intensity": 1.0, "position_x": None, "position_y": None, "scale": 1.0}
            if not is_all_defaults(value, props_defaults):
                result[key] = value
        elif key in ["material_range", "muted", "volume", "alignment", "intensity"]:
            # These fields: only include if not default
            if key == "material_range" and value is not None:
                result[key] = value
            elif key == "muted" and value != False:
                result[key] = value
            elif key == "volume" and value != 1.0:
                result[key] = value
            elif key == "alignment" and value != "center":
                result[key] = value
            elif key == "intensity" and value != 1.0:
                result[key] = value
        else:
            # For unknown fields, keep them
            result[key] = value
    
    return result


def strip_defaults_from_draft(draft_config: dict) -> dict:
    """
    Recursively strip default values from a complete draft configuration
    
    Args:
        draft_config: Complete draft configuration dictionary
        
    Returns:
        Draft configuration with defaults stripped
    """
    result = {}
    
    # Keep top-level fields
    for key in ["draft_id", "project", "created_timestamp", "last_modified", "status", "total_duration_ms"]:
        if key in draft_config:
            result[key] = draft_config[key]
    
    # Process tracks
    if "tracks" in draft_config:
        result["tracks"] = []
        for track in draft_config["tracks"]:
            track_result = {"track_type": track["track_type"]}
            
            # Only include muted/volume if non-default
            if track.get("muted", False) != False:
                track_result["muted"] = track["muted"]
            if track.get("volume", 1.0) != 1.0:
                track_result["volume"] = track["volume"]
            
            # Process segments
            if "segments" in track:
                track_result["segments"] = []
                for segment in track["segments"]:
                    segment_type = segment.get("type", "unknown")
                    stripped_segment = strip_default_values(segment, segment_type)
                    track_result["segments"].append(stripped_segment)
            
            result["tracks"].append(track_result)
    
    # Keep media_resources if present (though usually empty)
    if "media_resources" in draft_config and draft_config["media_resources"]:
        result["media_resources"] = draft_config["media_resources"]
    
    return result


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
    Main handler function for exporting drafts
    
    Args:
        args: Input arguments containing draft_ids and options
        
    Returns:
        Dict containing draft_data, exported_count, success status, and message
    """
    logger = getattr(args, 'logger', None)
    
    if logger:
        logger.info(f"Exporting drafts with parameters: {args.input}")
    
    try:
        # Handle export_all mode
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
        
        # Load draft configurations and strip default values
        loaded_configs = []
        failed_drafts = []
        
        for draft_id in draft_ids:
            success, config, error_msg = load_draft_config(draft_id)
            
            if success:
                # Strip default values to reduce data size
                stripped_config = strip_defaults_from_draft(config)
                loaded_configs.append(stripped_config)
                if logger:
                    logger.info(f"Loaded and optimized draft config: {draft_id}")
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