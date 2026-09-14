# P3-llm-providers · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-11 14:28 | 출처: verify-plan | 열림: 9 (필수 0) | 해소: 2

## F-81e3e5 · [필수] 없음: docs/wiki/packages/P3-llm-providers/02-plan-verify.md
상태: 해소 | 발견: 2026-09-11 (verify-plan) | 해소: 2026-09-11

### 증상 (검증 출력 인용)
```
FAIL  없음: docs/wiki/packages/P3-llm-providers/02-plan-verify.md
```

### 원인 분석
- 가설: 검증 순서상 정상 — 1차(14:13)·2차(14:14) 실행은 메인 세션이 02-plan-verify 작성 **전에** 돌린 것이고, 이 문서는 verifier(L-002) 가 새 컨텍스트에서 쓴다. `verify-plan.sh` 2번 항목은 파일 존재만 본다.
- 확인 방법(명령): `ls docs/wiki/packages/P3-llm-providers/` (1차 시점) · 작성 후 `PYTHONIOENCODING=utf-8 bash .claude/scripts/verify-plan.sh P3-llm-providers`
- 확인 결과: 1차 시점 디렉터리에 `01-plan.md`·`05-remediation.md`·`evidence/` 만 있었다(verifier `ls`, 14:20). 작성 후 최종 실행 `evidence/20260911-1421-verify-plan-final.txt` 2행 `PASS  존재: docs/wiki/packages/P3-llm-providers/02-plan-verify.md`, 19행 `PASS  검증자 = verifier (L-002)`.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/packages/P3-llm-providers/02-plan-verify.md` 를 `templates/plan-verify.md` 형식으로 verifier 가 작성(검증자 줄 `verifier (fable)`, 점검표 8행 카드 인용, §1a·§1b, §3 R-1~R-9) | `PYTHONIOENCODING=utf-8 bash .claude/scripts/verify-plan.sh P3-llm-providers \| grep -c "^FAIL"` | `0` | 완료(2026-09-11 14:25, `evidence/20260911-1421-verify-plan-final.txt` `== 결과: FAIL=0 WARN=11 ==`) |

### 재검증
- 명령: `PYTHONIOENCODING=utf-8 bash .claude/scripts/verify-plan.sh P3-llm-providers | tee docs/wiki/packages/P3-llm-providers/evidence/20260911-1421-verify-plan-final.txt`
- 결과 파일(evidence/): `20260911-1421-verify-plan-final.txt` — FAIL 0 / WARN 11. `findings.py … --source verify-plan` 출력 `✓ F-81e3e5  해소`.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-11fbee · [필수] 카드 없음: D11 (decisions/D11-*.md)
상태: 해소 | 발견: 2026-09-11 (verify-plan) | 해소: 2026-09-11

### 증상 (검증 출력 인용)
```
FAIL  카드 없음: D11 (decisions/D11-*.md)
```

### 원인 분석
- 가설: 01-plan 4행 태그 줄이 "기대는 결정: D3 (신설 후보 D11)" 로 `D11` 을 적었는데, 1차 실행(14:13) 시점에는 결정 6 (i) 로 확정된 카드 `decisions/D11-llm-provider-registry.md` 가 아직 없었다(계획 초안 커밋 `701fb8d` 에도 없음 — 변경 파일 6개에 `decisions/` 없음). 카드는 U4 산출물(01-plan 42행)이지만 `verify-plan.sh` 3번 항목은 태그 줄의 D 번호를 계획 검증 시점에 요구한다.
- 확인 방법(명령): `ls docs/wiki/decisions/D11-*.md` · `git status --short docs/wiki/decisions/` · `git diff -- docs/wiki/decisions/D03-confidence-formula.md | grep "^[-+]" | grep -v "^[-+][-+]"`
- 확인 결과: 메인 세션이 14:14 이전에 `docs/wiki/decisions/D11-llm-provider-registry.md` 를 신설(미추적 `??`)하고 `D03-confidence-formula.md` 파급에 "공급자 선택·활성 스위치·기본 공급자는 **D11**(이 공식은 공급자와 무관하게 동일)" 1줄 + 갱신 이력 1줄을 더했다(결정 문장 무변경 — 결정 6 (i) 그대로). 2차 실행 `evidence/20260911-1414-verify-plan-2.txt` 4행 `PASS  카드 존재: D11`, 최종 `20260911-1421-verify-plan-final.txt` 4행 동일. D11 "코드에서 지켜야 할 것" 5문장과 01-plan U1~U4 의 대응은 02-plan-verify 점검표 3행.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/decisions/D11-llm-provider-registry.md` 신설 + `D03-confidence-formula.md` 파급 상호참조 1줄(메인 세션, 결정 6 (i)) | `ls docs/wiki/decisions/D11-*.md && grep -c "D11" docs/wiki/decisions/D03-confidence-formula.md` | 파일 경로 1줄 + `1` 이상 | 완료(2026-09-11 14:14, `evidence/20260911-1414-verify-plan-2.txt` 4행 PASS) |
| 2 | 계획 승인 커밋에 D11·D03 diff 를 포함한다(현재 미커밋 — 메인 세션 `/commit`, `git add` 명시 경로) | `git log --oneline --grep D11 -- docs/wiki/decisions/` | 승인 커밋 해시 1줄 | 완료(025a7c4, 2026-09-14) |

