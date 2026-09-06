# P1-pilot-dataset · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-06 17:37 | 출처: verify-plan | 열림: 0 (필수 0) | 해소: 1

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

