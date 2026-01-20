"""
健康檢查路由
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    """健康檢查"""
    return {
        'status': 'ok',
        'message': 'Anki Generator API is running',
        'backend': 'backend2 (Python/FastAPI)'
    }

