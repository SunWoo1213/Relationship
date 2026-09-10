# P1-pilot-dataset · 완료 검토 (04-review)

날짜: 2026-09-10 | 검토자: verifier (fable) — 구현자(eval-agent, opus)와 다른 모델·새 컨텍스트(L-002). 코드·데이터·계획·카드·registry·backlog·review-index·CURRENT 는 고치지 않았다. 이 문서·05-remediation(F-14f3ef 해결 단계·재검증 칸)·03-log 검토 항목 1개·`evidence/20260910-*` 만 썼다.

검토 대상: HEAD `f78e9dc`(dev). 01-plan(U1~U7 전부 `[x]`, 결정 A~G·H-1~H-3·I~P) · 02-plan-verify(통과, 권고 R-4~R-12) · 03-log 12 항목(착수 4c80c31, U1 1e1320c, U2 09875aa, FIX baee71e, U3 aa6ecfc, U4 6775463, U5 40c36f8, U6 76add8a, U6-2 6906af4, U6-3 aeed0bd, U7 f78e9dc) · 05-remediation 소견 4(해소 3·열림 1) · evidence 63 파일 · 데이터 `data/scenarios/` 8파일 · `scripts/validate_scenarios.py`·`scripts/dump_scenarios.py`·`tests/test_validate_scenarios.py`. 라벨 자체는 재해석하지 않았다(R-3 — 검수는 `evidence/20260906-1938-label-review.md` 4차까지로 닫혔다).

증거 재사용: 이전 verifier 세션(2026-09-06 21:52~21:56)이 남긴 `evidence/20260906-2152-*` 16 파일은 모두 HEAD `f78e9dc` 에서 실행된 것이고(`-review-acceptance.txt` 머리 줄 `HEAD f78e9dc44c…`, `git status --porcelain -- data/ scripts/ tests/` 빈 출력) 이후 `data/`·`scripts/`·`tests/` 커밋이 없으므로(`gitlog.sh P1-pilot-dataset` 최신 커밋 = f78e9dc) 그대로 증거로 쓴다. 이 세션에서 새로 만든 것은 `20260910-0934-review-scope.txt`(범위 대조)와 `20260910-0938-review-verify-impl-final.txt`(최종 기계 검증, verify-impl.sh 가 함께 만든 `20260910-0938-{pytest,lint,commits,summary}.txt` 포함) 뿐이다.

## 1. 기계 검증 출력 (그대로 붙인다)

### 1a. 사전 실행 (04-review 작성 전, 2026-09-06 21:52 — 이전 verifier 세션)
명령: `bash .claude/scripts/verify-impl.sh P1-pilot-dataset | tee docs/wiki/packages/P1-pilot-dataset/evidence/20260906-2152-verify-impl.txt`
```
== verify-impl P1-pilot-dataset  (20260906-2152) ==
ssssssssssssssssssssssssss.............................................. [ 92%]
...................................                                      [100%]
317 passed, 150 skipped in 18.46s
PASS  pytest 통과 → evidence/20260906-2152-pytest.txt
PASS  compileall 통과 → evidence/20260906-2152-lint.txt
PASS  태그 P1-pilot-dataset 커밋 13 건 → evidence/20260906-2152-commits.txt
PASS  커밋에 태그 존재: D1
PASS  커밋에 태그 존재: D10
PASS  커밋에 태그 존재: D3
PASS  커밋에 태그 존재: D6
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.7
WARN  04-review.md 없음 (완료 검토 전이면 정상)
PASS  registry 에 P1-pilot-dataset 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=1 → evidence/20260906-2152-summary.txt ==
```
- WARN 1 은 04-review.md 부재(이 문서 작성 전) — `findings.py` 가 **F-14f3ef** 로 올렸고 원인 분석까지 verifier 가 채웠다. 아래 1b 최종 실행으로 해소 여부를 본다.
- pytest `150 skipped` 는 DB 포트 없는 환경에서 P1-schema·P2-tools·P3-er 의 DB 테스트가 skip 되는 하네스 한계(HANDOFF 기록)이며 이 패키지의 대상 테스트는 `tests/test_validate_scenarios.py` 69건이다 — `evidence/20260906-2152-review-acceptance.txt` 의 `python -m pytest tests/test_validate_scenarios.py -q -rs` → `69 passed in 1.43s`, skip 0.
- `evidence/20260906-2152-commits.txt` 13건 중 11건이 이 패키지(4c80c31~f78e9dc), 2건(b676799 P2-tools·5dc95bb P1-schema)은 커밋 본문이 P1-pilot-dataset 을 언급해 `--grep` 에 잡힌 것 — 이 패키지 변경 아님.

