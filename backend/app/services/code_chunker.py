from dataclasses import dataclass
import hashlib
import re
from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".java", ".cs", ".rb", ".rs", ".md", ".yml", ".yaml", ".json", ".sql"
}

IGNORE_DIRS = {".git", "node_modules", ".next", "dist", "build", "coverage", "__pycache__", ".venv", "venv"}

LANG_BY_EXT = {
    ".py": "python", ".ts": "typescript", ".tsx": "typescript-react", ".js": "javascript", ".jsx": "javascript-react",
    ".go": "go", ".java": "java", ".cs": "csharp", ".rb": "ruby", ".rs": "rust", ".md": "markdown",
    ".yml": "yaml", ".yaml": "yaml", ".json": "json", ".sql": "sql"
}

SYMBOL_PATTERNS = [
    re.compile(r"^\s*(?:async\s+)?def\s+(?P<name>[A-Za-z_][\w]*)\s*\("),
    re.compile(r"^\s*class\s+(?P<name>[A-Za-z_][\w]*)"),
    re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(?P<name>[A-Za-z_][\w]*)\s*\("),
    re.compile(r"^\s*(?:export\s+)?const\s+(?P<name>[A-Za-z_][\w]*)\s*=\s*(?:async\s*)?\("),
    re.compile(r"^\s*func\s+(?P<name>[A-Za-z_][\w]*)\s*\("),
    re.compile(r"^\s*(?:public|private|protected|internal|static|async|final|sealed|override|virtual|\s)+\s*[\w<>\[\]]+\s+(?P<name>[A-Za-z_][\w]*)\s*\("),
]

@dataclass(frozen=True)
class CodeChunk:
    file_path: str
    symbol_name: str | None
    symbol_type: str | None
    language: str
    start_line: int
    end_line: int
    content: str
    content_hash: str

class CodeChunker:
    def __init__(self, max_lines: int = 90, overlap_lines: int = 12):
        self.max_lines = max_lines
        self.overlap_lines = overlap_lines

    def iter_files(self, repo_path: Path) -> list[Path]:
        files: list[Path] = []
        for p in repo_path.rglob("*"):
            if not p.is_file():
                continue
            if any(part in IGNORE_DIRS for part in p.parts):
                continue
            if p.suffix.lower() in SUPPORTED_EXTENSIONS and p.stat().st_size < 512_000:
                files.append(p)
        return sorted(files)

    def chunk_file(self, root: Path, path: Path) -> list[CodeChunk]:
        rel = str(path.relative_to(root)).replace("\\", "/")
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        language = LANG_BY_EXT.get(path.suffix.lower(), "text")
        if not lines:
            return []

        symbol_starts: list[tuple[int, str, str]] = []
        for idx, line in enumerate(lines, start=1):
            for pat in SYMBOL_PATTERNS:
                match = pat.match(line)
                if match:
                    symbol_starts.append((idx, match.group("name"), "symbol"))
                    break

        chunks: list[CodeChunk] = []
        if symbol_starts:
            for i, (start, name, typ) in enumerate(symbol_starts):
                end = symbol_starts[i + 1][0] - 1 if i + 1 < len(symbol_starts) else len(lines)
                if end - start + 1 > self.max_lines:
                    chunks.extend(self._window_chunks(rel, language, lines, start, end, name, typ))
                else:
                    content = "\n".join(lines[start - 1:end])
                    chunks.append(self._make(rel, language, start, end, content, name, typ))
        else:
            chunks.extend(self._window_chunks(rel, language, lines, 1, len(lines), None, "file"))
        return chunks

    def _window_chunks(self, rel: str, language: str, lines: list[str], start: int, end: int, symbol: str | None, typ: str | None) -> list[CodeChunk]:
        chunks: list[CodeChunk] = []
        cur = start
        while cur <= end:
            win_end = min(cur + self.max_lines - 1, end)
            content = "\n".join(lines[cur - 1:win_end])
            chunks.append(self._make(rel, language, cur, win_end, content, symbol, typ))
            if win_end == end:
                break
            cur = max(cur + self.max_lines - self.overlap_lines, cur + 1)
        return chunks

    def _make(self, rel: str, language: str, start: int, end: int, content: str, symbol: str | None, typ: str | None) -> CodeChunk:
        h = hashlib.sha256(f"{rel}:{start}:{end}:{content}".encode("utf-8")).hexdigest()
        return CodeChunk(rel, symbol, typ, language, start, end, content, h)
