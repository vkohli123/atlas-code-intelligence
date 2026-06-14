#!/usr/bin/env bash
set -euo pipefail
curl -X POST http://localhost:8000/api/ask \
  -H 'Content-Type: application/json' \
  -d '{"repo":"sample-service","question":"Where is authentication handled?"}' | python -m json.tool
