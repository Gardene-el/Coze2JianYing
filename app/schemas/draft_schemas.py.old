"""
草稿生成 API 的数据模型 (Pydantic Schemas)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DraftStatus(str, Enum):
    """草稿生成状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DraftGenerateRequest(BaseModel):
    """草稿生成请求模型"""
    content: str = Field(..., description="Coze 导出的 JSON 数据（字符串格式）")
    output_folder: Optional[str] = Field(None, description="输出文件夹路径（可选，默认使用检测到的剪映文件夹）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": '{"draft_id": "...", "project_name": "测试项目", ...}',
                "output_folder": None
            }
        }


class DraftInfo(BaseModel):
    """草稿信息模型"""
    draft_id: str = Field(..., description="草稿ID")
    project_name: str = Field(..., description="项目名称")
    folder_path: str = Field(..., description="草稿文件夹完整路径")


class DraftGenerateResponse(BaseModel):
    """草稿生成响应模型"""
    status: str = Field(..., description="响应状态")
    message: str = Field(..., description="响应消息")
    draft_count: int = Field(..., description="生成的草稿数量")
    drafts: List[DraftInfo] = Field(..., description="生成的草稿列表")
    timestamp: datetime = Field(default_factory=datetime.now, description="生成时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "成功生成 1 个草稿",
                "draft_count": 1,
                "drafts": [
                    {
                        "draft_id": "12345678-1234-1234-1234-123456789abc",
                        "project_name": "测试项目",
                        "folder_path": "C:/Users/Username/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft/12345678-1234-1234-1234-123456789abc"
                    }
                ],
                "timestamp": "2025-11-04T08:00:00"
            }
        }


class DraftStatusResponse(BaseModel):
    """草稿状态查询响应"""
    draft_id: str = Field(..., description="草稿ID")
    status: DraftStatus = Field(..., description="草稿状态")
    project_name: Optional[str] = Field(None, description="项目名称")
    folder_path: Optional[str] = Field(None, description="草稿文件夹路径")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    error_message: Optional[str] = Field(None, description="错误信息（如果失败）")


class DraftListItem(BaseModel):
    """草稿列表项"""
    draft_id: str
    project_name: str
    created_at: datetime
    folder_path: str


class DraftListResponse(BaseModel):
    """草稿列表响应"""
    total: int = Field(..., description="总数量")
    drafts: List[DraftListItem] = Field(..., description="草稿列表")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    detail: Optional[str] = Field(None, description="详细错误信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")


class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="API版本")
    timestamp: datetime = Field(default_factory=datetime.now, description="检查时间")
    services: Dict[str, bool] = Field(..., description="各服务状态")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2025-11-04T08:00:00",
                "services": {
                    "draft_generator": True,
                    "material_downloader": True
                }
            }
        }