### 재검증
- 명령: `PYTHONIOENCODING=utf-8 bash .claude/scripts/verify-plan.sh P3-llm-providers | tee docs/wiki/packages/P3-llm-providers/evidence/20260911-1421-verify-plan-final.txt`
- 결과 파일(evidence/): `20260911-1414-verify-plan-2.txt`(카드 생성 직후, FAIL 1 = F-81e3e5 만) · `20260911-1421-verify-plan-final.txt`(FAIL 0). `findings.py` 출력 `✓ F-11fbee  해소`.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 — D3 결정 문장 무변경, D11 은 추가 결정(`decisions/README.md` "결정이 바뀌면 대체" 가 아니라 신설)
- FIX/CR 로 올려야 하는가: 아니오

## F-e93529 · [권고] registry 에 다른 패키지로 이미 있음: app/er/judge.py → | 모듈 | LLM 판정(3단계, 공급자 중립) | app/er/judge.py | P3-er | b1f
상태: 열림 | 발견: 2026-09-11 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/er/judge.py → | 모듈 | LLM 판정(3단계, 공급자 중립) | app/er/judge.py | P3-er | b1f
```

### 원인 분석
- 가설: **의도된 WARN.** `app/er/judge.py` 는 P3-er U5(`b1f2782`)가 만든 파일이고 이 패키지는 그 안의 `judge_from_env()` 를 등록표로 재작성하고 `GeminiJudge` 를 **추가**한다(01-plan 32행). 01-plan 43행 "`docs/wiki/registry.md` — `app/er/judge.py`(82행)·`llm_single.py`(119행)·`.env.example`(36행) 비고 갱신" 이 기존 행 비고만 덧붙인다고 적었다. `verify-plan.sh` 88~95행은 산출물 경로가 다른 패키지 행에 있으면 "확장"과 "재작성"을 구분하지 않고 WARN 을 낸다(같은 판정 선례: `packages/P3-baselines/05-remediation.md` F-0ffff5, `packages/P3-er/05-remediation.md` 244~266행). 출력에 같은 경로가 두 번 나온 것은 산출물 32행과 44행(evidence 설명)에서 정규식이 두 번 잡았기 때문 — 소견은 하나.
- 확인 방법(명령): `grep -n "| app/er/judge.py |" docs/wiki/registry.md` · `grep -c "| app/er/judge.py |" docs/wiki/registry.md` · `sed -n 43p docs/wiki/packages/P3-llm-providers/01-plan.md`
- 확인 결과: registry 82행 1개(패키지 열 `P3-er`, 커밋 `b1f2782`, 비고 "`Judge` Protocol·`ClaudeJudge`·`OpenAIJudge`…`FakeJudge`…`judge_from_env`"). 01-plan 43행 "비고 갱신" 문장 존재. (verifier 기록 — 계획 승인을 막지 않는다. 02-plan-verify §3·R-8 참조)

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음(계획 단계) — U4 에서 `registry.md` 82행 **비고만** 갱신(`P3-llm-providers U1/U2: JUDGES 등록표·enabled_providers·GeminiJudge`), 새 행 금지. 04-review §5 에서 verifier 가 행 수를 확인해 닫는다 | `grep -c "\| app/er/judge.py \|" docs/wiki/registry.md` | `1` (행 수 불변) — 그리고 82행 비고에 `P3-llm-providers U` 문구 존재 | 대기(U4) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-llm-providers` (U4 후, 04-review 단계)
- 결과 파일(evidence/): 계획 단계 재검증 `20260911-1421-verify-plan-final.txt` 26행에서 WARN 유지 — 예상된 상태. 닫는 evidence 는 04-review 에서.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-fdb56f · [권고] registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
상태: 열림 | 발견: 2026-09-11 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
```

### 원인 분석
- 가설: **의도된 WARN.** `app/settings.py` 는 P2-tools(`f217190`)가 만든 설정 모듈이고, P3-er 이 `ER_*`·`LLM_PROVIDER` 를 더했듯 이 패키지는 `LLM_PROVIDERS_ENABLED` 기본값 상수를 더하고 `LLM_PROVIDER` 기본값을 `"openai"` 로 바꾼다(01-plan 33행, 결정 확정 표 115행). 01-plan 43행은 이 파일을 비고 갱신 대상으로 이름을 적지 않았으나 산출물 33행의 서술("기본값 상수 … 기존 `LLM_PROVIDER` 주석 갱신")은 기존 파일 확장이다 — R-8 이 여덟 경로 모두에 "비고만" 규칙을 고정했다.
- 확인 방법(명령): `grep -n "| app/settings.py |" docs/wiki/registry.md` · `grep -c "| app/settings.py |" docs/wiki/registry.md` · `sed -n 90p app/settings.py`
- 확인 결과: registry 51행 1개(패키지 열 `P2-tools`). `app/settings.py:90` `LLM_PROVIDER = "anthropic"` — U1 이 `"openai"` 로 바꾼다(D11 "코드에서 지켜야 할 것" (c)).

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음(계획 단계) — U4 에서 `registry.md` 51행 **비고만** 갱신(`P3-llm-providers U1: LLM_PROVIDER 기본 openai(D11)·LLM_PROVIDERS_ENABLED 기본 전체`), 새 행 금지 | `grep -c "\| app/settings.py \|" docs/wiki/registry.md` | `1` (행 수 불변) + 51행 비고에 `P3-llm-providers U1` 문구 | 대기(U4) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-llm-providers` (U4 후, 04-review 단계)
- 결과 파일(evidence/): 계획 단계 `20260911-1421-verify-plan-final.txt` 27행 WARN 유지 — 예상된 상태.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음(D11 이 기본값 변경을 결정으로 기록)
- FIX/CR 로 올려야 하는가: 아니오

