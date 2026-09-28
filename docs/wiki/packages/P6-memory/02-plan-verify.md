# P6-memory · 계획 검증 (02-plan-verify)

대상: 01-plan.md (1차 개정본 2026-09-28 — 결정 A~G 사용자 확정, 1차 판정의 H-1~H-3·R-1~R-9 반영, 머리 "개정 이력: 1차" 줄) | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002) | 날짜: 2026-09-28 (1차 13:41~13:49 → 2차 재검증 14:06~14:15 → 3차 확인(승인 전 변경, 범위 한정) 14:31~14:35 → **4차 확인(H-4 닫힘만) 14:40~14:44**)

근거 해시(`bash .claude/scripts/gitlog.sh P6-memory D14`, 2026-09-28 14:06 — 1차 13:41 과 같은 값): dev = `2de7416`(CR-002 문서 커밋, 미푸시 ahead 1) · main = origin/main = `1e4afb4`. 태그 `P6-memory` 커밋 3건(`2de7416`·`9cb35b6`·`5dc95bb`), `D14` 는 `2de7416` 뿐. 1차와 2차 사이에 새 커밋 없음. 미커밋 변경은 `docs/wiki/HANDOFF.md`·`journal.md` 와 이 패키지 폴더뿐 — 제품 코드 0(`evidence/20260928-1410-verifier-2-fact-checks.txt` §16 `git status --short` 에서 `docs/` 밖 변경 0). 01-plan 8행의 시작 해시 `2de7416` 과 일치.

이 문서의 구성: §1 에 2차 기계 검증 출력(2차 = 판정 전, 2b = 판정 후)과 1차 출력 기록, §2 에 **2차 점검표(유일한 8행 표)**, 그 아래 1차 점검표 원문을 인용 블록으로 보존(행 앞에 `> ` 만 붙였다 — `verify-plan.sh` 가 `| 1 |`~`| 8 |` 행을 파일 전체에서 세어 정확히 8행을 요구하기 때문), §3 에 1차 보류의 닫힘 판정·권고 반영 여부·2차 새 권고, §4 결정.

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)

