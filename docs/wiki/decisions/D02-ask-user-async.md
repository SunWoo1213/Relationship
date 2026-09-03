# D2 · ask_user 는 비동기 대기 질문

상태: 유효 | 해결하는 검증: R7 | 원문: `docs/resolution-plan.md` §1 D2, §3.4

**결정** `ask_user(kind, question, options, context) → PendingQuestion`. 질문을 `pending_questions`에 저장하고 `{question_id, status:"pending"}`을 반환한 뒤 **그 턴을 종료**한다. `POST /answers/{question_id}`가 저장된 `context`로 루프를 재개한다.

**이유** 웹 채팅에서 툴이 한 HTTP 요청 안에서 사용자 답을 받을 수 없다. 인메모리 대기는 재시작에 사라진다.

**파급** `pending_questions` 테이블 (S3.1). 프론트 확인 칩 = 미답변 pending_questions 렌더링. 미답변 24h 만료. 답 없이 새 발화가 오면 대기 질문 유지하고 새 발화 우선.

**코드에서 지켜야 할 것** 동기 대기(sleep/poll) 금지. `ask_user`를 다른 툴에 합치지 않는다(원칙4 서사).
