"""
Rate Limiter - Protect APIs from overload

Implements:
- Token bucket algorithm
- Per-endpoint rate limiting
- Configurable limits
- Graceful degradation
"""

import time
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class TokenBucket:
    """Token bucket rate limiter"""

    def __init__(self, rate: float, capacity: int):
        """
        Initialize token bucket

        Args:
            rate: tokens per second
            capacity: max tokens
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()

    def allow_request(self, tokens: int = 1) -> bool:
        """Check if request allowed"""
        now = time.time()
        elapsed = now - self.last_refill

        # Refill tokens
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        return False

    def get_status(self) -> Dict:
        """Get current status"""
        return {
            "tokens": self.tokens,
            "capacity": self.capacity,
            "rate": self.rate
        }


class RateLimiter:
    """Rate limiter for APIs and endpoints"""

    def __init__(self):
        """Initialize rate limiter"""
        self.limiters: Dict[str, TokenBucket] = {}
        self._configure_limits()
        logger.info("Rate limiter initialized")

    def _configure_limits(self):
        """Configure rate limits per endpoint"""
        # Kiotviet API: 100 req/min
        self.limiters["kiotviet"] = TokenBucket(
            rate=100 / 60,  # 1.67 req/sec
            capacity=10     # Allow burst of 10
        )

        # Zalo API: 50 msg/min
        self.limiters["zalo"] = TokenBucket(
            rate=50 / 60,   # 0.83 msg/sec
            capacity=5      # Allow burst of 5
        )

        # Dashboard: 1000 req/min
        self.limiters["dashboard"] = TokenBucket(
            rate=1000 / 60, # 16.67 req/sec
            capacity=50     # Allow burst of 50
        )

    def check_limit(self, endpoint: str) -> bool:
        """Check if request allowed for endpoint"""
        if endpoint not in self.limiters:
            logger.warning(f"Unknown endpoint: {endpoint}")
            return True

        allowed = self.limiters[endpoint].allow_request()

        if not allowed:
            logger.warning(f"Rate limit exceeded: {endpoint}")

        return allowed

    def get_status(self, endpoint: str) -> Dict:
        """Get rate limit status"""
        limiter = self.limiters.get(endpoint)
        if not limiter:
            return {}

        return limiter.get_status()

    def get_all_status(self) -> Dict[str, Dict]:
        """Get status for all endpoints"""
        return {
            endpoint: limiter.get_status()
            for endpoint, limiter in self.limiters.items()
        }


# Global rate limiter
_limiter = None

def get_limiter() -> RateLimiter:
    """Get global rate limiter"""
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter()
    return _limiter
