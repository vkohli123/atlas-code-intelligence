# Atlas Architecture

Atlas is built as a layered system.

## Layers

1. **Presentation:** Next.js dashboard.
2. **API:** FastAPI routes for indexing, ask, PR review, evals.
3. **Application services:** indexing service, retrieval service, PR review service.
4. **Domain models:** Repository, CodeChunk, RetrievalResult, PRFinding.
5. **Infrastructure:** Postgres/pgvector, Redis, LLM providers, embedding providers, Git client.

## Data flow: repo indexing

```text
GitHub/local path -> repository reader -> file filter -> code chunker -> embedding provider -> pgvector insert -> repo stats update
```

## Data flow: asking a question

```text
User question -> embed query -> hybrid retrieval -> prompt builder -> LLM provider -> answer + citations -> query log + metrics
```

## Data flow: PR review

```text
PR diff -> parse changed files/hunks -> retrieve nearby context -> deterministic checks + LLM review -> structured findings
```

## Production extensions

- Move indexing into a job queue.
- Add tenant/org isolation.
- Add GitHub App installation flow.
- Add AST parsing with tree-sitter per language.
- Add cross-encoder reranking.
- Add eval datasets per repository.
