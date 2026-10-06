# review-FIX-026 · 커밋 전 코드 리뷰 — 사실 `updated_at` 갱신 회귀(F-20-1) + 패턴 사실 ON CONFLICT(R-20-1)

검토자: verifier (fable) · 2026-10-06 · 대상: 작업 트리 미커밋 diff(HEAD `3cd378c` 기준) | Refs: FIX-026 FIX-020 S3.1 S3.5 D14 P6-memory 원칙9

**판정: 통과** — [필수] 0건, [권고] 4건(R-26-1~R-26-4). 코드는 고치지 않았다.

## 1. 본 것

- diff: `app/memory/promote.py`(+13/−1) · `app/tools/persons.py`(+27/−2) · `app/memory/patterns.py`(+90/−30) · `scripts/mypy_baseline.txt`(+1/−0) · `tests/test_upsert_concurrency.py`(+131/−13) · 신규 `tests/test_fact_updated_at.py`(4 테스트).
- 문서: `docs/wiki/fixes/FIX-026.md`, 출발점 `docs/wiki/fixes/review-FIX-018-025.md` F-20-1(51~55행)·R-20-1(57행).
- 구현자 증거: `docs/wiki/fixes/evidence/20261006-fix026-{before,after,concurrency-3x,full,ruff,mypy,test-guards}.txt`, `20261006-1429-review-fix020-updated-at.txt`.
- 비교 원문: FIX-020 이전 ORM 코드 `git show 7459925^:app/memory/promote.py`(135~200행) · `git show 7459925^:app/tools/persons.py`(547~569행), FIX-026 이전 `git show HEAD:app/memory/patterns.py`(128~230행).
- 카드: `specs/S3.1-schema-v2.md` 8행(`person_facts(... updated_at)`)·25행(FIX-020 보충), `specs/S3.5-memory-promotion.md` 7~8행, `decisions/D14-pattern-window-config.md` "코드에서 지켜야 할 것" 10~14행.

## 2. 내가 직접 실행한 것(증거 파일)

| 명령 | 결과 | 증거 |
|---|---|---|
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | `1840 passed, 1 warning in 21.52s`(skip 0; 기준선 1835 + 신규 5) | `evidence/20261006-review-fix026-pytest-full.txt` |
| 새 테스트 2파일 5회 반복(`-p no:cacheprovider`) | 5회 모두 `8 passed` | `evidence/20261006-review-fix026-newtests-5x.txt` |
| `.venv/bin/ruff check app tests scripts evaluation` | `All checks passed!` exit 0 | `evidence/20261006-review-fix026-ruff-mypy.txt` |
| `.venv/bin/python scripts/mypy_check.py --run` | `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` exit 0 — `[info] 기준선에 있었지만 이번엔 없는 오류` 줄이 없으므로 기준선과 현재가 다중집합으로 **정확히 일치** | 같은 파일 |
| ORM 동작·새 코드 분기 직접 재현(테스트 DB `relationship_test`, 스크립트 본문은 scratchpad `verify_fix026_orm.py`, 만든 행은 finally 삭제) | 아래 §3 | `evidence/20261006-review-fix026-orm-repro.txt` |

재현 스크립트 출력(원문):
```
확인1 dirty?: True
확인1 UPDATE 문 발행 수: 0 | updated_at 유지?: True
확인2 UPDATE 문 발행 수: 1 | updated_at 전진?: True
확인3 (conf 0.5 → 같은 값 재저장) updated_at 전진?: True | confidence 복원?: True | value: 등산
확인3b (둘 다 같음) updated_at 유지?: True
확인4a 첫 실행 actions: [('meal', 'created')]
확인4b 변화 없는 재실행 changes: [] | updated_at 유지?: True
확인4c 이벤트 추가 후 action: ['updated'] | previous_value 3회?: True | value 4회?: True | updated_at 전진?: True | 링크 3→4?: (3, 4)
확인4d 기준 미달 actions: [('meal', 'deleted', '4회 (...)')] | 행 남음?: False
```

## 3. 판정 기준별 근거

