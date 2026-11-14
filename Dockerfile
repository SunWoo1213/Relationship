# Refs: P9-infra D17 R14 R-U10D-1 R-U10D-9 원칙8 security
#
# 운영 배포 이미지(EC2 1대 + Docker Compose, D17). 단계 3개 — docker-compose.prod.yml 이
# `target:` 으로 골라 쓴다. 이미지에는 비밀 값이 없다(.dockerignore 가 .env 를 빌드 문맥에서 뺀다).
#
#   web-build  프론트를 빌드한다(node:24-slim). glibc 기반이라 ARM(t4g)에서도 npm 바이너리가 맞다.
#   caddy      빌드된 정적 파일(/srv)과 Caddyfile 을 담은 프록시 이미지.
#   backend    FastAPI 백엔드(python:3.13-slim, 비루트 사용자).

# ---------------------------------------------------------------------------
# 1) 프론트 빌드 — alpine(musl) 을 쓰지 않는다(01-plan 사실 8).
# ---------------------------------------------------------------------------
FROM node:24-slim AS web-build
WORKDIR /web
# 잠금 파일을 먼저 복사해 의존성 층을 캐시한다. devDependencies(tsc·vite)가 빌드에 필요하므로
# npm ci 앞에서 NODE_ENV=production 을 켜지 않는다.
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# ---------------------------------------------------------------------------
# 2) Caddy — 정적 서빙 + /api/* 접두 제거 프록시
# ---------------------------------------------------------------------------
FROM caddy:2-alpine AS caddy
COPY --from=web-build /web/dist /srv
COPY Caddyfile /etc/caddy/Caddyfile

# ---------------------------------------------------------------------------
# 3) 백엔드 — 실행에 필요한 것만 담는다(app·alembic·alembic.ini·requirements·entrypoint, 사실 9)
# ---------------------------------------------------------------------------
FROM python:3.13-slim AS backend
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY docker/entrypoint.sh ./docker/entrypoint.sh
# Windows 체크아웃으로 CRLF 가 들어와도 sh 가 깨지지 않게 CR 을 지운다(실행 비트 불필요 — sh 로 실행).
RUN sed -i 's/\r$//' /app/docker/entrypoint.sh \
    && useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin app
USER app
EXPOSE 8000
ENTRYPOINT ["sh", "/app/docker/entrypoint.sh"]
