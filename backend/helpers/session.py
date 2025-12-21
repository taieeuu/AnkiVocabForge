"""
Session 管理相關工具函數
"""
from pathlib import Path
from nanoid import generate
from libs.config import OUTPUTS_DIR
import logging

logger = logging.getLogger(__name__)


def create_session_dir() -> Path:
    """創建以 nano_id 命名的會話目錄"""
    session_id = generate()
    session_dir = Path(OUTPUTS_DIR) / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created session directory: {session_dir}")
    return session_dir


def get_or_create_session_dir(session_id: str = None) -> Path:
    """
    獲取或創建會話目錄
    
    Args:
        session_id: 可選的會話 ID，如果提供則使用現有目錄，否則創建新目錄
        
    Returns:
        Path: 會話目錄路徑
    """
    if session_id:
        session_dir = Path(OUTPUTS_DIR) / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using existing session directory: {session_dir}")
        return session_dir
    else:
        return create_session_dir()


def setup_session_directories(session_dir: Path) -> dict:
    """
    設置會話所需的子目錄
    
    Args:
        session_dir: 會話根目錄
        
    Returns:
        dict: 包含各個子目錄路徑的字典
    """
    source_dir = session_dir / "source"
    orig_dir = session_dir / "orig"
    edited_dir = session_dir / "edited"
    
    source_dir.mkdir(parents=True, exist_ok=True)
    orig_dir.mkdir(parents=True, exist_ok=True)
    edited_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        'source': source_dir,
        'orig': orig_dir,
        'edited': edited_dir
    }

