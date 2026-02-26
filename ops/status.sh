#!/usr/bin/env bash
set -euo pipefail

PROJECT="consult"
docker ps --filter "label=com.docker.compose.project=$PROJECT"
