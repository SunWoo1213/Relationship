# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-05 17:35 (P2-tools 계획 승인, 착수 커밋 직전)
active: **P2-tools** | frozen: none | 브랜치: dev (dev = origin/dev = **main = 5dc95bb**). 미커밋: packages/P2-tools/*(계획 문서 일체)·CURRENT·HANDOFF·journal — 착수 커밋으로 정리 중

## 지금 어디까지
- **P2-tools 착수 진행 중(2026-09-05)**: 사용자 "P2-tools 시작해줘" → 선행 확인(P1-schema 완료 5dc95bb, 닫는 R6 R7 R10 R18, 카드 S3.2 S3.4 D1 D2 D6, registry 툴·세션 없음) → architect(opus) 01-plan 초안(U1~U8: 세션·ToolContext 주입, 임베딩 인터페이스만(공급자 P3), D1 DB 검사, source=user_said/confirmed/system, facts upsert, 실 DB 5433 롤백 픽스처, tools_check.py 시그니처 기계 대조) → verify-plan 1차 FAIL 1(02-plan-verify 부재)/WARN 5(기존 행 비고만, 의도) → 05-remediation 기입 → **사용자 결정: FastAPI 골격(app/main.py, GET /health, POST /answers 답 저장만)을 P2 포함, delete_person 은 제외·미결** → `--stage architect` 2회차 → 개정 1(U1~U9: U8 FastAPI 골격 app/api/·GET /health·POST /answers 404/409/422/200 신설, requirements +fastapi·uvicorn·httpx 는 U1, 결정 10~13) → verify-plan 2차 FAIL 1(02-plan-verify 부재)/WARN 6(기존 행 비고만) → 05 기입 → `--stage verifier` → verifier 02-plan-verify **통과**(FAIL 0/WARN 6 의도, 점검표 8행, 보류 0, 권고 9: F-08b3db 판정 표 포트 변수 / F-b97a06 D1 긍정 답 규약 / F-4d8d96 tool_error trace rollback 한계 / F-3c8d4a "U8" 참조→U9·S3.1 한 줄 / F-fbaaae pending_questions 에 user_id 없음 / F-0010e6 ALIAS_SOURCES 를 U2 로 / F-2418ef display_name 변경 시 별칭 누적 / F-4d2507 DELETE /persons backlog 항목 없음 / F-107a50 tools_check 출력) → **사용자 계획 승인(2026-09-05 17:30)** → active: P2-tools.
- **P1-schema 완료(2026-09-05)** — U1~U5 커밋(d7113e9 골격·config / 4dfaf33 모델 9개 / 09c2bd1 Alembic 0001 / 03e3ce3 schema_check·왕복 / ec2fe8c registry·README·db_check version) → verifier(fable) 04-review `결과: 완료`, 사용자 승인. verify-impl 최종 PASS/WARN 0/FAIL 0(`evidence/20260905-1439-verify-impl-final.txt`, done 후 재실행 `1552-verify-impl-done.txt` 동일). 수용 기준 "9개 테이블 생성, events.type 제약 존재" 를 verifier 독립 쿼리로 확인(컬럼 56). 변이 4종·expect-empty at head(exit 1)·badport(exit 2, 비밀 0회)·alembic check 직접 실행. R8 R9 → review-index "구현완료(4dfaf33, 09c2bd1)". backlog 체크, README P1 행 "완료", CURRENT none.
- 권고 인계(조치 안 함): **F-8eeb9b** `app/config.py` ConnInfo dataclass 기본 repr 에 password 포함(현재 호출부는 safe_summary 만 사용 — 유출 없음) → **P2-tools 엔진·세션 도입 전 `field(repr=False)` + 테스트**. **F-c7078e** `alembic/script.py.mako` 에 P1-schema Refs 고정 → P3-er 첫 revision 때 교체. F-36bed6(registry 38·39행 커밋 열) 은 done 에서 정정 완료. F-081752(ask_user status=expired 파생에 created_at 24h 조건) → P2-tools.
- P2-tools 인계(04-review §7): 모델·값 집합 상수는 `app.db.models` 에서 import(재정의 금지), 접속은 `app.config.resolve_connection()`/`sqlalchemy_url()`(엔진·sessionmaker·FastAPI 는 미구현 = P2), NOT NULL 계약(`person_aliases.source` 값 집합 미정), `agent_traces.tool_name/tokens` NOT NULL 과 툴 아닌 ER 단계 trace 규약(P3-er), 인물 삭제 사각지대(pending_questions·agent_traces 는 person FK 없음), `user_id` 출처, `person_facts` UNIQUE 미설정, 벡터 인덱스는 P3-er, requirements→pyproject 재검토.
- 로컬 DB: capstone2-postgres-1 호스트 5433, 스키마 `0001 (head)` 적용 상태. 명령 앞에 `POSTGRES_PORT=5433`. 한글 출력은 `PYTHONIOENCODING=utf-8` + 파일 리다이렉트.
- P0-compose 완료(819e1ac, main). .env.example 추적 유지 확정. 팀 밑작업(Agent Teams) 보류.

## 바로 다음에 할 것 (순서대로)
1. (완료) 완료 커밋 5dc95bb → dev 푸시 → main 승격(사용자 승인, 2026-09-05).
2. 착수 커밋 `/commit`(계획 문서·CURRENT·03-log·journal·HANDOFF) — 진행 중.
3. U1(사용자 승인 → `--stage backend-agent`): requirements +fastapi·uvicorn[standard]·httpx 실제 설치·핀·pip freeze evidence(리스크 B: httpx↔TestClient 호환 즉시 확인), ConnInfo.password `field(repr=False)`+테스트(F-8eeb9b), app/db/session.py(engine=sqlalchemy_url, SessionLocal, session_scope), app/settings.py(APP_USER_ID 기본 local), tests/conftest.py DB 롤백 픽스처·`dbtest` 마커(POSTGRES_PORT=5433, 없으면 skip + `-rs`). 이후 U2(types·ToolContext·@traced + **ALIAS_SOURCES 상수 여기서**, F-0010e6) → U3 → … → U9. 단위마다 `/commit`. 미착수: P1-pilot-dataset·P0-cost(eval-agent).

## 재개 시 읽을 카드 (이것만)
- `docs/wiki/CURRENT.md`, `docs/wiki/INDEX.md`, `.claude/gitlog.md`
- `packages/P2-tools/01-plan.md`(작업 단위·결정 1~13·판정 방법), `02-plan-verify.md` §3, `05-remediation.md` 권고 9건, `packages/P1-schema/04-review.md` §7
- `lessons/L-001`~`L-004`

## 열린 질문 · 사용자 결정 대기
- U1 시작 승인(L-004). P1-pilot-dataset·P0-cost 착수 시점.

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). **위임은 묻고 시작**(L-004): AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회.
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` 이 생기면 승격/수정을 묻고 멈춘다(L-003). "계속 작업" 결정은 `--decision fix` 로 마커 해제(2026-09-05 U2 뒤 그렇게 함). 승격은 `--release` → `git push origin dev:main` → `git fetch origin main:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저 만든다.
- Bash 명령 문자열에 훅 금지 문구(볼륨 삭제 옵션, 강제 푸시, DROP)가 **텍스트로라도** 들어가면 차단. 마이그레이션·README 는 Write 도구로. `.env` 존재 확인도 금지.
- `findings.py` 는 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 앞에 붙여 실행. `## 수용 기준` 절에는 backlog 문장 불릿만(설명 불릿은 verify-plan FAIL). `alembic.ini` 주석은 영어(cp949 configparser).
- registry 에 README·db_check 행은 각 1개(새 행 금지, 비고만). registry 커밋 열은 **그 파일을 실제로 바꾼 커밋**만(F-36bed6).
