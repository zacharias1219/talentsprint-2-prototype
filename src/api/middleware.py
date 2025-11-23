"""
API middleware module.

Provides middleware for authentication, error handling, and request processing.
"""

import time
from functools import wraps
from typing import Any, Callable, Dict, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Rate limiting storage (in production, use Redis)
_rate_limit_store: Dict[str, list] = {}


def rate_limit(
    max_requests: int = 60,
    window_seconds: int = 60,
):
    """
    Rate limiting decorator.

    Args:
        max_requests: Maximum requests per window.
        window_seconds: Time window in seconds.

    Returns:
        Decorated function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get identifier (user_id or IP address)
            identifier = kwargs.get("user_id") or kwargs.get("ip_address", "default")

            current_time = time.time()

            # Clean old entries
            if identifier in _rate_limit_store:
                _rate_limit_store[identifier] = [
                    t for t in _rate_limit_store[identifier]
                    if current_time - t < window_seconds
                ]
            else:
                _rate_limit_store[identifier] = []

            # Check rate limit
            if len(_rate_limit_store[identifier]) >= max_requests:
                logger.warning(f"Rate limit exceeded for {identifier}")
                raise Exception("Rate limit exceeded. Please try again later.")

            # Record request
            _rate_limit_store[identifier].append(current_time)

            return func(*args, **kwargs)

        return wrapper
    return decorator


def error_handler(func: Callable) -> Callable:
    """
    Error handling decorator.

    Args:
        func: Function to wrap.

    Returns:
        Decorated function.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            result = func(*args, **kwargs)
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }

    return wrapper


def log_request(func: Callable) -> Callable:
    """
    Request logging decorator.

    Args:
        func: Function to wrap.

    Returns:
        Decorated function.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        logger.info(f"Request: {func.__name__} with args: {args}, kwargs: {kwargs}")

        result = func(*args, **kwargs)

        duration = time.time() - start_time
        logger.info(f"Request {func.__name__} completed in {duration:.2f}s")

        return result

    return wrapper

