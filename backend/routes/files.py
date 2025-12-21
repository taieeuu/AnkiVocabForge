"""
文件管理 API 路由
"""
import json
import zipfile
import tempfile
import threading
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
import logging

from libs.config import OUTPUTS_DIR
from service.anki_service import AnkiService
from helpers.session import get_or_create_session_dir, setup_session_directories
from .generate_helpers import determine_card_type

router = APIRouter()
logger = logging.getLogger(__name__)


def get_display_name_for_apkg(file_path: Path, relative_path: Path) -> str:
    """
    為 .apkg 檔案生成顯示名稱
    
    Args:
        file_path: 檔案完整路徑
        relative_path: 相對於 session 目錄的路徑
        
    Returns:
        str: 顯示名稱
    """
    file_name = file_path.name
    display_name = file_name
    
    if file_path.suffix == '.apkg':
        parts = relative_path.parts
        if len(parts) > 1:
            parent_dir = parts[0]
            if parent_dir == 'orig':
                if '_orig' not in file_name:
                    base_name = file_name.replace('.apkg', '')
                    display_name = f"{base_name}_orig.apkg"
            elif parent_dir == 'edited':
                if '_edited' not in file_name:
                    base_name = file_name.replace('.apkg', '').replace('-edited', '')
                    display_name = f"{base_name}_edited.apkg"
    
    return display_name


