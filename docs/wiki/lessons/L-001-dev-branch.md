# L-001 · 브랜치 전략: dev 에서 작업·푸시, 실서버 검증 뒤 main 승격 + 에이전트 git log 연동

날짜: 2026-09-03 | 어디서(P / FIX / CR): 하네스 (P0-embed-pilot 진행 중 사용자 지시) | Refs: harness security L-001

## 무슨 일이 있었나
- 첫 커밋 2건(e062986, b4ddfef)을 `origin main` 에 직접 푸시했다. 사용자가 "푸시는 dev 브랜치로 먼저 가서 실제 서버에서 돌려 본 뒤 main 으로 최종 푸시하는 형태"를 원했다.
- 같은 시점에 "구현·계획 검증 에이전트가 git log 를 볼 수 있게 연동"도 요청했다. architect 에이전트는 Bash 가 없어 git log 를 직접 볼 수 없었고, backend/eval 에이전트는 볼 수는 있지만 절차에 "보라"는 단계가 없었다.

## 왜 그랬나
- 하네스 초안이 단일 브랜치(main)만 가정했다. 실서버 검증 단계가 흐름에 없었다.
- 위키(HANDOFF·journal·03-log)가 이력을 대신한다고 봤지만, 커밋 해시·태그별 변경은 git log 가 권위다. 계획 검증(점검표 5 의존성, 7 Refs)과 registry 중복 확인은 git log 없이는 "말로만" 될 수 있다.

## 다음부터
규칙으로 바꿀 것이 있으면 어느 파일(CLAUDE.md · 스킬 · 훅)을 고쳤는지 적는다.
- **브랜치**: 작업·푸시는 `dev` 로만. `main` 은 배포 브랜치이며 `/commit release`(AskUserQuestion 승인 → `approve-commit.sh --release` → `git push origin dev:main`)로만 올린다. 되돌리기는 dev 에 revert 커밋 후 재승격.
  - 고친 파일: `.claude/hooks/safety-guard.sh`(C 절: origin dev 만 허용, dev:main 은 승격 마커 필요, 그 외 main 푸시 거부), `approve-commit.sh`(`--release`), `commit-cleanup.sh`(승격 마커 정리·`RELEASE` 기록), `.claude/skills/commit/SKILL.md` §6·§7, `docs/wiki/security.md` §2, `CLAUDE.md`, `.gitignore`·`settings.json`(승격 마커), `.claude/scripts/test-guards.sh`(main 푸시 거부 사례 5건 추가).
- **git log 연동**: `.claude/scripts/gitlog.sh [태그]` 가 브랜치 상태·최근 커밋·태그별 커밋·마지막 커밋 파일·미커밋 변경을 출력한다. `session-start.sh`·`commit-cleanup.sh` 가 같은 내용을 `.claude/gitlog.md`(gitignore)에 저장하므로 Bash 없는 에이전트도 Read 로 본다. 계획(01-plan)·계획 검증(02-plan-verify 점검표 5·7)·구현 착수 전에 보도록 agents 3종·devlog 스킬에 단계를 넣었다.
  - 고친 파일: `.claude/scripts/gitlog.sh`(신설), `.claude/hooks/session-start.sh`, `commit-cleanup.sh`, `.claude/agents/{architect,backend-agent,eval-agent}.md`, `.claude/skills/devlog/SKILL.md`, `CLAUDE.md`.

---

## 개정 (2026-09-29) — 세 단계로: dev2 실험 → dev 검증 → main 배포

### 무슨 일이 있었나

기기를 Windows 에서 Mac 으로 옮기면서 상태 공유용으로 `dev2` 브랜치가 생겼고, 사용자가 "커밋마다 dev2 에도 푸시" 를 지시했다. 그래서 `dev → dev2` 한 방향 복사를 훅에 넣었다(FIX-009). 그런데 사용자가 원한 구조를 다시 설명했다: **dev2 는 아무때나 막 푸시해서 실험하는 곳, dev 는 실험을 통해 어느 정도 검증된 것을 두는 곳, main 은 dev 에서 끝난 것을 올리는 곳.**

즉 dev2 는 dev 의 사본이 아니라 dev 의 **상류**였다. 방향이 반대였다.

### 왜 그랬나

첫 지시("커밋마다 dev2 에 푸시")만 보고 dev2 를 백업 사본으로 해석했다. 사용자가 브랜치를 왜 셋으로 나누고 싶어 하는지 — 즉 **단계별 신뢰도**를 나누려 한다는 의도 — 를 확인하지 않았다. 지시의 표면(어디에 미느냐)만 구현하고 목적(무엇을 구분하려는가)을 묻지 않은 것이 원인이다.

### 다음부터

- **브랜치 세 단계**: `dev2` = 작업·실험(아무때나 `git push origin dev2`, 승인 마커 없음) → `dev` = 검증 통과분(`/commit` 승인 뒤 `git push origin dev2:dev`, 그 뒤 L-003 대기) → `main` = 배포(`/commit release` 로 `git push origin dev:main`, fast-forward 만).
- **`origin dev` 직접 푸시는 금지한다.** dev 는 승격으로만 들어오는 곳이라, 직접 밀 수 있으면 검증 단계가 무의미해진다.
- 승격은 **통째로(fast-forward)** 한다. 실험 중 버릴 것은 dev2 에 `git revert` 커밋을 남긴 뒤 승격한다. cherry-pick 선별은 dev2 와 dev 가 항상 갈라지게 만들고, 정리하려면 강제 푸시 금지를 풀어야 해서 택하지 않았다.
- 고친 파일: `.claude/hooks/safety-guard.sh`(푸시 허용표 재작성), `commit-cleanup.sh`(실험/승격/배포 세 갈래 + 각각 성공 판정), `approve-commit.sh`(안내 문구), `.claude/skills/commit/SKILL.md` §3·§6·§6.1·§7, `.claude/skills/devlog/SKILL.md`(브랜치 확인), `.claude/agents/verifier.md`, `docs/wiki/security.md` §2, `CLAUDE.md`, `.claude/scripts/test-guards.sh`, `docs/wiki/fixes/FIX-010.md`(구현·검증).
- **교훈 자체**: 사용자가 여러 브랜치·환경을 나누어 달라고 할 때는 "어디에 미느냐" 전에 **"각각을 무엇으로 구분하려는가"** 를 먼저 묻는다. 방향을 잘못 잡으면 훅·문서·스킬을 한 번 더 전부 고쳐야 한다.
