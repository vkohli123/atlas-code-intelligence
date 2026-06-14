import re
import time
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.schemas import PRReviewResponse
from app.observability.metrics import PR_FINDINGS
from app.services.llm import get_llm_provider
from app.services.retrieval import RetrievalService

class PRReviewService:
    def __init__(self) -> None:
        self.retrieval = RetrievalService()
        self.llm = get_llm_provider()

    async def review(self, session: AsyncSession, repo_name: str, diff: str, top_k: int) -> PRReviewResponse:
        start = time.perf_counter()
        query = self._diff_to_query(diff)
        citations = await self.retrieval.retrieve(session, repo_name, query, top_k=top_k)
        summary, findings = await self.llm.review_pr(diff, citations)
        latency_ms = int((time.perf_counter() - start) * 1000)
        for finding in findings:
            PR_FINDINGS.labels(repo=repo_name, severity=finding.severity).inc()
        return PRReviewResponse(summary=summary, findings=findings, citations=citations, latency_ms=latency_ms)

    def _diff_to_query(self, diff: str) -> str:
        files = re.findall(r"\+\+\+ b/(.+)", diff)
        added = "\n".join(line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
        return " ".join(files[:10]) + "\n" + added[:2000]
