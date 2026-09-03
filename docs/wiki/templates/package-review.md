# <패키지 id> · 완료 검토 (04-review)

날짜: | 검토자: verifier (fable) — 구현자와 다른 모델·컨텍스트(L-002)

## 1. 기계 검증 출력 (그대로 붙인다)
명령: `bash .claude/scripts/verify-impl.sh <id> | tee docs/wiki/packages/<id>/evidence/<ts>-verify-impl.txt`
```
(출력 전체)
```
FAIL 은 `findings.py … --source verify-impl` 로 05-remediation.md 에 올리고 조치·재검증한다. 열린 [필수] 소견이 있으면 결과는 완료가 될 수 없다.

## 2. 수용 기준 대조
증거 열은 `evidence/` 파일, 커밋 해시(7자 이상), 존재하는 파일 경로 중 하나여야 한다(`verify-impl.sh` 가 실재를 검사한다). 문장만 있는 증거는 FAIL.

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| | evidence/… | 통과/미달 |

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)
| 케이스 | 명령 | 증거 |
|--------|------|------|

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
-

## 5. registry.md 에 올린 산출물
-

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견
-

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)
-

결과: 완료 | 부분완료
승인:
