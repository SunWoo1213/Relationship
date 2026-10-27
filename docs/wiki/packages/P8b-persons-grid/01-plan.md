# P8b-persons-grid · 계획 (01-plan)

상태: 초안 개정 2(architect 초안 2026-10-21 → **사용자 확정 2026-10-21: 결정 K (나) · A~J 전부 추천안** — 메인 세션이 확정 칸·U0·판정 1·8행·수용 기준을 (나) 기준으로 고쳤고 D15·CR-003·backlog 를 같은 커밋에서 보정 → verifier 02-plan-verify **통과**(2026-10-27, [필수] 0 · [권고] R-1~R-9) → 개정 2: R-1 판정 1행 D15 인용 보완 · R-2 65행 (가) 잔존 제거 · R-3 INDEX 77행 · R-4 판정 8행 `tests/` diff · R-5 U1 testid 고정 · R-6 U1 리스크 4 기본값 (a) · R-7 U0 registry 61행·별칭 정렬·N+1 판정 · R-8 12행 grep · R-9 10행 기준선 — 판정 결과를 바꾸는 항목 없음) | 담당: frontend-agent(sonnet, `web/` 만) · backend-agent(sonnet, U0 만) · 검증 verifier(fable) · 메인 세션(U5 사람 점검 진행·D15 갱신 이력·03-log) | 작성: 2026-10-21
태그 — 패키지: P8b-persons-grid · 닫는 검증: 없음(INDEX 77행 패키지 표 "닫는 R —") · 기대는 결정: D15 (+ P8-frontend 01-plan 결정 L·결정 N) · 구현하는 명세: 없음(S 카드 무변경 — D15 "S 카드: 무변경") · 관련 원칙: 원칙5 원칙7 원칙8 · 변경 요청: CR-003 · 이어받는 소견: R-U10C-3 · R-U10R-10
의존: P8-frontend 04-review 완료 — **충족**(2026-10-21, `packages/P8-frontend/04-review.md` 결과 완료, 커밋 `fe76931`). P4 게이트는 P8 이 이미 통과(P4b-er-redesign 04-review 완료, P8 01-plan 5행).

- 근거 해시(`.claude/gitlog.md` 스냅샷 2026-10-21 22:20, Bash 없이 읽음 — L-001): 작업 브랜치 `dev2` HEAD = `fe76931`(P8 완료 처리), 그 앞 `75cb4ad`(CR-003 문서 이행), **`3bd5025`(P8 마지막 제품 코드 커밋 — 인물 화면 정렬 수정 1회, 상세 `card-wrap` 가운데 75%)**, `735f391`(FIX-035). `3bd5025..fe76931` 두 커밋은 문서뿐이다(커밋 제목 기준 — verifier 가 02 에서 `git diff --stat 3bd5025..HEAD -- app alembic web` 로 확인).
- **이 패키지의 무변경 diff 기준 해시 = `3bd5025`.** R-U10R-10(P8 04-review §6 271행 "다음 패키지 계획이 '무변경 diff' 를 쓸 때는 기준 해시를 마지막 FIX 커밋 뒤로 두거나 … `git diff --stat <fix>..HEAD` 로 적도록")에 따라, FIX-035(`735f391`)보다 뒤인 `3bd5025` 를 기준으로 **`git diff --stat 3bd5025..HEAD -- app alembic` 가 빈 출력**인지로 백엔드 무변경을 판정한다.
- 태그 `P8b-persons-grid` 커밋은 스냅샷에 없다(패키지 시작 전). 이력이 더 필요하면 메인 세션에 **`bash .claude/scripts/gitlog.sh P8b-persons-grid CR-003 D15` 실행 요청**.
- 스냅샷 시점 미커밋 변경: `docs/wiki/HANDOFF.md`·`docs/wiki/journal.md`(문서). 제품 코드 0.

### ⚠ D15 전제 불일치 — 코드에서 확인한 사실 (결정 K, 선결)

D15 결정 2 는 "검색·자르기는 프론트에서 한다(`GET /persons` 결과 전체를 이미 받음 — 새 API·새 쿼리 파라미터 없음)" 이고, 결정 1·2 는 타일에 별칭 1~2개·**별칭 부분 일치 검색**을 요구한다. 그런데 **`GET /persons` 응답에는 별칭이 없다.**

- `app/api/schemas.py` 312~319행 `class PersonListItemOut` = `id, display_name, relation_tag, hierarchy, last_contact_at` 5필드뿐.
- `web/src/api/types.ts` 53~59행 `PersonListItemOut` 도 같은 5필드. `aliases: string[]` 는 카드 응답 `PersonCardOut`(types.ts 99행, schemas.py 362행)에만 있다.
- `web/src/api/client.ts` 107행 `getPersons()` 인자 없음 → `/persons`.

그래서 D15 의 세 문장 — ① 별칭 검색·타일 별칭(결정 1·2) ② "백엔드 diff 0"(D15 코드 규칙 1번째 줄, backlog 89행 수용 기준) ③ "새 API 없음" — 을 동시에 지키는 방법은 "인물마다 기존 카드 API 를 부르는 것"(K-(가)) 하나뿐이었다. **사용자 확정(2026-10-21): 결정 K = (나)** — `GET /persons` 응답에 `aliases` 1필드(읽기 전용)를 더한다. 그래서 D15 코드 규칙 1번째 줄·D15 결정 2·CR-003 §2·backlog 89행을 "백엔드 변경은 `aliases` 필드 추가뿐" 으로 보정했다(CR-003 §2 가 예고한 "(나) 응답 1필드 추가(읽기 전용, 스키마 아님)" 갈래의 채택이라 새 CR 이 아니다 — D15 갱신 이력에 기록). ③ "새 API 없음" 은 그대로다(새 엔드포인트·쿼리 파라미터 없음). 아래 작업 단위·판정 표는 (나) 기준이다.

## 목표

CR-003(사용자 승인 2026-10-16)과 그것을 고정한 결정 카드 D15 를 코드로 옮긴다. 기획서 2장 범위 표의 포함 칸 "인물 카드 (사실 · 타임라인 · 마지막 접촉)" 안의 변경이고(CR-003 §1 "포함 칸 … 안의 변경이다"), 기획서 본문은 인물 화면의 **배치**를 정하지 않는다(CR-003 §1). 사용자 요구(U10 사람 점검 2026-10-16) — "인물 카드들을 왼쪽에 나열하지 않고 인물카드란을 만들어서 거기서 검색해서 찾아볼 수 있게", "왼쪽에 나열된건 최근에 수정한 5명 정도만", "진짜 카드처럼 클릭해서 볼 수 있게" — 를 실현한다. 구체적으로: `#/persons` 를 세로 목록에서 **카드 그리드 + 검색창 1개**로 바꾸고(타일을 누르면 기존 상세 `#/persons/:id`), 사이드바 인물 목록을 **최근 5명(`GET /persons` 서버 순서 앞 5명) + "전체 보기 →"** 로 줄인다. 예: 인물이 12명이면 사이드바에는 마지막 접촉이 최근인 5명과 "전체 보기 →" 가 보이고, 그 링크로 `#/persons` 에 가면 12장의 타일이 데스크톱 2~3열로 깔린다. 검색창에 "선영" 을 치면 `display_name` 또는 별칭에 "선영" 이 들어간 타일만 남는다(서버 문자열은 그대로 보인다 — 원칙7). 상세 화면의 가운데·75% 폭은 `3bd5025` 에 이미 들어가 있어 손대지 않는다.

## 범위

