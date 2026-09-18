# P3-llm-providers · 완료 검토 (04-review)

날짜: 2026-09-15 | 검토자: verifier (fable) — 구현자(backend-agent, sonnet)와 다른 모델·새 컨텍스트(L-002). 코드·01-plan·02-plan-verify·03-log·D 카드·registry·backlog·CURRENT·README·HANDOFF·journal 은 고치지 않았다. 이 문서·`05-remediation.md`(신규 소견 3건 원인 분석, registry 소견 9건 해소 칸)·`evidence/20260915-1514~1521-review-*` 만 썼다. `.env` 미열람, 네트워크 호출 0, 더미 키 값은 `"x"` 만, 환경변수 전체 출력 없음(`unset` 서브셸).

검토 대상: HEAD `10a66c3`(dev, U4). 착수 `025a7c4`(U1 직전) · U1 `c01381d` · U2 `cf01e9f` · U3 `7b94a69` · U4 `10a66c3` · 계획 초안 `701fb8d`. 01-plan(U4 만 `[x]`, U1~U3 은 `[ ]` — §6), 02-plan-verify(통과, 권고 R-1~R-9, 승인 2026-09-14), 03-log 5 항목(U4 항목 해시 `pending`), 05-remediation 소견 13(해소 3·열림 10 → 이 검토에서 registry 9건 해소, 신규 3건), evidence U1 11+1·U2 16·U3 9·U4 8 + 이 검토 10. 코드: `app/er/judge.py`·`app/settings.py`·`evaluation/resolvers/llm_single.py`·`scripts/er_smoke.py`·`scripts/baseline_smoke.py`·`tests/test_er_judge.py`·`tests/test_baseline_llm_single.py`·`tests/test_er_smoke.py`·`requirements.txt`. 구현자의 "backend-agent 판단" 8건은 근거가 아니라 확인 대상으로 읽었다(§6).

## 1. 기계 검증 출력 (그대로 붙인다)

### 1a. 초안 실행 (검토자 줄만 있는 04-review 골격으로, 본문 작성 전)
명령: `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P3-llm-providers | tee docs/wiki/packages/P3-llm-providers/evidence/20260915-1514-review-verify-impl-draft.txt`
```
== verify-impl P3-llm-providers  (20260915-1514) ==
........................................................................ [ 94%]
......................................................                   [100%]
918 passed in 37.00s
PASS  pytest 통과 → evidence/20260915-1514-pytest.txt
PASS  compileall 통과 → evidence/20260915-1514-lint.txt
PASS  태그 P3-llm-providers 커밋 6 건 → evidence/20260915-1514-commits.txt
PASS  커밋에 태그 존재: D11
PASS  커밋에 태그 존재: D3
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: R4
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.7
PASS  검토자 = verifier (L-002)
FAIL  04-review 수용 기준 표에 행이 없다
FAIL  registry.md 에 P3-llm-providers 의 산출물이 등록되지 않았다 (중복·누락 방지용)
WARN  미완료 작업 단위 3 개
== 결과: FAIL=2 WARN=1 → evidence/20260915-1514-summary.txt ==
```
- `findings.py … --source verify-impl` → 신규 소견 3: **F-445cda [필수]**(04-review 표 없음 — 초안 시점 정상, 1b 로 닫는다), **F-4ef1a3 [필수]**(registry 에 패키지 열 `P3-llm-providers` 행 없음 — §5·§6, 원인 분석만 채움), **F-2f0840 [권고]**(01-plan U1~U3 `[ ]` — §6). 05-remediation 참조.
- pytest **918 passed, skip 0**: `POSTGRES_PORT=5433` 을 호출 환경에 두면 `verify-impl.sh` 가 그대로 상속해 `dbtest` 가 skip 되지 않았다(P3-baselines 04-review [권고] 8 의 하네스 한계는 환경변수 export 로 우회됨 — 스크립트 수정 없음). U4 의 `evidence/20260915-1500-u4-pytest-all.txt`(918 passed) 와 같은 수치.
- `evidence/20260915-1514-commits.txt` 6건 = `701fb8d`·`025a7c4`·`c01381d`·`cf01e9f`·`7b94a69`·`10a66c3`(`gitlog.sh P3-llm-providers` 와 동일). 03-log Refs 태그(D11·D3·D4·R4·S3.2·S3.3·S3.7)는 모두 커밋 메시지에 있다. D11 은 U1~U4 커밋 4건 전부에 있다(R-9(a)).

### 1b. 최종 실행 (04-review 본문 작성 후)
(아래 §8 에 붙인다)

## 2. 수용 기준 대조
증거 열은 `evidence/` 파일, 커밋 해시(7자 이상), 존재하는 파일 경로 중 하나여야 한다(`verify-impl.sh` 가 실재를 검사한다). 문장만 있는 증거는 FAIL.

