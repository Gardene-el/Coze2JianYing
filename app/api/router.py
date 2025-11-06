"""
API 路由汇总
"""
from fastapi import APIRouter
from app.api.new_draft_routes import router as new_draft_router  # Draft 操作端点
from app.api.segment_routes import router as segment_router  # Segment 创建和操作端点

# 创建主路由
api_router = APIRouter()

# 注册各个子路由
# 新 API 设计端点（符合 API_ENDPOINTS_REFERENCE.md）
api_router.include_router(segment_router)  # Segment 创建和操作
api_router.include_router(new_draft_router)  # Draft 操作（create, add_track, add_segment, save 等）

# 注意：
# - 旧的 material_routes.py 中的 add-videos, add-audios, add-images, add-captions 端点已被移除
# - 旧的 draft_routes.py 中的 /generate, /status, /list 等端点已被移除
# - example_routes.py 示例路由已被移除
# 新设计统一使用 segment_routes 和 new_draft_routes
