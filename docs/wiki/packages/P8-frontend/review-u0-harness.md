# P8-frontend U0 하네스 — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과
대상: 작업 트리(기준 HEAD `2341f9e`) — `git diff --stat` 11파일(`.claude/hooks/approve-commit.sh`·`commit-guard.sh`·`delegate-guard.sh`, `.claude/scripts/fix_guard_check.py`·`test-guards.sh`, `.claude/settings.json`, `.claude/skills/devlog/SKILL.md`, `CLAUDE.md`, `docs/wiki/HANDOFF.md`·`INDEX.md`·`journal.md`) + 신규 `.claude/agents/frontend-agent.md` + 증거 `evidence/20261011-1237-u0-harness.txt`
근거 문서: `01-plan.md` U0(87~91행)·결정 A "frontend-agent 초안 내용"(227행), `02-plan-verify.md` 135행 `승인:` 조건 ①(모든 단위 커밋 전 verifier 리뷰)
내가 남긴 증거: `evidence/20261011-1241-verifier-u0-test-guards.txt`(test-guards 전체 출력) · `evidence/20261011-1241-verifier-u0-mutation.txt`(변이 시험)
소견 요약: [필수] 0건 · [권고] 4건(R-U0-1~4, 아래 §8). 커밋을 막는 항목 없음.

---

## 1. 범위 — 승인된 계획(①~⑧ + npm allow 4개)과 일치하는가, 범위 밖 변경은 없는가

실행: `git status --short` · `git diff --stat` · `git diff -- <각 파일>`

| 계획 항목 | 변경 위치 | 판정 |
|---|---|---|
| ① `.claude/agents/frontend-agent.md`(`model: sonnet`) | 신규 파일, frontmatter `name/description/tools/model` 4키, `skills` 없음 | 일치(§5) |
| ② `delegate-guard.sh` `GATED` | 15행 `GATED="architect backend-agent eval-agent verifier frontend-agent"` + 4행 주석 | 일치 |
| ③ `approve-commit.sh` `--stage` case·usage | 24행 case · 27행 usage 에 `frontend-agent` | 일치 |
| ④ `fix_guard_check.py` 경로 조건·메시지·docstring, `commit-guard.sh` 주석 | 182행 `or p.startswith("web/")`(주석 1줄 추가로 180→182행), 22행 docstring, 206행 메시지; `commit-guard.sh` 11·100행 주석만 | 일치 — `commit-guard.sh` 는 `+4 -4` 전부 `#` 줄 |
| ⑤ `test-guards.sh` 5경우 | 케이스 6·7(196~213행), `web/x.ts` stage-gate(392~393행), frontend-agent 거부/허용 + 마커 소비(462~466행) | 일치(5경우 + 마커 소비 확인 1줄) |
| ⑥ `CLAUDE.md` 팀 표·"아직 만들지 않았다"·FIX 분리 문장 | 21행 "활성 5", 27행 표 1행, 33행 문장, 114행 경로 `web/` | 일치 (111행 L-004 문장은 미갱신 — R-U0-1) |
| ⑦ `SKILL.md` 역할표·위임 문장 | 15행 L-004 문장, 54행 5단계 위임, 102행 표 1행, 111행 AskUserQuestion 없음 목록 | 일치 (55행 6단계 경로는 미갱신 — R-U0-2) |
| ⑧ `INDEX.md` P8 행 | 76행 | 일치 |
| `settings.json` allow | `Bash(npm run:*)`·`Bash(npm test:*)`·`Bash(npm ci:*)`·`Bash(npm install:*)` 정확히 4개, `npx` 없음, JSON 파싱 정상(`python3 -c json.load` OK), deny 에 npm 항목 없음 | 사용자 결정과 일치 |
| `stage-gate.sh` | `git diff --stat` 에 없음 · `grep -n "web/" .claude/hooks/stage-gate.sh` 0건 | 계획대로 고치지 않음(R-2) |

