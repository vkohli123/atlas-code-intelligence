import time
from collections import defaultdict, deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from app.core.config import settings
from app.observability.metrics import REQUEST_COUNT, REQUEST_LATENCY

class RequestMetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        latency = time.perf_counter() - start
        REQUEST_COUNT.labels(method=request.method, path=request.url.path, status=str(response.status_code)).inc()
        REQUEST_LATENCY.labels(method=request.method, path=request.url.path).observe(latency)
        return response

class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path in {"/metrics", "/health"} or request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
            return await call_next(request)
        if settings.require_api_key and request.headers.get("x-api-key") != settings.api_key:
            return JSONResponse({"detail": "invalid or missing x-api-key"}, status_code=401)
        now = time.time()
        key = request.client.host if request.client else "unknown"
        window = self.hits[key]
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= self.requests_per_minute:
            return JSONResponse({"detail": "rate limit exceeded"}, status_code=429)
        window.append(now)
        return await call_next(request)
