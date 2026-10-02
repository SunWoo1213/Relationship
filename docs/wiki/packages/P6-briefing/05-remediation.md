# P6-briefing · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-10-02 14:02 | 출처: verify-plan | 열림: 0 (필수 0) | 해소: 4

## F-ef47d1 · [필수] 없음: docs/wiki/packages/P6-briefing/02-plan-verify.md
상태: 해소 | 발견: 2026-10-02 (verify-plan) | 해소: 2026-10-02

### 증상 (검증 출력 인용)
```
FAIL  없음: docs/wiki/packages/P6-briefing/02-plan-verify.md
```

### 원인 분석
- 가설: verifier 가 02-plan-verify.md 를 쓰기 전에 기계 검증을 먼저 돌렸기 때문이다(위임 프롬프트가 "02 를 쓰기 전에 돌리면 FAIL 1 이 정상" 이라고 예고). 계획 자체의 결함이 아니다.
- 확인 방법(명령): `ls docs/wiki/packages/P6-briefing/02-plan-verify.md` → 02 작성 뒤 `bash .claude/scripts/verify-plan.sh P6-briefing` 재실행.
- 확인 결과: 1차 `evidence/20261002-1340-verify-plan.txt` 에서 `FAIL  없음: …/02-plan-verify.md` 1건 외 전부 PASS. 02 작성 뒤 재실행 결과는 아래 "재검증" 과 02-plan-verify §1 2차 출력에 있다.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/packages/P6-briefing/02-plan-verify.md` 작성(verifier, Write) | `bash .claude/scripts/verify-plan.sh P6-briefing` | `PASS  존재: …/02-plan-verify.md` | 완료(2026-10-02 13:48) |

### 재검증
- 명령: `bash .claude/scripts/verify-plan.sh P6-briefing`
- 결과 파일(evidence/): `evidence/20261002-1348-verify-plan-2.txt` — `PASS  존재: docs/wiki/packages/P6-briefing/02-plan-verify.md`, `== 결과: FAIL=0 WARN=1 ==`(WARN 은 `F-033bb1`)

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음
- FIX/CR 로 올려야 하는가: 아니오

## F-256944 · [필수] H-1 01-plan 74행(U4)·118행(판정 21행)의 `JudgeTimeout` 은 저장소에 없는 클래스다(grep 0건) — 기존 오류 어휘는 `JudgeUnavailable("timeout")`(app/er/types.py 49행, judge.py 232행)
상태: 해소 | 발견: 2026-10-02 (review) | 해소: 2026-10-02 (verifier 재검증 2차 13:59)

### 증상 (검증 출력 인용)
```
FAIL  H-1 01-plan 74행(U4)·118행(판정 21행)의 `JudgeTimeout` 은 저장소에 없는 클래스다(grep 0건) — 기존 오류 어휘는 `JudgeUnavailable("timeout")`(app/er/types.py 49행, judge.py 232행)
```

### 원인 분석
- 가설: architect 가 ER 오류 어휘(D11 "`timeout/rate_limit/api_error/connection/schema/out_of_range_id` 6종")를 **클래스 이름**으로 잘못 옮겨 적었다. 실제 어휘는 예외 클래스 하나(`JudgeUnavailable`)의 **메시지 문자열**이다. 01-plan 139행이 "새 오류 클래스를 만들지 않는다" 고 스스로 정했으므로, 74행(U4)·118행(판정 21행)을 글자 그대로 구현하면 139행·D11 과 모순이 되고 판정 21행을 기계적으로 실행할 수 없다.
- 확인 방법(명령): `grep -rn "JudgeTimeout" app tests | wc -l` · `grep -n "^class Judge" app/er/types.py app/er/judge.py` · `grep -n '"timeout"' app/er/judge.py`
- 확인 결과: `evidence/20261002-1340-verifier-fact-checks.txt` §5 — `JudgeTimeout` 0건; 클래스는 `app/er/types.py` 49행 `class JudgeUnavailable(Exception)` 뿐이고, `judge.py` 232·625행이 `raise JudgeUnavailable("timeout")` 로 어휘를 쓴다. 조치는 계획 문서 두 곳(74·118행)의 이름을 `JudgeUnavailable("timeout")` 로 바꾸는 것뿐(architect 또는 메인 세션, 코드 무변경). 02-plan-verify §3 H-1.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `01-plan.md` 판정 표 21행의 `JudgeTimeout` → `JudgeUnavailable("timeout")`(메인 세션, Edit, 사용자 승인 2026-10-02). 74행(U4)에는 `JudgeTimeout` 문자열이 없었다(`grep -n Judge 01-plan.md` 가 118행 1건뿐) — 소견 제목의 "74행" 은 위치 오기 | `grep -c "JudgeTimeout" docs/wiki/packages/P6-briefing/01-plan.md` · `grep -c 'JudgeUnavailable("timeout")' docs/wiki/packages/P6-briefing/01-plan.md` | `0` · `1` | 완료(2026-10-02) — 실제 출력 `0` · `1` |

### 재검증
- 명령: `grep -c "JudgeTimeout" docs/wiki/packages/P6-briefing/01-plan.md` → 0 · `grep -c 'JudgeUnavailable("timeout")' docs/wiki/packages/P6-briefing/01-plan.md` → 1 (원래 기대 "2 이상" 은 74행 오기에 기댄 값 — 바뀐 자리는 한 곳뿐이다)
- 결과 파일(evidence/): `evidence/20261002-1359-reverify.txt` "F-256944 (H-1) 재검증" — verifier(fable) 직접 실행. `grep -c "JudgeTimeout" 01-plan.md` = **0**, `grep -c 'JudgeUnavailable("timeout")' 01-plan.md` = **1**(118행 판정 21행 한 곳, `app/er/types.py` 49행·`judge.py` 232행 인용이 현재 코드와 일치 — 같은 파일에 `grep -n "^class Judge"`·`grep -n 'JudgeUnavailable("timeout")'` 출력 49·232·625행). 코드에 `JudgeTimeout` 0건, `git diff --stat 36c288e -- app tests` 빈 출력(코드 무변경). **판정: 해소** — 해소 조건(계획 문서에 존재하지 않는 이름 0건, 기존 어휘 한 곳)이 충족됐다.
- verifier 소견(2차): 해결 단계 표의 "74행 은 위치 오기" 주장은 **증거로 확정할 수 없다** — 01-plan 은 미추적 파일이라 수정 전 이력이 없고, 1차 `evidence/20261002-1340-verifier-fact-checks.txt` §5 는 `grep -rn JudgeTimeout app tests` 만 기록했지 01-plan 자체의 `grep -n` 출력은 남기지 않았다(1차 verifier 의 기록 누락). 현재 74행에는 `Judge` 문자열이 없다(reverify.txt `sed -n 74p | grep -c Judge` = 0). 어느 쪽이든 해소 조건과 무관하므로 판정에 영향 없음.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 있음 → D11 "코드에서 지켜야 할 것" 어휘 6종만(새 클래스 금지). 문서 오기이므로 이름만 고치면 충돌이 사라진다.
- FIX/CR 로 올려야 하는가: 아니오(계획 문서 수정)

## F-4029df · [필수] H-2 결정 B(i) `now ≤ scheduled_at ≤ now+24h` 는 S3.6·resolution-plan §3.6 공식 `scheduled_at - now() ≤ 24h` 의 해석이 아니라 하한을 더한 명세 좁힘이다 — S3.6 카드·resolution-plan §3.6 에 한 줄 보충 필요(CR 불필요)
상태: 해소 | 발견: 2026-10-02 (review) | 해소: 2026-10-02 (verifier 재검증 2차 13:59)

### 증상 (검증 출력 인용)
```
FAIL  H-2 결정 B(i) `now ≤ scheduled_at ≤ now+24h` 는 S3.6·resolution-plan §3.6 공식 `scheduled_at - now() ≤ 24h` 의 해석이 아니라 하한을 더한 명세 좁힘이다 — S3.6 카드·resolution-plan §3.6 에 한 줄 보충 필요(CR 불필요)
```

### 원인 분석
- 가설: S3.6 카드 1행과 `docs/resolution-plan.md` 197행의 공식 `scheduled_at - now() ≤ 24h AND briefed_at IS NULL` 은 상한만 있다 — 지난 일정(차이가 음수)도 글자 그대로 만족한다. 결정 B(i) 는 하한 `now ≤ scheduled_at` 을 더해 선정 집합을 **줄인다**. 집합이 달라지므로 "해석" 이 아니라 명세의 좁힘이다. 기획 의도(CLAUDE.md "만남 직전에 필요한 맥락만 요약", `get_briefing` 의 `upcoming_schedules` 가 이미 `scheduled_at >= now` 로 과거를 제외)와는 맞으므로 **결정 자체는 타당**하고, 필요한 것은 명세 문장을 결정과 일치시키는 보충이다. 기획서 본문(`docs/proposal.md`)에는 24h 공식이 없고(150행 스키마 줄뿐), 관련 D 카드도 없으며, R12 검증 항목·backlog 수용 기준은 바뀌지 않으므로 CR 은 필요 없다(CR-002 가 "기획서 본문에 숫자 없음 → 본문 그대로" 로 처리한 선례와 같은 조건이나, 그때는 D 카드·CLAUDE.md 원칙6 문장이 바뀌어 CR 이었다 — 여기는 S 카드 한 줄뿐).
- 확인 방법(명령): `grep -n "24h\|24시간\|scheduled_at - now" docs/proposal.md` · `sed -n 195,198p docs/resolution-plan.md` · `sed -n 29,30p app/tools/briefing.py`
- 확인 결과: `evidence/20261002-1340-verifier-fact-checks.txt` §12(기획서에 공식 없음, resolution-plan 197행 원문)·§17(`get_briefing` 과거 제외 선례). 조치(메인 세션, verifier 는 카드를 고치지 않는다): ① `docs/wiki/specs/S3.6-briefing-push.md` 1행 뒤에 한 줄 — "창은 `now ≤ scheduled_at ≤ now + 24h`(지난 일정 제외 — P6-briefing 결정 B(i), 2026-10-02 사용자 확정). `get_briefing` 의 `upcoming_schedules` 와 같은 방향." ② `docs/resolution-plan.md` 197행 끝에 같은 뜻의 괄호 주석 한 줄(CR-002 가 §3.5 에 주석을 단 방식). ③ 01-plan 판정 표 6행 기대 출력을 "선정 안 됨" 으로 확정 표기. U2 커밋 전에 끝나면 된다(승인 커밋에 포함 가능). 02-plan-verify §3 H-2.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `docs/wiki/specs/S3.6-briefing-push.md` 1행 아래 보충 줄(창 `now ≤ scheduled_at ≤ now + 24h`, 지난 일정 제외, 결정 B(i)) | `grep -c "now ≤ scheduled_at" docs/wiki/specs/S3.6-briefing-push.md` | `1` | 완료(2026-10-02) — 실제 `1` |
| 2 | `docs/resolution-plan.md` §3.6 197행 아래 괄호 보충 줄(CR-002 §3.5 방식) | `grep -c "now ≤ scheduled_at" docs/resolution-plan.md` | `1` | 완료(2026-10-02) — 실제 `1` |
| 3 | `01-plan.md` 판정 표 6행 기대값을 "선정 안 됨(결정 B(i) 확정, S3.6 카드 보충 줄)" 로 확정, 조건문 제거(R-7 함께) | `grep -c "선정 안 됨(결정 B(i) 확정" docs/wiki/packages/P6-briefing/01-plan.md` · `grep -c "(ii) 를 고르면 선정됨" docs/wiki/packages/P6-briefing/01-plan.md` | `1` · `0` | 완료(2026-10-02) — 실제 `1` · `0` |

### 재검증
- 명령: `grep -n "now ≤ scheduled_at\|지난 일정 제외" docs/wiki/specs/S3.6-briefing-push.md docs/resolution-plan.md` → 각 1건 이상 · `sed -n 103p docs/wiki/packages/P6-briefing/01-plan.md` 에 "선정 안 됨" 만 남음
- 결과 파일(evidence/): `evidence/20261002-1359-reverify.txt` "F-4029df (H-2) 재검증" — verifier(fable) 직접 실행. ① `S3.6-briefing-push.md` 6행·`resolution-plan.md` 198행에 `now ≤ scheduled_at ≤ now + 24h` + "지난 일정 제외" 각 1건. `git diff --numstat` = 두 파일 모두 **추가 1 / 삭제 0** — 원 공식(S3.6 5행·resolution-plan 197행)은 지워지지 않고 그대로이며 보충 줄이 "위 공식은 원 결정 기록" 이라고 명시. ② 01-plan 103행(판정 6행) = "선정 안 됨(결정 B(i) 확정, S3.6 카드 보충 줄)", 조건문(`(ii) 를 고르면 선정됨`·`권장안 (i) 이면`) 0건. ③ CR 조건 재확인: `docs/proposal.md` 에 `24h`·`scheduled_at - now` 0건, `git diff --stat -- docs/proposal.md docs/wiki/decisions CLAUDE.md docs/backlog.md docs/wiki/review-index.md` 빈 출력(기획서·D 카드·원칙·수용 기준·R12 무변경). ④ 보충이 인용한 선례 `app/tools/briefing.py` 29행 docstring·124행 `.where(Schedule.scheduled_at >= now)` 실존. ⑤ 같은 공식을 적은 다른 카드 없음(`grep -rn "24h|scheduled_at - now|now ≤ scheduled_at" docs/wiki/specs docs/wiki/decisions docs/wiki/review-index.md` → S3.6 두 줄 외에는 D02 의 "미답변 24h 만료" 뿐이고 무관). **판정: 해소** — 명세 문장과 결정 B(i) 가 일치하고 새 충돌·CR 사유가 생기지 않았다.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 있음 → S3.6 1행(보충 전까지). D 카드 충돌 없음. 원칙 충돌 없음.
- FIX/CR 로 올려야 하는가: 아니오(S 카드·resolution-plan 한 줄 보충, 문서 FIX 수준 — CR 조건인 기획서 본문·D 카드·검증 항목 변경이 없다)

## F-033bb1 · [권고] 보류 2 건 — 결과는 통과가 될 수 없다
상태: 해소 | 발견: 2026-10-02 (verify-plan) | 해소: 2026-10-02

### 증상 (검증 출력 인용)
```
WARN  보류 2 건 — 결과는 통과가 될 수 없다
```

### 원인 분석
- 가설: 이 WARN 은 독립 소견이 아니라 02-plan-verify 점검표 행 3·4 의 보류(H-1 `F-256944`, H-2 `F-4029df`)를 `verify-plan.sh` 가 세어 낸 것이다. 두 [필수] 소견이 닫히고 verifier 가 점검표 행 3·4 를 통과로 바꾸면 같은 명령에서 사라진다.
- 확인 방법(명령): `grep -E '^\| [1-8] \|' docs/wiki/packages/P6-briefing/02-plan-verify.md | grep -c '보류'` → 두 소견 해소 뒤 0.
- 확인 결과: 2차 `evidence/20261002-1348-verify-plan-2.txt` `WARN  보류 2 건`(행 3·4). 해소 조건은 `F-256944`·`F-4029df` 의 재검증 명령 그대로.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `F-256944`·`F-4029df` 해소 뒤 verifier 가 02-plan-verify 행 3·4 를 통과로 재판정 | `bash .claude/scripts/verify-plan.sh P6-briefing` | `PASS  보류 0건`, `== 결과: FAIL=0 WARN=0 ==` | 완료(2026-10-02 14:01, verifier) — 실제 `PASS  보류 0건` · `== 결과: FAIL=0 WARN=0 ==` |

### 재검증
- 명령: `bash .claude/scripts/verify-plan.sh P6-briefing`
- 결과 파일(evidence/): `evidence/20261002-1401-verify-plan-3.txt` — `PASS  보류 0건`, `== 결과: FAIL=0 WARN=0 ==`. 같은 파일로 `bash .claude/scripts/findings.sh P6-briefing … --source verify-plan` 실행(14:02) → "해소 1 (`F-033bb1`), 열림 0 (필수 0)". 02-plan-verify §1 3차 출력과 같다.

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음(파생 소견)
- FIX/CR 로 올려야 하는가: 아니오

