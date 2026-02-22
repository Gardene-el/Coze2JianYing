"""
API 路由汇总
"""

from fastapi import APIRouter

from app.backend.api.draft_routes import router as draft_router  # Draft 操作端点
from app.backend.api.segments.audio_routes import router as audio_router
from app.backend.api.segments.video_routes import router as video_router
from app.backend.api.segments.sticker_routes import router as sticker_router
from app.backend.api.segments.text_routes import router as text_router
from app.backend.api.segments.effect_routes import router as effect_router
from app.backend.api.segments.filter_routes import router as filter_router

# 创建主路由
api_router = APIRouter()

# 注册各个子路由
api_router.include_router(audio_router)    # AudioSegment 端点
api_router.include_router(video_router)    # VideoSegment 端点
api_router.include_router(sticker_router)  # StickerSegment 端点
api_router.include_router(text_router)     # TextSegment 端点
api_router.include_router(effect_router)   # EffectSegment 端点
api_router.include_router(filter_router)   # FilterSegment 端点
api_router.include_router(draft_router)    # Draft 草稿操作
