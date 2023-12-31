#!/bin/bash

set -e

# activate our virtual environment here
#. /opt/pysetup/.venv/bin/activate

WORKERS=${WORKERS:-1}
LOG_LEVEL=${LOG_LEVEL:-INFO}

usage() {
  echo "Usage: $0 [celery|fastapi]"
  echo "  - fastapi: start the fastapi server"
  echo "  - celery: start the celery worker"
}

if [[ "$1" == "celery" ]]; then
  celery --app=src.worker.celery_app worker --concurrency=$WORKERS --loglevel=$LOG_LEVEL
elif [[ "$1" == "fastapi" ]]; then
  # change to 1 process per container with uvicorn later if doing cluster level
  # https://fastapi.tiangolo.com/deployment/docker/#one-process-per-container
  gunicorn --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 -w $WORKERS main:app --log-level $LOG_LEVEL --timeout 300
elif [[ "$1" == "dashboard" ]]; then
  celery --broker=$REDIS_URL flower --port=5555
else
  echo "Unknown or missing sub-command: '$1'"
  usage
  exit 1
fi