수용 기준 문장의 동일성: `docs/backlog.md` 51행과 `01-plan.md` 55행이 글자 그대로 같다(02-plan-verify 점검표 6행 `SAME`, verifier 재확인 2026-09-15). 문장: "`LLM_PROVIDER` ∈ {anthropic, openai, gemini} 각각으로 `judge_from_env()`·`caller_from_env()` 가 해당 공급자의 판정기를 만들고, 비활성·미지 공급자는 `InvalidValue` 로 거부하며, 신규 테스트는 네트워크 0(스텁)이고 기존 pytest 전건이 통과한다".

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| `LLM_PROVIDER` ∈ {anthropic, openai, gemini} 각각으로 `judge_from_env()`·`caller_from_env()` 가 해당 공급자의 판정기를 만들고, 비활성·미지 공급자는 `InvalidValue` 로 거부하며, 신규 테스트는 네트워크 0(스텁)이고 기존 pytest 전건이 통과한다 — 전체 | evidence/20260915-1514-review-verify-impl-draft.txt, evidence/20260915-1517-review-pytest-nokey.txt, evidence/20260915-1516-review-negative-python.txt, c01381d, cf01e9f, 7b94a69, 10a66c3 | 통과 |
| 항목 1a `anthropic` → `judge_from_env()` 가 `ClaudeJudge` | evidence/20260915-1500-u4-providers-3-and-switch-reject.txt (`anthropic -> ClaudeJudge`), evidence/20260915-1517-review-pytest-nokey.txt (`-k` 64 passed 안에 `test_judge_from_env_builds_each_active_provider[anthropic]`), tests/test_er_judge.py (873~888행 parametrize·isinstance 단언) | 통과 |
| 항목 1b `openai` → `judge_from_env()` 가 `OpenAIJudge`(기본값도 openai, D11 결정 2) | evidence/20260915-1500-u4-providers-3-and-switch-reject.txt (`openai -> OpenAIJudge`), evidence/20260915-1516-review-negative-python.txt (`def3 select_provider({}) = 'openai'`), tests/test_er_judge.py (810~815행 `test_judge_from_env_defaults_to_openai`), app/settings.py (94행 `LLM_PROVIDER = "openai"`) | 통과 |
| 항목 1c `gemini` → `judge_from_env()` 가 `GeminiJudge`(더미 키·`GEMINI_MODEL` 설정, 네트워크 0) | evidence/20260915-1500-u4-providers-3-and-switch-reject.txt (`gemini -> GeminiJudge`), evidence/20260915-1516-review-negative-python.txt (`b' 정규화 양성 → GeminiJudge`), tests/test_er_judge.py (826~835행), app/er/judge.py (734~738행 `JUDGES`) | 통과 |
| 항목 2a `anthropic` → `caller_from_env()` 가 `ClaudeSingleCaller` | evidence/20260915-1517-review-pytest-nokey.txt (173 passed 안에 `test_caller_from_env_selects_provider`), tests/test_baseline_llm_single.py (377~381행), evidence/20260915-1200-u3-callers-keys.txt | 통과 |
| 항목 2b `openai` → `caller_from_env()` 가 `OpenAISingleCaller` | evidence/20260915-1517-review-pytest-nokey.txt, tests/test_baseline_llm_single.py (380~381행), evidence/20260915-1200-u3-callers-keys.txt | 통과 |
| 항목 2c `gemini` → `caller_from_env()` 가 `GeminiSingleCaller` | evidence/20260915-1517-review-pytest-nokey.txt (`test_caller_from_env_selects_gemini_provider`), tests/test_baseline_llm_single.py (393~398행), evaluation/resolvers/llm_single.py (619~621행 `CALLERS` 는 `JUDGES` 키 순회·645행 `select_provider(env)`) | 통과 |
| 항목 3 비활성 공급자 `InvalidValue`(팩토리 호출 시점, 메시지에 활성 목록, 키 값 없음) — 두 진입점 모두 | evidence/20260915-1516-review-negative-python.txt (a1·a2·a3 — `active: ['openai']`, `API_KEY` 문자열 없음), evidence/20260915-1500-u4-providers-3-and-switch-reject.txt, tests/test_er_judge.py (891~898행), tests/test_baseline_llm_single.py (410~417행), app/er/judge.py (814~819행) | 통과 |
| 항목 4 미지 공급자 `InvalidValue`(메시지에 표 키 목록) — `fake`·`FAKE `·`llama`·`''`, 활성 목록 안 오타도 거부 | evidence/20260915-1516-review-negative-python.txt (b 6건), evidence/20260914-1620-u1-invalidvalue-messages.txt, tests/test_er_judge.py (849~853·901~908·940~944행), tests/test_baseline_llm_single.py (384~390행), app/er/judge.py (770~775·808~812행) | 통과 |
| 항목 5 신규 테스트는 네트워크 0(스텁) — 키 이름 6개 `unset` 서브셸에서 세 테스트 파일 173 passed, skip 0 | evidence/20260915-1517-review-pytest-nokey.txt, tests/test_er_judge.py (163~190행 `StubGeminiClient`), tests/test_baseline_llm_single.py (185~215행 스텁), evidence/20260915-1516-review-negative-python.txt (스텁으로 43/43 재현) | 통과 |
| 항목 6 기존 pytest 전건 통과 — 918 passed / 0 failed / 0 skipped(859 + 신규 59), P3-er 회귀 + parity 137 passed, tools_check 7/7 | evidence/20260915-1514-pytest.txt, evidence/20260915-1500-u4-pytest-all.txt, evidence/20260915-1517-review-pytest-nokey.txt, evidence/20260915-1500-u4-tools-check.txt | 통과 (기존 테스트 "무수정"의 예외는 §3(h) — R-1 4건 + F-7afd7f 2건뿐) |

## 2b. 판정 방법 표(01-plan 65~78행) 12행 대조 — verify-impl 의 증거 열 검사 대상은 위 §2 뿐이다

| 01-plan 행 | 기대 출력(계획 문언) | 실측 evidence | 판정 |
|---|---|---|---|
| 67 세 공급자 생성 | `-k provider` 세 이름 parametrize 통과, skip 0 | `20260914-1735-u2-pytest-k-provider.txt` 15 passed; verifier `20260915-1517-review-pytest-nokey.txt` `-k` 64 passed skip 0 | 일치 |
| 68 등록표 키 | `['anthropic', 'gemini', 'openai']`(`fake` 없음) | `20260914-1620-u1-judges-keys.txt`·`20260914-1720-u2-judges-keys.txt`; verifier 부정 c1·c2·c4 | 일치 |
| 69 활성 스위치 거부 | `InvalidValue` + 활성 목록 | R-3 대로 **같은 `env`** 에서 읽어야 성립 — verifier a1(env 주입)·a2(`os.environ`) 둘 다 `active: ['openai']` | 일치(R-3 반영) |
| 70 미지 이름 거부 | `InvalidValue` + 표 키 목록 | `20260914-1620-u1-invalidvalue-messages.txt`; verifier b(llama) | 일치 |
| 71 두 진입점이 같은 표 | `True` | `20260915-1200-u3-callers-keys.txt` `True`; verifier c3·c5(헬퍼 동일 객체 `is`) | 일치 |
| 72 SDK·키 없이 import | `ok` | `20260914-1620-u1-import-both-modules.txt`·`20260914-1720-u2-import-module.txt`; verifier `20260915-1517-review-negative-bash.txt` (p) `ok`(키 4개 unset); `tests/test_er_judge.py:655` `sys.modules["google"]=None` 재로드 단언 | 일치 |
| 73 P3-er 회귀 | 기존 54 + 신규, 실패 0 | `20260915-1500-u4-pytest-er-regression.txt` 91 passed; verifier 회귀+parity 137 passed | 일치 |
| 74 parity 무변경 | 46 passed, skip 0 | `20260915-1500-u4-pytest-parity.txt` 46 passed; `git log 025a7c4..HEAD -- tests/test_baseline_parity.py` 0건(무수정) | 일치 |
| 75 전체 | 859 + 신규, 실패 0·skip 0 | 918 passed(U1 873 → U2 896 → U3 917 → U4 918, evidence 4개) | 일치 |
| 76 `app/` 수정 범위 | 정확히 2줄 | `20260915-1500-u4-app-diff.txt`; verifier (g) `app/er/judge.py`·`app/settings.py` | 일치 |
| 77 툴 시그니처 무변경 | `7/7 ok` | `20260915-1500-u4-tools-check.txt`; verifier 재실행 `7/7 ok` | 일치 |
| 78 실 Gemini 1회(사용자 실행) | 키 없으면 종료 코드 2 | `20260915-1500-u4-smoke-gemini-exit2.txt` rc=2(키 이름만); `tests/test_er_smoke.py:109` 같은 조건. **실 키 실행은 미수행**(사용자 몫) | rc=2 일치 / 실호출 미검증(§6·§7) |

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)

