# P3-er · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-05 22:19 | 출처: verify-plan | 열림: 14 (필수 0) | 해소: 12

## F-3cf08f · [필수] 없음: docs/wiki/packages/P3-er/02-plan-verify.md
상태: 해소 | 발견: 2026-09-05 (verify-plan) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
FAIL  없음: docs/wiki/packages/P3-er/02-plan-verify.md
```

### 원인 분석
- 가설: 02-plan-verify.md 는 verifier(fable)가 쓰는 문서(L-002). 계획 초안 직후 기계 검증에서는 항상 없다 — 절차상 정상.
- 확인 방법(명령): `ls docs/wiki/packages/P3-er/`
- 확인 결과: 01-plan.md·05-remediation.md·evidence/ 만 존재

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | verifier 위임(사용자 승인 + `--stage verifier`) → 02-plan-verify.md 작성 | `bash .claude/scripts/verify-plan.sh P3-er` | `PASS  존재: …02-plan-verify.md` | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): (verifier 실행 후)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-fdb56f · [권고] registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
```

### 원인 분석
- 가설: 해당 파일은 P1-schema/P2-tools/P0-embed-pilot/하네스 소유 registry 행이 이미 있다. 01-plan 은 이 파일들을 확장(settings ER_*, embedding 공급자 이동, context traced 확장, embed_pilot import 교체, requirements +openai·anthropic, conftest grouped_embedder, README P3 행)만 하고 **새 행 없이 기존 행 비고만 갱신**한다(01-plan 리스크 "예상 WARN 8건"). 의도된 WARN.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — 마지막 단위(U9 — 개정 1 에서 구 U8 이 U9 로 재매김)에서 기존 행 비고 갱신, 새 행 금지(04-review §5 확인) | `grep -c "| <경로> |" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-b3d90e · [권고] registry 에 다른 패키지로 이미 있음: app/embedding.py → | 스크립트 | 임베딩 파일럿(결정용 코드): EmbeddingProvider·OpenA
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/embedding.py → | 스크립트 | 임베딩 파일럿(결정용 코드): EmbeddingProvider·OpenA
```

### 원인 분석
- 가설: 해당 파일은 P1-schema/P2-tools/P0-embed-pilot/하네스 소유 registry 행이 이미 있다. 01-plan 은 이 파일들을 확장(settings ER_*, embedding 공급자 이동, context traced 확장, embed_pilot import 교체, requirements +openai·anthropic, conftest grouped_embedder, README P3 행)만 하고 **새 행 없이 기존 행 비고만 갱신**한다(01-plan 리스크 "예상 WARN 8건"). 의도된 WARN.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — 마지막 단위(U9 — 개정 1 에서 구 U8 이 U9 로 재매김)에서 기존 행 비고 갱신, 새 행 금지(04-review §5 확인) | `grep -c "| <경로> |" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-149891 · [권고] registry 에 다른 패키지로 이미 있음: app/tools/context.py → | 모듈 | ToolContext·@traced | app/tools/context.py | P2-tools | 4eca3e9 | �
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: app/tools/context.py → | 모듈 | ToolContext·@traced | app/tools/context.py | P2-tools | 4eca3e9 | �
```

### 원인 분석
- 가설: 해당 파일은 P1-schema/P2-tools/P0-embed-pilot/하네스 소유 registry 행이 이미 있다. 01-plan 은 이 파일들을 확장(settings ER_*, embedding 공급자 이동, context traced 확장, embed_pilot import 교체, requirements +openai·anthropic, conftest grouped_embedder, README P3 행)만 하고 **새 행 없이 기존 행 비고만 갱신**한다(01-plan 리스크 "예상 WARN 8건"). 의도된 WARN.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — 마지막 단위(U9 — 개정 1 에서 구 U8 이 U9 로 재매김)에서 기존 행 비고 갱신, 새 행 금지(04-review §5 확인) | `grep -c "| <경로> |" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-ef1fb8 · [권고] registry 에 다른 패키지로 이미 있음: scripts/embed_pilot.py → | 스크립트 | 임베딩 파일럿(결정용 코드): EmbeddingProvider·OpenA
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: scripts/embed_pilot.py → | 스크립트 | 임베딩 파일럿(결정용 코드): EmbeddingProvider·OpenA
```

### 원인 분석
- 가설: 해당 파일은 P1-schema/P2-tools/P0-embed-pilot/하네스 소유 registry 행이 이미 있다. 01-plan 은 이 파일들을 확장(settings ER_*, embedding 공급자 이동, context traced 확장, embed_pilot import 교체, requirements +openai·anthropic, conftest grouped_embedder, README P3 행)만 하고 **새 행 없이 기존 행 비고만 갱신**한다(01-plan 리스크 "예상 WARN 8건"). 의도된 WARN.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — 마지막 단위(U9 — 개정 1 에서 구 U8 이 U9 로 재매김)에서 기존 행 비고 갱신, 새 행 금지(04-review §5 확인) | `grep -c "| <경로> |" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-2c37bd · [권고] registry 에 다른 패키지로 이미 있음: requirements.txt → | 문서/설정 | 런타임·개발 의존성 선언(첫 도입, `==` 고정) |
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: requirements.txt → | 문서/설정 | 런타임·개발 의존성 선언(첫 도입, `==` 고정) |
```

### 원인 분석
- 가설: 해당 파일은 P1-schema/P2-tools/P0-embed-pilot/하네스 소유 registry 행이 이미 있다. 01-plan 은 이 파일들을 확장(settings ER_*, embedding 공급자 이동, context traced 확장, embed_pilot import 교체, requirements +openai·anthropic, conftest grouped_embedder, README P3 행)만 하고 **새 행 없이 기존 행 비고만 갱신**한다(01-plan 리스크 "예상 WARN 8건"). 의도된 WARN.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — 마지막 단위(U9 — 개정 1 에서 구 U8 이 U9 로 재매김)에서 기존 행 비고 갱신, 새 행 금지(04-review §5 확인) | `grep -c "| <경로> |" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-127d01 · [권고] registry 에 다른 패키지로 이미 있음: tests/conftest.py → | 테스트 | 저장소 루트 `sys.path` 등록(공용 fixture) | tests/conftes
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: tests/conftest.py → | 테스트 | 저장소 루트 `sys.path` 등록(공용 fixture) | tests/conftes
```

### 원인 분석
- 가설: 해당 파일은 P1-schema/P2-tools/P0-embed-pilot/하네스 소유 registry 행이 이미 있다. 01-plan 은 이 파일들을 확장(settings ER_*, embedding 공급자 이동, context traced 확장, embed_pilot import 교체, requirements +openai·anthropic, conftest grouped_embedder, README P3 행)만 하고 **새 행 없이 기존 행 비고만 갱신**한다(01-plan 리스크 "예상 WARN 8건"). 의도된 WARN.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — 마지막 단위(U9 — 개정 1 에서 구 U8 이 U9 로 재매김)에서 기존 행 비고 갱신, 새 행 금지(04-review §5 확인) | `grep -c "| <경로> |" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-b266cb · [권고] registry 에 다른 패키지로 이미 있음: tests/test_tools_context.py → | 테스트 | trace 행 기록·예외 시 tool_error·문자열 절단 | tests/
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: tests/test_tools_context.py → | 테스트 | trace 행 기록·예외 시 tool_error·문자열 절단 | tests/
```

### 원인 분석
- 가설: 해당 파일은 P1-schema/P2-tools/P0-embed-pilot/하네스 소유 registry 행이 이미 있다. 01-plan 은 이 파일들을 확장(settings ER_*, embedding 공급자 이동, context traced 확장, embed_pilot import 교체, requirements +openai·anthropic, conftest grouped_embedder, README P3 행)만 하고 **새 행 없이 기존 행 비고만 갱신**한다(01-plan 리스크 "예상 WARN 8건"). 의도된 WARN.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — 마지막 단위(U9 — 개정 1 에서 구 U8 이 U9 로 재매김)에서 기존 행 비고 갱신, 새 행 금지(04-review §5 확인) | `grep -c "| <경로> |" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-0ffff5 · [권고] registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
상태: 열림 | 발견: 2026-09-05 (verify-plan) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
```

