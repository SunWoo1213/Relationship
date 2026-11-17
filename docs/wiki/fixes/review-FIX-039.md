# review-FIX-039 · 인물 카드·브리핑의 영문 키를 한글 이름으로 보여 준다 — 커밋 전 리뷰

검토자: verifier (fable) · 2026-11-18 · 기준 HEAD `e4a7fc0` (dev2) + 작업 트리 미커밋 diff(`web/` 수정 4개 + 새 파일 2개) · Refs: FIX-039 P9b-auth P8-frontend 원칙5 원칙7

**결과: 통과 — [필수] 0건, [권고] 3건(R-39-1~3), [참고] 2건.** 변경은 FIX-039 수정안 그대로다. 표 16개 글자가 FIX 문서와 일치하고, `app/`·`alembic/` 변경은 0이며, `web/src` 에서 키·종류를 그리는 세 자리가 모두 새 함수를 쓴다. FIX 문서가 정한 핵심 변이 둘(표 글자 변경 → ①, 모르는 키 처리 → ③)은 테스트가 잡는다. 다만 내가 더 돌린 변이 10종 중 6종은 살아남았다 — 전부 "표에 없는 입력을 지어내지 않는다"·"value·content 무변경" 계약의 가장자리이고 지금 코드는 옳으므로 커밋을 막지 않고 권고로 남긴다.

## 1. 본 것

- `docs/wiki/fixes/FIX-039.md` 증상·원인·수정안·하지 않는 것·기획서 정합성·`계획 점검: 통과`.
- `git diff -- web/src docs/wiki/packages/P9b-auth/tests.md` 전체와 새 파일 `web/src/lib/labels.ts`·`web/src/__tests__/labels.test.tsx` 전문.
  - `PersonCardScreen.tsx`: 3행 주석, import 1줄, 121행 `eventTypeLabel(event.type)`, 218행 `factKeyLabel(fact.key)`. `{fact.value}`·`{event.content}`·원문·일정 제목 줄은 diff 에 없다.
  - `BriefingScreen.tsx`: import 1줄, 114행 `` `${factKeyLabel(p.key)} ${p.sentence}` ``. `l.text`·`record.suggestion.text` 줄은 diff 에 없다.
- 키 원천: `app/memory/types.py:356-366` `FACT_KEYS` 9종(`job workplace family hobby likes dislikes health life_event contact_note`), `app/db/models.py:71-79` `EVENT_TYPES` 7종(`conflict praise meal meeting personal_share favor other`). `labels.ts` 의 키 집합·순서가 같다.
- `git status --short -- app alembic` 출력 없음, `git diff --stat -- app alembic` 출력 없음 → 백엔드 변경 0.
- 구현자 증거 `fixes/evidence/20261118-0850-FIX-039-{vitest,build,typecheck,lint}.txt`(246 passed), `20261118-0848-FIX-039-mutations-run2.txt`(M1~M12 전부 실패 ≥ 1). `20261118-0848-FIX-039-mutations.txt` 는 exit 126(`mut.sh: Permission denied`)으로 끝난 첫 시도다 — 증거가 아니라 실패 기록이다([참고]).

### 표 16개 글자 대조 (FIX-039.md 26·28행 ↔ `labels.ts`)

| 키 | FIX 문서 | `labels.ts` | 일치 |
|---|---|---|---|
| job / workplace / family / hobby | 직업 / 소속 / 가족 / 취미 | 직업 / 소속 / 가족 / 취미 | 예 |
| likes / dislikes | 좋아하는 것 / 싫어하는 것 | 좋아하는 것 / 싫어하는 것 | 예 |
| health / life_event | 건강 / 근황 | 건강 / 근황 | 예 |
| contact_note | 연락·만남 메모 | 연락·만남 메모 (가운뎃점) | 예 |
| conflict / praise / meal / meeting | 갈등 / 칭찬 / 식사 / 만남 | 갈등 / 칭찬 / 식사 / 만남 | 예 |
| personal_share / favor / other | 개인 이야기 / 도움 / 기타 | 개인 이야기 / 도움 / 기타 | 예 |

