# P8-frontend U5 채팅 화면 + 확인 칩 — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 (2026-10-13 14:05) — **[필수] 0, [권고] 5.** 01-plan 96행·결정 D·E 계약 15항목 전부 코드·테스트로 충족(§1). 판정 명령 재실행 exit 0(typecheck · 47 passed · build, 번들 해시 구현자와 동일 — `-judge.txt`). 서버 문자열(`options`·`reply`·`question`) 변환 코드 0(원칙7, `-grep.txt`). 내 변이 5건 중 4건 검출·1건(V1 `options` trim 주입) 살아남음 = 테스트 공백(R-U5-1), 구현자 변이 M1·M4·M10 재실행 결과가 구현자 표와 실패 이름·건수까지 동일(`-mutation.txt`). R-U4-11 닫힘(셸 환경변수 `VITE_API_TARGET=http://x:1` 을 준 채 6 passed — `-env.txt`), R-U4-12 닫힘(`data-[side=left]:w-64 data-[side=left]:sm:max-w-none`). R-U0-3: `package.json`·lock HEAD 와 바이트 동일, scripts 7개 무변경, `npm audit --omit=dev` 0(`-deps.txt`). 보안·범위 위반 0(`app/`·`alembic/`·`tests/`·`.github/` 무변경, 삭제 0, 외부 URL 0, `/push-dev/` 0, `test-setup.ts` 무변경). 증거 규칙 (c) 는 구현자 단계에서 **재발**했으나(발췌본 자기 보고) 메인 세션이 원본 644행·스크립트를 보존해 증거 세트는 완전하다 — 등급 판단과 근본 대책 후보는 §6(R-U5-3). 구현자 선택 ①~⑥ 은 계획과 모순 없음(§2), 단 ④ 복원 실패 침묵은 사용자 결정 거리(R-U5-2).
대상: 작업 트리(기준 HEAD `975a8e5`) — `git diff -- web` 6파일(`proxy.test.ts` 14/3 · `client.ts` 29/2 · `AppShell.tsx` 1/1 · `proxy.ts` 8/0 · `ChatScreen.tsx` 296/3 · `vite.config.ts` 2/2) + 신규 `web/src/session.ts`·`web/src/__tests__/chat.test.tsx` · `docs/wiki/registry.md` U5 행 4개 · 구현 증거 `evidence/20261013-1325-u5-chat.txt`·`-u5-mutation.txt`(발췌본)·`-u5-mutation-raw.txt`(원본)·`-u5-mutation-script.mjs.txt`. `HANDOFF.md`·`journal.md`·`03-log.md` 변경은 대상 아님(03-log 맨 끝 "U5 시작" 은 근거 문서).
근거 문서: `01-plan.md` 96행(U5) · 19행(결정 L 사용자 방향) · 36~49행(하지 않는 것) · 52~80행(파일 목록) · 255~264행(결정 D·E) · 결정 J(가짜 API) · `app/api/schemas.py` 52~123행(`AnswerIn`·`ChatIn`·`StoredOut`·`ChatPendingQuestionOut`·`AnswerOut`·`ChatOut`) · `app/api/routes.py` 218~236행(409 `already_answered`/`expired`)·470~478행(`/questions/pending`) · `app/api/deps.py` 205~210행(422 `invalid_session_id`) · CLAUDE.md 원칙1·7 · `.claude/agents/frontend-agent.md` "하지 말 것" 3·5, 하네스 규칙 FIX-033 두 항목 · `review-u4-skeleton.md` R-U4-10·11·12 · `review-u3-read-questions-briefings.md` R-U3-3 · `docs/wiki/verification.md` "변이 시험 방법".

