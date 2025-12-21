"""
API 路由模組
"""
from fastapi import APIRouter

# 創建主路由器
api_router = APIRouter(prefix="/api")

# 導入各個路由模組（這會觸發路由註冊）
from . import health, settings, analyze, generate, files

# 註冊所有路由
api_router.include_router(health.router)
api_router.include_router(settings.router)
api_router.include_router(analyze.router)
api_router.include_router(generate.router)
api_router.include_router(files.router)

__all__ = ['api_router']