`labels.test.tsx` 의 `FACT_CASES`·`EVENT_CASES` 16쌍도 같은 글자를 값으로 단언한다(표를 import 해 자기 자신과 비교하지 않는다).

### 키·종류를 그리는 다른 곳이 남았는가

`grep -rnE "\.key\b|\.type\b|pattern:|fact_keys|pattern_sentences|\.kind\b" web/src`(테스트·`components/ui` 제외) 결과에서 서버 키·종류를 화면 글자로 그리는 곳은 `PersonCardScreen.tsx:121`·`:218`, `BriefingScreen.tsx:114` 세 줄뿐이고 셋 다 새 함수를 쓴다. 나머지는 React `key=`(`ChatScreen.tsx:268·277`, `AppShell.tsx:79`), 키보드 이벤트(`ChatScreen.tsx:250`), 서비스 워커 메시지 종류(`AppShell.tsx:144·161`), 타입 선언(`api/types.ts`)이다. `basis.fact_keys` 는 어디서도 그리지 않는다. `web/e2e/` 는 영문 키·종류를 화면 글자로 단언하지 않는다(`card.spec.ts`·`briefing.spec.ts` 의 `expect` 줄 직접 확인) — e2e 는 이번에 실행하지 않았다.

## 2. 내가 직접 실행한 것 (전부 `save_evidence.py` 통로, 출력 전문)

| # | 명령 | 결과 | 증거 |
|---|---|---|---|
| 1 | `npm --prefix web run test -- --run` | **12 files · 246 passed**, exit 0 | `fixes/evidence/20261118-0851-verifier-FIX-039-test.txt` |
| 2 | `npm --prefix web run typecheck` | exit 0 | `…-0851-verifier-FIX-039-typecheck.txt` |
| 3 | `npm --prefix web run lint` | exit 0 (경고만 — 전부 이번 diff 밖 파일: `ui/tabs.tsx`·`App.tsx`·`PersonList.tsx`·`ui/button.tsx`·`PersonsProvider.tsx`·`ui/badge.tsx`) | `…-0851-verifier-FIX-039-lint.txt` |
| 4 | `npm --prefix web run build` | `✓ built`, exit 0 | `…-0851-verifier-FIX-039-build.txt` |
| 5 | 대조군 + 변이 10종 — 스크래치패드 사본에서 `npx vitest run` (labels·card·briefing 3개 파일) | 아래 표 | `…-0852-verifier-FIX-039-mutations.txt` (V1~V10 은 `--append`) |

246 = 기준선 224 + 새 22건(`it.each` 9 + 7, 단건 1, 화면 5). `tests.md` 의 "22건(함수 17 + 화면 5)" 와 맞는다.

변이 사본: `/private/tmp/claude-501/-Users-sunwoo-Desktop-Portfolio-Relationship/1f888faf-f134-4b54-95c3-8ca7d22d83a7/scratchpad/fix-039-review/base/` — `web/` 의 `src public index.html package.json tsconfig.json tsconfig.app.json tsconfig.node.json vite.config.ts components.json` 만 이름을 지정해 복사했고 `node_modules` 는 심볼릭 링크다(점 파일 0개, `.env` 없음). 변이 스크립트는 같은 폴더의 `mutate.py`·`run.sh` 이고 치환이 정확히 1번 일어나지 않으면 실패한다. 변이 뒤 `git status --short -- web` 은 리뷰 시작 때와 같다(저장소 무수정).

