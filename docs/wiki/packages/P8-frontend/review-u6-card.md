# P8-frontend U6 인물 카드 화면 + 원문 펼치기 — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 (2026-10-13 18:50) — **[필수] 0, [권고] 5.** 01-plan 97행·결정 F·N 계약 14항목 전부 코드 위치 + 값 단언 테스트 + 변이 검출로 충족(§1). 판정 명령 재실행 exit 0(typecheck · 70 passed · build, 번들 `index-NxFNVU0m.css`/`index-BKYMHWv4.js` — 구현자 1629·메인 세션 1811 과 동일, `-judge.txt`). 서버 문자열(`content`·`value`·`raw_utterance`·`title`·`type`·`key`) 변환 코드 0 — grep 유일 적중 `aliases.join(', ')` 는 이어 붙이기일 뿐 각 별칭을 바꾸지 않는다(`-grep.txt`). 날짜 포맷은 `occurred_at`·`scheduled_at`·`last_contact_at` 세 필드에만(`-grep.txt` "formatDate 호출 인자" 5건). 서버 순서 보존: 목록·타임라인·사실·패턴·일정·근거 전부 응답 배열을 그대로 `map`(재정렬·재절단 0) — 구현자 M1·M6 재실행이 실패 이름·건수까지 구현자 표와 동일. 내 변이 4건 전부 검출(V2 섹션 누락·V3 근거 순서·V4 404↔500·V5 사이드바 다른 컴포넌트), 탐침 P1(카드·목록 응답에 원문을 몰래 실어도 미표시) 통과. 탐침 P2·P3 가 결함 2개를 드러냈으나 둘 다 97행 계약 문장 밖의 경계·신선도 문제라 [권고](R-U6-1·2). R-U5-1·2·4 닫힘(§5, M9·M10·M11·M12·M13 검출 + M10 재실행 동일). R-U0-3: package·lock 바이트 동일, scripts 7개 무변경, `npm audit --omit=dev` 0, `?raw` 는 저장소 안 소스 2파일만(`-deps.txt`). 증거는 전부 `save_evidence.py` 통로(머리줄 5개·`# exit`)지만 변이 스크립트가 vitest 출력을 요약하고 스크립트 원문이 스크래치패드에만 있었다 — [권고] R-U6-3, 내가 원문을 보존함. 보안·범위 위반 0(§7).
대상: 작업 트리(기준 HEAD `1944369`) — `git diff -- web` 5파일(`chat.test.tsx` 28/10 · `client.ts` 31/1 · `AppShell.tsx` 5/2 · `ChatScreen.tsx` 3/1 · `PersonCardScreen.tsx` 330/2) + 신규 `web/src/components/PersonList.tsx`(66행)·`web/src/lib/format.ts`(14행)·`web/src/__tests__/card.test.tsx`(414행) · `docs/wiki/registry.md` U6 행 3개 · 구현 증거 `evidence/20261013-1627-u6-card.txt`·`-1627-u6-mutation.txt`(15변이)·`-1628-u6-card.txt`(exit 1, 중간)·`-1628-u6-mutation-m1-rerun.txt`(중간)·`-1629-u6-card.txt`(최종)·`-1629-u6-mutation-m1-rerun.txt`(최종) · 메인 세션 `-1811-u6-main-recheck.txt`. `HANDOFF.md`·`journal.md`·`03-log.md` 변경은 대상 아님(03-log 맨 끝 "U6 시작" 은 근거 문서).
근거 문서: `01-plan.md` 97행(U6) · 결정 F(267~275행)·L(305~329행)·N(330~346행) · 36~49행(하지 않는 것) · 52~80행(파일 목록) · 판정표 114행(ㄴ 해석)·144~145행(18·19행) · 불변식 4·9·10(358~367행) · `docs/proposal.md` 318~343행(부록 A ② 카드 그림) · `app/api/schemas.py` 312~374행(`PersonListItemOut`·`PersonCardOut` — 원문 필드 없음)·377~407행(`EventRawOut`·`FactSourcesOut`) · `app/api/read.py` 134~135·157·198·224~225·235~236행(서버 정렬·상한) · CLAUDE.md 원칙5·7 · `review-u5-chat.md` R-U5-1·2·4 · `review-u0-harness.md` R-U0-3 · `docs/wiki/verification.md` "변이 시험 방법".