verifier 가 직접 실행. 파이썬 케이스는 저장소 밖 scratchpad `review_negative.py`(원문은 evidence 파일 끝에 첨부, `PYTHONPATH=.`), 스텁은 `tests/test_er_judge.py` 163~190행과 같은 형태로 재작성, 네트워크 0, 더미 키 값 `"x"` 만, 키 이름 6개 `unset` 서브셸. 출력: `evidence/20260915-1516-review-negative-python.txt` — **43 케이스 전부 기대와 일치(`MISMATCH=0`, rc=0)**. bash 케이스: `evidence/20260915-1517-review-negative-bash.txt`.

| 케이스 | 명령 | 증거 |
|--------|------|------|
| (a) `LLM_PROVIDERS_ENABLED=openai` + `LLM_PROVIDER=gemini` → `InvalidValue`, 메시지에 활성 목록 `['openai']`, `API_KEY`·모델명 문자열 없음 — a1 `env` 주입 / a2 `os.environ`(env 생략) / a3 `caller_from_env` 도 같은 메시지 | `PYTHONPATH=. python <scratchpad>/review_negative.py` | evidence/20260915-1516-review-negative-python.txt a1~a3 |
| (b) `LLM_PROVIDER` = `fake` · `FAKE ` · ` Fake` · `llama` · `''` → 전부 `InvalidValue` + 표 키 목록 `['anthropic', 'gemini', 'openai']`; 활성 목록 안 오타 `anthropic,llama` → `InvalidValue`(`['llama']` 지목); ` GEMINI ` 는 정규화되어 표에는 있으나 비활성이면 거부; 대조군 ` Gemini ` + ` GEMINI ,openai` → `GeminiJudge` | 같음 | 같은 파일 b 7건 + b' |
| (c) `FakeJudge ∉ JUDGES.values()`, `'fake' ∉ JUDGES`, `JUDGES.values() == {ClaudeJudge, OpenAIJudge, GeminiJudge}`, `CALLERS.keys() == JUDGES.keys()`, `llm_single._to_gemini_schema is judge._to_gemini_schema`·`select_provider` 동일 객체 | 같음 | c1~c5 |
| (d) `LLM_PROVIDER=gemini` + `GEMINI_API_KEY=x` + `GEMINI_MODEL` 미설정 → `InvalidValue`(`GEMINI_MODEL` 지목, 키 문자열 없음) — `judge_from_env`·`caller_from_env` 둘 다; `GEMINI_MODEL=''` 도 미설정 취급 | 같음 | d1~d3 |
| (e) `GeminiJudge` 오류 매핑(스텁 큐): timeout×2 → `timeout` 호출 2 / connection×2 → `connection` 호출 2 / **429 뒤 성공 큐** → `rate_limit` 호출 1(재시도 없음) / **500 뒤 성공 큐** → `api_error` 호출 1 / 400·503 → `api_error` 호출 1 / timeout 뒤 429 → `rate_limit` 호출 2(재시도 뒤 429 는 즉시) / text 없음·비JSON → `schema` / 후보 밖 id → `out_of_range_id` / `s_llm=1.5` → `schema` / timeout 1회 뒤 성공 → 호출 2·`provider="gemini"`·`model=model_version`·tokens (7,3); 관측 어휘 6종 ⊆ 계약 어휘. `GeminiSingleCaller` 도 timeout×2·429·500 같은 값 | 같음 | e 15건 + `e 관측된 오류 어휘 ⊆ 6종` |
| (f) `grep -rn "evaluation" app/ --include=*.py` 0건(rc=1); `grep -rln "google" app/ --include=*.py` = `app/er/judge.py` 뿐(judge.py 밖 0건) | bash | evidence/20260915-1517-review-negative-bash.txt (f) |
| (g) `git diff --name-only 025a7c4..HEAD -- app/` = `app/er/judge.py`·`app/settings.py` 정확히 2줄; `-- scripts/ tests/ requirements.txt evaluation/` = 7 파일(`llm_single.py`·`requirements.txt`·`baseline_smoke.py`·`er_smoke.py`·세 테스트 파일) — 03-log 선언 목록(U1: judge/settings/.env.example/test_er_judge/test_er_smoke/er_smoke/baseline_smoke · U2: judge/requirements/test_er_judge · U3: llm_single/test_baseline_llm_single · U4: README/user-setup 01·03·08/D11/registry/er_smoke/baseline_smoke/test_er_smoke)과 **전부 일치, 계획 밖 파일 0**(R-7 로 `scripts/`·`test_er_smoke.py` 가 선언됨). 전체 변경 파일 21개 중 나머지는 위키 문서(HANDOFF·journal·01/03/05·D11·registry)·`.env.example`·README·user-setup 3개 | bash | 같은 파일 (g) |
| (h) `git diff 025a7c4..HEAD --stat -- tests/` = 3 파일(+788/−16), 다른 테스트 파일 변경 0; 삭제·개명된 `def test_`/parametrize = **R-1 (a)(b)(c)(d) 네 개뿐**(`…defaults_to_anthropic`·`…gemini_is_reserved_not_implemented`·parametrize `["gemini","llama"]`+`…rejects_unimplemented_provider`·`…missing_anthropic_key_returns_2`); `test_er_smoke.py` 주석 제외 코드 변경 = R-1(d) 3줄 + F-7afd7f `setenv` 2줄 + 신규 gemini rc=2 테스트 9줄. F-7afd7f 해결 단계 2 의 `grep -c "OPENAI_API_KEY"` 는 7(코드 4 + 주석 2 + 문맥 1) — 코드 줄 4 는 기대와 일치 | bash | 같은 파일 (h) |
| (i) 공유 자산 무변경: `git diff 025a7c4..HEAD -- app/er/judge.py` 에 `JUDGEMENT_SCHEMA`·`build_prompt`·`validate_judgement`·`call_with_error_mapping`·`ClaudeJudge`·`OpenAIJudge`·`FakeJudge` 정의 줄 변경 0; 삭제된 31줄 전부 = 옛 docstring·`_KNOWN_PROVIDERS`·`if provider ==` 사다리·gemini 예약 `InvalidValue`; `confidence.py`·`embedding.py`·`rules.py`·`resolve.py` 무변경 | bash | 같은 파일 (i) |
| (j) `app/settings.py` diff = `LLM_PROVIDER "anthropic"→"openai"` + `LLM_PROVIDERS_ENABLED_DEFAULT` 신설 + 주석뿐 | bash | 같은 파일 (j) |
| (k) D4·`docs/proposal.md`·`reports/`·`app/embedding.py` 무변경(R-9(c)(d)) | bash | 같은 파일 (k) |
| (l) 오류 어휘: `judge.py`+`llm_single.py` 의 `JudgeUnavailable("…")` 리터럴 = 6종뿐(api_error 4·connection 2·out_of_range_id 1·rate_limit 2·schema 22·timeout 2); `safety\|blocked` 0건(D11 (d)) | bash | 같은 파일 (l) |
| (m) 등록표 단일성(R-5): `^JUDGES` 1 · `_KNOWN_PROVIDERS` 0 · `llm_single.py` 의 `InvalidValue(` 는 527행(`GeminiSingleCaller.__post_init__`, `GEMINI_MODEL` 미설정) 1곳뿐 · 변환기·매핑기·`select_provider`·`enabled_providers` 재정의 0 | bash | 같은 파일 (m) |
| (n) `HttpOptions.timeout` 단위 실측 = "milliseconds"(`Optional[int]`) → `int(self.timeout * 1000)`(`judge.py:673`·`llm_single.py:540`) 이 맞다(20초 → 20000) | bash | 같은 파일 (n) |
| (o) `pip show google-genai` Version 2.23.0 == `requirements.txt:18` 핀 | bash | 같은 파일 (o) |
| (p) 키 4개 unset 서브셸에서 `import app.er.judge, evaluation.resolvers.llm_single` → `ok` | bash | 같은 파일 (p) |
| (q) R-3 단일 출처: `os.environ` `LLM_PROVIDERS_ENABLED=gemini` 인데 `env` 주입 `anthropic` → `openai` 거부(`os.environ` 누설 없음) | python | negative-python r3 |
| (r) 기본값: `enabled_providers({})`·`('   ')` = 전체 3 / `select_provider({})` = `openai` | python | def1~def3 |
| (s) 스키마: `_to_gemini_schema` 뒤 `JUDGEMENT_SCHEMA` 불변(deepcopy 비교); 변환 결과 `matched_person_id` `{INTEGER, nullable}`·`s_llm` `NUMBER 0~1`·`required` 3; 요청 config `temperature=0`·`application/json`·`response_schema` 있음·`model` 전달; 요청 본문에 `GEMINI_API_KEY`·`LLM_PROVIDER` 문자열 없음 | python | s1~s4 |
| (t) **SDK 오프라인 수용(U2 판단 (2) 검증)**: 변환 dict 를 `types.Schema.model_validate` 가 받고(`nullable=True`·`additional_properties=False`·`extra=None`), `_transformers.t_schema` 가 `Schema` 로 만들며(`property_ordering` 자동 부여), `_GenerateContentConfig_to_mldev` 가 요청 config 를 만든다 — `RESOLUTION_SCHEMA`(enum·array items 포함)도 같은 결과. `GEMINI_API_KEY=x` 로 `genai.Client()` 생성만(네트워크 0) | `PYTHONPATH=. python - <<EOF …` | evidence/20260915-1520-review-sdk-offline.txt |
| (u) `GenerateContentResponse.text`/`_get_text` 소스: `raise` 문 0, 후보·parts 없으면 `return None` → `GeminiJudge`/`GeminiSingleCaller` 의 `if not text: raise JudgeUnavailable("schema")` 경로가 실제 SDK 동작과 맞다(안전 필터·빈 본문이 어휘 밖 예외로 새지 않는다) | python | evidence/20260915-1521-review-sdk-get-text.txt |
| (v) registry R-8 닫는 명령(§5) | bash | evidence/20260915-1517-review-registry-r8.txt |

