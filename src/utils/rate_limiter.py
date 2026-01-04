"""
Rate Limiter for API Protection.

Implements per-user rate limiting to protect external API quotas
(especially Alpha Vantage which has strict limits).
"""

import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, Any
from functools import wraps
import threading


class RateLimiter:
    """
    Token bucket rate limiter for API calls.
    
    Features:
    - Per-user tracking
    - Configurable limits
    - Thread-safe
    - Response caching
    """
    
    def __init__(
        self,
        max_calls: int = 5,
        window_seconds: int = 60,
        cache_ttl_seconds: int = 60
    ):
        """
        Initialize the rate limiter.
        
        Args:
            max_calls: Maximum calls allowed per window
            window_seconds: Time window in seconds
            cache_ttl_seconds: How long to cache responses
        """
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.cache_ttl = cache_ttl_seconds
        
        # Track calls per user: {user_id: [timestamp1, timestamp2, ...]}
        self.call_history: Dict[str, list] = defaultdict(list)
        
        # Response cache: {cache_key: (response, expiry_time)}
        self.cache: Dict[str, Tuple[Any, float]] = {}
        
        # Thread lock for thread safety
        self.lock = threading.Lock()
    
    def _clean_old_calls(self, user_id: str) -> None:
        """Remove calls outside the current window."""
        cutoff = time.time() - self.window_seconds
        self.call_history[user_id] = [
            t for t in self.call_history[user_id] if t > cutoff
        ]
    
    def _clean_expired_cache(self) -> None:
        """Remove expired cache entries."""
        now = time.time()
        expired = [k for k, (_, exp) in self.cache.items() if exp < now]
        for k in expired:
            del self.cache[k]
    
    def get_remaining_calls(self, user_id: str = "default") -> int:
        """
        Get remaining calls for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of calls remaining in current window
        """
        with self.lock:
            self._clean_old_calls(user_id)
            return max(0, self.max_calls - len(self.call_history[user_id]))
    
    def get_reset_time(self, user_id: str = "default") -> Optional[float]:
        """
        Get seconds until rate limit resets.
        
        Args:
            user_id: User identifier
            
        Returns:
            Seconds until reset, or None if not rate limited
        """
        with self.lock:
            self._clean_old_calls(user_id)
            if not self.call_history[user_id]:
                return None
            
            oldest_call = min(self.call_history[user_id])
            reset_at = oldest_call + self.window_seconds
            remaining = reset_at - time.time()
            return max(0, remaining)
    
    def check_rate_limit(self, user_id: str = "default") -> Tuple[bool, str]:
        """
        Check if a user can make a call.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (allowed, message)
        """
        with self.lock:
            self._clean_old_calls(user_id)
            
            current_calls = len(self.call_history[user_id])
            
            if current_calls >= self.max_calls:
                reset_time = self.get_reset_time(user_id)
                return False, f"Rate limit reached. Try again in {int(reset_time)}s"
            
            return True, f"{self.max_calls - current_calls} calls remaining"
    
    def record_call(self, user_id: str = "default") -> bool:
        """
        Record an API call for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if call was allowed, False if rate limited
        """
        with self.lock:
            self._clean_old_calls(user_id)
            
            if len(self.call_history[user_id]) >= self.max_calls:
                return False
            
            self.call_history[user_id].append(time.time())
            return True
    
    def get_cached(self, cache_key: str) -> Optional[Any]:
        """
        Get a cached response.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached response or None if not found/expired
        """
        with self.lock:
            self._clean_expired_cache()
            
            if cache_key in self.cache:
                response, expiry = self.cache[cache_key]
                if time.time() < expiry:
                    return response
            
            return None
    
    def set_cached(self, cache_key: str, response: Any) -> None:
        """
        Cache a response.
        
        Args:
            cache_key: Cache key
            response: Response to cache
        """
        with self.lock:
            expiry = time.time() + self.cache_ttl
            self.cache[cache_key] = (response, expiry)
    
    def rate_limited_call(
        self,
        func,
        cache_key: str,
        user_id: str = "default",
        *args,
        **kwargs
    ) -> Tuple[Any, bool, str]:
        """
        Execute a function with rate limiting and caching.
        
        Args:
            func: Function to call
            cache_key: Cache key for the response
            user_id: User identifier
            *args, **kwargs: Arguments to pass to func
            
        Returns:
            Tuple of (result, from_cache, message)
        """
        # Check cache first
        cached = self.get_cached(cache_key)
        if cached is not None:
            return cached, True, "Served from cache"
        
        # Check rate limit
        allowed, message = self.check_rate_limit(user_id)
        if not allowed:
            return None, False, message
        
        # Record call and execute
        self.record_call(user_id)
        
        try:
            result = func(*args, **kwargs)
            self.set_cached(cache_key, result)
            remaining = self.get_remaining_calls(user_id)
            return result, False, f"Success. {remaining} calls remaining"
        except Exception as e:
            return None, False, f"Error: {str(e)}"


# Global rate limiter for Alpha Vantage
# 5 calls per minute per user, 60s cache
_alpha_vantage_limiter: Optional[RateLimiter] = None


def get_alpha_vantage_limiter() -> RateLimiter:
    """Get the global Alpha Vantage rate limiter."""
    global _alpha_vantage_limiter
    if _alpha_vantage_limiter is None:
        _alpha_vantage_limiter = RateLimiter(
            max_calls=5,
            window_seconds=60,
            cache_ttl_seconds=60
        )
    return _alpha_vantage_limiter


def rate_limited(limiter: RateLimiter, cache_key_func=None):
    """
    Decorator for rate-limited functions.
    
    Args:
        limiter: RateLimiter instance
        cache_key_func: Function to generate cache key from args
        
    Example:
        @rate_limited(get_alpha_vantage_limiter())
        def fetch_stock_data(symbol):
            return requests.get(...)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Get user_id from kwargs if present
            user_id = kwargs.pop('_user_id', 'default')
            
            # Execute with rate limiting
            result, from_cache, message = limiter.rate_limited_call(
                lambda: func(*args, **kwargs),
                cache_key,
                user_id
            )
            
            if result is None and "Rate limit" in message:
                raise RateLimitExceeded(message)
            
            return result
        
        return wrapper
    return decorator


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    pass


def format_rate_limit_status(limiter: RateLimiter, user_id: str = "default") -> str:
    """
    Format rate limit status for display.
    
    Args:
        limiter: RateLimiter instance
        user_id: User identifier
        
    Returns:
        Formatted status string
    """
    remaining = limiter.get_remaining_calls(user_id)
    reset_time = limiter.get_reset_time(user_id)
    
    if remaining == 0:
        return f"⚠️ Rate limit reached. Resets in {int(reset_time)}s"
    elif remaining <= 2:
        return f"⚡ {remaining}/{limiter.max_calls} calls remaining"
    else:
        return f"✅ {remaining}/{limiter.max_calls} calls remaining"