### 3.1 F-20-1 이 닫혔는가 — 통과

- **`_upsert_fact`(promote.py 193~196행)**: `"updated_at": case((PersonFact.value == fact.value, PersonFact.updated_at), else_=func.now())`. FIX-020 이전 ORM 코드(`7459925^` 167~181행)는 `existing.value == fact.value` 면 `.value`/`.confidence` 를 건드리지 않아 UPDATE 가 없었고(→ `updated_at` 유지), 다르면 둘을 대입해 UPDATE(→ `onupdate` 전진). CASE 조건이 그 분기와 1:1 로 대응한다. 기존 `confidence` CASE(181~184행)와 같은 조건이라 일관.
- **`update_person`(persons.py 622~634행)**: `and_(PersonFact.value == normalized_value, PersonFact.confidence == DEFAULT_FACT_CONFIDENCE)` 일 때만 유지. 이전 ORM 코드(`7459925^` 558~560행)는 분기 없이 두 속성을 항상 대입했으므로 유지/전진은 SQLAlchemy 유닛오브워크가 결정한다. FIX-026.md "같은 값 재저장" 절의 실험 주장 2건을 **내가 `before_cursor_execute` 리스너로 UPDATE 문 수를 세어 재확인**했다: 확인1(두 속성 모두 같은 값 대입 → `session.dirty` 는 True 이지만 **UPDATE 0건**, `updated_at` 유지), 확인2(값 같고 `confidence` 만 다름 → **UPDATE 1건**, 전진). SQLAlchemy `persistence._collect_update_commands` 가 커밋 상태와 `is_equal` 인 속성을 params 에서 빼고 params 가 비면 UPDATE 를 내지 않는 동작과 일치한다. 따라서 AND 조건이 옛 동작의 정확한 재현이다. 새 코드의 AND **else 분기**(저장된 confidence ≠ DEFAULT)도 확인3 으로 직접 검증: `updated_at` 전진 + `confidence` 가 DEFAULT 로 복원.
- **테스트의 트랜잭션 분리**: `tests/test_fact_updated_at.py` 는 `db_engine` 으로 `Session` 을 직접 만들어 `session.commit()` 두 번 사이에 upsert 한다(85~95행). 첫 upsert 의 `now()` 는 T1 시작, 두 번째 upsert 는 커밋 뒤 자동 시작된 T2 의 `now()` 이므로 한 트랜잭션 `now()` 함정에 걸리지 않는다. 수정 전 FAILED(`evidence/20261006-fix026-before.txt`: `assert ... 05:44:56.861818 > ... 05:44:56.861818`) → 수정 후 passed 이므로 실패 조건을 실제로 검사한다(항상 통과 테스트 아님). 단 `time.sleep` 위치는 R-26-3.

### 3.2 R-20-1 — 통과

