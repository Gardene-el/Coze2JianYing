"""
error_codes — 领域错误词汇表

纯枚举定义，无任何业务逻辑，可在任意层安全导入。
"""
from enum import Enum
from typing import Any, Dict


class ErrorCategory(str, Enum):
    """错误类别枚举"""
    SUCCESS = "success"

    # 客户端错误（4xx系列）
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    INVALID_STATE = "invalid_state"
    TYPE_MISMATCH = "type_mismatch"

    # 服务端错误（5xx系列）
    INTERNAL_ERROR = "internal_error"
    DATABASE_ERROR = "database_error"
    FILE_SYSTEM_ERROR = "file_system_error"
    EXTERNAL_SERVICE_ERROR = "external_service_error"

    # 业务逻辑错误
    OPERATION_FAILED = "operation_failed"
    DEPENDENCY_ERROR = "dependency_error"
    RESOURCE_CONFLICT = "resource_conflict"


class ErrorCode(str, Enum):
    """详细的错误代码"""
    SUCCESS = "SUCCESS"

    # 草稿相关
    DRAFT_NOT_FOUND = "DRAFT_NOT_FOUND"
    DRAFT_ALREADY_EXISTS = "DRAFT_ALREADY_EXISTS"
    DRAFT_CREATE_FAILED = "DRAFT_CREATE_FAILED"
    DRAFT_UPDATE_FAILED = "DRAFT_UPDATE_FAILED"
    DRAFT_SAVE_FAILED = "DRAFT_SAVE_FAILED"
    DRAFT_INVALID_STATE = "DRAFT_INVALID_STATE"

    # 片段相关
    SEGMENT_NOT_FOUND = "SEGMENT_NOT_FOUND"
    SEGMENT_CREATE_FAILED = "SEGMENT_CREATE_FAILED"
    SEGMENT_TYPE_MISMATCH = "SEGMENT_TYPE_MISMATCH"
    SEGMENT_INVALID_CONFIG = "SEGMENT_INVALID_CONFIG"

    # 轨道相关
    TRACK_NOT_FOUND = "TRACK_NOT_FOUND"
    TRACK_INDEX_INVALID = "TRACK_INDEX_INVALID"
    TRACK_TYPE_MISMATCH = "TRACK_TYPE_MISMATCH"
    TRACK_OPERATION_FAILED = "TRACK_OPERATION_FAILED"

    # 素材相关
    MATERIAL_DOWNLOAD_FAILED = "MATERIAL_DOWNLOAD_FAILED"
    MATERIAL_INVALID_URL = "MATERIAL_INVALID_URL"
    MATERIAL_NOT_FOUND = "MATERIAL_NOT_FOUND"

    # 参数验证
    INVALID_PARAMETER = "INVALID_PARAMETER"
    MISSING_REQUIRED_PARAMETER = "MISSING_REQUIRED_PARAMETER"
    PARAMETER_OUT_OF_RANGE = "PARAMETER_OUT_OF_RANGE"

    # 操作相关
    OPERATION_NOT_SUPPORTED = "OPERATION_NOT_SUPPORTED"
    OPERATION_ALREADY_EXISTS = "OPERATION_ALREADY_EXISTS"
    OPERATION_FAILED = "OPERATION_FAILED"

    # 系统错误
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    FILE_SYSTEM_ERROR = "FILE_SYSTEM_ERROR"

    # 依赖错误
    DEPENDENCY_NOT_FOUND = "DEPENDENCY_NOT_FOUND"
    DEPENDENCY_INVALID = "DEPENDENCY_INVALID"