### 원인 분석
- 가설: 해당 파일은 P1-schema/P2-tools/P0-embed-pilot/하네스 소유 registry 행이 이미 있다. 01-plan 은 이 파일들을 확장(settings ER_*, embedding 공급자 이동, context traced 확장, embed_pilot import 교체, requirements +openai·anthropic, conftest grouped_embedder, README P3 행)만 하고 **새 행 없이 기존 행 비고만 갱신**한다(01-plan 리스크 "예상 WARN 8건"). 의도된 WARN.
- 확인 방법(명령): `grep -n "<경로>" docs/wiki/registry.md`
- 확인 결과: 기존 행 1개

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 조치 없음 — 마지막 단위(U9 — 개정 1 에서 구 U8 이 U9 로 재매김)에서 기존 행 비고 갱신, 새 행 금지(04-review §5 확인) | `grep -c "| <경로> |" docs/wiki/registry.md` | 1 (행 수 불변) | 대기(U9) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): U9 후 verify-impl 출력

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-138665 · [필수] 계획 미정: confidence 의 s_emb·s_rule 이 어느 후보의 값인지(matched_person_id 귀속)와 matched_person_id=null 일 때의 구간(merge 금지)이 01-plan 에 없다 — U5 "s_emb = 최고 후보의 인물별 max 유사도" 는 LLM 이 고른 후보와 다를 수 있다(원칙1·D3)
상태: 해소 | 발견: 2026-09-05 (review) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
FAIL  계획 미정: confidence 의 s_emb·s_rule 이 어느 후보의 값인지(matched_person_id 귀속)와 matched_person_id=null 일 때의 구간(merge 금지)이 01-plan 에 없다 — U5 "s_emb = 최고 후보의 인물별 max 유사도" 는 LLM 이 고른 후보와 다를 수 있다(원칙1·D3)
```

### 원인 분석
- 가설: 01-plan 은 `s_emb` 를 "최고 후보의 인물별 max 유사도"(U5, 89행)로, `s_rule` 을 "통과 수 / 평가 가능한 검사 수"(18행)로 적었을 뿐 **어느 후보의** 값인지 정하지 않았다. LLM 판정은 후보 하나(`matched_person_id`)를 고르므로 confidence 는 그 후보의 `s_emb`·`s_rule` 로 계산해야 한다 — 최고 유사도 후보 A 의 `s_emb` 로 LLM 이 고른 B 를 merge 하면 오병합 쪽으로 기운다(원칙1·D3 "s_emb: 후보 검색 코사인 유사도"). 또 `matched_person_id=null`(LLM 이 "아무도 아님")일 때 `s_llm` 이 높으면 산식상 confidence ≥ T_merge 가 될 수 있는데 merge 대상이 없다 — 이 경우 band 가 무엇인지(merge 금지, identity 또는 new_person) 계획에 없다.
- 확인 방법(명령): `grep -n -E "최고 후보|matched_person_id" docs/wiki/packages/P3-er/01-plan.md`
- 확인 결과: 89행 "`s_emb` = 최고 후보의 인물별 max 유사도"; `matched_person_id` 는 30·125·139행에 스키마·검증(후보 id 집합 ∪ {null})·trace 필드로만 등장, null 시 분기 문장 0건. 동명이인 회귀(40행)는 "FakeJudge 가 확신도를 나눠 최고값이 [T_new, T_merge)" 라 후보별 confidence 를 암시하나 `Judgement` 는 단일 `s_llm` 이다 — 두 문장이 서로 다른 모델을 전제한다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan 범위·결정 3 에 한 단락: (i) confidence 의 `s_emb`·`s_rule` 은 `matched_person_id` 후보의 값(rule 통과 후보 중), (ii) `matched_person_id=null` 이면 merge 금지 — band 는 `s_llm` 을 0 으로 두고 나머지 신호로 identity/new_person 만 판정하거나 통과 후보 유무로 정한다(architect 가 하나 고르고 근거를 적는다), (iii) 동명이인 회귀(c) 문장을 단일 `Judgement` 모델에 맞게 고친다 | `grep -c "matched_person_id\` 후보 하나에 귀속\|null\` 이면 병합하지" docs/wiki/packages/P3-er/01-plan.md` | 1 이상, verifier 재검토 통과 | **완료(개정 1)** — 01-plan 27행 "세 신호는 모두 LLM 이 고른 `matched_person_id` 후보 하나에 귀속된다(결정 3-c)", 28행 "`matched_person_id=null` … merge 를 금지하고 `s_llm=0` 으로 두어 규칙 통과 후보가 있으면 `identity`, 없으면 `new_person`", 138~141행 결정 3-c (a)(b)(c), 42행 회귀(c) "둘 중 하나를 `matched_person_id` 로 고르되 `s_llm` 을 중간값으로 자기보고(단일 `Judgement` 모델)", U4 "`matched_person_id=null` 이면 `band != "merge"`". 사용자 결정(journal 2026-09-06 00:10 "LLM 이 고른 인물의 s_emb·s_rule, null 이면 s_llm=0·병합 금지(후보 있으면 identity, 없으면 new_person)")과 문구 일치. 선택지 (A) 채택 → S3.3 `{matched_person_id \| null, s_llm, reason}` 그대로, 카드 변경 없음(verifier 재대조 2026-09-05 22:06) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2035-plan-review-findings.txt (발견) → 개정 1 재검토 evidence/20260905-2206-plan-review-findings-2.txt (이 소견 없음 = 해소). 남은 곁가지(llm_failed 경로의 귀속·null 경로 파이프라인 테스트)는 새 권고 소견으로 분리

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 있음 → D3·원칙1(후보 귀속 미정이면 오병합 방향)
- FIX/CR 로 올려야 하는가: 아니오 (01-plan 수정으로 해소)

## F-f43a9d · [필수] 계획 모순: resolve() 는 부수효과 없이 trace 행 1개를 쓰는데 그 행의 decision.applied·pending_question_id 는 apply_resolution 뒤에만 정해진다 — 같은 행 갱신 / er_apply 행 추가 / 필드 제거 중 무엇인지 미정(원칙9·결정 5 행 1개 계약)
상태: 해소 | 발견: 2026-09-05 (review) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
FAIL  계획 모순: resolve() 는 부수효과 없이 trace 행 1개를 쓰는데 그 행의 decision.applied·pending_question_id 는 apply_resolution 뒤에만 정해진다 — 같은 행 갱신 / er_apply 행 추가 / 필드 제거 중 무엇인지 미정(원칙9·결정 5 행 1개 계약)
```

### 원인 분석
- 가설: 결정 4(`resolve` 는 trace 행 1개만 남기고 DB 를 쓰지 않는다)와 결정 5 의 `output.decision{applied, pending_question_id}` 가 같은 행에 있다. `pending_question_id` 는 `apply_resolution` 이 `ask_user` 를 부른 뒤에야 생기므로, `resolve()` 가 쓴 행에는 항상 `applied=false`·`pending_question_id=null` 이 남는다. 계획은 (a) `apply_resolution` 이 그 행을 UPDATE 하는지(trace 변경 — 원칙9 관점에서 별도 근거 필요), (b) `step="er_apply"` 행을 추가하는지(결정 5 "행 1개" 와 충돌), (c) 두 필드를 빼고 `ask_user` 의 `tool_call` 행(같은 session_id)으로 연결하는지 정하지 않았다. `agent-observability` 스킬 체크리스트 "ask_user 호출에 pending_question_id 가 연결되는가" 의 충족 방식이 비어 있다.
- 확인 방법(명령): `grep -n -E "applied|pending_question_id|행 1개|부수효과" docs/wiki/packages/P3-er/01-plan.md`
- 확인 결과: 23행 "부수효과 없음 … trace 행 1개만 남긴다", 131행 "ER 1회당 행 1개", 140행 decision 스키마에 `applied, pending_question_id` — 갱신 주체·시점 문장 0건.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan 결정 4·5 에 한 줄로 확정: (a) `apply_resolution` 이 같은 trace 행의 `output.decision.applied/pending_question_id` 만 갱신(갱신 사실을 `decision.applied_at` 으로 남김) 또는 (c) 두 필드를 `Resolution`/`AppliedResolution` 반환값으로만 두고 trace 에서는 제거 — 어느 쪽이든 U6 테스트에 "apply 뒤 pending_question_id 가 trace 또는 ask_user 행에서 조회된다" 항목 추가 | `grep -n -E "applied_at|pending_question_id" docs/wiki/packages/P3-er/01-plan.md` | 갱신 방식 문장 1개 이상 | **완료(개정 1)** — 선택지 (a) 채택. 01-plan 26행 "`resolution.trace_id` 가 가리키는 같은 `er_resolve` 행의 `decision.applied`·`decision.pending_question_id`·`decision.applied_at` 세 필드만 JSONB 부분 갱신한다(판정 필드는 불변, 행 수는 그대로 1개)", 143행 결정 4 "trace 행의 갱신 주체" 문단(부분 갱신·판정 필드 불변·대안 (B)(C) 기각 근거), 164행, 산출물 `Resolution(trace_id 포함)`, U6 "`applied=false`·`pending_question_id=null`·`applied_at=null` 로 기록", U7 "apply 뒤 같은 trace 행에서 `pending_question_id` 를 조회할 수 있고 판정 필드는 그대로다"·"행 수는 여전히 판정당 1", 판정 방법 표 `-k applied` 행. 사용자 결정(journal 2026-09-06 00:10 "apply_resolution 이 er_resolve 같은 행에 applied·pending_question_id·applied_at 갱신")과 일치. `agent-observability` 체크리스트 "`ask_user` 호출에 `pending_question_id` 가 연결되는가" 충족 방식이 정해짐(verifier 재대조 2026-09-05 22:06) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2035-plan-review-findings.txt (발견) → 개정 1 재검토 evidence/20260905-2206-plan-review-findings-2.txt (이 소견 없음 = 해소). 부분 갱신의 **검증 방법**(identity map 이 아닌 SQL 재조회)과 **중복 apply** 동작은 새 권고 소견으로 분리

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 있음 → 원칙9·agent-observability 체크리스트(pending_question_id 연결)
- FIX/CR 로 올려야 하는가: 아니오 (01-plan 수정으로 해소)