- 전환 전후 diff 로 분기 보존 확인: 삭제 분기(`len(items) < min_count` → `session.delete(existing)` → `action="deleted"`, `previous_value` 보존) 는 변수명만 바뀌고 로직 동일(patterns.py 167~181행). `fact_sources` 교체(`to_add`/`to_remove` 집합 차, stale 링크 `session.delete`) 는 `existing.id` → `fact_id` 치환만(234~276행). `PatternChange` 반환: `inserted`(RETURNING `(xmax = 0)`) 면 `created`, 값·링크 중 하나라도 바뀌면 `updated`(이전 값 = 사전 조회 `existing.value`), 둘 다 그대로면 `changes` 에 넣지 않음 — 확인4a~4d 로 네 경로 모두 실측(created / 변경 없음 `[]` + `updated_at` 유지 / updated + 링크 3→4 + `updated_at` 전진 / deleted).
- `updated_at` CASE 는 `value` 비교 하나(220~223행). 패턴 사실의 `confidence` 는 상수 `_PATTERN_CONFIDENCE = 1.0` 이고 이전 ORM 코드도 `.value`·`.confidence(=1.0)` 를 대입했으므로 "값 같음 ⇒ 두 속성 모두 같음 ⇒ UPDATE 없음" — `update_person` 과 달리 AND 가 필요 없다. 일관.
- **`session.expire(existing)` 범위(230행)**: `app/db/models.py` 에 `relationship()` 이 하나도 없어(grep 0건) 이 세션이 그 행을 들고 있는 ORM 인스턴스는 식별자 맵의 `existing` 하나뿐이다 — 다른 쿼리로 같은 행을 받았더라도 같은 인스턴스를 돌려받으므로 expire 가 그것을 덮는다. `existing is None` 인데 충돌로 UPDATE 된 경우(동시성 테스트 시나리오) 는 이 세션에 그 행의 인스턴스가 아예 없어 stale 객체가 생길 수 없다. 안전하다.
- **동시성 테스트**(`test_detect_patterns_concurrent_connections_result_in_one_row`): B 가 0.5초 뒤에도 살아 있음(유일 인덱스 블로킹) → A 커밋 → B 가 `_WAIT_TIMEOUT=5.0` 안에 끝남 → 오류면 `pytest.fail`(수정 전 `IntegrityError ... uq_person_facts_person_id_key` 로 FAILED 확인, before.txt) → 행 1개·`3회` 로 시작. 수정 후 구현자 3회 + 내 5회 반복 모두 통과. 정리는 `FactSource → PersonFact → Event → AgentTrace(세션 2개) → Person` 순으로 FK 를 지키며, `finally` 에서 두 세션·커넥션을 먼저 닫아 B 가 막혀 있어도 풀린다.

### 3.3 회귀·기준선·절차

- 회귀: §2 표(1840 passed skip 0 · ruff 0 · mypy ok). 커버리지는 구현자 증거 `20261006-fix026-full.txt` 95.30%(내 실행은 `--cov` 없이 돌렸으므로 수치는 옮기지 않는다).
- mypy 기준선 +1(`app/memory/patterns.py: [var-annotated] Need type annotation for "stmt"`): 같은 메시지 선례가 `scripts/mypy_baseline.txt` 25행(`app/memory/promote.py`)·28행(`app/push/subscriptions.py`)에 있고 세 자리 모두 `pg_insert(...).values(...).on_conflict_do_update(...).returning(...)` 체인이다. `git diff --numstat` = `1 0`, `--run` 이 `[info]`(사라진 항목) 없이 38=38 → 다른 항목이 바뀌지 않았음을 기계로 확인. 정당하다.
- 절차 소견은 R-26-4.

### 3.4 정합성·보안

- 원칙: 자동 병합·임계치·ER·화면·제외 범위(원칙7) 와 무관한 저장 계층 수정. 원칙9 trace — `PatternChange`/`PromotedFact` 의 action·previous_value 의미 불변(§3.2). D14 "패턴 판정에 LLM 을 쓰지 않는다 / 설정값 / 창" 불변(판정 로직 미변경, 저장 문장만 교체).
- S3.1 8행 `person_facts(..., updated_at)` — "갱신 시각" 의미를 FIX-020 이전과 같게 되돌린 것이 이 FIX 의 목적이며, 스키마·리비전 변경 없음(`alembic` 무관). S3.5 7~8행(upsert·패턴 규칙) 그대로.
- 보안: diff 에 키·비밀 문자열 없음(정규식 스캔 0건). 증거 파일의 DB URL 은 `app:***` 로 가려져 있다. 개발 DB 미접촉 — 내 스크립트는 `apply_test_database_env()` 로 `relationship_test` 만 사용(`assert test.endswith("_test")`).

## 4. 소견

### [필수]
없음.

### [권고]

