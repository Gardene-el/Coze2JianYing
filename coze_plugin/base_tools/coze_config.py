"""
Coze 工具辅助配置模块

此模块为 Coze 插件工具提供配置支持。
由于 Coze 工具是独立脚本，不能依赖 app 包，因此需要独立的配置实现。

配置优先级：
1. 环境变量
2. Coze 平台默认 /tmp 目录
"""
import os
import tempfile


def get_coze_base_dir() -> str:
    """
    获取 Coze 工具的基础数据目录
    
    优先级：
    1. 环境变量 JIANYING_COZE_DATA_DIR
    2. 环境变量 JIANYING_DATA_ROOT
    3. Coze 平台默认 /tmp/jianying_assistant
    
    Returns:
        基础目录路径
    """
    # 1. Coze 专用环境变量
    coze_dir = os.getenv("JIANYING_COZE_DATA_DIR")
    if coze_dir:
        return coze_dir
    
    # 2. 通用数据根目录
    data_root = os.getenv("JIANYING_DATA_ROOT")
    if data_root:
        return data_root
    
    # 3. Coze 平台默认（/tmp 目录，Coze 限制为 512MB）
    return os.path.join("/tmp", "jianying_assistant")


def get_coze_drafts_dir() -> str:
    """
    获取 Coze 工具的草稿存储目录
    
    Returns:
        草稿目录路径
    """
    # 环境变量优先
    drafts_dir = os.getenv("JIANYING_COZE_DRAFTS_DIR")
    if drafts_dir:
        return drafts_dir
    
    # 使用基础目录下的 drafts 子目录
    base_dir = get_coze_base_dir()
    return os.path.join(base_dir, "drafts")


def ensure_dir_exists(path: str) -> str:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
        
    Returns:
        目录路径
        
    Raises:
        Exception: 如果无法创建目录
    """
    try:
        os.makedirs(path, exist_ok=True)
        return path
    except Exception as e:
        raise Exception(f"Failed to create directory {path}: {str(e)}")


# 预定义的路径常量（便于工具使用）
COZE_BASE_DIR = get_coze_base_dir()
COZE_DRAFTS_DIR = get_coze_drafts_dir()
