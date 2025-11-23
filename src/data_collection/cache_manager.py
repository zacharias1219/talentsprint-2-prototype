"""
Cache manager module.

Provides caching functionality using Redis or file-based cache.
"""

import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import redis

from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Cache manager for API responses and computed data."""

    def __init__(self, use_redis: Optional[bool] = None):
        """
        Initialize cache manager.

        Args:
            use_redis: Whether to use Redis. If None, uses config setting.
        """
        config = get_config()
        self.use_redis = use_redis if use_redis is not None else config.get("cache.enabled", True)

        if self.use_redis:
            try:
                self.redis_client = redis.Redis(
                    host=config.get("cache.host", "localhost"),
                    port=config.get("cache.port", 6379),
                    db=config.get("cache.db", 0),
                    decode_responses=False,  # We'll handle serialization ourselves
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Falling back to file cache.")
                self.use_redis = False

        if not self.use_redis:
            # File-based cache
            cache_dir = Path("data/cache")
            cache_dir.mkdir(parents=True, exist_ok=True)
            self.cache_dir = cache_dir
            logger.info(f"File-based cache initialized at {cache_dir}")

        self.default_ttl = config.get("cache.default_ttl", 3600)

    def _serialize(self, value: Any) -> bytes:
        """Serialize value for storage."""
        return pickle.dumps(value)

    def _deserialize(self, data: bytes) -> Any:
        """Deserialize value from storage."""
        return pickle.loads(data)

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key.

        Returns:
            Cached value or None if not found or expired.
        """
        try:
            if self.use_redis:
                data = self.redis_client.get(key)
                if data is None:
                    return None
                return self._deserialize(data)
            else:
                # File-based cache
                cache_file = self.cache_dir / f"{key}.cache"
                if not cache_file.exists():
                    return None

                # Check expiration
                meta_file = self.cache_dir / f"{key}.meta"
                if meta_file.exists():
                    with open(meta_file, "r") as f:
                        meta = json.load(f)
                    expires_at = datetime.fromisoformat(meta["expires_at"])
                    if datetime.now() > expires_at:
                        # Expired, delete files
                        cache_file.unlink()
                        meta_file.unlink()
                        return None

                # Load cached data
                with open(cache_file, "rb") as f:
                    return pickle.load(f)

        except Exception as e:
            logger.error(f"Error retrieving cache key {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time to live in seconds. If None, uses default.

        Returns:
            True if successful, False otherwise.
        """
        try:
            ttl = ttl or self.default_ttl

            if self.use_redis:
                serialized = self._serialize(value)
                self.redis_client.setex(key, ttl, serialized)
                return True
            else:
                # File-based cache
                cache_file = self.cache_dir / f"{key}.cache"
                meta_file = self.cache_dir / f"{key}.meta"

                # Save data
                with open(cache_file, "wb") as f:
                    pickle.dump(value, f)

                # Save metadata with expiration
                expires_at = datetime.now() + timedelta(seconds=ttl)
                meta = {"expires_at": expires_at.isoformat(), "created_at": datetime.now().isoformat()}
                with open(meta_file, "w") as f:
                    json.dump(meta, f)

                return True

        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key.

        Returns:
            True if successful, False otherwise.
        """
        try:
            if self.use_redis:
                self.redis_client.delete(key)
                return True
            else:
                cache_file = self.cache_dir / f"{key}.cache"
                meta_file = self.cache_dir / f"{key}.meta"

                if cache_file.exists():
                    cache_file.unlink()
                if meta_file.exists():
                    meta_file.unlink()

                return True

        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful, False otherwise.
        """
        try:
            if self.use_redis:
                self.redis_client.flushdb()
                return True
            else:
                # Delete all cache files
                for cache_file in self.cache_dir.glob("*.cache"):
                    cache_file.unlink()
                for meta_file in self.cache_dir.glob("*.meta"):
                    meta_file.unlink()
                return True

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

