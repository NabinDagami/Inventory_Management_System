"""
Error Logging System for Inventory Management Application
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from pathlib import Path

class AppLogger:
    """Application logger for error tracking and debugging"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.log_dir = Path(__file__).parent.parent.parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Main application log
        self.app_log_file = self.log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Error log file
        self.error_log_file = self.log_dir / f"error_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Setup loggers
        self._setup_app_logger()
        self._setup_error_logger()
        
    def _setup_app_logger(self):
        """Setup main application logger"""
        self.app_logger = logging.getLogger("InventoryApp")
        self.app_logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(self.app_log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.app_logger.addHandler(file_handler)
        self.app_logger.addHandler(console_handler)
        
    def _setup_error_logger(self):
        """Setup error logger for critical errors"""
        self.error_logger = logging.getLogger("InventoryAppErrors")
        self.error_logger.setLevel(logging.ERROR)
        
        # Error file handler
        error_handler = logging.FileHandler(self.error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        
        # Formatter with more details
        error_formatter = logging.Formatter(
            '\n' + '='*60 + '\n'
            '[%(asctime)s] CRITICAL ERROR\n'
            'Level: %(levelname)s\n'
            'Message: %(message)s\n'
            '='*60,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_formatter)
        
        self.error_logger.addHandler(error_handler)
    
    def debug(self, message):
        """Log debug message"""
        self.app_logger.debug(message)
    
    def info(self, message):
        """Log info message"""
        self.app_logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.app_logger.warning(message)
    
    def error(self, message, exc_info=None):
        """Log error message"""
        self.app_logger.error(message, exc_info=exc_info)
        self.error_logger.error(message, exc_info=exc_info)
    
    def critical(self, message, exc_info=None):
        """Log critical error message"""
        self.app_logger.critical(message, exc_info=exc_info)
        self.error_logger.critical(message, exc_info=exc_info)
    
    def log_exception(self, exception):
        """Log complete exception with traceback"""
        error_msg = f"Exception: {type(exception).__name__}: {str(exception)}"
        traceback_str = traceback.format_exc()
        
        full_message = f"{error_msg}\nTraceback:\n{traceback_str}"
        
        self.error(full_message)
        
        # Also write to error_file.txt for quick access
        self._write_to_error_file(error_msg, traceback_str)
    
    def _write_to_error_file(self, error_msg, traceback_str):
        """Write error to error_file.txt for quick access"""
        try:
            error_file = Path(__file__).parent.parent.parent / "error_file.txt"
            with open(error_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
                f.write(f"{error_msg}\n")
                f.write(f"Traceback:\n{traceback_str}\n")
                f.write(f"{'='*60}\n")
        except Exception as e:
            self.app_logger.error(f"Failed to write to error_file.txt: {e}")
    
    def get_log_files(self):
        """Get list of all log files"""
        return list(self.log_dir.glob("*.log"))
    
    def clear_old_logs(self, days=7):
        """Clear log files older than specified days"""
        try:
            current_time = datetime.now()
            for log_file in self.log_dir.glob("*.log"):
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if (current_time - file_time).days > days:
                    log_file.unlink()
                    self.info(f"Deleted old log file: {log_file.name}")
        except Exception as e:
            self.error(f"Failed to clear old logs: {e}")

# Global logger instance
logger = AppLogger()

def log_error(func):
    """Decorator to log errors in functions"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.log_exception(e)
            raise
    return wrapper