| 변이 | 사본에 한 일 | 기대 | 결과 |
|---|---|---|---|
| 대조군 | 없음 | 통과 | 91 passed |
| V1 | `contact_note` 글자 `연락·만남 메모` → `연락/만남 메모` | 실패 | **2 failed** — 함수 `contact_note`, 카드 사실 9종 |
| V2 | `other` 글자 `기타` → `그 외` | 실패 | **2 failed** — 함수 `other`, 카드 타임라인 7종 |
| V5 | 브리핑 패턴 줄의 이름과 sentence 사이 공백 제거 | 실패 | **2 failed** — `briefing.test` 순서 테스트, `labels.test` 브리핑 |
| V6 | 브리핑 `l.text` 에서 `pattern:` 글자 제거 | 실패 | **1 failed** — `labels.test` 브리핑(`lines` 무변경 단언) |
| V3 | `{fact.value}` → `{factKeyLabel(fact.value)}` | 실패 | **살아남음** (91 passed) → R-39-1 |
| V8 | `{event.content}` → `{eventTypeLabel(event.content)}` | 실패 | **살아남음** → R-39-1 |
| V4 | 표 조회를 `key.toLowerCase()` 로(대소문자 무시) | 실패 | **살아남음** → R-39-2 |
| V7 | `pattern:<사실 키>` 를 사실 키 한글로(`pattern:job` → `직업`) | 실패 | **살아남음** → R-39-2 |
| V9 | 사건 종류 조회가 사실 키 표로 넘어감(`type="job"` → `직업`) | 실패 | **살아남음** → R-39-2 |
| V10 | 사실 키 조회가 사건 종류 표로 넘어감(`key="meal"` → `식사`) | 실패 | **살아남음** → R-39-2 |

FIX 문서 35행이 정한 변이("표의 한 항목을 다른 글자로 바꾸면 ① 이, 모르는 키를 빈 문자열로 돌려주게 하면 ③ 이 잡는다") 중 앞의 것은 V1·V2 로 내가 확인했고(구현자와 다른 항목), 뒤의 것은 구현자 M2·M3 증거로 본다(다시 돌리지 않았다).

## 3. 범위 판정

| 계획 문장(FIX-039 수정안) | 판정 | 근거 |
|---|---|---|
| 표시 이름 표 9 + 7 글자 | 지킴 | 1절 대조표, V1·V2 |
| `pattern:<type>` → 사건 종류 한글, 접두사 숨김 | 지킴 | `labels.ts` `factKeyLabel`, 구현자 M4 |
| 표에 없는 키·종류·`pattern:<모르는 type>` 은 원문 그대로 | 지킴(코드) · 테스트는 일부만 | `lookup` 이 `hasOwnProperty` 자기 속성만 + `?? key`. 가장자리는 R-39-2 |
| value·content·원문·일정 제목 무변경 | 지킴(코드) · 테스트는 일부만 | diff 에 해당 줄 없음. 구현자 M12(value trim). R-39-1 |
| 브리핑 패턴 줄 `<표시 이름> <sentence>`, `lines`·`suggestion` 무변경 | 지킴 | V5·V6, `briefing.test.tsx:113-114` |
| `PersonCardScreen.tsx` 3행 주석 | 지킴 | diff |
| 다른 곳에 키·종류를 그리는 곳이 있으면 같은 함수 | 해당 없음 | 1절 grep — 세 자리뿐 |
| 회귀 테스트 ①~⑤ | 있음 | `labels.test.tsx` 5개 describe/it |
| 백엔드 무변경 | 지킴 | `app/`·`alembic/` diff 0 |
| 하지 않는 것(백엔드·MCP·DB 키, sentence 문장화, 디자인) | 넘지 않음 | className·구조 그대로 |

원칙5(화면 추가 없음, 표 하나와 세 자리 치환)·원칙7(value·content·원문은 재진술 그대로)·security(비밀·외부 전송·삭제 없음) 위반 없음. 스키마 v2·툴 7종 시그니처·API 응답은 건드리지 않았다.

