# review-FIX-037 · 인식 프롬프트(의도·이벤트 유형)·조회 답 프롬프트(근황)·거부 알림 — 커밋 전 리뷰

검토자: verifier (fable) · 2026-11-17 · 기준 HEAD `9fce41d` (dev2) + 미커밋 작업 트리(`app/agent/propose.py` +29/-3 · `respond.py` +6 · `loop.py` +2 · `tests/test_agent_query_answer.py` +1 · 새 `tests/test_agent_fix037.py` · 새 `evaluation/recognition/` · 새 `reports/recognition-probe.md`) · Refs: FIX-037 P5-loop P5b-query-turn D14 D16 S3.4 원칙1 원칙7 원칙8

**최종 결과(3차 수정 뒤 재검토, 맨 아래 8절): 통과 — [필수] 0건(R-37-1·2·3 닫힘), [권고]·이관 5건.**

아래 1~7절은 1차 수정 시점의 리뷰 기록이다(그때 결과: 보류 — [필수] 3건(R-37-1·R-37-2·R-37-3), [권고] 6건). 지우지 않고 남긴다.

FIX-037 이 스스로 정한 과교정 판정 조건(실제 질문 query 일치율, 없는 것 "기록이 없어요")은 after 증거에서 **둘 다 유지**됐고(30/30, 6/6), 고치려던 증상 (a)·(c)·(d)는 표본에서 크게 좋아졌다. 그러나 같은 after 증거가 이 수정이 **새로 만든 퇴행 두 가지**를 보여 준다 — 사건만 있는 발화에 지어낸 인물 사실이 붙고(4/70 → 43/70), 앞으로의 약속이 일정이 아니라 사건으로 제안된다(s01 `add_schedule` 5/5 → 0/5). 그리고 거부 알림 문장은 확인 질문이 떠 있는 턴에도 붙어 서로 어긋나는 답이 나온다. 코드·테스트·lint 는 깨끗하다(전체 pytest 2634 passed).

## 1. 본 것

- `docs/wiki/fixes/FIX-037.md` 증상·원인·수정안 0~3·회귀 테스트와 판정·하지 않는 것·기획서 정합성·`계획 점검: 통과`.
- `git diff HEAD -- app/agent/propose.py app/agent/respond.py app/agent/loop.py tests/test_agent_query_answer.py` 전체, `tests/test_agent_fix037.py`(10 테스트) 전체.
- `evaluation/recognition/heldout.jsonl`(32건) · `query_answer.json` · `probe.py`(438줄) 전체, `reports/recognition-probe.md`(before 만 적혀 있음).
- `app/agent/gate.py:180-346`(거부 사유·`_classify_args`·`check`), `app/agent/loop.py:1087-1187`(`run_turn`), `app/agent/respond.py:76-170`(`build_reply`·`_QUERY_SYSTEM_PROMPT`), `build_reply` 호출 지점 3곳(`loop.py:1164·1566·1956`).
- 카드: `decisions/D16-query-turn.md` 결정 1·5·6·8, `specs/S3.4-ask-user-protocol.md`, `packages/P9b-auth/u8-demo-script.md`(발화 13개 + 미커밋 "시연 계획" 절), `verification.md` "변이 시험 방법", `.claude/scripts/fix_guard_check.py`(`검증:` 줄 규칙).
- 구현자·eval 증거: `fixes/evidence/20261117-2133-fix037-probe-before-{recognition,answer}.txt`, `…-2138-…-before-summary.txt`, `…-2140-fix037-full-checks.txt`, `…-2141-fix037-mypy-before-after.txt`, `…-2142-fix037-mutations.txt`(M1~M13), 리뷰 중에 생긴 `…-2144-fix037-probe-after-{recognition,answer,server-check}.txt`.
- `bash .claude/scripts/gitlog.sh FIX-037 D16 P5b-query-turn`: FIX-037 태그 커밋 0(미커밋), D16·P5b 는 `f67d8e4` 로 완료.
- `.env` 는 읽지 않았다. 로컬 서버(:8000)에 요청을 보내지 않았고 `probe.py run` 을 돌리지 않았다. after 측정이 `DONE` 으로 끝난 뒤, after 증거의 `trace_ids` 로 로컬 DB `agent_traces` 를 **읽기 전용 SELECT** 한 번 했다(`probe.read_traces` 와 같은 방식).

## 2. 내가 직접 실행한 것 (전부 `save_evidence.py` 통로, 저장소 무수정)

