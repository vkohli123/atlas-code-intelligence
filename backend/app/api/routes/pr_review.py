from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.domain.schemas import PRReviewRequest, PRReviewResponse
from app.services.pr_review_service import PRReviewService

router = APIRouter()

@router.post("/pr-review", response_model=PRReviewResponse)
async def pr_review(payload: PRReviewRequest, session: AsyncSession = Depends(get_session)):
    return await PRReviewService().review(session, payload.repo, payload.diff, payload.top_k)
