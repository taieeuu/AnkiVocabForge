"""
Generate 路由的共用輔助函數
"""
import json
import tempfile
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from libs.config import OUTPUTS_DIR, PASSAGE_IMAGE_DIR, SOURCE_LANG, TARGET_LANG, AI_MODEL
from helpers.session import get_or_create_session_dir, setup_session_directories
from helpers.api_key import format_api_key_error
from helpers.file_utils import secure_filename

logger = logging.getLogger(__name__)


def parse_request_data(data: Dict[str, Any]) -> dict:
    """解析生成請求的數據"""
    vocab_list_data = data.get('vocabList', '')
    # 處理新的格式：vocabList 可能是對象 {content, filename} 或舊格式的字符串
    if isinstance(vocab_list_data, dict):
        vocab_list = vocab_list_data.get('content', '')
        vocab_file_name = vocab_list_data.get('filename', '')
    else:
        # 向後兼容：舊格式直接是字符串
        vocab_list = vocab_list_data
        vocab_file_name = data.get('vocabFileName', '')
    
    return {
        'images': data.get('images', []),
        'vocab_list': vocab_list,
        'vocab_file_name': vocab_file_name,
        'settings': data.get('settings', {}),
        'deck_name': data.get('deckName', 'TestDeck'),
        'note_name': data.get('noteName', 'Basic'),
        'user_goal': data.get('userGoal', ''),
        'tags': data.get('tags', ''),
        'session_id': data.get('sessionId'),
        'topic': data.get('topic', ''),
        'count': data.get('count', 10)
    }


def prepare_session_directories(session_id: Optional[str] = None) -> dict:
    """準備會話目錄結構"""
    session_dir = get_or_create_session_dir(session_id)
    dirs = setup_session_directories(session_dir)
    return {
        'session_dir': session_dir,
        **dirs
    }


def process_vocab_list(vocab_list: str, source_dir: Path, vocab_file_name: Optional[str] = None) -> Optional[str]:
    """
    處理單字列表，返回文件路徑
    
    當前端傳遞文本內容時（按下 start generate 時），會將文本內容保存到 source 目錄。
    因為此時文件還沒有儲存在 server 上，而是在 generate API 被調用時才會在
    outputs/{nano_id}/source/ 目錄中創建文件。
    
    Args:
        vocab_list: 單字列表文本或文件路徑
        source_dir: source 目錄路徑 (outputs/{nano_id}/source/)
        vocab_file_name: 原始文件名（如果有的話）
        
    Returns:
        str: 處理後的單字列表文件路徑
    """
    if not vocab_list or (isinstance(vocab_list, str) and not vocab_list.strip()):
        return None
    
    if isinstance(vocab_list, str) and vocab_list.strip():
        # 如果有 vocab_file_name，說明這是從前端傳來的文本內容，直接保存
        if vocab_file_name:
            vocab_filename = secure_filename(vocab_file_name)
            # 確保文件名有 .txt 擴展名
            if not vocab_filename.endswith('.txt'):
                vocab_filename = f"{vocab_filename}.txt"
            vocab_path = source_dir / vocab_filename
            vocab_path.write_text(vocab_list, encoding='utf-8')
            logger.info(f"Saved vocab list text to source directory: {vocab_path}")
            return str(vocab_path)
        
        # 沒有 vocab_file_name 時，檢查是否為已存在的文件路徑
        # 先檢查是否可能是文件路徑（不包含換行符且長度合理）
        if '\n' not in vocab_list and len(vocab_list) < 500:
            vocab_path_obj = Path(vocab_list)
            if vocab_path_obj.exists() and vocab_path_obj.is_file():
                # 是已存在的文件路徑，直接返回
                return vocab_list
        
        # 否則視為文本內容，使用臨時文件名
        vocab_filename = f"vocab_{Path(tempfile.mktemp()).stem}.txt"
        vocab_path = source_dir / vocab_filename
        vocab_path.write_text(vocab_list, encoding='utf-8')
        logger.info(f"Saved vocab list text to source directory: {vocab_path}")
        return str(vocab_path)
    
    return None


