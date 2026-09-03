# D1 · 신규 인물 등록은 확인형

상태: 유효 | 해결하는 검증: R6 | 원문: `docs/resolution-plan.md` §1 D1

**결정** 확신도 `< T_new`이면 자동 `create_person` 하지 않고 `ask_user(kind="new_person")`로 "○○을 기억해둘까요?"를 묻는다. 승인 시에만 `create_person`.

**이유** 데모 1번·부록 채팅 화면이 확인형이다. 자동 등록은 지나가는 언급(연예인 등)을 카드로 만든다. "모른다를 판단하는 행동" 서사와 일치.

**파급** `ask_user.kind` ∈ {identity, new_person, schedule}. 지표 `ask_user_rate_by_kind`로 분리 집계 (S3.7).

**코드에서 지켜야 할 것** `create_person` 호출 경로는 반드시 answered pending_question 을 거친다. 직접 호출 테스트는 실패해야 한다.
