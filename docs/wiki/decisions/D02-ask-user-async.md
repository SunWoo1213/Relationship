# D2 · ask_user 는 비동기 대기 질문

상태: 유효 | 해결하는 검증: R7 | 원문: `docs/resolution-plan.md` §1 D2, §3.4

**결정** `ask_user(kind, question, options, context) → PendingQuestion`. 질문을 `pending_questions`에 저장하고 `{question_id, status:"pending"}`을 반환한 뒤 **그 턴을 종료**한다. `POST /answers/{question_id}`가 저장된 `context`로 루프를 재개한다.

**이유** 웹 채팅에서 툴이 한 HTTP 요청 안에서 사용자 답을 받을 수 없다. 인메모리 대기는 재시작에 사라진다.

**파급** `pending_questions` 테이블 (S3.1). 프론트 확인 칩 = 미답변 pending_questions 렌더링. 미답변 24h 만료. 답 없이 새 발화가 오면 대기 질문 유지하고 새 발화 우선.

**코드에서 지켜야 할 것** 동기 대기(sleep/poll) 금지. `ask_user`를 다른 툴에 합치지 않는다(원칙4 서사).

**보충(CR-009 · D20, 2026-11-22)** `kind` 값 집합이 4종이 된다(`identity`·`new_person`·`schedule`·`sensitive`). 비동기 모델(저장 → 턴 종료 → 칩 → 재개)은 그대로. 질문을 만드는 쪽이 둘로 나뉜다: ① **사전 동의 질문**(LLM 전 서버 가드)은 라우트가 `ask_user` **툴을 부르지 않고** 같은 저장소(`pending_questions`)에 쓴다 — "에이전트가 모른다를 스스로 판단하는 행동" 이라는 툴 정의는 루프가 부르는 질문에만 남고, 툴의 `@traced` 가 원문을 trace 에 복제하지 않는다 ② **사후 확인 질문**(추출 LLM 이 민감 표시)은 루프가 `ask_user` 툴로 부른다. `sensitive` 는 긍정 답 규약(`_AFFIRMATIVE_REQUIRED_KINDS`)에 든다. 거절·만료 때의 원문 지우기는 D20 R-2·R-3.