범위 밖: `docs/wiki/HANDOFF.md`(위임 프롬프트 목록에 없음)가 바뀌어 있다 — 내용은 "커밋 안 된 변경"·"바로 다음에 할 것" 갱신으로 하네스가 요구하는 인수인계 문서 갱신(Stop 훅)이며 코드·규칙 변경이 아니다. 문제로 보지 않는다. `journal.md` 2줄은 `2341f9e` 자동 기록(위임 프롬프트 명시). 그 밖에 계획에 없는 파일 변경 없음.

## 2. `test-guards.sh` 직접 실행

실행: `bash .claude/scripts/test-guards.sh > docs/wiki/packages/P8-frontend/evidence/20261011-1241-verifier-u0-test-guards.txt 2>&1; echo exit=$?`

```
exit=0
ok 줄 수: 222   (메인 세션 증거 20261011-1237 과 같음, 변경 전 216)
XX 줄: 0
162:skip active=P8-frontend (product code gate not tested)   ← 기존 실제 저장소 의존 skip(R-30-1 후보), 변경과 무관
240:== 결과: 실패 0 ==
```

새 경우(증거 파일 행 번호):
```
71:ok   DENY   6) web/ 만 스테이징 + 검증 줄·review 문서 없음 → DENY
72:ok   allow  7) web/ 만 스테이징 + 검증 줄·review 문서 모두 있음 → allow
165:ok   DENY   web/x.ts (active: none) 거부 — 프론트도 활성 작업 필요
193:ok   DENY   frontend-agent without marker
194:ok   allow  marker=frontend-agent, frontend-agent allowed (consumed)
195:ok   frontend-agent marker consumed after allow
208:ok   agent frontmatter parses: .claude/agents/frontend-agent.md
```

## 3. 변이 시험 — `web/` 조건이 실제 판정에 쓰이는가

증거: `evidence/20261011-1241-verifier-u0-mutation.txt`. scratchpad 임시 git 저장소(커밋 없음, `git config` 변경 없음)에 `web/src/a.ts` 만 스테이징, 초안 `fix(FIX-999): t`, `FIX-999.md`·`review-FIX-999.md` 없음.

```
diff 원본 vs 변이본:
182c182
<   p.startswith("app/") or p.startswith("alembic/") or p.startswith("web/") for p in staged
>   p.startswith("app/") or p.startswith("alembic/") for p in staged

원본  : [fix-guard] 제품 코드(app/·alembic/·web/)를 바꾸는 FIX-999 커밋은 verifier 검증이 먼저다: …   exit=1
변이본: (출력 없음)                                                                                 exit=0
대조(변이본 + app/a.py 만 스테이징): [fix-guard] … exit=1
```

판정이 뒤집힌다(원본 거부 / 변이본 허용). 케이스 6 은 공허 통과가 아니다. 대조로 백엔드 조건은 변이본에서도 살아 있음을 확인했다(즉 뒤집힘의 원인이 `web/` 조건 하나임).

## 4. 케이스 6·7 준비·정리가 뒤 절을 깨지 않는가

읽은 것: `test-guards.sh` 190~245행(케이스 5 → 6·7 → 정리 → F-27-5 → F-27-4).

- 케이스 5 종료 상태: `app/a.py`·`docs/readme2.md` 스테이징, `FIX-999.md`·`review-FIX-999.md` 디스크에 없음, 초안 `feat(P7-push)`.
- 케이스 6·7: `app/a.py` 언스테이징 → `web/src/a.ts` 스테이징 → `rm -f` 두 문서 → 초안 `fix(FIX-999)` → (7) 검증 줄 작성·review 작성·스테이징.
- 정리(209~213행): `web/src/a.ts`·`review-FIX-999.md` 언스테이징 → 두 문서 `rm -f` → `app/a.py` 재스테이징 → 초안 `feat(P7-push)` 재작성. **케이스 5 종료 상태로 돌아간다**(차이는 디스크에 untracked `web/src/a.ts` 가 남는 것뿐 — `git diff --cached` 에 안 보이고, 이후 절에 FG_T 에서 `git add -A`/`git add .` 를 하는 곳이 없다. 67~69행의 `git add -A` 문자열은 safety-guard 거부 패턴 시험용 문자열이다).
- F-27-5(215~235행)는 초안 내용과 무관하게 명령 형태만 보고, F-27-4(239행)는 `app/a.py` 를 다시 `git add` 하고 review·FIX 문서를 새로 쓴다. 실제 실행에서 F-27-5 32경우·F-27-4·F-27-6·F-27-2·R-27-3 전부 ok(증거 73~104행 이후).