내 증거(전부 `save_evidence.py` 통로, `docs/wiki/packages/P8-frontend/evidence/`):
- `20261013-1843-verifier-u6-judge.txt` — `cd web && npm run typecheck && npm test -- --run && npm run build` exit 0, 5 files · 70 passed, 번들 해시 구현자와 동일.
- `20261013-1843-verifier-u6-deps.txt` — package.json·lock `git diff --quiet` exit 0, scripts HEAD/작업 트리 동일, `npm audit --omit=dev` 0, `?raw` import 2건의 대상 파일 경로·크기, 타입 선언은 `tsconfig.app.json` `vite/client`. (파일 머리 `# exit: 2` 는 마지막 `grep` 이 없는 `vite-env.d.ts` 를 찾은 결과 — 판정과 무관.)
- `20261013-1843-verifier-u6-grep.txt` — 원칙7 변환 grep · 날짜 포맷 호출 인자 · `raw_utterance` 사용처(불변식 4) · 불변식 9·10 · 외부 URL · `/push-dev/` · 라우트·앱 틀 무변경 · 범위(`app/alembic/tests/.github`) · 삭제 · `test-setup.ts` 무변경 · `git status` · numstat · 비밀 · 고정 문구 24개 · 상담·감정 어휘.
- `20261013-1847-verifier-u6-mutation.txt`(2664행) — V0 대조군 + 내 변이 V2~V5 + 구현자 M1·M3·M6·M10 재실행 + 탐침 P1~P3. vitest 출력 전체(`DEBUG_PRINT_LIMIT=0` 으로 DOM 덤프만 끔), 실행마다 끝에 `git status --short -- web` 으로 저장소 무수정 확인.
- `20261013-1848-verifier-u6-mutation-scripts.txt` — 구현자 `mut_u6.py` 와 내 `vmut_u6.py`·탐침 3파일 원문(줄 수·sha256 앞 16자리) — 스크래치패드는 세션과 함께 사라지므로 재현용 보존.

## 1. 01-plan 97행 · 결정 F·N 계약 대조

