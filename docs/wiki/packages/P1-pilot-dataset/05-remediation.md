# P1-pilot-dataset · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-06 18:28 | 출처: pytest | 열림: 0 | 해소: 3

## F-033bb1 · [권고] 보류 3 건 — 결과는 통과가 될 수 없다
상태: 해소 | 발견: 2026-09-06 (verify-plan) | 해소: 2026-09-06

### 증상 (검증 출력 인용)
```
WARN  보류 3 건 — 결과는 통과가 될 수 없다
```

### 원인 분석
- 가설: 스크립트 WARN 은 verifier 가 02-plan-verify 점검표 2행(원칙8)·4행(S 카드 일치)과 결과 줄을 `보류` 로 판정했기 때문이다. 판정 근거는 01-plan 의 세 가지 미정 사항 — 02-plan-verify §3 H-1(`ambiguous` 의 위치·`gold_person_id` null 허용 여부·30~50건 집계 포함 여부), H-2(결정 F 초안 생성 경로와 `manifest.json` 재현 기록 키, 초안 프롬프트에 ER 판정 프롬프트·사전·임계치 미포함 규칙), H-3(`label-review.md` 형식·완료 판정 명령·verifier 쓰기 범위 불일치). 이 문서·카드·코드의 결함이 아니라 01-plan 의 문장 부족이다.
- 확인 방법(명령): `grep -n "보류" docs/wiki/packages/P1-pilot-dataset/02-plan-verify.md` (2행·4행·결과 줄 3곳) · `grep -n "ambiguous\|시드\|label-review" docs/wiki/packages/P1-pilot-dataset/01-plan.md` (H-1~H-3 이 가리키는 문장)
- 확인 결과: 02-plan-verify 3차 evidence `evidence/20260906-1722-verify-plan-3.txt` 의 `WARN  보류 3 건` 과 §2 표의 2·4행 `보류`, §4 `결과: 보류` 가 일치. 01-plan 에는 `ambiguous` 가 44·67·77행에 나오나 mention/시나리오 단위·null 허용·집계 규칙 문장이 없고, "시드" 는 69·79행(결정 F)에만 있고 생성 경로 선택 문장이 없으며, `label-review.md` 는 35·47·58·70·80행에 있으나 형식·판정 명령이 없다. (verifier 기록. 해결 단계부터는 01-plan 을 고치는 쪽이 채운다 — verifier 는 계획을 고치지 않는다.)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P1-pilot-dataset` (계획 단계면 `verify-plan.sh P1-pilot-dataset`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-7bea05 · [필수] FAILED tests/test_validate_scenarios.py::test_repository_dataset_passes_with_zero_scenarios
상태: 해소 | 발견: 2026-09-06 (pytest) | 해소: 2026-09-06

### 증상 (검증 출력 인용)
```
FAILED tests/test_validate_scenarios.py::test_repository_dataset_passes_with_zero_scenarios
>       assert payload["total"] == 0
E       assert 16 == 0
```

### 원인 분석
- 가설: U1 이 만든 이 테스트는 **저장소의 실제 데이터셋**(`data/scenarios/`)을 대상으로 `total == 0`·`scenario_count == 0`·`counts 전부 0` 을 단정한다(`tests/test_validate_scenarios.py:468~476`, docstring "U1 시점: 시나리오 파일이 아직 없어도"). 이는 시점 의존 단정이라 U2 가 시나리오를 넣는 순간 반드시 깨진다. 데이터 결함이 아니라 테스트 설계 결함이다.
- 확인 방법(명령): `PYTHONUTF8=1 python scripts/validate_scenarios.py --json` 로 검증기 자체는 rc=0·issue_count=0 인지 확인.
- 확인 결과: 검증기 rc=0, `issue_count: 0`, `total: 16`, `counts.promotion=8`·`counts.alias=8` (evidence `20260906-1818-u2-validate.txt`). 즉 데이터·검증기는 정상이고 테스트의 기대값만 U1 상태에 고정돼 있다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `test_repository_dataset_passes_with_zero_scenarios` → `test_empty_dataset_passes_with_zero_scenarios(tmp_path, capsys)` 로 옮겼다. `write_dataset(tmp_path, files={})` 로 **manifest(counts 0)만 있고 시나리오 파일은 하나도 없는** fixture 를 만들어 `rc=0`·`total 0`·`scenario_count 0`·`counts` 전부 0·`files` 순서·`exists` 전부 False 를 단정한다. U1 의 검사 의도("파일이 없어도 돈다")가 달력이 아니라 검증기의 성질을 시험하게 됐다 | `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python -m pytest tests/test_validate_scenarios.py -q -rs` | 실패 0 | 완료 — `51 passed` (evidence `20260906-1828-fix-pytest.txt`) |
| 2 | 저장소 데이터셋용으로 `test_repository_dataset_satisfies_time_invariant_properties` 를 새로 뒀다. 시점 무관 단정만 한다 — `main(--json) == 0`, `ok is True`, `payload["total"] == manifest["total"]`, `scenario_count == manifest["total"]`, `set(counts) == set(CATEGORIES)`, `counts == manifest["counts"]`, `files` 순서 == `CATEGORY_FILES` | 같은 명령 | 실패 0 | 완료 — 같은 evidence |
| 3 | 기대 건수 정정: 위 표의 원래 기대값 `35 passed` 는 치환만 했을 때의 값이다. 같은 작업 단위에서 검사 (12)(13) 테스트 15건을 함께 넣었으므로 실제 총계는 **51**(35 − 1 치환 + 2 신규 + 15 신규 검사) | `... -q -rs` 마지막 줄 | `51 passed` | 완료 |

### 재검증
- 명령: `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python -m pytest tests/test_validate_scenarios.py -q -rs`
- 결과 파일(evidence/): `20260906-1828-fix-pytest.txt`
```
...................................................                      [100%]
51 passed in 1.15s
pytest rc=0
```
- 데이터셋 자체 재검증: `20260906-1828-fix-validate.txt` — rc=0, `결과: 시나리오 16건 / 오류 0`, `--json` 의 `issue_count: 0`·`total: 16`

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음. 원칙8(재현 가능)에 오히려 부합한다 — 시점 의존 단정을 없앴으므로 U2~U4 가 데이터를 채우는 동안에도 같은 입력이면 같은 결과다.
- FIX/CR 로 올려야 하는가: 아니오. 테스트 설계 결함이고 기획서·결정 카드에 닿지 않는다.
- `data/scenarios/*.json` 은 건드리지 않았다(U2 데이터와 다른 커밋).


## F-1ba055 · [필수] FAILED tests/test_validate_scenarios.py::test_repository_manifest_generator_keys_exist
상태: 해소 | 발견: 2026-09-06 (pytest) | 해소: 2026-09-06

### 증상 (검증 출력 인용)
```
FAILED tests/test_validate_scenarios.py::test_repository_manifest_generator_keys_exist
>       assert real_manifest["virtual_names"] == []
E       AssertionError: assert ['강도윤', '강실장'...연', '권쌤', ...] == []
```

### 원인 분석
- 가설: F-7bea05 와 같은 원인이다. 테스트 이름·docstring 은 "generator 키가 존재하는가"(H-2)인데 마지막 줄(`tests/test_validate_scenarios.py:491`)이 `virtual_names == []` 까지 단정한다. `virtual_names` 는 U2~U4 가 채우는 값이므로 이 단정은 U1 시점에서만 참이다.
- 확인 방법(명령): manifest 가 매니페스트 스키마를 통과하는지, 화이트리스트 검사 (7) 가 FAIL 을 내는지 확인.
- 확인 결과: `test_repository_manifest_validates_against_manifest_schema` 는 통과했고 검증기 `issue_count: 0` — `virtual_names` 68개는 스키마·검사 (7) 양쪽에서 정상이다. 단정 한 줄만 시점에 고정돼 있다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `assert real_manifest["virtual_names"] == []` 를 시점 무관 3단정으로 교체했다 — `isinstance(names, list)`, 원소가 전부 비어 있지 않은 `str`, `len(set(names)) == len(names)`(중복 없음). generator 키 5종 단정은 H-2 검사이므로 그대로 두고, docstring 의 "U1 에서는" 이라는 시점 문구만 없앴다 | `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python -m pytest tests/test_validate_scenarios.py -q -rs` | 실패 0 | 완료 — `51 passed` (evidence `20260906-1828-fix-pytest.txt`) |
| 2 | `generator` 값이 채워졌는지는 테스트가 아니라 U5/U7 수용 기준에서 본다(테스트에 넣으면 U2~U4 진행 중 다시 시점 의존). 지금 값은 명령으로 확인만 했다 | `PYTHONUTF8=1 python -c "import json;m=json.load(open('data/scenarios/manifest.json',encoding='utf-8'));print(m['generator'])"` | `model_id`·`prompt_ref` 가 null 이 아님 | 완료(확인만) — 실제 출력 `{"model_id": "claude-opus-5 (eval-agent)", "prompt_ref": ["docs/wiki/packages/P1-pilot-dataset/evidence/20260906-1850-gen-prompt-u2.md"], "seed": null, "seed_reason": "대화형 생성", "same_family_as_judge": true}`. `seed: null` 은 결정 F 의 기록 규칙대로 `seed_reason: "대화형 생성"` 이 사유를 남긴다 |

### 재검증
- 명령: `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python -m pytest tests/test_validate_scenarios.py -q -rs`
- 결과 파일(evidence/): `20260906-1828-fix-pytest.txt`
```
...................................................                      [100%]
51 passed in 1.15s
pytest rc=0
```
- `virtual_names` 현재 68개·중복 0 — 새 단정이 실제 값에서 참이고, 검증기 검사 (7) 도 PASS.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음. `virtual_names` 의 권위는 매니페스트 스키마와 검사 (7) 이고 테스트는 그 위에 시점 무관 성질만 얹는다.
- FIX/CR 로 올려야 하는가: 아니오.
