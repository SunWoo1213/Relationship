# L-002 · 계획·구현·검증은 서로 다른 모델·컨텍스트가 맡는다

날짜: 2026-09-03 | 어디서(P / FIX / CR): 하네스 (P0-embed-pilot 완료 직후 사용자 지시) | Refs: harness L-002 verification

## 무슨 일이 있었나
- P0-embed-pilot 에서 메인 세션(한 컨텍스트, 한 모델)이 01-plan 을 쓰고, 같은 자리에서 02-plan-verify 점검표 8행을 "통과"로 채우고, 04-review 까지 썼다. 기계 검증은 돌았지만 **판정을 쓴 쪽이 만든 쪽과 같았다.**
- 사용자: "계획, 구현, 검증을 한 개의 컨텍스트, 한 개의 에이전트 모델이 진행하면 평가를 후하게 하는 경향이 있는 것을 방지하기 위해서 모델들을 각각 다르게 하고 싶다."

## 왜 그랬나
- 하네스가 "증거로 검증"은 강제했지만 "누가 검증하는가"는 강제하지 않았다. 점검표 근거 열에 카드를 인용해도, 인용을 고르는 것은 계획을 쓴 쪽이었다.
- 자기 평가는 자기 계획의 전제를 의심하지 않는다. 다른 모델·빈 컨텍스트에서 카드와 증거만 보고 판정해야 전제까지 본다.

## 다음부터
규칙으로 바꿀 것이 있으면 어느 파일(CLAUDE.md · 스킬 · 훅)을 고쳤는지 적는다.
- **배치**: 계획 `architect`=opus · 구현 `backend-agent`=sonnet · 평가 데이터 `eval-agent`=opus · 검증 `verifier`(신설)=fable · 메인 세션=조율·승인·커밋. 한 패키지에서 같은 에이전트가 두 단계를 맡지 않는다. verifier 는 항상 새 컨텍스트.
- **강제**: `verify-plan.sh` 는 02-plan-verify `검증자:` 줄에 `verifier` 가 없으면 FAIL, `verify-impl.sh` 는 04-review `검토자:` 줄로 같은 검사. 템플릿 자리에 `verifier (fable)` 를 넣었다.
- **왜 fable 이 검증인가**: 검증은 가장 비판적이어야 하는 자리라 가장 강한 모델을 둔다. 메인 세션도 fable 이지만 컨텍스트가 다르고 판정을 쓰지 않는다. 비용이 문제가 되면 검증=opus, 계획=sonnet 으로 바꾸되 구현과 검증이 같은 모델이 되지 않게 한다.
- 고친 파일: `.claude/agents/verifier.md`(신설), `.claude/agents/backend-agent.md`(model sonnet), `.claude/scripts/verify-plan.sh`·`verify-impl.sh`(검증자 검사), `docs/wiki/templates/plan-verify.md`·`package-review.md`, `.claude/skills/devlog/SKILL.md`(start 6·done 2·역할별 모델 표), `CLAUDE.md` 팀 표.
- P0-embed-pilot 문서는 소급하지 않는다(완료·승인됨). 재실행하면 검증자 검사 FAIL 이 나는 것이 정상이며 이 카드가 그 이유다.
