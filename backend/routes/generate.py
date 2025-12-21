"""
生成 API 路由
"""
import os
import traceback
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
import logging

from libs.config import AI_MODEL, OPENAI_API_KEY
from service.main_processor import MainProcessor
from .generate_helpers import (
    parse_request_data,
    prepare_session_directories,
    process_vocab_list,
    process_image_paths,
    determine_card_type,
    get_language_settings,
    load_generated_cards,
    format_error_response
)
from helpers.api_key import validate_and_get_api_key

router = APIRouter()
logger = logging.getLogger(__name__)

processor = MainProcessor()


@router.post("/generate/article")
async def generate_article(data: Dict[str, Any]):
    """從文章生成卡片"""
    try:
        logger.info(f"Article generation request: {list(data.keys())}")
        
        # 解析請求數據
        req_data = parse_request_data(data)
        vocab_list = req_data['vocab_list']
        vocab_file_name = req_data['vocab_file_name']
        images = req_data['images']
        settings = req_data['settings']
        deck_name = req_data['deck_name']
        note_name = req_data['note_name']
        user_goal = req_data['user_goal']
        session_id = req_data['session_id']
        
        # 驗證必要參數
        if not vocab_list or (isinstance(vocab_list, str) and not vocab_list.strip()):
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Vocab list is required',
                    'details': 'Please provide a vocabulary list file or text content'
                }
            )
        
        # 準備會話目錄
        dirs = prepare_session_directories(session_id)
        session_dir = dirs['session_dir']
        source_dir = dirs['source']
        orig_dir = dirs['orig']
        
        # 處理單字列表
        vocab_path = process_vocab_list(vocab_list, source_dir, vocab_file_name)
        if not vocab_path:
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Invalid vocab list',
                    'details': 'Could not process vocabulary list'
                }
            )
        
        # 處理圖片路徑
        selected_images = process_image_paths(images, session_dir)
        
        # 確定卡片類型和語言設置
        card_type = determine_card_type(note_name)
        source_lang, target_lang = get_language_settings(settings)
        
        # 獲取 API Key
        api_key = validate_and_get_api_key(settings)
        if not api_key:
            error_msg = "OpenAI API Key is required. Please set it in Settings."
            logger.error(error_msg)
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'API Key required',
                    'details': error_msg
                }
            )
        
        # 獲取模型設置（從前端設置或使用預設值）
        model = settings.get('model') or AI_MODEL
        
        logger.info(f"Starting article generation: deck={deck_name}, card_type={card_type}, vocab_path={vocab_path}, images={len(selected_images) if selected_images else 0}, model={model}, orig_dir={orig_dir}")
        
        # 調用處理邏輯
        pdf_path = ''  # Article 模式可能不需要 PDF，如果圖片已提取
        result = processor.run_article_mode(
            pdf_path=pdf_path,
            text_path=vocab_path,
            deck_name=deck_name,
            target=user_goal,
            source_lang=source_lang,
            target_lang=target_lang,
            selected_images=selected_images,
            card_type=card_type,
            session_dir=str(orig_dir),
            api_key=api_key,
            model=model
        )
        
        # 讀取生成的卡片
        cards = load_generated_cards(orig_dir)
        
        return {
            'success': True,
            'cards': cards,
            'message': result,
            'sessionId': session_dir.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = format_error_response(e, 'Article generation')
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)


