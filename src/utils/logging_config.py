#!/usr/bin/env python3
"""
Logging Configuration
Provides comprehensive logging setup for production
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path

def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/kolekt.log",
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
):
    """Setup comprehensive logging configuration"""
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_file_size,
        backupCount=backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_log_file = log_path.parent / "kolekt_error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=max_file_size,
        backupCount=backup_count
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    
    # Log startup
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Error log file: {error_log_file}")

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

class RequestLogger:
    """Specialized logger for HTTP requests"""
    
    def __init__(self):
        self.logger = logging.getLogger("kolekt.requests")
    
    def log_request(self, method: str, path: str, status_code: int, duration: float, user_id: str = None):
        """Log HTTP request details"""
        user_info = f" (user: {user_id})" if user_id else ""
        self.logger.info(
            f"HTTP {method} {path} -> {status_code} ({duration:.3f}s){user_info}"
        )
    
    def log_error(self, method: str, path: str, error: str, user_id: str = None):
        """Log HTTP request errors"""
        user_info = f" (user: {user_id})" if user_id else ""
        self.logger.error(
            f"HTTP {method} {path} -> ERROR: {error}{user_info}"
        )

class PerformanceLogger:
    """Specialized logger for performance metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger("kolekt.performance")
    
    def log_operation(self, operation: str, duration: float, success: bool = True):
        """Log operation performance"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"PERF: {operation} -> {duration:.3f}s [{status}]")
    
    def log_slow_operation(self, operation: str, duration: float, threshold: float = 1.0):
        """Log slow operations"""
        if duration > threshold:
            self.logger.warning(f"SLOW: {operation} took {duration:.3f}s (threshold: {threshold}s)")

class SecurityLogger:
    """Specialized logger for security events"""
    
    def __init__(self):
        self.logger = logging.getLogger("kolekt.security")
    
    def log_login_attempt(self, email: str, success: bool, ip_address: str = None):
        """Log login attempts"""
        status = "SUCCESS" if success else "FAILED"
        ip_info = f" from {ip_address}" if ip_address else ""
        self.logger.info(f"AUTH: Login {status} for {email}{ip_info}")
    
    def log_rate_limit(self, ip_address: str, endpoint: str):
        """Log rate limit violations"""
        self.logger.warning(f"RATE_LIMIT: {ip_address} exceeded limit for {endpoint}")
    
    def log_suspicious_activity(self, activity: str, details: dict):
        """Log suspicious activities"""
        self.logger.warning(f"SUSPICIOUS: {activity} - {details}")

# Global logger instances
request_logger = RequestLogger()
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(f"kolekt.{name}")

# Initialize logging when module is imported
if not logging.getLogger().handlers:
    setup_logging()
