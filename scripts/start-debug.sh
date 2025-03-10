#!/usr/bin/env bash

set -e

DEFAULT_MODULE_NAME=src.main

MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
LOG_LEVEL=${LOG_LEVEL:-info}
LOG_CONFIG=${LOG_CONFIG:-/src/logging.ini}
# Running Migrations
alembic upgrade head
# Start Uvicorn with live reload
python /tmp/debugpy --wait-for-client --listen 0.0.0.0:5678 -m uvicorn --reload --proxy-headers --host $HOST --port $PORT --log-config $LOG_CONFIG "$APP_MODULE"