# user-setup — 사용자가 직접 해야 하는 설정·결정 모음

> 에이전트(Claude Code)가 **할 수 없거나 해서는 안 되는** 일만 모았다: 비밀 값 입력, 외부 서비스 콘솔 조작, 실 API 호출, 승인 결정.
> 각 카드는 "언제 필요한가 → 왜 사용자 몫인가 → 절차 → 끝났다는 증거 → 끝난 뒤 에이전트에게 알릴 말" 순서다.
> 상태 열은 사용자가 직접 갱신한다(에이전트는 증거 파일이 생기면 갱신을 제안만 한다).

## 색인

| # | 카드 | 언제 필요한가 | 상태 | 관련 |
|---|------|-------------|------|------|
| 01 | [환경변수·API 키(.env)](01-env-keys.md) | 로컬 DB 기동 시(DB 4개), 실 LLM 호출 시(키), P4 파일럿 평가 전 | DB 값 완료(5433) · LLM/임베딩 키 **미입력** | `.env.example`, `docs/wiki/security.md` §1 |
| 02 | [AWS Budgets 비용 알림](02-aws-budgets.md) | **첫날 필수** — 아직 미완. 실서버 배포(P9) 전에는 반드시 | **미완** | `docs/backlog.md` 13행, `SERVER-CHECKLIST.md` 0-5 |
| 03 | [ER 실호출 스모크](03-er-smoke.md) | 키를 넣은 뒤 아무 때나. P4 전에 한 번 | **미실행**(F-87c597 열림) | `docs/wiki/packages/P3-er/05-remediation.md` F-87c597 |
| 04 | [로컬 DB(Docker)](04-local-db.md) | 테스트·ER 회귀 실행 전 | 완료(컨테이너 capstone2-postgres-1, 호스트 포트 5433) | `README.md` "로컬 DB" |
| 05 | [실서버·배포 비밀(SSM·VAPID·GitHub)](05-server-secrets.md) | P7(웹푸시)·P9(Terraform/Actions) 착수 시 | 해당 없음(P9 전) | `SERVER-CHECKLIST.md` §0·§4, `docs/wiki/decisions/D07-tls-caddy.md` |
| 06 | [하네스 승인 결정(무엇을 물어보는가)](06-approval-decisions.md) | 매 세션 | 상시 | `docs/wiki/lessons/`, `.claude/skills/commit` |
| 07 | [데모 리허설(P11)](07-demo-rehearsal.md) | P9 배포 후 | 해당 없음 | `docs/backlog.md` 74행, `README.md` "데모 시나리오" |
| 08 | [베이스라인 3 실 LLM 스모크](08-baseline-smoke.md) | 키를 넣은 뒤. **P4 파일럿 평가 전에 한 번**(03 카드와 같은 시점) | **미실행** | `scripts/baseline_smoke.py`, `README.md` "베이스라인 3종 실행법" |

## 규칙 (전 카드 공통)

- **값은 `.env` 또는 셸 환경변수에만.** 이 디렉터리·위키·커밋 메시지·에이전트 대화에 키 값·비밀번호를 적지 않는다. 에이전트는 `.env` 를 읽지도 쓰지도 않는다(훅이 막는다).
- 에이전트에게 "값을 넣었다"고 알릴 때는 **변수 이름**만 말한다(예: "ANTHROPIC_API_KEY 넣었어").
- 실 API 를 호출하는 명령은 사용자가 직접 실행한다. Claude Code 프롬프트에서 `! <명령>` 으로 실행하면 출력이 대화에 들어오므로, **키 값을 명령줄에 쓰지 말고** `.env` 를 로드한 셸에서 실행한다.
- 끝난 항목은 이 표의 상태 열과 `docs/backlog.md` 의 `[사용자]` 체크박스를 함께 갱신한다(에이전트에게 부탁해도 된다).