## F-8c6354 · [필수] 계획 미정: 승진 회귀(a)가 "엄격 필터 위계 불일치 탈락 → 완화 1회" 를 실제로 거치려면 저장 인물 hierarchy 와 호칭 사전이 "부장님" 에 유도하는 위계가 달라야 하는데(상/동/하 모델에서 팀장·부장은 모두 상) 픽스처 값과 직급→위계 규칙이 01-plan 에 없다 — 완화 없이 통과하는 테스트 위험(원칙8)
상태: 해소 | 발견: 2026-09-05 (review) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
FAIL  계획 미정: 승진 회귀(a)가 "엄격 필터 위계 불일치 탈락 → 완화 1회" 를 실제로 거치려면 저장 인물 hierarchy 와 호칭 사전이 "부장님" 에 유도하는 위계가 달라야 하는데(상/동/하 모델에서 팀장·부장은 모두 상) 픽스처 값과 직급→위계 규칙이 01-plan 에 없다 — 완화 없이 통과하는 테스트 위험(원칙8)
```

### 원인 분석
- 가설: `hierarchy` 는 사용자 기준 상/동/하 3값(`app/tools/persons.py` `_HIERARCHY_ORDER`, `_is_hierarchy_adjacent` 는 인접 1칸만 True). 직장 직급 "팀장"·"부장" 은 사용자보다 위이면 둘 다 `상` 이라 위계 불일치가 생기지 않고, 그러면 회귀(a)의 "엄격 필터 탈락 → 완화 재평가 1회 → relaxed_retry=true" 가 거짓이 된다(테스트 단언을 만족시키려면 픽스처의 저장 인물을 `동` 으로 두고 호칭 사전이 "부장님"→`상` 을 유도해야 한다). 계획은 호칭 사전이 직급 → {group, hierarchy, rank} 를 준다고만 적고(16행), 직급을 상/동/하로 어떻게 매핑하는지(사용자 직급을 모른 채)와 회귀(a) 픽스처의 hierarchy 값·hints 유무를 적지 않았다. 원칙8 관점: 승진 회귀가 완화 없이 통과하거나, 사전을 테스트에 맞춰 조정할 여지가 열린다.
- 확인 방법(명령): `grep -n -E "상/동/하|hierarchy=|위계 불일치" docs/wiki/packages/P3-er/01-plan.md; grep -n "_is_hierarchy_adjacent" app/tools/persons.py`
- 확인 결과: 01-plan 27·38행에 "위계 불일치" 문구만, 픽스처 hierarchy 값 0건, 직급→위계 규칙 0건; persons.py 110행 `abs(order[a]-order[b]) == 1`.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan 결정 9 또는 회귀(a) 항목에 픽스처를 명시: 저장 인물 `{display_name, aliases:["팀장","김팀장"], relation_tag:직장, hierarchy:<값>}`, mention "부장님" 의 유도 hints `{hierarchy:<값>, relation_tag:직장}`, 두 값이 인접·불일치임을 적고, 호칭 사전의 직급→위계 규칙(예: 직급은 위계를 단정하지 않고 hints 로만 받거나, rank 차이로 인접을 판단)을 한 줄로 확정 | `grep -n -E "hierarchy:" docs/wiki/packages/P3-er/01-plan.md` | 회귀(a) 픽스처 hierarchy 값 2개 명시 | **완료(개정 1)** — 선택지 (A) 채택. 01-plan 40행·175~180행 결정 9 픽스처 `{display_name:"김민수", aliases:["팀장","김팀장"], relation_tag:"직장", hierarchy:"동"}` + `mention="부장님"`, `hints=None` → 결정 10 표(181~196행: `USER_RANK_ANCHOR=2`, 팀장 rank 2 → `동`, 부장 rank 4 → `상`) 가 `상` 유도 → "위계 `상` vs `동` 불일치 → 엄격 필터 탈락(통과 후보 0) → `_is_hierarchy_adjacent`(1칸) → 완화 재평가 1회 → 통과". verifier 산술(evidence/20260905-2206-plan-review-arith.txt): `0.5·0.95+0.3·0.85+0.2·(2/3) = 0.8633 ≥ 0.8`(완화 통과를 미통과로 계상한 값, 여유 0.063). 단언 `decision.relaxed_retry is True` 가 U7·판정 방법 표에 있어 "완화 없이 통과" 가 불가능. 사용자 결정(journal 2026-09-06 00:10 "픽스처 인물 hierarchy=동, 호칭 사전이 부장님→상 유도 → 1칸 차이 완화 경로")과 일치. D6 서사(팀장→부장 승진)와 표(동→상 1칸) 정합, `hierarchy` 값 집합은 `HIERARCHIES` 3값 그대로라 스키마 영향 없음. `USER_RANK_ANCHOR` 미노출 근거 195행(원칙8)(verifier 재대조 2026-09-05 22:06) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2035-plan-review-findings.txt (발견) → 개정 1 재검토 evidence/20260905-2206-plan-review-findings-2.txt (이 소견 없음 = 해소), 산술 evidence/20260905-2206-plan-review-arith.txt

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 있음 → S3.3 회귀 테스트 필수·원칙8
- FIX/CR 로 올려야 하는가: 아니오 (01-plan 수정으로 해소)

## F-4d1e21 · [권고] LLM 실패 강등(identity 강제)·후보 0건 경로에서 decision.band 가 confidence→구간 산식과 달라진다 — trace decision 에 band_by_threshold 와 forced_reason 을 분리 기록해야 P4 곡선 재계산이 어긋나지 않는다(S3.7)
상태: 해소 | 발견: 2026-09-05 (review) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
WARN  LLM 실패 강등(identity 강제)·후보 0건 경로에서 decision.band 가 confidence→구간 산식과 달라진다 — trace decision 에 band_by_threshold 와 forced_reason 을 분리 기록해야 P4 곡선 재계산이 어긋나지 않는다(S3.7)
```