| # | 계약(97행 / 결정) | 구현 | 테스트·변이 | 판정 |
|---|---|---|---|---|
| 1 | `#/persons` 목록 — 이름·태그·위계·마지막 접촉 4필드 | `PersonList.tsx` 50~60행 `data-field` name/tag/hierarchy/last-contact, `last_contact_at` null → `PERSON_LIST_NOTICE.noContact` | `card.test.tsx` 100행(4필드 값 전부) · 구현자 M14 검출 | ✓ |
| 2 | 필터 컨트롤 없음 | `PersonList.tsx` 에 input·select 0 | 115행(textbox·searchbox·combobox 0) | ✓ |
| 3 | 결정 N: 같은 목록 컴포넌트를 사이드바 아래에도 | `AppShell.tsx` 5행 `import PersonList from '@/components/PersonList'`·37행 `<PersonList onNavigate={onNavigate} />`; `PersonCardScreen.tsx` 15행 같은 import·333행 `<PersonList />` | 148행(`innerHTML` 동일·본문 1·사이드바 1) · 166행(import 문자열 동일) · 172행(서랍 닫힘) · 구현자 M15 검출 · **내 V5**(바이트 동일 사본 `PersonList2` 로 교체) 검출(166행) | ✓ |
| 4 | 새 API·새 라우트 없음 | `client.ts` 100~116행 4함수는 U1·U2 엔드포인트(`/persons`·`/persons/{id}`·`/events/{id}/raw`·`/persons/{id}/facts/{fid}/sources`); `routes.ts`·`App.tsx`·`main.tsx`·`index.html` diff 0; 불변식 10 → `AppShell.tsx` 1파일 | `-grep.txt` | ✓ |
| 5 | `#/persons/:id` 카드 — 부록 A ② 순서 | `PersonCardScreen.tsx` 249~315행 `data-section` header → aliases → last-contact → facts → patterns → timeline → schedules = 그림 318~343행 순서. 제목 글자도 그림과 같다("알고 있는 것"·"반복 패턴 ⚠"·"타임라인"·"다가오는 일정") | 191행(DOM 순서 7개 + h2 순서) · 구현자 M2 검출 · **내 V2**(별칭 단락 누락) 3건 검출 | ✓ |
| 6 | 타임라인 펼치기 → `GET /api/events/{id}/raw` 1회 | `TimelineItem` 109행 `getEventRaw(event.id)`, `useLazyDetail` 78행 `if (state.status === 'idle') run()` | 292행(1회·GET) · 313행(항목마다 각자 1회) · 구현자 M4 검출 | ✓ |
| 7 | 원문 글자 그대로 | `RawText` 100행 `whitespace-pre-wrap` + `{text}`(React 이스케이프, `innerHTML`/`dangerouslySetInnerHTML` 제품 코드 0). 변환 grep 0 | 301행 `RAW_A`(앞뒤 공백·`\n\n`·`\t`·`<b>`·`&`) `textContent` 완전 일치 · 구현자 M3 검출(내 재실행 2건 동일) | ✓ |
| 8 | 다시 펼쳐도 재요청 없음 | 78행 — `done` 이면 `run()` 안 함, 데이터는 항목 상태에 | 308~310행 · M4 | ✓ |
| 9 | "근거 보기" → `GET /api/persons/{id}/facts/{fact_id}/sources` 1회 | `SourcesToggle` 149행, `source_count <= 0` 이면 버튼 없음(151행) | 356행(1회·2건·날짜·content·원문)·380행(패턴 id)·240행(0 이면 버튼 없음) · 구현자 M7 검출 · **내 V3**(sources 뒤집기) 검출 | ✓ |
| 10 | 접기 | `Collapsible open={open}` 제어, 닫히면 Radix 가 내용 언마운트 | 305~306·373~374행(접으면 `raw-utterance`/`sources-11` 없음) | ✓ |
| 11 | 조회 실패 시 그 항목에만 안내 (+ 재시도) | `DetailStatus` 86~91행 `role=alert` 가 `CollapsibleContent` 안; `toggle` 75행 error 면 `run()` | 330행(alert 1개뿐·카드 유지·다른 항목 없음·재시도 2회)·394행 · 구현자 M5(포털로 body 에)·M8(재시도 대신 접기) 검출 | ✓ 주 경로 / 경계 결함 R-U6-1 |
| 12 | 404 처리 | `CardView` 227행 `e instanceof ApiError && e.status === 404 ? 'not_found' : 'failed'` → `CARD_NOTICE.notFound` + `#/persons` 링크 | 267행(404)·275행(500 은 다른 문장) · **내 V4**(404→500) 2건 검출 | ✓ |
| 13 | 채팅 `stored.persons/events > 0` → 카드 링크 | U5 에서 구현(`review-u5-chat.md` §1 14행), U6 재작성 0 — registry 비고 "재작성 안 함" 과 일치 | — | ✓ |
| 14 | 판정 `npm test -- --run src/__tests__/card.test.tsx` · 증거 `*-u6-card.txt` | 구현자 `-1629-u6-card.txt` exit 0(22 + 전체 70 + build) · 메인 `-1811` · 내 `-judge.txt` 70 passed | — | ✓ |

**결정 F(원문은 펼칠 때만)**: `types.ts` 53~105행(`PersonListItemOut`·`PersonCardOut`)에 `raw_utterance` 없음 = `schemas.py` 312~374행과 일치; `raw_utterance` 사용처는 원문 타입 2개·`RawText` 호출 2곳·테스트뿐(불변식 4, `-grep.txt`). 283행 테스트(카드만 열면 요청 `/api/persons/3` 1건, 원문 0) + **내 탐침 P1**: 카드 응답의 `person`·최상위·`facts`·`patterns`·`timeline`·`upcoming_schedules` 6자리와 목록 응답에 `raw_utterance` 를 몰래 실어도 `textContent`·`innerHTML` 어디에도 없고 원문 요청 0 — 2 passed(`-mutation.txt` "P1").