## F-07a652 · [권고] registry 에 다른 패키지로 이미 있음: evaluation/resolvers/llm_single.py → | 모듈 | 베이스라인 3 LLM 단일 프롬프트(`llm_single`) | evaluation/
상태: 열림 | 발견: 2026-09-11 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: evaluation/resolvers/llm_single.py → | 모듈 | 베이스라인 3 LLM 단일 프롬프트(`llm_single`) | evaluation/
```

### 원인 분석
- 가설: **의도된 WARN.** P3-baselines U5(`0d98e47`)가 만든 모듈에 `GeminiSingleCaller` 를 추가하고 `caller_from_env()` 가 U1 등록표를 import 하도록 고친다(01-plan 34행). 01-plan 43행 "`llm_single.py`(119행) 비고 갱신" 명시. 산출물 34행과 43행에 경로가 두 표기(`evaluation/resolvers/llm_single.py`·`llm_single.py`)로 나와 F-22010b 가 같은 행을 다시 가리킨다.
- 확인 방법(명령): `grep -n "| evaluation/resolvers/llm_single.py |" docs/wiki/registry.md` · `grep -c "| evaluation/resolvers/llm_single.py |" docs/wiki/registry.md` · `sed -n 468,511p evaluation/resolvers/llm_single.py`
- 확인 결과: registry 119행 1개(패키지 열 `P3-baselines`, 커밋 `0d98e47`). `llm_single.py:468 caller_from_env(...)` 가 `if provider == …` 사다리와 502행 gemini `InvalidValue` 를 갖고 있다 — U3 이 고칠 자리 그대로.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음(계획 단계) — U4 에서 `registry.md` 119행 **비고만** 갱신(`P3-llm-providers U3: GeminiSingleCaller·caller_from_env 가 judge.JUDGES/스위치 import`), 새 행 금지 | `grep -c "\| evaluation/resolvers/llm_single.py \|" docs/wiki/registry.md` | `1` (행 수 불변) + 119행 비고에 `P3-llm-providers U3` 문구 | 대기(U4) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-llm-providers` (U4 후, 04-review 단계)
- 결과 파일(evidence/): 계획 단계 `20260911-1421-verify-plan-final.txt` 28행 WARN 유지 — 예상된 상태.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-2c37bd · [권고] registry 에 다른 패키지로 이미 있음: requirements.txt → | 문서/설정 | 런타임·개발 의존성 선언(첫 도입, `==` 고정) |
상태: 열림 | 발견: 2026-09-11 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: requirements.txt → | 문서/설정 | 런타임·개발 의존성 선언(첫 도입, `==` 고정) |
```

### 원인 분석
- 가설: **의도된 WARN.** `requirements.txt` 는 P1-schema(`d7113e9`)가 도입했고 P2·P3-er 이 핀을 더해 왔다(파일 주석 `# Refs: P2-tools 결정10`, `# Refs: P3-er 결정6 결정3`). 이 패키지는 결정 5 (i) 대로 `google-genai==<pip show 실측>` 1줄을 `# Refs:` 주석과 함께 더한다(01-plan 35행). registry 행은 `requirements.txt, requirements-dev.txt` 를 한 행에 묶어 두었으므로 새 행이 아니라 비고 갱신 대상.
- 확인 방법(명령): `grep -n "requirements.txt" docs/wiki/registry.md` · `grep -c "requirements.txt" docs/wiki/registry.md` · `python -m pip show google-genai`
- 확인 결과: registry 45행 1개(패키지 열 `P1-schema`, 비고에 SQLAlchemy·alembic·psycopg·pgvector 버전 목록). `pip show google-genai` → `WARNING: Package(s) not found: google-genai`(2026-09-11 14:20) — U2 착수 시 설치 후 버전을 실측해 적어야 한다(원칙8, R-6).

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음(계획 단계) — U4 에서 `registry.md` 45행 **비고만** 갱신(`P3-llm-providers U2: google-genai==<버전>`), 새 행 금지 | `grep -c "requirements.txt" docs/wiki/registry.md` | `1` (행 수 불변) + 45행 비고에 `google-genai==` 와 `pip show` 실측 버전 | 대기(U4) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-llm-providers` (U4 후, 04-review 단계)
- 결과 파일(evidence/): 계획 단계 `20260911-1421-verify-plan-final.txt` 29행 WARN 유지 — 예상된 상태.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-6ff7bc · [권고] registry 에 다른 패키지로 이미 있음: tests/test_er_judge.py → | 테스트 | LLM 판정 요청/파싱/실패 분기(공급자 중립, 네트워
상태: 열림 | 발견: 2026-09-11 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: tests/test_er_judge.py → | 테스트 | LLM 판정 요청/파싱/실패 분기(공급자 중립, 네트워
```

