#!/usr/bin/env bash
set -e
celery -A app.worker.celery_app.celery_app worker --loglevel=info
