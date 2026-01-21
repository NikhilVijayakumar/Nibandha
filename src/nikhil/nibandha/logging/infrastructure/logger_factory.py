import logging
from pathlib import Path
from typing import Optional

def setup_logger(app_name: str, log_level: str, log_file: Optional[Path] = None) -> logging.Logger:
    """Initialize named logger with file and console handlers."""
    
    # Get the named logger FIRST
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)
    
    # Clear existing handlers to prevent duplication if called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()
    
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    
    # Create and attach file handler directly to named logger
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Create and attach console handler directly to named logger
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False
    
    return logger
