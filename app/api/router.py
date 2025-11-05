"""
API 路由汇总
"""
from fastapi import APIRouter
from app.api.example_routes import router as example_router
from app.api.draft_routes import router as draft_router
from app.api.material_routes import router as material_router

# 创建主路由
api_router = APIRouter()

# 注册各个子路由
api_router.include_router(draft_router)  # 草稿生成路由（核心功能）
api_router.include_router(material_router)  # 素材管理路由（新增）
api_router.include_router(example_router)  # 示例路由

# 可以继续添加其他路由
# api_router.include_router(other_router)
