# 01 · 환경변수·API 키 (.env)

## 언제 필요한가
| 변수 이름 | 필요한 시점 | 없으면 |
|-----------|-----------|--------|
| `POSTGRES_USER` `POSTGRES_PASSWORD` `POSTGRES_DB` `POSTGRES_PORT` `POSTGRES_HOST` `DATABASE_URL` | 로컬 DB 기동·모든 DB 테스트 | 테스트가 skip 된다(`-rs` 로 이유 표시) |
| `ANTHROPIC_API_KEY` `ANTHROPIC_MODEL` (`LLM_PROVIDER=anthropic`) | ER 실호출 스모크(03), P4 파일럿 평가, P5 이후 제품 에이전트 | 스모크 종료 코드 2(안내만) |
| `OPENAI_API_KEY` `EMBEDDING_MODEL` (`EMBEDDING_PROVIDER=openai`) | 임베딩 백필(`scripts/backfill_embeddings.py --apply`), 후보 검색 실사용, P4 | 백필 종료 코드 2 |
| `OPENAI_MODEL` (`LLM_PROVIDER=openai` 일 때) | 판정기를 OpenAI 로 비교할 때(스모크 `--provider openai`) | 스모크 종료 코드 2 |
| `T_MERGE` `T_NEW` `W_LLM` `W_EMB` `W_RULE` | 기본값(0.8 / 0.3 / 0.5 / 0.3 / 0.2)으로 충분. **P4 곡선 결과로만 바꾼다** | 기본값 사용 |
| `VAPID_*` | P7 웹푸시 | 05 카드 |
| `GEMINI_*` | 예약값. 미구현 | — |

## 왜 사용자 몫인가
비밀은 에이전트가 읽지도 쓰지도 않는다(`docs/wiki/security.md` §1, 훅 `safety-guard.sh`). 코드는 `os.environ` 으로만 읽는다.

## 절차
1. 저장소 루트에 `.env` 가 없으면 `.env.example` 을 복사해 만든다(`.env` 는 `.gitignore` 에 있다).
2. DB 절 4개와 `DATABASE_URL` 의 포트·비밀번호를 **같은 값**으로 맞춘다. 이 PC 는 5432 충돌 때문에 **5433** 을 쓴다(HANDOFF 기록). 즉 `POSTGRES_PORT=5433`, `DATABASE_URL=postgresql://<user>:<pw>@localhost:5433/<db>`.
3. Anthropic 콘솔(console.anthropic.com → API Keys)에서 키를 만들어 `ANTHROPIC_API_KEY` 에 넣는다. `ANTHROPIC_MODEL` 은 `.env.example` 기본값(`claude-sonnet-5`)을 둔다.
4. OpenAI 대시보드(platform.openai.com → API keys)에서 키를 만들어 `OPENAI_API_KEY` 에 넣는다. 임베딩(D4 결정)에 필요하다. 사용 한도(usage limit)를 낮게 걸어 둔다.
5. 셸에서 로드하는 방법(값을 명령줄에 쓰지 않는다):
   - Git Bash: `set -a; source .env; set +a`
   - PowerShell: 아래 한 줄
     ```powershell
     Get-Content .env | Where-Object { $_ -match '^\s*[^#][^=]*=' } | ForEach-Object { $k,$v = $_ -split '=',2; [Environment]::SetEnvironmentVariable($k.Trim(), $v.Trim(), 'Process') }
     ```
6. `docker compose` 는 `.env` 를 자동으로 읽는다. pytest·스크립트는 위 5번을 한 셸에서 실행한다.

## 끝났다는 증거
- 키 값 자체는 어디에도 남기지 않는다. 증거는 **그 키를 쓴 명령의 출력**이다: 03 카드 스모크 evidence, 백필 `--dry-run` 건수 출력.
- 이름만 확인: `python scripts/db_check.py`(DB), `python scripts/er_smoke.py`(LLM — 키 없으면 rc 2 로 어떤 이름이 없는지 알려준다).

## 끝난 뒤 에이전트에게
"`.env` 에 ANTHROPIC_API_KEY·OPENAI_API_KEY 넣었어. 스모크는 내가 돌릴게(03)." — 이름만.
