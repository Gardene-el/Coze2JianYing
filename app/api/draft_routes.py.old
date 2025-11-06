"""
草稿生成 API 路由
提供草稿生成的核心 API 端点
"""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Optional
from datetime import datetime
import json
import os
from pathlib import Path

from app.schemas.draft_schemas import (
    DraftGenerateRequest,
    DraftGenerateResponse,
    DraftStatusResponse,
    DraftListResponse,
    DraftListItem,
    DraftStatus,
    DraftInfo,
    ErrorResponse,
    HealthCheckResponse
)
from app.utils.draft_generator import DraftGenerator
from app.utils.logger import get_logger

router = APIRouter(prefix="/api/draft", tags=["草稿生成"])
logger = get_logger(__name__)

# 全局草稿生成器实例
draft_generator = DraftGenerator()

# 内存中的草稿状态存储（简单实现，生产环境应使用数据库）
draft_status_store: Dict[str, Dict] = {}


@router.post(
    "/generate",
    response_model=DraftGenerateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="生成剪映草稿",
    description="接收 Coze 导出的 JSON 数据，生成剪映草稿文件"
)
async def generate_draft(request: DraftGenerateRequest):
    """
    生成剪映草稿
    
    - **content**: Coze 导出的 JSON 数据（字符串格式）
    - **output_folder**: 可选的输出文件夹路径
    
    返回生成的草稿信息，包括草稿ID和文件夹路径
    """
    logger.info("=" * 60)
    logger.info("收到草稿生成请求")
    logger.info(f"内容长度: {len(request.content)} 字符")
    logger.info(f"输出文件夹: {request.output_folder or '默认'}")
    
    try:
        # 验证 JSON 格式
        try:
            json_data = json.loads(request.content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的 JSON 格式: {str(e)}"
            )
        
        # 生成草稿
        logger.info("开始生成草稿...")
        draft_ids = draft_generator.generate(
            content=request.content,
            output_folder=request.output_folder
        )
        
        if not draft_ids:
            logger.error("草稿生成失败：没有生成任何草稿")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="草稿生成失败：未能生成任何草稿"
            )
        
        logger.info(f"成功生成 {len(draft_ids)} 个草稿")
        
        # 构建响应
        drafts_info = []
        for draft_id in draft_ids:
            # 获取草稿文件夹路径
            if request.output_folder:
                folder_path = os.path.join(request.output_folder, draft_id)
            else:
                # 使用默认检测的文件夹
                default_folder = draft_generator.detect_default_draft_folder()
                if default_folder:
                    folder_path = os.path.join(default_folder, draft_id)
                else:
                    folder_path = f"未知路径/{draft_id}"
            
            # 尝试从 JSON 数据中获取项目名称
            project_name = "未命名项目"
            if isinstance(json_data, dict):
                project_name = json_data.get('project_name', json_data.get('draft_name', project_name))
            elif isinstance(json_data, list) and len(json_data) > 0:
                first_draft = json_data[0]
                if isinstance(first_draft, dict):
                    project_name = first_draft.get('project_name', first_draft.get('draft_name', project_name))
            
            draft_info = DraftInfo(
                draft_id=draft_id,
                project_name=project_name,
                folder_path=folder_path
            )
            drafts_info.append(draft_info)
            
            # 存储草稿状态
            draft_status_store[draft_id] = {
                "status": DraftStatus.COMPLETED,
                "project_name": project_name,
                "folder_path": folder_path,
                "created_at": datetime.now(),
                "error_message": None
            }
        
        response = DraftGenerateResponse(
            status="success",
            message=f"成功生成 {len(draft_ids)} 个草稿",
            draft_count=len(draft_ids),
            drafts=drafts_info
        )
        
        logger.info("草稿生成成功")
        logger.info("=" * 60)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"草稿生成过程中发生错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"草稿生成失败: {str(e)}"
        )


@router.get(
    "/status/{draft_id}",
    response_model=DraftStatusResponse,
    summary="查询草稿状态",
    description="根据草稿ID查询草稿的生成状态和信息"
)
async def get_draft_status(draft_id: str):
    """
    查询草稿状态
    
    - **draft_id**: 草稿的唯一标识符
    
    返回草稿的当前状态和相关信息
    """
    logger.info(f"查询草稿状态: {draft_id}")
    
    if draft_id not in draft_status_store:
        logger.warning(f"草稿不存在: {draft_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"草稿 {draft_id} 不存在"
        )
    
    draft_data = draft_status_store[draft_id]
    
    return DraftStatusResponse(
        draft_id=draft_id,
        status=draft_data["status"],
        project_name=draft_data.get("project_name"),
        folder_path=draft_data.get("folder_path"),
        created_at=draft_data.get("created_at"),
        error_message=draft_data.get("error_message")
    )


@router.get(
    "/list",
    response_model=DraftListResponse,
    summary="列出所有草稿",
    description="获取所有已生成草稿的列表"
)
async def list_drafts(
    skip: int = 0,
    limit: int = 100
):
    """
    列出所有草稿
    
    - **skip**: 跳过的记录数（分页）
    - **limit**: 返回的最大记录数
    
    返回草稿列表和总数
    """
    logger.info(f"列出草稿列表 (skip={skip}, limit={limit})")
    
    all_drafts = []
    for draft_id, draft_data in draft_status_store.items():
        if draft_data["status"] == DraftStatus.COMPLETED:
            all_drafts.append(
                DraftListItem(
                    draft_id=draft_id,
                    project_name=draft_data.get("project_name", "未命名"),
                    created_at=draft_data.get("created_at", datetime.now()),
                    folder_path=draft_data.get("folder_path", "")
                )
            )
    
    # 按创建时间倒序排序
    all_drafts.sort(key=lambda x: x.created_at, reverse=True)
    
    # 分页
    total = len(all_drafts)
    paginated_drafts = all_drafts[skip:skip + limit]
    
    logger.info(f"返回 {len(paginated_drafts)} 个草稿（总共 {total} 个）")
    
    return DraftListResponse(
        total=total,
        drafts=paginated_drafts
    )


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="健康检查",
    description="检查草稿生成服务的健康状态"
)
async def health_check():
    """
    健康检查
    
    返回服务状态和各个组件的运行情况
    """
    logger.debug("执行健康检查")
    
    # 检查各个服务组件
    services_status = {
        "draft_generator": True,  # 草稿生成器始终可用
        "material_downloader": True  # 素材下载器始终可用
    }
    
    # 检查是否能检测到剪映文件夹
    default_folder = draft_generator.detect_default_draft_folder()
    services_status["jianying_folder_detected"] = default_folder is not None
    
    overall_status = "healthy" if all(services_status.values()) else "degraded"
    
    return HealthCheckResponse(
        status=overall_status,
        version="1.0.0",
        services=services_status
    )


@router.delete(
    "/clear",
    summary="清空草稿状态存储",
    description="清空内存中的草稿状态存储（仅用于测试）"
)
async def clear_draft_store():
    """
    清空草稿状态存储
    
    ⚠️ 注意：这只会清空内存中的状态记录，不会删除实际的草稿文件
    """
    logger.info("清空草稿状态存储")
    draft_status_store.clear()
    return {"message": "草稿状态存储已清空", "status": "success"}