내 증거(전부 출력 전체, Write 로 저장 — `docs/wiki/packages/P8-frontend/evidence/`):
- `20261013-1349-verifier-u5-judge.txt` — `npm run typecheck` · `npm test -- --run --no-color` · `npm run build` 각각 exit 0, 47 passed, 번들 `index-CAOaKUIt.css`/`index-B0RGjTQd.js`(구현자와 동일).
- `20261013-1352-verifier-u5-deps.txt` — package.json·lock `git diff --quiet` exit 0, scripts HEAD/작업 트리 동일, `npm audit --omit=dev` 0, lock 항목 557.
- `20261013-1352-verifier-u5-env.txt` — `VITE_API_TARGET=http://x:1 npm test -- --run src/__tests__/proxy.test.ts` 6 passed(verbose 포함), HEAD 판 13행 인용.
- `20261013-1352-verifier-u5-grep.txt` — 원칙7 변환 grep · NOTICE 목록 · push-dev · URL · 비밀 · localStorage 사용처 · `test-setup.ts` 무변경 · 범위(`app/alembic/tests/.github`) · 삭제 · `git status` · numstat · 라우트 무변경 · 서랍 폭 클래스 · 테스트 데이터 공백 유무.
- `20261013-1354-verifier-u5-mutation.txt` — V0 대조군 + 내 변이 V1~V5 + 구현자 M1·M4·M10 재실행 + 원본 대조 + 탐침 P1, 변이마다 저장소 원본 `git diff --stat` 로 무수정 확인. 스크립트는 스크래치패드 `vmut.mjs`·`vprobe.mjs`·`probe.test.tsx`(저장소에 넣지 않음).

## 1. 01-plan 96행 · 결정 D·E 계약 대조