### 원인 분석
- 가설: 강등(`llm_failed`)·후보 0건 경로에서 최종 band 가 산식 구간과 달라지는데 한 필드에 섞이면 P4 곡선(S3.7 "x = T_merge")이 임계치 변화 효과를 잘못 잰다.
- 확인 방법(명령): `grep -n "band_by_threshold" docs/wiki/packages/P3-er/01-plan.md`
- 확인 결과(개정 1): 31행 "`band_by_threshold` 와 최종 `band`·`forced_reason` 을 분리해 남긴다", 153~155행 output 스키마 `band`/`band_by_threshold`/`forced_reason: llm_failed|no_matched|no_candidates|null`, 163행 "나누는 이유(F-4d1e21)" — `forced_reason=null` 행만 순수 산식 구간. U4·U6·판정 방법 표 3행에 반영.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan 결정 5 output 스키마·31행·163행에 `band_by_threshold`·`forced_reason` 분리 명시(개정 1) | `grep -c band_by_threshold docs/wiki/packages/P3-er/01-plan.md` | 1 이상 (실제 12) | **완료(개정 1)** |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2035-plan-review-findings.txt (발견) → 개정 1 재검토 evidence/20260905-2206-plan-review-findings-2.txt (이 소견 없음 = 해소)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-3ca6b5 · [권고] U1 F-ca12ad 재현 테스트(1535차원 → flush 실패)는 U2 의 check_dimension() 이 flush 전에 잡으면 더 이상 flush 실패 경로를 타지 않는다 — 판정 방법 표 "원래 DB 오류" 기대와 어긋남, flush 자체를 실패시키는 다른 수단으로 재현할 것
상태: 해소 | 발견: 2026-09-05 (review) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
WARN  U1 F-ca12ad 재현 테스트(1535차원 → flush 실패)는 U2 의 check_dimension() 이 flush 전에 잡으면 더 이상 flush 실패 경로를 타지 않는다 — 판정 방법 표 "원래 DB 오류" 기대와 어긋남, flush 자체를 실패시키는 다른 수단으로 재현할 것
```

### 원인 분석
- 가설: U2 `check_dimension()` 이 flush 전에 차원 불일치를 잡으면 U1 의 1535차원 재현은 더 이상 flush 실패 경로(F-ca12ad)를 타지 않아 회귀 테스트가 의미를 잃는다.
- 확인 방법(명령): `grep -n "NOT NULL 위반" docs/wiki/packages/P3-er/01-plan.md`
- 확인 결과(개정 1): 37행 "flush 실패 경로 테스트는 강제 flush 실패(예: `person_aliases.alias` NOT NULL 위반)로 바꿔 유지 … 두 테스트를 모두 남긴다", U1 (iii)·U2 굵은 문장, 판정 방법 표 "F-ca12ad (flush 실패 경로)"·"차원 사전 검출(U2)" 두 행으로 분리.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan 37행·U1·U2·판정 방법 표 2행에 재현 수단 전환 명시(개정 1) | `grep -c "NOT NULL 위반" docs/wiki/packages/P3-er/01-plan.md` | 1 이상 (실제 3) | **완료(개정 1)** |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2035-plan-review-findings.txt (발견) → 개정 1 재검토 evidence/20260905-2206-plan-review-findings-2.txt (이 소견 없음 = 해소)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-acc9b9 · [권고] 완화 재평가 뒤 s_rule 계산에서 완화로 통과한 위계 검사를 통과로 셀지 미통과로 셀지 미정 — rule_passed 와 함께 계획에 명시(원칙3 재계산 가능성)
상태: 해소 | 발견: 2026-09-05 (review) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
WARN  완화 재평가 뒤 s_rule 계산에서 완화로 통과한 위계 검사를 통과로 셀지 미통과로 셀지 미정 — rule_passed 와 함께 계획에 명시(원칙3 재계산 가능성)
```

### 원인 분석
- 가설: 완화로 통과한 위계 검사를 `rule_passed` 에 통과로 세면 완화가 confidence 를 올려 임계치 통과를 돕는다(원칙1 반대), 미통과로 세면 P4 재계산에 그 사실이 남아야 한다(원칙3·8).
- 확인 방법(명령): `grep -n "relaxed_pass" docs/wiki/packages/P3-er/01-plan.md`
- 확인 결과(개정 1): 29행 "완화로 통과한 위계 검사는 `s_rule` 의 `rule_passed` 에 미통과로 센다 … `relaxed_pass=true` 플래그", 131행 "완화 통과의 계상(F-acc9b9)", 결정 9 `rule_checked=3`·`rule_passed=2` → `s_rule ≈ 0.667`. verifier 산술(evidence/20260905-2206-plan-review-arith.txt) 로 회귀(a) 값이 미통과 계상 기준임을 확인.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan 29행·131행·결정 9 에 미통과 계상 + `relaxed_pass` 명시(개정 1) | `grep -c relaxed_pass docs/wiki/packages/P3-er/01-plan.md` | 1 이상 (실제 6) | **완료(개정 1)** |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2035-plan-review-findings.txt (발견) → 개정 1 재검토 evidence/20260905-2206-plan-review-findings-2.txt (이 소견 없음 = 해소)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-cab7d6 · [권고] U6 이 커밋 하나 크기를 넘는다(파이프라인+trace+apply+회귀 3종+테스트 5종) — U6a(resolve·trace·stages·no_side_effect) / U6b(apply_resolution·회귀 3종) 분할 권고
상태: 해소 | 발견: 2026-09-05 (review) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
WARN  U6 이 커밋 하나 크기를 넘는다(파이프라인+trace+apply+회귀 3종+테스트 5종) — U6a(resolve·trace·stages·no_side_effect) / U6b(apply_resolution·회귀 3종) 분할 권고
```

### 원인 분석
- 가설: 구 U6 가 resolve·trace·apply·회귀 3종·테스트 5종을 한 커밋에 담아 검토 단위가 너무 컸다.
- 확인 방법(명령): `grep -n "^- \[ \] U" docs/wiki/packages/P3-er/01-plan.md | wc -l`
- 확인 결과(개정 1): 9단위. U6 = `resolve()`·trace·stages·no_side_effect·LLM 실패 강등, U7 = `apply_resolution()`·`grouped_embedder`·회귀 3종·applied 계약 — 제안한 U6a/U6b 분할 그대로. verify-plan 출력 `PASS Refs 있음` U1~U9.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan 작업 단위 U1~U9 재매김(구 U6 → U6/U7)(개정 1) | `bash .claude/scripts/verify-plan.sh P3-er | grep -c "Refs 있음"` | 9 | **완료(개정 1)** |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2035-plan-review-findings.txt (발견) → 개정 1 재검토 evidence/20260905-2206-plan-review-findings-2.txt (이 소견 없음 = 해소)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-5aaf28 · [권고] er_smoke 가 사용자 실행이라 키 없이도 완료 판정이 가능하지만 R4 의 실 API 구조화 출력 파싱은 스텁으로만 검증된다 — 04-review 에서 R4 를 "구현완료(스텁 검증)·실호출 evidence 유무" 로 구분 표기하도록 계획에 적을 것
상태: 해소 | 발견: 2026-09-05 (review) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
WARN  er_smoke 가 사용자 실행이라 키 없이도 완료 판정이 가능하지만 R4 의 실 API 구조화 출력 파싱은 스텁으로만 검증된다 — 04-review 에서 R4 를 "구현완료(스텁 검증)·실호출 evidence 유무" 로 구분 표기하도록 계획에 적을 것
```

### 원인 분석
- 가설: `er_smoke` 는 사용자 실행이라 키가 없으면 R4 의 "실 API 가 스키마를 지킨다" 는 증거 없이 R4 를 닫은 것처럼 보일 수 있다(원칙8).
- 확인 방법(명령): `grep -n "실호출 미검증" docs/wiki/packages/P3-er/01-plan.md`
- 확인 결과(개정 1): 판정 방법 표 "R4 닫힘 표기(F-5aaf28)" 행 — (i) 스텁 검증 완료 / (ii) 실호출은 evidence 유무로 표기, 미결 5 "R4 의 닫힘 표기를 둘로 나눈다".

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan 판정 방법 표 R4 행·미결 5 에 이중 표기 규약 명시(개정 1) | `grep -c "실호출 미검증" docs/wiki/packages/P3-er/01-plan.md` | 1 이상 (실제 2) | **완료(개정 1)** |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2035-plan-review-findings.txt (발견) → 개정 1 재검토 evidence/20260905-2206-plan-review-findings-2.txt (이 소견 없음 = 해소)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-bad87c · [권고] OpenAIEmbeddingProvider 이동 시 scripts/embed_pilot.py 의 _load_dotenv_quietly() 는 스크립트에만 남기고 app/embedding.py·backfill 은 .env 를 읽지 않아야 한다(security.md §1, app/settings.py 규약) — 계획에 명시 없음
상태: 해소 | 발견: 2026-09-05 (review) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
WARN  OpenAIEmbeddingProvider 이동 시 scripts/embed_pilot.py 의 _load_dotenv_quietly() 는 스크립트에만 남기고 app/embedding.py·backfill 은 .env 를 읽지 않아야 한다(security.md §1, app/settings.py 규약) — 계획에 명시 없음
```

### 원인 분석
- 가설: `scripts/embed_pilot.py` 의 `_load_dotenv_quietly()` 가 공급자와 함께 `app/embedding.py` 로 따라가면 제품 코드가 `.env` 를 읽게 된다(security.md §1 위반).
- 확인 방법(명령): `grep -n "_load_dotenv_quietly" docs/wiki/packages/P3-er/01-plan.md`
- 확인 결과(개정 1): 35행 "`_load_dotenv_quietly()` 는 그 스크립트에만 남기고 옮기지 않는다 — `app/embedding.py`·`app/settings.py`·`scripts/backfill_embeddings.py`·`scripts/er_smoke.py` 는 `.env` 를 읽지 않고 `os.environ` 만 본다", U2, 결정 6(a) "옮기지 않는 것 하나(F-bad87c)" + 04-review 확인 명령 `grep -n "dotenv" app/ scripts/`.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan 35행·U2·결정 6(a) 에 dotenv 비이동 명시(개정 1); 구현 후 04-review 가 `grep -n dotenv app/ scripts/` 로 확인 | `grep -c _load_dotenv_quietly docs/wiki/packages/P3-er/01-plan.md` | 1 이상 (실제 3) | **완료(개정 1)** — 코드 확인은 04-review |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2035-plan-review-findings.txt (발견) → 개정 1 재검토 evidence/20260905-2206-plan-review-findings-2.txt (이 소견 없음 = 해소)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-05cbf1 · [권고] "후보 0건" 이 규칙 통과 후보 0 인지 검색 후보 0 인지 문구가 갈린다(범위 32행 vs 회귀 39행) — LLM 생략·new_person 분기 조건을 통과 후보 0 으로 명시
상태: 해소 | 발견: 2026-09-05 (review) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
WARN  "후보 0건" 이 규칙 통과 후보 0 인지 검색 후보 0 인지 문구가 갈린다(범위 32행 vs 회귀 39행) — LLM 생략·new_person 분기 조건을 통과 후보 0 으로 명시
```

