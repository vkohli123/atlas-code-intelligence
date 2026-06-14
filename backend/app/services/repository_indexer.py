import shutil
import subprocess
import tempfile
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.code_chunker import CodeChunker
from app.services.embeddings import get_embedding_provider, vector_literal
from app.observability.metrics import INDEXED_CHUNKS

class RepositoryIndexer:
    def __init__(self) -> None:
        self.chunker = CodeChunker()
        self.embedder = get_embedding_provider()

    async def index_local(self, session: AsyncSession, name: str, path: str, source_url: str | None = None) -> dict:
        repo_path = Path(path).resolve()
        if not repo_path.exists() or not repo_path.is_dir():
            raise ValueError(f"Repository path not found: {repo_path}")

        files = self.chunker.iter_files(repo_path)
        loc = 0
        chunks = []
        for file_path in files:
            text_content = file_path.read_text(encoding="utf-8", errors="ignore")
            loc += len(text_content.splitlines())
            chunks.extend(self.chunker.chunk_file(repo_path, file_path))

        repo_id = await self._upsert_repo(session, name, source_url, len(files), len(chunks), loc)
        await session.execute(text("DELETE FROM code_chunks WHERE repo_id = :repo_id"), {"repo_id": repo_id})

        for chunk in chunks:
            embedding = await self.embedder.embed(f"{chunk.file_path}\n{chunk.symbol_name or ''}\n{chunk.content}")
            await session.execute(
                text("""
                INSERT INTO code_chunks(repo_id, file_path, symbol_name, symbol_type, language, start_line, end_line, content, content_hash, embedding)
                VALUES (:repo_id, :file_path, :symbol_name, :symbol_type, :language, :start_line, :end_line, :content, :content_hash, CAST(:embedding AS vector))
                ON CONFLICT DO NOTHING
                """),
                {
                    "repo_id": repo_id,
                    "file_path": chunk.file_path,
                    "symbol_name": chunk.symbol_name,
                    "symbol_type": chunk.symbol_type,
                    "language": chunk.language,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "content": chunk.content,
                    "content_hash": chunk.content_hash,
                    "embedding": vector_literal(embedding),
                },
            )
        await session.commit()
        INDEXED_CHUNKS.labels(repo=name).set(len(chunks))
        return {"name": name, "files": len(files), "chunks": len(chunks), "loc": loc}

    async def index_github(self, session: AsyncSession, name: str, repo_url: str, branch: str = "main") -> dict:
        with tempfile.TemporaryDirectory(prefix="atlas_") as tmp:
            dest = Path(tmp) / "repo"
            cmd = ["git", "clone", "--depth", "1", "--branch", branch, repo_url, str(dest)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode != 0:
                # Retry without branch in case default branch is not main.
                cmd = ["git", "clone", "--depth", "1", repo_url, str(dest)]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                if result.returncode != 0:
                    raise ValueError(f"git clone failed: {result.stderr[:500]}")
            return await self.index_local(session, name=name, path=str(dest), source_url=repo_url)

    async def _upsert_repo(self, session: AsyncSession, name: str, source_url: str | None, file_count: int, chunk_count: int, loc_count: int) -> int:
        row = await session.execute(
            text("""
            INSERT INTO repositories(name, source_url, file_count, chunk_count, loc_count, indexed_at)
            VALUES (:name, :source_url, :file_count, :chunk_count, :loc_count, NOW())
            ON CONFLICT (name) DO UPDATE SET
              source_url = EXCLUDED.source_url,
              file_count = EXCLUDED.file_count,
              chunk_count = EXCLUDED.chunk_count,
              loc_count = EXCLUDED.loc_count,
              indexed_at = NOW()
            RETURNING id
            """),
            {
                "name": name,
                "source_url": source_url,
                "file_count": file_count,
                "chunk_count": chunk_count,
                "loc_count": loc_count,
            },
        )
        return int(row.scalar_one())
