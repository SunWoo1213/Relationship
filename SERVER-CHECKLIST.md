# 실서버 점검 가이드 (SERVER-CHECKLIST)

> 목적: `dev` 브랜치를 실서버에 올린 뒤 **무엇을, 어떤 순서로, 어떤 증거를 남기며** 점검하는지 정한다.
> 브랜치 전략(L-001): 작업·푸시는 `dev` → **실서버 검증** → `/commit release` 로 `main` 승격. 이 문서는 그 가운데 "실서버 검증" 단계의 기준이다.
> 원칙: 점검은 **가시적 증거**로만 한다(`docs/wiki/verification.md`). "확인했습니다"는 증거가 아니다. 명령 출력·HTTP 응답 본문·스크린샷 경로·커밋 해시만 증거다.
> 비밀: 키·비밀번호·접속 문자열은 **절대** 출력·복사·문서에 넣지 않는다(`docs/wiki/security.md` §1). 필요한 것은 환경변수 **이름**뿐이다.

배포 구성(확정 D7): CloudFront → EC2(Caddy, Let's Encrypt HTTPS) → FastAPI(Docker) → RDS PostgreSQL + pgvector(프라이빗 서브넷). 프론트는 S3 + CloudFront. 비밀은 SSM Parameter Store. ALB 없음.
인프라 자동화(Terraform·GitHub Actions)는 P9-infra 에서 만든다. 그 전까지는 아래 절차를 사람이 손으로 수행하되, 명령과 증거 규약은 동일하다.

---

## 0. 점검 전 준비 (배포하기 전에)

| # | 확인 | 방법 | 통과 기준 |
|---|------|------|-----------|
| 0-1 | 올릴 커밋이 dev 의 HEAD 이고 로컬 검증을 통과했다 | `git log --oneline -1 origin/dev`, 해당 패키지 `04-review.md` 의 `결과: 완료` | 해시 일치, 완료 판정 존재 |
| 0-2 | 서버에 필요한 환경변수 **이름**이 전부 있다 | `.env.example` 의 이름 목록과 SSM 파라미터 이름 대조 (값은 보지 않는다) | 누락 0 |
| 0-3 | DB 마이그레이션 계획이 있다 | `alembic history` 로 현재 head 확인, 새 revision 이면 downgrade 경로도 있는지 | head 명확, downgrade 존재 |
| 0-4 | 되돌릴 방법이 정해져 있다 | 직전 배포 이미지 태그(또는 커밋 해시) 메모 | 태그 1개 기록 |
| 0-5 | 비용 알림이 켜져 있다 | AWS Budgets $10 / $30 / $50 알림 3개 (콘솔) | 3개 활성 |

필수 환경변수 이름(값 없음): `DATABASE_URL` 또는 `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB`/`POSTGRES_HOST`/`POSTGRES_PORT`, `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `LLM_PROVIDER`, `T_MERGE`/`T_NEW`/`W_LLM`/`W_EMB`/`W_RULE`(임계치, 없으면 기본값). 정확한 목록은 항상 `.env.example` 이 권위다.

---

## 1. 배포 직후 — 프로세스·네트워크 (5분)

서버(EC2)에 SSH 로 들어가 실행한다. 출력은 `docs/wiki/packages/<패키지>/evidence/<YYYYMMDD-HHMM>-server-*.txt` 로 저장한다(서버에서 파일로 받아 저장소에 넣는다. 비밀이 섞이지 않았는지 저장 전에 읽는다).

| # | 확인 | 명령 | 통과 기준 |
|---|------|------|-----------|
| 1-1 | 컨테이너가 떠 있다 | `docker compose ps` | 백엔드 `running`, 재시작 루프 없음 |
| 1-2 | 최근 로그에 예외가 없다 | `docker compose logs --tail=200 backend` | Traceback 0, 접속 문자열·키 문자열 0 |
| 1-3 | Caddy 가 인증서를 받았다 | `docker compose logs --tail=100 caddy` 또는 `journalctl -u caddy -n 100` | `certificate obtained` 류 메시지, 오류 없음 |
| 1-4 | 로컬 포트에서 헬스가 뜬다 | `curl -s http://127.0.0.1:8000/health` | `{"status":"ok","db":"up","alembic_revision":"<head>"}` |
| 1-5 | HTTPS 종단이 응답한다 | `curl -sI https://<도메인>/health` | `HTTP/2 200`, 인증서 오류 없음 |
| 1-6 | CloudFront 를 거쳐도 같다 | `curl -s https://<CloudFront 도메인>/health` | 1-4 와 같은 본문 |

`/health` 가 503 `{"status":"degraded","db":"down"}` 이면 DB 접속 문제다. 본문에 접속 정보가 나오면 그 자체가 **보안 결함**이므로 즉시 되돌린다(§6).

---

## 2. 데이터베이스 (5분)

RDS 는 프라이빗 서브넷이므로 EC2 에서 실행한다. 컨테이너 안에서 실행하면 환경변수가 이미 있다: `docker compose exec backend <명령>`.

| # | 확인 | 명령 | 통과 기준 |
|---|------|------|-----------|
| 2-1 | 접속·확장 | `python scripts/db_check.py` | 종료 코드 0, pgvector 확장 확인 |
| 2-2 | 마이그레이션이 head 다 | `python -m alembic current` | 코드의 head revision 과 동일 |
| 2-3 | 스키마 실물이 모델과 같다 | `python scripts/schema_check.py` | FAIL 0 |
| 2-4 | 미적용 변경이 없다 | `python -m alembic check` | `No new upgrade operations detected.` |
| 2-5 | 임베딩 누락이 없다 | `python scripts/backfill_embeddings.py --dry-run` | 대상 건수 확인(0 이 정상, 0 이 아니면 §4-3) |

`alembic upgrade head` 는 **배포 절차의 일부**로 사람이 실행한다. 점검 단계에서는 상태만 본다. DROP/TRUNCATE 를 셸에서 치지 않는다(security.md §4).

---

## 3. API 계약 (5분)

서버 밖(개발 PC)에서 공개 도메인으로 실행한다. 응답 본문을 evidence 로 남긴다.

| # | 확인 | 명령 | 통과 기준 |
|---|------|------|-----------|
| 3-1 | 헬스 | `curl -s https://<도메인>/health` | 200, `alembic_revision` 이 2-2 와 같다 |
| 3-2 | 없는 질문 | `curl -s -o /dev/null -w "%{http_code}" -X POST https://<도메인>/answers/999999 -H "Content-Type: application/json" -d '{"answer":"예"}'` | `404` |
| 3-3 | 잘못된 본문 | 같은 명령에 `-d '{}'` | `422` |
| 3-4 | 툴 시그니처 회귀 | 서버 컨테이너에서 `python scripts/tools_check.py` | `7/7 ok` |
| 3-5 | 오류 본문에 내부 정보 없음 | 3-2·3-3 응답 본문 읽기 | 스택·경로·접속 문자열 0 |

P5-loop 이후에는 채팅 엔드포인트와 `POST /answers/{id}` 재개 흐름이 여기에 추가된다. 그때 이 표를 갱신한다.

---

## 4. 엔티티 해석(ER)·LLM 실호출 (10분, 키 필요)

로컬 자동 테스트는 실 LLM 을 부르지 않는다(원칙8 재현성). **실호출 검증은 실서버 점검에서만 한다.** 키는 SSM → 컨테이너 환경변수로만 흐른다. 명령줄에 키 값을 쓰지 않는다.

| # | 확인 | 명령(컨테이너 안) | 통과 기준 |
|---|------|------|-----------|
| 4-1 | 판정기 실호출 1회 | `python scripts/er_smoke.py` (공급자는 `LLM_PROVIDER`, 또는 `--provider anthropic\|openai`) | 종료 0, JSON 한 줄에 `provider`·`model`·`tokens_in`·`tokens_out`·`s_llm`·`confidence`·`band` |
| 4-2 | 다른 공급자로도 된다 | `python scripts/er_smoke.py --provider openai` | 4-1 과 같은 키 집합 |
| 4-3 | 임베딩 백필(대상이 있을 때만) | `python scripts/backfill_embeddings.py --dry-run` → 건수 확인 → `--apply` | apply 후 dry-run 대상 0 |
| 4-4 | trace 가 남는다 | 4-1 뒤 DB 에서 `SELECT step, tool_name, output->'confidence_breakdown', output->'decision' FROM agent_traces ORDER BY id DESC LIMIT 1;` | `step='er_resolve'`, `confidence_breakdown` 5키 + `matched_person_id`, `decision.band` |

스모크 출력에는 프롬프트 원문과 키가 나오지 않게 되어 있다. 그래도 저장 전에 한 번 읽는다. 종료 코드 2 는 키 이름이 환경에 없다는 뜻이고, 3 은 공급자 호출 실패(`{"error": "<유형>"}`)다. 3 이면 §6 이 아니라 공급자 상태·모델 이름(`ANTHROPIC_MODEL`/`OPENAI_MODEL`)·할당량을 먼저 본다.

4-1 의 출력 파일은 `docs/wiki/packages/P3-er/evidence/<YYYYMMDD-HHMM>-er-smoke-real.txt` 로 저장하고, `review-index.md` 의 R4 "실호출 미검증" 표기를 갱신한다.

---

## 5. 데모 시나리오 재현 (P8 이후, 15분)

`README.md` "데모 시나리오 (3분)" 5단계를 배포 URL 에서 그대로 재현한다. P9 의 수용 기준이 정확히 이것이다.

| 단계 | 발화 | 기대 |
|------|------|------|
| 1 | "오늘 김팀장이랑 또 부딪혔어" | 인물 인식 → 확인 질문(`new_person`) |
| 2 | 몇 턴 대화 | 인물 카드가 채워진다 |
| 3 | "다음 주 화요일에 그 사람이랑 회의 있어" | 일정 자동 추출 |
| 4 | "부장님이 또 그러시더라" | "김팀장님 말씀이신가요?" 확인(`identity`) — **자동 병합되면 실패** |
| 5 | 브리핑 | 최근 사건 패턴 + 한 줄 제안 |

각 단계의 화면 스크린샷을 `docs/wiki/packages/<패키지>/evidence/<YYYYMMDD-HHMM>-demo-<n>.png` 로 남긴다. 4단계에서 확인 없이 병합되면 원칙1 위반이므로 승격하지 않는다.

---

## 6. 되돌리기 기준과 방법

다음 중 하나면 **승격하지 않고** 직전 이미지로 되돌린다.

- `/health` 가 200 이 아니거나 `alembic_revision` 이 head 와 다르다.
- 오류 응답·로그에 접속 문자열·키·스택이 노출된다.
- `schema_check.py` FAIL, `tools_check.py` 가 7/7 이 아니다.
- 데모 4단계에서 확인 없이 자동 병합된다(원칙1).
- 실 LLM 스모크가 두 공급자 모두 실패한다(3 종료).

되돌리기: 컨테이너 이미지를 0-4 의 태그로 바꿔 `docker compose up -d`. DB 는 새 revision 을 올렸다면 `alembic downgrade <직전>` 을 **사람이** 판단해 실행한다(데이터 손실 여부를 먼저 본다). 코드는 `dev` 에 `git revert` 커밋을 만들어 다시 올린다. `main` 을 직접 고치지 않는다.

---

## 7. 승격 (검증이 끝나면)

1. §1~§4 의 evidence 파일이 저장소에 있고, 비밀이 없는지 읽어 확인한다.
2. `HANDOFF.md` 에 "실서버 검증: <날짜>, 증거 경로 목록" 한 줄.
3. `/commit release` — 사용자 승인 → `git push origin dev:main`(fast-forward 만). 훅이 main 직접 푸시를 막는다.
4. `journal.md` 에 `RELEASE` 줄이 붙는지 확인한다.

---

## 8. 정기 점검 (배포와 무관, 주 1회)

| 확인 | 방법 | 기준 |
|------|------|------|
| 비용 | AWS Budgets 알림·Cost Explorer | 예산 내, 알림 3개 활성 |
| 인증서 | `curl -sI https://<도메인>` 의 만료일 | 30일 이상 남음(Caddy 가 자동 갱신) |
| 디스크·로그 | `df -h`, `docker system df` | 80% 미만. 정리는 사용자가(prune 은 훅 금지 명령) |
| DB 크기·trace 누적 | `SELECT count(*) FROM agent_traces;` | 급증 시 보존 정책 결정(P5 이후) |
| 임베딩 누락 | `backfill_embeddings.py --dry-run` | 0 |

---

## 부록 — 점검 기록 양식

evidence 파일 머리에 다음을 적는다.

```
검증 대상: dev <해시>  /  배포 URL: https://<도메인>
일시: YYYY-MM-DD HH:MM  /  실행자: <역할>
항목: <표 번호>  /  명령: <그대로>  /  결과: <통과|실패>
```

한 파일에 한 명령. 파일 이름은 `<YYYYMMDD-HHMM>-server-<항목>.txt`. 비밀이 섞인 파일은 저장하지 않고 다시 뜬다.
