"""
API Key 驗證和管理相關工具函數
"""
import os
from libs.config import OPENAI_API_KEY
import logging

logger = logging.getLogger(__name__)


def validate_and_get_api_key(settings: dict = None) -> str:
    """
    驗證並獲取 API Key
    
    Args:
        settings: 包含 API Key 的設置字典
        
    Returns:
        str: API Key，如果無效則返回 None
        
    Raises:
        ValueError: 當 API Key 無效或缺失時
    """
    api_key = None
    
    # 優先使用前端傳來的 API Key
    if settings and settings.get('apiKey'):
        provided_key = settings.get('apiKey')
        # 檢查是否為掩碼值（前端可能傳送掩碼後的 key）
        if not provided_key.startswith('sk-***'):
            api_key = provided_key
            os.environ['OPENAI_API_KEY'] = api_key
            logger.info("Using API Key from frontend settings")
    
    # 如果沒有從前端獲取，使用環境變數中的
    if not api_key and OPENAI_API_KEY:
        api_key = OPENAI_API_KEY
    
    return api_key


def require_api_key(settings: dict = None) -> str:
    """
    要求必須提供有效的 API Key
    
    Args:
        settings: 包含 API Key 的設置字典
        
    Returns:
        str: API Key
        
    Raises:
        ValueError: 當 API Key 無效或缺失時
    """
    api_key = validate_and_get_api_key(settings)
    
    if not api_key:
        error_msg = "OpenAI API Key is required. Please set it in Settings."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    return api_key


def format_api_key_error(error_msg: str) -> str:
    """格式化 API Key 相關錯誤訊息"""
    if any(keyword in error_msg.lower() for keyword in ['api', 'key', 'unauthorized', 'forbidden']) or \
       any(code in error_msg for code in ['401', '403']):
        return f"API Key Error: {error_msg}\n\nThis error is likely due to missing or invalid OpenAI API Key. Please check your API Key in Settings."
    elif 'OPENAI_API_KEY' in error_msg or '未設定' in error_msg:
        return f"API Key Missing: {error_msg}\n\nPlease set your OpenAI API Key in Settings."
    return error_msg

