# P4b-er-redesign · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-09-22 · docs(P4b-er-redesign): 계획검증 통과·계획 승인 — CR-001 D12·D13 구현 + 재실행 + 게이트 재판정, 패키지 착수 · 83d33dd
- 변경: `01-plan.md`(architect 초안 → 메인 세션 형식 2건(작업 단위 접두·해석 불릿 들여쓰기) + "## 결정 (사용자 확정 2026-09-22)" 표 + `ER_PENALIZED_MERGE_POLICY` 치환 + 권고 R-3(`scripts/er_smoke.py:109` 산출물·U1 명시)·R-9(`*real-run*` 파일명 규약) 반영), `02-plan-verify.md`(verifier, `결과: 통과`, 승인 줄), `05-remediation.md`(findings.py [권고] 22 — registry 기존 행 18 + basename 오탐 4, [필수] 0), `evidence/`(verify-plan 1~3차 + verifier 1710·1718 + `1713-regression3-baseline.txt` 3 passed + `.gitkeep`), `docs/backlog.md` 65행(`types.py`(+`settings.py`) 허용 파일 — 개정 (2) 반영, (1) 거절), `docs/wiki/changes/CR-001.md` 36행(기준선 = stamp 사본, 결정 I), `CURRENT.md` active + 메모, journal DECISION·VERIFY·START, HANDOFF. 코드·`data/`·`reports/` 변경 **0**
- 이유(기획서·카드 연결): CR-001 §4 4항 "수정은 `P4b-er-redesign` 패키지 안에서". backlog "### P4b — 게이트 재도전 (CR-001)" 65·66행 = 01-plan 72·73행(diff 0줄). D12·D13 "코드에서 지켜야 할 것"이 U1~U3 의 문장이고, 결정 K(P4 01-plan 227행)·S3.7 게이트 식은 불변(결정 F). 사용자 결정 A~I(권장 조합, 18:20)
- 정합성 확인: 원칙 1(A(i) 강등)·3(D12 = CLAUDE.md 38행)·4·8(재실행 1회·기준선 stamp 사본)·9(weights_effective·penalized_by) / D12 D13 D10 / S3.3 S3.7 / 보안(`.env` 로드 주체 사용자 셸) — 위반 없음(02-plan-verify 점검표 8/8, 사실 주장 (a)~(f) 6/6). 코드 변경 0
- 남은 것 · 다음 단위: **U0**(메인 세션, R-7: `.claude/skills/entity-resolution/SKILL.md` 22·36·39행 D12·D13 정합 + "권위는 S3.3·D12·D13" 한 줄, CR-001 §2 파일 목록 갱신 이력 한 줄) → **U1**(backend-agent, L-004 승인 후): `combine()` 재정규화·`_breakdown` `weights_effective`/`rule_checked`·강제 경로·`er_smoke.py:109` + 테스트. U4→U5 순서 필수(recheck 가 새 trace 거부). R-4(U2 03-log 에 완화 통과 후보 `penalized_by` 채움 여부 확정)·R-5(U4 rule_checked=0 재계산 테스트)·R-8(U3 ask_payload candidate_ids 단언)·R-6(04-review 에 P4 04-review 220행 대체 한 줄)·R-2(하네스 L-nnn 후보: verify-plan 5번 불릿 의존 파싱)
- Refs: P4b-er-redesign CR-001 D12 D13 D10 S3.3 S3.7 R3 R4 원칙1 원칙3 원칙8 원칙9 L-002 L-004

## 2026-09-22 · harness(P4b-er-redesign): U0 entity-resolution 스킬 카드 D12·D13 정합 — 권위 문구·감점·재정규화 산식 · pending
- 변경: `.claude/skills/entity-resolution/SKILL.md` — 머리에 "권위는 S3.3·D12·D13·D10, 이 카드는 미러" 한 줄(R-7 이중 출처 방지), 22행 2단계 "명백히 다른 후보 배제" → 감점·후보 유지(사전 모순만 배제, D13), 36행 `s_rule` 미측정 규약(D12), 39행 산식 → `Σ w_i·s_i / Σ w_i` + 두 경우 전개 + `weights_effective`·보수 분기(`ER_PENALIZED_MERGE_POLICY=ask`, `relaxed_pass` 예외) 문단. `docs/wiki/changes/CR-001.md` 갱신 이력(§2 파일 목록에 `types.py`·`er_smoke.py`·SKILL.md). 이 로그(직전 `pending`→83d33dd). 코드 변경 **0**
- 이유(기획서·카드 연결): 01-plan U0 — backend-agent 가 자동 참조하는 카드가 D3 산식·배제 문장을 그대로 갖고 있으면 U1~U3 이 옛 규약으로 구현된다(02-plan-verify 사실 주장 (d): `D12|D13|CR-001|감점|penalized` grep 0건). verifier 분류(R-7): 위치는 하네스 파일이나 S3.3 3행이 "절차 상세"로 가리키는 명세 미러 → 하네스 문서 정합 커밋(메인 세션). 문장은 D12 6~8행·D13 5~8행·P4b 결정 A(i)·B(i) 를 옮겼다
- 정합성 확인: 원칙3(새 문장 = CLAUDE.md 38행 = D12)·원칙1(강등 기본)·원칙9 / D12 D13 D10 / S3.3 / 보안 — 위반 없음. 판정: `grep -nE "D12|D13|penalized|weights_effective" .claude/skills/entity-resolution/SKILL.md` ≥ 4건, `grep -c "0.5·s_llm + 0.3·s_emb + 0.2·s_rule" SKILL.md` = 1(세 신호 모두 관측 경우의 전개로만 남음)
- 남은 것 · 다음 단위: **U1** backend-agent 위임 승인(L-004) — `combine()` 재정규화·`_breakdown` `weights_effective`/`rule_checked`·강제 경로 키·`er_smoke.py:109` + 테스트(`test_er_confidence.py` 293행 원식 수치 유지, 미측정 케이스 추가)
- Refs: P4b-er-redesign CR-001 D12 D13 S3.3 원칙3 원칙9 L-004
