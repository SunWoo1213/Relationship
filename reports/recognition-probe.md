# 인식·조회 답 프로브 — FIX-037 수정 전(before) · 1차(after) · 2차(after3) · 3차(after4)

Refs: FIX-037 P5-loop P5b-query-turn D14 D16 S3.4 원칙7 원칙8

| | before | after (1차) | after3 (2차) | after4 (3차) |
|---|---|---|---|---|
| 코드 | `9fce41d` (dev2, `app/` 무변경) | `9fce41d` + 미커밋 1차 수정(`propose.py`·`respond.py`·`loop.py`) | + 미커밋 2차(R1~R4) | + 미커밋 3차(R5, `propose.py` 한 구간). 커밋 뒤 해시를 여기에 적는다 |
| 서버 재로드 | — | 워커 21:40:29 > mtime 21:39:51 | 워커 22:11:49 > mtime 22:04:26 | 워커 22:23:40 > `propose.py` mtime 22:19:04 |
| 측정 | 11-17 21:33~21:38 | 1회차 21:44~21:50 · 2회차(인식만) 21:50~21:56 | 22:12~22:16, 1회 | 22:23~22:28, 1회 |

- 로컬 `:8000` `--reload`, alembic 0004, 모델 `gpt-4o-mini-2024-07-18`(`er_resolve` trace 의 `llm.model`). 배포 서버는 부르지 않았다.
- 표본: `evaluation/recognition/heldout.jsonl`(32건) · `evaluation/recognition/query_answer.json`. 표본·라벨·반복 횟수·집계는 before 측정 전에 고정했고 이후 바꾸지 않았다.
- `probe.py` 변경(집계 무변경): `--label` 허용값에 `after3`·`after4` 추가 · R-37-9 주소 검사를 호스트 정확 일치(`http` + `localhost`/`127.0.0.1`)로(after3 전, 거부 주소 5개 확인 `…-2212-fix037-probe-addr-check.txt`).
- 원수치(증거, `docs/wiki/fixes/evidence/`):
  - before: `20261117-2133-fix037-probe-before-recognition.txt` · `…-2133-fix037-probe-before-answer.txt`
  - after: `20261117-2144-fix037-probe-after-recognition.txt` · `…-2144-fix037-probe-after-answer.txt` · 2회차 `…-2150-fix037-probe-after2-recognition.txt`
  - after3: `20261117-2212-fix037-probe-after3-recognition.txt` · `…-2212-fix037-probe-after3-answer.txt`
  - after4: `20261117-2223-fix037-probe-after4-recognition.txt` · `…-2223-fix037-probe-after4-answer.txt` · 서버 확인 `…-2223-fix037-probe-after4-server-check.txt`
  - 집계: `20261117-2228-fix037-probe-after4-summary.txt`(네 회차 `summarize`) · `…-2156-fix037-probe-after2-summary.txt` · 보조 `…-2228-fix037-probe-after4-extra.txt`
- 재현: 수치는 전부 `summarize` 가 증거 파일의 `TRIAL`/`ANSWER` 줄만 읽어 다시 낸다. LLM 은 결정적이지 않아 다시 돌리면 흔들린다(after 두 회차 차이 최대 4/130, 3절).

```
.venv/bin/python evaluation/recognition/probe.py run --label <before|after|after3|after4> --part recognition --secrets-dir <스크래치패드>/fix037[/afterN]
.venv/bin/python evaluation/recognition/probe.py run --label <…> --part answer --secrets-dir <스크래치패드>/fix037
.venv/bin/python evaluation/recognition/probe.py summarize <증거 파일 …>
```

## 1. 표본

| 묶음 | 건수 | 라벨 intent | 기대 도구 | 기대 type |
|---|---|---|---|---|
| fact (평서 사실·근황) | 8 | record | `update_person` (근황 2건 f07·f08 은 + `add_event`) | f07·f08 만 `personal_share` |
| event | 14 | record | `add_event` | conflict 3(회의·식사 자리 겹침 2 포함) · praise 2 · meal 2 · meeting 2 · personal_share 2 · favor 2 · other 1 |
| query (실제 질문) | 6 | query | 없음 | — |
| mixed (사건+사실) | 2 | record | `add_event`+`update_person` | meal · favor |
| schedule | 2 | record | `add_schedule` | — |

시연 발화 13개의 문장·인물 이름(김민수·이서연·박준호·엄마)은 쓰지 않았다. 인식 계정은 회차마다 빈 새 계정, 칩에는 답하지 않는다(저장 0).
조회 답 카드(계정 `fx37a1117213357`, 인물 `배성훈`, 사실 0, 사건 3건: 11/14 `meal` · 11/15 `other` "말다툼" · 11/17 `praise`). 네 회차의 `CARD` 줄은 라벨 값만 빼면 md5 `8c1c99e8…` 로 같다.