### 원인 분석
- 가설: **의도된 WARN.** P3-er U5(`b1f2782`) 의 36건 테스트 파일에 등록표·스위치·`GeminiJudge` 단언을 **추가**한다(01-plan 36행). 다만 "기존 36건 무수정 통과" 는 결정 2·3 때문에 그대로 성립하지 않는다 — `tests/test_er_judge.py:495 test_judge_from_env_defaults_to_anthropic`(`env={}` → `ClaudeJudge` 단언)과 `:510 test_judge_from_env_gemini_is_reserved_not_implemented`(U2 뒤에도 `GEMINI_MODEL` 미설정으로 `InvalidValue` 가 나와 틀린 이유로 통과) 2건은 바뀌어야 한다(02-plan-verify R-1). registry 비고의 "36건" 도 새 건수로 갱신한다.
- 확인 방법(명령): `grep -n "| tests/test_er_judge.py |" docs/wiki/registry.md` · `grep -c "| tests/test_er_judge.py |" docs/wiki/registry.md` · `grep -c "^def test_" tests/test_er_judge.py` · `sed -n 495,514p tests/test_er_judge.py`
- 확인 결과: registry 90행 1개(패키지 열 `P3-er`, 비고 "36건 — Claude·OpenAI 요청 스키마·`out_of_range_id`·4종 예외 매핑·`judge_f…`"). `grep -c "^def test_"` = 36. 495행 `assert isinstance(judge, ClaudeJudge)`(기본값 단언), 510~514행 gemini `pytest.raises(InvalidValue)`.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음(계획 단계) — U4 에서 `registry.md` 90행 **비고만** 갱신(`P3-llm-providers U1/U2: +N건, 기본값 단언 2건 R-1 갱신`), 새 행 금지 | `grep -c "\| tests/test_er_judge.py \|" docs/wiki/registry.md` | `1` (행 수 불변) + 90행 비고에 새 건수 | 대기(U4) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-llm-providers` (U4 후, 04-review 단계)
- 결과 파일(evidence/): 계획 단계 `20260911-1421-verify-plan-final.txt` 30행 WARN 유지 — 예상된 상태.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음(원칙8 — 기존 테스트 수정은 R-1 목록 4건으로 한정, 그 밖은 findings)
- FIX/CR 로 올려야 하는가: 아니오

## F-c6bd9b · [권고] registry 에 다른 패키지로 이미 있음: tests/test_baseline_llm_single.py → | 테스트 | LLM 단일 프롬프트 요청/파싱/강등/오류/키 미노출(
상태: 열림 | 발견: 2026-09-11 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: tests/test_baseline_llm_single.py → | 테스트 | LLM 단일 프롬프트 요청/파싱/강등/오류/키 미노출(
```

