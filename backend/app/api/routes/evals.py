import time
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.domain.schemas import EvalRunRequest, EvalRunResponse
from app.services.retrieval import RetrievalService

router = APIRouter()

@router.post("/run", response_model=EvalRunResponse)
async def run_eval(payload: EvalRunRequest, session: AsyncSession = Depends(get_session)):
    retrieval = RetrievalService()
    hits = 0
    latencies = []
    for sample in payload.samples:
        start = time.perf_counter()
        citations = await retrieval.retrieve(session, payload.repo, sample.question, payload.top_k)
        latencies.append((time.perf_counter() - start) * 1000)
        if any(sample.expected_file_contains.lower() in c.file_path.lower() for c in citations):
            hits += 1
    count = max(len(payload.samples), 1)
    recall = hits / count
    avg_latency = sum(latencies) / count
    await session.execute(
        text("INSERT INTO eval_runs(repo_name, recall_at_5, avg_latency_ms, sample_count) VALUES (:repo, :recall, :latency, :count)"),
        {"repo": payload.repo, "recall": recall, "latency": avg_latency, "count": len(payload.samples)},
    )
    await session.commit()
    return EvalRunResponse(recall_at_k=recall, avg_latency_ms=avg_latency, sample_count=len(payload.samples))