- 포함:
  - **인물 화면 카드 그리드**(D15 결정 1) — `#/persons` 목록 모드를 타일 그리드로. 타일: 이름·관계 태그·위계·마지막 접촉(·별칭, 결정 B·K). 타일 클릭 = 기존 상세 경로 `#/persons/:id`(결정 H). 데스크톱 2~3열·모바일 1열(결정 A). 그리드는 본문 폭 전체, 폭 상한 없음(D15 결정 5).
  - **이름·별칭 검색창 1개**(D15 결정 2) — 프론트에서 부분 일치로 그리드를 바로 줄인다(결정 C·G). 0건 문구·자리표시 문구는 프론트 고정 문장(결정 D).
  - **사이드바 최근 5명 + "전체 보기 →"**(D15 결정 4) — `GET /persons` 결과 앞 5명을 서버 순서 그대로(재정렬 금지), 그 아래 `#/persons` 링크(결정 E·F). 사이드바 구조(결정 N — 모든 폭 왼쪽 사이드바, 모바일 서랍형, 하단 탭바 없음)는 그대로.
  - **테스트 갱신·보강** — `card.test.tsx`(목록 → 그리드·검색, 사이드바 전원 → 5명, "필터·검색 컨트롤이 없다" 단언 교체) · `routes.test.tsx`(사이드바 항목 단언 72~79행이 "전체 보기" 추가에 맞는지 확인·갱신) · E2E `card.spec.ts`(76행 사이드바 링크 수 `3 + PERSONS.length`, 53·108행 사이드바 인물 클릭, 그리드 타일 클릭·검색) · **R-U10C-3 목록 폭 단언 보강**(결정 J).
  - **문서** — 이 패키지 `tests.md`(테스트 1건 = 1줄, 사용자 규칙 2026-10-15) · `registry.md` 행 갱신/추가 · D15 갱신 이력에 완료 해시(메인 세션) · `03-log.md`(메인 세션).
  - **`GET /persons` 응답에 `aliases` 1필드**(결정 K (나)) — backend-agent 단위 U0. 읽기 전용, 스키마 v2·툴 시그니처 무변경, 새 엔드포인트·쿼리 파라미터 없음.
- 이 패키지에서 하지 않는 것 (각 줄 끝이 "왜 안 하는가"):
  - **관계 태그 필터 컨트롤**(`relation_tag`·`hierarchy` 로 거르는 `<select>`·토글·칩) — 기획서 2장 표 제외 칸 "관계 태그 필터링", 원칙7, D15 결정 3 "넣고 싶으면 별도 CR".
  - **새 API·새 쿼리 파라미터**(`GET /persons?q=&limit=`) — D15 결정 2·CR-003 §3 ③(가). 인물이 수백 명이 되면 그때 별도 결정(D15 이유).
  - **새 라우트·새 화면·라우트 밖 패널** — 원칙5. 라우트는 `#/chat`·`#/persons`(`#/persons/:id`)·`#/briefings` 3경로 그대로, `web/src/routes.ts` 무변경. 검색은 인물 화면 안의 입력 1개다.
  - **서버 문자열 가공** — 원칙7·결정 L 경계·D15 결정 6. 이름·태그·위계·별칭은 서버 값 그대로 표시한다. 검색 하이라이트(일치 부분 강조)도 하지 않는다 — 문자열을 쪼개 다시 그리는 것이 "가공" 과 구분하기 어렵고 D15 "검색 하이라이트에서 … 가공하지 않는다" 를 가장 확실히 지키는 방법이다.
  - **상세 화면(`#/persons/:id`) 폭·정렬 변경** — `3bd5025` 의 `card-wrap mx-auto w-full md:w-3/4` 유지(D15 결정 5, backlog 89행).
  - **`ChatScreen.tsx`·`BriefingScreen.tsx` 변경** — D15 코드 규칙 6번째 줄.
  - **U0 밖의 백엔드(`app/`·`alembic/`)·스키마 v2·툴 7종 변경** — D15 "S 카드: 무변경", 코드 규칙 1번째 줄(보정 뒤: `read.py`·`schemas.py`·그 테스트 밖 diff 0). 마이그레이션 0.
  - **"최근 5명" 기준을 `persons.updated_at` 으로** — CR-003 §3 ①(a) 확정, 응답 필드 추가가 필요해 보류(D15 이유).
  - **검색어 저장(라우트·localStorage)·정렬 바꾸기 컨트롤·페이지 나눔** — 수용 기준 밖, 설정 저장이 생기면 원칙5 "UI에 시간을 쓰지 않는다" 와 어긋난다(결정 G).
  - **맞춤 디자인 반복** — P8 결정 L 시간 상한. 사람 점검 뒤 수정 1회만.
  - **P8 의 다른 [권고]**(R-U10R-1 알림 클릭 실확인·R-U10R-4 호칭 별칭 자동 병합·R-U10R-5 첫 브리핑 버튼 등) — P8 04-review §6 이 다른 경로(사용자 확인·FIX/CR 후보·P10)로 넘겼다. 단 R-U10R-2(밝은 모드)·R-U10R-3(모바일 폭)은 P8 04-review §7 280행 권고대로 U5 사람 점검에서 같이 본다.

## 산출물 (파일 경로)

**새로 만드는 파일** (결정 I 추천안 기준 — 확정에 따라 바뀐다)

- `web/src/components/PersonGrid.tsx` — 인물 화면 카드 그리드 + 검색창(결정 I 추천 (나)). 이름은 U1 시작 전 `registry.md` grep 으로 중복 없음 확인(이 계획 작성 시 registry 236~261행에 `PersonGrid` 없음).
- `docs/wiki/packages/P8b-persons-grid/tests.md` — 이 패키지가 더하거나 바꾸거나 지운 테스트 1건 = 1줄(P8 `tests.md` 표 모양: 파일::테스트 이름 · 무엇을 확인하나 · 입력 → 기대 · 결과 · 실패 이력) + 변경 구분 열(신규/변경/삭제).
- `docs/wiki/packages/P8b-persons-grid/evidence/*-u<n>-*.txt` — `save_evidence.py P8b-persons-grid <이름> -- <명령>` 산출물.

**고치는 기존 파일** (registry 에 P8-frontend 행으로 있다 — 새 행이 아니라 비고 확장)

| 파일 | 고치는 내용 | registry 행 |
|------|------------|------------|
| `web/src/components/PersonList.tsx` | 사이드바 전용으로: 선택 인자 `limit`(앞 n 명만, `slice(0, limit)` — 서버 순서 그대로) + 목록 아래 "전체 보기 →" 링크(결정 F) · `PERSON_LIST_NOTICE` 에 검색 문구 키 추가(결정 D) · 머리 주석 "`#/persons` 본문과 사이드바 두 자리에 같은 컴포넌트" 를 사이드바 전용으로 정정 | 245행 |
| `web/src/components/AppShell.tsx` | `SIDEBAR_RECENT_LIMIT = 5` 상수(결정 E)를 `<PersonList limit={…} onNavigate={…} />` 로 넘김. 36행 주석 정정 | 236·254행 |
| `web/src/screens/PersonCardScreen.tsx` | 334~337행 목록 분기 `<PersonList />` → `<PersonGrid />`, import 교체. **상세 분기 339행 `card-wrap` 는 무변경** | 246행 |
| `web/src/__tests__/card.test.tsx` | "인물 목록" describe(100~169행)를 그리드·검색으로 다시 씀, 116~126행 폭 단언을 R-U10C-3 대로 보강, 139~146행 "필터·검색 컨트롤이 없다" → "검색 입력 정확히 1개·select/combobox 0", "사이드바의 인물 목록" describe(171~331행)를 5명·전체 보기로, 309~313행 "같은 컴포넌트 import" 단언을 결정 I 에 맞게 교체 | 247·250행 |
| `web/src/__tests__/routes.test.tsx` | 72~79행 데스크톱 사이드바 링크 단언 — 이 테스트의 `fetch` 상태에서 "전체 보기" 링크가 보이는지(결정 F)에 맞춰 기대값 확인·갱신 | 238행 |
| `web/e2e/card.spec.ts` | 픽스처 `PERSONS`(8~11행, 2명)를 6명 이상으로 · 53·108행 사이드바 인물 클릭 유지 · 76행 `3 + PERSONS.length` → `3 + min(5, n) + 1`(전체 보기) · 그리드 타일 클릭·검색 1회 · 목록 폭 `boundingBox()` 단언(결정 J) · 픽스처 응답에 `aliases` 필드 추가(결정 K (나), U0 응답 모양과 1:1) | 256행 |
| `docs/wiki/registry.md` | 245·246·247행 비고 확장 + `PersonGrid` 새 행 | — |
| `docs/wiki/decisions/D15-persons-screen-layout.md` | 갱신 이력에 완료 해시 한 줄(메인 세션, 패키지 완료 때) | — |

(결정 K (나) — U0 산출물: `app/api/read.py` `list_persons` · `app/api/schemas.py` `PersonListItemOut.aliases` · `tests/test_api_read_persons.py` · `web/src/api/types.ts` `PersonListItemOut.aliases`(U1) — CR-003 §2 "코드(백엔드, 결정 ③ (나) 일 때만)" 목록과 같은 파일들.)

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 /commit)

