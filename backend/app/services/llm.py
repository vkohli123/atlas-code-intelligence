from abc import ABC, abstractmethod
from app.core.config import settings
from app.domain.schemas import Citation, PRFinding

class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def answer(self, question: str, citations: list[Citation]) -> str:
        raise NotImplementedError

    @abstractmethod
    async def review_pr(self, diff: str, citations: list[Citation]) -> tuple[str, list[PRFinding]]:
        raise NotImplementedError

class MockLLMProvider(LLMProvider):
    name = "mock"

    async def answer(self, question: str, citations: list[Citation]) -> str:
        if not citations:
            return "I could not find relevant code context for this question."
        lines = [f"Atlas found {len(citations)} relevant code regions for: '{question}'."]
        top = citations[:4]
        for i, c in enumerate(top, start=1):
            symbol = f" `{c.symbol_name}`" if c.symbol_name else ""
            lines.append(f"[{i}] `{c.file_path}` lines {c.start_line}-{c.end_line}{symbol}: {c.content_preview}")
        lines.append("\nUse these cited files as the starting point for implementation or debugging.")
        return "\n".join(lines)

    async def review_pr(self, diff: str, citations: list[Citation]) -> tuple[str, list[PRFinding]]:
        findings: list[PRFinding] = []
        lower = diff.lower()
        if "timeout" not in lower and ("requests." in lower or "httpx" in lower or "fetch(" in lower):
            findings.append(PRFinding(
                severity="high",
                title="Network call may lack an explicit timeout",
                file_path=None,
                line_hint=None,
                rationale="External calls without timeouts can hang workers and degrade p95/p99 latency.",
                recommendation="Add a bounded timeout, retry policy, and circuit-breaker/fallback behavior."
            ))
        if "test" not in lower and ("+def " in diff or "+export " in diff or "+async " in diff):
            findings.append(PRFinding(
                severity="medium",
                title="Missing tests for changed behavior",
                file_path=None,
                line_hint=None,
                rationale="The diff appears to add behavior without adding unit or integration coverage.",
                recommendation="Add tests covering success, failure, and edge cases."
            ))
        if "except exception" in lower or "catch (e" in lower:
            findings.append(PRFinding(
                severity="medium",
                title="Broad exception handling may hide failures",
                file_path=None,
                line_hint=None,
                rationale="Broad catches can mask production bugs and make observability weaker.",
                recommendation="Catch specific exceptions, log structured context, and return typed errors."
            ))
        if "select *" in lower:
            findings.append(PRFinding(
                severity="medium",
                title="Avoid SELECT * in production queries",
                file_path=None,
                line_hint=None,
                rationale="SELECT * increases payload size and couples code to schema changes.",
                recommendation="Select explicit columns and add query tests for expected fields."
            ))
        if not findings:
            findings.append(PRFinding(
                severity="low",
                title="No critical deterministic issues found",
                file_path=citations[0].file_path if citations else None,
                line_hint=citations[0].start_line if citations else None,
                rationale="Static heuristics did not detect obvious issues; LLM mode can provide deeper semantic review.",
                recommendation="Run integration tests and review related modules cited by Atlas."
            ))
        summary = f"Reviewed diff with {len(citations)} retrieved context regions and produced {len(findings)} findings."
        return summary, findings

class OpenAILLMProvider(LLMProvider):
    name = "openai"

    def __init__(self) -> None:
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def answer(self, question: str, citations: list[Citation]) -> str:
        context = "\n\n".join(
            f"[{i}] {c.file_path}:{c.start_line}-{c.end_line}\n{c.content_preview}"
            for i, c in enumerate(citations, start=1)
        )
        messages = [
            {"role": "system", "content": "You are Atlas. Answer using only supplied code context. Cite file paths and lines."},
            {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"},
        ]
        res = await self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.1)
        return res.choices[0].message.content or "No answer generated."

    async def review_pr(self, diff: str, citations: list[Citation]) -> tuple[str, list[PRFinding]]:
        context = "\n\n".join(
            f"{c.file_path}:{c.start_line}-{c.end_line}\n{c.content_preview}"
            for c in citations[:8]
        )
        prompt = f"""
Review this PR diff like a senior staff engineer. Find bugs, missing tests, security risks, reliability risks, and design issues.
Return concise bullets.

DIFF:
{diff[:12000]}

RELATED CONTEXT:
{context}
"""
        res = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        text = res.choices[0].message.content or "No findings."
        finding = PRFinding(
            severity="medium",
            title="LLM review output",
            rationale=text[:900],
            recommendation="Review the generated feedback and apply relevant fixes.",
        )
        return "LLM review completed.", [finding]

def get_llm_provider() -> LLMProvider:
    if settings.llm_provider.lower() == "openai":
        return OpenAILLMProvider()
    return MockLLMProvider()
