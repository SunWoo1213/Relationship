# P5-loop · 계획 검증 (02-plan-verify)

대상: 01-plan.md | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002) | 날짜: 2026-09-23 (1차 15:49 → 2차 16:28) → **2026-09-24 3차, 3차 개정본(`7351363`) 재검증**

> **개정 이력.** 1차(`결과: 보류` — H-1·H-2·H-3)와 2차(`결과: 보류` — H-1 잔존·H-4·H-5, 권고 R-9~R-19) 뒤, 사용자 결정 (a) "범위 묶은 3차 개정"(2026-09-24)으로 architect 가 01-plan 을 고쳤고(`7351363`) 사용자가 새 미결 M-3 를 안 A 로 확정했다. **이 문서에서 판정으로 유효한 것은 §1~§4(3차)다.** 2차 본문은 아래 "2차·판정 기록" 절로 옮기고 절 제목·점검표 행 번호 앞에 `2차·`, `결과:`/`승인:` 줄 앞에 `2차 ` 를 붙였다(`verify-plan.sh` 6절 `^\| [1-8] \|`·`^결과:` 가 현재 점검표만 세게 하기 위함 — 그 밖의 2차 본문은 한 글자도 바꾸지 않았다). 1차 블록(§5)은 제목·본문 모두 그대로다.

평가 대상 커밋: `HEAD = 7351363`(dev, `origin/dev` 보다 2 앞 — `20c2d7e` FIX-003·`7351363` 3차 개정, 미푸시). `bash .claude/scripts/gitlog.sh P5-loop`(2026-09-24 20:34) — 태그 `P5-loop` 커밋 7건(`7351363`·`20c2d7e`·`f5fde31`·`b10ac6e`·`cf82868`·`b676799`·`4d5817e`) 중 제품 코드 커밋은 여전히 `4d5817e`(P2 U8) 하나뿐이고 `app/agent/` 는 존재하지 않는다(`ls app/agent` → `No such file or directory`). `7351363` 의 변경 파일은 `01-plan.md`·`05-remediation.md`·evidence 3·`FIX-003.md`·`journal.md`·`HANDOFF.md` 뿐(gitlog "마지막 커밋의 파일"). 미커밋 변경: `docs/wiki/HANDOFF.md`·`docs/wiki/journal.md`, 미추적 `Usersswsj1.claudesettings.json`(0 바이트 — R-26) — `app/`·`tests/` 0. 01-plan 7행 "새 작업 단위 없음" 과 커밋 메시지 "코드 없음" 은 사실이다.

## 1. 기계 검증 출력 (3차 — 그대로 붙인다, 요약 금지)

3차 개정 커밋 `7351363` 에 evidence 3개가 있다: `20260924-1940-verify-plan.txt`(**FAIL 2** — `Refs 없음: U1`·`Refs 없음: U4`. 원인: 3차에서 U1·U4 가 여러 줄 항목이 되면서 `Refs:` 가 첫 줄에서 밀렸고 5절 grep 은 항목 첫 줄만 본다 → 05-remediation `F-d61978`·`F-9c9410`, 같은 날 해소) → `20260924-1941-verify-plan-2.txt`(Refs 를 첫 줄로 옮긴 뒤 FAIL 0 / WARN 8) → `20260924-1943-verify-plan-3.txt`(M-3 반영 후 FAIL 0 / WARN 8, **최신**). 아래는 최신 파일 전문이다(`python -c "open(..., encoding='utf-8', errors='replace')"` 로 읽음 — 5절의 항목 제목 절단 `�` 는 `cut -c1-60` 의 바이트 절단이지 파일 손상이 아니다).

명령: `bash .claude/scripts/verify-plan.sh P5-loop | tee docs/wiki/packages/P5-loop/evidence/20260924-1943-verify-plan-3.txt`
```
== verify-plan P5-loop  (2026-09-24 19:43) ==
PASS  존재: docs/wiki/packages/P5-loop/01-plan.md
PASS  존재: docs/wiki/packages/P5-loop/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D11
PASS  카드 존재: D12
PASS  카드 존재: D13
PASS  카드 존재: D2
PASS  카드 존재: D6
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P6-memory
PASS  검증 항목 존재: R10
PASS  검증 항목 존재: R6
PASS  검증 항목 존재: R7
PASS  Refs 있음: - [ ] U1 **[backend-agent] 루프 계약 타입 + trace 어�
PASS  Refs 있음: - [ ] U2 **[backend-agent] 인식 단계 — 발화 → `too
PASS  Refs 있음: - [ ] U3 **[backend-agent] 게이트 — 제안을 코드가
PASS  Refs 있음: - [ ] U4 **[backend-agent] 해석 단계 — ER 연결·되�
PASS  Refs 있음: - [ ] U5 **[backend-agent] 기록 + 응답 단계**: 게이�
PASS  Refs 있음: - [ ] U6 **[backend-agent] `POST /chat` — API 한 흐름**
PASS  Refs 있음: - [ ] U7 **[backend-agent] 재개 — `POST /answers/{questi
PASS  Refs 있음: - [ ] U8 **[backend-agent] 수용 기준 기계 검증 + 문
PASS  backlog 일치: [ ] [backend-agent] 에이전트 루프(인식→해석→�
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: app/agent/__init__.py
PASS  registry 중복 없음: app/agent/types.py
PASS  registry 중복 없음: app/agent/propose.py
PASS  registry 중복 없음: extract.py
WARN  registry 에 다른 패키지로 이미 있음: app/er/judge.py → | 모듈 | LLM 판정(3단계, 공급자 중립) | app/er/judge.py | P3-er | b1f
PASS  registry 중복 없음: app/agent/gate.py
PASS  registry 중복 없음: app.tools
WARN  registry 에 다른 패키지로 이미 있음: inspect.signa → | 스크립트 | 툴 시그니처 기계 검증 | scripts/tools_check.py | P2-to
PASS  registry 중복 없음: app/agent/loop.py
PASS  registry 중복 없음: dataclasses.repla
PASS  registry 중복 없음: app/agent/respond.py
PASS  registry 중복 없음: tests/test_agent_propose.py
PASS  registry 중복 없음: tests/test_agent_gate.py
PASS  registry 중복 없음: tests/test_agent_loop.py
PASS  registry 중복 없음: tests/test_agent_resume.py
PASS  registry 중복 없음: tests/test_api_chat.py
WARN  registry 에 다른 패키지로 이미 있음: app/api/routes.py → | 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-t
WARN  registry 에 다른 패키지로 이미 있음: app/api/schemas.py → | 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools 
WARN  registry 에 다른 패키지로 이미 있음: app/api/deps.py → | 엔드포인트 | 요청 단위 세션·ToolContext 조립 | app/api/deps.py |
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
WARN  registry 에 다른 패키지로 이미 있음: tests/test_api.py → | 테스트 | HTTP: /health·/answers 200/404/409/422 | tests/test_api.py | P2-t
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
| 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
| 문서 | FIX-001 main 병합(갈라진 배포 브랜치를 dev 로 되돌린�
== 결과: FAIL=0 WARN=8 ==
```

**WARN 8 의 판정** — 스크립트 원문(`.claude/scripts/verify-plan.sh` 97~102행: 산출물 절 `- ` 항목에서 `grep -oE '[A-Za-z0-9_./-]+[.][a-z]{1,5}'` 로 토큰을 뽑아 `grep -F` 로 `registry.md` 의 다른 패키지 행과 대조)을 읽고, 토큰 추출을 직접 재현했다(`awk … | grep -oE …` 출력 22 토큰 중 registry 일치 8).

| WARN | 무엇 | 판정 · 근거 |
|---|---|---|
| W-1 `app/er/judge.py` | 산출물 절 59행 "(`app/er/judge.py` 의 `select_provider`… 재사용)" 문장 속 경로 | **의도.** 01-plan 206행 "**무수정 재사용**(import). 인식 단계의 공급자 선택·오류 어휘를 새로 만들지 않는다(D11)", 판정 표 10행이 `app/er/` 변경을 미충족으로 본다. 만들지도 고치지도 않는 파일 · `F-e93529` [권고] |
| W-2 `inspect.signa` | 산출물 절 60행 "`inspect.signature` 인자 대조" 에서 정규식 `[.][a-z]{1,5}` 가 `signature` 를 `signa`(5자)에서 자른 **가짜 토큰**. registry 67행(`scripts/tools_check.py` 행 비고 "`inspect.signature` 대조")에 `grep -F` 로 걸렸다 | **하네스 결함(R-19), 계획 결함 아님.** 같은 정규식이 `app.tools`·`dataclasses.repla`·`extract.py` 도 만들었지만 registry 에 없어 PASS 로 찍혔을 뿐이다. `F-b38c2c` [권고] — 원인 분석 칸을 이 3차에서 채웠다(05-remediation). 해결은 하네스 FIX 후보, 이 패키지 조치 없음 |
| W-3~W-7 `app/api/routes.py`·`schemas.py`·`deps.py`·`app/settings.py`·`tests/test_api.py` | "고치는 기존 파일"(01-plan 68~72행) | **의도.** U8 95행 "고친 기존 파일 … 은 **비고에 P5-loop 한 줄과 커밋 해시를 더한다**(새 행을 만들지 않는다 — F-0ffff5·F-95c6a7 선례)". P4b 05-remediation 이 같은 성격 WARN 22건을 U7(`cf5a171`)로 닫은 선례 · `F-8e3e74`·`F-6ae8ad`·`F-d68447`·`F-fdb56f`·`F-7e6e84` [권고] |
| W-8 `README.md` | 문서 갱신 대상(73행) | **의도.** 95행 "절을 새로 만들지 않고 기존 절에 이어 붙인다" · `F-0ffff5` [권고] |

→ **8 = registry 기존 행 7(의도) + 하네스 정규식 1(R-19). 위임 프롬프트의 가설과 일치한다.** 05-remediation 머리줄 "열림: 8 (필수 0) | 해소: 14" 와도 일치한다(열림 8 = 위 소견 8). 단, `F-e93529` 등 [권고] 7건은 1차 15:44 이후 verify-plan 을 **7회** 재실행하는 동안 계속 열려 있다 — 의도된 WARN 이고 닫는 자리는 U8 이지만 "같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고" 규칙에 따라 여기 보고한다(R-27).

### 1b. 3차 — 이 문서를 갱신한 뒤 재실행 (점검표·`결과:` 줄이 스크립트에 잡히는지 확인)
명령: `bash .claude/scripts/verify-plan.sh P5-loop | tee docs/wiki/packages/P5-loop/evidence/20260924-2051-verify-plan-4.txt`
```
== verify-plan P5-loop  (2026-09-24 20:51) ==
PASS  존재: docs/wiki/packages/P5-loop/01-plan.md
PASS  존재: docs/wiki/packages/P5-loop/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D11
PASS  카드 존재: D12
PASS  카드 존재: D13
PASS  카드 존재: D2
PASS  카드 존재: D6
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P6-memory
PASS  검증 항목 존재: R10
PASS  검증 항목 존재: R6
PASS  검증 항목 존재: R7
PASS  Refs 있음: - [ ] U1 **[backend-agent] 루프 계약 타입 + trace 어�
PASS  Refs 있음: - [ ] U2 **[backend-agent] 인식 단계 — 발화 → `too
PASS  Refs 있음: - [ ] U3 **[backend-agent] 게이트 — 제안을 코드가
PASS  Refs 있음: - [ ] U4 **[backend-agent] 해석 단계 — ER 연결·되�
PASS  Refs 있음: - [ ] U5 **[backend-agent] 기록 + 응답 단계**: 게이�
PASS  Refs 있음: - [ ] U6 **[backend-agent] `POST /chat` — API 한 흐름**
PASS  Refs 있음: - [ ] U7 **[backend-agent] 재개 — `POST /answers/{questi
PASS  Refs 있음: - [ ] U8 **[backend-agent] 수용 기준 기계 검증 + 문
PASS  backlog 일치: [ ] [backend-agent] 에이전트 루프(인식→해석→�
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: app/agent/__init__.py
PASS  registry 중복 없음: app/agent/types.py
PASS  registry 중복 없음: app/agent/propose.py
PASS  registry 중복 없음: extract.py
WARN  registry 에 다른 패키지로 이미 있음: app/er/judge.py → | 모듈 | LLM 판정(3단계, 공급자 중립) | app/er/judge.py | P3-er | b1f
PASS  registry 중복 없음: app/agent/gate.py
PASS  registry 중복 없음: app.tools
WARN  registry 에 다른 패키지로 이미 있음: inspect.signa → | 스크립트 | 툴 시그니처 기계 검증 | scripts/tools_check.py | P2-to
PASS  registry 중복 없음: app/agent/loop.py
PASS  registry 중복 없음: dataclasses.repla
PASS  registry 중복 없음: app/agent/respond.py
PASS  registry 중복 없음: tests/test_agent_propose.py
PASS  registry 중복 없음: tests/test_agent_gate.py
PASS  registry 중복 없음: tests/test_agent_loop.py
PASS  registry 중복 없음: tests/test_agent_resume.py
PASS  registry 중복 없음: tests/test_api_chat.py
WARN  registry 에 다른 패키지로 이미 있음: app/api/routes.py → | 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-t
WARN  registry 에 다른 패키지로 이미 있음: app/api/schemas.py → | 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools 
WARN  registry 에 다른 패키지로 이미 있음: app/api/deps.py → | 엔드포인트 | 요청 단위 세션·ToolContext 조립 | app/api/deps.py |
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
WARN  registry 에 다른 패키지로 이미 있음: tests/test_api.py → | 테스트 | HTTP: /health·/answers 200/404/409/422 | tests/test_api.py | P2-t
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
| 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
| 문서 | FIX-001 main 병합(갈라진 배포 브랜치를 dev 로 되돌린�
== 결과: FAIL=0 WARN=8 ==
```

3차 갱신 뒤 판정: **FAIL 0 / WARN 8, `PASS  검증자 = verifier (L-002)`·`PASS  점검표 8행 존재`·`PASS  보류 0건`·`PASS  결과: 줄 존재`** — 6절이 세는 것은 §2 의 3차 8행뿐이고(2차 행은 `| 2차·n |`, 2차 `결과:` 는 `2차 결과:` 로 바꿔 두었다), WARN 8 은 §1 표 W-1~W-8 그대로다(1943 과 동일). FAIL 이 하나라도 있으면 아래 결과는 통과가 될 수 없다. FAIL/WARN 은 `python .claude/scripts/findings.py <id> evidence/<ts>-verify-plan.txt --source verify-plan` 으로 05-remediation.md 에 소견으로 올리고, 조치 후 다시 실행한다 — 이번 WARN 8 은 이미 소견 8건(`F-e93529`·`F-8e3e74`·`F-6ae8ad`·`F-d68447`·`F-fdb56f`·`F-7e6e84`·`F-0ffff5`·`F-b38c2c`)으로 올라가 있어 새 소견은 만들지 않았다.