공통: 위임은 단위마다 L-004(AskUserQuestion → `approve-commit.sh --stage frontend-agent`). 판정 명령은 저장소 루트에서 `npm --prefix web run typecheck` · `npm --prefix web test -- --run <파일>` · `npm --prefix web run build` · `npm --prefix web run e2e`(스크립트 이름은 `web/package.json` 10~18행에서 확인: `typecheck`="tsc -b", `test`="vitest", `build`="tsc -b && vite build", `e2e`="playwright test" — E2E 는 `playwright.config.ts` 의 `webServer` 가 빌드·`vite preview` 4173 을 띄운다). 출력은 전부 `python3 .claude/scripts/save_evidence.py P8b-persons-grid <이름> -- <명령>`(FIX-034, Windows 는 `python`)으로 `evidence/<ts>-u<n>-<이름>.txt`. 위임 프롬프트에 FIX-033 네 규칙을 넣는다: (a) 계약 값(필터·자르기 개수·순서·href·폭 클래스)은 값으로 단언하고 "변이 → 잡는 테스트" 표를 보고에 넣는다(아래 단위별 표가 최소) (b) **이 계획에 없는 상수·정렬·상한·방어 조건이 필요하면 구현 전에 멈추고 보고**(값 후보와 이유) (c) 증거는 `save_evidence.py` 출력 전체 (d) 임시 파일·변이 스크립트는 스크래치패드 리터럴 절대 경로. 테스트 1건 = 이 패키지 `tests.md` 1줄(사용자 규칙 2026-10-15) — 단위마다 그 단위에서 더하거나 바꾼 테스트를 그 단위 커밋에 같이 적는다. 각 단위는 시작 전 `registry.md` grep, 끝나면 Vitest 전체 1회(`npm --prefix web test -- --run`)로 다른 파일 회귀 0 확인.

- [ ] U0 `GET /persons` 응답에 `aliases: list[str]` — [backend-agent] (결정 K (나) 확정 2026-10-21 — D15·CR-003·backlog 보정은 이 계획 커밋에 포함) `PersonListItemOut` 에 `aliases`(카드 응답과 같은 정렬 규칙 = `read.py` 의 카드 별칭 `sorted()`(U0 뒤 188행)와 같은 Python 코드포인트 순 — `_person_out` 재사용 여부는 registry 61행 `app/tools/persons.py` 보고), `list_persons` 가 별칭을 한 번의 조인/집계로(N+1 금지 — 판정 **사용자 확정 2026-10-27 (i)**: 테스트에서 SQLAlchemy 이벤트로 질의 횟수를 세어 인물 3명일 때와 10명일 때 `GET /persons` 의 SELECT 수가 같은 상수임을 단언한다), 원문 필드 없음·쓰기 0(P8 판정 4·7행 단언 유지), `web/src/api/types.ts` 동기화는 U1 에서. 판정: `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_api_read_persons.py -v` · 증거 `evidence/*-u0-read-persons-aliases.txt` / Refs: P8b-persons-grid D15 CR-003 원칙7 원칙9 R-U10R-10
- [ ] U1 인물 화면 카드 그리드 + 이름·별칭 검색 + 목록 폭 단언 보강(Vitest) — [frontend-agent] `PersonGrid`(결정 I) 신설: `usePersons()` 값을 받아 검색어로 거른 뒤(결정 C — `Array.prototype.filter` 만, 순서는 서버 그대로) shadcn `Card`(registry 235행 `ui/card`)를 `<a href="#/persons/:id">` 로 감싼 타일 그리드(결정 A·H). 타일 필드: 이름(`data-field="name"`)·태그(`tag`)·위계(`hierarchy`)·마지막 접촉(`last-contact`, `formatDate`·`PERSON_LIST_NOTICE.noContact` 재사용)·별칭(`aliases`, 결정 B·K). 검색창 `<input type="search">` 1개(결정 D 문구·`aria-label`), 0건이면 결정 D 문구 1줄, 빈·실패 상태는 기존 `PERSON_LIST_NOTICE.empty`·`failed` 재사용. 검색어는 컴포넌트 상태(결정 G). **testid 고정(R-5)**: 그리드 컨테이너 `data-testid="person-grid"`, 타일 `data-testid="person-tile"`(`data-person-id` 속성에 id), 검색창 `data-testid="person-search"`, 0건 문구 `data-testid="person-grid-empty"` — 테스트·E2E 가 같은 이름을 쓴다. **리스크 4 기본값 (a)(R-6)**: `isComposing` 처리·`compositionend` 보류·NFC/NFD 정규화는 넣지 않는다(결정 C 의 정규화만). `PersonCardScreen.tsx` 목록 분기만 교체(상세 `card-wrap` 무변경). `card.test.tsx` "인물 목록" describe 재작성 + **R-U10C-3 조상 검사**(결정 J). `web/src/api/types.ts` `PersonListItemOut` 에 `aliases: string[]` 동기화(U0 응답과 1:1). 판정: `npm --prefix web run typecheck` · `npm --prefix web test -- --run src/__tests__/card.test.tsx` · 전체 `npm --prefix web test -- --run` · 증거 `evidence/*-u1-grid.txt` · 변이 `evidence/*-u1-mutation.txt` / Refs: P8b-persons-grid D15 CR-003 결정L 원칙5 원칙7 R-U10C-3
  - 변이 → 잡는 테스트(최소, FIX-033 (a)):

    | 변이 | 잡아야 할 테스트(판정 행) |
    |------|-----------------------|
    | V1-1 검색어 무시(필터 제거) | 이름 부분 일치 테스트(판정 2행) |
    | V1-2 별칭을 검색 대상에서 뺌 | 별칭 부분 일치 테스트(2행) |
    | V1-3 대소문자·공백 정규화 제거 | 정규화 경계 테스트(결정 C, 2행) |
    | V1-4 거른 결과를 이름순 `sort` | 서버 순서 유지 테스트(2행·D15 "재정렬하지 않는다") |
    | V1-5 타일 `href` 를 `#/persons?id=` 등으로 | 타일 href·클릭 해시 테스트(3행) |
    | V1-6 그리드 안쪽 래퍼에 `mx-auto max-w-3xl`(R-U10C-3 의 M4 그대로) | 조상·자신 폭 클래스 테스트(5행) — **P8 에서 살아남은 변이, 이번엔 반드시 검출** |
    | V1-7 `section` 에 `max-w-4xl`(U10 수정 전 모양) | 같은 테스트(5행) |
    | V1-8 0건 문구 미표시 | 0건 테스트(2행) |
    | V1-9 별칭 표시 상한 2 → 3 / `display_name` 과 같은 별칭 제외 제거 | 타일 별칭 테스트(결정 B, 1행) |
    | V1-10 태그 `<select>` 하나 추가 | 컨트롤 개수 테스트(searchbox 1·combobox 0, 2행·D15 2번째 줄) |
    | V1-11 상세 `card-wrap` 의 `md:w-3/4` → `md:w-1/2` | 기존 상세 테스트(card.test 128~137행, 5행) — 회귀 확인 |
- [ ] U2 사이드바 최근 5명 + "전체 보기 →" — [frontend-agent] `AppShell.tsx` 에 `SIDEBAR_RECENT_LIMIT = 5`(결정 E), `PersonList` 에 `limit` 인자 → `persons.slice(0, limit)`(서버 순서 그대로, 재정렬·필터 없음), 목록 아래 "전체 보기 →"(`href="#/persons"`, 서랍에서는 `onNavigate` 로 닫힘, 결정 F). `card.test.tsx` "사이드바의 인물 목록" describe 갱신(6명 이상 픽스처로 5명·순서·전체 보기·서랍 닫힘, R-U6-2·R-U7-2 재조회 테스트는 5명 안의 인물로 유지) · `routes.test.tsx` 72~79행 기대값 확인·갱신. 판정: `npm --prefix web run typecheck` · `npm --prefix web test -- --run src/__tests__/card.test.tsx src/__tests__/routes.test.tsx` · 전체 Vitest · 증거 `evidence/*-u2-sidebar.txt` · 변이 `evidence/*-u2-mutation.txt` / Refs: P8b-persons-grid D15 CR-003 결정L 결정N 원칙5 R-U10C-3
  - 변이 → 잡는 테스트:

    | 변이 | 잡아야 할 테스트(판정 행) |
    |------|-----------------------|
    | V2-1 `slice(0, 5)` → `slice(0, 6)` / 자르기 제거(전원) | 사이드바 5명 테스트(4행) |
    | V2-2 `slice(-5)`(뒤 5명) / 이름순 정렬 후 자르기 | 사이드바 순서 테스트 — 서버 앞 5명과 순서까지 같음(4행) |
    | V2-3 "전체 보기" `href` 를 `#/chat` 으로 / 링크 제거 | 전체 보기 링크 테스트(4행) |
    | V2-4 서랍에서 "전체 보기" 클릭에 `onNavigate` 미연결 | 좁은 폭 서랍 닫힘 테스트(4행) |
    | V2-5 그리드(`#/persons` 본문)에도 5명 자르기 적용 | 그리드 전원 표시 테스트(1행) |