### 원인 분석
- 가설: "후보 0건" 이 검색 후보 0 인지 규칙 통과 후보 0 인지에 따라 LLM 생략·`new_person` 분기 조건이 달라진다.
- 확인 방법(명령): `grep -n "규칙 통과 후보 0" docs/wiki/packages/P3-er/01-plan.md`
- 확인 결과(개정 1): 34행 "이 계획에서 **"후보 0건"은 언제나 "2단계 규칙 통과 후보 0건"**을 뜻한다(검색 후보가 0이면 통과 후보도 0이므로 그 경우를 포함한다)", 회귀(b) "규칙 통과 후보 0 → LLM 생략", `forced_reason="no_candidates"`.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | 01-plan 34행에 정의 문장 + 회귀(b)·결정 5 어휘 통일(개정 1) | `grep -c "규칙 통과 후보 0" docs/wiki/packages/P3-er/01-plan.md` | 1 이상 (실제 4) | **완료(개정 1)** |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2035-plan-review-findings.txt (발견) → 개정 1 재검토 evidence/20260905-2206-plan-review-findings-2.txt (이 소견 없음 = 해소)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-033bb1 · [권고] 보류 1 건 — 결과는 통과가 될 수 없다
상태: 해소 | 발견: 2026-09-05 (verify-plan) | 해소: 2026-09-05

### 증상 (검증 출력 인용)
```
WARN  보류 1 건 — 결과는 통과가 될 수 없다
```

