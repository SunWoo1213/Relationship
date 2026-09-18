# P4-pilot-eval · 계획 검증 (02-plan-verify)

대상: 01-plan.md | 검증자: verifier (fable) — 계획 작성자(eval-agent, 초안 701fb8d + 미커밋 개정)와 다른 모델·컨텍스트(L-002) | 날짜: 2026-09-17 | **2차 재검증: 2026-09-17 09:50** — 1차(09:30) `결과: 보류`(H-1) → 사용자 결정 (a) 지배 기준 → 메인 세션이 01-plan 개정(3행 `개정: 2026-09-17(…)`) → 이 문서는 **개정 diff 만** 대조해 §1c·§1d·§2(2·3·4·6행 덧붙임)·§3·§3c K 행·§4 를 갱신했다. 1차 본문의 01-plan 행 번호는 09:30 작업본 기준이며 현재 파일과의 오프셋은 §3 O-6 에 적었다.

기준 상태: `bash .claude/scripts/gitlog.sh P4-pilot-eval` — `dev = main(origin) = 3c6108d`, 승격 대기 0, `P4-pilot-eval` 태그 커밋 1건(701fb8d 계획 초안), 미커밋 변경 = `01-plan.md`(P3-llm-providers 인계 7항 표·해시 59c67cc·카드 번호 10·pytest 918 반영, `git diff` +26/−11) + `05-remediation.md`·`evidence/`(신규). 코드 0줄 — 미착수 정상. **2차 시점**: HEAD 여전히 3c6108d, `01-plan.md` 미커밋 diff 에 09-17 개정분(hunk `+52`·`+105,3`·`+226`·`+278,2` 등, `evidence/20260917-0950-plan-refs2.txt` 첫 블록)이 더해져 282행.

이 문서가 남긴 evidence(전부 `docs/wiki/packages/P4-pilot-eval/evidence/`):
- `20260917-0922-verify-plan.txt` — 1a 초안 실행(FAIL 1 = 이 문서 부재)
- `20260917-0922-validate-scenarios.txt` — `python scripts/validate_scenarios.py --strict --json` rc=0, `total` 40·`ambiguous_mention_count` 3·`trap_count` 12·`schema_version` 2
- `20260917-0922-plan-signatures.txt` — 01-plan 이 인용한 시그니처·detail 키·판정 규칙 grep(116줄)
- `20260917-0922-plan-refs.txt` — 인용 커밋 해시 27건 실재(`MISSING` 0)·backlog/INDEX/registry 실제 행 번호·수용 기준 글자 대조(`SAME_AFTER_CHECKBOX_STRIP`)
- `20260917-0930-verify-plan.txt` — 1b 최종 실행(아래 §1b)
- `20260917-0943-verify-plan.txt` — 2차: 개정본 기계 검증(메인 세션 실행, 아래 §1c)
- `20260917-0950-plan-refs2.txt` — 2차: 개정 7항 grep 대조(155줄) — K 행·U4 `gate` 산식·판정 표 행 인용, 결정 K 원문 `K_ORIGINAL_PRESERVED`, backlog 15행 문장 `grep -F` 일치, registry 16행·backlog 59/61·INDEX 70/80 실제 행, `ANTHROPIC_API_KEY` 잔재 0, 수용 기준 `SAME_AFTER_CHECKBOX_STRIP`(backlog 61 ↔ 01-plan 76), `exact_match.py:264~276`·`confidence.py:82~90` 원문
- `20260917-0954-verify-plan.txt` — 2차 최종 실행(아래 §1d, FAIL 0·WARN 3)

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)

