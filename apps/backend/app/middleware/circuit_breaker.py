import time
from typing import Callable
from enum import Enum
from loguru import logger

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service is back


class CircuitBreaker:
    """Circuit breaker implementation for protecting services"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.success_count = 0
        self.half_open_threshold = 3

    def can_execute(self) -> bool:
        """Check if the circuit breaker allows execution"""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                logger.info(f"Circuit breaker {self.name} transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            return True

        return False

    def on_success(self):
        """Record a successful execution"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_threshold:
                logger.info(f"Circuit breaker {self.name} transitioning to CLOSED")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        else:
            self.failure_count = max(0, self.failure_count - 1)

    def on_failure(self):
        """Record a failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            logger.warning(f"Circuit breaker {self.name} transitioning to OPEN after {self.failure_count} failures")
            self.state = CircuitState.OPEN

    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "can_execute": self.can_execute()
        }


class WebSocketCircuitBreaker(CircuitBreaker):
    """Circuit breaker specifically for WebSocket operations"""

    def __init__(self):
        super().__init__(
            failure_threshold=3,
            recovery_timeout=30.0,
            expected_exception=Exception,
            name="websocket"
        )
        self.websocket_errors = 0
        self.last_websocket_error = 0

    def on_websocket_error(self):
        """Record a WebSocket-specific error"""
        self.websocket_errors += 1
        self.last_websocket_error = time.time()
        self.on_failure()

        # If WebSocket is failing too much, we might want to disable real-time features
        if self.websocket_errors >= 10:
            logger.error(f"WebSocket circuit breaker {self.name} has recorded {self.websocket_errors} errors")

    def reset_websocket_errors(self):
        """Reset WebSocket error count when connection is restored"""
        self.websocket_errors = 0
        logger.info(f"WebSocket circuit breaker {self.name} reset after successful connection")


# Global circuit breaker instances
websocket_circuit_breaker = WebSocketCircuitBreaker()
api_circuit_breaker = CircuitBreaker(
    failure_threshold=10,
    recovery_timeout=120.0,
    name="api"
)


class CircuitBreakerMiddleware(BaseHTTPMiddleware):
    """Middleware to implement circuit breaker pattern"""

    def __init__(self, app, websocket_cb: WebSocketCircuitBreaker = None, api_cb: CircuitBreaker = None):
        super().__init__(app)
        self.websocket_cb = websocket_cb or websocket_circuit_breaker
        self.api_cb = api_cb or api_circuit_breaker

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through circuit breaker"""

        # Check if this is a WebSocket endpoint
        is_websocket = request.url.path.startswith("/api/v1/ws")

        if is_websocket:
            # Use WebSocket circuit breaker
            if not self.websocket_cb.can_execute():
                logger.warning(f"WebSocket circuit breaker is OPEN, rejecting request to {request.url.path}")
                return Response(
                    content="WebSocket service temporarily unavailable",
                    status_code=503,
                    media_type="text/plain"
                )

            try:
                response = await call_next(request)
                self.websocket_cb.on_success()
                return response
            except Exception:
                self.websocket_cb.on_websocket_error()
                raise
        else:
            # Use API circuit breaker
            if not self.api_cb.can_execute():
                logger.warning(f"API circuit breaker is OPEN, rejecting request to {request.url.path}")
                return Response(
                    content="API service temporarily unavailable",
                    status_code=503,
                    media_type="text/plain"
                )

            try:
                response = await call_next(request)
                self.api_cb.on_success()
                return response
            except Exception:
                self.api_cb.on_failure()
                raise


def get_websocket_circuit_breaker() -> WebSocketCircuitBreaker:
    """Get the global WebSocket circuit breaker instance"""
    return websocket_circuit_breaker


def get_api_circuit_breaker() -> CircuitBreaker:
    """Get the global API circuit breaker instance"""
    return api_circuit_breaker


async def check_circuit_breaker_health() -> dict:
    """Check the health of all circuit breakers"""
    try:
        return {
            "websocket": websocket_circuit_breaker.get_state(),
            "api": api_circuit_breaker.get_state(),
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error checking circuit breaker health: {e}")
        return {
            "error": str(e),
            "timestamp": time.time()
        }


def reset_websocket_circuit_breaker():
    """Reset the WebSocket circuit breaker (useful for testing or manual recovery)"""
    websocket_circuit_breaker.state = CircuitState.CLOSED
    websocket_circuit_breaker.failure_count = 0
    websocket_circuit_breaker.websocket_errors = 0
    logger.info("WebSocket circuit breaker manually reset")


def reset_api_circuit_breaker():
    """Reset the API circuit breaker (useful for testing or manual recovery)"""
    api_circuit_breaker.state = CircuitState.CLOSED
    api_circuit_breaker.failure_count = 0
    logger.info("API circuit breaker manually reset")
