# security — 기본 보안 규칙 카드

> 집행부: `.claude/hooks/safety-guard.sh`(명령), `secret-guard.sh`(파일 쓰기), `.githooks/pre-commit`(git), `settings.json` deny 목록.
> 이 카드는 **왜 막는지**와 **대신 어떻게 하는지**를 적는다. 훅 메시지가 이 카드를 가리킨다.

## 1. 비밀(API 키·비밀번호·개인키)

| 규칙 | 대신 |
|------|------|
| `.env`, `*.pem`, `*.key`, tfstate/tfvars 는 에이전트가 읽지도 쓰지도 않는다 | 사용자가 직접 만든다. 에이전트는 `.env.example`에 **이름만** 적는다 |
| 코드·문서·커밋에 키 문자열을 넣지 않는다 (패턴 검사) | `os.environ["OPENAI_API_KEY"]` 로 읽는다. 배포는 SSM Parameter Store |
| 환경변수 전체 출력(`env`, `printenv`, `Get-ChildItem env:`)·KEY/SECRET 변수 echo 금지 | 존재 여부만: `test -n "$OPENAI_API_KEY" && echo set` 는 허용 |
| `git add -A` / `git add .` 금지 — 비밀·임시 파일이 섞인다 | 파일을 명시해서 `git add path/a path/b` |
| 로그·trace에 키·비밀을 남기지 않는다 | `agent_traces.input`은 발화·후보만. 헤더·키는 마스킹 |

## 2. GitHub / git

| 규칙 | 대신 |
|------|------|
| 강제 푸시(`--force`, `-f`, `+ref`, `--mirror`, `--delete`) 금지 | 새 커밋으로 고친다. 잘못된 커밋은 `git revert` |
| 푸시는 `origin dev` 로만, `/commit` 절차에서 사용자가 승인한 뒤에만 | `/commit` 의 "커밋 + 푸시" 선택 → `git push -u origin dev` |
| dev 푸시 뒤에는 사용자가 승격/수정을 정할 때까지 다음 작업·커밋 금지 (L-003, `.claude/.awaiting-decision`) | 푸시 직후 `AskUserQuestion`. 수정이면 `approve-commit.sh --decision fix`, 승격이면 `/commit release` |
| `main` 직접 푸시 금지 (L-001 브랜치 전략: dev → 실서버 검증 → main) | `/commit release` — 사용자 승인 → `approve-commit.sh --release` → `git push origin dev:main` (fast-forward 만, 강제 옵션은 별도 차단) |
| 커밋은 승인된 초안 파일로만, `--amend`·`--no-verify` 금지 | `/commit` |
| `reset --hard`, `checkout -- .`, `restore .`, `clean`, `branch -D`, `stash drop`, `filter-branch` 금지 | 되돌리기는 `git revert`. 정말 필요하면 사용자가 직접 |
| 원격·자격·사용자 설정 변경(`remote set-url`, `config credential…`) 금지 | 사용자가 직접 |
| 저장소: `https://github.com/SunWoo1213/Relationship.git` (origin). 작업 브랜치 `dev`, 배포 브랜치 `main` | 로컬은 항상 `dev` 에서 작업. `main` 은 승격 뒤 `git fetch origin main:main` 으로만 맞춘다 |

## 3. 파일 시스템

| 규칙 | 대신 |
|------|------|
| 재귀 삭제(`rm -r`, `Remove-Item -Recurse`, `rd /s`, `shutil.rmtree`, `find -delete`)는 scratchpad 밖에서 금지 | 파일을 하나씩 지정해 삭제. 폴더 삭제는 사용자에게 요청 |
| `sudo`, `chmod 777`, `chown -R`, 디스크·시스템·레지스트리 명령 금지 | 필요 시 사용자가 직접 |
| 다운로드한 스크립트 즉시 실행(`curl … | sh`, `iex(DownloadString)`) 금지 | 파일로 저장 → 내용 확인 → 실행 |

## 4. 인프라 · 데이터

| 규칙 | 대신 |
|------|------|
| `terraform destroy`, `apply -auto-approve` 금지 | `terraform plan` 까지. apply/destroy 는 사용자 |
| `aws … delete-*/terminate-*`, `s3 rm/rb`, `sync --delete` 금지 | 콘솔에서 사용자 |
| `docker … prune`, `volume rm`, `compose down -v` 금지 | 컨테이너만 내리기(`down`). 볼륨 삭제는 사용자 |
| 셸에서 `DROP`/`TRUNCATE` 금지 | Alembic 마이그레이션 파일로 작성해 검토 |
| 로컬 서버 이외로 데이터 전송(`curl -d/-F/-T`, `scp`, `rclone`) 금지 | 외부 API 호출은 코드(SDK)로, 키는 환경변수 |

## 5. 제품 코드가 지킬 것 (기획서 9장 "제3자 개인정보")

- 인물 단위 완전 삭제 API (`DELETE /persons/{id}` → CASCADE).
- 저장 최소화: `pending_questions.context`에는 재개에 필요한 것만. 전체 대화 이력 저장 금지.
- 웹푸시 VAPID 개인키는 환경변수/SSM. 프론트에는 공개키만.
- RDS 프라이빗 서브넷, 저장 시 암호화(RDS 기본), 전송 시 TLS(D7).
- 멀티테넌시 미검증(부록 A) — 그래도 모든 조회는 `user_id` 조건을 넣는다.

## 6. 예외가 필요할 때

훅이 막은 명령이 정말 필요하면 에이전트는 **우회하지 않고** 사용자에게 명령을 그대로 보여주고 직접 실행을 요청한다(`! <command>`). 규칙 자체를 바꾸려면 이 카드와 훅을 같은 커밋에서 고치고 `L-nnn` 교훈을 남긴다.