### 원인 분석
- 가설: **의도된 WARN.** P3-baselines U5(`0d98e47`) 의 테스트 파일에 `GeminiSingleCaller`·`caller_from_env` 단언을 **추가**한다(01-plan 37행). 기존 건수는 registry 비고 "69건"(파일 내 `def test_` 47 + parametrize 확장). 결정 2·3 으로 `:334 test_caller_from_env_rejects_unimplemented_provider["gemini"]` 는 U3 뒤 틀린 이유로 통과하므로 R-1(c) 대로 옮긴다.
- 확인 방법(명령): `grep -n "| tests/test_baseline_llm_single.py |" docs/wiki/registry.md` · `grep -c "| tests/test_baseline_llm_single.py |" docs/wiki/registry.md` · `sed -n 326,337p tests/test_baseline_llm_single.py`
- 확인 결과: registry 120행 1개(패키지 열 `P3-baselines`, 비고 "69건 -- 프롬프트 층…"). 334행 `@pytest.mark.parametrize("provider", ["gemini", "llama"])` + 337행 `pytest.raises(InvalidValue)`.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음(계획 단계) — U4 에서 `registry.md` 120행 **비고만** 갱신(`P3-llm-providers U3: +N건, gemini 거부 케이스 → 양성 케이스`), 새 행 금지 | `grep -c "\| tests/test_baseline_llm_single.py \|" docs/wiki/registry.md` | `1` (행 수 불변) + 120행 비고에 새 건수 | 대기(U4) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-llm-providers` (U4 후, 04-review 단계)
- 결과 파일(evidence/): 계획 단계 `20260911-1421-verify-plan-final.txt` 31행 WARN 유지 — 예상된 상태.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-cfdfa4 · [권고] registry 에 다른 패키지로 이미 있음: .env.examp → | 문서 | 환경변수 이름 목록(값 비움, 추적 유지) | .env.example
상태: 열림 | 발견: 2026-09-11 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: .env.examp → | 문서 | 환경변수 이름 목록(값 비움, 추적 유지) | .env.example
```

