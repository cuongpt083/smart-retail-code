"""
Cache Manager - High-performance caching with TTL support

Supports:
- In-memory caching
- Redis backing (optional)
- Configurable TTL per cache type
- Cache invalidation
"""

import time
from typing import Any, Optional, Dict
from abc import ABC, abstractmethod
import logging
import json

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """Abstract base for cache backends"""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int):
        pass

    @abstractmethod
    def delete(self, key: str):
        pass


class MemoryCache(CacheBackend):
    """In-memory cache with TTL support"""

    def __init__(self):
        self.cache: Dict[str, tuple] = {}  # {key: (value, expire_time)}
        logger.info("Memory cache initialized")

    def get(self, key: str) -> Optional[Any]:
        """Get value if not expired"""
        if key not in self.cache:
            return None

        value, expire_time = self.cache[key]
        if time.time() > expire_time:
            del self.cache[key]
            return None

        logger.debug(f"Cache hit: {key}")
        return value

    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value with TTL in seconds"""
        expire_time = time.time() + ttl
        self.cache[key] = (value, expire_time)
        logger.debug(f"Cache set: {key} (TTL={ttl}s)")

    def delete(self, key: str):
        """Delete key"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache deleted: {key}")

    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        logger.info("Cache cleared")


class RedisCache(CacheBackend):
    """Redis-backed cache"""

    def __init__(self, host: str = "localhost", port: int = 6379):
        """Initialize Redis cache"""
        try:
            import redis
            self.redis = redis.Redis(host=host, port=port, decode_responses=True)
            self.redis.ping()
            logger.info(f"Redis cache initialized: {host}:{port}")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            value = self.redis.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in Redis with TTL"""
        try:
            self.redis.setex(key, ttl, json.dumps(value))
            logger.debug(f"Cache set: {key} (TTL={ttl}s)")
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    def delete(self, key: str):
        """Delete key from Redis"""
        try:
            self.redis.delete(key)
            logger.debug(f"Cache deleted: {key}")
        except Exception as e:
            logger.error(f"Cache delete error: {e}")


class CacheManager:
    """
    High-level cache manager with sensible defaults

    Cache TTLs:
    - RFM scores: 5 minutes
    - Apriori rules: 10 minutes
    - Products: 1 hour
    - Customers: 30 minutes
    """

    def __init__(self, backend: str = "memory"):
        """
        Initialize cache manager

        Args:
            backend: "memory" or "redis"
        """
        if backend == "memory":
            self.backend = MemoryCache()
        elif backend == "redis":
            self.backend = RedisCache()
        else:
            raise ValueError(f"Unknown cache backend: {backend}")

        logger.info(f"Cache manager initialized: backend={backend}")

    # RFM Cache Methods
    def get_rfm_scores(self, customer_id: str) -> Optional[Dict]:
        """Get RFM scores for customer"""
        return self.backend.get(f"rfm:{customer_id}")

    def set_rfm_scores(self, customer_id: str, scores: Dict):
        """Cache RFM scores (5 min TTL)"""
        self.backend.set(f"rfm:{customer_id}", scores, ttl=300)

    def invalidate_rfm_scores(self, customer_id: Optional[str] = None):
        """Invalidate RFM cache"""
        if customer_id:
            self.backend.delete(f"rfm:{customer_id}")
        logger.info("RFM cache invalidated")

    # Apriori Cache Methods
    def get_apriori_rules(self) -> Optional[list]:
        """Get cached Apriori rules"""
        return self.backend.get("apriori:rules")

    def set_apriori_rules(self, rules: list):
        """Cache Apriori rules (10 min TTL)"""
        self.backend.set("apriori:rules", rules, ttl=600)

    def invalidate_apriori(self):
        """Invalidate Apriori cache"""
        self.backend.delete("apriori:rules")
        logger.info("Apriori cache invalidated")

    # Product Cache Methods
    def get_products(self) -> Optional[list]:
        """Get cached product list"""
        return self.backend.get("products:all")

    def set_products(self, products: list):
        """Cache product list (1 hour TTL)"""
        self.backend.set("products:all", products, ttl=3600)

    def invalidate_products(self):
        """Invalidate product cache"""
        self.backend.delete("products:all")
        logger.info("Product cache invalidated")

    # Customer Cache Methods
    def get_customers(self) -> Optional[list]:
        """Get cached customer list"""
        return self.backend.get("customers:all")

    def set_customers(self, customers: list):
        """Cache customer list (30 min TTL)"""
        self.backend.set("customers:all", customers, ttl=1800)

    def invalidate_customers(self):
        """Invalidate customer cache"""
        self.backend.delete("customers:all")
        logger.info("Customer cache invalidated")

    # Utility Methods
    def invalidate_all(self):
        """Invalidate all caches"""
        self.invalidate_rfm_scores()
        self.invalidate_apriori()
        self.invalidate_products()
        self.invalidate_customers()
        logger.info("All caches invalidated")


# Global cache instance
_cache = None

def init_cache(backend: str = "memory") -> CacheManager:
    """Initialize global cache"""
    global _cache
    if _cache is None:
        _cache = CacheManager(backend=backend)
    return _cache

def get_cache() -> CacheManager:
    """Get global cache"""
    global _cache
    if _cache is None:
        _cache = init_cache()
    return _cache
