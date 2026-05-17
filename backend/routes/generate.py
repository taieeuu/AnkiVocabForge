"""
生成 API 路由

遵循 FastAPI 最佳實踐：
- 使用 Pydantic models 定義請求和響應
- 使用依賴注入處理驗證邏輯
- 清晰的錯誤處理和文檔
"""
import traceback
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
import logging

from libs.config import AI_MODEL
from service.main_processor import MainProcessor
from .models import (
    ArticleGenerationRequest,
    VocabGenerationRequest,
    AIGenerationRequest,
    GrammarGenerationRequest,
    GenerationResponse,
    ErrorResponse
)
from .dependencies import get_validated_settings, ValidatedSettings, validate_settings_from_request
from .generate_helpers import (
    prepare_session_directories,
    process_vocab_list,
    process_image_paths,
    determine_card_type,
    load_generated_cards,
    format_error_response
)

router = APIRouter(
    tags=["生成"],
    responses={
        400: {"model": ErrorResponse, "description": "請求參數錯誤"},
        500: {"model": ErrorResponse, "description": "服務器內部錯誤"}
    }
)
logger = logging.getLogger(__name__)

processor = MainProcessor()


@router.post(
    "/generate/article",
    response_model=GenerationResponse,
    summary="從文章生成卡片",
    description="從上傳的文章（PDF/圖片）和單字列表生成 Anki 卡片"
)
async def generate_article(
    request: ArticleGenerationRequest
):
    """
    從文章生成卡片
    
    - **deckName**: 目標牌組名稱
    - **noteName**: Anki 筆記類型名稱
    - **images**: 選中的圖片列表（從 PDF 或圖片文件提取）
    - **vocabList**: 單字列表（可以是對象格式 {content, filename} 或字符串）
    - **settings**: 生成設置（API Key、模型、語言等）
    - **userGoal**: 可選的使用者目標/指示
    - **tags**: 可選的標籤（空格分隔）
    - **sessionId**: 可選的 Session ID（用於多檔案處理）
    """
    try:
        logger.info(f"Article generation request: request:{request}")
        
        # 驗證設置
        validated_settings = validate_settings_from_request(request)
        
        # 處理單字列表
        vocab_list_data = request.vocabList
        if not vocab_list_data:
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Vocab list is required',
                    'details': 'Please provide a vocabulary list file or text content'
                }
            )
        
        # 解析單字列表（支持對象或字符串格式）
        if isinstance(vocab_list_data, dict):
            vocab_list = vocab_list_data.get('content', '')
            vocab_file_name = vocab_list_data.get('filename', '')
        else:
            vocab_list = str(vocab_list_data)
            vocab_file_name = None
        
        if not vocab_list or not vocab_list.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Vocab list is required',
                    'details': 'Please provide a vocabulary list file or text content'
                }
            )
        
        # 準備會話目錄
        dirs = prepare_session_directories(request.sessionId)
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
        images_dict = [img.dict() for img in request.images]
        selected_images = process_image_paths(images_dict, session_dir)
        
        # 確定卡片類型
        card_type = determine_card_type(request.noteName)
        
        logger.info(
            f"Starting article generation: deck={request.deckName}, "
            f"card_type={card_type}, vocab_path={vocab_path}, "
            f"images={len(selected_images) if selected_images else 0}, "
            f"model={validated_settings.model}, orig_dir={orig_dir}"
        )
        
        # 調用處理邏輯
        pdf_path = ''  # Article 模式可能不需要 PDF，如果圖片已提取
        result = processor.run_article_mode(
            pdf_path=pdf_path,
            text_path=vocab_path,
            deck_name=request.deckName,
            target=request.userGoal or '',
            source_lang=validated_settings.learning_lang,
            target_lang=validated_settings.native_lang,
            selected_images=selected_images,
            card_type=card_type,
            session_dir=str(orig_dir),
            api_key=validated_settings.api_key,
            model=validated_settings.model
        )
        
        # 讀取生成的卡片
        cards = load_generated_cards(orig_dir)
        
        return GenerationResponse(
            success=True,
            cards=cards,
            message=result,
            sessionId=session_dir.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = format_error_response(e, 'Article generation')
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)


