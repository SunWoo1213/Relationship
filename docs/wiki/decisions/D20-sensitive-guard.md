# D20 · 민감 정보 가드레일 — LLM 전 서버 규칙 검사, 식별·인증 정보 가림, 민감 범주 건별 동의, 가입 때 OpenAI API 전송 고지

상태: 유효 | 해결하는 검증: (직접 R 없음 — 기획서 9장 "제3자 개인정보" 행 `docs/proposal.md:264` 의 대응을 구체화. 간접: R7·R10·R12·R19) | 출처: CR-009 (제기 2026-11-18, 사용자 결정 21건 2026-11-22, verifier 재검토(개정 2) "이행 가능") · 원문 `docs/wiki/changes/CR-009.md`(개정 3)

> 이 카드의 범주 정의는 **법령상 분류가 아니다** — 이 프로젝트가 쓴 짧은 정의다. 이 카드는 법적 적법성·충분성을 판단하지 않는다. 가드레일은 **완화이며 기록 대상(제3자)의 동의 문제는 해결하지 않는다**(CR-009 W1).

**사용자 원문**
1. (2026-11-18) "민간한 내용에 대한 가드레일이 없는 것 같아 예를들어서 누군가가 마약을 했다 이런식으로 해버리면 그냥 들어가네"
2. (2026-11-18) "권장안으로 평가 뒤에 진행해줘" → 5 로 바뀜
3. (2026-11-18) "법적으로 문제가 되는 내용을 차단하고 싶은거야 혹은 사용자가 동의를 하면 들어갈 수 있게 민간 정보는 ChatGPT로 넘어간다는 알림이 있어야 할 것 같아."
4. (2026-11-18) "1 ~ 4번을 모두 계획을 세워서 독립검토 해줘"
5. (2026-11-18) "서버를 좀 더 열어야해 가드레일에 관련한 민감정보는 어떻게 할건지 피드백을 받았기 때문에 그걸 해결할 때까지.." · "그대로 두고 가드레일 본작업 먼저 진행해줘"
6. (2026-11-22) "11월 18일 것을 해결하려고 해" · "진행해주세요" — 이어서 AskUserQuestion 으로 결정 21건(아래)

**사용자 결정 21건 (번호는 CR-009 3.2 표 그대로)**
1. 범죄·불법 = 동의하면 저장. 가림(차단)은 식별·인증 정보에만
2. 건강 = 좁은 범위만 동의 대상(정신과 진료·정신질환 진단, 중증·난치 질환, 성병·HIV 등). "감기 걸렸대" 는 지금처럼
3. 동의하고 저장한 민감 항목은 **인물 카드에서만** — 브리핑·푸시·MCP·조회 답에 나가지 않는다
4. 규칙이 놓친 문장은 저장 전에 한 번 더 묻는다(사후 확인)
5. 기존 가입자 = 다음 접속 때 모달 한 번, 로그인돼 있는 세션에도 바로, 동의 전 채팅 전송 403, 문구가 바뀌면 다시
6. 가림 = 주민등록번호·계좌번호·카드번호·비밀번호 + 여권번호·운전면허번호. 전화번호·주소는 지금처럼 기억
7. 전송처 표기 "OpenAI API". 약관 내용(보관 기간·학습 사용)은 단정하지 않는다
8. 동의 전 원문 = 대기 중 보관, 거절·만료 시 대화 기록 줄 대체 + 대기 질문·trace 원문 삭제. 범주·규칙 id·동의 기록은 남김
9. 기존 데이터 소급하지 않음(배포 이후 입력에만)
10. 운영 반영은 다 끝난 뒤 한 번에(백업 → 0006 → 재배포 → 바깥 확인 → 기존 가입자 재고지 실제 확인)
11. 완료 = 운영 반영 + 평가 보고서 + verifier 완료 검토 + 사용자 화면 확인. 서버 종료일은 그때
12. 시험 세트 = 범주·유형별 민감 15~20 + 평범 100 + 함정 30 + 우회 20, dev·test 각각
13. 사전 검사에 걸린 조회형 문장 = 같은 칩·중립 문구. 답은 일반 기록만, 민감만 있으면 카드 안내 한 줄
14. 추출 LLM 이 사후에 민감으로 표시한 문장은 조회여도 묻는다 — 판정·임베딩·조회 답 LLM 전에 멈춤, 거절하면 대화 기록·trace 에서 지움, 규칙이 잡았을 때와 같은 처리
15. 민감 낱말이 든 표현이 이름·별칭으로 저장되려 할 때 = 저장하지 않고 안내, "새로운 사람인가요?" 전에 멈춤
16. 403 은 칩 답변(`POST /answers/{id}`)에도. 동의하면 떠 있던 칩에 그대로 답할 수 있다
17. 고지 미동의 계정 = 주기 브리핑 생성·푸시도 건너뜀
18. 문구 확정안(CR-009 8.2)
19. 문구 세 곳 수정(사전 동의 칩·사후 확인 칩·가입 고지 문단 — CR-009 8.2 ①②④)
20. 사후 표시된 조회 문장 칩 = 전용 문구(CR-009 8.2 ⑥)
21. 수동 브리핑 `POST /briefings/run` 도 미동의면 403 `notice_required`, 고지 모달로 잇는다

