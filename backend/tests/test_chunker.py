from pathlib import Path
from app.services.code_chunker import CodeChunker

def test_chunker_finds_python_symbols(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    f = repo / "main.py"
    f.write_text("class AuthService:\n    pass\n\ndef login():\n    return True\n", encoding="utf-8")
    chunks = CodeChunker().chunk_file(repo, f)
    names = {c.symbol_name for c in chunks}
    assert "AuthService" in names
    assert "login" in names