| # | 계약(96행 / 결정) | 구현 | 테스트·변이 | 판정 |
|---|---|---|---|---|
| 1 | 발화 전송 `POST /api/chat` 본문 `{utterance}` | `client.ts` `postChat` — `ChatIn = { utterance }`, `apiFetch('/chat', {method:'POST'})` | 93행(method·body 값), `-judge.txt` | ✓ |
| 2 | 결정 D (i): 응답 `session_id` 를 `localStorage` 보관·다음 요청 `X-Session-Id` 재전송, 첫 요청 헤더 없음 | `session.ts` 키 `relationship.session_id`(get/set/clear 전부 try/catch) · `client.ts` 48~49행 `sessionId === undefined ? getSessionId()` · `postChat` 이 `setSessionId(out.session_id)` | 105행(첫 요청 헤더 `undefined` → 저장 → 둘째 요청 헤더 값) · 121행(복원 요청도 헤더) · 구현자 M3·M6 검출 · 내 V3 검출 · 탐침 P1(저장소 throw 에도 생존) | ✓ |
| 3 | 대화 기록은 화면 메모리에만 | `useState<Message[]>` 만. `localStorage` 사용처는 `session.ts` 3곳뿐(`-grep.txt`) | 코드 검사 | ✓ |
| 4 | 결정 L 챗봇형: 꽉 찬 대화 영역 · 하단 고정 자동 높이 입력창 · 오른쪽 사용자 말풍선/왼쪽 본문형 응답 · 타이핑 점 · 자동 스크롤 | `section h-full flex-col` → 목록 `min-h-0 flex-1 overflow-y-auto` + 입력 `shrink-0`; `AppShell` 은 `flex h-dvh` → `<main class="flex-1 overflow-y-auto p-6">` 라 `h-full` 유효. `textarea rows=1` + `resizeInput`(`scrollHeight`, 상한 `INPUT_MAX_HEIGHT=160`). 사용자 `flex justify-end` + `bg-primary rounded-2xl`(`data-role="user"`), 봇 `data-role="bot"` 본문형(말풍선 없음). `TypingDots`(`role=status`, `data-testid=typing`, `waiting>0`). `useEffect` 가 `scrollTop = scrollHeight`. | 173행(타이핑 점 등장·소멸) · 93행(`data-role=user`) · 205행(칩이 봇 본문 안). **jsdom 한계**: 높이·스크롤·레이아웃은 계산되지 않아 자동 높이·자동 스크롤·꽉 찬 영역은 코드 검사뿐 — U10 사람 점검. | ✓ (레이아웃은 코드 검사) |
| 5 | 원칙7 · 결정 E: 칩 = `options` 문자열·순서 그대로 | `toQuestion` `options: q.options`(배열 참조 그대로), `question.options.map((option, i) => …{option})`. 변환(`trim/sort/reverse/replace/normalize/toLowerCase`) 0 — `ChatScreen.tsx` 의 `trim` 2건은 사용자 입력 `draft` 뿐(`-grep.txt`) | 205행(`labels toEqual OPTIONS`)·270행 · 구현자 M1 검출(내 재실행 동일) · **내 V1(trim 주입) 살아남음, V2(정렬 주입) 1건만** — R-U5-1 | ✓ 코드 / 테스트 공백 |
| 6 | 칩 클릭 → `POST /api/answers/{id}` 본문 `{answer: 그 문자열}` | `pick(questionId, option)` → `postAnswer` — `AnswerIn = { answer }` 그대로 | 218행(url·method·body 값) · 구현자 M2 검출 | ✓ |
| 7 | 누른 칩 선택 고정·나머지 비활성 | `locked = closed \|\| selected !== null`, `disabled={locked}`, `aria-pressed={pressed}` | 218행(aria-pressed true/false·disabled) · 구현자 M8·M11 검출 | ✓ |
| 8 | `reply` 이어 붙임 · 새 `pending_question` 이면 그 아래 새 칩 | `pick` 성공 시 `{role:'bot', text: out.reply, question: out.pending_question ? toQuestion(...) : undefined}` 추가 | 245행(새 칩이 이어 붙은 reply 안, 앞 칩 고정 유지) | ✓ |
| 9 | 결정 E: 진입 시 `GET /api/questions/pending` 으로 미답변 **전부** 질문별 복원 | `useEffect` → `getPendingQuestions()` → `have` 로 중복 제거 후 **전부** 맵, 응답 순서(서버 `created_at` 오름차순, U3) 유지 | 270행(2개·글자·순서·요청 1회) · 구현자 M10 검출(재실행 동일) · 내 V3 검출 | ✓ |
| 10 | 결정 E: 대기 중 입력 막지 않음 | `textarea` 에 `disabled` 없음; `sending` 은 보내기 버튼·Enter 만 | 188행(칩이 떠 있어도 입력 가능) | ✓ |
| 11 | 409 `already_answered`/`expired` → 그 질문 칩 비활성·한 줄 안내·재시도 없음 | `pick` catch `error.status === 409` → `{selected:null, closed:true, notice: NOTICE.questionClosed}`; 재시도 호출 없음 | 286행 `it.each` 두 코드(비활성·aria-pressed false·안내·다른 질문 무영향·요청 1회) · 구현자 M4·M13 검출 · 내 V4(코드 하나만 처리) 검출 | ✓ |
| 12 | P5 오류 규약·5xx → 한 줄 안내 | `setNotice(failureNotice(error))` → `NOTICE.failed`(`role=alert`) | 322행(5xx)·330행(네트워크)·307행(답 5xx) · 내 V5 검출 | ✓ |
| 13 | 422 `invalid_session_id`(deps.py 210행) → 저장 세션 버림 | `client.ts` 66행 `clearSessionId()` + 화면 `NOTICE.sessionReset` | 129행(버림·다음 요청 헤더 없음) · 구현자 M9 검출 | ✓ |
| 14 | `stored.persons/events > 0` → 카드 링크 한 줄(01-plan 97행 U6 문장을 U5 가 앞당김) | `hasStored`, `<a href={HREF.persons}>` | 353·361·368행(persons / events / schedules 만은 없음) · 구현자 M5 검출 | ✓ |
| 15 | 판정 `npm test -- --run src/__tests__/chat.test.tsx` · 증거 `*-u5-chat.txt` | 구현자 `-1325-u5-chat.txt` 21 passed + 전체 47 + build · 내 `-judge.txt` 47 passed | — | ✓ |

