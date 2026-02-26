"""
API 路由汇总
"""

from fastapi import APIRouter

from app.backend.api.basic import router as basic_router  # 基础操作端点
from app.backend.api.easy import router as easy_router  # 简化操作端点

# 创建主路由
api_router = APIRouter()

# 注册各个子路由
# 新 API 设计端点（符合 API_ENDPOINTS_REFERENCE.md）
api_router.include_router(easy_router)
api_router.include_router(basic_router)