고친 기존 테스트는 약해지지 않았다: `card.test.tsx:700-701` 은 `child`(표에 없는 키 원문) 단언을 남기고 `취미` 를 더했고, `:704` `pattern:conflict` → `갈등`, `:716·718` `meal`/`conflict` → `식사`/`갈등`, `briefing.test.tsx:113` 은 완전 일치 배열(`갈등 ${PATTERN}` — 앞뒤 공백이 있는 문장 그대로)이다.

## 4. 소견

- **[권고] R-39-1** `web/src/__tests__/labels.test.tsx` — "value·content 는 서버 문자열 그대로"(회귀 ④)가 **값이 키와 같은 글자일 때**를 보지 않는다. V3(`factKeyLabel(fact.value)`)·V8(`eventTypeLabel(event.content)`)이 91 passed 로 살아남았다. 지금 테스트 값(`값-job`, ` 내용 <meal> & "그대로" `)은 표의 키와 완전히 같지 않아 표시 함수를 통과해도 안 바뀐다. 사실 한 줄에 `value: 'job'`(기대 `직업 job`), 타임라인 한 줄에 `content: 'meal'`(기대 배지 `식사` + 내용 `meal`)을 더하면 닫힌다.
- **[권고] R-39-2** `web/src/__tests__/labels.test.tsx:70-77` — "표에 없는 문자열은 그대로" 단언이 두 표 사이·대소문자를 보지 않는다. V4·V7·V9·V10 이 살아남았다. `expect(factKeyLabel('meal')).toBe('meal')` · `expect(eventTypeLabel('job')).toBe('job')` · `expect(factKeyLabel('pattern:job')).toBe('pattern:job')` · `expect(factKeyLabel('JOB')).toBe('JOB')` 네 줄이면 닫힌다. 서버 어휘(`FACT_KEYS`·`EVENT_TYPES`)는 고정이라 지금 운영 데이터에서 이 입력이 올 길은 없고 코드도 옳다 — 그래서 필수가 아니다.
- **[권고] R-39-3 (사용자가 볼 화면에 영문이 남는 곳 — FIX 범위 밖)** 브리핑이 템플릿 생성기로 만들어지면 `lines[].text` 자체에 영문 키·종류가 들어 있다: `app/briefing/compose.py` `template_briefing` 의 `text=f'{fact["key"]}: {fact["value"]}'` 와 `text=f'{event["occurred_at"]} {event["type"]}: {event["content"]}'`. 이 글자는 서버 문자열이고 FIX-039 는 "`lines`·`suggestion` 은 건드리지 않는다"·"백엔드 무변경"이라 이번 변경이 옳게 손대지 않았다. 다만 사용자 요청 원문("영문 키를 한글로 바꿔줘")으로 보면 브리핑 화면에 `job: 팀장`·`… meal: …` 이 남을 수 있다. 운영이 어느 생성기를 쓰는지는 이 리뷰에서 확인하지 않았다(운영 `.env` 는 열지 않는다). 메인 세션이 운영 브리핑 화면을 한 번 보고, 남아 있으면 별도 FIX 로 사용자에게 올릴 일이다.
- **[참고]** LLM 생성기가 만든 패턴 문장은 종류를 이미 말로 담을 수 있다(예: "최근 갈등이 3회…"). 그 경우 화면은 `갈등 최근 갈등이 3회…` 처럼 이름이 겹친다. 수정안 32행이 정한 모양(`<표시 이름> <sentence>`) 그대로라 결함은 아니다. 증상란의 예(`3회 (2026-11-09, …)`)는 규칙 `value` 그대로인 템플릿 문장이다.
- **[참고]** `fixes/evidence/20261118-0848-FIX-039-mutations.txt` 는 exit 126 으로 끝난 구현자 첫 시도다. `tests.md` 가 가리키는 것은 `-run2` 이므로 맞다. 지우지 않고 둔다(실패 기록).

## 5. 열린 문제

없음. R-39-1~3 은 커밋을 막지 않는다. R-39-3 은 메인 세션이 운영 화면에서 확인할 몫이다.