TS 타입: `client.ts` 가 쓰는 `ChatIn`·`ChatOut`·`AnswerIn`·`AnswerOut`·`ChatPendingQuestionOut`·`StoredOut` 은 `types.ts` 10~49행 — `schemas.py` 52~123행과 필드·null 가능성 일치(U4 전수 대조 유지, 이번 변경 없음).

## 2. 구현자 선택 사항 ①~⑥ 의 계획 적합성

| # | 구현 안 | 계획 대조 | 판정 |
|---|---|---|---|
| ① | 고정 안내 문장 `NOTICE` 5개(빈 상태·실패·질문 닫힘·세션 초기화·링크 글자) | frontend-agent.md 품질 체크 "프론트가 만든 안내 문구는 오류·빈 상태 안내뿐인가" — 4개는 오류·빈 상태, `personsLink` 는 링크 글자(97행 "링크 한 줄"). 서버 문장 아님, 고민 상담·감정 문구 아님(원칙7) | 적합 — 기록 |
| ② | `/chat` 전송 중 보내기 버튼·Enter 잠금(`sending`), 입력창은 열림 | 결정 E "대기 중 입력 (i) 막지 않는다" 의 "대기" 는 **확인 칩 대기**(S3.4 "답 없이 다음 발화가 오면 대기 질문 유지")다. 전송 중 중복 전송 방지는 그 문장과 다른 축이고 입력창은 열려 있다(188행). 칩 답(`pick`) 은 `sending` 을 올리지 않아 답 전송 중에도 발화 가능. 계획에 없는 방어 조건이지만 보고됐다(R-U4-10 절차 준수) | 모순 없음 — 기록. 단 전송 중 Enter 는 조용히 무시되고 draft 는 남는다(사용자가 다시 Enter) — 테스트 없음(R-U5-4) |
| ③ | 칩 답이 5xx·네트워크로 실패하면 선택을 풀어 재클릭 가능, 409 만 영구 비활성 | 결정 E "409: … 그 칩을 지우고 한 줄 안내. 재시도하지 않는다" — "재시도하지 않는다" 는 409 항목 안의 문장이라 범위는 409 다. 96행도 409 와 5xx 를 다른 절로 적었다("5xx → 한 줄 안내" 만). 5xx 뒤 사용자가 다시 누르는 것은 자동 재시도가 아니다 | 적합 — 기록. 내 V5(5xx 도 영구 비활성)가 검출되므로 이 선택은 테스트로 고정돼 있다 |
| ④ | 복원(`GET /questions/pending`) 실패 시 안내 없음 | 96행 "P5 오류 규약·5xx → 한 줄 안내" 는 복원 요청을 제외하지 않는다. 침묵이면 사용자는 대기 질문이 있는 줄 모른 채 새 발화를 보낸다(서버는 질문을 유지하니 데이터 손상은 없음, 재진입 시 다시 복원). 343행 테스트가 `queryByRole('alert')` null 로 **침묵을 고정**한다 | 모순은 아니나 계획이 침묵을 허락한 것도 아니다 — R-U5-2 [권고], 사용자 결정 |
| ⑤ | 낙관적 선택 고정(요청 전에 `selected` 를 두고 실패 시 복원) | 96행 "칩 클릭 → POST → 누른 칩은 선택 상태로 고정" — 순서를 강제하지 않음. 실패 경로에서 푸는 것이 ③·409 와 일관 | 적합 — 기록 |
| ⑥ | 한글 조합 중 Enter(`nativeEvent.isComposing`) 미전송 | 계획 무언급, IME 환경의 표준 처리. 변이로 없애도 통과(테스트 없음, jsdom 에서 composition 이벤트는 `fireEvent` 로만 흉내 가능) | 적합 — 기록, 테스트 없음(R-U5-4) |