@router.post("/generate/vocab")
async def generate_vocab(data: Dict[str, Any]):
    """從單字列表生成卡片"""
    try:
        logger.info(f"Vocab generation request: {list(data.keys())}")
        
        # 解析請求數據
        req_data = parse_request_data(data)
        vocab_list = req_data['vocab_list']
        vocab_file_name = req_data['vocab_file_name']
        settings = req_data['settings']
        deck_name = req_data['deck_name']
        note_name = req_data['note_name']
        user_goal = req_data['user_goal']
        session_id = req_data['session_id']
        
        # 驗證必要參數
        if not vocab_list or (isinstance(vocab_list, str) and not vocab_list.strip()):
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Vocab list is required',
                    'details': 'Please provide a vocabulary list file or text content'
                }
            )
        
        # 準備會話目錄
        dirs = prepare_session_directories(session_id)
        session_dir = dirs['session_dir']
        source_dir = dirs['source']
        orig_dir = dirs['orig']
        
        # 處理單字列表
        vocab_path = process_vocab_list(vocab_list, source_dir, vocab_file_name)
        if not vocab_path:
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Invalid vocab list',
                    'details': 'Could not process vocabulary list'
                }
            )
        
        # 確定卡片類型和語言設置
        card_type = determine_card_type(note_name)
        source_lang, target_lang = get_language_settings(settings)
        
        # 獲取 API Key
        api_key = validate_and_get_api_key(settings)
        if not api_key:
            error_msg = "OpenAI API Key is required. Please set it in Settings."
            logger.error(error_msg)
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'API Key required',
                    'details': error_msg
                }
            )
        
        # 獲取模型設置（從前端設置或使用預設值）
        model = settings.get('model') or AI_MODEL
        
        logger.info(f"Starting vocab generation: deck={deck_name}, card_type={card_type}, vocab_path={vocab_path}, model={model}, orig_dir={orig_dir}")
        
        # 調用處理邏輯
        result = processor.run_vocab_mode(
            text_path=vocab_path,
            target=user_goal,
            deck_name=deck_name,
            source_lang=source_lang,
            target_lang=target_lang,
            card_type=card_type,
            session_dir=str(orig_dir),
            api_key=api_key,
            model=model
        )
        
        # 讀取生成的卡片
        cards = load_generated_cards(orig_dir)
        
        return {
            'success': True,
            'cards': cards,
            'message': result,
            'sessionId': session_dir.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = format_error_response(e, 'Vocab generation')
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)


@router.post("/generate/ai")
async def generate_ai(data: Dict[str, Any]):
    """AI 生成卡片"""
    try:
        logger.info(f"AI generation request: {list(data.keys())}")
        
        # 解析請求數據
        req_data = parse_request_data(data)
        topic = req_data['topic']
        settings = req_data['settings']
        deck_name = req_data['deck_name']
        note_name = req_data['note_name']
        user_goal = req_data['user_goal'] or topic
        count = req_data['count']
        session_id = req_data['session_id']
        
        if not topic:
            raise HTTPException(status_code=400, detail='Topic is required')
        
        # 準備會話目錄
        dirs = prepare_session_directories(session_id)
        session_dir = dirs['session_dir']
        orig_dir = dirs['orig']
        
        # 確定卡片類型和語言設置
        card_type = determine_card_type(note_name)
        source_lang, target_lang = get_language_settings(settings)
        
        # 獲取 API Key
        api_key = validate_and_get_api_key(settings)
        if not api_key:
            error_msg = "OpenAI API Key is required. Please set it in Settings."
            logger.error(error_msg)
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'API Key required',
                    'details': error_msg
                }
            )
        
        # 獲取模型設置（從前端設置或使用預設值）
        model = settings.get('model') or AI_MODEL
        
        logger.info(f"Starting AI generation: deck={deck_name}, card_type={card_type}, topic={topic}, model={model}, orig_dir={orig_dir}")
        
        # 調用處理邏輯
        result = processor.run_ai_generate_mode(
            target=user_goal or topic,
            count=count,
            deck_name=deck_name,
            source_lang=source_lang,
            target_lang=target_lang,
            card_type=card_type,
            session_dir=str(orig_dir),
            api_key=api_key,
            model=model
        )
        
        # 讀取生成的卡片
        cards = load_generated_cards(orig_dir)
        
        return {
            'success': True,
            'cards': cards,
            'message': result,
            'sessionId': session_dir.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = format_error_response(e, 'AI generation')
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)


@router.post("/generate/grammar")
async def generate_grammar(data: Dict[str, Any]):
    """從文法生成卡片（暫時返回空）"""
    try:
        logger.info(f"Grammar generation request: {list(data.keys())}")
        
        # TODO: 實現文法處理邏輯
        return {
            'success': True,
            'cards': [],
            'message': 'Grammar mode not yet implemented'
        }
        
    except Exception as e:
        logger.error(f"Grammar generation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={'error': 'Generation failed', 'details': str(e)})

