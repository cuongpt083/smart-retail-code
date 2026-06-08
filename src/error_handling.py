"""
Error Handling & Circuit Breaker - Protect system from cascading failures

Implements:
- Circuit breaker pattern
- Retry with exponential backoff
- Graceful degradation
"""

import time
import logging
from enum import Enum
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Fail fast
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """
    Circuit breaker for external APIs

    States:
    - CLOSED: normal operation, calls proceed
    - OPEN: fail fast, don't call external API
    - HALF_OPEN: test if API recovered
    """

    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker

        Args:
            name: Breaker name for logging
            failure_threshold: failures before opening
            recovery_timeout: seconds before half-open
            expected_exception: exception type to catch
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None

        logger.info(f"Circuit breaker '{name}' initialized")

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
                logger.info(f"Circuit breaker '{self.name}': HALF_OPEN")
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is OPEN"
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
            logger.info(f"Circuit breaker '{self.name}': CLOSED (recovered)")

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker '{self.name}' OPEN: "
                f"{self.failure_count} failures"
            )

    def get_state(self) -> str:
        """Get current state"""
        return self.state.value


class RetryWithBackoff:
    """Retry with exponential backoff"""

    def __init__(
        self,
        name: str = "default",
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0
    ):
        """
        Initialize retry strategy

        Args:
            name: Retry name for logging
            max_retries: maximum number of retries
            initial_delay: initial delay in seconds
            backoff_factor: multiply delay by this each retry
            max_delay: maximum delay between retries
        """
        self.name = name
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay

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
                    # Calculate delay with cap
                    actual_delay = min(delay, self.max_delay)

                    logger.warning(
                        f"[{self.name}] Attempt {attempt + 1} failed, "
                        f"retrying in {actual_delay}s: {type(e).__name__}"
                    )
                    time.sleep(actual_delay)
                    delay *= self.backoff_factor
                else:
                    logger.error(
                        f"[{self.name}] All {self.max_retries} attempts failed: "
                        f"{type(e).__name__}"
                    )

        raise last_exception


# Built-in circuit breakers
_circuit_breakers = {}

def get_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60
) -> CircuitBreaker:
    """Get or create circuit breaker"""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
    return _circuit_breakers[name]


def call_with_circuit_breaker(
    breaker_name: str,
    func: Callable,
    *args,
    **kwargs
) -> Any:
    """Call function with circuit breaker"""
    breaker = get_circuit_breaker(breaker_name)
    return breaker.call(func, *args, **kwargs)