**서버 순서 보존**: `read.py` 157행(목록 `last_contact desc nulls_last, id asc`)·224행(타임라인 `occurred_at desc, id desc` 상한 20)·134행(근거 `occurred_at desc` 상한 20)·198행(사실 `updated_at desc`)·235행(일정 `scheduled_at asc` 상한 10) — 프론트는 `persons.map`·`card.facts.map`·`card.patterns.map`·`card.timeline.map`·`card.upcoming_schedules.map`·`sources.map` 전부 응답 배열 그대로, `.sort/.reverse/.slice/.filter` 0(`-grep.txt`). 테스트 데이터는 날짜·이름·id 어느 정렬과도 다르게 골라져 있다(43~48행 `PERSONS` 는 9/1 → 10/5 → null, 65~69행 타임라인은 8/21 → 9/3 → 7/28). 구현자 M1(목록 이름순)·M6(타임라인 뒤집기) 재실행: M1 3 failed · M6 1 failed — 구현자 1629 재실행·1627 표와 이름·건수 동일.

TS 타입: `client.ts` 가 쓰는 `PersonListItemOut`·`PersonCardOut`·`EventRawOut`·`FactSourcesOut` 과 하위 7모델은 `types.ts` 53~135행 — `schemas.py` 312~407행과 필드·null 가능성 일치(U4 전수 대조 유지, 이번 변경 없음).

## 2. 구현자 판단 ①~③ 의 계획 적합성

| # | 구현 안 | 계획 대조 | 판정 |
|---|---|---|---|
| ① | 고정 문구 `PERSON_LIST_NOTICE` 3개 + `CARD_NOTICE` 21개 | 전부 빈 상태·오류·라벨·버튼 글자·로딩 라벨(`-grep.txt` 목록). 서버 문장을 대신하는 것 0 — `type`·`key`·`hierarchy` 는 원값 그대로(`직장 · 상`, 그림의 "상급자" 로 한글 매핑하지 않음 — 원칙7, 03-log 보고와 일치). 상담·감정 어휘 0. 섹션 제목 4개는 기획서 그림과 글자 동일. `detailFailed` "원문을 불러오지 못했어요" 가 근거 보기 실패에도 쓰이는데 근거도 원문이라 어긋남 없음 | 적합 — 기록. `hierarchy` 원값 표시는 U10 사람 점검에서 "상급자" 같은 표기를 원하면 수정 1회 상한 안(결정 L) |
| ② | 날짜 절대 표기(`Intl.DateTimeFormat('ko-KR', dateStyle medium)` → "2026. 9. 3.", 일정은 `timeStyle short`) — 그림의 "3일 전"·"09/03"·"09/10 (화) 15:00" 과 다름 | 97행은 "(부록 A ② **순서**)" 만 계약이고 판정표 18·19행·결정 L 어디에도 날짜 표기 규칙이 없다. "3일 전" 은 현재 시각 의존(작업 단위 머리글 "프론트 가짜 시계로 고정" 은 시계를 쓸 때의 규칙이지 상대 표기 요구가 아님). 절대 표기는 시계 없이 결정적이고 테스트가 UTC 정오로 시간대 독립(2행 주석). 파싱 불가 문자열은 그대로 돌려줌(`format.ts` 5행) — 서버 문장 훼손 0 | 모순 없음 — 기록. 그림과의 차이는 U10 에서 사용자가 보고 정한다(수정 1회 상한) |
| ③ | `PersonList` 두 곳 마운트 → `#/persons` 에서 `GET /persons` 2회 | 계획에 공유 캐시 없음. 읽기 전용·trace 0(U1) 이라 비용은 요청 1회. **그러나 탐침 P2 가 더 중요한 것을 드러냈다**: 데스크톱 `<aside>`(`AppShell.tsx` 56~59행)는 라우트가 바뀌어도 언마운트되지 않아 사이드바 `PersonList` 의 `useEffect(…, [])`(20행)가 **앱 마운트 때 한 번만** 돈다 → 채팅으로 새 인물이 생겨도 사이드바는 새로고침 전까지 옛 목록(모바일 서랍은 열 때마다 마운트라 신선). 결정 N 346행 이유 "데스크톱에서 대화 중에도 인물 목록이 보여 데모 1~2단계(채팅 → 카드 채워짐)를 한 화면 폭에서" 와 맞물린다 | 2회 자체 = 기록(계약 위반 아님). 신선도 = **R-U6-2 [권고]**, 사용자 결정 |

