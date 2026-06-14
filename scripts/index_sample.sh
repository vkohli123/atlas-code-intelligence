#!/usr/bin/env bash
set -euo pipefail
curl -X POST http://localhost:8000/api/repos/index-local \
  -H 'Content-Type: application/json' \
  -d '{"name":"sample-service","path":"/app/examples/sample-service"}'