class ResponseLevel(str, Enum):
    """响应级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# 错误码元数据：category + level + 消息模板
ERROR_META: Dict[ErrorCode, Dict[str, Any]] = {
    ErrorCode.SUCCESS: {
        "category": ErrorCategory.SUCCESS,
        "level": ResponseLevel.INFO,
        "template": "操作成功",
    },
    ErrorCode.DRAFT_NOT_FOUND: {
        "category": ErrorCategory.NOT_FOUND,
        "level": ResponseLevel.ERROR,
        "template": "草稿不存在: {draft_id}",
    },
    ErrorCode.DRAFT_ALREADY_EXISTS: {
        "category": ErrorCategory.ALREADY_EXISTS,
        "level": ResponseLevel.ERROR,
        "template": "草稿已存在: {draft_name}",
    },
    ErrorCode.DRAFT_CREATE_FAILED: {
        "category": ErrorCategory.OPERATION_FAILED,
        "level": ResponseLevel.ERROR,
        "template": "草稿创建失败: {reason}",
    },
    ErrorCode.DRAFT_UPDATE_FAILED: {
        "category": ErrorCategory.OPERATION_FAILED,
        "level": ResponseLevel.ERROR,
        "template": "草稿更新失败: {reason}",
    },
    ErrorCode.DRAFT_SAVE_FAILED: {
        "category": ErrorCategory.OPERATION_FAILED,
        "level": ResponseLevel.ERROR,
        "template": "草稿保存失败: {reason}",
    },
    ErrorCode.DRAFT_INVALID_STATE: {
        "category": ErrorCategory.INVALID_STATE,
        "level": ResponseLevel.ERROR,
        "template": "草稿状态无效: {state}",
    },
    ErrorCode.SEGMENT_NOT_FOUND: {
        "category": ErrorCategory.NOT_FOUND,
        "level": ResponseLevel.ERROR,
        "template": "片段不存在: {segment_id}",
    },
    ErrorCode.SEGMENT_CREATE_FAILED: {
        "category": ErrorCategory.OPERATION_FAILED,
        "level": ResponseLevel.ERROR,
        "template": "片段创建失败: {reason}",
    },
    ErrorCode.SEGMENT_TYPE_MISMATCH: {
        "category": ErrorCategory.TYPE_MISMATCH,
        "level": ResponseLevel.ERROR,
        "template": "片段类型不匹配: 期望 {expected}，实际 {actual}",
    },
    ErrorCode.SEGMENT_INVALID_CONFIG: {
        "category": ErrorCategory.VALIDATION_ERROR,
        "level": ResponseLevel.ERROR,
        "template": "片段配置无效: {reason}",
    },
    ErrorCode.TRACK_NOT_FOUND: {
        "category": ErrorCategory.NOT_FOUND,
        "level": ResponseLevel.ERROR,
        "template": "轨道不存在: {track_index}",
    },
    ErrorCode.TRACK_INDEX_INVALID: {
        "category": ErrorCategory.VALIDATION_ERROR,
        "level": ResponseLevel.ERROR,
        "template": "轨道索引无效: {track_index}",
    },
    ErrorCode.TRACK_TYPE_MISMATCH: {
        "category": ErrorCategory.TYPE_MISMATCH,
        "level": ResponseLevel.ERROR,
        "template": "轨道类型不匹配: 片段类型 {segment_type} 不能添加到 {track_type} 轨道",
    },
    ErrorCode.TRACK_OPERATION_FAILED: {
        "category": ErrorCategory.OPERATION_FAILED,
        "level": ResponseLevel.ERROR,
        "template": "轨道操作失败: {reason}",
    },
    ErrorCode.MATERIAL_DOWNLOAD_FAILED: {
        "category": ErrorCategory.EXTERNAL_SERVICE_ERROR,
        "level": ResponseLevel.ERROR,
        "template": "素材下载失败: {url}",
    },
    ErrorCode.MATERIAL_INVALID_URL: {
        "category": ErrorCategory.VALIDATION_ERROR,
        "level": ResponseLevel.ERROR,
        "template": "素材 URL 无效: {url}",
    },
    ErrorCode.MATERIAL_NOT_FOUND: {
        "category": ErrorCategory.NOT_FOUND,
        "level": ResponseLevel.ERROR,
        "template": "素材不存在: {material_id}",
    },
    ErrorCode.INVALID_PARAMETER: {
        "category": ErrorCategory.VALIDATION_ERROR,
        "level": ResponseLevel.ERROR,
        "template": "参数无效: {parameter} - {reason}",
    },
    ErrorCode.MISSING_REQUIRED_PARAMETER: {
        "category": ErrorCategory.VALIDATION_ERROR,
        "level": ResponseLevel.ERROR,
        "template": "缺少必需参数: {parameter}",
    },
    ErrorCode.PARAMETER_OUT_OF_RANGE: {
        "category": ErrorCategory.VALIDATION_ERROR,
        "level": ResponseLevel.ERROR,
        "template": "参数超出范围: {parameter} 应在 {min} 到 {max} 之间，实际值 {value}",
    },
    ErrorCode.OPERATION_NOT_SUPPORTED: {
        "category": ErrorCategory.OPERATION_FAILED,
        "level": ResponseLevel.ERROR,
        "template": "操作不支持: {operation}",
    },
    ErrorCode.OPERATION_ALREADY_EXISTS: {
        "category": ErrorCategory.ALREADY_EXISTS,
        "level": ResponseLevel.ERROR,
        "template": "操作已存在: {operation}",
    },
    ErrorCode.OPERATION_FAILED: {
        "category": ErrorCategory.OPERATION_FAILED,
        "level": ResponseLevel.ERROR,
        "template": "操作失败: {reason}",
    },
    ErrorCode.INTERNAL_ERROR: {
        "category": ErrorCategory.INTERNAL_ERROR,
        "level": ResponseLevel.CRITICAL,
        "template": "内部错误: {error}",
    },
    ErrorCode.DATABASE_ERROR: {
        "category": ErrorCategory.DATABASE_ERROR,
        "level": ResponseLevel.CRITICAL,
        "template": "数据库错误: {error}",
    },
    ErrorCode.FILE_SYSTEM_ERROR: {
        "category": ErrorCategory.FILE_SYSTEM_ERROR,
        "level": ResponseLevel.CRITICAL,
        "template": "文件系统错误: {error}",
    },
    ErrorCode.DEPENDENCY_NOT_FOUND: {
        "category": ErrorCategory.DEPENDENCY_ERROR,
        "level": ResponseLevel.ERROR,
        "template": "依赖不存在: {dependency}",
    },
    ErrorCode.DEPENDENCY_INVALID: {
        "category": ErrorCategory.DEPENDENCY_ERROR,
        "level": ResponseLevel.ERROR,
        "template": "依赖无效: {dependency} - {reason}",
    },
}
