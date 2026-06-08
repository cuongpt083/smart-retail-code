# 🔒 Task #17: Production Hardening

**Task ID**: #17  
**Status**: Pending  
**Effort**: 24 hours  
**Priority**: HIGH (Critical for reliability)  
**Owner**: Development Team  
**Start Date**: June 12, 2026  
**Target Completion**: June 14, 2026

---

## 🎯 Objective

Harden the Smart Retail Analytics MVP for production deployment by implementing:
- Connection pooling & WAL mode for SQLite
- Caching layer for performance
- Rate limiting for API safety
- Advanced error handling & recovery
- Structured logging for debugging
- Security hardening
- Configuration management

**Target SLA**: 99.5% uptime, < 500ms response time, graceful API failure handling

---

## 📋 Requirements

### Functional Requirements

1. **Connection Pooling**
   - Max 2 concurrent SQLite connections
   - Connection timeout: 5 seconds
   - Automatic connection cleanup
   - WAL mode enabled for concurrent access

2. **Caching Layer**
   - Cache RFM scores (5-min TTL)
   - Cache Apriori rules (10-min TTL)
   - Cache product catalog (1-hour TTL)
   - Cache customer list (30-min TTL)
   - Manual invalidation on data updates
   - Support in-memory and Redis backends

3. **Rate Limiting**
   - Kiotviet API: 100 req/min
   - Zalo API: 50 msg/min
   - Dashboard: 1000 req/min
   - Token bucket algorithm
   - Per-endpoint limiting
   - Graceful degradation (queue requests)

4. **Error Handling**
   - Circuit breaker for external APIs
   - Automatic retry with exponential backoff
   - Fallback to cached data on API failure
   - Graceful degradation (partial functionality)
   - Detailed error messages for debugging

5. **Logging**
   - Structured JSON logging
   - Log levels: DEBUG, INFO, WARNING, ERROR
   - Contextual information (user, request ID, etc.)
   - No sensitive data in logs
   - Rotation: 10MB/file, keep 10 files

### Non-Functional Requirements

- **Performance**: Cache hit rate > 80%, response time < 200ms
- **Reliability**: Circuit breaker restores service in < 60 sec
- **Security**: No API keys in logs, password never logged
- **Maintainability**: Clear configuration, easy to adjust thresholds
- **Observability**: All errors logged with full context

---

## 🏗️ Architecture

### Current State
```
Streamlit App
    ↓
Data Loader (SQLite direct)
    ↓
Kiotviet Client (no caching)
Zalo Messenger (no pooling)
    ↓
SQLite (no pooling, no WAL)
```

### New State (After Hardening)
```
Streamlit App
    ↓
Rate Limiter (per endpoint)
    ↓
Cache Manager (RFM, Apriori, Products)
    ↓
Circuit Breaker (for APIs)
    ↓
Data Loader + Connection Pool
Kiotviet Client (with retries)
Zalo Messenger (with retries)
    ↓
SQLite (WAL mode, pooled connections)
    ↓
Monitoring & Logging (structured JSON)
```

---

## 💻 Implementation Details

### Component 1: Connection Pool (Hours 1-4)

**File**: `src/connection_pool.py`

