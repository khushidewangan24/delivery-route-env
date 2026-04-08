"""Structured logging configuration for strict logging requirement"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        if hasattr(record, "action"):
            log_data["action"] = record.action
        if hasattr(record, "reward"):
            log_data["reward"] = record.reward
        if hasattr(record, "cumulative_reward"):
            log_data["cumulative_reward"] = record.cumulative_reward
        if hasattr(record, "step_number"):
            log_data["step_number"] = record.step_number
            
        # Add any extra attributes
        for key, value in record.__dict__.items():
            if key not in ["session_id", "action", "reward", "cumulative_reward", "step_number"]:
                continue
                
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)


def setup_logger(name: str = "delivery_env") -> logging.Logger:
    """Setup structured logger"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler for persistent logs
    file_handler = logging.FileHandler("delivery_env.log")
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logger()