# review-FIX-036 · 인프라 파일 검사 테스트 27 을 "작업 트리에 없다" 에서 "git 이 추적하지 않는다" 로 — 커밋 전 리뷰

검토자: verifier (fable) · 2026-11-15 · 기준 HEAD `5c0f26d` (dev2) + 작업 트리 미커밋 diff(`tests/test_infra_files.py` +29/-10) · Refs: FIX-036 P9-infra D17 security

**결과: 통과 — [필수] 0건, [권고] 2건(R-36-1·R-36-2), [참고] 2건.** 고친 테스트는 FIX-036 수정안 세 항목을 모두 지키고, 옛 테스트가 잡던 경우 가운데 새 테스트가 놓치는 것은 "추적되지 않고 ignore 된 상태 파일이 작업 트리에 있다" 하나뿐이며 그것이 이 FIX 가 의도한 변경이다. 내가 돌린 변이 9종 중 8종이 기대대로였고 1종(C9)이 살아남았으나, 옛 테스트도 잡지 못하던 경우라 약화가 아니다.

## 1. 본 것

- `docs/wiki/fixes/FIX-036.md` 증상·원인·수정안·기획서 정합성·`계획 점검: 통과`.
- `git diff -- tests/test_infra_files.py` 전체: `import subprocess` 추가, `_is_state_or_vars()`·`_git()` 신설, 테스트 27 을 `test_no_state_or_vars_files_are_tracked_by_git` 로 교체.
- `git status --short`: 추적 파일 변경은 `docs/wiki/CURRENT.md`·`HANDOFF.md`·`journal.md`·`tests/test_infra_files.py` 4개. `app/`·`alembic/`·`web/`·`infra/` 변경 0(리뷰 시작·종료 모두 `4 files changed, 32 insertions(+), 11 deletions(-)`). 앞의 문서 3개는 위임 지시대로 판정에서 뺐다.
- 근거 문장: `docs/wiki/security.md:10` "`.env`, `*.pem`, `*.key`, tfstate/tfvars 는 에이전트가 읽지도 쓰지도 않는다" · `.gitignore:40-42`(`*.tfstate`·`*.tfstate.backup`·`*.tfvars`)·`:46-49`(`infra/*.tfstate`·`infra/*.tfstate.*`·`infra/*.tfvars`·`!infra/terraform.tfvars.example`).
- 구현자 증거 3개 `fixes/evidence/20261115-2024-FIX-036-{infra-tests,pytest-all,mutations}.txt` (40 passed · 2261 passed · V0~V8).
- `infra/terraform.tfstate` 는 **이름만** 봤다(`ls infra`). 내용을 읽지 않았고 지우거나 옮기지 않았다. 변이 사본은 `git archive HEAD` 로 만들어 추적 파일만 들어간다(상태 파일은 추적되지 않으므로 사본에 없다 — C0 의 `ls infra` 출력으로 확인).

## 2. 내가 직접 실행한 것 (전부 `save_evidence.py` 통로, 출력 전문)