### 1b. 최종 실행 (04-review 작성 후)
명령: `bash .claude/scripts/verify-impl.sh P1-pilot-dataset | tee docs/wiki/packages/P1-pilot-dataset/evidence/20260910-0938-review-verify-impl-final.txt`
```
== verify-impl P1-pilot-dataset  (20260910-0938) ==
ssssssssssssssssssssssssss.............................................. [ 92%]
...................................                                      [100%]
317 passed, 150 skipped in 27.01s
PASS  pytest 통과 → evidence/20260910-0938-pytest.txt
PASS  compileall 통과 → evidence/20260910-0938-lint.txt
PASS  태그 P1-pilot-dataset 커밋 13 건 → evidence/20260910-0938-commits.txt
PASS  커밋에 태그 존재: D1
PASS  커밋에 태그 존재: D10
PASS  커밋에 태그 존재: D3
PASS  커밋에 태그 존재: D6
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.7
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  파일럿 데이터셋 30~50건 — `scripts/vali ← evidence/20260906-2152-review-acceptance
PASS  증거 확인:  (승진·대명사·별칭·정상·신규) — ` ← evidence/20260906-2152-review-acceptance
PASS  증거 확인:  `data/scenarios/` JSON — 해당 디렉터리에 ← evidence/20260906-2152-review-acceptance
PASS  증거 확인:  라벨 검수 완료 — `evidence/<ts>-label-rev ← evidence/20260906-2152-review-acceptance
PASS  registry 에 P1-pilot-dataset 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=0 → evidence/20260910-0938-summary.txt ==
```
- 최종 FAIL 0 / WARN 0. `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python .claude/scripts/findings.py P1-pilot-dataset docs/wiki/packages/P1-pilot-dataset/evidence/20260910-0938-review-verify-impl-final.txt --source verify-impl` → `05-remediation.md 갱신: 새 소견 0, 해소 1, 열림 0 (필수 0)` / `✓ F-14f3ef  해소`. 05-remediation 머리 줄 `열림: 0 (필수 0) | 해소: 4`. **열린 [필수] 소견 0.**

## 2. 수용 기준 대조
증거 열은 `evidence/` 파일, 커밋 해시(7자 이상), 존재하는 파일 경로 중 하나여야 한다(`verify-impl.sh` 가 실재를 검사한다). 문장만 있는 증거는 FAIL.

backlog 23행 원문(권위, 글자 그대로): **"파일럿 데이터셋 30~50건 (승진·대명사·별칭·정상·신규) / 의존: 평가 명세(resolution-plan 3.7) / 수용기준: `data/scenarios/` JSON, 라벨 검수 완료"**. 01-plan 50~58행이 이 문장을 4개의 기계 판정으로 나눴고(문장 자체는 바꾸지 않음), 아래 표는 그 4문장 각각이다. 모든 값은 HEAD `f78e9dc` 에서 재실행한 `evidence/20260906-2152-review-acceptance.txt` 의 출력이다(U7 의 `evidence/20260907-1300-u7-acceptance.txt` 는 aeed0bd 기준 — 값 동일).

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| 파일럿 데이터셋 30~50건 — `scripts/validate_scenarios.py` 가 세는 총 시나리오 수가 30 이상 50 이하(계획값 40) | evidence/20260906-2152-review-acceptance.txt (`--strict --json` → `"scenario_count": 40`, `"total": 40`, `"ok": true`; `--strict` → `== 결과: 시나리오 40건 / 오류 0 ==`), data/scenarios/manifest.json, f78e9dc | 통과 — 40 ∈ [30, 50] |
| (승진·대명사·별칭·정상·신규) — `category` 5종이 모두 1건 이상이며 배분표가 `manifest.json` 과 일치 | evidence/20260906-2152-review-acceptance.txt (`"counts": {"alias": 8, "new_person": 6, "normal": 10, "promotion": 8, "pronoun": 8}`, `[PASS] (6) manifest counts·total 일치`, `[PASS] (11) 파일명 <-> category 일치`), data/scenarios/promotion.json, data/scenarios/pronoun.json, data/scenarios/alias.json, data/scenarios/normal.json, data/scenarios/new_person.json | 통과 — 5종 각 ≥ 1, 합 40 = total |
| `data/scenarios/` JSON — 해당 디렉터리에 스키마 검증을 통과하는 JSON 파일이 존재(rc=0 출력이 evidence 에 있다) | evidence/20260906-2152-review-acceptance.txt (`$ python scripts/validate_scenarios.py --strict` → `[PASS] (0)`~`[PASS] (15)` 16행, `rc=0`; `ls data/scenarios` 8파일; `md5sum data/scenarios/*.json` 8행), data/scenarios/schema.json, data/scenarios/manifest.schema.json, evidence/20260906-2152-pytest.txt, evidence/20260906-2152-lint.txt | 통과 — rc=0, 검사 16항목 PASS, `69 passed` |
| 라벨 검수 완료 — `evidence/<ts>-label-review.md` 머리 줄에 eval-agent 가 아닌 검수자 이름이 있고, 지적 표의 `열림` 상태가 0 이며 반영 상태에 U6 커밋 해시가 있다 | evidence/20260906-2152-review-acceptance.txt (`sed -n 3p` → `검수자: verifier (fable, 새 컨텍스트) | 표본: 40/40 | 사용자 검수: 함정 12건·new_person 지나가는 언급 3건`; `grep -cE '\| *열림 *\|'` → `0`; 반영 셀 `21`·기각 셀 `1`; 271행 `사용자가 **12/12 동의**`), evidence/20260906-1938-label-review.md, 76add8a, 6906af4, aeed0bd, f78e9dc | 통과 — 검수자 ≠ eval-agent, 열림 0, 반영 21 건의 해시가 U6·U6-2·U6-3 커밋 |

검토자가 이 세션에서 다시 센 값(2026-09-10, HEAD f78e9dc): `grep -cE '\| *열림 *\|'` = 0, `^\| *[0-9]+ \|.*\| *반영 ` = 21, `기각 ` = 1 — evidence 와 일치. 데이터 md5 는 `-review-acceptance.txt` 의 8행과 같은 파일이며 이후 `data/` 커밋 없음.

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)

모두 이전 verifier 세션이 **저장소 원본을 건드리지 않고 scratchpad 복사본만 변이**시켜 `python scripts/validate_scenarios.py --strict --dir <복사본>` 을 직접 실행한 출력이다(각 파일 2행 "저장소 원본 data/scenarios 무수정 — 복사본만 변이"). 변이 8종은 오류 ≥ 1 이면서 **기대한 검사 번호의 FAIL 코드**가 나와야 하고, 대조군(무변이 복사본)은 오류 0 이어야 한다 — 대조군이 없으면 "복사본이라서 실패했다"를 배제할 수 없다.

| 케이스 | 명령 (변이 내용) | 증거 | 마지막 결과 줄 | 기대 검사·코드 | 판정 |
|--------|------------------|------|----------------|----------------|------|
| a-total | manifest.total 40→41 | evidence/20260906-2152-review-negative-a-total.txt | `== 결과: 시나리오 40건 / 오류 1 ==` rc=1 | (6) `TOTAL_MISMATCH manifest=41 실제=40` | 검출 |
| b-orphan | sc-001 mentions[0].gold_person_id p1→p9(persons 에 없음) | evidence/20260906-2152-review-negative-b-orphan.txt | `== 결과: 시나리오 40건 / 오류 1 ==` rc=1 | (2) `GOLD_ID_ORPHAN` | 검출 |
| c-null | sc-001 mentions[0].gold_person_id → null (ambiguous 없음) | evidence/20260906-2152-review-negative-c-null.txt | `== 결과: 시나리오 40건 / 오류 1 ==` rc=1 | (2) `GOLD_NULL_NOT_AMBIGUOUS` (H-1) | 검출 |
| d-surface | sc-001 mentions[0].surface 김팀장→박팀장(발화에 없음) | evidence/20260906-2152-review-negative-d-surface.txt | `== 결과: 시나리오 40건 / 오류 1 ==` rc=1 | (12) `SURFACE_NOT_IN_UTTERANCE` | 검출 |
| e-overlap | sc-038 passing_mentions[1].surface → 다인이(turn 2 mention 과 겹침) | evidence/20260906-2152-review-negative-e-overlap.txt | `== 결과: 시나리오 40건 / 오류 1 ==` rc=1 | (15) `PASSING_MENTION_OVERLAP` | 검출 |
| f-category | promotion.json sc-001 category promotion→normal | evidence/20260906-2152-review-negative-f-category.txt | `== 결과: 시나리오 40건 / 오류 3 ==` rc=1 | (11) `FILE_CATEGORY_MISMATCH` + (6) `COUNT_MISMATCH` ×2(normal 10→11, promotion 8→7) | 검출 — 부수 오류 2 는 같은 변이의 필연적 결과 |
| g-short | sc-001 utterances[3] → '부장님이 밥사'(7자) | evidence/20260906-2152-review-negative-g-short.txt | `== 결과: 시나리오 40건 / 오류 1 ==` rc=1 | (13) `UTTERANCE_LENGTH 길이 7자 가 규칙(8~60자) 밖` | 검출 |
| h-name | sc-001 persons[0].display_name 김민준→홍길동(virtual_names 밖) | evidence/20260906-2152-review-negative-h-name.txt | `== 결과: 시나리오 40건 / 오류 1 ==` rc=1 | (7) `NAME_NOT_IN_VIRTUAL_NAMES` | 검출 |
| z-control | 무변이 복사본(대조군) | evidence/20260906-2152-review-negative-z-control.txt | `== 결과: 시나리오 40건 / 오류 0 ==` rc=0 | 없음 | 오류 0 — 복사·`--dir` 경로 자체는 실패 원인이 아님 |

- 8/8 변이가 기대 검사 번호의 FAIL 코드로 잡혔고 대조군은 0. U1 의 완료 판정 "위반 표본 8종을 전부 잡는다"(01-plan 42행)가 **저장소 실데이터 위에서도** 성립한다(테스트는 합성 fixture 위에서 같은 코드를 검사 — `evidence/20260910-0934-review-scope.txt` 마지막 절, `assert "<CODE>" in codes` 19종: 위 8종 코드 전부 포함 + `AMBIGUOUS_COUNT_MISMATCH`·`TRAP_COUNT_MISMATCH`·`SEED_PERSON_UNKNOWN`·`DUPLICATE_ID`·`TURN_OUT_OF_RANGE`·`EVENT_TYPE_UNKNOWN` 등).
- 항상 통과하는 테스트인지: `evidence/20260906-1801-u1-validate-empty.txt`(시나리오 0건에서 rc=0)와 위 변이(오류 ≥1, rc=1)가 같은 검증기의 양쪽 결과다 — rc 가 입력에 따라 바뀐다. 05-remediation F-7bea05·F-1ba055 는 U1 테스트가 시점에 고정돼 있던 결함을 baee71e 가 고친 기록이며 지금 테스트는 tmp fixture 만 쓴다.
- 범위 부정 케이스(01-plan "하지 않는 것"): `evidence/20260910-0934-review-scope.txt` — `git diff --stat 4c80c31..f78e9dc -- app/ alembic/ reports/` **빈 출력**(제품 코드·마이그레이션·평가 산출물 무변경), 저장소 변경 파일은 `README.md`·`data/scenarios/*`·`requirements-dev.txt`(jsonschema 4.26.0, 런타임 requirements 아님)·`scripts/{validate,dump}_scenarios.py`·`tests/test_validate_scenarios.py`·`docs/wiki/**` 뿐. `validate_scenarios.py`·`dump_scenarios.py` 에 네트워크·DB·`app` import 없음(grep 일치 0). 단 `tests/test_validate_scenarios.py:33` 은 `from app.db.models import EVENT_TYPES, HIERARCHIES, QUESTION_KINDS, RELATION_TAGS` 로 **읽기 import** 한다 — `app/` 수정이 아니므로 "하지 않는 것" 위반은 아니나 registry 105행 문구와 어긋난다(§6 관찰 2).

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
- **이 패키지가 닫는 R 은 없다.** 01-plan 3행 "닫는 검증: 없음(INDEX.md 패키지 표의 '닫는 R' 열이 `—`. 이 패키지는 R 을 닫지 않고 R3·R4 를 닫는 P4-pilot-eval 의 입력을 만든다)" · `docs/wiki/INDEX.md` 65행 `| P1-pilot-dataset | 파일럿 데이터셋 30~50건 | eval-agent | — |` · `docs/wiki/review-index.md` 표에 P1-pilot-dataset 을 "다음 카드"로 가진 행 없음(`grep -n 'P1-pilot' review-index.md` 일치 0).
- 따라서 메인 세션이 review-index 에서 바꿔야 할 R 행: **없음**. R3(상태 `해소(문서)`)·R4(`구현완료(b1f2782 …)`, 실호출 미검증) 는 P4-pilot-eval 이 파일럿 수치로 닫는다 — 이 데이터셋이 그 입력이다.

## 5. registry.md 에 올린 산출물
`docs/wiki/registry.md` 95~106행, `grep -c 'P1-pilot-dataset'` = 12(evidence/20260906-2152-review-registry.txt 마지막 줄). 커밋 열 대조는 같은 evidence 의 `git log --oneline -- <경로>` 출력이다.

| # | 종류 | 경로 | 존재 | registry 커밋 열 | git log 와 일치 |
|---|------|------|------|------------------|-----------------|
| 1 | 데이터셋 | data/scenarios/schema.json | yes | 1e1320c 40c36f8 76add8a 6906af4 aeed0bd | 일치(5/5) |
| 2 | 데이터셋 | data/scenarios/manifest.schema.json | yes | 1e1320c 40c36f8 | 일치(2/2) |
| 3 | 데이터셋 | data/scenarios/manifest.json | yes | 1e1320c 09875aa aa6ecfc 6775463 40c36f8 76add8a 6906af4 aeed0bd | 일치(8/8) |
| 4 | 데이터셋 | data/scenarios/promotion.json | yes | 09875aa 76add8a 6906af4 | 일치(3/3) |
| 5 | 데이터셋 | data/scenarios/alias.json | yes | 09875aa 76add8a 6906af4 | 일치(3/3) |
| 6 | 데이터셋 | data/scenarios/pronoun.json | yes | aa6ecfc 76add8a | 일치(2/2) |
| 7 | 데이터셋 | data/scenarios/normal.json | yes | aa6ecfc 76add8a aeed0bd | 일치(3/3) |
| 8 | 데이터셋 | data/scenarios/new_person.json | yes | 6775463 40c36f8 76add8a 6906af4 | 일치(4/4) |
| 9 | 스크립트 | scripts/validate_scenarios.py | yes | 1e1320c baee71e 40c36f8 | 일치(3/3) |
| 10 | 스크립트 | scripts/dump_scenarios.py | yes | 40c36f8 76add8a 6906af4 aeed0bd | 일치(4/4) |
| 11 | 테스트 | tests/test_validate_scenarios.py | yes | 1e1320c baee71e 40c36f8 | 일치(3/3) |
| 12 | 문서 | docs/wiki/packages/P1-pilot-dataset/evidence/20260906-1938-label-review.md | yes | 76add8a 6906af4 aeed0bd | **불일치 — git log 는 4건(f78e9dc 추가)**. U7 커밋 f78e9dc 자체가 이 파일에 4차 재검수 절·사용자 검수 절을 넣었는데(커밋 본문 3번째 변경 항목) 행을 쓸 때는 그 해시가 아직 없었다. §6 관찰 1 |

- 12/12 존재, 11/12 커밋 열 일치. 행 12 는 자기 커밋 해시 누락(사실 오류 아님, 갱신 누락) — 메인 세션이 닫는 커밋에서 `f78e9dc` 를 덧붙이면 된다. 데이터셋 값 서술(total 40 / counts / ambiguous 3 / trap 12 / virtual_names 100 / prompt_ref 3파일)은 §2 evidence 및 `manifest.json` 과 일치.
- 산출물 절(01-plan 28~38행)과의 대조: 계획에 열거된 8종 경로 모두 registry 에 있음. `scripts/dump_scenarios.py` 는 산출물 절에 경로로는 없으나 U5 문장 "검수자가 볼 수 있게 시나리오를 사람이 읽는 표로 덤프한다"(01-plan 46행)의 구현이므로 범위 안.

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견

**05-remediation 잔여**: 소견 4 = F-033bb1(해소, verify-plan)·F-7bea05(해소, baee71e)·F-1ba055(해소, baee71e)·**F-14f3ef(04-review 부재 → §1b 최종 실행으로 해소, `findings.py` 출력 `✓ F-14f3ef  해소`)**. 열림 0, 필수 0. 새 소견 없음.

**02-plan-verify §3 권고 R-4~R-12 처리 상태**

| 권고 | 내용(요약) | 상태 | 근거 |
|------|-----------|------|------|
| R-4 | 검수 항목에 "고민 상담·감정 조언 요청 발화가 아닌가"(원칙7) | **반영** | `scripts/dump_scenarios.py` 84행 `"고민 상담·감정 조언 아님 (R-4)"` 검수 항목; `evidence/20260906-1938-label-review.md` 85행 `(5) 고민 상담 — 0`, 94행 "고민 상담·감정 조언 요청 발화 0건" |
| R-5 | `new_person` 하위 유형 각 3건 이상 고정·배분표에 하위 유형·trap 열 | **반영** | `data/scenarios/manifest.json` `distribution.new_person_subtypes` = register_target [sc-035·036·037] / passing_mention [sc-038·039·040]; `distribution.by_trap_kind` 7종 합 12 = `trap_count` |
| R-6 | "ask_user 로 넘긴 mention" 을 오병합/미검출 어느 쪽도 아닌 제3 범주로 집계 | **미반영 → P4 이관** | 03-log·README·01-plan 어디에도 "제3 범주" 문구 없음(grep 일치 0). 원래부터 P4 01-plan 지표 정의 항목이라 P1 산출물 결함은 아님 — §7 인계 6 에 넣었다 |
| R-7 | `id` 전역 연번·카테고리별 5파일·`schema_version: 1` 을 U1 첫 커밋에 | **반영** | `git show 1e1320c:data/scenarios/schema.json` 4행 `"schema_version": 1`; 파일 5개(`ls data/scenarios`); id `sc-001`~`sc-040`(검사 (4) 전역 유일 PASS). 판 2 승격은 U5 40c36f8(`passing_mentions` 추가) |
| R-8 | `prompt_ref` 저장 책임·배열화·`test -f`·`same_family_as_judge` 재기록 | **반영(P1 몫) / 일부 P4 이관** | `manifest.json` `generator.prompt_ref` 배열 3개 → 이 세션 `test -f` 3/3 exists(`evidence/20260906-1850-gen-prompt-u2.md`·`-1900-gen-prompt-u3.md`·`-1930-gen-prompt-u4.md`). `same_family_as_judge: true` 는 생성 시점 기록으로 고정 — P4 가 판정 모델별로 다시 적는 것은 §7 인계 8 |
| R-9 | `ambiguous_mention_count` 일치 검사를 위반 표본 8종째로 | **반영** | 검사 (8) `manifest ambiguous_mention_count 일치`(acceptance PASS); `tests/test_validate_scenarios.py` 297~302행 `AMBIGUOUS_COUNT_MISMATCH`; 01-plan 42행 U1 표본 8종째 문장; backlog 25행 "위반 표본 8종" |
| R-10 | `grep -c "열림"` 헤더 오탐 → 셀 단위 패턴 | **반영** | U7·acceptance·이 검토 모두 `grep -cE '\| *열림 *\|'` 사용(= 0). `grep -c "반영 "` 이 산문 포함 29 인 것과 상태 셀 21 을 evidence 에 병기(`-review-acceptance.txt`) — 수치를 고르지 않았다 |
| R-11 | 상태 열 갱신 주체 = 검수자(eval-agent 가 자기 지적을 닫지 않음) | **반영** | 03-log U6·U6-2·U6-3 각 "지적 표 `상태` 열 무접촉 — 닫는 것은 검수자"; label-review 머리 8행 "상태 열은 검수자가 닫는다(R-11)"; 상태 셀은 verifier 재검수 절(2·3·4차)에서 닫혔고 커밋 6906af4·aeed0bd·f78e9dc 본문이 "label-review 재검수 절/3차 절/4차 재검수 절" 로 기록 |
| R-12 | (a) `ask_user.kind` 3종 문구 (b) "검사 항목으로 추가 가능" 잔존 (c) backlog "6종" | **반영** | (a) 01-plan 30행 "`expected_ask_user.allowed` 3종 — `ask_user.kind` 와 별도 enum, R-1" (b) 01-plan 에 "검사 항목으로 추가 가능" 문구 없음(grep 0) (c) backlog 25행 "위반 표본 8종" |

**03-log 해시**: `pending` 은 **U7 항목 1곳**(87행 `… 수용 기준 기계 검증 evidence · pending`)만 남아 있다. 위임 프롬프트가 말한 "U6-3 항목 pending" 은 이미 `aeed0bd` 로 채워져 있다(78행). 메인 세션이 U7 항목의 `pending` 을 `f78e9dc` 로 바꾼다(03-log 는 소급 수정하지 않는 기록이지만 해시 자리 채움은 애초 그렇게 예정된 것 — 92행 "메인 세션이 `/commit` 에서 채운다"). 이 검토가 03-log 에 추가한 2026-09-10 09:40 항목의 `pending` 은 닫는 커밋의 해시로 메인 세션이 채운다.

**관찰(소견 아님, 닫는 커밋에서 정리 권고)**
1. registry 106행(label-review.md) 커밋 열에 `f78e9dc` 누락 — §5 행 12. 메인 세션/architect 가 덧붙인다.
2. registry 105행 문구 "라벨 어휘가 `app.db.models` 값 집합과 글자 일치(**import 없이** 대조)" 는 부정확 — `tests/test_validate_scenarios.py:33` 이 `app.db.models` 를 import 해 대조한다(`evidence/20260910-0934-review-scope.txt`). "하지 않는 것"(app/ 생성·수정 금지)의 위반은 아니며 `validate_scenarios.py` 자체는 app 을 import 하지 않는다. 문구를 "테스트가 `app.db.models` 를 import 해 대조(검증기는 미import)" 로 고치면 된다.
3. backlog 23행 P1 행과 25~31행 U1~U7 체크박스가 `[ ]` — 메인 세션이 완료 표기(다른 완료 패키지 형식: "— 완료(날짜, 04-review 완료, verify-impl FAIL 0)").
4. 미커밋 변경(이 검토와 무관): `.gitignore`(졸업작품신청서.md 제외 — 사용자 결정 2026-09-10), `docs/wiki/HANDOFF.md`, `docs/wiki/journal.md`, `졸업작품신청서.md`(untracked) — 메인 세션이 `/commit` 에서 분리 처리.
5. FIX·L 신규 없음. 이 패키지는 CR 대상 아님(기획서 무변경).

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)

03-log U6(68행)·U6-2(76행)·U6-3(85행)·U7(92행)의 인계, README 알려진 한계 5항, 01-plan 리스크 절, 02-plan-verify R-3·R-6·R-8 을 합쳤다. **P4-pilot-eval 01-plan 이 아래를 옮겨 적었는지 P4 계획 검증(02-plan-verify)에서 본다.**

**P4-pilot-eval 로**
1. **시나리오 사이 DB 초기화.** 같은 가상 성명이 시나리오마다 다른 관계·위계로 재등장한다(`virtual_names` 100, 시나리오 40). 비우지 않으면 사전 상태가 오염돼 4방식 비교의 동일 조건이 깨진다(README 한계 4).
2. **사전 상태 적재 = `seed_persons` + `persons[].aliases` 그대로.** 결정 I: `aliases` 는 대화 시작 전 알려진 별칭만이고 승진 후 호칭·대화 중 첫 등장 호칭은 없다. 공유 호칭(팀장님·주임님·부장님)은 양쪽 다 없다. 대화에서 배운 호칭 누적은 P4 러너·ER(D6) 몫이다.
3. **오병합률·미검출률·F1 분모에서 `ambiguous: true` mention 3개 제외**: sc-022 t1 `걔`, sc-024 t4 `걔`, sc-013 t3 `걔`(`manifest.distribution.ambiguous_mentions`, `ambiguous_mention_count` 3). 시나리오 3건 자체는 40건에 포함(H-1).
4. **`passing_mentions` 6개(sc-038·039·040) = 오탐 분자.** 여기서 `create_person` 또는 `ask_user(kind=new_person)` 이 나오면 오탐(D1 확인형 등록의 반대 방향). 정답 mention 과 겹치지 않음은 검사 (15) 가 보장.
5. **`expected_ask_user.allowed` 는 허용 집합**(`identity/new_person/none`, `ask_user.kind` 와 별도 enum). 임계치 스윕(D10, `T_merge` 0.5→0.95)에서 단일 정답으로 채점하지 않는다. sc-003·sc-007 은 `["none"]`, sc-012 는 `["identity","new_person"]`(#7·#8 반영).
6. **R-6(미반영, P4 지표 정의로)**: `ask_user` 로 넘긴 mention 은 오병합에도 미검출에도 넣지 않는 **제3 범주**로 따로 집계하고 `ask_user_rate_by_kind`(D1 파급)와 함께 보고한다. 3 과 함께 P4 01-plan 지표 정의에 두 줄.
7. **이벤트 F1 은 클래스별로 보고.** 76건 분포: personal_share 25 · meal 17 · meeting 12 · favor 10 · conflict 6 · other 5 · **praise 1**; `occurred_at_kind` relative 48 · none 28 · **absolute 0**(결정 N). `favor` 10 중 사용자→인물 1건. 매크로 F1 하나로 뭉치면 praise·absolute 가 사라진다.
8. **`manifest.generator`**: `model_id` "claude-opus-5 (eval-agent)", `prompt_ref` 3파일(존재 확인), `seed: null`+`seed_reason`, `same_family_as_judge: true` 는 **P3-er Claude 판정기 기준의 생성 시점 기록**이다. P4 가 OpenAI 판정기(`gpt-4o-mini`)로도 돌리면 판정 모델별로 이 값을 P4 evidence 에 다시 적는다(R-8). P1 값은 고치지 않는다.
9. **라벨 재해석 금지(R-3, H-3).** P4 04-review 는 골드 라벨을 다시 판단하지 않는다. 라벨이 틀렸다고 보이면 FIX 가 아니라 이 패키지 `evidence/20260906-1938-label-review.md` 형식의 새 검수 기록 + 사용자 결정으로 간다(원칙8 — 결과에 맞춰 라벨을 고치지 않는다).
10. **스키마 계약**: `schema_version` 2. 소비자가 mention 단위 정보(함정 대상·선행사 턴·발화 안 위치 등)를 더 원하면 FIX 가 아니라 `schema_version` 3 + `manifest.json` 갱신(01-plan "소비자와의 계약 미확정", README 한계 5). `--strict --json` 의 `counts`·`ambiguous_mention_count`·`trap_count` 가 분모 계약(registry 96행).
11. **표본 크기**: 40건은 카테고리당 6~10건 — P4 결과는 "방향과 실패 유형"만 보고, 운영 임계치 확정은 P10 150건(01-plan 리스크 "표본 크기"). P4 01-plan 에 명시.
12. **P3-er 인계와의 관계**(01-plan 리스크): F-251dc2(trace `candidates[].similarity/aliases_matched` 복제) — P4 가 trace 로 재계산할 때의 문제, 골드 라벨 무관. F-bdd6c5(`ERConfig.top_k` 무효) — **P4 는 `top_k` 를 스윕하지 않는다**. 둘 다 P4 01-plan 이 결정.
13. **함정 12건**(`trap_count`, `by_trap_kind` 7종)은 오병합 방향을 재는 장치 — 수치가 나쁘게 나와도 데이터를 되돌리지 않는다(01-plan 리스크 "함정 난이도의 자의성", 원칙8).

**P10-final-eval 로**
1. `occurred_at_kind: absolute` **0건** — 과거 절대 날짜 발화를 보충해야 absolute 분모가 생긴다(결정 N 의 결과).
2. `praise` 1·`other` 5 표본 부족, `personal_share` 25/76 편중, `favor` 사용자→인물 방향 1건 편중.
3. 위계 `하` 6/60, 발화 길이 10~26자, 턴 수 3~5, 한 턴 지칭 1개 편중 — 실사용보다 쉬운 **과대평가 방향** 편향(README 한계 3, label-review §3).
4. **일정(schedule) 골드 라벨**(결정 C): `normal` 의 일정 발화 4건(sc-025·027·029·033)과 미래 약속 발화(sc-001 t3·sc-005 t4·sc-011 t3·sc-018 t3)에 P10 이 라벨을 덧붙인다. 정밀 `occurred_at` 정규화 평가도 P10(결정 B).
5. `schema_version` 승격 규칙은 P4 와 같다(위 10).

**주의(공통)**: `data/scenarios/*.json` 은 8~60자·3~5턴·`virtual_names` 화이트리스트를 검증기가 강제한다 — 시나리오를 추가하면 `python scripts/validate_scenarios.py --strict` rc=0 과 `--write-distribution`(멱등) 을 같은 커밋에 넣는다. 검증기·덤프는 네트워크·DB·`app/` 을 쓰지 않는다.

결과: 완료 — 수용 기준 4문장 전부 evidence 로 통과(§2), 부정 케이스 8/8 검출·대조군 0(§3), 범위 이탈 없음(app/·alembic/·reports/ 무변경), 최종 verify-impl FAIL 0 / WARN 0(§1b), 05-remediation 열림 0. §6 관찰 5건은 닫는 커밋의 문서 정리이며 판정에 영향 없음.
승인: 사용자 (2026-09-10)
