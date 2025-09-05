import asyncio
import time
from typing import Callable
from contextlib import asynccontextmanager

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger



class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to handle request timeouts and prevent blocking"""

    def __init__(self, app, default_timeout: float = 30.0, max_timeout: float = 120.0):
        super().__init__(app)
        self.default_timeout = default_timeout
        self.max_timeout = max_timeout

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with timeout protection"""

        # Get timeout from request headers or use default
        timeout_header = request.headers.get("X-Timeout")
        if timeout_header:
            try:
                timeout = min(float(timeout_header), self.max_timeout)
            except ValueError:
                timeout = self.default_timeout
        else:
            timeout = self.default_timeout

        # Log request with timeout
        start_time = time.time()
        logger.debug(f"Request {request.method} {request.url.path} with timeout {timeout}s")

        try:
            # Execute request with timeout
            response = await asyncio.wait_for(
                call_next(request),
                timeout=timeout
            )

            # Log successful response
            duration = time.time() - start_time
            logger.debug(f"Request {request.method} {request.url.path} completed in {duration:.2f}s")

            # Add timing headers to response
            response.headers["X-Request-Duration"] = f"{duration:.3f}"
            response.headers["X-Request-Timeout"] = str(timeout)

            return response

        except asyncio.TimeoutError:
            # Handle timeout
            duration = time.time() - start_time
            logger.warning(f"Request {request.method} {request.url.path} timed out after {duration:.2f}s (limit: {timeout}s)")

            # Return timeout error response
            return Response(
                content=f"Request timed out after {timeout} seconds",
                status_code=408,
                media_type="text/plain",
                headers={
                    "X-Request-Duration": f"{duration:.3f}",
                    "X-Request-Timeout": str(timeout),
                    "X-Timeout-Reason": "Request exceeded timeout limit"
                }
            )

        except Exception as e:
            # Handle other errors
            duration = time.time() - start_time
            logger.error(f"Request {request.method} {request.url.path} failed after {duration:.2f}s: {e}")

            # Re-raise the exception for proper error handling
            raise


class RequestRateLimiter:
    """Rate limiter for preventing API abuse"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        current_time = time.time()

        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if current_time - req_time < self.window_seconds
            ]
        else:
            self.requests[client_id] = []

        # Check if limit exceeded
        if len(self.requests[client_id]) >= self.max_requests:
            return False

        # Add current request
        self.requests[client_id].append(current_time)
        return True


class ConcurrencyLimiter:
    """Limit concurrent requests to prevent resource exhaustion"""

    def __init__(self, max_concurrent: int = 50):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_requests = 0

    async def acquire(self):
        """Acquire permission to process request"""
        await self.semaphore.acquire()
        self.active_requests += 1

    def release(self):
        """Release permission after request processing"""
        self.semaphore.release()
        self.active_requests -= 1

    @property
    def current_load(self) -> float:
        """Get current load percentage"""
        return (self.active_requests / self.max_concurrent) * 100


# Global instances
rate_limiter = RequestRateLimiter()
concurrency_limiter = ConcurrencyLimiter()


class AdvancedTimeoutMiddleware(BaseHTTPMiddleware):
    """Advanced middleware with rate limiting and concurrency control"""

    def __init__(self, app, default_timeout: float = 30.0):
        super().__init__(app)
        self.default_timeout = default_timeout

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with advanced protection"""

        # Get client identifier
        client_id = self._get_client_id(request)

        # Check rate limiting
        if not rate_limiter.is_allowed(client_id):
            logger.warning(f"Rate limit exceeded for client {client_id}")
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=429,
                media_type="text/plain",
                headers={"Retry-After": str(rate_limiter.window_seconds)}
            )

        # Check concurrency limit
        if concurrency_limiter.current_load > 90:
            logger.warning(f"High concurrency load: {concurrency_limiter.current_load:.1f}%")

        # Acquire concurrency permission
        await concurrency_limiter.acquire()

        try:
            # Get timeout from request or use default
            timeout = self._get_request_timeout(request)

            # Execute request with timeout
            start_time = time.time()
            response = await asyncio.wait_for(
                call_next(request),
                timeout=timeout
            )

            # Add performance headers
            duration = time.time() - start_time
            response.headers.update({
                "X-Request-Duration": f"{duration:.3f}",
                "X-Request-Timeout": str(timeout),
                "X-Concurrency-Load": f"{concurrency_limiter.current_load:.1f}%"
            })

            return response

        except asyncio.TimeoutError:
            # Handle timeout
            duration = time.time() - start_time
            logger.warning(f"Request {request.method} {request.url.path} timed out after {duration:.2f}s")

            return Response(
                content=f"Request timed out after {timeout} seconds",
                status_code=408,
                media_type="text/plain",
                headers={
                    "X-Request-Duration": f"{duration:.3f}",
                    "X-Request-Timeout": str(timeout),
                    "X-Timeout-Reason": "Request exceeded timeout limit"
                }
            )

        except Exception as e:
            # Handle other errors
            duration = time.time() - start_time
            logger.error(f"Request {request.method} {request.url.path} failed after {duration:.2f}s: {e}")
            raise

        finally:
            # Always release concurrency permission
            concurrency_limiter.release()

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get from various sources
        client_id = (
            request.headers.get("X-Client-ID") or
            request.headers.get("X-Forwarded-For") or
            request.client.host if request.client else "unknown"
        )
        return str(client_id)

    def _get_request_timeout(self, request: Request) -> float:
        """Get timeout for request"""
        # Check for custom timeout in headers
        timeout_header = request.headers.get("X-Timeout")
        if timeout_header:
            try:
                return min(float(timeout_header), 120.0)  # Max 2 minutes
            except ValueError:
                pass

        # Check for specific endpoint timeouts
        path = request.url.path

        # Long-running operations get more time
        if "/ai/" in path or "/training/" in path:
            return 60.0
        elif "/export/" in path or "/import/" in path:
            return 120.0
        elif "/websocket" in path:
            return 30.0
        else:
            return self.default_timeout


# Context manager for timeout control
@asynccontextmanager
async def timeout_context(timeout: float, operation_name: str = "operation"):
    """Context manager for timeout control"""
    try:
        await asyncio.wait_for(
            asyncio.sleep(0),  # Yield control
            timeout=timeout
        )
        yield
    except asyncio.TimeoutError:
        logger.error(f"Operation {operation_name} timed out after {timeout}s")
        raise HTTPException(
            status_code=408,
            detail=f"Operation {operation_name} timed out after {timeout} seconds"
        )


# Utility functions for timeout management
def get_timeout_for_operation(operation_type: str) -> float:
    """Get appropriate timeout for operation type"""
    timeouts = {
        "database": 10.0,
        "api_call": 15.0,
        "ai_analysis": 60.0,
        "file_upload": 30.0,
        "websocket": 30.0,
        "background_task": 300.0,
        "default": 30.0
    }
    return timeouts.get(operation_type, timeouts["default"])


async def execute_with_timeout(func, *args, timeout: float = None, **kwargs):
    """Execute function with timeout protection"""
    if timeout is None:
        timeout = get_timeout_for_operation("default")

    try:
        return await asyncio.wait_for(
            func(*args, **kwargs),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.error(f"Function {func.__name__} timed out after {timeout}s")
        raise HTTPException(
            status_code=408,
            detail=f"Operation timed out after {timeout} seconds"
        )
