"""
示例 API 的数据模型 (Pydantic Schemas)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ItemBase(BaseModel):
    """Item 基础模型"""
    name: str = Field(..., description="项目名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="项目描述")
    price: float = Field(..., description="价格", ge=0)
    is_active: bool = Field(True, description="是否激活")


class ItemCreate(ItemBase):
    """创建 Item 的请求模型"""
    pass


class ItemUpdate(BaseModel):
    """更新 Item 的请求模型 (所有字段可选)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ItemResponse(ItemBase):
    """Item 响应模型"""
    id: int = Field(..., description="项目ID")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    status: str = "success"


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: datetime
    version: str


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    filename: str
    size: int
    content_type: str
    message: str


class QueryParams(BaseModel):
    """查询参数模型"""
    skip: int = Field(0, ge=0, description="跳过的记录数")
    limit: int = Field(10, ge=1, le=100, description="返回的记录数")
    search: Optional[str] = Field(None, description="搜索关键词")
    is_active: Optional[bool] = Field(None, description="是否激活")


class BatchItemsCreate(BaseModel):
    """批量创建 Items"""
    items: List[ItemCreate] = Field(..., description="Item列表")


class BatchItemsResponse(BaseModel):
    """批量操作响应"""
    created_count: int
    items: List[ItemResponse]
