#!/usr/bin/env bash
set -euo pipefail

: "${STORAGE_DIR:=/app/storage}"
: "${OUTPUT_DIR:=/app/storage/outputs}"
: "${CHECKPOINTS_DIR:=/app/checkpoints_v2}"

echo "[openvoice-worker] Starting service"
echo "[openvoice-worker] STORAGE_DIR=${STORAGE_DIR}"
echo "[openvoice-worker] OUTPUT_DIR=${OUTPUT_DIR}"
echo "[openvoice-worker] CHECKPOINTS_DIR=${CHECKPOINTS_DIR}"

mkdir -p "${OUTPUT_DIR}"

if [ ! -d "${CHECKPOINTS_DIR}" ]; then
  echo "[openvoice-worker] WARNING: checkpoints directory not found at ${CHECKPOINTS_DIR}"
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8001