```python
import sqlite3
import queue
import threading
from typing import Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SQLiteConnectionPool:
    """
    SQLite connection pool with WAL mode and connection timeout.
    
    Implements:
    - Maximum concurrent connections (default 2 for SQLite)
    - Connection timeout and reuse
    - Automatic cleanup of idle connections
    - WAL mode for better concurrency
    """
    
    def __init__(
        self,
        db_path: str,
        max_connections: int = 2,
        timeout: float = 5.0,
        check_same_thread: bool = False
    ):
        """
        Initialize connection pool
        
        Args:
            db_path: Path to SQLite database
            max_connections: Max concurrent connections (SQLite default 2)
            timeout: Connection acquisition timeout in seconds
            check_same_thread: SQLite thread safety check
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self.check_same_thread = check_same_thread
        
        # Connection pool queue
        self.available = queue.Queue(maxsize=max_connections)
        self.connections = []
        self.lock = threading.Lock()
        
        # Initialize pool
        self._init_pool()
        
        logger.info(
            f"Connection pool initialized: max={max_connections}, "
            f"timeout={timeout}s, db={db_path}"
        )
    
    def _init_pool(self):
        """Create initial connections"""
        for _ in range(self.max_connections):
            conn = self._create_connection()
            self.connections.append(conn)
            self.available.put(conn)
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create and configure SQLite connection"""
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.timeout,
            check_same_thread=self.check_same_thread
        )
        
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        
        # Set reasonable timeouts
        conn.execute("PRAGMA busy_timeout=5000")  # 5 second timeout
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys=ON")
        
        return conn
    
    def get_connection(self, timeout: Optional[float] = None) -> sqlite3.Connection:
        """
        Get connection from pool with optional timeout
        
        Args:
            timeout: Override default timeout (seconds)
            
        Returns:
            SQLite connection
            
        Raises:
            queue.Empty: If no connection available within timeout
        """
        timeout = timeout or self.timeout
        
        try:
            conn = self.available.get(timeout=timeout)
            logger.debug("Connection acquired from pool")
            return conn
        except queue.Empty:
            logger.error(f"Connection pool exhausted (timeout={timeout}s)")
            raise ConnectionPoolExhausted(
                f"No connections available (timeout={timeout}s)"
            )
    
    def return_connection(self, conn: sqlite3.Connection):
        """
        Return connection to pool for reuse
        
        Args:
            conn: SQLite connection to return
        """
        if conn and conn in self.connections:
            self.available.put(conn)
            logger.debug("Connection returned to pool")
    
    def close_all(self):
        """Close all connections in pool"""
        with self.lock:
            for conn in self.connections:
                try:
                    conn.close()
                except:
                    pass
            self.connections.clear()
        logger.info("All connections closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_all()


class ConnectionPoolExhausted(Exception):
    """Raised when connection pool is exhausted"""
    pass


# Global pool instance
_pool = None

def init_pool(db_path: str = "retail.db", max_conn: int = 2):
    """Initialize global connection pool"""
    global _pool
    if _pool is None:
        _pool = SQLiteConnectionPool(db_path, max_connections=max_conn)
    return _pool

def get_pool() -> SQLiteConnectionPool:
    """Get global connection pool"""
    global _pool
    if _pool is None:
        _pool = init_pool()
    return _pool
```

**Usage in app.py**:
```python
from connection_pool import init_pool, get_pool

# Initialize at startup
pool = init_pool("retail.db", max_conn=2)

# Use in data loader
def load_customers():
    pool = get_pool()
    conn = pool.get_connection()
    try:
        df = pd.read_sql("SELECT * FROM customers", conn)
        return df
    finally:
        pool.return_connection(conn)

# Cleanup on exit
import atexit
atexit.register(lambda: get_pool().close_all())
```

**Tests**:
```python
def test_pool_initialization():
    """Test pool creates N connections"""
    pool = SQLiteConnectionPool(":memory:", max_connections=2)
    assert len(pool.connections) == 2
    pool.close_all()

def test_get_return_connection():
    """Test acquire and return"""
    pool = SQLiteConnectionPool(":memory:", max_connections=2)
    conn = pool.get_connection()
    assert conn is not None
    pool.return_connection(conn)
    pool.close_all()

def test_pool_exhaustion():
    """Test error on pool exhaustion"""
    pool = SQLiteConnectionPool(":memory:", max_connections=1)
    conn1 = pool.get_connection()
    with pytest.raises(ConnectionPoolExhausted):
        pool.get_connection(timeout=0.1)
    pool.close_all()

def test_wal_mode_enabled():
    """Test WAL mode is enabled"""
    pool = SQLiteConnectionPool(":memory:")
    conn = pool.get_connection()
    cursor = conn.cursor()
    mode = cursor.execute("PRAGMA journal_mode").fetchone()[0]
    assert mode.upper() == "WAL"
    pool.close_all()
```

---

### Component 2: Caching Layer (Hours 4-9)

**File**: `src/cache_manager.py`

```python
import json
import time
from typing import Any, Optional, Dict
from abc import ABC, abstractmethod
import logging

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


class RedisCache(CacheBackend):
    """Redis-backed cache"""
    
    def __init__(self, host: str = "localhost", port: int = 6379):
        """Initialize Redis cache"""
        try:
            import redis
            self.redis = redis.Redis(host=host, port=port, decode_responses=True)
            self.redis.ping()
            logger.info("Redis cache initialized")
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
    
    Caches:
    - RFM scores: 5 minutes
    - Apriori rules: 10 minutes
    - Product catalog: 1 hour
    - Customer list: 30 minutes
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
    
    # RFM Cache
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
        else:
            # Invalidate all RFM keys (implementation depends on backend)
            logger.info("RFM cache invalidated")
    
    # Apriori Cache
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
    
    # Product Catalog Cache
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
    
    # Customer List Cache
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
```

