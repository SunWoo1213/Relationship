# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`·`fixes/FIX-nnn.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-11-14 오후 (**CR-005 개정 ② — 플랫폼을 AWS 최소로 다시 바꿈**: 사용자 "배포를 aws로 최소로 한다고 하면 어때?" → 비교표 → 선택 "AWS 최소(EC2 1대 + Compose)" · "실제로 띄우는 건 아직 말고 계획부터" · "무료티어 신규 계정, 비상업". D17 개정·관련 문서 10개 되돌림/갱신(커밋 중). Vercel 안 P9 01-plan(미커밋)은 폐기 → **architect 에 AWS 최소 안 01-plan 재작성 위임**(계획·파일·로컬 compose 스모크까지만, EC2 기동은 사용자 지시 뒤). 다음: 결정 묻기(인스턴스 t3.micro/t4g.small·도메인 유무→sslip.io·리전 서울·SSH) → verifier 02-plan-verify → 활성화 → backend-agent(Dockerfile·compose.prod·Caddyfile·entrypoint) → user-setup 11/12 → 사용자 "띄워 달라" 때 U-기동. 아래는 1차(Vercel) 기록.) (**배포 번복 → CR-005 승인**: 사용자 11-13 "Vercel 로 배포, DB 는 무료 티어" → 11-14 결정 A Vercel Python 함수 · B Neon · C GitHub Actions 5분 스케줄이 `/api/briefings/run` 호출 · D 보호 없이 **11-18(수) 졸업평가까지만 공개 뒤 종료**. `changes/CR-005.md` 승인 상태 · **CR-005 문서 이행 끝(미커밋)**: D17 신설 · D07 대체됨 · S3.6 운용 보충 · CLAUDE.md 스택 3줄 · backlog P9 · review-index R14 · INDEX P9 · user-setup 09/02 상단 · proposal 상단 · security §5. 되돌릴 코드 없음 → frozen 생략(문서 커밋 1건, U2 커밋 직후). **architect P9-infra 01-plan 작성 중**. **일정**: 11-18 전 배포 필수 → **P2b 는 U2 커밋까지만 하고 보류**, CR-005 문서 이행(frozen 짧게) → P9-infra 재계획(architect: `vercel.json`·함수 진입점·`/briefings/run` 비밀 헤더·GH Actions 스케줄·Neon 마이그레이션·종료 절차) → 구현 → 배포. U2 verifier 리뷰 **통과**([필수] 0 · [권고] 5 → 03-log) → **U2 커밋 `3a1bcec`** → P2b **보류**(CURRENT active none, 메모) → **CR-005 문서 커밋 중**. 아래 11-09 메모는 이력.) (P5b-query-turn 완료·승격 끝(dev2=dev=main `f67d8e4`). 사용자 2026-11-09 "다음 일들도 쭉 진행, 배포는 하지 않음" → 11-14 번복됨. 다음 패키지 **`P2b-person-delete`**(`DELETE /persons/{id}`, backlog 38행) — 01-plan 끝(U1 판별 함수 · U2 삭제 서비스 · U3 라우트 · U4 프론트 카드 인라인 확인 · U5 판정·문서), 결정 A~K **확정**(사용자 2026-11-09: A 서버 2단계+화면 확인 · B 프론트 포함 · C 참조 행 통째 삭제 · G id 참조만+한계 문서화, 나머지 추천안 위임). verifier 02-plan-verify **통과**([필수] 0 · [권고] R-1~R-4 → 03-log). **활성화** · 계획 커밋 `2ff0efb` → **U1 구현 끝**(새 `app/api/delete.py`·`tests/test_person_refs.py` 41건, 전체 2177 skip 0, 변이 9/9, 미커밋) → verifier U1 리뷰 1차 **보류**([필수] R-U1-1 계획 문구 `resume.person_ids` 오기 → 01-plan·02-plan-verify 보정 2줄 **넣음**) → 재리뷰 **통과** → **U1 커밋 `a4b44b1`** dev2 푸시 끝 → **U2 backend-agent 진행 중**(삭제 서비스 `delete_person`; 11-09 API 타임아웃으로 끊겨 11-13 SendMessage 로 재개 — tests.md 쓰는 단계였음)(위임문에 R-U1-2 docstring 7→8곳 · R-U1-3 규칙 2 `tool_name` 없이 고정 테스트). (U1 위임 때(R-1 따옴표 요령·R-2 원칙8 범위·R-4② `client.request("DELETE", …)` 포함). 단위마다 verifier 커밋 전 리뷰 → 커밋 → dev2. 그 뒤 FIX 후보(R-U10R-4 오병합 계열 등) → 하네스 후보.)

active: **none** | frozen: none | **origin/dev2 = origin/dev = origin/main = `f67d8e4`** | 미커밋: `journal.md`(훅이 쓴 COMMIT·PUSH·RELEASE 3줄 — 다음 커밋에 같이) | DB `capstone2-postgres-1`(5433): 개발 `relationship`(인물 12), 테스트 `relationship_test` | 기준선: 백엔드 **2136 passed skip 0** · 프론트 156 passed · E2E 4 | 로컬 서버 :8000(`--reload`, 메인 세션이 직접 기동 가능 — L-007)

