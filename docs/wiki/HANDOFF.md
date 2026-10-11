# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`·`fixes/FIX-nnn.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-10-12 00:10 (세션 종료 기록 — 사용자 지시 "검증 끝나면 기록하고 멈춰라". FIX-033 verifier 재검증 통과, 커밋 승인 대기 중)

active: **P8-frontend**(U0·U1·U2 완료 — **U3 부터**) | frozen: none | 브랜치 `dev2` = origin/dev2 `22a6822`(+ FIX-033 커밋 예정) | origin/dev = `f9500fe` · origin/main = `f05d017`(사용자 README) | DB `capstone2-postgres-1`(5433): 개발 `relationship`, 테스트 `relationship_test` | 전체 **1912 passed skip 0** · test-guards **ok 333 실패 0 skip 0**

## 2026-10-11 세션에 끝낸 것 (커밋 순, 전부 origin/dev2·CI 세 job success)
| 커밋 | 내용 | CI(windows) |
|---|---|---|
| `440a0e5` | **U0** frontend-agent 신설(sonnet) · 위임 게이트 · FIX 게이트 `web/` · settings npm 4개 | 38111227562 windows 멈춤 → FIX-031 |
| `6479c1d` | **FIX-031** test-guards session-start `\| head` 멈춤 수정 + `timeout-minutes: 20` | 38116488226 3분32초 |
| `6c2d0e7` | **U1** `GET /persons`·`GET /persons/{id}` (verifier 1차 보류 → 테스트 보강 → 통과, 변이 7건) | 38117011109 |
| `2c902f0` | **U2** `GET /events/{id}/raw`·`GET /persons/{pid}/facts/{fid}/sources` (변이 8건) | 38119853036 |
| `d16375e` | FIX-014·032·033 **계획** 문서 | (문서) |
| `de35242` | **FIX-014** `bash-write-guard` — 프로젝트 안 Bash 쓰기 거부 + commit-cleanup 조각 판정 (verifier 4라운드) | 38136995433 4분14초 |
| `22a6822` | **FIX-032** test-guards 저장소 의존 격리(skip 0) · session-start 바이트 · dev2 문구 · 서명 고정값 | 38141012624 3분59초 |
| (대기) | **FIX-033** 에이전트 규칙 (a)~(d) · verifier 변이 시험 의무 · verification.md 변이 절 (verifier 재검증 통과 `FIX-033.md` 30행) | — |

## 커밋 안 된 변경 (FIX-033 커밋 하나로 들어갈 것 — 사용자 승인 대기)
- FIX-033 문서 9 + `review-FIX-033.md` + evidence 11 · `FIX-032.md` 결과절 해시·run 줄 · 이 HANDOFF · journal 자동 줄. 초안 `.claude/commit-draft.txt`(docs(FIX-033): …). 승인 안 받고 세션이 끊겼으면 **다음 세션 첫 질문이 이 커밋 승인**.

## 바로 다음에 할 것 (순서대로)
1. **FIX-033 커밋**(승인 → `approve-commit.sh` → `git add` 명시 경로 → `git commit -F` → `git push origin dev2` → CI 확인) → FIX-033.md 결과절에 해시·run(다음 커밋).
2. **P8 U3**(backend-agent, L-004 승인 먼저): 대기 질문 목록·브리핑 조회 API(01-plan 94행; 조인 `tool_name='briefing' AND step='briefing_compose'` 최신 1행, 결정 G). 위임 프롬프트에 FIX-033 (a)~(d) + **R-U2-2** `app/api/read.py` 모듈 docstring 갱신 + **R-U2-3** 판정표 7행(`briefed_at`·`updated_at` 변화 0) 값 테스트. → verifier 리뷰(변이 ≥1) → /commit → CI.
3. **U4~U9**(frontend-agent — U0 완료로 위임 가능, R-U0-3: 단위마다 verifier 가 `web/package.json` scripts·의존성·lock 점검) → **U10 사람 점검** → verifier 04-review.
4. **복기자료**: `~/Desktop/Portfolio/wiki/interview/relationship/17-개발과정-해설.md` 에 이 세션(U0·FIX-031·U1·U2·약점 11개·FIX-014 4라운드·032·033) 절 **미기록** — 문제점 목록(2026-10-11 15:20 보고)을 한계·교훈으로. README 갱신 기록 → `python3 양식/도구/interview_pdf.py relationship`.