| # | 명령 | 결과 | 증거 |
|---|---|---|---|
| 1 | `.venv/bin/python -m pytest tests/test_infra_files.py -q` | **40 passed**, exit 0 | `fixes/evidence/20261115-2026-verifier-FIX-036-infra-tests.txt` |
| 2 | `.venv/bin/python -m ruff check tests/test_infra_files.py` | All checks passed, exit 0 | `…-2026-verifier-FIX-036-ruff.txt` |
| 3 | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -q -rs` | **2261 passed**, 실패 0, skip 요약 줄 없음, exit 0 (기준선 `1 failed, 2260 passed` 의 1건이 닫힘) | `…-2026-verifier-FIX-036-pytest-all.txt` |
| 4 | 변이 9종 — 스크래치패드 `vmut036/` 아래 사례마다 새 사본(`git archive HEAD tests/test_infra_files.py infra .gitignore` + 작업 트리의 테스트 파일 덮어쓰기 + `git init`·`git add -A`, 커밋 없음). 저장소 무수정 | 아래 표 | `…-2027-verifier-FIX-036-mutations.txt` (C9 는 `--append`) |

변이 표:

| ID | 사본 상태 | 기대 | 결과 |
|---|---|---|---|
| C0 | 무변이(대조군) | PASS | 1 passed |
| C1 | `infra/x.tfstate` 를 `git add -f` | FAIL | FAIL — `git 이 상태·변수 파일을 추적한다: ['infra/x.tfstate']` |
| C2 | 추적 안 됨 + ignore 된 `infra/terraform.tfstate` 만 있음(배포 뒤 이 기기 상태) | PASS | 1 passed — FIX 의 목적 |
| C3 | `.gitignore` 의 tfstate 줄 제거 + 작업 트리 `infra/terraform.tfstate` | FAIL | FAIL — `작업 트리에 있는데 ignore 되지 않는다(rc=1)` |
| C4 | `infra/비밀.tfvars` 를 `git add -f` (파일은 작업 트리에도 있음) | FAIL | FAIL — 다만 **추적 단언이 아니라 둘째 단언(check-ignore)** 이 잡았다 → R-36-1 |
| C5 | `.gitignore` tfstate 줄 제거, `.git/info/exclude` 로만 ignore | 27 은 통과 가능 | 27 **통과**, 같은 파일의 `test_gitignore_blocks_state_vars_and_plugin_cache` 가 FAIL — 묶음으로는 검출 → R-36-2 |
| C6 | `infra/env/prod.tfvars` 를 `git add -f` (하위 디렉터리) | FAIL | FAIL — 옛 테스트(`iterdir()` 최상위만)보다 **강해진** 부분 |
| C7 | `.gitignore` tfvars 줄 제거 + 추적 안 된 `infra/prod.auto.tfvars` | FAIL | FAIL — check-ignore 단언 |
| C8 | 옛 테스트(HEAD 판)를 C2 상태에 | FAIL | FAIL `AssertionError: terraform.tfstate` — FIX-036 증상 재현 |
| **C9** | C4 에서 작업 트리의 `infra/비밀.tfvars` 만 지움(색인에는 남음) | FAIL | **살아남음(1 passed)** → R-36-1 |

## 3. 판정

### 3.1 수정안 대조 (`FIX-036.md` 20~23행)

| 항목 | 코드·시험 | 판정 |
|---|---|---|
| 테스트 27 만 고친다, 제품 코드 무변경 | diff 는 이 파일의 27 과 그 헬퍼 2개뿐. `app/`·`alembic/`·`web/` 변경 0 | 충족 |
| `git ls-files infra` 에 `.tfstate`·`.tfvars`(example 제외) 없음 단언 | `_is_state_or_vars(Path(t).name)` — `terraform.tfvars.example` 은 `.tfvars` 로 끝나지 않아 제외. C1·C6, 구현자 V1~V3 | 충족 |
| 작업 트리에 있으면 `git check-ignore` 단언, 없으면 건너뛰지 않고 통과 | `for p in (ROOT/"infra").iterdir()` + `check-ignore -q`. `pytest.skip` 호출 없음. C2·C3·C7 | 충족 |
| 함수 이름 변경·docstring 수정 | 이름·docstring 모두 사실과 일치("파일 내용은 읽지 않고 이름만 본다" — 코드에 `read_text`·`open` 없음) | 충족 |
| 이름을 참조하는 문서 함께 고침 | `grep -rn present_in_tree docs tests .claude .github` — 남은 곳은 과거 증거·리뷰(P9-infra review-u3c, evidence)와 P9b-auth 계획의 기준선 서술뿐. 과거 기록은 고치지 않는 것이 맞다. `packages/P9-infra/tests.md` 에는 이 함수 이름이 없다 | 충족(고칠 곳 없음) |
| 회귀·변이 | §2 #1·#3·#4 | 충족 |

### 3.2 약해진 곳이 있는가

- 옛 테스트가 잡고 새 테스트가 못 잡는 경우는 **"추적 안 됨 + ignore 됨 + 작업 트리에 있음"** 하나다(C2 ↔ C8). 이것이 FIX 의 의도이고, security.md:10 과 D17 이 금지하는 것은 저장소에 들어가는 것·에이전트가 읽고 쓰는 것이지 사용자가 apply 한 산출물이 로컬에 있는 것이 아니다.
- 그 대가로 옛 docstring 의 부수 신호("에이전트는 apply 한 적이 없다")는 더 이상 이 테스트로 보이지 않는다. apply 는 사용자 몫이고 이미 실행됐으므로 그 신호는 지금 뜻이 없다 — 약화로 보지 않는다.
- 강해진 곳: 하위 디렉터리의 추적 파일(C6), 색인에만 있고 작업 트리에서 지워진 추적 파일(ASCII 이름), git 을 못 부르면 실패(구현자 V7 — `returncode 128` 단언, skip 아님), 추적 0개면 실패(`assert tracked`).
- 항상 통과하는 테스트가 아니다: C1·C3·C6·C7 에서 실패한다.

## 4. 소견

- **R-36-1 [권고] 비ASCII 이름의 `*.tfvars` 가 추적 단언을 빠져나간다.** `git ls-files` 는 기본(`core.quotepath=true`)으로 비ASCII 경로를 `"infra/\353\271\204\353\260\200.tfvars"` 처럼 따옴표로 감싸 낸다. 그러면 `Path(t).name` 이 `.tfvars"` 로 끝나 `name.endswith(".tfvars")` 가 거짓이 된다(`tests/test_infra_files.py:430`·`447`). 파일이 작업 트리에도 있으면 둘째 단언이 대신 잡지만(C4), **색인에만 남은 경우는 통과한다(C9, 1 passed).** `.tfstate` 쪽은 `in` 검사라 영향이 없다. 옛 테스트도 이 경우(작업 트리에 파일 없음)를 잡지 못했으므로 약화는 아니다. 고치려면 `git -c core.quotepath=off ls-files infra` 또는 `ls-files -z` + `\0` 분리. 이 프로젝트의 변수 파일 이름이 한글일 가능성은 낮아 필수로 올리지 않는다.
- **R-36-2 [권고] check-ignore 는 저장소 밖 ignore 설정도 인정한다.** `.git/info/exclude` 나 사용자 전역 `core.excludesFile` 로만 막혀 있어도 27 은 통과한다(C5). 다른 체크아웃에서는 막히지 않는 상태다. 지금은 같은 파일의 테스트 25(`test_gitignore_blocks_state_vars_and_plugin_cache`)가 `.gitignore` 글자를 직접 보아 묶음으로 검출하므로(C5 둘째 실행) 공백은 아니다. 27 의 docstring 이 "`.gitignore` 가 막고 있어야 한다" 고 쓰는데 실제 보장은 25 와 함께일 때만 성립한다는 점을 적어 둔다 — 25 를 고칠 때 이 의존을 기억할 것.
- **[참고] 구현자 변이 V8 의 서술이 모호하다.** `20261115-2024-FIX-036-mutations.txt` 의 V8("약화 테스트는 PASS")은 테스트를 약화하면 backup 추적을 놓친다는 것, 즉 `'.tfstate' in` 판정이 V3 을 떠받친다는 것을 보인 것으로 읽힌다. 결과는 타당하나 "기대: FAIL 해야 하나 … PASS" 문장만으로는 통과·실패 중 무엇이 기대였는지 한 번에 읽히지 않는다. 판정에는 영향 없음.
- **[참고] 검사 범위는 여전히 `infra/` 다.** 저장소 루트 등 다른 곳에 추적된 `*.tfstate` 는 27 이 보지 않는다(옛 테스트도 같았다, `.gitignore:40-42` 가 전역으로 막는다). 범위 변경 없음.

## 5. 결론

통과. [권고] 2건은 커밋을 막지 않는다 — R-36-1 은 다음에 이 테스트를 만질 때 함께 고치면 된다. `FIX-036.md` 의 `검증:` 줄을 채웠다. 코드는 고치지 않았고 커밋하지 않았다.