## 최근 끝낸 것
| 무엇 | 결과 | 기록 |
|---|---|---|
| **P5b-query-turn 완료(11-09)** | U1 `1dccb95` · U2 `06b7bb5` · U3 `a002706` · U4 `18219ba` · U5 `49c1c67` · U6 `a004cdd` · U7 `e49f78d`·`cf26dce` · 04-review `fb8841a`. verifier `완료`([필수] 0), 판정 표 통과 20·문구 보정 1, 변이 7/7, 실 LLM 4차 ① 관계 질문 정답 | `packages/P5b-query-turn/04-review.md`·`03-log.md`·`tests.md` |
| 하네스 L-006(11-07) | 사용자 승인 관문 폐지, 완성 확인 1회만 | `be67c76`, `lessons/L-006-*` |
| 하네스 L-007(11-08) | 서버 기동 `uvicorn app.main:… --env-file .env` 만 safety-guard 예외 | `9eb9d2e`, `lessons/L-007-*` |
| P8b-persons-grid 완료(10-28) | `678bca7` | `packages/P8b-persons-grid/04-review.md` |

## 진행 중 (이 턴에서 멈춘 자리)
- 없음. 완료 커밋 `f67d8e4` → `dev2:dev`(678bca7..f67d8e4) → `dev:main`(0e943eb..f67d8e4, fast-forward) 끝.

## 바로 다음에 할 것 (순서대로)
1. 사용자 요청 대기. 새 작업을 시작하면 첫 커밋에 미커밋 `journal.md` 3줄을 같이 넣는다.
2. 다음 패키지 후보(사용자 요청 대기): **① 구글 로그인 + 사용자 격리**(CR, P9 착수 조건 R-U10D-3·F-fbaaae) → P9-infra(R-U10D-1~4·S1~S15) · P10 평가.
3. FIX 후보: R-U10R-4·이번 ⑦ — 호칭 단독/같은 성·같은 직함 2명일 때 자동 병합("박 과장님" → 박선우 conf 0.838, 박선영도 있음; 원칙1) · R-U7F3-3 E-5 템플릿 "직장·동" vs LLM 답 "직장 관계, 위계 동(같은 급)" 표기 통일(사용자 결정) · R-U5R-1/3/4 · R-U10R-5.
4. 하네스 L/FIX 후보: `stage-gate.sh`·`verify-impl.sh` 가 `결과: **통과**` 굵게를 못 읽음 · `save_evidence.py` 가 `-k "a or b"`·`-c "…"` 인자를 쪼갬(이번 04-review 에서 재실행 필요했음) · 서브에이전트 429 중단 시 SendMessage 로 재개하면 이어서 된다(이번 확인) · ruff 하네스 기존 경고(`findings.py` DTZ005·`bash_write_check.py` B007).
5. P10 인계: "박 과장님" 오병합 위험 표본 → 평가셋에 "같은 성·같은 직함 2명" 함정 · 결정 3-c(b) 되묻기 설계 · facts 양성 재진술 표본 · 혼합 발화 기록 누락 · 조회 턴 `not_callable_by_llm` 은 설계(집계 시 intent 분리).

## 사용자가 정한 것 (최근)
- 2026-11-09: **P5b 완료 확인**(E-6 1문장 추가·표기 차·P10 인계 고지 받음).
- 2026-11-08: 서버 재기동은 메인이 직접 — safety-guard 에 좁은 예외(L-007).
- 2026-11-07: 승인 관문 폐지(L-006) — main 승격까지 자동, verifier 게이트 유지, 완성 확인 1회.

## 사용자 몫 · 주의
- **무효 evidence 3개 삭제(훅이 rm 막음, 미추적이라 커밋엔 안 들어감)**:
  `rm /Users/sunwoo/Desktop/Portfolio/Relationship/docs/wiki/packages/P5b-query-turn/evidence/20261107-1455-u7fix-ruff.txt /Users/sunwoo/Desktop/Portfolio/Relationship/docs/wiki/fixes/evidence/20261108-2000-L-007-test-guards.txt /Users/sunwoo/Desktop/Portfolio/Relationship/docs/wiki/packages/P5b-query-turn/evidence/20261108-2009-u7fix3-review-baseline.txt`
- 다른 기기: `git checkout dev2 && git pull --ff-only`, `pip install -r requirements-dev.txt`, `alembic upgrade head`, `cd web && npm ci`.
- **언어 전부 한국어** · 승인 질문 없음(L-006) — 완성 확인 1회만, 결정(상수·CR)은 예시와 함께 묻는다 · 위임문은 01-plan 원문 인용·임의 제한 금지 · **파일 변경은 Write/Edit 로만** · 서브에이전트 보고는 재실행으로 재확인 · `.env` 읽지 않음(서버 기동 `--env-file` 만 예외) · 테스트 1건 = tests.md 1줄.
