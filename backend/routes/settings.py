"""
設置 API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from libs.config import OPENAI_API_KEY, AI_MODEL, TARGET_LANG, SOURCE_LANG
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/settings")
async def get_settings():
    """獲取設置"""
    return {
        'apiKey': OPENAI_API_KEY[:10] + '***' if OPENAI_API_KEY else '',
        'model': AI_MODEL,
        'language': TARGET_LANG,
        'sourceLang': SOURCE_LANG
    }


@router.post("/settings")
async def update_settings(settings: Dict[str, Any]):
    """接收設置（僅用於確認，不保存到全局配置）"""
    try:
        logger.info(f"Settings received from frontend (not saved to global config)")
        # 前端設置只保存在瀏覽器 cookie 中，不修改後端全局配置
        return {'success': True, 'message': 'Settings received (stored in browser cookie only)'}
        
    except Exception as e:
        logger.error(f"Settings update error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

