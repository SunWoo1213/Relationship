# P1-pilot-dataset · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-09-06 21:05 · docs(P1-pilot-dataset): 계획·계획검증 승인, 패키지 착수 — 파일럿 데이터셋 40건·검증기·verifier 라벨 검수 · 4c80c31
- 변경: 01-plan(architect 초안 + 결정 A~G·H-1~H-3 확정 블록), 02-plan-verify(verifier 1차 보류 → 2차 통과, 기계 검증 1~6차), 05-remediation(F-033bb1 해소), evidence 6파일, backlog P1 하위 불릿 U1~U7, CURRENT active, 03-log 생성
- 이유(기획서·카드 연결): S3.7 평가 명세의 입력 데이터셋(backlog P1 "파일럿 데이터셋 30~50건"). P4 게이트 선행. eval-harness §1 스키마를 persons·events·seed_persons·expected_ask_user.allowed·ambiguous 로 확장(D1 D3 D10 근거)
- 정합성 확인: 원칙 1 4 7 8 9 / D1 D3 D10 / S3.7 S3.1 S3.2 / security(가상 이름·키 미기록·네트워크 없음) — 위반 없음(verifier 점검표 8행 통과)
- 남은 것 · 다음 단위: U1 스키마·검증기·테스트(eval-agent, L-004 승인 후). R-8: U2 위임 시 메인 세션이 위임 프롬프트를 evidence/<ts>-gen-prompt.md 로 저장
- Refs: P1-pilot-dataset S3.7 S3.1 S3.2 D1 D3 D10 원칙8 F-033bb1

## 2026-09-06 18:01 · feat(P1-pilot-dataset): U1 시나리오 스키마·검증기·검증기 테스트 · pending
- 변경: `data/scenarios/schema.json`(시나리오 객체, Draft 2020-12, schema_version 1), `data/scenarios/manifest.schema.json`(매니페스트 스키마 — schema.json $defs 가 아닌 별도 파일), `data/scenarios/manifest.json`(counts 전부 0·total 0·virtual_names []·generator 키 5종 null), `scripts/validate_scenarios.py`(검사 (0)~(10) 함수 분리, `--dir`/`--json`/`--strict`, 네트워크·DB·app import 없음), `tests/test_validate_scenarios.py`(35건), `requirements-dev.txt`(jsonschema==4.26.0), evidence 2파일
- 이유(기획서·카드 연결): S3.7 이 요구하는 "오병합률·미검출률 분리 측정" 의 입력을 기계가 검사하게 한다. 결정 A(persons)·B(events type·occurred_at_kind)·C(schedule 라벨 없음)·D+H-1(expected_ask_user.allowed·mentions[].ambiguous)·E(seed_persons)·F+H-2(generator 키)를 enum·필수 키로 고정. 위반 표본 8종(01-plan 42행)을 전부 잡는 것이 U1 완료 판정
- 정합성 확인: 원칙1(함정·trap 라벨로 오병합을 측정 가능하게) / 원칙4·D10(허용 집합 라벨이라 T_merge 스윕이 라벨을 위반하지 않음) / 원칙7(인물–인물 필드 없음) / 원칙8(같은 입력 → 같은 요약, Issue 정렬 결정적, generator.seed=null·seed_reason 으로 재현 불가를 숨기지 않음) / S3.1(events.type 7종·relation_tag 5종·hierarchy 3종 enum 이 `app.db.models` 튜플과 순서까지 일치함을 테스트가 대조, 코드 import 없음) / R-1(allowed enum ≠ ask_user.kind, schedule 제외) · R-2(virtual_names 화이트리스트 검사) · R-7(id 전역 연번 `sc-001`·카테고리별 5파일) · R-8(prompt_ref string|string[]) · R-9(ambiguous_mention_count 일치 검사) / security(가상 이름만·키 없음·네트워크 없음) — 위반 없음
- 남은 것 · 다음 단위: U2 promotion 8건 + alias 8건(함정 3건 이상). R-8 대로 메인 세션이 U2 위임 프롬프트를 `evidence/<ts>-gen-prompt.md` 로 저장하고 `manifest.generator` 를 채운다. registry 행·README 는 U7. 남긴 결정 2건 — (a) 없는 시나리오 파일은 기본 0건, `--strict` 면 FAIL(U5·U7 수용 기준 검증은 `--strict` 로), (b) 이름 판정 규칙 = display_name 전체 + 한글 2~4자 alias(`utterances` 본문은 검사하지 않는다 — 사람 검수 항목) **U5 에서 추가(사용자 결정)**: 파일명 ↔ `category` 대응 검사(검사 11).
- Refs: P1-pilot-dataset S3.7 S3.1 D1 D3 D6 D10 원칙1 원칙4 원칙7 원칙8 R-1 R-2 R-7 R-8 R-9
