---
name: commit
description: 승인 기반 커밋 절차. 작업 단위(사소한 수정 포함) 하나가 끝날 때마다 변경 내용을 LLM이 기획서 태그와 함께 초안으로 쓰고, 사용자에게 AskUserQuestion으로 커밋(선택적으로 푸시) 승인을 받은 뒤에만 커밋한다. 훅(commit-guard·safety-guard)이 다른 경로의 커밋·푸시를 막는다. "커밋", "커밋해줘", "저장해", "푸시" 요청 또는 작업 단위 종료 시 쓴다.
---

# commit — 승인 기반 커밋

## 왜 이렇게 하나

- **작은 단위로 자주**: 사소한 수정도 커밋 하나. 잘못된 방향이 한 커밋 안에 갇혀 `git revert` 한 번으로 되돌아간다.
- **LLM이 쓰는 메시지가 곧 로그**: 무엇을·왜·기획서 어디에 근거해 바꿨는지 사람이 읽을 수 있게 남긴다. 코딩 에이전트가 기획서 의도에서 벗어나면 이 단계에서 드러난다.
- **태그(Refs)로 역추적**: 기획서가 바뀌면 `git log --grep 'D5'`로 영향 커밋을 바로 구한다(CR 출구 절차).
- **사용자가 매번 승인**: 승인 마커 없이는 훅이 커밋을 거부한다. 초안이 승인 뒤 바뀌면 해시 불일치로 거부된다.

## 절차 (순서를 바꾸지 않는다)

### 0. 한 커밋 = 한 의도인지 확인
`git status --short`, `git diff --stat`을 본다. 서로 다른 의도(예: 스키마 수정 + 평가 스크립트)가 섞였으면 **나눠서** 절차를 두 번 돈다. 비밀·임시 파일(`.env`, `*.pem`, `.claude/.commit-approved` 등)이 보이면 스테이징하지 않는다.

### 1. 정합성 자기 점검 (메시지에 결과를 쓴다)
diff를 `docs/wiki` 카드와 대조한다 — devlog 스킬의 점검표 1~4, 8번. 특히:
- CLAUDE.md 불변 원칙(오병합 금지·임계치 2개·3신호·4단계·화면 3개·제외 범위·원문 보존·근거 기록)
- 인용한 D 카드의 "코드에서 지켜야 할 것"
- S 카드의 스키마·시그니처
위반이 있으면 커밋하지 않고 고치거나 사용자에게 보고한다.

### 2. 초안 작성 → `.claude/commit-draft.txt`
형식(고정):

```
<type>(<scope>): <제목, 50자 이내, 한국어 가능>

변경:
- <파일/모듈 단위로 무엇이 바뀌었나>
이유: <기획서·카드의 어느 문장을 실현/수정하는가>
정합성: 원칙 <n> · D<n> · S3.<n> 대조 — 위반 없음 | 예외: <사유>
검증: <실행한 테스트/명령과 결과. 없으면 "없음(문서)">
Refs: <P-id> <D..> <S..> <R..> <FIX-/CR- 있으면>

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: <이 세션의 URL>
```

- `type`: `feat` `fix` `test` `docs` `eval` `refactor` `chore` `harness`(하네스·훅·스킬·위키) `cr`(기획서 변경 이행)
- `scope`: 패키지 id(`P3-er`) 또는 영역(`wiki`, `hooks`, `schema`). CURRENT의 active와 다르면 이유를 이유 줄에 쓴다.
- 제목 줄은 `commit-cleanup.sh`가 HEAD 제목과 비교하므로 초안 첫 줄과 실제 커밋 제목이 같아야 한다(`-F`로 넣으면 자동으로 같다).

### 3. 사용자 승인 (AskUserQuestion)
초안 전문과 `git diff --stat`을 보여주고 묻는다. 선택지:
- **커밋** — 커밋만
- **커밋 + 푸시** — origin **dev** 로 푸시까지 (main 직접 푸시는 없다 — §7)
- **초안 수정** — 사용자의 수정 내용을 반영해 2번부터 다시
- **취소**

### 4. 승인 마커 생성
```
bash .claude/hooks/approve-commit.sh            # 커밋만
bash .claude/hooks/approve-commit.sh --push     # 커밋 + 푸시
```
마커에는 초안의 sha256이 들어간다. 이후 초안을 고치면 5번이 거부된다 → 3번부터 다시.

