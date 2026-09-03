# P0-embed-pilot · 검증 결과 조치 계획 (05-remediation)

> `findings.py` 가 검증 출력에서 만든다. 소견 본문(원인·해결 단계·재검증·영향)은 에이전트가 채우고, 해결 단계의 완료 판정 명령을 실제로 실행한 출력이 증거다. 소견은 지우지 않는다(해소만 한다).
> 루프: 검증 → 소견 → 단계별 조치 → 재검증(같은 명령) → 해소. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다.

갱신: 2026-09-03 19:33 | 출처: verify-impl | 열림: 0 (필수 0) | 해소: 1

## F-445cda · [필수] 04-review 수용 기준 표에 행이 없다
상태: 해소 | 발견: 2026-09-03 (verify-impl) | 해소: 2026-09-03

### 증상 (검증 출력 인용)
```
FAIL  04-review 수용 기준 표에 행이 없다
```

### 원인 분석
- 가설: `verify-impl.sh` 5번이 04-review 의 표를 `^## 수용 기준 대조` 로 찾는데, `templates/package-review.md` 의 제목은 `## 2. 수용 기준 대조`(번호 있음)라 절을 못 찾는다. 검증 스크립트와 템플릿의 불일치(하네스 버그).
- 확인 방법(명령): `grep -n "수용 기준 대조" docs/wiki/templates/package-review.md .claude/scripts/verify-impl.sh`
- 확인 결과: 템플릿 `## 2. 수용 기준 대조`, 스크립트 `awk '/^## 수용 기준 대조/` — 번호 접두가 있어 불일치 확인.

### 해결 단계 (단계 하나 = 확인 가능한 변경 하나)
| # | 변경 (파일 · 방법) | 완료 판정 명령 | 기대 출력 | 상태 |
|---|--------------------|----------------|-----------|------|
| 1 | `.claude/scripts/verify-impl.sh` 69행 awk 패턴을 `^## ([0-9]+[.] )?수용 기준 대조` 로(번호 유무 모두 허용) | `bash .claude/scripts/verify-impl.sh P0-embed-pilot \| grep "증거 확인"` | `PASS  증거 확인: …` 5행, `FAIL 04-review 수용 기준 표에 행이 없다` 없음 | 완료 |

### 재검증
- 명령: `bash .claude/scripts/verify-impl.sh P0-embed-pilot` (계획 단계면 `verify-plan.sh P0-embed-pilot`)
- 결과 파일(evidence/): evidence/20260903-verify-impl-2.txt

### 영향 확인
- 관련 카드(D/S/원칙)와 충돌: 없음 | 있음 → 어느 카드
- FIX/CR 로 올려야 하는가: 아니오 | 예 (FIX-nnn / CR-nnn)