| # | 무엇 | 결과 | 증거 (`docs/wiki/fixes/evidence/`) |
|---|---|---|---|
| 1 | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q` 전체 | **2634 passed**, 실패 0, skip 0, exit 0 | `20261117-2147-verifier-FIX-037-checks.txt` |
| 2 | 새 테스트 파일만 `-v` | 10 passed | 같은 파일 |
| 3 | `.venv/bin/python -m ruff check app tests evaluation` | All checks passed, exit 0 | 같은 파일 |
| 4 | `mypy app` — 작업 트리 vs `git archive HEAD app pyproject.toml` 사본 | 39 errors / 39 errors, 줄 번호 뺀 diff **차이 없음**. 변경 파일의 오류 2줄(`loop.py:890`·`:1162`)은 HEAD 에도 있다 | 같은 파일 |
| 5 | `probe.py summarize` 를 before 증거 2개로 재실행 | 구현자 집계 파일과 **전체 줄 동일**. `probe.py` 를 쓰지 않은 독립 재계산도 같은 수치(의도 139/160, query 30/30, 유형 48/90, conflict 2/15, enum 이탈 0/62, bad_args 4, 근황 10/12, 없는 것 6/6) | `20261117-2148-verifier-FIX-037-summarize.txt` |
| 6 | 원칙 8 대조(프롬프트 ↔ 시연 13발화 ↔ 표본 42발화) | 아래 4절 | `20261117-2148-verifier-FIX-037-principle8.txt` |
| 7 | after 증거 분석(before/after 과제안·누락, 일정 발화, trace 의 실제 제안 인자) | 아래 3절 | `20261117-2154-verifier-FIX-037-after-detail.txt` |
| 8 | 대조군 + 관찰 시나리오 3개 + 변이 13종(스크래치패드 사본, `.env*`·`.git`·`docs`·`web` 제외, 변이마다 **전체 pytest**) | 아래 5절 | `20261117-2149-verifier-FIX-037-mutations.txt` |

after 증거로 내가 다시 낸 수치(`summarize`, 같은 표본 32건 × 5회 · 조회 답 6문형 × 3회):

| 지표 | before | after |
|---|---|---|
| 의도 일치(전체) | 139/160 | 160/160 |
| └ **실제 질문 query** (과교정 판정 기준) | 30/30 | **30/30** |
| `raw.intent` 누락(→ record 로 간주) | 6/160 | **35/160** |
| 유형 일치 | 48/90 | 79/90 |
| └ conflict 라벨 | 2/15 | 15/15 |
| enum 이탈 | 0/62 | 0/92 |
| `bad_args` 거부 | 4 | 0 |
| **도구 집합 정확 일치** | 126/160 (78.8%) | **105/160 (65.6%)** |
| 기대 도구 포함(기록 라벨) | 97/130 | 120/130 |
| 끝까지 통과(기록 라벨) | 91/130 | 120/130 |
| `query_turn_no_write` 로 버려진 기록 턴 | 10/130 | 0/130 |
| 근황 질문 답변율 | 10/12 | 12/12 |
| **없는 것 → "기록이 없어요"** (과교정 판정 기준) | 6/6 | **6/6** |

## 3. [필수] 소견

### R-37-1 · 사건만 있는 발화에 지어낸 인물 사실이 붙는다 (4/70 → 43/70)

- 근거(`…-2154-verifier-FIX-037-after-detail.txt` 1·3·4절): 사건 묶음 14발화 × 5회에서 기대에 없는 `update_person` 제안이 before **4/70** → after **43/70**. 전부 게이트를 통과했다(`accepted`).
- 실제 제안 값(after rep 0·1 의 `loop_extract` trace): e02 `{"key":"workplace","value":"모르는 회사 이름"}` · e02 rep1 `workplace=""` · e05 `workplace="기타"` · e04 `job="선배"` · e13 `job="발표자"` · e11 `life_event="어릴 적 이야기 공유"` · e12 `life_event="이사"`. 발화에 없는 값이거나 사실이 아닌 것을 사실 칸에 넣는다.
- 추정 원인(가설): 새 문장 `propose.py` "record 일 때 한 발화에 사건(add_event)과 인물 사실(update_person 의 facts)이 함께 들어 있으면 둘 다 제안하라". 확인된 것은 전후 수치 차이뿐이다.
- 왜 필수인가: 이 제안은 확인 칩 뒤(이미 아는 인물이면 자동 연결 뒤 바로) `person_facts` 에 저장되고, 조회 답과 브리핑은 그것을 "기록된 사실"로 다시 말한다. 원칙 7 · D16 결정 8(조회 답은 **기록된 사실의 재진술**)의 바탕이 오염된다. FIX-037 수정안 1 이 노린 것은 (g) "한쪽만 제안"이었지 사실 지어내기가 아니다.
- 완료 판정: 같은 표본·같은 횟수로 다시 재서 `event:update_person` 기대 밖 제안 수와 값(빈 문자열·"모르는…"·"기타" 류)을 보고서에 적고, before 수준으로 돌아왔는지 본다. mixed 묶음 두 도구 포함(10/10)이 같이 떨어지면 그것도 그대로 적는다.

### R-37-2 · 앞으로의 약속이 일정이 아니라 사건으로 제안된다 (s01 `add_schedule` 5/5 → 0/5)

- 근거(같은 증거 2·4절): s01 "다음 주 화요일 저녁 7시에 홍지훈이랑 저녁 약속 있어" — before `add_schedule` 5/5, after `add_event(type="meal", occurred_at="2026-11-22T19:00:00+09:00")` **5/5**, `add_schedule` 0/5. s02("면담이 잡혔어")는 5/5 유지.
- 함께 본 것: f07 `add_event(type="other", occurred_at="2027-03-01…")`(미래 날짜 사건) 5/5, f04(습관) `add_event(other)` 2/5, e14(엘리베이터) `conflict` 1/5.
- 추정 원인(가설): 새 유형 설명에 일정 낱말이 들어갔다 — `EVENT_TYPE_DESCRIPTIONS["meeting"]` "만남·회의·**약속**처럼 함께 모인 일", `meal` "식사·술·커피처럼…". FIX-037 이전 프롬프트에는 "약속"이 없었다(`git show HEAD:app/agent/propose.py` 에서 0건).
- 왜 필수인가: 일정이 저장되지 않으면 브리핑이 만들어지지 않는다(제품의 끝단). 미래 시각의 `meal`·`meeting` 사건은 D14 반복 패턴 횟수에도 들어간다. 시연 발화 13번("내일 오후 4시에 … 분기 리뷰 회의 일정 있어")이 같은 꼴이라 재배포 뒤 시연 계정 준비가 이 지점에서 막힐 수 있다 — 13번을 직접 넣어 보지는 않았다(4절 미확인).
- 완료 판정: 같은 표본 재측정에서 schedule 묶음 `add_schedule` 포함 10/10(before 수준), `schedule:add_event` 0.

**R-37-1·2 공통 — 보고서**: `reports/recognition-probe.md` 는 아직 before 만 있다. after 를 적을 때 위 두 퇴행(도구 집합 정확 일치 78.8% → 65.6%, `raw.intent` 누락 6 → 35 포함)을 좋아진 수치와 **나란히** 적는다(원칙 8 — 미달도 결과). 프롬프트를 다시 고치면 표본은 이미 결과를 본 표본이 된다 — 표본·라벨은 그대로 두고, "after 를 보고 프롬프트를 한 번 더 고쳤다"를 보고서에 적는다.

### R-37-3 · 거부 알림이 확인 질문이 떠 있는 턴에도 붙는다

- 근거(`…-2149-verifier-FIX-037-mutations.txt` 관찰 시나리오, 현재 작업 트리 코드 그대로):
  - S1 `create_person`(aliases 없음 → `bad_args`) + `update_person`(통과) → 답 `'말씀하신 내용을 기록하지 못했어요. 다시 한 번 말씀해 주시겠어요?\n"오유나"을(를) 새 인물로 기억해둘까요?'`, `stop_reason=ask_user`.
  - S2 `add_event(type="health")`(거부) + `add_event(type="other")`(통과) → 같은 모양.
- 이 꼴은 가상이 아니다: before 증거 f05 는 5회 중 3회가 "`create_person` `bad_args` + `update_person` 통과 + `new_person` 질문"이었다(`…-2148-verifier-FIX-037-summarize.txt` "bad_args 거부가 있던 before 시도").
- 무엇이 틀렸나: 통과한 제안이 사용자의 칩 답을 기다리는 중인데 "기록하지 못했어요, 다시 말씀해 주세요"라고 말한다. 칩을 누르면 기록된다 — 문장이 사실과 다르다. 미커밋 `u8-demo-script.md` 준비 순서 4 는 "'기록하지 못했어요'가 나오면 같은 내용을 한 번 더 보낸다"고 안내하므로, 사용자는 질문을 둔 채 같은 말을 다시 보내게 된다(대기 질문이 겹친다, S3.4 "답 없이 다음 발화가 오면 대기 질문 유지").
- 덧붙여 `create_person` 은 게이트에서 힌트 전용(`BUCKET_HINT_ONLY`)이라 그 거부로 잃는 기록이 없다. FIX-037 수정안 3 의 "게이트가 **기록 제안**을 `bad_args` 로 버린 경우"에 `create_person` 이 드는지는 계획이 정하지 않았다.
- 테스트 공백: 변이 V8(`elif rejected_bad_args and pending_question is None`)·V9(`add_event` 의 `bad_args` 만 알림)가 전체 pytest 에서 살아남는다 — 어느 쪽이 계약인지 테스트가 고정하지 않는다.
- 완료 판정: 대기 질문이 있는 턴·`create_person` 만 거부된 턴의 문장을 계획(FIX-037 수정안 3)에 한 줄로 정하고, 그 값을 단언하는 테스트를 더한다. S1·S2 를 다시 돌려 답이 어긋나지 않는지 본다.

## 4. 따진 항목별 판정

**① 범위** — 통과. diff 는 `propose.py` 프롬프트 문구·상수 1개, `respond.py` 문장 1개·키워드 인자 1개·프롬프트 1문장, `loop.py` import 1줄·인자 1줄뿐이다. `gate.py`·`app/er/`·`app/settings.py`·`alembic/`·스키마 변경 0(`git status --short app tests`). "둘이 섞이면 query 다."는 그대로 있고 테스트가 단언한다(D16 결정 6). `build_reply(rejected_bad_args=False)` 기본값 덕에 재개 경로 두 곳(`loop.py:1566·1956`)은 옛 문장 그대로다(관찰 S3, 변이 V13 이 `tests/test_agent_loop.py` 에서도 잡힘). 조회 턴은 `build_reply` 전에 갈라진다(`loop.py:1128`). `loop.py` 의 `REASON_BAD_ARGS` import 는 이미 `gate.check` 를 가져오던 모듈이라 순환이 없다. 형식이 틀린 유형을 `other` 로 고치는 보정은 없다(계획대로).

**② 프롬프트와 원칙 7 · D16** — 조회 답 쪽은 통과, 인식 쪽은 R-37-1·2.
- 근황 문장: "자료의 최근 사건·일정을 날짜와 함께 그대로 재진술하라"는 재진술 범위 안이고, "평가·조언·감정 대화는 하지 않는다"·"자료에 없는 것은 '기록이 없어요'"·"위로·조언·감정 표현을 쓰지 마라"가 그대로 남아 있다(정확 일치 테스트). after 답 18개에 평가·조언·감정 표현은 보이지 않았고(전부 날짜 + 사건 재진술), 없는 것 6/6 "기록이 없어요". **한계**: 표본 카드는 사건이 3건 있는 카드 하나다. "사실만 있고 사건·일정이 0건인 카드에 '요즘 어때?'"는 재지 않았다 — 그때 "기록이 없어요"가 나오는지, 사실을 근황처럼 말하는지 모른다(권고 R-37-8).
- 의도 문장: 실제 질문 6문형 30/30 이 query 로 유지됐고 `raw_intent` 도 30/30 `query` 였다. 질문이 record 로 새어 기록 제안이 나온 시도 0. 다만 `raw.intent` 누락이 6 → 35 로 늘었다(전부 기록 라벨 발화, 파서 기본값 record 로 맞음). 질문에서 intent 가 빠지면 기본값 때문에 record 가 되므로, 표본 6문형 밖의 질문 꼴은 보장이 없다(권고 R-37-5).
- 원칙 1: ER·임계치·자동 병합 경로는 건드리지 않았다. 다만 R-37-1 의 지어낸 사실은 자동 연결된 인물에게 확인 없이 저장된다 — 오병합은 아니지만 같은 "확인 없는 잘못된 기록" 쪽 위험이다.

**③ 원칙 8** — 통과(권고 2건).
- 프롬프트(`propose.system`·`propose.user`·`query.system`) 안에 시연 13발화·표본 42발화의 **원문 통째 일치 0건**. 6글자 조각 공유는 1건 — 표본 f06 "…주말에만 연락이 돼" ↔ 프롬프트 "주말에만 연락됨". 이 문구는 FIX-017 의 `FACT_KEY_DESCRIPTIONS["contact_note"]` 예시로 HEAD 에 이미 있던 것이라 전후 비교에는 같은 영향이다(권고 R-37-6).
- 표본에 시연 인물 이름(김민수·이서연·박준호·엄마) 0건, 통째 일치 0건. 문장 틀이 같은 것 2건(f01 "…는 걸 좋아하셔" ↔ 시연 3, f07 "…한다고 하더라" ↔ 시연 7) — 같은 현상을 다른 문장으로 잰 것이다.
- 유형 설명의 갈등 낱말 "언쟁·지적받음·부딪힘"은 시연 1·2·4 의 낱말이고 표본에는 없다(표본 갈등은 "싸웠어"·"언성이 높아졌어"·"말다툼"). 표본 conflict 15/15 는 시연 낱말에 기대지 않은 결과다. 반대로 시연 계정 결과는 이 낱말에 맞춰진 프롬프트의 결과이므로 성능 수치로 쓰면 안 된다(권고 R-37-7).
- 라벨: `heldout.jsonl` mtime 21:31:48, `query_answer.json` 21:33:36 — before 측정 시작 21:33:57 **이전**이고 그 뒤 수정 흔적이 없다. TRIAL 160줄 = 32 id × 5회, id 집합이 표본과 같다. 보고서 수치는 5번 재실행·독립 재계산과 전부 맞는다.
- 확인하지 못한 것: 파일이 전부 untracked 라 git diff 로 이력을 볼 수 없다. `probe.py` mtime 은 21:34:58 로 before 실행이 도는 중에 한 번 바뀌었다 — 무엇이 바뀌었는지는 모른다(`summarize` 재현성은 5번으로 확인).

**④ 테스트** — 전체 2634 passed, ruff·mypy 새 오류 0. 변이는 5절.

**⑤ 보안** — 통과. 새 파일에 키·비밀 문자열 0(6번 증거 8절; 유일한 일치는 `probe.py:426` 의 배포 주소 거부 조건). 시험 계정 자격은 `--secrets-dir`(저장소 안이면 거부)에만 쓰고 출력하지 않는다. `probe.py` 는 로컬 주소만 받고 DB 는 SELECT 1개만 한다. 삭제·외부 전송 없음. 스크래치패드의 자격 파일은 열지 않았다. 시험 계정 2개(`fx37r…`·`fx37a…`)와 after 인식 계정은 로컬 DB 에 남아 있다(지우지 않았다).

## 5. 변이 시험 (내 것 13종, 변이마다 전체 pytest)

사본에는 `.env.example`·`.git` 이 없어 대조군이 `2 failed`(`test_deploy_files`·`test_infra_files`) 다. 그래서 **"실패 2건"은 살아남은 것**이고 3건 이상이 잡힌 것이다(증거 파일의 "잡힘" 표시는 이 기준선을 빼지 않은 것이라 실패 건수로 읽는다).

| ID | 변이 | 결과 |
|---|---|---|
| 대조군 | 변이 없음 | 2 failed(사본 환경 탓), 2632 passed |
| V1 | 모든 거부에 알림 | 잡힘 — `test_run_turn_non_bad_args_rejection_keeps_nothing_stored_sentence` |
| V2 | 저장된 것이 있어도 거부 문장 | 잡힘 — `test_build_reply_bad_args_flag_…` |
| V3 | 유형 설명에서 `other` 삭제 | 잡힘 — `test_event_type_descriptions_keys_equal_event_types_exactly` |
| V4 | 근황 문장 삭제 | 잡힘 — `test_prompt_system_exact_sentences` |
| **V5** | `not_callable_by_llm` 거부(기록 턴의 `search_person`)에도 알림 | **살아남음** |
| **V6** | `person_id_from_llm`·`limit`·`needs_confirmation` 거부에도 알림 | **살아남음** |
| **V7** | `praise` 설명을 `favor` 설명으로 바꿈 | **살아남음** |
| **V8** | 대기 질문이 있으면 거부 문장 안 씀 | **살아남음** (R-37-3) |
| **V9** | `add_event` 의 `bad_args` 만 알림 | **살아남음** (R-37-3) |
| **V10** | 의도 문장에서 "이미 기록된 인물 정보를 묻는 것" 조건 삭제 | **살아남음** |
| V11 | 근황 문장을 "기록이 없어요" 뒤로 옮김 | 잡힘 — 정확 일치 테스트 |
| V12 | 유형 우선순위 문장 삭제 | 잡힘 |
| V13 | `build_reply` 기본값 True | 잡힘 — 새 테스트 + `tests/test_agent_loop.py` |

구현자 M1~M13 은 전부 잡힌 것으로 적혀 있고 내 V1~V4 가 같은 결론이다. V5 는 가벼운 공백이 아니다 — before 증거에서 f07 은 5/5 가 "`search_person` 만 제안"이었으므로, 누가 조건을 넓히면 그런 턴마다 "기록하지 못했어요"가 나가는데 테스트는 `unknown_tool` 하나만 본다.

## 6. [권고] 소견

- **R-37-4** 거부 사유 부정 테스트를 `unknown_tool` 하나에서 `not_callable_by_llm`·`person_id_from_llm`·`needs_confirmation`·`limit` 로 넓힌다(V5·V6). `update_person`·`add_schedule` 의 `bad_args` 도 알림이 나오는지 값으로 고정한다(V9).
- **R-37-5** 유형 설명 7줄과 의도 문장을 정확 일치로 고정한다(V7·V10). 지금은 키와 일부 조각만 본다. `raw.intent` 누락 6 → 35 를 보고서에 적고, 질문에서 intent 가 빠질 때 record 가 되는 기본값을 P10 표본 항목으로 넘긴다.
- **R-37-6** 표본 f06 이 기존 프롬프트 예시("주말에만 연락됨")와 겹친다는 것을 보고서 한계 절에 적는다(표본은 고치지 않는다).
- **R-37-7** 유형 설명의 갈등 낱말이 시연 발화 낱말과 같다는 것, 그래서 시연 계정 결과는 평가 수치가 아니라는 것을 보고서나 FIX 결과 절에 한 줄 적는다.
- **R-37-8** 조회 답 표본의 한계(사건이 있는 카드 1장, 문형마다 3회)를 보고서에 적는다. 사건·일정 0건 카드의 근황 질문은 재지 않았다.
- **R-37-9** `probe.py:426` 의 주소 검사는 접두 일치라 `http://localhost.example.com` 같은 주소가 통과한다. 호스트를 파싱해 `localhost`·`127.0.0.1` 과 정확히 비교한다. 구현자 증거 `…-2140-fix037-full-checks.txt` 의 "git stash 기준선" 표기는 스크립트에 stash 명령이 없어 실제와 다르다 — 표기를 고친다.

