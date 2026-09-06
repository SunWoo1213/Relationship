# P1-pilot-dataset · 계획 검증 (02-plan-verify)

대상: 01-plan.md | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002) | 날짜: 2026-09-06 (1차 판정 17:22 → 재검증 17:28, 새 verifier 컨텍스트)

선행 확인(`bash .claude/scripts/gitlog.sh P1-pilot-dataset S3.7`, 재검증 시점): dev = main = `bdf9f70`, 승격 대기 0. 선행 패키지 완료 커밋 P1-schema `5dc95bb`, P3-er `0527ab8`. 미커밋 변경: `docs/backlog.md`(P1 절 하위 불릿 9줄·리스크 로그 1행 추가 — `git diff docs/backlog.md | grep -E '^[-+]'` 출력에 `+` 줄만 있고 `-` 줄 없음을 재확인. 하위 불릿 U6 의 기록 경로가 `packages/P1-pilot-dataset/evidence/<ts>-label-review.md` 로 갱신됨), `docs/wiki/HANDOFF.md`, `docs/wiki/journal.md`, `README.md`, `docs/SERVER-CHECKLIST.md`, `docs/wiki/packages/P1-pilot-dataset/`(신규). 01-plan 은 신규 파일이라 diff 가 없으므로 재검증은 01-plan 을 다시 읽어 행 번호로 인용한다.

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 bash .claude/scripts/verify-plan.sh P1-pilot-dataset | tee docs/wiki/packages/P1-pilot-dataset/evidence/<ts>-verify-plan-N.txt`

1차 — 메인 세션 실행 `evidence/20260906-1713-verify-plan.txt` (02-plan-verify.md 작성 전, FAIL 1 = 이 문서 부재):
```
== verify-plan P1-pilot-dataset  (2026-09-06 17:13) ==
PASS  존재: docs/wiki/packages/P1-pilot-dataset/01-plan.md
FAIL  없음: docs/wiki/packages/P1-pilot-dataset/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D10
PASS  카드 존재: D6
PASS  패키지 id 등록됨: P0-cost
PASS  패키지 id 등록됨: P1-pilot-dataset
PASS  패키지 id 등록됨: P1-schema
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P4-pilot-eval
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R13
PASS  Refs 있음: - [ ] U1 시나리오 스키마 확정 + JSON Schema + 검�
PASS  Refs 있음: - [ ] U2 `promotion` 8건 + `alias` 8건 작성. 승진 후 
PASS  Refs 있음: - [ ] U3 `pronoun` 8건 + `normal` 10건 작성. `pronoun` �
PASS  Refs 있음: - [ ] U4 `new_person` 6건 작성. 처음 등장하는 인�
PASS  Refs 있음: - [ ] U5 전건 무결성 점검 + 검수 패킷 생성. `va
PASS  Refs 있음: - [ ] U6 라벨 검수 지적 반영. verifier 또는 사용
PASS  Refs 있음: - [ ] U7 registry 행 추가 · README "평가 데이터셋"
PASS  backlog 일치: 파일럿 데이터셋 30~50건 (승진·대명사·별칭·
PASS  의존 완료: P1-schema
PASS  의존 완료: P3-er
PASS  registry 중복 없음: data/scenarios/schema.json
PASS  registry 중복 없음: events.type
PASS  registry 중복 없음: ask_user.kind
PASS  registry 중복 없음: data/scenarios/promotion.json
PASS  registry 중복 없음: data/scenarios/pronoun.json
PASS  registry 중복 없음: data/scenarios/alias.json
PASS  registry 중복 없음: data/scenarios/normal.json
PASS  registry 중복 없음: data/scenarios/new_person.json
PASS  registry 중복 없음: data/scenarios/manifest.json
PASS  registry 중복 없음: scripts/validate_scenarios.py
PASS  registry 중복 없음: tests/test_validate_scenarios.py
PASS  registry 중복 없음: docs/wiki/packages/P1-pilot-dataset/label-review.md
== 결과: FAIL=1 WARN=0 ==
```