테스트가 실제로 실패 조건을 검사하는지(항상 통과하는 테스트가 아닌지): `tests/test_er_judge.py` 837~846·849~853·891~898·901~908·911~920·940~944행 `pytest.raises(InvalidValue)` + 메시지 문자열 단언, 564~610행 `assert len(client.calls) == 1|2`(재시도 횟수를 숫자로 고정 — 루프가 3회로 늘거나 429 를 재시도하면 깨진다), 655~686행 `sys.modules["google"] = None` 뒤 reload(모듈 상단 import 가 생기면 즉시 깨진다), 693~698행 deepcopy 비교; `tests/test_baseline_llm_single.py` 384~417행 `pytest.raises`, 421~442행 `set(CALLERS)==set(JUDGES)`·`is` 동일성, 1049~1103행 호출 횟수 단언, 1105~1114행 실패 → `identity`·`person_id None`·`score 0.0`(merge 아님, 원칙1). verifier 의 43 케이스가 같은 조건을 독립 코드로 재현해 같은 값이 나왔다.

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
- 없음. INDEX 69행 "닫는 R" 열은 `—`("R4 는 P4 가 닫는다 — 이 패키지는 공급자를 늘릴 뿐 실호출 미검증 꼬리표를 풀지 않는다"), `grep -n "P3-llm-providers" docs/wiki/review-index.md` → 0건(rc=1). R4 의 꼬리표는 오히려 공급자 수만큼 늘었다(§6 R-9(b)).