### 1a. 초안 실행 (이 문서 작성 전)
명령: `bash .claude/scripts/verify-plan.sh P4-pilot-eval | tee docs/wiki/packages/P4-pilot-eval/evidence/20260917-0922-verify-plan.txt`
```
== verify-plan P4-pilot-eval  (2026-09-17 09:25) ==
PASS  존재: docs/wiki/packages/P4-pilot-eval/01-plan.md
FAIL  없음: docs/wiki/packages/P4-pilot-eval/02-plan-verify.md
PASS  카드 존재: D10
PASS  카드 존재: D11
PASS  카드 존재: D3
PASS  카드 존재: D4
PASS  카드 존재: D5
PASS  패키지 id 등록됨: P0-cost
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P3-llm-providers
PASS  패키지 id 등록됨: P4-pilot-eval
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R3
PASS  검증 항목 존재: R9
PASS  Refs 있음: - [ ] U1 **러너 골격·격리·적재**: `evaluation/runn
PASS  Refs 있음: - [ ] U2 **지표 계산기**: `evaluation/metrics.py` — �
PASS  Refs 있음: - [ ] U3 **보정표**: `evaluation/calibration.py` → `rep
PASS  Refs 있음: - [ ] U4 **곡선·metrics.json 조립**: `evaluation/curve.
PASS  Refs 있음: - [ ] U5 **리포트 생성기**: `evaluation/report.py` —
PASS  Refs 있음: - [ ] U6 **실행 CLI·dry-run·비용 가드**: `scripts/ru
PASS  Refs 있음: - [ ] U7 **실 공급자 1회 실행**: 임베딩 OpenAI `te
PASS  Refs 있음: - [ ] U8 **실패 케이스 분석**: `reports/failure_cases
PASS  Refs 있음: - [ ] U9 **수용 기준 기계 검증 + 문서**: 전체 `P
PASS  backlog 일치: [eval-agent] **파일럿 평가** (오병합률·미검출�
PASS  의존 완료: P1-pilot-dataset
PASS  의존 완료: P3-baselines
PASS  의존 완료: P3-er
PASS  의존 완료: P3-llm-providers
PASS  registry 중복 없음: evaluation/runner.py
PASS  registry 중복 없음: evaluation/metrics.py
PASS  registry 중복 없음: evaluation/calibration.py
PASS  registry 중복 없음: evaluation/curve.py
PASS  registry 중복 없음: evaluation/report.py
PASS  registry 중복 없음: reports/metrics.json
PASS  registry 중복 없음: reports/eval.md
PASS  registry 중복 없음: scripts/run_pilot_eval.py
PASS  registry 중복 없음: reports/metrics.json
PASS  registry 중복 없음: reports/calibration.json
PASS  registry 중복 없음: reports/curve.csv
PASS  registry 중복 없음: reports/eval.md
WARN  registry 에 다른 패키지로 이미 있음: metrics.json → | 모듈 | 이름→팩토리 방식 표(`RESOLVERS`·`register`·`get_resolver`
PASS  registry 중복 없음: reports/failure_cases.md
PASS  registry 중복 없음: tests/test_eval_runner.py
PASS  registry 중복 없음: tests/test_eval_metrics.py
PASS  registry 중복 없음: tests/test_eval_calibration.py
PASS  registry 중복 없음: tests/test_eval_curve.py
PASS  registry 중복 없음: tests/test_eval_report.py
WARN  registry 에 다른 패키지로 이미 있음: metrics.json → | 모듈 | 이름→팩토리 방식 표(`RESOLVERS`·`register`·`get_resolver`
PASS  registry 중복 없음: docs/user-setup/10-pilot-eval-run.md
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
== 결과: FAIL=1 WARN=3 ==
```
FAIL 1 = 이 문서(02-plan-verify.md) 부재 → 이 문서로 해소(05-remediation F-0e133a). WARN 3 판정(05-remediation F-95c6a7·F-0ffff5):
- `metrics.json` ×2 — 스크립트가 basename `metrics.json` 을 registry 전문에서 찾아 **112행 비고 문구**(`evaluation/resolvers/registry.py` 행의 "예약 이름 5개 … = `metrics.json` 키")에 걸린 것이다(`evidence/20260917-0922-plan-refs.txt` `grep -n "metrics.json" docs/wiki/registry.md` → 112행 1건뿐, `reports/metrics.json` 행은 없다). 신규 산출물이 맞고 중복 구현이 아니다. 오탐 — 조치 없음.
- `README.md` — registry 33행(하네스, pending)의 기존 파일이다. 01-plan 120행이 "새 절을 만들지 않고 **'파일럿 평가 실행법'을 이어 붙인다**(F-0ffff5 선례 — registry 비고에 한 줄)" 로 **의도된 확장**을 명시했고, 59행 "registry — 신규 행(기존 행은 비고만)" 과 정합. P3-baselines·P3-llm-providers 가 같은 방식(R-8 "기존 행 비고만")으로 닫았다. 의도된 확장 — 조치 없음. 04-review 가 registry 33행 비고에 `P4-pilot-eval U9` 한 줄이 있는지 본다.

### 1b. 최종 실행 (이 문서 작성 후)
명령: `bash .claude/scripts/verify-plan.sh P4-pilot-eval | tee docs/wiki/packages/P4-pilot-eval/evidence/20260917-0930-verify-plan.txt`
```
== verify-plan P4-pilot-eval  (2026-09-17 09:30) ==
PASS  존재: docs/wiki/packages/P4-pilot-eval/01-plan.md
PASS  존재: docs/wiki/packages/P4-pilot-eval/02-plan-verify.md
PASS  카드 존재: D10
PASS  카드 존재: D11
PASS  카드 존재: D3
PASS  카드 존재: D4
PASS  카드 존재: D5
PASS  패키지 id 등록됨: P0-cost
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P3-llm-providers
PASS  패키지 id 등록됨: P4-pilot-eval
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R3
PASS  검증 항목 존재: R9
PASS  Refs 있음: - [ ] U1 **러너 골격·격리·적재**: `evaluation/runn
PASS  Refs 있음: - [ ] U2 **지표 계산기**: `evaluation/metrics.py` — �
PASS  Refs 있음: - [ ] U3 **보정표**: `evaluation/calibration.py` → `rep
PASS  Refs 있음: - [ ] U4 **곡선·metrics.json 조립**: `evaluation/curve.
PASS  Refs 있음: - [ ] U5 **리포트 생성기**: `evaluation/report.py` —
PASS  Refs 있음: - [ ] U6 **실행 CLI·dry-run·비용 가드**: `scripts/ru
PASS  Refs 있음: - [ ] U7 **실 공급자 1회 실행**: 임베딩 OpenAI `te
PASS  Refs 있음: - [ ] U8 **실패 케이스 분석**: `reports/failure_cases
PASS  Refs 있음: - [ ] U9 **수용 기준 기계 검증 + 문서**: 전체 `P
PASS  backlog 일치: [eval-agent] **파일럿 평가** (오병합률·미검출�
PASS  의존 완료: P1-pilot-dataset
PASS  의존 완료: P3-baselines
PASS  의존 완료: P3-er
PASS  의존 완료: P3-llm-providers
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: evaluation/runner.py
PASS  registry 중복 없음: evaluation/metrics.py
PASS  registry 중복 없음: evaluation/calibration.py
PASS  registry 중복 없음: evaluation/curve.py
PASS  registry 중복 없음: evaluation/report.py
PASS  registry 중복 없음: reports/metrics.json
PASS  registry 중복 없음: reports/eval.md
PASS  registry 중복 없음: scripts/run_pilot_eval.py
PASS  registry 중복 없음: reports/metrics.json
PASS  registry 중복 없음: reports/calibration.json
PASS  registry 중복 없음: reports/curve.csv
PASS  registry 중복 없음: reports/eval.md
WARN  registry 에 다른 패키지로 이미 있음: metrics.json → | 모듈 | 이름→팩토리 방식 표(`RESOLVERS`·`register`·`get_resolver`
PASS  registry 중복 없음: reports/failure_cases.md
PASS  registry 중복 없음: tests/test_eval_runner.py
PASS  registry 중복 없음: tests/test_eval_metrics.py
PASS  registry 중복 없음: tests/test_eval_calibration.py
PASS  registry 중복 없음: tests/test_eval_curve.py
PASS  registry 중복 없음: tests/test_eval_report.py
WARN  registry 에 다른 패키지로 이미 있음: metrics.json → | 모듈 | 이름→팩토리 방식 표(`RESOLVERS`·`register`·`get_resolver`
PASS  registry 중복 없음: docs/user-setup/10-pilot-eval-run.md
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
== 결과: FAIL=0 WARN=3 ==
```
FAIL 0. WARN 3 은 §1a 판정 그대로(오탐 1종 ×2·의도된 확장 1) — 조치 없음. 스크립트의 "보류 0건" 은 §2 점검표 8행 기준이며, §3 H-1(결정 K 판정식)은 점검표 밖의 사용자 결정 항목이라 1차 §4 결과는 **보류**였다(2차에서 해소, §3·§4).

### 1c. 2차 — 개정본 기계 검증 (메인 세션 실행, 01-plan 개정 직후)
명령: `bash .claude/scripts/verify-plan.sh P4-pilot-eval | tee docs/wiki/packages/P4-pilot-eval/evidence/20260917-0943-verify-plan.txt`
```
== verify-plan P4-pilot-eval  (2026-09-17 09:43) ==
PASS  존재: docs/wiki/packages/P4-pilot-eval/01-plan.md
PASS  존재: docs/wiki/packages/P4-pilot-eval/02-plan-verify.md
PASS  카드 존재: D10
PASS  카드 존재: D11
PASS  카드 존재: D3
PASS  카드 존재: D4
PASS  카드 존재: D5
PASS  패키지 id 등록됨: P0-cost
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P3-llm-providers
PASS  패키지 id 등록됨: P4-pilot-eval
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R3
PASS  검증 항목 존재: R9
PASS  Refs 있음: - [ ] U1 **러너 골격·격리·적재**: `evaluation/runn
PASS  Refs 있음: - [ ] U2 **지표 계산기**: `evaluation/metrics.py` — �
PASS  Refs 있음: - [ ] U3 **보정표**: `evaluation/calibration.py` → `rep
PASS  Refs 있음: - [ ] U4 **곡선·metrics.json 조립**: `evaluation/curve.
PASS  Refs 있음: - [ ] U5 **리포트 생성기**: `evaluation/report.py` —
PASS  Refs 있음: - [ ] U6 **실행 CLI·dry-run·비용 가드**: `scripts/ru
PASS  Refs 있음: - [ ] U7 **실 공급자 1회 실행**: 임베딩 OpenAI `te
PASS  Refs 있음: - [ ] U8 **실패 케이스 분석**: `reports/failure_cases
PASS  Refs 있음: - [ ] U9 **수용 기준 기계 검증 + 문서**: 전체 `P
PASS  backlog 일치: [eval-agent] **파일럿 평가** (오병합률·미검출�
PASS  의존 완료: P1-pilot-dataset
PASS  의존 완료: P3-baselines
PASS  의존 완료: P3-er
PASS  의존 완료: P3-llm-providers
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: evaluation/runner.py
PASS  registry 중복 없음: evaluation/metrics.py
PASS  registry 중복 없음: evaluation/calibration.py
PASS  registry 중복 없음: evaluation/curve.py
PASS  registry 중복 없음: evaluation/report.py
PASS  registry 중복 없음: reports/metrics.json
PASS  registry 중복 없음: reports/eval.md
PASS  registry 중복 없음: scripts/run_pilot_eval.py
PASS  registry 중복 없음: reports/metrics.json
PASS  registry 중복 없음: reports/calibration.json
PASS  registry 중복 없음: reports/curve.csv
PASS  registry 중복 없음: reports/eval.md
WARN  registry 에 다른 패키지로 이미 있음: metrics.json → | 모듈 | 이름→팩토리 방식 표(`RESOLVERS`·`register`·`get_resolver`
PASS  registry 중복 없음: reports/failure_cases.md
PASS  registry 중복 없음: reports/cost_estimate.md
PASS  registry 중복 없음: tests/test_eval_runner.py
PASS  registry 중복 없음: tests/test_eval_metrics.py
PASS  registry 중복 없음: tests/test_eval_calibration.py
PASS  registry 중복 없음: tests/test_eval_curve.py
PASS  registry 중복 없음: tests/test_eval_report.py
WARN  registry 에 다른 패키지로 이미 있음: metrics.json → | 모듈 | 이름→팩토리 방식 표(`RESOLVERS`·`register`·`get_resolver`
PASS  registry 중복 없음: docs/user-setup/10-pilot-eval-run.md
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
== 결과: FAIL=0 WARN=3 ==
```
1b 대비 차이 1줄: `PASS  registry 중복 없음: reports/cost_estimate.md` 추가(R-1 반영으로 01-plan 125행 "신규(registry 행 예정)" 에 들어감). WARN 3 동일(오탐 ×2·의도된 확장 1, §1a 판정).

### 1d. 2차 최종 실행 (이 문서 갱신 후)
명령: `bash .claude/scripts/verify-plan.sh P4-pilot-eval | tee docs/wiki/packages/P4-pilot-eval/evidence/20260917-0954-verify-plan.txt`
```
== verify-plan P4-pilot-eval  (2026-09-17 09:54) ==
PASS  존재: docs/wiki/packages/P4-pilot-eval/01-plan.md
PASS  존재: docs/wiki/packages/P4-pilot-eval/02-plan-verify.md
PASS  카드 존재: D10
PASS  카드 존재: D11
PASS  카드 존재: D3
PASS  카드 존재: D4
PASS  카드 존재: D5
PASS  패키지 id 등록됨: P0-cost
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P3-llm-providers
PASS  패키지 id 등록됨: P4-pilot-eval
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R3
PASS  검증 항목 존재: R9
PASS  Refs 있음: - [ ] U1 **러너 골격·격리·적재**: `evaluation/runn
PASS  Refs 있음: - [ ] U2 **지표 계산기**: `evaluation/metrics.py` — �
PASS  Refs 있음: - [ ] U3 **보정표**: `evaluation/calibration.py` → `rep
PASS  Refs 있음: - [ ] U4 **곡선·metrics.json 조립**: `evaluation/curve.
PASS  Refs 있음: - [ ] U5 **리포트 생성기**: `evaluation/report.py` —
PASS  Refs 있음: - [ ] U6 **실행 CLI·dry-run·비용 가드**: `scripts/ru
PASS  Refs 있음: - [ ] U7 **실 공급자 1회 실행**: 임베딩 OpenAI `te
PASS  Refs 있음: - [ ] U8 **실패 케이스 분석**: `reports/failure_cases
PASS  Refs 있음: - [ ] U9 **수용 기준 기계 검증 + 문서**: 전체 `P
PASS  backlog 일치: [eval-agent] **파일럿 평가** (오병합률·미검출�
PASS  의존 완료: P1-pilot-dataset
PASS  의존 완료: P3-baselines
PASS  의존 완료: P3-er
PASS  의존 완료: P3-llm-providers
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: evaluation/runner.py
PASS  registry 중복 없음: evaluation/metrics.py
PASS  registry 중복 없음: evaluation/calibration.py
PASS  registry 중복 없음: evaluation/curve.py
PASS  registry 중복 없음: evaluation/report.py
PASS  registry 중복 없음: reports/metrics.json
PASS  registry 중복 없음: reports/eval.md
PASS  registry 중복 없음: scripts/run_pilot_eval.py
PASS  registry 중복 없음: reports/metrics.json
PASS  registry 중복 없음: reports/calibration.json
PASS  registry 중복 없음: reports/curve.csv
PASS  registry 중복 없음: reports/eval.md
WARN  registry 에 다른 패키지로 이미 있음: metrics.json → | 모듈 | 이름→팩토리 방식 표(`RESOLVERS`·`register`·`get_resolver`
PASS  registry 중복 없음: reports/failure_cases.md
PASS  registry 중복 없음: reports/cost_estimate.md
PASS  registry 중복 없음: tests/test_eval_runner.py
PASS  registry 중복 없음: tests/test_eval_metrics.py
PASS  registry 중복 없음: tests/test_eval_calibration.py
PASS  registry 중복 없음: tests/test_eval_curve.py
PASS  registry 중복 없음: tests/test_eval_report.py
WARN  registry 에 다른 패키지로 이미 있음: metrics.json → | 모듈 | 이름→팩토리 방식 표(`RESOLVERS`·`register`·`get_resolver`
PASS  registry 중복 없음: docs/user-setup/10-pilot-eval-run.md
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
== 결과: FAIL=0 WARN=3 ==
```
FAIL 0. §1c 와 동일(WARN 3 = 오탐 ×2·의도된 확장 1, 조치 없음 — §1a·§3d). 새 소견 없음 → `05-remediation.md` 손대지 않음.

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `CLAUDE.md` 원칙7 "의도적으로 제외한 것: 고민 상담, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성 입력, 네이티브 앱" ↔ 01-plan 36행 "하지 않는 것: … **고민 상담·인물 간 관계·감정 대화**(원칙7)". 01-plan 29~36행 "이 패키지에서 하지 않는 것" 7항(150건·운영 임계치·`app/` 수정·골드 라벨·추출 F1·`top_k`/가중치 스윕·프론트/루프) 명시. 산출물(38~59행)은 `evaluation/`·`scripts/`·`tests/`·`reports/`·문서뿐 — 화면·툴·스키마 추가 없음(원칙5 "프론트 화면은 3개로 고정" 무관). 제외 항목을 재는 지표도 없다 |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | 원칙1 `CLAUDE.md` "확신도가 임계치 미만이면 절대 자동 병합하지 말고 ask_user" ↔ 01-plan 10행 "(b) 오병합률과 미검출률을 **분리**해(원칙1 의 비대칭 비용)", 64행 "ask_user 로 간 mention 은 … **제3 범주**". 원칙2 "임계치는 두 개다" ↔ 23행 "`T_new` = 0.3 **고정**"·66행 "`T_new` 불변". 원칙3 "confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule … 보정표(`reports/calibration.json`)" ↔ 65행 U3 보정표·69행 U7 "재계산 abs diff 0". 원칙4 "LLM 단일 호출로 하지 않는다" ↔ 32행 "`app/` 수정 — 고치지 않는다(원칙4 경계)"; `llm_single` 은 평가 대조군일 뿐 제품 경로가 아니다(P3-baselines registry 121행 "베이스라인 3 LLM 단일 프롬프트"). 원칙8 "데이터셋·라벨·베이스라인을 조작하지 않는다. 성능 미달도 결과다" ↔ 26행 "**미달이든 아니든 만든다**", 33행 "골드 라벨 수정·재해석 — 하지 않는다", 83행 (iii) "미달이면 같은 설정으로 재실행한 evidence 가 **없어야 한다**", 101행 `git diff -- app/ data/` 0줄, 234행 "게이트 패키지의 자기검증 유혹" 방어. 원칙9 "모든 판정에는 근거를 남긴다" ↔ 63행 "`trace_id` 를 그대로 보존 … `agent_traces WHERE step='er_resolve'`", 104행 확신도 재계산 표본. 원칙6·7 은 이 패키지 무관(추출·패턴 감지는 P5 이후, 34행). **2차(개정 반영)**: 결정 K (a) 지배 기준(01-plan 226행 "지배 = 그 베이스라인의 오병합률 ≤ 제안 방식 **그리고** 미검출률 ≤ 제안 방식, 둘 중 하나는 엄격히 <")은 원칙1 의 두 축(오병합·미검출)을 그대로 쓰고 자동 병합 규칙에 손대지 않는다; U4 `gate` 는 **한 번 실행한** `metrics.json` 의 수치로만 계산되고(67행 `pass = (dominated_by == []) and d10_direction`) 해석 (ii) "04-review 가 한 번만 내린다"·(iii) "같은 설정으로 재실행한 evidence 가 없어야 한다"(84행) 는 원문 그대로라 원칙8 "설정을 바꿔 다시 돌리기" 금지와 정합. 판정 표 107행이 `t_merge` 출력을 `0.8` 로 고정해 게이트 임계치를 바꿔 통과시키는 길도 없다. U4 Refs 에 원칙1 추가(`evidence/20260917-0950-plan-refs2.txt` 항2) |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `D03-confidence-formula.md` "**보정** `s_llm` 0.1 구간별 실제 정답률 → `reports/calibration.json` (P4)" ↔ 65행 U3 "`s_llm` 0.1 구간 10칸"; "trace `confidence_breakdown{s_llm,s_emb,s_rule,weights,confidence}` 필수" ↔ 69행 재계산. `D04-embedding-provider.md` "**확정** 모델 `text-embedding-3-small`, **N = 1536**" ↔ 25·69행 동일 문자열; "임베딩 호출은 반드시 `EmbeddingProvider` 인터페이스 뒤에" ↔ 19행 `load_scenario_state(…, embedder=…)`(`scenario_state.py` 325행 `as_provider(embedder)`, P3-baselines 04-review U6 (3)). `D05-alias-level-embedding.md` "인물당 대표 벡터를 만들지 않는다" ↔ 19행 "`ScenarioState.embedded_alias_count == alias_count` 를 러너가 단언" (별칭 단위 임베딩을 전제). `D10-two-thresholds.md` "임계치 하나로 구현하지 않는다. 두 값 모두 설정값이며 trace `decision`에 어느 구간이었는지" ↔ 23행 `T_new` 고정·`ERConfig(t_merge=…)` 주입(설정값 3층, `app/er/types.py:287~293` docstring "P4 가 `T_merge ∈ {0.5,…,0.95}` 를 한 프로세스 안에서 스윕"). `D11-llm-provider-registry.md` "`judge_from_env()`·`caller_from_env()` 는 `LLM_PROVIDER` 와 `LLM_PROVIDERS_ENABLED` 를 읽고" / "`app/settings.py` `LLM_PROVIDER = "openai"`" ↔ 63행 "`LLM_PROVIDER=openai` 를 **명시**로 넣고 `LLM_PROVIDERS_ENABLED` 는 넣지 않는다"; "키·프롬프트 원문은 로그·예외·evidence 에 남지 않는다(security §1)" ↔ 25행·201행. 충돌 지점 없음. **주의(R-3)**: 96행 실 실행 명령이 `ANTHROPIC_API_KEY=…` 를 아직 나열 — 결정 A(ii) OpenAI 1벌과 어긋난 잔재(D4 파급 "`ANTHROPIC_API_KEY`(LLM)" 은 D11 이 대체). **2차(개정 반영)**: R-3 해소 — 97행 `LLM_PROVIDER=openai OPENAI_API_KEY=… POSTGRES_PORT=5433 python scripts/run_pilot_eval.py --out reports/pilot/`, `grep -c ANTHROPIC_API_KEY` = 0(`plan-refs2.txt` 항5). 새 `d10_direction`(67행 "제안 방식 곡선에서 `T_merge` 최저→최고 사이 오병합률이 증가하지 않고 `ask_user(identity)` 발생률이 감소하지 않음") ↔ `D10-two-thresholds.md` "**방향** T_merge를 **높이면** 오병합↓ 질문↑. 곡선 x축 = T_merge ∈ {0.5,…,0.95}, T_new 고정" — 같은 방향, 비엄격(≤/≥)이라 40건 평탄 구간을 역방향으로 오판하지 않는다; D10 "코드에서 지켜야 할 것"(임계치 하나 금지·설정값·trace decision)은 게이트 산식이 건드리지 않는다(`T_new` 0.3 고정 유지, 67행). `gate.t_merge: 0.8` = D10 "초기값 `T_merge=0.8`" |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `S3.7-eval-spec.md` "곡선: x = T_merge ∈ {0.5,…,0.95}, T_new=0.3 고정. y = 오병합률·ask_user(identity)율·미검출률" ↔ 23·66행 동일; "산출물: `reports/metrics.json`(원수치), `reports/calibration.json`, `reports/eval.md`(metrics.json만으로 재생성 가능)" ↔ 24·44·67행 "입력은 `metrics.json` **하나뿐**"·100행 diff 0줄; "**P4 미달 시 재시도가 아니라 실패 케이스 분석 산출물 + S3.3 재설계**" ↔ 70·83행. S3.7 지표 목록 중 "추출 F1(`events.type` 고정 집합), 툴 호출 정확도" 는 01-plan 34행이 **범위 밖(P10)** 으로 명시하고 249행 §P10 6 으로 재인계 — S3.7 적용 패키지가 P4·P10 둘 다이므로 분담으로 인정(관찰 O-1). `S3.3-er-pipeline.md` "≥ T_merge → 연결 / [T_new, T_merge) → ask_user(kind="identity") / < T_new → ask_user(kind="new_person")" ↔ 64행 `ask_user_rate_by_kind{identity,new_person,schedule}`; "초기값 T_merge=0.8" ↔ 223행 결정 K "`T_merge=0.8`". `S3.2-tools-v2.md` `search_person (query, hints?) → Candidate[]` 무변경 ↔ 204행 결정 H "`search_person` 시그니처(S3.2)는 변경 금지 대상"; `ask_user` 비동기(D2)는 이 패키지가 호출하지 않는다(`resolve()` 는 부수효과 0, P3-er §7). 시그니처 실재: `evidence/20260917-0922-plan-signatures.txt` — `get_resolver(name, /, **kwargs)`(registry.py:92), `resolve_mention(ctx, mention, utterance, hints=None, *, config=None)`(base.py:186~194), `load_scenario_state(`(scenario_state.py:280)·`embedded_alias_count`(157·166·357행)·`check_schema_version`(210행), `MentionDecision.to_dict`(base.py:147, `trace_id`/`tokens_in`/`tokens_out` 158~160행), `ERConfig`(types.py:287, `t_merge: float = 0.8` 300행·`top_k: int = SEARCH_TOP_K` 305행), `band_for`(confidence.py:82), `select_provider`(judge.py:780), `JUDGES`(judge.py:734), `ER_TRACE_STEP = "er_resolve"`(types.py:29), `caller_from_env`(llm_single.py:624), `detail["band_by_threshold"]`(proposed.py:172·embedding_only.py:214)·`score_clamped`(proposed.py:194·llm_single.py:805)·`raw_decision`(llm_single.py:783) — 01-plan 이 인용한 이름 전부 존재. **2차(개정 반영)**: `metrics.json` 최상위에 `gate{t_merge, proposed, baselines, dominated_by[], d10_direction, pass}` 가 추가됐다(67행). `S3.7-eval-spec.md` "산출물: `reports/metrics.json`(원수치) … `reports/eval.md`(metrics.json만으로 재생성 가능)" 과 충돌 없음 — `gate` 는 같은 파일의 `proposed`/`baselines` 원수치에서 유도되는 블록이고 `eval.md` 는 여전히 `metrics.json` 하나로 재생성된다; S3.7 "P4 미달 시 재시도가 아니라 실패 케이스 분석 산출물 + S3.3 재설계" ↔ 107행 판정 표 "미달(→ U8 + `/devlog change`)". `S3.3-er-pipeline.md` 밴드 3구간·"초기값 T_merge=0.8" ↔ `gate.t_merge: 0.8`. 단 P3-baselines 인계 4 "`RESOLVERS` 이름 = `metrics.json` 키(순서 고정)" 는 `meta` 에 이어 `gate` 도 예약 비-방식 키로 두는 것이므로 U9 스키마 검증이 `meta`·`gate` 를 제외하고 다섯 키를 세는지 04-review 가 본다(O-4) |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `docs/backlog.md` 7행 "**원칙: P4 파일럿 평가 이전에 P5 이후를 시작하지 않는다.**"·61행 "의존: P3, P3-llm-providers"; `docs/wiki/INDEX.md` 80행 "**P4 이전에 P5 이후를 시작하지 않는다.**" ↔ 01-plan 6행 "**이 패키지가 P5 이후의 게이트다**". 선행 04-review: `P1-pilot-dataset/04-review.md` "결과: 완료 … 승인: 사용자 (2026-09-10)", `P3-er/04-review.md` "결과: 완료 / 승인: 사용자 승인 2026-09-06 19:20", `P3-baselines/04-review.md` "결과: 완료 … 승인: 사용자 (2026-09-11)", `P3-llm-providers/04-review.md`(59c67cc 커밋 메시지 "verifier 04-review 완료(수용 11/11·부정 43/43·소견 0)"). 커밋 해시: `evidence/20260917-0922-plan-refs.txt` — 01-plan 5행 인용 13건(701fb8d·f78e9dc·5cac9bf·b3bcc2d·0527ab8·ad394ba·5a1bcbe·c01381d·cf01e9f·7b94a69·10a66c3·59c67cc·3c6108d)과 재사용 표 인용 14건 전부 `git log -1` 실재, `MISSING` 0; `git rev-parse` HEAD=dev=main=origin/main=3c6108d(승격 대기 0, L-001·L-003 대기 상태 없음). 스크립트 "의존 완료" 4건 PASS(§1a). 입력 데이터 실재: `evidence/20260917-0922-validate-scenarios.txt` rc=0·`total` 40·`ambiguous_mention_count` 3·`trap_count` 12·`schema_version` 2 = 01-plan 5·64·70행 전제. 01-plan 이 "P4 통과 여부"를 의존에 넣지 않은 것(6행)도 게이트 정의와 정합 |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `evidence/20260917-0922-plan-refs.txt`: `diff <(sed -n 61p docs/backlog.md \| sed "s/^- \[ \] //") <(sed -n 75p …/01-plan.md \| sed "s/^- //")` → `SAME_AFTER_CHECKBOX_STRIP`(차이는 backlog 체크박스 `[ ] ` 뿐, 스크립트 4번 `grep -F` PASS). 01-plan 77행 "해석(기계 판정 방법, 위 문장을 바꾸지 않는다)" 6항은 판정 명령·기대 출력을 각각 갖는다(78~83행). 단 **결정 K(i) 게이트 판정식은 H-1**(§3) — 수용 기준 문장 자체가 아니라 "미달" 정의의 판정 가능성 문제. **R-2**: 01-plan 5행 "backlog 52~54행"·264행 "52~54행 P4 절"·262행 "INDEX 69행·79행" 은 현재 파일에서 각각 59~61행·70행·80행(backlog 15행 갱신·INDEX 69행 P3-llm-providers 삽입으로 밀림) — 행 번호만 다르고 인용 문장은 일치. **2차(개정 반영)**: 수용 기준 문장 재대조 `diff <(sed -n 61p docs/backlog.md …) <(sed -n 76p …/01-plan.md …)` → `SAME_AFTER_CHECKBOX_STRIP`(`plan-refs2.txt`, 개정으로 1행 밀렸을 뿐 문장 불변). H-1 해소 — 해석 (ii) 의 "결정 K 의 기준" 이 226행 (a) 지배 기준 + 67행 `gate` 산식 + 107행 판정 명령(`0.8 [] True True`)으로 기계 판정 가능해졌고 세 곳 정의가 같다(§3c K 행). R-1 반영 — backlog 15행 "시나리오 1건당 토큰 실측, 150건 × 4방식 × 10임계치 총액 추정" 이 69행 U6 에 `grep -F` 로 글자 그대로 인용되고 106행 판정 표 행(`grep -nE "1건당|150건" reports/cost_estimate.md`)이 붙었다. R-2 반영 — 5행 `59~61행`·6행 `INDEX 80행`·265행 `70행`/`80행`·267행 `59~61행` 과 재사용 표 115~121행 registry 번호(110~113·115·117·119·121·124·106·107·87·123·78~85)가 `sed -n Np docs/wiki/registry.md` 실제 경로와 전부 일치(`plan-refs2.txt` 항4). 잔재 1건: 267행 "backlog 85~93행 리스크 로그" 는 실제 92~98행(항목 94·97행) — 읽은 카드 목록의 위치 표기일 뿐 인용 문장·판정에 영향 없음(R-2 잔재) |
| 7 | 작업 단위마다 Refs 태그 | 통과 | §1a "Refs 있음" U1~U9 9건 PASS. 각 Refs 에 `P4-pilot-eval` 태그 + 카드: U1 `S3.7 D5 D10 원칙8 원칙9`, U2 `S3.7 D10 원칙1 원칙2 원칙8`, U3 `R4 D3 원칙3 원칙9`, U4 `R3 D10 S3.7 원칙2`, U5 `S3.7 원칙8`, U6 `D4 원칙8 L-004`, U7 `R4 R9 D3 D4 D5 원칙3 원칙8 원칙9`, U8 `S3.3 S3.7 원칙1 원칙8`, U9 `S3.7 원칙4 원칙8 원칙9`(01-plan 63~71행). 인용 카드 전부 실재(§1a 카드 존재 D10·D11·D3·D4·D5, 검증 항목 R3·R9; `review-index.md` 12행 R4 "구현완료(b1f2782 … **실호출 미검증**)"·17행 R9 "**실 공급자 호출 미검증**, P4 에서 실측" — U7 이 닫는 대상과 일치). 단위 = 커밋 하나 크기: U1~U5 모듈 1 + 테스트 1, U6 CLI + 카드, U7 실행 산출물 1벌(결정 E), U8 문서 1, U9 검증·registry·README(P3-baselines U8 선례 ad394ba 와 같은 묶음) |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §1 "`.env` … 에이전트가 읽지도 쓰지도 않는다 … `.env.example`에 **이름만**" ↔ 01-plan 45행 "키 없으면 종료 코드 2(이름만 안내, `.env` 미독)"·71행 README "환경변수 **이름**만"·89행 "`.env` 는 읽지 않는다"; §1 "로그·trace에 키·비밀을 남기지 않는다" ↔ 25행 "키는 사용자 셸 환경변수로만 들어가고 저장소·프롬프트·로그·예외에 남지 않는다"·69행 "실행 명령(키 값 없이)"·201행 결정 E "프롬프트 원문·키·응답 원문 중 개인정보·비밀은 넣지 않는다"; §4 "로컬 서버 이외로 데이터 전송 금지 … 외부 API 호출은 코드(SDK)로, 키는 환경변수" ↔ 실 호출은 `judge_from_env`/`OpenAIEmbeddingProvider` SDK 경로만(63·118행); §6 "훅이 막은 명령이 정말 필요하면 우회하지 않고" ↔ 106행 "Docker Desktop 이 꺼져 있거나 키가 없으면 **우회하지 않고** 사용자에게 명령을 보여 주고 멈춘다". 삭제·강제 푸시·DROP 해당 문장 없음(결정 D(i) 롤백은 트랜잭션 rollback 이지 데이터 삭제가 아니다). 시나리오 본문은 `virtual_names` 가상 성명(P1 §7 공통 주의) — 원시 JSONL 커밋(결정 E)에 개인정보 없음 |

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)

### 보류 H-n (사용자 결정 필요 — 이 문서는 고르지 않는다)

- **H-1 → 해소(2차, 사용자 (a) 지배 기준, 2026-09-17; 01-plan 226행 K 행·67행 U4 `gate`·107행 판정 표 행).** 세 곳의 지배 정의 대조(`evidence/20260917-0950-plan-refs2.txt` 항2): 226행 "지배 = 그 베이스라인의 오병합률 ≤ 제안 방식 **그리고** 미검출률 ≤ 제안 방식, 둘 중 하나는 엄격히 <" = 67행 "`dominated_by` 는 `T_merge=0.8` 에서 오병합률 ≤ 제안 방식 **그리고** 미검출률 ≤ 제안 방식이며 둘 중 하나는 엄격히 < 인 베이스라인 목록" = 107행 "`dominated_by` 가 비어 있지 않거나 `d10_direction` 이 False 면 미달". **동률 처리가 같다**: 두 축 모두 동률이면 "하나는 엄격히 <" 가 거짓 → 지배 아님 → `dominated_by` 에 안 들어감 → 통과 쪽. 1차가 지적한 `exact_raw` 오병합 0 케이스는 제안 방식이 오병합 0·미검출이 더 낮으면 미지배(통과), 오병합 0·미검출이 더 높으면 지배(미달) — 방식 품질이 결과를 정한다. 결정 K 원문 문단(210행)은 HEAD 와 diff 0(`K_ORIGINAL_PRESERVED`). 67행 테스트 문장 "`gate` 판정식(동률 4조합·지배 1건·D10 역방향 1건 손 입력)" 이 위 동률 규칙을 검사 대상으로 명시한다. 아래 1차 원문은 기록으로 보존.
- (1차 원문) **H-1 · 결정 K(i) 게이트 판정식이 "제안 방식 오병합률 **<** 베이스라인 3종 최저" 인데, 완전일치 베이스라인의 오병합률이 0 이면 어떤 결과도 통과할 수 없다.** 근거: `evaluation/resolvers/exact_match.py:264~276`(`evidence/20260917-0922-plan-signatures.txt`) — `exact_raw`/`exact_norm` 는 별칭과 문자열이 정확히 일치하는 인물이 **1명일 때만 `merge`**, 2명 이상이면 `identity`, 0명이면 `new_person`. 사전 상태 별칭은 "대화 시작 전 알려진 별칭만 … 공유 호칭(팀장님·주임님·부장님)은 양쪽 다 없다"(`P1-pilot-dataset/04-review.md` §7 2)이므로, 완전일치가 **틀린 인물에 단독 일치**하는 경우는 함정 설계상 거의 없고 40건 표본에서 `false_merge_rate` 가 0 이 될 가능성이 높다(오병합 대신 미검출로 떨어지는 방식). 그러면 결정 K(i)의 첫 조건 "베이스라인 최저(=0)보다 낮다" 는 제안 방식이 오병합 0 이어도 `0 < 0` 이 거짓이라 **미달**이 되고, 01-plan 83행 (ii)·223행에 따라 P5 미착수 + S3.3 재설계 후보로 간다 — 판정식이 방식의 좋고 나쁨과 무관하게 결과를 정한다(원칙8 "재현 가능한 수치"의 취지와 반대). 기획서·S3.7 에 절대 수치가 없어 상대 기준을 택한 이유(207행)는 타당하나, 비교 대상에 "오병합을 구조적으로 거의 내지 않는 대신 미검출이 큰" 방식이 들어 있으면 단일 부등식으로는 우위를 표현할 수 없다. **선택지**(사용자 결정, 결정 K 개정은 architect·메인 세션이 01-plan 결정 확정 표에 기록): (a) 지배 기준 — "`T_merge=0.8` 에서 어떤 베이스라인도 제안 방식을 (오병합률 ≤ **그리고** 미검출률 ≤, 둘 중 하나는 <) 로 지배하지 않는다" + D10 방향 유지(현 문장의 의도를 살리고 동률 0 을 처리) / (b) 비교 집합 축소 — 오병합률 비교는 `embedding_only`·`llm_single` 두 방식(임계치·LLM 을 실제로 쓰는 대조군)과만, 미검출률 비교는 3종 전부 / (c) 부등호만 `≤` 로 완화(동률 0 통과, 단 `exact_raw` 가 오병합 0·제안 방식이 오병합 >0 이면 여전히 미달 — 그것이 의도라면 유지) / (d) 현 문장 유지(위 결과를 알고 감수). 어느 쪽이든 분자/분모(`{"n","d","rate"}` 형식, 228행)를 함께 적는 조건은 그대로.

### 권고 R-n (보류 아님 — 승인 전 개정 또는 04-review 에서 확인)

**2차 처리 상태(2026-09-17 09:50, `evidence/20260917-0950-plan-refs2.txt`)**:
- R-1 → **반영**(01-plan 52행 산출물 "reports/cost_estimate.md — 40건 실측(…) → 150건 × 5방식 × 10임계치 총액 외삽(결정 B(i), backlog 15행 P0-cost 흡수. 본문에 "4방식 → 5방식(`exact_raw`/`exact_norm` 분리)" 한 줄)", 69행 U6 "**`reports/cost_estimate.md`**(결정 B(i), backlog 15행 "시나리오 1건당 토큰 실측, 150건 × 4방식 × 10임계치 총액 추정" — 문장은 그대로 …) … 1건당 토큰·150건 외삽 총액(USD) 두 수치", 106행 판정 표 "비용 실측·외삽(P0-cost 흡수, 결정 B) | `grep -nE "1건당|150건" reports/cost_estimate.md`", 125행 신규 목록 `cost_estimate.md`; §1c `PASS registry 중복 없음: reports/cost_estimate.md`). backlog 15행 문장 `grep -F` 일치(항3).
- R-2 → **반영**(01-plan 5행 `59~61행`, 6행 `INDEX 80행`, 64행 `registry 124행`, 115~121행 registry 번호 110~113·115·117·119·121·124·106·107·87·123·78~85, 265행 `70행`·`80행`, 267행 `59~61행` — 전부 현재 파일 실제 행과 일치, 항4). 잔재 1건: 267행 "85~93행 리스크 로그" → 실제 92~98행(위치 표기, 판정 무관). 개정 불필요.
- R-3 → **반영**(01-plan 97행 `LLM_PROVIDER=openai OPENAI_API_KEY=… POSTGRES_PORT=5433 python scripts/run_pilot_eval.py --out reports/pilot/` (결정 A(ii) OpenAI 1벌); `grep -c ANTHROPIC_API_KEY` = 0, 항5).
- R-4 → **반영**(01-plan 64행 U1 "결정 D(i) 롤백에서는 **실행 중에 한함**: U7 이 표본을 실행 중에 덤프하고 04-review 는 그 evidence 를 실행 로그와 같은 ts 로 요구한다", 105행 판정 표 "확신도 재계산(표본) | … (결정 D(i) 롤백이므로 **실행 중 덤프**, 실행 로그와 같은 ts)", 항6).
- R-5·R-6 → **유지**(구현 시 참고 — 01-plan 278행 읽은 카드 "R-5(재밴드 시 `embedding_only` 동점 강등 재적용 테스트)·R-6(`meta.model` 은 응답 모델명)은 U1·U3 구현 시 참고", 항7). 04-review 가 `tests/test_eval_runner.py` 동점 단언·`meta.model_configured` 를 본다.
- R-7 → **신규(2차, 개정 불필요 — U4 구현·04-review 확인)**: (1) `d10_direction` 67행 "최저→최고 사이 … 증가하지 않고 … 감소하지 않음" 은 **연속 격자점 쌍 전부**(양 끝점 비교가 아니라)로 구현하고 `tests/test_eval_curve.py` 역방향 케이스가 중간 점 역전으로 False 를 내게 한다 — 결정 C(i) 재밴드(`confidence.py:82~90` `band_for` 가 같은 `confidence` 에 `>=` 비교)라 `proposed` 곡선은 구조상 단조이므로 두 읽기의 결과는 같아야 하고, 다르면 러너 버그다. (2) `gate.t_merge` 조회는 격자를 부동소수로 만들 때 `0.8` 이 `0.8000000000000002` 가 되지 않도록 격자 값을 문자열/`Decimal` 또는 `round(x, 2)` 로 고정한다(판정 표 107행이 출력 `0.8` 을 요구). (3) `gate.baselines` 키 집합 = `RESOLVERS` − `proposed` = `{exact_raw, exact_norm, embedding_only, llm_single}` 4개를 테스트가 단언한다(원문 "베이스라인 3종" 은 5방식 분리 전 표현, 226행 "어떤 베이스라인도" 가 4개 전부를 뜻함).

- **R-1 · `reports/cost_estimate.md` 가 산출물 목록·U6·registry 예정 행에 없다.** 결정 B(i)(01-plan 214행) "U6 이 40건 실측으로 150건을 외삽해 `reports/cost_estimate.md` 를 채워 P0-cost 를 닫는다" 와 `docs/backlog.md` 15행 "**P4-pilot-eval U6 로 흡수** … 완료 판정은 P4 04-review 에서" 가 확정됐는데, 38~59행 산출물·68행 U6 본문·122행 "신규(registry 행 예정)"·91~104행 판정 방법 표 어디에도 `reports/cost_estimate.md` 가 없다(184행 인계 5 각주에만 등장). backlog 15행 수용기준 "시나리오 1건당 토큰 실측, 150건 × 4방식 × 10임계치 총액 추정" 을 04-review 가 기계적으로 판정할 명령도 없다. 개정 시 산출물 1줄·U6 문장 1줄·판정 표 1행("`reports/cost_estimate.md` 존재 + 1건당 토큰·150건 외삽 총액 두 수치") 추가. 개정하지 않아도 04-review 는 결정 B·backlog 15행을 근거로 이 파일을 **필수 산출물**로 본다. 참고: backlog 15행의 "4방식" 은 P3-baselines 에서 5방식(`exact_raw`/`exact_norm` 분리)이 됐다 — 문장은 권위이므로 바꾸지 않고 `cost_estimate.md` 본문이 5방식 기준임을 한 줄 적는다.
- **R-2 · 인용 행 번호 잔재(문장은 일치).** 01-plan 5·264행 "backlog 52~54행" → 실제 59~61행(15행 갱신·P3-llm-providers 절 삽입), 262행 "INDEX 69행·79행" → 70·80행, 재사용 표 111~120행 registry 행 "108~111·113·115·117·119·122·104·105·85·121·76~82" → 실제 110~113·115·117·119·121·124·106·107·87·123·78~85(`evidence/20260917-0922-plan-refs.txt`; 59c67cc D11 행·3c6108d 09 카드 행 삽입으로 +2). 해시(05d90f0·e0812f7·1e1320c·40c36f8·107ace3·0d98e47·02e6f14·b1f2782·593c254·d6e5949·cc5d24f)와 파일명은 전부 일치하므로 판정에 영향 없음. 개정 시 행 번호만 갱신.
- **R-3 · 판정 방법 표 96행 실 실행 명령이 `ANTHROPIC_API_KEY=…` 를 나열.** 결정 A(ii)(213행) "P4 U7 은 `LLM_PROVIDER=openai` + `OPENAI_MODEL` 로만 돈다(임베딩과 키 하나)" 와 63행 "`LLM_PROVIDER=openai` 를 **명시**" 에 맞추면 명령은 `LLM_PROVIDER=openai OPENAI_API_KEY=… POSTGRES_PORT=5433 python scripts/run_pilot_eval.py --out reports/pilot/` 이어야 한다(값은 사용자 셸에만). `docs/user-setup/10-pilot-eval-run.md` 를 쓸 때 이 줄을 기준으로 삼지 않도록 정정.
- **R-4 · 결정 D(i) 롤백 ↔ U1 "trace_id 로 되짚을 수 있게".** 시나리오별 롤백이면 실행 종료 후 `agent_traces` 에 행이 없다(200·231행이 스스로 명시 "실행 중에만 조회 가능"). 04-review 는 U7 의 "실행 중 표본 덤프" evidence(재계산 abs diff 0, 104행)를 **실행 로그와 같은 ts** 로 요구한다. U1 63행 문장에 "(결정 D(i)에서는 실행 중에 한함)" 한 구절을 두면 오독이 없다.
- **R-5 · 결정 C(i) "판정 1회 → 밴드 10벌" 의 전제 확인(코드 근거, 개정 불필요).** `app/er/confidence.py` 에서 `config.t_merge`/`config.t_new` 를 읽는 곳은 `band_for()`(86·88행)와 breakdown 기록(170~171행)뿐이고, 강제 경로(`no_candidates`/`llm_failed`/`no_matched`/`out_of_range_id`, `decide()` 223행 docstring)는 통과 후보 수로 밴드가 정해져 임계치와 무관하며, 완화 재검색은 `run_rule_stage()` 의 엄격 통과 0건 조건(`app/er/rules.py`)이라 역시 임계치 무관 — 따라서 `resolve()` 1회 결과의 `confidence` 에 `band_for(confidence, ERConfig(t_merge=x))` 를 다시 매기는 것은 순수 재계산이다. 단 `embedding_only` 의 동점 강등(P3-baselines 04-review U4 (1) "동점 강등은 `merge` 밴드에서만")은 재밴드 시 **다시 적용**해야 하므로 U1 은 `embedding_only` 를 임계치마다 `resolve_mention()` 재호출(LLM 0, mention 임베딩만)하거나 동점 규칙을 재밴드 함수에 포함해야 한다 — `tests/test_eval_runner.py` 에 "동점 mention 이 모든 임계치에서 `merge` 가 아니다" 단언 1건을 권고. `llm_single` 은 `raw_decision` 이 임계치를 읽지 않으므로 곡선이 평탄한 것이 정상(P3-baselines 01-plan 178행 "네 방식 모두 스윕 가능" 은 인터페이스 약속이지 값이 변한다는 뜻이 아니다) — `eval.md` 한계 절에 한 줄.
- **R-6 · P1 §7 인계 8 의 모델명 예시.** `P1-pilot-dataset/04-review.md` §7 8 은 "OpenAI 판정기(`gpt-4o-mini`)" 를 예시로 적었다. U7 `meta.model` 은 설정 문자열이 아니라 `Judgement.model`(응답이 돌려준 값)이어야 한다는 65행·183행 규칙이 우선 — evidence 에 `OPENAI_MODEL` 설정값과 응답 모델명을 둘 다 적는다(이미 `meta.model_configured` 로 계획됨, 확인용).

### 관찰 O-n (조치 불필요)

- **O-1** · S3.7 지표 "추출 F1·툴 호출 정확도" 는 P10 으로(§2 4행). 04-review 는 `eval.md` 한계 절에 이 분담이 적혀 있는지 본다.
- **O-2** · 01-plan 이 미커밋 상태(`git diff` +26/−11: P3-llm-providers 인계 7항 표·해시 59c67cc·카드 번호 10·pytest 918)다. 승인 커밋에 이 문서·05·evidence 와 함께 들어가야 verify-plan 의 "의존 완료: P3-llm-providers" 근거가 저장소에 남는다(메인 세션 `/commit` 몫).
- **O-3** · 05-remediation 소견 3건은 전부 절차·오탐(§1a 판정) — 코드·카드 변경 없음.
- **O-4**(2차) · `metrics.json` 최상위 비-방식 키가 `meta`·`gate` 2개가 됐다(01-plan 67행). U9 스키마 검증·`tests/test_eval_curve.py` "방식 키 5개와 순서" 가 두 키를 제외하고 세는지, 04-review 가 `gate` 를 같은 파일의 `proposed`/`baselines` 수치로 **독립 재계산**해 `pass` 와 일치하는지 본다(게이트 판정을 U4 코드 한 곳이 자기 보고하는 구조이므로 재계산이 증거다).
- **O-5**(2차) · 지배 기준은 두 축을 대칭으로 본다 — 제안 방식이 모든 베이스라인보다 오병합률이 높아도 미검출률이 가장 낮으면 미지배(통과)가 가능하다. 사용자가 (a) 를 이 정의 그대로 골랐으므로 결정 사항이며 보류가 아니다. 다만 원칙1(오병합 ≫ 미검출)을 독자가 판단할 수 있게 `eval.md`·`failure_cases.md` 가 `T_merge=0.8` 오병합률 순위표(5방식, 분자/분모 포함)를 게이트 결과 옆에 적는지 04-review 가 본다.
- **O-6**(2차) · 이 문서 1차 본문(§2·§3 R-n·§3b·§3c)의 01-plan 행 번호는 09:30 작업본 기준이다. 09-17 개정이 52행(+1)·106~107행(+2)·278행(+1)을 삽입했으므로 현재 파일 행 = 09:30 행 + (≤51: 0 / 52~104: +1 / 105~274: +3 / ≥275: +4). 예: 96→97(R-3), 104→105(R-4), 223→226(K 행), 264→267, 262→265(`plan-refs2.txt` 마지막 블록).

## 3b. 인계 항목 대장 대조 (01-plan 124~191행 ↔ 원천 §7)

원천의 항목 하나 = 행 하나. O = 01-plan 대장에 있고 처리 U/결정이 원천 문장과 맞음, X = 빠짐 또는 처리가 어긋남.

| 원천 | # | 원천 문장(요지) | 01-plan 처리 | 대조 |
|---|---|---|---|---|
| P3-baselines 04-review §7 | 1 | DB 초기화·반복 실행 | U1 + 결정 D | O |
| 〃 | 2 | 분모 규칙 3종 | U2 `meta.denominator_rule` | O |
| 〃 | 3 | 지표·곡선·보정표·`ERConfig(t_merge)`·`top_k` 미스윕 | U2·U3·U4 + 결정 H | O |
| 〃 | 4 | `RESOLVERS` 이름 = `metrics.json` 키(순서 고정) | U4 작성·U9 검증 | O |
| 〃 | 5 | 판정 모델별 재기록(`detail["provider"\|"model"]`) | U3·U7 | O |
| 〃 | 6 | 실 임베딩·실 LLM 은 P4 가 처음 | U6·U7 | O |
| 〃 | 7 | trace 증분 실측(+2/+1/0) | U1(단일 출처)·U7 전제 | O |
| 〃 | 8 | `embedder=` 명시 + `embedded_alias_count == alias_count` | U1 즉시 실패 | O |
| 〃 | 9 | 두 번 적재 두 벌 → 롤백/`user_id` | U1 + 결정 D | O |
| 〃 | 10 | `hints` 다섯 방식 같은 값·기본 `None` | U1 호출 스파이 | O |
| 〃 | 11 | `forced_reason` 한 자리 하나·`score_clamped` 규칙 | U2·U3 | O |
| 〃 | 12 | 비용(`prompt_chars`·`person_count`) | U6 + 결정 B | O |
| 〃 | 13 | 스모크 08 결과를 P4 evidence 로 | U6 + 결정 I | O |
| 〃 | 14 | `score` 같은 축 금지 | U2·U4 | O |
| 〃 | 15 | 40건은 방향·유형만 | U8 + 범위 | O |
| P3-baselines 04-review §6 | 권고 2 | `score_clamped` 보정표 제외/별도 표시 | U3 `excluded_clamped` | O |
| 〃 | 권고 6 | 사용자 스모크 08, P4 착수 전 1회 | 결정 I + U6 | O |
| P3-baselines 01-plan 178~183행 | 1~6 | §7 1~6 과 동일 문장(§7 이 "그대로 유효" 라 명시) | 위 1~6 | O |
| P1-pilot-dataset 04-review §7 | 1 | DB 초기화(가상 성명 재등장) | U1 | O |
| 〃 | 2 | 사전 상태 = `seed_persons`+`aliases` 그대로 | U1 `scenario_state` 재사용 | O |
| 〃 | 3 | `ambiguous: true` 3건 제외 | U2 | O |
| 〃 | 4 | `passing_mentions` 6개 = 오탐 분자 | U2 | O |
| 〃 | 5 | `expected_ask_user.allowed` 허용 집합 | U2 | O |
| 〃 | 6 | ask_user 제3 범주 + `ask_user_rate_by_kind` | U2 | O |
| 〃 | 7 | 이벤트 F1 클래스별 보고 | **범위 밖(의도) → §P10 6 재인계** | O (빠짐이 아니라 명시적 이관 — 34·158·249행) |
| 〃 | 8 | `manifest.generator` 판정 모델별 재기록 | U7 evidence `meta` | O (R-6) |
| 〃 | 9 | 라벨 재해석 금지 | U8·U9 | O |
| 〃 | 10 | `schema_version` 2 계약 | U1 `check_schema_version()` + 리스크 233행 | O |
| 〃 | 11 | 40건 방향만, 운영 임계치 P10 | U8 + 범위 | O |
| 〃 | 12 | F-251dc2·F-bdd6c5 는 P4 01-plan 이 결정 | 결정 G·H | O |
| 〃 | 13 | 함정 12건 되돌리지 않음 | U8 `by_trap_kind` | O |
| P3-er 04-review §7 P4 절 | a | 재계산 입력 계약(`step='er_resolve' AND tool_name='er'`) | U1·U7·U9 | O |
| 〃 | b | 공급자별 보정표·`llm.error` 6종·`llm.skipped` | U3 | O |
| 〃 | c | `config=ERConfig(t_merge=…)`·`band_by_threshold`·`forced_reason` 별도 | U2·U4 | O |
| 〃 | d | 리스크 계측(`rule_checked==0`·`relaxed_retry`·`derive_hints` 빈 dict) | U2·U8 | O |
| 〃 | e | 실 임베딩·실 LLM 은 P4 가 처음(R4·R9) | U7 | O |
| 〃 | f | 실 스모크 명령(사용자 실행, 03 카드) | 결정 I(03·08 선행) | O |
| P3-er 05-remediation | F-251dc2 | `_to_scored` 확장 또는 불필요 명시 | 결정 G (b) 불필요 명시, `app/` 무수정 | O (해결 단계 1 (b) 문장 = 190행) |
| 〃 | F-bdd6c5 | `top_k` 스윕 금지 또는 `search_person` 확장 | 결정 H 스윕 금지 + `meta.top_k_swept:false` | O (해결 단계 1 전반부 = 191행) |
| P3-llm-providers 04-review §7 | 1 | `LLM_PROVIDER=openai` 명시·`meta` 출처 `JUDGES` | U1·U4·U7 | O |
| 〃 | 2 | Gemini 0/3, 기본 안 돈다 | 결정 A 그대로, §P10 9 | O |
| 〃 | 3 | 재시도 비대칭 각주 | U2 각주 | O |
| 〃 | 4 | `Judgement.model` = `model_version` 우선 | U3 `meta.model_configured` | O |
| 〃 | 5 | 토큰 필드(Gemini) | U6 각주(`cost_estimate.md`) | O (파일 자체는 R-1) |
| 〃 | 6 | 전 mention `api_error` 면 공급자 층 | U7 + 오류율 5% 규칙 | O |
| 〃 | 7 | 닫는 커밋 해시를 5행에 | 5행 `59c67cc` | O (`git log -1 59c67cc` 실재) |
| P3-llm-providers 01-plan 131~136행 | 1~4 | 의존 줄 해시 / `meta.provider` 값 집합 / 결정 A 재확인 / 보정표 그룹 키 | 5행 / 82행·인계 1 / 213행 / U3 | O |

X 항목 0. 원천 §6 의 다른 권고(P3-baselines 1·4·5·7·8, P3-llm-providers 1·2·3·5·7·8)는 P4 대상이 아니다(닫는 커밋·하네스 몫으로 원천이 명시).

## 3c. 결정 A~K 정합 (01-plan 197~223행)

| 결정 | 확정 | 계획 본문 반영 | 카드·원칙 정합 | 판정 |
|---|---|---|---|---|
| A 공급자 | (ii) OpenAI 1벌 + Gemini 소패키지 선행 | 5행 의존(59c67cc)·25·63·69행 | D11 "`LLM_PROVIDER = "openai"`"; D3 "공식은 공급자와 무관" | 정합 (R-3 96행 잔재) |
| B 비용 상한·P0-cost 흡수 | (i) U6 실측→150건 외삽, `--max-cost-usd` $5 | 68행 상한·backlog 15행 갱신됨 | `CLAUDE.md` "AWS Budgets $10/$30/$50" 의 절반; 원칙8 | 정합 (R-1 산출물 누락) |
| C 스윕·반복 | (i) LLM 1회→밴드 10벌 | 63행 U1 구조 | D10 "두 값 모두 설정값"; `confidence.py` 임계치 사용처 = `band_for` 뿐 | 정합 (R-5 동점 강등 재적용) |
| D 격리 | (i) 시나리오별 롤백 | 63행 증분 0 단언·231행 | security §3 삭제 아님; 원칙9 는 실행 중 덤프로 | 정합 (R-4) |
| E `reports/` 커밋 | (i) 원시 JSONL 포함 전부 | 46~51행 | 원칙8 재현; security §1 비밀 없음 | 정합 |
| F `s_llm` 정답 | (i) `decision`+`person_id` 골드 일치 | 65행 U3 | D3 보정표 정의; 오병합률 분모와 동일 | 정합 |
| G F-251dc2 | (i) 불필요 명시, `app/` 무수정 | 190행 (i)~(iv) | 원칙4·원칙8(게이트가 대상 코드 불변경); F-251dc2 해결 단계 (b) | 정합 |
| H F-bdd6c5 | (i) `top_k` 미스윕, `meta.top_k_swept:false` | 23·66·191행 | S3.2 `search_person` 무변경; F-bdd6c5 해결 단계 전반부 | 정합 |
| I 스모크 선행 | (i) U6 전 03·08 사용자 1회 | 68·117행 | P3-baselines 권고 6; P3-er F-87c597; L-004(사용자 실행) | 정합 |
| J 곡선 형식 | (i) `curve.csv` + Markdown 표 | 49·66·67행 | S3.7 "metrics.json 만으로 재생성"; 의존성 0 | 정합 |
| K 게이트 기준 | (1차) (i) 상대 기준(오병합 < 최저, 미검출 ≤ 최고, D10 방향) → **(2차) (i) → 개정 (a) 지배 기준**(사용자 2026-09-17): `T_merge=0.8` 에서 어떤 베이스라인도 제안 방식을 지배하지 않는다(오병합률 ≤ 그리고 미검출률 ≤, 하나는 엄격히 <) 그리고 곡선 D10 방향 | 226행 K 행(개정 사유 `exact_match.py:264~276` 인용 = 1차 H-1 근거와 동일) · 67행 U4 `gate{t_merge:0.8, proposed, baselines, dominated_by[], d10_direction, pass}` + `pass = (dominated_by == []) and d10_direction` + `test_eval_curve.py` "동률 4조합·지배 1건·D10 역방향 1건" · 107행 판정 표 `0.8 [] True True` · 84행 해석 (ii) "결정 K 의 기준으로 04-review 가 한 번만" (원문 불변) · 210행 결정 K 원문 보존(`K_ORIGINAL_PRESERVED`) | 원칙1 두 축 유지·자동 병합 규칙 무관; 원칙8 단일 실행 수치로만 판정, 재실행 금지 (iii) 유지; S3.7 "미달 시 재시도가 아니라 실패 케이스 분석 + S3.3 재설계" ↔ 107행 "미달(→ U8 + `/devlog change`)"; D10 "높이면 오병합↓ 질문↑" ↔ `d10_direction` 비엄격 단조. **세 곳 정의 동일, 동률 = 미지배 = 통과 쪽.** 잔여는 구현 정밀도(R-7: 연속 쌍 단조·격자 0.8 정확 표현·baselines 4키)와 04-review 독립 재계산(O-4) | **정합 (H-1 해소)** |

## 3d. 05-remediation 소견 3건 처리

| F-id | 등급 | 판정 | 조치 |
|---|---|---|---|
| F-0e133a 02-plan-verify 없음 | 필수 | 이 문서로 해소 | §1b 재실행 FAIL 0 으로 닫음 |
| F-95c6a7 registry `metrics.json` 기존 행(×2) | 권고 | 오탐 — registry 112행 비고 문구 basename 일치 | 조치 없음, WARN 잔존(스크립트 한계, 사유 §1a) |
| F-0ffff5 registry `README.md` 기존 행 | 권고 | 의도된 확장(01-plan 59·120행) | 조치 없음, WARN 잔존. 04-review 가 registry 33행 비고 확인 |

## 4. 결정
1차(2026-09-17 09:30): 보류 — H-1(결정 K(i) 판정식의 동률·0 처리) 사용자 결정 후 01-plan 결정 확정 표 개정 → 이 문서 §3c K 행 갱신 → 승인. R-1~R-4 는 같은 개정에 같이 넣기를 권고(별도 재검증 불필요, 행 번호·문장 수준). 기계 검증은 §1b(FAIL 0·WARN 3 오탐/의도).

결과: 통과 — **2차 재검증 2026-09-17 09:50**. 근거: H-1 해소(사용자 (a) 지배 기준, 01-plan 226행; U4 67행 `gate` 산식·107행 판정 명령과 세 곳 정의 동일, 동률 = 미지배 = 통과 쪽 — §3 H-1·§3c K 행, `evidence/20260917-0950-plan-refs2.txt`), R-1~R-4 반영(01-plan 52·69·106·125행 / 5·6·64·115~121·265·267행 / 97행 / 64·105행), R-5·R-6 은 구현 시 참고로 01-plan 278행에 기록, 새 보류 없음(R-7·O-4~O-6 은 구현·04-review 확인 사항). 기계 검증 §1c(0943, FAIL 0·WARN 3 = 1차와 같은 오탐/의도)·§1d(최종). 점검표 8행 전부 통과. 승인 커밋에는 01-plan 개정본·이 문서·05-remediation·evidence 7파일이 함께 들어가야 한다(O-2).
승인: 사용자 (2026-09-18)
