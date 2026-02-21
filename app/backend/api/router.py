"""
API 路由汇总
"""

from fastapi import APIRouter

from app.backend.api.draft_routes import router as draft_router  # Draft 操作端点
from app.backend.api.easy_routes import router as easy_router  # Easy API 端点
from app.backend.api.segment_routes import router as segment_router  # Segment 创建和操作端点

# 创建主路由
api_router = APIRouter()

# 注册各个子路由
# 新 API 设计端点（符合 API_ENDPOINTS_REFERENCE.md）
api_router.include_router(segment_router)  # Segment 创建和操作
api_router.include_router(draft_router)
api_router.include_router(easy_router)     # Easy API (简化 add_xxs 系列)