기록(소견 아님): `send()` 실패 시 입력창의 draft 는 비워진 채 남고 말풍선만 남는다(322행이 말풍선 잔존을 단언). 재입력 비용이 있으나 계획이 정하지 않았고 결정 L 의 시간 상한 안에서 바꿀 이유가 없다 — U10 사람 점검에서 사용자가 보고 정한다.

## 3. R-U4-11 · R-U4-12 닫힘

- **R-U4-11 닫힘.** `proxy.ts` 에 `DEFAULT_API_TARGET`·`resolveApiTarget(env)` 순수 함수, `vite.config.ts` 12행이 `resolveApiTarget(env)`. `proxy.test.ts` 는 `rule.target` 단언을 지우고(`grep rule.target` 0건) `resolveApiTarget({})`·`({VITE_API_TARGET:''})`·`({VITE_API_TARGET:'http://x:9'})` 를 값으로 단언. 실측: `VITE_API_TARGET=http://x:1 npm test -- --run src/__tests__/proxy.test.ts` **6 passed**(`-env.txt`) — U4 E1 의 재현 조건에서 더는 깨지지 않는다. 구현자 M12(`||` 제거) 검출.
- **R-U4-12 닫힘.** `AppShell.tsx` 68행 `data-[side=left]:w-64 data-[side=left]:sm:max-w-none` — `sheet.tsx` 63행의 `data-[side=left]:w-3/4 … sm:max-w-sm` 과 같은 변형 접두라 특이도 동률, `cn()`(tailwind-merge)이 뒤쪽을 남긴다(`-grep.txt`). jsdom 은 CSS 를 계산하지 않아 자동 테스트 없음 — U10 1항(같은 앱 틀)에서 눈으로.

## 4. R-U0-3 고정 점검 (`-deps.txt`)

`git diff --quiet -- web/package.json web/package-lock.json` exit 0(바이트 동일) — 새 패키지 0. scripts 7개 HEAD 와 동일(`dev/build/typecheck/test/e2e/lint/preview`, `&&` 만). `npm audit --omit=dev` "found 0 vulnerabilities". lock `node_modules/` 항목 557(U4 2차와 같음). `lucide-react` `SendIcon` 은 기존 의존성.

## 5. 변이 시험 (`-mutation.txt`, 저장소 무수정 — 변이마다 `git diff --stat -- web/src` 가 U5 작업 트리 그대로)

| 변이 | 결과 |
|---|---|
| V0 대조군 | 21 passed |
| V1 `toQuestion` 에 `options.map(o => o.trim())` 주입 | **살아남음** — 테스트 options 데이터에 앞뒤 공백 문자열이 없다 |
| V2 `[...q.options].sort()` 주입 | 1 failed(263행만) — 205행 `OPTIONS`·279행 `['가','나']`·`['다','라','마']` 는 이미 코드포인트 오름차순이라 전용 순서 테스트가 정렬을 못 가른다 |
| V3 복원 요청 `sessionId: null` | 1 failed(126행) |
| V4 409 를 `already_answered` 만 처리 | 1 failed(`expired` 케이스) |
| V5 5xx 때 `closed: true` | 1 failed(317행) |
| M1·M4·M10 재실행 | 3·2·3 failed — 실패 테스트 이름·건수가 구현자 원본과 동일 |
| P1 탐침 `Storage.prototype` set/get/remove 전부 throw | 통과 — 전송·reply·칩·답 동작, alert 0, 세 번째 요청 헤더 없음(재발급 경로) |

구현자 표 신뢰성: 발췌본과 원본의 변이 헤더·`[exit`·`Tests N failed` 줄 `diff` 비어 있음(13건 전부 exit 1). 내 재실행 3건이 이름·건수까지 일치. 표를 신뢰한다.

## 6. 증거 규칙 (c) 재발 판정 — R-U5-3