**Usage in app.py**:
```python
from cache_manager import init_cache, get_cache

# Initialize
cache = init_cache(backend="memory")

# Use in data loading
def load_rfm_data():
    cache = get_cache()
    
    # Try cache first
    cached = cache.get_rfm_scores("all")
    if cached:
        return cached
    
    # Load from DB
    rfm_data = calculate_rfm_for_customers(...)
    
    # Cache for 5 minutes
    cache.set_rfm_scores("all", rfm_data.to_dict('records'))
    
    return rfm_data

# Invalidate on data update
def sync_kiotviet_data():
    cache = get_cache()
    result = client.sync_to_sqlite()
    
    # Invalidate affected caches
    cache.invalidate_customers()
    cache.invalidate_products()
    cache.invalidate_rfm_scores()
    
    return result
```

**Tests**:
```python
def test_memory_cache_get_set():
    cache = MemoryCache()
    cache.set("key", "value", ttl=10)
    assert cache.get("key") == "value"

def test_cache_ttl_expiration():
    cache = MemoryCache()
    cache.set("key", "value", ttl=0)  # Instant expiry
    time.sleep(0.1)
    assert cache.get("key") is None

def test_cache_manager_rfm():
    manager = CacheManager(backend="memory")
    scores = {"R": 5, "F": 4, "M": 3}
    manager.set_rfm_scores("cust_001", scores)
    assert manager.get_rfm_scores("cust_001") == scores

def test_cache_invalidation():
    manager = CacheManager(backend="memory")
    manager.set_products([{"id": 1}])
    manager.invalidate_products()
    assert manager.get_products() is None
```

---

### Component 3: Rate Limiting (Hours 9-12)

**File**: `src/rate_limiter.py`

```python
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


class RateLimiter:
    """Rate limiter for APIs and endpoints"""
    
    def __init__(self):
        """Initialize rate limiter"""
        self.limiters: Dict[str, TokenBucket] = {}
        self._configure_limits()
    
    def _configure_limits(self):
        """Configure rate limits per endpoint"""
        # API rate limits
        self.limiters["kiotviet"] = TokenBucket(
            rate=100 / 60,  # 100 req/min
            capacity=10     # Allow burst of 10
        )
        
        self.limiters["zalo"] = TokenBucket(
            rate=50 / 60,   # 50 msg/min
            capacity=5      # Allow burst of 5
        )
        
        self.limiters["dashboard"] = TokenBucket(
            rate=1000 / 60, # 1000 req/min
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
        
        return {
            "tokens": limiter.tokens,
            "capacity": limiter.capacity,
            "rate": limiter.rate
        }


# Global rate limiter
_limiter = None

def get_limiter() -> RateLimiter:
    """Get global rate limiter"""
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter()
    return _limiter
```

**Usage**:
```python
from rate_limiter import get_limiter

limiter = get_limiter()

# Check before API call
if not limiter.check_limit("kiotviet"):
    st.warning("⚠️ Rate limit approaching - please wait")
    time.sleep(1)

# In Kiotviet client
def _make_request(self, ...):
    if not get_limiter().check_limit("kiotviet"):
        raise RateLimitExceeded()
    
    return super()._make_request(...)
```

---

### Component 4: Error Handling & Circuit Breaker (Hours 12-18)

**File**: `src/error_handling.py`

```python
import time
import logging
from enum import Enum
from typing import Callable, Any

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker for external APIs
    
    States:
    - CLOSED: normal operation
    - OPEN: fail fast, don't call external API
    - HALF_OPEN: test if API recovered
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: failures before opening
            recovery_timeout: seconds before half-open
            expected_exception: exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerError: If circuit is open
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker: HALF_OPEN")
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker open for {self.__class__.__name__}"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if recovery timeout elapsed"""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker: CLOSED (recovered)")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker OPEN: {self.failure_count} failures"
            )


class RetryWithBackoff:
    """Retry with exponential backoff"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry"""
        delay = self.initial_delay
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                    )
                    time.sleep(delay)
                    delay *= self.backoff_factor
                else:
                    logger.error(f"All {self.max_retries} attempts failed: {e}")
        
        raise last_exception
```

**Usage**:
```python
# In Kiotviet client
breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
retry = RetryWithBackoff(max_retries=3)

def get_customers(self):
    def fetch():
        return self._make_request("GET", "customers")
    
    try:
        return breaker.call(retry.call, fetch)
    except CircuitBreakerError:
        logger.error("Kiotviet API unavailable, using cached data")
        return load_cached_customers()
```

---

### Component 5: Structured Logging (Hours 18-22)

**File**: `src/logging_config.py`