메인 세션 결정: P9b-auth 보류 → P9d 활성 · 만료 정리는 기존 1분 루프의 주기 작업 · 0006 downgrade 는 민감 행이 있으면 명시적 실패.

**결정**
1. **3단 가드**: ① 식별·인증 정보(6종)는 LLM 호출 **전**에 서버가 유형별 자리표시(`[주민등록번호]` 등)로 가리고 가린 문장만 처리·저장한다 ② 동의 범주(`crime`·`health`(좁음)·`sex`·`politics_religion`·`finance` — 이름은 01-plan 확정, 개수 5)는 칩 동의 **전에는 OpenAI 호출 0** ③ 가입 때(기존 가입자는 다음 접속 때 모달) OpenAI API 전송 고지·필수 동의, 판 번호 `PRIVACY_NOTICE_VERSION`.
2. **규칙 검사는 서버 안, LLM 0·네트워크 0의 순수 함수**(`app/guard/`). 낱말·정규식 목록은 코드 상수 한 파일, dev 세트로만 다듬는다. 규칙 id 는 낱말을 드러내지 않는 번호(`<범주|유형>.<세 자리>`).
3. **사전 동의 질문**은 라우트가 `ask_user` **툴을 부르지 않고** `pending_questions` 저장소에 쓴다(`kind="sensitive"`, phase `pre`). `ask_user` 정의("에이전트가 모른다를 스스로 판단")는 루프가 부르는 질문에만 남는다. **사후 확인 질문**(phase `post`, 기록·조회 모두)은 루프가 `ask_user` 툴로 부른다. 긍정 답 규약은 기존 형식(비어 있지 않은 문자열 리스트), `sensitive` 는 `_AFFIRMATIVE_REQUIRED_KINDS` 에 든다.
4. **표시 단위 = 턴**: 동의 턴(후속 질문 사슬 끝까지)에서 저장되는 사건·사실·일정 전부 `sensitive_category`. 인물 행·관계 태그·위계는 표시 대상 아님.
5. **민감 항목은 인물 카드 계층에서만**(카드·원문 조회 2·자기 대화 기록). 그 밖 모든 내보내는 경로는 기본 제외(fail-closed).
6. 고지 미동의 계정: `POST /chat`·`POST /answers/{id}`·`POST /briefings/run` 403 `notice_required`, 주기 브리핑·푸시 건너뜀. 로그인 없이 열린 예외 경로는 늘지 않는다.
7. 기존 데이터 소급 없음. 운영 반영은 모든 단위·평가·완료 검토 뒤 한 번.

**이유**
- 원문 1 의 문장은 지금 아무 검사 없이 OpenAI 로 가고 카드·브리핑·푸시·MCP·조회 답으로 다시 나간다. LLM 으로 감지하면 이미 전송된 뒤라 **LLM 전 규칙 검사**가 먼저여야 한다(규칙이 놓친 것은 고지와 사후 확인이 받친다 — 사후 확인은 "전송 전" 이 아니라 "저장 전" 동의다).
- 오병합과 같은 모양의 비대칭: 민감한데 일반으로 저장(미검출)이 일반인데 묻기(오탐)보다 나쁘다 → 턴 단위 표시·사실 표시 단조·내보내기 기본 제외.
- 동의 질문을 `pending_questions` 에 두면 칩·1회 소비·남의 질문 404·만료·대화 기록 `question_id` 를 재사용한다(중복 구현 0). 사전 질문을 툴로 부르지 않으면 `@traced` 가 원문을 trace 에 복제하지 않는다.

