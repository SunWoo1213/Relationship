# CURRENT — 지금 하는 일

active: none
frozen: none

<!--
  "active" — 패키지 id (예: P1-schema) 또는 FIX-nnn. 없으면 none.
             stage-gate.sh 가 첫 번째 active: 줄을 읽는다. 활성 작업이 없으면 docs/·.claude/·reports/ 밖의 파일을 쓸 수 없다.
  "frozen" — 열린 기획서 변경 요청 id (예: CR-001). none 이 아니면 제품 코드 쓰기가 전부 차단된다.
             /devlog change 로 설정하고, CR 이행 완료 시 none 으로 되돌린다.
  갱신은 /devlog 절차로만 한다. 위 두 줄 외에 줄 첫머리에 active:/frozen: 을 쓰지 않는다.
-->

## 메모
- P3-baselines 완료(2026-09-11, verifier 04-review `완료`, verify-impl FAIL 0/WARN 0, 수용 기준 4/4, 부정 33/33, 필수 0·권고 8 중 1·2·3·4·5·7 처리, 사용자 승인). 다음 후보: P4-pilot-eval(04-review §7 인계 15항 + P1 §7 13항) / 사용자 스모크 03·08 / P0-cost. P4 통과 전 P5 이후 시작 금지.
- P3-baselines 계획 승인(2026-09-10, architect 초안 → 사용자 결정 A~H 전부 권장안 → verifier 통과 FAIL 0/WARN 1 의도, 권고 R-1~R-9 → 사용자 결정 I(R-3 candidate_person_ids)·J(R-5 judge.py 공개 승격 1건 예외)). U1 부터 eval-agent(L-004 매번). 코드는 `evaluation/` 최상위.
- P1-pilot-dataset 완료(2026-09-10, verifier 04-review `완료`, verify-impl FAIL 0/WARN 0, 사용자 승인). 다음 후보: P3 베이스라인 3종 / P4-pilot-eval(04-review §7 인계 13+5항) / P0-cost. P4 통과 전 P5 이후 시작 금지.
- P1-pilot-dataset 계획 승인(2026-09-06, architect 초안 → 사용자 결정 A~G → verifier 보류 3(H-1~H-3, F-033bb1) → 사용자 결정 → 반영 → 재검증 통과 FAIL 0/WARN 0, 권고 R-4~R-12). U1 부터 eval-agent(L-004 매번). 검수는 verifier 새 컨텍스트(U6 전).
- P3-er 계획 승인(2026-09-06, architect 초안 → verifier 보류 3 → 사용자 결정 → 개정 1 → 재검증 통과 FAIL 0/WARN 8 의도, 권고 6). U1 부터 backend-agent. 미착수: P1-pilot-dataset·P0-cost(eval-agent). 열림: F-4d2507(architect). 팀 밑작업 보류.
