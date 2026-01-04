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


def log_api_call(
    logger: logging.Logger,
    endpoint: str,
    user_id: str,
    duration: float,
    status_code: int = 200,
    error: Optional[str] = None,
) -> None:
    """
    Log API call with structured information.

    Args:
        logger: Logger instance.
        endpoint: API endpoint called.
        user_id: User identifier.
        duration: Request duration in seconds.
        status_code: HTTP status code.
        error: Error message if any.
    """
    log_data = {
        "endpoint": endpoint,
        "user_id": user_id,
        "duration_seconds": duration,
        "status_code": status_code,
    }
    
    if error:
        log_data["error"] = error
        logger.error(f"API Call: {log_data}")
    else:
        logger.info(f"API Call: {log_data}")


def log_model_inference(
    logger: logging.Logger,
    user_id: str,
    query_length: int,
    response_length: int,
    inference_time: float,
    model_name: str = "gpt2-finetuned",
) -> None:
    """
    Log model inference metrics.

    Args:
        logger: Logger instance.
        user_id: User identifier.
        query_length: Length of input query.
        response_length: Length of generated response.
        inference_time: Inference time in seconds.
        model_name: Model name.
    """
    log_data = {
        "event": "model_inference",
        "user_id": user_id,
        "query_length": query_length,
        "response_length": response_length,
        "inference_time_seconds": inference_time,
        "model": model_name,
        "tokens_per_second": response_length / inference_time if inference_time > 0 else 0,
    }
    
    logger.info(f"Model Inference: {log_data}")


def log_api_key_usage(
    logger: logging.Logger,
    service: str,
    endpoint: str,
    remaining_calls: Optional[int] = None,
) -> None:
    """
    Log API key usage for external services (e.g., Alpha Vantage).

    Args:
        logger: Logger instance.
        service: Service name (e.g., "alpha_vantage").
        endpoint: API endpoint called.
        remaining_calls: Remaining API calls if available.
    """
    log_data = {
        "service": service,
        "endpoint": endpoint,
    }
    
    if remaining_calls is not None:
        log_data["remaining_calls"] = remaining_calls
    
    logger.info(f"API Key Usage: {log_data}")
