from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.domain.schemas import IndexGithubRequest, IndexLocalRequest, RepoSummary
from app.services.repository_indexer import RepositoryIndexer

router = APIRouter()

@router.get("", response_model=list[RepoSummary])
async def list_repos(session: AsyncSession = Depends(get_session)):
    rows = await session.execute(text("SELECT name, source_url, file_count, chunk_count, loc_count FROM repositories ORDER BY indexed_at DESC"))
    return [RepoSummary(name=r.name, source_url=r.source_url, file_count=r.file_count, chunk_count=r.chunk_count, loc_count=r.loc_count) for r in rows]

@router.post("/index-local")
async def index_local(payload: IndexLocalRequest, session: AsyncSession = Depends(get_session)):
    try:
        return await RepositoryIndexer().index_local(session, payload.name, payload.path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.post("/index-github")
async def index_github(payload: IndexGithubRequest, session: AsyncSession = Depends(get_session)):
    try:
        return await RepositoryIndexer().index_github(session, payload.name, payload.repo_url, payload.branch)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
