# review-FIX-029 · 커밋 전 리뷰 — `app.push` 를 먼저 import 하면 순환 import 로 실패한다

검토자: verifier (fable) · 2026-10-10 · 기준 HEAD `6428180` + 작업 트리 미커밋 diff(`app/briefing/scheduler.py` +4/-1, `tests/test_import_order.py` 신규 56줄) · Refs: FIX-029 F-c7c1e5 P7-push S3.6 R12

**판정: 통과** — [필수] 0건, [권고] 4건(R-29-1~R-29-4). 코드는 고치지 않았다(대조용 임시 변이는 Edit 로 넣고 Edit 로 원복, diff 바이트 동일 확인). FIX-029.md 의 `검증:` 줄 한 줄만 갱신.

통과 요지: (1) diff 가 계획 표 A 그대로다 — 모듈 상단 79행 제거, `default_run_once()` 본문 첫머리로 이동, 주석 2줄, 그 밖 변경 없음(`git status` 상 코드 파일 2개뿐). (2) 새 테스트는 공허하지 않다 — A 를 되돌리면 `app.push` 계열 6건이 순환 ImportError 로 FAILED, 원복하면 9 passed(§2 변이). (3) 전체 회귀 1882 passed·skip 0, `mypy_check.py --run` 기준선 38/38, ruff 통과 — 전부 직접 실행. (4) `app/` 아래 54개 모듈 전부를 새 프로세스로 단독 import 해 실패 0 — 같은 종류의 다른 순환은 지금 없다. (5) Windows job 조건(DB 환경변수 없음)으로도 import exit 0.

## 1. 본 것

- 문서: `docs/wiki/fixes/FIX-029.md`(증상·원인·수정안 A~E·결과). 발견 근거 `packages/P7-push/evidence/20261010-2005-review-import-cycle.txt`(내가 P7-push 04-review 에서 남긴 것), 구현 증거 `fixes/evidence/20261010-2030-fix029-contrast-and-regression.txt`.
- diff: `app/briefing/scheduler.py` 76~80행(상단 import 5→4줄), 92~94행(지연 import + 주석). 주석이 순환 경로를 정확히 적는다(push.notifier → briefing 패키지 → 이 모듈 → push.notifier). 시그니처·호출(105행 `notifier_from_env(session, ctx.user_id, ctx.now)`)·`run_briefings(..., trigger="scheduler")` 무변경.
- `tests/test_import_order.py`: 모듈 9개 parametrize, `subprocess.run([sys.executable, "-c", f"import {m}"], cwd=REPO_ROOT, timeout=60)`, returncode 0 단언, 실패 시 stderr 마지막 5줄을 메시지에 붙임. `dbtest` 마커 없음(DB 불필요 — 맞다). 왜 서브프로세스여야 하는지(conftest 가 `app.main` 을 먼저 올려 순환이 가려짐) 를 docstring 에 적었다.
- 순환의 구조(변경 없음): `app/push/__init__.py:38` → `app/push/notifier.py:65 from app.briefing.types import ...` → 패키지 `app/briefing/__init__.py:27 from app.briefing.scheduler import ...` → scheduler 가 다시 `app.push.notifier`. `app/settings.py:105, 376` 이 이미 같은 이유로 `app.push.types` 를 함수 안에서 지연 import 하고 있어(주석 "순환 import 회피") 이번 방식은 저장소의 선례와 일치한다.
- 다른 상단 import 진입점: `app/api/deps.py:114`, `app/api/routes.py:150` — 둘 다 `app.push` 를 상단에서 가져오지만 역방향(`app.push` → `app.api`) 경로가 없어 순환이 아니다(§2 전수 조사로 확인).

## 2. 내가 직접 실행한 것