### 원인 분석
- 가설: **의도된 WARN.** 경로가 `.env.examp` 로 잘린 것은 `verify-plan.sh` 89행 정규식 `[A-Za-z0-9_./-]+[.][a-z]{1,5}` 가 확장자를 최대 5글자로 잡기 때문(스크립트 표시 문제, 판정에는 영향 없음 — `grep -F` 부분 일치로 36행을 찾았다). 파일 자체는 하네스 행(`e062986`)이고 P0-compose·P2-tools·P3-er 이 이름을 덧붙여 온 파일이다. 이 패키지는 4~11행 주석의 "gemini(미구현, 예약)" 제거, `LLM_PROVIDER=openai`(결정 2), 활성 스위치 이름 추가(값 비움)만 한다(01-plan 38행, security §1 "이름만"). 출력에 두 번 나온 것은 산출물 38행과 43행에서 두 번 잡혔기 때문 — 소견은 하나. **값 비움이 "전부 끔" 으로 해석되면 안 된다** → R-4(빈 값 = 기본 전체 켬).
- 확인 방법(명령): `grep -n "환경변수 이름 목록" docs/wiki/registry.md` · `grep -c "환경변수 이름 목록" docs/wiki/registry.md` · `sed -n 4,11p .env.example`(값 없는 예시 파일 — 이름만 확인)
- 확인 결과: registry 36행 1개(패키지 열 `하네스`, 비고 "값·키는 절대 넣지 않는다(security.md §1). P0-compose 749bb8e: … P2-tools f217190: 앱 설정 / P…"). `.env.example` 5~6행 주석 "anthropic(기본) | openai | gemini(미구현, 예약)"·`LLM_PROVIDER=anthropic`, 10~11행 `GEMINI_API_KEY=`·`GEMINI_MODEL=`(값 비움).

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음(계획 단계) — U4 에서 `registry.md` 36행 **비고만** 갱신(`P3-llm-providers U4: LLM_PROVIDER 기본 openai, LLM_PROVIDERS_ENABLED 이름 추가(값 비움)`), 새 행 금지. `.env.example` 에는 이름만 | `grep -c "환경변수 이름 목록" docs/wiki/registry.md && grep -c "^LLM_PROVIDERS_ENABLED=$" .env.example` | `1` (행 수 불변) 그리고 `1`(값 비움) | 대기(U4) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-llm-providers` (U4 후, 04-review 단계)
- 결과 파일(evidence/): 계획 단계 `20260911-1421-verify-plan-final.txt` 32행 WARN 유지 — 예상된 상태.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음(security §1 이름만)
- FIX/CR 로 올려야 하는가: 아니오

## F-0ffff5 · [권고] registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
상태: 열림 | 발견: 2026-09-11 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
```

### 원인 분석
- 가설: **의도된 WARN.** `README.md` 는 `registry.md` 33행 하네스 소유 행이고, 비고에 P0-compose·P1-schema·P2-tools U9·P3-er U9·P3-baselines U8 이 절을 덧붙인 이력이 쌓여 있다. 이 패키지는 217행 "엔티티 해석(ER) 실행법"·293행 "베이스라인 3종 실행법" 두 절의 환경변수 문단만 고친다(01-plan 39행). 같은 F-id 가 P3-er·P3-baselines 에서 같은 판정으로 닫혔다(`packages/P3-baselines/05-remediation.md` F-0ffff5 "조치 없음(계획 단계) — … 비고만 … `grep -c` = 1 … 판정: 해소", evidence `20260911-1305-close-f0ffff5.txt`).
- 확인 방법(명령): `grep -n "| README.md |" docs/wiki/registry.md` · `grep -c "| README.md |" docs/wiki/registry.md` · `grep -n "^### 엔티티 해석(ER) 실행법\|^### 베이스라인 3종 실행법" README.md`
- 확인 결과: registry 33행 1개(패키지 열 `하네스`, `pending`). README 217행·293행 두 절 제목 실재(01-plan 39행과 일치).

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음(계획 단계) — U4 에서 README 두 절의 환경변수 문단을 고치되 `registry.md` 는 33행 **비고만**(`P3-llm-providers U4: ER·베이스라인 실행법 절 공급자 3종·스위치 문단`), 새 행 금지. 04-review §5 에서 닫는다 | `grep -c "\| README.md \|" docs/wiki/registry.md` | `1` (행 수 불변) + 33행 비고에 `P3-llm-providers U4:` 문구 | 대기(U4) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-llm-providers` (U4 후, 04-review 단계)
- 결과 파일(evidence/): 계획 단계 `20260911-1421-verify-plan-final.txt` 34행 WARN 유지 — 예상된 상태.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-22010b · [권고] registry 에 다른 패키지로 이미 있음: llm_single.py → | 모듈 | 베이스라인 3 LLM 단일 프롬프트(`llm_single`) | evaluation/
상태: 열림 | 발견: 2026-09-11 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: llm_single.py → | 모듈 | 베이스라인 3 LLM 단일 프롬프트(`llm_single`) | evaluation/
```

