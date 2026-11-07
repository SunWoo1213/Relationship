---
name: commit
description: 자동 커밋 절차(L-006). 작업 단위(사소한 수정 포함) 하나가 끝날 때마다 변경 내용을 LLM이 기획서 태그와 함께 초안으로 쓰고, 묻지 않고 커밋한 뒤 origin dev2 로 푸시한다. 검증 승격(dev2:dev)과 main 승격(dev:main)은 verifier 완료 검토 통과 + 사용자 완성 확인(한 번) 뒤에 이어서 한다. 훅(commit-guard·safety-guard)이 초안 형식·금지 옵션·FIX verifier 게이트·허용 외 푸시를 막는다. "커밋", "커밋해줘", "저장해", "푸시" 요청 또는 작업 단위 종료 시 쓴다.
---

# commit — 자동 커밋 (L-006, 2026-11-07 개정)

## 왜 이렇게 하나

- **작은 단위로 자주**: 사소한 수정도 커밋 하나. 잘못된 방향이 한 커밋 안에 갇혀 `git revert` 한 번으로 되돌아간다.
- **LLM이 쓰는 메시지가 곧 로그**: 무엇을·왜·기획서 어디에 근거해 바꿨는지 사람이 읽을 수 있게 남긴다. 코딩 에이전트가 기획서 의도에서 벗어나면 이 단계에서 드러난다.
- **태그(Refs)로 역추적**: 기획서가 바뀌면 `git log --grep 'D5'`로 영향 커밋을 바로 구한다(CR 출구 절차).
- **사용자 승인은 없다(L-006)**: 2026-09 의 승인 마커·초안 해시 비교·L-003 대기는 폐지됐다. 신뢰성은 verifier 게이트(L-002·FIX-027)와 테스트가 지킨다. 사용자는 패키지가 완성됐을 때 한 번 확인한다(`/devlog done`).

## 절차 (순서를 바꾸지 않는다)

### 0. 한 커밋 = 한 의도인지 확인
`git status --short`, `git diff --stat`을 본다. 서로 다른 의도(예: 스키마 수정 + 평가 스크립트)가 섞였으면 **나눠서** 절차를 두 번 돈다. 비밀·임시 파일(`.env`, `*.pem`, `.claude/commit-draft.txt` 등)이 보이면 스테이징하지 않는다.

### 1. 정합성 자기 점검 (메시지에 결과를 쓴다)
diff를 `docs/wiki` 카드와 대조한다 — devlog 스킬의 점검표 1~4, 8번. 특히:
- CLAUDE.md 불변 원칙(오병합 금지·임계치 2개·3신호·4단계·화면 3개·제외 범위·원문 보존·근거 기록)
- 인용한 D 카드의 "코드에서 지켜야 할 것"
- S 카드의 스키마·시그니처
위반이 있으면 커밋하지 않고 고치거나 사용자에게 보고한다.

### 2. 초안 작성 → `.claude/commit-draft.txt`
형식(고정):

```
<type>(<scope>): <제목, 50자 이내, 한국어>

변경:
- <파일/모듈 단위로 무엇이 바뀌었나>
이유: <기획서·카드의 어느 문장을 실현/수정하는가>
정합성: 원칙 <n> · D<n> · S3.<n> 대조 — 위반 없음 | 예외: <사유>
검증: <실행한 테스트/명령과 결과. 없으면 "없음(문서)">
Refs: <P-id> <D..> <S..> <R..> <FIX-/CR- 있으면>

<세션 시스템 안내(attribution reminder)가 주는 Co-Authored-By 줄을 그대로 쓴다. Claude-Session: 줄은 안내에 있을 때만 쓴다>
```

- **서명 줄은 고정값이 아니다(FIX-032).** 모델명은 세션마다 달라지므로 이 템플릿에 적어 두지 않는다. 세션이 알려 주는 `Co-Authored-By` 줄을 한 글자도 바꾸지 않고 마지막에 붙이고, 안내에 `Claude-Session:` 줄이 없으면 쓰지 않는다.
- **사람이 읽고 바로 알아볼 수 있게 쓴다** (사용자 지시 2026-09-29). 제목만 봐도 무엇이 달라졌는지 알 수 있어야 한다. 본문은 한 줄에 한 가지만 담아 짧게 끊고, 코드 식별자를 늘어놓는 대신 그 변경이 실제로 무슨 일을 하는지 평범한 말로 적는다. "이유" 줄에는 어느 카드의 요구를 실현하는지와 **왜 그 방법을 골랐는지**를 함께 쓴다.
- **언어: 한국어.** 제목·본문과 `03-log.md`·`HANDOFF.md`·`journal.md` 항목은 한국어 문장으로 쓴다. 원문 그대로 두는 것: `type` 접두어, 코드 식별자·파일 경로·명령어·태그(Refs), `Co-Authored-By` 서명 줄.
- `type`: `feat` `fix` `test` `docs` `eval` `refactor` `chore` `harness`(하네스·훅·스킬·위키) `cr`(기획서 변경 이행)
- `scope`: 패키지 id(`P3-er`) 또는 영역(`wiki`, `hooks`, `schema`). CURRENT의 active와 다르면 이유를 이유 줄에 쓴다.
- 제목 줄은 `commit-cleanup.sh`가 HEAD 제목과 비교하므로 초안 첫 줄과 실제 커밋 제목이 같아야 한다(`-F`로 넣으면 자동으로 같다).