## 2. 정합성 점검표 (3차 — 3차 개정본 기준으로 전부 다시 판정. 기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다. 01-plan 행 번호는 3차 개정본(395행, `7351363`) 기준.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 2장 표 55~62행 제외 열 "고민 상담 기능 / 인물 간(A–B) 관계 저장 / 관계 태그 필터링 / 상담 페르소나 / 톤 설정 / 음성 입력 / 네이티브 앱" ↔ 01-plan 46행 "**고민 상담·감정 대화**(원칙7) — 응답은 '무엇을 기억했는가'와 되묻기뿐이다", 47행 "**인물 간(A–B) 관계 저장**(원칙7) … 두 사람 각각의 이벤트이지 둘 사이의 간선이 아니다", 48행 "**상담 페르소나·음성 입력·네이티브 앱**(원칙7)", 42행 "프론트 3화면·PWA·확인 칩 UI(P8-frontend)" 제외. 3차 개정이 더한 것(hint_only 버킷·`needs_confirmation`·`LOOP_MAX_PROPOSALS`·`NEW_PERSON_TAG_OPTIONS`·`schedule` 재개 재료)은 전부 툴 7종 호출을 **더 좁히는** 쪽이다 — 28행 ① "화이트리스트: `name ∉ app.tools.TOOL_NAMES` → 거부", 344행 "화이트리스트가 **허용 목록**이라 새 동작은 원리상 제안될 수 없고, 삭제 툴은 애초에 없다". 관계 태그 **필터**는 산출물(57~73행)·U1~U8 어디에도 없다 — M-1(d) 의 태그 옵션은 필터가 아니라 `create_person` 의 필수 인자(`persons.py` 430행 `relation_tag not in RELATION_TAGS`)를 사용자 확인으로 채우는 것이다. 결정 B(i) 240행 "템플릿은 공감·조언을 만들 수 없다" + 판정 표 18행 부정 테스트 유지 |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | `CLAUDE.md` 원칙1 "확신도가 임계치 미만이면 절대 자동 병합하지 말고 `ask_user`"·원칙2 두 임계치·원칙4 "반드시 4단계" ↔ 01-plan 29행 "**루프는 확신도를 다시 계산하지도, 임계치를 다시 비교하지도 않는다**", 28행 ④ "`person_id` 는 오직 `resolve()` → `apply_resolution()` 을 거쳐서만 얻는다", ② "`search_person`·`ask_user`·`get_briefing` 제안은 거부", 295행 `person_id` 출처 셋(① merge ② `candidate_ids[answer]` ③ `resume.schedule.person_id` — ②③ 은 ① 또는 사용자가 고른 ER 후보로 거슬러 올라간다; 코드로 확인: `pipeline.py` 200행 `candidate_ids = {c.display_name: c.person_id …}`, `questions.py` 263행 `answer not in question.options` → 클라이언트 입력은 저장된 옵션 안), 판정 표 6·19~22행. 3차가 더한 `hint_only` 는 LLM 의 `create_person` 제안을 **실행 0** 으로 고정한다(87행, 판정 표 21행 spy 0회). 원칙8 ↔ 43행 "`app/er/` 내부 수정 … 루프는 **호출자로만** 붙는다", 판정 표 10·13·14행, 302행 M-0 ① "`app/er/` 를 한 줄도 고치지 않는다". 원칙9 ↔ 결정 F 257행 output 스키마 + 80~82행 U1 세 스키마 고정(`loop_gate`·`loop_record`·등식). 원칙5·6·7 은 42·40·46행. **원칙 위반 없음.** 2차가 남긴 "판정 표 7·22·5행이 계획 자신과 모순" 은 §2b 에서 해소로 판정했다 |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `D01-new-person-confirm.md` 11행 "`create_person` 호출 경로는 반드시 answered pending_question 을 거친다. 직접 호출 테스트는 실패해야 한다" ↔ 01-plan 94행 U7 "`ctx.confirmed_question_id` 를 세운 채 `create_person` 을 부르되 **`context.mention` 이 가리키는 대상에만**", 124행 5a "`-B1` 앞줄이 `ctx.confirmed_question_id = …` 대입", 28행 ③ "`create_person` 제안은 실행 버킷이 아니라 **힌트 전용 버킷(`hint_only`)** … (D1 — 실행은 재개 경로뿐)". `D02-ask-user-async.md` 11행 "동기 대기(sleep/poll) 금지. `ask_user`를 다른 툴에 합치지 않는다" ↔ 88행 "D2 — sleep/poll 금지", 판정 표 9행; 루프가 직접 부르는 `ask_user(kind="schedule")`(92행)은 **같은 툴을 따로 호출**하는 것이지 합치는 것이 아니다; D2 파급 "답 없이 새 발화가 오면 대기 질문 유지" ↔ 판정 표 25행. `D06-display-name-policy.md` "`update_person(display_name=…)`은 사용자 확인(answered question)을 거친 경우에만" ↔ 28행 ③ "`update_person` 제안에 `display_name` 이 있으면 거부(`needs_confirmation`, D6)", 판정 표 5b ① `display_name` 0건 — 2차 R-11 반영으로 게이트 단에서도 막힌다. `D12-observed-signal-renormalization.md`·`D13-rule-filter-penalty.md` 의 "코드에서 지켜야 할 것" 은 전부 `app/er/confidence.py`·`rules.py`·`pipeline.py` 대상 → 43행·75행 무수정(판정 표 10행). D12 산식은 §2b H-1 (나) 의 merge 기대를 뒷받침한다(`0.625·0.95 + 0.375·1.0 = 0.96875 ≥ 0.8`). `D11` ↔ 86행 "`judge.py` 를 고치지 않는다 — import 만 한다" |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `S3.4-ask-user-protocol.md` 13행 "`context`에는 재개에 필요한 것만(발화, 후보 id, 확신도 분해). 비밀·전체 대화 이력 저장 금지" ↔ 83행 `PendingResume` 스키마(`pending_calls`·`hints`·`tag_by_answer`·`schedule`·`schedule_options` — 전부 재개 재료), 305행 크기 통제 "발화 원문은 ER 이 이미 `context["utterance"]` 로 **1건** 넣었고 루프는 더 넣지 않는다", 85행 U1 테스트 "`PendingResume.to_dict()` 가 발화 원문을 담지 않음(S3.4 13행)", 판정 표 23·24행. S3.4 7행 "턴 N+1 … 저장된 context로 루프 재개 → 후속 툴" ↔ U7 94행. `S3.2-tools-v2.md` 8행 `create_person` "D1: answered new_person 질문 뒤에만" ↔ hint_only; 10행 `add_event` "런타임이 raw_utterance 자동 주입" ↔ 28행 ③ "LLM 이 `raw_utterance` 를 주면 덮어쓰지 않고 `bad_args`", 30행 "`raw_utterance` 는 LLM 제안에서 받지 않고 사용자가 친 원문 그대로 루프가 주입"; 16행 "모든 툴 호출은 `agent_traces`에 기록" ↔ 판정 표 23행 부정 grep(ORM 직접 쓰기 0). `S3.3-er-pipeline.md` 17행 "**LLM 단일 호출로 대체 금지**(원칙4). **T_merge 미만 자동 병합 금지**(원칙1·2)" ↔ 29·91행. `S3.1` `pending_questions.kind` ∈ {identity, new_person, schedule} ↔ `models.py` 73행, K(i)·M-2(i); 판정 표 11행 `alembic check`. 코드로 확인한 M-0 경로: `app/er/types.py` 193행 `@dataclass(frozen=True) class Resolution`·243행 `ask_payload`; `pipeline.py` 474~480행 `ask_user(ctx, kind=…, question=…, options=…, context=…)` 네 키만; `questions.py` 156~162행 최상위 키 비밀 검사, 175행 `AFFIRMATIVE_KEY ⊆ options` → 90행 세 값 동시 교체가 이 검사를 지난다; 145행 중복 옵션 거부 → 태그 5 문자열은 서로 다르고 ER 부정 옵션과도 다르다. **S 카드 충돌 없음.** 2차 H-4 가 지적한 계획 내부 불일치는 §2b 에서 해소로 판정했다 |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `docs/backlog.md` 73행 "의존: P3, **P4b 게이트 통과**(P4 는 부분완료·미달, CR-001)". `packages/P4b-er-redesign/04-review.md` 144행 `결과: 완료`, `packages/P2-tools/04-review.md` 118행 `결과: 완료`, `packages/P3-er/04-review.md` 166행 `결과: 완료`(이번에 `grep '^결과:'` 로 재확인). 기계 검증 §1 "PASS  P4 게이트 통과 (P4b-er-redesign)". 01-plan 12~16행이 인용한 해시 `1075dd6`·`855a26b`·`4338eea`·`cf5a171`·`1227026` 은 전부 gitlog 최근 20건에 있다. 3차 개정에서 의존 절은 바뀌지 않았다 |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 73행 "- [ ] [backend-agent] 에이전트 루프(인식→해석→기록→응답) + ask_user 재개 / 의존: P3, **P4b 게이트 통과**(P4 는 부분완료·미달, CR-001) / 수용기준: 발화 → 툴 선택 → 저장 → 응답이 API 한 흐름으로 동작, `POST /answers/{question_id}`로 루프 재개" = 01-plan 100행. 기계 검증 "PASS  backlog 일치". 해석 절(102~112행)은 "위 한 줄을 바꾸지 않는다" 를 지키며 3차에서 "툴 선택" 해석만 U1 등식으로 갱신했다(106행 "(d) `accepted` = `executed` ∪ `failed` ∪ `resume.pending_calls` ∪ `hint_only`(U1 등식)"). backlog 74행 "(U1~U7). 70행의 문장" 과 75행 "전부 (i)): 툴 선택은 코드가 한다" 는 여전히 개정 전 문장이다 — 01-plan 337행이 "반영은 **승인 커밋에서 메인 세션**이 한다" 로 적었고 이 패키지는 backlog 를 고치지 않는다(R-9 상태: 계획에 기록됨·backlog 미반영, §2c) |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 기계 검증 §1 "PASS  Refs 있음" U1~U8 8건(1940 의 FAIL 2 는 U1·U4 의 `Refs:` 를 첫 줄로 옮겨 1941 에서 닫혔다 — 커밋 메시지 "Refs 를 U1·U4 첫 줄로 옮김(내용 불변)"). 01-plan 79~95행 각 단위 `Refs: P5-loop …`(U1 `S3.2 S3.4 원칙9`, U2 `D11 S3.4 원칙7 원칙9`, U3 `S3.2 원칙1 원칙4 원칙9`, U4 `D1 D2 D12 D13 S3.3 S3.4 원칙1 원칙2 원칙4`, U5 `S3.2 S3.4 원칙7 원칙9`, U6 `R7 D2 S3.4 원칙9`, U7 `**R6 R7** D1 D2 S3.4 원칙1`, U8 `R6 R7 원칙8 원칙9`), 04-review 행 `Refs: P5-loop R6 R7 D1 D2`. 단위 = 커밋 하나: 77행 "단위 하나 = 커밋 하나 후보", 358행 "한 단위가 커밋 하나를 넘지 않는다". 3차로 U1 이 커졌지만(`GateVerdict`·`loop_record`·`PendingResume` 스키마 + 상수 2 + 테스트 6종) 전부 `types.py`·`__init__.py`·`settings.py` 상수라 한 커밋 크기다. 새 단위 없음(7행) |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §1 "로그·trace에 키·비밀을 남기지 않는다" ↔ 01-plan 86행 U2 "프롬프트에 키·환경변수·전체 대화 이력을 넣지 않는다(S3.4 13행·security §1)", 결정 G 261행 "예외 코드·공급자명·프롬프트는 응답에 담지 않고 trace 에만 어휘로", 판정 표 15행. §1 "`.env` … 읽지도 쓰지도 않는다" ↔ 116행 "`.env` 는 스크립트가 읽지 않는다 … 로드 주체는 사용자 셸". §3 재귀 삭제 금지 ↔ 196행 "시드 행(`judge-row7-*`)은 로컬 DB 에 남는다 — 삭제 명령은 쓰지 않는다(security)". §4 "로컬 서버 이외로 데이터 전송 금지" ↔ 판정 표 8행 `127.0.0.1:8000`. §5 "`pending_questions.context`에는 재개에 필요한 것만. 전체 대화 이력 저장 금지" ↔ 305행 + 판정 표 24행; "중첩 값에 비밀이 없게 하는 것은 루프의 몫" 을 305행이 받았다(`questions.py` 156~162행은 최상위 키 이름만 본다 — 사실). §5 "`DELETE /persons/{id}`" ↔ backlog 39행 별도 항목(사용자 승인 2026-09-23). §5 "모든 조회는 `user_id` 조건" 미충족(F-fbaaae)은 backlog 105행 리스크 로그로 남았다. 7행 명령의 `Person(user_id=tag …)` 시드는 로컬 DB 에 테스트 행을 남기지만 삭제·외부 전송 없음. 3차 개정에 새 셸 명령은 7행 명령의 `python -c` 하나뿐이며 위험 명령이 없다 |

## 2b. 2차 보류 3건 재판정 (각각 01-plan 인용 + 코드 확인)

**H-1 — 해소.** 판정 표 7·22행의 기대 출력이 이제 구조상 성립한다. 2차가 든 세 가지 이유를 각각 본다.

- (a) *ER 내부 `@traced` 툴이 `tool_call` 행에 섞인다* → 01-plan 82행 "ER 내부 `search_person`·`update_person`(merge 별칭 누적)·`ask_user` 의 `tool_call` 행은 `executed[].trace_id` 가 가리키지 않으므로 **등식 밖**이다", 106행 "`tool_call` 행과의 대조는 `executed[].trace_id` 가 가리키는 행으로 **한정**한다". 7행 명령 189~190행이 이를 코드로 못박는다: `ex = {e['trace_id'] for e in out['loop_record']['executed']}` → `print([(st, tn) for i, st, tn, _ in rows if i in ex])`. 코드로 확인한 ER 내부 행 셋: `app/er/candidates.py` 112행 `search_person(ctx, mention, effective_hints or None)`(`persons.py` 138행 `@traced("search_person")`), `app/er/pipeline.py` 461행 `update_person(ctx, person_id=…, new_alias=…)`(`persons.py` 467행 `@traced`), `pipeline.py` 474행 `ask_user(ctx, kind=…)`(`questions.py` 183행 `@traced`). 세 행 모두 `ex` 에 없으므로 줄 3 에 나타나지 않고, 줄 4 등식(191~193행)은 `loop_gate.accepted` 인덱스와 `executed`·`failed`·`pending_calls`·`hint_only` 인덱스만 비교한다 — `tool_call` 행 수를 세지 않는다. 2차 등식("`accepted` 이름 집합 = `tool_call` 이름 집합")은 사라졌다. **잔여(권고 R-20)**: (가)(나) 줄 1 기대 목록에 `search_person` `tool_call` 1 이 빠져 있다(candidates.py 112행이 항상 부른다). 기대 목록이 "이것들이 있다" 이지 "이것뿐이다" 가 아니어서 판정은 성립하지만, 04-review 가 헷갈리지 않게 명시하는 편이 낫다.
- (b) *빈 DB 에서 되묻기로 끝나 `loop_record` 가 없다* → 7행이 두 갈래로 갈렸다. 127행 "**(가) 빈 DB — 되묻기로 끝남**: … `record.executed` = `[]`, `pending_calls[].index` = `[0]`, 질문 `kind` = `new_person`", 81행 "`run_turn`/`resume_turn` 은 게이트를 지난 턴마다 `loop_record` 를 **정확히 1행** 남긴다 — 되묻기로 끝나 실행이 0건이어도 `executed: []` 로 남긴다(판정 표 7행 (가) 가 이 행을 본다)". 코드로 확인: 151행 "같은 값을 `user_id` 로도 써서 (가) 의 빈 후보를 보장한다" 는 `persons.py` 165·191·204행 `.where(Person.user_id == ctx.user_id)`·`candidates.py` 70행 `Person.user_id == ctx.user_id` 로 사실이다(명령 174행 `tag = 'judge-row7-' + uuid…`, 180행 `user_id=tag`); 후보 0 → `pipeline.py` 15~17행 "통과 후보가 0건이면 호출하지 않는다" → `no_candidates` → `new_person` band → `_build_ask_payload` 220~235행 옵션 2개 → 루프가 90행 식으로 태그 5 + 부정 1 로 교체(M-3 안 A) → `ask_user` 검증 통과(§2 4행). 줄 4: `acc = {0, 1}`, parts = `[∅, ∅, {0}, {1}]` → 합집합 `{0,1}`, 크기 합 2 = 2 → `True`. 성립.
- (c) *시드 DB 에서 `judge=` 미주입* → 명령 175·179행 `judge = FakeJudge()` / `judge = FakeJudge(table={p.id: 0.95})`, 181행 `run_turn(ctx, U, proposer=FakeProposer(table={U: calls}), judge=judge)`; 61행 `run_turn(ctx, utterance, *, proposer=None, judge=None, config=None)`. 코드로 확인: `pipeline.py` 344행 `resolved_judge = judge if judge is not None else judge_from_env()` — 주입하면 실 공급자를 만들지 않는다; `judge.py` 418~440행 `@dataclass class FakeJudge` `table: dict[int, float]`, docstring "`pick` 이 없으면 `table` 과 **통과 후보 교집합** 중 `s_llm` 최고인 id 하나를 고른다" → `p.id`, `s_llm=0.95`. 스텁 임베더: `context.py` 103행 `embedder: EmbeddingProvider | EmbedderCallable | None`, `persons.py` 354행 `as_provider(embedder)`, 시드 별칭 `embedding=stub(['민수'])[0]`(1536 차원, `embedding.py` 35행 `EMBEDDING_DIM = 1536`) → 195행 `embedding_ran` → 코사인 거리 0 → `s_emb = 1.0`. 산술(직접 실행 `derive_hints('민수')` → `{}` → `rule_checked = 0`): D12 재정규화 `0.625·0.95 + 0.375·1.0 = 0.96875 ≥ T_merge 0.8`, `penalized_by` 없음(힌트 없음) → merge. (나) 기대 "`executed` = `[{0,add_event,<id>}]`, 줄 3 `[('tool_call','add_event')]`, 줄 4 `True`" 성립(`acc = {0}` = `executed {0}`). 127행 끝 "기대와 다르면 … 시드·표를 바꾸지 않고 FAIL 소견으로 올린다(원칙8)" 도 적절하다.
- 22행(`SEED=1 REJECTS=1`): 명령 170~173행 제안 5개를 28·87행 게이트 순서 ①②④③⑤ 로 따라가면 — index 1 `update_person{person_id:3}` → ④ `person_id_from_llm`; index 2 `search_person` → ② `not_callable_by_llm`; index 3 `delete_person` → ① `unknown_tool`(`app/tools/__init__.py` 25~33행 `TOOL_NAMES` 7종에 없음); index 4 `add_event{…, raw_utterance:'x'}` → ③ `bad_args`(28행 "LLM 이 `raw_utterance` 를 주면 … `bad_args`"). `rejected` 4건·`accepted = [{0,add_event,execute}]`·줄 4 `True` — 142행 기대와 같다. 28행이 순서 ①②④③⑤ 의 이유("③ 이 먼저 돌면 `person_id` 제안이 `bad_args` 로 묻힌다")까지 적어 사유 어휘가 결정적이다.

**H-4 — 해소.** (a) 83행 `PendingResume` = "`version`·`mention`·`hints`·`pending_calls[{index,name,args}]`·`held_drafts[]`·`dropped` + 질문 종류별 필드: `new_person` … `tag_by_answer{옵션 문자열→relation_tag}`(값 ⊆ `RELATION_TAGS`), `schedule` 질문(M-2(i))이면 `schedule{person_id,title,call_index}` + `schedule_options{옵션 문자열→ISO 8601}`" — 2차가 요구한 네 필드 전부. (b) 89~90행 `replace` 식이 질문 종류로 갈리고, M-1(d) 갈래는 "`options`: tags + neg, `affirmative_options`: tags, `context`: {…, AFFIRMATIVE_KEY: tags, "resume": …}" 로 **세 값을 함께 교체** — `questions.py` 175행·`persons.py` 306행을 지난다(§2 4행). `neg` 를 ER 원본에서 뽑는 것("문자열을 베끼지 않는다")도 맞다 — `_NEW_PERSON_REJECT_OPTION` 은 `pipeline.py` 상수이고 루프가 import 하면 `app/er/` 결합이 는다. (c) 94행 U7 "`relation_tag = tag_by_answer[answer]`(**답에서 온다**), `hierarchy` = `resume.hints.hierarchy` 가 `HIERARCHIES` 안이면 그 값, 아니면 `동` — `hints` 는 `hierarchy` 판단에만 쓰인다" — 옛 문장("미추론 시 처리는 결정 M-1 — 사용자 결정 대기")은 사라졌다. (d) 302행 M-0 ③ "**유일한 예외(3차 개정, H-4 (d))**: M-1(d) 를 적용하는 `new_person` 질문에 한해 `options`·`affirmative_options`·`context[AFFIRMATIVE_KEY]` 세 값을 … **함께 교체**한다 … `identity` 질문은 예외 없이 `"resume"` 만 더한다" — 모순 해소. (e) 힌트가 있을 때 → M-3 신설(309~312행) 후 314행 "**확정 M-3 = 안 A** (사용자, 2026-09-24) — 힌트가 있어도 `new_person` 질문은 항상 태그 5 + 부정 1 로 묻고, `relation_tag` 는 답에서만 온다 … 남은 **'안 B' 괄호는 무효**다". 판정 표 28행 신설(148행 `new_person_reject` — `create_person` spy 0회·`persons` 행 불변·`loop_resume` 기록). **잔여(권고 R-21)**: 안 A 확정 뒤에도 7행 머리말("새 미결 1건: M-3 … 사용자 결정 대기"), 89행("M-3 안 B 에서 힌트가 유효할 때"), 94행 괄호, 127행 "(안 B: … 2개)", 312행 "01-plan 은 이 결정을 **확정하지 않았다**" 가 남아 있다. 314행이 우선순위를 선언해 테스트 기대값은 하나(6개)로 정해지므로 보류가 아니지만 승인 커밋에서 지워야 한다.