### 원인 분석
- 가설: **F-07a652 와 같은 경로의 중복 소견.** 01-plan 43행이 `llm_single.py`(119행) 라는 짧은 표기를 쓰고 34행은 전체 경로를 써서 정규식이 두 토큰으로 잡았다. `grep -F "llm_single.py"` 가 119행(모듈)과 120행(테스트, `test_baseline_llm_single.py` 부분 일치)을 함께 돌려주어 출력 두 줄이 붙었다. 실체는 F-07a652 하나.
- 확인 방법(명령): `grep -n "llm_single.py" docs/wiki/registry.md` · `grep -c "| evaluation/resolvers/llm_single.py |" docs/wiki/registry.md`
- 확인 결과: 119행(모듈)·120행(테스트) 2개 행이 부분 일치 — 모듈 행은 1개. F-07a652 해결 단계 1 이 이 소견도 닫는다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음(계획 단계) — F-07a652 와 동일(U4 에서 119행 비고만). 04-review 에서 F-07a652 와 함께 닫는다 | `grep -c "\| evaluation/resolvers/llm_single.py \|" docs/wiki/registry.md` | `1` (행 수 불변) | 대기(U4) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-llm-providers` (U4 후, 04-review 단계)
- 결과 파일(evidence/): 계획 단계 `20260911-1421-verify-plan-final.txt` 43행 WARN 유지 — 예상된 상태.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-7afd7f · [권고] U1 기존 테스트 변경이 R-1 목록 밖 2건: tests/test_er_smoke.py test_main_success_path_prints_expected_json · test_main_judge_unavailable_returns_3 의 setenv 키 이름
상태: 해소 | 발견: 2026-09-14 (review) | 해소: 2026-09-14

### 증상 (검증 출력 인용)
```
git diff -- tests/test_er_smoke.py | grep "^[-+]" | grep -v "^[-+][-+]"
-    monkeypatch.setenv("ANTHROPIC_API_KEY", _FAKE_KEY_MARKER)
+    monkeypatch.setenv("OPENAI_API_KEY", _FAKE_KEY_MARKER)   (2곳 — success_path · judge_unavailable)
(01-plan 127행 "테스트를 고쳐서 통과시키는 일이 있으면 그 자체를 findings 로 올린다"; 02-plan-verify R-1 은 바뀌는 기존 테스트를 4건으로 고정)
```

### 원인 분석
- 가설: 두 테스트는 `LLM_PROVIDER` 를 지정하지 않고 기본 공급자의 키(`ANTHROPIC_API_KEY`)만 설정해 `scripts/er_smoke.py` 의 키 사전 확인을 통과시키고 있었다. 결정 2 로 기본이 `openai` 가 되자 필요한 키가 `OPENAI_API_KEY` 로 바뀌어 rc=2 로 깨졌다 — R-1(d) 와 **같은 원인**이며 verifier 가 R-1 작성 시 이 두 함수를 빠뜨렸다(기본 키 이름을 단언하지 않고 setenv 로만 쓰므로 grep 에 안 잡힘).
- 확인 방법(명령): `git stash`-없이 확인 — `git diff 025a7c4 -- tests/test_er_smoke.py | grep "^[-+]    def\|^[-+]def\|setenv\|delenv"` · `git show 025a7c4:tests/test_er_smoke.py | grep -n "ANTHROPIC_API_KEY"`
- 확인 결과: U1 직전 파일에서 `ANTHROPIC_API_KEY` 는 세 함수(missing_key·success_path·judge_unavailable)에만 있고, 셋 다 `LLM_PROVIDER` 미지정 = 기본 공급자 의존. 변경은 키 이름 3곳 + 함수 개명 1곳뿐, 단언·검증 로직 무변경(evidence `20260914-1620-u1-git-diff-tests-removed-defs.txt` — 삭제·개명 함수는 R-1(a)(d) 2개뿐).

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `tests/test_er_smoke.py` 두 함수의 `setenv` 키 이름을 `OPENAI_API_KEY` 로(backend-agent U1, 검증 로직 무변경) | `python -m pytest tests/test_er_smoke.py -q` | 전건 통과 | 완료(evidence `20260914-1620-u1-pytest-er-regression.txt`) |
| 2 | R-1 의 "네 건" 을 "네 건 + 이 두 건(키 이름만)" 으로 읽는다 — 04-review 의 `git diff <U1 직전>..HEAD -- tests/` 대조 목록에 이 소견을 포함(verifier 몫) | `git diff 025a7c4..HEAD -- tests/test_er_smoke.py \| grep -c "OPENAI_API_KEY"` | `4`(delenv 1 + assert 1 + setenv 2) | 대기(04-review) |

### 재검증
- 명령: `POSTGRES_PORT=5433 python -m pytest tests/test_er_smoke.py tests/test_er_judge.py -q -rs`
- 결과 파일(evidence/): `20260914-1620-u1-pytest-er-regression.txt`(실패 0)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 — D11 결정 2 의 직접 결과. 원칙8(테스트를 고쳐 통과시킨 사실을 숨기지 않음)
- FIX/CR 로 올려야 하는가: 아니오
