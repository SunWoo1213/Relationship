# D6 · 승진 후 표시 이름

상태: 유효 | 해결하는 검증: R18 | 원문: `docs/resolution-plan.md` §1 D6

**결정** `display_name` = 사용자가 확인한 **가장 최근 호칭**. 이전 호칭은 `person_aliases`에 남기고 카드에 "이전: 김팀장"으로 표시. 데모 5번 브리핑은 "김부장 회의".

**코드에서 지켜야 할 것** `update_person(display_name=…)`은 사용자 확인(answered question)을 거친 경우에만. 별칭은 절대 삭제하지 않는다.