**파급**
- S3.1(리비전 0006) · S3.2(`ask_user.kind` 4종, `get_briefing` 제외 동작, 이름 규칙) · S3.4(`sensitive` 두 갈래) · S3.5(사실 표시 단조·승격 입력 제외) · S3.6(미동의 건너뜀·브리핑 제외 자리) · S3.7(민감 가드 시험 세트).
- D2·D14·D16·D17·D18·D19 보충. CLAUDE.md 원칙6·7·9 구절, 툴 표 아래 kind, 데이터 모델 0006, 기술 스택(인증 고지·운영 기간). security §5. 기획서 상단 한 줄.
- 패키지 `P9d-sensitive-guard`(U0~U12, CR-009 4.2).

**코드에서 지켜야 할 것 — ① 수용 기준 표(CR-009 4.3)**
| # | 기준 | 판정 명령 | 단위 |
|---|------|-----------|------|
| 1 | 동의 범주 문장은 동의 전 LLM·임베딩 호출 0 | `pytest tests/test_guard_pre.py -q` | U5b |
| 2 | 차단 유형 원문은 DB 전 테이블·응답·로그에 없음 | `pytest tests/test_guard_mask.py -q` · `grep -rnE "logger\.\|print\(" app/guard` 0줄 | U5a |
| 3 | 규칙 검사는 `append_chat_message`·`run_turn` 보다 앞 | `pytest tests/test_guard_mask.py tests/test_guard_pre.py -q` + 변이 | U5a·U5b |
| 4 | 거절·만료 뒤 원문(발화·제안 내용)이 DB 전 테이블(trace 포함)에 0, 질문 context 는 R-2 남기는 키만, 동의 기록은 남음 — 사전·사후(기록·조회) 모두 | `pytest tests/test_guard_resume.py tests/test_guard_posthoc.py -q` | U5c·U6 |
| 5 | 사후 표시 턴은 기록이든 조회든 저장·ER 판정 LLM·임베딩·조회 답 LLM 전에 멈춤 | `pytest tests/test_guard_posthoc.py -q` | U6 |
| 6 | 동의 턴 저장물 전부 표시, 후속 질문 사슬 끝까지, 바이트 절단 뒤에도 | `pytest tests/test_guard_storage.py -q -k chain` | U7 |
| 7 | 사실 표시는 단조 규칙 하나(R-5) | `pytest tests/test_guard_storage.py -q -k monotone` | U7 |
| 8 | 민감 항목은 카드 계층에서만, 제외 경로 열거 시험으로 0 | `pytest tests/test_guard_export.py -q` | U8 |
| 9 | 카드 읽기 함수 기본값이 제외 | 같은 시험 + 변이 | U8 |
| 10 | 가입 고지 필수, 기존 계정 `notice_required`, 미동의 `/chat`·`/answers`·`/briefings/run` 403·LLM 0, 미동의 계정 주기 브리핑·푸시 0 | `pytest tests/test_privacy_notice.py tests/test_briefing_scheduler*.py -q` | U4 |
| 10b | 이름 규칙에 걸린 언급은 별칭·표시 이름 저장 0, identity·new_person 질문 생성 전에 멈춤 | `pytest tests/test_guard_storage.py -q -k name` | U7 |
| 11 | 로그인 없이 열린 경로 수 변화 0 | `pytest tests/test_auth_required_routes.py -q` | U4 |
| 12 | 툴 7종 시그니처 불변, ER·임계치·확신도 무변경 | `python3 scripts/tools_check.py`(7/7) · `git diff --stat <U0 해시> -- app/er/` 0줄(작업 트리 포함 모양 — 재검토 VR3) | 전 단위 |
| 13 | 가드 문구가 이 카드에 적힌 확정 문구와 문자열 일치, `BRIEFING_FORBIDDEN_EXPRESSIONS` 어느 항목도 포함 안 함(목록은 검사 도구로만 재사용, 합치지 않음) | `pytest tests/test_guard_messages.py -q` | U4·U5a·U5b·U6·U7·U8·U9a |
| 14 | `pending_questions.kind` CHECK 4종, downgrade 는 민감 행이 있으면 실패하고 데이터 불변 | `pytest tests/test_schema_0006.py -q` | U3 |
| 15 | 배포 전 모양의 대기 질문은 가드를 거치지 않고 재개되지 않음 | `pytest tests/test_guard_resume.py -q -k legacy` | U5c |
| 16 | 감지율·오탐률·실패 사례가 test 세트(동결)로 재현 가능, 규칙·LLM 수치 분리 | `python3 -I evaluation/sensitive_guard/run.py --split test` | U1·U10 |
| 17 | 완료 = 운영 반영 증거 + 평가 보고서 + verifier 완료 검토 `결과: 완료` + 사용자 화면 확인 | U12 증거 · `reports/sensitive_guard.md` · 04-review | U10·U11·U12 |