**H-5 — 해소.** 5행이 5a/5b 로 갈렸다. 124행 5a `grep -rnE -B1 "create_person\(" app/agent/` → "일치 **1줄** — `app/agent/loop.py` 의 **재개 경로** … `-B1` 앞줄이 `ctx.confirmed_question_id = …` 대입"; 125행 5b ① `update_person\(` 뒤 4줄에 `display_name` **0건**, ② 호출은 "허용 목록 두 곳뿐: (ㄱ) 기록 단계(U5) `update_person(ctx, person_id, facts=…)`/`new_alias=…` (ㄴ) `identity` 재개(U7) `update_person(ctx, person_id, new_alias=context["mention"])`". U5 92행 "`update_person`(`facts`/`new_alias` 만 — `display_name` 은 게이트가 이미 거부했다)", U7 94행 "`update_person(person_id, new_alias=context["mention"])`" 과 정합 — 올바른 구현이 5a·5b 를 깨뜨리지 않는다. "두 호출 모두 `confirmed_question_id` 가 필요 없다" 는 `persons.py` 271행 docstring "`create_person`/`update_person(display_name=...)` 가 진행되려면 다음이 모두 참" 으로 사실이다(`facts`/`new_alias` 경로는 검사 대상이 아니다). 5b 가 2차 정규식을 버린 이유(125행 "재개 경로의 `create_person(…, display_name=…)` 인자까지 잡아 올바른 구현을 FAIL 시키므로")도 맞다. `ToolContext` 는 `@dataclass`(비 frozen, `context.py` 91행)라 `ctx.confirmed_question_id = …` 대입이 가능하다. **잔여(권고 R-22)**: 5a·5b ①·② 는 `app/agent/` 전체를 grep 하므로 `propose.py` 의 **프롬프트 문자열 리터럴**이 `create_person(display_name, …)`·`update_person(person_id, …, display_name?)` 을 담으면 거짓 FAIL 이 된다. 124행 규칙("주석·docstring 에는 괄호 붙은 표기를 쓰지 않는다")이 문자열 리터럴을 덮지 않는다.

## 2c. 권고 R-9~R-19 반영 상태

| 권고 | 상태 | 01-plan 근거 |
|---|---|---|
| R-9 backlog 세분화 줄 모순 | 계획에 기록 · backlog **미반영**(승인 커밋 몫) | 337행 "(3차 개정, R-9) 현재 backlog 의 결정 요약 줄 … 는 개정 전 문장으로 확정 L(iii) 와 모순된다 — '**L(iii) 하이브리드 — LLM 제안 + 코드 게이트**' 로 바꾸고 … 반영은 **승인 커밋에서 메인 세션**이 한다". backlog 74·75행은 지금도 "(U1~U7). 70행의 문장"·"전부 (i))" |
| R-10 승인 줄이 F 6종·A 게이트를 덮는다 | 반영 | 6행 "**정정(R-10).** … F 는 step 5종 → 6종, A 는 상한 적용 지점이 … 게이트로 옮겨졌다(3차에서 총 제안 수 상한 `LOOP_MAX_PROPOSALS` 도 더했다, R-13) … 예: '승인: 사용자 (YYYY-MM-DD) — F 6종·A 게이트 적용·총 제안 상한 포함'" |
| R-11 게이트 어휘·주입 인자 단일 출처 | 반영 | 60행 "**거부 사유 어휘·버킷 어휘·주입 인자 집합은 이 모듈이 단일 출처**(거부: `unknown_tool`·`not_callable_by_llm`·`bad_args`·`person_id_from_llm`·`needs_confirmation`·`limit` / 버킷: `execute`·`hint_only` / 주입 인자: `ctx`·`person_id`·`raw_utterance`, R-11)", 346행 정정("2차까지의 '`person_id` 치환 하나' 는 사실과 달랐다"), 판정 표 21행 세 케이스 |
| R-12 U2/U3 이중 검사 문장 | 반영 | 27행 "`PROPOSAL_SCHEMA` 의 enum … 으로 LLM 을 **유도**할 뿐이고, 7종 밖 값의 **거부(강제)는 게이트가 한다**(`bad_args`, 판정 표 21행 — R-12)" |
| R-13 총 제안 수 상한 | 반영 · **값 13** | 236행 "**총 제안 수 상한 `LOOP_MAX_PROPOSALS = 13`**(= 5+5+3, `app/settings.py` 상수 + 환경변수 오버라이드)을 게이트 ⑤ 에 더한다 … 값 13 은 기존 세 상한의 합에서 파생한 것이고 새 튜닝값이 아니다", 80행 `limits:{mentions,events,schedules,proposals}` |
| R-14 재개 체인 테스트 | 반영 | 94행 U7 테스트 "**재개 중 두 번째 언급이 되묻기 → `AnswerOut` 에 새 `question_id`·`options`, 첫 질문은 answered 유지**(R-14), **identity 답 뒤 `schedule` 질문**(R-14)" |
| R-15 27행 기계화 + docstring | 반영 | 147행 `-k "alias_embedding"` + "스텁 임베더(`tests/conftest.py::fake_embedder`)" — 픽스처 실재(conftest.py 95행); 93행 U6 docstring 문장 "임베딩 키가 없는 환경에서는 `embedder=None` 이고 ER 은 `embedding_skipped` 로 돌며 … 미검출된다" |
| R-16 두 기록의 권위 + 이름 어긋남 | 반영 | 303행 "**두 기록의 권위(R-16)**: M-1(d) 로 교체된 옵션은 `ask_user` 의 `tool_call` trace 와 `pending_questions` 행이 **권위**다"; 86행 U2 "모듈 docstring 에 'step 이름 `loop_extract` 는 결정 F 로 고정된 이름이고 내용은 LLM 제안 원문이다' 한 줄" |
| R-17 판정 명령의 `judge=` | 반영 | 127·142·147행 "`judge=FakeJudge(...)`·스텁 임베더 주입, 네트워크 0(R-17)", 7행 명령 175~181행 |
| R-18 05-remediation 머리줄 | 반영(메인 세션) | 05-remediation 6행 "열림: 8 (필수 0) | 해소: 14", `F-25b70f` "상태: 해소 … 해소: 2026-09-24" |
| R-19 verify-plan.sh 토큰 정규식 | 미수정(의도 — 하네스) | §1 W-2. `F-b38c2c` 로 소견화됐고 원인 분석은 이 3차가 채웠다. 계획 조치 없음 |

## 2d. 범위 준수 판정 — 3차 개정이 2차 보류를 닫는 범위를 넘었는가

**넘지 않았다.** 근거: (1) 7행 "새 작업 단위 없음. 확정 A~K·L(iii)·M-0·M-1(d)·M-2(i) 는 다시 열지 않았다" — 산출물은 여전히 새 모듈 6(`__init__`·`types`·`propose`·`gate`·`loop`·`respond`)·테스트 5·고치는 기존 파일 4(57~73행), 허용 파일 각주(75행)·"하지 않는 것" 절(38~51행) 무변경. (2) 3차가 새로 만든 개념을 전부 2차 소견으로 역추적할 수 있다: `GateVerdict.bucket`/`hint_only`·`needs_confirmation`·주입 인자 셋 ← R-11; `loop_record.output`(`executed[].trace_id`·`failed`)·U1 등식·7행 (가)(나)·22행 ← H-1; `PendingResume` 질문 종류별 필드·`NEW_PERSON_TAG_OPTIONS`·U4 두 갈래·U7 `tag_by_answer`·M-0 예외·28행 ← H-4; 5a/5b ← H-5; `LOOP_MAX_PROPOSALS` ← R-13; 27행 pytest ← R-15; docstring 두 줄 ← R-15·R-16; U7 테스트 2건 ← R-14; `person_id` 출처 셋(295행) ← 2차 §2d-1. (3) 유일한 새 결정 M-3 는 H-4 (e) 가 요구한 것이고 사용자가 확정했다. (4) 확정 A(i) 의 "툴 호출 횟수 자체는 상한을 두지 않는다" 는 236행이 "그대로다 — 제안 목록 크기 상한" 으로 지켰다. (5) `git show 7351363 --stat`(gitlog) 변경 파일에 `app/`·`tests/`·backlog·카드가 없다.

## 3. 소견 (3차) — 보류 0 · 새 권고 R-20~R-27

**보류(H) — 없음.** 2차 H-1·H-4·H-5 는 §2b 대로 전부 해소.

**권고(R) — 착수를 막지 않는다. [권고] 만 있고 [필수] 는 없다. 반영 자리를 각각 적는다.**

- R-20 [권고] **7행 (가)(나) 줄 1 기대에 `search_person` `tool_call` 1 을 명시.** `candidates.py` 112행이 매 `resolve()` 마다 부르므로 줄 1 에 항상 나타난다(ER 내부 행, 대조 대상 아님 — 82행 규약 그대로). 지금 127행은 (나)에서 `update_person` 행만 언급한다. 04-review 가 "기대에 없는 행" 으로 오판하지 않게 한 구절. → 승인 커밋(architect 문장) 또는 U8 03-log.
- R-21 [권고] **M-3 안 A 확정 뒤 잔존 문장 정리.** 7행 머리말 "사용자 결정 대기", 89행 "M-3 안 B 에서 힌트가 유효할 때" 갈래, 94행 괄호, 127행 "(안 B: …)", 312행 "확정하지 않았다" — 314행이 무효를 선언했으니 지운다. 코드 기대값에는 영향 없음(6개로 확정). → 승인 커밋.
- R-22 [권고] **5a·5b grep 의 프롬프트 리터럴 함정.** `propose.py` 의 `build_propose_prompt()` 가 툴 7종 시그니처를 문자열로 적으면 `create_person(`·`update_person(` + `display_name` 이 `app/agent/` 안에 생겨 5a(1줄 초과)·5b ①(`display_name` 검출)이 거짓 FAIL 이 된다. 조치 둘 중 하나를 U2 03-log 에 적는다: (ㄱ) 124행 규칙을 "`app/agent/` 의 **모든 문자열 리터럴**" 로 넓혀 프롬프트에 괄호 붙은 호출 표기를 쓰지 않는다, (ㄴ) 프롬프트의 툴 설명을 `inspect.signature(app.tools.<name>)` 로 생성한다(게이트 ③ 과 같은 출처 — 시그니처가 바뀌면 프롬프트·게이트·`tools_check.py` 가 함께 움직인다. 권장). 판정 표 6행(`confidence` 0건)은 프롬프트에 그 단어가 없으면 무관.
- R-23 [권고] **`add_schedule` 제안의 "`scheduled_at` 미확정" 표현과 게이트 ③ 의 충돌.** U2 86행 "확정 불가는 결정 K 규약으로 처리" / U5 92행 "`scheduled_at` 이 확정되지 않았으면 … `ask_user(kind="schedule")`" 인데, 게이트 ③ 은 `inspect.signature` 로 필수 누락·타입 위반을 `bad_args` 로 거부한다(`add_schedule(ctx, person_id, title, scheduled_at)` — `scheduled_at` 필수). 제안이 `scheduled_at` 을 빼거나 `null` 로 주면 U5 에 닿기 전에 ③ 이 거부해 `schedule` 질문 경로(K(i)·M-2(i)·판정 표 4행·U7 "identity 답 뒤 `schedule` 질문")가 **한 번도 실행되지 않는다**. U3 03-log 에서 표현 하나를 정한다(예: `scheduled_at: null` 은 `add_schedule` 에 한해 타입 위반이 아니라 "미확정" 으로 통과시키고 `GateVerdict` 에 표시) + `bad_args` 테스트에 "`null` 은 거부하지 않는다" 1건. 같은 자리에서 ISO 문자열 파싱 실패(U2 형식 변환)가 `bad_args` 인지 결정 G 오류인지도 한 줄.
- R-24 [권고] **`loop_record.failed[]` 와 U6 예외 범위의 관계.** 81행 "`failed` 는 `ToolError` 로 끝난 실행 제안" 은 루프가 호출 단위로 `ToolError` 를 잡아 기록하고 턴을 계속한다는 뜻인데(결정 D(i) 확정분 유지와 정합), 93행 U6 "삼키는 것은 `LoopError` 계층·공급자 오류·`ToolError` 계층뿐" 은 라우트 단에서 잡는 것으로 읽힌다. 기록 단계의 `ToolError` 가 `run_turn` 밖으로 나가면 `loop_record` "정확히 1행"(81행)과 등식이 그 턴에서 깨진다. U5 03-log 에 "기록 단계 `ToolError` 는 호출 단위로 잡아 `failed[]` 에 남기고 다음 제안으로 간다; 라우트가 잡는 것은 `run_turn` 밖으로 나온 예외뿐" 을 적고 U5 테스트에 `failed` 1건(예: `add_event` `InvalidValue`)을 더한다 — 지금 U5 테스트 목록에 `failed` 케이스가 없다(테스트 없는 분기).
- R-25 [권고] **`hint_only` 힌트의 언급 매칭 규칙과 `held_drafts` 정의.** (ㄱ) 언급 5·`create_person` 제안 여러 개일 때 어느 제안의 `relation_tag`/`hierarchy` 가 어느 언급의 `hints` 가 되는지 없다(7행 명령은 언급 1·제안 1 이라 드러나지 않는다). U4 03-log 에 규칙 하나(예: `args.aliases` 또는 `args.display_name` 이 언급 문자열과 같을 때만, 그 외는 무시하고 `loop_resolve_done` 에 남긴다). (ㄴ) `PendingResume.held_drafts[]`(83행)는 `pending_calls` 와 무엇이 다른지 정의가 없다 — L(i) 시절 `EventDraft`/`ScheduleDraft` 의 잔재로 보인다. 같은 정보면 필드를 없애고 24행 "`held_drafts` 를 버린다" 를 "`pending_calls[].args` 의 `content` 를 절단한다" 같은 실제 동작으로 바꾸거나, 다르면 U1 03-log 에 정의한다.
- R-26 [권고 · 메인 세션] **저장소 루트의 미추적 0바이트 파일 `Usersswsj1.claudesettings.json`.** 경로 구분자가 빠진 `C:\Users\swsj1\.claude\settings.json` 모양이며 이 패키지와 무관하다. `git add` 대상에 넣지 않고 사용자가 지운다(에이전트 삭제 금지 규칙과 무관하게 원인이 하네스 쪽일 수 있어 사용자 확인 후).
- R-27 [보고] **[권고] 소견 7건(`F-e93529`·`F-8e3e74`·`F-6ae8ad`·`F-d68447`·`F-fdb56f`·`F-7e6e84`·`F-0ffff5`)이 verify-plan 7회(1544→1549→1628→1640→1940→1941→1943)에 걸쳐 열려 있다.** 의도된 WARN(§1)이고 닫는 자리는 U8(95행: 착수 전 원인 분석 칸 채움 → registry 비고 확장 → 04-review)이므로 조치는 없다 — "3회 재검증 후에도 열려 있으면 사용자에게 보고" 규칙에 따라 보고만 한다.

05-remediation: 3차에서 새 FAIL 없음. `F-b38c2c`(inspect.signa) 원인 분석 칸을 이 3차가 채웠다(하네스 결함 확인, 해결 단계는 이 패키지 밖). 나머지 [권고] 7건의 원인 분석은 U8 착수 전 backend-agent 몫(R-2, 95행). H-1·H-4·H-5 재판정은 verifier 판정이므로 이 절이 기록이다.

## 4. 결정
결과: 통과 — 2차 보류 3건 전부 해소(H-1: 7·22행 기대 출력이 `executed[].trace_id` 한정·빈 DB/시드 DB 분리·`FakeJudge` 주입으로 구조상 성립, 코드·산술로 확인 / H-4: M-1(d)·M-2(i) 가 U1 스키마·U4 `replace` 식·U7 문장·M-0 예외에 반영, M-3 안 A 확정 / H-5: 5a·5b 가 U5·U7 의 `update_person` 호출과 정합). 점검표 8행 전부 통과, 3차 개정은 2차 보류를 닫는 범위 안이다(§2d). 새 소견은 [권고] R-20~R-25 와 보고 R-26·R-27 뿐이며 착수를 막지 않는다 — R-22·R-23·R-24 는 U2·U3·U5 03-log 에서 한 줄씩 정하고 04-review 가 확인한다.

**승인 시 사용자가 확인할 항목**(둘 다 01-plan 에 있다): ① R-10 — 6행의 승인 문구 예시 "승인: 사용자 (YYYY-MM-DD) — F 6종·A 게이트 적용·총 제안 상한 포함" 대로 `승인:` 줄이 **F 6종·A 게이트 적용·총 제안 상한** 셋을 명시한다. ② R-13 — 236행 `LOOP_MAX_PROPOSALS = 13`(= 5+5+3) 이 사용자가 받아들이는 값이다. 그리고 backlog 74·75행 개정(R-9)·M-3 잔존 괄호 정리(R-21)를 같은 승인 커밋에서 메인 세션이 반영한다.
승인: 사용자 (2026-09-24) — F 6종·A 게이트 적용·총 제안 상한(`LOOP_MAX_PROPOSALS = 13`) 포함. 같은 커밋에서 backlog P5 세분화 줄 개정(R-9)·01-plan M-3 안 B 잔존 문장 정리(R-21)

---

## 2차·판정 기록 (2026-09-23 16:28 — 보존. 절 제목·점검표 행 번호 앞에 `2차·`, `결과:`/`승인:` 줄 앞에 `2차 ` 만 붙였다)

