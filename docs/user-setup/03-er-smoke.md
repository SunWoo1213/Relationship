# 03 · 엔티티 해석(ER) 실 LLM 호출 스모크 — F-87c597

## 언제 필요한가
P3-er 의 판정기(`app/er/judge.py`)는 스텁 테스트 36건으로만 검증됐다. 실제 API 가 구조화 출력(도구 정의 `strict`)을 받아 주는지, 모델 id(`claude-sonnet-5`)가 맞는지는 **키를 넣은 1회 실행**으로만 확인된다. 열린 권고 F-87c597(`docs/wiki/packages/P3-er/05-remediation.md`). 사용자 결정(2026-09-10): 지금은 건너뛰고 나중에 — **P4 파일럿 평가 전에는 해야 한다.**

## 왜 사용자 몫인가
자동 테스트는 실 LLM 을 부르지 않는다(원칙8 재현성). 키는 사용자만 다룬다(`security.md` §6).

## 절차 (5분, 01 카드 완료 후)
1. `.env` 를 로드한 셸(01 카드 5번)에서, 저장소 루트에서:
   ```bash
   # Git Bash
   python scripts/er_smoke.py > docs/wiki/packages/P3-er/evidence/$(date +%Y%m%d-%H%M)-er-smoke-real.txt
   ```
   ```powershell
   # PowerShell
   $ts = Get-Date -Format yyyyMMdd-HHmm
   python scripts/er_smoke.py > docs/wiki/packages/P3-er/evidence/$ts-er-smoke-real.txt
   ```
2. (선택) OpenAI 판정기 비교: `python scripts/er_smoke.py --provider openai > ...-er-smoke-real-openai.txt` (`OPENAI_MODEL` 필요).
3. 저장한 파일을 **한 번 읽는다**. 키·프롬프트 원문이 나오지 않게 되어 있지만 저장 전 확인은 사용자 몫이다.
4. 종료 코드 해석: 0 = 성공(JSON 한 줄, 9키 `provider model tokens_in tokens_out s_llm matched_person_id reason confidence band`). 2 = 환경에 키 이름이 없음(01 카드). 3 = 공급자 호출 실패(`{"error": "<유형>"}`) — 모델 이름·할당량·공급자 상태를 먼저 본다. **실패도 결과다** — 그 출력도 evidence 로 둔다.
5. DB 가 떠 있으면 trace 확인(선택): `SELECT step, tool_name, output->'confidence_breakdown', output->'decision' FROM agent_traces ORDER BY id DESC LIMIT 1;`

## 끝났다는 증거
- `docs/wiki/packages/P3-er/evidence/<ts>-er-smoke-real.txt` 가 존재하고 비어 있지 않다.
- 판정 명령(05-remediation F-87c597 해결 단계 1): `python -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); print(sorted(d))" <그 파일>` → 9키 또는 `error` 1키.

## 끝난 뒤 에이전트에게
"스모크 돌렸어, 파일 `<경로>`" → 에이전트가 F-87c597 을 닫고 `review-index.md` R4 표기("실호출 확인")를 갱신하는 작은 docs 커밋 초안을 올린다.