**코드에서 지켜야 할 것 — ② 규칙 R-1~R-12(CR-009 4.4)**
- **R-1 원문 보관 자리**: 사전 동의 대기 중 원문(식별 정보는 가린 것)은 `pending_questions.context.utterance` 와 그 사용자 줄 `chat_messages` 한 줄에만. 사전 경로는 `ask_user` 툴(`@traced`)을 부르지 않으므로 trace 에 원문 0.
- **R-2 거절·만료 때 질문·대화 기록에서 지우는 것**: `kind='sensitive'` 질문의 context 는 **남기는 키 — `phase`·`intent`·`categories`·`rule_ids`·`chat_message_id`·`turn_trace_range`·`AFFIRMATIVE_KEY`·`redacted`(true) — 밖의 키를 전부 지운다**(`utterance`·`pending_calls`·`held_drafts`·`mention`·`resume`·`hints`·`candidate_ids` 등 앞으로 더해질 키 포함). 대화 기록 줄 → "(기억하지 않은 민감한 내용)". 질문 행·`question`·`options`·`answer`·`answered_at`·`guard_check` trace 는 남는다.
- **R-3 거절·만료 때 trace 에서 지우는 것(사후)**: 같은 `session_id` 이고 id 가 `turn_trace_range`(라우트가 `run_turn` 직전·직후의 그 세션 최대 trace id 로 만든 구간) 안인 모든 행의 `input`·`output` 을 `{"redacted":"sensitive_declined","categories":[...],"rule_ids":[...]}` 로 바꾼다. 행·step·tool_name·토큰·시각은 남긴다. 거절 분기는 `resume_turn` 앞에서 끝난다. trace 를 덮어쓰는 **유일한** 자리는 `app/guard/consent.py::redact_declined` 이다(원칙9 예외 — 판정 메타는 남기고 사용자가 거절한 원문만 지운다).
- **R-4 남는 흔적**: 거절 뒤에도 범주·규칙 id·질문 행이 남는다 — 그 자체가 흔적이다(받아들인 위험).
- **R-5 사실 표시 단일 규칙**: 사실의 민감 여부는 `person_facts.sensitive_category` 컬럼 하나. 모든 쓰기(`update_person` upsert·`direct_facts`·승격 `_upsert_fact`)는 `COALESCE(기존값, 이번 쓰기의 범주)` 로만 바꾼다 — 올라가기만 한다. `fact_sources` 링크를 끊지 않는다. 브리핑 근거 원문은 사건 표시로도 거른다.
- **R-6 내보내는 경로**: 카드 계층(포함) = `GET /persons/{id}`(`include_sensitive=True`) · `GET /events/{id}/raw` · `GET /persons/{id}/facts/{fid}/sources` · `GET /chat/history`(자기 대화 기록). 제외 = `GET /persons`(`last_contact_at` 일반 사건만) · MCP 4도구(`sensitive_category` 키 제거, D19 모양 불변) · `get_briefing`(사실·최근 사건·다가오는 일정, 상한은 거른 뒤, 민감 대상 일정은 `ScheduleNotFound`) · 브리핑 입력 사실 재조회·`_fact_sources` · 브리핑 일정 선정(기본·수동, 수동은 skip 사유 `sensitive_schedule`) · 브리핑 LLM 프롬프트 · 푸시 · 조회 답 프롬프트·응답(민감만 있으면 카드 안내) · 승격 추출 LLM. 배포 전에 만든 저장 브리핑은 그대로 나간다(결정 9). `GET /questions/pending` 문구는 고정 문장.
- **R-7 이름 규칙**: 별칭·표시 이름이 될 수 있는 문자열은 `name_allowed`(= `detect` 에 차단·동의 범주 0)를 거친다. 판정은 `app/agent/loop.py` 안이고 `app/er/`·툴 7종은 고치지 않는다 — 언급을 ER(`resolve()`)에 넘기기 **전**(`_resolve_mentions_impl` 안, `_ordered_mentions` 뒤), 재개 방어(identity 답 별칭·new_person 답 표시 이름 앞), `_execute_call` 의 LLM `update_person.new_alias`. 걸리면 그 별칭·인물 저장·임베딩 0, identity·new_person 질문 생성 0("새로운 사람인가요?" 전에 멈춤), 같은 턴의 다른 언급은 그대로, 답에 이름 거부 문구. 걸린 언급의 제안은 다른 언급의 되묻기 context 에도 실리지 않는다. 정확한 줄 자리는 01-plan. **원칙2 와의 관계**: 이것은 확신도 판정 **이전**의 제외이며 병합·생성·질문 어느 것도 하지 않는다 — "임계치 미만은 반드시 `ask_user`" 의 예외가 아니다(판정이 일어나지 않는다). 오병합이 생기지 않고(원칙1) ER 을 LLM 한 번으로 대신하지도 않는다(원칙4). **근거 trace**: 버린 판정마다 결정값·규칙 id·제안 인덱스를 남기는 행 하나(원문 0, 모양은 01-plan — 원칙9). **결과(사실대로)**: 배포 전에 이미 저장된 별칭에 민감 낱말이 있으면 그 별칭으로 부른 기록 턴은 ER 앞에서 잘려 그 인물에 더 기록되지 않는다(조회 턴은 별칭을 쌓지 않는 경로라 대상 아님). 사용자 결정 15 의 "저장되려 할 때" 보다 넓다 — 사용자 결정 대기(CR-009 8.4 N7).
- **R-8 승격 입력 제외**: 승격 추출 LLM 에 민감 사건 원문·민감 사실을 넣지 않고, 민감 사건은 최소 사건 수에도 세지 않는다(동의 뒤 재전송 0). 그 결과 동의한 민감 사건은 요약 사실로 이어지지 않는다.
- **R-9 동의 문맥 사슬**: `ToolContext.consent` 로 싣고, 그 턴의 모든 후속 질문 context 에 예약 키 `consent = {question_id, categories}`. 재개는 이 키로 되살린다. `_apply_resume_byte_limit` 는 `consent` 를 자르지 않는다.
- **R-10 배포 전 대기 질문**: 동의 문맥 없이 재개되는 질문은 저장된 `utterance` 에 `detect` 를 다시 돌려 걸리면 재개하지 않고 409 `expired` 와 같은 응답(LLM 0).
- **R-11 긍정 답 규약**: `sensitive` ∈ `_AFFIRMATIVE_REQUIRED_KINDS`, `context[AFFIRMATIVE_KEY]` 는 `options` 의 비어 있지 않은 문자열 리스트 부분집합.
- **R-12 JSONB 키**: P9d 가 JSONB 에 인물 id 를 넣을 때는 기존 키(`person_id`)만(`app/api/delete.py:59~63` 의무).
- 그 밖: 0006 downgrade 는 `kind='sensitive'` 행·민감 표시 행·`consent_question_id` 가 하나라도 있으면 아무것도 지우지 않고 실패. 만료 정리는 1분 루프의 **사용자 반복 밖 독립 단계** — `BRIEFING_SCHEDULER_ENABLED` 가 꺼진 환경에서는 만료 원문이 정리되지 않는다(`docs/RUNNING.md` 한 줄).

