"""
Logging utility module.

Provides centralized logging configuration for the application.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from src.utils.config import get_config


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: Optional[str] = None,
) -> logging.Logger:
    """
    Set up a logger with file and console handlers.

    Args:
        name: Logger name (typically __name__).
        log_file: Optional path to log file. If None, uses config default.
        level: Optional log level. If None, uses config default.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Get configuration
    config = get_config()
    log_level = level or config.get("logging.level", "INFO")
    log_format = config.get("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Set log level
    logger.setLevel(getattr(logging, log_level.upper()))

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file)
    else:
        log_file_path = config.get("logging.file", "logs/app.log")
        log_path = Path(log_file_path)

    # Create logs directory if it doesn't exist
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # File handler with rotation
    max_bytes = config.get("logging.max_bytes", 10485760)  # 10MB
    backup_count = config.get("logging.backup_count", 5)

    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Logger instance.
    """
    return setup_logger(name)

