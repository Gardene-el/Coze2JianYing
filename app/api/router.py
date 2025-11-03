"""
API 路由汇总
"""
from fastapi import APIRouter
from app.api.example_routes import router as example_router

# 创建主路由
api_router = APIRouter()

# 注册各个子路由
api_router.include_router(example_router)

# 可以继续添加其他路由
# api_router.include_router(other_router)
