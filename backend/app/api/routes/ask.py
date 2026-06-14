from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.domain.schemas import AskRequest, AskResponse
from app.services.qa_service import QAService

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest, session: AsyncSession = Depends(get_session)):
    return await QAService().ask(session, payload.repo, payload.question, payload.top_k)