### 3. 로그 항목 → 스테이징 → 커밋 (묻지 않는다)
1. 활성 패키지가 있으면 `docs/wiki/packages/<active>/03-log.md` **맨 아래**에 `templates/package-log.md` 형식의 항목을 붙인다(hash는 `pending`). `HANDOFF.md`의 갱신 시각·지금 어디까지·다음을 갱신한다.
2. 명시 경로로 스테이징: `git add <파일1> <파일2> … docs/wiki/packages/<active>/03-log.md docs/wiki/HANDOFF.md docs/wiki/journal.md` (`-A`·`.` 금지, 훅이 막는다)
3. `git commit -F .claude/commit-draft.txt` — 훅이 보는 것: 초안 파일 존재, `-F <초안>` 외 인자 없음, `--amend`·`--no-verify` 없음, FIX 커밋이면 verifier 검증 줄 + `review-FIX-nnn.md`(FIX-027).
4. `.githooks/pre-commit`이 비밀·대용량을 검사한다. 실패하면 원인을 고치고 2번부터 다시 — `--no-verify`는 금지.
5. 성공하면 `commit-cleanup.sh`가 `journal.md`에 `COMMIT | <hash> <제목>` 줄을 붙이고 `gitlog.md`를 갱신한다. `03-log.md`의 `pending`을 해시로 바꾸는 것은 **다음 커밋**에 포함한다.

### 4. 실험 푸시 — 커밋 직후 바로
> 푸시는 커밋과 **다른 Bash 호출**로 실행한다(한 명령에 묶지 않는다 — 각 단계 결과를 보고 넘어가기 위해서다, FIX-013).

로컬 작업 브랜치는 항상 `dev2`다(`git branch --show-current`로 확인, 아니면 `git checkout dev2`).
```
git push origin dev2
```
사용자 지시(2026-10): 커밋할 때마다 dev2 로 민다.

### 5. 검증 승격·main 승격 — 완성 확인 뒤에 이어서 (L-001 · L-006)
`main`은 배포 브랜치다. `/devlog done` 에서 verifier 완료 검토가 `결과: 완료` 이고, 사용자가 완성 확인 질문에 **확인**을 택한 직후에만 아래를 순서대로 실행한다. 중간 커밋 뒤에는 하지 않는다.
```
git push origin dev2:dev        # 검증 승격
git fetch origin dev:dev        # 로컬 dev 맞춤
git push origin dev:main        # 최종 승격 (fast-forward 만, 강제 옵션은 별도 차단)
git fetch origin main:main
```
`safety-guard.sh`는 이 둘과 `origin dev2` 외의 모든 푸시(`origin dev`·`origin main` 직접 푸시 포함)와 강제 옵션을 거부한다. 승격이 끝나면 cleanup이 `journal.md`에 `PUSH`·`RELEASE` 줄을 붙인다. `HANDOFF.md`에 "main = <hash>" 를 적는다.
- 되돌리기: main 에서 문제가 나면 dev2 에 `git revert` 커밋을 만들어 같은 경로로 다시 승격한다. main 을 직접 고치지 않는다.
- 사용자가 완성 확인에서 **수정 필요**를 택하면 승격하지 않고 FIX 로 계속한다(`/devlog fix`).

## 하지 말 것
- `git commit -m` (초안 파일 외 경로), `--amend`, `--no-verify`, `git add -A/.`, 강제 푸시.
- 완성 확인 전에 `dev2:dev`·`dev:main` 승격.
- 여러 의도를 한 커밋에 묶기. "정리하면서 같이" 는 별도 커밋.
- 서브에이전트가 커밋하기 — 커밋은 메인 세션만 한다.

## 첫 커밋 (저장소에 커밋이 없을 때)
- `git config core.hooksPath .githooks`가 설정돼 있는지 확인(`git config core.hooksPath`).
- 원격이 `https://github.com/SunWoo1213/Relationship.git`인지 확인(`git remote -v`).
- 하네스 전체를 `harness(wiki): …` 한 커밋으로. 이후부터는 작업 단위별.
- 작업 브랜치 `dev2`가 없으면 `git checkout -b dev2`로 만들고 이후 모든 커밋은 dev2 에서 한다.
