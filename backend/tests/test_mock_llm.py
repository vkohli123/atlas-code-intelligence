import pytest
from app.domain.schemas import Citation
from app.services.llm import MockLLMProvider

@pytest.mark.asyncio
async def test_mock_llm_answer_contains_citation():
    llm = MockLLMProvider()
    ans = await llm.answer("where is auth?", [Citation(file_path="auth.py", start_line=1, end_line=5, symbol_name="AuthService", score=0.9, content_preview="class AuthService")])
    assert "auth.py" in ans
    assert "AuthService" in ans