## 3. 탐침으로 드러난 결함 2개 (둘 다 97행 문장 밖 — [권고])

- **P3 — `useLazyDetail.toggle` 경계(`PersonCardScreen.tsx` 74~79행).** 펼치기(로딩 중) → 접기 → 요청 실패 → 다시 "원문 펼치기" 클릭: 75행 `if (state.status === 'error') return run()` 이 `open` 을 켜지 않아 **요청만 한 번 더 나가고 항목은 열리지 않는다**(버튼 이름도 "원문 펼치기" 그대로, 접힌 동안 실패 안내는 `CollapsibleContent` 언마운트로 보이지 않음). 한 번 더 누르면 `done` 상태라 열린다. 실측: `[P3] 접힌 채 실패 뒤 alert 보임 = false`, `4) 뒤 요청 수 = 2`, `원문 보임 = false`, `버튼 이름 = 원문 펼치기`(`-mutation.txt` "P3"). 주 경로(열린 채 실패 → 안내 → 재시도)는 330·394행 테스트가 고정하고 있다. 처방은 R-U6-1.
- **P2 — 데스크톱 사이드바 목록 신선도.** `#/chat` 에서 앱을 열어 사이드바가 `[첫째]` 를 받은 뒤 `#/persons` 로 옮기면 본문 목록은 새 응답 `[둘째, 첫째]` 를 받지만 사이드바는 `[첫째]` 그대로. 실측: `GET /persons 호출 수 = 2`, `본문에 둘째 = true`, `사이드바에 둘째 = false`(`-mutation.txt` "P2"). 처방은 R-U6-2.

## 4. 변이 시험 (`-mutation.txt`, 저장소 무수정 — 실행마다 `git status --short -- web` 이 U6 작업 트리 그대로)

| 변이 | 기대 | 결과 |
|---|---|---|
| V0 대조군 | 70 passed | 70 passed |
| V2 별칭 단락(`data-section="aliases"`) 삭제 | 섹션 순서 테스트 실패 | **3 failed**(191·209·249행) |
| V3 근거 `[...sources].reverse()` | 356행 실패 | **1 failed**(356행 — `items[0]` 에 '2026. 8. 21. · 점심 같이 함' 기대) |
| V4 `e.status === 404` → `=== 500` | 404·500 테스트 둘 다 실패 | **2 failed**(267·275행) |
| V5 사이드바가 바이트 동일 사본 `PersonList2` 를 import | 166행 import 문자열 테스트 실패 | **1 failed**(166행). 148행 `innerHTML` 동일 테스트는 사본이라 통과 — import 동일성 테스트가 이 경우를 가르는 유일한 단언 |
| M1 재실행(목록 이름순) | 구현자 1629: 3 failed | 3 failed — 이름 동일(100·137·148행) |
| M3 재실행(원문 trim) | 구현자: 2 failed | 2 failed — 이름 동일(292·330행), 단언 메시지에 앞뒤 공백 소실이 그대로 보임 |
| M6 재실행(타임라인 뒤집기) | 구현자: 1 failed | 1 failed — 227행 |
| M10 재실행(칩 정렬, R-U5-1) | 구현자: 3 failed | 3 failed — 218·231·238행, `OPTIONS` 비정렬이라 첫 테스트가 직접 가른다 |
| P1 탐침(원문 몰래 실음) | 통과 | 2 passed |
| P2 탐침(사이드바 신선도) | 바람직 동작 단언 → 실패하면 stale | **실패** → stale 확인 |
| P3 탐침(로딩 중 접기 → 실패 → 펼치기) | 바람직 동작 단언 → 실패하면 결함 | **실패** → 결함 확인 |

구현자 표 신뢰성: 재실행 4건이 실패 테스트 이름·건수까지 1627 표·1629 재실행과 동일. 15종 전부 검출(M1 은 1629 재실행 기준)을 신뢰한다. 참고: 1627 표의 M1 "살아남음" 은 테스트 데이터가 이름순과 우연히 같았던 것이고, 1628 중간 산출물은 데이터 1차 수정이 137행 링크 테스트의 인덱스를 함께 고치지 않아 `expected '#/persons/9' to be '#/persons/4'` 로 exit 1 이 난 흔적이다(1628 m1-rerun 의 3 failed 에는 그 기준선 실패가 섞여 있다) — 1629 쌍이 최종이고 registry 가 1629 를 가리키므로 문제 없음, 03-log 한 줄 권고(R-U6-5).