**사실.** `-u5-mutation.txt`(617행)는 구현자가 "사람이 다시 옮겨 적은 것… (c) 를 완전히 충족하지 못한다" 고 머리에 자기 보고했고 M9·M10·M11·M13 네 자리를 줄였다. R-U3-3 은 "다시 미달이면 그때는 [필수]". 구현자 단계에서는 **재발이 맞다**. 다만 메인 세션이 스크립트 출력 원본을 `-u5-mutation-raw.txt`(644행, ANSI 만 제거, ESC 0)로 보존하고 스크립트도 `-u5-mutation-script.mjs.txt` 로 남겨, **증거 세트로서는 (c) 를 충족한다**(내 `diff` 로 판정 줄 동일 확인, 재실행 3건 일치).

**등급: [권고] R-U5-3 — 재작업 요구 안 함.** 이유: ① R-U3-3 이 [필수]를 건 목적은 "원본 없는 발췌" 를 막는 것인데 이번에는 원본이 증거 폴더에 있다 — 재작업(구현자가 다시 받아 쓰기)은 이미 있는 파일을 다시 만드는 일이다. ② 구현자가 미달을 숨기지 않고 머리에 위치까지 적었다(FIX-033 (c) 의 "요약·발췌는 따로 표시" 는 지켰다). ③ 원인이 구현자 태만이 아니라 구조다 — 아래. 그러나 **같은 구조가 남아 있으면 U6·U7 에서도 반복된다**. 그래서 이번 판정의 실질은 "구현자 재작업" 이 아니라 "근본 대책 선택" 이고, 그것을 사용자에게 올린다. 대책이 정해지기 전까지는 이번 방식(스크래치패드 원본 → 메인 세션이 Write 로 보존)을 U6 위임 프롬프트에 명시해 두면 된다.

**원인.** `bash-write-guard`(FIX-014)가 프로젝트 안 경로로의 `>`·`tee` 를 막으므로 에이전트는 명령 출력을 스크래치패드에 받고, 그것을 컨텍스트로 읽어 Write 로 다시 써야 한다. 644행·86 KB 를 모델이 "옮겨 적는" 과정은 그 자체가 요약 압력이다(DOM 덤프를 끄는 `DEBUG_PRINT_LIMIT=0` 도 같은 압력의 산물). 가드는 `pytest`·`python x.py`·`node` 처럼 **프로그램이 스스로 쓰는 것은 막지 않는다**(CLAUDE.md 가 명시한 한계)라, 증거를 프로그램이 쓰게 하면 가드 취지(활성 작업 게이트·frozen·L-003·비밀 검사)와 충돌하지 않으면서 수작업을 없앨 수 있다.

**대책 후보(사용자가 고른다 — FIX 번호는 메인 세션이 붙인다).**

