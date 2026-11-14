"""Refs: P9-infra D17 R14 R-U10D-1 R-U10D-2 R-U10D-4 R-U10D-5 R-U10D-9 원칙8 security -- 운영 배포 파일 텍스트 검사.

`Dockerfile`·`docker/entrypoint.sh`·`docker-compose.prod.yml`·`Caddyfile`·`.dockerignore`·`.env.example`
의 계약 값을 **텍스트로** 단언한다. DB·Docker·PyYAML 이 필요 없고(skip 0), 파일만 읽는다.

번호 ①~⑮ 는 `docs/wiki/packages/P9-infra/01-plan.md` U1 "테스트" 항목의 번호다.
변이 시험(V1-1~V1-15)은 이 파일과 배포 파일을 스크래치패드 사본에 복사해 한 줄씩 어긋나게 만든 뒤
돌린다 -- 그래서 저장소 루트는 이 파일 위치(`<루트>/tests/`)에서 계산한다.

compose 서비스 블록은 들여쓰기로 잘라 본다(`services:` 아래 2칸 들여쓴 키). 주석 줄은 값 검사에서 뺀다.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMPOSE = "docker-compose.prod.yml"
CADDYFILE = "Caddyfile"
DOCKERFILE = "Dockerfile"
ENTRYPOINT = "docker/entrypoint.sh"
DOCKERIGNORE = ".dockerignore"
ENV_EXAMPLE = ".env.example"

SERVICES = ("caddy", "backend", "postgres")


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _code_lines(text: str) -> list[str]:
    """주석(`#` 로 시작하는 줄)과 빈 줄을 뺀 줄 목록. 줄 끝 공백은 지운다."""
    out = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        out.append(line.rstrip())
    return out


def _code_text(relpath: str) -> str:
    return "\n".join(_code_lines(_read(relpath)))


def _service_blocks(compose_text: str) -> dict[str, str]:
    """`services:` 아래 서비스를 이름 → 블록 본문(주석 제외)으로 자른다.

    서비스 키는 정확히 2칸 들여쓴 `name:` 줄이고, 블록은 다음 2칸 키(또는 들여쓰기 0 키) 직전까지다.
    """
    lines = _code_lines(compose_text)
    blocks: dict[str, list[str]] = {}
    in_services = False
    current: str | None = None
    for line in lines:
        if re.match(r"^services:\s*$", line):
            in_services = True
            current = None
            continue
        if in_services and re.match(r"^\S", line):  # 들여쓰기 0 키 → services 끝
            in_services = False
            current = None
            continue
        if not in_services:
            continue
        m = re.match(r"^ {2}([A-Za-z0-9_-]+):\s*$", line)
        if m:
            current = m.group(1)
            blocks[current] = []
            continue
        if current is not None:
            blocks[current].append(line)
    return {name: "\n".join(body) for name, body in blocks.items()}


def _top_level_volumes(compose_text: str) -> set[str]:
    """들여쓰기 0 의 `volumes:` 아래 2칸 키 이름 집합."""
    lines = _code_lines(compose_text)
    names: set[str] = set()
    in_vol = False
    for line in lines:
        if re.match(r"^volumes:\s*$", line):
            in_vol = True
            continue
        if in_vol and re.match(r"^\S", line):
            in_vol = False
        if in_vol:
            m = re.match(r"^ {2}([A-Za-z0-9_-]+):", line)
            if m:
                names.add(m.group(1))
    return names


def _brace_block(text: str, header_regex: str) -> str:
    """`header_regex` 로 시작해 `{` 로 여는 블록의 중괄호 안쪽 본문을 돌려준다(없으면 빈 문자열)."""
    m = re.search(header_regex + r"\s*\{", text)
    if not m:
        return ""
    depth = 1
    i = m.end()
    start = i
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start : i - 1]


# --- 비밀 탐지 패턴: secret-guard.sh 의 비밀 패턴과 같은 의미(⑥) ---------------------------------
_PEM = "-----BEGIN " + "[A-Z ]*" + "PRIVATE KEY-----"
SECRET_PATTERNS: dict[str, str] = {
    "openai-anthropic-key": r"sk-(proj-|ant-)?[A-Za-z0-9_-]{24,}",
    "pem-private-key": _PEM,
    "db-url-with-password": r"postgres(ql)?://[^:/\s]+:[^@\s]{8,}@",
    "long-alnum-chunk": r"[A-Za-z0-9]{32,}",
}


def _secret_hits(text: str) -> list[str]:
    return [name for name, pat in SECRET_PATTERNS.items() if re.search(pat, text)]


# ① -------------------------------------------------------------------------------------------
def test_compose_project_name_is_relationship_prod():
    """① 최상위 `name: relationship-prod` — 개발 볼륨(capstone2·relationship)과 섞이지 않는 유일한 방어."""
    text = _read(COMPOSE)
    assert re.search(r"^name:\s*relationship-prod\s*$", text, re.M)


# ② -------------------------------------------------------------------------------------------
def test_compose_has_three_services():
    """② 서비스 caddy·backend·postgres 셋 다 있다(그 밖의 서비스는 없다)."""
    blocks = _service_blocks(_read(COMPOSE))
    assert set(blocks) == set(SERVICES)


# ③ -------------------------------------------------------------------------------------------
def test_postgres_has_no_host_ports():
    """③ postgres 는 호스트 포트를 노출하지 않는다(D17 3, S17)."""
    block = _service_blocks(_read(COMPOSE))["postgres"]
    assert not re.search(r"^\s*ports:", block, re.M)


# ④ -------------------------------------------------------------------------------------------
def test_backend_has_no_host_ports():
    """④ backend 도 호스트 포트가 없다 — caddy 만 backend:8000 으로 프록시한다."""
    block = _service_blocks(_read(COMPOSE))["backend"]
    assert not re.search(r"^\s*ports:", block, re.M)


# ⑤ -------------------------------------------------------------------------------------------
def test_env_file_only_on_backend():
    """⑤ postgres 에는 env_file 0(앱 비밀을 DB 컨테이너에 안 줌), backend 에는 정확히 1."""
    blocks = _service_blocks(_read(COMPOSE))
    assert len(re.findall(r"^\s*env_file:", blocks["postgres"], re.M)) == 0
    assert len(re.findall(r"^\s*env_file:", blocks["backend"], re.M)) == 1
    assert len(re.findall(r"^\s*env_file:", blocks["caddy"], re.M)) == 0


# ⑥ -------------------------------------------------------------------------------------------
def test_secret_detector_catches_samples():
    """⑥(전제) 비밀 탐지기가 실제로 잡는다 — 항상 통과하는 검사가 아님을 보인다. 표본은 조각을 이어 만든다."""
    key = "sk-" + "proj-" + "a" * 30
    pem = "-----BEGIN " + "RSA " + "PRIVATE KEY-----"
    dburl = "postgresql://" + "user:" + "longpassword1" + "@db:5432/x"
    chunk = "A1" * 20
    assert "openai-anthropic-key" in _secret_hits(key)
    assert "pem-private-key" in _secret_hits(pem)
    assert "db-url-with-password" in _secret_hits(dburl)
    assert "long-alnum-chunk" in _secret_hits(chunk)
    # 비밀번호 없는 URL 은 잡지 않는다(결정 O).
    assert _secret_hits("postgresql://${POSTGRES_USER}@postgres:5432/${POSTGRES_DB}") == []


def test_no_secret_values_in_deploy_files():
    """⑥ compose·Caddyfile·Dockerfile·entrypoint 에 비밀 값 0, POSTGRES_PASSWORD 는 `${…:?}` 보간뿐."""
    for rel in (COMPOSE, CADDYFILE, DOCKERFILE, ENTRYPOINT):
        code = _code_text(rel)
        assert _secret_hits(code) == [], f"{rel}: 비밀로 보이는 문자열"

    compose = _code_text(COMPOSE)
    # POSTGRES_PASSWORD 에 값을 주는 줄은 전부 `${POSTGRES_PASSWORD:?…}` 여야 한다(리터럴·기본값 금지).
    values = re.findall(r"POSTGRES_PASSWORD\s*[:=]\s*(\S.*)$", compose, re.M)
    assert values, "POSTGRES_PASSWORD 줄이 없다"
    for value in values:
        assert value.startswith("${POSTGRES_PASSWORD:?"), f"리터럴/기본값 의심: 값 형태 {value[:3]!r}…"
    assert "${POSTGRES_PASSWORD:-" not in compose


# ⑦ -------------------------------------------------------------------------------------------
def test_required_variables_use_colon_question():
    """⑦ POSTGRES_USER·POSTGRES_PASSWORD·POSTGRES_DB·SITE_ADDRESS 는 `:?` 보간(없으면 기동 거부)."""
    compose = _code_text(COMPOSE)
    for name in ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", "SITE_ADDRESS"):
        assert "${" + name + ":?" in compose, name
        assert "${" + name + ":-" not in compose, f"{name} 에 기본값이 있다"


# ⑧ -------------------------------------------------------------------------------------------
def test_restart_unless_stopped_on_all_services():
    """⑧ 세 서비스 모두 `restart: unless-stopped`(재부팅·프로세스 종료를 버틴다)."""
    blocks = _service_blocks(_read(COMPOSE))
    for name in SERVICES:
        assert re.search(r"^\s*restart:\s*unless-stopped\s*$", blocks[name], re.M), name


# ⑨ -------------------------------------------------------------------------------------------
def test_volumes_declared_and_mounted():
    """⑨ 볼륨 pgdata·caddy_data 선언 + 각 서비스에 마운트(인증서·DB 보존)."""
    text = _read(COMPOSE)
    declared = _top_level_volumes(text)
    assert {"pgdata", "caddy_data"} <= declared
    blocks = _service_blocks(text)
    assert re.search(r"^\s*-\s*pgdata:/var/lib/postgresql/data\s*$", blocks["postgres"], re.M)
    assert re.search(r"^\s*-\s*caddy_data:/data\s*$", blocks["caddy"], re.M)


# ⑩ -------------------------------------------------------------------------------------------
def test_backend_database_url_has_no_password():
    """⑩ backend DATABASE_URL 은 `@postgres:5432/` 를 가리키고 사용자 부분에 `:` 가 없다(비밀번호 없는 URL).
    비밀번호는 environment 의 `POSTGRES_PASSWORD` 보간으로 간다(결정 O)."""
    block = _service_blocks(_read(COMPOSE))["backend"]
    m = re.search(r"^\s*DATABASE_URL:\s*(\S+)\s*$", block, re.M)
    assert m, "backend environment 에 DATABASE_URL 이 없다"
    url = m.group(1).strip("\"'")
    assert url.startswith("postgresql://")
    assert "@postgres:5432/" in url
    userinfo = url.split("://", 1)[1].split("@", 1)[0]
    assert ":" not in userinfo, "DATABASE_URL 사용자 부분에 비밀번호(:)가 있다"
    assert re.search(r"^\s*POSTGRES_PASSWORD:\s*\$\{POSTGRES_PASSWORD", block, re.M)


# ⑪ -------------------------------------------------------------------------------------------
def test_caddyfile_routing_contract():
    """⑪ Caddyfile — 호스트명 자리표시자·`/api/*` 접두 제거 프록시·SPA fallback·헤더·docs 404 순서(F-P9V-1)."""
    raw = _read(CADDYFILE)
    code = _code_text(CADDYFILE)

    assert "{$SITE_ADDRESS}" in code
    # 호스트명 리터럴(도메인 꼴) 0
    assert not re.search(r"[A-Za-z0-9-]+\.(sslip\.io|nip\.io|com|net|org|io|kr|app|dev)\b", code)

    api = _brace_block(code, r"handle_path\s+/api/\*")
    assert api, "handle_path /api/* 블록이 없다"
    assert re.search(r"reverse_proxy\s+backend:8000\b", api)

    # 404 는 handle_path 블록 안, reverse_proxy 줄보다 앞(최상위 respond 는 뒤에 평가돼 새어 나간다).
    lines = [ln.strip() for ln in api.splitlines() if ln.strip()]
    respond_idx = [i for i, ln in enumerate(lines) if re.match(r"respond\s+.*\b404\b", ln)]
    proxy_idx = [i for i, ln in enumerate(lines) if ln.startswith("reverse_proxy")]
    assert respond_idx and proxy_idx
    assert respond_idx[0] < proxy_idx[0]
    # 매처: 접두 없는 세 경로 정확히
    m = re.search(r"@docs\s+path\s+(.+)", api)
    assert m
    assert set(m.group(1).split()) == {"/docs*", "/redoc*", "/openapi.json"}
    assert "respond @docs 404" in api
    # 404 가 블록 밖(최상위)에도 있으면 안 된다 — 최상위 respond 는 새는 배치다.
    outside = code.replace(api, "")
    assert not re.search(r"respond\s+.*\b404\b", outside)

    assert "try_files {path} /index.html" in code
    assert "file_server" in code
    assert re.search(r'header\s+/sw\.js\s+Cache-Control\s+"no-cache"', code)
    assert re.search(r'header\s+/index\.html\s+Cache-Control\s+"no-cache"', code)
    assert re.search(
        r'header\s+/manifest\.webmanifest\s+Content-Type\s+"application/manifest\+json"', code
    )
    assert "header -Server" in code
    assert raw.strip()  # 빈 파일 방지


# ⑫ -------------------------------------------------------------------------------------------
def test_entrypoint_migrates_then_execs_single_worker():
    """⑫ entrypoint — `set -e`, alembic upgrade head 가 uvicorn 보다 앞, exec, `--workers 1`, app.main:app."""
    code = _code_lines(_read(ENTRYPOINT))
    joined = "\n".join(code)
    assert re.search(r"^set -[a-z]*e[a-z]*\s*$", joined, re.M)
    mig = [i for i, ln in enumerate(code) if "alembic upgrade head" in ln]
    run = [i for i, ln in enumerate(code) if "uvicorn" in ln]
    assert mig and run
    assert mig[0] < run[0]
    run_line = code[run[0]]
    assert run_line.lstrip().startswith("exec ")
    assert re.search(r"--workers 1\b", run_line)
    assert "app.main:app" in run_line


# ⑬ -------------------------------------------------------------------------------------------
def test_dockerfile_stages_user_and_bases():
    """⑬ Dockerfile — 단계 3개·기반 이미지·비루트 USER·.env 복사 없음·npm ci 앞에 NODE_ENV=production 없음."""
    text = _code_text(DOCKERFILE)
    stages = dict(
        (name, base) for base, name in re.findall(r"^FROM\s+(\S+)\s+AS\s+(\S+)\s*$", text, re.M)
    )
    assert stages == {
        "web-build": "node:24-slim",
        "caddy": "caddy:2-alpine",
        "backend": "python:3.13-slim",
    }

    # backend 단계 마지막 USER 는 root 가 아니다.
    backend_text = text.split("AS backend", 1)[1]
    users = re.findall(r"^USER\s+(\S+)\s*$", backend_text, re.M)
    assert users, "backend 단계에 USER 가 없다"
    assert users[-1] not in ("root", "0")

    assert not re.search(r"^COPY\b.*\.env", text, re.M)

    web_text = text.split("AS web-build", 1)[1].split("AS caddy", 1)[0]
    before_ci = web_text.split("npm ci", 1)[0]
    assert "NODE_ENV=production" not in before_ci
    assert "NODE_ENV" not in before_ci


# ⑭ -------------------------------------------------------------------------------------------
def test_dockerignore_excludes_secrets_and_vcs():
    """⑭ .dockerignore 에 `.env`·`.git`·`web/node_modules` 줄(빌드 문맥에 비밀이 안 들어간다)."""
    lines = {ln.strip() for ln in _read(DOCKERIGNORE).splitlines()}
    for entry in (".env", ".env.*", ".git", "web/node_modules"):
        assert entry in lines, entry


# ⑮ -------------------------------------------------------------------------------------------
def test_env_example_has_empty_site_address():
    """⑮ .env.example 에 `SITE_ADDRESS=` 이름 줄이 있고 값이 비어 있다."""
    lines = _read(ENV_EXAMPLE).splitlines()
    assert "SITE_ADDRESS=" in [ln.rstrip() for ln in lines]


# 보조 -----------------------------------------------------------------------------------------
def test_compose_backend_dependencies_logging_and_tags():
    """보조 — backend 는 postgres healthy 를 기다리고, 헬스체크 start_period 60s, 로그 10m×3, 이미지 태그는
    `${GIT_SHA:-local}`(커밋 해시), caddy 는 인증서 볼륨·backend 의존(service_started 기본)."""
    text = _read(COMPOSE)
    blocks = _service_blocks(text)
    backend = blocks["backend"]
    assert re.search(r"condition:\s*service_healthy", backend)
    assert re.search(r"start_period:\s*60s", backend)
    assert "http://127.0.0.1:8000/health" in backend
    assert "image: relationship-backend:${GIT_SHA:-local}" in backend
    assert "image: relationship-caddy:${GIT_SHA:-local}" in blocks["caddy"]
    assert "pgvector/pgvector:pg16" in blocks["postgres"]
    assert 'max-size: "10m"' in text and 'max-file: "3"' in text
    for name in SERVICES:
        assert "logging: *default-logging" in blocks[name], name
    assert "${APP_ENV_FILE:-.env}" in backend
    assert re.search(r"target:\s*backend", backend)
    assert re.search(r"target:\s*caddy", blocks["caddy"])