### 5. 로그 항목 → 스테이징 → 커밋
1. 활성 패키지가 있으면 `docs/wiki/packages/<active>/03-log.md` **맨 아래**에 `templates/package-log.md` 형식의 항목을 붙인다(hash는 `pending`). `HANDOFF.md`의 갱신 시각·지금 어디까지·다음을 갱신한다.
2. 명시 경로로 스테이징: `git add <파일1> <파일2> … docs/wiki/packages/<active>/03-log.md docs/wiki/HANDOFF.md docs/wiki/journal.md` (`-A`·`.` 금지, 훅이 막는다)
3. `git commit -F .claude/commit-draft.txt`
4. `.githooks/pre-commit`이 비밀·대용량을 검사한다. 실패하면 원인을 고치고 3번(승인)부터 다시 — `--no-verify`는 금지.
5. 성공하면 `commit-cleanup.sh`가 마커를 지우고 `journal.md`에 `COMMIT | <hash> <제목>` 줄을 붙인다. `03-log.md`의 `pending`을 해시로 바꾸는 것은 **다음 커밋**에 포함한다(고쳐 쓰지 않아도 journal에 해시가 있다).

### 6. 푸시 (승인한 경우만) — 항상 `dev`
```
git push -u origin dev       # 첫 푸시
git push origin dev
```
`safety-guard.sh`는 `origin dev` 이외(main 직접 푸시 포함)·강제 옵션·마커 없는 푸시를 거부한다. 푸시가 끝나면 cleanup이 푸시 마커를 지운다. 로컬 작업 브랜치는 항상 `dev`다(`git branch --show-current`로 확인, 아니면 `git checkout dev`).

### 6.1 dev 푸시 뒤에는 멈춘다 (L-003)
푸시가 끝나면 cleanup 훅이 `.claude/.awaiting-decision` 마커를 만든다. 이 마커가 있는 동안 stage-gate 는 HANDOFF·journal·초안 외 모든 쓰기를, commit-guard 는 새 커밋을 거부한다.
1. `HANDOFF.md`를 갱신하고 **즉시 `AskUserQuestion`**: "dev 에 <hash> 푸시됨. 실서버에서 확인 후 결정해 주세요" — 선택지: **main 승격** / **수정 필요(내용)** / **보류(나중에 결정)**.
2. 승격 → §7. 수정 → `bash .claude/hooks/approve-commit.sh --decision fix` 로 마커를 지우고 FIX/작업 계속. 보류 → 마커를 둔 채 턴을 끝낸다(다음 세션 재개 시 다시 묻는다).
3. 사용자가 정하기 전에는 다음 패키지·작업 단위를 시작하지 않는다.

### 7. main 승격 — `/commit release` (L-001 브랜치 전략: dev → 실서버 검증 → main)
`main`은 배포 브랜치다. `dev`를 실제 서버에서 돌려 본 뒤에만 올린다.
1. 사용자에게 승격 대상을 보인다: `git log --oneline origin/main..dev`(승격될 커밋), 실서버 검증 근거(사용자가 말한 결과·evidence 파일 경로).
2. `AskUserQuestion` — 선택지: **승격** / 취소. 실서버 검증을 했는지 명시적으로 묻는다.
3. 승인 시 `bash .claude/hooks/approve-commit.sh --release` → `git push origin dev:main` (fast-forward 만. 강제 옵션은 별도 차단) → `git fetch origin main:main` 으로 로컬 main 을 맞춘다.
4. cleanup 훅이 승격 마커를 지우고 `journal.md`에 `RELEASE` 줄을 붙인다. `HANDOFF.md`에 "main = <hash>" 를 적는다.
- 되돌리기: main 에서 문제가 나면 dev 에 `git revert` 커밋을 만들어 다시 승격한다. main 을 직접 고치지 않는다.

## 하지 말 것
- `git commit -m` (초안 파일 외 경로), `--amend`, `--no-verify`, `git add -A/.`, 강제 푸시.
- 사용자 승인 없이 마커를 만들거나(`approve-commit.sh`는 3번 직후에만) 마커 파일을 직접 쓰기.
- 여러 의도를 한 커밋에 묶기. "정리하면서 같이" 는 별도 커밋.
- 서브에이전트가 커밋하기 — 커밋은 메인 세션만 한다.

## 첫 커밋 (저장소에 커밋이 없을 때)
- `git config core.hooksPath .githooks`가 설정돼 있는지 확인(`git config core.hooksPath`).
- 원격이 `https://github.com/SunWoo1213/Relationship.git`인지 확인(`git remote -v`).
- 하네스 전체를 `harness(wiki): …` 한 커밋으로. 이후부터는 작업 단위별.
- 작업 브랜치 `dev`가 없으면 `git checkout -b dev`로 만들고 이후 모든 커밋·푸시는 dev 에서 한다(§6·§7).