```python
import logging
import json
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add custom fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        return json.dumps(log_data)


def configure_logging():
    """Configure structured logging"""
    
    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    
    # Console handler (JSON format)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(JSONFormatter())
    root.addHandler(console)
    
    # File handler (with rotation)
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(JSONFormatter())
    root.addHandler(file_handler)
    
    return root


# Initialize on import
logger = configure_logging()
```

**Usage**:
```python
import logging
from logging_config import configure_logging

logger = configure_logging()

# Log with context
logger.info("campaign_sent", extra={
    "campaign_id": "camp_001",
    "segment": "Champions",
    "count": 50
})

# Logs output as:
# {"timestamp": "2026-06-12T...", "level": "INFO", "message": "campaign_sent", 
#  "campaign_id": "camp_001", "segment": "Champions", "count": 50}
```

---

### Component 6: Configuration Management (Hours 22-24)

**File**: `.env.example`

```
# Database
DB_PATH=retail.db
DB_MAX_CONNECTIONS=2
DB_TIMEOUT=5
DB_WAL_MODE=true

# Cache
CACHE_BACKEND=memory  # or redis
CACHE_TTL_RFM=300
CACHE_TTL_APRIORI=600
CACHE_TTL_PRODUCTS=3600

# Rate Limiting
RATE_LIMIT_KIOTVIET=100
RATE_LIMIT_ZALO=50
RATE_LIMIT_DASHBOARD=1000

# Circuit Breaker
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60

# APIs
KIOTVIET_RETAIL_ID=your_retail_id
KIOTVIET_API_KEY=your_api_key
ZALO_ACCESS_TOKEN=your_zalo_token

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # or text
LOG_FILE=logs/app.log
LOG_MAX_SIZE=10485760  # 10MB

# Feature Flags
FEATURE_ZALO_CAMPAIGNS=true
FEATURE_CACHING=true
FEATURE_CIRCUIT_BREAKER=true
```

**Usage**:
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
DB_PATH = os.getenv("DB_PATH", "retail.db")
MAX_CONNECTIONS = int(os.getenv("DB_MAX_CONNECTIONS", "2"))
CACHE_BACKEND = os.getenv("CACHE_BACKEND", "memory")
```

---

## ✅ Testing Strategy

### Performance Tests (10+ tests)
```python
def test_cache_hit_rate():
    """Measure cache hit rate"""
    # Load same data 10 times
    # Expect > 80% cache hits

def test_connection_pool_performance():
    """Test pool doesn't bottleneck"""
    # 100 concurrent queries
    # Expect < 500ms response time

def test_rate_limiter_accuracy():
    """Test rate limiter enforcement"""
    # Make 150 requests in 60s (limit 100)
    # Expect some requests queued/rejected
```

### Reliability Tests (10+ tests)
```python
def test_circuit_breaker_opens():
    """Test breaker opens after failures"""
    # Mock 5 API failures
    # Verify circuit opens
    # Subsequent calls fail fast

def test_circuit_breaker_recovery():
    """Test breaker recovers"""
    # Open circuit
    # Wait recovery timeout
    # Mock successful API call
    # Verify circuit closes

def test_retry_with_backoff():
    """Test retry logic"""
    # Mock failing then succeeding call
    # Verify retried with backoff
    # Verify success on retry
```

### Security Tests (5+ tests)
```python
def test_no_sensitive_data_in_logs():
    """Verify passwords/tokens not logged"""
    # Log API request
    # Verify no API key in logs
    
def test_sql_injection_prevention():
    """Test parameterized queries"""
    # Attempt SQL injection
    # Verify prevented
```

---

## ✅ Acceptance Criteria

- [ ] Connection pool: max 2 concurrent connections
- [ ] WAL mode: enabled on SQLite
- [ ] Cache hit rate: > 80% for RFM scores
- [ ] Rate limiting: respected per endpoint
- [ ] Circuit breaker: opens on 5 failures
- [ ] Circuit breaker: recovers after 60 sec
- [ ] Retry: exponential backoff working
- [ ] Logs: JSON formatted, no sensitive data
- [ ] Logs: rotated at 10MB, keep 10 files
- [ ] Config: all options in .env.example
- [ ] Error handling: graceful degradation
- [ ] Performance: < 500ms response time
- [ ] 30+ reliability tests passing
- [ ] 10+ performance tests passing
- [ ] 5+ security tests passing

---

## 📊 Success Metrics

- Cache hit rate: > 80%
- API availability: > 99.5%
- Response time: < 500ms (p95)
- Error recovery time: < 60 sec
- Dashboard uptime: > 99%
- Support tickets: < 2/week

---

**Task Owner**: Development Team  
**Last Updated**: June 8, 2026  
**Version**: 1.0