> **개정 이력.** 1차 판정(§5 에 그대로 보존)은 `결과: 보류` — H-1(판정 표 7행 실행 불가)·H-2(`context` 확장 경로 부재)·H-3(결정 L(i) 의 기획서 3.1 이탈 미기록), 권고 R-1~R-8. 그 뒤 architect 가 01-plan 을 개정했고(결정 L (i)→(iii) 하이브리드, U1~U7 → U1~U8, `extract.py` → `propose.py` + `gate.py`, 결정 F 5종 → 6종, 결정 M-0 신설, 판정 표 7행 실행 가능화 + 19~27행 신설) 사용자가 미결 M-1 = (d)·M-2 = (i) 를 확정했다. **이 문서에서 판정으로 유효한 것은 §1~§4(2차)다.** §5 의 1차 점검표는 행 번호 앞에 `1차·` 를 붙여 `verify-plan.sh` 6절이 현재 점검표(§2)만 세게 했고, 1차 `결과:` 줄은 `1차 결과:` 로 바꿨다 — 그 밖의 1차 본문은 한 글자도 바꾸지 않았다(1차 evidence `20260923-1544-plan-verify.txt`·`20260923-1549-plan-verify-2.txt` 도 그대로).
평가 대상 커밋: `HEAD = cf82868`(dev, 1차와 동일 — 코드 변경 0). 기계 검증 전 `bash .claude/scripts/gitlog.sh P5-loop D1 D2 R6 R7`(16:22) 재실행 — 태그 `P5-loop` 커밋은 여전히 `cf82868`·`b676799`·`4d5817e` 셋, 제품 코드 커밋 0. 미커밋 변경: `docs/backlog.md`·`docs/wiki/HANDOFF.md`·`docs/wiki/fixes/FIX-002.md`·`docs/wiki/journal.md`·`docs/wiki/packages/P5-loop/`(미추적)·`reports/pilot/` 2건 — `app/`·`tests/` 0. 개정본이 "코드·테스트를 한 줄도 쓰지 않았다"(01-plan 5행)는 주장은 사실이다.

## 2차·1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)

### 2차·1a. 2차 — 이 문서를 갱신하기 전 (1차 판정이 아직 `보류` 인 상태)
명령: `bash .claude/scripts/verify-plan.sh P5-loop | tee docs/wiki/packages/P5-loop/evidence/20260923-1628-plan-verify-3.txt`
```
== verify-plan P5-loop  (2026-09-23 16:28) ==
PASS  존재: docs/wiki/packages/P5-loop/01-plan.md
PASS  존재: docs/wiki/packages/P5-loop/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D11
PASS  카드 존재: D12
PASS  카드 존재: D13
PASS  카드 존재: D2
PASS  카드 존재: D6
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P6-memory
PASS  검증 항목 존재: R10
PASS  검증 항목 존재: R6
PASS  검증 항목 존재: R7
PASS  Refs 있음: - [ ] U1 **[backend-agent] 루프 계약 타입 + trace 어�
PASS  Refs 있음: - [ ] U2 **[backend-agent] 인식 단계 — 발화 → `too
PASS  Refs 있음: - [ ] U3 **[backend-agent] 게이트 — 제안을 코드가
PASS  Refs 있음: - [ ] U4 **[backend-agent] 해석 단계 — ER 연결·되�
PASS  Refs 있음: - [ ] U5 **[backend-agent] 기록 + 응답 단계**: 게이�
PASS  Refs 있음: - [ ] U6 **[backend-agent] `POST /chat` — API 한 흐름**
PASS  Refs 있음: - [ ] U7 **[backend-agent] 재개 — `POST /answers/{questi
PASS  Refs 있음: - [ ] U8 **[backend-agent] 수용 기준 기계 검증 + 문
PASS  backlog 일치: [ ] [backend-agent] 에이전트 루프(인식→해석→�
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
WARN  보류 1 건 — 결과는 통과가 될 수 없다
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: app/agent/__init__.py
PASS  registry 중복 없음: app/agent/types.py
PASS  registry 중복 없음: app/agent/propose.py
PASS  registry 중복 없음: extract.py
WARN  registry 에 다른 패키지로 이미 있음: app/er/judge.py → | 모듈 | LLM 판정(3단계, 공급자 중립) | app/er/judge.py | P3-er | b1f
PASS  registry 중복 없음: app/agent/gate.py
PASS  registry 중복 없음: app.tools
WARN  registry 에 다른 패키지로 이미 있음: inspect.signa → | 스크립트 | 툴 시그니처 기계 검증 | scripts/tools_check.py | P2-to
PASS  registry 중복 없음: app/agent/loop.py
PASS  registry 중복 없음: dataclasses.repla
PASS  registry 중복 없음: app/agent/respond.py
PASS  registry 중복 없음: tests/test_agent_propose.py
PASS  registry 중복 없음: tests/test_agent_gate.py
PASS  registry 중복 없음: tests/test_agent_loop.py
PASS  registry 중복 없음: tests/test_agent_resume.py
PASS  registry 중복 없음: tests/test_api_chat.py
WARN  registry 에 다른 패키지로 이미 있음: app/api/routes.py → | 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-t
WARN  registry 에 다른 패키지로 이미 있음: app/api/schemas.py → | 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools 
WARN  registry 에 다른 패키지로 이미 있음: app/api/deps.py → | 엔드포인트 | 요청 단위 세션·ToolContext 조립 | app/api/deps.py |
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
WARN  registry 에 다른 패키지로 이미 있음: tests/test_api.py → | 테스트 | HTTP: /health·/answers 200/404/409/422 | tests/test_api.py | P2-t
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
| 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
| 문서 | FIX-001 main 병합(갈라진 배포 브랜치를 dev 로 되돌린�
== 결과: FAIL=0 WARN=9 ==
```

WARN 9건의 무해성 판정(스크립트 원문 `.claude/scripts/verify-plan.sh` 6·7절을 읽고 판정):

| WARN | 무엇 | 판정 · 근거 |
|---|---|---|
| W-a `보류 1 건` | 6절 `held=$(grep -E '^\| [1-8] \|' "$PV" \| grep -c '보류')` — 1차 점검표 4행의 `**보류**` 를 센 것 | **이 문서가 원인.** 2차 점검표(§2)는 8행 전부 판정을 다시 했고 1차 표는 `1차·n` 으로 바꿔 세지 않게 했다. §1b 재실행에서 사라져야 한다 |
| W-b `app/er/judge.py` | 산출물 절 57행 "(`app/er/judge.py` 의 `select_provider`… 재사용)" 문장 속 경로 토큰 | 무해. 01-plan 148행 "**무수정 재사용**(import)", 판정 표 10행이 `app/er/` 변경을 미충족으로 본다. 만들지도 고치지도 않는 파일 — U8 registry 대상 아님(05-remediation `F-e93529` [권고]) |
| W-c `inspect.signa` | 7절 정규식 `[A-Za-z0-9_./-]+[.][a-z]{1,5}` 가 58행 "`inspect.signature` 인자 대조" 에서 `signa`(5자) 까지만 잘라 만든 **가짜 토큰**. `grep -F` 가 registry 67행(`scripts/tools_check.py` 행 비고의 "`inspect.signature` 대조")에 걸렸다 | 무해. 산출물 경로가 아니다. 같은 이유로 `app.tools`·`dataclasses.repla`·`extract.py` 도 가짜 토큰인데 registry 에 없어 PASS 로 찍혔을 뿐이다. 스크립트 결함이지 계획 결함이 아니다(R-19) |
| W-d~W-h `app/api/routes.py`·`schemas.py`·`deps.py`·`app/settings.py`·`tests/test_api.py` | "고치는 기존 파일"(01-plan 64~70행) | 무해. U8 84행 "고친 기존 파일 … 은 **비고에 P5-loop 한 줄과 커밋 해시를 더한다**(새 행을 만들지 않는다 — F-0ffff5·F-95c6a7 선례)". P4b 05-remediation 8행이 같은 성격 WARN 22건을 U7(`cf5a171`)로 닫은 선례. 05-remediation `F-8e3e74`·`F-6ae8ad`·`F-d68447`·`F-fdb56f`·`F-7e6e84` [권고] — U8 착수 전 원인 분석 칸 채움(R-2 반영, 84행) |
| W-i `README.md` | 문서 갱신 대상 | 무해. 위와 같음(`F-0ffff5`), 84행 "절을 새로 만들지 않고 기존 절에 이어 붙인다" |

### 2차·1b. 2차 — 이 문서를 갱신한 뒤 (W-a 소멸 확인)
명령: `bash .claude/scripts/verify-plan.sh P5-loop | tee docs/wiki/packages/P5-loop/evidence/20260923-1640-plan-verify-4.txt`
```
== verify-plan P5-loop  (2026-09-23 16:38) ==
PASS  존재: docs/wiki/packages/P5-loop/01-plan.md
PASS  존재: docs/wiki/packages/P5-loop/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D11
PASS  카드 존재: D12
PASS  카드 존재: D13
PASS  카드 존재: D2
PASS  카드 존재: D6
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P6-memory
PASS  검증 항목 존재: R10
PASS  검증 항목 존재: R6
PASS  검증 항목 존재: R7
PASS  Refs 있음: - [ ] U1 **[backend-agent] 루프 계약 타입 + trace 어�
PASS  Refs 있음: - [ ] U2 **[backend-agent] 인식 단계 — 발화 → `too
PASS  Refs 있음: - [ ] U3 **[backend-agent] 게이트 — 제안을 코드가
PASS  Refs 있음: - [ ] U4 **[backend-agent] 해석 단계 — ER 연결·되�
PASS  Refs 있음: - [ ] U5 **[backend-agent] 기록 + 응답 단계**: 게이�
PASS  Refs 있음: - [ ] U6 **[backend-agent] `POST /chat` — API 한 흐름**
PASS  Refs 있음: - [ ] U7 **[backend-agent] 재개 — `POST /answers/{questi
PASS  Refs 있음: - [ ] U8 **[backend-agent] 수용 기준 기계 검증 + 문
PASS  backlog 일치: [ ] [backend-agent] 에이전트 루프(인식→해석→�
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: app/agent/__init__.py
PASS  registry 중복 없음: app/agent/types.py
PASS  registry 중복 없음: app/agent/propose.py
PASS  registry 중복 없음: extract.py
WARN  registry 에 다른 패키지로 이미 있음: app/er/judge.py → | 모듈 | LLM 판정(3단계, 공급자 중립) | app/er/judge.py | P3-er | b1f
PASS  registry 중복 없음: app/agent/gate.py
PASS  registry 중복 없음: app.tools
WARN  registry 에 다른 패키지로 이미 있음: inspect.signa → | 스크립트 | 툴 시그니처 기계 검증 | scripts/tools_check.py | P2-to
PASS  registry 중복 없음: app/agent/loop.py
PASS  registry 중복 없음: dataclasses.repla
PASS  registry 중복 없음: app/agent/respond.py
PASS  registry 중복 없음: tests/test_agent_propose.py
PASS  registry 중복 없음: tests/test_agent_gate.py
PASS  registry 중복 없음: tests/test_agent_loop.py
PASS  registry 중복 없음: tests/test_agent_resume.py
PASS  registry 중복 없음: tests/test_api_chat.py
WARN  registry 에 다른 패키지로 이미 있음: app/api/routes.py → | 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-t
WARN  registry 에 다른 패키지로 이미 있음: app/api/schemas.py → | 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools 
WARN  registry 에 다른 패키지로 이미 있음: app/api/deps.py → | 엔드포인트 | 요청 단위 세션·ToolContext 조립 | app/api/deps.py |
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
WARN  registry 에 다른 패키지로 이미 있음: tests/test_api.py → | 테스트 | HTTP: /health·/answers 200/404/409/422 | tests/test_api.py | P2-t
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
| 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
| 문서 | FIX-001 main 병합(갈라진 배포 브랜치를 dev 로 되돌린�
== 결과: FAIL=0 WARN=8 ==
```

2차 갱신 뒤 판정: **W-a(`보류 1 건`)가 사라져 `PASS  보류 0건`, FAIL=0 WARN=8.** 남은 WARN 8건은 §1a 표 W-b~W-i 그대로(무수정 import 1·스크립트 가짜 토큰 1·고치는 기존 파일 5·README 1)이며 전부 U8 등록 규약과 R-19 로 설명된다. (파일명 `1640` 은 tee 시각, 스크립트 머리줄 `16:38` 은 실행 시각 — 같은 실행이다.)

FAIL 이 하나라도 있으면 아래 결과는 통과가 될 수 없다. FAIL/WARN 은 `python .claude/scripts/findings.py <id> evidence/<ts>-verify-plan.txt --source verify-plan` 으로 05-remediation.md 에 소견으로 올리고, 조치 후 다시 실행한다.