## 7. 확인하지 못한 것

- R-37-1·2 의 원인 문장(가설). 본 것은 전후 수치와 trace 값이다.
- 시연 13발화를 수정 뒤 코드에 넣은 결과(서버 요청 금지 — 특히 13번 일정 발화).
- 지어낸 사실이 실제로 `person_facts` 에 저장된 행(프로브는 칩에 답하지 않아 저장 0). 게이트 통과까지만 확인했다.
- 같은 명령 재실행의 변동 폭(before·after 각 1회 측정). 다만 s01 5/5 → 0/5, 43/70 은 변동으로 보기 어렵다.
- `probe.py` 가 before 실행 도중 바뀐 내용.
- 배포 서버 상태(호출하지 않았다).

---

## 8. 재검토 — 3차 수정 뒤 (2026-11-17 22:30, 같은 검토자·새 실행)

검토자: verifier (fable) · 기준 HEAD `9fce41d` (dev2) + 미커밋 작업 트리(`propose.py` +39/-3 · `respond.py` +6 · `loop.py` +2 · `tests/test_agent_query_answer.py` +1 · `tests/test_agent_fix037.py` 27 테스트). `web/` 의 FIX-038 변경은 보지 않았다.

**결과: 통과 — [필수] 0건. R-37-1·2·3 닫힘, 3차 판정 5조건 전부 충족, 과교정 조건 유지. 남은 것 5건은 [권고]·이관.**

