# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`·`fixes/FIX-nnn.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-11-09 01:30 (P5b-query-turn **완료 — 사용자 확인 2026-11-09**. 완료 커밋 뒤 dev2 → dev → main 승격 진행 중.)

active: **none** | frozen: none | 브랜치 `dev2`(04-review 커밋 `fb8841a` 뒤 완료 커밋) → 승격 대상 `dev2:dev` → `dev:main` | 승격 전 origin/dev `678bca7` · origin/main `f05d017` | DB `capstone2-postgres-1`(5433): 개발 `relationship`(인물 12), 테스트 `relationship_test` | 기준선: 백엔드 **2136 passed skip 0** · 프론트 156 passed · E2E 4 | 로컬 서버 :8000(`--reload`, 메인 세션이 직접 기동 가능 — L-007)

## 최근 끝낸 것
| 무엇 | 결과 | 기록 |
|---|---|---|
| **P5b-query-turn 완료(11-09)** | U1 `1dccb95` · U2 `06b7bb5` · U3 `a002706` · U4 `18219ba` · U5 `49c1c67` · U6 `a004cdd` · U7 `e49f78d`·`cf26dce` · 04-review `fb8841a`. verifier `완료`([필수] 0), 판정 표 통과 20·문구 보정 1, 변이 7/7, 실 LLM 4차 ① 관계 질문 정답 | `packages/P5b-query-turn/04-review.md`·`03-log.md`·`tests.md` |
| 하네스 L-006(11-07) | 사용자 승인 관문 폐지, 완성 확인 1회만 | `be67c76`, `lessons/L-006-*` |
| 하네스 L-007(11-08) | 서버 기동 `uvicorn app.main:… --env-file .env` 만 safety-guard 예외 | `9eb9d2e`, `lessons/L-007-*` |
| P8b-persons-grid 완료(10-28) | `678bca7` | `packages/P8b-persons-grid/04-review.md` |

## 진행 중 (이 턴에서 멈춘 자리)
- 완료 커밋(04-review `확인:` 줄 · CURRENT active none · journal DONE · 이 문서) → `git push origin dev2` → `git push origin dev2:dev` → `git fetch origin dev:dev` → `git push origin dev:main` → `git fetch origin main:main`. 이 순서 중 어디서 멈췄는지는 `git log --oneline -1 origin/main` 으로 확인한다.

## 바로 다음에 할 것 (순서대로)
1. 승격이 끝났는지 확인(origin/dev·origin/main 이 완료 커밋과 같은지). 안 끝났으면 위 순서 이어서.
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