## 2차·2. 정합성 점검표 (2차 — 개정본 기준으로 전부 다시 판정. 기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다. 01-plan 행 번호는 개정본(327행) 기준.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 2차·1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 2장 표 제외 열 "고민 상담 기능 / 인물 간(A–B) 관계 저장 / 관계 태그 필터링 / 상담 페르소나 · 톤 설정 / 음성 입력 / 네이티브 앱" ↔ 01-plan 44행 "**고민 상담·감정 대화**(원칙7) — 응답은 '무엇을 기억했는가'와 되묻기뿐", 45행 "**인물 간(A–B) 관계 저장**(원칙7) … 두 사람 각각의 이벤트이지 둘 사이의 간선이 아니다", 46행 "**상담 페르소나·음성 입력·네이티브 앱**(원칙7)", 40행 "프론트 3화면·PWA·확인 칩 UI(P8-frontend)" 제외. L(iii) 가 범위를 넓히지 않는 근거: 26행 ① "화이트리스트: `name ∉ app.tools.TOOL_NAMES` → 거부" + 277행 "화이트리스트가 **허용 목록**이라 새 동작은 원리상 제안될 수 없고, 삭제 툴은 애초에 없다" — LLM 이 제안할 수 있는 동작이 툴 7종으로 닫혀 있어 상담·A–B 간선을 만드는 툴 자체가 없다. 결정 B(i) 181행 "템플릿은 공감·조언을 만들 수 없다" + 판정 표 18행 부정 테스트 유지. 관계 태그 필터는 산출물(51~71행)·U1~U8 어디에도 없다 |
| 2차·2 | 불변 원칙 1~9 위반 없음 | 통과 | `CLAUDE.md` 원칙1 "확신도가 임계치 미만이면 절대 자동 병합하지 말고 ask_user"·원칙2·원칙4 "반드시 4단계" ↔ 01-plan 27행 "**루프는 확신도를 다시 계산하지도, 임계치를 다시 비교하지도 않는다**", 26행 ④ "`person_id` 는 오직 `resolve()` → `apply_resolution()` 을 거쳐서만", ② "`search_person`·`ask_user`·`get_briefing` 제안은 거부 — 앞의 둘은 ER 4단계 안에서만 불려야 오병합 방어가 유지되고", 판정 표 6·19·20행. L(iii) 의 LLM 1회는 **제안**이지 동일성 판정이 아니므로 원칙4 "엔티티 해석은 LLM 단일 호출로 하지 않는다" 와 무관하다 — 해석은 `app/er/pipeline.py::resolve`(4단계, 무수정)가 그대로 한다(80행 U4). 원칙8 ↔ 41행 "`app/er/` 내부 수정 … 루프는 **호출자로만** 붙는다", 판정 표 10·13·14행, 결정 M-0 243행 ① "`replace` 가 새 객체를 만들고 **`app/er/` 를 한 줄도 고치지 않는다**". 원칙9 ↔ 결정 F 198행 "output 스키마: `{accepted:[{index,name}], rejected:[{index,name,reason}], limits:{…}}`", 34행 "거부한 제안은 사유와 함께 trace 에 남긴다". 원칙5·6·7 은 1행·37~40행과 같다. **원칙 위반은 없다.** 단, 원칙9 를 판정하는 표 7·22행의 기대 출력과 R6 을 판정하는 표 5행의 기대 출력이 계획 자신과 모순돼 판정 불능이다 → §3 H-1·H-5(원칙 위반이 아니라 판정 방법 결함) |
| 2차·3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `D01-new-person-confirm.md` "`create_person` 호출 경로는 반드시 answered pending_question 을 거친다. 직접 호출 테스트는 실패해야 한다" ↔ 01-plan 83행 U7 "`ctx.confirmed_question_id` 를 세운 채 `create_person` 을 부르되 **`context.mention` 이 가리키는 대상에만**", 236행 "`create_person` 은 재개 경로에서만, answered `new_person` 질문과 함께만 실행된다(D1)", 256행 "LLM 이 `create_person` 을 제안할 때 … 게이트를 통과하면 `resume.hints` 로 실린다"(제안은 실행이 아니라 힌트다). `D02-ask-user-async.md` "동기 대기(sleep/poll) 금지. `ask_user`를 다른 툴에 합치지 않는다" ↔ 80행 "D2 — sleep/poll 금지", 판정 표 9행; D2 파급 "답 없이 새 발화가 오면 대기 질문 유지하고 새 발화 우선" ↔ 82행 U6 테스트 + 판정 표 25행(1차 R-4 반영). `D06`(display_name 은 확인 후에만) ↔ 게이트가 `update_person.display_name` 제안을 거부하지 않지만 `app/tools/persons.py` 467행 `update_person` 이 `_require_confirmation` 으로 막으므로 카드 위반은 아니다(R-11 에서 게이트 거부 권고). `D11` ↔ 78행 U2 "`judge.py` 를 고치지 않는다 — import 만 한다". `D12`·`D13` 의 "코드에서 지켜야 할 것" 은 전부 `app/er/*` 대상 → 41행·73행 무수정. `D09`·`D10` 은 1차와 동일(P6-memory, 임계치 미참조) |
| 2차·4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | **1차 H-2 사유 해소** — `S3.4-ask-user-protocol.md` 13행 "`context`에는 재개에 필요한 것만(발화, 후보 id, 확신도 분해). 비밀·전체 대화 이력 저장 금지" ↔ 결정 M-0 243행 "`apply_resolution()` 을 부르기 전에 `dataclasses.replace(resolution, ask_payload=…)` 로 `context` 를 확장", 245행 크기 통제(요지: ㉮ 게이트 통과 제안 ㉯ 미저장 draft ㉰ hints 세 가지뿐, "발화 원문은 ER 이 이미 `context["utterance"]` 로 **1건**", `LOOP_MAX_RESUME_BYTES`), 판정 표 23·24행. 코드로 확인: `app/er/types.py` 193~194행 `@dataclass(frozen=True) class Resolution`, 243행 `ask_payload: dict[str, Any] | None = None`(replace 가능); `app/er/pipeline.py` 474~479행 `question = ask_user(ctx, kind=payload["kind"], question=payload["question"], options=payload["options"], context=payload["context"])` — 네 키만 뽑아 넘기므로 확장된 `context` 가 그대로 저장된다; `app/tools/questions.py` 152~178행 `_validate_context` 는 최상위 키 이름(`_SECRET_KEY_MARKERS` 91행)과 `AFFIRMATIVE_KEY` ⊆ options(175행)만 검사 → `"resume"` 키는 통과. `S3.2-tools-v2.md` "런타임이 raw_utterance 자동 주입" ↔ 28행; "모든 툴 호출은 `agent_traces`에 … 기록" ↔ 244행 (b) 경로 폐기 + 판정 표 23행 `PendingQuestion|flag_modified|\.context *=` 0건. `S3.1-schema-v2.md` "`pending_questions.kind` ∈ {identity, new_person, schedule}" ↔ K(i)·M-2, `app/db/models.py` 73행; 판정 표 11행 `alembic check`. `S3.3-er-pipeline.md` "**LLM 단일 호출로 대체 금지**(원칙4). **T_merge 미만 자동 병합 금지**" ↔ 27행·80행. S 카드 충돌은 없다. M-1(d)가 01-plan 자신의 M-0 ③ 문장과 모순되는 것은 S 카드 문제가 아니라 계획 내부 불일치 → §3 H-4 |
| 2차·5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | 1차와 동일 상태(코드 커밋 0). `docs/backlog.md` P5 항목 "의존: P3, **P4b 게이트 통과**(P4 는 부분완료·미달, CR-001)". `packages/P4b-er-redesign/04-review.md` `결과: 완료`(1차 확인 144행), `packages/P2-tools/04-review.md` `결과: 완료`, `packages/P3-er/04-review.md` `결과: 완료`. 기계 검증 §1a "PASS  P4 게이트 통과 (P4b-er-redesign)". gitlog(16:22) `1075dd6 docs(P4b-er-redesign): 패키지를 닫는다 — 게이트를 통과했고 위키를 정리한다`. 01-plan 10행이 게이트 수치 `0.8 [] True True` 와 해시 `1075dd6`·`855a26b`·`4338eea`·`cf5a171` 을 인용 |
| 2차·6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` P5 절 첫 항목 "- [ ] [backend-agent] 에이전트 루프(인식→해석→기록→응답) + ask_user 재개 / 의존: P3, **P4b 게이트 통과**(P4 는 부분완료·미달, CR-001) / 수용기준: 발화 → 툴 선택 → 저장 → 응답이 API 한 흐름으로 동작, `POST /answers/{question_id}`로 루프 재개" = 01-plan 89행. 기계 검증 "PASS  backlog 일치". `git diff 1227026 -- docs/backlog.md` 에서 이 줄은 **문맥 줄**(무변경)이고, 이번에 더해진 것은 리스크 로그 "**다중 사용자 격리가 없다(F-fbaaae)** … 사용자 승인 2026-09-23" 1항목뿐 — **수용 기준 문장은 바뀌지 않았다.** 해석 절(91~101행)은 "위 한 줄을 바꾸지 않는다" 를 지키며 "툴 선택" 해석만 L(iii) 로 갱신했다(95행 "LLM 이 고르고 코드가 거른다"). 단, backlog P5 항목 아래 세분화 줄 "(U1~U7). 70행의 문장" 과 "전부 (i)): 툴 선택은 코드가 한다(LLM 은 구조화 추출만)" 은 개정 전 내용이라 **backlog 의 결정 기록이 확정 L(iii) 와 모순**된다 — 01-plan 270행 개정 제안 2 가 이미 고치라고 적어 두었고 아직 반영 전 → R-9 |
| 2차·7 | 작업 단위마다 Refs 태그 | 통과 | 기계 검증 §1a "PASS  Refs 있음" U1~U8 8건. 01-plan 77~84행 각 단위 끝 `Refs: P5-loop …`(U1 `S3.2 S3.4 원칙9`, U2 `D11 S3.4 원칙7 원칙9`, U3 `S3.2 원칙1 원칙4 원칙9`, U4 `D1 D2 D12 D13 S3.3 S3.4 원칙1 원칙2 원칙4`, U5 `S3.2 S3.4 원칙7 원칙9`, U6 `R7 D2 S3.4 원칙9`, U7 `**R6 R7** D1 D2 S3.4 원칙1`, U8 `R6 R7 원칙8 원칙9`), 04-review 행 `Refs: P5-loop R6 R7 D1 D2`. 단위 = 커밋 하나: 75행 "단위 하나 = 커밋 하나 후보", 291행 "`app/agent/` 6파일과 `app/api/` 3파일을 한 단위로 묶지 않는다 … L(iii) 로 게이트가 생기면서 U3 이 독립 단위가 됐다". U8(소견 채움 + 판정 표 전행 + registry + README + user-setup)은 P4b U7 `cf5a171` 과 같은 크기의 선례가 있다. U4·U5 가 같은 `loop.py` 를 두 커밋으로 나누는 것은 해석/기록 구간이 분리돼 있어 무리가 없다 |
| 2차·8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §1 "로그·trace에 키·비밀을 남기지 않는다" ↔ 01-plan 78행 U2 "프롬프트에 키·환경변수·전체 대화 이력을 넣지 않는다", 결정 G 202행 "예외 코드·공급자명·프롬프트는 응답에 담지 않고 trace 에만 어휘로", 판정 표 15행. §1 "`.env` … 읽지도 쓰지도 않는다" ↔ 105행 "`.env` 는 스크립트가 읽지 않는다". §4 "로컬 서버 이외로 데이터 전송 금지" ↔ 판정 표 8행 `127.0.0.1:8000`. §5 "`pending_questions.context`에는 재개에 필요한 것만. 전체 대화 이력 저장 금지" ↔ 245행 크기 통제 + 판정 표 24행; `ask_user` 의 비밀 검사가 최상위 키 이름만 본다는 한계(`questions.py` 152~160행)를 245행이 "중첩 값에 비밀이 없게 하는 것은 루프의 몫" 으로 받았다. §5 "`DELETE /persons/{id}`" ↔ backlog P2 절에 별도 항목 신설(사용자 승인, 1차 R 반영). §5 "모든 조회는 `user_id` 조건" 의 미충족(F-fbaaae)은 backlog 리스크 로그 1항목으로 남았다(1차 R-6 반영). 프롬프트 주입은 277행 "게이트가 유일한 방어선 … 화이트리스트가 허용 목록" — 삭제·외부 전송 툴이 없어 제안될 수 없다. 삭제·강제 푸시·재귀 삭제 명령 없음 |

## 2차·2b. 확정 결정 ↔ 구조 변경(L(iii)) 재대조 — 확정 11건 중 성립하지 않게 된 것이 있는가

| 결정 | 2차 판정 | 근거 |
|---|---|---|
| A(i) 상한 5·5·3 | 정합 — 적용 지점만 이동, 결정 유지 | 177행 "5·5·3 은 게이트가 **LLM 제안 목록**에 적용한다(언급 = 서로 다른 `args.person` 값의 수, 이벤트 = `add_event` 제안 수, 일정 = `add_schedule` 제안 수)". 상한 3종·`stop_reason="limit"`·알림 한 줄 그대로. 구멍: `update_person`·`create_person` 제안 수에는 상한이 없다 → R-13 |
| B(i)·D(i)·G(i)·H(i)·I(i) | 정합 — L(iii) 와 무관 | 1차 2b 표와 같다. R-3 는 U6 82행("`SQLAlchemyError` 는 삼키지 않고")·판정 표 26행에 반영됐다 |
| C(i) 순차 처리·첫 되묻기에서 턴 종료 | 정합 · 재개 체인 미기술 | 185행 그대로. 다만 재개에서 남은 언급을 `resolve()` 하면 또 되묻기가 날 수 있고(E(i) "해석 단계부터"), M-2 의 `schedule` 질문도 identity 질문 뒤에 올 수 있다 — `resume_turn` 이 새 `pending_question` 으로 끝나는 케이스가 U7 테스트에 없다 → R-14 |
| E(i) 재개는 해석 단계부터 | 정합 | 193행. L(iii) 에서 "보류 draft" = 게이트 통과 제안(`pending_calls[]`) — 인식 LLM 을 다시 부르지 않는다는 원칙이 그대로다 |
| F(i) `tool_name="agent"` + `loop_` 5종 → **6종** | **같은 규약 안의 확장으로 판정 — 확정을 뒤집은 것은 아니다** | 규약의 실체는 `tool_name="agent"`·`loop_` 접두사·"한 단계 = 한 행"(198행 ③)이고 이름 5종은 불변이다. L(iii) 가 게이트라는 단계를 만들었으니 그 규약을 적용하면 행이 하나 는다. P3-er `er_resolve` 선례와 `agent_traces` 컬럼(S3.1) 그대로. 다만 개정 이력 5행 "확정 11건 … 은 그대로다" 는 F(5→6)·A(적용 지점)에 대해 정확하지 않으므로 **사용자 `승인:` 이 그 둘을 명시적으로 덮어야** 한다 → R-10. `loop_extract` 이름과 `propose.py` 파일명의 어긋남은 F 를 지키려는 의도적 선택(198행)이며 docstring 한 줄이면 된다(R-16) |
| J(i) 409 + `context["mention"]` 바인딩 | 정합 · 사실 재확인 | `app/tools/persons.py` 266~308행 `_require_confirmation` 6검사(마지막 306행 `question.answer not in affirmative_options`). `questions.py` 255~262행 `already_answered` → 409. L(iii) 가 바꾼 것 없음 |
| K(i) + M-2(i) `ask_user(kind="schedule")` | 정합 · **루프가 `ask_user` 를 직접 부르는 두 번째 자리**가 생긴다 | ER 밖에서 `ask_user` 를 부르는 것은 코드이지 LLM 이 아니므로 게이트 ② 와 충돌하지 않고, D2 "독립 툴 유지" 와 정합. `questions.py` 96행 `_AFFIRMATIVE_REQUIRED_KINDS = ("identity", "new_person")` — `schedule` 은 `AFFIRMATIVE_KEY` 불요. 답 검증은 263행 `answer not in question.options` → M-2(i) "후보 시각 2~3개 + 모르겠어요" 와 정합. 재개가 `add_schedule(person_id, title, scheduled_at)` 을 부르려면 `person_id`·`title` 이 `resume` 에 있어야 하는데 U1 의 `PendingResume` 스키마에 없다 → H-4 |
| L(iii) 하이브리드 | 기획서 정합 — §2c H-3 | 아래 |
| M-0 `dataclasses.replace` 경로 | 정합 · 코드 확인 | 위 점검표 4행. (b) ORM 직접 수정은 판정 표 23행 부정 grep 으로 막혀 있다 |
| M-1(d) 태그별 긍정 옵션 | 카드·코드 제약과 **충돌 없음** · 01-plan 내부 불일치 있음 | 코드: `questions.py` 137~150행 `_validate_options` 는 개수 상한 없음·중복만 거부 → 태그 5(`models.py` 71행 `RELATION_TAGS`) + "아니요" = 6개 서로 다른 문자열 통과; 175행 `AFFIRMATIVE_KEY ⊆ options` → 루프가 `context[AFFIRMATIVE_KEY]` 도 태그 옵션 5개로 **함께** 바꿔야 통과; `persons.py` 306행 `question.answer not in affirmative_options` → 태그별 옵션 중 하나가 답이면 통과; `create_person` 430행 `relation_tag not in RELATION_TAGS` → 답→태그 매핑 값이 고정 집합이면 통과. D1 "긍정 답" 규약은 identity 가 이미 후보 이름 여러 개를 affirmative 로 두는 선례(`pipeline.py` 208행 `AFFIRMATIVE_KEY: list(names)`)라 깨지지 않는다. **불일치**: M-0 243행 ③ "ER 이 이미 넣은 키(… `AFFIRMATIVE_KEY`)는 **읽지도 고치지도 않고** 최상위에 `"resume"` 한 키만 더한다" 와 U4 80행의 `replace` 식(`resume` 만 추가)이 M-1(d) 260행 "`options`/`affirmative_options` 를 … 태그별 긍정 옵션으로 확장" 과 모순된다. `er_resolve` trace output 에는 원본 `ask_payload`(옵션 2개)가, `ask_user` 의 `tool_call` trace 와 저장 행에는 확장본(6개)이 남는다 — 어느 것이 권위인지 한 줄 필요(R-16). LLM 힌트가 있어도 태그를 묻는지(항상 묻기 / 힌트 있으면 생략)가 없다 → H-4 |
| M-2(i) 후보 시각 + "모르겠어요" | 카드·코드 제약과 충돌 없음 | 위 K 행. `resume["schedule_options"]` 는 항목 3~4개의 문자열→ISO 사전이라 `LOOP_MAX_RESUME_BYTES` 와 충돌하지 않는다. 후보 시각을 만드는 규칙(263행 "U5 에서 정해야 한다")은 03-log 몫으로 남겨도 된다 |

## 2차·2c. 1차 보류 3건의 닫힘 판정

- **H-1 — 미닫힘(부분).** 판정 표 7행은 이제 **실행 가능한 명령**이고 조회 대상(`agent_traces(session_id, step, tool_name, output)`, S3.1)·세션 id(`r.session_id`)가 고정돼 있어 1차가 지적한 "자리표시자" 문제는 풀렸다. 그러나 **기대 출력이 구조상 성립할 수 없다** — `verification.md` 31행 "이 명령을 치면 이것이 보인다" 의 "이것" 이 틀렸다. (a) "`accepted` 의 툴 이름 집합 = 첫 줄 `tool_call` 행의 `tool_name` 집합": 한 턴의 `tool_call` 행에는 ER 내부 호출이 반드시 섞인다 — `app/er/candidates.py` 41행 `from app.tools.persons import search_person`(`persons.py` 138행 `@traced("search_person")`), merge 경로의 `update_person`(`pipeline.py` 455행, `persons.py` 467행 `@traced`), 되묻기 경로의 `ask_user`(`questions.py` 183행 `@traced`). 이 셋은 게이트 ② 가 LLM 제안에서 거부하므로 `accepted` 에 있을 수 없다 → 등식은 **어떤 턴에서도 거짓**이다. (b) 7행의 발화 "어제 민수랑 저녁 먹었어" 를 빈 DB 에서 돌리면 후보 0 → `pipeline.py` 15~17행 "통과 후보가 0건이면 호출하지 않는다" → `new_person` 되묻기 → C(i) 로 턴 종료 → `add_event` 제안은 실행되지 않고 `resume` 으로 가며 `loop_record` 행은 나올 이유가 없다. 기대 출력 "`loop_record` … 이 모두 있고 … `accepted` = 실행" 은 계획이 스스로 "정상 경로"(282행, 되묻기 23.5%)라 부른 기본 케이스에서 실패한다. 민수가 DB 에 있으면 반대로 `resolve()` 344행 `judge_from_env()` 가 실 공급자 판정기를 만들고 LLM 을 부른다 — 7행 명령은 `run_turn(…, judge=…)` 인자(59행 시그니처에 있다)를 주지 않아 **키·네트워크에 의존**한다. (c) `create_person` 제안은 게이트를 통과하지만(② 에 없다) 실행되지 않고 힌트로만 쓰인다(236·256행) → `accepted` 와 실행 집합이 또 어긋난다. 22행("같은 턴의 `tool_call` 행 수 = `accepted` 수")도 같은 이유로 거짓이다. **조치(architect)**: 기대 출력을 "`loop_gate.output.accepted[]` = `loop_record.output.executed[]`(인덱스·`trace_id` 로 연결) ∪ `context["resume"]["pending_calls"][]`(보류) ∪ 힌트 전용(`create_person`)" 으로 바꾸고 `tool_call` 비교는 `loop_record.executed[].trace_id` 가 가리키는 행으로 한정한다; 명령에 `judge=FakeJudge(...)` 를 넣고, 빈 DB(되묻기로 끝남)와 시드 DB(merge 로 끝남) 두 기대 출력을 따로 적는다. 이것은 U1 의 `GateVerdict`/`loop_record` output 스키마를 정하는 일이므로 **U1 착수 전**에 닫혀야 한다.
- **H-2 — 닫힘.** 경로가 명시됐고 코드가 뒷받침한다(점검표 4행 근거: `types.py` 193·243행, `pipeline.py` 474~479행, `questions.py` 152~178행). `app/er/` 무수정 제약을 지키고(새 객체를 만들 뿐), `ask_user` 의 검증을 우회하지 않으며(같은 `ask_user` 호출을 지난다), ORM 직접 수정은 판정 표 23행 부정 grep 이 막는다. `new_person` 재개의 `relation_tag`/`hierarchy` 출처도 M-1(d)로 정해졌다. 남은 것은 M-1(d)·M-2(i) 확정이 U1·U4·U7·M-0 본문에 반영되지 않은 **계획 내부 불일치** → H-4(새 보류, H-2 의 재개방이 아니다).
- **H-3 — 닫힘. "CR·새 D 카드가 필요 없다" 는 주장은 성립한다.** `docs/proposal.md` 3.1 절 제목 "툴 정의 (Function Calling)"·72행 "파이프라인 하드코딩이 아니라 LLM이 툴을 선택·호출하는 구조로 설계한다" ↔ 01-plan 25행 "LLM **1회** 구조화 출력으로 `{tool_calls: [{name, args}, …]}` 를 받는다" — 선택 주체가 LLM 이고, 코드는 거른 뒤 실행한다(함수 호출 런타임의 통상 구조). 176행 "툴 호출 정확도 | 올바른 툴을 선택한 비율" ↔ 299행 "분모는 `loop_extract.output.tool_calls` 의 제안 수, 분자는 라벨과 일치하는 제안 수" — 잴 대상(선택 행위)이 실재한다. 108행 "다단계 루프 … 각 단계에서 툴 선택이 일어난다" ↔ 인식(LLM 제안)·해석(ER 이 band 로 `update_person`/`ask_user` 선택, S3.3 그대로)·기록(통과 제안 실행) 세 단계에서 선택이 일어난다. 원칙1·4 는 게이트 ④(`person_id` 금지)와 ②(`ask_user`·`search_person` 거부)로 지켜지므로 기획서를 지키면서 D 카드가 새로 필요한 이탈이 없다. 확정 L(iii) 의 기록 위치가 01-plan 과 backlog 세분화 줄인데 후자가 아직 "(i)" 로 적혀 있는 것은 R-9 다.

## 2차·2d. 구조 변경(L(iii)·M-1·M-2)이 만든 새 위험 — 코드로 확인한 사실과 함께

1. **`person_id` 를 얻는 길이 셋이다 — 계획은 하나라고 적었다.** ① `apply_resolution()` merge(현재 턴), ② 재개 `identity`: `context["candidate_ids"][answer]`(ER 이 `_build_ask_payload` 199행에서 넣은 값), ③ 재개 `schedule`(M-2): `context["resume"]` 안의 `person_id`(루프가 넣는 값 — U1 스키마에 아직 없다). ②③ 은 **저장된 `context` 에서 읽는** 경로다. 신뢰 근거는 (가) `context` 를 쓰는 유일한 길이 `ask_user`(판정 표 23행 grep), (나) 클라이언트 입력은 `AnswerIn.answer`(`app/api/schemas.py` 19~23행) 하나이고 그 값은 `options` 안이어야 한다(`questions.py` 263행) — 그래서 우회로는 아니다. 그러나 236행 "`person_id` 의 유일한 출처는 `apply_resolution()` 이다" 는 사실과 다르고, 판정 표 19~22행 부정 테스트는 LLM 경로만 본다. `args` 안 다른 키(`facts` 값·`content` 문자열)로 인물을 가리키는 것은 문자열일 뿐 툴이 id 로 해석하지 않으므로 우회가 아니다(`records.py` 70~76행 `add_event` 는 `person_id: int` 만 받는다). → H-4 에서 `PendingResume` 에 `person_id` 필드를 두고 "저장된 context 는 두 번째 출처이며 23행이 그 신뢰의 근거" 를 236행에 적는다.
2. **게이트 ③ 의 "의도적 불일치는 하나" 가 사실이 아니다.** 279행 "유일한 **의도적 불일치**는 `person_id` → `person` 치환 하나" — 실제 툴 시그니처는 `ctx` 가 첫 인자이고(`scripts/tools_check.py` 문서 3항), `add_event` 는 `raw_utterance` 가 **필수**다(`records.py` 70~76행). 루프가 주입하는 인자는 `ctx`·`person_id`·`raw_utterance` 셋이다. 게이트가 `inspect.signature` 로 "필수 누락" 을 보면 `raw_utterance` 없는 모든 `add_event` 제안이 `bad_args` 가 되고, 반대로 LLM 이 `raw_utterance` 를 주면 원문 보존(S3.2 "런타임이 raw_utterance 자동 주입") 이 깨진다. `update_person.display_name` 제안(D6 확인 필요)과 `create_person` 제안(실행 금지, 힌트 전용)도 게이트 어휘에 없다. → R-11.
3. **U2/U3 경계 — 이중 검사 문장.** 25행 "`add_event` 의 `type` 은 … 7종 밖 값을 받지 않는다(`EVENT_TYPES` 재사용)" 는 인식 단계(U2) 문장이고, 판정 표 21행은 같은 것을 게이트 `bad_args` 로 본다. 78행 "두 자리에서 같은 검사를 하지 않는다" 와 어긋난다. 스키마 enum 은 LLM 유도, 게이트가 강제(원칙1 "프롬프트 의존 금지")라고 정리하면 된다 → R-12.
4. **`loop_gate` step** — 2b F 행. 규약 안의 확장. R-10.
5. **`extract.py` → `propose.py`** — 산출물 57행·U2 78행·테스트 61행(`test_agent_propose.py`)·허용 파일 각주 73행 "신규 6"·U8 84행 "새 모듈 6·엔드포인트 1·테스트 5"·291행 "`app/agent/` 6파일" 모두 일치. 기계 검증의 `extract.py` 토큰은 57행 문장 속 옛 이름이라 무해. backlog 74행 "(U1~U7)" 만 옛 것 → R-9.
6. **U8 단위 경계** — 점검표 7행. 문제 없음.
7. **`embedder=None` 구멍 — 사실이다(부분).** `app/api/deps.py` 61행 `embedder=None`; `app/tools/persons.py` 451·460행 `create_person` 이 `embedder=ctx.embedder` 로 `_add_alias` 를 부르고 353~357행 `provider is None` 이면 `embedding = None` 으로 저장; `search_person` 192·205행 임베딩 top-K 가 `PersonAlias.embedding.is_not(None)` 로 거른다 → 임베딩 채널에서는 빠진다. 다만 같은 함수의 별칭 정확/부분 일치 채널은 문자열로 찾으므로 "후보 검색에서 완전히 빠진다" 는 아니다 — 다른 표기("민수" ↔ "김민수 대리")일 때 미검출이 된다. 판정 표 27행의 조치는 방향이 맞지만 **조건부("임베더가 설정된 환경에서")** 라 키 없는 환경에서는 판정이 비어 있다 → R-15(스텁 임베더 pytest 로 기계화).
8. **재개 체인.** C(i) 순차 처리 + E(i) 해석부터 = 재개 중 다른 언급의 `resolve()` 가 또 되묻을 수 있고, M-2 의 `schedule` 질문이 identity 뒤에 온다. `resume_turn -> TurnResult` 에 `pending_question` 이 있어 구조는 받지만 U7 테스트 목록·`AnswerOut` 확장 설명에 "재개가 새 질문으로 끝난다" 가 없다 → R-14.
9. **A(i) 상한의 구멍** — `update_person`·`create_person` 제안 수 무상한 → R-13.
10. **M-1(d) 두 기록.** `er_resolve` trace(`Resolution.ask_payload` 원본 2옵션) vs `ask_user` `tool_call` trace·`pending_questions` 행(6옵션). 원칙9 위반은 아니나 04-review·P10 이 읽을 곳을 한 줄로 정해야 한다 → R-16.

## 2차·3. 보류 소견과 조치 (2차)

**보류(H) — 하나라도 남으면 결과는 보류. 조치는 architect(01-plan 문장), 사용자 승인. 코드 결정을 뒤집는 것은 없다.**

- **H-1(잔존) 판정 표 7·22행의 기대 출력이 성립할 수 없다.** 근거·조치는 §2c H-1. 한 줄 요약: `accepted` 집합과 `tool_call` 행 집합의 등식은 ER 내부 `search_person`/`update_person`/`ask_user` trace 때문에 어떤 턴에서도 거짓이고, 7행의 예시 발화는 빈 DB 에서 되묻기로 끝나 `loop_record` 가 없으며, `judge=` 를 주지 않아 시드 DB 에서는 실 LLM 을 부른다. 기대 출력을 `loop_record.output.executed[]`(인덱스·`trace_id`) ∪ `resume.pending_calls[]` ∪ 힌트 전용 으로 다시 쓰고 `judge=FakeJudge(...)` 를 넣는다. **U1 착수 전**(`GateVerdict`·`loop_record` output 스키마가 여기서 정해진다).
- **H-4(신규) 사용자 확정 M-1(d)·M-2(i) 가 계획 본문에 반영되지 않았다 — 다섯 곳.** (a) U1 77행 `PendingResume` 스키마에 `tag_by_answer{옵션→relation_tag}`(M-1)·`schedule_options{옵션→ISO}`(M-2)·`schedule` 재개용 `person_id`·`title` 이 없다 — U1 이 첫 단위이므로 지금 스키마로 착수하면 U7 에서 되돌아온다. (b) U4 80행 `replace` 식이 `"resume"` 만 더한다 — M-1(d) 는 `options`·`affirmative_options`·`context[AFFIRMATIVE_KEY]` 세 값을 함께 바꿔야 `questions.py` 175행 부분집합 검사와 `persons.py` 306행 긍정 검사를 지난다. (c) U7 83행 "미추론 시 처리는 **결정 M-1** — 사용자 결정 대기" 와 "`relation_tag`·`hierarchy` 는 `context["resume"]["hints"]` 에서" 가 옛 문장이다 — (d) 에서는 `relation_tag` 가 **답**에서 오고 `hints` 는 `hierarchy` 기본값(`동`) 판단에만 쓰인다. (d) M-0 243행 ③ "ER 이 이미 넣은 키(… `AFFIRMATIVE_KEY`)는 읽지도 고치지도 않고" 가 M-1(d) 와 모순 — "`new_person` 질문에 한해 `options`/`affirmative_options`/`context[AFFIRMATIVE_KEY]` 를 태그별 옵션으로 **교체**한다(유일한 예외)" 로 고친다. (e) LLM 힌트(`relation_tag`)가 있을 때도 태그를 묻는가 — 항상 묻고 답이 이긴다 / 힌트가 있으면 ER 원본 질문 그대로, 둘 중 하나를 적는다(테스트 기대값이 갈린다). 판정 표에 M-1(d) 부정 테스트 1행("`new_person` 답이 태그 옵션 밖(`아니요`)이면 `create_person` 0회") 을 더한다.
- **H-5(신규) 판정 표 5행의 기대 출력이 U5·U7 과 모순된다.** 5행: `grep -rn "create_person\|update_person" app/agent/` → "재개 경로 **1곳**에서만 … 인식·기록 단계에는 0건". 그러나 U5 81행은 기록 단계가 "`add_event`·`add_schedule`·**`update_person`** 을 호출한다"(LLM 이 제안한 `facts`/`new_alias`)고 적고, U7 의 identity 재개도 `update_person(person_id, new_alias=mention)` 로 연결한다(이 호출에는 `confirmed_question_id` 가 필요 없다). 올바른 구현이 5행을 반드시 깨뜨린다 → R6 의 기계 판정이 없다. 조치: 5행을 둘로 나눈다 — `grep -rn "create_person" app/agent/` → 재개 경로 1곳 + 앞줄 `ctx.confirmed_question_id` 대입; `grep -rnE "update_person\(.*display_name|display_name=" app/agent/` → 0건(D6). `update_person` 의 `facts`/`new_alias` 호출은 허용 목록으로 적는다.

**권고(R) — 착수를 막지 않는다. 03-log·04-review 에서 확인. R-1~R-8 반영 상태는 아래 끝에.**

- R-9 **backlog 세분화 줄이 확정과 모순된다.** `docs/backlog.md` P5 항목 아래 "세분화는 … (U1~U7). 70행의 문장" 과 "01-plan 결정 항목(… 전부 (i)): 툴 선택은 코드가 한다(LLM 은 구조화 추출만) / …" 은 개정 전 문장이다. 01-plan 270행 개정 제안 2 가 이미 "(U1~U8)" 과 인용문 표기로 고치라고 적었다 — **승인 커밋에서 메인 세션이 함께 반영**하고 결정 요약 줄을 "L(iii) 하이브리드 — LLM 제안 + 코드 게이트" 로 바꾼다. 수용 기준 문장은 손대지 않는다.
- R-10 **`승인:` 줄이 F(5→6종)·A(적용 지점 이동)를 명시적으로 덮어야 한다.** 개정 이력 5행 "확정 11건 … 은 그대로다" 는 이 둘에 대해 정확하지 않다. 규약 안의 확장으로 판정했지만(2b), 확정을 고친 사실을 사용자가 본 기록이 있어야 한다 — 승인 문구 예: "승인: 사용자 (날짜) — F 6종·A 게이트 적용 포함".
- R-11 **게이트 어휘·주입 인자 집합을 `gate.py` 한 곳에 못박는다(279행 "불일치 하나" 정정).** 주입 인자 = `ctx`·`person_id`(← `person` 언급)·`raw_utterance` 셋. LLM 이 `raw_utterance` 를 주면 `bad_args`(덮어쓰기 금지 — S3.2 원문 보존). `update_person.display_name` 제안 → 거부 사유 추가(예: `needs_confirmation`, D6). `create_person` 제안 → 실행 버킷이 아니라 힌트 전용 버킷(`hint_only`)으로 분류해 `loop_gate.output` 에 남긴다(H-1 등식의 세 번째 항). 판정 표 21행에 세 케이스를 더한다.
- R-12 **U2/U3 이중 검사 문장 정리.** 25행의 "`type` 은 7종 밖 값을 받지 않는다" 를 "스키마 enum 으로 LLM 을 유도하되 강제는 게이트(21행)" 로 바꿔 78행 "두 자리에서 같은 검사를 하지 않는다" 와 맞춘다.
- R-13 **A(i) 총 제안 수 상한.** `update_person`·`create_person` 제안이 무상한이다. 총 제안 수 상한 하나(예: `LOOP_MAX_PROPOSALS = 13`) 또는 `update_person` 상한을 더하고 `limits` 에 넣는다 — 결정 A 를 바꾸지 않고 "툴 호출 횟수 자체는 상한을 두지 않는다" 의 뜻(다회 왕복 예산)을 유지한 채 제안 목록 크기만 막는다.
- R-14 **재개 체인 테스트.** U7 에 "재개 중 두 번째 언급이 되묻기 → `AnswerOut` 에 새 `question_id`·`options`, 첫 질문은 answered 유지" 1건과 "identity 답 뒤 `schedule` 질문" 1건. P8 프론트 계약(298행)이 이 응답 모양을 전제한다.
- R-15 **판정 표 27행 기계화.** `tests/test_agent_resume.py -k alias_embedding` 로 스텁 임베더 주입 → `person_aliases.embedding IS NOT NULL` 단언. 키 없는 환경의 `/chat` 은 `embedder=None` → ER `embedding_skipped`(`persons.py` 21행) 로 도는데 그때 새 인물의 별칭이 NULL 로 남는다는 사실을 deps.py docstring 에 적는다(조용한 미검출 방지).
- R-16 **두 기록의 권위 + 이름 어긋남 한 줄.** M-1(d) 확장 옵션은 `ask_user` `tool_call` trace 와 `pending_questions` 행이 권위, `er_resolve.output.ask_payload` 는 ER 원본 — 04-review·P10 이 전자를 읽는다. `loop_extract` step 이름을 `propose.py` docstring 에서 "결정 F 이름 고정, 내용은 제안 원문" 으로 설명한다.
- R-17 **`run_turn` 판정 명령의 `judge=`.** 7·22·27행 세 명령 모두 `judge=FakeJudge(...)` 와 스텁 임베더를 명시해 판정 표 2행 "네트워크 0" 이 판정 명령에도 적용되게 한다(H-1 조치에 포함).
- R-18 **05-remediation 머리줄 갱신.** "열림: 8 (필수 1)" 의 필수 1(`F-25b70f` 02-plan-verify 부재)은 1차 문서 생성으로 사실상 해소됐으나 `상태: 열림` 그대로다 — 메인 세션이 `findings.py` 를 §1b evidence 로 재실행해 해소 표시한다.
- R-19 **`verify-plan.sh` 7절 토큰 추출 결함(하네스).** `[a-z]{1,5}` 확장자 정규식이 문장 속 `inspect.signature`·`app.tools`·`dataclasses.replace` 를 산출물 경로로 오인한다. 계획 결함이 아니므로 이 패키지에서 고치지 않는다 — 하네스 FIX 후보로만 남긴다.

**1차 권고 R-1~R-8 반영 상태**: R-1 반영(116행 `-H "Content-Type: application/json"`·"②에 `X-Session-Id` 를 넣지 않는다" 이유) · R-2 반영(84행 U8 착수 전 소견 7건 원인 분석) · R-3 반영(82행 U6·판정 표 26행) · R-4 반영(82행·판정 표 25행) · R-5 01-plan 은 반영(6행 "줄 번호로 가리키지 않는다"), backlog 74행 "70행" 은 미반영 → R-9 · R-6 반영(backlog 리스크 로그 "다중 사용자 격리가 없다(F-fbaaae)") · R-7 반영(M-2(i)) · R-8 반영(`docs/wiki/fixes/FIX-002.md` 62행이 실재 파일 `evidence/20260923-1526-verify-plan-2.txt` 를 가리킨다 — `ls` 확인).

05-remediation: 2차에서 새 FAIL 없음. H-1·H-4·H-5 는 verifier 판정이므로 findings.py 소견이 아니라 이 절이 기록이다.

## 2차·4. 결정
2차 결과: 보류 — H-1(잔존: 판정 표 7·22행 기대 출력이 ER 내부 `tool_call` 행·되묻기 기본 경로·`judge` 미주입 때문에 성립 불가), H-4(신규: 확정 M-1(d)·M-2(i) 가 U1 `PendingResume` 스키마·U4 `replace` 식·U7 문장·M-0 ③ 에 미반영, 힌트 존재 시 규칙 미정), H-5(신규: 판정 표 5행 기대 출력이 U5 기록 단계의 `update_person` 호출과 모순). **1차 보류 중 H-2·H-3 은 닫혔다** — `context` 확장 경로는 코드(`types.py` 193행 frozen, `pipeline.py` 474~479행 네 키 추출, `questions.py` 최상위 키 검사)로 성립하고, L(iii) 는 `proposal.md` 72·108·176행과 정합해 CR·새 D 카드가 필요 없다는 주장이 성립한다. 점검표 8행 전부 통과 — 세 보류는 원칙·카드 위반이 아니라 **판정 방법과 계획 내부 정합**의 결함이며 전부 01-plan 문장 수정으로 닫힌다(코드 결정 뒤집기 없음, 확정 A~K·M-1·M-2 유지). 사용자 확정 M-1(d)·M-2(i) 는 카드·코드 제약과 충돌하지 않는다. 결정 F 6종·A 적용 지점은 확정 규약 안의 확장으로 판정하되 승인 줄이 명시적으로 덮어야 한다(R-10).
2차 승인: (사용자 승인 전 비워 둔다 → "사용자 (YYYY-MM-DD)")


---

## 5. 1차 판정 기록 (2026-09-23 15:49 — 보존. 점검표 행 번호만 `1차·n` 으로, `결과:` 줄만 `1차 결과:` 로 바꿨다)

평가 대상 커밋: `HEAD = cf82868`(dev). 패키지 시작 해시(무변경 diff 기준점) `1227026`. 기계 검증 전 `bash .claude/scripts/gitlog.sh P5-loop D1 D2 R6 R7` 을 실행했다 — 태그 `P5-loop` 커밋은 `cf82868`(FIX-002 하네스)·`b676799`·`4d5817e`(P2 가 P5 를 지목한 커밋) 셋뿐이고 제품 코드 커밋은 0, 미커밋 변경은 `docs/backlog.md`·`docs/wiki/journal.md`·`docs/wiki/packages/P5-loop/`·`reports/pilot/` 2건(제품 코드 0).

### 5.1 기계 검증 출력 (1차)

#### 5.1a. 1차 — 이 문서를 쓰기 전 (FAIL 1 = 이 문서 자체의 부재)
명령: `bash .claude/scripts/verify-plan.sh P5-loop | tee docs/wiki/packages/P5-loop/evidence/20260923-1544-plan-verify.txt`
```
== verify-plan P5-loop  (2026-09-23 15:44) ==
PASS  존재: docs/wiki/packages/P5-loop/01-plan.md
FAIL  없음: docs/wiki/packages/P5-loop/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D11
PASS  카드 존재: D12
PASS  카드 존재: D13
PASS  카드 존재: D2
PASS  카드 존재: D6
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P6-memory
PASS  검증 항목 존재: R10
PASS  검증 항목 존재: R6
PASS  검증 항목 존재: R7
PASS  Refs 있음: - [ ] U1 **[backend-agent] 루프 계약 타입 + trace 어�
PASS  Refs 있음: - [ ] U2 **[backend-agent] 인식 단계 — 발화 → 구�
PASS  Refs 있음: - [ ] U3 **[backend-agent] 해석 단계 — ER 연결과 �
PASS  Refs 있음: - [ ] U4 **[backend-agent] 기록 + 응답 단계**: 확정�
PASS  Refs 있음: - [ ] U5 **[backend-agent] `POST /chat` — API 한 흐름**
PASS  Refs 있음: - [ ] U6 **[backend-agent] 재개 — `POST /answers/{questi
PASS  Refs 있음: - [ ] U7 **[backend-agent] 수용 기준 기계 검증 + 문
PASS  backlog 일치: [ ] [backend-agent] 에이전트 루프(인식→해석→�
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  registry 중복 없음: app/agent/__init__.py
PASS  registry 중복 없음: app/agent/types.py
PASS  registry 중복 없음: app/agent/extract.py
WARN  registry 에 다른 패키지로 이미 있음: app/er/judge.py → | 모듈 | LLM 판정(3단계, 공급자 중립) | app/er/judge.py | P3-er | b1f
PASS  registry 중복 없음: app/agent/loop.py
PASS  registry 중복 없음: app/agent/respond.py
PASS  registry 중복 없음: tests/test_agent_extract.py
PASS  registry 중복 없음: tests/test_agent_loop.py
PASS  registry 중복 없음: tests/test_agent_resume.py
PASS  registry 중복 없음: tests/test_api_chat.py
WARN  registry 에 다른 패키지로 이미 있음: app/api/routes.py → | 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-t
WARN  registry 에 다른 패키지로 이미 있음: app/api/schemas.py → | 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools 
WARN  registry 에 다른 패키지로 이미 있음: app/api/deps.py → | 엔드포인트 | 요청 단위 세션·ToolContext 조립 | app/api/deps.py |
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
WARN  registry 에 다른 패키지로 이미 있음: tests/test_api.py → | 테스트 | HTTP: /health·/answers 200/404/409/422 | tests/test_api.py | P2-t
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
| 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
| 문서 | FIX-001 main 병합(갈라진 배포 브랜치를 dev 로 되돌린�
== 결과: FAIL=1 WARN=7 ==
```