## 5. registry.md 에 올린 산출물
- **R-8 닫는 명령(verifier 재실행, `evidence/20260915-1517-review-registry-r8.txt`)**: `for f in app/er/judge.py app/settings.py evaluation/resolvers/llm_single.py tests/test_er_judge.py tests/test_baseline_llm_single.py README.md; do grep -c "| $f |" …; done` → **전부 `1`**; `grep -c "requirements.txt"` = `1`; `grep -c "환경변수 이름 목록"` = `1`; `grep -c "^LLM_PROVIDERS_ENABLED=$" .env.example` = `1`(값 비움). 새 행(패키지 열 `| P3-llm-providers |`) = **0**(R-8 기대값). 각 행 비고의 `P3-llm-providers U<n>(<해시>)` 문구: judge.py `U1(c01381d)`+`U2(cf01e9f)`(GeminiJudge·`_to_gemini_schema`) · settings.py `U1(c01381d)` · llm_single.py `U3(7b94a69)` · test_er_judge.py `U1·U2`(73건 수집/`def test_` 68 — verifier 실측 `grep -c "^def test_"` = 68 일치) · test_baseline_llm_single.py `U3`(90건/69 — 실측 69 일치) · README.md `U4(pending)` · test_er_smoke.py `U4(pending)`(현재 10건 — 실측 `def test_` 10 일치) · requirements `U2(cf01e9f)`+`google-genai==2.23.0`(pip show 일치) · .env.example `U1(c01381d)`. U4 의 `evidence/20260915-1500-u4-registry-r8.txt` 와 같은 값.
- → 05-remediation 의 registry 소견 9건(F-e93529·F-fdb56f·F-07a652·F-2c37bd·F-6ff7bc·F-c6bd9b·F-cfdfa4·F-0ffff5·F-22010b)을 **해소**로 닫았다(각 블록 해결 단계 상태 완료·재검증 칸에 위 evidence).
- **잔여 1**: README 33행·test_er_smoke.py 94행 비고의 `U4(pending)` 은 U4 커밋 `10a66c3` 으로 채워야 한다(닫는 docs 커밋 몫, [권고] — §6 3).
- **`verify-impl.sh` 6번 항목과 R-8 의 충돌(F-4ef1a3 [필수])**: 스크립트 94행 `grep -Fq "| P3-llm-providers |"` 는 **패키지 열**이 이 id 인 행을 요구하는데, R-8 은 "기존 행 비고만, 새 행 0" 을 고정했고 구현이 그대로 따랐다. 이 패키지가 실제로 **새로 만든 파일**은 `docs/wiki/decisions/D11-llm-provider-registry.md`(025a7c4, 메인 세션) 하나뿐이고 registry 에는 아직 없다(`grep "decisions/" registry.md` 0건 — 결정 카드 행 선례도 없다). 해소 후보는 §6 1 에 적었다. verifier 는 registry 를 고치지 않는다.

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견

### [필수]
1. **F-4ef1a3 — registry 에 패키지 열 `P3-llm-providers` 행 없음(`verify-impl.sh` 6번 FAIL)**. 코드 결함이 아니라 R-8("새 행 0")과 스크립트 6번("패키지 행 필수")의 충돌이다. 해소 후보(사용자·메인 세션 결정, verifier 는 고르지 않는다): (i) 이 패키지가 실제로 만든 새 파일 `docs/wiki/decisions/D11-llm-provider-registry.md` 를 `| 문서 | 결정 카드 D11 … | docs/wiki/decisions/D11-llm-provider-registry.md | P3-llm-providers | 025a7c4 | … |` 로 **1행 추가**(R-8 의 "새 행은 새 파일에만" 원칙과 충돌하지 않는다 — R-8 이 D11 을 새 파일로 세지 않은 것은 verifier 의 누락), 닫는 docs 커밋에서 `verify-impl.sh` 재실행으로 닫는다; (ii) 스크립트 6번을 "패키지 열 또는 비고에 `<id>` 가 있으면 PASS" 로 완화(하네스 변경 = L-nnn 교훈 + 사용자 결정, 이 패키지 조치 아님). 어느 쪽이든 1b 최종 실행에서 FAIL=1 이 남아 있는 한 결과는 `완료` 가 아니다.

### [권고] (패키지 닫기 전제 아님 — 닫는 docs 커밋 또는 P4 계획에서 처리)
2. **F-2f0840 — 01-plan 48~50행 U1~U3 이 `[ ]`** 인데 03-log·커밋(c01381d·cf01e9f·7b94a69)·evidence 는 완료다. U4 만 `[x]`. 닫는 docs 커밋에서 세 줄을 `[x]` 로(하네스 절차 — `verify-impl.sh` 7번 WARN).
3. **`pending` 해시 3곳** — 03-log U4 항목 머리 줄 `· pending` → `10a66c3`; registry 33행(README)·94행(test_er_smoke.py) 비고 `U4(pending)` → `U4(10a66c3)`(P3-baselines 04-review [권고] 5 와 같은 처리).
4. **R-9(b)·01-plan 126행 문장 그대로**: **실호출로 검증된 공급자 0/3(F-87c597 열림, R4 꼬리표는 P4 가 닫는다)**. 자동 테스트는 전부 스텁이고 Gemini 의 실제 응답 모양·`additionalProperties`/`nullable` 의 실 API 수용 여부는 사용자 스모크(`docs/user-setup/03`·`08` 의 `--provider gemini` 줄)에서 처음 확인된다. 오프라인으로 확인한 범위는 §3(t)(u) 까지다(SDK 요청 변환기까지 통과, 서버 응답은 미검증). 실 API 가 스키마를 거부하면 `ClientError(400)` → `api_error` 로 강등되므로(§3(e)) 크래시가 아니라 `llm_failed`/`identity` 로 드러난다.
5. **H-1(사용자 결정, 판정하지 않음) — `docs/proposal.md` 상단 안내문 갱신 여부**(R-9(c), D11 파급 "04-review 에서 판단"). 기획서 전제는 "제품은 Claude API" 인데 운영 기본값이 `LLM_PROVIDER=openai`(D11 결정 2)로 바뀌었다. 이 패키지는 `docs/proposal.md` 를 손대지 않았다(§3(k)). 선택지: (a) 상단 안내문에 한 줄("LLM 공급자는 등록표로 교체 가능, 운영 기본은 OpenAI — D11", `/devlog change` 없이 안내문만) / (b) `/devlog change` CR 로 정식 처리 / (c) 기획서는 그대로 두고 D11 만 단일 출처. verifier 의견: D11 이 "운영 기본값의 변경이지 D3·프롬프트·스키마 변경이 아니다" 라고 이미 못박았으므로 (a) 또는 (c) 로 충분해 보이나, "확정 사항" 해당 여부는 사용자 몫.
6. **R-9(d) 확인** — D4 카드 무수정(`git diff --name-only 025a7c4..HEAD -- docs/wiki/decisions/D04*` 0줄, §3(k)). D4 파급의 "`ANTHROPIC_API_KEY`(LLM)" 문구는 D11 이 LLM 몫을 대체한다는 메인 세션 메모 그대로.
7. **관찰(조치 불필요)** — `select_provider` 거부 메시지가 `LLM_PROVIDER` 원값을 `repr` 로 되돌려준다(`'FAKE '`). 키 변수가 아니므로 security §1 위반은 아니나, 값을 잘못 넣은 사람이 키를 이 변수에 넣는 실수까지 막지는 않는다. 기존 두 공급자의 옛 메시지도 같은 형식이었다(삭제 줄 §3(i)).
8. **하네스** — (a) `verify-impl.sh` 6번은 "기존 파일만 확장한 패키지" 를 표현할 수 없다(위 1 (ii), L-nnn 후보). (b) `POSTGRES_PORT` 는 호출 환경에 export 하면 스크립트가 상속한다(이번 918 passed skip 0) — P3-baselines [권고] 8 의 스크립트 수정은 필수가 아니며, 04-review 명령 줄에 포트를 적는 관행으로 충분하다.

