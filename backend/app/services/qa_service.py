import time
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.schemas import AskResponse
from app.domain.schemas import Citation
from app.observability.metrics import CACHE_EVENTS, QUERY_LATENCY
from app.services.cache import AnswerCache
from app.services.llm import get_llm_provider
from app.services.retrieval import RetrievalService

class QAService:
    def __init__(self) -> None:
        self.retrieval = RetrievalService()
        self.llm = get_llm_provider()
        self.cache = AnswerCache()

    async def ask(self, session: AsyncSession, repo_name: str, question: str, top_k: int) -> AskResponse:
        start = time.perf_counter()
        cached = await self.cache.get(repo_name, question, top_k)
        if cached:
            CACHE_EVENTS.labels(event="hit").inc()
            citations = [Citation(**c) for c in cached["citations"]]
            return AskResponse(answer=cached["answer"], citations=citations, latency_ms=0, provider=f"{self.llm.name}:cache")
        CACHE_EVENTS.labels(event="miss").inc()
        citations = await self.retrieval.retrieve(session, repo_name, question, top_k=top_k)
        answer = await self.llm.answer(question, citations)
        latency_ms = int((time.perf_counter() - start) * 1000)
        await session.execute(
            text("INSERT INTO query_logs(repo_name, question, latency_ms, provider) VALUES (:repo, :question, :latency, :provider)"),
            {"repo": repo_name, "question": question, "latency": latency_ms, "provider": self.llm.name},
        )
        await session.commit()
        QUERY_LATENCY.labels(repo=repo_name).observe(latency_ms / 1000)
        response = AskResponse(answer=answer, citations=citations, latency_ms=latency_ms, provider=self.llm.name)
        await self.cache.set(repo_name, question, top_k, response.model_dump())
        return response