| 명령 | 결과 | 증거 |
|---|---|---|
| 표 A 루프(9개 모듈 단독 import) | `FAIL` 줄 0, 9개 모두 OK | `evidence/20261010-2040-review-fix029-regression.txt` §2 |
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest tests/test_import_order.py tests/test_push_wiring.py -q` (B+E) | `18 passed in 3.00s` | 같은 파일 §3 |
| `POSTGRES_PORT=5433 .venv/bin/python -m pytest -rs` (D) | `1882 passed, 1 warning in 22.52s`, skip 0 (= 1873 + 9) | 같은 파일 §4 |
| `.venv/bin/python scripts/mypy_check.py --run` | `[ok] 새 오류 없음 (현재 38건, 기준선 38건)` exit 0 | 같은 파일 §5 |
| `.venv/bin/ruff check app tests scripts evaluation` | `All checks passed!` | 같은 파일 §5 |
| `app/` 전수 단독 import(pkgutil.walk_packages, 54개, 각각 새 프로세스) | 실패 0 | 같은 파일 §6 |
| 최소 환경변수(PYTHONUTF8·PATH 만, DB 변수 없음)로 subprocess import 5개 | 전부 exit 0 | 같은 파일 §7(a) |
| 다른 cwd(/private/tmp)에서 import | `ModuleNotFoundError` — 테스트의 `cwd=REPO_ROOT` 가 필요한 설계임을 확인 | 같은 파일 §7(b) |
| **변이(표 C)**: Edit 로 A 되돌림(`git diff --stat` 빈 출력 = HEAD 동일) → B 실행 → 표 A 루프 → Edit 로 원복 → 저장해 둔 diff 와 `diff` 비교 | 변이: **6 failed, 3 passed**(app.push 6건 모두 `ImportError: cannot import name 'notifier_from_env' from partially initialized module`), 루프 FAIL 6; 원복: `diff 동일: 원복 완료`, md5 동일, `9 passed` | `evidence/20261010-2040-review-fix029-mutation.txt` |

실행 후 작업 트리는 구현 직후와 같다: `git diff --stat` = `scheduler.py 5 ++++-`, `HANDOFF.md 2 +-`, `journal.md 2 ++`(§2 증거 §6). 스크래치패드 밖에 잔여물 없음.

## 3. 확인 항목별 판정

### 3.1 계획 표 A~E 와의 대조 — 일치
- A: import 1줄 이동 + 주석. `notifier_from_env` 를 쓰는 자리는 scheduler 안에서 105행 하나뿐(`grep -rn notifier_from_env app`). 동작·시그니처 무변경(18 passed·1882 passed).
- B: 표 A 의 9개 모듈과 같은 목록(`MODULES`), 서브프로세스, returncode 단언. 요구대로.
- C: 구현 증거의 "6 failed, 3 passed → 9 passed" 를 내가 독립적으로 재현했다(위 표). 되돌린 코드는 커밋되지 않는다(원복 확인).
- D: 1882 = 1873 + 9, skip 0. E: push_wiring 9 passed.
- 범위: 바뀐 코드 파일은 계획이 적은 2개뿐. `docs/wiki/HANDOFF.md`·`journal.md` 는 문서.

### 3.2 테스트가 실제로 실패 조건을 검사하는가 — 그렇다
변이에서 6건 FAILED, 메시지에 순환 ImportError 와 파일 경로가 그대로 드러난다. `app.briefing`·`app.briefing.scheduler`·`app.main` 3건은 변이에서도 통과하는데 이는 결함 자체가 "push 를 먼저 올릴 때만" 나는 것이라 맞는 결과다(04-review 증거 20261010-2005 와 같은 분포).

### 3.3 같은 종류의 다른 순환 — 지금은 없다
`app/` 54개 모듈(요청에 있던 `app.api.*`·`app.briefing.*`·`app.settings` 포함) 전부 새 프로세스 단독 import 실패 0. 참고로 `app.push.devpage` 라는 모듈은 없다 — `/push-dev/` 는 `app.api.routes` 안에 있고 그것도 통과. 단 새 테스트는 9개만 고정 목록으로 본다 → R-29-1.

### 3.4 CI(Linux 3.13·3.14, Windows)에서 의미 있게 도는가 — 그렇다
- cwd: `REPO_ROOT = Path(__file__).resolve().parent.parent` 절대경로를 `cwd=` 로 넘기므로 pytest 를 어디서 띄우든 `app` 이 보인다(§7(b) 가 반례를 보여 줌). CI 는 저장소 루트에서 `python -m pytest ... tests/` 라 어차피 맞는다.
- 인터프리터: `sys.executable` — Linux 는 setup-python 의 python, Windows 도 같은 네이티브 python. venv 가 없어도 성립.
- 환경변수: 부모 환경을 그대로 상속. Windows job 은 `DATABASE_URL`·`POSTGRES_*` 를 주지 않는데, 최소 환경(§7(a))으로도 5개 모듈 import 가 exit 0 이므로 import 시점에 DB 접속·필수 변수 검사가 없다. `PYTHONUTF8=1` 이 세 job 모두에 있어 stderr 디코딩(`text=True`)도 문제없다.
- 마커: `dbtest` 아님 → Windows `-m "not dbtest"` 에서도 실행된다(deselect 되지 않음). 커버리지: 서브프로세스는 `--cov=app` 에 안 잡히지만 app 코드 커버리지를 깎지도 않는다(fail_under 90% 무관).
- 소요: 로컬 9건 2.5초. Windows 프로세스 생성이 느려도 `timeout=60`/건이라 여유.

### 3.5 지연 import 가 몽키패치 지점·동작을 바꾸는가 — 바꾸지 않는다
- tests/ 전체에서 `setattr(scheduler_module, …)` 대상은 `BRIEFING_INTERVAL_SECONDS`·`composer_from_env`·`default_run_once`·`run_briefings`·`session_scope` 뿐(§8). `scheduler_module.notifier_from_env` 를 패치하는 테스트는 0건 — 이 이름이 더 이상 scheduler 전역이 아니어도 깨지는 테스트가 없다(1882 passed 가 뒷받침).
- `test_push_wiring` (c) 3건은 `notifier_module.PyWebPushSender` 를 패치한다. 지연 import 는 호출 때마다 `app.push.notifier` 의 함수 객체를 가져오고 그 함수는 자기 모듈 전역에서 `PyWebPushSender` 를 읽으므로 패치가 그대로 먹는다(18 passed).
- 런타임: `default_run_once` 는 `asyncio.to_thread` 로 워커 스레드에서 돈다. 첫 호출 때 import 가 일어나지만 `app.main` 이 lifespan 에서 `app.api.deps`(상단 `from app.push.notifier import …`)를 이미 올려 두므로 실제로는 `sys.modules` 조회 한 번이다. import lock 경합도 없다.
- 향후 주의(R-29-4): 테스트가 scheduler 쪽에서 `notifier_from_env` 를 바꿔 끼우려면 `app.push.notifier.notifier_from_env` 를 패치해야 한다(지연 import 가 호출 시점에 그 모듈 전역을 읽으므로 효과 있음).

### 3.6 정합성 — 원칙·D·S 무영향
import 위치만 바뀐다. 툴 시그니처(S3.2)·스키마·브리핑/푸시 동작(S3.6) 무변경. 비밀 문자열 없음(diff 에 상수·키 없음). 테스트 없는 분기 없음(바뀐 분기는 import 한 줄이고 새 테스트가 그것을 본다).

## 4. 소견

### [필수] — 없음

### [권고] — 커밋을 막지 않음

- **R-29-1 테스트 모듈 목록의 범위.** 지금은 9개 고정 목록이라 `app.api.deps`·`app.api.routes`·`app.settings`(모두 `app.push` 를 가져오는 진입점, §9)나 앞으로 생길 모듈의 순환은 잡지 못한다. 내 전수 조사(54개, 실패 0)는 오늘 한 번의 증거일 뿐이다. 선택지: (a) `pkgutil.walk_packages` 로 `app/` 전체를 parametrize(로컬 54건 약 16초, Windows 는 더 느림 — `timeout` 과 CI 시간 고려), (b) 최소한 위 3개 진입점을 목록에 더한다(비용 거의 없음). 이번 FIX 범위 밖이므로 기록만 한다.
- **R-29-2 FIX-029.md 결과절의 mypy 수치.** "mypy 39건은 기존 오류" 는 `mypy app tests/test_import_order.py` 를 `--ignore-missing-imports` 없이 돌린 수치다. CI 기준은 `scripts/mypy_check.py --run`(38건 = 기준선 38건, exit 0)이므로 결과절에는 그 명령·출력을 적는 것이 사실성 규칙에 맞다(수치가 다른 두 명령이 섞이면 다음 사람이 "1건 늘었나" 를 다시 확인해야 한다).
- **R-29-3 구조적 원인은 남아 있다.** 지연 import 는 `app/settings.py` 의 선례와 같은 방식이고 이번 결함을 닫지만, 뿌리는 `app/push/notifier.py:65` 가 `app.briefing.types` 하나를 가져오려고 패키지 `app/briefing/__init__.py` 의 eager re-export(27행 scheduler 포함) 를 통째로 실행하는 구조다. scheduler 가 나중에 `app.push` 에서 이름을 하나 더 상단 import 하면 같은 함정이 재발한다. 다음에 briefing/push 경계를 손볼 때 `app/briefing/__init__.py` 의 scheduler re-export 를 빼거나 `NullNotifier`/`ComposedBriefing` 을 패키지 실행 없이 닿을 수 있게 두는 것을 검토한다. 범위 밖.
- **R-29-4 몽키패치 안내.** `notifier_from_env` 가 scheduler 전역에서 사라졌으므로 향후 테스트는 `monkeypatch.setattr(app.push.notifier, "notifier_from_env", …)` 를 써야 한다. scheduler 모듈 docstring 의 "테스트가 간격·실행 함수를 주입하는 방법" 절에 한 줄 적어 두면 같은 혼란을 막는다. 이번 FIX 범위 밖.

## 5. 결론

`검증: 통과 — verifier (fable) 2026-10-10, review-FIX-029.md` 를 FIX-029.md 에 기록한다. 제품 코드(`app/`)를 바꾸므로 commit-guard 규칙 6 대상이며, `검증:` 줄(정확히 하나, 구분자 뒤 verifier)과 이 리뷰 파일(`검토자:` 줄에 verifier)이 그 조건을 채운다. 작업 트리는 구현 직후와 동일하다(§2 끝). 커밋은 메인 세션이 `/commit` 으로 한다.