### 02-plan-verify §3 권고 R-1~R-9 반영 판정
| # | 판정 | 근거(파일·행·evidence) |
|---|---|---|
| R-1 바뀌는 기존 테스트 4건 고정 | 반영(+F-7afd7f 2건, 해소됨) | §3(h): 삭제·개명 def = 네 개뿐; `test_er_smoke.py` setenv 2줄은 F-7afd7f 로 기록·해소(원인 동일 — 결정 2). parity·pipeline 무수정 |
| R-2 더미 키로 생성 성공, 네트워크는 `judge()` 시점 | 반영 | `20260914-1700-u2-client-no-key.txt`(키 없음 → `ValueError`, 키 값 없음); `tests/test_er_judge.py:826~835,873~888` `_FAKE_KEY_MARKER`; verifier §3(t) `GEMINI_API_KEY=x` 로 `Client()` 생성만 |
| R-3 스위치·공급자 같은 `env` | 반영 | `judge.py:760~761,802~803,814`; `tests/test_er_judge.py:911~920`; verifier (q) |
| R-4 파싱 규칙(strip·lower·빈 항목·미설정=전체·오타 거부) | 반영 | `judge.py:763~777`; `tests/test_er_judge.py:923~944`; `app/settings.py:101` 단일 출처(`judge.py` 에 목록 리터럴 없음 — `grep LLM_PROVIDERS_ENABLED judge.py` 는 docstring·`env.get`·메시지뿐); verifier b·def1·def2 |
| R-5 등록표 단일성 판정 명령 | 반영 | §3(m): `^JUDGES` 1·`_KNOWN_PROVIDERS` 0·`llm_single` 거부 0·`CALLERS` 는 `JUDGES` 키 순회(619~621행)·`set(CALLERS)==set(JUDGES)` 테스트 421행 |
| R-6 실측 3건 + 변환기 단일 + 재시도 실측 | 반영 | `20260914-1700-u2-pip-show/errors-classes/schema-fields/httpoptions-fields/retry-and-error-mapping-detail.txt`; `_to_gemini_schema` 는 `judge.py` 한 곳(§3(m) 재정의 0); `tests/test_er_judge.py:693~728`; verifier §3(s)(t) |
| R-7 `scripts/`·`test_er_smoke.py` 산출물 선언 | 반영 | 03-log U1(docstring)·U4(`_REQUIRED_KEY_BY_PROVIDER["gemini"]`·help·테스트 1건) 선언; §3(g) 대조 일치; `scripts/er_smoke.py:42~45,87`·`baseline_smoke.py:49~52,96` |
| R-8 registry 기존 행 비고만 | 반영 | §5, `20260915-1517-review-registry-r8.txt`. 부작용: `verify-impl.sh` 6번 FAIL(F-4ef1a3) |
| R-9 (a) Refs·커밋 D11 (b) 0/3 문장 (c) proposal 미수정 (d) D4 미수정 (e) user-setup 01 7·9행 반전 | (a)(c)(d)(e) 반영, (b) §6 4 에 기재 | (a) §1a 커밋 4건 D11; (c)(d) §3(k); (e) `docs/user-setup/01-env-keys.md:7,9,12,13`(OpenAI 기본·Anthropic 선택·Gemini 사용 가능·`LLM_PROVIDERS_ENABLED` 행) |

### 03-log "backend-agent 판단" 8건 판정 (U2 2·U3 3·U4 3)
| 항목 | 판정 | 근거 |
|---|---|---|
| U2 (1) `HttpOptions.retry_options` 미채택 → 수동 1회 루프(timeout·connection 한정) | **채택** | `20260914-1700-u2-retry-and-error-mapping-detail.txt`: `retry_args(None)` = `stop_after_attempt(1)`(SDK 기본 재시도 없음), `http_status_codes=()` 는 falsy 라 기본 목록(408·429·5xx)으로 되돌아가 "timeout·connection 에만" 을 표현 못 함 → 01-plan 96행 "동등한 설정이 없으면" 조건 충족. `judge.py:607~623` 루프 `for attempt in (1, 2)`; verifier §3(e) 15건(429 뒤 성공 큐에서도 호출 1 = SDK 도 헬퍼도 429 를 재시도하지 않음, timeout 뒤 429 = 호출 2) |
| U2 (2) `response_schema` 에 변환 dict 그대로 전달(`types.Schema` 명시 구성 없음) | **채택(오프라인 한도)** | §3(t) `evidence/20260915-1520-review-sdk-offline.txt`: `Schema.model_validate` ok·`t_schema` → `Schema`·mldev config 변환 ok, `RESOLUTION_SCHEMA` 도 동일. 스텁 테스트(`config.response_schema == _to_gemini_schema(...)`)만으로는 SDK 수용을 증명하지 못하므로 verifier 가 보강했다. 실 API 수용은 미검증(§6 4) |
| U3 (1) `CALLERS = {name: _CALLER_FACTORY_BY_NAME[name] for name in JUDGES}` | **채택** | `llm_single.py:613~621`; `JUDGES` 에 팩토리 없는 이름이 생기면 import 시 `KeyError`(조용한 누락 없음); 테스트 421행 + verifier c3. 팩토리 표에 세 이름 리터럴이 한 번 더 있으나 키 집합의 단일 출처는 `JUDGES` 이고 불일치는 즉시 드러난다(R-5 의 의도 충족) |
| U3 (2) `GeminiSingleCaller` 에 `max_retries` 없음, 래퍼가 버림 | **채택 + P4 인계** | `llm_single.py:599~605` `del max_retries`; `GeminiJudge` 와 동일 규약(`judge.py:652~654`); 재시도는 헬퍼 안 1회. 결과적으로 Gemini 는 429/5xx 무재시도·Claude/OpenAI 는 SDK `max_retries=1` 로 429/5xx 도 재시도 — `llm.error` 집계에서 Gemini 의 `rate_limit`/`api_error` 비율이 상대적으로 높게 나올 수 있다(§7 3) |
| U3 (3) Gemini 테스트를 4b 절로 분리(기존 parametrize 무수정) | **채택** | §3(h): 삭제된 parametrize 는 R-1(c) 1곳뿐; `tests/test_baseline_llm_single.py:458,477,501` Claude/OpenAI parametrize 무변경, 925~1130행 별도 절 |
| U4 (1) `.env.example` 은 U1 에서 반영, U4 변경 없음 | **채택** | `git diff --name-only c01381d..HEAD -- .env.example` 0줄, `025a7c4..c01381d` 1줄(주석·`LLM_PROVIDER=openai`·`LLM_PROVIDERS_ENABLED=` 이름만); registry 36행 비고 `U1(c01381d)` 로 정확 |
| U4 (2) registry 새 행 0, 기존 행 비고만 + `U4(pending)` 표기 | **채택(단, pending 2곳·F-4ef1a3)** | §5; 03-log 형식상 커밋 전 `pending` 은 정상이나 닫는 커밋에서 채운다(§6 3). 새 행 0 이 스크립트 6번과 충돌(§6 1) |
| U4 (3) gemini 스모크 exit2 evidence 를 `unset` 서브셸로(훅이 `env`/`printenv` 차단 → 우회 아님) | **채택** | `20260915-1500-u4-smoke-gemini-exit2.txt`(키 이름만, rc=2); security §1 "존재 여부만" 규칙과 정합 — `unset` 은 값을 출력하지 않는다. verifier 도 같은 방식(§3 머리) |

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)

