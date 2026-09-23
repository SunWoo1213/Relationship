# HANDOFF — 다음 세션이 가장 먼저 읽는 문서

> 목적: 컨텍스트가 끊겨도(압축·세션 종료·토큰 소진·크래시) 이 파일만 읽고 같은 자리에서 이어간다.
> 갱신 시점: (1) /commit 마다 (2) 작업 단위 하나가 끝날 때 (3) 컨텍스트가 절반 넘게 찼다고 판단될 때 (4) 큰 파일·여러 파일을 읽기 직전 (5) 턴을 끝내기 전 — `handoff-check.sh`(Stop 훅)가 변경 파일보다 이 문서가 오래됐으면 종료를 막는다.
> 길이: 60줄 이내. 이력은 `journal.md`, 상세는 `packages/<id>/03-log.md`. 여기에는 "지금 어디, 다음 무엇"만.
> 세션 시작·재개·압축 직후 `session-start.sh`가 이 문서를 자동으로 컨텍스트에 넣는다.

갱신: 2026-09-23 12:06 (재개) — **P4b U0~U6 완료. 남은 것은 U7 과 04-review 둘뿐이다.** 이번 세션 경과: 20:40 중단(U4 미커밋) 재개 → 사용자 확정 4건(결정 D 해석 구현대로 · `METRICS_SCHEMA_VERSION` 2 유지 · `report.py` 3열 유지 · P4 기준선 재검증은 명시적 거부, 하위 호환 분기 없음) → **U4 `b5b412c`**(평가 도구 D12·D13 정합, 전체 1325 passed/0 failed) → **U5 선행 `a8faa81`**(결정 I 기준선 stamp 사본 4개 + 카드 10 P4b 갱신) → **U5 준비 `f96d15b`**(비용추정·스텁 사슬 rc=0·recheck rc=0·직전 점검; Docker 꺼져 한 번 막혔다가 사용자 기동 뒤 완료) → **U5 실 실행 `855a26b`**(사용자 1회, rc=0, **게이트 통과**) → **U6**(이 커밋). **게이트: `0.8 [] True True`** — T_merge 0.8 에서 제안 방식 오병합 0/132 · 미검출 0/132, 베이스라인 4종 모두 `dominates_proposed=false`, F1 0.8972(precision 1.0 · recall 0.8136), 되묻기 31건 23.5%. P4 기준선은 `0.8 ['embedding_only'] True False` 로 미달이었다. 비용 $0.0274(상한 $5), 실측 토큰 in 132,017 / out 12,681, `network_calls=340`. **U6 이 찾아낸 것(04-review 가 반드시 읽을 것)**: (1) 오병합·미검출이 사라진 자리는 정답이 아니라 **되묻기**다 — `sc-015` t0 '부장님'은 골드 후보가 3단계에 도달해 귀속이 바뀌었으나 `penalized_candidate` 로 강등돼 deferred, `sc-007` t2 '문실장님'도 conf 0.0→0.5442 로 deferred. (2) **보수 강등 5건은 전부 귀속이 골드였다** — 이 정책이 막은 오병합 0건, 대신 정답 5건을 되물었다(마찰 31건의 16%). (3) **실행 간 `s_llm` 자기보고가 136 mention 중 60건 달랐다** — 게이트 개선을 D12·D13 단독 효과로 읽으면 안 된다(40건으로 분해 불가). 다만 `exact_raw`·`exact_norm`·`embedding_only` 는 결정 변화 0 이라 지배가 풀린 것이 베이스라인 악화 때문은 아니다. (4) **`penalized_merge` 정의 주의**: 원시에서 '후보 아무나 감점' 기준이면 22건, `metrics.json` 이 세는 '귀속 인물 자신이 감점 후보' 기준이면 **14건**(둘 다 오병합 0). 메인 세션이 원시를 직접 다시 세어 확인했다. 04-review 는 이 정의를 함께 읽어야 한다. **커밋 메시지는 사람이 읽는 문장 형식(사용자 지시 19:40) 계속 적용.** **재개(09-23 12:06) 사용자 결정: 미커밋 2파일(U6 후행 기록)을 먼저 커밋하고 U7 → 04-review 순서로 간다. 열린 소견 22건은 전부 [권고]이고 [필수] 는 0 이며 U7 registry 갱신·04-review §5 에서 닫힌다.**
active: **P4b-er-redesign** | frozen: none | 브랜치: dev — dev = origin/dev = **4338eea**(동기화, 01:00 푸시. L-003 마커는 사용자 보류 결정으로 해제). **origin/main = `0dbf2c9` — dev 와 갈라져 fast-forward 승격 불가**(열린 질문 참조). Docker `capstone2-postgres-1` 5433. 미추적 2파일은 **의도적으로 커밋하지 않는 것**: `reports/pilot/raw-20260922-150931.jsonl`(평문 7.7MB, 훅 5MB 한도 — `.gz` 만 커밋)·`reports/pilot/metrics-stage.json`(중간 산출물, P4 도 커밋하지 않았다). 지우지 말고 그대로 둔다.

