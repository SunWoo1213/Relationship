#!/bin/sh
# Refs: P9-infra D17 R-U10D-4 R-U10D-9 S3.6
#
# 백엔드 컨테이너 진입점. 마이그레이션을 먼저 하고 서버를 띄운다.
# `set -e` 라서 마이그레이션이 실패하면 컨테이너가 죽는다(`docker compose ps` 에 Exited/재시작으로 보인다).
# 워커는 1개로 고정한다 — 1분 브리핑 스케줄러가 워커마다 lifespan 에서 뜨므로(app/main.py)
# 2개 이상이면 같은 일정을 두 번 브리핑할 수 있다(R-U10D-9).
set -eu

python -m alembic upgrade head
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