**확정 문구(사용자 결정 18·19·20 — 글자 그대로)**
1. 사전 동의 칩: "민감할 수 있는 내용이 들어 있어요. 이 문장은 분석을 위해 OpenAI API로 전송되고, 기록할 내용이면 저장돼요. 저장한 기록은 인물 카드에서만 보여요. 진행하면 입력한 문장이 대화 기록에 남고, 진행하지 않으면 지워져요. 진행할까요?" — [진행해요] [진행하지 않아요]
2. 사후 확인 칩: "민감할 수 있는 내용으로 보여요. 이 문장은 분석을 위해 이미 OpenAI API로 전송됐지만, 아직 저장하지 않았어요. 저장한 기록은 인물 카드에서만 보여요. 기억하면 입력한 문장이 대화 기록에 남고, 기억하지 않으면 지워져요. 기억할까요?" — [기억해요] [기억하지 않아요]
3. 차단 안내: "주민등록번호·여권번호·운전면허번호·계좌번호·카드번호·비밀번호로 보이는 부분은 가린 뒤 처리했어요."
4. 가입 고지 / 재고지 모달 문단: "이 서비스는 입력한 대화를 분석하고 기억하기 위해 그 문장을 OpenAI API로 전송합니다. 대화에 나오는 다른 사람에 관한 내용도 함께 전송·저장될 수 있습니다. 저장된 내용은 브리핑을 만들거나 질문에 답하거나 기억을 정리하는 과정에서 다시 OpenAI API로 전송될 수 있습니다. 동의를 거쳐 저장한 민감한 기록은 다시 전송하지 않습니다. 주민등록번호·여권번호·운전면허번호·계좌번호·카드번호·비밀번호로 보이는 부분은 전송 전에 가리고, 민감할 수 있는 내용은 보내기 전에 한 번 더 묻습니다. 다만 모든 경우를 찾아내지는 못합니다." — 체크 "위 안내를 확인했고 동의합니다(필수)"
5. 재고지 모달: 제목 "대화 전송 안내" + 4 와 같은 문단 + "동의하기 전에는 대화를 보낼 수 없어요." + [동의하고 계속하기]
6. 사후 표시된 조회 문장 칩: "민감할 수 있는 내용으로 보여요. 이 문장은 분석을 위해 이미 OpenAI API로 전송됐어요. 답을 찾으려면 한 번 더 전송돼요. 답에는 민감한 기록을 쓰지 않아요. 진행하면 입력한 문장이 대화 기록에 남고, 진행하지 않으면 지워져요. 진행할까요?" — [진행해요] [진행하지 않아요]
- 부속: 거절 뒤 "기억하지 않았어요." / 조회 안내 "민감한 기록은 인물 카드에서 확인할 수 있어요." / 민감 일정 "이 일정은 민감한 내용이라 브리핑과 알림을 보내지 않아요." / 이름 거부 "그 표현은 이름으로 기억하지 않아요. 이름이나 호칭으로 다시 말해 주세요." / 거절·만료 뒤 대화 기록 대체 줄 "(기억하지 않은 민감한 내용)"