| 후보 | 내용 | 장점 | 단점·주의 |
|---|---|---|---|
| (가) 허용 목록 | `bash_write_check.py` 에 `docs/wiki/packages/*/evidence/` 를 `>`/`>>`/`tee` **만** 허용하는 예외 | 수작업 0, `cmd > evidence/x.txt` 로 원본 그대로. 변경이 가드 한 곳 | 네 가드 중 **비밀 검사**가 그 경로에서 열린다(명령 출력에 `.env` 내용이 섞이는 사고를 못 막음) — PostToolUse 로 그 폴더만 비밀 패턴 재검사하거나 `secret-guard` 를 evidence 경로에도 걸어야 한다. `sed -i`·`cp` 는 계속 막아야 함. 활성 작업 게이트는 evidence 가 제품 코드가 아니라 무관 |
| (나) 절차 고정 | 이번 U5 방식을 규칙으로: 구현 에이전트는 스크래치패드 원본 경로만 보고하고 **메인 세션이** Write 로 `-raw.txt` 보존 + 스크립트 보존, 구현자 발췌본은 선택 | 훅 무변경, 바로 적용 | 메인 세션 토큰(644행을 읽고 다시 씀)·시간 비용이 단위마다 든다. 아주 큰 출력은 분할해야 하고 여전히 사람이 옮긴다. `-mutation.txt` 와 `-raw.txt` 두 벌이 남아 어느 쪽이 권위인지 헷갈릴 수 있다 |
| (다) 대조 의무 | Write 전 스크래치패드 원본과 `wc -l`·`shasum` 을 대조해 증거 파일 머리에 적는다 | 가볍고 어떤 후보와도 겸할 수 있다 | 옮기는 구조는 그대로라 압력을 없애지 못한다. 보조 수단 |
| (라) 전용 스크립트 | `.claude/scripts/save-evidence.py <pkg> <이름> -- <명령…>` 이 명령을 실행해 stdout+stderr 전체를 ANSI 제거·머리줄(명령·시각·exit)과 함께 `evidence/<ts>-<이름>.txt` 에 쓴다. 가드의 "프로그램이 쓰는 것은 막지 않는다" 한계를 **의도된 통로**로 삼는다 | 수작업 0, 형식 통일(머리줄·exit 코드 자동), ANSI 문제도 해결. 스크립트 안에서 비밀 패턴 검사를 넣을 수 있어 (가) 의 단점을 피한다. 변이 스크립트도 같은 통로로 | 새 스크립트 1개 + `security.md`·`verification.md` 한 줄. 스크립트가 쓰는 경로를 evidence 폴더로 고정해야 하고(인자 검증), `test-guards.sh` 에 경우를 더해야 함(Mac·Windows 양쪽) |

내 권고 순서: (라) > (가)+(다) > (나). (라) 가 원인을 없애면서 비밀 검사·형식까지 가져간다. 결정 전까지는 (나).

## 7. 보안·범위

- `git status --short -- app alembic tests .github` 빈 출력 — 백엔드·CI 무변경. `git diff --diff-filter=D` 빈 출력 — 삭제 0. 라우트·앱 틀(`routes.ts`·`App.tsx`) 무변경, 화면 3개 그대로(원칙5).
- 비밀 패턴 0, 외부 호스트 URL 0(`http://x:9`·`localhost:8000` 은 테스트·기본값), `/push-dev/` 0.
- 결정 J: `test-setup.ts` 무변경(기본 fetch 는 throw), `chat.test.tsx` 는 `vi.stubGlobal('fetch')` + `afterEach(vi.unstubAllGlobals)` — 실 네트워크 0. 제품 코드의 `fetch` 호출은 `client.ts` 51행 한 곳.
- `web/src` 바깥 쓰기 없음(`git status`).

## 8. registry · 03-log

- registry U5 행 4개(채팅 화면 · 세션 보관·채팅 호출 · 프록시 대상 · 테스트) — 코드와 대조: `NOTICE` 5개 ✓, 키 `relationship.session_id` ✓, `postChat`/`postAnswer`/`getPendingQuestions` ✓, 422 버림 ✓, `resolveApiTarget` ✓, 21건/47건 ✓, 변이 13건 ✓. 해시 칸 "(U5 미커밋)" 4개는 커밋 뒤 교체. 테스트 행의 증거 경로가 발췌본(`-u5-mutation.txt`)만 가리킨다 — 원본 `-raw.txt` 도 적는 편이 맞다(R-U5-5).
- 03-log "U5 시작"(13:18) 항목은 위임 범위·R-U4-11·12·FIX-033 (c) 를 적었다. 완료 항목에 적을 것은 R-U5-5.

## 9. 소견