## 2. 수치

### 3차 판정 (FIX-037 "3차 수정" 절)

| 조건 | before | after | after3 | after4 | 결과 |
|---|---|---|---|---|---|
| ① 실제 질문 query 일치율 | 30/30 | 30/30 | 30/30 | 30/30 | **충족** |
| ① 없는 것 → "기록이 없어요"(엄격) | 6/6 | 6/6 | 6/6 | 6/6 | **충족** |
| ② 일정 `add_schedule` (s01+s02) | 10/10 | 5/10 | 10/10 | 10/10 | **충족** |
| ③ `add_event` 제안 없음 (기대 type 있는 90) | 28/90 | 5/90 | 22/90 | **10/90** | 22 보다 줄었다 — **충족** |
| ③ e10 `personal_share` | 3/5 | 5/5 | 1/5 | **5/5** | 수정 전(3/5)보다 낮지 않다 — **충족** |
| ④ 기대 밖 `update_person` | 4 | 43 | 23 | **0** | 23 보다 늘지 않았다 — **충족** |
| ⑤ conflict 유형 | 2/15 | 15/15 | 15/15 | 15/15 | **충족** |
| ⑤ 끝까지 기록 | 91/130 | 120/130 | 108/130 | 120/130 | **충족** |
| ⑤ mixed 두 도구 모두 | 5/10 | 10/10 | 9/10 | 10/10 | **충족** |

after4 의 `add_event` 제안 없음 10건은 전부 f07·f08(근황 전언, 라벨이 `update_person`+`personal_share`)이다(4절).

### 인식 (32건 × 5회 = 160 시도, 네 회차 모두 HTTP 오류 0)

| 지표 | 정의 | before | after | after3 | after4 |
|---|---|---|---|---|---|
| 의도 일치율 (전체) | 파싱된 `loop_extract.output.intent` == 라벨 | 139/160 | 160/160 | 160/160 | 160/160 |
| └ fact | | 30/40 | 40/40 | 40/40 | 40/40 |
| └ event | | 63/70 | 70/70 | 70/70 | 70/70 |
| └ query | | 30/30 | 30/30 | 30/30 | 30/30 |
| └ mixed | | 6/10 | 10/10 | 10/10 | 10/10 |
| └ schedule | | 10/10 | 10/10 | 10/10 | 10/10 |
| `raw.intent` 누락(→ 코드가 record 로 간주) | | 6 | 35 | 0 | 2 (mixed) |
| └ 명시적으로 맞힌 의도 | | 133/160 | 125/160 | 160/160 | 158/160 |
| 유형 일치율 | 기대 type 이 있는 발화: 제안된 `add_event` 중 기대 type 이 하나라도 있음 | 48/90 | 79/90 | 68/90 | **80/90** |
| └ event 묶음만 | | 43/70 | 69/70 | 59/70 | **70/70** |
| └ conflict 라벨만 | | 2/15 | 15/15 | 15/15 | 15/15 |
| └ `add_event` 제안 없음 | | 28/90 | 5/90 | 22/90 | 10/90 |
| enum 이탈 수 | `add_event.type` 7종 밖 | 0/62 | 0/92 | 0/68 | 0/82 |
| `bad_args` 거부 | | 4 | 0 | 0 | 0 |
| `unknown_tool` 거부 | | 0 | 0 | 1 | 0 |
| 도구 집합 정확 일치 | 제안 기록 도구 집합 == 기대 | 126/160 | 105/160 | 125/160 | **148/160** |
| 기대 도구 포함(기록 라벨) | 기대 ⊆ 제안 | 97/130 | 120/130 | 108/130 | 120/130 |
| └ mixed 두 도구 모두 | | 5/10 | 10/10 | 9/10 | 10/10 |
| 끝까지 통과(기록 라벨) | intent=record 이고 기대 도구가 모두 게이트 통과 | 91/130 | 120/130 | 108/130 | 120/130 |
| `query_turn_no_write` 로 버려진 제안이 있는 턴 | 기록 라벨 | 10/130 | 0/130 | 0/130 | 0/130 |
| └ 질문 발화에서 | 보조 | 0 | 0 | 0 | **2 (q06)** |
| 기대 밖 `update_person` | 보조 집계 | 4 | 43 | 23 | 0 |
| 거부 알림 문장("말씀하신 내용을 기록하지 못했어요…") | TRIAL `reply` | 0 | 0 | 0 | 0 |

### 조회 답 (6문형 × 3회 = 18, 전부 조회 경로, `answer_source=llm`)