### 8.1 본 것 · 직접 실행한 것

- `FIX-037.md` "2차 수정"(R1~R4)·"3차 수정"(R5, 3차 판정 5조건), `git diff -- app/agent/ tests/` 전체, `tests/test_agent_fix037.py` 전체, `reports/recognition-probe.md`(네 회차).
- 서버가 최종 코드를 읽었는가: `…-2223-fix037-probe-after4-server-check.txt` — `propose.py` mtime 22:19:04, 워커 시작 22:23:40, 측정 시작 22:23:50. 순서가 맞다.
- 표본 무변경: `heldout.jsonl` mtime 21:31:48 · `query_answer.json` 21:33:36(둘 다 before 측정 전 그대로), 내가 21:55 에 뜬 사본과 `diff` 동일. `probe.py` 는 그 사본 대비 3곳만 다르다 — `--label` 허용값에 `after3`·`after4`, 주소 검사를 호스트 정확 일치로(R-37-9 반영). 집계·수집 코드는 같다.

| # | 무엇 | 결과 | 증거 (`docs/wiki/fixes/evidence/`) |
|---|---|---|---|
| 1 | 전체 pytest(`POSTGRES_PORT=5433`) · 새 테스트 `-v` · `ruff check app tests evaluation` · `mypy app`(작업 트리 vs HEAD 사본) | **2651 passed**(실패 0, skip 0) · 27 passed · All checks passed · 39/39 줄 번호 뺀 diff 차이 없음 | `20261117-2231-verifier-FIX-037-r3-checks.txt` |
| 2 | `probe.py summarize` 를 before + after4 원자료로 재실행, 구현자 집계 파일의 after4 구역과 대조 | 72줄 **차이 없음** | `20261117-2230-verifier-FIX-037-r3-summarize.txt` |
| 3 | `summarize` 를 쓰지 않은 독립 계산(네 회차 TRIAL·ANSWER 줄) + after4 발화별 도구·유형 + 남은 어긋남 12건의 trace 값(로컬 DB 읽기 전용 SELECT) | 아래 8.2 | `20261117-2230-verifier-FIX-037-r3-detail.txt` |
| 4 | 원칙 8 대조 재실행(최종 프롬프트 ↔ 시연 13발화 ↔ 표본 42발화) | 통째 일치 0, 시연 인물 이름 0 | `20261117-2232-verifier-FIX-037-r3-principle8.txt` |
| 5 | 변이 13종(스크래치패드 사본, 환경 파일·`.git`·`docs`·`web` 제외) | 대조군 339 passed, **13종 전부 잡힘, 살아남은 변이 없음** | `20261117-2232-verifier-FIX-037-r3-mutations.txt` |

