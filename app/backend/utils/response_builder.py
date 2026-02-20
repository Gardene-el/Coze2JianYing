"""
API 响应构建工具

归属：utils/ — 无状态工具函数，统一 API 响应格式，确保对 Coze 友好（始终返回 success=True）。

设计原则：
- 对 Coze 友好：总是返回 success=True
- 对开发者友好：提供详细的错误信息和分类
- 无状态：纯函数，无单例，直接导入使用
"""

from enum import Enum
from typing import Optional, Dict, Any, Type, TypeVar
from datetime import datetime
from pydantic import BaseModel

ResponseType = TypeVar('ResponseType', bound=BaseModel)


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
_ERROR_META: Dict[ErrorCode, Dict[str, Any]] = {
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


# ──────────────────────────────────────────────
# 基础响应构建函数
# ──────────────────────────────────────────────

def build_success(
    message: str = "操作成功",
    data: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """构建成功响应字典"""
    resp: Dict[str, Any] = {
        "success": True,
        "error_code": ErrorCode.SUCCESS,
        "category": ErrorCategory.SUCCESS,
        "level": ResponseLevel.INFO,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }
    if data:
        resp["data"] = data
    resp.update(kwargs)
    return resp


def build_error(
    error_code: ErrorCode,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """构建错误响应字典（success 仍为 True，对 Coze 友好）"""
    meta = _ERROR_META.get(error_code, _ERROR_META[ErrorCode.INTERNAL_ERROR])
    if error_code not in _ERROR_META:
        error_code = ErrorCode.INTERNAL_ERROR

    if message is None:
        template = meta["template"]
        try:
            message = template.format(**(details or {}))
        except KeyError:
            message = template

    resp: Dict[str, Any] = {
        "success": True,  # 始终 True，便于 Coze 测试通过
        "error_code": error_code,
        "category": meta["category"],
        "level": meta["level"],
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }
    if details:
        resp["details"] = details
    resp.update(kwargs)
    return resp


def wrap_data(data: Dict[str, Any], message: str = "操作成功") -> Dict[str, Any]:
    """将数据包装为成功响应（便捷函数）"""
    return build_success(message=message, data=data)


# ──────────────────────────────────────────────
# 常用错误场景快捷函数
# ──────────────────────────────────────────────

def build_validation_error(field: str, value: Any, reason: str) -> Dict[str, Any]:
    """构建参数验证错误响应"""
    return build_error(
        ErrorCode.INVALID_PARAMETER,
        details={"parameter": field, "value": str(value), "reason": reason},
    )


def build_not_found_error(resource_type: str, resource_id: str) -> Dict[str, Any]:
    """构建资源不存在错误响应"""
    _code_map = {
        "draft": ErrorCode.DRAFT_NOT_FOUND,
        "segment": ErrorCode.SEGMENT_NOT_FOUND,
        "track": ErrorCode.TRACK_NOT_FOUND,
        "material": ErrorCode.MATERIAL_NOT_FOUND,
    }
    code = _code_map.get(resource_type, ErrorCode.DEPENDENCY_NOT_FOUND)
    return build_error(code, details={f"{resource_type}_id": resource_id})


def build_operation_error(operation: str, reason: str) -> Dict[str, Any]:
    """构建操作失败错误响应"""
    return build_error(
        ErrorCode.OPERATION_FAILED,
        details={"operation": operation, "reason": reason},
    )


def build_internal_error(error: Exception) -> Dict[str, Any]:
    """构建内部异常错误响应"""
    return build_error(
        ErrorCode.INTERNAL_ERROR,
        details={"error": str(error), "error_type": type(error).__name__},
    )


# ──────────────────────────────────────────────
# 类型化响应构建函数（配合 Pydantic Response 模型）
# ──────────────────────────────────────────────

def create_response(response_class: Type[ResponseType], **fields) -> ResponseType:
    """从字段字典直接实例化 Pydantic 响应模型"""
    if "timestamp" not in fields and hasattr(response_class, "timestamp"):
        fields["timestamp"] = datetime.now()
    return response_class(**fields)


def success_response(
    response_class: Type[ResponseType],
    message: str = "操作成功",
    **specific_fields,
) -> ResponseType:
    """构建成功的类型化响应"""
    return create_response(response_class, **{**build_success(message=message), **specific_fields})


def error_response(
    response_class: Type[ResponseType],
    error_code: ErrorCode,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    **specific_fields,
) -> ResponseType:
    """构建错误的类型化响应"""
    base = build_error(error_code, message=message, details=details)
    return create_response(response_class, **{**base, **specific_fields})


def not_found_response(
    response_class: Type[ResponseType],
    resource_type: str,
    resource_id: str,
    **specific_fields,
) -> ResponseType:
    """构建资源不存在的类型化响应"""
    base = build_not_found_error(resource_type, resource_id)
    return create_response(response_class, **{**base, **specific_fields})


def internal_error_response(
    response_class: Type[ResponseType],
    error: Exception,
    **specific_fields,
) -> ResponseType:
    """构建内部异常的类型化响应"""
    base = build_internal_error(error)
    return create_response(response_class, **{**base, **specific_fields})
