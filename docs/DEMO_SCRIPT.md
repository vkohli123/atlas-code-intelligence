# Demo Script

## 30-second recruiter demo

1. Open http://localhost:3000.
2. Click **Index sample repo**.
3. Ask: `Where is authentication handled?`
4. Show the answer with file citations: `app/auth.py` and line ranges.
5. Open PR Review tab and click **Review PR**.
6. Show deterministic findings: missing timeout, missing tests, reliability risk.
7. Open http://localhost:8000/metrics and show Prometheus metrics.

## Interview talking points

- Why code chunking by symbol beats naive fixed-size chunking.
- How hybrid retrieval balances semantic recall and lexical precision.
- Why pgvector is good enough for a portfolio/MVP and when to migrate to Milvus/Pinecone.
- How the mock provider makes the system demoable without paid AI keys.
- How you would add GitHub App auth and push PR comments back to GitHub.
- How to measure retrieval quality using recall@k and answer faithfulness.
