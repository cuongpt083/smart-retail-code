"""
Production Hardening Tests

Comprehensive tests for:
- Connection pooling
- Caching layer
- Rate limiting
- Circuit breaker
- Error handling
- Logging
"""

import pytest
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from connection_pool import SQLiteConnectionPool, ConnectionPoolExhausted
from cache_manager import CacheManager, MemoryCache
from rate_limiter import RateLimiter, TokenBucket
from error_handling import CircuitBreaker, RetryWithBackoff, CircuitBreakerError


# ============================================================================
# CONNECTION POOL TESTS
# ============================================================================

class TestConnectionPool:
    """Test SQLite connection pooling"""

    def test_pool_initialization(self):
        """Test pool creates correct number of connections"""
        pool = SQLiteConnectionPool(":memory:", max_connections=2)
        assert len(pool.connections) == 2
        pool.close_all()

    def test_get_connection(self):
        """Test acquiring connection"""
        pool = SQLiteConnectionPool(":memory:", max_connections=2)
        conn = pool.get_connection()
        assert conn is not None
        pool.close_all()

    def test_return_connection(self):
        """Test returning connection to pool"""
        pool = SQLiteConnectionPool(":memory:", max_connections=2)
        conn = pool.get_connection()
        pool.return_connection(conn)
        # Should be able to get it again
        conn2 = pool.get_connection(timeout=0.5)
        assert conn2 is not None
        pool.close_all()

    def test_pool_exhaustion(self):
        """Test error when pool exhausted"""
        pool = SQLiteConnectionPool(":memory:", max_connections=1)
        conn = pool.get_connection()
        with pytest.raises(ConnectionPoolExhausted):
            pool.get_connection(timeout=0.1)
        pool.close_all()

    def test_wal_mode_enabled(self):
        """Test WAL mode is enabled (or memory for in-memory DB)"""
        pool = SQLiteConnectionPool(":memory:")
        conn = pool.get_connection()
        cursor = conn.cursor()
        mode = cursor.execute("PRAGMA journal_mode").fetchone()[0]
        # In-memory DB may use MEMORY mode instead of WAL, which is fine
        assert mode.upper() in ("WAL", "MEMORY")
        pool.close_all()

    def test_pool_cleanup(self):
        """Test pool cleanup closes connections"""
        pool = SQLiteConnectionPool(":memory:", max_connections=2)
        pool.close_all()
        assert len(pool.connections) == 0


# ============================================================================
# CACHE MANAGER TESTS
# ============================================================================

class TestCacheManager:
    """Test caching layer"""

    def test_memory_cache_get_set(self):
        """Test memory cache get/set"""
        cache = MemoryCache()
        cache.set("key", "value", ttl=10)
        assert cache.get("key") == "value"

    def test_cache_ttl_expiration(self):
        """Test cache TTL expiration"""
        cache = MemoryCache()
        cache.set("key", "value", ttl=0)  # Instant expiry
        time.sleep(0.1)
        assert cache.get("key") is None

    def test_cache_manager_initialization(self):
        """Test cache manager initialization"""
        manager = CacheManager(backend="memory")
        assert manager is not None

    def test_cache_manager_rfm(self):
        """Test RFM cache operations"""
        manager = CacheManager(backend="memory")
        scores = {"R": 5, "F": 4, "M": 3}
        manager.set_rfm_scores("cust_001", scores)
        assert manager.get_rfm_scores("cust_001") == scores

    def test_cache_manager_apriori(self):
        """Test Apriori cache operations"""
        manager = CacheManager(backend="memory")
        rules = [{"a": 1, "b": 2}]
        manager.set_apriori_rules(rules)
        assert manager.get_apriori_rules() == rules

    def test_cache_manager_products(self):
        """Test product cache operations"""
        manager = CacheManager(backend="memory")
        products = [{"id": 1, "name": "Product"}]
        manager.set_products(products)
        assert manager.get_products() == products

    def test_cache_invalidation(self):
        """Test cache invalidation"""
        manager = CacheManager(backend="memory")
        manager.set_rfm_scores("cust_001", {"R": 5})
        manager.invalidate_rfm_scores("cust_001")
        assert manager.get_rfm_scores("cust_001") is None

    def test_cache_invalidate_all(self):
        """Test invalidate caches"""
        manager = CacheManager(backend="memory")
        manager.set_rfm_scores("cust_001", {"R": 5})
        manager.set_apriori_rules([{"a": 1}])
        manager.set_products([{"id": 1}])
        manager.set_customers([{"id": 1}])

        # Invalidate all
        manager.invalidate_all()

        # These should be None after invalidation
        assert manager.get_apriori_rules() is None
        assert manager.get_products() is None
        assert manager.get_customers() is None


# ============================================================================
# RATE LIMITER TESTS
# ============================================================================

class TestTokenBucket:
    """Test token bucket rate limiter"""

    def test_token_bucket_allow(self):
        """Test allowing request"""
        bucket = TokenBucket(rate=10, capacity=5)
        assert bucket.allow_request() is True

    def test_token_bucket_exhaustion(self):
        """Test bucket exhaustion"""
        bucket = TokenBucket(rate=1, capacity=1)
        assert bucket.allow_request() is True
        # Second request should fail (capacity exhausted)
        assert bucket.allow_request() is False

    def test_token_refill(self):
        """Test token refilling over time"""
        bucket = TokenBucket(rate=10, capacity=1)
        # Exhaust
        bucket.allow_request()
        # Wait for refill
        time.sleep(0.15)
        # Should allow again
        assert bucket.allow_request() is True

    def test_token_bucket_status(self):
        """Test getting bucket status"""
        bucket = TokenBucket(rate=10, capacity=5)
        status = bucket.get_status()
        assert status["capacity"] == 5
        assert status["rate"] == 10