서버(:8000)에는 요청하지 않았고 `probe.py run` 도 돌리지 않았다.

### 8.2 [필수] 세 건이 닫혔는가 (원자료에서 내가 센 값)

| 소견 | before | after(1차) | after3(2차) | **after4(3차)** | 판정 |
|---|---|---|---|---|---|
| R-37-1 기대 밖 `update_person`(전부 사건 묶음) | 4/70 | 43/70 | 23/70 | **0/70** | 닫힘 — 수정 전보다도 낮다. 사건 14발화 70회 모두 `add_event` 하나만 제안 |
| R-37-2 일정 묶음 `add_schedule` 포함 / 일정에 `add_event` | 10/10 · 0 | 5/10 · 5 | 10/10 · 0 | **10/10 · 0** | 닫힘 — s01 `add_schedule` 5/5 |
| R-37-3 대기 질문이 있는 턴의 거부 문장 | — | 붙음(S1·S2) | — | 조건 `and pending_question is None` | 닫힘 — 테스트 `test_build_reply_r4_…` 가 값으로 고정, 변이 W1 이 잡힘. `create_person` 만 거부된 턴은 "알림을 낸다"로 정해 테스트가 고정(W3) |

덧붙여 1차 때 본 것들: `raw.intent` 누락 35 → **2/160**, 사실 발화(f 묶음)에 `add_event` 7 → **0/40**, conflict 아닌 발화에 `conflict` 1 → **0/145**, 도구 집합 정확 일치 105 → **148/160**(before 126).

