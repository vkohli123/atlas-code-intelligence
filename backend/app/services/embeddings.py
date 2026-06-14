import hashlib
import math
from abc import ABC, abstractmethod
from app.core.config import settings

class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError

class HashEmbeddingProvider(EmbeddingProvider):
    """Deterministic local embedding provider for free demos.

    It is not semantically equivalent to a real embedding model, but it makes the
    whole system runnable without API keys and keeps pgvector paths exercised.
    """
    def __init__(self, dim: int = 384):
        self.dim = dim

    async def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        tokens = [t.strip().lower() for t in text.replace("_", " ").replace("-", " ").split() if t.strip()]
        if not tokens:
            tokens = [text[:64] or "empty"]
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for i, byte in enumerate(digest):
                idx = (byte + i * 31) % self.dim
                vec[idx] += 1.0 if i % 2 == 0 else -0.5
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model

    async def embed(self, text: str) -> list[float]:
        result = await self.client.embeddings.create(model=self.model, input=text[:12000], dimensions=settings.embedding_dim)
        return result.data[0].embedding

def get_embedding_provider() -> EmbeddingProvider:
    if settings.embedding_provider.lower() == "openai":
        return OpenAIEmbeddingProvider()
    return HashEmbeddingProvider(dim=settings.embedding_dim)

def vector_literal(vec: list[float]) -> str:
    return "[" + ",".join(f"{v:.8f}" for v in vec) + "]"