## 5. R-U5-1 · R-U5-2 · R-U5-4 닫힘

- **R-U5-1 닫힘.** `chat.test.tsx` 216행 `OPTIONS = ['  잘 모르겠어요', '아니요,   다른 사람이에요 ', '네, 같은 사람이에요  ']` — 코드포인트 순(`' '` < `'네'` < `'아'`)이 아니고 앞·뒤·연속 공백 포함. 218행이 `textContent` 배열을 `OPTIONS` 와 `toEqual`, 231행이 `POST` 본문 `{answer: OPTIONS[1]}` 와 `chosen.textContent` 를 그대로 단언(접근 이름이 공백을 정리하므로 순서로 집는다는 주석 포함). 구현자 M9(trim)·M10(정렬) 검출, 내 M10 재실행 동일.
- **R-U5-2 닫힘.** `ChatScreen.tsx` 19행 `NOTICE.restoreFailed`, 139~140행 `.catch(() => { if (alive) setNotice(NOTICE.restoreFailed) })`. 361행 테스트가 `role=alert` 에 그 문장 + 빈 상태 안내 유지. 구현자 M11 검출.
- **R-U5-4 닫힘.** 183~189행 — 보내는 중 글자를 더 써도 보내기 버튼 `toBeDisabled()`, 응답 뒤 `toBeEnabled()`; 192~198행 — `fireEvent.keyDown(…, {key:'Enter', isComposing:true})` 뒤 `/api/chat` 0회. 구현자 M12·M13 검출. 남은 작은 틈: 전송 중 **Enter** 경로(`if (!text || sending)`)는 버튼과 달리 단언이 없다 — R-U6-4 에 묶음.

## 6. R-U0-3 고정 점검 · `?raw` (`-deps.txt`)

`git diff --quiet -- web/package.json web/package-lock.json` exit 0 — 새 패키지 0. scripts 7개 HEAD 와 동일(`dev/build/typecheck/test/e2e/lint/preview`, 셸 전용 명령 0). `npm audit --omit=dev` "found 0 vulnerabilities". `lucide-react` `ChevronDownIcon`·`TriangleAlertIcon`, shadcn `badge·button·card·collapsible·skeleton` 은 U4 기존 부품(새 `shadcn add` 0). `?raw` import 2건(`card.test.tsx` 9~10행)은 `@/components/AppShell.tsx`·`@/screens/PersonCardScreen.tsx` — `@` 별칭 = `web/src`, 저장소 안 소스 2파일(3488·11710 바이트)의 본문 문자열을 Vite 가 테스트 번들에 넣는다. 저장소 밖 파일·`.env`·비밀 접근 0. 타입은 `tsconfig.app.json` `types: ["vite/client", …]` 의 `*?raw` 선언. 단 이 테스트는 import 문장의 **글자**(따옴표·공백)에 묶여 있어 포매터가 바꾸면 깨진다 — 기록(V5 가 보여 주듯 실질 효용은 있다).

## 7. 보안·범위

- `git status --short -- app alembic tests .github` 빈 출력 — 백엔드·CI 무변경. 삭제 파일 0. `routes.ts`·`App.tsx`·`main.tsx`·`index.html` diff 0 — 라우트 3개·화면 3개 그대로(원칙5), 불변식 10 `AppShell.tsx` 1파일.
- 비밀 패턴 0, 외부 URL 0, 외부 글꼴·CDN 0(불변식 9), `/push-dev/` 0.
- 결정 J: `test-setup.ts` 무변경(기본 `fetch` 는 throw), `card.test.tsx` 는 `vi.stubGlobal('fetch')` + `afterEach(vi.unstubAllGlobals)` + `router` 가 표 밖 요청을 throw — 실 네트워크 0.
- 원문 표시는 React 텍스트 노드(`innerHTML`·`dangerouslySetInnerHTML` 제품 코드 0) — `<b>`·`&` 가 든 RAW_A 가 글자 그대로 보이고 해석되지 않는다.
- `web/src` 바깥 쓰기 없음(`git status`).