### 8.3 3차 판정 5조건

| # | 조건 | 기준 | after4 | 결과 |
|---|---|---|---|---|
| ① | 실제 질문 query 일치 · 없는 것 "기록이 없어요" 유지 | 30/30 · 6/6 | **30/30 · 6/6** | 충족 |
| ② | 일정 `add_schedule` 10/10 유지 | 10/10 | **10/10** | 충족 |
| ③ | `add_event` 제안 없음이 22/90 보다 줄고, e10 이 3/5 보다 낮지 않다 | < 22/90 · ≥ 3/5 | **10/90 · 5/5** | 충족 |
| ④ | 기대 밖 `update_person` 이 23 보다 늘지 않는다 | ≤ 23 | **0** | 충족 |
| ⑤ | conflict · 끝까지 기록 · mixed 가 수정 전보다 낮지 않다 | ≥ 2/15 · ≥ 91/130 · ≥ 5/10 | **15/15 · 120/130 · 10/10** | 충족 |

조회 답 18개(after4)는 근황 12/12 가 날짜와 함께 카드 사건을 재진술했고 평가·조언·감정 표현은 없었다(원자료를 읽어 확인, 자동 판정 아님). 없는 것 6/6 "기록이 없어요."

### 8.4 원칙 8 · 범위 · 테스트