## 지금 어디까지
- **P3-llm-providers 완료(2026-09-15)** — U1 c01381d·U2 cf01e9f·U3 7b94a69·U4 10a66c3. verifier 04-review `완료`: 수용 기준 11/11(backlog 51행 글자 일치), 부정 python 43/43 + bash, D11 (a)~(e) 코드 1:1, 03-log 판단 8건 채택, registry 소견 9건 해소. verifier 판정은 부분완료(F-4ef1a3 [필수] = R-8 "새 행 0" vs `verify-impl.sh` 94행 "패키지 열 행 필수" 충돌) → 사용자 결정 (i) D11 카드 registry 행 1줄·H-1 (a) proposal 상단 안내문 1줄 → 메인 세션 재실행 **FAIL 0 / WARN 0**(`evidence/20260915-1537-close-verify-impl.txt`, 918 passed), 04-review §9·결과 `완료`·승인 줄. CURRENT active none, backlog 51·53~56 `[x]`, journal DONE.
- **실호출로 검증된 공급자 1/3(openai)** — 스모크 03(2ebf061)·08(750f11b) 완료, F-87c597 해소, R4 "실호출 확인". anthropic·gemini 는 선택(미실행). U7 실 실행 750f11b 기준 완료(결과는 위 갱신 줄).
- **P4 인계(04-review §7, 7항)**: 결정 A 정합(`LLM_PROVIDER=openai` 명시, meta.provider/model 출처 `select_provider`·`Judgement.model`) · Gemini 실호출 0/3 · Gemini 429/5xx 무재시도 비대칭 각주 · Gemini `model` 은 `model_version` 우선 · 토큰 필드·thinking 토큰 · 스키마 실 API 거부 시 `api_error(400)` 강등 · done 커밋 해시를 P4 01-plan 5행에. + P3-baselines 04-review §7 15항, P1-pilot-dataset §7 13항.
- **하네스 L-nnn 후보 2**: (1) `verify-impl.sh` 6번(94행)이 "기존 파일 확장 전용 패키지"를 표현하지 못함 — 이번엔 D11 새 파일 행으로 해소, 다음 확장 패키지가 나오면 "패키지 열 또는 비고 문구" 완화 결정. (2) `POSTGRES_PORT` 는 `export` 로 상속되므로 스크립트 포트 전달 수정은 불필요(verifier 실측) — 후보에서 내린다.
- **실서버 검증 없이 승격됨(2026-09-15, 사용자 결정)** — main 59c67cc 는 pytest 918 만 통과. 첫 실서버 검증은 P9 배포 후 `SERVER-CHECKLIST.md`.
- 이전 패키지 열린 소견: P3-er F-46f1eb, F-036185(F-87c597 은 750f11b 에서 해소), F-251dc2·F-bdd6c5(P4). P2 F-4d2507·F-4d8d96(P5), F-c7078e. P3-llm-providers 열린 소견 0.
- 로컬 DB: capstone2-postgres-1 호스트 5433(Docker Desktop 켜짐), 명령 앞 `POSTGRES_PORT=5433`(export 하면 스크립트도 상속), pytest `-rs`, 한글 출력 `PYTHONIOENCODING=utf-8`, JSON 읽기 `PYTHONUTF8=1`. 사용자 `!` 실행은 셸이 매번 새로 떠서 `set -a; . ./.env; set +a;` 접두 필요(키). `.env` 의 `DATABASE_URL` 은 사용자가 2026-09-22 에 5433 으로 수정(`app/config.py` 규칙 1: DATABASE_URL 이 POSTGRES_PORT 보다 우선 — U7 1·2차 실패 원인). 설치: anthropic 1.4.0·openai 2.33.0·google-genai 2.23.0.

