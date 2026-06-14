CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS repositories (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    source_url TEXT,
    default_branch TEXT DEFAULT 'main',
    indexed_at TIMESTAMPTZ DEFAULT NOW(),
    file_count INTEGER DEFAULT 0,
    chunk_count INTEGER DEFAULT 0,
    loc_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS code_chunks (
    id BIGSERIAL PRIMARY KEY,
    repo_id BIGINT NOT NULL REFERENCES repositories(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    symbol_name TEXT,
    symbol_type TEXT,
    language TEXT,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    embedding vector(384),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    search_tsv tsvector GENERATED ALWAYS AS (
      setweight(to_tsvector('english', coalesce(file_path, '')), 'A') ||
      setweight(to_tsvector('english', coalesce(symbol_name, '')), 'A') ||
      setweight(to_tsvector('english', coalesce(content, '')), 'B')
    ) STORED
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_code_chunks_unique
ON code_chunks(repo_id, file_path, start_line, end_line, content_hash);

CREATE INDEX IF NOT EXISTS idx_code_chunks_repo ON code_chunks(repo_id);
CREATE INDEX IF NOT EXISTS idx_code_chunks_tsv ON code_chunks USING GIN(search_tsv);
CREATE INDEX IF NOT EXISTS idx_code_chunks_embedding_hnsw
ON code_chunks USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS query_logs (
    id BIGSERIAL PRIMARY KEY,
    repo_name TEXT NOT NULL,
    question TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    provider TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS eval_runs (
    id BIGSERIAL PRIMARY KEY,
    repo_name TEXT NOT NULL,
    recall_at_5 DOUBLE PRECISION NOT NULL,
    avg_latency_ms DOUBLE PRECISION NOT NULL,
    sample_count INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