- 프롬프트 안 시연·표본 발화 원문 0건, 표본에 시연 인물 이름 0건(1차와 같음). 표본·라벨은 바뀌지 않았다.
- 보고서 5절 ⓐ 가 "after 결과를 보고 프롬프트를 세 번 고쳤다 — after4 수치는 홀드아웃 성능이 아니라 같은 표본에서 회귀가 풀렸는지의 확인"이라고 적고 있다. 3차 문구의 "털어놓았다"는 표본 e10("털어놨어")과 같은 낱말이므로 이 단서가 꼭 필요하고, 실제로 적혀 있다. 미달 항목(8.5)도 보고서 4절에 그대로 있다.
- 범위: `gate.py`·`app/er/`·임계치·스키마·`alembic/` 변경 0. 함수 스키마의 `required` 에 `intent` 는 넣지 않았다(문구만). "둘이 섞이면 query 다." 유지(W11 이 두 테스트에서 잡힘). 조회 답 프롬프트는 1차와 같다.
- 테스트: 1차에 살아남던 V5~V10 에 해당하는 변이(W1·W2·W3·W10·W13)가 이번에는 전부 잡힌다. 거부 사유 6종 전부와 도구 4종을 매개변수 테스트가 값으로 고정한다.

### 8.5 남은 것 — 막지 않는 이유와 함께

