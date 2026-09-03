# <패키지 id> · 계획 검증 (02-plan-verify)

대상: 01-plan.md | 검증자: | 날짜: YYYY-MM-DD

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `bash .claude/scripts/verify-plan.sh <패키지 id> | tee docs/wiki/packages/<id>/evidence/<ts>-verify-plan.txt`
```
(출력 전체)
```
FAIL 이 하나라도 있으면 아래 결과는 통과가 될 수 없다. FAIL/WARN 은 `python .claude/scripts/findings.py <id> evidence/<ts>-verify-plan.txt --source verify-plan` 으로 05-remediation.md 에 소견으로 올리고, 조치 후 다시 실행한다.

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과/보류 | |
| 2 | 불변 원칙 1~9 위반 없음 | | |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | | |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | | |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | | |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | | |
| 7 | 작업 단위마다 Refs 태그 | | |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | | |

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)
-

## 4. 결정
결과: 통과 | 보류
승인: (사용자 승인 전 비워 둔다 → "사용자 (YYYY-MM-DD)")
