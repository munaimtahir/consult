#!/usr/bin/env bash
set -euo pipefail

PROJECT="consult"
docker compose -p "$PROJECT" restart