이번이 마지막 재측정이다(FIX-037 "이 뒤에도 남는 문제는 더 고치지 않고 그대로 적어 사용자에게 보고"). 아래는 [필수]로 막지 않았다.

| ID | 무엇 | 수치 | 막지 않는 이유 | 처리 |
|---|---|---|---|---|
| R-37-10 | 질문 q06 "…마지막으로 만난 게 언제였더라?" 에 `add_event(meeting)` 제안이 섞인다. trace 값은 `content="마지막으로 만난 날"` 같은 지어낸 사건 | 2/30 (before·after·after3 는 0) | intent 는 5/5 query 이고 게이트가 `query_turn_no_write` 로 **코드로** 버린다(D16 결정 1). `accepted=[]`, 저장 0, 답 정상. 프롬프트가 아니라 게이트가 막는 자리라 기록 오염이 없다 | [권고]·이관 — P10 표본. 질문에서 `intent` 가 빠지면 기본값 record 로 이 제안이 기록이 되므로(이번 표본 질문에서는 누락 0), "과거 사건을 묻는 질문" 꼴을 P10 표본에 넣는다 |
| R-37-11 | 근황 전언 f07·f08 에 `personal_share` 사건이 없다(`update_person` 만 5/5) | 0/10 | 수정 전에도 0/10 이라 퇴행이 아니다. 내용은 `life_event` 사실("결혼 예정"·"이사")로 기록된다. 라벨(P1 결정 J(c))대로 사건도 남길지는 결정 거리다 | 이관 — 사용자 결정 |
| R-37-12 | after4 는 이미 결과를 본 표본의 수치다 | — | 보고서에 밝혀져 있고 표본·라벨은 그대로다. FIX 의 판정은 "회귀가 풀렸는가"이지 일반화 성능 주장이 아니다 | 이관 — 새 표본은 P10. 이 수치를 성능으로 인용하지 않는다 |
| R-37-13 | 시연 13발화를 최종 코드에 넣은 결과, 사건·일정 0건 카드의 근황 질문, 6문형 밖의 질문 꼴은 재지 않았다. 회차마다 1회 측정이다 | — | 측정 밖이지 결함이 확인된 것이 아니다. 시연 준비 순서(u8-demo-script)가 발화마다 답을 확인하게 돼 있다 | [권고] — 재배포 뒤 시연 계정 준비 때 13번 일정·12번 근황 답을 눈으로 확인 |
| R-37-14 | 지어낸 사실 값을 막는 것은 프롬프트 문구뿐이다(게이트는 빈 문자열·"기타" 값을 거르지 않는다) | after4 0건 | 이번 표본에서 재발 0. 게이트 규칙 추가는 FIX-037 범위 밖(사용자 결정 사항으로 남긴 것과 같은 종류) | [권고] — 유형 `other` 보정·D16 결정 6 과 함께 사용자에게 묻는 목록에 넣는다 |

### 8.6 확인하지 못한 것

- 일반화(새 표본에서의 수치), 시연 발화 결과, 배포 서버 상태.
- 재실행 변동 폭(after4 1회). R-37-10 의 2/30 이 변동인지 3차 문구 탓인지(보고서도 가설로 적음).
- 표본·프로브 파일의 git 이력(untracked — mtime 과 내 사본 대조로만 확인).
