# P6-memory · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-28 14:44 (verifier 4차, F-04ecbe 해소) | 출처: review | 열림: 0 (필수 0) | 해소: 6

## F-95c005 · [필수] 없음: docs/wiki/packages/P6-memory/02-plan-verify.md
상태: 해소 | 발견: 2026-09-28 (verify-plan) | 해소: 2026-09-28

### 증상 (검증 출력 인용)
```
FAIL  없음: docs/wiki/packages/P6-memory/02-plan-verify.md
```

### 원인 분석
- 가설: 02-plan-verify.md 가 아직 없었다(verifier 미착수). 계획 자체의 결함이 아니다.
- 확인 방법(명령): `ls docs/wiki/packages/P6-memory/02-plan-verify.md` → 2차 `bash .claude/scripts/verify-plan.sh P6-memory`
- 확인 결과: 2차(evidence/20260928-1355-verifier-verify-plan-2.txt) `PASS  존재: …/02-plan-verify.md`, FAIL 0. 해소.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 |  |  |  | 대기 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P6-memory` (계획 단계면 `verify-plan.sh P6-memory`)
- 결과 파일(evidence/):

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-033bb1 · [권고] 보류 2 건 — 결과는 통과가 될 수 없다
상태: 해소 | 발견: 2026-09-28 (verify-plan) | 해소: 2026-09-28

### 증상 (검증 출력 인용)
```
WARN  보류 2 건 — 결과는 통과가 될 수 없다
```

### 원인 분석
- 가설: verifier 점검표 3행이 보류(H-1·H-2, D14 코드 요구 누락)이고 §3 에 H-3 이 더 있어 결과가 보류다. 스크립트가 보류를 세어 낸 의도된 WARN — 계획을 고치기 전에는 사라질 수 없다.
- 확인 방법(명령): H-1~H-3 반영한 01-plan 개정본으로 `bash .claude/scripts/verify-plan.sh P6-memory` 재실행 → verifier 재판정(점검표 8/8 통과)
- 확인 결과: 1차 판정(2026-09-28): 보류 3건 열림(F-bbf7fa·F-56df6c·F-14ad9f). 재검증 대기. → 2차(14:15, verifier): 세 건 닫힘 뒤 02-plan-verify 점검표 8/8 통과, 2b 실행 `PASS  보류 0건` — 해소.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `02-plan-verify.md` 를 2차 판정으로 갱신(H-1~H-3 닫힘 근거 §3-1, 점검표 8행에 보류 0) — verifier | `bash .claude/scripts/verify-plan.sh P6-memory` | `PASS  보류 0건`, `== 결과: FAIL=0 WARN=0 ==` | 완료(2026-09-28 14:15) |

### 재검증
- 명령: `bash .claude/scripts/verify-plan.sh P6-memory`
- 결과 파일(evidence/): `20260928-1410-verifier-2-verify-plan.txt`(판정 갱신 전, WARN 1 그대로) → `20260928-1415-verifier-2b-verify-plan.txt`(판정 갱신 후, `PASS  보류 0건`, FAIL 0 WARN 0)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-bbf7fa · [필수] H-1 D14 .env.example 기본값 줄이 01-plan U1·파일 표에 없음
상태: 해소 | 발견: 2026-09-28 (review) | 해소: 2026-09-28 (계획 단계 — 3단계 실파일은 U1 구현 판정으로 이월)

### 증상 (검증 출력 인용)
```
FAIL  H-1 D14 .env.example 기본값 줄이 01-plan U1·파일 표에 없음
```

### 원인 분석
- 가설: architect 가 D14 카드를 읽었으나(01-plan 221행) '코드에서 지켜야 할 것' 11행의 마지막 구절 "`.env.example` 에 기본값 줄" 을 파일 표·U1 로 옮기지 않았다. CR-002 16행도 같은 요구를 한다. 원인은 카드 요구 → 산출물 표 대조 누락.
- 확인 방법(명령): `grep -n 'env.example' docs/wiki/packages/P6-memory/01-plan.md` (기대: 0건 → 개정 후 ≥1건) · `grep -n PATTERN .env.example` (현재 0건, U1 뒤 2건)
- 확인 결과: 01-plan 에 `env.example` 0건(2026-09-28), `.env.example` 에 `PATTERN` 0건(evidence/20260928-1350-verifier-fact-checks.txt §16). 해결은 01-plan 개정(U1 산출물·고치는 파일 표에 `.env.example` 추가) — 계획 개정자 몫.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `01-plan.md` 고치는 파일 표에 `.env.example` 행 추가(두 줄 `PATTERN_WINDOW_DAYS=`·`PATTERN_MIN_COUNT=`, 값 비움·"비우면 기본 365/3" 설명만, 비밀 없음, 소유 = 하네스 registry 38행) | `grep -n 'env\.example. . 두 줄 추가' docs/wiki/packages/P6-memory/01-plan.md` | 1건(고치는 파일 표 행) | 완료(1차 개정, 2026-09-28) |
| 2 | `01-plan.md` U1 문장에 `.env.example` 기본값 줄과 판정 `grep -n PATTERN .env.example`(2건) 추가, 범위 "문서·설정 예시" 줄에도 명시 | `grep -n 'env.example' docs/wiki/packages/P6-memory/01-plan.md` | ≥3건(범위 줄·파일 표·U1) | 완료(1차 개정, 2026-09-28) |
| 3 | (구현 시점 — U1) 실제 `.env.example` 에 두 줄 추가 | `grep -n PATTERN .env.example` | 2건 | 대기(U1 구현 몫, 계획 보류 해소 조건 아님 — verifier 2차도 같은 판단: 04-review 에서 U1 evidence 로 판정) |

### 재검증
- 명령: 1·2단계 = 위 표의 완료 판정 명령을 05 표에서 awk 로 잘라내 그대로 실행(verifier, 2026-09-28 14:09) · 3단계 = U1 뒤 `verify-impl.sh P6-memory` + 04-review
- 결과 파일(evidence/): `20260928-1410-verifier-2-hold-recheck.txt` — 1단계 `60:` 1건(exit 0) · 2단계 3·25·60·67·233행 5건 ≥ 3(exit 0) · 3단계 0건(exit 1, 구현 전이라 기대대로). **계획 단계 소견 해소**(02-plan-verify 2차 §3-1). 3단계는 열린 채로 U1 이 닫는다(04-review 수용 기준 표에서 `grep -n PATTERN .env.example` 2건 확인)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-56df6c · [필수] H-2 D14 실제 쓴 기간·횟수 기록이 결정 F memory_pattern output 스키마·U2 에 없음
상태: 해소 | 발견: 2026-09-28 (review) | 해소: 2026-09-28

### 증상 (검증 출력 인용)
```
FAIL  H-2 D14 실제 쓴 기간·횟수 기록이 결정 F memory_pattern output 스키마·U2 에 없음
```

### 원인 분석
- 가설: D14 13행 요구가 01-plan 의 해석 ㄷ(84행)·판정 3행(95행)에는 들어갔지만, backend-agent 의 구현 계약인 결정 F(183행) `memory_pattern` output 스키마와 U2(66행)에는 옮겨지지 않았다 — CR-002 를 반영할 때 판정 표만 고치고 결정 F 를 다시 보지 않은 것. `window.from/to` 로 일수는 역산돼도 `min_count` 는 어디에도 남지 않아 설정 변경 뒤 과거 판정 재현이 안 된다(원칙8·9).
- 확인 방법(명령): `grep -nE 'window_days|min_count' docs/wiki/packages/P6-memory/01-plan.md` (기대: 결정 F·U2 에 ≥1건씩)
- 확인 결과: 2026-09-28 현재 결정 F 183행 output 에 `window:{from,to}` 만 있고 기간·횟수 키 없음(01-plan 직접 읽음). 해결은 결정 F output 에 `window_days`·`min_count` 추가 + U2 문장 보강 — 계획 개정자 몫.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `01-plan.md` 결정 F `memory_pattern` output 스키마에 `window_days`·`min_count`(실제 적용한 `pattern_config()` 값) 추가, D14 13행 인용 | `grep -nF 'window:{from,to}, window_days, min_count' docs/wiki/packages/P6-memory/01-plan.md` | 1건(결정 F 줄) | 완료(1차 개정, 2026-09-28) |
| 2 | `01-plan.md` U2 문장에 "실제로 쓴 기간·횟수를 output 의 `window_days`·`min_count` 에 기록(D14, 결정 F)" 추가 | `grep -n 'U2 패턴 감지 규칙.*window_days' docs/wiki/packages/P6-memory/01-plan.md` | 1건(U2 줄) | 완료(1차 개정, 2026-09-28) |
| 3 | 판정 표 3행 기대·해석 ㄷ 를 이 두 키로 고정(`window_days=90`·`min_count=2`) | `grep -nE 'window_days=90' docs/wiki/packages/P6-memory/01-plan.md` | 1건(판정 3행) | 완료(1차 개정, 2026-09-28) — verifier 2차 확인 |

### 재검증
- 명령: 위 표의 완료 판정 명령 3개를 05 표에서 awk 로 잘라내 그대로 실행(verifier, 2026-09-28 14:09)
- 결과 파일(evidence/): `20260928-1410-verifier-2-hold-recheck.txt` — 1단계 `186:` 1건(결정 F output 에 `window:{from,to}, window_days, min_count`) · 2단계 `68:` 1건(U2 줄) · 3단계 `97:` 1건(판정 3행) — 전부 exit 0. **해소**(02-plan-verify 2차 §3-1, 점검표 3행 통과)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-14ad9f · [필수] H-3 지킬 불변식 grep delete\( 이 C-5(i)·D-6·U2 의 사실·링크 삭제와 모순
상태: 해소 | 발견: 2026-09-28 (review) | 해소: 2026-09-28

### 증상 (검증 출력 인용)
```
FAIL  H-3 지킬 불변식 grep delete\( 이 C-5(i)·D-6·U2 의 사실·링크 삭제와 모순
```

### 원인 분석
- 가설: 195행 불변식 grep `delete\(` 은 `events` 삭제를 잡으려는 의도인데 대상을 `app/memory/` 전체로 잡았다. 같은 계획의 C-5(i)(패턴 사실 행 삭제)·D-6(링크 교체)·U2(빠진 링크 제거)가 `app/memory/` 에 `PersonFact`/`FactSource` 삭제 코드를 반드시 만들므로 이 grep 은 U8 에서 항상 히트한다. 의도(원문 불변)와 명령(모든 delete 금지)의 불일치.
- 확인 방법(명령): 01-plan 195행을 `Event` 대상으로 좁힌 grep 으로 바꾸거나 판정 13행 테스트만 불변식으로 삼는다. 확인: `sed -n 195p docs/wiki/packages/P6-memory/01-plan.md` 에 `delete\(Event` 류 한정 표현 또는 grep 삭제
- 확인 결과: 2026-09-28 현재 195행 `grep -rnE "delete\(|\.content\s*=|raw_utterance\s*=" app/memory/` — 사실·링크 삭제와 모순(02-plan-verify §3 H-3). 해결은 01-plan 문장 수정 — 계획 개정자 몫.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `01-plan.md` "지킬 불변식" 첫 줄을 두 겹으로 확정: 권위 판정 = 판정 표 13행 테스트, 보조 grep 은 `Event` 대상만(`delete\(Event`·`update\(Event`·`.raw_utterance =`·`.content =`, 비교 `==` 제외). `PersonFact`/`FactSource` 삭제(C-5(i)·D-6·U2)는 대상 아님을 명시 | `grep -nF 'delete\(Event' docs/wiki/packages/P6-memory/01-plan.md` | 1건(지킬 불변식 줄) | 완료(1차 개정, 2026-09-28) |
| 2 | 옛 무한정 grep(대상 제한 없이 `delete\(` 로 시작하던 명령) 제거 | `grep -c 'rnE "delete\\([^E]' docs/wiki/packages/P6-memory/01-plan.md` | `0` | 완료(1차 개정, 2026-09-28) — verifier 2차 확인 |

### 재검증
- 명령: 위 표의 완료 판정 명령 2개를 05 표에서 awk 로 잘라내 그대로 실행(verifier, 2026-09-28 14:09). 주의: 2단계 명령은 백슬래시가 두 겹이라 **손으로 옮겨 치면** 이스케이프가 달라져 `grep: Unmatched ( or \(` 가 난다 — 다시 돌릴 때는 파일에서 잘라 실행하거나 고정 문자열 `grep -nF 'delete\(|' 01-plan.md` → 0건으로 대신한다(02-plan-verify 2차 R-11)
- 결과 파일(evidence/): `20260928-1410-verifier-2-hold-recheck.txt` — 1단계 `198:` 1건(`delete\(Event|update\(Event|\.raw_utterance\s*=[^=]|\.content\s*=[^=]`, `Event` 대상만) · 2단계 `0`(옛 grep 잔존 없음). **해소**(02-plan-verify 2차 §3-1, 점검표 4행 통과)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

## F-04ecbe · [필수] H-4 01-plan 25행 .env.example 기본값 줄 개수가 2개/365/3 로 남아 60·67행(3줄·365/3/5)과 어긋남
상태: 해소 | 발견: 2026-09-28 (review) | 해소: 2026-09-28 (verifier 4차 14:40~14:44)

### 증상 (검증 출력 인용)
```
FAIL  H-4 01-plan 25행 .env.example 기본값 줄 개수가 2개/365/3 로 남아 60·67행(3줄·365/3/5)과 어긋남
```

### 원인 분석
- 가설: 승인 전 변경(2026-09-28, `MEMORY_PROMOTE_MIN_EVENTS` 환경변수 덮어쓰기 추가)을 01-plan 에 넣을 때 25행 "문서·설정 예시" 줄의 **앞 절반**(RUNNING 설명 — "3개")만 고치고 **뒤 절반**(`.env.example` — "그 2개의 기본값 줄(… "비우면 기본 365/3" …)")은 1차 개정 문구 그대로 남았다. 같은 줄 안에서 "3개" 와 "2개" 가 공존하고, 60행(세 줄 추가 · 365일/3회/5건)·67행 U1(그 3개의 기본값 줄 · 365/3/5 · grep 3건)과 어긋난다 — 구현자가 25행을 따르면 `.env.example` 에 두 줄만 넣어 U1 판정(3건)이 실패한다. 카드·코드·범위 문제가 아니라 01-plan 한 구절의 표기 불일치다.
- 확인 방법(명령): `grep -nE '2개의|두 줄|365/3"' docs/wiki/packages/P6-memory/01-plan.md` (기대: 개정 전 25행 1건 → 개정 후 0건) · `grep -nE '3개의|세 줄|365/3/5' docs/wiki/packages/P6-memory/01-plan.md` (기대: 25·60·67행 3건 이상)
- 확인 결과: 2026-09-28 14:31 `evidence/20260928-1431-verifier-3-fact-checks.txt` §1 — 25행 1건(`그 2개의 기본값 줄(이름과 "비우면 기본 365/3" 설명만`), §2 — 60·67행은 "세 줄"·"3개"·"365/3/5". 해결은 01-plan 25행 뒤 절반을 "그 3개의 기본값 줄(이름과 "비우면 기본 365/3/5" 설명만 …)" 로 고치는 것 — 계획 개정자(메인 세션) 몫. 05 `F-bbf7fa` 3단계(`grep -n PATTERN .env.example` 2건)와 U1 판정(`grep -nE "PATTERN_|MEMORY_PROMOTE_MIN_EVENTS" .env.example` 3건)은 모순이 아니다(§9 — `PATTERN` 접두 줄은 여전히 2건, U1 은 세 이름을 모두 세는 다른 명령).

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/packages/P6-memory/01-plan.md` 25행 뒤 절반을 "그 3개의 기본값 줄(… 365/3/5 …)" 로 교체(메인 세션, 2026-09-28) | `grep -cE '2개의\|두 줄\|365/3"' docs/wiki/packages/P6-memory/01-plan.md` | `0` | 완료 |
| 2 | 같은 파일 55행 중복 `MEMORY_PROMOTE_MIN_EVENTS=5` 제거(R-13) | `sed -n 55p docs/wiki/packages/P6-memory/01-plan.md \| grep -o "MEMORY_PROMOTE_MIN_EVENTS=5" \| wc -l` | `1` | 완료 |

### 재검증
- 명령: `bash .claude/scripts/verify-plan.sh P6-memory` + 위 해결 단계 표의 완료 판정 명령 2개를 **05 파일에서 잘라 그대로** 실행(verifier 4차, 2026-09-28 14:40 — 표 칸의 `\|` 는 `|` 로 되돌려 실행. awk 로 자르면 이 환경에서 칸이 글자 단위로 깨지므로 python 스크립트로 잘랐다; 실패한 시도도 evidence §1·§1b 에 그대로 남겼다) + 확인 방법의 grep 2개
- 결과 파일(evidence/): `20260928-1440-verifier-4-recheck.txt` — §1c 1단계 `grep -cE '2개의|두 줄|365/3"' 01-plan.md` → `0`(exit 1 = 0건) · 2단계 `sed -n 55p … | grep -o "MEMORY_PROMOTE_MIN_EVENTS=5" | wc -l` → `1` — 둘 다 기대와 일치. §2 `grep -nE '2개의|두 줄|365/3"'` → 0건 · §3 `grep -nE '3개의|세 줄|365/3/5'` → 14·25·60·67행 · §4 25행 원문 "`.env.example` 에 그 3개의 기본값 줄(이름과 "비우면 기본 365/3/5" 설명만 …)" · §8 환경변수 개수 표기 25·67·74행 전부 "3개". `20260928-1442-verifier-4-verify-plan.txt` `== 결과: FAIL=0 WARN=0 ==`. **해소.**

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 — 25행은 60·67행과 같은 뜻이 됐고 D14 11행 "`.env.example` 에 기본값 줄"·security §1 "이름만" 그대로 충족(recheck §4). 함께 들어온 R-12(S3.5 6행 한 구절)·R-13·R-14 는 02-plan-verify §3-5 에서 확인 — 새 모순 없음
- FIX/CR 로 올려야 하는가: 아니오 (01-plan 한 구절 표기 수정, 코드·스키마·기본값 무변경 — recheck §10 `docs/` 밖 변경 0)

