# P8b-persons-grid · 계획 검증 (02-plan-verify)

대상: 01-plan.md(초안 개정 1 — 결정 K (나)·A~J 사용자 확정 2026-10-21) | 검증자: verifier (fable) — 계획 작성자(architect)·메인 세션과 다른 모델·새 컨텍스트(L-002) | 날짜: 2026-10-27

이 검증에서 고친 파일: 없음(코드·계획·카드 무수정, 커밋 없음, `.env` 미열람). 읽은 것은 위임 프롬프트가 지정한 카드·절과 01-plan 이 인용한 코드 행뿐이다. 앞선 시도(API 한도 중단)가 남긴 파일은 없었고 처음부터 다시 했다.

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)

명령: `python3 .claude/scripts/save_evidence.py P8b-persons-grid verifier-verify-plan -- bash .claude/scripts/verify-plan.sh P8b-persons-grid` (FIX-034 — Write 로 옮겨 적지 않고 스크립트가 evidence 에 직접 저장)

### 1차 — 02-plan-verify 작성 전 (`evidence/20261027-1316-verifier-verify-plan.txt`)
```
# 명령: bash .claude/scripts/verify-plan.sh P8b-persons-grid
# 시각: 2026-10-27T13:16:46+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: fe76931 (dev2)
# exit: 1
# ---
== verify-plan P8b-persons-grid  (2026-10-27 13:16) ==
PASS  존재: docs/wiki/packages/P8b-persons-grid/01-plan.md
FAIL  없음: docs/wiki/packages/P8b-persons-grid/02-plan-verify.md
PASS  카드 존재: D15
PASS  패키지 id 등록됨: P8-frontend
PASS  Refs 있음: - [ ] U0 `GET /persons` 응답에 `aliases: list[str]` — [backend-
PASS  Refs 있음: - [ ] U1 인물 화면 카드 그리드 + 이름·별칭 검색 + 목록 폭 단언 보강(Vitest) — [fro
PASS  Refs 있음: - [ ] U2 사이드바 최근 5명 + "전체 보기 →" — [frontend-agent] `AppShell
PASS  Refs 있음: - [ ] U3 E2E 갱신 + 목록 폭 `boundingBox()` 단언 — [frontend-agent]
PASS  Refs 있음: - [ ] U4 자동 판정 전체 + 문서 — [frontend-agent: 판정 실행·`tests.md`·`
PASS  Refs 있음: - [ ] U5 사람 점검 — [사용자·메인 세션] 판정 표 14행(데스크톱·모바일 폭에서 그리드·검색·사이
PASS  backlog 일치: D15 "코드에서 지켜야 할 것" 전부 · 백엔드 변경은 `GET /persons` 응답에 `aliases`
PASS  의존 완료: P8-frontend
PASS  registry 중복 없음: web/src/components/PersonGrid.tsx
WARN  registry 에 다른 패키지로 이미 있음: registry.md → | 문서 | 결정 카드 D11 LLM 판정기 공급자 등록표·활성 스위치·기본 openai | docs/wiki/decisions/D11-llm-
PASS  registry 중복 없음: docs/wiki/packages/P8b-persons-grid/tests.md
WARN  registry 에 다른 패키지로 이미 있음: tests.md → | 문서 | 테스트 기록 — 프론트 Vitest 135건·E2E 4건을 표 1줄씩(무엇을 확인·입력 → 기대·결과·검출한 변이 ID), 총계와 
WARN  registry 에 다른 패키지로 이미 있음: save_evidence.py → | 스크립트 | 증거 저장 전용 통로 — 명령을 가드 검사 후 실행해 출력 전체·머리줄 5개·exit 를 evidence 에 직접 저장(비밀 검
== 결과: FAIL=1 WARN=3 ==
```
FAIL 1 = 이 문서(02-plan-verify.md)가 아직 없었다는 것 — 이 문서 작성으로 해소(2차 참조). WARN 3 = 01-plan 이 "고치는 기존 파일" 로 적은 `registry.md`·`tests.md`·`save_evidence.py` 가 registry 에 다른 패키지 행으로 이미 있다는 뜻 — 01-plan 56행이 "새 행이 아니라 비고 확장" 이라 적었고(산출물 절), 이 패키지 `tests.md` 는 경로가 다른 새 파일(`packages/P8b-persons-grid/tests.md`)이며 `save_evidence.py` 는 쓰는 도구이지 산출물이 아니다 → 의도된 WARN, 소견으로 올리지 않는다.

### 2차 — 02-plan-verify 작성 뒤 (`evidence/20261027-1322-verifier-verify-plan-2.txt`)
```
# 명령: bash .claude/scripts/verify-plan.sh P8b-persons-grid
# 시각: 2026-10-27T13:22:13+09:00
# cwd: /Users/sunwoo/Desktop/Portfolio/Relationship
# HEAD: fe76931 (dev2)
# exit: 0
# ---
== verify-plan P8b-persons-grid  (2026-10-27 13:22) ==
PASS  존재: docs/wiki/packages/P8b-persons-grid/01-plan.md
PASS  존재: docs/wiki/packages/P8b-persons-grid/02-plan-verify.md
PASS  카드 존재: D15
PASS  패키지 id 등록됨: P8-frontend
PASS  Refs 있음: - [ ] U0 `GET /persons` 응답에 `aliases: list[str]` — [backend-
PASS  Refs 있음: - [ ] U1 인물 화면 카드 그리드 + 이름·별칭 검색 + 목록 폭 단언 보강(Vitest) — [fro
PASS  Refs 있음: - [ ] U2 사이드바 최근 5명 + "전체 보기 →" — [frontend-agent] `AppShell
PASS  Refs 있음: - [ ] U3 E2E 갱신 + 목록 폭 `boundingBox()` 단언 — [frontend-agent]
PASS  Refs 있음: - [ ] U4 자동 판정 전체 + 문서 — [frontend-agent: 판정 실행·`tests.md`·`
PASS  Refs 있음: - [ ] U5 사람 점검 — [사용자·메인 세션] 판정 표 14행(데스크톱·모바일 폭에서 그리드·검색·사이
PASS  backlog 일치: D15 "코드에서 지켜야 할 것" 전부 · 백엔드 변경은 `GET /persons` 응답에 `aliases`
PASS  의존 완료: P8-frontend
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: web/src/components/PersonGrid.tsx
WARN  registry 에 다른 패키지로 이미 있음: registry.md → | 문서 | 결정 카드 D11 LLM 판정기 공급자 등록표·활성 스위치·기본 openai | docs/wiki/decisions/D11-llm-
PASS  registry 중복 없음: docs/wiki/packages/P8b-persons-grid/tests.md
WARN  registry 에 다른 패키지로 이미 있음: tests.md → | 문서 | 테스트 기록 — 프론트 Vitest 135건·E2E 4건을 표 1줄씩(무엇을 확인·입력 → 기대·결과·검출한 변이 ID), 총계와 
WARN  registry 에 다른 패키지로 이미 있음: save_evidence.py → | 스크립트 | 증거 저장 전용 통로 — 명령을 가드 검사 후 실행해 출력 전체·머리줄 5개·exit 를 evidence 에 직접 저장(비밀 검
== 결과: FAIL=0 WARN=3 ==
```
FAIL 0 · WARN 3(1차와 같은 의도된 WARN).

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표" 77~88행)
근거 열에는 카드 파일명 + 인용 문장을 쓴다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 2장 표(55행~) 제외 칸: "고민 상담 기능 / 인물 간(A–B) 관계 저장 / **관계 태그 필터링** / 상담 페르소나 / 음성 입력 / 네이티브 앱". 01-plan "하지 않는 것" 36행: "**관계 태그 필터 컨트롤**(`relation_tag`·`hierarchy` 로 거르는 `<select>`·토글·칩) — 기획서 2장 표 제외 칸 '관계 태그 필터링', 원칙7, D15 결정 3". 판정 2행이 이를 값으로 잡는다: "`combobox`·`listbox`·`radio`·`checkbox`·`switch` 0 · 태그 문자열(예: '직장')로 검색 → 태그만 일치하는 인물은 **안 나옴**". `CR-003.md` §1: "**제외 칸 '관계 태그 필터링'은 움직이지 않는다** — 검색은 이름·별칭 문자열만 받고 태그로 거르는 컨트롤을 두지 않는다". `D15` 결정 3: "**관계 태그 필터 컨트롤은 두지 않는다.** … 넣고 싶으면 별도 CR". 나머지 제외 5항은 이 패키지가 건드리지 않는다(화면 배치·조회 응답 필드뿐). |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | CLAUDE.md 원칙5 "프론트 화면은 3개로 고정: 채팅 / 인물 카드 / 브리핑" ↔ 01-plan 38행 "**새 라우트·새 화면·라우트 밖 패널** — 원칙5. 라우트는 … 3경로 그대로, `web/src/routes.ts` 무변경" + 판정 3·12행(`git diff --stat 3bd5025..HEAD -- web/src/routes.ts` 빈 출력, 서랍 1파일뿐). `D15` 파급: "CLAUDE.md 원칙: 5(화면 3개)·7(제외 범위) 그대로 — 문장 교체 없음". 원칙7 ↔ 점검표 1행 + 01-plan 39행 "**서버 문자열 가공** — 원칙7·결정 L 경계·D15 결정 6 … 검색 하이라이트도 하지 않는다" + 판정 7행. 원칙8 ↔ 01-plan 판정 14행 "실서버 인물 수(6명 이상이어야 5명 자르기가 보인다 — 모자라면 그 사실을 적는다)" · 리스크 6 "개발 DB 에 확인용 인물을 더 만들지는 사용자 결정 — 원칙8". 원칙1~4·6·9(ER·임계치·패턴·trace)는 이 패키지가 ER 코드·루프·trace 를 건드리지 않아 해당 없음 — U0 는 `list_persons` 읽기 전용(`app/api/read.py` 148행, `select(Person, …)` 만)이고 01-plan U0 "원문 필드 없음·쓰기 0(P8 판정 4·7행 단언 유지)". |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `D15-persons-screen-layout.md` "코드에서 지켜야 할 것" 7문장(23~29행)을 01-plan 판정 표 1~7행과 대조했다 — 2~7행은 **글자 그대로** 같다(예: 5행 "`[data-screen="persons"]` 목록 모드의 **조상·자신 어디에도** `max-w-*`·`mx-auto` 가 없다(R-U10C-3 — …) 상세 모드는 `data-testid="card-wrap"` 가 `mx-auto w-full md:w-3/4` 이고 `max-w-*` 가 없다"). 1행은 보정(2026-10-21) 뒤 문장과 뜻이 같고 두 토막만 빠졌다: D15 23행 "(결정 K (나), **2026-10-21**)" 의 날짜와 끝의 "**, 마이그레이션 0**" — 마이그레이션 0 은 판정 8행 "`git diff --stat 3bd5025..HEAD -- alembic` → 빈 출력(마이그레이션 0)" 이 따로 잡으므로 충돌이 아니라 문구 누락(R-1 권고). 결정 K (나)의 네 문서 정합: D15 결정 2 "새 엔드포인트·새 쿼리 파라미터 없음 … **보정** … 응답에 `aliases: list[str]` … 1필드를 더한다 … 스키마 v2·툴 시그니처 v2 는 그대로" · `CR-003.md` §2 "**이행 중 보정(2026-10-21, P8b 01-plan 결정 K)** … `GET /persons` 응답에 `aliases` 1필드를 더한다(읽기 전용, 새 엔드포인트·쿼리 파라미터 없음 — 위 (나) 와 같은 모양)" · `docs/backlog.md` 89행 "백엔드 변경은 `GET /persons` 응답에 `aliases` 필드를 더하는 것뿐(결정 K (나), 읽기 전용, 스키마 v2 무변경 …)" · 01-plan 20행 "③ '새 API 없음' 은 그대로다(새 엔드포인트·쿼리 파라미터 없음)" — 네 곳이 같은 뜻이다. CR-003 §3 ③ 표의 "(가) … **새 API 없음** 유지" 는 승인 당시 원문이고 §2 보정 문단이 그 위에 얹혀 있어 모순이 아니다. 전제 사실도 코드로 확인: `app/api/schemas.py` 312~319행 `PersonListItemOut` = `id, display_name, relation_tag, hierarchy, last_contact_at` 5필드, 362행 `PersonCardOut.aliases: list[str]` — 01-plan 16~17행 그대로. |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `S3.1-schema-v2.md` 머리 "persons(id, user_id, display_name, relation_tag, hierarchy, created_at, updated_at) / person_aliases(id, person_id, alias, source, embedding vector(1536), confirmed_at)" — U0 는 이 두 테이블을 **읽기만** 한다(새 열·마이그레이션 없음, 판정 8행 `alembic` diff 빈 출력). `S3.2-tools-v2.md` 머리 표의 툴 7종 시그니처는 그대로 — `aliases` 는 조회 API(`GET /persons`, P8 에서 생긴 FastAPI 응답 모델)의 필드이지 툴·테이블이 아니다. `D15` 파급: "S 카드: 무변경(스키마 v2·툴 시그니처 v2). 조회 API 응답은 `GET /persons` 에 `aliases` 1필드 추가(읽기 전용, 결정 K (나)) — S 카드가 정하는 범위 밖(조회 API 는 P8 에서 생긴 것)". 01-plan 4행 "구현하는 명세: 없음(S 카드 무변경 — D15 'S 카드: 무변경')", 34행 "읽기 전용, 스키마 v2·툴 시그니처 무변경, 새 엔드포인트·쿼리 파라미터 없음". 임계치·ask_user 는 이 패키지가 ER·루프를 건드리지 않아 해당 없음. |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `packages/P8-frontend/04-review.md` 296행 "결과: 완료 — [필수] 0 · [권고] 10 … P8b 는 이 문서 뒤 시작 가능(backlog 89행 '의존: P8-frontend 04-review 완료')", 297행 "승인: 사용자 (2026-10-21)" — 커밋 `fe76931`(`.claude/gitlog.md` "fe76931 2026-10-21 docs(P8-frontend): 사람 점검을 끝내고 프론트 3화면 패키지를 완료로 닫는다", 변경 파일에 `04-review.md | 297 +`). `docs/backlog.md` 88행 "**P8-frontend 완료 2026-10-21** … 마지막 제품 코드 커밋 `3bd5025`" · 89행 "의존: P8-frontend 04-review 완료(충족 2026-10-21)". P4 게이트: `packages/P4b-er-redesign/04-review.md` 144행 "결과: 완료". 01-plan 7행 주장 "`3bd5025..fe76931` 두 커밋은 문서뿐" — 내가 실행한 `git diff --stat 3bd5025..HEAD -- app alembic web` 은 **빈 출력**(exit 0) → 무변경 기준 해시 `3bd5025` 가 HEAD 와 제품 코드 동일. 이어받는 소견: `04-review.md` §6 R-U10R-10 "기준 해시를 **마지막 FIX 커밋 뒤**로 두거나 … `git diff --stat <fix>..HEAD`" → 01-plan 8행이 FIX-035(`735f391`) 뒤인 `3bd5025` 를 채택. 닫는 R: `docs/wiki/review-index.md` 에 `P8b` 0건, `INDEX.md` 77행 "… \| — \|" — 01-plan 4행 "닫는 검증: 없음" 과 일치. 미커밋 변경은 문서 5개 + 이 패키지 폴더뿐(`git status --short`: `docs/backlog.md`·`HANDOFF.md`·`CR-003.md`·`D15…md`·`journal.md`·`packages/P8b-persons-grid/`), 제품 코드 0. |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 89행 "수용기준: " 뒤 문자열과 01-plan 115행("- " 뒤)을 `diff` 로 대조 → **IDENTICAL**(스크래치패드 `bl.txt`/`pl.txt`). verify-plan 1차 `PASS  backlog 일치`. 기준 원문: "D15 "코드에서 지켜야 할 것" 전부 · 백엔드 변경은 `GET /persons` 응답에 `aliases` 필드를 더하는 것뿐(… `app/api/read.py`·`app/api/schemas.py`·`tests/test_api_read_persons.py` 밖 `app/`·`alembic/` diff 0) · `card.test.tsx`·`routes.test.tsx`·E2E `card.spec.ts` 사이드바 단언 5명으로 갱신 · 목록 폭 단언 보강(R-U10C-3, 조상 전부 + `boundingBox()`) · typecheck·Vitest·build·E2E 통과 · 상세 가운데 75% 는 `3bd5025` 유지 — 사용자 승인 2026-10-16, 결정 K·A~J 확정 2026-10-21". 01-plan "해석" 표 ㄱ~ㅂ 은 새 기준을 더하지 않고 각 구절을 판정 행(1~7 · 8 · 4 · 5 · 9~11 · 5)으로만 묶는다. |
| 7 | 작업 단위마다 Refs 태그 | 통과 | verify-plan 1차 `PASS  Refs 있음` × 6(U0~U5). 01-plan 75행 U0 "Refs: P8b-persons-grid D15 CR-003 원칙7 원칙9 R-U10R-10" · 76행 U1 "… D15 CR-003 결정L 원칙5 원칙7 R-U10C-3" · 92행 U2 "… 결정N 원칙5 R-U10C-3" · 102행 U3 · 110행 U4 "… 원칙8 R-U10C-3 R-U10R-10" · 111행 U5 "… 결정L 결정N 원칙5 원칙8". 속한 P·기대는 D·CR·이어받는 R 이 모두 들어 있다(SKILL.md 태그 규칙 "닫는 R, 기대는 D, 구현하는 S, 속한 P, 해소한 F-id/FIX/CR"). 단위 크기: U0~U3 각각 파일 1~4개·커밋 1개 후보, U4 판정·문서, U5 사람 점검 — 커밋 하나 크기다. |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §1 "`.env`, `*.pem`, `*.key` … 읽지도 쓰지도 않는다" — 01-plan 의 판정 명령은 `npm --prefix web run typecheck/test/build/e2e`·`POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_api_read_persons.py`·`git diff --stat`·`grep` 뿐이고 비밀 파일을 열지 않는다. §4 "로컬 서버 이외로 데이터 전송(`curl -d/-F/-T` …) 금지" — 판정 방법 132행 "Vitest 행은 `fetch` 를 가짜로 바꿔 끼운 기존 방식 … E2E 는 `installFakeApi` … 실 네트워크 0", 167행 "**새 shadcn 부품을 내려받지 않는다**"(외부 레지스트리 요청 0), 판정 12행 P8 불변식 7·9(`VITE_*KEY`·외부 글꼴) 재실행. §3 재귀 삭제·§4 `DROP`·`prune` 해당 명령 없음. §4b(FIX-014) — 01-plan 73행 "출력은 전부 `python3 .claude/scripts/save_evidence.py …`", FIX-033 (d) "임시 파일·변이 스크립트는 스크래치패드 리터럴 절대 경로". 커밋은 "단위마다 `/commit`"(메인 세션), 서브에이전트 커밋 없음. |

### 위임 프롬프트 "특히 볼 것" 5항 판정

1. **결정 K (나) ↔ "새 API 없음"** — 모순 없음(점검표 3행). 새 엔드포인트·쿼리 파라미터 0, 응답 필드 1개. 네 문서(D15 결정 2·코드 규칙 1번째 줄 · CR-003 §2 · backlog 89행 · 01-plan 20·34행)가 같은 뜻. 잔존 불일치 2곳은 R-2·R-3(문서 문구).
2. **판정 8행 + 1행이 "U0 밖 백엔드 0" 을 덮는가** — `app/api/routes.py` 가 새면 8행(`-- app alembic ':!app/api/read.py' ':!app/api/schemas.py'` 가 `routes.py` 를 제외하지 않음)이 잡는다 · `alembic/` 은 8행 두 번째 명령 · `read.py`·`schemas.py` 는 1행 "변경이 `aliases` 추가(+ docstring)뿐(사람이 대조)". **빈틈 1**: `tests/` 는 수용 기준·8행 어디에도 없어 `tests/conftest.py`·다른 `tests/test_*.py` 변경은 어느 행도 잡지 않는다(수용 기준이 `app/`·`alembic/` 만 말하므로 기준 위반은 아니지만 "U0 밖 백엔드 0" 의 뜻에는 구멍) → R-4.
3. **FIX-033 (a)~(d)·V1-6/V3-1** — 01-plan 73행이 (a)~(d) 네 규칙을 위임 프롬프트에 넣도록 명시, 단위마다 "변이 → 잡는 테스트" 표(U1 11·U2 5·U3 3). V1-6 = `review-u10-closeout.md` 42행 M4 "목록을 감싼 안쪽 `<div className="mt-4">` 에 `mx-auto max-w-3xl` … **`31 passed (31)` — 생존**" 과 같은 자리. 판정 5행 Vitest 는 "`<App />` 렌더, 그리드 요소에서 `main` 까지 모든 조상 + 그리드 자신 + `[data-screen="persons"]` 의 자손 중 그리드를 감싼 요소 전부에 `mx-auto`·`max-w-*`·`md:w-*` 클래스 0" — M4 의 `<div>` 는 `section` 과 그리드 사이의 조상이므로 검출된다. E2E V3-1: 1280px 에서 사이드바 256 을 뺀 `main` 콘텐츠 ≈ 976px 인데 `max-w-3xl`=768px 이면 차이 208px > 허용 2px → 검출. 설계는 맞다. 단, "그리드 요소" 를 찾을 `data-testid` 가 계획에 없다 → R-5.
4. **14행 "수정 반영 횟수 1 상한"** — `packages/P8-frontend/01-plan.md` 결정 L(305행~) "화면마다 한 번 구현 + 사람 점검(32행) 뒤 '수정 필요' 를 **한 번만** 반영" ↔ 01-plan 판정 14행 "**'수정 반영 횟수: n' 줄 — n ≤ 1**(P8 결정 L 상한, 넘으면 CR 여부를 사용자에게)", 45행 "**맞춤 디자인 반복** — P8 결정 L 시간 상한. 사람 점검 뒤 수정 1회만". 일치.
5. **리스크 미결이 구현을 막는가** — 막지 않는다. 리스크 4(한글 조합·NFC)는 "(a) 그대로 둔다(추천)" + "사람 점검 14행 ③ 에서 보고 이상하면 '수정 1회' 안에서 (b)" 로 처리 경로가 있고 결정 C 가 "유니코드 NFC/NFD 정규화는 넣지 않는다" 로 확정. 리스크 8(P8 `tests.md` 갱신 여부)은 이 패키지 `tests.md` 에 "변경/삭제(P8 tests.md 몇 행)" 로 적는 것으로 닫히며 P8 표 갱신은 사용자 결정으로 남는다 — 구현·판정과 무관. 다만 리스크 4 의 (a) 가 U1 위임문에 "조합 이벤트 처리 코드를 넣지 않는다" 로 명시돼야 FIX-033 (b) 왕복이 없다 → R-6.

### 코드 사실 대조 (01-plan 이 인용한 행 번호 — 표본 전부 일치)

`app/api/schemas.py` 312~319행 `class PersonListItemOut` 5필드 ✓ · 358~367행 `PersonCardOut.aliases: list[str]` ✓ · `web/src/api/types.ts` 53~59행 5필드·99행 `aliases: string[]` ✓ · `web/src/api/client.ts` 107행 `export function getPersons(): Promise<PersonListItemOut[]>` 인자 없음 ✓ · `web/src/components/AppShell.tsx` 36행 주석 "`#/persons` 본문과 같은 컴포넌트"·37행 `data-testid="sidebar-persons"`·141행 `<main className="min-w-0 flex-1 overflow-y-auto p-6 pt-14 lg:pt-6">`(`p-6` = 좌우 24px → 결정 J 의 48) ✓ · `web/src/screens/PersonCardScreen.tsx` 334~337행 목록 분기 `<div className="mt-4"><PersonList /></div>`·339행 `data-testid="card-wrap" className="mx-auto w-full md:w-3/4"` ✓ · `web/e2e/card.spec.ts` 8~11행 `PERSONS` 2명·53·108행 사이드바 `김팀장` 클릭·76행 `toHaveCount(3 + PERSONS.length)` ✓ · `web/src/__tests__/card.test.tsx` 116~126행 목록 폭(`section` 한 요소만)·128~137행 상세·139~146행 "필터·검색 컨트롤이 없다"·309~313행 "같은 컴포넌트(PersonList)를 import" ✓ · `web/package.json` 10~18행 `typecheck`="tsc -b"·`test`="vitest"·`build`="tsc -b && vite build"·`e2e`="playwright test" ✓ · `web/src/__tests__/routes.test.tsx` 72~79행 `nav.querySelectorAll('a')` 3링크 ✓ · `web/src/screens/ChatScreen.tsx` 230행 `isComposing` ✓ · 재사용 산출물 존재: `routes.ts` `HREF`(9행)·`parseHash`(25행), `lib/format.ts` `formatDate`(6행), `__tests__/helpers.ts` `installFakeMatchMedia`(7행), `e2e/fixtures.ts` `freezeClock`(35)·`installFakeApi`(39)·`expectNoStrayRequests`(90), `components/ui/` 8개(badge·button·card·collapsible·sheet·skeleton·sonner·tabs — `input` 없음) ✓ · `PersonList.tsx` 에 `limit`·`slice` 없음, `data-testid="person-list"`·`PERSON_LIST_NOTICE` 있음 ✓ · registry 235·236·238·245·246·247·249·250·254·256·258행 내용이 01-plan "기존 산출물 재사용" 표와 일치, `PersonGrid` 0건 ✓.

**불일치 2건**: (i) 01-plan 75행 U0 "`_person_out` 재사용 여부는 registry **58행** 보고" — registry 58행은 `app/tools/__init__.py`(P2-tools 툴 재export)이고 `_person_out` 은 `app/tools/persons.py` 432행(registry **61행**). 또 `app/api/read.py` 175~177행 주석 "정렬은 DB 콜레이션에 맡기지 않고 `_person_out` 과 같은 Python `sorted()`(코드포인트 순)" 이 카드 응답의 별칭 정렬 규칙이다 → R-7. (ii) 01-plan 판정 12행 `grep -rlE "Sheet\|Dialog\|Drawer" …` 를 이 Mac(BSD grep)에서 글자 그대로 실행하면 **0건(exit 1)** — `-E` 에서 `\|` 는 교대가 아니다. P8 01-plan 369행 원문은 `"Sheet|Dialog|Drawer"` 이고 그 명령은 `web/src/components/AppShell.tsx` 1파일을 낸다(내가 둘 다 실행). 표 안 `|` 이스케이프가 명령에 섞여 들어간 것 → R-8.

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)

보류 소견 없음([필수] 0). verify-plan FAIL 은 이 문서 부재뿐이라 `findings.py` 소견을 만들지 않았다(05-remediation.md 없음). 아래는 [권고] — 승인 전 메인 세션이 01-plan 문구를 고치거나(R-1~R-4·R-7·R-8), 위임 프롬프트에 넣거나(R-5·R-6·R-9), 패키지 완료 때 닫는다.

- **R-1 [권고] 판정 1행 D15 인용에서 두 토막 누락.** D15 23행 "(결정 K (나), 2026-10-21)" 의 날짜와 끝 ", 마이그레이션 0" 이 빠졌다. 해석 ㄱ "일곱 문장을 … **글자 그대로** 한 행씩" 이라 적었으므로 1행 문구를 D15 23행과 같게 맞추거나, 1행 끝에 "(마이그레이션 0 은 8행)" 을 적는다. 판정 내용은 8행이 덮고 있어 결과에 영향 없음.
- **R-2 [권고] 01-plan 65행 `card.spec.ts` 행 끝 "새 픽스처 인물의 카드 요청이 있으면 가짜 표에 추가(결정 K **(가)**)" — K (나) 확정 뒤 잔존.** (나)에서는 그리드가 카드 API 를 부르지 않으므로 가짜 표에 더할 카드 응답은 "타일 클릭 → `#/persons/:id`" 로 열 그 인물 1명분뿐이다. "(결정 K (나) — 타일 클릭으로 여는 인물만)" 으로 고친다.
- **R-3 [권고] `docs/wiki/INDEX.md` 77행 "frontend-agent(`web/` 만, 백엔드 0)" 가 K (나)(U0 backend-agent, `read.py`·`schemas.py` 변경)와 어긋난다.** 문서만. 계획 커밋 또는 패키지 완료 때 "frontend-agent + backend-agent U0(`aliases` 1필드)" 로.
- **R-4 [권고] `tests/` 의 U0 밖 변경을 잡는 행이 없다.** 판정 8행에 `git diff --stat 3bd5025..HEAD -- tests ':!tests/test_api_read_persons.py'` → 빈 출력 한 줄을 더하면 "U0 밖 백엔드 0" 이 `app/`·`alembic/`·`tests/` 세 곳을 전부 덮는다. 수용 기준 원문은 바꾸지 않는다(기준은 `app/`·`alembic/` 만 말하므로 이 행은 보조 판정).
- **R-5 [권고] 그리드 컨테이너·타일의 `data-testid` 가 계획에 없다.** 판정 5행 Vitest "그리드 요소에서 `main` 까지" 와 E2E `boundingBox()`, 판정 1행 "타일 필드 4개+별칭" 은 그 요소를 찾을 선택자가 필요하다. 기존 `person-list`(`PersonList.tsx` 30행) 관례대로 `data-testid="person-grid"`(컨테이너)·`data-testid="person-tile"`(타일 `<a>`) 를 U1 위임문에 값으로 적어 두면 FIX-033 (b) 왕복이 없다(사용자 메모 "위임 전에 계획이 비워 둔 상수를 먼저 확정").
- **R-6 [권고] 리스크 4 의 기본값 (a) 를 U1 위임문에 명시.** "검색 `onChange` 에 `isComposing`·`compositionend` 처리를 넣지 않는다(리스크 4 (a)); NFC/NFD 정규화도 넣지 않는다(결정 C)". 지금 문장은 "후보 (a)/(b) … 추천" 이라 구현자가 FIX-033 (b) 로 멈출 수 있다.
- **R-7 [권고] 01-plan 75행 "registry 58행" → "registry 61행(`app/tools/persons.py` `_person_out`)" 으로 정정하고, U0 의 정렬 규칙을 값으로 적는다**: `app/api/read.py` 177행과 같은 `sorted()`(코드포인트 순) — 판정 1행 "카드 응답 `aliases` 와 같은 값·같은 순서" 가 이것을 뜻한다. 또 U0 "별칭을 한 번의 조인/집계로(N+1 금지)" 는 판정 명령이 없다 — `tests/test_api_read_persons.py` 에 SQLAlchemy `event.listen(engine, "before_cursor_execute", …)` 로 질의 횟수를 세어 인물 수와 무관하게 상수임을 단언하거나, 그것이 과하면 U0 단위 리뷰(verifier)가 `list_persons` 본문으로 확인한다고 적는다.
- **R-8 [권고] 판정 12행 grep 패턴 `"Sheet\|Dialog\|Drawer"` → `"Sheet|Dialog|Drawer"`.** 표 셀 안이라면 코드 스팬 밖에서 `\|` 로 이스케이프하지 말고 P8 불변식 10(369행)처럼 쓰거나, 명령을 표 밖 코드 블록에 둔다. 글자 그대로 실행하면 0파일이 나와 "1파일뿐" 기대가 거짓 실패한다(내가 bash 에서 둘 다 실행해 확인).
- **R-9 [권고] 판정 10행 기준선.** "총 건수 = 기준선(U1 시작 전 같은 명령으로 측정해 03-log 에 기록)" — U0 가 먼저이므로 기준선 측정은 **U0 전**(지금 HEAD, P8 04-review 재실행 값 Vitest 137)으로 적는 편이 어긋남이 없다. U0 는 백엔드라 Vitest 수에 영향이 없지만 기록 시점을 하나로.

## 4. 결정
결과: 통과 — (표기만 메인 세션이 2026-10-27 수정: 원문 `**통과**` 의 굵게 표시가 `stage-gate.sh` 의 `^결과:[[:space:]]*통과` 정규식과 어긋나 backend-agent 의 제품 코드 쓰기가 거부됨 — 판정 내용 무변경, 하네스 FIX 후보) 점검표 8/8 통과, [필수] 0, [권고] R-1~R-9(전부 문구·위임문 보완, 코드·수용 기준 변경 없음). 근거: 기계 검증 2차 FAIL 0(아래), WARN 3 은 의도(1절), 수용 기준 = backlog 89행 `diff` IDENTICAL, D15 7문장 ↔ 판정 1~7행 대조(1행 두 토막 누락은 R-1), 결정 K (나) 네 문서 정합, 무변경 기준 해시 `3bd5025` 와 HEAD 의 제품 코드 diff 빈 출력(직접 실행), 01-plan 인용 행 번호 표본 전부 일치, V1-6/V3-1 이 M4 를 두 층에서 잡는 설계 확인.
승인: 사용자 (2026-10-27) — AskUserQuestion "승인". [권고] R-1~R-9 는 승인 전 메인 세션이 01-plan(개정 2)·INDEX 77행에 반영했고 기계 검증 재실행 FAIL 0/WARN 3(`evidence/20261027-1324-verify-plan-3.txt`). U0 부터 L-004 매번. 결정 K (나)·A~J 는 2026-10-21 사용자 확정.