## 8. 증거 규칙 (c) · registry · 03-log

- **증거 통로**: 구현자 증거 7파일 전부 `save_evidence.py` 머리줄 5개 + `# exit` — Write 옮겨 적기 0(FIX-034 첫 적용 성공). **그러나** `mut_u6.py` 가 `capture_output=True` 로 vitest 출력을 받아 "실패 테스트:" 줄과 `Tests` 합계만 인쇄한다(`-mutation-scripts.txt` 에 원문) — evidence 에 남은 것은 **스크립트의 요약**이지 vitest 출력 전체가 아니다(변이당 ~14행). R-U3-3 의 "변이마다 테스트 출력 전체" 취지에는 미달이나, 판정에 필요한 정보(실패 이름·건수)는 있고 내 재실행 4건이 전부 일치하므로 표를 신뢰한다. 스크립트가 스크래치패드에만 있어 재현 경로가 세션과 함께 사라지는 문제는 내가 `-1848-verifier-u6-mutation-scripts.txt` 로 닫았다. 등급 [권고] R-U6-3.
- 중간 산출물 1627·1628 보존: 문제 아님 — 과정(M1 생존 → 데이터 수정 → 1차 수정 실패 → 2차 수정)을 숨기지 않은 것이고 registry 는 최종(1629)을 가리킨다.
- registry U6 행 3개 — 코드와 대조: `PERSON_LIST_NOTICE` 3개 ✓ · `CARD_NOTICE` 고정 문장/버튼 글자 ✓ · 섹션 7개 순서 ✓ · `useLazyDetail` 1회 조회·캐시·항목 안 실패·재시도 ✓ · 404 안내+목록 링크 ✓ · `format.ts` ✓ · `client.ts` 4함수 ✓ · `restoreFailed` ✓ · 22건 + 이월 3건 보강 → 70건 ✓ · 변이 15건(M1 재실행 포함) ✓ · 증거 경로 1627·1629 ✓. "(U6 미커밋)" 3칸은 커밋 뒤 해시.
- 03-log "U6 시작"(16:22) 항목의 구현 결과 문단 — 내 확인과 일치("한글 매핑 없음", "`GET /persons` 2회 — verifier 판정", "(c) 미달 0" 은 통로 기준으로는 맞고 요약 문제는 위). 완료 항목에 적을 것은 R-U6-5.

## 9. 소견

