# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-05 23:00 (P2-tools 완료 처리, 완료 커밋 직전)
active: none | frozen: none | 브랜치: dev (origin/dev = main = 5dc95bb. 로컬 dev 는 P2-tools 10커밋 + 완료 커밋 = 11개 앞섬, **미푸시**)

## 지금 어디까지
- **P2-tools 완료(2026-09-05)** — U1~U9 커밋(f217190 기반 / 4eca3e9 ToolContext·@traced / a9cb254 search_person / f318d58 create·update_person / 9cb35b6 add_event·add_schedule / 8162e09 ask_user / 7c94aad get_briefing / 4d5817e FastAPI 골격 / f2e9e05 tools_check·문서) → verifier(fable) 04-review `결과: 완료`, 사용자 승인. verify-impl 최종 PASS/WARN 0/FAIL 0(`evidence/20260905-1948-verify-impl.txt`, done 후 `2255-verify-impl-done.txt` 동일). 수용 기준: 시그니처 = CLAUDE.md(tools_check 7/7 + verifier 독립 대조 MISMATCH 0, `ctx` 편차는 훼손 아님), ask_user → pending_questions(독립 세션 실행·조회·rollback). 변이 4종 전부 검출, 원칙 침범 grep 0, uvicorn 200/404/422, pytest 206. R6 R7 R10 R18 → review-index "구현완료(해시)". backlog 체크, README P2 "완료", CURRENT none.
- **열린 소견(필수 0)**: **F-4d2507** `DELETE /persons/{id}`(security.md §5) backlog 항목 없음 → **architect** 가 P5/P8 계획 때 항목 신설. **F-ca12ad** `@traced` except 경로가 flush 실패 뒤 같은 세션에 tool_error 를 add+flush 해 PendingRollbackError 가 원래 오류를 덮고 tool_error 행도 남지 않음(실제 embedder 연결 시 도달, `evidence/20260905-1942-review-tool-error-probe.txt`) → **P3-er 첫 단위**에서 savepoint/rollback 후 기록으로 수정 + 테스트. F-4d8d96(tool_error rollback 소실)·F-c7078e(mako Refs)도 P3/P5.
- **P3-er 인계**(04-review §7): `Candidate` 계약(배제 없음, rule_flags 6, hierarchy_adjacent), `EmbeddingProvider.embed()` 만 있음 — D4 의 `dimension` 추가 권장(F-ca12ad 와 묶어), OpenAI 공급자는 `scripts/embed_pilot.py` 호출을 옮겨 `app/embedding.py` 에, NULL 임베딩 백필, 벡터 인덱스 revision(source CHECK 동승 여부), `AFFIRMATIVE_KEY` 규약(context["affirmative_options"]), `ALIAS_SOURCES` import.
- **P5-loop 인계**: ctx 생성 단일화·`X-Session-Id`, **확인 질문이 특정 인물·이름에 묶이지 않고 1회 소비되지도 않음**(같은 answered new_person 질문으로 create_person 반복 가능 — 1회 소비·대상 바인딩은 P5 결정), POST /answers 재개 확장, `list_pending` 라우트, expired 24h, user_id 격리(F-fbaaae — pending_questions·agent_traces 에 user_id 없음), LLM 에 노출하는 툴 스키마는 `ctx` 를 뗀 매개변수만, agent_traces tokens 는 P5 부터 실제 값.
- 관찰(조치 불필요): TRACE_MAX_STRING 은 context.py 2000(계획 표기 settings 4000 과 다름), /health 키 `alembic_revision`, verify-impl.sh 가 POSTGRES_PORT·-rs 없이 pytest 호출(조용한 skip 위험 — 하네스 개선 후보), context 비밀 방어는 키 이름만.
- 로컬 DB: capstone2-postgres-1 호스트 5433, 스키마 0001(head). 명령 앞 `POSTGRES_PORT=5433`, pytest `-rs`. 한글 출력은 PYTHONIOENCODING=utf-8 + 파일 리다이렉트.
- P0-compose·P1-schema 완료(main 5dc95bb). .env.example 추적 유지. 팀 밑작업(Agent Teams) 보류.

## 바로 다음에 할 것 (순서대로)
1. 완료 커밋 `/commit`(04-review·05·evidence·registry·review-index·backlog·README·CURRENT·03-log 해시·journal·HANDOFF) — 진행 중 → **dev 푸시**(11커밋) → L-003: 사용자 결정 "패키지 완료 후 승격" → **main 승격** 제안(`--release` → `git push origin dev:main`).
2. 다음 패키지 사용자 선택: **P3-er**(backend-agent, ER 4단계+확신도+trace, 의존 P2 충족, R4 R9; 첫 단위에 F-ca12ad) / **P1-pilot-dataset**(eval-agent, 30~50건 — P3 평가에 필요) / **P0-cost**(eval-agent). `/devlog start <id>` — architect 위임 전 AskUserQuestion + `--stage architect`(L-004). P4 게이트: P5 이후는 P4-pilot-eval 전 시작 금지.

## 재개 시 읽을 카드 (이것만)
- `docs/wiki/CURRENT.md`, `docs/wiki/INDEX.md`, `.claude/gitlog.md`
- `packages/P2-tools/04-review.md` §6·§7(열린 문제·인계), `docs/backlog.md` P2/P3 절
- `lessons/L-001`~`L-004`

## 열린 질문 · 사용자 결정 대기
- dev 푸시 뒤 main 승격(L-003).
- 다음 패키지 선택(P3-er / P1-pilot-dataset / P0-cost).

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). **위임은 묻고 시작**(L-004): AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회. 재검증·개정도 매번.
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` → 승격/수정/보류를 묻고 멈춘다(L-003). "계속 작업"은 `--decision fix`. 승격은 `--release` → `git push origin dev:main` → `git fetch origin main:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저. Bash 문자열에 훅 금지 문구(볼륨 삭제, 강제 푸시, DROP) 금지 — 문서·마이그레이션은 Write 도구. `.env` 존재 확인도 금지. 변이 검사 원복에 `git checkout --` 는 safety-guard 가 막는다(복사본으로 원복).
- `findings.py` 는 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 앞에. `## 수용 기준` 절엔 backlog 문장 불릿만. registry 커밋 열은 파일을 실제로 바꾼 커밋만, README·db_check·requirements·models·config·conftest·test_config 행은 각 1개(비고만).
- 서브에이전트가 만든 pending 해시·상태 줄은 done 커밋에서 메인 세션이 정리한다.