- [ ] U3 E2E 갱신 + 목록 폭 `boundingBox()` 단언 — [frontend-agent] `web/e2e/card.spec.ts`: 픽스처 인물 6명 이상(서버 순서가 이름·id 순과 다르게), 데스크톱 1280px — 사이드바 인물 링크 5개 + 전체 보기, 76행 링크 수 갱신, 전체 보기 → `#/persons` 그리드 → 검색 1회(이름 또는 별칭) → 타일 클릭 → `#/persons/:id` 카드·원문 펼치기(기존 59~63행 단언 유지), **목록 폭 `boundingBox()`**(결정 J) / 모바일 390px — 서랍 안 사이드바 5명 + 전체 보기, 그리드 1열(타일 x 좌표가 모두 같음). `expectNoStrayRequests` 유지(판정 27b 취지). 판정: `npm --prefix web run e2e` · 증거 `evidence/*-u3-e2e.txt` · 변이 `evidence/*-u3-mutation.txt` / Refs: P8b-persons-grid D15 CR-003 결정L 결정N 원칙5 R-U10C-3
  - 변이 → 잡는 테스트:

    | 변이 | 잡아야 할 테스트(판정 행) |
    |------|-----------------------|
    | V3-1 그리드 래퍼에 `max-w-3xl`(V1-6 과 같은 변이를 E2E 로) | 데스크톱 목록 폭 boundingBox(5행) |
    | V3-2 사이드바 `slice(0, 6)` | 데스크톱 사이드바 링크 수(4행) |
    | V3-3 모바일에서도 `grid-cols-2` | 모바일 1열 단언(1행) |
- [ ] U4 자동 판정 전체 + 문서 — [frontend-agent: 판정 실행·`tests.md`·`registry.md`] + [메인 세션: `03-log.md`·D15 갱신 이력 해시(패키지 완료 때)] 아래 판정 표 1~13행 전부 실행(typecheck·Vitest 전체·build·E2E·불변식 grep·백엔드 무변경 diff), `tests.md` 행 수 = 이 패키지가 더하거나 바꾼 테스트 수 대조(13행), registry 행 갱신. 판정: 판정 표 그대로 · 증거 `evidence/*-u4-final-judge.txt`·`*-u4-invariants.txt`·`*-u4-tests-md-check.txt` / Refs: P8b-persons-grid D15 CR-003 원칙5 원칙7 원칙8 R-U10C-3 R-U10R-10
- [ ] U5 사람 점검 — [사용자·메인 세션] 판정 표 14행(데스크톱·모바일 폭에서 그리드·검색·사이드바 5명·전체 보기·상세 75% 회귀, P8 체크리스트 19·20항 "5명 기준" 재점검, R-U10R-2 밝은 모드 1회, 원하면 R-U10R-3). "수정 필요" 반영은 **1회 상한**(P8 결정 L), 증거에 "수정 반영 횟수: n" 줄. 증거 `evidence/*-u5-check-screens.txt` / Refs: P8b-persons-grid D15 CR-003 결정L 결정N 원칙5 원칙8

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- D15 "코드에서 지켜야 할 것" 전부 · 백엔드 변경은 `GET /persons` 응답에 `aliases` 필드를 더하는 것뿐(결정 K (나), 읽기 전용, 스키마 v2 무변경 — `app/api/read.py`·`app/api/schemas.py`·`tests/test_api_read_persons.py` 밖 `app/`·`alembic/` diff 0) · `card.test.tsx`·`routes.test.tsx`·E2E `card.spec.ts` 사이드바 단언 5명으로 갱신 · 목록 폭 단언 보강(R-U10C-3, 조상 전부 + `boundingBox()`) · typecheck·Vitest·build·E2E 통과 · 상세 가운데 75% 는 `3bd5025` 유지 — 사용자 승인 2026-10-16, 결정 K·A~J 확정 2026-10-21

(backlog 89행과 글자 그대로 같다 — 결정 K (나) 확정으로 2026-10-21 함께 바꿨다.)

## 해석 — 수용 기준 (새 기준을 더하는 것이 아니다)

| # | 원문 구절 | 이 계획의 해석 → 판정 행 |
|---|----------|----------------------|
| ㄱ | D15 "코드에서 지켜야 할 것" 전부 | D15 22~29행 일곱 문장을 판정 표 1~7행에 **글자 그대로** 한 행씩 |
| ㄴ | 백엔드 변경은 `aliases` 필드 추가뿐 … 밖 diff 0 | `git diff --stat 3bd5025..HEAD -- app alembic ':!app/api/read.py' ':!app/api/schemas.py'` 빈 출력(R-U10R-10 — 기준 해시는 FIX-035 뒤) + 그 두 파일·`tests/test_api_read_persons.py` 의 diff 는 U0 판정(`aliases` 추가 외 변경 0) → 8행 |
| ㄷ | 사이드바 단언 5명으로 갱신 | `card.test.tsx`·`routes.test.tsx`·`card.spec.ts` 의 사이드바 단언이 "앞 5명 + 전체 보기" 를 값으로 단언 → 4행 |
| ㄹ | 목록 폭 단언 보강(R-U10C-3) | Vitest 조상 전부 검사 + E2E `boundingBox()`(결정 J 추천) — V1-6 변이(M4) 검출 → 5행 |
| ㅁ | typecheck·Vitest·build·E2E 통과 | 9~11행 |
| ㅂ | 상세 가운데 75% 는 `3bd5025` 유지 | 5행 후반 + `card-wrap` 줄 grep → 5행 |

## 판정 방법 (수용 기준을 기계적으로 확인하는 명령)

자동 1~13행이 전부 통과한 뒤에만 사람 점검 14행을 시작한다(P8 결정 J 순서). Vitest 행은 `fetch` 를 가짜로 바꿔 끼운 기존 방식(card.test 26~41행 `install`·`router` — 표 밖 요청은 throw), E2E 는 `installFakeApi`(표 밖 요청 중단·기록) + `expectNoStrayRequests`. 실 네트워크 0.

