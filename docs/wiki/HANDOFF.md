# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-06 10:50 (U1 완료·커밋, 다음 U2 는 사용자 승인 후)
active: **P3-er** | frozen: none | 브랜치: dev (dev = origin/dev = **main = b676799**). 미푸시 2커밋: 착수 bb1abfe + U1 커밋(journal COMMIT 줄 참조). **U1 완료(2026-09-06)** — 다음은 U2, 시작 전 AskUserQuestion(L-004)

## 지금 어디까지
- **P3-er 착수 진행 중(2026-09-05)**: 사용자 "P3-er 시작해줘" → 선행 확인(P2-tools 완료 b676799, 닫는 R4 R9, 카드 S3.3 D3 D10 D5, .env.example 에 ANTHROPIC_API_KEY·ANTHROPIC_MODEL·OPENAI_API_KEY 이름 있음, anthropic·openai 미설치) → `--stage architect` → architect(opus) 01-plan 초안 U1~U8(app/er/{types,dictionary,candidates,rules,judge,confidence,pipeline}, Anthropic tool_use 강제 구조화 출력·실패 시 안전 강등 s_llm=0→identity, resolve() 부수효과 0 + apply_resolution(), trace 1행 step=er_resolve tool_name="er", FakeJudge+grouped_embedder 회귀 3종, 벡터 인덱스 연기, U1 F-ca12ad begin_nested) → verify-plan FAIL 1(02-plan-verify 부재)/WARN 8(기존 행) → **사용자 확인 3건(23:45 DECISION)**: 별칭만 누적·이름은 확인 후 / tool_name="er" / 인덱스 연기·공급자 이동·의존성 추가 → verifier 02-plan-verify **보류**(FAIL 0/WARN 9: 점검표 #2 원칙 보류 1 + 기존 행 8; 필수 3: F-138665 confidence 후보 귀속·null 구간 / F-f43a9d resolve 부수효과 0 vs trace applied 필드 / F-8c6354 승진 픽스처 위계; 권고 7) → **사용자 결정(00:10 DECISION)**: LLM 이 고른 인물의 값·null 은 병합 금지 / apply 가 같은 행 갱신 / 픽스처 hierarchy=동 → `--stage architect` 2회차 → 개정 1(결정 3-c 신설·결정 4 apply 부분 갱신·결정 9·10 승진 픽스처 hierarchy=동·직급→위계 표(USER_RANK_ANCHOR=2)·결정 2 배제 규칙 수정, 권고 7 반영, U6 분할 → U1~U9, 신규 리스크: 부동소수 round·힌트 없는 상한 0.8=T_merge→P4 인계) → verify-plan FAIL 0/WARN 9(옛 보류 표기 1 + 기존 행 8) → `--stage verifier` 2회차 → 재검증 **통과**(FAIL 0/WARN 8 의도, 보류 3 닫힘·권고 7 해소, 새 권고 6: F-7fe239 허용오차 1e-9 / F-93f063 JSONB 갱신 원시 SQL 재조회 / F-8809f2 apply 중복 거부 / F-f3b245 llm_failed 귀속 / F-5a97ef 범위 집합 통일 / F-1d65ac null 경로 테스트) → **사용자 계획 승인(2026-09-06 01:00)** → active: P3-er.
- **P2-tools 완료(2026-09-05)** — U1~U9 커밋(f217190 기반 / 4eca3e9 ToolContext·@traced / a9cb254 search_person / f318d58 create·update_person / 9cb35b6 add_event·add_schedule / 8162e09 ask_user / 7c94aad get_briefing / 4d5817e FastAPI 골격 / f2e9e05 tools_check·문서) → verifier(fable) 04-review `결과: 완료`, 사용자 승인. verify-impl 최종 PASS/WARN 0/FAIL 0(`evidence/20260905-1948-verify-impl.txt`, done 후 `2255-verify-impl-done.txt` 동일). 수용 기준: 시그니처 = CLAUDE.md(tools_check 7/7 + verifier 독립 대조 MISMATCH 0, `ctx` 편차는 훼손 아님), ask_user → pending_questions(독립 세션 실행·조회·rollback). 변이 4종 전부 검출, 원칙 침범 grep 0, uvicorn 200/404/422, pytest 206. R6 R7 R10 R18 → review-index "구현완료(해시)". backlog 체크, README P2 "완료", CURRENT none.
- **열린 소견(필수 0)**: **F-4d2507** `DELETE /persons/{id}`(security.md §5) backlog 항목 없음 → **architect** 가 P5/P8 계획 때 항목 신설. **F-ca12ad** `@traced` except 경로가 flush 실패 뒤 같은 세션에 tool_error 를 add+flush 해 PendingRollbackError 가 원래 오류를 덮고 tool_error 행도 남지 않음(실제 embedder 연결 시 도달, `evidence/20260905-1942-review-tool-error-probe.txt`) → **P3-er 첫 단위**에서 savepoint/rollback 후 기록으로 수정 + 테스트. F-4d8d96(tool_error rollback 소실)·F-c7078e(mako Refs)도 P3/P5.
- **P3-er 인계**(04-review §7): `Candidate` 계약(배제 없음, rule_flags 6, hierarchy_adjacent), `EmbeddingProvider.embed()` 만 있음 — D4 의 `dimension` 추가 권장(F-ca12ad 와 묶어), OpenAI 공급자는 `scripts/embed_pilot.py` 호출을 옮겨 `app/embedding.py` 에, NULL 임베딩 백필, 벡터 인덱스 revision(source CHECK 동승 여부), `AFFIRMATIVE_KEY` 규약(context["affirmative_options"]), `ALIAS_SOURCES` import.
- **P5-loop 인계**: ctx 생성 단일화·`X-Session-Id`, **확인 질문이 특정 인물·이름에 묶이지 않고 1회 소비되지도 않음**(같은 answered new_person 질문으로 create_person 반복 가능 — 1회 소비·대상 바인딩은 P5 결정), POST /answers 재개 확장, `list_pending` 라우트, expired 24h, user_id 격리(F-fbaaae — pending_questions·agent_traces 에 user_id 없음), LLM 에 노출하는 툴 스키마는 `ctx` 를 뗀 매개변수만, agent_traces tokens 는 P5 부터 실제 값.
- 관찰(조치 불필요): TRACE_MAX_STRING 은 context.py 2000(계획 표기 settings 4000 과 다름), /health 키 `alembic_revision`, verify-impl.sh 가 POSTGRES_PORT·-rs 없이 pytest 호출(조용한 skip 위험 — 하네스 개선 후보), context 비밀 방어는 키 이름만.
- 로컬 DB: capstone2-postgres-1 호스트 5433, 스키마 0001(head). 명령 앞 `POSTGRES_PORT=5433`, pytest `-rs`. 한글 출력은 PYTHONIOENCODING=utf-8 + 파일 리다이렉트.
- P0-compose·P1-schema 완료(main 5dc95bb). .env.example 추적 유지. 팀 밑작업(Agent Teams) 보류.

## 바로 다음에 할 것 (순서대로)
1. (완료) 완료 커밋 b676799 → dev 푸시(11커밋) → main 승격(사용자 승인, 2026-09-05).
2. (완료) 착수 커밋 bb1abfe.
3. (완료) **U1** — backend-agent(sonnet) 구현, pytest 208 passed/skip 0·tools_check 7/7(evidence `20260906-1030-u1-*.txt`), 03-log 항목 pending 해시는 다음 커밋에서 교체. 내용: app/tools/context.py `@traced` except 경로 — `begin_nested()` 세이브포인트로 tool_error 기록, 기록 실패 시 원래 예외 보존(`raise from`), step 인자·`trace_tokens`(tokens_in/out 주입) 확장; 재현 테스트: 1535차원 임베딩 flush 실패 → 원래 DataError 가 보존되고 tool_error 행이 남는지(F-ca12ad). 이후 U2 임베딩 공급자 이동(dimension·check_dimension·NOT NULL 위반으로 flush 실패 테스트 전환·openai/anthropic 핀·dotenv 는 embed_pilot 에만) → U3 호칭 사전·규칙 필터 → U4 확신도·두 임계치(권고 F-7fe239 F-f3b245 F-5a97ef) → U5 후보 어댑터·Judge → U6 resolve·trace(F-1d65ac) → U7 apply·회귀 3종(F-93f063 F-8809f2) → U8 백필·스모크 → U9 검증·문서.
4. **다음: U2 임베딩 런타임 공급자** — 시작 전 AskUserQuestion → `--stage backend-agent`. U1 인계: flush 실패 테스트 재현 수단을 NOT NULL 위반으로 전환(F-3ca6b5), `check_dimension()` 을 `_add_alias` 저장 직전에.

## 재개 시 읽을 카드 (이것만)
- `docs/wiki/CURRENT.md`, `docs/wiki/INDEX.md`, `.claude/gitlog.md`
- `packages/P3-er/01-plan.md`(결정 1~10·판정 방법·회귀 3종), `02-plan-verify.md` §3, `05-remediation.md` 권고 6, `packages/P2-tools/04-review.md` §7
- `lessons/L-001`~`L-004`

## 열린 질문 · 사용자 결정 대기
- **U2 시작 승인(L-004)**. 미푸시 2커밋(bb1abfe·U1) 푸시 시점. P1-pilot-dataset·P0-cost 착수 시점.

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). **위임은 묻고 시작**(L-004): AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회. 재검증·개정도 매번.
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` → 승격/수정/보류를 묻고 멈춘다(L-003). "계속 작업"은 `--decision fix`. 승격은 `--release` → `git push origin dev:main` → `git fetch origin main:main`.
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저. Bash 문자열에 훅 금지 문구(볼륨 삭제, 강제 푸시, DROP) 금지 — 문서·마이그레이션은 Write 도구. `.env` 존재 확인도 금지. 변이 검사 원복에 `git checkout --` 는 safety-guard 가 막는다(복사본으로 원복).
- `findings.py` 는 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 앞에. `## 수용 기준` 절엔 backlog 문장 불릿만. registry 커밋 열은 파일을 실제로 바꾼 커밋만, README·db_check·requirements·models·config·conftest·test_config 행은 각 1개(비고만).
- 서브에이전트가 만든 pending 해시·상태 줄은 done 커밋에서 메인 세션이 정리한다.
