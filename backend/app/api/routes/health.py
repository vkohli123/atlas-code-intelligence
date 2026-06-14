from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health():
    return {"status": "ok", "env": settings.env, "llm_provider": settings.llm_provider, "embedding_provider": settings.embedding_provider}
