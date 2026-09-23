# CURRENT — 지금 하는 일

active: FIX-001
frozen: none

<!--
  "active" — 패키지 id (예: P1-schema) 또는 FIX-nnn. 없으면 none.
             stage-gate.sh 가 첫 번째 active: 줄을 읽는다. 활성 작업이 없으면 docs/·.claude/·reports/ 밖의 파일을 쓸 수 없다.
  "frozen" — 열린 기획서 변경 요청 id (예: CR-001). none 이 아니면 제품 코드 쓰기가 전부 차단된다.
             /devlog change 로 설정하고, CR 이행 완료 시 none 으로 되돌린다.
  갱신은 /devlog 절차로만 한다. 위 두 줄 외에 줄 첫머리에 active:/frozen: 을 쓰지 않는다.
-->

## 메모
- **P4b-er-redesign 완료(2026-09-23, verifier 04-review `완료`, 사용자 승인)** — verify-impl FAIL 0/WARN 1(01-plan 체크박스 표기), 수용 기준 16행 전부 충족, 부정 케이스 18건, 열린 [필수] 0. **게이트 `0.8 [] True True`**(T_merge 0.8 에서 오병합 0/132·미검출 0/132, 베이스라인 4종 모두 미지배, F1 0.8972, 되묻기 31건 23.5%, $0.0274). verifier 가 원시 지표에서 독립 재계산해 `metrics.json.gate` 와 일치 확인. U0 83d33dd·U1 85ceda7·U2 08bda7c·U3 dbcfca0·U4 b5b412c·U5선행 a8faa81·U5 855a26b·U6 4338eea·U7 cf5a171. **한계(판정에 박음)**: 40건·1회 실행이고 실행 간 `s_llm` 자기보고가 136 mention 중 60건 달라 게이트 개선을 D12·D13 단독 효과로 분해할 수 없다. 보수 강등 5건은 전부 귀속이 골드였다(막은 오병합 0). **P5 착수 가능.** 남은 [권고]: 판정 표 20행 경로 오기(01-plan 111행), 03-log Refs R8 어휘 충돌(L-nnn 후보), main 병합 작업 단위.
- P4b-er-redesign 계획 승인(2026-09-22, architect 초안 → 사용자 결정 A~I 권장 조합 → verifier 02-plan-verify 통과 FAIL 0/WARN 22 의도, 점검표 8/8, 사실 주장 6/6, 보류 0, 권고 R-1~R-9). U0 은 메인 세션(SKILL.md 정합, R-7), U1~U3 backend-agent(app/er 5파일 + er_smoke.py), U4~U7 eval-agent, U5 실 실행은 사용자(새 stamp, 기준선 stamp 사본 선커밋), 04-review verifier. **U4→U5 순서 필수.** 결정 A(i) ask 강등+relaxed_pass 예외·B ER_PENALIZED_MERGE_POLICY·C 완화 트리거 "감점 없는 후보 0"·D recheck weights_effective·E $5/1회·F 결정 K 불변·G §13·H meta 2키·I stamp 사본. P5 는 04-review 게이트 통과 후.
- **CR-001 이행완료(문서, 2026-09-22, 사용자 A 수용)**: D12(관측 신호 재정규화)·D13(규칙 필터 감점) 신설, D3 대체됨, S3.3·CLAUDE.md 원칙3·resolution-plan §3.3·proposal 상단·backlog P4b 행·review-index R3/R4·INDEX 갱신. frozen 은 문서 커밋으로 해제. **코드는 `P4b-er-redesign`**(backlog "P4b — 게이트 재도전") — `/devlog start P4b-er-redesign` 부터(architect 01-plan → verifier → 승인). P5 는 P4b 게이트 통과 후.
- P4-pilot-eval **부분완료**(2026-09-22, verifier 04-review, verify-impl FAIL 0/WARN 1→종료 커밋에서 0, 수용 기준 문장 2·해석 6·판정 표 14 중 게이트 2행 미달, 부정 20/20, 열린 [필수] 0, 사용자 승인). 게이트 미달(embedding_only 지배) → 재실행 없음, failure_cases.md. **다음 = /devlog change CR(①4단계 미측정 신호 가중치 재정규화 + ②2단계 규칙 필터 배제→감점, 사용자 결정 2026-09-22)**. P5 이후 시작 금지(결정 K (a)). dev f01ea35 푸시됨·승격 보류(L-003). 남은 [권고]: 러너 safe_summary FIX 후보, stamp UTC, 03-log Refs=커밋 Refs L-nnn, P10 F(iii)·mention_index 조인 키.
- P4-pilot-eval 계획 승인(2026-09-18, 01-plan 개정 2026-09-17 → verifier 1차 보류 H-1(결정 K 판정식) → 사용자 (a) 지배 기준·R-1~R-4 반영 → verifier 2차 통과(FAIL 0/WARN 3 의도, 점검표 8/8, 보류 0, R-5~R-7·O-4~O-6 은 구현·04-review 확인)). U1 부터 eval-agent(L-004 매번). 이 패키지가 P5 이후 게이트. 권고 F-95c6a7·F-0ffff5(registry 기존 행 확장) 는 04-review §5 에서 닫음.
- P3-llm-providers 완료(2026-09-15, verifier 04-review `완료`, verify-impl FAIL 0/WARN 0, 수용 기준 11/11, 부정 43/43, 열린 소견 0, 사용자 승인). U1 c01381d·U2 cf01e9f·U3 7b94a69·U4 10a66c3. 실호출 검증 공급자 0/3(F-87c597, 사용자 스모크 03·08). 다음 후보: P4-pilot-eval(04-review §7 인계 7항 + P3-baselines 15항 + P1 13항 — 01-plan 5행에 done 해시) / 사용자 스모크 03·08 / P0-cost. P4 통과 전 P5 이후 시작 금지.
- P3-llm-providers 계획 승인(2026-09-14, architect 초안 + 결정 1~7 확정(2026-09-11) → verifier 통과 FAIL 0/WARN 11 의도(registry 기존 행), 점검표 8/8, 보류 0, 권고 R-1~R-9 실행 시 반영). U1 부터 backend-agent(L-004 매번). `app/` 수정은 `judge.py`·`settings.py` 2파일뿐. D11 카드 신설.
- P3-baselines 완료(2026-09-11, verifier 04-review `완료`, verify-impl FAIL 0/WARN 0, 수용 기준 4/4, 부정 33/33, 필수 0·권고 8 중 1·2·3·4·5·7 처리, 사용자 승인). 다음 후보: P4-pilot-eval(04-review §7 인계 15항 + P1 §7 13항) / 사용자 스모크 03·08 / P0-cost. P4 통과 전 P5 이후 시작 금지.
- P3-baselines 계획 승인(2026-09-10, architect 초안 → 사용자 결정 A~H 전부 권장안 → verifier 통과 FAIL 0/WARN 1 의도, 권고 R-1~R-9 → 사용자 결정 I(R-3 candidate_person_ids)·J(R-5 judge.py 공개 승격 1건 예외)). U1 부터 eval-agent(L-004 매번). 코드는 `evaluation/` 최상위.
- P1-pilot-dataset 완료(2026-09-10, verifier 04-review `완료`, verify-impl FAIL 0/WARN 0, 사용자 승인). 다음 후보: P3 베이스라인 3종 / P4-pilot-eval(04-review §7 인계 13+5항) / P0-cost. P4 통과 전 P5 이후 시작 금지.
- P1-pilot-dataset 계획 승인(2026-09-06, architect 초안 → 사용자 결정 A~G → verifier 보류 3(H-1~H-3, F-033bb1) → 사용자 결정 → 반영 → 재검증 통과 FAIL 0/WARN 0, 권고 R-4~R-12). U1 부터 eval-agent(L-004 매번). 검수는 verifier 새 컨텍스트(U6 전).
- P3-er 계획 승인(2026-09-06, architect 초안 → verifier 보류 3 → 사용자 결정 → 개정 1 → 재검증 통과 FAIL 0/WARN 8 의도, 권고 6). U1 부터 backend-agent. 미착수: P1-pilot-dataset·P0-cost(eval-agent). 열림: F-4d2507(architect). 팀 밑작업 보류.