### 2차 (개정본 대상, 이 문서를 고치기 전 — WARN 1 은 1차 판정이 남아 있어서 생긴 것)
명령: `bash .claude/scripts/verify-plan.sh P6-memory | tee docs/wiki/packages/P6-memory/evidence/20260928-1410-verifier-2-verify-plan.txt`
```
== verify-plan P6-memory  (2026-09-28 14:06) ==
PASS  존재: docs/wiki/packages/P6-memory/01-plan.md
PASS  존재: docs/wiki/packages/P6-memory/02-plan-verify.md
PASS  카드 존재: D06
PASS  카드 존재: D11
PASS  카드 존재: D14
PASS  카드 존재: D6
PASS  카드 존재: D9
PASS  패키지 id 등록됨: P1-schema
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P6-memory
PASS  검증 항목 존재: R11
PASS  검증 항목 존재: R8
PASS  Refs 있음: - [ ] U1 골격 — 설정 상수 6개(그중 환경변수�
PASS  Refs 있음: - [ ] U2 패턴 감지 규칙 — `detect_patterns(ctx, pers
PASS  Refs 있음: - [ ] U3 `pattern:` 접두 키 보호 — `update_person(fac
PASS  Refs 있음: - [ ] U4 사실 추출기 — `FactExtractor.extract(person,
PASS  Refs 있음: - [ ] U5 승격 — `promote_person(ctx, person_id, extracto
PASS  Refs 있음: - [ ] U6 루프 연결 — `after_record(ctx, person_ids, ex
PASS  Refs 있음: - [ ] U7 (결정 G 가 (ii) 일 때만) 루프 직접 사실
PASS  Refs 있음: - [ ] U8 수용 기준 기계 검증·문서 — 아래 판�
PASS  backlog 일치: 승격 후 사실→원문 링크 존재, 설정된 기간·
PASS  의존 완료: P5-loop
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
WARN  보류 2 건 — 결과는 통과가 될 수 없다
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: app/memory/__init__.py
PASS  registry 중복 없음: app/memory/types.py
PASS  registry 중복 없음: app/memory/patterns.py
PASS  registry 중복 없음: app/memory/extract.py
PASS  registry 중복 없음: app/memory/promote.py
PASS  registry 중복 없음: tests/test_memory_patterns.py
PASS  registry 중복 없음: tests/test_memory_extract.py
PASS  registry 중복 없음: tests/test_memory_promote.py
PASS  registry 중복 없음: tests/test_memory_loop.py
== 결과: FAIL=0 WARN=1 ==
```
FAIL 0. WARN 1 은 이 실행 시점의 02(1차 판정)가 아직 남아 있어서 난 것(`F-033bb1`). 메인 세션이 개정 직후 돌린 `evidence/20260928-1356-rev1-verify-plan.txt`(13:56)와 줄 단위로 같다. 개정본 01-plan 자체에 대한 FAIL·WARN 은 없다(카드·backlog·Refs·의존·registry 전부 PASS).

### 2b (2차 판정을 이 문서에 쓴 뒤 재실행)
명령: `bash .claude/scripts/verify-plan.sh P6-memory | tee docs/wiki/packages/P6-memory/evidence/20260928-1415-verifier-2b-verify-plan.txt`
```
== verify-plan P6-memory  (2026-09-28 14:15) ==
PASS  존재: docs/wiki/packages/P6-memory/01-plan.md
PASS  존재: docs/wiki/packages/P6-memory/02-plan-verify.md
PASS  카드 존재: D06
PASS  카드 존재: D11
PASS  카드 존재: D14
PASS  카드 존재: D6
PASS  카드 존재: D9
PASS  패키지 id 등록됨: P1-schema
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P6-memory
PASS  검증 항목 존재: R11
PASS  검증 항목 존재: R8
PASS  Refs 있음: - [ ] U1 골격 — 설정 상수 6개(그중 환경변수�
PASS  Refs 있음: - [ ] U2 패턴 감지 규칙 — `detect_patterns(ctx, pers
PASS  Refs 있음: - [ ] U3 `pattern:` 접두 키 보호 — `update_person(fac
PASS  Refs 있음: - [ ] U4 사실 추출기 — `FactExtractor.extract(person,
PASS  Refs 있음: - [ ] U5 승격 — `promote_person(ctx, person_id, extracto
PASS  Refs 있음: - [ ] U6 루프 연결 — `after_record(ctx, person_ids, ex
PASS  Refs 있음: - [ ] U7 (결정 G 가 (ii) 일 때만) 루프 직접 사실
PASS  Refs 있음: - [ ] U8 수용 기준 기계 검증·문서 — 아래 판�
PASS  backlog 일치: 승격 후 사실→원문 링크 존재, 설정된 기간·
PASS  의존 완료: P5-loop
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: app/memory/__init__.py
PASS  registry 중복 없음: app/memory/types.py
PASS  registry 중복 없음: app/memory/patterns.py
PASS  registry 중복 없음: app/memory/extract.py
PASS  registry 중복 없음: app/memory/promote.py
PASS  registry 중복 없음: tests/test_memory_patterns.py
PASS  registry 중복 없음: tests/test_memory_extract.py
PASS  registry 중복 없음: tests/test_memory_promote.py
PASS  registry 중복 없음: tests/test_memory_loop.py
== 결과: FAIL=0 WARN=0 ==
```
2b: FAIL 0 · WARN 0. `PASS  보류 0건` — 1차의 `F-033bb1`(의도된 WARN)이 사라졌다(05-remediation 에서 해소 처리).

### 1차 기록 (2026-09-28 13:41 / 13:49 — 보존)
1차 실행(`evidence/20260928-1345-verifier-verify-plan.txt`, 02 부재로 `FAIL  없음: …/02-plan-verify.md` 1건, 나머지 PASS, `== 결과: FAIL=1 WARN=0 ==`)과 1차 문서 작성 후 실행(`evidence/20260928-1355-verifier-verify-plan-2.txt`, `WARN  보류 2 건` 1건 외 PASS, `== 결과: FAIL=0 WARN=1 ==`)의 전체 출력은 위 두 evidence 파일에 있다. 1차 FAIL 은 `F-95c005`(해소), WARN 은 `F-033bb1` 로 05-remediation 에 있다. 1차의 사실 주장 확인 evidence 는 `evidence/20260928-1350-verifier-fact-checks.txt`(23항, 이하 "fact-checks §n").

### 2차 evidence (이 판정이 새로 만든 것)
- `evidence/20260928-1410-verifier-2-hold-recheck.txt` — 05-remediation 의 H-1~H-3 해결 단계 표 "완료 판정 명령" 8개를 표에서 awk 로 잘라내 **그대로** 실행한 출력(손 입력 없음). 이하 "hold-recheck".
- `evidence/20260928-1410-verifier-2-fact-checks.txt` — 개정본이 새로 주장한 코드 위치(`RecordOutcome`·862행·`_owned_person`·registry 38행)와 새 위험(기본 추출기 해소 시점) 확인 16항. 이하 "fact-checks-2 §n".

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표") — 2차 판정
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다. 1차와 달라진 행은 3(닫힘)·2(조건 해제)·7(R-2 반영)·8(R-5 반영)이고 나머지는 1차 근거가 그대로 유효한지 개정본 행 번호로 다시 확인했다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 58~63행 제외 열 "고민 상담 기능 / 인물 간(A–B) 관계 저장 / 관계 태그 필터링 / 상담 페르소나 / 톤 설정 / 음성 입력 / 네이티브 앱"(2차 sed 로 재확인). 01-plan 34행 "하지 않는 것" 에 "**고민 상담·감정 대화, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성, 네이티브 앱**(원칙7) — 추출기가 뽑는 사실은 **그 한 인물**에 관한 기록된 사실뿐이다 … 검증기는 스키마 밖 키를 거부한다". 결정 D-5(174행) "인물 간 관계 키는 두지 않는다(원칙7)". 개정으로 범위가 넓어지지 않았다: 1차 개정이 더한 것은 `.env.example` 두 줄(H-1)·trace 키 2개(H-2)·grep 표기(H-3)·`RecordOutcome` 필드 2개(R-4·R-7)·소유 검사 재사용(R-5)뿐이며 산출물 파일 표(53~61행)의 파일 집합은 `.env.example` 행 추가 외 1차와 같다. 새 엔드포인트 없음(32행), UI 없음(28행) |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | 원칙6 CLAUDE.md "반복 패턴 감지(규칙 기반, D9) … LLM은 패턴 문장화만" ↔ 01-plan 19행 "SQL 과 파이썬만 쓰고 LLM·임베딩을 부르지 않는다", 199행 "`app/memory/patterns.py` 는 `app.memory.extract`·`app.er.judge`·`app.embedding` 을 import 하지 않는다", 판정 9행 "추출기 호출 0회, `memory_pattern` trace `tokens_in=tokens_out=0`". 원칙8: C-3 값 형식·C-4 confidence 1.0 결정적, 65행 "모든 테스트는 **실 키·네트워크 없이** 돈다", 205행 "추출 품질은 측정되지 않는다" 를 숨기지 않음. 원칙9: 결정 F(186행) `memory_pattern` output 에 `window_days`·`min_count` 가 들어가 D14 13행 "실제 쓴 기간·횟수를 패턴 trace 에 기록" 을 충족(1차 조건부의 근거였던 H-2 가 닫힘 — hold-recheck F-56df6c 1~3단계). 원칙1~4(ER): 31행 "`app/er/` 수정 — P4b 게이트 수치의 근거 코드다 … import 해서 쓰기만", 200행 `app/agent/` 금지 리터럴 grep 기준선(fact-checks §6). 원칙5: 28행 "프론트 3화면·인물 카드 원문 펼치기 UI(P8-frontend, 원칙5)" 제외. 원칙7: 행 1 |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | **D14** `D14-pattern-window-config.md` 11행 "`.env.example` 에 기본값 줄" ↔ 01-plan 60행 "`.env.example` \| 두 줄 추가: `PATTERN_WINDOW_DAYS=`·`PATTERN_MIN_COUNT=`(값은 비워 두고 주석으로 … 설명만 — 비밀 없음)" · 67행 U1 판정 "`grep -n PATTERN .env.example`(2건)" (hold-recheck F-bbf7fa 1단계 1건·2단계 5건 ≥ 3 — **1차 H-1 닫힘**; 3단계 실파일 `grep -n PATTERN .env.example` 은 0건이 맞다 — U1 구현 몫이라 계획 판정 조건이 아니며 04-review 에서 U1 evidence 로 본다). D14 13행 "실제 쓴 기간·횟수를 패턴 trace(`memory_pattern`)에 기록한다" ↔ 186행 output `{person_id, window:{from,to}, window_days, min_count, counts:{type:n}, changes:[…]}` + "`window_days`·`min_count` 는 **이번 판정에 실제로 적용한** `pattern_config()` 값이다(D14 13행 …)" · 68행 U2 "이번 판정에 실제로 쓴 기간·횟수를 output 의 `window_days`·`min_count` 에 기록한다(D14, 결정 F)" · 97행 판정 3행 "`window_days=90`·`min_count=2` 가 기록된다" (hold-recheck F-56df6c 1~3단계 각 1건 — **1차 H-2 닫힘**). D14 10행 "패턴 판정에 LLM 을 쓰지 않는다"(19·199행), 11행 "양의 정수만, 아니면 오류, 비우면 기본값"(55행 `pattern_config(env=None)` "양의 정수만·아니면 `InvalidValue`·비우면 기본값"), 12행 "1년 = 365일 고정 … 창 = `[now − PATTERN_WINDOW_DAYS일, now]`, `occurred_at` 기준"(C-2 162행 "UTC 절대 시간(일수 × 24시간)"). **D11** `D11-llm-provider-registry.md` 26행 "표·스위치를 `judge.py` 에서 import 한다(자체 표 금지)" ↔ D-1(170행 "자체 표 금지")·U4(70행 `select_provider`·`call_with_error_mapping` import); 10행 "기존 오류 어휘 6종" ↔ 70행 "오류 어휘는 기존 6종만"; 29행 "키·프롬프트 원문은 로그·예외·evidence 에 남지 않는다" ↔ 186행 "프롬프트·키 원문 미기록(security §1)"; 9행 "`FakeJudge` 는 등록표 **밖**" ↔ D-3(172행) `FakeFactExtractor` 등록표 밖. **D6** `D06-display-name-policy.md` — 234행 "이 패키지는 `display_name` 을 다루지 않는다", 30행 `update_person` 시그니처 불변 → 충돌 없음. **D9** `D09-pattern-rule.md` 3행 "상태: 대체됨(→D14, CR-002 …)" — 01-plan 5행 "D14(D9 대체, CR-002)", U2·U3 Refs 가 `D14 D9` 병기(R-2 반영) |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | **S3.5** `S3.5-memory-promotion.md` 6행 "승격 트리거: 같은 인물의 미승격 events ≥ 5건" ↔ 해석 ㄱ(84행)·U5(71행 `MEMORY_PROMOTE_MIN_EVENTS`); 7행 "LLM이 사실 후보 추출 → `person_facts` upsert → 각 사실을 `fact_sources`로 근거 이벤트에 연결" ↔ U4·U5; 8행 "같은 type 이 설정된 기간(`PATTERN_WINDOW_DAYS`, 기본 365일) 내 설정된 횟수(`PATTERN_MIN_COUNT`, 기본 3회) 이상 → `pattern:{type}` 사실 (규칙, D14 …). LLM은 문장화만" ↔ U2·결정 E; 9행 "**원문은 어떤 경우에도 삭제하지 않는다**" ↔ 198행 "**원문(`events`) 삭제·수정 금지.** 권위 있는 판정은 판정 표 13행 테스트 … 보조 grep 은 **`Event` 대상만** … `PersonFact`·`FactSource` … 의 삭제는 이 불변식의 대상이 아니며 허용된다" — grep 이 `delete\(Event|update\(Event|\.raw_utterance\s*=[^=]|\.content\s*=[^=]` 로 좁혀져 C-5(i)·D-6·U2 와의 자기 모순이 없어졌다(hold-recheck F-14ad9f 1단계 1건·2단계 `0` — **1차 H-3 닫힘**). **S3.1** `S3.1-schema-v2.md` 8~10·14행 `person_facts`·`fact_sources(fact_id, event_id)`·`events`·`agent_traces` — 29행 "스키마 v2 변경·마이그레이션 없음", 결정 B(ii) 는 `agent_traces.output` JSONB 조회만(fact-checks §9), 판정 20행 `alembic check`. **S3.2** `S3.2-tools-v2.md` 9행 `update_person (person_id, facts?, new_alias?, display_name?) → Person` ↔ 30행 "시그니처를 그대로 두고 **값 검사 한 줄**만", 판정 20행 `tools_check.py` 7/7. 16행 "모든 툴 호출은 `agent_traces`에 … 기록" ↔ 결정 F `memory_*` step. 임계치 2개·`ask_user` 비동기는 이 패키지가 건드리지 않음(31행 `app/er/` 무수정) |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `packages/P5-loop/04-review.md` 196행 "결과: 완료", 197행 "승인: 사용자 (2026-09-25)"(2차 sed 재확인), 완료 처리 커밋 `f9bfba7`(gitlog 최근 20건). 190행 인계 "승격 훅은 `app/agent/loop.py` 의 `_record_impl`(기록 단계, `loop_record` 한 행) 뒤에 건다" ↔ 01-plan 10·22행·U6. verify-plan 2차 `PASS  의존 완료: P5-loop`, `PASS  P4 게이트 통과 (P4b-er-redesign)`. `docs/backlog.md` P6 "의존: P5". CR-002 이행완료(`CR-002.md` 3행), `CURRENT.md` `active: none` / `frozen: none`. 01-plan 8행 시작 해시 `2de7416` = 현재 dev HEAD(gitlog 14:06) — R-1 반영 |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` P6 첫 항목 "승격 후 사실→원문 링크 존재, 설정된 기간·횟수 규칙(기본 365일 3회)으로 `pattern:{type}` 사실 생성" = 01-plan 78행(2차 sed 로 재확인, fact-checks §21). verify-plan 2차 `PASS  backlog 일치`. 해석 표 ㄱ~ㄹ(82~87행)은 네 구절만 풀었고 개정으로 새 기준을 더하지 않았다(ㄷ 에 D14 trace 키 문장이 붙었으나 이는 판정 방법이지 기준 추가가 아니다) |
| 7 | 작업 단위마다 Refs 태그 | 통과 | verify-plan 2차 `PASS  Refs 있음` U1~U8 8건. 태그가 가리키는 카드 전부 존재(`PASS  카드 존재` D06·D11·D14·D6·D9, `검증 항목 존재` R8·R11). U2 Refs "P6-memory D14 D9 S3.5 R11 원칙6 원칙8 원칙9", U3 Refs "P6-memory D14 D9 S3.2 원칙6" — 대체된 D9 를 D14 와 병기(R-2 반영). U1 Refs 에 `D14 CR-002` 추가. 태그별 이력 `D14` = `2de7416` 뿐, `P6-memory` 3건 코드 없음(계획 9행과 일치) |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §1 "에이전트는 `.env.example`에 **이름만** 적는다" ↔ 01-plan 60행 "값은 비워 두고 주석으로 … 설명만 — 비밀 없음, security §1", 67행 U1 "이름 + … 설명 주석만, 비밀 없음"; §1 "로그·trace에 키·비밀을 남기지 않는다" ↔ 186행 `memory_error` "프롬프트·키 원문 미기록(security §1)". §5 "모든 조회는 `user_id` 조건을 넣는다" ↔ 68행 U2·71행 U5 "첫 줄에서 `app/tools/persons.py` 의 `_owned_person(ctx.session, person_id, ctx.user_id)` 를 재사용 … 새 소유 검사 함수를 만들지 않는다" + 다른 `user_id` 인물 id 부정 테스트 각 1건(R-5 반영; `_owned_person` 은 persons.py 371행에 실재 — fact-checks-2 §12). §4 셸 `DROP`/`TRUNCATE`·외부 전송 명령 없음(판정 표 전부 pytest·grep·alembic check). §3 재귀 삭제 없음. `.env.example` 소유는 하네스(registry 38행, fact-checks-2 §13) — 계획이 그렇게 적었다(60행) |

### 1차 점검표 (2026-09-28 13:49, 원문 보존 — 행 앞에 `> ` 만 붙였다)

> | # | 항목 | 결과 | 근거(카드·절·인용) |
> |---|------|------|--------------------|
> | 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 56~63행 제외 열 "고민 상담 기능 / 인물 간(A–B) 관계 저장 / 관계 태그 필터링 / 상담 페르소나 / 음성 입력 / 네이티브 앱". 01-plan 33행 "하지 않는 것"에 여섯 항목 전부 열거하고 이유를 붙였다: "추출기가 뽑는 사실은 **그 한 인물**에 관한 기록된 사실뿐이다 … 두 인물 사이의 관계는 사실 키 어휘에 자리가 없고(결정 D-5), 감정 해석·조언 문장도 만들지 않는다. 검증기는 스키마 밖 키를 거부한다". 결정 D-5(171행) 고정 어휘 9키에 인물 간 관계 키 없음("인물 간 관계 키는 두지 않는다(원칙7)"). 브리핑 문장화·화면은 P6-briefing·P8 로 미룸(26~27행). CLAUDE.md 원칙7 경계 문장과 충돌 없음 |
> | 2 | 불변 원칙 1~9 위반 없음 | 통과 (H-2 조건부) | 원칙6 CLAUDE.md "반복 패턴 감지(규칙 기반, D9) … LLM은 패턴 문장화만" ↔ 01-plan 18행 "SQL 과 파이썬만 쓰고 LLM·임베딩을 부르지 않는다", 196행 "`patterns.py` 는 `app.memory.extract`·`app.er.judge`·`app.embedding` 을 import 하지 않는다", 판정 9행 "추출기 호출 0회, tokens 0". 문장화는 결정 E 로 P6-briefing 에 넘김 — 원칙6 "LLM 은 문장화만" 의 범위 안. 원칙8: 규칙 결정적(C-3 값 형식·C-4 confidence 1.0), 가짜 추출기로 네트워크 0(63행), 실패도 결과(201행 "추출 품질은 측정되지 않는다"). 원칙9: 결정 F 어휘 3종에 입력·출력·근거 id·토큰(183행) — 단 D14 가 요구하는 "실제 쓴 기간·횟수" 가 F 의 `memory_pattern` output 스키마에 없다(→ H-2, 행 3 에서 보류). 원칙1~4(ER)는 30행 "`app/er/` 수정 없음 … import 해서 쓰기만" 으로 건드리지 않음, fact-checks §6 기준선(`app/agent/` 에 `T_merge|T_new|confidence` 0건, `create_person(` 1건 = loop.py 1227행)이 U6 뒤에도 그대로여야 함(판정 19행). 원칙5: 27행 UI 없음. 원칙7: 행 1 |
> | 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | **보류** (H-1·H-2) | **D14** `D14-pattern-window-config.md` 11행 "기본값은 `app/settings.py` 한 곳 … 환경변수 … (양의 정수만, 아니면 오류, 비우면 기본값). **`.env.example` 에 기본값 줄.**" → 01-plan U1(65행)·고치는 파일 표(52~59행)에 `.env.example` 이 없다. `CR-002.md` 16행도 "`.env.example` 에 기본값 줄 추가" 를 요구. 현재 `.env.example` 에 `PATTERN` 줄 0(fact-checks §16). → **H-1**. D14 13행 "실제 쓴 기간·횟수를 패턴 trace(`memory_pattern`)에 기록한다" → 01-plan 해석 ㄷ(84행)·판정 3행(95행 "trace 에 90/2 가 기록된다")은 요구하지만, 구현 계약인 결정 F(183행) `memory_pattern` output `{person_id, window:{from,to}, counts, changes}` 에 기간·횟수 키가 없고 U2(66행)도 적지 않았다 → **H-2**. 나머지 D14 항목 일치: "패턴 판정에 LLM 을 쓰지 않는다"(18·196행), "1년 = 365일 고정 … 창 = `[now − PATTERN_WINDOW_DAYS일, now]`, `occurred_at` 기준"(C-2 159행 "UTC 절대 시간(일수 × 24시간)"), 환경변수 검증(54행 "양의 정수만·아니면 `InvalidValue`·비우면 기본값"). **D11** `D11-llm-provider-registry.md` 26행 "`caller_from_env()` 는 표·스위치를 `judge.py` 에서 import 한다(자체 표 금지)", 10행 "기존 오류 어휘 6종 … 어휘를 늘리지 않는다", 29행 "키·프롬프트 원문은 로그·예외·evidence 에 남지 않는다" ↔ 01-plan D-1(167행 "자체 표 금지"), U4(68행 "오류 어휘는 기존 6종만"), F(183행 "프롬프트·키 원문 미기록"). `FakeFactExtractor` 는 등록표 밖(D-3, D11 9행 `FakeJudge` 규약과 같음). 선례 `app/agent/propose.py` 90~95행이 실제로 `select_provider`·`call_with_error_mapping`·`call_with_gemini_error_mapping` 을 import 한다(fact-checks §11·§12). **D6** `D06-display-name-policy.md` 7행 "`update_person(display_name=…)`은 사용자 확인 … 별칭은 절대 삭제하지 않는다" — 이 패키지는 `display_name`·별칭을 다루지 않고(229행) `update_person` 시그니처 불변(29행) → 충돌 없음. **D9** 는 대체됨(3행 "상태: 대체됨(→D14)") — 01-plan 4행이 "D14(D9 대체, CR-002)" 로 바르게 적음 |
> | 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | **S3.5** `S3.5-memory-promotion.md` 6행 "승격 트리거: 같은 인물의 미승격 events ≥ 5건" ↔ 01-plan 해석 ㄱ·U5(69행 `MEMORY_PROMOTE_MIN_EVENTS`=5); 7행 "LLM이 사실 후보 추출 → `person_facts` upsert → 각 사실을 `fact_sources`로 근거 이벤트에 연결" ↔ U4·U5; 8행 패턴 규칙 ↔ U2; 9행 "**원문은 어떤 경우에도 삭제하지 않는다**" ↔ 195행 불변식·판정 13행. 결정 C-5(i) 패턴 행 삭제는 원문(`events`)이 아니라 파생 요약(`person_facts`) 삭제이며 `fact_sources` CASCADE 는 링크 행이다(`app/db/models.py` 162~167행, fact-checks §9) — `events` 에 대한 UPDATE/DELETE 코드는 `app/` 전체에 0(fact-checks §8), 계획도 69행 "`events` 행은 읽기만 한다" → 충돌 없음(단 불변식 grep 표기는 H-3). **S3.1** `S3.1-schema-v2.md` 8~10·14행 `person_facts`·`fact_sources(fact_id, event_id)`·`events`·`agent_traces` 그대로 — 결정 B(ii) 는 `agent_traces.output`(JSONB, models.py 256행) 의 기존 열을 조회할 뿐 컬럼·테이블을 더하지 않는다(28행 "스키마 v2 변경·마이그레이션 없음", 판정 20행 `alembic check`). B(iii) 이 아닌 (ii) 로 확정됐으므로 CR 불필요. **S3.2** `S3.2-tools-v2.md` 9행 `update_person (person_id, facts?, new_alias?, display_name?) → Person` — 29행 "시그니처를 그대로 두고 **값 검사 한 줄**만", 판정 20행 `tools_check.py` 7/7. 16행 "모든 툴 호출은 `agent_traces`에 … 기록" — 패턴·승격은 툴을 거치지 않는 대신 결정 F 의 `memory_*` step 으로 기록. 임계치 2개·`ask_user` 비동기는 이 패키지가 건드리지 않음(`app/er/` 무수정, 30행) |
> | 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `packages/P5-loop/04-review.md` 196행 "결과: 완료", 197행 "승인: 사용자 (2026-09-25)", 완료 처리 커밋 `f9bfba7`(gitlog 최근 20건). 190행 인계 "승격 훅은 `app/agent/loop.py` 의 `_record_impl`(기록 단계, `loop_record` 한 행) 뒤에 건다" ↔ 01-plan 21행·U6. P4 게이트: verify-plan `PASS  P4 게이트 통과 (P4b-er-redesign)`, P5 04-review 92행 "`144:결과: 완료`". `docs/backlog.md` 79행 "의존: P5". CR-002 는 이행완료(`CR-002.md` 3행, 커밋 `2de7416`), `CURRENT.md` `frozen: none`. 계획 7행 시작 해시 `1e4afb4` 는 스냅샷 시점 값이고 현재 dev HEAD 는 `2de7416`(문서만, `app/` 무변경 — 커밋 파일 목록 14개 전부 docs/.claude/CLAUDE.md) → R-1 |
> | 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 79행 "승격 후 사실→원문 링크 존재, 설정된 기간·횟수 규칙(기본 365일 3회)으로 `pattern:{type}` 사실 생성" = 01-plan 76행(fact-checks §21). verify-plan `PASS  backlog 일치`. 해석 표 ㄱ~ㄹ(80~85행)은 새 기준을 더하지 않고 네 구절만 풀었다 |
> | 7 | 작업 단위마다 Refs 태그 | 통과 | verify-plan `PASS  Refs 있음` U1~U8 8건. 각 Refs 에 `P6-memory` 와 R/D/S 태그가 있고, 태그가 가리키는 카드는 전부 존재(`PASS  카드 존재` 5건·`검증 항목 존재` 2건). 태그별 이력: `D14`·`S3.5`·`R11` = `2de7416` 뿐, `P6-memory` = `2de7416`·`9cb35b6`·`5dc95bb`(코드 없음, 계획 8행과 일치). U2·U3 Refs 가 대체된 `D9` 를 쓴다 → R-2(권고) |
> | 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §1 "로그·trace에 키·비밀을 남기지 않는다" ↔ 01-plan 183행 "`memory_error` … 프롬프트·키 원문 미기록(security §1)"; §1 ".env.example에 **이름만**" ↔ H-1 조치도 이름·기본값 설명만. §4 "셸에서 `DROP`/`TRUNCATE` 금지", "로컬 서버 이외로 데이터 전송 금지" — 계획에 셸 삭제·외부 전송 명령 없음, 외부 호출은 기존 등록표(SDK)뿐. §5 "모든 조회는 `user_id` 조건을 넣는다" — 공개 함수 `detect_patterns(ctx, person_id)`·`promote_person(ctx, person_id, …)` 의 소유 검사 명시가 없다 → R-5(권고; 루프가 넘기는 id 는 `_owned_person` 을 지난 값이라 위반은 아님). 재귀 삭제·강제 푸시 없음 |

### 1차 "위임 프롬프트가 지정한 사실 주장 확인" (evidence `20260928-1350-verifier-fact-checks.txt`, 보존)

| 주장(1차 01-plan 행) | 확인 | 결과 |
|------------------|------|------|
| `propose.py` `facts.key` 가 enum 없는 문자열(20행) | §1: 150행 `"key": {"type": "string"}` | 참 |
| `gate.py` 231~239행은 모양만 본다(20행) | §2: list/dict/`{"key","value"}`/str 검사만 | 참 |
| `persons.py` `update_person` 이 키를 거르지 않는다(20행, 534~555행) | §3: 523~532행 비어 있지 않은 str 검사만, 접두 검사 없음 | 참 — `pattern:` 구멍 실재 |
| `_record()` 를 `run_turn`·`resume_turn` 이 962행·1286행에서 부른다(21행) | §4 | 참 |
| 결정 B(ii) 가 원칙9·스키마 v2 와 충돌하지 않는가 | §9 `agent_traces.output` JSONB, S3.1 14행 열 그대로; 원칙9 는 기록을 **요구**하지 사용을 금하지 않음. `traced()` 예외 경로는 `tool_error` 행을 세이브포인트 안에 쓴다(§14, context.py 165~171행) → 승격 실패 시 U6 의 외부 세이브포인트 롤백으로 함께 사라지므로 계획 151행 "롤백되면 기록도 함께 사라져 재시도" 성립 | 충돌 없음(R-6 권고: `memory_error` 행은 롤백 **뒤** 바깥에서 써야 남는다는 점을 U6 에 명시) |
| 결정 C-5(i) 패턴 행 삭제 vs "원문 삭제 금지" | §8 `events` UPDATE/DELETE 코드 0, §15 `add_event` 원문 그대로 저장, 모델 `Event` 불변 | 충돌 없음(행 4) — 단 195행 grep 은 자기 모순(H-3) |
| U6 가 `app/agent/` 금지 리터럴 규칙을 지키는가 | §6 기준선: `create_person(` 1건(loop.py 1227행, 기존), `T_merge|T_new|confidence` 0건. U6 추가분은 `after_record(ctx, person_ids, extractor)` 호출·`extractor` 키워드뿐(56·70행) | 지킬 수 있음 — 기준선을 이 evidence 로 고정 |
| D14 설정값이 U1·U2·판정 표에 반영됐는가 | U1(65행) `pattern_config()` 기본 365/3·환경변수·거부 ○, 판정 3행 ○, 해석 ㄷ ○, **U2 문장·결정 F 스키마 ×**, `.env.example` × | 부분 — H-1·H-2 |
| 재사용 대상 존재: `DEFAULT_FACT_CONFIDENCE`·`user_timezone()`·`select_provider`·`call_with_error_mapping`·`trace_tokens()`·`FactSource` 복합 PK | §10·§11·§13·§9 | 전부 실재 |
| `_record_impl` 이 이벤트 실행 인물 id 를 모으는가(리스크 208행) | §5 `RecordOutcome(executed, failed, events, schedules, schedule_question)` — 인물 id 없음 | 계획의 리스크 인지와 일치 → R-4 |

### 2차 — 개정으로 새로 생긴 것의 확인 (evidence `20260928-1410-verifier-2-fact-checks.txt`)

| 확인할 것 | 근거 | 결과 |
|-----------|------|------|
| U6·U7 의 `RecordOutcome` 새 필드 2개(`event_person_ids`·`fact_keys_by_person`)가 P5-loop 코드와 충돌하는가 | §1 `RecordOutcome` 은 `@dataclass(frozen=True)` 이고 모든 필드에 기본값(`field(default_factory=list)`·`0`·`None`)이 있다. §3 생성 자리는 loop.py 868행 **하나**. §6 `app/agent/__init__.py` 재export 는 이름만. §14 `_record()` 는 901행에서 `_traced(...)` 결과를 그대로 돌려주므로 계획 22행 "기록 단계 trace 가 끝난 **뒤** 한 줄" 자리가 실재한다 | 기본값 있는 필드 추가 = 추가만(additive). 충돌 없음 |
| 새 필드가 기존 테스트와 충돌하는가 | §4 `tests/` 에 `RecordOutcome` 참조 0. §5 `loop_record.output` 단언은 `record_out["executed"]`·`record_out["failed"]` 두 키뿐(test_agent_loop.py 409~647행), `to_dict()` 는 두 키만 낸다(§1) — 계획 57행 "`loop_record` output 의 기존 키는 불변" 과 일치 | 충돌 없음 |
| U7 "`executed[]` 항목에는 인자가 없다 — loop.py 862행" | §2 `executed.append({"index": …, "name": …, "trace_id": …})` — `args` 없음. `call.args`·`person_id` 는 같은 루프 본문(`_record_impl` 815·833행)에서 접근 가능 | 참. 계획대로 `_record_impl` 안에서 모을 수 있다 |
| 범위가 넓어졌는가 | 산출물 파일 표(53~61행)에 더해진 것은 `.env.example` 행뿐. `app/er/`·`gate.py`·`propose.py`·`respond.py` 는 산출물 표에 없고(§15 — 유일한 매치는 124행 "기존 산출물 재사용" 표의 "import 만"), 새 엔드포인트 없음(32행). U7 은 결정 G(ii) 사용자 확정(136행)의 결과이고 R8 "사실→원문 링크" 범위 안 | 넓어지지 않음 |
| **새 위험 — U6 `extractor` 기본값(`None` → `extractor_from_env()`)의 해소 시점** | §7 `run_turn` 954행은 `proposer_from_env()` 를 **진입 즉시** 부른다(선례). §8 공급자 생성자는 `openai.OpenAI(...)` 를 생성 시점에 만든다 — 키가 없으면 여기서 예외. §9 기존 테스트는 `extractor` 를 넘기지 않고 `run_turn`/`resume_turn` 을 8곳에서 부르고, §10 API 테스트는 `get_proposer()`/`get_judge()` 처럼 deps 가 `None` 을 돌려준다. 즉 `extractor` 를 954행 방식(즉시)으로 해소하면 **키 없는 테스트 환경에서 기존 회귀가 루프 진입 전에 깨진다**. §11 기존 테스트에는 한 인물에 5건을 쌓는 루프가 없으므로, 트리거가 걸린 뒤(미승격 ≥ 5)에만 지연 해소하면 기존 테스트는 추출기를 만들지 않는다 | 계획 문장 자체는 시점을 정하지 않았고 U6 판정이 회귀 4파일을 포함해 구현 중 잡힌다 → **권고 R-10**(아래 §3), 판정 조건 아님 |

계획이 **하지 않는 것**을 명시했는가: 26~35행 10항, 각 줄에 이유 — 충족(1차와 같음). 작업 단위가 커밋 하나 크기인가: U1~U8 — 충족(U6 가 `loop.py`·`deps.py`·`routes.py` + 회귀 4파일로 가장 크지만 한 커밋 범위, U7 은 `loop.py` 한 자리 + 테스트 1파일). 수용 기준이 기계적으로 판정 가능한가: 판정 표 21행 전부 명령·기대값, 19행이 198·200·201행의 명령을 "그 절에 적힌 명령 그대로" 로 가리켜 표기 불일치(1차 R-8)도 사라짐 — 충족.

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)

### 3-1. 1차 H-1~H-3 닫힘 판정 (evidence `20260928-1410-verifier-2-hold-recheck.txt` — 05 표의 완료 판정 명령을 표에서 잘라내 그대로 실행)

| 1차 소견 | F-id | 실행한 완료 판정 명령 → 출력 | 판정 |
|----------|------|----------------------------|------|
| H-1 D14 `.env.example` 기본값 줄 누락 | `F-bbf7fa` | 1단계 `grep -n 'env\.example. . 두 줄 추가' 01-plan.md` → 60행 1건 · 2단계 `grep -n 'env.example' 01-plan.md` → 3·25·60·67·233행 5건(≥3) · 3단계 `grep -n PATTERN .env.example` → 0건(exit 1) | **닫힘.** 3단계는 U1 이 실제 파일을 고쳐야 2건이 되는 구현 몫이라 계획 판정 조건이 아니다(05 표에도 "대기(U1 구현 몫, 계획 보류 해소 조건 아님)" 로 적혀 있고 verifier 도 같은 판단). 04-review 에서 U1 evidence(`evidence/*-u1-*.txt` 의 `grep -n PATTERN .env.example` 2건)로 본다 |
| H-2 D14 "실제 쓴 기간·횟수 trace 기록" 이 결정 F·U2 에 없음 | `F-56df6c` | 1단계 `grep -nF 'window:{from,to}, window_days, min_count'` → 186행 1건 · 2단계 `grep -n 'U2 패턴 감지 규칙.*window_days'` → 68행 1건 · 3단계 `grep -nE 'window_days=90'` → 97행 1건 | **닫힘.** 결정 F output·U2 문장·판정 3행이 같은 두 키를 가리킨다 |
| H-3 "지킬 불변식" grep 이 C-5(i)·D-6·U2 와 모순 | `F-14ad9f` | 1단계 `grep -nF 'delete\(Event'` → 198행 1건 · 2단계 `grep -c 'rnE "delete\\([^E]'` → `0`(옛 무한정 grep 잔존 0) · 보조 `grep -nF 'delete\(\|'` → 0건 | **닫힘.** 198행 grep 은 `delete\(Event\|update\(Event\|\.raw_utterance\s*=[^=]\|\.content\s*=[^=]` 로 `Event` 만 본다. 05 2단계 명령은 파일에서 잘라 실행하면 `0` 이 나오지만 손으로 옮겨 치면 백슬래시 이스케이프가 달라져 `Unmatched (` 오류가 난다 — 재검증은 파일에서 잘라 실행할 것(evidence 머리에 방식 기록) |

`F-033bb1`(1차 판정이 남아 있어 생긴 WARN)은 이 문서의 2차 판정으로 점검표에 "보류" 행이 0 이 되면 2b 실행에서 사라진다(§1-2b).

### 3-2. 권고 R-1~R-9 반영 여부 (반영 안 돼도 판정 조건 아님)

| 권고 | 반영 자리(개정본 행) | 결과 |
|------|---------------------|------|
| R-1 시작 해시 갱신 | 8행 "이 패키지의 시작 해시(무변경 diff 기준점) = `2de7416`(코드 기준으로는 `1e4afb4` 와 동일)" | 반영 |
| R-2 U2·U3 Refs `D9`→`D14` | 68행 U2 Refs "D14 D9", 69행 U3 Refs "D14 D9"(병기) | 반영 |
| R-3 설정값 개수 표기 통일 | 25행 "설정 상수 6개 중 환경변수로 덮을 수 있는 것은 … 2개", 67행 U1, 74행 U8 "RUNNING 절에 '설정 상수 6개 중 환경변수 2개' 로 적는다" | 반영 |
| R-4 U6 `RecordOutcome` 확장 명시 | 72행 "`RecordOutcome` 에 **`event_person_ids: list[int]`** … 필드를 추가", 212행 리스크 | 반영 |
| R-5 공개 함수 소유 검사 | 68행 U2·71행 U5 "첫 줄에서 `_owned_person(...)` 재사용(security §5)", 129행 재사용 표 행, 부정 테스트 각 1건 | 반영 |
| R-6 `memory_error` 기록 자리·B(ii) 세션 무관 조회 | 72행 U6 "**`memory_error` 행은 세이브포인트 롤백이 끝난 뒤 바깥 트랜잭션에서 기록한다**", 186행 결정 F 같은 문장, 71행 U5 "`session_id` 와 무관하게 … 세션을 넘어 누적 조회" | 반영 |
| R-7 U7 fact id 취득 방법 | 73행 U7 "`call.args["facts"][].key` … `RecordOutcome` 에 `fact_keys_by_person: dict[int, list[str]]` … `updated_at desc` 첫 행 … 같은 키가 두 번 실행되면 … 한 번만 잇는다" | 반영 |
| R-8 판정 19행 grep 표기 통일 | 113행 판정 19행 "'지킬 불변식' 절의 grep 3개를 **그 절에 적힌 명령 그대로** 실행", 200행 `T_merge\|T_new\|confidence\|create_person\(` 한 표기 | 반영 |
| R-9 `dbtest` 는 마커 | 128행 "픽스처 `db_session`·`fake_embedder`, 마커 `dbtest`" | 반영 |

### 3-3. 2차 새 권고 (착수를 막지 않는다)

- **R-10 [권고] U6 `extractor` 기본값은 트리거 뒤에 지연 해소한다.** 근거: fact-checks-2 §7~§11 — `run_turn` 954행 `active_proposer = proposer if proposer is not None else proposer_from_env()` 는 진입 즉시 해소하고, 공급자 생성자는 `openai.OpenAI(...)` 를 그 자리에서 만들어 키가 없으면 예외다. 기존 회귀 테스트는 `extractor` 를 넘기지 않고 `run_turn`/`resume_turn` 을 8곳에서 부르고 API 테스트는 deps 가 `None` 을 돌려주므로, `extractor` 를 954행 방식으로 두면 U6 판정(회귀 4파일)이 루프 진입 전에 깨진다. 조치: `extractor_from_env()` 호출을 `promote_person` 안, 미승격 ≥ `MEMORY_PROMOTE_MIN_EVENTS` 판정 **뒤**·U6 세이브포인트 **안**에 두어 실패가 `memory_error` 로만 남게 한다(기존 테스트는 한 인물에 5건을 쌓지 않으므로 §11 추출기를 만들지 않는다). 판정 16행(가짜 추출기 `timeout` → 200·`memory_error`)과 같은 규약. → U6 03-log 에 시점 한 줄.
- **R-11 [권고] 05-remediation `F-14ad9f` 2단계 명령의 재실행 방식.** 백슬래시가 두 겹인 명령이라 손으로 옮겨 치면 이스케이프가 달라진다(3-1 표). 04-review 에서 같은 명령을 다시 쓸 일이 있으면 05 표에서 잘라 실행하거나 `grep -nF 'delete\(\|'` → 0건(고정 문자열)으로 대체한다. → 04-review 작성자(verifier) 메모.

### 3-4. 3차 확인 — 승인 전 변경(2026-09-28, 사용자 결정) 범위 한정 (점검표 8행은 2차 그대로 두고 표 행을 새로 만들지 않는다)

대상: 01-plan 4·25·55·60·67·71·74행(`MEMORY_PROMOTE_MIN_EVENTS` 환경변수 덮어쓰기, 읽기 함수 `promote_min_events(env=None)`, `.env.example` 세 번째 줄, U1 판정 3건, "환경변수 3개" 표기) + `docs/backlog.md` P8 절 새 항목 1줄(`git diff docs/backlog.md`, 1 insertion). 미커밋 새 파일이라 diff 대신 행을 직접 읽었다. evidence: `20260928-1431-verifier-3-verify-plan.txt`(기계 검증, FAIL 0 WARN 0 — 메인 세션 `20260928-1429-preapproval-verify-plan.txt` 와 줄 단위로 같음), `20260928-1431-verifier-3-fact-checks.txt`(이하 "fc-3 §n"), `20260928-1431-verifier-3-hold-findings.txt`(findings.py 입력).

| 확인할 것 | 근거 | 결과 |
|-----------|------|------|
| ① S3.5 "승격 트리거: 같은 인물의 미승격 events ≥ 5건"·`docs/resolution-plan.md` 190행 "5건 이상" 과 충돌하는가 / CR 이 필요한가 | fc-3 §5 두 원문 그대로. 01-plan 55행 "기본 5 = S3.5", 71행 U5 "≥ `promote_min_events()`(기본 5, 환경변수로 덮음)", 84행 해석 ㄱ "5건 이상" — 환경변수가 없으면 카드와 같은 동작. D14 의 선례(CR-002)는 **값 자체가 90→365 로 바뀌어** CR 을 거친 것이고, 이번은 기본값·스키마(S3.1)·시그니처(S3.2) 전부 불변인 운영 손잡이 추가다. 다만 fc-3 §6: `MEMORY_PROMOTE_MIN_EVENTS` 는 S3.5·D14·CR-002·`resolution-plan.md`·CLAUDE.md 어디에도 없다 — 01-plan 14행 "S3.5·D9 가 이미 적어 둔 것을 옮길 뿐" 이 이 한 가지에는 정확히 맞지 않는다 | **충돌 없음, CR 불필요**(기본값 불변). 권고 R-12: S3.5 카드 6행에 "(`MEMORY_PROMOTE_MIN_EVENTS`, 기본 5 — P6-memory 계획에서 설정값화)" 한 구절을 메인 세션이 덧붙이면 카드와 계획이 다시 1:1 이 된다. 착수 조건 아님 |
| ② 범위가 넓어졌는가(원칙5·7, 스키마·시그니처) | 산출물 파일 표(53~61행)·새 파일 목록(41~49행)에 추가된 파일 없음, 32행 "새 API 엔드포인트 없음"·28행 "프론트 3화면 … 제외" 그대로(fc-3 §12). 설정 상수 개수는 여전히 6(`PATTERN_WINDOW_DAYS`·`PATTERN_MIN_COUNT`·`PATTERN_KEY_PREFIX`·`MEMORY_PROMOTE_MIN_EVENTS`·`MEMORY_PROMOTE_MAX_EVENTS`·`MEMORY_MAX_FACTS`) — 바뀐 것은 그중 환경변수로 덮는 것의 수(2→3)뿐. `alembic check`·`tools_check.py` 7/7(판정 20행) 그대로. 제품 코드 변경 0(fc-3 §13 `git status` 는 `docs/` 만) | **넓어지지 않음** |
| ③ 01-plan 안의 어긋난 문장 | fc-3 §1: **25행** 뒤 절반이 `` `.env.example` 에 그  2개의 기본값 줄(이름과 "비우면 기본 365/3" 설명만 `` 으로 남아 있다. 같은 25행 앞 절반은 "3개", 60행은 "세 줄 추가 … 365일 / 3회 / 5건", 67행 U1 은 "그 3개의 기본값 줄 … 365/3/5 … `grep -nE "PATTERN_\|MEMORY_PROMOTE_MIN_EVENTS" .env.example`(3건)"(fc-3 §2). 구현자가 25행을 따르면 두 줄만 넣어 U1 판정(3건)이 실패한다. fc-3 §4: 55행에 `MEMORY_PROMOTE_MIN_EVENTS=5` 가 두 번 적혀 있다(D14 괄호 안 + 상수 나열) — 중복이지 모순은 아니다. 05 `F-bbf7fa` 3단계 `grep -n PATTERN .env.example` 2건 vs U1 3건(fc-3 §9): `PATTERN` 접두 줄은 여전히 2건이고 U1 은 세 이름을 다 세는 다른 명령이므로 **모순 아님** — 04-review 에서 둘 다 그대로 실행하면 된다 | **H-4 보류**(25행 한 구절) → `F-04ecbe`. 권고 R-13: 55행의 두 번째 `MEMORY_PROMOTE_MIN_EVENTS=5` 를 지워 한 번만 적는다(선택) |
| ④ 백로그 새 항목이 P 순서·수용 기준 규칙에 문제를 일으키는가 | `git diff docs/backlog.md` — P8 절 끝에 `[미정 — CR 필요] … / 의존: P6-memory, P8 / 수용기준: (CR 에서 정함)` 1줄. P6 첫 항목(79행)은 무변경이고 01-plan 78행과 글자 그대로 같다(fc-3 §11, verify-plan `PASS  backlog 일치`). 패키지 id 를 갖지 않고(`P8-…` 아님) "미정" 표시라 `verify-plan` 의 패키지 등록·의존 검사 대상이 아니다. 내용도 원칙5(3화면 안)·스키마 변경(설정 테이블 → CR) 을 스스로 적어 두어 CLAUDE.md "기획서가 바뀌면 `/devlog change`" 와 맞다 | **문제 없음** |
| ⑤ `verify-plan.sh` | `20260928-1431-verifier-3-verify-plan.txt`(이 절을 쓰기 전) · `20260928-1434-verifier-3b-verify-plan.txt`(쓴 뒤 재실행) — 둘 다 `== 결과: FAIL=0 WARN=0 ==`, `PASS  backlog 일치`, `PASS  Refs 있음` U1~U8, `PASS  점검표 8행 존재`, `PASS  보류 0건`(점검표 행 기준 — 3차 표는 ①~⑤ 로 번호를 매겨 8행 규칙에 걸리지 않는다) | 기계 검증 통과. 아래 결과 줄이 보류인 이유는 ③ 하나 |

3차 소견 뒤 점검표(§2)의 3·8행 근거에 인용된 "60행 두 줄 추가"·"U1 `grep -n PATTERN .env.example`(2건)" 은 **2차 시점 원문**이며, 지금 60행은 "세 줄 추가", U1 은 `grep -nE "PATTERN_|MEMORY_PROMOTE_MIN_EVENTS"`(3건)이다 — 근거의 결론(D14 11행 `.env.example` 기본값 줄 요구 충족, security §1 이름만)은 그대로 성립한다. 표 행은 고치지 않았다(2차 판정 보존).

권고(착수 조건 아님): **R-12** S3.5 카드 한 구절(위 ①). **R-13** 55행 중복 표기 정리(위 ③). **R-14** 결정 F `memory_promote` output 과 187행 `unpromoted_count` 옆에 이번 판정에 쓴 `min_events`(= `promote_min_events()` 값)를 함께 적는다 — fc-3 §7 에 `min_events` 0건. D14 13행이 패턴에 요구한 "실제 쓴 기간·횟수 기록" 과 같은 이유(원칙8·9: 설정을 바꾼 뒤 "왜 그때 승격했나/안 했나" 를 재현)이며, 카드가 직접 요구하지는 않으므로 권고에 둔다. U5 03-log 한 줄이면 된다.

### 3-5. 4차 확인 — 3차 보류 H-4(`F-04ecbe`) 닫힘 판정 (범위: H-4 + 함께 들어온 R-12~R-14. 점검표 8행 표는 2차 그대로, 새로 만들지 않는다)

대상: 메인 세션이 고친 01-plan 25행(뒤 절반 "그 3개의 기본값 줄 … 365/3/5")·55행(R-13)·71행(R-14) + `docs/wiki/specs/S3.5-memory-promotion.md` 6행(R-12, `git diff` 1 insertion 1 deletion). evidence: `20260928-1440-verifier-4-recheck.txt`(이하 "rc-4 §n" — §1·§1b 는 표 칸 자르기가 이 환경에서 깨진 실패 시도이고 §1c 가 실행 결과다; 실패도 지우지 않았다), `20260928-1442-verifier-4-verify-plan.txt`.

| 확인할 것 | 근거 | 결과 |
|-----------|------|------|
| ① H-4 — 05 `F-04ecbe` 해결 단계 표의 완료 판정 명령을 **파일에서 잘라 그대로** 실행 | rc-4 §1c: 1단계 `grep -cE '2개의\|두 줄\|365/3"' 01-plan.md` → `0`(기대 `0`) · 2단계 `sed -n 55p … \| grep -o "MEMORY_PROMOTE_MIN_EVENTS=5" \| wc -l` → `1`(기대 `1`). §2 위임 프롬프트 grep `grep -nE '2개의\|두 줄\|365/3"'` → 0건(exit 1). §3 반대편 표기 `3개의\|세 줄\|365/3/5` → 14·25·60·67행. §4 25행 원문: "`.env.example` 에 그 3개의 기본값 줄(이름과 "비우면 기본 365/3/5" 설명만 — 비밀 없음, D14·CR-002, security §1)" — 60행 "세 줄 추가 … 365일 / 3회 / 5건"·67행 U1 "그 3개의 기본값 줄 … 365/3/5 … (3건)" 과 같은 뜻. §8 환경변수 개수 표기가 있는 25·67·74행 전부 "3개"(74행 RUNNING "설정 상수 6개 중 환경변수 3개") | **닫힘.** 05 `F-04ecbe` 상태 해소(재검증 칸에 같은 evidence) |
| ② R-12 — S3.5 카드 6행 한 구절이 카드 의미를 바꾸는가 | rc-4 §7: diff 는 6행 하나, "승격 트리거: 같은 인물의 미승격 events ≥ 5건" → "… ≥ 5건(설정값 `MEMORY_PROMOTE_MIN_EVENTS`, 기본 5 — 2026-09-28 사용자 결정, 기본값 불변)". 카드의 숫자 목록은 `5건·365일·3회·90일` 로 변경 전과 같고, 원문 `docs/resolution-plan.md` 190행 "승격 트리거: 같은 인물의 미승격 `events`가 5건 이상" 과 기본 동작이 같다. §12b: `MEMORY_PROMOTE_MIN_EVENTS`·"5건" 은 D14·CR-002·INDEX·CLAUDE.md·review-index 에 0건 — 이 카드 밖에 어긋날 문장이 없다. 3차 ① 판정(기본값 불변 → CR 불필요)과 같은 결론이고, 01-plan 55행 "기본 5 = S3.5"·71행 U5 "`promote_min_events()`(기본 5, 환경변수로 덮음)"·84행 해석 ㄱ "5건 이상" 이 카드와 1:1 이 됐다. 원문(resolution-plan)은 손대지 않았다 — 카드가 원문보다 설정 이름 한 구절을 더 갖지만 기본값이 같아 동작 모순은 없다(CR-002 때는 값이 바뀌어 원문까지 고쳤고, 이번은 값 불변이라 카드에만 둔 것이 맞다) | **의미 불변, 새 모순 없음** |
| ③ R-13 — 55행 중복 제거 | rc-4 §5: 55행에서 `MEMORY_PROMOTE_MIN_EVENTS=5` 1회(3차 fc-3 §4 는 2회). 55행 원문에 상수 이름은 `=5`(값) 한 번 + 환경변수 이름 한 번 — 서로 다른 뜻이라 중복이 아니다. 파일 전체 등장 행 5(25·55·60·67·71) | **반영** |
| ④ R-14 — 실제 쓴 `min_events` 를 승격 trace 에 기록 | rc-4 §6·§11: 71행 U5 "`memory_promote` trace 1행(tokens 는 추출기 사용량, 이번 판정에 실제로 쓴 `min_events`(R-14), `considered_event_ids`·…)". 186행 결정 F `memory_promote` output 스키마 `{person_id, unpromoted_count, considered_event_ids, facts:[…], rejected:[…], llm:{…}}` 와 187행에는 `min_events` 가 없다(§6 grep 55·67·71행만) | **U5 에 반영(권고의 절반).** 결정 F 스키마와 U5 문장이 키 하나 어긋나지만, 구현자가 따르는 작업 단위 문장(U5)이 기록을 요구하고 output 에 키를 더하는 것은 P5 U1 스키마 규약(03-log 기재)으로 이미 허용된 일이며 카드가 요구하는 키가 아니다 → 보류 아님. **권고 R-15**: 결정 F 186행 `memory_promote` output 에 `min_events` 를 적어 두 자리를 맞춘다(한 단어, U5 03-log 에서 해도 된다) |
| ⑤ 새 모순·범위 확대 | rc-4 §9 backlog 79행 = 01-plan 78행(verify-plan `PASS  backlog 일치`), §10 `git status` 에 `docs/` 밖 변경 0, §13b backlog diff 는 3차 ④ 의 `[미정 — CR 필요]` 1줄 그대로. 산출물 파일 표·"하지 않는 것" 무변경(3차 ② 와 같은 파일 집합) | **없음** |
| ⑥ `verify-plan.sh` | `20260928-1442-verifier-4-verify-plan.txt` `== 결과: FAIL=0 WARN=0 ==`(메인 세션 `20260928-1435-h4fix-verify-plan.txt` 와 줄 단위로 같음) · 이 절을 쓴 뒤 `-4b-` 재실행(아래 결과 줄에 파일명) | 통과 |

## 4. 결정
결과: 통과 — 3차 보류 H-4(`F-04ecbe`) 닫힘(3-5 ①, `evidence/20260928-1440-verifier-4-recheck.txt` §1c·§2·§4). 점검표 8/8 통과(2차 표 유지), 3차 권고 R-12·R-13 반영, R-14 는 U5 에 반영(결정 F 스키마 한 단어는 새 권고 R-15, 착수 조건 아님). 카드·코드·범위·스키마·시그니처 무변경(3-5 ②⑤). 기계 검증 `20260928-1442-verifier-4-verify-plan.txt` FAIL 0 WARN 0, 이 문서 갱신 뒤 재실행 `20260928-1444-verifier-4b-verify-plan.txt` FAIL 0 WARN 0. `F-bbf7fa` 3단계(`.env.example` 실파일)는 2차 결정대로 U1 구현 판정으로 이월.
승인: 사용자 (2026-09-28) — 결정 A~G 권장안(B 방법 2), CR-002(패턴 기본 365일·3회 설정값), 승인 전 추가 `MEMORY_PROMOTE_MIN_EVENTS` 설정값(기본 5) 포함. 권고 R-10·R-15 는 U5·U6 03-log 에서.

> 3차 결정(2026-09-28 14:35, 보존): 결과: 보류 — H-4 하나(01-plan 25행 뒤 절반 "그 2개의 기본값 줄 … 365/3" 이 60·67행 "세 줄 · 365/3/5" 과 어긋남, `F-04ecbe`). 카드·코드·범위·스키마·시그니처 문제 없음(3-4 ①②④), 기계 검증 FAIL 0 WARN 0(⑤). 25행 한 구절을 고치고 `grep -nE '2개의|두 줄|365/3"' 01-plan.md` 0건을 확인하면 통과로 바꿀 수 있다. 권고 R-12~R-14 는 착수를 막지 않는다.

> 2차 결정(2026-09-28 14:15, 보존): 결과: 통과 — 1차 H-1·H-2·H-3 전부 닫힘(3-1, evidence `20260928-1410-verifier-2-hold-recheck.txt`), 점검표 8/8, 권고 R-1~R-9 전부 반영, 새 권고 R-10·R-11 은 착수를 막지 않는다. `F-bbf7fa` 3단계(`.env.example` 실파일)는 U1 구현 판정으로 이월.

> 1차 결정(2026-09-28 13:49, 보존): 결과: 보류 — H-1·H-2·H-3(전부 01-plan 문장 수정, 카드·코드 무변경). 세 건을 반영한 개정본으로 재검증하면 통과 예상. 권고 R-1~R-9 는 착수를 막지 않는다.
