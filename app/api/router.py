"""
API 路由汇总
"""
from fastapi import APIRouter
from app.api.example_routes import router as example_router
from app.api.draft_routes import router as old_draft_router  # 保留旧的草稿生成端点
from app.api.new_draft_routes import router as new_draft_router  # 新的 Draft 操作端点
from app.api.segment_routes import router as segment_router  # Segment 创建和操作端点

# 创建主路由
api_router = APIRouter()

# 注册各个子路由
# 新 API 设计端点（符合 API_ENDPOINTS_REFERENCE.md）
api_router.include_router(segment_router)  # Segment 创建和操作
api_router.include_router(new_draft_router)  # Draft 操作（create, add_track, add_segment, save 等）

# 旧 API 端点（保留用于向后兼容，仅 /generate 等简单端点）
api_router.include_router(old_draft_router)  # 草稿生成路由（/generate, /status, /list 等）

# 示例路由
api_router.include_router(example_router)  # 示例路由

# 注意：旧的 material_routes.py 中的 add-videos, add-audios, add-images, add-captions 端点已被移除
# 新设计使用 segment_routes 和 new_draft_routes 替代