1차 판정: FAIL 1 은 `02-plan-verify.md` 부재(= 이 문서, 05-remediation `F-25b70f`) — 이 문서가 생기면 닫힌다. WARN 7 은 전부 "registry 에 다른 패키지로 이미 있음" — 01-plan 30행("registry.md 행(새 모듈)·비고 확장(고친 기존 파일)")·77행 U7("고친 기존 파일 … 은 **비고에 P5-loop 한 줄과 커밋 해시를 더한다**(새 행을 만들지 않는다 — F-0ffff5·F-95c6a7 선례)")이 U7 에서 닫는 방식을 이미 적어 두었고, `app/er/judge.py` 는 01-plan 132행이 "**무수정 재사용**(import)" 으로 분류한다. P4b 05-remediation 8행이 같은 성격의 WARN 22건을 "의도적으로 낸 WARN … U7(`cf5a171`)이 기존 행의 비고를 확장하고 새 산출물만 행으로 넣어 닫았다"로 닫은 선례와 동일하다. 열린 소견 `F-e93529`·`F-8e3e74`·`F-6ae8ad`·`F-d68447`·`F-fdb56f`·`F-7e6e84`·`F-0ffff5`(전부 [권고])는 계획 단계 조치 없음, U7 + 04-review §5 에서 해소.