**P4-pilot-eval 로** — 01-plan 131~136행 4항(의존 줄 해시·`meta.provider` 값 집합·결정 A 재확인·보정표 그룹 키)은 그대로 유효. 여기에 이 검토에서 생긴 것을 더한다. **P4 01-plan 이 아래를 옮겨 적었는지 P4 02-plan-verify 에서 본다.**

1. **공급자 선택·결정 A 정합** — P4 실 실행은 OpenAI 1벌. 러너는 `LLM_PROVIDER=openai` 를 **명시**로 넘기고(기본값과 같더라도 — 기본값이 바뀌어도 재현되게), `LLM_PROVIDERS_ENABLED` 는 미설정(전체) 또는 `openai` 로 두며, `meta.provider`·`meta.model` 은 `select_provider(env)` 가 돌려준 이름과 `Judgement.model`/`MentionDecision.detail["model"]` 에서 가져온다(단일 출처 = `JUDGES` 표, `fake`/`stub` 은 표 밖이라 등록표 조회로 나올 수 없다).
2. **Gemini 실호출 미검증(0/3)** — P4 가 Gemini 벌을 돌릴지는 사용자 결정(기본 안 돈다, 01-plan 135행). 돌린다면 그 전에 `docs/user-setup/03`·`08` 의 `--provider gemini` 스모크 1회가 첫 실호출이다(`GEMINI_API_KEY`·`GEMINI_MODEL` 필요, 모델명은 콘솔에서 확인 — 기본값 없음). 결과 파일(공급자·모델·`llm.error`)을 P4 evidence 에 옮겨 적는다.
3. **재시도 비대칭** — Gemini: timeout·connection 만 1회 재시도, 429/5xx 무재시도(호출 1). Claude/OpenAI: SDK `max_retries=1` 이 429/5xx 도 재시도. `llm.error` 범주 집계를 공급자 간 비교할 때 이 차이를 각주로 둔다.
4. **`Judgement.model`(Gemini) 은 `response.model_version`** 우선(`judge.py:716`) — 설정한 `GEMINI_MODEL` 문자열과 다를 수 있다(예: 버전 접미). 보정표 그룹 키를 `model` 로 나눌 때 어느 값을 쓰는지 P4 가 정한다.
5. **토큰 필드** — Gemini `usage_metadata.prompt_token_count`/`candidates_token_count`(None 이면 0). 사고(thinking) 토큰은 `candidates_token_count` 에 포함되지 않을 수 있어 비용 추정 시 별도 확인.
6. **스키마 실 API 수용 여부** — `additionalProperties=false`·`nullable` 이 서버에서 거부되면 `api_error`(400) 로 강등된다. 첫 실호출에서 `llm.error == "api_error"` 가 모든 mention 에 나오면 스키마 변환(`_to_gemini_schema`)을 의심한다 — 판정 로직이 아니라 공급자 층의 문제다.
7. **닫는 커밋 해시**를 P4 01-plan 5행 의존 줄에 채운다(01-plan 인계 1, architect·메인 세션 몫).

**하네스로** — §6 1 (ii)·8: `verify-impl.sh` 6번의 "기존 파일 확장 패키지" 표현 문제(L-nnn 후보), 사용자 결정.

## 8. 1b 최종 실행 출력 (04-review 본문 작성 후)
명령: `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P3-llm-providers | tee docs/wiki/packages/P3-llm-providers/evidence/20260915-1527-review-verify-impl-final.txt`
```
== verify-impl P3-llm-providers  (20260915-1527) ==
........................................................................ [ 94%]
......................................................                   [100%]
918 passed in 36.26s
PASS  pytest 통과 → evidence/20260915-1527-pytest.txt
PASS  compileall 통과 → evidence/20260915-1527-lint.txt
PASS  태그 P3-llm-providers 커밋 6 건 → evidence/20260915-1527-commits.txt
PASS  커밋에 태그 존재: D11
PASS  커밋에 태그 존재: D3
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: R4
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.7
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  `LLM_PROVIDER` ∈ {anthropic, openai, gemini} � ← evidence/20260915-1514-review-verify-imp
PASS  증거 확인:  항목 1a `anthropic` → `judge_from_env()` 가  ← evidence/20260915-1500-u4-providers-3-an
PASS  증거 확인:  항목 1b `openai` → `judge_from_env()` 가 `Op ← evidence/20260915-1500-u4-providers-3-an
PASS  증거 확인:  항목 1c `gemini` → `judge_from_env()` 가 `Ge ← evidence/20260915-1500-u4-providers-3-an
PASS  증거 확인:  항목 2a `anthropic` → `caller_from_env()` 가 ← evidence/20260915-1517-review-pytest-nok
PASS  증거 확인:  항목 2b `openai` → `caller_from_env()` 가 `O ← evidence/20260915-1517-review-pytest-nok
PASS  증거 확인:  항목 2c `gemini` → `caller_from_env()` 가 `G ← evidence/20260915-1517-review-pytest-nok
PASS  증거 확인:  항목 3 비활성 공급자 `InvalidValue`(팩� ← evidence/20260915-1516-review-negative-p
PASS  증거 확인:  항목 4 미지 공급자 `InvalidValue`(메시� ← evidence/20260915-1516-review-negative-p
PASS  증거 확인:  항목 5 신규 테스트는 네트워크 0(스� ← evidence/20260915-1517-review-pytest-nok
PASS  증거 확인:  항목 6 기존 pytest 전건 통과 — 918 pass ← evidence/20260915-1514-pytest.txt, evide
FAIL  registry.md 에 P3-llm-providers 의 산출물이 등록되지 않았다 (중복·누락 방지용)
WARN  미완료 작업 단위 3 개
== 결과: FAIL=1 WARN=1 → evidence/20260915-1527-summary.txt ==
```
- **FAIL 1 · WARN 1.** 1a 의 F-445cda(04-review 표 없음)는 이 실행으로 **해소**(`findings.py … 20260915-1527-review-verify-impl-final.txt --source verify-impl` 재실행, 05-remediation 머리 줄). 남은 FAIL = **F-4ef1a3 [필수]**(registry 패키지 행, §6 1 — R-8 과 스크립트 6번의 충돌, verifier 는 registry 를 고치지 않는다), WARN = F-2f0840 [권고](01-plan U1~U3 `[ ]`). pytest 918 passed skip 0(1a 와 동일). 수용 기준 증거 12행 전부 `증거 확인` PASS.