| # | 무엇을 | 입력 → 기대 | 증거 |
|---|--------|------------|------|
| 1 | D15(보정 2026-10-21): "`web/src/api/client.ts` 의 `getPersons` 는 인자가 없다 — `?q=`·`?limit=` 를 붙이지 않는다. 백엔드 변경은 `GET /persons` 응답(`PersonListItemOut`)에 `aliases: list[str]` 를 더하는 것뿐(결정 K (나), 2026-10-21) — `app/api/read.py`·`app/api/schemas.py`·`tests/test_api_read_persons.py` 밖 `app/`·`alembic/` diff 0, 마이그레이션 0." | `grep -n "export function getPersons()" web/src/api/client.ts` → 1건 · `grep -rnE "persons\?|[?&](q|limit)=" web/src --exclude-dir=__tests__` → 0건 · `git diff 3bd5025..HEAD -- app/api/read.py app/api/schemas.py` 의 변경이 `aliases` 추가(+ docstring)뿐(사람이 대조, 증거에 붙임) · U0 pytest: `GET /persons` 각 행 `aliases` 가 카드 응답 `aliases` 와 같은 값·같은 순서, 원문 키 0, 쓰기 0(기존 `assert_no_writes`) · Vitest: `#/persons` 진입 시 `fetch` 호출 URL 이 `/api/persons` 정확히 1회 · 그리드 테스트: 타일 필드 4개+별칭 값이 서버 값 그대로, 데스크톱 클래스 결정 A, 그리드는 5명 넘게 전원 | `*-u0-read-persons-aliases.txt` · `*-u4-invariants.txt` · `*-u1-grid.txt` |
| 2 | D15: "인물 화면에 `relation_tag`·`hierarchy` 로 거르는 `<select>`/토글이 없다. 검색 `<input>` 은 1개이고 `display_name`·`aliases` 부분 일치만 한다." | Vitest: 인물 화면에서 `getAllByRole('searchbox')` 길이 1 · `combobox`·`listbox`·`radio`·`checkbox`·`switch` 0 · `grep -rnE "<select|role=\"(combobox|switch)\"" web/src/components/PersonGrid.tsx` 0건 · 검색 "선영"(이름 일부) → 해당 타일만 · 별칭 일부 → 그 인물만(결정 K) · 태그 문자열(예: "직장")로 검색 → 태그만 일치하는 인물은 **안 나옴**(태그는 검색 대상 아님) · 결정 C 정규화 경계(앞뒤 공백·대소문자) · 빈 검색어 → 전원 · 0건 → 결정 D 문구 1줄 · 거른 결과 순서 = 서버 순서 | `*-u1-grid.txt` |
| 3 | D15: "타일은 `#/persons/:id` 로 이동한다(`href="#/persons/`). 라우트는 여전히 3경로(`#/chat`·`#/persons`·`#/briefings`) — 판정 13행." | Vitest: 타일 `href` 배열 = 서버 순서의 `#/persons/<id>` · 타일 클릭 → `window.location.hash` = `#/persons/<id>` · Tab 으로 타일에 포커스·Enter 로 이동(결정 H) · `routes.test.tsx` 판정 13행(P8) 테스트 통과 · `git diff --stat 3bd5025..HEAD -- web/src/routes.ts` → 빈 출력 | `*-u1-grid.txt` · `*-u4-invariants.txt` |
| 4 | D15: "사이드바(`AppShell.tsx`)가 그리는 인물은 `GET /persons` 결과의 **앞 5명**이고 그 아래 `#/persons` 링크가 있다. 서버 정렬을 프론트가 재정렬하지 않는다." | Vitest(`card.test.tsx`): 서버가 7명을 이름·id·날짜 어느 순서와도 다르게 줌 → `sidebar-persons` 안 인물 링크가 정확히 앞 5명·같은 순서 + 마지막 링크 "전체 보기 →" `href="#/persons"` · 인물 3명이면 3명 + 전체 보기(결정 F) · 좁은 폭 서랍에서 전체 보기 클릭 → 서랍 닫힘·`#/persons` · `routes.test.tsx` 72~79행 갱신 기대 통과 · E2E 데스크톱 `sidebar` 링크 수 = 3 + 5 + 1, 모바일 서랍 안 인물 5 + 전체 보기 | `*-u2-sidebar.txt` · `*-u3-e2e.txt` |
| 5 | D15: "`[data-screen="persons"]` 목록 모드의 **조상·자신 어디에도** `max-w-*`·`mx-auto` 가 없다(R-U10C-3 — `section` 한 요소만 보는 테스트는 부족, 조상 전부 또는 E2E `boundingBox()` 로 목록 폭 ≈ `main` 폭). 상세 모드는 `data-testid="card-wrap"` 가 `mx-auto w-full md:w-3/4` 이고 `max-w-*` 가 없다." | Vitest(`<App />` 렌더, `#/persons`): 그리드 요소에서 `main` 까지 모든 조상 + 그리드 자신 + `[data-screen="persons"]` 의 자손 중 그리드를 감싼 요소 전부에 `mx-auto`·`max-w-*`·`md:w-*` 클래스 0 (결정 J) · E2E 1280px: 그리드 `boundingBox().width` 와 `main` 콘텐츠 폭의 차이 ≤ 결정 J 허용치 · 상세: 기존 card.test 128~137행 통과 + `grep -n 'data-testid="card-wrap" className="mx-auto w-full md:w-3/4"' web/src/screens/PersonCardScreen.tsx` → 1건 · `git diff 3bd5025..HEAD -- web/src/screens/PersonCardScreen.tsx` 에서 `card-wrap` 줄 변경 0 · **변이 V1-6(R-U10C-3 의 M4) 검출** | `*-u1-grid.txt` · `*-u1-mutation.txt` · `*-u3-e2e.txt` |
| 6 | D15: "`ChatScreen.tsx` 의 `mx-auto max-w-3xl`·`BriefingScreen.tsx` 폭은 이 결정으로 바꾸지 않는다." | `git diff --stat 3bd5025..HEAD -- web/src/screens/ChatScreen.tsx web/src/screens/BriefingScreen.tsx` → 빈 출력 | `*-u4-invariants.txt` |
| 7 | D15: "서버 문자열 변환 0(원칙7) — 타일·검색 하이라이트에서 `reply`·이름·별칭을 가공하지 않는다." | Vitest: 특수문자·앞뒤 공백·영문 대소문자가 섞인 `display_name`·별칭 픽스처 → 타일 `textContent` 가 서버 값과 완전 일치(검색 정규화는 비교에만 쓰이고 표시는 원본) · 검색 중에도 타일 이름 `textContent` 동일(하이라이트 없음 — 이름 칸 안 자식 요소 0) · `grep -rnE "toUpperCase|toLowerCase|replace\(|trim\(" web/src/components/PersonGrid.tsx` 결과가 결정 C 의 비교 함수 안에만 있음(사람이 줄을 대조, 증거에 붙임) | `*-u1-grid.txt` · `*-u4-invariants.txt` |
| 8 | 백엔드 변경은 `aliases` 필드 추가뿐 (backlog, 결정 K (나)) · 무변경 기준 R-U10R-10 | `git diff --stat 3bd5025..HEAD -- app alembic ':!app/api/read.py' ':!app/api/schemas.py'` → **빈 출력** · `git diff --stat 3bd5025..HEAD -- alembic` → 빈 출력(마이그레이션 0) · `git diff --stat 3bd5025..HEAD -- tests ':!tests/test_api_read_persons.py'` → 빈 출력(R-4 — U0 밖 백엔드 테스트 무변경) · `app/api/read.py`·`schemas.py`·`tests/test_api_read_persons.py` 는 1행(U0) 판정 | `*-u4-invariants.txt` |
| 9 | typecheck · build | `npm --prefix web run typecheck` 종료 0 · `npm --prefix web run build` 종료 0, `web/dist/index.html`·`web/dist/sw.js`·`web/dist/manifest.webmanifest` 존재 | `*-u4-final-judge.txt` |
| 10 | Vitest 전체 | `npm --prefix web test -- --run --reporter=verbose` → 실패 0, 총 건수 = 기준선(**U0 시작 전 = 지금 HEAD `fe76931`, 137 passed** — P8 04-review 재실행 값; U1 시작 전에 같은 명령으로 한 번 더 재어 03-log 에 기록, R-9) + 신규 − 삭제 | `*-u4-final-judge.txt` |
| 11 | E2E 전체 | `npm --prefix web run e2e` → 실패 0(chat·card·briefing 3편), `expectNoStrayRequests` 통과 | `*-u4-final-judge.txt` |
| 12 | 불변식 — 화면 3개·라우트 밖 패널 1개(원칙5, P8 불변식 10·판정 13행) | `git diff --stat 3bd5025..HEAD -- web/src/routes.ts` 빈 출력 · `grep -rlE "Sheet|Dialog|Drawer" web/src --include=*.tsx \| grep -v "^web/src/components/ui/"` → `web/src/components/AppShell.tsx` **1파일뿐** · P8 불변식 1·2·4·7·9 명령 재실행(`push-dev`·음성·`raw_utterance`·`VITE_*KEY`·외부 글꼴) → P8 과 같은 기대값 | `*-u4-invariants.txt` |
| 13 | `tests.md` 행 수 = 테스트 수 | 이 패키지 `tests.md` 의 표 행 수(`grep -c "^| .*\.\(tsx\|ts\)::" tests.md`) = U1~U3 에서 신규 + 변경 + 삭제한 테스트 수(각 단위 보고의 목록 합) · 표의 테스트 이름이 `--reporter=verbose` 출력 이름과 1:1(삭제 행 제외) | `*-u4-tests-md-check.txt` |

### 사람 점검 (자동 1~13행 통과 뒤)

| # | 무엇을 | 체크리스트 | 증거가 갖출 항목 |
|---|--------|-----------|----------------|
| 14 | 데스크톱·모바일 폭에서 그리드·검색·사이드바 5명·전체 보기 (P8 결정 L·N) | ① 데스크톱(창 넓게)에서 `#/persons` 그리드가 본문 폭 전체를 쓰고 2~3열(결정 A) ② 모바일 폭(개발자 도구 기기 모드 390 또는 Chrome 최소 폭 — R-U10R-3)에서 1열·가로 스크롤 없음 ③ 검색창에 한글 이름 일부·별칭 일부를 쳐서 그리드가 바로 줄고, 한글 조합 중에도 깨지지 않음 ④ 0건 문구 ⑤ 타일 클릭 → 상세가 가운데·본문 75%(회귀 없음) ⑥ 사이드바 인물이 최근 5명 + "전체 보기 →", 누르면 그리드(서랍이면 닫힘) — **P8 체크리스트 19·20항을 5명 기준으로 재점검** ⑦ 타일이 채팅·카드와 같은 디자인 언어(P8 체크리스트 16항, 결정 L) ⑧ 밝은 모드 1회(R-U10R-2) | 항목마다 통과/수정 필요 + 사용자 한 줄 의견, 데스크톱·모바일 각 1회, 어두운·밝은 각 1회, 실서버 인물 수(6명 이상이어야 5명 자르기가 보인다 — 모자라면 그 사실을 적는다), **"수정 반영 횟수: n" 줄 — n ≤ 1**(P8 결정 L 상한, 넘으면 CR 여부를 사용자에게) |

