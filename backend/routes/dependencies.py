"""
路由依賴注入函數
"""
from typing import Optional
from fastapi import Depends, HTTPException
from pydantic import BaseModel

from helpers.api_key import validate_and_get_api_key
from libs.config import AI_MODEL


class ValidatedSettings(BaseModel):
    """驗證後的設置"""
    api_key: str
    model: str
    source_lang: str
    target_lang: str


def get_validated_settings(settings: dict) -> ValidatedSettings:
    """
    驗證並獲取設置（依賴注入）
    
    Args:
        settings: 設置字典
        
    Returns:
        ValidatedSettings: 驗證後的設置
        
    Raises:
        HTTPException: 如果 API Key 無效
    """
    api_key = validate_and_get_api_key(settings)
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail={
                'success': False,
                'error': 'API Key required',
                'details': 'OpenAI API Key is required. Please set it in Settings.'
            }
        )
    
    def _get_setting_value(values: dict, *keys: str, default: str) -> str:
        for key in keys:
            value = values.get(key)
            if value is not None and str(value).strip():
                return str(value).strip()
        return default

    model = settings.get('model') or AI_MODEL
    source_lang = _get_setting_value(
        settings,
        'sourceLang',
        'sourceLanguage',
        'source_language',
        default='English'
    )
    target_lang = _get_setting_value(
        settings,
        'language',
        'targetLang',
        'targetLanguage',
        'target_language',
        default='Chinese'
    )
    
    return ValidatedSettings(
        api_key=api_key,
        model=model,
        source_lang=source_lang,
        target_lang=target_lang
    )


def validate_settings_from_request(request: BaseModel) -> ValidatedSettings:
    """
    從請求對象中驗證並獲取設置
    
    Args:
        request: 包含 settings 屬性的請求對象
        
    Returns:
        ValidatedSettings: 驗證後的設置
    """
    settings_dict = request.settings.dict() if hasattr(request.settings, 'dict') else request.settings
    return get_validated_settings(settings_dict)