## 5. `frontend-agent.md` — 초안 내용 ①~⑧ 포함 여부·frontmatter

frontmatter(1~6행): `name: frontend-agent` · `description`(01-plan 227행 문장과 글자 그대로 일치) · `tools: Read, Write, Edit, Glob, Grep, Bash, TodoWrite` · `model: sonnet` · `skills` 없음 — 계획과 일치. YAML 파싱 ok(증거 208행).

| 초안 항목 | 본문 위치 |
|---|---|
| ① `web/`·활성 01-plan 지정 CI·문서만, `app/`·`alembic/`·`tests/` 금지 | "하지 말 것" 1 |
| ② 화면 3개 고정·새 라우트 금지(원칙5)·결정 L 시간 상한 | "하지 말 것" 2 |
| ③ 서버 문자열 고치거나 지어내지 않음(원칙7) | "하지 말 것" 3 |
| ④ `/push-dev/` 링크 금지 | "하지 말 것" 4 |
| ⑤ 자동 테스트 실 네트워크 0 | "하지 말 것" 5 |
| ⑥ 하네스 공통(한국어·registry grep·증거·커밋 금지·`.env` 금지·Bash 쓰기 금지) | "하네스 규칙" 절 6줄 + "작업 절차" 2·3 |
| ⑦ npm 스크립트 Mac·Windows, `rm -rf`·`rimraf` 금지(`safety-guard.sh` 60행 근거) | "하지 말 것" 6 |
| ⑧ `npx` 버전 고정(security §3 취지) | "하지 말 것" 7 |

누락 없음. 추가된 내용(책임·입력·품질 체크)은 결정 N(사이드바)·M(오프라인 제외)·J 와 정합하며 ①~⑧ 과 충돌하지 않는다. 읽기 대상으로 `app/api/schemas.py` 를 적었는데 ①(쓰기 금지)과 충돌하지 않는다(읽기만).

## 6. `npm install` allow 와 `security.md` 취지

`docs/wiki/security.md` §3 은 "다운로드한 스크립트 즉시 실행(`curl … | sh`) 금지 — 파일로 저장 → 내용 확인 → 실행" 이다. `npm install`/`npm ci` 는 받은 패키지의 lifecycle 스크립트(`postinstall` 등)를 바로 실행하므로 같은 범주의 위험이 있고, `npm run <이름>` 은 `package.json` 안의 셸 명령을 실행하므로 **`safety-guard.sh` 의 텍스트 매칭(명령 문자열만 봄, `npm` 언급 0건)을 우회하는 간접 경로**가 된다(예: `"clean": "rm -rf dist"` 를 `npm run clean` 으로 부르면 훅은 `rm -rf` 를 못 본다). 다만 allow 는 권한 프롬프트 생략일 뿐 훅은 그대로 돌고, 계획이 이미 완화책을 갖고 있다: 초안 ⑦(npm 스크립트에 `rm -rf`·`rimraf` 금지)·⑧(버전 고정)·U4 `package-lock.json` 커밋·승인 조건 ①(단위마다 verifier 리뷰). **충돌이 아니라 "리뷰에서 봐야 할 지점"으로 판단 → 권고(R-U0-3).**

## 7. Mac·Windows 셸 문법

새로 들어간 셸 구문: `( cd "$FG_T" && git reset -q … )`, `mkdir -p`, `printf … >`, `rm -f`, `echo frontend-agent > "$SA"`, `grep -q '"deny"'` — 모두 같은 파일의 기존 절(케이스 1~5·R-27-3·delegate-guard 절)에서 이미 쓰는 형태이고 Windows CI(FIX-022 job)에서 통과한 구문이다. `fix_guard_check.py` 변경은 순수 파이썬(경로는 177~179행에서 `\\`→`/` 정규화 뒤 비교). `delegate-guard.sh`·`approve-commit.sh` 는 문자열 목록만 늘었다. `frontend-agent.md`·`settings.json` 은 셸 아님. **새 OS 의존 구문 없음.** Windows 실증은 계획대로 커밋 뒤 CI windows job(`gh run view`)으로 확인하고 증거 파일 끝에 덧붙인다(열린 항목, 커밋 차단 사유 아님).