| 지표 | before | after | after3 | after4 |
|---|---|---|---|---|
| 근황 질문 답변율 (인물 확정 + "기록 없음" 뜻 문구 없음) | 10/12 | 12/12 | 12/12 | 12/12 |
| 없는 것 → "기록이 없어요"(엄격) | 6/6 | 6/6 | 6/6 | 6/6 |
| 같은 것(넓은 정규식) | 6/6 | 6/6 | 6/6 | 6/6 |

after 이후 근황 답 36건은 모두 카드 사건을 날짜와 함께 재진술했다(사람이 읽어 확인, 자동 판정 아님). after3 a04 1회에 붙었던 "한 번에 한 사람씩 물어봐 주세요." 는 after4 에서 0회.

### 지정 발화의 제안 분포 (`search_person` 제외, 5회. "없음" = 기록 도구 0)

| 발화 (라벨) | before | after | after3 | after4 |
|---|---|---|---|---|
| s01 미래 약속 (`add_schedule`) | add_schedule 5 | add_event:meal 5 | add_schedule 5 | add_schedule 5 |
| s02 면담 잡힘 (`add_schedule`) | add_schedule 5 | add_schedule 5 | add_schedule 5 | add_schedule 5 |
| e04 칭찬 (`praise`) | 없음 5 (query) | praise+update_person 5 | update_person 3 · praise+update_person 2 | **praise 5** |
| e10 털어놓음 (`personal_share`) | personal_share 3 · update_person 2 | personal_share+update_person 5 | update_person 4 · personal_share+update_person 1 | **personal_share 5** |
| e12 도움 받음 (`favor`) | favor 5 | favor+update_person 5 | favor+update_person 5 | favor 5 |
| e13 도움 줌 (`favor`) | meeting 1 · other 1 · meeting+update_person 1 · update_person 1 · 없음 1 | favor+update_person 5 | update_person 2 · favor+update_person 2 · favor 1 | **favor 5** |
| f01 선호 "…좋아하셔" (`update_person`) | 없음 3 · update_person 2 (query 5) | update_person 5 | update_person 5 | update_person 5 |
| f03 부정 선호 "…안 드셔" (`update_person`) | update_person 4 · 없음 1 (query 4) | update_person 5 | update_person 5 | update_person 5 |
| f07 결혼 전언 (`update_person`+`personal_share`) | 없음 5 | other+update_person 5 | update_person 5 | update_person 5 |
| f08 이사 전언 (`update_person`+`personal_share`) | update_person 5 | update_person 5 | update_person 5 | update_person 5 |
| m01 식사+알레르기 (`meal`+`update_person`) | meal+update_person 5 | meal+update_person 5 | meal+update_person 5 | meal+update_person 5 |
| m02 도움+습관 (`favor`+`update_person`) | update_person 4 · 없음 1 (query 4) | favor+update_person 5 | favor+update_person 4 · `praise`(도구 이름 오류)+update_person 1 | favor+update_person 5 |
| (참고) e14 other | other 4 · meeting 1 | other 2 · other+update_person 2 · conflict+update_person 1 | other 4 · 없음 1 | other 5 |

**사실만 말하는 평서문(f 묶음)이 사건으로 끌려갔는가**: after4 에서 f01~f08 40회 시도 모두 `update_person` 만 제안했고 `add_event` 는 **0/40** 이다(1차 after 에서는 f04 2회·f07 5회가 `add_event:other` 로 끌려갔었다). 3차 문구("일어난 일은 반드시 `add_event`")가 사실 평서문을 사건으로 끌어오지는 않았다 — 다만 그 반대편으로, 근황 전언 f07·f08 도 사건이 0 이다(4절).

## 3. 변동 폭 (after 1회차 vs 2회차, 같은 코드·같은 명령)

| 지표 | 1회차 | 2회차 | 차이 |
|---|---|---|---|
| 의도 일치 | 160 | 160 | 0 |
| 유형 일치 | 79/90 | 78/90 | 1 |
| `add_event` 없음 | 5 | 9 | 4 |
| 도구 정확 일치 | 105 | 102 | 3 |
| 끝까지 통과 | 120/130 | 116/130 | 4 |
| `raw.intent` 누락 | 35 | 39 | 4 |
| 기대 밖 `update_person` | 43 | 41 | 2 |

before·after3·after4 는 1회씩만 돌렸다. 회차 사이 변동(최대 4)보다 작은 차이는 수정 효과로 읽지 않는다.

## 4. 3차 뒤에도 남은 것 · 나빠진 것

**3차 뒤에도 남는 문제는 더 고치지 않고 그대로 적는다**(FIX-037 3차 절, 같은 소견 재검증 3회 한도 · 원칙 8).

