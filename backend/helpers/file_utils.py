"""
文件處理相關工具函數
"""
import os
import re
from pathlib import Path


def slugify(s: str) -> str:
    """
    將字符串轉換為安全的文件名格式
    
    Args:
        s: 原始字符串
        
    Returns:
        str: slugified 字符串（小寫，特殊字符替換為下劃線）
    """
    s = s.strip().lower()
    s = re.sub(r"[^\w\-]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")


def secure_filename(filename: str) -> str:
    """
    安全文件名處理（FastAPI 沒有內建的 secure_filename）
    使用 slugify 確保文件名安全
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 處理後的安全文件名
    """
    # 移除路徑分隔符
    filename = os.path.basename(filename)
    # 分離文件名和擴展名
    name, ext = os.path.splitext(filename)
    # 對文件名部分進行 slugify
    safe_name = slugify(name)
    # 保留擴展名（如果有的話）
    return safe_name + ext if ext else safe_name


def safe_voice_filename(text: str, max_length: int = 200) -> str:
    """
    為語音文件生成安全的文件名
    
    使用 slugify 處理文件名，確保安全且一致。
    
    Args:
        text: 原始文本
        max_length: 最大文件名長度
        
    Returns:
        str: 處理後的安全文件名
    """
    # 使用 slugify 處理文件名
    safe_name = slugify(text)
    # 限制長度
    if len(safe_name) > max_length:
        safe_name = safe_name[:max_length]
    return safe_name


def get_image_path(session_id: str, filename: str) -> Path:
    """
    獲取圖片文件路徑（按優先順序查找）
    
    Args:
        session_id: 會話 ID
        filename: 文件名
        
    Returns:
        Path: 圖片文件路徑，如果不存在則返回 None
    """
    from libs.config import OUTPUTS_DIR, PASSAGE_IMAGE_DIR
    
    session_dir = Path(OUTPUTS_DIR) / session_id
    
    # 優先順序：source 目錄 -> session 根目錄 -> passage_images（向後兼容）
    paths_to_check = [
        session_dir / "source" / filename,
        session_dir / filename,
        Path(PASSAGE_IMAGE_DIR) / filename
    ]
    
    for path in paths_to_check:
        if path.exists():
            return path
    
    return None