- **[권고] R-U5-1 · 원칙7 테스트 공백.** V1(`options` trim 주입) 살아남음, V2(정렬 주입) 전용 순서 테스트(205행)·복원 테스트(279행) 미검출. 처방: 205행 `OPTIONS` 를 정렬 순이 아니고 앞뒤·연속 공백을 가진 문자열을 포함하게 바꾼다(예: `['잘 모르겠어요', '  네, 같은 사람이에요 ', '아니요,  다른 사람이에요']`) 하고 칩 `textContent` 와 218행 `POST` 본문을 그 문자열 그대로 단언한다. 한 테스트 데이터 수정이면 두 변이가 다 잡힌다. 커밋을 막지 않는다(코드에 변환이 없음을 grep 으로 확인) — U6 위임에 끼우거나 이 커밋 전에 frontend-agent 가 고쳐도 된다.
- **[권고] R-U5-2 · 복원 실패 침묵(④).** 96행 "5xx → 한 줄 안내" 가 복원 요청을 제외하지 않으며 343행 테스트가 침묵을 고정한다. 사용자 결정: (i) 지금처럼 침묵(테스트 유지) 또는 (ii) `NOTICE.failed` 류 한 줄(343행 단언 반전). 어느 쪽이든 03-log 에 결정으로 남긴다.
- **[권고] R-U5-3 · 증거 규칙 (c) 재발 — 근본 대책 선택.** §6. 등급 이유·후보 (가)~(라)·권고 순서는 §6 에 있다. 결정 전까지 U6 위임 프롬프트에 (나) 를 명시.
- **[권고] R-U5-4 · 테스트 없는 분기 2개.** ② `sending` 중 Enter·버튼 잠금(변이 `if (!text || sending)` → `if (!text)` 가 살아남을 것 — 173행이 버튼 상태를 단언하지 않음) · ⑥ `isComposing` 분기. 둘 다 계획 밖 선택이라 값 단언 의무(FIX-033)의 직접 대상은 아니지만, 분기가 있으면 테스트가 있어야 한다(verifier 리뷰 기준 "테스트 없는 분기"). `fireEvent.keyDown(box, {key:'Enter', isComposing:true})` 와 173행에 `expect(보내기).toBeDisabled()` 한 줄씩.
- **[권고] R-U5-5 · 03-log U5 완료 항목·registry 에 적을 것.** ① 구현 안 ①~⑥ 과 이 리뷰의 판정(§2) ② (c) 재발 사실과 메인 세션 보존(`-raw.txt`·스크립트), 대책 결정 ③ U6 97행의 카드 링크를 U5 가 앞당겨 구현했음(U6 registry 행에서 중복 기재 금지) ④ R-U4-11·12 닫힘 ⑤ registry 테스트 행 증거 경로에 `-u5-mutation-raw.txt` 추가, "(U5 미커밋)" 4칸 → 해시 ⑥ Refs `P8-frontend U5 S3.4 D1 D2 원칙1 원칙7 R-U4-11 R-U4-12 R-U3-3`.

## 10. 판정 근거 요약

- 판정 명령 3개 재실행 exit 0, 47 passed, 번들 해시 구현자와 동일(`-judge.txt`).
- 96행·결정 D·E 계약 15항목 전부 코드 위치 + 값 단언 테스트 + 변이 검출로 뒷받침(§1).
- 원칙7: 서버 문자열 변환 코드 0(`-grep.txt`); 테스트 공백은 R-U5-1 로 분리(코드 결함 아님).
- 구현자 선택 ①~⑥ 계획 모순 0(§2); ④ 만 사용자 결정 거리.
- R-U4-11 실측 닫힘(`-env.txt`), R-U4-12 클래스 확인, R-U0-3 전부 충족(`-deps.txt`).
- 변이 5건 중 4건 검출 + 재실행 3건 일치 + 탐침 통과, 저장소 무수정(`-mutation.txt`).
- (c) 재발은 원본 보존으로 증거 완전 — [권고] + 대책 선택(§6).
- 보안·범위 위반 0(§7).
- **[필수] 0 → 통과.** 커밋 전 선택 사항: R-U5-1·R-U5-4 는 이 커밋에서 frontend-agent 가 고쳐도 되고 U6 에 끼워도 된다(둘 다 테스트 파일만 바뀐다).