@router.post(
    "/generate/vocab",
    response_model=GenerationResponse,
    summary="從單字列表生成卡片",
    description="從單字列表文件生成 Anki 卡片"
)
async def generate_vocab(
    request: VocabGenerationRequest
):
    """
    從單字列表生成卡片
    
    - **deckName**: 目標牌組名稱
    - **noteName**: Anki 筆記類型名稱
    - **vocabList**: 單字列表（可以是對象格式 {content, filename} 或字符串）
    - **settings**: 生成設置（API Key、模型、語言等）
    - **userGoal**: 可選的使用者目標/指示
    - **tags**: 可選的標籤（空格分隔）
    - **sessionId**: 可選的 Session ID
    """
    try:
        logger.info(f"Vocab generation request: deck={request.deckName}, note={request.noteName}")
        
        # 驗證設置
        validated_settings = validate_settings_from_request(request)
        
        # 處理單字列表
        vocab_list_data = request.vocabList
        if not vocab_list_data:
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Vocab list is required',
                    'details': 'Please provide a vocabulary list file or text content'
                }
            )
        
        # 解析單字列表（支持對象或字符串格式）
        if isinstance(vocab_list_data, dict):
            vocab_list = vocab_list_data.get('content', '')
            vocab_file_name = vocab_list_data.get('filename', '')
        else:
            vocab_list = str(vocab_list_data)
            vocab_file_name = None
        
        if not vocab_list or not vocab_list.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Vocab list is required',
                    'details': 'Please provide a vocabulary list file or text content'
                }
            )
        
        # 準備會話目錄
        dirs = prepare_session_directories(request.sessionId)
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
        
        # 確定卡片類型
        card_type = determine_card_type(request.noteName)
        
        logger.info(
            f"Starting vocab generation: deck={request.deckName}, "
            f"card_type={card_type}, vocab_path={vocab_path}, "
            f"model={validated_settings.model}, orig_dir={orig_dir}"
        )
        
        # 調用處理邏輯
        result = processor.run_vocab_mode(
            text_path=vocab_path,
            target=request.userGoal or '',
            deck_name=request.deckName,
            source_lang=validated_settings.learning_lang,
            target_lang=validated_settings.native_lang,
            card_type=card_type,
            session_dir=str(orig_dir),
            api_key=validated_settings.api_key,
            model=validated_settings.model
        )
        
        # 讀取生成的卡片
        cards = load_generated_cards(orig_dir)
        
        return GenerationResponse(
            success=True,
            cards=cards,
            message=result,
            sessionId=session_dir.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = format_error_response(e, 'Vocab generation')
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)


@router.post(
    "/generate/ai",
    response_model=GenerationResponse,
    summary="AI 生成卡片",
    description="使用 AI 根據主題生成單字或文法卡片（支持選擇 Word 或 Grammar）"
)
async def generate_ai(
    request: AIGenerationRequest
):
    """
    AI 生成卡片
    
    - **topic**: 生成主題（必填）
    - **count**: 生成數量（1-100，默認 10）
    - **contentType**: 內容類型，'Word' 或 'Grammar'（默認 'Word'）
    - **deckName**: 目標牌組名稱
    - **noteName**: Anki 筆記類型名稱（僅用於 Word 類型）
    - **settings**: 生成設置（API Key、模型、語言等）
    - **userGoal**: 可選的使用者目標/指示（如果未提供則使用 topic）
    - **tags**: 可選的標籤（空格分隔）
    - **sessionId**: 可選的 Session ID
    """
    try:
        logger.info(f"AI generation request: topic={request.topic}, type={request.contentType}, count={request.count}")
        
        # 驗證設置
        validated_settings = validate_settings_from_request(request)
        
        if not request.topic or not request.topic.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Topic is required',
                    'details': 'Please provide a topic for AI generation'
                }
            )
        
        # 準備會話目錄
        dirs = prepare_session_directories(request.sessionId)
        session_dir = dirs['session_dir']
        orig_dir = dirs['orig']
        
        user_goal = request.userGoal or request.topic
        content_type = request.contentType or 'Word'
        
        # 根據 content_type 選擇生成類型
        if content_type.lower() == 'grammar':
            # 生成文法
            logger.info(
                f"Starting AI grammar generation: deck={request.deckName}, "
                f"goal={user_goal}, count={request.count}, "
                f"model={validated_settings.model}, orig_dir={orig_dir}"
            )
            
            result = processor.run_grammar_mode(
                target=user_goal,
                count=request.count,
                deck_name=request.deckName,
                source_lang=validated_settings.learning_lang,
                target_lang=validated_settings.native_lang,
                session_dir=str(orig_dir),
                api_key=validated_settings.api_key,
                model=validated_settings.model
            )
        else:
            # 生成單字（默認）
            card_type = determine_card_type(request.noteName)
            logger.info(
                f"Starting AI vocab generation: deck={request.deckName}, "
                f"card_type={card_type}, topic={request.topic}, "
                f"model={validated_settings.model}, orig_dir={orig_dir}"
            )
            
            result = processor.run_ai_generate_mode(
                target=user_goal,
                count=request.count,
                deck_name=request.deckName,
                source_lang=validated_settings.learning_lang,
                target_lang=validated_settings.native_lang,
                card_type=card_type,
                session_dir=str(orig_dir),
                api_key=validated_settings.api_key,
                model=validated_settings.model
            )
        
        # 讀取生成的卡片
        cards = load_generated_cards(orig_dir)
        
        return GenerationResponse(
            success=True,
            cards=cards,
            message=result,
            sessionId=session_dir.name
        )
    except Exception as e:
        error_detail = format_error_response(e, 'AI generation')
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)