## 8. 소견

- **[권고] R-U0-1** `CLAUDE.md` 111행 L-004 문장 "architect·backend-agent·eval-agent·verifier 를 띄우기 전에" 에 `frontend-agent` 가 없다. 같은 파일 27·114행과 `SKILL.md` 15행은 갱신됐는데 이 줄만 옛 목록이다(계획 ⑥ 의 명시 범위 밖이라 범위 위반은 아님). 집행은 `delegate-guard.sh` 15행이 하므로 안전에는 영향 없음 — 문서 정합만. 이 커밋에서 함께 고치거나 U0 03-log 에 한 줄 남기고 다음 문서 커밋에서.
- **[권고] R-U0-2** `.claude/skills/devlog/SKILL.md` 55행(`/devlog fix` 6단계) "제품 코드(`app/`·`alembic/`)를 바꾼 FIX/test 커밋은 verifier 리뷰가 먼저다" 가 `web/` 없이 남아 있다. `CLAUDE.md` 114행·`fix_guard_check.py` 206행 메시지는 `web/` 을 포함하므로 절차 문서와 집행 메시지가 어긋난다. 메인 세션이 `/devlog fix` 를 따를 때 `web/` FIX 에서 리뷰를 건너뛰어도 되는 것처럼 읽힐 수 있다(훅은 거부하므로 실제 구멍은 아님). R-U0-1 과 같이 처리.
- **[권고] R-U0-3** `settings.json` 의 `npm run:*`·`npm install:*` 는 §6 대로 `safety-guard.sh` 텍스트 매칭을 우회하는 간접 실행 경로다. U4 이후 단위별 verifier 리뷰에서 ① `web/package.json` 의 `scripts` 전부(셸 전용 명령·삭제 명령 유무) ② `dependencies`/`devDependencies` 변경(버전 고정·출처) ③ `package-lock.json` 동반 변경 여부를 고정 점검 항목으로 둔다. `security.md` 에 "npm 스크립트는 package.json 을 리뷰 대상에 넣는다" 한 줄을 넣을지는 사용자 판단(§6 "규칙을 바꾸면 카드와 훅을 같은 커밋에서" — 이번 변경은 훅 규칙 변경이 아니라 프롬프트 완화라 필수로 보지 않는다).
- **[권고] R-U0-4** `01-plan` U0 판정의 Windows 항목(CI windows job success)은 커밋 뒤에만 확인 가능하다. 커밋·푸시 뒤 `gh run view <id>` 결과를 `evidence/20261011-1237-u0-harness.txt` 끝에 덧붙이기 전까지 U0 는 "Mac 통과·Windows 대기" 상태다 — 03-log U0 에 그렇게 적고, windows job 이 실패하면 FIX 로 다룬다(frontend-agent 위임은 그 뒤).

## 9. 판정 근거 요약

- 승인된 계획(①~⑧ + npm allow 4개)과 변경이 1:1 대응하고 범위 밖 코드·규칙 변경 없음(§1).
- `test-guards.sh` 실패 0·ok 222, 새 5경우 + 마커 소비 모두 ok(§2, 증거 파일).
- `web/` 경로 조건 변이 시험에서 판정이 뒤집힘 — 케이스 6 은 실제 판정을 시험한다(§3, 증거 파일).
- 케이스 6·7 정리 뒤 상태가 케이스 5 와 같고 이후 절 전부 ok(§4).
- `frontend-agent.md` 초안 ①~⑧ 누락 없음, frontmatter 일치(§5).
- 보류 사유(근거 없는 항목·범위 침범·게이트 약화) 없음. 권고 4건은 문서 정합·후속 리뷰 항목이며 커밋을 막지 않는다.