- **[권고] R-U6-1 · `useLazyDetail.toggle` error 분기가 `open` 을 켜지 않는다**(`PersonCardScreen.tsx` 75행, 탐침 P3). 처방: 75행을 `if (state.status === 'error') { setOpen(true); return run() }` 로(또는 error 분기 전에 `open` 을 먼저 처리). 테스트는 탐침 P3(`-mutation-scripts.txt` 의 `zz_probe_p3.test.tsx`)를 `card.test.tsx` 에 그대로 옮기면 된다 — 지금 코드에서 실패하고 처방 뒤 통과. 코드 1줄 + 테스트 1건이라 이 커밋에서 frontend-agent 가 고쳐도, U7 에 끼워도 된다. 커밋을 막지 않는다(주 경로는 330·394행이 고정).
- **[권고] R-U6-2 · 데스크톱 사이드바 인물 목록 신선도**(`PersonList.tsx` 20행 `useEffect(…, [])` + `AppShell.tsx` 56~59행 영구 마운트, 탐침 P2). 채팅으로 새 인물이 생겨도 데스크톱 사이드바는 새로고침 전까지 옛 목록이다 — 결정 N 346행의 데모 이유와 U10 체크리스트 20항에서 드러날 가능성이 크다. 사용자 결정: (i) 지금 그대로 두고 U10 에서 본다(수정 1회 상한 안) (ii) `PersonList` 가 `hashchange` 때 재조회 — 작은 변경, 요청은 여전히 2회 (iii) `AppShell` 이 한 번 조회해 사이드바·본문에 내려주고 채팅 `stored.persons > 0` 뒤·라우트 변경 때 재조회 — 구현자 판단 ③(`GET /persons` 2회)도 함께 1회로. 계획 변경 아님(97행·결정 N 문장 그대로). 어느 쪽이든 03-log 에 결정으로.
- **[권고] R-U6-3 · 변이 증거가 스크립트 요약(실패 이름·합계)이고 스크립트가 스크래치패드에만 있었다.** 통로(`save_evidence.py`)는 맞다. 다음 단위부터 변이 스크립트는 `capture_output` 없이 vitest 출력을 그대로 흘리고(내 `vmut_u6.py` 방식), 스크립트 원문을 `save_evidence.py … -- cat <스크립트>` 로 evidence 에 남긴다. 이번 것은 `-1848-verifier-u6-mutation-scripts.txt` 가 대신한다 — registry 테스트 행·03-log 에 그 경로를 적는다.
- **[권고] R-U6-4 · 테스트 데이터·단언 작은 틈 3개.** ① 별칭 `['팀장', '우리 팀장님', '부장님']`(57행)에 앞뒤 공백이 없어 `aliases.map(a => a.trim())` 류 변이가 살아남는다(정렬 변이는 216행 완전 일치로 잡힘) — 한 별칭에 `'  부장님 '` 처럼 공백을 넣고 216행 기대값을 그대로 맞춘다. ② R-U5-4 의 전송 중 **Enter** 경로 단언 없음(버튼만) — 183행 테스트에 `await user.keyboard('{Enter}')` 뒤 `/api/chat` 1회 유지 한 줄. ③ `type`·`key` 는 `toContain('meal')`·`getByText('child')` 라 소문자 변환 변이가 살아남지만 서버 집합이 소문자 고정이라 실질 위험 0 — 기록만.
- **[권고] R-U6-5 · 03-log U6 완료 항목·registry 에 적을 것.** ① 구현자 판단 ①~③ 과 이 리뷰 판정(§2) — 특히 절대 날짜 표기·`hierarchy` 원값 표시는 U10 에서 사용자가 보고 정한다는 것 ② 1628 중간 산출물의 뜻(데이터 1차 수정이 137행 인덱스를 안 맞춰 exit 1 → 2차 수정, 1629 가 최종) ③ R-U6-1·2 의 사용자 결정 ④ `-1848-verifier-u6-mutation-scripts.txt` 참조와 R-U6-3 운용 규칙 ⑤ "(U6 미커밋)" 3칸 → 해시 ⑥ Refs `P8-frontend U6 R8 S3.5 원칙7 FIX-034 R-U5-1 R-U5-2 R-U5-4`.

## 10. 판정 근거 요약

- 판정 명령 3개 재실행 exit 0, 70 passed, 번들 해시 구현자·메인 세션과 동일(`-judge.txt`).
- 97행·결정 F·N 계약 14항목 전부 코드 위치 + 값 단언 테스트 + 변이 검출(§1). 섹션 7개 순서는 DOM 순서로 단언(191행) + 누락 변이 검출.
- 원칙7·결정 F: 서버 문자열 변환 코드 0, 날짜 포맷은 3필드만, 원문은 두 엔드포인트로만·몰래 실어도 미표시(P1)(`-grep.txt`·`-mutation.txt`).
- 서버 순서 보존: 재정렬·재절단 코드 0 + M1·M6 재실행 동일.
- 구현자 판단 ①~③ 계획 모순 0(§2); ③ 에서 파생된 신선도 문제는 [권고].
- R-U5-1·2·4 닫힘(§5), R-U0-3 전부 충족·`?raw` 저장소 안 2파일(§6).
- 변이 4건 전부 검출 + 재실행 4건 일치 + 탐침 3건(통과 1·결함 2), 저장소 무수정(`-mutation.txt`).
- 보안·범위 위반 0(§7). 증거 통로 FIX-034 준수, 요약·스크립트 보존 문제는 [권고](§8).
- **[필수] 0 → 통과.** 커밋 전 선택 사항: R-U6-1 은 코드 1줄 + 테스트 1건이라 이 커밋에서 고쳐도 되고 U7 에 끼워도 된다. R-U6-2 는 사용자 결정 뒤.