@router.get("/files/download/{session_id}")
async def download_file(session_id: str):
    """打包整個 session 目錄為 .zip 檔案"""
    try:
        session_dir = Path(OUTPUTS_DIR) / session_id
        if not session_dir.exists():
            raise HTTPException(status_code=404, detail='Session not found')
        
        # 創建臨時 zip 檔案
        zip_filename = f"{session_id}.zip"
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_zip_path = temp_zip.name
        temp_zip.close()
        
        # 打包整個 session 目錄
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in session_dir.rglob('*'):
                if file_path.is_file():
                    # 計算相對路徑（相對於 session_dir）
                    arcname = file_path.relative_to(session_dir)
                    zipf.write(file_path, arcname)
        
        logger.info(f"Created zip file for session {session_id}: {temp_zip_path}")
        
        # 使用 StreamingResponse 來處理檔案下載和清理
        def generate():
            try:
                with open(temp_zip_path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        yield chunk
            finally:
                # 清理臨時檔案
                try:
                    if Path(temp_zip_path).exists():
                        Path(temp_zip_path).unlink()
                        logger.info(f"Cleaned up temp file: {temp_zip_path}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp file {temp_zip_path}: {e}")
        
        return StreamingResponse(
            generate(),
            media_type='application/zip',
            headers={'Content-Disposition': f'attachment; filename="{zip_filename}"'}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # 確保清理臨時檔案
        try:
            if 'temp_zip_path' in locals() and Path(temp_zip_path).exists():
                Path(temp_zip_path).unlink()
        except:
            pass
        logger.error(f"Download error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={'error': 'Download failed', 'details': str(e)})


@router.get("/files/list/{session_id}")
async def list_session_files(session_id: str):
    """列出 session 目錄中的所有文件"""
    try:
        session_dir = Path(OUTPUTS_DIR) / session_id
        if not session_dir.exists():
            raise HTTPException(status_code=404, detail='Session not found')
        
        files = []
        # 列出所有文件
        for file_path in session_dir.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(session_dir)
                file_name = file_path.name
                display_name = get_display_name_for_apkg(file_path, relative_path)
                
                files.append({
                    'name': display_name,
                    'originalName': file_name,
                    'path': str(relative_path),
                    'size': file_path.stat().st_size,
                    'type': file_path.suffix,
                    'isApkg': file_path.suffix == '.apkg'
                })
        
        return {
            'success': True,
            'files': files,
            'sessionId': session_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List files error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={'error': 'Failed to list files', 'details': str(e)})


@router.get("/files/download/{session_id}/{file_path:path}")
async def download_specific_file(session_id: str, file_path: str):
    """下載 session 目錄中的特定文件"""
    try:
        session_dir = Path(OUTPUTS_DIR) / session_id
        if not session_dir.exists():
            raise HTTPException(status_code=404, detail='Session not found')
        
        # 防止路徑遍歷攻擊
        target_file = (session_dir / file_path).resolve()
        if not str(target_file).startswith(str(session_dir.resolve())):
            raise HTTPException(status_code=400, detail='Invalid file path')
        
        if not target_file.exists() or not target_file.is_file():
            raise HTTPException(status_code=404, detail='File not found')
        
        # 確定下載時的檔案名稱（使用顯示名稱）
        relative_path = Path(file_path)
        download_filename = get_display_name_for_apkg(target_file, relative_path)
        
        logger.info(f"Sending file for download: {target_file} as {download_filename}")
        return FileResponse(
            str(target_file),
            filename=download_filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={'error': 'Download failed', 'details': str(e)})


@router.delete("/files/cleanup/{session_id}")
async def cleanup_session(session_id: str):
    """刪除 session 目錄（延遲刪除）"""
    try:
        session_dir = Path(OUTPUTS_DIR) / session_id
        if not session_dir.exists():
            raise HTTPException(status_code=404, detail='Session not found')
        
        # 使用線程延遲刪除
        def delayed_delete():
            time.sleep(5)  # 等待 5 秒後刪除
            try:
                if session_dir.exists():
                    shutil.rmtree(session_dir)
                    logger.info(f"Cleaned up session directory: {session_dir}")
            except Exception as e:
                logger.error(f"Failed to cleanup session {session_id}: {e}")
        
        thread = threading.Thread(target=delayed_delete, daemon=True)
        thread.start()
        
        return {
            'success': True,
            'message': f'Session {session_id} will be deleted in 5 seconds'
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={'error': 'Cleanup failed', 'details': str(e)})


@router.post("/generate/package")
async def package_cards(data: Dict[str, Any]):
    """打包卡片為 .apkg 文件"""
    try:
        logger.info(f"Package request: {list(data.keys())}")
        
        cards = data.get('cards', [])
        deck_name = data.get('deckName', 'TestDeck')
        note_name = data.get('noteName', 'Basic')
        tags = data.get('tags', '')
        session_id = data.get('sessionId')
        
        if not cards:
            raise HTTPException(status_code=400, detail='No cards provided')
        
        # 使用提供的 sessionId 或創建新的 session 目錄
        session_dir = get_or_create_session_dir(session_id)
        dirs = setup_session_directories(session_dir)
        edited_dir = dirs['edited']
        orig_dir = dirs['orig']
        orig_voice_dir = orig_dir / "voice"
        
        # 確定卡片類型
        card_type = determine_card_type(note_name)
        
        # 轉換卡片格式
        vocab_list = []
        for card in cards:
            vocab_list.append({
                'word': card.get('word', card.get('front', '')),
                'pos': card.get('pos', ''),
                'meaning': card.get('meaning', card.get('back', '')),
                'synonyms': card.get('synonyms', ''),
                'ex1_ori': card.get('ex1_ori', card.get('sentence', '')),
                'ex1_trans': card.get('ex1_trans', ''),
                'ex2_ori': card.get('ex2_ori', ''),
                'ex2_trans': card.get('ex2_trans', ''),
                'hint': card.get('hint', '')
            })
        
        # 儲存修改後的 JSON 到 edited 目錄
        from helpers.file_utils import slugify
        safe_deck_name = slugify(deck_name)
        json_filename = f"{safe_deck_name}-edited-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_path = edited_dir / json_filename
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(vocab_list, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved edited JSON to: {json_path}")
        
        # 確定 voice 目錄：優先使用 orig/voice，如果不存在則使用 edited/voice（向後兼容）
        voice_dir_to_use = None
        if orig_voice_dir.exists():
            voice_dir_to_use = str(orig_voice_dir)
        else:
            edited_voice_dir = edited_dir / "voice"
            if edited_voice_dir.exists():
                voice_dir_to_use = str(edited_voice_dir)
        
        # 調用打包邏輯
        if card_type == 'Basic':
            result = AnkiService.import_basic_model_notes(
                vocab_list, deck_name, 
                session_dir=str(edited_dir), 
                voice_dir=voice_dir_to_use, 
                filename_suffix='edited'
            )
        elif card_type == 'Cloze':
            result = AnkiService.import_cloze_model_notes(
                vocab_list, deck_name, 
                session_dir=str(edited_dir), 
                voice_dir=voice_dir_to_use, 
                filename_suffix='edited'
            )
        else:
            result = AnkiService.import_basic_and_cloze_notes(
                vocab_list, deck_name, 
                session_dir=str(edited_dir), 
                voice_dir=voice_dir_to_use, 
                filename_suffix='edited'
            )
        
        # 在 edited_dir 中查找生成的 .apkg 文件
        from helpers.file_utils import slugify
        safe_deck_name = slugify(deck_name)
        apkg_files = sorted(edited_dir.glob('*.apkg'), key=lambda p: p.stat().st_mtime, reverse=True)
        if apkg_files:
            file_path = str(apkg_files[0])
        else:
            file_path = str(edited_dir / f"{safe_deck_name}_edited.apkg")
        
        return {
            'success': True,
            'filePath': file_path,
            'message': result,
            'sessionId': session_dir.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Package error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail={'error': 'Packaging failed', 'details': str(e)})