## 기존 산출물 재사용 (registry grep — 중복 구현 금지)

| 쓰는 것 | 경로 | registry 근거 | 이 패키지에서 |
|---------|------|--------------|-------------|
| 인물 목록 단일 조회 `PersonsProvider`·`usePersons`·`notifyPersonsChanged` | `web/src/components/PersonsProvider.tsx` | 249행 | 그리드·사이드바 모두 여기서 읽는다. `GET /persons` 를 새로 부르는 코드 금지(R-U6-2 "1회" 테스트 유지) |
| `PersonList`·`PERSON_LIST_NOTICE` | `web/src/components/PersonList.tsx` | 245행 | 사이드바용으로 남기고 `limit`·"전체 보기" 추가. 문구 상수는 그리드도 재사용(`empty`·`failed`·`noContact`) |
| `AppShell`·`SidebarContent`·`DESKTOP_QUERY` | `web/src/components/AppShell.tsx` | 236·254행 | 사이드바 5명 상수만 더한다. 서랍 구조 무변경(불변식 10) |
| `PersonCardScreen` 목록/상세 분기·`card-wrap`·`CardView` | `web/src/screens/PersonCardScreen.tsx` | 246행 | 목록 분기 한 줄만 교체. 상세 무변경 |
| 해시 라우팅 `HREF`·`parseHash` | `web/src/routes.ts` | 236행 | `HREF.persons` 로 타일·전체 보기 href 를 만든다. 파일 무변경 |
| `getPersons`·`getPersonCard` | `web/src/api/client.ts` | 246행 | 인자 추가 금지(D15). 목록 화면은 `getPersons` 만 부른다(별칭은 응답에 포함, 결정 K (나)) |
| `formatDate` | `web/src/lib/format.ts` | 246행 | 타일의 마지막 접촉 |
| shadcn `Card`·`Badge` | `web/src/components/ui/card.tsx`·`badge.tsx` | 235행 | 타일 모양(결정 L 같은 디자인 언어). **새 shadcn 부품을 내려받지 않는다** — `ui/` 8개 밖이고 `input` 이 없으므로 검색창은 토큰 클래스를 쓴 `<input type="search">`(결정 I) |
| 가짜 `matchMedia` `installFakeMatchMedia` | `web/src/__tests__/helpers.ts` | 238행 | 1280·800 폭 테스트 |
| E2E `installFakeApi`·`freezeClock`·`expectNoStrayRequests` | `web/e2e/fixtures.ts` | 256행 | card.spec 갱신에 그대로 |
| 테스트 기록표 형식 | `docs/wiki/packages/P8-frontend/tests.md` | 258행 | 같은 열 모양으로 이 패키지 `tests.md` |

## 결정 항목 (후보·추천·근거 — **확정은 사용자**, 비어 있는 "확정" 칸은 위임 전에 채운다)

이 표의 A~K 는 이 패키지의 결정이다. Refs 의 `결정L`·`결정N` 은 P8-frontend 01-plan 의 결정 L(챗봇형 UI·수정 1회 상한)·결정 N(사이드바)을 가리킨다.

