# 08 · 베이스라인 3(LLM 단일 프롬프트) 실 LLM 스모크

## 언제 필요한가
P3-baselines 의 베이스라인 3(`evaluation/resolvers/llm_single.py`)은 스텁 클라이언트 테스트 69건으로만 검증됐다 — 자동 테스트는 네트워크를 부르지 않는다. 실제 API 가 이 방식의 구조화 출력 스키마(`{decision, matched_person_id, s_llm, reason, candidate_person_ids}`)를 받아 주는지, 제안 방식과 **같은 모델**로 도는지는 키를 넣은 **1회 실행**으로만 확인된다. P4 파일럿 평가는 이 방식을 40 시나리오에 돌리므로 **P4 착수 전에 한 번** 해 둔다(03 카드 ER 스모크와 같은 시점에 하면 왕복이 준다).

## 왜 사용자 몫인가
자동 테스트는 실 LLM 을 부르지 않는다(원칙8 재현성 — 재현 불가능한 수치를 만들지 않는다). 키는 사용자만 다룬다(`security.md` §6).

## 절차 (3분, 01 카드 완료 후)
1. `.env` 를 로드한 셸(01 카드 5번)에서, 저장소 루트에서:
   ```bash
   # Git Bash
   python scripts/baseline_smoke.py > docs/wiki/packages/P3-baselines/evidence/$(date +%Y%m%d-%H%M)-baseline-smoke-real.txt
   ```
   ```powershell
   # PowerShell
   $ts = Get-Date -Format yyyyMMdd-HHmm
   python scripts/baseline_smoke.py > docs/wiki/packages/P3-baselines/evidence/$ts-baseline-smoke-real.txt
   ```
2. (선택) OpenAI 경로 비교: `python scripts/baseline_smoke.py --provider openai > ...-baseline-smoke-real-openai.txt` (`OPENAI_API_KEY`·`OPENAI_MODEL` 필요).
3. 저장한 파일을 **한 번 읽는다**. 프롬프트는 길이(`prompt_chars`)와 인물 수(`person_count`)만 나가게 되어 있지만 저장 전 확인은 사용자 몫이다.
4. 종료 코드 해석: 0 = 성공(JSON 한 줄 — `method decision person_id score tokens_in tokens_out provider model forced_reason llm_error candidate_person_ids dropped_ids prompt_chars person_count mention`). 2 = 환경에 키 이름이 없음(01 카드). 3 = 공급자 호출·응답 오류(`llm_error` 가 `timeout`/`rate_limit`/`api_error`/`connection`/`schema` 중 하나, 결정은 `identity` 로 강등돼 나온다). **실패도 결과다** — 그 출력도 그대로 evidence 로 둔다.
5. DB 는 쓰지 않는다(이 스모크는 사전 상태 3명을 메모리에서 만든다). 즉 컨테이너가 꺼져 있어도 된다.

## 끝났다는 증거
- `docs/wiki/packages/P3-baselines/evidence/<ts>-baseline-smoke-real.txt` 가 존재하고 비어 있지 않다.
- 판정 명령: `python -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); print(d['provider'], d['model'], d['decision'], d['tokens_in'], d['tokens_out'], d['llm_error'])" <그 파일>` → 공급자·모델·결정이 찍히고 `llm_error` 가 `None` 이면 성공이다.

## 끝난 뒤 에이전트에게
"베이스라인 스모크 돌렸어, 파일 `<경로>`" → 에이전트가 P3-baselines 04-review·P4 계획에 "베이스라인 3 을 어느 공급자·모델로 돌렸는가"(01-plan P4 인계 5)를 적고 이 표의 상태 열을 갱신하는 작은 docs 커밋 초안을 올린다.