#### 5.1b. 2차 — 이 문서를 쓴 뒤 (FAIL 0 확인)
명령: `bash .claude/scripts/verify-plan.sh P5-loop | tee docs/wiki/packages/P5-loop/evidence/20260923-1549-plan-verify-2.txt`
```
== verify-plan P5-loop  (2026-09-23 15:49) ==
PASS  존재: docs/wiki/packages/P5-loop/01-plan.md
PASS  존재: docs/wiki/packages/P5-loop/02-plan-verify.md
PASS  카드 존재: D1
PASS  카드 존재: D11
PASS  카드 존재: D12
PASS  카드 존재: D13
PASS  카드 존재: D2
PASS  카드 존재: D6
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P3-er
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P6-memory
PASS  검증 항목 존재: R10
PASS  검증 항목 존재: R6
PASS  검증 항목 존재: R7
PASS  Refs 있음: - [ ] U1 **[backend-agent] 루프 계약 타입 + trace 어�
PASS  Refs 있음: - [ ] U2 **[backend-agent] 인식 단계 — 발화 → 구�
PASS  Refs 있음: - [ ] U3 **[backend-agent] 해석 단계 — ER 연결과 �
PASS  Refs 있음: - [ ] U4 **[backend-agent] 기록 + 응답 단계**: 확정�
PASS  Refs 있음: - [ ] U5 **[backend-agent] `POST /chat` — API 한 흐름**
PASS  Refs 있음: - [ ] U6 **[backend-agent] 재개 — `POST /answers/{questi
PASS  Refs 있음: - [ ] U7 **[backend-agent] 수용 기준 기계 검증 + 문
PASS  backlog 일치: [ ] [backend-agent] 에이전트 루프(인식→해석→�
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
WARN  보류 1 건 — 결과는 통과가 될 수 없다
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: app/agent/__init__.py
PASS  registry 중복 없음: app/agent/types.py
PASS  registry 중복 없음: app/agent/extract.py
WARN  registry 에 다른 패키지로 이미 있음: app/er/judge.py → | 모듈 | LLM 판정(3단계, 공급자 중립) | app/er/judge.py | P3-er | b1f
PASS  registry 중복 없음: app/agent/loop.py
PASS  registry 중복 없음: app/agent/respond.py
PASS  registry 중복 없음: tests/test_agent_extract.py
PASS  registry 중복 없음: tests/test_agent_loop.py
PASS  registry 중복 없음: tests/test_agent_resume.py
PASS  registry 중복 없음: tests/test_api_chat.py
WARN  registry 에 다른 패키지로 이미 있음: app/api/routes.py → | 엔드포인트 | GET /health · POST /answers/{id} | app/api/routes.py | P2-t
WARN  registry 에 다른 패키지로 이미 있음: app/api/schemas.py → | 엔드포인트 | API 요청/응답 스키마 | app/api/schemas.py | P2-tools 
WARN  registry 에 다른 패키지로 이미 있음: app/api/deps.py → | 엔드포인트 | 요청 단위 세션·ToolContext 조립 | app/api/deps.py |
WARN  registry 에 다른 패키지로 이미 있음: app/settings.py → | 모듈 | 런타임 설정값 | app/settings.py | P2-tools | f217190 | `app_use
WARN  registry 에 다른 패키지로 이미 있음: tests/test_api.py → | 테스트 | HTTP: /health·/answers 200/404/409/422 | tests/test_api.py | P2-t
PASS  registry 중복 없음: docs/wiki/registry.md
WARN  registry 에 다른 패키지로 이미 있음: README.md → | 문서 | 프로젝트 README(전체 소개·스택·진행 상태·하네스·
| 문서 | 사용자 카드 10 파일럿 평가 실 실행(환경변수 이름·
| 문서 | FIX-001 main 병합(갈라진 배포 브랜치를 dev 로 되돌린�
== 결과: FAIL=0 WARN=8 ==
```

### 5.2 정합성 점검표 (1차)
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1차·1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 2장 표 제외 열: "고민 상담 기능 / 인물 간(A–B) 관계 저장 / 관계 태그 필터링 / 상담 페르소나 · 톤 설정 / 음성 입력 / 네이티브 앱". 01-plan 39행 "**고민 상담·감정 대화**(원칙7) — 응답은 '무엇을 기억했는가'와 되묻기뿐이다", 40행 "**인물 간(A–B) 관계 저장**(원칙7) — 인식 단계가 '민수와 지훈이 싸웠다'에서 뽑는 것은 **두 사람 각각의 이벤트**이지 둘 사이의 간선이 아니다", 41행 "**상담 페르소나·음성 입력·네이티브 앱**(원칙7) — 입력은 텍스트 한 줄, 응답은 결정적 문장이다", 35행 "프론트 3화면·PWA·확인 칩 UI(P8-frontend)" 제외. 관계 태그 필터는 산출물 목록(50~65행)·U1~U7 어디에도 없다. 결정 B(i)(159행) "템플릿은 공감·조언을 만들 수 없다" + 판정 표 18행 부정 테스트가 상담 경계를 구조로 막는다 |
| 1차·2 | 불변 원칙 1~9 위반 없음 | 통과 | `CLAUDE.md` 원칙1 "확신도가 임계치 미만이면 절대 자동 병합하지 말고 ask_user" · 원칙2 두 임계치 · 원칙4 "4단계" ↔ 01-plan 23행 "**루프는 확신도를 다시 계산하지도, 임계치를 다시 비교하지도 않는다**", 73행 U3 "**루프는 confidence·T_merge·T_new 를 읽지도 비교하지도 않는다**", 판정 표 6행 `grep … app/agent/` **0건**·5행 `create_person` 재개 경로 1곳. 원칙5 ↔ 35행(UI 없음). 원칙6 ↔ 33행 D9 는 P6-memory. 원칙7 ↔ 1행. 원칙8 ↔ 36행 "루프를 붙이면서 ER 을 손대면 그 수치의 근거가 사라진다", 판정 표 10·13·14행(허용 파일·ER 회귀·데이터 무변경). 원칙9 "agent_traces 에 step·입력·출력·툴·토큰" ↔ 결정 F(i) `loop_extract/loop_resolve_done/loop_record/loop_turn/loop_resume`, 결정 G·H 가 `loop_error` 를 같은 트랜잭션에 커밋해 남긴다(`app/tools/context.py` 27~31행 "별도 커넥션으로 오류를 영구 기록할지는 **P5-loop 01-plan** 이 결정한다"). 결정 L(i)는 원칙4 의 정신("판정을 단계로 쪼갠 것")과 정합이고 P3-er `apply_resolution` 이 band 로 `update_person`/`ask_user` 를 고르는 선례(`app/er/pipeline.py` 453~477행)와 같은 방식이다 — 다만 기획서 3.1 원문과의 어긋남은 §3 H-3 |
| 1차·3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | `D01-new-person-confirm.md` "`create_person` 호출 경로는 반드시 answered pending_question 을 거친다. 직접 호출 테스트는 실패해야 한다" ↔ 01-plan 76행 U6 "`ctx.confirmed_question_id` 를 세운 채 `create_person` 을 부르되 **`context.mention` 이 가리키는 대상에만**", 판정 표 5행. `D02-ask-user-async.md` "동기 대기(sleep/poll) 금지. `ask_user`를 다른 툴에 합치지 않는다" ↔ 73행 "D2 — sleep/poll 금지", 판정 표 9행 `time.sleep|asyncio.sleep|while True` 0건, ask_user 는 ER `apply_resolution` 이 그대로 부른다(23행). `D09-pattern-rule.md` "적용은 P6-memory" ↔ 33행 제외. `D10-two-thresholds.md` "임계치 하나로 구현하지 않는다" ↔ 루프는 임계치를 읽지 않는다(판정 표 6행). `D12`·`D13` "코드에서 지켜야 할 것" 은 전부 `app/er/*` 대상이고 01-plan 36행·67행이 `app/er/*` 무수정을 못박는다(판정 표 10행). `D11` ↔ 72행 U2 "`app/er/judge.py` 의 등록표·`select_provider(env)`·`enabled_providers(env)`·`call_with_error_mapping` 을 그대로 재사용 … import 만 한다". D2 파급 "답 없이 새 발화가 오면 대기 질문 유지하고 새 발화 우선" 은 01-plan 236행이 읽었다고 적었으나 단위·테스트가 없다 → §3 R-4 |
| 1차·4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | **보류** | `S3.1-schema-v2.md` 12행 `pending_questions(id, session_id, kind, question, options, context, answer, …)`·21행 "`pending_questions.kind` ∈ {identity, new_person, schedule}" ↔ 결정 K(i) `kind="schedule"`, `app/db/models.py` 73행 `QUESTION_KINDS = ("identity", "new_person", "schedule")`; 판정 표 11행 `alembic check` 무변경. `S3.2-tools-v2.md` 10행 "런타임이 raw_utterance 자동 주입" ↔ 74행 U4 "`raw_utterance` = 발화 원문 그대로 루프가 주입"; 판정 표 12행 `tools_check.py 7/7`. `S3.3-er-pipeline.md` 17행 "**LLM 단일 호출로 대체 금지**(원칙4). **T_merge 미만 자동 병합 금지**(원칙1·2)" ↔ 23행·73행(ER 만 판정). `S3.4-ask-user-protocol.md` 6~7행 "턴 N … 턴 종료 / 턴 N+1 칩 선택 → POST /answers/{question_id} → 저장된 context로 루프 재개 → 후속 툴" ↔ U5·U6. **보류 사유(H-2)**: S3.4 13행 "`context`에는 재개에 필요한 것만(발화, 후보 id, 확신도 분해)" — 결정 C(i)·D(i)·E(i) 는 보류 draft·미처리 언급·(new_person 재개에 필요한) 힌트를 `context` 에 싣는데, 그 행을 만드는 것은 무수정 대상인 `app/er/pipeline.py::apply_resolution` 이고 `context` 는 `_build_ask_payload`(165~235행)가 `mention·utterance·candidate_ids·confidence_breakdown·affirmative_options` 만 채운다. 루프가 무엇을 어느 경로로 `context` 에 더하는지(그리고 `ask_user` 의 검증을 우회하지 않는지)가 01-plan 에 없다 |
| 1차·5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `docs/backlog.md` 73행 "의존: P3, **P4b 게이트 통과**(P4 는 부분완료·미달, CR-001)". `packages/P2-tools/04-review.md` 118행 `결과: 완료`, `packages/P3-er/04-review.md` 166행 `결과: 완료`, `packages/P4b-er-redesign/04-review.md` 144행 `결과: 완료`, `packages/P4-pilot-eval/04-review.md` 232행 `결과: 부분완료`(P4b 가 받았다). 기계 검증 §1a "PASS  P4 게이트 통과 (P4b-er-redesign)"(`FIX-002.md` 가 고친 검사, 커밋 `cf82868`). gitlog: `1075dd6 docs(P4b-er-redesign): 패키지를 닫는다 — 게이트를 통과했고 위키를 정리한다`. `docs/wiki/INDEX.md` 81행 "P4 미달 → P4b 게이트 통과가 조건, CR-001" |
| 1차·6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 73행 "- [ ] [backend-agent] 에이전트 루프(인식→해석→기록→응답) + ask_user 재개 / 의존: P3, **P4b 게이트 통과**(P4 는 부분완료·미달, CR-001) / 수용기준: 발화 → 툴 선택 → 저장 → 응답이 API 한 흐름으로 동작, `POST /answers/{question_id}`로 루프 재개" = 01-plan 82행. 기계 검증 "PASS  backlog 일치". `git diff 1227026 -- docs/backlog.md`(미커밋)에서 이 줄은 **문맥 줄**(변경 없음)이고 추가된 것은 74·75행 세분화 줄, P2 절 `DELETE /persons/{id}` 항목(3줄), P10 행 비고 1줄뿐 — 01-plan 205~207행 "backlog 개정 제안" 1·2·3 그대로. 단, 항목 삽입으로 P5 줄이 70→73행이 되어 01-plan 17·233행과 backlog 74행의 "70행" 이 어긋난다 → R-5 |
| 1차·7 | 작업 단위마다 Refs 태그 | 통과 | 기계 검증 §1a "PASS  Refs 있음" U1~U7 7건. 01-plan 71~78행 각 단위 끝 `Refs: P5-loop …`(U1 `S3.2 S3.4 원칙9`, U2 `D11 S3.4 원칙7 원칙9`, U3 `D1 D2 D12 D13 S3.3 S3.4 원칙1 원칙2 원칙4`, U4 `S3.2 S3.4 원칙7 원칙9`, U5 `R7 D2 S3.4 원칙9`, U6 `**R6 R7** D1 D2 S3.4 원칙1`, U7 `R6 R7 원칙8 원칙9`), 04-review 행도 `Refs: P5-loop R6 R7 D1 D2`. 단위 = 커밋 하나 크기(69행 "단위 하나 = 커밋 하나 후보", 224행 "`app/agent/` 5파일과 `app/api/` 3파일을 한 단위로 묶지 않는다") |
| 1차·8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | `security.md` §1 "로그·trace에 키·비밀을 남기지 않는다" ↔ 01-plan 72행 U2 "프롬프트에 키·환경변수·전체 대화 이력을 넣지 않는다", 결정 G(i) 179행 "예외 코드·공급자명·프롬프트는 응답에 담지 않고 trace 에만 어휘(`timeout` 등)로", 판정 표 15행 grep. §1 "`.env` … 읽지도 쓰지도 않는다" ↔ 98행 "`.env` 는 스크립트가 읽지 않는다 … 로드 주체는 사용자 셸". §4 "로컬 서버 이외로 데이터 전송(`curl -d …`) 금지" ↔ 판정 표 8행은 `:8000` 로컬이며 "수동 왕복(사용자)". §5 "`pending_questions.context`에는 재개에 필요한 것만. 전체 대화 이력 저장 금지" ↔ 44행·결정 A(i) 상한이 context 크기 상한, 216행 "원문은 발화 1건만 싣는다". §5 "`DELETE /persons/{id}`" ↔ 43행이 P5 에 끼우지 않고 backlog 항목으로 올려 사용자 승인됨(backlog 38~39행). 삭제·강제 푸시·재귀 삭제 명령 없음. 남는 것: §5 "모든 조회는 `user_id` 조건" 은 `pending_questions`·`agent_traces` 에 `user_id` 가 없어(P1 스키마, F-fbaaae) 이 패키지 전에도 충족 불가 — 결정 I(i) 가 "명시만" 으로 넘긴다 → R-6 |

### 5.2b 사용자 확정 12건 ↔ 카드·원칙 대조 (1차, 01-plan 초안 146행)

| 결정 | 판정 | 근거 |
|---|---|---|
| A(i) 상한 5·5·3, 초과 알림 | 정합 | 카드에 상한 규정 없음. 원칙9 ↔ 155행 "trace 에 버린 수를 남기며". 결정 L(i) 와 짝(툴 호출 수는 상한에서 파생) |
| B(i) 템플릿 응답 | 정합 · 원칙7 경계를 구조로 보장 | `CLAUDE.md` 원칙7 경계 문장 "감정·고민에 대한 대화는 하지 않는다" ↔ 159행 "템플릿은 공감·조언을 만들 수 없다" + 판정 표 18행. `S3.7` 재현성(원칙8)과도 정합 |
| C(i) 순차 처리, 첫 되묻기에서 턴 종료 | 정합 | `D02` "그 턴을 종료" ↔ 163행. `S3.4` 12행 "프론트 확인 칩 = 미답변 pending_questions" 에 질문 1개/턴이 맞다. 미처리 언급을 `context` 에 싣는 경로는 H-2 |
| D(i) 되돌리지 않는다 | 정합 | 원칙9 ↔ 167행 ②③; 롤백하면 `pending_questions` 행·`agent_traces` 가 같은 트랜잭션에서 사라진다는 주장은 `app/api/deps.py` 35~45행(`get_session` 예외 시 `rollback()`)·`app/tools/questions.py` 224~226행(`ask_user` 는 `add`+`flush` 만)으로 사실이다 |
| E(i) 재개는 해석 단계부터 | 정합(원칙8) · 실행 경로 미정(H-2) | `S3.4` 13행 "재개에 필요한 것만" — 보류 draft 는 발화 1건에서 뽑은 구조화 결과이지 "전체 대화 이력" 이 아니므로 그 문장과 충돌하지 않는다. 다만 누가 어떻게 `context` 에 넣는지 없음 |
| F(i) `tool_name="agent"` + `loop_` 5종 | 정합 | P3-er 선례(`app/er/pipeline.py` `ER_TRACE_TOOL_NAME`·`step=ER_TRACE_STEP`), `S3.1` 14행 `agent_traces(… step, tool_name …)` 컬럼 그대로. `app/db/models.py` 에 step 값 CHECK 없음(registry 44행 값 집합 상수 `EVENT_TYPES`·`QUESTION_KINDS` 만) |
| G(i) 200 + 한 줄 + 저장 0 + `loop_error` | 정합(원칙9) | 179행 "예외 코드·공급자명·프롬프트는 응답에 담지 않고" ↔ `security.md` §1. 예외 종류 범위는 R-3 |
| H(i) 예외를 삼켜 같은 트랜잭션에 커밋 | 정합(원칙9) · 사실 확인됨 | `app/tools/context.py` 27~31행 인용: "별도 커넥션으로 오류를 영구 기록할지는 **P5-loop 01-plan** 이 결정한다 -- 이 한계를 지금 여기서 우회(예: 별도 커넥션 즉시 커밋)로 고치지 않는다" — 01-plan 183행 주장 그대로다. `deps.py` 40행 정상 종료 `commit()` 이므로 200 이면 `loop_error` 행이 남는다. 단 DB 오류(`SQLAlchemyError`)를 삼키면 세션이 롤백 필요 상태라 `commit()` 이 실패한다 — 어느 예외를 삼키는지 범위가 없다 → R-3 |
| I(i) 헤더 없으면 `uuid4`, 격리 부재 명시 | 정합 · 기존 결함 승계 | P2 04-review 107행 "`X-Session-Id` 헤더 규약은 채팅 엔드포인트가 정한다", 110행 "`user_id` 격리가 없다(F-fbaaae, 해소=명문화)". `security.md` §5 "모든 조회는 `user_id` 조건" 은 스키마상 불가(위 8행) → R-6 |
| J(i) 소비 1회 = 409, 대상 = `context["mention"]` | 정합 · 사실 확인됨 | `app/tools/persons.py` 266~310행 `_require_confirmation` 6검사 = `no_confirmation`·`not_found`·`wrong_kind`·`not_answered`·`session_mismatch`·`not_affirmative` — **`display_name`·`mention` 을 읽는 검사는 없다**(01-plan 148행 주장 사실). `questions.py` 258~262행 `status == "answered"` → `QuestionNotAnswerable("already_answered")` 가 409(`app/main.py` `_question_not_answerable_handler`). `D01` "answered pending_question 을 거친다" 는 P2 가 닫았고, P2 04-review 108행 구멍(임의 이름·다회)을 J 가 `context` 바인딩 + 409 로 닫는다. 남는 구멍: `create_person` 은 `relation_tag`·`hierarchy` 가 필수인데 ER 이 만든 `context` 에는 없다 → H-2 에 포함 |
| K(i) 이벤트는 `now`, 일정은 `ask_user(kind="schedule")` | 정합 | `S3.1` 21행·`D01` 파급 "`ask_user.kind` ∈ {identity, new_person, schedule}"·`models.py` 73행. P4 04-review 214행 "`ask_user(kind=schedule)` … P5 루프가 만든 뒤 P10 이 잰다". `questions.py` 200~203행: `schedule` 은 `AFFIRMATIVE_KEY` 불요. `options` 내용은 미정 → R-7 |
| L(i) 툴 선택은 코드가 한다 | S·D 카드 위반 아님 · 기획서 3.1 원문과 어긋남 → H-3 | 어느 S 카드도 툴 선택 주체를 정하지 않는다. `S3.3` 17행 "LLM 단일 호출로 대체 금지", 원칙1·4 는 (i)를 지지하고, `apply_resolution` 이 band 로 툴을 고르는 P3-er 가 이미 같은 방식이다. `CLAUDE.md` "툴 7종을 호출하고 엔티티 해석을 수행하는 런타임 에이전트" 도 위반이 아니다(호출은 한다). 그러나 `docs/proposal.md` 72행 "**파이프라인 하드코딩이 아니라 LLM이 툴을 선택·호출하는 구조로 설계한다**", 108행 "각 단계에서 툴 선택이 일어난다는 점이 에이전트 구조의 근거", 176행 "툴 호출 정확도: 올바른 툴을 선택한 비율" 과 정면으로 다르고, 이 어긋남을 기록한 D 카드·R 항목·기획서 상단 안내문·`S3.7` 갱신이 없다(`grep -rni "function calling\|툴 선택" docs/wiki/decisions docs/wiki/review-index.md docs/proposal-review.md` 0건). 01-plan 17행 "새 결정·새 명세를 만들지 않는다" 와도 어긋난다 |

### 5.3 보류 소견과 조치 (1차)

**보류(H) — 하나라도 남으면 결과는 보류. 조치는 계획 작성자(architect)·메인 세션, 사용자 결정.**

- **H-1 판정 표 7행이 실행 가능한 명령이 아니다.** 01-plan 108행은 `python -c "<한 턴 실행 후 agent_traces 조회 …>"` 자리표시자이고 122행이 "지금 스키마가 없어 필드 이름을 못 박을 수 없다" 고 했으나, 조회 대상 `agent_traces(session_id, step, tool_name)` 은 `S3.1` 14행으로 이미 고정돼 있고 세션 id 는 결정 I(i) `ChatOut.session_id` 로 확정됐다. 이 행은 수용 기준 해석 두 조항("에이전트 루프(인식→해석→기록→응답)" 판정 표 3·7행, "툴 선택" 판정 표 7행 **단독**)의 유일한 기계 판정이다. `verification.md` 6행 "이 중 하나가 없으면 보류", 31행 "수용 기준마다 '이 명령을 치면 이것이 보인다'를 적고". 조치: U1 착수 전에 7행을 실행 가능한 형태로 채운다 — 예: `PYTHONUTF8=1 POSTGRES_PORT=5433 python -c "…run_turn(ctx, '<발화>', extractor=FakeExtractor(...))…; print(session.execute(text('SELECT step, tool_name FROM agent_traces WHERE session_id=:s ORDER BY id'), {'s': sid}).all())"` 와 기대 출력(`loop_extract`·`loop_resolve_done`·`loop_record`·`loop_turn` 4종 + `tool_call`(툴 7종 이름) 1건 이상 + `er_resolve` 1건 이상). 8행(curl)은 실행 가능하므로 보류 아님(R-1).
- **H-2 `pending_questions.context` 확장 경로가 없다(S3.4 13행·D2·원칙9·S3.2 16행).** 결정 C(i)·D(i)·E(i)·J(i) 는 재개에 "보류 draft·미처리 언급·`mention`·`candidate_ids`" 가 `context` 에 있어야 성립하는데, 그 행은 무수정 대상 `app/er/pipeline.py::apply_resolution`(469~477행)이 `resolution.ask_payload["context"]` 를 `ask_user` 에 그대로 넘겨 만들고, 그 `context` 는 `_build_ask_payload`(165~235행)가 `mention·utterance·candidate_ids·confidence_breakdown·affirmative_options` 만 채운다. 01-plan U4(74행) "`pending_questions.context` 에 실어 재개에 넘긴다" 는 **누가·어느 API 로** 싣는지 없다. 두 가지 길이 있고 둘 다 결과가 다르다: (a) `apply_resolution` 전에 `dataclasses.replace(resolution, ask_payload={…, "context": {…ER context…, "resume": PendingResume.to_dict()}})` — `Resolution` 은 `@dataclass(frozen=True)`(`app/er/types.py` 193행)라 `replace` 가 가능하고 `ask_user` 의 검증(`questions.py` 208~210행 비밀 키·`AFFIRMATIVE_KEY` 검사)을 그대로 지난다; (b) `apply_resolution` 뒤에 `PendingQuestion.context` 행을 ORM 으로 직접 고친다 — 툴 밖 쓰기라 `S3.2` 16행 "모든 툴 호출은 agent_traces 에 기록" 과 `ask_user` 검증을 우회한다. 같은 구멍이 `new_person` 재개에도 있다: `create_person(display_name, aliases, relation_tag, hierarchy)` 는 `relation_tag`·`hierarchy` 가 필수(`persons.py` 405~430행, `RELATION_TAGS` 검사)인데 ER `context` 에 힌트가 없고, 01-plan 은 힌트가 추론되지 않았을 때의 기본값도 정하지 않았다. 조치: 01-plan U3/U4 에 (a) 를 명시(또는 사용자가 다른 길을 고르고), `PendingResume` 스키마(U1)에 `hints{relation_tag, hierarchy}` 와 미추론 시 기본값(또는 `new_person` 을 만들지 않고 응답에 알림)을 적고, 판정 표에 "`app/agent/` 가 `PendingQuestion` 을 직접 쓰지 않는다" 부정 grep 1행을 더한다.
- **H-3 결정 L(i) 가 기획서 3.1 원문과 어긋나는데 기록이 없다.** 위 2b L 행. 결정 자체는 원칙1·4·8 과 정합이고 P3-er 선례와 같아 **뒤집을 이유는 없다**. 문제는 기록 위치다 — `CLAUDE.md` "기획서가 바뀌면 `/devlog change`", 기획서 상단 안내문 "설계 확정은 resolution-plan 3장이 권위" 인데 어느 D 카드·S 카드·안내문도 "툴 선택은 코드가 한다" 를 담지 않으며, `S3.7` "툴 호출 정확도" 의 뜻(LLM 이 올바른 툴을 골랐는가 → 코드 매핑이라 곧 추출 정확도)이 바뀌는 것도 적혀 있지 않다. P10 이 이 지표를 잴 때 정의가 없으면 재현 불가(원칙8). 조치(사용자 결정): (1) D 카드 신설(예: `D14-tool-selection-by-code.md` — 결정·이유·"코드에서 지켜야 할 것: `app/agent/` 는 LLM 출력에서 툴 이름을 읽지 않는다"), 기획서 상단 안내문 한 줄, `S3.7` 툴 호출 정확도 정의 한 줄 — 또는 (2) CR-002 로 정식 처리. 01-plan 17행 "새 결정·새 명세를 만들지 않는다" 는 문장은 L 에 대해 사실이 아니므로 함께 고친다.

**권고(R) — 착수를 막지 않는다. 03-log·04-review 에서 확인.**

- R-1 판정 표 8행 curl: `-H "Content-Type: application/json"` 이 없으면 FastAPI 가 422 를 낸다. `AnswerIn.answer`(`app/api/schemas.py`) 필드명은 맞다. `X-Session-Id` 를 ②에 넣지 않아도 되는 이유(`build_ctx` 결정 12: 행의 `session_id` 권위)를 한 줄 적어 두면 04-review 가 다시 묻지 않는다.
- R-2 [권고] 소견 7건(`F-e93529`·`F-8e3e74`·`F-6ae8ad`·`F-d68447`·`F-fdb56f`·`F-7e6e84`·`F-0ffff5`)은 P4b 05-remediation 8행과 같은 성격(확장 패키지의 의도된 WARN)이고 01-plan 77행 U7 이 닫는 방식을 적었다. 05-remediation 의 각 소견 원인 분석 칸은 비어 있다 — U7 전에 P4b 형식(가설·확인 명령·확인 결과)으로 채워 두라. `app/er/judge.py`(F-e93529)는 "무수정 import" 이므로 registry 비고조차 바꾸지 않는다는 것을 04-review 가 확인한다.
- R-3 결정 G·H 는 "인식 LLM 실패" 만 예로 든다. 해석·기록 중 `SQLAlchemyError`(예: `IntegrityError`) 를 삼키고 200 으로 내리면 `get_session` 의 `commit()` 이 `PendingRollbackError` 로 실패해 500 + trace 소실이 된다. U5 03-log 에 "삼키는 예외 = `LoopError`·`JudgeUnavailable`·`ToolError` 계층, DB 예외는 그대로 올려 `main.py` 500" 처럼 범위를 적고 테스트 1건을 두라.
- R-4 D2 파급 "답 없이 새 발화가 오면 대기 질문 유지, 새 발화 우선" — 루프가 기존 `pending_questions` 를 만지지 않으면 자동으로 성립하지만 테스트가 없다. U5 에 "미답변 질문이 있는 세션에 `/chat` → 200, 기존 행 `answered_at` NULL 유지·status pending" 1건.
- R-5 backlog 줄 번호 드리프트: `DELETE /persons/{id}` 항목 삽입으로 P5 줄이 73행이 됐다. 01-plan 17·233행 "70행" 과 backlog 74행 "70행의 문장" 은 이제 틀린 번호다(문장 일치 검사는 텍스트 기준이라 기계 검증엔 영향 없음). 다음 문서 커밋에서 줄 번호 대신 "P5 절 첫 항목" 같은 표현으로 바꾸거나 번호를 고친다.
- R-6 `security.md` §5 "모든 조회는 `user_id` 조건" 은 `pending_questions`·`agent_traces` 에 `user_id` 가 없어 이 패키지 전부터 미충족(F-fbaaae). I(i) "명시만" 은 P5 범위로는 맞지만, 열린 보안 부채로 backlog 리스크 로그(97~104행)나 `DELETE /persons/{id}` 항목 옆에 "세션→사용자 귀속" 항목을 두어 잃어버리지 않게 하라.
- R-7 결정 K(i) `ask_user(kind="schedule")` 의 `options`(비어 있지 않은 문자열 목록, `questions.py` `_validate_options`)와 답을 `scheduled_at` 로 바꾸는 규칙이 없다. U4 03-log 에서 정한다(예: 후보 시각 2~3개 + "모르겠어요").
- R-8 `docs/wiki/fixes/FIX-002.md` 결과 절이 증거로 `evidence/20260923-1518-verify-plan-2.txt` 를 가리키나 실재 파일은 `evidence/20260923-1526-verify-plan-2.txt` 다(`ls` 확인). `verification.md` 15행 "존재하는 파일" 규약 위반 — 메인 세션이 FIX-002 경로를 고친다(이 패키지 계획과 무관).

05-remediation: `F-25b70f`(02-plan-verify 부재)는 이 문서로 해소 대상 — §1b 재실행으로 확인. H-1~H-3 은 verify-plan 출력이 아니라 verifier 판정이므로 findings.py 소견이 아니라 이 절이 기록이다.

### 5.4 결정 (1차)
1차 결과: 보류 — H-1(판정 표 7행 실행 불가), H-2(`context` 확장 경로·`new_person` 재개의 `relation_tag`/`hierarchy` 출처 미정), H-3(결정 L 의 기획서 3.1 이탈 미기록). 점검표 8행 중 7행 통과, 4행 보류. 사용자 확정 12건 중 카드·원칙과 충돌하는 것은 없고, L(i)는 기획서 원문과만 어긋난다(기록 문제). 세 보류는 모두 01-plan 문장 추가(+ D 카드 1장)로 닫히며 코드 결정을 뒤집지 않는다.
