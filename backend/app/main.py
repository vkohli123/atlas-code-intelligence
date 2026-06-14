from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api.routes import ask, evals, health, pr_review, repos
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware import RequestMetricsMiddleware, SimpleRateLimitMiddleware
from app.db.session import init_db

configure_logging()

app = FastAPI(
    title="Atlas API",
    description="AI codebase intelligence and PR review agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestMetricsMiddleware)
app.add_middleware(SimpleRateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)

app.include_router(health.router)
app.include_router(repos.router, prefix="/api/repos", tags=["repositories"])
app.include_router(ask.router, prefix="/api", tags=["ask"])
app.include_router(pr_review.router, prefix="/api", tags=["pr-review"])
app.include_router(evals.router, prefix="/api/evals", tags=["evals"])

app.mount("/metrics", make_asgi_app())

@app.on_event("startup")
async def startup() -> None:
    await init_db()
