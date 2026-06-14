from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter("atlas_http_requests_total", "HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("atlas_http_request_duration_seconds", "HTTP latency", ["method", "path"])
QUERY_LATENCY = Histogram("atlas_query_duration_seconds", "Ask endpoint latency", ["repo"])
RETRIEVAL_LATENCY = Histogram("atlas_retrieval_duration_seconds", "Retrieval latency", ["repo"])
INDEXED_CHUNKS = Gauge("atlas_indexed_chunks", "Indexed chunks", ["repo"])
PR_FINDINGS = Counter("atlas_pr_findings_total", "PR findings", ["repo", "severity"])

CACHE_EVENTS = Counter("atlas_cache_events_total", "Cache events", ["event"])