| # | 무엇 | 후보 | 추천 | 근거 | 확정 |
|---|------|------|------|------|------|
| **K (선결)** | 별칭 데이터를 어디서 얻나 (D15 전제 불일치 — 위 ⚠ 절) | (가) 인물 화면 진입 시 인물마다 기존 `GET /persons/{id}` 를 불러 `aliases` 를 모은다(백엔드 0, 새 API 0). 별칭이 오기 전엔 이름만으로 검색, 카드 응답 캐시 범위(언제 다시 부르나)를 추가로 정해야 함 · (나) `GET /persons` 응답에 `aliases: list[str]` 1필드 추가(읽기 전용, 스키마 v2 무변경, backend-agent U0) — **D15 코드 규칙 1번째 줄·backlog 89행 "백엔드 diff 0" 을 바꾸므로 CR-003 보정 선행** · (다) 별칭을 빼고 이름만 검색·타일 별칭 없음 — **CR-003 ②(a) 사용자 결정을 뒤집으므로 CR** | **(나)** | (가)는 인물 N 명이면 요청 N+1 회이고 카드 응답(사실·타임라인·일정)을 별칭 하나 때문에 통째로 받는다. `PersonsProvider` 가 해시 변경마다 다시 읽으므로(249행) 캐시 규칙이라는 새 상수가 생기고, "검색 결과가 별칭 로딩 전후로 달라지는" 상태가 테스트·사용자 모두에게 헷갈린다. (나)는 한 요청·한 상태로 D15 결정 1·2 의 뜻(별칭 검색)을 그대로 지키며, CR-003 §2 가 이미 같은 모양의 "(나) 응답 1필드 추가(읽기 전용, 스키마 아님)" 를 검토 대상으로 적어 두었다. 백엔드 0 을 끝까지 지키는 것이 더 중요하면 (가). (다)는 "선영 과장님으로 박선영 과장님을 찾아야 쓸모"(CR-003 ② 추천 이유)를 잃는다 | **(나)** — 사용자 2026-10-21 |
| A | 그리드 열 수 | (a) `grid-cols-1 md:grid-cols-2 xl:grid-cols-3` (화면 폭 기준) · (b) `grid-cols-[repeat(auto-fill,minmax(16rem,1fr))]` (본문 폭 기준 자동) · (c) `grid-cols-1 lg:grid-cols-2 2xl:grid-cols-3` | **(a)** | D15 "데스크톱 2~3열, 모바일 1열" 을 열 수 상한까지 그대로 지킨다. (b)는 1920px 창에서 5~6열이 되어 "2~3열" 을 넘는다. (a)에서 1024~1279px 은 사이드바 256px 를 빼면 본문 약 720px 에 2열, 1280px 이상은 약 976px 이상에 3열이라 타일 폭이 300px 안팎으로 유지된다. 간격은 4px 배수 척도의 `gap-4`(16px, P8 결정 L 여백 규칙) | **(a)** — 사용자 2026-10-21 |
| B | 타일에 보이는 별칭 (K 가 (다)면 해당 없음) | (a) 서버 순서 그대로, `display_name` 과 글자가 완전히 같은 별칭은 빼고, 최대 2개, 넘치면 "+n"(n = 남은 개수) · (b) 최대 1개, 넘침 표시 없음 · (c) 전부 | **(a)** | D15 결정 1 "별칭 1~2개". `display_name` 과 같은 별칭(별칭 테이블에 본명이 들어간 경우)을 다시 보이면 같은 글자가 두 번 나온다. "+n" 은 "더 있다" 는 사실만 알려 검색 대상임을 짐작하게 한다 — 이 "+n" 은 프론트 고정 문구(서버 문자열 가공 아님). 별칭 사이 구분은 기존 목록의 `' · '` 와 같게 | **(a)** — 사용자 2026-10-21 |
| C | 검색 일치 규칙 | (a) 비교용으로만 양쪽을 `trim` + 영문 소문자화(`toLowerCase`) + **안쪽 공백 제거**, 대상 = `display_name` 과 `aliases[]` 각각, 하나라도 부분 일치(`includes`)면 보임, 빈 검색어(공백뿐 포함) = 전원 · (b) (a)에서 안쪽 공백은 그대로 · (c) 대소문자 구분·정규화 없음 | **(a)** | "선영과장님" 처럼 띄어쓰기를 빼고 쳐도 "선영 과장님" 을 찾는다(한국어 호칭은 띄어쓰기가 들쭉날쭉하다). 정규화는 비교 함수 안에서만 하고 **표시는 서버 원문**이라 원칙7(가공 0)과 충돌하지 않는다(판정 7행). 한글은 대소문자가 없어 소문자화의 영향이 없다. 유니코드 NFC/NFD 정규화는 넣지 않는다(입력·서버 모두 NFC 가 보통 — 문제가 보이면 그때 결정, 리스크 4) | **(a)** — 사용자 2026-10-21 |
| D | 검색 0건 문구·자리표시·접근성 이름 (프론트 고정 문장, `PERSON_LIST_NOTICE` 에 추가) | 0건: (a) "찾는 인물이 없어요." · (b) "검색 결과가 없어요." / 자리표시: (a) "이름이나 별칭으로 찾기" · (b) "인물 검색" / `aria-label`: "인물 검색" | **0건 (a) · 자리표시 (a) · aria-label "인물 검색"** | 기존 문구 말투("아직 기록된 인물이 없어요.")와 맞춘다. 자리표시가 검색 대상(이름·별칭)을 직접 알려 태그로 찾을 수 있다는 오해를 막는다(태그 필터 제외 — 원칙7). 서버 문자열이 아니라 프론트 상수다(D15 결정 6 과 무관) | **0건 "찾는 인물이 없어요." · 자리표시 "이름이나 별칭으로 찾기" · aria-label "인물 검색"** — 사용자 2026-10-21 |
| E | 사이드바 5명 상수 이름·위치·자르는 법 | 이름 `SIDEBAR_RECENT_LIMIT = 5` · 위치 (a) `AppShell.tsx` 에 두고 `PersonList` 에 `limit` 인자로 넘김 · (b) `PersonList.tsx` 안 · 자르기 = `persons.slice(0, limit)`(서버 순서 그대로, 재정렬 금지) | **이름 `SIDEBAR_RECENT_LIMIT`, 위치 (a), `slice(0, limit)`** | D15 코드 규칙 4번째 줄이 "사이드바(`AppShell.tsx`)가 그리는 인물은 … 앞 5명" 이라 상수가 `AppShell.tsx` 에 있어야 리뷰어 grep 이 바로 맞는다. 상수는 export 해 테스트가 값(5)을 import 해서 쓴다. `last_contact_at` 기준 정렬은 서버가 이미 한다(P8 U1 "정렬: `last_contact_at` 내림차순·없으면 뒤") — 프론트 `sort` 0 | **`SIDEBAR_RECENT_LIMIT = 5`, `AppShell.tsx` export, `slice(0, limit)`** — 사용자 2026-10-21 |
| F | "전체 보기 →" 링크 | 보이는 조건: (a) 인물이 1명 이상이면 항상 · (b) 5명 초과일 때만 · (c) 빈 목록·실패일 때도 / 글자: "전체 보기 →"(D15 글자 그대로) / 위치: 인물 목록 바로 아래, 같은 `sidebar-persons` 영역 안 | **(a), "전체 보기 →", 목록 아래** | D15 결정 4 는 조건 없이 "그 아래 '전체 보기 →'" 라 (a)가 가장 가깝고, 5명 이하일 때도 "인물 화면에 검색이 있다" 는 입구가 된다. (b)는 E2E 가 6명 이상일 때만 링크를 보게 되어 조건 분기 테스트가 늘어난다. (c)는 빈 목록 문구 밑에 링크가 생겨 `routes.test.tsx` 72~79행(이 테스트에서 인물 조회 상태)에 영향을 준다 — (a)이면 인물이 0명·실패일 때 링크가 없어 72~79행 기대값이 그대로일 가능성이 높다(U2 에서 실행으로 확인) | **(a), "전체 보기 →", 목록 아래** — 사용자 2026-10-21 |
| G | 검색어 상태 | (a) `PersonGrid` 컴포넌트 상태만 — 라우트·localStorage 에 안 남김, 새로고침하면 비움, 타일을 눌러 상세로 갔다 돌아오면 비움(목록 분기 언마운트로 자연히) · (b) 상위로 끌어올려 상세에서 돌아와도 유지 · (c) 해시 쿼리 `#/persons?q=` | **(a)** | (c)는 라우트 모양을 바꾸고(routes.ts 무변경 불변식) (b)는 상태 끌어올리기 코드가 늘어난다. 검색은 "한 번 찾아 들어가는" 동작이라 돌아왔을 때 비어 있어도 손해가 작다. P8 결정 N "열림/닫힘은 레이아웃 상태일 뿐 라우트·저장 설정 아님" 과 같은 원칙 | **(a)** — 사용자 2026-10-21 |
| H | 타일 클릭 방식 | (a) 타일 전체를 `<a href="#/persons/:id">` 하나로(사이드바 항목과 같은 방식, Tab 이동·Enter 는 브라우저 기본) · (b) `<div onClick>` + `role="link"` · (c) 타일 안 "열기" 버튼 | **(a)** | D15 코드 규칙 3번째 줄 "`href="#/persons/`" 를 grep 으로 확인한다는 문장에 맞고, 키보드·가운데 클릭·새 탭이 공짜다. (b)는 접근성을 손으로 맞춰야 하고 (c)는 "진짜 카드처럼 클릭" 요청과 다르다 | **(a)** — 사용자 2026-10-21 |
| I | 컴포넌트 구조 · 검색 입력 부품 | 구조: (가) `PersonList` 를 확장(`variant="grid"\|"sidebar"`) · (나) `PersonGrid` 신설(인물 화면), `PersonList` 는 사이드바 전용으로 유지 / 입력 부품: (ㄱ) `<input type="search">` + 기존 토큰 클래스 · (ㄴ) `npx shadcn@4.21.4 add input` 으로 `ui/input.tsx` 받기 | **(나) + (ㄱ)** | 그리드(검색·0건·타일·열)와 사이드바(자르기·전체 보기·서랍 닫힘)는 공통점이 "같은 데이터를 읽는다" 뿐이고 그것은 이미 `usePersons` 가 맡는다(registry 249행) — 한 컴포넌트에 분기를 넣으면 두 화면의 테스트가 서로 얽힌다. 중복은 필드 4개 그리기 정도이고 문구 상수·`formatDate`·`HREF` 는 재사용한다. card.test 309~313행 "같은 컴포넌트 import" 단언은 D15 로 의미가 사라지므로 "본문은 `PersonGrid`, 사이드바는 `PersonList` 를 import" 로 교체. 입력 부품은 내려받기(외부 레지스트리)를 늘리지 않고 registry 235행 "이 8개 밖의 컴포넌트는 받지 않았다" 를 유지 | **(나) + (ㄱ)** — 사용자 2026-10-21 |
| J | 목록 폭 단언 방법 (R-U10C-3) | (a) Vitest 조상 전부 검사만 · (b) E2E `boundingBox()` 만 · (c) 둘 다 | **(c)** — Vitest: 그리드 요소에서 `main` 까지 조상 + 자신 + 그리드를 감싼 `section` 안 래퍼 전부에 `mx-auto`·`max-w-*`·`md:w-*` 0 / E2E 1280px: `abs(grid.width − (main.width − 48)) ≤ 2` (48 = `main` 의 `p-6` 좌우 24px×2, 허용치 2px) | jsdom 은 레이아웃이 없어 Vitest 는 클래스만 본다 — 임의 CSS·인라인 `style`·새 클래스 이름(예: `container`)은 못 잡는다. E2E 는 실제 폭을 재지만 1개 폭만 본다. 둘 다 두면 R-U10C-3 의 M4(안쪽 `div` 에 `mx-auto max-w-3xl`)를 두 층에서 잡는다(V1-6·V3-1). 허용치 2px 는 반올림·스크롤바 차이 여유이고 E2E 는 `vite preview` Chromium 이라 스크롤바 폭이 0 일 수 있다 — U3 에서 실측값을 03-log 에 남기고 허용치가 맞지 않으면 멈추고 보고(FIX-033 (b)) | **(c)** — 사용자 2026-10-21 |

## 리스크 · 미결