### 원인 분석
- 가설: 02-plan-verify.md 점검표 #2(불변 원칙) 가 보류다 — 원인은 review 출처 필수 소견 3건(F-138665 F-f43a9d F-8c6354). 이 소견은 그 3건의 집계 지표일 뿐 별도 문제가 아니다.
- 확인 방법(명령): `grep -c '보류' docs/wiki/packages/P3-er/02-plan-verify.md`(점검표 행 기준은 verify-plan.sh 82행 규칙)
- 확인 결과: 점검표 행 중 보류 1(#2). 필수 3건 해소 → architect 01-plan 보완 → verifier 재검토에서 #2 통과로 바뀌면 자동 해소.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | F-138665·F-f43a9d·F-8c6354 해소 후 verifier 가 02-plan-verify #2 를 통과로 재판정 | `bash .claude/scripts/verify-plan.sh P3-er` | `PASS  보류 0건` | 대기(architect → verifier) |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-7fe239 · [권고] 임계치 비교 허용오차가 두 갈래다(round(·,6) 또는 isclose(1e-9)) — round(·,6) 은 T_merge-5e-7 을 merge 로 판정해 스윕 테스트 "원값 confidence < T_merge 이면 band != merge" 와 모순될 수 있다(원칙1 방향 반대). 1e-9 급 하나로 고정하고 스윕·경계 테스트가 같은 비교 함수를 쓰게 할 것(evidence plan-review-arith)
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  임계치 비교 허용오차가 두 갈래다(round(·,6) 또는 isclose(1e-9)) — round(·,6) 은 T_merge-5e-7 을 merge 로 판정해 스윕 테스트 "원값 confidence < T_merge 이면 band != merge" 와 모순될 수 있다(원칙1 방향 반대). 1e-9 급 하나로 고정하고 스윕·경계 테스트가 같은 비교 함수를 쓰게 할 것(evidence plan-review-arith)
```

### 원인 분석
- 가설: 01-plan 28행·43행·201행이 비교 규약을 `round(confidence, 6) ≥ round(T, 6)` "(또는 `math.isclose(abs_tol=1e-9)`)" 로 두 갈래 적었다. 두 규약은 허용오차가 1e-6 대 1e-9 로 3자리 다르다. `round(·,6)` 은 `T_merge - 5e-7` 까지 merge 로 판정하므로 "`T_merge` 미만 자동 병합 금지"(S3.3·원칙1) 를 가장 엄밀하게 읽으면 어긋나고, U4 스윕 테스트("`confidence < T_merge` 인 모든 조합에서 `band != merge`")가 원값으로 비교하면 0.7999996 같은 조합에서 실패한다. 실제 필요한 것은 표현 오차(예: `0.5·0.8+0.3·1+0.2·0.5 = 0.7999999999999999`)만 흡수하는 1e-9 급이다.
- 확인 방법(명령): `grep -n "round(" docs/wiki/packages/P3-er/01-plan.md`; `cat docs/wiki/packages/P3-er/evidence/20260905-2206-plan-review-arith.txt`
- 확인 결과: 28·43·111·201행 4곳에 `round(·,6)` 우선 표기. 산술 evidence: `0.7999999999999999 >= 0.8` False / `round6` True; `0.7999996`: `round6` True, `round9` False, `isclose 1e-9` False.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | U4 구현 시 비교 함수 하나(`_ge(a, b) = a > b or math.isclose(a, b, abs_tol=1e-9)` 또는 `round(·,9)`)를 `app/er/confidence.py` 단일 출처로 두고, 경계 테스트·스윕 테스트가 같은 함수를 import 해 쓴다. 03-log 에 규약 확정을 적는다(01-plan 문구는 개정하지 않아도 되나 두 갈래 중 1e-9 를 택했다는 기록은 남긴다) | `python -m pytest tests/test_er_confidence.py -q -k "boundary or threshold"` | 통과 — 0.7999999999999999 는 merge, 0.7999996 은 identity | 완료(backend-agent U4, 커밋 대기) |

**구현 요약(U4)**: `app/er/confidence.py::ge_with_tolerance(a, b, tolerance=ER_TOLERANCE)`(별칭 `_ge`, 같은 객체 — `_ge is ge_with_tolerance`)를 유일한 비교 함수로 두었다. `round()` **함수 호출** 0건 -- `grep -n "round(" app/er/confidence.py app/settings.py` 의 매치는 전부 `round(·,6)` 을 쓰지 않는 이유를 설명하는 docstring/주석 문장뿐이고 실제 호출 코드는 없다(evidence 로 grep 원문 자체를 남긴다). `ER_TOLERANCE = 1e-9`(`app/settings.py`)가 허용오차 단일 출처다. `band_for()`·`decide()` 내부 판정이 모두 이 함수를 거친다. 경계 테스트 `test_boundary_t_merge_minus_5e7_is_not_merge_round_regression`(`T_merge-5e-7` → `band != "merge"`, F-7fe239 가 지적한 정확한 회귀 케이스)와 `test_boundary_t_merge_minus_5e10_is_merge_within_tolerance`(`T_merge-5e-10` → merge)가 두 방향을 모두 단언한다. 스윕 테스트(`test_threshold_sweep_uses_same_comparison_function_as_boundary`)가 `ge_with_tolerance` 를 직접 import 해 `band_for()` 결과와 교차검증한다.

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2206-plan-review-findings-2.txt (발견, verifier 계획 재검증) → 구현 후 04-review 에서 완료 판정 명령 출력으로 닫는다. U4 구현 증거: `docs/wiki/packages/P3-er/evidence/20260906-1330-u4-pytest-boundary.txt`(7 passed)·`20260906-1330-u4-pytest-threshold.txt`(4 passed)·`20260906-1330-u4-grep-round.txt`(round() 매치는 전부 docstring/주석) — verifier 가 04-review 에서 이 세 파일을 재현하면 닫을 수 있다.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 있음 → 원칙1·S3.3 "T_merge 미만 자동 병합 금지"(5e-7 폭이지만 방향이 반대) — 1e-9 로 고정하면 없음
- FIX/CR 로 올려야 하는가: 아니오 (구현 규약, 카드 무변경)

## F-93f063 · [권고] apply_resolution 의 JSONB 부분 갱신을 검증하는 U7 테스트가 같은 세션 identity map 으로 읽으면 in-place dict 변경이 flush 되지 않아도 통과한다 — 원시 SQL 또는 expire 후 재조회로 읽고, 구현은 jsonb_set/|| 또는 flag_modified 를 쓴다고 명시할 것(원칙8·원칙9)
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  apply_resolution 의 JSONB 부분 갱신을 검증하는 U7 테스트가 같은 세션 identity map 으로 읽으면 in-place dict 변경이 flush 되지 않아도 통과한다 — 원시 SQL 또는 expire 후 재조회로 읽고, 구현은 jsonb_set/|| 또는 flag_modified 를 쓴다고 명시할 것(원칙8·원칙9)
```

### 원인 분석
- 가설: `agent_traces.output` 은 SQLAlchemy `JSONB` 컬럼(`app/db/models.py` 256행)이라 파이썬 dict 를 in-place 로 바꾸면 변경 추적이 되지 않아 flush 되지 않는다(`MutableDict` 미사용). U7 테스트가 같은 `db_session` 의 identity map 에서 같은 인스턴스를 다시 얻으면 메모리 값만 보고 통과할 수 있다 — "항상 통과하는 테스트"(원칙8). 01-plan 143행은 "부분 갱신·전체 재기록 금지" 만 적고 구현 수단·읽기 수단을 정하지 않았다.
- 확인 방법(명령): `grep -n "JSONB\|MutableDict" app/db/models.py`; `grep -n "jsonb_set\|flag_modified\|expire" docs/wiki/packages/P3-er/01-plan.md`
- 확인 결과: models.py 에 `MutableDict` 0건(JSONB 컬럼 그대로); 01-plan 에 `jsonb_set`·`flag_modified`·`expire` 0건. 판정 방법 표 `-k applied` 행은 "같은 행에서 셋만 바뀌고" 라고만 적었다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | U7 구현: 갱신은 SQL 수준(`UPDATE agent_traces SET output = jsonb_set(...)` 또는 `output || :patch` 를 `decision` 키 아래에만) 로 하거나 dict 병합 후 `flag_modified(row, "output")`. U7 테스트: `session.flush(); session.expire_all()` 뒤 원시 `SELECT output->'decision' FROM agent_traces WHERE id=:trace_id` 로 읽어 `applied=true`·`pending_question_id`·`applied_at` 와 판정 필드 불변을 단언(03-log 에 수단 기록) | `POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -rs -k applied` | 통과, 테스트 본문에 SQL 재조회 또는 `expire_all` 존재(04-review 가 확인) | 구현됨(backend-agent U7) — (b) 방식(dict 제자리 수정 + `sqlalchemy.orm.attributes.flag_modified(trace_row, "output")`) 채택, 원시 `jsonb_set` UPDATE 는 쓰지 않음(근거: `app/er/pipeline.py.apply_resolution` docstring "trace 부분 갱신" 절). 테스트 `test_apply_resolution_updates_only_three_decision_fields_via_raw_sql_applied` 이 `db_session.execute(text("SELECT output FROM agent_traces WHERE id=:id"), ...)` **원시 SQL** 로 갱신 전/후를 각각 재조회해 `applied`/`pending_question_id`/`applied_at` 만 바뀌고 `confidence_breakdown`/`candidates`/`llm`/`band` 는 `json.dumps(..., sort_keys=True)` 문자열 비교로 완전히 동일함을 단언, `er_resolve` 행 수 1 유지도 확인. 판정 명령 실행 결과: `POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -rs -k applied` → `2 passed`(U6 의 `applied_fields` + U7 의 신규 테스트, evidence `docs/wiki/packages/P3-er/evidence/20260906-1332-u7-pytest-applied.txt`) — 04-review 가 이 evidence 로 닫을 수 있다. |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2206-plan-review-findings-2.txt (발견, verifier 계획 재검증) → 구현 후 04-review 에서 완료 판정 명령 출력으로 닫는다

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 (원칙8·9 검증 방법 문제)
- FIX/CR 로 올려야 하는가: 아니오

## F-8809f2 · [권고] apply_resolution 을 같은 Resolution 으로 두 번 부를 때의 동작이 없다 — identity/new_person 경로는 pending_questions 2행과 pending_question_id 덮어쓰기가 생긴다. applied=true 면 거부(예외) 또는 기존 AppliedResolution 반환 중 하나를 정하고 테스트할 것
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  apply_resolution 을 같은 Resolution 으로 두 번 부를 때의 동작이 없다 — identity/new_person 경로는 pending_questions 2행과 pending_question_id 덮어쓰기가 생긴다. applied=true 면 거부(예외) 또는 기존 AppliedResolution 반환 중 하나를 정하고 테스트할 것
```

### 원인 분석
- 가설: `apply_resolution(ctx, resolution)` 은 순수 함수가 아니다. merge 경로는 P2 `_add_alias` upsert 라 두 번 불러도 행이 늘지 않지만(`app/tools/persons.py` 339~351행), identity/new_person 경로는 `ask_user` 를 다시 불러 `pending_questions` 행이 하나 더 생기고 trace 의 `pending_question_id` 가 마지막 값으로 덮인다. P5 가 재시도·재개 경로에서 두 번 부를 가능성이 있는데 계약이 없다. trace 에 `applied` 플래그가 이미 있으므로 방어가 값싸다.
- 확인 방법(명령): `grep -n "두 번\|중복 실행\|idempot\|이미 applied" docs/wiki/packages/P3-er/01-plan.md`
- 확인 결과: 0건.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | U7 에서 규약 하나 채택 — (권장) trace 행의 `decision.applied=true` 면 `InvalidValue`(또는 전용 예외) 로 거부하고 아무것도 쓰지 않는다; 대안은 저장된 `pending_question_id` 로 같은 `AppliedResolution` 을 돌려주기. 테스트: 같은 `Resolution` 으로 두 번 호출 → `pending_questions` 행 수 1 유지·`er_resolve` 행 1 유지. 03-log 에 기록, P5-loop 인계에 한 줄 | `POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -rs -k "applied and twice"` | 통과 — 두 번째 호출이 행을 만들지 않음 | 구현됨(backend-agent U7) — 권장안(거부/예외) 채택. `app/er/types.py` 에 `AlreadyApplied(InvalidValue)` 신설, `apply_resolution` 이 `decision["applied"] is True` 를 확인하는 즉시 이 예외를 던지고 `update_person`/`ask_user`/trace 갱신 어느 것도 실행하지 않는다. 테스트 이름은 위임 프롬프트 명명 규칙(`-k double_apply`)을 따라 `test_apply_resolution_twice_raises_and_leaves_state_unchanged_double_apply` 로 지었다(`-k "applied and twice"` 는 이 이름과 매치되지 않아 대신 `-k double_apply` 로 재현) — `POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -rs -k double_apply` → `1 passed`(evidence `docs/wiki/packages/P3-er/evidence/20260906-1332-u7-pytest-double_apply.txt`), 두 번째 호출 전후 `_row_counts`(persons/aliases/pending_questions)와 `er_resolve` 행 수가 그대로임을 단언. 04-review 가 이 evidence 로 닫을 수 있다. |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2206-plan-review-findings-2.txt (발견, verifier 계획 재검증) → 구현 후 04-review 에서 완료 판정 명령 출력으로 닫는다

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 (S3.4 질문 프로토콜의 중복 질문 방지 — P5 인계 사항과 맞닿음)
- FIX/CR 로 올려야 하는가: 아니오

## F-f3b245 · [권고] llm_failed 경로의 s_emb·s_rule 귀속이 없다 — 결정 3-c 는 null 경로만 0 으로 정했고 JudgeUnavailable 경로는 matched_person_id 가 없는데 confidence_breakdown 값이 미정(S3.7 재계산 일관성). null 과 같은 규약(s_emb=s_rule=0, matched_person_id=null, band_by_threshold=new_person)으로 명시할 것
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  llm_failed 경로의 s_emb·s_rule 귀속이 없다 — 결정 3-c 는 null 경로만 0 으로 정했고 JudgeUnavailable 경로는 matched_person_id 가 없는데 confidence_breakdown 값이 미정(S3.7 재계산 일관성). null 과 같은 규약(s_emb=s_rule=0, matched_person_id=null, band_by_threshold=new_person)으로 명시할 것
```

### 원인 분석
- 가설: 결정 3-c(b) 는 `matched_person_id=null` 일 때 `s_emb=s_rule=0`·`confidence=0`·`band_by_threshold=new_person` 을 정했지만, 결정 3(c)·33행의 `JudgeUnavailable` 경로는 "`s_llm=0.0` 으로 계산" 만 적고 `s_emb`·`s_rule` 을 어느 후보로 귀속할지(귀속 후보가 없다) 적지 않았다. 귀속 규칙(3-c(a))을 그대로 적용하면 자연히 0 이지만 명시가 없어 구현자가 "최고 유사도 후보" 로 되돌릴 여지가 있고, 그러면 `confidence_breakdown.matched_person_id` 가 null 인데 `s_emb>0` 인 행이 생겨 P4 재계산(S3.7)이 두 규약을 섞는다. band 는 어차피 identity 강제라 오병합 위험은 없다 — 일관성 문제.
- 확인 방법(명령): `grep -n "llm_failed" docs/wiki/packages/P3-er/01-plan.md`
- 확인 결과: 33·92·155·163행 — `s_llm=0.0`·`forced_reason`·`band_by_threshold` 만, `s_emb`/`s_rule` 귀속 문장 0건.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | U4/U6 구현: `JudgeUnavailable` 경로는 null 경로와 같은 분해(`matched_person_id=null`, `s_llm=s_emb=s_rule=0`, `confidence=0`, `band_by_threshold=new_person`, `band=identity`(통과 후보 ≥1), `forced_reason=llm_failed`). U6 테스트 "LLM 실패 시 identity 강등" 에 `confidence_breakdown` 값 단언 추가. 03-log 기록 | `POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -rs -k llm_failed` | 통과 — breakdown `matched_person_id` null·세 신호 0 | 완료(backend-agent U4, `app/er/confidence.py::decide()` 레벨 — U6 파이프라인 통합 테스트는 대기) |

**구현 요약(U4)**: `app/er/confidence.py::decide(*, judgement, passed, llm_failed=True, config)` 가 `_forced_decision(forced_reason="llm_failed", passed=passed, config=config)` 를 호출한다 — 이 helper 가 null 경로(`forced_reason="no_matched"`)와 **완전히 같은 귀속**(`matched_person_id=None`, `s_llm=s_emb=s_rule=0`, `confidence=0.0`, `band_by_threshold=band_for(0.0, config)`)을 만들고 `band` 만 통과 후보 유무(`identity`/`new_person`)로 갈린다. 두 경로가 같은 함수를 공유하므로 값이 갈릴 수 없다(코드 구조 자체가 일관성을 강제, F-f3b245 가 우려한 "구현자가 최고 유사도 후보로 되돌릴 여지"가 원천 차단됨). `tests/test_er_confidence.py::test_decide_llm_failed_with_passed_candidates_is_identity` 가 `confidence_breakdown` 의 `s_llm`/`s_emb`/`s_rule`=0, `band_by_threshold="new_person"`, `band="identity"`, `matched_person_id is None` 을 단언하고, `test_decide_llm_failed_without_passed_candidates_is_new_person` 이 통과 후보 0 인 경우(`no_candidates` 가 우선하는 방어적 분기)를 확인한다. U6 파이프라인 통합 테스트(`tests/test_er_pipeline.py -k llm_failed`, `JudgeUnavailable` 실제 예외 처리·trace 기록)는 아직 없다 — `decide()` 순수 함수 레벨은 이 단위에서 완전히 닫혔다.

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2206-plan-review-findings-2.txt (발견, verifier 계획 재검증) → 구현 후 04-review 에서 완료 판정 명령 출력으로 닫는다. U4 구현 증거(`decide()` 레벨): `python -m pytest tests/test_er_confidence.py -q -k llm_failed` — 통과 6건(evidence 위 `20260906-1330-u4-pytest-confidence.txt` 전체 실행에 포함).

**U6 파이프라인 테스트 통과**: `tests/test_er_pipeline.py::test_resolve_llm_failed_forces_identity_band_llm_failed`(`-k llm_failed`) — `FakeJudge(fail="timeout")` 로 실제 `JudgeUnavailable` 예외를 흡수해 `forced_reason="llm_failed"`·`band="identity"`(통과 후보 ≥1)·`confidence_breakdown` 세 신호 0·`matched_person_id is None`·`llm.error=="timeout"`·`llm.skipped is False` 단언. 명령: `POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -rs -k llm_failed` → 1 passed(evidence `docs/wiki/packages/P3-er/evidence/20260906-1301-u6-pytest-pipeline.txt` 전체 실행 10건에 포함). `decide()` 순수 함수 레벨(U4)과 파이프라인 통합 레벨(U6) 모두 닫혔다.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 (D3 trace `confidence_breakdown` 필수 5키는 유지, 값 규약만)
- FIX/CR 로 올려야 하는가: 아니오

## F-5a97ef · [권고] matched_person_id 범위 검증 집합이 결정 3(a) "후보 id 집합" 과 34행 "통과 후보 id 집합" 으로 표기가 갈린다 — 통과 후보 집합으로 통일하고, 배제 후보 id 를 답한 경우 JudgeUnavailable(llm_failed) 로 가되 llm.error 유형으로 API 장애와 구분되게 할 것(P4 실패 케이스 분석)
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  matched_person_id 범위 검증 집합이 결정 3(a) "후보 id 집합" 과 34행 "통과 후보 id 집합" 으로 표기가 갈린다 — 통과 후보 집합으로 통일하고, 배제 후보 id 를 답한 경우 JudgeUnavailable(llm_failed) 로 가되 llm.error 유형으로 API 장애와 구분되게 할 것(P4 실패 케이스 분석)
```

### 원인 분석
- 가설: 34행은 "LLM 에 넘기는 후보 집합도 규칙 통과 후보뿐이며, 따라서 `matched_person_id ∈ 통과 후보 id 집합 ∪ {null}`" 로 쓰고, 133행 결정 3(a) 는 "`matched_person_id ∈ 후보 id 집합 ∪ {null}` 을 다시 검증한다(존재하지 않는 id 를 지어내면 판정 무효)" 로 썼다. `Judge.judge(mention, utterance, candidates)` 가 통과 후보만 받으므로(U5) 검증 집합은 사실상 통과 후보 집합이지만, "후보 id 집합" 을 검색 후보 전체로 읽으면 배제된 후보 id 를 답한 경우가 통과해 배제 후보에 merge 가 갈 수 있다(원칙1·2단계 무력화). 또 범위 밖 id 를 `JudgeUnavailable` → `forced_reason=llm_failed` 로 묶으면 P4 가 API 장애와 모델 환각을 `llm.error` 유형으로만 구분할 수 있다 — 그 유형 이름이 구분되게 정해져야 한다.
- 확인 방법(명령): `grep -n "후보 id 집합" docs/wiki/packages/P3-er/01-plan.md`
- 확인 결과: 34행 "통과 후보 id 집합", 133행 "후보 id 집합" — 두 표기.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | U5 구현: `ClaudeJudge`·`FakeJudge` 공통 후처리에서 `matched_person_id` 가 통과 후보 id 집합 밖이면 구분되는 예외 유형(예: `JudgeUnavailable` 의 `error="out_of_range_id"`)을 쓰고 `llm.error` 에 그 이름을 남긴다. `tests/test_er_judge.py` 에 배제 후보 id·존재하지 않는 id 두 케이스 추가. 03-log 기록(계획 표기 통일은 03-log 한 줄로 충분) | `python -m pytest tests/test_er_judge.py -q -k out_of_range` | 통과 — 두 케이스 모두 `JudgeUnavailable`, 오류 유형이 타임아웃과 다름 | 부분 완료(backend-agent U4 가 `decide()` 레벨 방어를 먼저 닫음 — U5 의 `Judge` 레벨 조기 차단은 대기) |

**구현 요약(U4, 표기 통일 + 방어 계층 1)**: 표기는 34행("통과 후보 id 집합") 쪽으로 통일했다 — `app/er/confidence.py::decide()` 가 `passed_ids = {c.person_id for c in passed}`(2단계 규칙 통과 후보만)를 검증 집합으로 명시적으로 쓴다. 위임 프롬프트가 "범위는 규칙 통과 후보 id 집합 ∪ {null} 로 통일"(01-plan 34행)이라고 U4 자체에도 이 검증을 요구했으므로, `Judge` 구현(U5)보다 먼저 **`decide()` 자체에 이중 방어**를 넣었다: `judgement.matched_person_id` 가 `passed_ids ∪ {None}` 밖(배제된 후보 id·존재하지 않는 id 둘 다)이면 llm_failed 와 같은 귀속에 `Decision.llm_error_kind="out_of_range_id"` 를 얹어 반환한다(F-f3b245 의 귀속 규약을 그대로 재사용). `tests/test_er_confidence.py::test_decide_out_of_range_matched_person_id_is_llm_failed_with_error_kind`(존재하지 않는 id 999)·`test_decide_out_of_range_excluded_candidate_id_is_llm_failed`(배제된 후보 id)가 두 케이스 모두 `forced_reason="llm_failed"`·`llm_error_kind="out_of_range_id"`·`band != "merge"` 를 단언한다. **U5 몫은 남아 있다**: `ClaudeJudge`/`FakeJudge` 가 API 응답을 파싱하는 시점에 더 일찍 `JudgeUnavailable(error="out_of_range_id")` 를 던져 `llm.error` 에 API 장애(`timeout`/`api_error`/`schema`)와 구분되는 이름을 남기는 것 — `decide()` 의 방어는 U5 가 놓치더라도 오병합(원칙1)은 막지만, trace `llm.error` 필드 자체는 U5 가 채워야 한다(`decide()` 는 `llm` 객체를 만들지 않는다, 결정5 스키마 — 그건 U6/U5 몫).

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2206-plan-review-findings-2.txt (발견, verifier 계획 재검증) → 구현 후 04-review 에서 완료 판정 명령 출력으로 닫는다. U4 방어 계층 증거: `python -m pytest tests/test_er_confidence.py -q -k out_of_range` — 통과 6건("out_of_range" 이름 매치, 그중 `matched_person_id` 범위 밖 케이스는 `test_decide_out_of_range_matched_person_id_is_llm_failed_with_error_kind`·`test_decide_out_of_range_excluded_candidate_id_is_llm_failed` 2건, 나머지 4건은 `combine()` 의 `s_llm`/`s_rule` `[0,1]` 범위 검증(`test_combine_s_llm_out_of_range_rejected`·`test_combine_s_rule_out_of_range_rejected`, 각 파라미터화 2건) — evidence 위 `20260906-1330-u4-pytest-confidence.txt` 전체 실행에 포함. U5 가 `tests/test_er_judge.py -k out_of_range` 를 추가해야 완전히 닫힌다.
- **U5 Judge 조기 차단 구현 완료(공급자 중립, 사용자 결정 2026-09-06)**: `app/er/judge.py::validate_judgement(raw, allowed_ids)` 가 `ClaudeJudge`·`OpenAIJudge` 양쪽에서 공유되어, `matched_person_id` 가 통과 후보 id 집합(`allowed_ids`) ∪ `{None}` 밖이면 두 공급자 모두 조기에 `JudgeUnavailable(error="out_of_range_id")` 를 던진다(API 장애 `timeout`/`rate_limit`/`api_error`/`connection` 과 구분). 판정 명령: `python -m pytest tests/test_er_judge.py -k out_of_range -q` → 5 passed(`test_claude_judge_s_llm_out_of_range_is_schema_error`·`test_openai_judge_s_llm_out_of_range_is_schema_error`·`test_claude_judge_out_of_range_matched_id_is_out_of_range_id`·`test_openai_judge_out_of_range_matched_id_is_out_of_range_id`·`test_claude_judge_excluded_candidate_id_is_out_of_range_id`). evidence `docs/wiki/packages/P3-er/evidence/20260906-1204-u5-pytest-judge.txt`(전체 36건 포함). 이제 U4(`decide()` 레벨)·U5(`Judge` 레벨) 이중 방어가 모두 구현됨 — U6 파이프라인 통합에서 두 레벨이 일관되게 동작하는지 확인하는 것만 남는다.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 — 통과 후보 집합으로 통일하면 원칙1·4(2단계 필터 유효) 유지
- FIX/CR 로 올려야 하는가: 아니오

## F-1d65ac · [권고] 결정 3-c(b) null 경로의 파이프라인 테스트가 U6 목록·판정 방법 표에 없다(FakeJudge → null, 통과 후보 있음 → band=identity·band_by_threshold=new_person·forced_reason=no_matched). 후보 0건이면 LLM 을 부르지 않으므로 null 은 항상 통과 후보 ≥1 에서만 생긴다 — "없으면 new_person" 가지는 도달 불가이며 테스트한 것으로 세지 말 것
상태: 열림 | 발견: 2026-09-05 (review) | 해소: -

### 증상 (검증 출력 인용)
```
WARN  결정 3-c(b) null 경로의 파이프라인 테스트가 U6 목록·판정 방법 표에 없다(FakeJudge → null, 통과 후보 있음 → band=identity·band_by_threshold=new_person·forced_reason=no_matched). 후보 0건이면 LLM 을 부르지 않으므로 null 은 항상 통과 후보 ≥1 에서만 생긴다 — "없으면 new_person" 가지는 도달 불가이며 테스트한 것으로 세지 말 것
```

### 원인 분석
- 가설: 결정 3-c(b) 는 개정 1 에서 새로 생긴 경로인데 U4 에는 "`matched_person_id=null` 이면 `band != merge`" 성질 테스트만 있고, U6 테스트 목록(trace 스키마·stages·no_side_effect·llm_failed·no_candidates)과 판정 방법 표에는 null 경로(`forced_reason=no_matched`)의 파이프라인 테스트가 없다. 또 34행의 최적화(통과 후보 0 → LLM 미호출) 때문에 null 은 통과 후보 ≥1 인 상황에서만 나올 수 있어 3-c(b) 의 "없으면 `new_person`" 가지는 도달 불가다 — 코드에 남겨도 되지만 커버리지·04-review 에서 "테스트됨" 으로 세면 안 된다(원칙8).
- 확인 방법(명령): `grep -n "no_matched" docs/wiki/packages/P3-er/01-plan.md`
- 확인 결과: 140·155·163행(결정·스키마·이유) 에만 있고 U6·U7·판정 방법 표에는 0건.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | U6 테스트에 케이스 추가: `FakeJudge` 가 `matched_person_id=None` 을 돌려주고 통과 후보 1개 이상 → `band=identity`·`band_by_threshold=new_person`·`forced_reason=no_matched`·`confidence_breakdown.matched_person_id is None`·세 신호 0, `apply` 뒤 `ask_user(kind=identity)` 의 `options` 에 통과 후보 이름. 도달 불가 가지는 docstring 에 명시. 03-log 기록 | `POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -rs -k no_matched` | 통과 1건 이상 | 대기(backend-agent U6) |

**U6 파이프라인 테스트 통과**: `tests/test_er_pipeline.py::test_resolve_null_matched_person_id_forces_identity_not_new_person_null_path`(`-k null_path`, 테스트 이름에 `no_matched` 대신 결정3-c(b) 사유 코드 `null_path` 를 붙였다 — 위 명령의 `-k no_matched` 대신 `-k null_path` 로 실행) — `FakeJudge(table={})` 로 통과 후보와 교집합이 없어 `matched_person_id=None` 자동 생성, `band="identity"`·`band_by_threshold="new_person"`·`forced_reason="no_matched"`·`confidence_breakdown` 세 신호 0·`matched_person_id is None`·`ask_payload.kind=="identity"` 단언. 명령: `POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -rs -k null_path` → 1 passed(evidence `docs/wiki/packages/P3-er/evidence/20260906-1301-u6-pytest-pipeline.txt` 전체 실행 10건에 포함, 단독 실행은 evidence `20260906-1301-u6-pytest-pipeline-kwise.txt` 로 확인). "통과 후보 0 + null" 가지는 테스트 docstring 에 도달 불가로 명시하고 테스트하지 않음(원칙8).

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P3-er` (계획 단계면 `verify-plan.sh P3-er`)
- 결과 파일(evidence/): evidence/20260905-2206-plan-review-findings-2.txt (발견, verifier 계획 재검증) → 구현 후 04-review 에서 완료 판정 명령 출력으로 닫는다

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 (원칙8 커버리지 표기)
- FIX/CR 로 올려야 하는가: 아니오