## 바로 다음에 할 것 (순서대로)
1. **U7** eval-agent 위임 승인(L-004) — (a) 01-plan "판정 방법" 표 21행의 **모든 명령**을 실행해 evidence 로 남긴다(특히 11행 게이트 `0.8 [] True True`, 12행 `sc-015`/`sc-007`, 17행 기준선 sha256 `25e16dd6…`, 20행 `subsets.penalized_merge`, 21행 `*real-run*` 파일 1개). (b) `docs/wiki/registry.md` — `app/er/*` 81·82·85행은 **비고에 D12·D13 한 줄과 새 커밋 해시**만 더하고(새 행 금지, F-0ffff5·F-95c6a7 선례), 새 산출물은 행으로: 기준선 stamp 사본 4개 · 재실행 `raw-20260922-150931.jsonl.gz`·`traces-20260922-150931.jsonl` · `failure_cases.md` §13 · U4 가 바꾼 평가 5파일 · `schema_version` 2. (c) `README.md` "파일럿 평가 실행법 (P4)" 절에 P4b 재실행 한 문단, 33행 비고에 패키지명. (d) `docs/user-setup/10-pilot-eval-run.md` 는 a8faa81 에서 고친 내용 확정.
2. **04-review** verifier 위임(L-002·L-004, 새 컨텍스트) — 게이트를 **독립 재계산**한다(도구 판정을 그대로 믿지 않는다). 결정 K (a) 식 그대로 한 번만. 확인할 것: `metrics.json.gate` 인용 + 독립 재계산, `sc-015`/`sc-007` 두 조항(수용 기준의 별도 항목 — `gate.pass` 안에 없다), 기준선 불변(사본 4개·원시 2개 sha256), `app/`·`data/` 무변경, 회귀 3종, D12·D13 "코드에서 지켜야 할 것" 전 항목 grep, `penalized_by` merge 건수 보고. **위 갱신 줄의 U6 발견 4가지를 위임 프롬프트에 넣는다**(구현자 자기 평가는 넣지 않는다). 통과면 `/devlog done` → 패키지 종료 → P5.
3. 그 뒤: `docs/backlog.md` 체크박스, `review-index.md` 상태를 "구현완료(해시)"로, `CURRENT.md active: none`.
4. **main 승격**(열린 질문) — dev 와 갈라져 있어 병합 작업 단위가 먼저 필요하다. 게이트 재판정이 끝난 뒤에 연다.
5. 보류: 하네스 L-nnn(R-2 verify-plan 5번 불릿 의존·03-log Refs=커밋 Refs·main 직접 커밋 차단 장치 없음), 러너 `safe_summary` FIX, 09 카드 §2, anthropic·gemini 스모크, F-46f1eb·F-036185, P10 인계.

## 재개 시 읽을 카드 (이것만)
- `packages/P4b-er-redesign/01-plan.md`(작업 단위 58~69행, 결정 표, 판정 표), `02-plan-verify.md` §2·권고 R-1~R-9, `03-log.md` 마지막 항목, `decisions/D12*.md`·`D13*.md`(코드에서 지켜야 할 것), `changes/CR-001.md` §2, `docs/backlog.md` "P4b" 절
- `docs/wiki/CURRENT.md`, `.claude/gitlog.md`, `decisions/D11-llm-provider-registry.md`
- `lessons/L-001`~`L-004`