| 항목 | before | after4 | 내용 |
|---|---|---|---|
| 근황 전언(f07·f08)에 `personal_share` 사건 0 | 0/10 | **0/10** | "…결혼한다고 하더라"·"…이사했대" 는 `update_person`(근황 사실)만 5/5. 라벨(P1 결정 J(c) "인물 소식 = personal_share + 사실")과 다르다. 기록 자체는 사실로 된다. after4 의 `add_event` 없음 10/90 과 유형 불일치 10/90 이 전부 이것이다. 라벨이 옳은지(전언 근황을 사건으로도 남길지)는 사용자 결정 거리다 |
| 질문 발화에서 기록 도구 제안 | 0 | **2/5 (q06)** | "한도윤이랑 마지막으로 만난 게 언제였더라?" 가 intent 는 query 5/5 인데 2회 `add_event:meeting` 을 함께 제안했다. 게이트가 `query_turn_no_write` 로 버려 저장·답은 정상이다. 3차 문구("일어난 일 → 반드시 add_event")가 과거 사건을 묻는 질문에도 작용한 것으로 보인다(가설). intent 가 record 로 빠지는 경우가 생기면 기록이 된다 |
| `raw.intent` 누락 | 6 | 2 | 둘 다 mixed, 기본값 record 로 결과는 맞다. 질문에서 빠지면 record 가 된다(5절 ⓔ) |
| 거부 알림(수정안 3·R4) 실측 | — | 0회 | 네 회차 모두 `bad_args` 거부 0 — 분모가 없어 동작을 보지 못했다 |

수정 전보다 낮아진 지표는 없다(2절 표). 1차 after 와 비교하면 유형 일치 79 → 80, 도구 정확 일치 105 → 148, 기대 밖 사실 43 → 0, 끝까지 기록 120 → 120.

## 5. 한계 · 측정하지 못한 것

- ⓐ **원칙 8 — 이미 본 표본.** after 결과를 보고 프롬프트를 **세 번** 고쳤다(1차 → after, 2차 → after3, 3차 → after4). after3·after4 에서 이 표본은 이미 결과를 본 표본이고, 특히 after4 수치는 홀드아웃 성능이 아니라 "같은 표본에서 회귀가 풀렸는가" 의 확인이다. 일반화는 새 표본(P10)으로 재야 한다. 3차 뒤에도 남는 문제(4절)는 더 고치지 않고 그대로 적는다.
- ⓑ R-37-6: 표본 f06 "…주말에만 연락이 돼" 가 기존 프롬프트 예시(`FACT_KEY_DESCRIPTIONS["contact_note"]` "주말에만 연락됨", FIX-017 부터 HEAD 에 있던 문구)와 겹친다. 네 회차 모두 같은 영향이며 표본은 고치지 않았다.
- ⓒ R-37-7: 유형 설명의 갈등 낱말("언쟁·지적받음·부딪힘")은 시연 발화 1·2·4 의 낱말과 같다. 표본 갈등 문장은 다른 낱말("싸웠어"·"언성이 높아졌어"·"말다툼")이라 conflict 15/15 는 그 낱말에 기대지 않은 결과지만, **시연 계정에서 나온 결과는 평가 수치로 쓰지 않는다.**
- ⓓ R-37-8: 조회 답 표본은 사건이 있는 카드 1장, 문형마다 3회다. 사실만 있고 사건·일정이 0건인 카드에 근황을 물으면 어떻게 답하는지는 재지 않았다.
- ⓔ 질문에서 `intent` 키가 빠지면 코드 기본값이 record 라 기록 턴이 된다. 이 표본의 질문에서는 누락 0 이지만, 6문형 밖의 질문 꼴은 보장이 없다 — 이 기본값 문제는 P10 표본으로 넘긴다. q06 처럼 질문에도 기록 제안이 섞이는 꼴(4절)과 겹치면 위험이 커진다.
- 증상 (b)(유형 enum 이탈)를 일으킨 꼴(건강·병원 사건) 문장이 표본에 없어 enum 이탈은 네 회차 모두 0 이다 — (b) 수정 효과와 거부 알림(수정안 3·R4)은 이 표본으로 볼 수 없다.
- before·after3·after4 는 1회씩만 돌렸다(변동 폭은 after 두 회차로만 가늠).
- 제안기(`loop_extract`) 토큰은 trace 에 0 으로 남아 비용을 trace 로 셀 수 없다.
- 조회 답의 정확성(날짜·내용)은 자동 판정하지 않았다. per_item 원문 답이 증거에 있다.
- (before 준비 단계 관찰, 지표 밖) query 로 오분류된 평서문 "배성훈 선배가 내 이력서를 꼼꼼하게 봐 줬어" 에 조회 답이 카드에 없는 그 문장을 기록된 것처럼 되읊었다(trace 1045). 이후 회차에서는 이 꼴을 다시 재지 않았다.
