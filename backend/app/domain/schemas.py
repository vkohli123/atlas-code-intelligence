from pydantic import BaseModel, Field

class IndexLocalRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    path: str = Field(..., description="Path visible inside the backend container")

class IndexGithubRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    repo_url: str
    branch: str = "main"

class RepoSummary(BaseModel):
    name: str
    source_url: str | None = None
    file_count: int
    chunk_count: int
    loc_count: int

class Citation(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    symbol_name: str | None = None
    score: float
    content_preview: str

class AskRequest(BaseModel):
    repo: str
    question: str = Field(..., min_length=2)
    top_k: int = Field(8, ge=1, le=20)

class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    latency_ms: int
    provider: str

class PRReviewRequest(BaseModel):
    repo: str
    diff: str = Field(..., min_length=5)
    top_k: int = Field(8, ge=1, le=20)

class PRFinding(BaseModel):
    severity: str
    title: str
    file_path: str | None = None
    line_hint: int | None = None
    rationale: str
    recommendation: str

class PRReviewResponse(BaseModel):
    summary: str
    findings: list[PRFinding]
    citations: list[Citation]
    latency_ms: int

class EvalQuestion(BaseModel):
    question: str
    expected_file_contains: str

class EvalRunRequest(BaseModel):
    repo: str
    samples: list[EvalQuestion]
    top_k: int = Field(5, ge=1, le=20)

class EvalRunResponse(BaseModel):
    recall_at_k: float
    avg_latency_ms: float
    sample_count: int