## 열린 질문 · 사용자 결정 대기
- **main 이 dev 와 갈라졌다 (2026-09-23 00:10 발견, 승격 시도 중).** 갈림점은 `3c6108d`. main 에만 있는 6커밋(`abfb795`·`8714935`·`e29ac75`·`472e85f`·`b6afc2c`·`0dbf2c9`)이 dev 를 거치지 않고 직접 올라갔다(L-001 과 어긋난다). 건드린 파일: `README.md`·`.github/workflows/tests.yml`·`LICENSE`·`.claude/scripts/verify-impl.sh`·`docs/wiki/evidence/20260919-openai-live-smoke.txt`. `git merge-tree --write-tree dev origin/main` 시뮬레이션 결과 **`README.md` 1건 충돌**(갈림점 이후 main 212줄 수정 / dev 는 `f01ea35` 에서 24줄 수정), 나머지 4파일은 dev 에 없어 충돌 없음. `/commit release` 는 fast-forward 만 허용하므로 `git push origin dev:main` 은 거부된다. 강제 푸시·이력 파괴는 하지 않는다. **사용자 결정(00:12): 승격 보류 — U5 실 실행을 먼저 하고, 게이트 재판정 뒤에 `origin/main` 을 dev 로 병합하는 작업 단위를 따로 연다.** 그때 README 두 본을 다 읽고 합친 뒤 사용자 승인 → 병합 커밋 → dev 푸시 → 승격 순서로 간다. 하네스 L-nnn 후보: main 직접 커밋을 막는 장치가 없다(훅은 `dev` 푸시만 강제하고, 다른 경로로 main 에 올라간 것은 잡지 못한다).
- 09 카드 §2 결정 10개(리전·DB A/B·인스턴스·도메인·443 제한·Session Manager·수동 dispatch·EC2 빌드·프론트·백업) — P9 착수 전 사용자 확정. DB A안(compose) 선택 시 D12 카드 필요.
- 하네스 L-nnn: `verify-impl.sh` 6번 완화 여부(다음 확장 전용 패키지 때 결정).

## 주의 (다음 세션이 실수하기 쉬운 것)
- 재개 시 커밋 안 된 변경·진행 중 항목이 있으면 **먼저 사용자에게 목록을 보이고 우선순위를 묻는다**(`/devlog resume`).
- **점검표·완료 검토는 verifier 에게 위임**(L-002). **위임은 묻고 시작**(L-004): AskUserQuestion → `approve-commit.sh --stage <이름>` → Agent 1회. Docker 가 꺼져 있으면 우회하지 않고 사용자에게 켜 달라고 한다(security §6).
- **푸시는 `git push origin dev` 만**. 푸시 뒤 `.claude/.awaiting-decision` → 승격/수정/보류를 묻고 멈춘다(L-003).
- 승인 마커는 커밋 명령과 **다른 Bash 호출**에서 먼저. `git commit` 과 `git push` 를 한 Bash 호출에 묶지 않는다. Bash 문자열에 마커 파일명·훅 금지 문구·환경변수 전체 출력(`environ` grep·`env -u` 포함) 금지 — 문서 수정은 scratchpad 스크립트 + python 또는 Write. `.env` 존재 확인 금지. `git checkout --` 금지. evidence 파일은 cp949 혼입이 있을 수 있어 python 읽기는 `errors="replace"`.
- **푸시 명령은 Bash 호출 하나에 단독으로**(뒤에 `grep` 등 실패할 수 있는 명령을 붙이면 종료 코드가 0 이 아니어서 cleanup 훅이 돌지 않는다 — 2026-09-15 실측, 같은 push 재실행으로 복구).
- `findings.py` 는 `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` 앞에. verify-impl 재실행마다 `<ts>-pytest/lint/commits/summary.txt` 4개가 생기므로 중복 실행분은 지우고 커밋한다.
- 서브에이전트에게 HANDOFF·journal 금지 명시. `app/` docstring 에 "evaluation" 문자열 금지(`test_app_does_not_mention_evaluation_package_at_all`).
