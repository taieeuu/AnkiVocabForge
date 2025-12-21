"""
分析 API 路由
"""
import json
import traceback
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import logging

from libs.config import OUTPUTS_DIR, PASSAGE_IMAGE_DIR
from libs.parser import Parser
from helpers.session import get_or_create_session_dir, setup_session_directories
from helpers.file_utils import secure_filename, get_image_path
from helpers.api_key import validate_and_get_api_key, format_api_key_error

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze/images")
async def analyze_images(
    file: UploadFile = File(...),
    settings: Optional[str] = Form(None),
    sessionId: Optional[str] = Form(None)
):
    """分析 PDF 或圖片文件，提取圖片列表"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail='No file selected')
        
        # 解析 settings
        settings_dict = {}
        if settings:
            try:
                settings_dict = json.loads(settings)
            except:
                pass
        
        # 驗證 API Key
        api_key = validate_and_get_api_key(settings_dict)
        if not api_key:
            error_msg = "OpenAI API Key is required for image analysis. Please set it in Settings."
            logger.error(error_msg)
            raise HTTPException(
                status_code=400,
                detail={
                    'error': 'API Key required',
                    'details': error_msg
                }
            )
        
        # 使用提供的 sessionId 或創建新的 session 目錄
        session_dir = get_or_create_session_dir(sessionId)
        dirs = setup_session_directories(session_dir)
        source_dir = dirs['source']
        
        filename = secure_filename(file.filename)
        filepath = source_dir / filename
        
        # 保存文件
        with open(filepath, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        images = []
        
        # 如果是 PDF，解析提取圖片（圖片會儲存在 source 目錄中）
        if filename.lower().endswith('.pdf'):
            parser = Parser(session_dir=str(source_dir), api_key=api_key)
            parser.parse_pdf(str(filepath))
            
            # 獲取提取的圖片（從 source 目錄中查找）
            image_dir = Path(parser.passage_image_path)
            image_files = sorted(
                list(image_dir.glob('*.jpg')) + 
                list(image_dir.glob('*.png')) + 
                list(image_dir.glob('*.jpeg')),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # 只獲取最近解析的圖片（匹配當前PDF文件名）
            pdf_stem = Path(filename).stem
            pdf_images = [img for img in image_files if img.stem.startswith(pdf_stem)]
            
            # 如果沒有找到匹配的圖片，使用所有圖片（可能是第一次解析）
            if not pdf_images:
                pdf_images = image_files[:10]  # 限制最多10張，避免太多
            
            for idx, img_path in enumerate(pdf_images, start=1):
                # 轉換為可訪問的 URL 路徑
                images.append({
                    'id': len(images) + idx,
                    'src': f'/api/files/image/{session_dir.name}/{img_path.name}',
                    'path': str(img_path),
                    'selected': True
                })
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # 單個圖片文件
            images.append({
                'id': 1,
                'src': f'/api/files/image/{session_dir.name}/{filename}',
                'path': str(filepath),
                'selected': True
            })
        
        return {
            'success': True,
            'images': images,
            'sessionId': session_dir.name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        full_traceback = traceback.format_exc()
        detailed_error = format_api_key_error(error_msg)
        
        logger.error(f"Image analysis error: {detailed_error}\n{full_traceback}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={'error': 'Analysis failed', 'details': detailed_error}
        )


@router.get("/files/image/{session_id}/{filename}")
async def get_image(session_id: str, filename: str):
    """獲取圖片文件"""
    try:
        image_path = get_image_path(session_id, filename)
        
        if image_path and image_path.exists():
            return FileResponse(
                str(image_path),
                media_type='image/jpeg' if filename.lower().endswith('.jpg') else 'image/png'
            )
        else:
            raise HTTPException(status_code=404, detail='Image not found')
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image retrieval error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail='Failed to retrieve image')

