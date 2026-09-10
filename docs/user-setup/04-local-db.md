# 04 · 로컬 DB (Docker Desktop + docker-compose + pgvector)

## 언제 필요한가
DB 를 쓰는 테스트(툴 7종·ER 파이프라인·trace) 실행 전. 없으면 해당 테스트가 skip 된다.

## 왜 사용자 몫인가
Docker Desktop 실행·볼륨은 사용자 PC 자원이다. 에이전트는 `docker compose up/down/ps` 는 실행할 수 있지만 볼륨 삭제·prune 은 훅이 막는다.

## 현재 상태 (2026-09-10)
- 컨테이너 `capstone2-postgres-1`, 호스트 포트 **5433**(5432 충돌 회피), 스키마 revision 0001(head).
- 명령 앞에 `POSTGRES_PORT=5433` 을 붙이거나 `.env` 에 같은 값을 둔다.

## 절차
1. Docker Desktop 실행.
2. `docker compose up -d` → `docker compose ps` 로 healthy 확인.
3. 스키마: `POSTGRES_PORT=5433 alembic upgrade head` (처음 또는 새 revision 이 생겼을 때).
4. 확인: `POSTGRES_PORT=5433 python scripts/db_check.py`.
5. 테스트: `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs` (한글 출력이 깨지면 `PYTHONIOENCODING=utf-8`).
6. 끄기: `docker compose down` 만. 볼륨 `pgdata` 는 지우지 않는다.

## 알아 둘 것
- `verify-impl.sh` 안의 pytest 는 포트 없이 돌아 DB 테스트가 skip 으로 나온다(하네스 한계). 증거가 필요하면 위 5번을 직접 실행해 파일로 남긴다.
- 포트를 바꾸면 `.env` 의 `POSTGRES_PORT` 와 `DATABASE_URL` 을 **같이** 바꾼다.
- P3-baselines·P4 는 시나리오 사이에 DB 를 초기화한다(같은 가상 성명이 다른 관계로 재등장). 로컬 DB 에 개인 데이터를 넣어 두지 않는다.