## 사용자가 이 세션에서 정한 것
- security.md 에 npm 간접 실행 문구 **추가하지 않음**(단위별 verifier 점검만) · 일정 상한 `UPCOMING_SCHEDULES_LIMIT=10` 유지+테스트 · FIX-014 방식 "프로젝트 안 Bash 쓰기 거부" · 순서 "U2 끝내고 FIX 먼저" · FIX-014 회차 상한(2차 재작업이 마지막 필수 라운드, 새 우회는 후속 후보) → 3차 보류(deno/bun `run -`)는 (a) 한 건만 더 닫기 · FIX-033 재작업 "R-33-1·2·6 위임 + FIX-033.md 는 메인 세션".

## FIX 후보 (미착수 — 사용자에게 순서 묻기)
- **FIX-014 후속**(FIX-014.md "마무리" 절): **R-14-19(1순위)** deno/bun 값 옵션(`deno run -c x -`) allow · R-14-5 awk/perl/php 패턴 · R-14-6 PowerShell `iex` · R-14-7 `CLAUDE_SCRATCHPAD` 죽은 분기 · R-14-8 `tar -C`·`unzip -d` · R-14-9~11 · R-14-15 · R-14-17·18 python/node heredoc `$(…)` · R-14-20. 한계(수정안 5): 프로그램 자체 쓰기(pytest·npm·pip)·`subprocess` 경유는 막지 않음.
- **FIX-032 후속**: **R-32-1** `test-guards.sh` `full=${#full} bytes` 가 UTF-8 에서 문자 수(14323 vs 20800) → `wc -c`(1줄) · R-32-2 test-guards 가 시작·종료 시 마커·git status 자체 기록.
- **FIX-033 후속**: R-33-7 CLAUDE.md 120행 "리터럴로" 구절 · R-33-8 verifier.md 에 변이 시험 의무 명시.
- 하네스 기존: **R-27-10** commit-guard git commit 감지 우회(`(git …)`·`/usr/bin/git`) · R-27-11~13 · R-30-2 `head -c 150` 한글 절단 · R-12 verify-plan 파일명 절단 · R-29-1 import 전수 · R-29-3 `notifier.py:65` · `findings.py` ruff 3건 · "완료 커밋 뒤 CI 확인" 을 SKILL 규칙으로.
- 제품: 발송이 일정 잠금 안에서 네트워크(P7) · 잠금 404(결정 K) · `judge.py` docstring · 작업 메모리 미구현(S3.5) · `s_emb=0` 합산 · `.env.example` · 인물 분리 없음 · `loop_extract` 토큰 0 · `/health` · `update_person` 부분 반영 · `memory_promote` `source` 비대칭.
- 보류 아이디어: Jev(결정 전용 모델) 오프라인 파일럿 — 채택 시 원칙3·D11 CR.

## 절차 기록 (이 세션)
- 메인 세션 L-004 순서 위반 1건: FIX-014 구현 위임 **승인 전에** `--stage backend-agent` 마커 생성(16:05) → 사용자에게 보고, "시작" 승인으로 진행. 원인: 커밋·푸시·CI 확인과 한 응답에 묶음. **마커는 AskUserQuestion 답을 받은 뒤에만.**
- backend-agent 가 U1 1차에서 Bash heredoc 으로 제품 파일 3개를 씀(가드 우회) → FIX-014 의 직접 계기. 이후 위임 프롬프트 맨 앞에 "Write/Edit 로만" 재명시 + FIX-014 훅으로 강제.
- 구현자 증거 요약본 3건(FIX-031·FIX-014 rework2/3) → FIX-033 (c) 로 규칙화.

## 사용자 몫 · 주의
- 브랜치: `dev2` 작업 → `dev` 승격(`dev2:dev`, L-003) → `main`. **dev 승격 아직 안 함**(P7·FIX-018~033 전부 dev2 에만). 다른 기기: `git checkout dev2 && git pull --ff-only`, `pip install -r requirements-dev.txt`, `alembic upgrade head`.
- 웹푸시 키 `.env` `VAPID_*`·`PUSH_DEV_PAGE_ENABLED=1`. [미확인] Windows 실기기 · 빈 DB `relationship_test_fix006_evidence` · main 보호.
- **언어 전부 한국어** · 승인 질문 전 자세한 설명 · 위임 매번 L-004 · 마커 생성/커밋/푸시 각각 따로 실행 · **파일 변경은 Write/Edit 로만(FIX-014 훅이 Bash 쓰기를 거부 — 임시 파일은 스크래치패드 리터럴 절대 경로)** · 서브에이전트 보고는 재실행으로 재확인 · `.env` 읽지 않음 · 실서버 `set -a; . ./.env; set +a; .venv/bin/uvicorn app.main:create_app --factory --port 8765`.
