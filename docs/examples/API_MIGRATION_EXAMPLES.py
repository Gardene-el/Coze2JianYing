"""
API 端点迁移示例

展示如何将现有的 API 端点迁移到使用 response_builder 工具函数

本文件包含：
1. 迁移前后的对比
2. 常见模式的处理方法
3. 最佳实践建议
"""

# ============================================================================
# 示例 1：简单的资源查询端点
# ============================================================================

# --- 迁移前 ---
from fastapi import APIRouter, HTTPException, status

@router.get("/api/draft/{draft_id}")
async def get_draft_old(draft_id: str):
    """旧版本：使用 HTTPException"""
    draft = draft_manager.get_draft(draft_id)
    
    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"草稿 {draft_id} 不存在"
        )
    
    return {
        "success": True,
        "draft": draft,
        "message": "查询成功"
    }


# --- 迁移后 ---
from fastapi import APIRouter, status
from app.backend.utils.response_builder import build_success, build_error, wrap_data, build_not_found_error, build_validation_error, build_operation_error, build_internal_error, success_response, error_response, not_found_response, internal_error_response, ErrorCode

@router.get("/api/draft/{draft_id}")
async def get_draft_new(draft_id: str):
    """新版本：使用 response_builder"""
    draft = draft_manager.get_draft(draft_id)
    
    if draft is None:
        return build_not_found_error("draft", draft_id)
    
    return wrap_data(
        data={"draft": draft},
        message="查询成功"
    )


# ============================================================================
# 示例 2：创建资源端点（带参数验证）
# ============================================================================

# --- 迁移前 ---
@router.post("/api/segment/create")
async def create_segment_old(request: CreateSegmentRequest):
    """旧版本：抛出异常"""
    try:
        # 参数验证
        if request.volume < 0 or request.volume > 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="音量必须在 0-2 之间"
            )
        
        # 创建片段
        result = segment_manager.create_segment(request)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        return {
            "success": True,
            "segment_id": result["segment_id"],
            "message": "片段创建成功"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建片段失败: {str(e)}"
        )


# --- 迁移后 ---
@router.post("/api/segment/create")
async def create_segment_new(request: CreateSegmentRequest):
    """新版本：始终返回 success=True"""
    try:
        # 参数验证（依然返回 success=True）
        if request.volume < 0 or request.volume > 2:
            return build_validation_error(
                field="volume",
                value=request.volume,
                reason="音量必须在 0-2 之间"
            )
        
        # 创建片段
        result = segment_manager.create_segment(request)
        
        if not result["success"]:
            return build_error(
                error_code=ErrorCode.SEGMENT_CREATE_FAILED,
                details={"reason": result["message"]}
            )
        
        # 成功
        success_response = build_success(
            message="片段创建成功",
            data={"segment_id": result["segment_id"]}
        )
        
        # 提升 segment_id 到顶层（保持向后兼容）
        return {
            "segment_id": result["segment_id"],
            **success_response
        }
    
    except Exception as e:
        # 捕获所有异常，返回内部错误（依然 success=True）
        return build_internal_error(e)


# ============================================================================
# 示例 3：复杂的业务逻辑端点
# ============================================================================

# --- 迁移前 ---
@router.post("/api/draft/{draft_id}/add_segment")
async def add_segment_old(draft_id: str, segment_id: str):
    """旧版本：多个异常点"""
    # 验证草稿存在
    if not draft_manager.exists(draft_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"草稿 {draft_id} 不存在"
        )
    
    # 验证片段存在
    if not segment_manager.exists(segment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"片段 {segment_id} 不存在"
        )
    
    # 验证类型匹配
    segment = segment_manager.get(segment_id)
    track_type = draft_manager.get_track_type(draft_id)
    
    if not types_match(segment["type"], track_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"片段类型 {segment['type']} 不匹配轨道类型 {track_type}"
        )
    
    # 执行添加
    try:
        draft_manager.add_segment(draft_id, segment_id)
        return {"success": True, "message": "片段添加成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加片段失败: {str(e)}"
        )


