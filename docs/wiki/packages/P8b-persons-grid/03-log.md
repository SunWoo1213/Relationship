# P8b-persons-grid · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-10-27 13:30 · docs(P8b-persons-grid): 인물 화면 그리드·검색·사이드바 5명 계획을 검증·승인까지 마치고 활성화한다 · 0973858
- 변경: 신규 `01-plan.md`(architect 초안 2026-10-21 → 사용자 확정 결정 K (나)·A~J 반영 개정 1 → verifier [권고] R-1~R-9 반영 개정 2) · 신규 `02-plan-verify.md`(verifier 통과, 점검표 8/8, [필수] 0, 사용자 승인 2026-10-27) · 증거 5개(`evidence/20261022-0809·0810-verify-plan*.txt` 메인 세션, `20261027-1316·1322-verifier-verify-plan*.txt` verifier, `20261027-1324-verify-plan-3.txt` 재실행) · 이 03-log 생성 · `CURRENT.md active: P8b-persons-grid`. **결정 K 보정**: `decisions/D15-persons-screen-layout.md`(결정 2·코드 규칙 1줄·파급 S·갱신 이력) · `changes/CR-003.md` §2 보정 문단 · `docs/backlog.md` 89행 수용 기준("백엔드 diff 0" → "`aliases` 필드 추가뿐") · `docs/wiki/INDEX.md` 77행(backend-agent U0). journal DECISION 2줄·START 1줄.
- 이유(기획서·카드 연결): CR-003(사용자 승인 2026-10-16)·D15 를 코드로 옮기는 패키지. architect 가 D15 전제 오류("목록 전체를 이미 받음")를 코드(`schemas.py` 312~319행 `PersonListItemOut` 5필드)로 찾아 결정 K 를 선결로 올렸고, 사용자가 (나) `GET /persons` 응답에 `aliases` 1필드 추가를 골랐다 — CR-003 §2 가 예고한 "(나) 응답 1필드 추가(읽기 전용, 스키마 아님)" 갈래라 새 CR 을 내지 않고 D15 갱신 이력에 보정으로 기록했다. 새 엔드포인트·쿼리 파라미터는 없다(CR-003 ③(가) 유지).
- 정합성 확인: 원칙5(화면 3개 — 라우트 3개·서랍 1파일 불변식 판정 12행) / 원칙7(태그 필터 없음·서버 문자열 가공 0, 판정 2·7행) / D15 7문장 = 판정 1~7행 글자 그대로 / S3.1·S3.2 무변경(`aliases` 는 조회 응답 필드) / 보안 — 위반 없음. verify-plan 3차 FAIL 0 / WARN 3(registry 기존 행 재사용 — 의도).
- 남은 것 · 다음 단위: U0 `GET /persons` `aliases`(backend-agent, L-004) → U1 그리드+검색(frontend-agent) → U2 사이드바 5명 → U3 E2E+`boundingBox` → U4 자동 판정·tests.md·registry → U5 사람 점검(수정 1회 상한). Vitest 기준선 137(HEAD `fe76931`), 무변경 diff 기준 `3bd5025`. 1차 verifier 시도(2026-10-22)는 Fable 한도 429 로 중단돼 파일 없이 재시도했다(하네스 관찰: 한도 중단은 마커만 소비하고 산출물이 없다 — 재시도 때 마커 재생성 필요).
- Refs: P8b-persons-grid D15 CR-003 결정L 결정N 원칙5 원칙7 R-U10C-3 R-U10R-10

## 2026-10-27 15:45 · feat(P8b-persons-grid): 인물 목록 조회 응답에 별칭 목록을 더한다 · pending (U0, backend-agent)
- 변경: `app/api/schemas.py` `PersonListItemOut.aliases: list[str]`(+docstring) · `app/api/read.py` `list_persons` — 사용자 범위 별칭을 **질의 1회**로 모아 dict 에 담고 행마다 `sorted()` 코드포인트 순(카드 `get_person_card` 와 같은 규칙, `_person_out` 재사용 안 함 — registry 61행 보고 충족) · `tests/test_api_read_persons.py` 신규 5건(값·순서 = 카드 / 빈 배열 / SELECT 수 2 가 인물 3명·10명 동일 / 타 사용자 격리 / 원문 키 없음) + **기존 테스트 변경 1건**(137행 키 집합에 `"aliases"` — 메인 세션 사전 결정, 그 밖 11건 무수정) · `registry.md` 세 행 비고 · 신규 `tests.md`(6행). `web/` 0 · `alembic` 0.
- 이유(기획서·카드 연결): D15 결정 2 보정(결정 K (나), 2026-10-21) — 별칭 검색을 프론트에서 하려면 목록 응답에 별칭이 있어야 한다. 새 엔드포인트·쿼리 파라미터 없음(CR-003 ③(가)).
- 정합성 확인: 원칙7(원문 키 0)·원칙9(읽기 API, trace 0, 쓰기 0 `assert_no_writes`) / D15 코드 규칙 1번째 줄(판정 8행 두 diff 빈 출력) / S3.1·S3.2 무변경 / 보안 grep 0 — 위반 없음.
- 검증: backend-agent 17 passed·1958 passed·ruff → 메인 세션 재실행 17 passed·ruff·diff 범위 → **verifier 리뷰 통과**(`review-u0-read-persons-aliases.md`, [필수] 0 · [권고] R-U0-1~3): verifier 직접 17 passed · 1958 passed skip 0 · ruff · 변이 M1(N+1)·M2(정렬 제거)·M4(`display_name` 채움)·M5(`None`)·M6(`str.lower`)·M7(집계 키 오류) 전부 검출, **M3(별칭 질의 `user_id` 조건 제거) 생존 = 출력 동등·질의 비동등**(응답은 내 인물 id 로만 찾아 타 사용자 별칭이 새지 않음, 조건은 성능·심층 방어 — 잡으려면 `cursor.rowcount` 단언 1건, FIX 후보) · 진단 D1/D2 로 SELECT 2 = 목록 1 + 별칭 1, 계측(`db_session.get_bind()` Connection) 유효. 증거 `evidence/20261027-1436-u0-read-persons-aliases.txt`·`-1436-u0-pytest-all.txt`·`-1435-u0-ruff.txt`·`-1437-u0-mutation.txt`(구현자) · `-1535-verifier-u0-{tests,full-regression,lint}.txt`·`-1537-verifier-u0-mutation.txt`(verifier).
- 과정 기록: 1차 위임은 `stage-gate.sh` 정규식(`^결과:\s*통과`)이 02-plan-verify 의 `결과: **통과**`(굵게)를 못 읽어 코드 쓰기 거부 → 표기만 제거(판정 무변경, 하네스 FIX 후보) · 2차는 Docker 데몬 꺼짐으로 pytest 전부 skip → 메인 세션이 Docker·Postgres 기동 뒤 같은 에이전트 재개(skip 증거 1개 삭제) · R-U0-3 01-plan 75행 "177행" → "188행" 으로 행 번호 갱신.
- 남은 것 · 다음 단위: U1 그리드+검색(frontend-agent — `types.ts` `aliases` 동기화 포함, testid 4종, 결정 A~D·G~I, 리스크 4 (a), 변이 V1-1~V1-11). R-U0-1 `rowcount` 단언은 FIX 후보.
- Refs: P8b-persons-grid U0 D15 CR-003 원칙7 원칙9 R-U10R-10 R-U0-1 R-U0-2 R-U0-3