결과: 완료 — verifier 판정(부분완료, 아래 원문)은 F-4ef1a3 [필수] 하나 때문이었고, 사용자 결정 (i)(D11 카드 행 1줄, 2026-09-15)·(a)(proposal 상단 안내문 1줄) 와 [권고] 2·3(01-plan `[x]` 3줄, `pending` 3곳) 을 닫는 docs 편집으로 반영한 뒤 메인 세션이 같은 명령으로 재실행한 §9 가 **FAIL 0 / WARN 0**(`evidence/20260915-1537-close-verify-impl.txt`), F-4ef1a3·F-2f0840 해소(`findings.py` 출력), 열린 소견 0. 실호출로 검증된 공급자 0/3(F-87c597 열림, R4 꼬리표는 P4 가 닫는다). 
> verifier 원문(2026-09-15 15:27): **부분완료** — 수용 기준 §2 11/11 항목 통과(backlog 51행과 글자 일치), §2b 판정 표 12/12 실측 일치(78행 실 Gemini 는 rc=2 만 일치·실호출 미검증), §3 부정 케이스 python 43/43 + bash (f)~(p) 전부 기대와 일치, D11 "코드에서 지켜야 할 것" (a)~(e) 코드 1:1 대조 통과, 03-log 판단 8건 전부 채택, registry 소견 9건 해소. **`완료` 가 아닌 유일한 이유는 §1b FAIL=1 = F-4ef1a3 [필수]**(registry 에 패키지 열 `P3-llm-providers` 행 0 — 구현 결함이 아니라 02-plan-verify R-8 "새 행 0" 과 `verify-impl.sh` 6번의 충돌; 해소 후보 (i) D11 카드 행 1줄 추가 / (ii) 스크립트 완화 는 사용자·메인 세션 결정). 그 결정과 [권고] 2·3(01-plan `[x]` 3줄, `pending` 해시 3곳)을 닫는 docs 커밋에 담고 같은 명령으로 재검증해 FAIL 0 이 되면 `완료` 로 바꿀 수 있다. H-1(proposal 상단 안내문)은 사용자 결정. 실호출로 검증된 공급자 0/3(F-87c597 열림, R4 꼬리표는 P4 가 닫는다).
승인: 사용자 (2026-09-15) — 완료 승인. F-4ef1a3 해소 방식 (i)·H-1 (a) 도 같은 날 사용자 결정
## 9. 닫는 docs 커밋 후 재실행 (메인 세션, verifier §6 지시대로 같은 명령)
명령: `PYTHONUTF8=1 PYTHONIOENCODING=utf-8 POSTGRES_PORT=5433 bash .claude/scripts/verify-impl.sh P3-llm-providers | tee docs/wiki/packages/P3-llm-providers/evidence/20260915-1537-close-verify-impl.txt`
닫는 편집(코드 0줄): `docs/wiki/registry.md` D11 카드 행 1줄(패키지 열 `P3-llm-providers`, 025a7c4) + `U4(pending)`→`U4(10a66c3)` 2곳 · `01-plan.md` U1~U3 `[x]` · `03-log.md` U4 해시 · `docs/proposal.md` 상단 안내문 1줄(H-1 (a)) · `05-remediation.md` F-4ef1a3·F-2f0840 해결 단계·재검증.
```
== verify-impl P3-llm-providers  (20260915-1537) ==
........................................................................ [ 94%]
......................................................                   [100%]
918 passed in 36.16s
PASS  pytest 통과 → evidence/20260915-1537-pytest.txt
PASS  compileall 통과 → evidence/20260915-1537-lint.txt
PASS  태그 P3-llm-providers 커밋 6 건 → evidence/20260915-1537-commits.txt
PASS  커밋에 태그 존재: D11
PASS  커밋에 태그 존재: D3
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: R4
PASS  커밋에 태그 존재: S3.2
PASS  커밋에 태그 존재: S3.3
PASS  커밋에 태그 존재: S3.7
PASS  검토자 = verifier (L-002)
PASS  증거 확인:  `LLM_PROVIDER` ∈ {anthropic, openai, gemini} � ← evidence/20260915-1514-review-verify-imp
PASS  증거 확인:  항목 1a `anthropic` → `judge_from_env()` 가  ← evidence/20260915-1500-u4-providers-3-an
PASS  증거 확인:  항목 1b `openai` → `judge_from_env()` 가 `Op ← evidence/20260915-1500-u4-providers-3-an
PASS  증거 확인:  항목 1c `gemini` → `judge_from_env()` 가 `Ge ← evidence/20260915-1500-u4-providers-3-an
PASS  증거 확인:  항목 2a `anthropic` → `caller_from_env()` 가 ← evidence/20260915-1517-review-pytest-nok
PASS  증거 확인:  항목 2b `openai` → `caller_from_env()` 가 `O ← evidence/20260915-1517-review-pytest-nok
PASS  증거 확인:  항목 2c `gemini` → `caller_from_env()` 가 `G ← evidence/20260915-1517-review-pytest-nok
PASS  증거 확인:  항목 3 비활성 공급자 `InvalidValue`(팩� ← evidence/20260915-1516-review-negative-p
PASS  증거 확인:  항목 4 미지 공급자 `InvalidValue`(메시� ← evidence/20260915-1516-review-negative-p
PASS  증거 확인:  항목 5 신규 테스트는 네트워크 0(스� ← evidence/20260915-1517-review-pytest-nok
PASS  증거 확인:  항목 6 기존 pytest 전건 통과 — 918 pass ← evidence/20260915-1514-pytest.txt, evide
PASS  registry 에 P3-llm-providers 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=0 → evidence/20260915-1537-summary.txt ==
```