# --- 迁移后 ---
@router.post("/api/draft/{draft_id}/add_segment")
async def add_segment_new(draft_id: str, segment_id: str):
    """新版本：统一的错误处理"""
    try:
        # 验证草稿存在（返回结构化错误）
        if not draft_manager.exists(draft_id):
            return build_not_found_error("draft", draft_id)
        
        # 验证片段存在
        if not segment_manager.exists(segment_id):
            return build_not_found_error("segment", segment_id)
        
        # 验证类型匹配
        segment = segment_manager.get(segment_id)
        track_type = draft_manager.get_track_type(draft_id)
        
        if not types_match(segment["type"], track_type):
            return build_error(
                error_code=ErrorCode.TRACK_TYPE_MISMATCH,
                details={
                    "segment_type": segment["type"],
                    "track_type": track_type
                }
            )
        
        # 执行添加
        draft_manager.add_segment(draft_id, segment_id)
        return build_success(message="片段添加成功")
        
    except Exception as e:
        return build_internal_error(e)


# ============================================================================
# 迁移检查清单
# ============================================================================

"""
迁移一个端点时的检查清单：

□ 1. 导入 response_builder 工具函数
   from app.backend.utils.response_builder import build_success, build_error, wrap_data, ErrorCode

□ 2. 替换所有 HTTPException
   - 404 Not Found -> build_not_found_error()
   - 400 Bad Request -> build_validation_error()
   - 500 Internal Server Error -> build_internal_error()

□ 4. 替换成功响应
   - 简单数据 -> wrap_data()
   - 复杂响应 -> build_success()

□ 5. 捕获所有异常
   try:
       # 业务逻辑
   except Exception as e:
       return build_internal_error(e)

□ 6. 更新响应模型（如果有）
   - 添加可选字段：error_code, category, level, details

□ 7. 更新 HTTP 状态码
   - 将 status.HTTP_201_CREATED 改为 status.HTTP_200_OK
   - 保持其他状态码不变

□ 8. 保持向后兼容
   - 如果有必需字段（如 draft_id），确保提升到顶层
   - 检查是否影响现有客户端

□ 9. 测试
   - 成功场景
   - 各种错误场景
   - 验证 success 始终为 True

□ 10. 更新文档
   - API 端点文档
   - 示例代码
"""


# ============================================================================
# 常见模式和最佳实践
# ============================================================================

# 模式 1：资源不存在
def check_resource_exists(resource_type: str, resource_id: str):
    """统一的资源存在性检查"""
    if not manager.exists(resource_id):
        return build_not_found_error(resource_type, resource_id)
    return None  # 资源存在，无错误


# 模式 2：参数验证
def validate_parameter(name: str, value: Any, validator_func) -> Optional[Dict]:
    """统一的参数验证"""
    try:
        validator_func(value)
        return None  # 验证通过
    except ValueError as e:
        return build_validation_error(
            field=name,
            value=value,
            reason=str(e)
        )


# 模式 3：操作结果检查
def check_operation_result(result: Dict, operation_name: str):
    """统一的操作结果检查"""
    if not result.get("success"):
        return build_operation_error(
            operation=operation_name,
            reason=result.get("message", "未知错误")
        )
    return None  # 操作成功


# 使用这些模式的端点示例
@router.post("/api/example")
async def example_endpoint(resource_id: str, param: float):
    """使用统一模式的端点"""
    try:
        # 1. 检查资源
        error = check_resource_exists("resource", resource_id)
        if error:
            return error
        
        # 2. 验证参数
        error = validate_parameter("param", param, lambda x: x > 0)
        if error:
            return error
        
        # 3. 执行操作
        result = perform_operation(resource_id, param)
        
        # 4. 检查结果
        error = check_operation_result(result, "示例操作")
        if error:
            return error
        
        # 5. 返回成功
        return build_success(
            message="操作成功",
            data=result
        )
        
    except Exception as e:
        return build_internal_error(e)


# ============================================================================
# 提示和技巧
# ============================================================================

"""
提示和技巧：

1. 使用辅助方法
   - format_not_found_error() 用于资源不存在
   - format_validation_error() 用于参数验证
   - format_operation_error() 用于业务逻辑错误
   - format_internal_error() 用于异常捕获

2. 保持一致性
   - 所有端点都应该返回相同的响应结构
   - 使用相同的错误代码表示相同的错误
   - 消息格式保持一致

3. 详细的错误信息
   - 在 details 字段中提供足够的信息用于调试
   - 但不要暴露敏感信息（如数据库结构、内部路径）

4. 日志记录
   - 在返回错误前记录日志
   - logger.error() 用于错误情况
   - logger.info() 用于成功情况

5. 测试覆盖
   - 测试成功场景
   - 测试每种可能的错误场景
   - 验证 success 始终为 True
   - 验证 error_code 的正确性
"""