@router.post(
    "/generate/grammar",
    response_model=GenerationResponse,
    summary="從文法文件生成卡片",
    description="從文法列表文件生成 Anki 卡片（僅支持文件輸入）"
)
async def generate_grammar(
    request: GrammarGenerationRequest
):
    """
    從文法文件生成卡片
    
    - **grammarFile**: 文法文件內容（字符串格式，必填）
    - **deckName**: 目標牌組名稱
    - **settings**: 生成設置（API Key、模型、語言等）
    - **userGoal**: 可選的使用者目標/指示
    - **tags**: 可選的標籤（空格分隔）
    - **sessionId**: 可選的 Session ID
    """
    try:
        logger.info(f"Grammar generation request: deck={request.deckName}")
        
        # 驗證設置
        validated_settings = validate_settings_from_request(request)
        
        # 處理文法文件
        if not request.grammarFile or not request.grammarFile.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Grammar file is required',
                    'details': 'Please provide a grammar file content'
                }
            )
        
        grammar_list = request.grammarFile
        grammar_file_name = None
        
        if not grammar_list or not grammar_list.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Grammar list is required',
                    'details': 'Please provide a grammar list file or text content'
                }
            )
        
        # 準備會話目錄
        dirs = prepare_session_directories(request.sessionId)
        session_dir = dirs['session_dir']
        source_dir = dirs['source']
        orig_dir = dirs['orig']
        
        # 處理文法列表文件
        grammar_path = process_vocab_list(grammar_list, source_dir, grammar_file_name)
        if not grammar_path:
            raise HTTPException(
                status_code=400,
                detail={
                    'success': False,
                    'error': 'Invalid grammar list',
                    'details': 'Could not process grammar list'
                }
            )
        
        logger.info(
            f"Starting grammar generation from file: deck={request.deckName}, "
            f"grammar_path={grammar_path}, model={validated_settings.model}, "
            f"orig_dir={orig_dir}"
        )
        
        # 調用處理邏輯
        result = processor.run_grammar_from_file_mode(
            text_path=grammar_path,
            target=request.userGoal or '',
            deck_name=request.deckName,
            source_lang=validated_settings.learning_lang,
            target_lang=validated_settings.native_lang,
            session_dir=str(orig_dir),
            api_key=validated_settings.api_key,
            model=validated_settings.model
        )
        
        # 讀取生成的卡片
        cards = load_generated_cards(orig_dir)
        
        return GenerationResponse(
            success=True,
            cards=cards,
            message=result,
            sessionId=session_dir.name
        )
        
    except Exception as e:
        error_detail = format_error_response(e, 'Grammar generation')
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)

