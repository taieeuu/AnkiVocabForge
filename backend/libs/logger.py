"""
共用的日誌記錄模組
可以在 UI 和其他 script 中使用
"""
from enum import Enum
from typing import Callable, Optional
import sys

class LogLevel(Enum):
    """日誌級別"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"
    DISPLAY = "display"
    DEFAULT = None

    def _get_priority(self) -> int:
        """取得日誌級別的優先順序數值（用於過濾）"""
        if self.value is None:
            return -1
        # 優先順序：ERROR (4) > WARNING (3) > SUCCESS/INFO (2) > DISPLAY (1) > DEBUG (0)
        priority_map = {
            "error": 4,
            "warning": 3,
            "success": 2,
            "info": 2,
            "display": 1,
            "debug": 0,
        }
        return priority_map.get(self.value, 0)

# 顏色配置（用於 UI）
LOG_COLORS = {
    LogLevel.INFO: "#0066CC",
    LogLevel.SUCCESS: "#00AA00",
    LogLevel.WARNING: "#FF8800",
    LogLevel.ERROR: "#CC0000",
    LogLevel.DEBUG: "#888888",
    LogLevel.DISPLAY: "#666666",
}

# ANSI 顏色碼（用於終端機）
ANSI_COLORS = {
    LogLevel.INFO: "\033[94m",      # 藍色
    LogLevel.SUCCESS: "\033[92m",   # 綠色
    LogLevel.WARNING: "\033[93m",   # 黃色
    LogLevel.ERROR: "\033[91m",     # 紅色
    LogLevel.DEBUG: "\033[90m",     # 灰色
    LogLevel.DISPLAY: "\033[90m", # 灰色
}
ANSI_RESET = "\033[0m"


class Logger:
    """
    共用的日誌記錄器
    可以註冊回調函數來處理日誌輸出
    """
    def __init__(self):
        self._callbacks: list[Callable[[LogLevel, str], None]] = []
        self._default_output = True  # 預設輸出到 stdout
        self._min_level: Optional[LogLevel] = None  # 最小日誌級別（None 表示不過濾）
    
    def set_min_level(self, level: Optional[LogLevel]):
        """
        設定最小日誌級別，低於此級別的日誌將被過濾
        
        Args:
            level: 最小日誌級別，None 表示不過濾（顯示所有日誌）
                  例如：LogLevel.INFO 會過濾掉 DEBUG 訊息
        """
        self._min_level = level
    
    def set_debug_mode(self, enabled: bool):
        """
        設定是否啟用 Debug 模式
        
        Args:
            enabled: True 表示顯示所有日誌（包括 DEBUG），False 表示過濾 DEBUG 訊息
        """
        if enabled:
            self._min_level = None  # 不過濾，顯示所有日誌
        else:
            self._min_level = LogLevel.INFO  # 過濾 DEBUG 訊息
    
    def register_callback(self, callback: Callable[[LogLevel, str], None]):
        """
        註冊日誌回調函數
        
        Args:
            callback: 回調函數，接收 (level: LogLevel, msg: str) 參數
        """
        self._callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable[[LogLevel, str], None]):
        """移除日誌回調函數"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def set_default_output(self, enabled: bool):
        """設定是否預設輸出到 stdout"""
        self._default_output = enabled
    
    def log(self, level: LogLevel, msg: str):
        """
        記錄日誌
        
        Args:
            level: 日誌級別
            msg: 訊息內容
        """
        # 如果設定了最小日誌級別，過濾低級別的日誌
        if self._min_level is not None:
            # 如果當前日誌級別的優先順序低於最小級別，則過濾
            if level.value is not None:
                level_priority = level._get_priority()
                min_priority = self._min_level._get_priority()
                if level_priority < min_priority:
                    return
        
        # 調用所有註冊的回調函數
        for callback in self._callbacks:
            try:
                callback(level, msg)
            except Exception:
                pass
        
        # 如果啟用預設輸出，輸出到 stdout（帶 ANSI 顏色）
        if self._default_output and not self._callbacks:
            self._print_to_stdout(level, msg)
    
    def _print_to_stdout(self, level: LogLevel, msg: str):
        """輸出到 stdout（帶 ANSI 顏色）"""
        if level == LogLevel.DEFAULT or level.value is None:
            print(msg, end="")
        else:
            # 添加標籤
            tag = f"[{level.name}]"
            color = ANSI_COLORS.get(level, "")
            reset = ANSI_RESET
            print(f"{color}{tag}{reset} {msg}", end="")
    
    # 便利方法
    def info(self, msg: str):
        """記錄 INFO 級別日誌"""
        self.log(LogLevel.INFO, msg)
    
    def success(self, msg: str):
        """記錄 SUCCESS 級別日誌"""
        self.log(LogLevel.SUCCESS, msg)
    
    def warning(self, msg: str):
        """記錄 WARNING 級別日誌"""
        self.log(LogLevel.WARNING, msg)
    
    def error(self, msg: str):
        """記錄 ERROR 級別日誌"""
        self.log(LogLevel.ERROR, msg)
    
    def debug(self, msg: str):
        """記錄 DEBUG 級別日誌"""
        self.log(LogLevel.DEBUG, msg)


# 全域 logger 實例
_global_logger = Logger()

def get_logger() -> Logger:
    """取得全域 logger 實例"""
    return _global_logger

def log(level: LogLevel, msg: str):
    """便利函數：記錄日誌"""
    _global_logger.log(level, msg)

def info(msg: str):
    """便利函數：記錄 INFO 級別日誌"""
    _global_logger.info(msg)

def success(msg: str):
    """便利函數：記錄 SUCCESS 級別日誌"""
    _global_logger.success(msg)

def warning(msg: str):
    """便利函數：記錄 WARNING 級別日誌"""
    _global_logger.warning(msg)

def error(msg: str):
    """便利函數：記錄 ERROR 級別日誌"""
    _global_logger.error(msg)

def debug(msg: str):
    """便利函數：記錄 DEBUG 級別日誌"""
    _global_logger.debug(msg)

