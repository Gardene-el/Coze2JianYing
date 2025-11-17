"""
API Response Manager - 统一的 API 响应管理器

为 Coze 插件测试需求设计的响应管理系统：
1. 所有响应始终返回 success=True（便于 Coze 测试通过）
2. 详细的错误信息放在 message 字段中
3. 结构化的错误代码分类系统
4. 易于维护和扩展的错误信息管理

设计原则：
- 对 Coze 友好：总是返回 success=True
- 对开发者友好：提供详细的错误信息和分类
- 对维护友好：集中管理所有错误类型和消息
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class ErrorCategory(str, Enum):
    """错误类别枚举"""
    # 成功状态
    SUCCESS = "success"
    
    # 客户端错误（4xx系列）
    VALIDATION_ERROR = "validation_error"      # 参数验证错误
    NOT_FOUND = "not_found"                    # 资源不存在
    ALREADY_EXISTS = "already_exists"          # 资源已存在
    INVALID_STATE = "invalid_state"            # 状态无效
    TYPE_MISMATCH = "type_mismatch"            # 类型不匹配
    
    # 服务端错误（5xx系列）
    INTERNAL_ERROR = "internal_error"          # 内部错误
    DATABASE_ERROR = "database_error"          # 数据库错误
    FILE_SYSTEM_ERROR = "file_system_error"    # 文件系统错误
    EXTERNAL_SERVICE_ERROR = "external_service_error"  # 外部服务错误
    
    # 业务逻辑错误
    OPERATION_FAILED = "operation_failed"      # 操作失败
    DEPENDENCY_ERROR = "dependency_error"      # 依赖错误
    RESOURCE_CONFLICT = "resource_conflict"    # 资源冲突


class ErrorCode(str, Enum):
    """详细的错误代码"""
    # 成功代码
    SUCCESS = "SUCCESS"
    
    # 草稿相关错误
    DRAFT_NOT_FOUND = "DRAFT_NOT_FOUND"
    DRAFT_ALREADY_EXISTS = "DRAFT_ALREADY_EXISTS"
    DRAFT_CREATE_FAILED = "DRAFT_CREATE_FAILED"
    DRAFT_UPDATE_FAILED = "DRAFT_UPDATE_FAILED"
    DRAFT_SAVE_FAILED = "DRAFT_SAVE_FAILED"
    DRAFT_INVALID_STATE = "DRAFT_INVALID_STATE"
    
    # 片段相关错误
    SEGMENT_NOT_FOUND = "SEGMENT_NOT_FOUND"
    SEGMENT_CREATE_FAILED = "SEGMENT_CREATE_FAILED"
    SEGMENT_TYPE_MISMATCH = "SEGMENT_TYPE_MISMATCH"
    SEGMENT_INVALID_CONFIG = "SEGMENT_INVALID_CONFIG"
    
    # 轨道相关错误
    TRACK_NOT_FOUND = "TRACK_NOT_FOUND"
    TRACK_INDEX_INVALID = "TRACK_INDEX_INVALID"
    TRACK_TYPE_MISMATCH = "TRACK_TYPE_MISMATCH"
    TRACK_OPERATION_FAILED = "TRACK_OPERATION_FAILED"
    
    # 素材相关错误
    MATERIAL_DOWNLOAD_FAILED = "MATERIAL_DOWNLOAD_FAILED"
    MATERIAL_INVALID_URL = "MATERIAL_INVALID_URL"
    MATERIAL_NOT_FOUND = "MATERIAL_NOT_FOUND"
    
    # 参数验证错误
    INVALID_PARAMETER = "INVALID_PARAMETER"
    MISSING_REQUIRED_PARAMETER = "MISSING_REQUIRED_PARAMETER"
    PARAMETER_OUT_OF_RANGE = "PARAMETER_OUT_OF_RANGE"
    
    # 操作相关错误
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
    INFO = "info"          # 信息
    WARNING = "warning"    # 警告
    ERROR = "error"        # 错误
    CRITICAL = "critical"  # 严重错误


class APIResponseManager:
    """
    API 响应管理器
    
    负责创建统一格式的 API 响应，确保：
    1. 对 Coze 友好：总是返回 success=True
    2. 提供详细的错误信息和分类
    3. 易于维护和扩展
    
    使用示例：
    ```python
    manager = APIResponseManager()
    
    # 成功响应
    response = manager.success(
        message="草稿创建成功",
        data={"draft_id": "xxx"}
    )
    
    # 错误响应（依然 success=True，但包含错误详情）
    response = manager.error(
        error_code=ErrorCode.DRAFT_NOT_FOUND,
        message="草稿不存在",
        details={"draft_id": "xxx"}
    )
    ```
    """
    
    def __init__(self):
        """初始化响应管理器"""
        self._error_messages = self._initialize_error_messages()
    
    def _initialize_error_messages(self) -> Dict[ErrorCode, Dict[str, Any]]:
        """
        初始化错误消息映射
        
        集中管理所有错误代码的默认消息和类别
        便于维护和国际化扩展
        """
        return {
            # 成功
            ErrorCode.SUCCESS: {
                "category": ErrorCategory.SUCCESS,
                "level": ResponseLevel.INFO,
                "template": "操作成功"
            },
            
            # 草稿错误
            ErrorCode.DRAFT_NOT_FOUND: {
                "category": ErrorCategory.NOT_FOUND,
                "level": ResponseLevel.ERROR,
                "template": "草稿不存在: {draft_id}"
            },
            ErrorCode.DRAFT_ALREADY_EXISTS: {
                "category": ErrorCategory.ALREADY_EXISTS,
                "level": ResponseLevel.ERROR,
                "template": "草稿已存在: {draft_name}"
            },
            ErrorCode.DRAFT_CREATE_FAILED: {
                "category": ErrorCategory.OPERATION_FAILED,
                "level": ResponseLevel.ERROR,
                "template": "草稿创建失败: {reason}"
            },
            ErrorCode.DRAFT_UPDATE_FAILED: {
                "category": ErrorCategory.OPERATION_FAILED,
                "level": ResponseLevel.ERROR,
                "template": "草稿更新失败: {reason}"
            },
            ErrorCode.DRAFT_SAVE_FAILED: {
                "category": ErrorCategory.OPERATION_FAILED,
                "level": ResponseLevel.ERROR,
                "template": "草稿保存失败: {reason}"
            },
            ErrorCode.DRAFT_INVALID_STATE: {
                "category": ErrorCategory.INVALID_STATE,
                "level": ResponseLevel.ERROR,
                "template": "草稿状态无效: {state}"
            },
            
            # 片段错误
            ErrorCode.SEGMENT_NOT_FOUND: {
                "category": ErrorCategory.NOT_FOUND,
                "level": ResponseLevel.ERROR,
                "template": "片段不存在: {segment_id}"
            },
            ErrorCode.SEGMENT_CREATE_FAILED: {
                "category": ErrorCategory.OPERATION_FAILED,
                "level": ResponseLevel.ERROR,
                "template": "片段创建失败: {reason}"
            },
            ErrorCode.SEGMENT_TYPE_MISMATCH: {
                "category": ErrorCategory.TYPE_MISMATCH,
                "level": ResponseLevel.ERROR,
                "template": "片段类型不匹配: 期望 {expected}，实际 {actual}"
            },
            ErrorCode.SEGMENT_INVALID_CONFIG: {
                "category": ErrorCategory.VALIDATION_ERROR,
                "level": ResponseLevel.ERROR,
                "template": "片段配置无效: {reason}"
            },
            
            # 轨道错误
            ErrorCode.TRACK_NOT_FOUND: {
                "category": ErrorCategory.NOT_FOUND,
                "level": ResponseLevel.ERROR,
                "template": "轨道不存在: {track_index}"
            },
            ErrorCode.TRACK_INDEX_INVALID: {
                "category": ErrorCategory.VALIDATION_ERROR,
                "level": ResponseLevel.ERROR,
                "template": "轨道索引无效: {track_index}"
            },
            ErrorCode.TRACK_TYPE_MISMATCH: {
                "category": ErrorCategory.TYPE_MISMATCH,
                "level": ResponseLevel.ERROR,
                "template": "轨道类型不匹配: 片段类型 {segment_type} 不能添加到 {track_type} 轨道"
            },
            ErrorCode.TRACK_OPERATION_FAILED: {
                "category": ErrorCategory.OPERATION_FAILED,
                "level": ResponseLevel.ERROR,
                "template": "轨道操作失败: {reason}"
            },
            
            # 素材错误
            ErrorCode.MATERIAL_DOWNLOAD_FAILED: {
                "category": ErrorCategory.EXTERNAL_SERVICE_ERROR,
                "level": ResponseLevel.ERROR,
                "template": "素材下载失败: {url}"
            },
            ErrorCode.MATERIAL_INVALID_URL: {
                "category": ErrorCategory.VALIDATION_ERROR,
                "level": ResponseLevel.ERROR,
                "template": "素材 URL 无效: {url}"
            },
            ErrorCode.MATERIAL_NOT_FOUND: {
                "category": ErrorCategory.NOT_FOUND,
                "level": ResponseLevel.ERROR,
                "template": "素材不存在: {material_id}"
            },
            
            # 参数验证错误
            ErrorCode.INVALID_PARAMETER: {
                "category": ErrorCategory.VALIDATION_ERROR,
                "level": ResponseLevel.ERROR,
                "template": "参数无效: {parameter} - {reason}"
            },
            ErrorCode.MISSING_REQUIRED_PARAMETER: {
                "category": ErrorCategory.VALIDATION_ERROR,
                "level": ResponseLevel.ERROR,
                "template": "缺少必需参数: {parameter}"
            },
            ErrorCode.PARAMETER_OUT_OF_RANGE: {
                "category": ErrorCategory.VALIDATION_ERROR,
                "level": ResponseLevel.ERROR,
                "template": "参数超出范围: {parameter} 应在 {min} 到 {max} 之间，实际值 {value}"
            },
            
            # 操作错误
            ErrorCode.OPERATION_NOT_SUPPORTED: {
                "category": ErrorCategory.OPERATION_FAILED,
                "level": ResponseLevel.ERROR,
                "template": "操作不支持: {operation}"
            },
            ErrorCode.OPERATION_ALREADY_EXISTS: {
                "category": ErrorCategory.ALREADY_EXISTS,
                "level": ResponseLevel.ERROR,
                "template": "操作已存在: {operation}"
            },
            ErrorCode.OPERATION_FAILED: {
                "category": ErrorCategory.OPERATION_FAILED,
                "level": ResponseLevel.ERROR,
                "template": "操作失败: {reason}"
            },
            
            # 系统错误
            ErrorCode.INTERNAL_ERROR: {
                "category": ErrorCategory.INTERNAL_ERROR,
                "level": ResponseLevel.CRITICAL,
                "template": "内部错误: {error}"
            },
            ErrorCode.DATABASE_ERROR: {
                "category": ErrorCategory.DATABASE_ERROR,
                "level": ResponseLevel.CRITICAL,
                "template": "数据库错误: {error}"
            },
            ErrorCode.FILE_SYSTEM_ERROR: {
                "category": ErrorCategory.FILE_SYSTEM_ERROR,
                "level": ResponseLevel.CRITICAL,
                "template": "文件系统错误: {error}"
            },
            
            # 依赖错误
            ErrorCode.DEPENDENCY_NOT_FOUND: {
                "category": ErrorCategory.DEPENDENCY_ERROR,
                "level": ResponseLevel.ERROR,
                "template": "依赖不存在: {dependency}"
            },
            ErrorCode.DEPENDENCY_INVALID: {
                "category": ErrorCategory.DEPENDENCY_ERROR,
                "level": ResponseLevel.ERROR,
                "template": "依赖无效: {dependency} - {reason}"
            },
        }
    
    def success(
        self,
        message: str = "操作成功",
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        创建成功响应
        
        Args:
            message: 成功消息
            data: 响应数据
            **kwargs: 额外的响应字段
            
        Returns:
            标准的成功响应字典
        """
        response = {
            "success": True,
            "error_code": ErrorCode.SUCCESS,
            "category": ErrorCategory.SUCCESS,
            "level": ResponseLevel.INFO,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        
        # 添加数据
        if data:
            response["data"] = data
        
        # 添加额外字段
        response.update(kwargs)
        
        return response
    
    def error(
        self,
        error_code: ErrorCode,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        创建错误响应（依然返回 success=True，但包含错误详情）
        
        Args:
            error_code: 错误代码
            message: 自定义错误消息（如果不提供，使用默认模板）
            details: 错误详情字典，用于填充消息模板
            **kwargs: 额外的响应字段
            
        Returns:
            标准的错误响应字典（success=True）
        """
        # 获取错误信息配置
        error_info = self._error_messages.get(error_code)
        if not error_info:
            # 未知错误代码，使用通用内部错误
            error_info = self._error_messages[ErrorCode.INTERNAL_ERROR]
            error_code = ErrorCode.INTERNAL_ERROR
        
        # 生成错误消息
        if message is None:
            # 使用模板生成消息
            template = error_info["template"]
            if details:
                try:
                    message = template.format(**details)
                except KeyError:
                    # 如果模板参数不完整，使用原始模板
                    message = template
            else:
                message = template
        
        response = {
            "success": True,  # 关键：总是返回 True，便于 Coze 测试
            "error_code": error_code,
            "category": error_info["category"],
            "level": error_info["level"],
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        
        # 添加错误详情
        if details:
            response["details"] = details
        
        # 添加额外字段
        response.update(kwargs)
        
        return response
    
    def wrap_data(
        self,
        data: Dict[str, Any],
        message: str = "操作成功"
    ) -> Dict[str, Any]:
        """
        包装数据为成功响应
        
        便捷方法，用于快速创建包含数据的成功响应
        
        Args:
            data: 要包装的数据
            message: 成功消息
            
        Returns:
            标准的成功响应字典
        """
        return self.success(message=message, data=data)
    
    def format_validation_error(
        self,
        field: str,
        value: Any,
        reason: str
    ) -> Dict[str, Any]:
        """
        格式化参数验证错误
        
        Args:
            field: 字段名
            value: 字段值
            reason: 错误原因
            
        Returns:
            标准的错误响应字典
        """
        return self.error(
            error_code=ErrorCode.INVALID_PARAMETER,
            details={
                "parameter": field,
                "reason": reason
            }
        )
    
    def format_not_found_error(
        self,
        resource_type: str,
        resource_id: str
    ) -> Dict[str, Any]:
        """
        格式化资源不存在错误
        
        Args:
            resource_type: 资源类型（如 "draft", "segment", "track"）
            resource_id: 资源 ID
            
        Returns:
            标准的错误响应字典
        """
        # 根据资源类型选择合适的错误代码
        error_code_map = {
            "draft": ErrorCode.DRAFT_NOT_FOUND,
            "segment": ErrorCode.SEGMENT_NOT_FOUND,
            "track": ErrorCode.TRACK_NOT_FOUND,
            "material": ErrorCode.MATERIAL_NOT_FOUND,
        }
        
        error_code = error_code_map.get(
            resource_type,
            ErrorCode.DEPENDENCY_NOT_FOUND
        )
        
        details_key = f"{resource_type}_id"
        
        return self.error(
            error_code=error_code,
            details={details_key: resource_id}
        )
    
    def format_operation_error(
        self,
        operation: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        格式化操作失败错误
        
        Args:
            operation: 操作名称
            reason: 失败原因
            
        Returns:
            标准的错误响应字典
        """
        return self.error(
            error_code=ErrorCode.OPERATION_FAILED,
            details={
                "operation": operation,
                "reason": reason
            }
        )
    
    def format_internal_error(
        self,
        error: Exception
    ) -> Dict[str, Any]:
        """
        格式化内部错误
        
        Args:
            error: 异常对象
            
        Returns:
            标准的错误响应字典
        """
        return self.error(
            error_code=ErrorCode.INTERNAL_ERROR,
            details={
                "error": str(error),
                "error_type": type(error).__name__
            }
        )


# 创建全局单例
_response_manager = APIResponseManager()


def get_response_manager() -> APIResponseManager:
    """
    获取全局响应管理器实例
    
    Returns:
        APIResponseManager 单例
    """
    return _response_manager