def process_image_paths(images: List[Dict], session_dir: Path) -> Optional[List[str]]:
    """
    處理圖片路徑列表
    
    Args:
        images: 圖片信息列表
        session_dir: 會話目錄
        
    Returns:
        List[str]: 處理後的圖片路徑列表
    """
    if not images:
        return None
    
    selected_images = []
    for img in images:
        if img.get('selected', True):
            # 優先使用 path
            img_path = img.get('path')
            if not img_path:
                # 從 src 提取文件名和 session_id
                src = img.get('src', '')
                if src:
                    # src 格式: /api/files/image/{session_id}/{filename}
                    parts = src.split('/')
                    if len(parts) >= 5 and parts[-2]:  # 有 session_id
                        img_session_id = parts[-2]
                        filename = parts[-1]
                        img_session_dir = Path(OUTPUTS_DIR) / img_session_id
                        img_path = img_session_dir / "source" / filename
                        if not img_path.exists():
                            img_path = img_session_dir / filename
                        img_path = str(img_path) if img_path.exists() else None
                    else:
                        # 向後兼容：嘗試在 passage_images 目錄查找
                        filename = Path(src).name
                        img_path = Path(PASSAGE_IMAGE_DIR) / filename
                        img_path = str(img_path) if img_path.exists() else None
            
            if img_path and Path(img_path).exists():
                selected_images.append(str(img_path))
    
    return selected_images if selected_images else None


def determine_card_type(note_name: str) -> str:
    """根據 note_name 確定卡片類型"""
    if not note_name:
        return 'Basic'
    
    note_lower = note_name.lower()
    if 'cloze' in note_lower and 'basic' in note_lower:
        return 'Basic+Cloze'
    elif 'cloze' in note_lower:
        return 'Cloze'
    else:
        return 'Basic'


def get_language_settings(settings: Dict[str, Any]) -> tuple:
    """獲取語言設置"""
    source_lang = settings.get('sourceLang', SOURCE_LANG)
    target_lang = settings.get('language', TARGET_LANG)
    return source_lang, target_lang


def load_generated_cards(orig_dir: Path) -> List[Dict]:
    """
    從 orig_dir 中讀取生成的卡片 JSON 文件
    
    Args:
        orig_dir: orig 目錄路徑
        
    Returns:
        List[Dict]: 卡片列表
    """
    json_files = sorted(orig_dir.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    if not json_files:
        return []
    
    with open(json_files[0], 'r', encoding='utf-8') as f:
        cards_data = json.load(f)
        # 確保 cards_data 是列表
        if isinstance(cards_data, dict) and 'notes' in cards_data:
            cards_data = cards_data['notes']
        elif not isinstance(cards_data, list):
            cards_data = []
        
        # 轉換為前端需要的格式
        cards = []
        for item in cards_data:
            cards.append({
                'id': len(cards) + 1,
                'front': item.get('word', ''),
                'back': item.get('meaning', ''),
                'sentence': item.get('ex1_ori', ''),
                'word': item.get('word', ''),
                'pos': item.get('pos', ''),
                'meaning': item.get('meaning', ''),
                'synonyms': item.get('synonyms', ''),
                'ex1_ori': item.get('ex1_ori', ''),
                'ex1_trans': item.get('ex1_trans', ''),
                'ex2_ori': item.get('ex2_ori', ''),
                'ex2_trans': item.get('ex2_trans', ''),
                'hint': item.get('hint', '')
            })
        
        return cards


def format_error_response(e: Exception, operation: str) -> Dict[str, Any]:
    """格式化錯誤響應"""
    error_msg = str(e)
    full_traceback = traceback.format_exc()
    detailed_error = format_api_key_error(error_msg)
    
    logger.error(f"{operation} error: {detailed_error}\n{full_traceback}", exc_info=True)
    
    return {
        'success': False,
        'error': f'{operation} failed',
        'details': detailed_error
    }

