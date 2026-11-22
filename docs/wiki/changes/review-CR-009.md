# review-CR-009 · 민감 정보 가드레일 초안 독립 검토

**판정: 수정 뒤 이행** — 방향(차단·건별 동의·전반 고지, LLM 전 규칙 검사, fail-closed 내보내기)은 원칙·카드와 큰 충돌이 없다. 그러나 [필수] 9건이 열려 있고, 그중 4건(M2·M3·M4·M5)은 초안이 내건 수용 기준(4.3 #2·#4·#7)을 지금 설계대로는 만족시킬 수 없게 만든다. 다시 쓸 필요는 없고, 아래 [필수]를 반영한 개정 1 이면 이행할 수 있다.

검토자: verifier (fable) | 검토일: 2026-11-18 | 대상: `docs/wiki/changes/CR-009.md`(316행, 미커밋 초안) | 기준 커밋: `cef47d0`
이 문서는 초안·카드·코드를 고치지 않는다. 법적 판단은 하지 않는다.

---

## 1. 본 것

- 초안 전문(1~316행), `docs/wiki/templates/change-request.md`
- 코드: `app/api/routes.py` 196~559행(`submit_answer`·`_record_loop_error`·`chat`·읽기 라우트), `app/agent/loop.py` 1087~1187행(`run_turn`)·1790~1982행(`resume_turn`)·함수 목록, `app/tools/questions.py` 90~324행, `app/tools/context.py` 90~268행(`ToolContext`·`traced`), `app/mcp_server/tools.py` 전부, `app/briefing/inputs.py` 전부, grep 으로 `app/api/read.py`·`app/briefing/select.py`·`compose.py`·`run.py`·`app/push/payload.py`·`app/tools/briefing.py`·`app/tools/persons.py`(596~640행은 직접 읽음)·`app/memory/*`·`app/agent/respond.py`·`propose.py`·`app/auth/routes.py`·`deps.py`·`app/db/models.py`·`alembic/versions/0001_schema_v2.py`
- 카드: `security.md` §5(64~73행), D19 결정 4·지킬 것 6, S3.4 11·13행, D2·S3.2 의 `ask_user` 줄, `CURRENT.md`, `HANDOFF.md` 24·25·27행, `docs/proposal.md` 22·264행
- **보지 못한 것(확인 안 됨으로 남김)**: `web/src` 의 칩이 모르는 `kind` 를 어떻게 그리는지(grep 결과 0줄), `app/er/judge.py` 프롬프트에 후보 인물의 기존 사실·사건이 실리는지, D14·D16·D18·S3.1·S3.5·S3.6·S3.7 카드 본문 전체(인용 줄만 대조), `app/agent/gate.py`·`propose.py` 본문

## 2. 직접 실행한 명령과 핵심 출력

| # | 명령 | 핵심 출력 |
|---|------|-----------|
| C1 | `bash .claude/scripts/gitlog.sh D2` · `D16` · `FIX-015` · `P6-briefing` · `P7-push` | 태그별 2줄씩: D2 `49c1c67`·`18219ba` / D16 `935aa4a`·`f67d8e4` / FIX-015 `36c288e`·`d79381a` / P6-briefing `3cd378c`·`125976a` / P7-push `50fd7fc`·`e555142`. 브랜치: `dev2 cef47d0`, `dev = main = f67d8e4`, 승격 대기 0 |
| C2 | `git log -1 --format='%h %s' <해시>` 26개(초안 2.6 절 전부) | 26개 모두 존재하고 제목이 초안 설명과 맞는다(예: `a25123b feat(P9b-auth): 대화를 계정별로 저장하고…`, `0f9223e …리비전 0003`, `a2f032d …U4 LLM 이 브리핑 문장을 쓰고 코드가 한 줄씩 검사한다`) |
| C3 | `grep -n "kind\|CheckConstraint\|ck_" alembic/versions/0001_schema_v2.py` | `98: sa.CheckConstraint(` / `99: "kind IN ('identity', 'new_person', 'schedule')",` / `100: name=op.f("ck_pending_questions_kind_valid")` |
| C4 | `sed -n 228,236p app/db/models.py` | `CheckConstraint("kind IN ('identity', 'new_person', 'schedule')", name="kind_valid")` |
| C5 | `grep -n … app/briefing/compose.py` | `227: f'id={source["event_id"]} raw="{source["raw_utterance"]}"' for source in sources` · `258: f'다가오는 일정: "{briefing_input.title}" '` |
| C6 | `grep -n "raw_utterance" app/memory/extract.py` | `208: f'raw="{event.raw_utterance}"'`(승격 추출 LLM 프롬프트) |
| C7 | `grep -n … app/tools/persons.py` | `214: query_vector = provider.embed([q])[0]` · `372: embedding = provider.embed([alias])[0]` · 사실 upsert `620: .on_conflict_do_update(index_elements=["person_id", "key"]` |
| C8 | `grep -nE "11-19\|CR-009\|가드레일" docs/wiki/HANDOFF.md` | 24행 "11-19 종료 취소, 가드레일(CR-009) 해결 때까지 유지(새 종료일 미정). 가드레일은 '평가 뒤' 가 아니라 지금부터의 주 작업" · 27행 "운영 서버 = `c85a0e8`, 리비전 `0005` … 계정 1·인물 7·사건 100·대화 278·일정 2" |
| C9 | `grep -rnE "logger\.(info\|warning\|error\|exception)" app` | `app/briefing/scheduler.py:178`·`199` 두 곳뿐(발화를 싣는 로그 호출은 못 찾음) |

`save_evidence.py` 로 따로 저장하지 않고 위 표에 명령과 핵심 줄을 인용했다(지시가 허용한 두 번째 방식).

---

## 3. 소견

### [필수]

**M1 · 초안이 사용자의 마지막 말(원문 5)과 어긋난다 — 상태·일정·운영 반영 가정 전부.**
사용자 "서버를 좀 더 열어야해 … 그걸 해결할 때까지" · "그대로 두고 가드레일 본작업 먼저 진행해줘". 어긋나는 자리:
- 3행 상태 줄 "이행은 평가 뒤" → 지금부터.
- 8~12행 원문 목록에 원문 5 가 없다.
- 2.2 D17 행 "운영 서버(11-19 종료 예정) 반영은 하지 않는 것이 기본(G13)" · G13 권장 (a) "하지 않음 — 서버는 11-19 종료" → 운영 반영이 이 CR 의 목적이 됐다. D17 은 "유지"가 아니라 **보충**(종료일 문장)이고, `security.md` §5 의 "공개 기간(~2026-11-19) 뒤 인스턴스·EBS·EIP 삭제" · "공개 기간(~11-19) 종료 때 서버와 함께 사라진다"(67·69행), `CLAUDE.md` 기술 스택 "공개 기간 한정(~2026-11-19 …) 뒤 인스턴스 종료" 도 2.7 수정 목록에 들어가야 한다.
- G16 권장 근거 "운영 DB 는 11-19 종료로 의미가 작고 로컬 개발 DB 대상" → 운영 DB 에 실데이터가 있다(C8: 사건 100·대화 278). 근거가 뒤집혔다.
- 4.1-1 "지금(초안)은 하지 않는다", 2.5 "P9b 를 닫은 뒤 이 CR 을 이행한다", W12 "이행이 평가 뒤라", 3.2 결정 4 (c) 위험 "시연 계정이 갑자기 로그아웃"(시연 전제).
- **빠진 작업 단위**: 운영 배포(리비전 0006 을 실데이터에 적용 — 적용 전 백업, 전후 행 수, 바깥 확인, 기존 가입자 재고지 실제 확인, 운영 소급 실행). U12 는 "운영 서버 반영은 G13" 한 줄뿐이다.
- 본작업이 끝날 때까지 가드 없이 가입·대화가 계속된다(사용자가 그렇게 정함) — 초안은 이 기간을 위험 표에 적지 않았다. 결정은 이미 났으므로 기록만 필요.

**M2 · "동의 전 원문은 `pending_questions.context` 한 곳에만" 은 지금 코드로 성립하지 않는다 — `ask_user` 가 `@traced` 다.**
`app/tools/questions.py:183` `@traced("ask_user")`, `app/tools/context.py:190~193` 이 `ctx` 를 뺀 **모든 인자**(= `context` 포함)를 `agent_traces.input` 에 넣는다. 그러므로 U4 의 `ask_user(kind="sensitive", context={"utterance": …})` 는 호출 즉시 원문을 trace 에 복제한다. 같은 식으로 복제되는 자리:
- `_log_resume_entry(ctx, resume_input)`(`loop.py:1482`) — 재개 진입 trace 에 `context` 통째.
- `_record_loop_error`(`routes.py:323`) `input={"utterance": utterance[:…]}`.
- 사후 경로(U5)는 더 넓다: `_propose`(`loop.py:691`, `loop_extract` 입력 = 발화, 출력 = 제안 내용) · `_gate` trace 가 질문보다 **먼저** 쓰인다.
결과: 2.4 원칙9 행의 "동의 대기 중 원문은 trace 에 넣지 않는다", 4.3 #4 "거절·만료 시 원문 삭제"가 `pending_questions.context` 만 지워서는 거짓이 된다. 개정에서 정해야 할 것: (a) 사전 동의 질문은 `ask_user` 툴 함수를 그대로 부르지 않고 trace 입력을 줄이는 경로를 쓸지(그러면 G3 (i) 의 "재사용" 비용 평가가 달라진다), (b) 거절·만료 때 지울 대상 목록에 `agent_traces`(ask_user·loop_resume·loop_extract·loop_gate·loop_turn 행)를 넣을지 — 넣으면 원칙9("근거를 남긴다")·기존 "trace 는 덮어쓰지 않는다"(`amend_trace_output` 은 추가만) 관례와 부딪히므로 D20 에 규칙으로 적어야 한다, (c) U4 수용 기준의 "DB 전수 `LIKE` 단언"을 **동의 범주 거절·만료 뒤**에도 건다(지금은 차단 유형 원문에만 건다).

**M3 · 리비전 0006 이 `pending_questions.kind` CHECK 제약을 빠뜨렸고, 되돌리기가 깨진다.**
DB 에 `ck_pending_questions_kind_valid`(C3)와 모델 `CheckConstraint`(C4)가 있다. U3 은 "`QUESTION_KINDS` 에 `"sensitive"`" 만 적었다 — 상수만 바꾸면 첫 동의 질문 INSERT 가 CHECK 위반으로 실패한다. 0006 에 제약 교체가 들어가야 하고, 그러면 **downgrade 는 `kind='sensitive'` 행이 하나라도 있으면 옛 CHECK 를 다시 걸 수 없어 실패한다.** 5절 되돌리기는 "컬럼만 지운다"고만 적었다. 개정에서: downgrade 가 그 행을 어떻게 하는지(삭제 = 동의 기록 소실, G10 (a) 와 충돌) 정하고, U3 수용 기준의 왕복 시험을 "sensitive 질문 행이 있는 상태"로 한다. 5절의 "downgrade 뒤 민감 항목이 다시 브리핑·MCP 로 나간다"는 초안이 스스로 적은 대로 사용자 결정 사안이다.

**M4 · 사실 덮어쓰기 규칙(U3)과 승격 상속 규칙(U6)이 서로 모순되고, 그 틈으로 민감 원문이 브리핑 LLM 으로 나간다.**
U3: "같은 키를 일반 턴이 덮으면 표시도 NULL … 옛 민감 값이 사라지므로 표시를 남길 이유가 없다". 그러나 `update_person` 의 upsert(`app/tools/persons.py:613~631`)는 값만 덮고 **`fact_sources` 링크는 건드리지 않는다**. 옛 민감 사건 링크가 남은 채 사실이 "일반"이 되면:
- `app/briefing/inputs.py:152~171` `_fact_sources` 가 그 사건의 `raw_utterance` 를 뽑고 `compose.py:227` 이 브리핑 LLM 프롬프트에 넣는다(U7 수용 기준 "브리핑 LLM 프롬프트에 민감 문자열 0" 위반).
- `GET /persons/{id}/facts/{fact_id}/sources`(`read.py:109`)가 그 원문을 돌려준다.
- U6 의 "근거 이벤트 중 하나라도 민감이면 사실도 민감" 으로 판정하면 같은 사실이 다시 민감이 된다 — 두 규칙이 같은 행에 반대 답을 낸다.
개정에서 사실의 표시를 무엇으로 정하는지 **한 규칙**으로 고정해야 한다(컬럼값인지, `fact_sources` 로 파생하는지, 덮어쓸 때 옛 민감 링크를 끊는지). 함께 정할 것: 민감 턴이 일반 사실의 같은 키를 덮는 반대 방향, 승격 `_upsert_fact` 의 "값이 같으면 유지" 분기(`promote.py:147`), 근거 원문 조회는 사실 표시와 별개로 **사건 표시로도** 걸러야 한다는 점.

**M5 · 브리핑 제외를 `inputs.py`·`select.py` 에서 한다는 계획이 실제 자료 흐름과 맞지 않는다.**
`build_briefing_input` 은 자료를 직접 읽지 않고 **툴 7종의 `get_briefing`** 을 부른다(`inputs.py:92`). 최근 사건은 `briefing_out.recent_events`(`inputs.py:148`)에서 오고 `EventOut` 에는 표시 필드가 없다(초안은 "툴 7종 시그니처에 인자를 더하지 않는다"고 했지만 **반환 타입**에 필드를 더할지는 말하지 않았다 — S3.2 `→ Event`/`→ Briefing` 의 모양 문제). 정해야 할 것:
- 제외를 `get_briefing` 안에서 할지 밖에서 할지. 밖이면 표시를 다시 조회해야 하고 "최근 5건"이 걸러진 뒤 줄어든다. 안이면 툴 동작 변경이라 S3.2·`tools_check` 설명이 필요하다.
- `get_briefing` 은 `@traced` 라 걸러지기 전 결과가 `agent_traces.output` 에 남는다(내부 저장이라 허용할지 명시).
- 민감 일정 제외는 기본 모드뿐 아니라 `schedule_id` 수동 모드(`select.py:58`, `POST /briefings/run`)에도 걸려야 한다 — 수동 지정 시 404 인지 건너뜀인지.
- **이미 저장된 브리핑**(`agent_traces` 의 브리핑 행)은 `GET /briefings`·MCP `list_briefings` 로 계속 나간다. 초안 어디에도 다루지 않았다(M8).

**M6 · 내보내는 경로 목록에 빠진 것이 있다 — "열거 계약 시험"의 목록을 초안이 확정하지 않았다.**
초안 U7 이 든 것: 카드·조회 답·브리핑 입력·푸시·MCP 4도구. 직접 grep 으로 찾은 나머지:
- `GET /events/{event_id}/raw`(`read.py:81`) · `GET /persons/{id}/facts/{fact_id}/sources`(`read.py:109`) — 카드 화면의 하위 경로다. "카드에서만"에 포함되는 것으로 볼지 명시가 없다(G20 "눌러서 보기"와 묶인다).
- `GET /chat/history`(`routes.py:419`) — 민감 원문이 든 사용자 줄을 그대로 돌려준다. 동의한 경우 허용인지 적어야 한다.
- `GET /questions/pending`(`routes.py:533`) — 질문 문구·옵션(사후 질문 문구에 내용이 실리지 않는지).
- `list_persons` 의 `last_contact_at = max(Event.occurred_at)`(`read.py:152`) — 민감 사건의 **시각**이 인물 목록·MCP `list_people`/`find_person` 으로 나간다. 초안 U7 은 "4개 도구 모두 기본값 경로"라 했지만 이 둘은 `get_person_card` 를 쓰지 않아 `include_sensitive` 인자가 닿지 않는다(`mcp_server/tools.py:45·64`).
- 승격 추출 LLM(`extract.py:208`, 사건 `raw_utterance` 를 보냄) — 동의 문구 "OpenAI 로 전송"의 범위 안이지만 "동의한 그 턴 한 번"이 아니라 **이후 승격 때 다시** 전송된다. 문구(G6)와 D20 에 적어야 한다.
- 인물 삭제 `app/api/delete.py`(영향 없음으로 보이나 확인 안 됨) · ER 판정 프롬프트(`app/er/judge.py`)에 후보의 기존 사실이 실리는지 **확인 안 됨** — 실린다면 일반 턴의 ER 이 민감 사실을 OpenAI 로 다시 보낸다. 01-plan 전에 architect 가 grep 으로 닫아야 한다.
- 민감 낱말이 든 **별칭**(W6)은 카드 밖 모든 경로(목록·MCP·ER 후보·질문 문구)로 나간다. 초안은 "01-plan 에서 판단"으로 미뤘는데, 결정 2 (가)의 수용 기준(4.3 #7)과 직접 부딪히므로 CR 에서 규칙을 정해야 한다.

**M7 · 사전 검사는 의도(기록/조회)를 모르는 채 돈다 — 조회 문장·재개 사슬 설계가 비어 있다.**
- 의도 판별은 추출 LLM 뒤다(`loop.py:1128`). "민수 마약 했다는 게 언제였지?" 는 사전 검사에 걸려 **"기억할까요?"** 칩이 뜨는데, 저장할 것이 없고, 동의해도 결정 2 (가) 때문에 답은 "카드에서 확인" 한 줄이다. U5 는 사후 경로의 조회만 다뤘다("묻지 않는다"). 사전 경로의 조회 문장을 어떻게 할지(문구를 "전송할까요?" 로 중립화, 규칙으로 의문형 구분 등) 정해야 한다.
- 사전 동의 재개는 `run_turn` 을 처음부터 돌린다고 했는데 `submit_answer`(`routes.py:213~221`)에는 `proposer`·`answerer` 의존성이 없다 — 라우트 서명 변경이 필요하다(U4 파일 목록엔 있으나 작업으로 적히지 않음).
- 동의 문맥을 후속 질문에 싣는 자리가 한 곳이 아니다: `_extend_for_ask`·`_followup_new_person_turn`(`loop.py:1497`)·`_ask_schedule`(`loop.py:793`)·`_resume_query_turn`·`_apply_resume_byte_limit`(`LOOP_MAX_RESUME_BYTES` 절단이 동의 문맥을 잘라내지 않는다는 보장). 수용 기준에 **"동의 → identity 거절 → new_person → schedule" 사슬 끝의 저장물에도 표시가 있다**는 시험이 없다. 사슬 중간에서 표시가 빠지면 M-급 미검출(민감인데 일반으로 저장)이다.
- 배포 시점에 이미 떠 있는 대기 질문(가드 이전에 만들어진 `context["utterance"]`)이 재개되면 가드를 거치지 않고 ER 판정 LLM 으로 간다. 규칙 한 줄 필요.
- `kind="sensitive"` 는 `_AFFIRMATIVE_REQUIRED_KINDS`(`questions.py:96`)에 없다 — 긍정 답 규약을 강제할지 정하고, 초안의 `AFFIRMATIVE_KEY: "기억해요"`(문자열)는 기존 규약(비어 있지 않은 **문자열 리스트**, `questions.py:164~178`)과 형식이 다르다.

**M8 · 기존 데이터 소급(U11)의 범위가 표시 대상 3표에 그친다.**
U11 은 `events`·`person_facts`·`schedules` 만 본다. 같은 원문이 `chat_messages`(운영 278행), `agent_traces`(입력 발화·제안·저장된 브리핑 문장), `pending_questions.context`, `person_aliases` 에도 있다. 특히 차단 유형(주민번호 등)을 "가린 값으로 덮어쓰기"한다면서 trace·대화 기록의 같은 문자열은 남는다 — 4.3 #2 의 취지와 어긋난다. 또 표시를 붙여도 **이미 만들어진 브리핑**은 그대로 나간다(M5). 운영 DB 덮어쓰기는 되돌릴 수 없으므로(초안 5절도 인정) 범위·백업·실행 주체를 CR 에서 정하고 사용자에게 묻는다.

**M9 · 실행 순서·크기·판정 가능성.**
- **활성 패키지 충돌**: `CURRENT.md` 는 `active: P9b-auth` 이고 P9-infra 04-review 도 열려 있다. 초안은 "P9b 를 닫은 뒤"라 했는데 사용자 지시는 "지금부터"다. P9b 를 먼저 닫는지(04-review·완성 확인이 선행), 보류로 돌리는지 메인 세션이 정해 개정에 적어야 한다(임의로 두 패키지를 동시에 열 수 없다).
- **U4 가 커밋 하나 크기가 아니다**: 가림 적용 · 사전 동의 질문 · 재개(긍정/부정) · 만료 정리 · 403 스위치 · trace 규칙이 한 단위다. 최소 3개(가림 / 사전 질문 / 재개·거절·만료)로 나눈다.
- **의존 그림 오류**: U4 의 1번(403 `notice_required`)은 U8 계약에 기대는데 그림은 `U3 → U8`·`U4` 가 병렬이고 "U8 전에는 꺼 둔 스위치"라는 임시 상태를 만든다. 스위치의 이름·기본값·누가 켜는지가 없다. U8 을 U4 앞으로 옮기는 편이 단순하다.
- **U0 검증 명령**이 U0 시점에 실행 불가(`verify-plan.sh P9d-…` 는 01-plan 작성 뒤).
- **판정 명령이 없는 수용 기준**: 4.3 #2 의 "로그 어디에도 없음"(무엇을 grep 하는지 없음), #12 "감정·평가·조언 표현 0"(어떤 목록으로 판정하는지 없음 — `BRIEFING_FORBIDDEN_EXPRESSIONS` 와 합치지 않는다고만 했다), U5 "지금과 동작이 바이트 단위로 같음"(무엇의 바이트인지 — 프롬프트는 스키마 필드가 늘어 달라진다).
- **U1 "라벨 검수는 verifier"**: 라벨을 만드는 것은 eval-agent 이고 verifier 는 검수 판정만 쓴다는 점을 단위 설명에 분명히(verifier 가 라벨을 고치지 않는다).
- **U9** 는 U4·U7·U8 뒤인데 병렬 가능한 부분(가입 화면 고지)과 불가능한 부분(칩·배지)이 한 단위다. 최소 2개.

### [권고]

- **R1 · `ask_user` 정의와의 긴장(G3·W9).** "에이전트가 모른다를 스스로 판단하는 행동"(CLAUDE.md)에서 서버 가드가 LLM 전에 만드는 동의 질문은 벗어난다 — 호출자가 에이전트 루프가 아니라 라우트다. 초안은 이를 W9 로 정직하게 적었다. 툴 7종의 **개수·시그니처**는 불변이므로 원칙 위반은 아니지만, 사전 동의는 `ask_user` **툴**을 부르지 않고 `pending_questions` **저장소만** 같이 쓰는 형태(M2 (a))가 정의도 지키고 trace 복제도 없앤다. 사후 확인(U5)은 루프가 부르므로 `ask_user` 그대로가 자연스럽다. D2 보충 문장을 이 구분으로 쓰기를 권한다.
- **R2 · 원칙8.** 사후 LLM 표시의 "규칙+LLM 합산 감지율"은 1회 실행이라 재현 수치가 아니다(초안 W8 이 인정). 보고서에서 규칙 단독 수치와 **같은 표에 섞지 않는다**는 것을 U10 수용 기준으로 올린다. test 동결 해시를 "U2 착수 전"으로 건 것은 적절하다. dev 세트를 본 eval-agent 가 test 도 쓴다는 점(누출 경로)은 README 에 적는다.
- **R3 · 원칙9.** `guard_check` trace 의 "규칙 id" 가 낱말을 그대로 드러내지 않는지(예: `crime.drug.마약`) 규칙 id 명명 규칙을 정한다. "기억하지 않아요" 뒤에도 범주·규칙 id 는 남는다 — 그것 자체가 민감 사실의 흔적이라는 점을 D20 에 적는다.
- **R4 · D19 출력 계약.** `PersonCardOut` 에 `sensitive_category` 필드를 더하면 MCP `get_person_card` 응답 모양도 바뀐다(`model_dump` 그대로, `mcp_server/tools.py:83`). 제외 경로에서는 필드 자체를 빼거나 항상 null 임을 계약 시험에 넣는다. 민감 항목만 있는 인물의 카드가 "빈 카드"로 보이는 것이 존재 누설인지도 한 줄.
- **R5 · 턴 단위 표시(G5 (i))와 인물 생성.** 동의 턴에서 새로 만든 **인물 행**·관계 태그는 표시 대상이 아니다(표 3개만). "마약 하던 걔"가 `display_name` 이 되는 경우를 M6 의 별칭 규칙과 함께 다룬다.
- **R6 · 만료 정리(G19 (a)).** 다음 `/chat` 때만 지우면 다시 오지 않는 사용자의 원문은 영구히 남는다. 운영 서버가 계속 열리게 됐으므로 (b) 주기 작업 쪽 근거가 강해졌다. 사용자에게 물을 때 이 점을 함께.
- **R7 · 2.6 절 갱신.** 초안이 메인 세션에 요청한 태그 검색 결과는 위 C1·C2 다. 그대로 2.6 에 붙이면 된다.
- **R8 · 템플릿.** 5개 절·`승인:` 줄은 템플릿과 맞는다. 다만 상태 값이 템플릿 어휘(열림/승인/거절/이행완료)가 아니고, L-006 으로 `승인:` 줄은 쓰이지 않는다 — 개정 때 상태를 "열림"으로.
- **R9 · 가림 뒤 문장의 품질.** `[주민등록번호]` 자리표시가 든 문장을 추출 LLM 에 넣었을 때 생기는 이상 사실을 "게이트에서 버린다"(G4)는 규칙은 U4·U5 어느 단위의 수용 기준에도 없다.

### [참고]

- 초안이 스스로 적은 열린 위험 W1(사용자 동의 ≠ 기록 대상 동의)·W3(규칙이 놓친 문장은 이미 전송)·W10(동의 전 원문이 우리 DB 에 저장)은 정확하고, 숨기지 않았다.
- 2.5 의 완료 패키지 코드 자리, 2.6 의 해시 26개, 되돌릴 커밋 0 은 사실과 맞다(4절).
- 1.3 "임베딩은 별칭(이름)에만"은 `persons.py:372`(별칭)와 `:214`(검색 질의 `q`) 두 곳으로 확인된다. 질의 `q` 가 항상 언급(이름)인지는 호출자 전수를 보지 않아 **확인 안 됨**.
- 로그: 발화를 싣는 `logger` 호출은 찾지 못했다(C9). 접근 로그(Caddy)는 본문을 남기지 않는 것으로 보이나 확인하지 않았다.

---

## 4. 초안의 사실 주장 대조

| 주장(초안 자리) | 결과 | 근거 |
|---|---|---|
| `append_chat_message` 가 루프 전에 발화 저장, `routes.py:389` (2.6·U4) | 맞음 | `routes.py:389` |
| ask_user `kind` 검사 `app/tools/questions.py:125` (2.5) | 맞음 | `questions.py:124~126` |
| `BRIEFING_FORBIDDEN_EXPRESSIONS` `app/briefing/types.py:242` (2.4) | 맞음 | grep 242행 |
| `person_facts` upsert 키 = (인물, 키) (U3) | 맞음 | `persons.py:620`, `models.py:155` |
| 푸시 제목에 일정 제목이 실린다 (2.5) | 맞음. 본문에는 **제안 문장**도 실린다(`payload.py:86·89`) | — |
| 조회 답 카드 읽기 `_read_card` → `get_person_card` (2.5) | 맞음 | `loop.py:1263`, `read.py:183` |
| 재개는 "인식 LLM 재호출 없음" (U4) | 맞음 | `resume_turn` docstring 1803~1805행 |
| 기획서 9장 "제3자 개인정보" 행 = 본문 264행 (2.1) | 맞음 | `proposal.md:264` |
| 2.6 커밋 해시 26개 | 전부 존재·설명 일치 | C2 |
| `_EXEMPT`·`_MUST_REQUIRE_LOGIN` (U8) | 존재 | `tests/test_auth_required_routes.py:39·51` |
| **"동의 대기 중 원문은 `pending_questions.context` 한 곳에만"** (2.4 원칙9) | **틀림** | `ask_user` 가 `@traced`(M2). 초안 W10 은 `chat_messages` 에도 있다고 적어 스스로와도 어긋난다 |
| **U3 — kind 추가는 `QUESTION_KINDS` 한 줄** (U3·G3 비용 칸 "1줄") | **틀림(누락)** | DB CHECK + 모델 CHECK(M3) |
| **브리핑 민감 제외 자리 = `inputs.py::build_briefing_input`** (2.3 S3.6·U7) | **부정확** | 자료는 `get_briefing` 툴에서 온다(M5) |
| **"MCP 4개 도구 모두 기본값 경로"** (U7) | **부정확** | `list_people`·`find_person` 은 `list_persons` 를 쓴다(M6) |
| **U4 `AFFIRMATIVE_KEY: "기억해요"`** | **형식 불일치** | 기존 규약은 문자열 리스트(M7) |
| **U3 "옛 민감 값이 사라지므로 표시를 남길 이유가 없다"** | **틀림** | `fact_sources` 링크와 원문이 남는다(M4) |
| **상태 줄·G13·G16·D17 행의 "11-19 종료·평가 뒤"** | **낡음** | HANDOFF 24행(C8), 원문 5 (M1) |
| FIX-015 가 `propose.py` 스키마를 바꿨다 (2.5) | 내용은 `CURRENT.md` 메모와 맞음. FIX-015 자체 커밋 해시는 `gitlog.sh FIX-015` 2줄에 없어 **확인 안 됨** | C1 |
| 프론트 칩이 새 kind 를 재사용할 수 있다 (U9) | **확인 안 됨** | `web/src` grep 0줄 |

## 5. 사용자 원문 충실도

- 원문 1(가드레일 없음·"마약을 했다")·원문 4(1~4 계획 + 독립검토)는 담겼다.
- **원문 3 의 "법적으로 문제가 되는 내용을 차단하고 싶은거야 혹은 사용자가 동의를 하면 들어갈 수 있게"** — 초안은 "차단"을 식별·인증 정보에만 걸고, 범죄·불법은 "동의" 쪽에 넣었다. 문장은 "차단 **혹은** 동의"라 이 배정이 사용자의 뜻인지 문서만으로는 판정할 수 없다. 초안은 이것을 해석 주석으로도, 결정 목록으로도 올리지 않았다 → **꼭 물어야 한다**(6절 1번).
- 원문 3 의 "ChatGPT 로 넘어간다는 알림" — 초안은 가입 고지 + 기존 가입자 재동의 + 미동의 시 `/chat` 403 까지 넓혔다. 사용자가 말한 것은 "알림"이고 채팅 차단은 초안의 확장이다(결정 4 에 묶여 있으니 그 질문에서 드러내면 된다).
- 원문 2("권장안으로 평가 뒤에")의 권장안은 HANDOFF 25행 기준 "저장하되 표시·제외"였고 원문 3 으로 바뀌었다 — 초안은 원문 3 을 따랐다(적절).
- 원문 5 는 반영되지 않았다(M1).

## 6. 사용자 결정 목록 분류

**꼭 물어야 하는 것(한 번에)**
1. **원문 3 해석** — 범죄·불법 내용을 (가) 동의하면 저장 (나) 아예 차단. (초안에 없는 결정)
2. **결정 1** 건강 범위 · **결정 2** 민감 항목 사용 범위 · **결정 3** 사후 확인 · **결정 4** 기존 가입자 재고지 — 사용자가 직접 든 4건. 결정 4 는 "미동의면 채팅을 막는다(403)"까지 포함된다는 점을 함께.
3. **G22** 차단 대상 식별 정보의 범위(전화번호·주소 포함 여부) — 제품이 기억해 주는 정보와 겹친다.
4. **G6** 문구 5종과 "ChatGPT → OpenAI API" 표기, 그리고 W2(약관 내용을 고지문에 적을지 — 확인은 사용자 몫).
5. **G9 / W10** 동의 **전** 원문을 우리 DB 에 잠시라도 저장해도 되는지(대화 기록에 원문 유지 vs 처음부터 가림). M2 의 trace 처리와 한 묶음.
6. **G16 + M8** 운영 DB 기존 데이터 소급 — 할지, 범위(대화 기록·trace·저장된 브리핑 포함 여부), 덮어쓰기는 되돌릴 수 없음.
7. **G13 대체** 운영 반영 시점·방식과 새 종료 기준("해결할 때까지"의 완료 판정 — 무엇이 되면 해결인가).
8. **G17** 시험 세트 크기(비용·시간).
9. **5절** downgrade 때 민감 행·동의 질문 행 처리(M3) — 되돌릴 일이 생길 때 물어도 되지만 규칙은 미리.

**권장안으로 진행해도 되는 것(설계 선택 — 근거가 문서에 있고 되돌릴 수 있다)**
G2(목록 출처, 사용자 검토는 U1·U2 산출물로) · G3(단 M2·R1 반영 조건) · G4 · G5 · G7 · G8 · G10 · G11 · G12 · G14 · G18 · G20 · G21. G15(P9c 와 순서)는 사용자가 "가드레일 본작업 먼저"라고 이미 정했다. G19 는 R6 때문에 권장 (a) 의 근거가 약해졌다 — (b) 로 바꾸거나 6번 질문에 한 줄 붙인다. G1(범주 정의)은 결정 1·질문 1 의 답으로 대부분 정해진다.

**초안에 빠진 결정**: 위 1·7·9, 그리고 민감 낱말이 든 별칭·표시 이름의 처리(M6·R5), 조회 문장이 사전 검사에 걸렸을 때의 동작(M7).

## 7. 법적 판단에 해당하는 문장

초안은 7절 머리와 G1·W1·W2 에서 "법적 판단은 하지 않는다"를 반복했고, 법적 충분성·적법성을 **단정한 문장은 찾지 못했다.** 주의할 표현 2곳:
- 1.1 의 9장 새 문장 "… 최소 수집(…), 외부 LLM 전송 고지, **암호화**" — 대응이 "되었다"로 읽힌다. W1 의 "해결이 아니라 완화"가 같은 문장 안에 들어가야 한다(초안도 W1 에서 그렇게 하겠다고 적었다).
- G1 (b) "법령의 '민감정보' 범주 이름을 참고" — 범주 이름을 법령에서 가져오면 제품이 법령 준수를 주장하는 것으로 읽힐 수 있다. 권장 (a) 를 유지하고 D20 에 "법령상 분류가 아니다"를 적는다.

## 8. 재검토 조건

개정 1 에서 M1~M9 가 반영되면 이 문서에 재검토 절을 더한다. 재검토 때 직접 볼 것: M2 의 trace 처리 규칙과 거절 뒤 전수 `LIKE` 수용 기준, M3 의 0006 CHECK 교체·downgrade 규칙, M4 의 단일 표시 규칙, M5·M6 의 내보내는 경로 확정 목록(`app/er/judge.py` 확인 결과 포함), M9 의 단위 분할과 활성 패키지 순서.

---

# 재검토(개정 1)

**판정: 수정 뒤 이행** — 1차 [필수] 9건 중 6건(M1·M3·M4·M5·M8 + M2 의 설계)은 닫혔고, 사용자 결정 12건과 어긋나는 자리는 찾지 못했다. 다만 개정 1 이 새로 적은 규칙 3곳이 실제 코드와 맞지 않거나 문서 안에서 서로 어긋난다(아래 RM1~RM3). 셋 다 D20 카드·S3.2 보충에 **글자 그대로 옮겨질 문장**이라 카드 작성 전에 고쳐야 한다. 각각 한 문단 이내의 수정이고 설계를 다시 짤 필요는 없다. 고친 뒤의 재검토는 RM1~RM3 자리만 보면 된다.

검토자: verifier (fable) | 재검토일: 2026-11-22 | 대상: `docs/wiki/changes/CR-009.md` 개정 1(465행, 미커밋) | 기준 커밋: `cef47d0`
이 절은 CR·카드·코드를 고치지 않는다. 법적 판단은 하지 않는다.

## R-1. 직접 실행한 명령과 핵심 출력

| # | 명령 | 핵심 출력 |
|---|------|-----------|
| D1 | `bash .claude/scripts/gitlog.sh CR-009` | 태그 커밋 0줄(CR 미커밋). `dev2 = cef47d0`, `dev = main = f67d8e4`, 승격 대기 0 — 개정 1 의 2.6 과 같음 |
| D2 | `sed -n 120,175p app/er/judge.py` · `grep -n "facts\|events\|raw_utterance\|person_facts" app/er/judge.py` | `_candidate_summary`(143~155행)는 `person_id`·`display_name`·`aliases`·`relation_tag`·`hierarchy`·`rule_flags` 6키. `build_prompt`(158~176행)는 mention·utterance·후보 요약만. 사실·사건 grep 0줄 |
| D3 | `sed -n 80,125p web/src/screens/ChatScreen.tsx` · `grep -rn "kind" web/src --include='*.ts' --include='*.tsx'`(시험 파일 제외) | `QuestionChips`(88~124행)는 `question.options` 만 그린다. `kind` 는 `web/src/api/types.ts:68: kind: string` 한 줄뿐 |
| D4 | `grep -rn "delete_person\|api\.delete\|api import delete" app --include='*.py'`(`delete.py` 자신 제외) · `grep -n "@router\." app/api/routes.py app/auth/routes.py` | 첫째 0줄. 라우트 20개(api 12 + auth 8)에 `DELETE /persons` 없음. `delete.py:59~63` 에 "새 trace 모양을 만드는 패키지의 의무" 절 있음 |
| D5 | `grep -rn "\.embed(" app --include='*.py'` · `grep -n "search_candidates(ctx" app/er/pipeline.py` · `grep -n "raw_candidates = search_person" app/er/candidates.py` · `grep -n "def _ordered_mentions" -A 22 app/agent/loop.py` | 임베딩 호출은 `persons.py:214`(질의 `q`)·`:372`(별칭) 두 곳. `pipeline.py:255` → `candidates.py:112` → `search_person`. 언급은 기록 턴 `_ordered_mentions`(`loop.py:323~342`, 제안의 `person` 인자)·조회 턴 `_query_mentions`(`loop.py:1238~1262`) — 둘 다 추출 LLM 제안에서 읽는다 |
| D6 | `sed -n 110,122p app/settings.py` | `118: QUESTION_TTL_HOURS = 24` / `119: QUESTION_TTL = timedelta(hours=QUESTION_TTL_HOURS)` |
| D7 | `sed -n 55,150p app/tools/briefing.py` · `sed -n 80,175p app/briefing/inputs.py` · `sed -n 40,80p app/briefing/select.py` | `get_briefing` 이 사실·최근 사건(`limit(BRIEFING_RECENT_EVENTS)`)·다가오는 일정을 직접 읽는다. `inputs.py:92` 가 그 툴을 부르고 97~105행에서 사실을 다시 읽으며 `_fact_sources`(153~172행)가 `raw_utterance` 를 뽑는다. `select.py:55~69` 수동 모드는 일정 한 건을 그대로 돌려준다 |
| D8 | `sed -n 90,200p app/tools/questions.py` · `sed -n 183,200p app/tools/context.py` | `96: _AFFIRMATIVE_REQUIRED_KINDS = ("identity", "new_person")` · `183: @traced("ask_user")` · `context.py:186~190` 이 `ctx` 밖 인자 전부를 `input_payload` 로 |
| D9 | `sed -n 196,432p app/api/routes.py` | `submit_answer`(213~221행) 의존성은 `judge`·`embedder`·`extractor` 뿐(`proposer`·`answerer` 없음). `chat` 은 389행에서 사용자 줄을 루프 **앞**에 저장. `_record_loop_error` 는 `input={"utterance": …}` |
| D10 | `sed -n 80,84p`·`226,237p app/db/models.py` · `sed -n 430,436p app/agent/types.py` | `models.py:82 QUESTION_KINDS` 3종, 231~234행 CHECK 3종, `types.py:434` 에서 `QUESTION_KINDS` 검사 |
| D11 | `grep -rn "create_person(\|update_person(" app --include='*.py'` · `sed -n 425,472p app/er/pipeline.py` · `sed -n 869,900p`·`1838,1885p app/agent/loop.py` | 별칭·인물이 실제로 만들어지는 자리 4곳: `app/er/pipeline.py:461~465`(merge → `update_person(new_alias=mention)`) · `loop.py:1847`(identity 답 → 별칭) · `loop.py:1877`(new_person 답 → `create_person(display_name=mention, aliases=[mention])`) · `loop.py:892`(`_execute_call` 의 `update_person` — LLM 이 낸 `new_alias` 만). **`_execute_call` 은 `create_person` 을 부르지 않는다** |
| D12 | `sed -n 376,428p app/agent/types.py` · `sed -n 451,463p`·`1118,1190p app/agent/loop.py` | 재개 context 의 `resume` 은 `mention`·`hints`·`pending_calls`·`held_drafts`·… 를 담는다. `_apply_resume_byte_limit` 는 `held_drafts` 만 비운다. `TurnResult.trace_ids` 는 extract·gate·resolve·record **4개**(1180~1184행) — `ask_user` 행·`loop_turn` 행은 들어 있지 않다 |
| D13 | `sed -n 100,215p app/briefing/scheduler.py` · `grep -n "BRIEFING_SCHEDULER_ENABLED" -r app` | `default_run_once` 는 창 안에 일정이 있는 사용자만 돈다(없으면 표식 사용자 1회). 루프는 스위치(`settings.py:354`)가 켜졌을 때만 뜬다 |
| D14 | `ls tests \| grep -iE "loop\|read"` · `ls scripts` · `python3 -I -c "import app"` | `test_agent_loop.py`·`test_memory_loop.py`·`test_api_read_*.py` 는 있고 **`tests/test_loop*.py`·`tests/test_read*.py` 에 맞는 파일은 0개**. `schema_check.py`·`tools_check.py` 있음. `-I` 에서는 `ModuleNotFoundError: No module named 'app'`(기존 스크립트는 `sys.path.insert` 로 푼다 — `scripts/tools_check.py:43`) |
| D15 | `grep -n "11-19" docs/wiki/security.md docs/wiki/decisions/D17-vercel-deploy.md CLAUDE.md` · `ls docs/wiki/decisions docs/wiki/specs` | `security.md:69`·`:71`, `D17-vercel-deploy.md:11`, `CLAUDE.md:54`. U0 검증 명령이 가리키는 파일(`D17-vercel-deploy.md`·`S3.2-tools-v2.md`·`S3.4-ask-user-protocol.md`) 전부 존재 |
| D16 | `.venv/bin/python`(읽기 전용) — `BRIEFING_FORBIDDEN_EXPRESSIONS` 14개를 8절 "N4 문구 초안" 구간에 대조 | 걸리는 항목 `[]` |
| D17 | `grep -n "CHAT_UTTERANCE_MAX_LENGTH\|max_length" app/api/schemas.py` | `69: CHAT_UTTERANCE_MAX_LENGTH = 2000` — U2 의 "입력 상한 2000자" 는 새 상수가 아니다 |
| D18 | `grep -nE "11-22\|11-18\|CR-009" docs/wiki/HANDOFF.md` · `sed -n 1,5p docs/wiki/CURRENT.md` | HANDOFF 24행(11-22 결정 12건)·25행(서버 종료 연기)·27행(행 수 `1·7·99·278·2`). `CURRENT.md` 는 아직 `active: P9b-auth` · `frozen: none`(개정 1 의 4.1-1 이 이행 때 메인 세션이 바꾼다고 적음) |

## R-2. M1~M9 판정

| 소견 | 판정 | 근거 |
|------|------|------|
| **M1** 사용자 원문 5 | **닫힘** | 상태 줄·원문 5·6, 2.2 D17 "보충", 2.7 에 `CLAUDE.md` 공개 기간 문장과 `security.md` 69·71행(D15 로 행 번호 확인), U12 운영 반영 단위, W13(가드 없는 기간). 사용자 결정 10·11 과 U12·4.3 #17 이 맞는다 |
| **M2** trace 복제·거절 뒤 삭제 | **닫힘(잔여 → RM2)** | 사전 질문은 `ask_user` 를 부르지 않는다(2.2 D2·R-1, 근거 코드 D8). 사후는 R-3 의 지우기 함수 하나. 거절·만료 뒤 전수 `LIKE` 가 U5c ①②·U6 ②·4.3 #4 에 있다. 원칙9 예외 구절도 2.4 에 있다. 남은 것: R-2·R-3 문장이 사후 질문 context 의 제안 내용을 지우는 대상으로 적지 않았다(RM2) |
| **M3** 0006 CHECK·downgrade | **닫힘** | U3 이 `ck_pending_questions_kind_valid` 교체, 모델 CHECK(`models.py:231~234`)·`QUESTION_KINDS`(`:82`) 4종, downgrade 는 민감 행이 있으면 지우지 않고 실패, 그 상태의 시험(수용 기준 ②③)을 적었다. 5절·4.3 #14 와 맞는다 |
| **M4** 사실 표시 단일 규칙 | **닫힘** | R-5 — 컬럼 하나, `COALESCE(기존값, 이번 범주)` 단조, 링크를 끊지 않음, 근거 원문은 사건 표시로도 거름. U7 ④ 가 4방향 시험. 대상 코드 `persons.py:612~631`·`promote.py:148` 확인. 과잉 가림은 W5 에 적혔다 |
| **M5** 브리핑 자료 흐름 | **닫힘** | 2.3 S3.2·S3.6, R-6 의 `get_briefing`·브리핑 입력·일정 선정 행이 D7 의 실제 흐름과 맞는다(툴 안 제외 + 재조회·근거 원문 + 기본·수동 선정, 거른 뒤 상한, 거른 결과만 trace). 저장된 브리핑은 W14 |
| **M6** 내보내는 경로 목록 | **부분** | R-6 표는 1차가 든 자리를 모두 담았고 `judge.py`·`delete.py`·질의 `q` 확인 결과가 코드와 맞다(D2·D4·D5). 그러나 그 목록이 기대는 **이름 규칙 R-7 의 자리가 코드와 맞지 않는다**(RM1) — 별칭이 실제로 저장되는 4곳 중 3곳이 `_execute_call` 밖이다 |
| **M7** 조회 문장·재개 사슬 | **닫힘(잔여 → RM3)** | N1 로 사전 경로의 조회 문장을 올렸고, `submit_answer` 서명 변경(U5c — D9 로 필요성 확인), `consent` 예약 키 사슬(R-9·U7 ②③), 배포 전 대기 질문(R-10·4.3 #15), 긍정 규약(R-11 — D8 형식과 일치)을 적었다. 남은 것: **사후 표시된 조회 문장**이 1.2 표와 U6 에서 다르게 적혔다(RM3) |
| **M8** 소급 | **닫힘** | 사용자 결정 9 로 단위 삭제, W14 가 남는 위험 3가지를 완화책 없이 적었다. 2.7 의 일회성 스크립트도 삭제 |
| **M9** 순서·크기·판정 가능성 | **부분** | P9b 보류(메인 세션 결정), U5a·b·c 분할, U4 를 앞으로(스위치 제거), U9a·b 분할, U0 명령이 그 시점에 실행 가능(D15), U1 역할 구분은 반영됐다. 새로 생긴 것: 단위 검증 명령 일부가 실행되지 않고(RR1), U5c ③ 이 U7 산출물에 기댄다(RR2) |

1차 8절이 "직접 볼 것"으로 든 자리: M2(위) · M3(위) · M4(위) · M5·M6 목록과 `judge.py`(D2 — 사실·사건 미포함 확인) · M9 분할과 활성 패키지(위).

## R-3. 개정 1 이 새로 한 사실 주장 대조

| 주장(개정 1 자리) | 결과 | 근거 |
|---|---|---|
| ER 판정 프롬프트에 후보의 사실·사건이 실리지 않는다 (1.3, R-6) | 맞음 | D2 |
| `QuestionChips` 는 `kind` 를 보지 않는다 (2.4 원칙5, U9b) | 맞음(행 범위는 88~124) | D3 |
| `delete_person` 라우트 등록 0, `delete.py:59~63` 의무 (2.6, R-12) | 맞음 | D4 |
| 질의 `q` 는 항상 추출 LLM 이 낸 언급 (1.3) | 결론은 맞음. 인용한 `loop.py:1248~1259` 는 조회 턴(`_query_mentions`)이고 기록 턴은 `_ordered_mentions`(`loop.py:323~342`) — 인용 보충 필요 | D5 |
| `QUESTION_TTL` 24시간 `app/settings.py:118` (3.2 메인 2) | 맞음(상수는 119행, 시간 수는 118행) | D6 |
| 브리핑 자료 흐름 (2.3 S3.6, R-6) | 맞음 | D7 |
| `ask_user` 는 `@traced`, 인자 전부가 trace 입력 (R-1) | 맞음(`questions.py:183`, `context.py:186~190`) | D8 |
| `submit_answer` 에 `proposer`·`answerer` 없음 (U5c) | 맞음 | D9 |
| `security.md` 69·71행 (2.7) | 맞음 | D15 |
| **이름 규칙 거부는 루프 `_execute_call` 에서 (2.3 S3.2, U7)** | **틀림** | D11 — RM1 |
| **그 턴의 trace id 목록으로 지운다 (U6, R-3)** | **부정확** — `TurnResult.trace_ids` 에는 `ask_user`·`loop_turn` 행이 없다 | D12 — RM2 |
| 단위 검증 명령의 `tests/test_loop*.py`·`tests/test_read*.py` (U6·U7·U8) | **맞는 파일 0개** | D14 — RR1 |
| P9b 남은 것 목록의 세부(review-u12·u13 권고, 01-plan 541·557행) (2.5) | **확인 안 함** — 이 CR 의 판정에 쓰이지 않는다 | — |

## R-4. 사용자 결정 12건 대조

| # | 결정 | 개정 1 | 결과 |
|---|------|--------|------|
| 1 | 범죄·불법 = 동의하면 저장, 차단은 식별·인증만 | 3.2 사용자 1, 범주 `crime`, `BLOCK_TYPES` 6종 | 맞음 |
| 2 | 건강 좁은 범위 | 3.2 사용자 2, 1.2 "감기" 행, U1 함정 | 맞음 |
| 3 | 민감 항목은 인물 카드에서만 | R-6 표, U8 | 맞음. `GET /chat/history` 가 동의한 원문을 그대로 돌려주는 것은 "사용자 자신의 대화 기록"으로 포함했다 — 결정 8 이 대화 기록 보관을 전제하므로 어긋나지 않지만 문구 ①과 묶어 한 줄 알릴 것(R-6. 참고 ①) |
| 4 | 놓친 문장은 저장 전 한 번 더 | U6 | 기록 문장은 맞음. **조회 문장은 RM3** |
| 5 | 모달 한 번·로그인 세션에도 바로·채팅 403·문구 바뀌면 다시 | U4·U9a, `PRIVACY_NOTICE_VERSION` | 맞음. 403 을 `POST /answers/{id}` 까지 넓힌 것은 architect 해석(3.2 에 그렇게 적음) — 사용자에게 한 줄 확인 |
| 6 | 차단 6종, 전화번호·주소는 기억 | U2 `BLOCK_TYPES`, U1 함정 | 맞음 |
| 7 | "OpenAI API", 약관 단정 없음, 문구 확정 대기 | 8절 N4, W2 | 맞음(R-7 절) |
| 8 | 대기 중 보관, 거절·만료 시 대화 기록 줄 대체 + 대기 질문·trace 원문 삭제, 범주·규칙 id·동의 기록은 남김 | R-1~R-4, U5c·U6 | 방향은 맞음. **R-2·R-3 문장이 사후 질문 context 의 제안 내용을 빠뜨렸다(RM2)** |
| 9 | 소급하지 않음, 완화책 임의 추가 없음 | 구 U11 삭제, W14 | 맞음. R-10(배포 전 대기 질문 재검사 뒤 409)은 기존 데이터를 바꾸지 않고 배포 뒤의 답 처리에만 걸린다 — 소급으로 보지 않았다 |
| 10 | 다 끝난 뒤 한 번에, 순서 | U12 ①~⑦ | 맞음 |
| 11 | 완료 기준 4가지, 종료일은 그때 | 4.3 #17, 2.2 D17 | 맞음 |
| 12 | 세트 크기, dev·test 각각 | U1(11개 범주·유형마다 15~20 + 100 + 30 + 20) | 맞음 |

메인 세션 결정 4건(P9b 보류 · 주기 정리 · downgrade 실패 · 권장안 확정)은 3.2·4.1-1·U5c·U3·6절에 그대로 들어 있다.

## R-5. 소견

### [필수]

**RM1 · 이름 규칙(R-7)을 거는 자리가 실제 코드와 다르고, 그대로면 4.3 #12 와 부딪힌다.**
2.3 S3.2 행 "이 거부는 툴 밖(루프 `_execute_call`)에서 한다", U7 파일 목록 "`_execute_call`(… 이름 규칙 거부)". 그러나 D11:
- `_execute_call`(`loop.py:869~897`)은 `create_person` 을 **부르지 않는다**. LLM 이 낸 `update_person.new_alias` 만 지난다.
- 언급이 별칭·표시 이름으로 저장되는 자리는 `app/er/pipeline.py:461~465`(자동 연결 → 언급을 별칭으로), `loop.py:1847`(identity 답), `loop.py:1877`(new_person 답 → `display_name=mention`) 이다. 1.3 이 스스로 든 "마약 하던 걔" 는 이 세 자리로 들어온다.
- 첫째 자리는 `app/er/` 안인데 4.3 #12 는 `git diff --stat <U0 해시>.. -- app/er/` 0줄을 요구한다. `_execute_call` 에만 걸면 U7 ⑦("걸리는 별칭은 저장·임베딩 0")을 만족할 수 없고, `app/er/` 를 고치면 #12 가 깨진다.
- 표시 이름이 걸릴 때 **언제** 자르는지도 없다 — new_person 질문을 띄우기 전인지, 사용자가 관계 태그 칩을 누른 뒤(`loop.py:1877`)인지. 뒤라면 칩을 누른 사용자에게 "그 표현은 이름으로 기억하지 않아요" 가 나간다.
고칠 자리: 2.3 S3.2 행 · 4.4 R-7 · U7 파일·방식. 네 자리를 이름으로 적고, `app/er/` 를 건드리지 않는 방법(예: 루프가 `apply_resolution` 을 부르기 전에 언급을 판정 — 조회 턴이 이미 쓰는 "별칭 누적 0" 경로 `loop.py:1322`)인지, #12 를 "판정 로직 무변경"으로 고쳐 쓸지, 툴 안에서 막을지(그러면 툴 동작 변경이라 S3.2 문장이 달라진다) 하나로 정한다. 표시 이름이 걸리는 시점(질문 앞)도 R-7 에 적는다.

**RM2 · R-2·R-3 이 지우는 대상이 사후 질문의 context 를 다 덮지 못한다 — 사용자 결정 8·U6 ② 와 어긋난다.**
R-2 는 "`context` 의 `utterance` 를 지우고" 만 적었고 R-3 은 "R-2 에 더해 trace 행" 만 더한다. 사후 질문의 context 는 `pending_calls`(제안 인자 = 사건 내용·사실 값·일정 제목)·`held_drafts`·`mention` 을 담는다(D12, U6 방식의 context 모양에도 `pending_calls` 가 있다). U6 ② 는 "원문(발화와 **제안 내용**) 문자열이 DB 전수 `LIKE` 0" 을 요구하므로 규칙 문장과 수용 기준이 서로 다른 것을 말한다. D20 카드에는 R-2·R-3 문장이 옮겨진다.
또 R-3 의 `turn_trace_ids` 를 U6 은 "라우트가 그 턴의 trace id 목록을 덧붙인다"로 적었는데, 라우트가 받는 `TurnResult.trace_ids` 에는 `ask_user` 행과 `loop_turn` 행이 없다(D12). R-3 이 이름으로 든 4종(`loop_extract`·`loop_gate`·`ask_user`·`loop_turn`)을 그 목록으로는 다 못 잡는다.
고칠 자리: 4.4 R-2·R-3, U6 방식. 지우는 대상을 "남기는 키(예: `phase`·`categories`·`rule_ids`·`redacted`·`chat_message_id`·trace id 목록) 밖의 context 키 전부" 처럼 **남기는 쪽을 열거**하는 문장으로 바꾸고, 그 턴의 trace 행을 어떻게 모으는지(예: 같은 `session_id` 의 id 구간) 한 줄 적는다.

**RM3 · 사후 표시된 조회 문장의 처리가 문서 안에서 어긋나고, 남는 원문이 결정으로 올라오지 않았다.**
1.2 표 "규칙이 놓친 민감 문장" 행은 "저장 전·**ER 판정 LLM·임베딩 전에 묻는다**" 인데 U6 은 "조회 의도(`INTENT_QUERY`)는 저장이 없으므로 묻지 않는다". 묻지 않으면 그 문장은 ① ER 판정 LLM(`judge.py:166` 이 발화를 싣는다)·임베딩·조회 답 LLM 으로 한 번씩 더 가고 ② `chat_messages` 와 trace(`loop_extract`·`loop_query`)에 **동의도 거절도 없이** 남는다. 같은 문장이 규칙에 걸렸다면 N1 (a) 로 동의 칩을 거치고 거절하면 지워진다 — 규칙이 잡았는지에 따라 같은 문장의 처리가 갈린다. 사용자 결정 4 는 "저장 전에 한 번 더 묻는다"이고 조회에는 저장물이 없으니 U6 쪽이 틀렸다고 단정할 수는 없다. 그래서 사용자가 정할 일이다.
고칠 자리: 1.2 표의 그 행(기록 문장에 한정한다고 적거나 조회도 묻는 것으로) · U6 · 8절(N1 에 한 줄 더하거나 새 항목). R-6 표에도 "사후 표시된 조회 문장의 대화 기록·trace" 한 행.

### [권고] — 01-plan 에서 고치면 된다(02-plan-verify 에서 다시 본다)

- **RR1 · 실행되지 않는 검증 명령.** U6·U7 의 `tests/test_loop*.py`, U8 의 `tests/test_read*.py` 는 맞는 파일이 없다(D14 — 실제 이름은 `test_agent_loop.py`·`test_agent_query_loop.py`·`test_api_read_*.py`). zsh 에서는 명령 자체가 "no matches found" 로 죽는다. U2 검증의 `evaluation/sensitive_guard/run.py --split dev --rules-only` 는 러너를 U10 이 만들기로 돼 있어 U2 시점에 없다 — 러너의 규칙 부분을 U1 이나 U2 산출물로 옮긴다. `python3 -I …/run.py` 는 `app.guard` 를 import 해야 하는데 `-I` 에서는 저장소 루트가 경로에 없다(D14) — 기존 스크립트처럼 러너가 경로를 넣는다고 적는다.
- **RR2 · U5c ③ 의 "저장물에 표시"는 U7 산출물이다.** 표시 전파(`ToolContext.consent`·`_record`·`records.py`)는 U7 파일 목록에 있다. U5c 에서는 "추출 LLM 이 정확히 1회 불린다"까지만 두고 표시는 U7 ① 로 넘긴다(또는 최소 전파를 U5c 로 당긴다).
- **RR3 · 주인 없는 시험 파일·명령 없는 기준.** 4.3 #13 의 `tests/test_guard_messages.py` 가 어느 단위 파일 목록에도 없다. 4.3 #3 의 판정 명령 칸은 "U11 변이"뿐이다 — 변이 대상 시험 이름(`test_guard_pre.py` 의 trace 0 단언 등)을 함께 적는다.
- **RR4 · 만료 정리가 주기 작업 스위치에 묶인다.** 1분 루프는 `BRIEFING_SCHEDULER_ENABLED` 가 켜졌을 때만 뜨고(D13), `default_run_once` 는 일정이 있는 사용자만 돈다 — 정리는 사용자 반복 밖의 독립 단계여야 한다. 스위치가 꺼진 환경에서는 만료 원문이 남는다는 것을 D20·`docs/RUNNING.md` 에 한 줄.
- **RR5 · 낱말 목록을 누가 만드는가.** 6절 G2 는 "eval-agent 가 dev 세트에서 귀납", U2 는 backend-agent 가 `rules.py` 를 쓴다. test 세트를 쓴 eval-agent 가 목록을 귀납하면 U1 README 에 적기로 한 누출 경로가 더 직접적이 된다. test 를 열지 않는 쪽(backend-agent)이 dev 만 보고 귀납하는 것으로 한 줄 정한다(원칙8).
- **RR6 · 이름 규칙의 오탐을 재지 않는다.** R-7 은 호칭("교회 오빠", "정신과 선생님")이 표시 이름일 때 인물을 만들지 않는다. U1 함정 세트에 호칭형 이름을 넣고 U10 에 이름 규칙 오탐 표를 따로 둔다 — 지금 지표(감지율·오탐률)는 문장 단위뿐이다.
- **RR7 · U4 가 기존 시험 픽스처에 미치는 영향.** `require_notice` 가 `chat`·`submit_answer` 에 붙으면 고지 미동의 계정을 만드는 기존 시험이 403 이 된다. U6 ③ "기존 루프 시험 무수정 통과"와 함께 읽히도록, U4 에서 공용 픽스처를 어떻게 바꾸는지(시험 본문 수정 0) 적는다.
- **RR8 · 1.3 의 인용 보충.** 질의 `q` 근거에 기록 턴 자리 `loop.py:323~342`(`_ordered_mentions`)를 더한다(D5).

### [참고]

- ① 문구 ①·②의 "인물 카드에서만 보여요" 와 달리 **대화 기록에는 그 문장이 그대로 남는다**(R-6 표 `GET /chat/history` 행). 문구 확정 때 사용자가 함께 보면 된다.
- ② `get_briefing` 이 민감 항목을 돌려주지 않게 되는 것은 **툴 동작 변경**이다(시그니처·반환 모양은 그대로). 2.3 S3.2 가 그렇게 적었고 `get_briefing` 의 호출자는 `inputs.py:92` 하나뿐이라 영향 범위는 브리핑에 그친다. 툴 7종의 개수·시그니처, `ask_user` 별도 툴 유지는 지켜진다.
- ③ 원칙9 예외(거절·만료된 원문을 trace 에서 지움)는 사용자 결정 8 의 "trace 의 원문도 지운다"에서 바로 나온다. 행·step·tool_name·토큰·시각·범주·규칙 id 를 남기는 것으로 "무엇을 언제 왜 판정했나"는 유지된다. `CLAUDE.md` 원칙9 문장 수정이 2.7 목록에 있다.
- ④ 원칙8: test 세트를 U2 착수 전에 동결하고 해시를 적는 것, 규칙 수치와 LLM 수치를 같은 표에 두지 않는 것, 목표치를 정하지 않고 실패 사례를 산출물로 두는 것이 수용 기준에 있다.
- ⑤ 원칙7: 문구 초안에서 `BRIEFING_FORBIDDEN_EXPRESSIONS` 14개에 걸리는 표현 0(D16). 공감·평가·조언 문장은 찾지 못했다.
- ⑥ R-8(민감 사건은 승격에 넣지 않는다)·R-5(한 번 민감이면 그 키는 계속 민감)는 개정 1 이 새로 고른 설계다. 둘 다 되돌릴 수 있고 W5 에 과잉 가림으로 적혀 있다. 사용자 결정이 필요한 것으로 보지는 않았으나, 결과("동의한 민감 사건은 요약 사실로 이어지지 않는다", "그 키의 일반 값도 브리핑에서 빠진다")를 사용자에게 한 줄 알리는 편이 낫다.
- ⑦ R-10 은 규칙 목록이 대기 질문 생성과 답 사이에 바뀌면(재배포) 정상 질문도 409 가 될 수 있다. 창이 24시간이라 영향은 작다.
- ⑧ 루프 예외로 끝난 턴의 `loop_error` 행에는 발화가 실린다(D9). 차단 유형은 U5a 가 가린 문장으로 덮지만, 규칙이 놓친 민감 문장은 표시 없이 남는다 — W3 의 범위다.

## R-6. "남은 사용자 결정"(8절) 점검

- **N1·N3·N4** 는 사용자만 정할 수 있는 것이 맞다(제품이 사용자에게 무엇을 묻고 무엇을 막는가, 고지 문구).
- **N2** 는 설계 선택에 가깝지만 사용자에게 보이는 동작("이름으로 기억하지 않아요")이라 올린 것이 적절하다. RM1 의 시점 문제와 함께 묻는다.
- **빠진 것**: RM3(사후 표시된 조회 문장). 그리고 결정 5 의 403 을 `POST /answers/{id}` 까지 넓힌 해석은 3.2 표 안에만 있다 — 8절에 확인 항목으로 한 줄.
- 6절의 권장 확정분(G2~G21)은 1차 검토 6절이 "권장안으로 진행해도 되는 것"으로 분류한 범위 안이다. 새 상수를 임의로 만든 자리는 찾지 못했다(`QUESTION_TTL`·2000자·`LOOP_MAX_RESUME_BYTES` 는 기존 값, `PRIVACY_NOTICE_VERSION = 1` 은 판 번호의 시작값).

## R-7. 고지·동의 문구 초안

법적 충분성을 단정한 문장, OpenAI API 약관 내용(보관 기간·학습 사용)을 단정한 문장은 **찾지 못했다**. 1.1 의 9장 줄은 "완화이며 … 해결하지 않는다"를 같은 문장에 넣었고, 범주 정의는 "법령상 분류가 아니다"로 적었다. 법적 판단이 아니라 **사실과 맞는지**의 관점에서 사용자가 확정할 때 볼 곳 3가지:
1. 문구 ③ "…같은 정보는 기억하지 않아요", 문구 ④ "…는 전송 전에 가립니다" — 단정형이다. 가림은 정규식이라 놓칠 수 있고(특히 비밀번호는 정해진 모양이 없다), "모든 경우를 찾아내지는 못합니다"는 민감 내용 문장에만 붙어 있다.
2. 문구 ①·② "인물 카드에서만 보여요" — 대화 기록에는 남는다(참고 ①).
3. 문구 ④ 는 "입력한 대화 … 그 문장을 전송"만 말한다. 실제로는 저장된 사실·원문이 브리핑·승격·조회 답을 만들 때 다시 OpenAI API 로 간다(`compose.py:227`·`extract.py:208`). 넣을지는 사용자 몫이다.

## R-8. 다음 재검토 조건

RM1~RM3 을 고친 개정이 오면 이 문서에 절을 하나 더한다. 볼 자리: 2.3 S3.2 행·4.4 R-7·U7(RM1), 4.4 R-2·R-3·U6(RM2), 1.2 표·U6·8절(RM3). 그 밖의 절은 다시 보지 않는다. [권고] RR1~RR8 은 `P9d-sensitive-guard` 02-plan-verify 에서 확인한다.

---

# 재검토(개정 2)

**판정: 이행 가능** — RM1~RM3 은 셋 다 닫혔고, 사용자 결정 18건과 어긋나는 자리는 찾지 못했다. [필수] 는 0건이다. 개정 2 가 새로 적은 문장 중 코드와 맞지 않는 자리가 있으나(아래 VR1~VR8) 모두 수용 기준을 서로 모순되게 만들지 않고, 카드에 옮길 때 한 문장을 고쳐 적거나 01-plan 에서 닫을 수 있는 크기다. 이 CR 을 근거로 문서 이행(D20 카드 등)과 `P9d-sensitive-guard` 01-plan 작성을 시작해도 된다. 단 ① VR1·VR2 는 **S3.2·S3.4 보충에 글자 그대로 옮기지 말고 고쳐 적는다** ② 사용자에게 물을 것은 8.4 의 N5·N6 에 **수동 브리핑 403(VR4)** 한 건을 더한다. 02-plan-verify 에서 VR1~VR8 을 다시 본다.

검토자: verifier (fable) | 재검토일: 2026-11-22 | 대상: `docs/wiki/changes/CR-009.md` 개정 2(539행, 미커밋) | 기준 커밋: `cef47d0`
이 절은 CR·카드·코드를 고치지 않는다. 법적 판단은 하지 않는다. 문구 수정안도 내지 않는다.

## V-1. 직접 실행한 명령과 핵심 출력

| # | 명령 | 핵심 출력 |
|---|------|-----------|
| E1 | `bash .claude/scripts/gitlog.sh CR-009` · `git status --short` | CR 태그 커밋 0(미커밋). `CR-009.md`·`review-CR-009.md` 는 `??`, `HANDOFF.md`·`journal.md` 는 `M`. `CURRENT.md` 는 아직 `active: P9b-auth` · `frozen: none` |
| E2 | `sed -n 315,345p`·`536,690p app/agent/loop.py` · `grep -n "_ordered_mentions(" app/agent/loop.py` | `_ordered_mentions` 정의 323~342행. **호출은 552행 한 곳 — `_resolve_mentions_impl` 안**(`resolve_mentions` 628행이 감싼다). 581행 `resolve(ctx, mention, …)` 이 `app.er` 진입, 583~584행 merge 면 `apply_resolution` |
| E3 | `sed -n 865,900p app/agent/loop.py` | `_execute_call` 869~897행. `update_person` 분기(892~895행)는 `facts=args.get("facts"), new_alias=args.get("new_alias")` 만 넘긴다 — **`display_name` 은 넘기지 않는다.** `create_person` 호출 없음 |
| E4 | `grep -n "display_name" app/agent/gate.py app/agent/propose.py` | `gate.py:49`·`:264` — `update_person` 제안에 `display_name` 이 있으면 게이트가 `needs_confirmation` 으로 거부. `propose.py:161` 스키마에는 필드가 있다 |
| E5 | `sed -n 1636,1648p`·`398,430p app/agent/loop.py` | `_drop_calls_for_mention(pending_calls: list[PendingCall], mention)` 1641행에 **있다**. 인자는 재개의 `PendingCall` 목록. `_pending_calls_from`(398~430행)은 확정되지 않은 **모든** 언급의 제안을 되묻기 context 에 담는다 |
| E6 | `sed -n 1710,1990p app/agent/loop.py` | 1847행 `app_tools.update_person(ctx, person_id, new_alias=mention)`(identity 답) · 1877~1883행 `create_person(display_name=mention, aliases=[mention] …)`(new_person 답) · 1857행 identity 거절 → `_followup_new_person_turn` · 재개도 `resolve_mentions(…, preresolved=…)` 를 다시 탄다 |
| E7 | `sed -n 425,470p app/er/pipeline.py` | merge 밴드 → `update_person(ctx, person_id=resolution.matched_person_id, new_alias=resolution.mention)` (461~465행 부근) |
| E8 | `sed -n 1087,1190p app/agent/loop.py` | `_propose` → `_gate` → `if proposal.intent == INTENT_QUERY: return _run_query_turn(…)` → `resolve_mentions` → `_record`. `TurnResult.trace_ids` 는 extract·gate·resolve·record 4개(1180~1184행) |
| E9 | `sed -n 1238,1345p`·`1650,1709p app/agent/loop.py` | `_run_query_turn` 은 `_query_mentions(proposal)` 로 언급을 모아 `resolve()` 를 부르고, merge 면 `apply_resolution` 을 부르지 않는다("별칭 누적 0"). **`_resume_query_turn` 은 identity 답 전용** — `context["candidate_ids"][answer]` 로 인물을 고르고 `resolve()` 를 부르지 않는다 |
| E10 | `grep -n "class AgentTrace" -A 14 app/db/models.py` · `grep -n "session_id" app/api/deps.py` · `grep -n "session_id" app/briefing/run.py` | `agent_traces(id PK, session_id Text NOT NULL, …)`, 색인 `(session_id, created_at)`. 대화 ctx 는 `chat_session_id(user.id)` = `chat:<user_id>`(`deps.py:120`·`:218`), 답 ctx 는 질문 행의 `session_id`(`:152`). 브리핑 실행은 `briefing:<uuid4>`(`run.py:183`) — 대화 구간에 섞이지 않는다 |
| E11 | `sed -n 212,304p`·`330,432p app/api/routes.py` · `grep -n "@traced" app/tools/questions.py` | `chat` 은 `append_chat_message` 뒤 `session.begin_nested()` 안에서 `run_turn`. `submit_answer` 는 `answer_question`(`@traced("answer_question")`, 237행 — 입력은 질문 id·답 문자열) → `load_resume_input` → `resume_turn`. 의존성에 `proposer`·`answerer` 없음 |
| E12 | `sed -n 433,462p app/api/routes.py` · `sed -n 105,175p app/briefing/scheduler.py` | `POST /briefings/run`(`run_briefings_endpoint`)은 **로그인 계정 한 명**의 `run_briefings(trigger="manual")`. 주기 작업은 `_due_user_ids`(= `persons.user_id`, `users` 를 읽지 않음) → 사용자마다 `_run_for_user` → `run_briefings`. `briefing_run` trace 는 `run_briefings` 가 쓴다(`run.py:321`) |
| E13 | `ls tests` 대조(개정 2 가 든 이름) | 실재: `conftest.py`·`test_agent_loop.py`·`test_agent_query_loop.py`·`test_agent_query_answer.py`·`test_memory_loop.py`·`test_tools_questions.py`·`test_auth_required_routes.py`. 글롭 개수: `test_auth*` 8 · `test_briefing_scheduler*` 2 · `test_briefing*` 6 · `test_mcp*` 3 · `test_push*` 7 · `test_api_read_*` 4 · `test_memory*` 4. `test_guard_*`·`test_schema_0006`·`test_privacy_notice` 는 아직 없음(새 파일 — 2.7 과 맞음) |
| E14 | `grep -n "fixture\|def " tests/conftest.py` · `sed -n 50,135p tests/auth_helpers.py` · `grep -rl "auth_helpers" tests \| wc -l` | **`tests/conftest.py` 에 로그인 계정 픽스처가 없다**(DB·임베더 픽스처뿐). 계정을 만드는 공용 도우미는 `tests/auth_helpers.py::make_user`(58행)·`logged_in_client`(108행), 쓰는 파일 23개 |
| E15 | `grep -rn "auth/signup" tests` · `grep -cE "_signup\(" tests/test_auth_api.py tests/test_auth_nickname.py` · `grep -n "status_code == 201" tests/test_auth_api.py` | 가입 본문을 직접 보내는 시험 파일 4개(`test_auth_api.py` `_signup(` 32곳·`test_auth_nickname.py` 31곳·`test_auth_availability.py:47`·`:125`·`test_auth_origin.py:104`). 본문은 `username`·`password`·`nickname` 뿐이고 201 을 단언한다(`test_auth_api.py:94`·`129`·`143`·`152`·`175`·`188`) |
| E16 | `sed -n 200,209p app/memory/extract.py` · `grep -rn "recent_chat_messages" app` · `sed -n 143,176p app/er/judge.py` | `extract.py:203` 기존 사실 줄·`:208` `raw="{event.raw_utterance}"`. `recent_chat_messages` 사용처는 `routes.py:429` 하나. `judge.py` 후보 요약에 `display_name`·`aliases`, 프롬프트에 mention·utterance |
| E17 | `.venv/bin/python`(읽기 전용) — `BRIEFING_FORBIDDEN_EXPRESSIONS` 14개를 8.2 구간과 8.4 N5 행에 대조, HANDOFF 24행의 문구 조각 3개를 8.2 에서 셈 | 걸리는 항목 `[]`·`[]`. 조각 출현 수 2("입력한 문장은 대화 기록에 남아요" — ①·②)·1("…로 보이는 부분은 가린 뒤 처리했어요")·1("저장된 내용은 브리핑을 만들거나 질문에 답할 때 다시 OpenAI API로 전송될 수 있습니다") |
| E18 | `grep -n "LOOP_MAX_RESUME_BYTES\s*=\|QUESTION_TTL\|BRIEFING_LEAD_HOURS\s*=\|BRIEFING_INTERVAL_SECONDS\s*=" app/settings.py` | `118 QUESTION_TTL_HOURS = 24`·`119 QUESTION_TTL`·`209 LOOP_MAX_RESUME_BYTES = 8192`·`215 BRIEFING_LEAD_HOURS = 24`·`220 BRIEFING_INTERVAL_SECONDS = 60` |

## V-2. RM1~RM3 판정

| 소견 | 판정 | 근거 |
|------|------|------|
| **RM1** 이름 규칙 자리 | **닫힘**(잔여 VR2) | 2.3 S3.2 행·4.4 R-7·U7 파일 목록·⑦⑧·4.3 #10b 가 네 자리를 이름으로 적었고 전부 `app/agent/loop.py` 안이다. 언급을 `resolve()`(E2, 581행) 앞에서 자르면 E7 의 자동 연결 별칭·identity/new_person 질문(585~609행)·E6 의 두 저장 자리에 닿지 않는다 — `app/er/` 를 고치지 않고 성립하므로 4.3 #12 와의 충돌이 없어졌다. 시점("새로운 사람인가요?" 질문 전)도 R-7 ①·U7 ⑦ 에 적혔다(사용자 결정 15 와 일치). `_drop_calls_for_mention` 은 실재한다(E5) |
| **RM2** 지우는 대상 | **닫힘** | R-2 가 **남기는 키 8개를 열거**하고 그 밖은 전부 지우는 문장으로 바뀌었다 — `pending_calls`·`held_drafts`·`mention`·`resume` 이 빠질 수 없다. U5c ⑦·U6 ②·4.3 #4 가 "키 집합이 남기는 키의 부분집합" 으로 기계 판정한다. trace 는 `TurnResult.trace_ids` 대신 같은 `session_id` 의 id 구간으로 모은다 — 스키마에서 가능하다(E10: `id` 정수 PK + `session_id`, 대화는 `chat:<user_id>` 하나, 브리핑은 다른 `session_id`). `ask_user`·`loop_turn` 행은 `run_turn` 안에서 쓰이므로 구간에 든다(E8·E11). 동시 요청 겹침은 "더 넓게 지우는 쪽" 으로 적고 8.6 으로 넘겼다 |
| **RM3** 사후 표시된 조회 문장 | **닫힘**(잔여 VR1) | 1.2 표·U6 방식·수용 기준 ①·4.3 #5·R-6 새 행이 모두 "기록이든 조회든 묻는다, ER 판정·임베딩·조회 답 LLM 전에 멈춘다" 로 같아졌다(사용자 결정 14 와 일치). U6 의 자리 "게이트 직후, 의도 분기보다 앞" 은 E8 의 순서에서 가능하다. 미확정 문구는 8.4 N5 로 올라왔다 |

## V-3. RR1~RR8 처리

| 권고 | 처리 | 확인 |
|------|------|------|
| RR1 실행 안 되는 명령 | 고침 | U6·U7·U8 의 시험 파일 이름이 실재한다(E13). 러너 규칙 모드를 U2 로 옮기고 `sys.path` 삽입을 적었다 |
| RR2 U5c ③ | 고침 | 표시 단언을 U7 ① 로 넘겼다 |
| RR3 주인 없는 시험 파일 | 고침(잔여 VR5) | `test_guard_messages.py` 주인 = U5a, 4.3 #3 에 시험 이름. 다만 문구 ④·⑤(고지 문단)의 서버 상수 주인이 없다 |
| RR4 만료 정리 | 고침 | 사용자 반복 밖 독립 단계 + `RUNNING.md` 한 줄(U5c) |
| RR5 목록 귀납 주체 | 고침 | U2·3.2·6절 G2 가 backend-agent(dev 만)로 같다 |
| RR6 이름 규칙 오탐 | 고침 | U1 호칭형 함정·U10 이름 규칙 오탐 표 |
| RR7 기존 시험 픽스처 | **부분 — 01-plan 으로 넘김(8.6), 넘긴 기준 자체가 틀림(VR3)** | E14·E15 |
| RR8 1.3 인용 | 고침 | 1.3 에 `loop.py:323~342`. 9절 개정 1 표의 옛 인용(`1248~1259`)은 이력 줄 |

## V-4. 사용자 결정 13~18 대조

번호는 CR 3.2 표 기준이다. **CR 의 16·17 은 이번 요청이 준 순서(16 = 브리핑, 17 = 403)와 서로 바뀌어 있다 — 내용은 같다.** 카드·보고에서 번호로 부를 때 CR 3.2 번호를 쓴다.

| CR # | 결정 | 개정 2 | 결과 |
|------|------|--------|------|
| 13 | 조회형 = 같은 칩·중립 문구, 답은 일반 기록만, 민감만 있으면 카드 안내 | 1.2 표·U5b·8.2 문구 ①("진행할까요?") | 맞음 |
| 14 | 사후 표시된 조회도 묻는다, 더 보내기 전에 멈춤, 거절하면 대화 기록·trace 에서 지움, 규칙이 잡았을 때와 같은 처리 | 1.2 표·U6·R-2·R-3·R-6·U6 ⑤ | 맞음. 문구는 N5 |
| 15 | 민감한 이름·별칭 = 저장하지 않고 안내, new_person 질문 전에 멈춤 | R-7·U7 ⑦·4.3 #10b·8.2 부속 | 맞음. 결정의 조건은 "저장되려 할 때" 인데 설계는 ER 앞에서 자른다 — 그 결과는 VR6 |
| 16 | 403 을 칩 답변에도, 동의하면 떠 있던 칩에 답할 수 있다 | U4 수용 기준("동의 뒤 떠 있던(미만료) 칩에 답하면 200")·4.3 #10 | 맞음 |
| 17 | 미동의 계정 = 브리핑 생성·푸시도 건너뜀 | U4·2.3 S3.6·4.3 #10 | 맞음. **수동 브리핑 403 은 사용자가 답하지 않았다** — 개정 2 는 1.2·3.2·U4·8.1·9절에서 "architect 제안" 으로 표시했지만 2.2 D18 행·4.3 #10·W16 에는 표시 없이 들어 있고 8.4 "남은 사용자 결정" 에는 없다(VR4) |
| 18 | 문구 확정안 글자 그대로 | 8.2 | HANDOFF 24행에 남은 조각 3개가 8.2 에 그대로 있다(E17). **확정안 전문은 내가 볼 수 있는 자료(HANDOFF·journal)에 없어 나머지 글자는 대조하지 못했다 — 확인 안 됨.** 메인 세션이 사용자 답 원문과 8.2 를 한 번 맞춰 본다 |

## V-5. 8.3 A1~A3 대조 (문구 수정안은 내지 않는다)

| # | 개정 2 의 주장 | 결과 | 근거 |
|---|----------------|------|------|
| A1 | ①·② "대화 기록에 남아요" 는 거절·만료 때 대체되는 설계와 어긋난다 | **사실** | R-2 "대화 기록 줄 `content` → (기억하지 않은 민감한 내용)", 사용자 결정 8. 문구에는 조건이 없다 |
| A2 | ④ "저장된 내용은 … 다시 전송될 수 있습니다" 는 민감 기록에는 해당하지 않는다(넓게 말함) | **사실** | R-6 제외 행(브리핑 입력·조회 답)·R-8(승격 입력 제외). "수 있습니다" 라 거짓은 아니다 |
| A3 | 일반 기록의 재전송 경로는 승격·ER 판정에도 있다(좁게 말함) | **사실** | E16 — `extract.py:203·208`, `judge.py` 후보 요약의 표시 이름·별칭. 대화 기록은 LLM 으로 가지 않는다(`recent_chat_messages` 사용처 1) |

개정 2 가 들지 않은 것 한 가지(참고): ④ "민감할 수 있는 내용은 **보내기 전에** 한 번 더 묻습니다" — 규칙이 놓친 문장은 보낸 뒤에 묻는다(W3, 문구 ②). 뒤 문장 "다만 모든 경우를 찾아내지는 못합니다" 가 받치고 있어 어긋남으로 보지는 않았다. N6 에서 사용자가 함께 보면 된다.

## V-6. 소견

### [필수]

없음.

### [권고] — 카드 전사(U0) 또는 01-plan 에서 닫는다. 02-plan-verify 에서 다시 본다

- **VR1 · 사후 표시된 조회의 재개 함수가 코드와 맞지 않는다(2.3 S3.4 행 ②, U6 방식).** "조회는 기존 조회 재개 경로 `_resume_query_turn`" 이라 적었는데 그 함수는 identity 답 전용이다 — `context["candidate_ids"][answer]` 로 인물을 고르고 `resolve()` 를 부르지 않는다(E9). 사후 질문은 ER **앞**에서 멈췄으므로 후보가 없다. 긍정 재개가 다시 타야 하는 것은 언급 해석부터 도는 `_run_query_turn` 쪽이고, 그 함수는 `Proposal` 을 받아 `_query_mentions(proposal)` 로 언급을 모은다(게이트 판정과 무관 — 조회 턴에서는 기록 툴 제안이 게이트에서 전부 거부된다). 그래서 context 에 저장할 것도 게이트를 통과한 `pending_calls` 가 아니라 제안의 툴 호출(또는 언급 목록)이어야 한다. **S3.4 보충에 함수 이름을 그대로 옮기지 말고** "조회는 언급 해석 단계부터 다시 돈다(인식 LLM 재호출 없음)" 로 적고, 함수·context 모양은 01-plan U6 에서 정한다. 수용 기준(U6 ①·②)은 그대로 성립한다.
- **VR2 · R-7 의 자리 문장 세 곳(2.3 S3.2 행, 4.4 R-7, U7).** ① "`_ordered_mentions` 뒤·`resolve_mentions` 앞" 이라는 자리는 문자 그대로는 없다 — `_ordered_mentions` 는 `resolve_mentions` 가 감싼 `_resolve_mentions_impl` **안**(552행)에서 불린다(E2). 실제 자리는 "552행 뒤·581행 `resolve()` 앞" 이거나 `run_turn` 에서 미리 거르는 것이다. 전자면 재개의 `resolve_mentions` 재진입(E6)도 같이 덮인다. ② "기존 `_drop_calls_for_mention` 재사용" — 그 함수는 재개의 `PendingCall` 목록을 받는다(E5). 첫 턴의 제안은 `Proposal`/`GateVerdict` 모양이고, 거른 언급의 제안이 **다른 언급의 되묻기 context**(`_pending_calls_from`, E5)에 실려 재개 때 되살아나지 않게 하는 처리가 따로 필요하다. ③ ④번 자리의 "`update_person.new_alias`·`display_name`" — `_execute_call` 은 `display_name` 을 넘기지 않고(E3) 게이트가 그 제안을 먼저 거부한다(E4). 닿지 않는 경로다. 카드에는 "`new_alias`" 만 적는다. ④ identity 거절 → `_followup_new_person_turn`(1857행)은 네 자리에 없다 — 배포 전 identity 질문에서만 닿고 R-10 재검사와 ③(1877행)이 받치지만, 그 경우 "새로운 사람인가요?" 가 한 번 뜬 뒤 막힌다. 01-plan 에서 자리로 넣을지 한 줄.
- **VR3 · U4 의 기존 시험 기준이 서로 모순된다(U4 파일 목록·수용 기준 마지막 항, 8.6 RR7).** ① "`tests/conftest.py` 의 로그인 계정 픽스처" 는 없다. 계정을 만드는 공용 도우미는 `tests/auth_helpers.py`(23개 파일이 쓴다, E14)다. 판정 명령의 제외 목록(`:!tests/conftest.py`·`:!tests/test_privacy_notice.py`)에 그 파일이 없어, 도우미를 고치면 "0줄" 이 깨진다. ② 가입 본문에 `privacy_notice_accepted: true` 가 없으면 422 라는 기준과 "기존 시험 본문 diff 0" 은 같이 성립하지 않는다 — 가입 본문을 직접 보내고 201 을 단언하는 시험이 4개 파일 60곳 넘게 있다(E15). 01-plan U4 에서 고칠 파일 목록(도우미 1 + 가입 시험 4)을 적고 diff 0 기준을 "그 목록 밖 0줄" 로 바꾼다. ③ `git diff --stat <해시>..` 는 `<해시>` 와 HEAD 의 비교라 **커밋 전 작업 트리 변경을 보지 못한다**(구현 에이전트는 커밋하지 않는다). U4·U7·4.3 #12 의 세 명령을 `git diff --stat <해시> -- …`(작업 트리 포함)로 적는다.
- **VR4 · 수동 브리핑 403 이 "남은 사용자 결정" 에 없다(8.4, 2.2 D18 행, 4.3 #10, W16).** 사용자 결정 17 은 주기 브리핑·푸시만 말했다. 개정 2 는 다섯 곳에서 "architect 제안" 이라 표시했으나 D18 보충 행·수용 기준 #10·W16("사용자 결정 17 — … 수동 브리핑은 403")에는 확정처럼 들어 있고 8.4 에는 항목이 없다. 근거 3가지는 타당하고 `POST /briefings/run` 이 로그인 계정 한 명의 실행이라(E12) `require_notice` 를 그대로 걸 수 있다. 다만 사용자에게 보이는 동작이므로 N5·N6 과 함께 한 줄 확인받고, 그 전에 D18 보충을 쓸 때는 "(사용자 확인 대기)" 를 붙인다.
- **VR5 · 문구 ④·⑤(가입 고지·재고지 모달)의 서버 쪽 주인과 순서.** U9a 는 "문구는 U4 서버 상수와 같은 문자열" 이라 하는데 U4 파일 목록에는 문구 상수가 없고(`PRIVACY_NOTICE_VERSION` 뿐), 문구의 단일 출처 `app/guard/messages.py`·`tests/test_guard_messages.py` 는 U4 **뒤**의 U5a 가 만든다. 4.3 #13 의 단위 칸(U5a·U5b·U6·U9a)에도 U4·U7·U8 이 없다(U5a 는 U4·U7·U8 이 자기 문구를 더한다고 적었다). 01-plan 에서 ④·⑤ 를 서버에 둘지 `web/` 에만 둘지, 판 번호(G8)와 문구 변경을 무엇으로 묶어 판정하는지, 파일을 만드는 단위를 정한다.
- **VR6 · 이름 규칙이 ER 을 건너뛰는 것을 D20 에 규칙으로 적는다(원칙1·2·4·9).** 걸린 언급은 병합되지도, 인물로 만들어지지도, 질문으로 가지도 않고 딸린 기록이 버려진다 — 오병합(원칙1)이 생기지 않고, ER 을 LLM 한 번으로 대신하는 것도 아니므로(원칙4) 원칙과 충돌하지 않는다. 같은 모양의 선례가 조회 턴에 있다(`loop.py` new_person 밴드 "질문 행 0", E9). 다만 원칙2 문장("그 미만은 반드시 `ask_user`")을 읽는 사람이 예외로 오해하지 않도록 D20 에 "확신도 판정 이전의 제외이며 병합·생성·질문 어느 것도 하지 않는다" 를 적는다. 함께 적을 것 둘: ① **근거 trace** — 이름 규칙으로 버린 판정을 무엇으로 남기는지가 없다(`guard_check` 는 사전 검사·가림에만 정의됐다). 원칙9 에 따라 결정값·규칙 id·제안 인덱스를 남기는 행을 정한다. ② **결과** — 배포 전에 이미 저장된 별칭에 민감 낱말이 들어 있으면, 그 별칭으로 부른 기록 턴은 ER 앞에서 잘려 그 인물에 더는 기록되지 않는다(조회 턴은 대상이 아니다). 사용자 결정 15 의 조건("저장되려 할 때")보다 넓게 걸리는 자리다. 소급하지 않는다는 결정 9 와 맞닿으므로 D20·W14 에 한 줄 적고 사용자에게 알린다.
- **VR7 · 미동의 계정을 건너뛰는 자리와 trace.** U4 는 "사용자 반복에서 건너뜀 … `briefing_run` trace 에 사유 `notice_required` 와 일정 id" 라 적었다. `briefing_run` 행은 `run_briefings` 가 쓰고(E12) 대상 사용자는 `persons.user_id` 에서 나오며 `users` 를 읽지 않는다. 반복에서 건너뛰면 그 행을 누가 쓰는지, `briefed_at` 이 NULL 로 남는 동안 1분마다 한 행씩 쌓이는지(창 24시간 — E18)를 01-plan 에서 정한다.
- **VR8 · U6 사후 질문 context 의 `chat_message_id`.** U6 은 루프가 `ask_user(context={… "chat_message_id": …})` 를 부른다고 적었는데, 그 줄 id 는 라우트의 `append_chat_message` 가 만들고 `run_turn` 은 받지 않는다(E11). `turn_trace_range` 처럼 라우트가 덧붙이는지 ctx 로 넘기는지 01-plan 에서 정한다. R-2 의 대화 기록 대체가 이 키에 기댄다.

### [참고]

- ① `turn_trace_range` 는 `chat` 의 세이브포인트 안에서 쓰인 행을 같은 세션으로 읽으므로 "직후 최대 id" 가 자기 행을 본다(E11). 답 저장 trace(`answer_question`)는 구간 밖이지만 원문을 담지 않는다(질문 id·칩 문자열).
- ② 루프 예외로 끝난 사후 턴은 세이브포인트가 되돌려져 질문이 남지 않고 `loop_error` 행에 발화가 남는다 — 개정 1 재검토 참고 ⑧(W3 범위)과 같다. 달라진 것 없음.
- ③ 확정 문구(8.2)와 N5 (가) 후보에서 `BRIEFING_FORBIDDEN_EXPRESSIONS` 14개에 걸리는 표현 0(E17). 법적 충분성·약관 내용을 단정한 문장은 찾지 못했다.
- ④ 툴 7종: 개수·시그니처 변경 없음. `ask_user` 는 별도 툴로 남고 `kind` 값 집합만 4종이 된다. `get_briefing` 의 동작 변경은 개정 1 재검토 참고 ② 그대로다.
- ⑤ 원칙8: test 세트 동결·귀납 주체 분리·규칙/LLM 표 분리가 U1·U2·U10 수용 기준에 있다.
- ⑥ 코드 행 번호(`323~342`·`869~897`·`1180~1184`·`1847`·`1877`·`pipeline.py:461~465`·`types.py:400~407`)는 `cef47d0` 에서 맞다(E2·E3·E6·E7·E8).
- ⑦ 4.1-1 의 이행 시작 조건("8절 남은 결정 답 뒤")과 HANDOFF 의 "통과면 남은 결정만 사용자에게" 는 순서가 같다.

## V-7. "남은 사용자 결정"(8.4) 점검

- **N5**(사후 표시된 조회의 칩 문구)·**N6**(A1~A3 을 어떻게 할지) — 둘 다 사용자에게 보이는 문구라 사용자만 정할 수 있는 것이 맞다. architect 가 N6 에 문구 수정안을 내지 않은 것도 지시와 맞다.
- **빠진 것 1건**: 수동 브리핑 `POST /briefings/run` 의 403(VR4).
- **알리기만 하면 되는 것**(결정이 아니라 결과): VR6 ② (기존 별칭에 민감 낱말이 있으면 그 별칭으로는 기록되지 않는다), 개정 1 재검토 참고 ⑥ 의 두 결과(동의한 민감 사건은 요약 사실로 이어지지 않는다 · 한 번 민감이 된 키는 일반 값으로 덮어도 브리핑에서 빠진다 — W5).
- 임의로 만든 상수는 찾지 못했다(`QUESTION_TTL`·8192·2000자는 기존 값 — E18).

## V-8. 01-plan · 02-plan-verify 에서 닫을 것

1. VR1 — 사후 조회 재개의 함수·context 모양(S3.4 보충 문장은 U0 에서 고쳐 적는다)
2. VR2 — 이름 규칙 ① 의 실제 자리, 첫 턴 제안 버리기와 `_pending_calls_from`, `display_name` 삭제, `_followup_new_person_turn`
3. VR3 — U4 가 고치는 시험 파일 목록과 diff 기준, `git diff` 명령 세 곳의 모양
4. VR5 — 문구 ④·⑤ 의 주인·판정 방법·만드는 단위
5. VR6 — 이름 규칙의 근거 trace, D20 의 원칙2 관계 문장, 기존 별칭 결과 한 줄
6. VR7 — 미동의 건너뜀의 자리와 trace 빈도
7. VR8 — `chat_message_id` 를 context 에 싣는 주체
8. 개정 2 의 8.6 목록 그대로(행 번호 재확인 · `gitlog.sh FIX-015` · `loop.py:1322` 직접 읽기 · 동시 요청 겹침의 크기 · R-10 규칙 목록 변경 창)
9. 사용자 결정 18 — 확정 문구 전문과 8.2 의 글자 대조(메인 세션, U0 전)
