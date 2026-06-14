import time
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.schemas import Citation
from app.observability.metrics import RETRIEVAL_LATENCY
from app.services.embeddings import get_embedding_provider, vector_literal

class RetrievalService:
    def __init__(self) -> None:
        self.embedder = get_embedding_provider()

    async def retrieve(self, session: AsyncSession, repo_name: str, query: str, top_k: int = 8) -> list[Citation]:
        start = time.perf_counter()
        try:
            repo_id_row = await session.execute(text("SELECT id FROM repositories WHERE name = :name"), {"name": repo_name})
            repo_id = repo_id_row.scalar_one_or_none()
            if repo_id is None:
                return []
            qvec = await self.embedder.embed(query)
            rows = await session.execute(
                text("""
                WITH ranked AS (
                  SELECT
                    file_path,
                    symbol_name,
                    start_line,
                    end_line,
                    content,
                    (1 - (embedding <=> CAST(:embedding AS vector))) AS vector_score,
                    ts_rank_cd(search_tsv, websearch_to_tsquery('english', :query)) AS text_score
                  FROM code_chunks
                  WHERE repo_id = :repo_id
                )
                SELECT *,
                  ((0.72 * vector_score) + (0.28 * COALESCE(text_score, 0))) AS score
                FROM ranked
                ORDER BY score DESC
                LIMIT :top_k
                """),
                {"repo_id": repo_id, "embedding": vector_literal(qvec), "query": query, "top_k": top_k},
            )
            citations = []
            for r in rows.mappings().all():
                preview = " ".join(str(r["content"]).split())[:420]
                citations.append(Citation(
                    file_path=r["file_path"],
                    start_line=r["start_line"],
                    end_line=r["end_line"],
                    symbol_name=r["symbol_name"],
                    score=float(r["score"] or 0.0),
                    content_preview=preview,
                ))
            return citations
        finally:
            RETRIEVAL_LATENCY.labels(repo=repo_name).observe(time.perf_counter() - start)