**01-plan 에서 닫을 것**(재검토(개정 2) V-8 · CR-009 8.6)
1. VR1 사후 조회 재개의 함수·context 모양(언급 해석부터, `_run_query_turn` 쪽)
2. VR2 이름 규칙 ① 의 줄 자리, 첫 턴 제안 버리기와 `_pending_calls_from`, `_followup_new_person_turn` 을 자리로 넣을지
3. VR3 U4 가 고치는 시험 파일 목록(`tests/auth_helpers.py` + 가입 시험 4개 파일)과 diff 기준("목록 밖 0줄"), `git diff --stat <해시> -- …` 모양(작업 트리 포함) 세 곳
4. VR5 문구 ④·⑤ 의 주인(서버 상수인지 `web/` 만인지)·판 번호와 문구 변경을 묶는 판정·파일을 만드는 단위
5. VR6 이름 규칙 근거 trace 의 모양(이 카드에 규칙은 적음)
6. VR7 미동의 건너뜀의 자리(대상 사용자는 `persons.user_id` 에서 나오고 `users` 를 읽지 않는다)와 `briefing_run` trace 빈도(1분마다 쌓이는지)
7. VR8 사후 질문 context 의 `chat_message_id` 를 누가 싣는지(라우트 덧붙임 / ctx)
8. 행 번호 재확인 · `gitlog.sh FIX-015` · `loop.py:1322` 직접 읽기 · `turn_trace_range` 동시 요청 겹침의 크기 · R-10 규칙 목록 변경 창
9. 사용자 결정 대기: CR-009 8.4 **N7**(기존 별칭에 민감 낱말이 있을 때)

**갱신 이력**
- 2026-11-22 신설(CR-009 문서 이행, U0). 구현은 `P9d-sensitive-guard` — 완료 해시는 그때 적는다.