- **R-26-1 — `patterns.py` 의 "변경 없음 = DB 를 쓰지 않는다" 문구가 더는 글자 그대로 참이 아니다.** 모듈 docstring 66행("값·링크 모두 그대로면 DB 를 쓰지 않고") 와 260행 주석("DB 를 건드리지 않고") 은 FIX-026 이전 동작이다. 지금은 `INSERT ... ON CONFLICT DO UPDATE` 가 분기 **전에** 항상 실행되어, 값이 같아도 동일 값으로 UPDATE(행 잠금 + 새 튜플 버전)가 나간다. 관측 가능한 상태(`value`·`confidence`·`updated_at`·`changes[]`)는 그대로임을 확인4b 로 확인했으니 결함은 아니지만, 문구를 "값·링크 모두 그대로면 **상태 변화가 없고** `changes` 에도 넣지 않는다(upsert 문 자체는 나간다)" 로 맞출 것.
- **R-26-2 — `update_person` AND 조건의 else 분기(저장된 confidence ≠ DEFAULT, 값은 같음)를 고정하는 테스트가 없다.** 이번 리뷰에서 직접 재현(확인3: 전진 + confidence 복원)했지만, 테스트 스위트에는 "둘 다 같음 → 유지"와 "값 다름 → 전진" 만 있다. `tests/test_fact_updated_at.py` 에 confidence 를 0.5 로 미리 바꿔 둔 뒤 같은 값을 재저장하는 케이스 1건을 추가하면 AND 가 필요했던 이유가 테스트로 남는다.
- **R-26-3 — `time.sleep(_SLEEP)` 위치.** 네 테스트 모두 `t1` SELECT(커밋 직후 autobegin → T2 시작) **뒤에** sleep 한다. T2 의 `now()` 는 T2 시작 시각이므로 sleep 은 T1·T2 시작 간격을 벌리지 못한다. 그래도 T2 시작 > T1 커밋 > T1 시작이라 `t2 > t1` 은 성립하고(5회 반복 통과), "유지" 테스트는 영향이 없다. 다만 주석(53행 "커밋 사이 시각 차이를 보장")이 실제 효과와 다르다 — sleep 을 `t1` SELECT 앞으로 옮기거나 SELECT 뒤 `session.commit()` 으로 T2 를 닫고 upsert 를 새 트랜잭션에서 시작하면 의도가 코드와 맞는다.
- **R-26-4(절차) — `scripts/mypy_check.py --update-baseline` 을 Bash 로 실행해 저장소 파일 `scripts/mypy_baseline.txt` 를 덮어썼다(1차는 `--run` 누락으로 0건 기준선이 되었다가 Write 로 복구).** 프로젝트 규칙(CLAUDE.md "파일 변경은 Write/Edit 툴로만", 2026-09-29)에 어긋나며 `stage-gate.sh`·`secret-guard.sh` 를 거치지 않았다. 최종 내용은 내가 독립 확인했다(§3.3: +1/−0, 38=38 정확 일치)므로 이번 커밋을 막을 사유는 아니지만, journal 에 이미 적힌 대로 절차 위반으로 남기고, 앞으로는 `--update-baseline` 출력을 scratchpad 경로로 받아 Write 로 옮기거나 스크립트에 `--output <path>` 옵션을 두는 쪽(하네스 변경, 승인 먼저)을 권한다. 덧붙여 이번 제품 코드 쓰기는 `CURRENT.md active: P7-push` 아래에서 통과했으므로 `stage-gate.sh` 의 FIX 분기(`검증: 통과` 요구)는 FIX-026 에 대해 실행되지 않았다 — review-FIX-018-025 R-공통-1 과 같은 구조적 문제이며, "제품 코드 FIX 는 커밋 전 verifier 리뷰" 규칙을 `/devlog fix` 에 반영할 때 함께 다룰 것.

## 5. 결론

F-20-1 은 세 저장 자리(`_upsert_fact`·`update_person`·`detect_patterns`) 모두에서 FIX-020 이전 ORM 동작과 같은 조건으로 닫혔고, R-20-1 은 삭제·링크 교체·반환값을 보존한 채 ON CONFLICT 로 전환되었다. 수정 전 FAILED → 수정 후 passed 가 증거로 남아 있고, 전체 회귀·ruff·mypy 를 내가 재실행해 일치했다. **통과** — `FIX-026.md` 의 `검증:` 줄을 이 문서로 갱신한다. [권고] 4건은 커밋을 막지 않으며 다음 작업 단위에서 닫을 것.