- **1. (해소 2026-10-21) 결정 K = (나)** — D15 전제("목록 전체를 이미 받음")가 별칭에는 맞지 않았다(⚠ 절). 사용자 결정으로 `GET /persons` 응답에 `aliases` 를 더하고(U0), D15 코드 규칙 1번째 줄·결정 2·CR-003 §2·backlog 89행을 보정했다(새 CR 아님 — CR-003 §2 가 예고한 (나) 갈래). 남은 위험: U0 이 `aliases` 외의 것을 바꾸면 판정 1·8행이 잡는다.
- **2. 인물이 많아지면 프론트 필터의 한계** — 지금 사용자 `local` 인물 수(P8 04-review §7 "사용자 `local` 이 5명")에서는 문제가 없다. 수백 명이 되면 `GET /persons` 전량(별칭 포함)이 무거워진다. 그때 서버 `GET /persons?q=&limit=` 를 별도 결정으로(D15 이유 문장).
- **3. 사이드바가 5명으로 줄면 기존 테스트 단언이 바뀐다** — `card.spec.ts` 76행 `3 + PERSONS.length`(지금 2명 픽스처라 5명 자르기가 보이지 않음 → 픽스처를 6명 이상으로), 53·108행 사이드바 인물 클릭(그 인물이 앞 5명 안이어야 함), `card.test.tsx` 171~331행 사이드바 describe(3명 픽스처 → 5명 자르기를 보려면 6명 이상 픽스처 추가, R-U6-2·R-U7-2 재조회 테스트가 새 인물을 사이드바에서 찾으므로 그 인물이 앞 5명 안에 있게), `routes.test.tsx` 72~79행. 바꾼 테스트는 전부 `tests.md` 에 "변경" 행으로(13행).
- **4. 검색 입력의 한글 조합(`isComposing`)** — 검색은 Enter 제출이 아니라 `onChange` 마다 거르므로 조합 중 중간 글자(예: "ㅅ", "서")로도 바로 걸러진다. 깨지는 동작은 아니지만 조합 중 결과가 잠깐 0건으로 깜빡일 수 있다. 처리 방침 후보: (a) 그대로 둔다(추천 — 조합 이벤트 처리 코드가 늘지 않고, 채팅 입력의 `isComposing` 은 Enter 전송 때문이었다 — `ChatScreen.tsx` 230행) / (b) `compositionend` 까지 필터 보류. 사람 점검 14행 ③ 에서 보고 이상하면 "수정 1회" 안에서 (b). 유니코드 정규화(NFC/NFD)도 같은 자리에서 본다(결정 C).
- **5. 타일 그리드가 결정 L "채팅과 같은 디자인 언어" 를 지키는가** — shadcn `Card`·기존 토큰·4px 배수 간격만 쓰고 새 색·그림자·애니메이션을 만들지 않는다. 판정은 사람 점검 14행 ⑦(P8 체크리스트 16항). 맞춤 반복은 1회 상한.
- **6. P8 체크리스트 19·20항 재점검은 5명 기준** — P8 01-plan 201~202행 메모. 실서버 인물이 5명 이하면 자르기가 화면에서 보이지 않는다 — 그 경우 14행 증거에 인원수를 적고 자르기는 자동 테스트(4행)로 닫혔다고 적는다(개발 DB 에 확인용 인물을 더 만들지는 사용자 결정 — 원칙8, P8 리스크 10 "지우지 않는다").
- **7. `PersonsProvider` 재조회와 검색 상태** — 해시가 바뀔 때마다 `GET /persons` 를 다시 읽는다(registry 249행). 검색 중에는 해시가 바뀌지 않으므로 목록이 바뀌지 않지만, 채팅 화면이 아닌 곳에서 `notifyPersonsChanged` 가 오면 검색어는 유지된 채 목록만 갱신된다 — 의도된 동작으로 본다(검색어 상태는 결정 G).
- **8. 기존 테스트 이름이 바뀌면 P8 `tests.md` 와 어긋난다** — P8 은 닫혔고 그 표는 P8 시점 기록이다. 이 패키지는 P8 `tests.md` 를 고치지 않고, 바뀐·지운 테스트를 이 패키지 `tests.md` 에 "변경/삭제(P8 tests.md 몇 행)" 로 적는다. P8 표를 갱신할지는 사용자 결정(미결).
- **9. "+n"·"전체 보기 →"·0건 문구는 프론트 고정 문장** — 서버 문자열 가공 금지(원칙7)와 별개다. 판정 7행은 서버 값 칸(이름·태그·위계·별칭)만 본다.

## 후행 패키지가 이 패키지에서 기대하는 것

- **P9-infra**: 무관(정적 산출물 경로·빌드 명령 무변경). 결정 K (나)이면 `GET /persons` 응답 모양이 바뀐 것을 P9 스모크 S1~S15 대조 때 참고.
- **P10-final-eval**: 무관(화면은 trace 를 남기지 않는다).

## 읽은 카드

(이 계획을 쓰며 실제로 연 카드만)

- `docs/wiki/decisions/D15-persons-screen-layout.md` 전문(33행) — 결정 1~6, 이유, 파급, "코드에서 지켜야 할 것" 7문장(22~29행 — 판정 1~7행에 글자 그대로), 갱신 이력 "그리드·검색·사이드바 5명은 P8b-persons-grid 에서 구현 — 완료 해시는 그때 적는다".
- `docs/wiki/changes/CR-003.md` 전문 — §1 표("**카드 그리드** — 타일마다 이름·관계 태그·위계·마지막 접촉(·별칭 1~2개)"), "제외 칸 '관계 태그 필터링'은 움직이지 않는다", §2 수정 파일 목록, §3 열린 결정 ①(a) `last_contact_at` "추가 코드 0" · ②(a) "'선영 과장님'으로 '박선영 과장님'을 찾아야 쓸모" · ③(가) "새 API 없음 유지" · ④(a) · ⑤(a) · ⑥(a), 승인 줄.
- `docs/backlog.md` 86~89행 — P8 완료 줄("마지막 제품 코드 커밋 `3bd5025`")과 P8b 수용 기준 원문.
- `docs/wiki/INDEX.md` 77행 — "`P8b-persons-grid` | … | frontend-agent(`web/` 만, 백엔드 0) | —".
- `docs/wiki/packages/P8-frontend/01-plan.md` 1~389행 중 형식·판정 표(118~165행)·U6 줄(97행 "**CR-003·D15 로 대체(2026-10-16)**")·체크리스트 19·20(201~202행 "그 뒤 점검은 5명 기준")·결정 L(305~328행 "사람 점검(32행) 뒤 '수정 필요' 를 **한 번만** 반영")·결정 N(330~348행, CR-003 인용문 332행)·지킬 불변식(356~369행, 10 "서랍 컴포넌트 **1파일뿐**").
- `docs/wiki/packages/P8-frontend/04-review.md` §6(251~273행) — R-U10R-10 "기준 해시를 **마지막 FIX 커밋 뒤**로 두거나 … `git diff --stat <fix>..HEAD`", R-U10R-2·3; §7(275~280행) — "R-U10C-3: `card.test.tsx` 목록 폭 단언을 `[data-screen="persons"]` 조상·자손 전부(또는 E2E `boundingBox()`) 로 보강 … `e2e/card.spec.ts:43` 사이드바 단언을 함께 갱신. 상세 `card-wrap mx-auto w-full md:w-3/4` 는 `3bd5025` 유지".
- `docs/wiki/packages/P8-frontend/review-u10-closeout.md` 39~42행 — 변이 표 "M4 (verifier, 공백 탐침) | 목록을 감싼 안쪽 `<div className="mt-4">` 에 `mx-auto max-w-3xl` | … | **`31 passed (31)` — 생존** | 공백 → R-U10C-3".
- `docs/wiki/registry.md` 230~261행 — 235(ui 8개 "이 8개 밖의 컴포넌트는 받지 않았다")·236(앱 틀)·238(routes.test)·245(PersonList "필터·검색 없음")·246(PersonCardScreen, `card-wrap` `3bd5025`)·247·249(PersonsProvider)·250·256(E2E)·258(tests.md) 행.
- `docs/wiki/packages/P8-frontend/tests.md` 9~13행(세는 법), 183~190행(표 모양 "파일::테스트 이름 | 무엇을 확인하나 | 입력 → 기대 | 결과 | 실패 이력").
- `.claude/skills/devlog/SKILL.md` 77~88행 "정합성 점검표" 8항.
- `docs/wiki/fixes/FIX-033.md` 18~21행 — "(b) **계획에 없는 상수·정렬·상한·추가 방어 조건이 필요하면 구현하기 전에 멈추고 보고한다**".
- `docs/wiki/verification.md` 18행(`save_evidence.py` 기본), 79~87행(변이 시험 방법 — "변이가 통과하면 테스트 공백이다(소견)").
- `docs/wiki/templates/plan.md` — 절 형식.
- 코드(확인 범위만): `web/src/components/PersonList.tsx` 1~54행 · `AppShell.tsx` 1~148행(36~39행 `sidebar-persons`, 141행 `main` `p-6`) · `PersonsProvider.tsx` 1~62행 · `web/src/screens/PersonCardScreen.tsx` 324~340행(목록 분기 334~337, `card-wrap` 339) · `web/src/api/client.ts` 107~113행 · `web/src/api/types.ts` 53~59·99행 · `app/api/schemas.py` 312~319·358~367행 · `web/src/routes.ts` 5~31행 · `web/package.json` 10~18행 · `web/src/__tests__/card.test.tsx` 1~190·305~331행 · `routes.test.tsx` 66~87행 · `web/e2e/card.spec.ts` 전문(124행) · `web/e2e/fixtures.ts` 31·50·66·82행 · `web/src/screens/ChatScreen.tsx` 230행(`isComposing`).
