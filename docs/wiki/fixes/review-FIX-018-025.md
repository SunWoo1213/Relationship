# FIX-018 ~ FIX-025 사후 일괄 검토

검토자: verifier (fable)
날짜: 2026-10-06
대상 커밋(dev2): `7bc2e60`(FIX-018) · `4912865`(FIX-019) · `7459925`(FIX-020) · `b124c8e`·`3e4d67c`(FIX-021) · `80ae193`(FIX-022) · `125976a`(FIX-023) · `a9ae04f`(FIX-024) · `3cd378c`(FIX-025)
성격: 여덟 FIX 모두 계획 문서의 `검증: 통과` 줄을 메인 세션이 직접 썼고 독립 검증자가 들어가지 않았다(L-002 미이행). 이 문서가 그 사후 검증이다. 코드·문서는 고치지 않았다 — 판정과 소견만 남긴다.

## 0. 검토 방법과 현재 상태 (직접 실행)

| 명령 | 결과 |
|---|---|
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` (dev2 `3cd378c`) | `1835 passed, 1 warning in 20.65s`, skip 0 |
| `POSTGRES_PORT=1 .venv/bin/python -m pytest -q -m "not dbtest"` (Windows job 경로 재현) | `1399 passed, 436 deselected`, skip 0 |
| `.venv/bin/ruff check app tests scripts evaluation` | `All checks passed!` |
| `.venv/bin/python scripts/mypy_check.py --run` | `[ok] 새 오류 없음 (현재 37건, 기준선 37건)` |
| `gh run list --branch dev2 --limit 15` | FIX-018~025 커밋 전부 `completed success`; 유일한 `failure` 는 `b124c8e`(run 37397329951, FIX-021 1차)이고 `3e4d67c` 로 닫힘 |
| 검증자 추가 실행(아래 FIX-020 소견 F-1) | `docs/wiki/fixes/evidence/20261006-1429-review-fix020-updated-at.txt` |

원문은 카드가 가리키는 절만 읽었다: `D12-observed-signal-renormalization.md`, `S3.1-schema-v2.md` 25행(보충 줄), `P5-loop/01-plan.md` 결정 H(264~267행), `P6-briefing/01-plan.md` 47행(`validate_briefing()`), `security.md` 절 제목, CLAUDE.md 불변 원칙.

## 1. FIX 별 판정

### FIX-018 · dev2 CI 트리거 — **통과**

- 증상·원인: `7bc2e60` diff 는 `.github/workflows/tests.yml` 의 `branches: [main, dev, dev2]` 와 `concurrency: tests-${{ github.ref }}` / `cancel-in-progress: true` 두 변경뿐. 제품 코드 무변경(stat 5파일 전부 워크플로·위키).
- 동작 확인: run 37299302544(`fix(FIX-018)…`, dev2, push, success) — 이 커밋이 dev2 첫 CI 실행이라는 문서 주장과 `gh run list` 출력이 일치한다.
- 소견 [권고] R-18-1: `cancel-in-progress: true` 는 `main`·`dev` 그룹에도 적용된다. `main` 은 fast-forward 한 번씩만 들어오므로 실질 위험은 낮지만, 연속 두 번 승격하면 앞 커밋의 CI 기록이 "cancelled" 로 남는다. 필요하면 `cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}` 로 좁힐 수 있다(선택).

### FIX-019 · `answer_question` 행 잠금 — **통과** (소견 [권고] 1)

- 재현 증거: `evidence/20261005-2001-fix019-before.txt` 67행 `AssertionError: B 가 already_answered 없이 통과했다(오병합 경로 재현)`, 165행 `{'a': <Response [200 OK]>, 'b': <Response [200 OK]>}` — 수정 전 실제 실패. `…-after.txt` 2 passed. 테스트 파일 `tests/test_answer_concurrency.py` 는 커밋 `4912865` 에 포함.
- 제품 변경 정확성(`app/tools/questions.py` 1줄 `with_for_update=True`):
  - SQLAlchemy 2.0.50 `Session._get_impl` 은 `for_update_arg is None` 일 때만 식별자 맵을 먼저 보고, 그렇지 않으면 반드시 `SELECT … FOR UPDATE` 를 낸다(소스 확인). 즉 같은 세션에 캐시가 있어도 잠금 질의가 실제로 나간다.
  - 잠금 범위: `pending_questions` 한 행. `POST /answers/{id}` 에서 `answer_question` 이 첫 DB 연산(`app/api/routes.py:232`)이라 B 는 다른 잠금을 들고 대기하지 않는다 → 교착 사이클 없음. READ COMMITTED 에서 잠금 대기 후 최신 행을 재평가하므로 B 는 `answered_at IS NOT NULL` 을 보고 409 로 끝난다(테스트 (a) 가 그대로 단언).
  - 잠금은 A 의 요청 트랜잭션(재개·LLM 호출 포함)이 끝날 때까지 유지된다 — 같은 질문의 두 번째 요청만 블로킹되고 다른 요청에는 영향 없음(문서 주장과 일치).
- 테스트 품질: 스레드 순서를 이벤트로 제어하고 `_WAIT_TIMEOUT` 은 상한. (b) 의 최종 단언(`[200, 409]`, `resume_turn` 1회, `Schedule` 1행)이 결함을 직접 검사한다. 정리는 try/finally·지정 ID 삭제. 3회 반복 통과(문서) + 내 전체 실행 통과.
- 정합성: S3.4(409 `already_answered`)·D2·원칙1 — 위반 없음. 스키마·응답 모양 무변경 확인(diff).
- 소견 [권고] R-19-1: B 가 A 의 재개(LLM 호출 포함) 전체 시간만큼 HTTP 응답을 기다린다. 사용자가 칩을 두 번 눌렀을 때 두 번째 요청을 즉시 409 로 돌려보내고 싶다면 `with_for_update={"nowait": True}` + `OperationalError` → 409 매핑이 대안이다. 지금 동작도 정합하므로 필수 아님.

### FIX-020 · UNIQUE 3개 + ON CONFLICT, Alembic 0002 — **소견 있음** ([필수] 1 · [권고] 4)

통과한 것(증거):
- 재현: `evidence/20261006-0920-fix020-before.txt` 42·97·137행 세 자리 모두 `B 가 A 의 커밋을 기다리지 않고 곧바로 끝났다` 로 FAILED(`3 failed in 0.43s`) → `…-0935-fix020-after.txt` 3회 반복 `3 passed`.
- 마이그레이션 `alembic/versions/0002_unique_upsert_keys.py`: 사전 검사(`GROUP BY … HAVING count(*) > 1`)와 제약 생성이 같은 트랜잭션(transactional DDL, 증거 `…-0940-fix020-alembic.txt` 2행) 안에서 돌고, 중복이 있으면 `RuntimeError` 로 멈추며 메시지에 테이블명·그룹 수만 담는다(security §1 정합). `downgrade` 는 역순으로 세 제약 제거. 왕복 증거 `check → downgrade 0002->0001 → upgrade 0001->0002 → check "No new upgrade operations detected." → current 0002 (head)`, 대상 DB `relationship_test`.
- 제약 이름: `name=` 미지정 + `uq_%(table_name)s_%(column_0_N_name)s` 컨벤션 → `uq_person_facts_person_id_key` 등 — 0002 의 상수 `_UNIQUE_SPECS` 와 `tests/test_briefing_inputs.py` 의 `match="uq_person_facts_person_id_key"` 가 같은 이름을 쓰고 `alembic check` 가 통과했으니 모델·DB 이름이 일치한다.
- `xmax = 0` 신규/충돌 판정: ON CONFLICT DO UPDATE 가 기존 행을 갱신하면 `xmax` 가 현재 트랜잭션 id 로 바뀌므로 `inserted=False`, 새 삽입은 `xmax=0`. 테스트 1(`action == "updated"`, `fact_id` 동일)·테스트 3(`created is False`, `id` 동일)이 반환값 동등성을 검사한다.
- 별칭 경로(`_add_alias`): 먼저 일반 SELECT 로 존재를 가려 **있으면 임베딩을 부르지 않고**, 없을 때만 임베딩 → `ON CONFLICT DO NOTHING` → 충돌 시 재조회 후 `_ALIAS_RANK` 격상. 테스트 2 가 B(상위 `confirmed` 소스)로 격상·`confirmed_at` 보존을 단언. 좁은 창에서 임베딩이 두 번 계산될 수 있다는 점은 docstring 에 명시됨(문서 "충돌 시 임베딩 API 를 부르지 않도록" 과는 약간 다르지만, 코드 주석이 정확히 설명한다).
- `expire_all()` 부작용 범위: `session.flush()` 직후에 호출하고 `sessionmaker(autoflush=True)`(`app/db/session.py:59`)라 미flush 변경 손실은 없다. `update_person` 에서는 `facts` 분기 안에서만 호출된다. 정합성 문제 없음(비용은 아래 R-20-3).
- 정합성: S3.1 25행 보충 줄 존재. D6 "동명이인 허용" 과 `UNIQUE(person_id, alias)`(인물 단위) 양립. `tests/test_api.py` 리비전 기대값 `0002`.

**[필수] F-20-1 — 사실 값이 바뀌어도 `person_facts.updated_at` 이 더 이상 갱신되지 않는다(회귀).**
- 근거: `PersonFact.updated_at` 은 `onupdate=func.now()`(`app/db/models.py:157~161`)이고, 예전 코드는 ORM 속성 변경(`existing.value = …`)으로 UPDATE 를 내 `updated_at` 이 함께 갱신됐다. FIX-020 이 바꾼 `INSERT … ON CONFLICT DO UPDATE SET` 은 SQLAlchemy 가 `Column.onupdate` 를 `set_` 에 **적용하지 않는다**(공식 문서 경고). 컴파일 결과: `… DO UPDATE SET value = %(param_1)s, confidence = CASE … END RETURNING …` — SET 절에 `updated_at` 없음.
- 재현(테스트 DB, 커밋 두 번): `evidence/20261006-1429-review-fix020-updated-at.txt` — `row1: (05:29:01.286341, '등산')` → `_upsert_fact(… '클라이밍')` 후 `row2: (05:29:01.286341, '클라이밍')` → `updated_at advanced after value change?: False`. 같은 행을 ORM 으로 바꾸면 `ORM path advanced?: True`. 스크립트 본문이 증거 파일 상단에 있다.
- 영향: 같은 결함이 `app/memory/promote.py::_upsert_fact` 와 `app/tools/persons.py::update_person` 두 자리에 있다. `updated_at` 은 브리핑 입력에 그대로 노출되고(`app/briefing/inputs.py:134`, `app/tools/briefing.py:93` `fact.updated_at.isoformat()`), 정렬 기준이며(`inputs.py:101`, `patterns.py:133`, `direct_facts.py:95`), S3.1 이 정의한 열이다. 기존 1808개 테스트 중 "값 변경 뒤 `updated_at` 전진" 을 단언하는 테스트가 없어 그대로 통과했다 — "전체 회귀 통과" 가 이 변경을 보증하지 못한 사례.
- 권장 조치: 두 upsert 의 `set_` 에 `"updated_at": func.now()` 를 명시하고, 서로 다른 트랜잭션 두 번(`now()` 는 트랜잭션 시작 시각이라 한 트랜잭션 안에서는 재현 불가)으로 `updated_at` 전진을 단언하는 회귀 테스트를 `tests/test_upsert_concurrency.py` 또는 `tests/test_memory_promote*.py` 에 추가. 별도 FIX(FIX-026 후보)로 처리.

**[권고] R-20-1 — 네 번째 "조회 후 삽입" 자리가 남았다.** `app/memory/patterns.py:131~168` 은 `person_facts(key="pattern:{type}")` 를 `select … .first()` 뒤 `PersonFact(...)` 로 삽입한다. FIX-020 문서는 "세 곳" 이라 했지만 이 자리는 바꾸지 않았다. UNIQUE 가 생겼으니 동시 경쟁은 중복 행 대신 `IntegrityError`(→ 턴 전체 500, 결정 H 경로)로 드러난다 — 전보다 낫지만 FIX-020 의 완결 주장과 다르다. 같은 ON CONFLICT 패턴으로 통일하거나 문서에 "patterns.py 는 미전환, IntegrityError 로 실패" 를 적을 것.

**[권고] R-20-2 — 중복 인덱스.** 새 UNIQUE 제약이 만드는 유니크 인덱스와 기존 `ix_person_facts_person_id_key`(같은 두 열), `ix_person_aliases_person_id`(유니크 `(person_id, alias)` 의 접두)가 겹친다. 정확성 문제는 아니고 쓰기 비용·저장 공간만. 0003 에서 정리할지 결정.

**[권고] R-20-3 — `expire_all()` 비용과 trace 정확성.** `_upsert_fact` 는 사실 하나마다 세션 전체를 expire 하므로 `_promote_and_trace` 가 들고 있던 `existing_rows` 등 모든 ORM 객체가 다음 접근 때 한 건씩 다시 읽힌다(N+1). `session.expire(obj)` 또는 upsert 뒤 해당 `PersonFact` 만 `refresh` 로 좁힐 수 있다. 또 `action`/`previous_value` 가 잠금 없는 사전 읽기 추정치라 테스트 1 이 `action == "updated"` 와 `previous_value is None` 을 **동시에** 단언한다 — 원칙9 의 trace 근거가 좁은 창에서 부정확해질 수 있음을 문서가 인정하지만, 정확한 이전 값이 필요하면 `RETURNING` 에 `(SELECT value …)` 대신 `DO UPDATE` 전 행을 CTE 로 잡는 방식이 있다. 지금은 문서화된 트레이드오프로 두어도 된다.

**[권고] R-20-4 — 도달 불가 분기.** `app/briefing/inputs.py` 의 `superseded_by_newer` 분기는 테스트가 대체되어(`tests/test_briefing_inputs.py` 265~291행 주석) 실행 증거가 없는 코드로 남았다. 제거하거나 "defense-in-depth, 미도달" 주석을 코드 쪽에도 남길 것.

### FIX-021 · ruff·mypy 기준선·커버리지 (b124c8e, 3e4d67c) — **통과** (소견 [권고] 1)

- CI 변경: `python -m ruff check …` 단계, pytest `--cov=app --cov-branch --cov-report=term`(`[tool.coverage.report] fail_under = 90`), `python scripts/mypy_check.py --run`. 1차 CI(run 37397329951) 실패 → `3e4d67c` 가 `[tool.mypy] python_version = "3.13"` 고정 + 기준선 한 줄(`SupportsTrunc`) 교체로 닫음(run 37397662883 success). 원인 설명(typeshed 문구 차이)과 diff 가 일치한다.
- 부정 확인 증거: `…-0958-fix021-negcheck-ruff.txt` `DTZ005 … app/tools/records.py:49:26`, `…-negcheck-mypy.txt` `[new] … app/embedding.py: [return-value] … exit=1`. 도구가 실제로 잡는다.
- `scripts/mypy_check.py`: 정규식이 `[코드]` 없는 줄을 무시하므로 코드 없는 mypy 오류는 비교 밖(거의 없음). 다중집합(Counter) 비교라 "같은 메시지 1곳 추가" 도 잡는다. `--run` 이 subprocess 로 돌려 pipefail 문제를 피한다. 적절.
- 제품 변경 3건: `compose.py:463` `isinstance(key, str)` 가드(회귀 테스트 `test_validate_briefing_rejects_pattern_sentence_with_unhashable_key`, 수정 전 TypeError 확인 기록) · `persons.py:211` narrowing(동작 동일) · `persons.py:388` `None` 이면 `RuntimeError`(조용한 None 반환 차단). 세 건 모두 정상 입력 동작을 바꾸지 않는다.
- 소견 [권고] R-21-1: B905 로 `zip(..., strict=True)` 를 15곳에 넣었다(`app/` 에는 `app/agent/loop.py:483` 1곳, 모듈 레벨 assert 가 길이를 보증). tests/scripts 의 13곳은 "길이 보장" 판단이 틀리면 운영 스크립트(`scripts/`)에서 `ValueError` 로 드러난다 — 의도된 실패 방향이므로 수용. 다만 `scripts/backfill_embeddings.py` 는 이제 공급자 응답 수가 어긋나면 중단되므로 운영 메모(README/스크립트 docstring)에 한 줄 있으면 좋다.

### FIX-022 · CI matrix·Windows·test-guards — **통과** (소견 [권고] 1)

- 워크플로: `strategy.matrix.python-version: ["3.13","3.14"]`(`fail-fast: false`), `bash .claude/scripts/test-guards.sh` 단계, `windows` job(`windows-latest`, 3.14, `shell: bash`, `-m "not dbtest"` + 같은 skip grep). concurrency 그룹 키가 `github.ref` 하나라 한 run 안의 세 job 은 서로 취소하지 않는다 — run 37399075084 에서 세 job 모두 success(문서 기록과 일치).
- `dbtest` 누락 9건: `tests/test_run_pilot_eval.py` 9곳에 마커 추가(diff). 내 재현 `POSTGRES_PORT=1 … -m "not dbtest"` → `1399 passed, 436 deselected`, skip 0 — Windows job 경로에 DB 접속이 없음을 확인.
- Windows job 에 DB 환경변수가 없어도 `tests/conftest.py` 의 `apply_test_database_env()` 가 접속 없는 순수 계산이라는 설명은 CI success 로 뒷받침된다.
- 소견 [권고] R-22-1: `test-guards.sh` 의 frontmatter YAML 검사는 PyYAML 이 없으면 `skip` 으로 조용히 넘어간다(FIX-022 문서가 스스로 보고). 사용자 메모리("환경 차이로 검사를 수행할 수 없을 때는 통과가 아니라 실패") 와 어긋나는 방향이다. `requirements-dev.txt` 에 `pyyaml` 을 넣거나 CI 에서는 skip 을 실패로 승격할 것(훅 변경이라 별도 승인 대상).

### FIX-023 · 커밋 경계 통합 테스트·CI 마이그레이션 왕복 — **통과** (소견 [권고] 2)

- `tests/test_commit_boundaries.py` 4건: `get_session` 미오버라이드, 요청 뒤 **새 `Session`** 으로 조회(1a·1c), 1b 는 실제 시그니처를 유지한 `add_event` 교체로 게이트를 통과시킨 뒤 `SQLAlchemyError` → 500 `{"detail":{"code":"internal_error"}}`·행 0·trace 0 을 단언(결정 H 264~265행과 일치, 예외 원문 미노출 단언 포함 — security §1). 1d 는 `session_scope()` 로 `run_briefings` 실행 → 실패 일정 `briefed_at IS NULL`·`briefing_compose` trace 는 성공 일정만·`briefing_error` 1행. 가짜 LLM/임베더만 사용(원칙8). 각 테스트 고유 `user_id`/`session_id`, 지정 삭제.
- CI 왕복 단계: `alembic/env.py:54` 가 `DATABASE_URL` 을 읽으므로 스텝 `env:` 의 `…/relationship_test` 가 실제 대상이다(개발 DB `relationship` 은 job env 그대로, 스텝에서만 덮어씀). `0001.downgrade` 는 `vector` 확장을 지우지 않아(`0001` 30·274행) `downgrade base → upgrade head` 가 안전. 로컬 증거 `…-1040-fix023-alembic-roundtrip.txt` 와 run 37400595262 success.
- 소견 [권고] R-23-1: 1d 의 정리 블록이 `if "run_session_id" in locals()` 로 trace 삭제를 조건부로 하는데, `run_session_id = result.session_id` 는 `assert result.errors == 1` **뒤**에 있다. 그 단언이 실패하면 `run_briefings` 가 커밋한 trace 행이 테스트 DB 에 남는다(FIX-019 교훈과 같은 종류). 대입을 단언 앞으로 옮길 것.
- 소견 [권고] R-23-2: 1b 는 "DB 오류 요청은 trace 도 남지 않는다" 를 정상 동작으로 고정한다. 결정 H 가 받아들인 트레이드오프이고 docstring 이 명시하지만, 원칙9 예외 상태가 테스트로 굳는다는 뜻이다. 재결정(예: `loop_error` 만 별도 짧은 트랜잭션으로 기록) 후보로 backlog 에 남겨 두기를 권한다.

### FIX-024 · hypothesis 성질 테스트 — **통과** (소견 [권고] 1)

- `tests/test_properties.py` 20건, `settings(max_examples=60, deadline=None, derandomize=True)`. 성질이 실제 원칙 문장과 대응한다: 단독 신호 1 → 기본 설정에서 `< T_merge`(원칙3·D12 산술 0.5/0.625 로 설명), `band_for` 단조·독립 오라클(경계 1e-6 밖), `decide` 의 `no_candidates`/`llm_failed`/`no_matched`/`out_of_range` 가 merge 로 가지 않음(원칙1·2), 푸시 페이로드 길이·ttl·마커 미노출(문자 집합 분리로 `assume` 없이), 검증기 무예외. 7건 위반을 실제로 찾아 `xfail(strict=True)` 로 고정한 뒤 FIX-025 로 넘긴 흐름은 원칙8("성능 미달도 결과") 에 맞다. 제품 코드 무변경(stat).
- 소견 [권고] R-24-1: `derandomize=True` 는 재현성을 주지만 매 실행 같은 60개 예시만 본다 — 탐색력이 고정된다. 로컬/야간용 `settings.register_profile("explore", derandomize=False, max_examples=500)` 를 두고 CI 는 현재 프로파일을 쓰는 이중 구성을 권한다. 또 푸시 마커 성질은 함수가 `lines`/`pattern_sentences` 를 읽지 않아 구조적으로 참이다(문서도 인정) — 회귀 가드로는 유효하므로 유지.

### FIX-025 · ERConfig 가중치 검증·`validate_briefing` 형태 가드 — **통과** (소견 [권고] 1)

- `app/er/types.py:356` `abs(w_llm + w_emb) <= 1e-9 → InvalidValue`. 기본값(0.8)·기존 테스트 설정 전부 통과(내 전체 실행 1835 passed). 막히는 설정은 `w_rule=1.0` 단독뿐이며 원칙3(3신호 결합)·D12(재정규화 분모 `w_llm+w_emb`) 상 정당한 설정이 아니다. 환경변수 로더 경로도 같은 검증을 탄다(`tests/test_er_confidence.py::test_er_config_rejects_env_weights_with_zero_llm_emb_sum`).
- `app/briefing/compose.py` `_is_valid_basis_shape`: `dict` · `fact_keys` 전부 `str` · `event_ids` 전부 `int`(bool 제외). 파서 `_parse_composed/_parse_line_item`(281~308행)이 이미 **같은 규칙**(304행 `isinstance(raw_id, bool) or not isinstance(raw_id, int)` 거부)으로 정규화하므로 운영 경로의 정상 데이터는 가드에 걸리지 않는다. `tests/test_briefing_compose.py` 무수정 통과가 이를 뒷받침. 패턴 문장 비문자열은 템플릿 문장으로 보강(`missing_pattern` 과 같은 성격) — P6-briefing 검증기 약속(무예외·근거 없는 줄 버림) 과 정합.
- 성질 테스트 전략이 `None`·중첩 리스트·비문자열을 포함하도록 넓어졐고 `test_validate_briefing_never_raises_for_weird_typed_input` 이 그대로 통과(3회 반복 증거 `…-1352-fix025-properties-3x.txt`).
- 소견 [권고] R-25-1: "예외를 던지지 않는다" 약속에 남은 구멍 — `pattern_sentences` 원소가 dict 가 아니면 `entry.get("key")` 에서 `AttributeError`. 검증자 탐침(2026-10-06): `ComposedBriefing(pattern_sentences=[None], …)` → `AttributeError: 'NoneType' object has no attribute 'get'`, `["abc"]` → `'str' object has no attribute 'get'`. 타입 주석(`list[dict]`)을 어기는 입력이고 `_parse_composed` 가 운영 경로에서 걸러 주므로 우선순위는 낮다. `isinstance(entry, dict)` 가드 한 줄을 넣거나 docstring 에 "원소는 dict 여야 한다" 전제를 적을 것. 성질 전략(`_pattern_sentence_strategy`)도 `st.none()`/`st.text()` 원소를 섞으면 자동으로 잡힌다.

## 2. 공통 소견

**[권고] R-공통-1 — 계획 검증 절차(L-002) 미이행.** 여덟 FIX 문서의 `검증: 통과(점검표 1~8 …)` 줄은 카드 인용 없이 메인 세션이 썼다. FIX-020 처럼 제품 코드·스키마를 바꾸는 FIX 는 02-plan-verify 와 같은 8행 점검표(카드 파일명 + 인용)를 verifier 가 쓰는 것이 규칙이다. 이 검토가 사후 보정이지만, FIX 템플릿의 `검증:` 줄에 `검증자: verifier` 를 요구하도록 `verify-plan.sh` 류 기계 검사를 FIX 문서에도 적용하는 것을 권한다. F-20-1 은 바로 그 절차가 있었다면 "D 카드·S 카드 코드에서 지켜야 할 것 — `updated_at` 의미" 행에서 걸릴 수 있던 종류다.

작업 트리 참고: 검토 시작 시 `docs/wiki/journal.md` 가, 검토 중 `docs/wiki/HANDOFF.md` 가 미커밋 변경 상태였다(검증자가 만든 것은 `docs/wiki/fixes/evidence/20261006-1429-review-fix020-updated-at.txt` 와 이 문서뿐).

## 3. [필수] 소견 목록

| ID | FIX | 내용 | 재현 | 권장 조치 |
|---|---|---|---|---|
| F-20-1 | FIX-020 | `_upsert_fact`/`update_person` 의 `ON CONFLICT DO UPDATE` 가 `updated_at` 을 갱신하지 않음(SQLAlchemy `onupdate` 미적용) → 값이 바뀌어도 `person_facts.updated_at` 정지. 브리핑 노출·정렬 기준 열. | `evidence/20261006-1429-review-fix020-updated-at.txt`(스크립트 본문 포함, 테스트 DB) | 두 `set_` 에 `"updated_at": func.now()` 추가 + 트랜잭션 2회 회귀 테스트. 별도 FIX. |

## 4. 결론

여덟 건 중 일곱 건은 증거·diff·CI 가 주장과 일치해 **통과**(권고 소견만), FIX-020 은 동시성 목표는 달성했으나 `updated_at` 갱신 회귀 **[필수] 1건**으로 **소견 있음** — F-20-1 을 별도 FIX 로 닫기 전에는 FIX-018~025 묶음을 `dev` 로 승격하지 않기를 권한다.