2차 — verifier 직접 실행 `evidence/20260906-1719-verify-plan-2.txt` (이 문서 작성 직전, 같은 FAIL 1 재현):
```
== verify-plan P1-pilot-dataset  (2026-09-06 17:19) ==
PASS  존재: docs/wiki/packages/P1-pilot-dataset/01-plan.md
FAIL  없음: docs/wiki/packages/P1-pilot-dataset/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D10
PASS  카드 존재: D6
PASS  패키지 id 등록됨: P0-cost
PASS  패키지 id 등록됨: P1-pilot-dataset
PASS  패키지 id 등록됨: P1-schema
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P4-pilot-eval
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R13
PASS  Refs 있음: - [ ] U1 시나리오 스키마 확정 + JSON Schema + 검�
PASS  Refs 있음: - [ ] U2 `promotion` 8건 + `alias` 8건 작성. 승진 후 
PASS  Refs 있음: - [ ] U3 `pronoun` 8건 + `normal` 10건 작성. `pronoun` �
PASS  Refs 있음: - [ ] U4 `new_person` 6건 작성. 처음 등장하는 인�
PASS  Refs 있음: - [ ] U5 전건 무결성 점검 + 검수 패킷 생성. `va
PASS  Refs 있음: - [ ] U6 라벨 검수 지적 반영. verifier 또는 사용
PASS  Refs 있음: - [ ] U7 registry 행 추가 · README "평가 데이터셋"
PASS  backlog 일치: 파일럿 데이터셋 30~50건 (승진·대명사·별칭·
PASS  의존 완료: P1-schema
PASS  의존 완료: P3-er
PASS  registry 중복 없음: data/scenarios/schema.json
PASS  registry 중복 없음: events.type
PASS  registry 중복 없음: ask_user.kind
PASS  registry 중복 없음: data/scenarios/promotion.json
PASS  registry 중복 없음: data/scenarios/pronoun.json
PASS  registry 중복 없음: data/scenarios/alias.json
PASS  registry 중복 없음: data/scenarios/normal.json
PASS  registry 중복 없음: data/scenarios/new_person.json
PASS  registry 중복 없음: data/scenarios/manifest.json
PASS  registry 중복 없음: scripts/validate_scenarios.py
PASS  registry 중복 없음: tests/test_validate_scenarios.py
PASS  registry 중복 없음: docs/wiki/packages/P1-pilot-dataset/label-review.md
== 결과: FAIL=1 WARN=0 ==
```

3차 — 이 문서 작성 후 verifier 재실행 `evidence/20260906-1722-verify-plan-3.txt` (1차 판정: 점검표 2·4행과 결과 줄이 "보류" 였으므로 WARN 1):
```
== verify-plan P1-pilot-dataset  (2026-09-06 17:22) ==
PASS  존재: docs/wiki/packages/P1-pilot-dataset/01-plan.md
PASS  존재: docs/wiki/packages/P1-pilot-dataset/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D10
PASS  카드 존재: D6
PASS  패키지 id 등록됨: P0-cost
PASS  패키지 id 등록됨: P1-pilot-dataset
PASS  패키지 id 등록됨: P1-schema
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P4-pilot-eval
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R13
PASS  Refs 있음: - [ ] U1 시나리오 스키마 확정 + JSON Schema + 검�
PASS  Refs 있음: - [ ] U2 `promotion` 8건 + `alias` 8건 작성. 승진 후 
PASS  Refs 있음: - [ ] U3 `pronoun` 8건 + `normal` 10건 작성. `pronoun` �
PASS  Refs 있음: - [ ] U4 `new_person` 6건 작성. 처음 등장하는 인�
PASS  Refs 있음: - [ ] U5 전건 무결성 점검 + 검수 패킷 생성. `va
PASS  Refs 있음: - [ ] U6 라벨 검수 지적 반영. verifier 또는 사용
PASS  Refs 있음: - [ ] U7 registry 행 추가 · README "평가 데이터셋"
PASS  backlog 일치: 파일럿 데이터셋 30~50건 (승진·대명사·별칭·
PASS  의존 완료: P1-schema
PASS  의존 완료: P3-er
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
WARN  보류 3 건 — 결과는 통과가 될 수 없다
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: data/scenarios/schema.json
PASS  registry 중복 없음: events.type
PASS  registry 중복 없음: ask_user.kind
PASS  registry 중복 없음: data/scenarios/promotion.json
PASS  registry 중복 없음: data/scenarios/pronoun.json
PASS  registry 중복 없음: data/scenarios/alias.json
PASS  registry 중복 없음: data/scenarios/normal.json
PASS  registry 중복 없음: data/scenarios/new_person.json
PASS  registry 중복 없음: data/scenarios/manifest.json
PASS  registry 중복 없음: scripts/validate_scenarios.py
PASS  registry 중복 없음: tests/test_validate_scenarios.py
PASS  registry 중복 없음: docs/wiki/packages/P1-pilot-dataset/label-review.md
== 결과: FAIL=0 WARN=1 ==
```

4차 — 메인 세션이 H-1~H-3 결정을 01-plan 에 반영한 뒤 실행 `evidence/20260906-1727-verify-plan-4.txt` (02-plan-verify 는 아직 1차 판정 그대로라 WARN 1 유지):
```
== verify-plan P1-pilot-dataset  (2026-09-06 17:27) ==
PASS  존재: docs/wiki/packages/P1-pilot-dataset/01-plan.md
PASS  존재: docs/wiki/packages/P1-pilot-dataset/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D10
PASS  카드 존재: D6
PASS  패키지 id 등록됨: P0-cost
PASS  패키지 id 등록됨: P1-pilot-dataset
PASS  패키지 id 등록됨: P1-schema
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P4-pilot-eval
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R13
PASS  Refs 있음: - [ ] U1 시나리오 스키마 확정 + JSON Schema + 검�
PASS  Refs 있음: - [ ] U2 `promotion` 8건 + `alias` 8건 작성. 승진 후 
PASS  Refs 있음: - [ ] U3 `pronoun` 8건 + `normal` 10건 작성. `pronoun` �
PASS  Refs 있음: - [ ] U4 `new_person` 6건 작성. 처음 등장하는 인�
PASS  Refs 있음: - [ ] U5 전건 무결성 점검 + 검수 패킷 생성. `va
PASS  Refs 있음: - [ ] U6 라벨 검수 지적 반영. verifier 또는 사용
PASS  Refs 있음: - [ ] U7 registry 행 추가 · README "평가 데이터셋"
PASS  backlog 일치: 파일럿 데이터셋 30~50건 (승진·대명사·별칭·
PASS  의존 완료: P1-schema
PASS  의존 완료: P3-er
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
WARN  보류 3 건 — 결과는 통과가 될 수 없다
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: data/scenarios/schema.json
PASS  registry 중복 없음: events.type
PASS  registry 중복 없음: ask_user.kind
PASS  registry 중복 없음: data/scenarios/promotion.json
PASS  registry 중복 없음: data/scenarios/pronoun.json
PASS  registry 중복 없음: data/scenarios/alias.json
PASS  registry 중복 없음: data/scenarios/normal.json
PASS  registry 중복 없음: data/scenarios/new_person.json
PASS  registry 중복 없음: data/scenarios/manifest.json
PASS  registry 중복 없음: scripts/validate_scenarios.py
PASS  registry 중복 없음: tests/test_validate_scenarios.py
PASS  registry 중복 없음: -label-review.md
== 결과: FAIL=0 WARN=1 ==
```

5차 — 재검증 verifier(새 컨텍스트) 가 이 문서를 갱신하기 전에 실행 `evidence/20260906-1728-verify-plan-5.txt` (4차와 동일, WARN 1 재현):
```
== verify-plan P1-pilot-dataset  (2026-09-06 17:28) ==
PASS  존재: docs/wiki/packages/P1-pilot-dataset/01-plan.md
PASS  존재: docs/wiki/packages/P1-pilot-dataset/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D10
PASS  카드 존재: D6
PASS  패키지 id 등록됨: P0-cost
PASS  패키지 id 등록됨: P1-pilot-dataset
PASS  패키지 id 등록됨: P1-schema
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P4-pilot-eval
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R13
PASS  Refs 있음: - [ ] U1 시나리오 스키마 확정 + JSON Schema + 검�
PASS  Refs 있음: - [ ] U2 `promotion` 8건 + `alias` 8건 작성. 승진 후 
PASS  Refs 있음: - [ ] U3 `pronoun` 8건 + `normal` 10건 작성. `pronoun` �
PASS  Refs 있음: - [ ] U4 `new_person` 6건 작성. 처음 등장하는 인�
PASS  Refs 있음: - [ ] U5 전건 무결성 점검 + 검수 패킷 생성. `va
PASS  Refs 있음: - [ ] U6 라벨 검수 지적 반영. verifier 또는 사용
PASS  Refs 있음: - [ ] U7 registry 행 추가 · README "평가 데이터셋"
PASS  backlog 일치: 파일럿 데이터셋 30~50건 (승진·대명사·별칭·
PASS  의존 완료: P1-schema
PASS  의존 완료: P3-er
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
WARN  보류 3 건 — 결과는 통과가 될 수 없다
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: data/scenarios/schema.json
PASS  registry 중복 없음: events.type
PASS  registry 중복 없음: ask_user.kind
PASS  registry 중복 없음: data/scenarios/promotion.json
PASS  registry 중복 없음: data/scenarios/pronoun.json
PASS  registry 중복 없음: data/scenarios/alias.json
PASS  registry 중복 없음: data/scenarios/normal.json
PASS  registry 중복 없음: data/scenarios/new_person.json
PASS  registry 중복 없음: data/scenarios/manifest.json
PASS  registry 중복 없음: scripts/validate_scenarios.py
PASS  registry 중복 없음: tests/test_validate_scenarios.py
PASS  registry 중복 없음: -label-review.md
== 결과: FAIL=0 WARN=1 ==
```

6차 — 이 문서의 2·4·6행과 결과 줄을 갱신한 뒤 verifier 재실행 `evidence/20260906-1736-verify-plan-6.txt`:
```
== verify-plan P1-pilot-dataset  (2026-09-06 17:36) ==
PASS  존재: docs/wiki/packages/P1-pilot-dataset/01-plan.md
PASS  존재: docs/wiki/packages/P1-pilot-dataset/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D10
PASS  카드 존재: D6
PASS  패키지 id 등록됨: P0-cost
PASS  패키지 id 등록됨: P1-pilot-dataset
PASS  패키지 id 등록됨: P1-schema
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P3-baselines
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P4-pilot-eval
PASS  패키지 id 등록됨: P5-loop
PASS  검증 항목 존재: R13
PASS  Refs 있음: - [ ] U1 시나리오 스키마 확정 + JSON Schema + 검�
PASS  Refs 있음: - [ ] U2 `promotion` 8건 + `alias` 8건 작성. 승진 후 
PASS  Refs 있음: - [ ] U3 `pronoun` 8건 + `normal` 10건 작성. `pronoun` �
PASS  Refs 있음: - [ ] U4 `new_person` 6건 작성. 처음 등장하는 인�
PASS  Refs 있음: - [ ] U5 전건 무결성 점검 + 검수 패킷 생성. `va
PASS  Refs 있음: - [ ] U6 라벨 검수 지적 반영. verifier 또는 사용
PASS  Refs 있음: - [ ] U7 registry 행 추가 · README "평가 데이터셋"
PASS  backlog 일치: 파일럿 데이터셋 30~50건 (승진·대명사·별칭·
PASS  의존 완료: P1-schema
PASS  의존 완료: P3-er
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: data/scenarios/schema.json
PASS  registry 중복 없음: events.type
PASS  registry 중복 없음: ask_user.kind
PASS  registry 중복 없음: data/scenarios/promotion.json
PASS  registry 중복 없음: data/scenarios/pronoun.json
PASS  registry 중복 없음: data/scenarios/alias.json
PASS  registry 중복 없음: data/scenarios/normal.json
PASS  registry 중복 없음: data/scenarios/new_person.json
PASS  registry 중복 없음: data/scenarios/manifest.json
PASS  registry 중복 없음: scripts/validate_scenarios.py
PASS  registry 중복 없음: tests/test_validate_scenarios.py
PASS  registry 중복 없음: -label-review.md
== 결과: FAIL=0 WARN=0 ==
```
FAIL 이 하나라도 있으면 아래 결과는 통과가 될 수 없다. FAIL/WARN 은 `python .claude/scripts/findings.py <id> evidence/<ts>-verify-plan.txt --source verify-plan` 으로 05-remediation.md 에 소견으로 올리고, 조치 후 다시 실행한다.
(1·2차의 FAIL 1 은 "02-plan-verify.md 없음" 하나뿐이며 이 문서 자체가 조치라 별도 소견을 만들지 않았다. 3차의 WARN 1 은 1차 판정의 점검표 2·4행 "보류" 를 스크립트가 센 것이며 `findings.py … 20260906-1722-verify-plan-3.txt --source verify-plan` 으로 **F-033bb1**(권고) 이 생성됐다. 4·5차 WARN 1 은 01-plan 이 고쳐진 뒤에도 이 문서가 1차 판정 그대로였기 때문이며, 6차는 이 문서 갱신 후의 재실행이다 — 3절 F-033bb1 상태 참조. 참고: 4차부터 "registry 중복 없음" 마지막 줄이 `-label-review.md` 로 잘려 나오는 것은 스크립트가 산출물 경로 `evidence/<ts>-label-review.md` 의 `<ts>` 자리표시자를 파일명 경계로 읽은 표시 문제이고 검사 자체는 수행됐다 — 자리표시자 경로의 한계라 소견으로 올리지 않는다.)

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다. 행 번호는 재검증 시점의 01-plan.md 기준.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 2장 표 제외 열: "고민 상담 기능 / 인물 간(A–B) 관계 저장 / 관계 태그 필터링 / 상담 페르소나 / 톤 설정 / 음성 입력 / 네이티브 앱". 01-plan 74행 결정 A 확정 "`persons[{person_id, display_name, relation_tag, hierarchy, aliases[]}]`" 는 사용자–인물 메타뿐이며 인물–인물 필드가 없다(`S3.1-schema-v2.md` "인물–인물 관계 테이블 없음 (D8, 원칙7)" 과 같은 방향). 01-plan 24행 "**제품 코드 변경 없음**: `app/` 아래 파일을 만들지도 고치지도 않는다", 26행 "DB 적재 … 는 하지 않는다". 발화 데이터는 텍스트 JSON 이라 음성·네이티브·페르소나와 무관. 재검증에서 바뀐 것 없음. 시나리오 발화에 고민 상담형 대화를 넣지 않는 검수 항목은 여전히 권고(3절 R-4, 미반영). |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | 원칙1·2·4: 01-plan 43행 U2 "오병합 유도 함정 … 최소 3건 포함하고 그 건의 `gold_person_id` 를 다르게 준다(원칙1 비대칭 비용을 측정 가능하게)", 45행 U4 "허용 집합으로 라벨한다(임계치에 따라 달라지므로 단일 정답으로 고정하지 않는다 — D10)" — 임계치 하나·자동 병합을 전제한 라벨이 없다. 원칙6·7: 패턴 감지·제외 항목 무관(1행). 원칙9: 산출물이 데이터라 trace 대상 아님. **원칙8(1차 판정에서 미정이던 생성 경로) 해소**: 01-plan 79행 "생성 경로는 **eval-agent(opus) 가 자기 컨텍스트에서 JSON 을 직접 작성**한다(스크립트 API 호출 없음 — "하지 않는 것"의 네트워크 미사용 문장 유지)" 가 25행 "실 LLM·실 임베딩 API 호출 없음(검증기는 네트워크를 쓰지 않는다)" 과 같은 경로를 가리켜 모순이 사라졌다. 재현 기록의 내용도 79행이 키 단위로 고정: "`manifest.json` 필수 키: `generator.model_id`(eval-agent 모델 id), `generator.prompt_ref`(위임 프롬프트를 저장한 `evidence/<ts>-gen-prompt.md` 경로), `generator.seed: null` + `seed_reason: "대화형 생성"`, `generator.same_family_as_judge: true`(P3-er 판정 모델과 같은 공급자 계열)" — 시드가 없는 대화형 생성이라는 사실 자체를 기록하므로 원칙8 "재현 가능" 의 정직한 형태다(재현 불가를 숨기지 않음). 자기 채점 편향 차단 문장 79행 "**금지: 초안 위임 프롬프트에 ER 판정 프롬프트·호칭 사전(`app/er/dictionary`)·임계치 값을 넣지 않는다**" 존재. 남는 것은 `prompt_ref` 가 가리키는 파일을 **어느 단위가 저장하는지** U1~U7(42~48행) 어디에도 없다는 점 — 판정을 막지는 않으나 권고 R-8. |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `D01-new-person-confirm.md` "코드에서 지켜야 할 것: `create_person` 호출 경로는 반드시 answered pending_question 을 거친다" — 데이터셋은 코드를 호출하지 않으며, 01-plan 45행 U4 "지나가는 언급(… 등록하면 안 되는 것)을 섞어 D1 의 확인형 등록이 옳게 동작하는지 측정 가능하게" 는 이 규칙을 측정 대상으로 삼는다. `D10-two-thresholds.md` "임계치 하나로 구현하지 않는다. 두 값 모두 설정값" — 77행 결정 D 허용 집합 라벨은 `T_merge` 스윕(D10 "곡선 x축 = T_merge ∈ {0.5,…,0.95}, T_new 고정")과 정합. `D03-confidence-formula.md` "`s_rule`: 규칙 통과 수 / 검사 수 (위계 일치, 관계 태그 일치, 호칭 사전 호환)" — 74행 결정 A 의 `relation_tag`·`hierarchy` 포함이 `s_rule` 계산 전제를 채운다. `D06` "별칭은 절대 삭제하지 않는다" — 43행 U2 "승진 후 호칭이 바뀌어도 같은 인물(D6 별칭 누적 정책과 같은 방향)" 정합. 재검증에서 바뀐 것 없음. |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `S3.7-eval-spec.md` "데이터셋 스키마: eval-harness 스킬 1절. 카테고리에 `new_person` 추가" — 01-plan 30행 "`category` 5종" 에 `new_person` 포함, `.claude/skills/eval-harness/SKILL.md` §1 의 `id`·`category`·`utterances`·`mentions[{turn,surface,gold_person_id}]` 를 유지한 채 `persons`·`events`·`seed_persons`·`expected_ask_user.allowed`·`mentions[].ambiguous` 를 **추가**만 한다(74~78행, 기존 필드 의미 변경 없음 → 확장). `S3.1-schema-v2.md` "`events.type` CHECK 제약: `conflict / praise / meal / meeting / personal_share / favor / other`", "`relation_tag` ∈ {가족, 연인, 친구, 직장, 지인}, `hierarchy` ∈ {상, 동, 하}" — 75행 결정 B "`type` 고정 7종", 30행 "관계 태그 5종, 위계 3종" 일치. `S3.1` "`pending_questions.kind` ∈ {identity, new_person, schedule}" — 77행 "`allowed` enum 은 `ask_user.kind` 와 별도 정의(`identity/new_person/none`, R-1)" 로 `none` 이 kind 집합을 오염시키지 않음. 임계치 2개·ask_user 비동기는 데이터 형식이 침범하지 않음. **1차 판정의 H-1 세 문장 충돌 해소** — 세 문장을 나란히 놓으면: 77행 "(1) `ambiguous` 는 `mentions[]` 단위 필드, (2) `ambiguous: true` 인 mention 만 `gold_person_id: null` 허용(검증기 예외), (3) 그 시나리오는 30~50 건수와 배분표에 포함하되 `manifest.json` 에 `ambiguous_mention_count` 를 별도로 두고 오병합률·미검출률·F1 분모에서 해당 mention 을 제외한다" / 42행 U1 "교차 검사 예외(H-1): `mentions[].ambiguous == true` 인 mention 만 `gold_person_id: null` 을 허용하고, `ambiguous` 가 없거나 false 면 null 은 FAIL" / 44행 U3 "선행사가 사람도 정할 수 없는 발화는 그 mention 을 `ambiguous: true`·`gold_person_id: null` 로 라벨한다(… 시나리오 자체는 건수에 포함, 해당 mention 만 지표 분모 제외)". 단위(mention)·null 허용 조건(ambiguous==true 만)·집계(시나리오는 포함, mention 만 분모 제외)가 세 곳에서 같다. `ambiguous_mention_count` 와 U1 "배분표와 실제 건수 일치"(33행) 의 충돌 여부: 배분표는 **시나리오** 단위(카테고리·관계 태그·위계, 32행), `ambiguous_mention_count` 는 **mention** 단위라 서로 다른 총계이며 시나리오 40건은 그대로 40건 — 충돌 없음. eval-harness §2 "오병합률과 미검출률은 반드시 분리 측정" 의 분모(유효 mention = `ambiguous` 아닌 mention)가 계획만으로 정해진다. 남는 것: 검증기가 `ambiguous_mention_count` 값과 실제 `ambiguous:true` 수의 일치를 검사하는지는 42행 위반 표본 7종에 없다 — 권고 R-9. 30행 "`ask_user.kind` 3종" 을 schema.json enum 으로 고정한다는 문구는 77행 `allowed` 별도 enum 과 병존 가능하나 시나리오 필드 중 `kind` 3종을 쓰는 곳이 없어 잔존 문구다 — 권고 R-12. |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `docs/wiki/packages/P1-schema/04-review.md` 115행 "결과: 완료", 116행 "승인: 사용자 (2026-09-05)" — 완료 커밋 `5dc95bb`(gitlog.sh: "docs(P1-schema): 완료 — verifier 04-review 완료 판정·사용자 승인, R8 R9 구현완료, 패키지 닫음"). `docs/wiki/packages/P3-er/04-review.md` 166행 "결과: 완료", 167행 "승인: 사용자 승인 2026-09-06 19:20" — 완료 커밋 `0527ab8`. 재검증 시점 gitlog: dev = main = `bdf9f70`, 승격 대기 0(P3-er 닫는 커밋이 main 에 올라가 있음). `docs/backlog.md` P1 절 "의존: 평가 명세(resolution-plan 3.7)" — `specs/S3.7-eval-spec.md` 존재. P4 게이트: backlog 머리말 "P4 파일럿 평가 이전에 P5 이후를 시작하지 않는다" — 본 패키지는 P1 이며 `S3.7` "적용: P1-pilot-dataset, P3-baselines, P4-pilot-eval" 순서상 P4 의 입력이다(01-plan 5행). INDEX.md 65행 "`P1-pilot-dataset` … 닫는 R `—`" 로 R 을 닫지 않는다는 01-plan 4행 기술 일치. 01-plan 5행 "두 패키지의 코드에 런타임 의존하지 않는다" 는 산출물 목록(30~38행: JSON·`scripts/validate_scenarios.py`·테스트)에 `app/` import 가 없어 정합. |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` P1 절 "- [ ] [eval-agent] 파일럿 데이터셋 30~50건 (승진·대명사·별칭·정상·신규) / 의존: 평가 명세(resolution-plan 3.7) / 수용기준: `data/scenarios/` JSON, 라벨 검수 완료" = 01-plan 52행. 5차 출력 "PASS  backlog 일치: 파일럿 데이터셋 30~50건 (승진·대명사·별칭·". `git diff docs/backlog.md`: 재검증 시점에도 `-` 줄 0, `+` 줄은 하위 불릿 9줄(U6 경로가 `packages/P1-pilot-dataset/evidence/<ts>-label-review.md` 로 갱신됨)과 리스크 로그 1줄뿐이며 하위 불릿 첫 줄이 "위 행의 문장·수용기준은 권위이며 바꾸지 않는다" 를 명시. 40건 배분(8+8+8+10+6=40)은 30~50 안이고 다섯 범주 각각 1건 이상. **"라벨 검수 완료" 의 기계 판정 방법(1차 판정 H-3) 해소**: 58행 "`evidence/<ts>-label-review.md` 머리 줄에 **eval-agent 가 아닌** 검수자 이름이 있고, 지적 표의 `열림` 상태가 0(`grep -c "열림"` 출력 0)이며 반영 상태에 U6 커밋 해시가 있다" + 48행 U7 evidence "검수 완료 출력 = `evidence/<ts>-label-review.md` 에 대한 `grep -c "반영 "` 과 `grep -c "열림"`(후자 0)" + 35행 형식 고정. 해석 4줄 모두 파일·명령·기대 출력이 있어 기계 판정 가능. `grep -c "열림"` 의 오탐 가능성은 권고 R-10. |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 5차 출력 "PASS  Refs 있음" 7줄(U1~U7). 01-plan 42~48행 각 단위 끝 "/ Refs: P1-pilot-dataset S3.7 …". 사용 태그 `S3.7`·`S3.1`·`D1`·`D6`·`D10`·`원칙1/8/9`·`L-002` 는 모두 INDEX.md 태그 어휘(53행 "`L-nnn` | 교훈 | `lessons/`")와 카드 존재(5차 "PASS 카드 존재: D1/D10/D6")로 확인. 재검증에서 U1·U3·U6·U7 문장이 바뀌었으나 Refs 는 유지됨. |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §1 "코드·문서·커밋에 키 문자열을 넣지 않는다" — 01-plan 38행 "README 에 … 검증기 실행법 한 줄. 값·키 금지". §4 "로컬 서버 이외로 데이터 전송(`curl -d …`) 금지 / 외부 API 호출은 코드(SDK)로, 키는 환경변수" — 25행 "검증기는 네트워크를 쓰지 않는다" 와 79행 "스크립트 API 호출 없음" 으로 외부 전송 경로 자체가 없어졌다(1차 판정에서 남겨 둔 "API 초안 생성을 택할 경우" 분기가 사라짐). §3 재귀 삭제·§5 개인정보(기획서 9장) — 데이터가 가상이며 삭제 명령 없음. **1차 권고 R-2 반영 확인**: 42행 U1 "일부러 깨뜨린 표본 7종(… 배분표 불일치·`manifest.json` 가상 성명 목록 밖 이름)을 전부 잡는 것이 완료 판정" — 가상 성명 검사가 U1 필수 검사가 됐다. 84행 리스크 문단의 "U1 에서 검사 항목으로 추가 가능" 은 갱신되지 않은 잔존 문구이나 42행(작업 단위)이 권위라 판정에 영향 없음(권고 R-12 에 기록). |

## 3. 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)

1차 판정(17:22, 이전 verifier 컨텍스트)은 H-1~H-3 세 건을 근거로 결과를 통과로 내지 않았고, 그 판정을 3차 기계 검증이 WARN 1 로 세어 **F-033bb1** 이 05-remediation.md 에 생겼다. 사용자가 세 건을 결정하고 메인 세션이 01-plan 에 문장으로 반영했으며(01-plan 3행 "결정 반영·… H-1~H-3 반영(재검증 대기)"), 아래는 새 verifier 컨텍스트의 재판정이다.

**H-1~H-3 상태 (재검증)**

- **H-1 해소** (점검표 4). 01-plan 77행 "H-1 확정(사용자): (1) `ambiguous` 는 `mentions[]` 단위 필드, (2) `ambiguous: true` 인 mention 만 `gold_person_id: null` 허용(검증기 예외), (3) 그 시나리오는 30~50 건수와 배분표에 포함하되 `manifest.json` 에 `ambiguous_mention_count` 를 별도로 두고 오병합률·미검출률·F1 분모에서 해당 mention 을 제외한다" · 42행 U1 "교차 검사 예외(H-1): … `ambiguous` 가 없거나 false 면 null 은 FAIL" · 44행 U3 "그 mention 을 `ambiguous: true`·`gold_person_id: null` 로 라벨한다(… 시나리오 자체는 건수에 포함, 해당 mention 만 지표 분모 제외)". 1차 판정이 요구한 (1)(2)(3) 이 각각 한 문장씩 있고, 이전 U3 "넣지 않는다" 문장은 사라져 세 문장이 서로 모순되지 않는다. `ambiguous_mention_count` 는 mention 총계이고 배분표는 시나리오 총계라 U1 "배분표와 실제 건수 일치" 와 충돌하지 않는다(점검표 4 근거).
- **H-2 해소** (점검표 2, 원칙8). 01-plan 79행 "생성 경로는 **eval-agent(opus) 가 자기 컨텍스트에서 JSON 을 직접 작성**한다(스크립트 API 호출 없음 …). `manifest.json` 필수 키: `generator.model_id` … `generator.prompt_ref`(위임 프롬프트를 저장한 `evidence/<ts>-gen-prompt.md` 경로), `generator.seed: null` + `seed_reason: "대화형 생성"`, `generator.same_family_as_judge: true` … **금지: 초안 위임 프롬프트에 ER 판정 프롬프트·호칭 사전(`app/er/dictionary`)·임계치 값을 넣지 않는다**". 1차 판정이 요구한 생성 경로 1개 선택·필수 키 4종·금지 문장이 모두 있고 25행 "하지 않는 것" 과 같은 경로다. `prompt_ref` 파일 저장 책임은 권고 R-8.
- **H-3 해소** (수용 기준 기계 판정). 01-plan 35행 산출물 "`docs/wiki/packages/P1-pilot-dataset/evidence/<ts>-label-review.md` — 라벨 검수 기록. **작성자는 verifier 또는 사용자**(verifier 의 쓰기 허용 경로가 `evidence/` 이므로 여기에 둔다 — H-3). 형식 고정: 머리 줄 `검수자: verifier (fable, 새 컨텍스트) | 표본: 40/40 | 사용자 검수: 함정 n건·new_person 지나가는 언급 m건`, 지적 표 열 `id | 시나리오 id | 지적 | 상태(반영 <해시> / 기각 <사유> / 열림)`. **열림 0 이 검수 완료 조건.**" · 47행 U6 "`evidence/<ts>-label-review.md` 에 남긴 지적" · 48행 U7 "`grep -c "반영 "` 과 `grep -c "열림"`(후자 0)" · 58행 해석 · 80행 "H-3 확정(사용자): 기록은 `evidence/<ts>-label-review.md` 한 파일 … 검수는 **새 verifier 컨텍스트**에서 하고 P4 04-review 에서 라벨을 재해석하지 않는다(R-3, P4 01-plan 인계)". 1차 판정의 택1 (i) 경로 이동이 채택돼 `verifier.md` 쓰기 목록("`packages/<id>/evidence/`") 과 충돌하지 않는다. backlog 하위 불릿 U6 도 같은 경로로 갱신됨(`git diff docs/backlog.md` `+` 줄). grep 오탐 가능성은 권고 R-10.

**F-033bb1 상태**: 6차 기계 검증(1절)에서 WARN 이 사라지면 `findings.py P1-pilot-dataset evidence/20260906-1736-verify-plan-6.txt --source verify-plan` 재실행으로 자동 해소된다. 실행 결과는 05-remediation.md 머리 줄과 소견 `상태:` 줄이 증거다. 실행(17:37, verifier): `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python .claude/scripts/findings.py P1-pilot-dataset docs/wiki/packages/P1-pilot-dataset/evidence/20260906-1736-verify-plan-6.txt --source verify-plan` → 출력 `05-remediation.md 갱신: 새 소견 0, 해소 1, 열림 0 (필수 0)` / `✓ F-033bb1  해소`. 05-remediation.md 머리 줄 `갱신: 2026-09-06 17:37 | 출처: verify-plan | 열림: 0 (필수 0) | 해소: 1`, F-033bb1 `상태: 해소 | … | 해소: 2026-09-06`. **F-033bb1 해소.**

**권고 (승인 조건 아님 — 실행 시 반영하고 04-review 에서 본다). 1차 권고 R-1~R-7 의 반영 여부와 재검증에서 추가한 R-8~R-12.**

- R-1 **반영됨** — 01-plan 77행 "`allowed` enum 은 `ask_user.kind` 와 별도 정의(`identity/new_person/none`, R-1)".
- R-2 **반영됨** — 42행 U1 위반 표본 7종째 "`manifest.json` 가상 성명 목록 밖 이름".
- R-3 **반영됨** — 80행 "검수는 **새 verifier 컨텍스트**에서 하고 P4 04-review 에서 라벨을 재해석하지 않는다(R-3, P4 01-plan 인계)". P4 01-plan 작성 시 두 줄을 실제로 옮기는지 P4 계획 검증에서 본다.
- R-4 **미반영(권고 유지)** — 검수 항목에 "발화가 고민 상담·감정 조언을 요청하는 대화가 아닌가(기획서 2장 제외)" 추가. 라벨 검수(`<ts>-label-review.md`) 지적 항목으로 verifier 가 직접 볼 수 있으므로 계획 수정 없이도 실행 가능.
- R-5 **미반영(권고 유지)** — `new_person` 6건의 두 하위 유형 각 3건 이상 고정·`manifest.json` 배분표에 하위 유형·`trap` 열. U5 배분표 생성 시 반영하면 된다.
- R-6 **미반영(P4 인계 기록)** — "ask_user 로 넘긴 mention" 을 오병합/미검출 어느 쪽에도 넣지 않고 제3 범주로 집계. H-1 (3) 의 `ambiguous` 분모 제외와 함께 P4 01-plan 의 지표 정의에 두 줄로 들어가야 한다.
- R-7 **유지** — `id` 전역 연번·카테고리별 5파일·`schema_version: 1` 을 U1 첫 커밋에.
- **R-8 (신규, 점검표 2 잔여) `prompt_ref` 저장 책임 미명시.** 79행은 `generator.prompt_ref` 가 "위임 프롬프트를 저장한 `evidence/<ts>-gen-prompt.md` 경로" 라고 정하지만 U1~U7 어느 단위도 그 파일을 저장한다고 쓰지 않았다. 권고: U2 착수 위임(첫 생성 호출) 시 **메인 세션이** 위임 프롬프트 전문을 `evidence/<ts>-gen-prompt.md` 로 저장하고, U2·U3·U4 가 서로 다른 위임 호출이면 `prompt_ref` 를 배열로 두어 호출마다 파일 하나씩 가리키게 한다. 또한 `same_family_as_judge: true` 는 P3-er 의 Claude 판정기 기준이므로 P4 가 OpenAI 판정기(`gpt-4o-mini`)로도 돌린다면 P4 가 판정 모델별로 이 값을 다시 적는다(P1 의 값은 생성 시점 기록으로 고정). 04-review 에서 `manifest.json` 의 `prompt_ref` 가 존재하는 파일을 가리키는지 `test -f` 로 본다.
- **R-9 (신규, 점검표 4 잔여) `ambiguous_mention_count` 일치 검사.** 77행이 `manifest.json` 에 이 키를 두라고 하지만 42행 U1 위반 표본 7종에는 "`ambiguous_mention_count` 와 실제 `ambiguous:true` mention 수 불일치" 가 없다. 배분표 불일치 검사(33행)를 mention 총계까지 확장해 위반 표본 8종째로 두는 것을 권고. 없으면 P4 가 분모를 manifest 값으로 읽을 때 실제와 어긋날 수 있다. 04-review 에서 검증기 테스트에 이 케이스가 있는지 본다.
- **R-10 (신규, 점검표 6 잔여) `grep -c "열림"` 오탐.** 35행 형식의 표 헤더 `상태(반영 <해시> / 기각 <사유> / 열림)` 이 `<ts>-label-review.md` 파일 안에 그대로 들어가면 헤더 줄 자체가 "열림" 을 포함해 `grep -c "열림"` 이 지적 0건이어도 최소 1 을 낸다(35행의 "열림 0 이 검수 완료 조건" 문장을 파일에 옮겨 적어도 같다). 머리 줄 형식(`검수자: … | 표본: … | 사용자 검수: …`)에는 "열림" 이 없어 안전. 권고: 파일의 표 헤더 열 이름은 `상태` 만 쓰고 값 어휘(`반영 <해시>` / `기각 <사유>` / `열림`)는 02·01-plan 에만 두거나, U7 명령을 셀 단위 패턴 `grep -cE '\| *열림 *\|'` 로 좁힌다. `grep -c "반영 "` 도 같은 이유로 셀 패턴이 안전하다. 04-review 에서 verifier 가 명령을 직접 실행해 확인한다.
- **R-11 (신규, L-002) 상태 열 갱신 주체.** 35행 "작성자는 verifier 또는 사용자" 를 상태 열(`반영 <해시>`)에도 적용한다 — U6 을 수행한 eval-agent 가 자기 지적을 "반영" 으로 닫지 않는다. U6 커밋 뒤 검수자(verifier 새 컨텍스트 또는 사용자)가 해시를 확인해 상태를 적는다. 계획 문장으로도 읽히지만 04-review 에서 파일 작성 이력(03-log·journal)으로 본다.
- **R-12 (신규, 잔존 문구·backlog 동기화) 판정 무관 정리 항목.** (a) 01-plan 30행 "`ask_user.kind` 3종" 을 schema.json enum 으로 고정한다는 문구 — 시나리오 필드에 `kind` 3종을 쓰는 곳이 없으므로(77행 `allowed` 는 별도 enum) U1 에서 넣지 않거나 주석으로 남긴다. (b) 84행 "U1 에서 검사 항목으로 추가 가능" — 42행이 필수로 확정했으므로 잔존 문구. (c) `docs/backlog.md` 하위 불릿 U1 "위반 표본 6종" vs 01-plan 42행 "7종" — 권위 행이 아닌 하위 불릿이라 수용 기준 판정과 무관하나 architect 가 backlog 를 만질 때 7종으로 맞춘다. 셋 다 계획 승인 조건이 아니다.

## 4. 결정
결과: 통과 — H-1·H-2·H-3 이 01-plan 42·44·77·79·80·35·48·58행에 문장으로 반영됐고 점검표 8행 모두 통과. 권고 R-4~R-12 는 승인 조건이 아니며 04-review 에서 본다. 6차 기계 검증(1절) FAIL 0 WARN 0 이 이 판정의 기계 근거다.
승인: 사용자 (2026-09-06) — 메인 세션 AskUserQuestion, 결정 A~G·H-1~H-3 포함