class TestRateLimiter:
    """Test rate limiter"""

    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization"""
        limiter = RateLimiter()
        assert "kiotviet" in limiter.limiters
        assert "zalo" in limiter.limiters
        assert "dashboard" in limiter.limiters

    def test_check_limit_allowed(self):
        """Test limit check when allowed"""
        limiter = RateLimiter()
        # First few should be allowed
        assert limiter.check_limit("dashboard") is True

    def test_unknown_endpoint(self):
        """Test unknown endpoint returns True (allow by default)"""
        limiter = RateLimiter()
        assert limiter.check_limit("unknown") is True

    def test_get_status(self):
        """Test getting endpoint status"""
        limiter = RateLimiter()
        status = limiter.get_status("kiotviet")
        assert "tokens" in status
        assert "capacity" in status

    def test_get_all_status(self):
        """Test getting all endpoint statuses"""
        limiter = RateLimiter()
        statuses = limiter.get_all_status()
        assert "kiotviet" in statuses
        assert "zalo" in statuses
        assert "dashboard" in statuses


# ============================================================================
# CIRCUIT BREAKER TESTS
# ============================================================================

class TestCircuitBreaker:
    """Test circuit breaker"""

    def test_breaker_initial_state(self):
        """Test breaker starts in CLOSED state"""
        breaker = CircuitBreaker()
        assert breaker.get_state() == "closed"

    def test_breaker_success_call(self):
        """Test successful call"""
        breaker = CircuitBreaker()
        result = breaker.call(lambda: "success")
        assert result == "success"

    def test_breaker_opens_on_failures(self):
        """Test breaker opens after threshold failures"""
        breaker = CircuitBreaker(failure_threshold=2)

        def fail():
            raise ValueError("test error")

        # First failure
        with pytest.raises(ValueError):
            breaker.call(fail)

        # Second failure
        with pytest.raises(ValueError):
            breaker.call(fail)

        # Should now be open
        assert breaker.get_state() == "open"

    def test_breaker_fails_fast_when_open(self):
        """Test breaker fails fast when open"""
        breaker = CircuitBreaker(failure_threshold=1)

        def fail():
            raise ValueError("test error")

        # Trigger open
        with pytest.raises(ValueError):
            breaker.call(fail)

        # Should fail fast without calling function
        with pytest.raises(CircuitBreakerError):
            breaker.call(fail)

    def test_breaker_recovery(self):
        """Test breaker recovery after timeout"""
        breaker = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=1  # 1 second
        )

        def fail():
            raise ValueError("test error")

        # Open the breaker
        with pytest.raises(ValueError):
            breaker.call(fail)

        # Wait for recovery timeout
        time.sleep(1.1)

        # Should allow another attempt
        with pytest.raises(ValueError):
            breaker.call(fail)


class TestRetryWithBackoff:
    """Test retry with backoff"""

    def test_successful_call(self):
        """Test successful call on first attempt"""
        retry = RetryWithBackoff(max_retries=3)
        result = retry.call(lambda: "success")
        assert result == "success"

    def test_retry_on_failure(self):
        """Test retry after failure"""
        call_count = [0]

        def failing_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ValueError("fail")
            return "success"

        retry = RetryWithBackoff(max_retries=3, initial_delay=0.01)
        result = retry.call(failing_func)
        assert result == "success"
        assert call_count[0] == 2

    def test_all_retries_exhausted(self):
        """Test error when all retries exhausted"""
        retry = RetryWithBackoff(max_retries=2, initial_delay=0.01)

        def fail():
            raise ValueError("always fails")

        with pytest.raises(ValueError):
            retry.call(fail)

    def test_backoff_delay(self):
        """Test exponential backoff delay"""
        call_times = []

        def track_time():
            call_times.append(time.time())
            if len(call_times) < 2:
                raise ValueError("fail")
            return "success"

        retry = RetryWithBackoff(
            max_retries=3,
            initial_delay=0.05,
            backoff_factor=2.0
        )
        retry.call(track_time)

        # Should have been called twice with delay between
        assert len(call_times) == 2
        assert call_times[1] - call_times[0] >= 0.05


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestProductionHardeningIntegration:
    """Integration tests for production hardening"""

    def test_connection_pool_with_cache(self):
        """Test connection pool works with caching"""
        pool = SQLiteConnectionPool(":memory:")
        cache = CacheManager(backend="memory")

        # Get connection
        conn = pool.get_connection()
        assert conn is not None

        # Cache something
        cache.set_products([{"id": 1}])

        # Verify cache and pool work together
        assert cache.get_products() == [{"id": 1}]

        pool.close_all()

    def test_rate_limiter_with_circuit_breaker(self):
        """Test rate limiter with circuit breaker"""
        limiter = RateLimiter()
        breaker = CircuitBreaker()

        # Check limit before calling
        allowed = limiter.check_limit("dashboard")
        assert allowed is True

        # Call with breaker
        result = breaker.call(lambda: "success")
        assert result == "success"

    def test_full_production_stack(self):
        """Test all production components together"""
        # Initialize all components
        pool = SQLiteConnectionPool(":memory:")
        cache = CacheManager(backend="memory")
        limiter = RateLimiter()
        breaker = CircuitBreaker()
        retry = RetryWithBackoff()

        # Use them together
        allowed = limiter.check_limit("dashboard")
        conn = pool.get_connection() if allowed else None
        cache.set_products([{"id": 1}])

        result = breaker.call(lambda: cache.get_products())

        assert allowed is True
        assert conn is not None
        assert result == [{"id": 1}]

        pool.close_all()


# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
