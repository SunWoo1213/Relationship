# P4b-er-redesign · 계획 검증 (02-plan-verify)

대상: 01-plan.md | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002)

검증 입력: `01-plan.md`(architect 초안 + 메인 세션 형식 2건·"## 결정" 표·`ER_PENALIZED_MERGE_POLICY` 치환), 사용자 확정 결정 A(i)·B(i)·C(i)·D(i)·E(i)·F(i)·G(i)·H(i)·I(i), backlog 개정 (2) 반영·(1) 거절. 선행 커밋: `bash .claude/scripts/gitlog.sh P4b-er-redesign CR-001` → dev HEAD `e4109cc`(CR-001 이행완료 = 시작 해시), `adf9f1b`(P4 부분완료), 미커밋 `docs/backlog.md`·`docs/wiki/changes/CR-001.md`·`HANDOFF.md`·`journal.md` + `packages/P4b-er-redesign/`(신규).

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)

### 1a. 1차 (02-plan-verify 작성 전)
명령: `bash .claude/scripts/verify-plan.sh P4b-er-redesign | tee docs/wiki/packages/P4b-er-redesign/evidence/20260922-1710-verify-plan-review.txt`
```
== verify-plan P4b-er-redesign  (2026-09-22 17:10) ==
PASS  존재: docs/wiki/packages/P4b-er-redesign/01-plan.md
FAIL  없음: docs/wiki/packages/P4b-er-redesign/02-plan-verify.md
PASS  카드 존재: D10
PASS  카드 존재: D12
PASS  카드 존재: D13
PASS  카드 존재: D3
PASS  카드 존재: D4
PASS  카드 존재: D5
PASS  패키지 id 등록됨: P3-er
PASS  검증 항목 존재: R3
PASS  검증 항목 존재: R4
PASS  Refs 있음: - [ ] U0 **[메인 세션] 스킬 카드 정합 (U1 착수 �
PASS  Refs 있음: - [ ] U1 **[backend-agent] D12 — 관측 신호 재정규�
PASS  Refs 있음: - [ ] U2 **[backend-agent] D13 — 규칙 필터는 감점**
PASS  Refs 있음: - [ ] U3 **[backend-agent] 파이프라인·보수 분기·�
PASS  Refs 있음: - [ ] U4 **[eval-agent] 평가 도구 정합 + 전체 회귀
PASS  Refs 있음: - [ ] U5 **[eval-agent 준비 → 사용자 실행] dry-run 
PASS  Refs 있음: - [ ] U6 **[eval-agent] P4 기준선 대비 실패 케이스
PASS  Refs 있음: - [ ] U7 **[eval-agent] 수용 기준 기계 검증 + 문서
PASS  backlog 일치: [ ] [backend-agent + eval-agent] **ER 재설계 후 파일�
WARN  registry 에 다른 패키지로 이미 있음: app/er/confidence.py → | 모듈 | 확신도·두 임계치(4단계, 순수 함수) | app/er/confidence.
| 스크립트 | 파일럿 평가 실행 CLI(예상 비용 → 가드 → runner
WARN  registry 에 다른 패키지로 이미 있음: app/er/rules.py → | 모듈 | 규칙 필터(2단계, 순수 함수) | app/er/rules.py | P3-er | 02e
WARN  registry 에 다른 패키지로 이미 있음: app/er/pipeline.py → | 모듈 | ER 오케스트레이션(resolve/apply_resolution) | app/er/pipeline.
WARN  registry 에 다른 패키지로 이미 있음: app/er/types.py → | 모듈 | ER 공용 타입 | app/er/types.py | P3-er | cc5d24f | `ScoredCandida
PASS  registry 중복 없음: ScoredCandidate.penal
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
WARN  registry 에 다른 패키지로 이미 있음: scripts/run_pilot_eval.py → | 스크립트 | 파일럿 평가 실행 CLI(예상 비용 → 가드 → runner
WARN  registry 에 다른 패키지로 이미 있음: evaluation/curve.py → | 모듈 | 파일럿 평가 지표 계산기(U1 JSONL → 방식 × `T_merge` �
| 모듈 | 곡선(`T_merge` 10점 × 3계열 × 5방식)·`metrics.json` 조립�
PASS  registry 중복 없음: meta.weigh
PASS  registry 중복 없음: meta.penal
WARN  registry 에 다른 패키지로 이미 있음: evaluation/metrics.py → | 모듈 | 파일럿 평가 지표 계산기(U1 JSONL → 방식 × `T_merge` �
WARN  registry 에 다른 패키지로 이미 있음: evaluation/calibration.py → | 모듈 | 보정표 작성기(U1 JSONL → `s_llm` 구간별 실제 정답률 =
WARN  registry 에 다른 패키지로 이미 있음: evaluation/resolvers/proposed.py → | 모듈 | 제안 4단계 하이브리드 어댑터(`app.er.resolve` -> `Mention
WARN  registry 에 다른 패키지로 이미 있음: tests/test_er_confidence.py → | 테스트 | 확신도 가중합·경계값·임계치 스윕 | tests/test_er_c
WARN  registry 에 다른 패키지로 이미 있음: test_er_rules.py → | 테스트 | 규칙 필터 배제·완화 재평가·s_rule 분모 | tests/test
WARN  registry 에 다른 패키지로 이미 있음: test_er_pipeline.py → | 테스트 | ER 파이프라인 회귀(승진·이모 배제·동명이인)·tr
WARN  registry 에 다른 패키지로 이미 있음: test_run_pilot_eval.py → | 테스트 | 실행 CLI 순수 층(지문·run_id·비용 추정·환경변수 
WARN  registry 에 다른 패키지로 이미 있음: .jsonl.gz → | 모듈 | 파일럿 평가 지표 계산기(U1 JSONL → 방식 × `T_merge` �
| 스크립트 | 파일럿 평가 실행 CLI(예상 비용 → 가드 → runner
| 데이터 | 원시 판정 JSONL(gzip, 실 실행 40건·7050행, 결정 E) | r
| 리포트 | 실패 케이스 분석(오병합·미검출 전건, 강제 경로
| 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
WARN  registry 에 다른 패키지로 이미 있음: reports/metrics.json → | 리포트 | 파일럿 지표(5방식 × 10임계치 · 게이트 판정) | rep
WARN  registry 에 다른 패키지로 이미 있음: calibration.json → | 모듈 | 보정표 작성기(U1 JSONL → `s_llm` 구간별 실제 정답률 =
| 리포트 | 보정표(`s_llm` 10구간 실제 정답률, 실 실행) | reports
| 리포트 | 실패 케이스 분석(오병합·미검출 전건, 강제 경로
WARN  registry 에 다른 패키지로 이미 있음: curve.csv → | 모듈 | 곡선(`T_merge` 10점 × 3계열 × 5방식)·`metrics.json` 조립�
| 테스트 | 곡선 격자·`T_new` 불변·방식 5키 순서·게이트 판�
| 모듈 | 리포트 생성기(`metrics.json` → `reports/eval.md` — 표·곡
| 테스트 | `eval.md` 바이트 재현성·입력에 없는 수치 금지(숫�
| 리포트 | 트레이드오프 곡선(T_merge 10점 × 3계열 × 5방식) | r
WARN  registry 에 다른 패키지로 이미 있음: eval.md → | 모듈 | 리포트 생성기(`metrics.json` → `reports/eval.md` — 표·곡
| 테스트 | `eval.md` 바이트 재현성·입력에 없는 수치 금지(숫�
| 리포트 | 파일럿 평가 리포트(metrics.json 단일 입력, 멱등) | r
WARN  registry 에 다른 패키지로 이미 있음: reports/failure_cases.md → | 리포트 | 실패 케이스 분석(오병합·미검출 전건, 강제 경로
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
| 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
WARN  registry 에 다른 패키지로 이미 있음: docs/user-setup/10-pilot-eval-run.md → | 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
PASS  registry 중복 없음: .claude/skills/entity-resolution/SKILL.md
== 결과: FAIL=1 WARN=22 ==
```
FAIL 1 = 이 문서(02-plan-verify.md) 부재. 2차 실행(1b)에서 사라져야 한다.

**WARN 22 판정 — 의도된 경고(기존 파일 확장 패키지).** 22건 전부 스크립트 7번 "산출물 경로가 registry 에 다른 패키지로 있음"이다. (i) `app/er/*` 4·`app/settings.py`·`scripts/run_pilot_eval.py`·`evaluation/*` 4·`tests/*` 4·`reports/*` 2·문서 2 = 18건은 01-plan 이 **수정**을 선언한 기존 파일이다 — 01-plan 26행 "`docs/wiki/registry.md` 행(수정 파일은 비고 확장)", 67행 "수정한 기존 행(81·82·85행 `app/er/*`)은 비고에 D12·D13 한 줄과 새 커밋 해시를 더하고(새 행을 만들지 않는다, F-0ffff5·F-95c6a7 선례)", 115~127행 재사용 표가 각 행을 "수정 / 무수정 / 갱신해 재사용"으로 분류했다. (ii) `.jsonl.gz`·`calibration.json`·`curve.csv`·`eval.md` 4건은 산출물 줄의 `reports/pilot/raw-\<새 ts\>.jsonl.gz`·`reports/metrics.json · calibration.json · …` 을 스크립트가 공백으로 쪼개 basename 으로 grep 한 오탐 — P4 04-review 230행 "`verify-plan.sh` 5번 basename 오탐(F-95c6a7 계열) 관찰 유지"와 같은 계열. 새 산출물 3종(`ScoredCandidate.penalized_by`·`meta.weights_policy`·`meta.penalized_merge_policy`)과 `SKILL.md` 는 "중복 없음" PASS. → 22건은 [권고] 소견으로 05-remediation 에 등록하고 U7 registry 비고 확장 뒤 04-review §5 에서 닫는다(P3-llm-providers·P4 선례).

### 1b. 2차 (02-plan-verify 작성 후)
명령: `bash .claude/scripts/verify-plan.sh P4b-er-redesign | tee docs/wiki/packages/P4b-er-redesign/evidence/20260922-1718-verify-plan-review-2.txt`
```
== verify-plan P4b-er-redesign  (2026-09-22 17:18) ==
PASS  존재: docs/wiki/packages/P4b-er-redesign/01-plan.md
PASS  존재: docs/wiki/packages/P4b-er-redesign/02-plan-verify.md
PASS  카드 존재: D10
PASS  카드 존재: D12
PASS  카드 존재: D13
PASS  카드 존재: D3
PASS  카드 존재: D4
PASS  카드 존재: D5
PASS  패키지 id 등록됨: P3-er
PASS  검증 항목 존재: R3
PASS  검증 항목 존재: R4
PASS  Refs 있음: - [ ] U0 **[메인 세션] 스킬 카드 정합 (U1 착수 �
PASS  Refs 있음: - [ ] U1 **[backend-agent] D12 — 관측 신호 재정규�
PASS  Refs 있음: - [ ] U2 **[backend-agent] D13 — 규칙 필터는 감점**
PASS  Refs 있음: - [ ] U3 **[backend-agent] 파이프라인·보수 분기·�
PASS  Refs 있음: - [ ] U4 **[eval-agent] 평가 도구 정합 + 전체 회귀
PASS  Refs 있음: - [ ] U5 **[eval-agent 준비 → 사용자 실행] dry-run 
PASS  Refs 있음: - [ ] U6 **[eval-agent] P4 기준선 대비 실패 케이스
PASS  Refs 있음: - [ ] U7 **[eval-agent] 수용 기준 기계 검증 + 문서
PASS  backlog 일치: [ ] [backend-agent + eval-agent] **ER 재설계 후 파일�
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
WARN  registry 에 다른 패키지로 이미 있음: app/er/confidence.py → | 모듈 | 확신도·두 임계치(4단계, 순수 함수) | app/er/confidence.
| 스크립트 | 파일럿 평가 실행 CLI(예상 비용 → 가드 → runner
WARN  registry 에 다른 패키지로 이미 있음: app/er/rules.py → | 모듈 | 규칙 필터(2단계, 순수 함수) | app/er/rules.py | P3-er | 02e
WARN  registry 에 다른 패키지로 이미 있음: app/er/pipeline.py → | 모듈 | ER 오케스트레이션(resolve/apply_resolution) | app/er/pipeline.
WARN  registry 에 다른 패키지로 이미 있음: app/er/types.py → | 모듈 | ER 공용 타입 | app/er/types.py | P3-er | cc5d24f | `ScoredCandida
PASS  registry 중복 없음: ScoredCandidate.penal
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
WARN  registry 에 다른 패키지로 이미 있음: scripts/run_pilot_eval.py → | 스크립트 | 파일럿 평가 실행 CLI(예상 비용 → 가드 → runner
WARN  registry 에 다른 패키지로 이미 있음: evaluation/curve.py → | 모듈 | 파일럿 평가 지표 계산기(U1 JSONL → 방식 × `T_merge` �
| 모듈 | 곡선(`T_merge` 10점 × 3계열 × 5방식)·`metrics.json` 조립�
PASS  registry 중복 없음: meta.weigh
PASS  registry 중복 없음: meta.penal
WARN  registry 에 다른 패키지로 이미 있음: evaluation/metrics.py → | 모듈 | 파일럿 평가 지표 계산기(U1 JSONL → 방식 × `T_merge` �
WARN  registry 에 다른 패키지로 이미 있음: evaluation/calibration.py → | 모듈 | 보정표 작성기(U1 JSONL → `s_llm` 구간별 실제 정답률 =
WARN  registry 에 다른 패키지로 이미 있음: evaluation/resolvers/proposed.py → | 모듈 | 제안 4단계 하이브리드 어댑터(`app.er.resolve` -> `Mention
WARN  registry 에 다른 패키지로 이미 있음: tests/test_er_confidence.py → | 테스트 | 확신도 가중합·경계값·임계치 스윕 | tests/test_er_c
WARN  registry 에 다른 패키지로 이미 있음: test_er_rules.py → | 테스트 | 규칙 필터 배제·완화 재평가·s_rule 분모 | tests/test
WARN  registry 에 다른 패키지로 이미 있음: test_er_pipeline.py → | 테스트 | ER 파이프라인 회귀(승진·이모 배제·동명이인)·tr
WARN  registry 에 다른 패키지로 이미 있음: test_run_pilot_eval.py → | 테스트 | 실행 CLI 순수 층(지문·run_id·비용 추정·환경변수 
WARN  registry 에 다른 패키지로 이미 있음: .jsonl.gz → | 모듈 | 파일럿 평가 지표 계산기(U1 JSONL → 방식 × `T_merge` �
| 스크립트 | 파일럿 평가 실행 CLI(예상 비용 → 가드 → runner
| 데이터 | 원시 판정 JSONL(gzip, 실 실행 40건·7050행, 결정 E) | r
| 리포트 | 실패 케이스 분석(오병합·미검출 전건, 강제 경로
| 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
WARN  registry 에 다른 패키지로 이미 있음: reports/metrics.json → | 리포트 | 파일럿 지표(5방식 × 10임계치 · 게이트 판정) | rep
WARN  registry 에 다른 패키지로 이미 있음: calibration.json → | 모듈 | 보정표 작성기(U1 JSONL → `s_llm` 구간별 실제 정답률 =
| 리포트 | 보정표(`s_llm` 10구간 실제 정답률, 실 실행) | reports
| 리포트 | 실패 케이스 분석(오병합·미검출 전건, 강제 경로
WARN  registry 에 다른 패키지로 이미 있음: curve.csv → | 모듈 | 곡선(`T_merge` 10점 × 3계열 × 5방식)·`metrics.json` 조립�
| 테스트 | 곡선 격자·`T_new` 불변·방식 5키 순서·게이트 판�
| 모듈 | 리포트 생성기(`metrics.json` → `reports/eval.md` — 표·곡
| 테스트 | `eval.md` 바이트 재현성·입력에 없는 수치 금지(숫�
| 리포트 | 트레이드오프 곡선(T_merge 10점 × 3계열 × 5방식) | r
WARN  registry 에 다른 패키지로 이미 있음: eval.md → | 모듈 | 리포트 생성기(`metrics.json` → `reports/eval.md` — 표·곡
| 테스트 | `eval.md` 바이트 재현성·입력에 없는 수치 금지(숫�
| 리포트 | 파일럿 평가 리포트(metrics.json 단일 입력, 멱등) | r
WARN  registry 에 다른 패키지로 이미 있음: reports/failure_cases.md → | 리포트 | 실패 케이스 분석(오병합·미검출 전건, 강제 경로
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
| 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
WARN  registry 에 다른 패키지로 이미 있음: docs/user-setup/10-pilot-eval-run.md → | 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
PASS  registry 중복 없음: .claude/skills/entity-resolution/SKILL.md
== 결과: FAIL=0 WARN=22 ==
```
FAIL 0 (1차의 "없음: 02-plan-verify" 소멸). 점검표 검사 6항 전부 PASS(검증자 = verifier · 8행 · 판정 · 보류 0 · 결과 줄 · 근거). WARN 22 는 1a 판정대로 의도된 경고·basename 오탐 — `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python .claude/scripts/findings.py P4b-er-redesign docs/wiki/packages/P4b-er-redesign/evidence/20260922-1718-verify-plan-review-2.txt --source verify-plan` → "새 소견 22, 해소 0, 열림 22 (필수 0)", rc=0. 원인 분석 칸은 verifier 가 채웠고(의도된 기존 파일 확장 18 · basename 오탐 4) 해결 단계·재검증은 U7(registry 비고 확장)·04-review §5 의 몫이다.

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 2장 표(55~62행) 제외 열 "고민 상담 기능 / 인물 간(A–B) 관계 저장 / 관계 태그 필터링 / 상담 페르소나 / 톤 설정 / 음성 입력 / 네이티브 앱" 중 어느 것도 01-plan 산출물(39~54행: `app/er/*` 4·`app/settings.py`·`scripts/run_pilot_eval.py`·`evaluation/*` 5·`tests/*`·`reports/*`·문서)에 없다 — 화면·API·테이블 추가 항목 0. `changes/CR-001.md` §1 "범위(기획서 2장 표)는 움직이지 않는다 — 포함/제외 칸 변화 없음". 01-plan 28행 "S3.3 4단계 구조·툴 시그니처 v2·스키마 v2 변경 없음(원칙4). … `search_person` 시그니처·`ERConfig.top_k` 주입은 손대지 않는다"; 판정 표 19행 `alembic check` → "No new upgrade operations detected." · `tools_check.py` → `7/7 ok`. `docs/proposal.md` 15행 상단 확정 "확신도 결합 산식은 관측된 신호만 재정규화하고, 규칙 필터는 배제가 아니라 감점으로 확정(CR-001 · D12·D13)" — 본문 무수정 |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | **원칙1** `decisions/D13-rule-filter-penalty.md` 8행 "기본 권장안: 강등 — 후보가 늘어 오병합 기회가 늘어나는 위험을 40건으로 검증할 수 없기 때문" ↔ 01-plan 결정 A(i) "`ask` 강등(`forced_reason="penalized_candidate"`)" — 보수 방향 일치. `relaxed_pass` 예외는 `specs/S3.3-er-pipeline.md` 15행 "인접 위계까지 허용으로 완화한 재검색 1회"가 P3-er 부터 자동 연결하던 경로(`tests/test_er_pipeline.py` 444행 `assert result.band == "merge"`, 본 검증 실행 `3 passed`)라 새 완화가 아니다. **원칙2** `decisions/D10-two-thresholds.md` 6~9행 세 구간 그대로, 01-plan 31행 "`T_merge`/`T_new` 운영값 재설정 — … 40건으로 튜닝하지 않는다", `app/er/types.py` 300~301행 `t_merge=0.8·t_new=0.3` 무수정. **원칙3** `CLAUDE.md` 38행 "`confidence = Σ w_i·s_i / Σ w_i` — 관측된 신호만 결합하며 … `s_rule` 이 미측정(`rule_checked=0`)이면 0 으로 넣지 않고 분모에서 뺀다(`0.625·s_llm + 0.375·s_emb`). 2단계 규칙 충돌은 후보 배제가 아니라 `s_rule` 감점이다(D13)" = `D12` 6~8행 = 01-plan 20행 "`0.625·s_llm + 0.375·s_emb`, 세 신호가 모두 관측되면 D3 원식과 부동소수까지 같은 값". **원칙4** 01-plan 28행 "단계를 합치거나 LLM 단일 호출로 대체하지 않는다"; U3 63행 `_run_pipeline` 4단계 순서 유지. **원칙8** 01-plan 24행 "재실행 1회", 29행 "`data/` 무수정", 30행 "P4 기준선 덮어쓰기 금지", 35행 "재실행 반복 — … 가장 흔한 위반", 결정 E(i) "실 실행 1회, 미달 시 재실행 금지"; `specs/S3.7-eval-spec.md` 10행 "P4 미달 시 재시도가 아니라 실패 케이스 분석 산출물"; 판정 표 16·17·21행. **원칙9** 01-plan 20행 "`weights`(설정값)·`weights_effective`(적용된 정규화 가중치)·`rule_checked` 를 모두 기록", 21행 "`penalized_by` 로 표시", 63행 "강등은 판정 기록을 덮어쓰지 않고 별도 필드(`forced_reason`·`band_by_threshold`)로". 원칙5·6·7 은 손대는 항목 없음(1행) |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `D12` 23~27행 4항 ↔ U1(61행): "`rule_checked`(또는 `s_rule is None`)를 입력으로 받아 미측정이면 `(w_llm·s_llm + w_emb·s_emb) / (w_llm + w_emb)`", "abs diff == 0(무작위 표본 단언)", "`weights`·`weights_effective`·`rule_checked`·`rule_passed` 를 모두 남긴다", "`rule_checked > 0`·`rule_passed == 0` 은 여전히 `s_rule = 0` 으로 합산", 회귀 3종(63행) — 4항 전부 문장으로 있음. `D13` 21~25행 4항 ↔ U2(62행) "`excluded_by` 에는 `dictionary_conflict` 만 등장", "3단계에 전달되는 후보 수 == 1단계 후보 수 − `dictionary_conflict` 후보 수"; U3·결정 B(i) `ER_PENALIZED_MERGE_POLICY`(D13 24행 예시 이름 그대로) "설정값 하나로 켜고 끈다 … trace 에 적용 여부"; 수용 기준 72행 "`sc-015` 오병합·`sc-007` 미검출 아님". 결정 C(i) 트리거 변경은 `D13` 17행 "완화 재검색 167행 재검토 — 배제가 없어지면 재검색의 의미가 줄어드는지 01-plan 이 결정"의 위임 범위 안이고 `D13` 7행 "완화 재검색(승진 인접 위계) 규약은 유지"(1회·trace 기록)를 지킨다. `D10` 13행 "임계치 하나로 구현하지 않는다 … trace `decision`에 어느 구간이었는지" ↔ 63행 `band_by_threshold`(순수 산식 밴드) 유지. `D03` 3행 "상태: 대체됨(→D12, CR-001)" — 01-plan 은 D3 를 "원식과 동치" 비교 기준으로만 인용(20·61행), U0 이 `.claude/skills/entity-resolution/SKILL.md` 의 잔존 D3 문장(22·36·39행, 본 검증 grep 에서 D12/D13/CR-001 언급 0건)을 고친다 |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `specs/S3.3-er-pipeline.md` 7행 "(D13: 관계 태그·위계 충돌은 감점·후보 유지, 사전 모순만 제외)" ↔ 01-plan 21행 "`dictionary_conflict` 배제와 후보 0명의 `no_candidates` 강제 경로는 종전 그대로"; 9행 "`confidence = Σ w_i·s_i / Σ w_i` (관측 신호만 … `s_rule` 미측정이면 `0.625·s_llm + 0.375·s_emb`)" ↔ 20행; 18행 "회귀 테스트 필수: 승진 … 팀장↔이모 배제, 동명이인 분리. D13 이후에도 셋 다 유지" ↔ 63행 (a)(b)(c) + 판정 표 2행 `3 passed`. 임계치 2개: S3.3 10~12행 3분기 문장 무변경, `ERConfig` 필드 추가는 정책값 하나(42행)뿐. ask_user 비동기: 강등은 `band="identity"` 로 기존 `apply_resolution` 경로(`registry.md` 85행 "identity/new_person→`ask_user`, 같은 trace 행의 `applied`/`pending_question_id`/`applied_at` 3필드만 부분 갱신")를 타며 `pending_questions`·`POST /answers` 를 바꾸는 단위 없음. 시그니처 v2: 28행 "`search_person` 시그니처 … 손대지 않는다", 판정 표 19행 `tools_check.py 7/7`. `specs/S3.7-eval-spec.md` 6~9행 지표·곡선·산출물 불변 — 결정 F(i) "결정 K (a) 식·`metrics.json.gate` 판정식 불변", 산출물 45행 `curve.py` 는 meta 키 2개만(결정 H(i)); `S3.7` 9행 "`eval.md`(metrics.json만으로 재생성 가능)" ↔ 판정 표 14행 멱등 diff 0줄 |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | 01-plan 6~11행. `gitlog.sh P4b-er-redesign CR-001` 출력(본 검증 실행): "`e4109cc` 2026-09-22 cr(CR-001): … P4b 패키지 신설"(dev HEAD = 시작 해시), "`adf9f1b` docs(P4-pilot-eval): 완료 검토 — verifier 04-review 부분완료", `ef18143`·`ea1bbb2`·`f01ea35` 실재. `packages/P4-pilot-eval/04-review.md` 232행 "결과: 부분완료 — … 게이트가 미달 … P5 미착수", 233행 "승인: 사용자 (2026-09-22)". `packages/P3-er/04-review.md` 166행 "결과: 완료". registry 81·82·85행 해시 4개 실재(`git log -1` 02e6f14 "U3 호칭 사전·규칙 필터" · 593c254 "U4 확신도·두 임계치" · d6e5949 "U6 resolve()" · cc5d24f "U7 apply_resolution·회귀 3종" — 01-plan 8행이 요청한 태그 확인을 본 검증에서 대신 수행). `docs/backlog.md` 65행 "의존: P4 부분완료(adf9f1b), CR-001 승인", 70행 P5 "의존: P3, **P4b 게이트 통과**", `INDEX.md` 81행 "P4 미달 → P4b 게이트 통과가 조건". `CURRENT.md` "active: none / frozen: none". 주의: 스크립트 5번(의존 04-review `결과: 완료`)은 01-plan 5행이 `의존:` 단독 줄 + 불릿이라 **실행되지 않았다**(`verify-plan.sh` 62행 `grep -E '^의존:'` 같은 줄의 P id 만) — backlog 가 의존을 "부분완료"로 정한 패키지라 위 수동 확인이 대체한다(R-2) |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | 본 검증 실행 `diff <(sed -n 65,66p docs/backlog.md) <(sed -n 72,73p docs/wiki/packages/P4b-er-redesign/01-plan.md)` → 출력 0줄, `diff rc=0`. 스크립트 4번 "PASS backlog 일치". 단, backlog 65행의 "`·types.py`(+`settings.py` 설정값)" 는 **미커밋 작업본**이다 — `git diff docs/backlog.md` 에 `-…pipeline.py 가 D12·D13` → `+…pipeline.py·types.py(+settings.py 설정값) 가 D12·D13` 1행; 커밋본 `e4109cc` 의 backlog 와는 다르다. 계획 승인 커밋에 backlog·CR-001 변경을 함께 넣어야 일치가 저장소에 남는다(R-1). 01-plan 75~83행 "해석"은 두 줄을 바꾸지 않고 판정 명령으로만 풀었다(판정 표 1~21행) |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 스크립트 3번 "Refs 있음" U0·U1·U2·U3·U4·U5·U6·U7 8행 PASS. 68행 04-review 불릿도 "Refs: CR-001 D12 D13 D10 R3 R4 원칙8". Refs 가 가리키는 카드는 스크립트 2번 전부 PASS(D10·D12·D13·D3·D4·D5, S3.3, R3·R4, P3-er). U0 60행 "Refs: CR-001 D12 D13 S3.3 원칙3", U1 61행 "Refs: CR-001 D12 D10 S3.3 원칙3 원칙9", U2 62행 "Refs: CR-001 D13 S3.3 원칙1 원칙9", U3 63행 "Refs: CR-001 D13 D12 D10 S3.3 원칙1 원칙2 원칙9", U4 64행 "Refs: CR-001 D12 D13 S3.7 원칙8 원칙9", U5 65행 "Refs: CR-001 D4 D11 원칙8 L-004", U6 66행 "Refs: CR-001 D12 D13 S3.3 S3.7 원칙1 원칙8", U7 67행 "Refs: CR-001 S3.7 원칙4 원칙8 원칙9" |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §1 "`.env` … 에이전트가 읽지도 쓰지도 않는다 / 사용자가 직접 만든다" ↔ 01-plan 65행 "사용자가 쓰는 `.env` 로드 접두 … 스크립트는 `.env` 를 읽지 않는다, 로드 주체는 사용자 셸이다·security §1", 159행 "스크립트가 `.env` 를 읽는 것 … 후자는 security §1 위반"; `app/settings.py` 118행 "`.env` 파일 자체는 읽지 않는다(security.md §1)"; `docs/user-setup/10-pilot-eval-run.md` 9행 "스크립트는 `.env` 를 읽지 않고 환경변수를 통째로 출력하지도 않는다. 필요한 값은 사용자 셸에만 둔다". 키·프롬프트 미노출: `scripts/run_pilot_eval.py` 68행 "프롬프트 원문·`llm.reason` 자유 서술·키는 덤프에 넣지 않는다(security §1)", 01-plan 65행 evidence "실행 명령(키 값 없이)". `reports/` 쓰기: 결정 I(i) 는 복사·갱신만(삭제 없음), 30행 raw·traces 덮어쓰기 금지, 판정 표 17행 sha256 대조(본 검증 시점 `reports/metrics.json` sha256 `25e16dd67ea7…` 일치, `reports/pilot/` 에는 raw·traces 2파일뿐이라 사본 경로 충돌 없음). 외부 전송: OpenAI 호출은 SDK(`security.md` §4 "외부 API 호출은 코드(SDK)로, 키는 환경변수"). 재귀 삭제·강제 푸시·DROP·`git add -A` 언급 0건. 113행 "Docker Desktop 이 꺼져 있거나 키가 없으면 우회하지 않고 사용자에게 명령을 보여 주고 멈춘다(security §6)" |

## 2b. 계획의 사실 주장 검증 (코드·테스트로 직접 확인)

| # | 주장(01-plan) | 판정 | 근거(파일:행 + 인용 / 실행 출력) |
|---|---|---|---|
| (a) | "예외 없는 전면 강등은 승진 회귀 1을 깬다"(134·136행) | 맞음 | `tests/test_er_pipeline.py` 421행 `hierarchy="동"`, 429행 mention "부장님"(유도 위계 상) → 435~437행 `rule_checked == 3`·`rule_passed == 2`·`s_rule ≈ 2/3` = 위계 1항 불일치, 444행 `assert result.band == "merge"`, 445행 `forced_reason is None`. D13 뒤 김민수는 `hierarchy_conflict` 감점 후보이므로 "감점 후보 ≥ T_merge → identity" 를 예외 없이 적용하면 444·445행이 깨진다. 현재 상태 `3 passed`(evidence `20260922-1713-regression3-baseline.txt`). 정밀화: `app/er/rules.py` 105~108행 `if relaxed and adjacent: relaxed_pass = True … else: conflicts.add("hierarchy_conflict")` — **완화 모드 평가에서는 충돌이 conflicts 에 들어가지 않는다**. U2 가 완화 통과 후보의 `penalized_by` 를 비우는 구현을 택하면 예외 규칙이 없어도 강등되지 않지만, 결정 A(i) 의 명시적 예외는 어느 구현에서도 회귀 1 을 성립시킨다(R-4) |
| (b) | "D13 이후 완화 트리거가 영영 안 돈다"(139행 C(i)) | 맞음 | `app/er/rules.py` 149행 `passed_rules=not conflicts`, 188~191행 `strict_passed = [c for c in strict_scored if c.passed_rules]; if strict_passed: return strict_passed, strict_scored, False`. D13 로 `hierarchy_conflict` 후보가 `passed_rules=True` 가 되면 `strict_passed` 가 비지 않아 191행에서 즉시 반환 → 200~202행 완화 재평가 미도달 → `tests/test_er_pipeline.py` 432행 `relaxed_retry is True`·434행 `relaxed_pass is True` 가 깨진다. 트리거를 "감점 없는 후보 0"으로 바꿔야 193~202행이 다시 산다 |
| (c) | 동명이인 회귀가 D12 로 "≈0.575 → ≈0.72" 가 되어도 `[0.3, 0.8)`(63·151행) | 맞음 | `tests/test_er_pipeline.py` 534~538행 두 인물이 같은 별칭 "민수"를 같은 결정적 벡터(`tests/conftest.py` 141~144행 "결정적이다")로 가짐 → 질의 "민수"와 코사인 1.0 = `s_emb`; 541행 `s_llm 0.55`; 546·553행 `passed_rules True`·`s_rule == 0.0` ⇒ `rule_checked == 0`. 본 검증 계산: `D3 = 0.5·0.55 + 0.3·1.0 + 0.2·0 = 0.575`, `D12 = (0.5·0.55 + 0.3·1.0)/0.8 = 0.71875`, `0.3 ≤ 0.71875 < 0.8 → True`, `T_merge` 까지 여유 `0.08125`, `weights_effective = {llm 0.625, emb 0.375, rule 0.0}` 합 1.0. 549행 `t_new <= confidence < t_merge` 유지 |
| (d) | U0: `SKILL.md` 22·36·39행이 "아직 D3·배제 규약 그대로"(60행) | 맞음 | `.claude/skills/entity-resolution/SKILL.md` 22행 "2. 규칙 필터 … 명백히 다른 후보 배제", 36행 "`s_rule` … 규칙 필터 통과 항목 수 / 검사 항목 수", 39행 "`confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule`"; `grep -n "D12\|D13\|CR-001\|감점\|penalized"` → 0건(rc=1). `CLAUDE.md` 39행 원칙4 "이유는 `.claude/skills/entity-resolution` 참조", `S3.3` 3행 "절차 상세: `.claude/skills/entity-resolution`" — backend-agent 가 자동 참조하는 문서가 대체된 결정을 담고 있다 |
| (e) | "`--recheck-traces` 가 새 trace 를 거부할 수 있다"(153행; 904·921행) | 맞음(형태 정밀화) | `scripts/run_pilot_eval.py` 914~924행 `weights = breakdown.get("weights") … if recorded != ER_WEIGHTS: raise TraceRecheckError(… 원칙3)`, 931~936행 `combine(s_llm, s_emb, s_rule, _Weights(…))` = D3 형태 재계산, 942행 "판정 기준은 `diff == 0.0`". 결정 H(i)·D(i) 대로 `weights` 에 설정값을 그대로 적으면 921행 거부는 걸리지 않지만 `rule_checked=0` 행의 재계산 `0.5·s_llm+0.3·s_emb` ≠ 기록 `0.625·s_llm+0.375·s_emb` 로 diff ≠ 0 → rc=1(64행 "하나라도 어긋나면 rc=1"). `weights` 에 유효 가중치를 적으면 921행에서 거부. 어느 쪽이든 U4 → U5 순서가 필수라는 결론은 그대로(R-5) |
| (f) | 결정 I 경로 정합(CR-001 36행 정정 후 backlog·계획·CR 일치) | 일치(미커밋) | `git diff docs/wiki/changes/CR-001.md` 36행 `+… reports/pilot/raw-… · traces-… 는 덮어쓰지 않는다; reports/metrics.json(sha256 25e16dd6…)·calibration·curve·eval.md 는 재실행 전에 reports/pilot/<이름>-20260922-042440.* stamp 사본으로 커밋해 보존하고 최상위는 재실행 결과로 갱신한다(P4b 01-plan 결정 I(i))` = 01-plan 결정 I(i)·판정 표 17행 `reports/pilot/metrics-20260922-042440.json` = backlog 65행 "새 stamp … `reports/metrics.json` 로 결정 K 게이트 … P4 기준선(`raw-20260922-042440.jsonl.gz`) 미변경". `D12` 20행 "P4 기준선 … 보존한다"는 사본으로 충족. `ls reports/pilot/` → `raw-20260922-042440.jsonl.gz`·`traces-20260922-042440.jsonl` 2파일뿐(사본 경로 충돌 없음). 남는 옛 문구는 `packages/P4-pilot-eval/04-review.md` 220행(닫힌 기록, 수정 대상 아님 — R-6) |

## 2c. 추가 관찰

- **U0 분류(권고 의견)**: `.claude/skills/entity-resolution/SKILL.md` 는 위치상 **개발 하네스 파일**이다(`CLAUDE.md` "이 문서와 `.claude/`는 개발 하네스다"). 그러나 내용은 `S3.3` 3행이 "절차 상세"로 가리키는 **명세 미러**이고 `CLAUDE.md` 원칙4 가 이유의 출처로 지목한다. 따라서 U0 은 제품 코드가 아니라 **하네스 문서 정합**(문서 커밋, 메인 세션, `CURRENT.md` 활성 없이도 `.claude/` 쓰기 가능)으로 다루는 것이 맞고, 커밋 Refs 는 `CR-001 D12 D13 S3.3`. `CR-001.md` §2 "수정할 파일 목록"에 이 파일이 없었던 것은 CR 문서의 누락이다 — U0 이 그 틈을 닫는다(R-7).
- 01-plan 10행 "미커밋 변경은 `journal.md` 1건뿐"은 스냅샷 시점 사실이고, 본 검증 시점 `git status` 는 `backlog.md`·`HANDOFF.md`·`CR-001.md`·`journal.md` 수정 + `packages/P4b-er-redesign/` 신규다. 제품 코드·`data/`·`reports/` 변경 0 은 그대로.
- U1(61행)이 `scripts/er_smoke.py:109`(`combine(judgement.s_llm, s_emb, s_rule, config)`) 호출부를 고친다고 적었으나 산출물 목록(39~54행)·재사용 표(115~127행)에 `scripts/er_smoke.py` 가 없고, 담당 분리(3행 backend-agent=`app/`, eval-agent=`scripts/`)와도 어긋난다(R-3).
- 회귀 3종 현재 baseline: `POSTGRES_PORT=5433 python -m pytest tests/test_er_pipeline.py -q -k "promotion or aunt or homonym"` → `3 passed, 15 deselected` (evidence `20260922-1713-regression3-baseline.txt`). U3 뒤 같은 명령 출력이 판정 표 2행 증거가 된다.

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)

보류(H-n): **없음** — 원칙·카드 충돌, 수용 기준 불일치, 사실 주장 오류, 보안 위반 중 해당 없음.

권고(R-n, 통과와 양립 — 실행 시 반영):
- **R-1** `docs/backlog.md` 65행(`types.py`+`settings.py`)·`docs/wiki/changes/CR-001.md` 36행(결정 I 문구) 변경이 **미커밋**이다. 점검표 6행의 "글자 그대로" 일치는 작업본 기준이므로 계획 승인 커밋(`docs(P4b-er-redesign): 계획검증 통과·계획 승인`)에 두 파일을 함께 `git add`(명시 경로) 한다. Refs 에 `CR-001` 포함.
- **R-2** `verify-plan.sh` 5번(의존 04-review `결과: 완료`)이 01-plan 의존 줄 형식(단독 `의존:` + 불릿) 때문에 실행되지 않았다. 이번은 5행 수동 확인(해시·04-review 인용)으로 대체했다. 하네스 교훈 후보: 스크립트가 불릿 의존을 읽고, backlog 가 "부분완료(해시)" 로 정한 의존은 04-review `부분완료` + 사용자 승인 줄로 통과시키는 규칙(L-nnn).
- **R-3** `scripts/er_smoke.py` 를 01-plan 산출물 목록·registry 재사용 표에 추가하고 U1 커밋 소속(backend-agent 가 고치는 `scripts/` 1파일)을 03-log 에 명시한다. 판정 표 15행(`app/` 부분집합)에는 영향 없음.
- **R-4** U2 03-log 에 "완화 통과(`relaxed_pass=True`) 후보의 `penalized_by` 를 `hierarchy_conflict` 로 채우는가, 비우는가"를 한 줄로 확정한다(`rules.py` 105~108행 분기). 결정 A(i) 예외의 의미(명시적 예외 vs 자연 통과)가 여기서 고정되고, U4 `penalized_merge` 부분집합의 `relaxed_pass` 계수 정의도 이에 따른다.
- **R-5** 01-plan 153행 "거부"는 결정 H(i)(`weights` 설정값 유지) 아래서는 "921행 통과 후 재계산 diff ≠ 0 → rc=1" 형태로 나타난다. U4 (i) 의 테스트에 이 케이스(`rule_checked=0` 행이 옛 재계산으로 diff ≠ 0 → 새 재계산으로 0.0)를 넣으면 결정 D(i) 가 증명된다.
- **R-6** `packages/P4-pilot-eval/04-review.md` 220행("`metrics.json` … 덮어쓰지 않는다")은 닫힌 기록이라 고치지 않는다. P4b 04-review §7 또는 03-log 에 "결정 I(i) 로 대체(CR-001 36행 정정)" 한 줄을 남긴다.
- **R-7** U0 은 하네스 문서 커밋으로 처리(2c). `SKILL.md` 에 "산식·2단계 규약의 권위는 `S3.3`·`D12`·`D13`" 한 줄을 넣어 이중 출처를 막고, `CR-001.md` 갱신 이력에 "SKILL.md 누락 → P4b U0 에서 정합" 한 줄(메인 세션).
- **R-8** U3 의 강등 케이스 테스트에 `ask_payload["context"]["candidate_ids"]` 가 **감점 후보를 포함**하는 단언을 넣는다(`tests/test_er_pipeline.py` 561행 규약 — 사용자가 칩에서 감점 후보를 고를 수 있어야 강등이 "묻는 것"이 된다, 원칙1·D13 13행 "원칙1 은 확신이 없으면 묻는 것이지 후보를 숨기는 것이 아니다").
- **R-9** 판정 표 21행 `ls evidence/*real-run*` 이 성립하려면 U5 evidence 파일명에 `real-run` 을 포함한다는 규약을 U5 문장에 명시한다.

05-remediation 소견([권고] 22, [필수] 0 — `findings.py --source verify-plan`, 2차 출력): 기존 파일 확장 18건 = F-ed9327(`app/er/confidence.py`) F-99f745(`rules.py`) F-ead503(`pipeline.py`) F-c4dc23(`types.py`) F-fdb56f(`app/settings.py`) F-3e8c8f(`scripts/run_pilot_eval.py`) F-111cde(`evaluation/curve.py`) F-c9f2fe(`metrics.py`) F-63a805(`calibration.py`) F-a58eb4(`resolvers/proposed.py`) F-2e533b(`tests/test_er_confidence.py`) F-107c92(`test_er_rules.py`) F-8439c7(`test_er_pipeline.py`) F-27a843(`test_run_pilot_eval.py`) F-5d4642(`reports/metrics.json`) F-00846b(`reports/failure_cases.md`) F-0ffff5(`README.md` — P4 와 같은 ID·같은 선례) F-225938(`docs/user-setup/10-pilot-eval-run.md`); basename 오탐 4건 = F-fcf0a9(`.jsonl.gz`) F-a4bedc(`calibration.json`) F-09ad74(`curve.csv`) F-3f9278(`eval.md`). 원인 분석 칸 기입 완료. 해소 = U7 registry 비고 확장(새 행 없음) + 새 stamp 행 등재 → 04-review §5 에서 닫는다.

## 4. 결정
결과: 통과
승인: 사용자 (2026-09-22) — 권고 R-3·R-9 는 01-plan 에 즉시 반영, R-1 은 START 커밋에 포함, R-7 채택(U0 = 하네스 문서 정합), R-2 하네스 L-nnn 후보, 나머지는 해당 단위 실행 시
