# P7-push · 계획 (01-plan)

상태: 초안(architect 작성 · 결정 A~G 사용자 확정 2026-10-02 전부 권장안 · 02-plan-verify 는 verifier 몫) | 담당: backend-agent(`app/push/` 새 패키지 · `app/api/routes.py`·`deps.py`·`schemas.py` 엔드포인트 자리 · `app/briefing/scheduler.py` 알림기 주입 한 자리 · `app/settings.py` 상수 · `requirements.txt` 한 줄 · `.env.example` 한 줄) + 사용자·메인 세션(U8 실발송 확인) | 작성: 2026-10-02
태그 — 패키지: P7-push · 닫는 검증: R12(푸시 절반 — 브리핑 트리거 절반은 P6-briefing 이 닫음) · 기대는 결정: 없음(D7 은 배포 HTTPS — 운영 푸시의 보안 컨텍스트 조건으로 P9-infra 에 넘긴다) · 구현하는 명세: S3.6 S3.1 · 관련 원칙: 원칙5 원칙7 원칙8 원칙9
의존: P6-briefing(04-review `결과: 완료`, 완료 처리 `f9500fe`) · 선행 게이트 P4b-er-redesign(04-review `결과: 완료`)

- 근거 해시(`.claude/gitlog.md` 스냅샷 2026-10-02 20:54, Bash 없이 읽음 — L-001): 작업 브랜치 `dev2` HEAD = `608694b`(FIX-017 "사실 키의 뜻을 LLM 에게 알려 '안 좋아해' 가 likes 로 가지 않게 한다"), origin/dev = `f9500fe`(P6-briefing 완료 처리), main = `f05d017`. P6-briefing 단위 커밋 U1 `e2155f9` · U2 `db3c645` · U3 `cfb55ea` · U4 `a2f032d` · U5 `e037728` · U6 `8589e37` · U7 `a67692e` · U8 `e2cca80`, 완료 처리 `f9500fe`.
- **이 패키지의 시작 해시(무변경 diff 기준점) = `608694b`.** 스냅샷 시점 미커밋 변경은 `docs/wiki/journal.md` 하나이고 제품 코드는 0이다.
- 태그 `P7-push` 로 이미 있는 커밋은 스냅샷에서 확인되지 않는다. 이력이 더 필요하면 메인 세션에 **`bash .claude/scripts/gitlog.sh P7-push R12 S3.6` 실행을 요청**한다.
- P6-briefing 04-review §7 인계(이 계획이 기대는 것): ① `Notifier.notify(schedule: Schedule, composed: ComposedBriefing) -> str` 자리(`app/briefing/types.py`)와 기본 `NullNotifier`(`"not_configured"`). ② 호출 순서 = 입력 조립 → 생성·검증 → `notify` → `briefing_compose` trace, 전부 **같은 세이브포인트** 안 — `notify` 가 예외를 내면 그 일정의 `briefed_at` 까지 되돌려지고(`stage="notify"`) 다음 분에 다시 집혀 **LLM 이 다시 돈다**. ③ 반환 문자열이 응답 `briefings[].push` 와 trace `output.push` 에 그대로 실린다. ④ 호출하는 곳은 두 군데 — `app/api/routes.py::run_briefings_endpoint`(수동)와 `app/briefing/scheduler.py::default_run_once`(1분 주기). 둘 다 지금은 `notifier` 를 넘기지 않아 기본 `NullNotifier` 가 쓰인다. ⑤ §6-3: LLM 이 요약 줄에 사용자 원문을 **글자 그대로** 옮긴 사례가 U4·U6·U7 실서버에서 반복 관찰됐다("민수는 고수를 진짜 싫어하더라"). 응답 스키마에 원문 필드는 없지만 푸시 본문에 실리면 원문이 알림으로 노출된다.

## 목표

`docs/resolution-plan.md` §3.6 과 S3.6 카드의 첫 문장과 마지막 문장 — "주기 작업(컨테이너 내, 1분): … → `get_briefing` → **웹푸시** → `briefed_at`", "푸시 구독은 `push_subscriptions`. VAPID 키는 SSM/환경변수, 코드·저장소에 두지 않는다" — 중 P6-briefing 이 비워 둔 **웹푸시 칸**을 채운다. 지금은 브리핑이 만들어져도 응답과 `agent_traces` 에만 남고, 사용자가 화면을 열지 않으면 만남 직전에 아무것도 알 수 없다. 이 패키지는 세 가지를 만든다. ① **구독 저장**: 브라우저가 만든 웹푸시 구독(엔드포인트 URL + 암호 키 두 개)을 `push_subscriptions` 에 사용자 단위로 저장하는 API 와, VAPID 공개키를 브라우저에 건네는 API. ② **VAPID 발송**: `Notifier` 자리에 `WebPushNotifier` 를 끼워, 브리핑이 생기면 그 사용자의 구독 전부에 VAPID 로 서명한 암호화 푸시를 보내고, 결과(성공·실패·만료 구독 정리)를 trace 에 남긴다. ③ **확인 경로**: 데스크톱 Chrome 에서 실제로 알림을 받는 것을 사람이 확인할 수 있도록, 개발·확인 전용 구독 페이지(결정 A)와 확인 절차. 예: 사용자가 Chrome 확인 페이지에서 "알림 받기" 를 한 번 누르면 구독이 저장되고, 이후 내일 저녁 7시 민수와의 약속이 24시간 안으로 들어온 순간 1분 안에 데스크톱에 "민수 · 저녁 약속 — 10/03 19:00 · 제안: 고수 없는 식당을 고르세요" 알림이 뜬다. **브리핑 내용 생성 방식(프롬프트·검증기)은 바꾸지 않는다**(P6-briefing 코드 무변경).

## 범위

- 포함:
  - **설정·의존성** — `pywebpush` 한 줄(버전 고정), `app/settings.py` 에 VAPID 설정 읽기 함수(값을 반환만 하고 로그·trace 에 쓰지 않는다)·발송 상수(시간 초과·TTL 상한·본문 상한)·확인 페이지 스위치 읽기 함수, `.env.example` 에 확인 페이지 스위치 한 줄(기존 VAPID 이름 줄 31~34행은 그대로).
  - **구독 저장 API** — `GET /push/vapid-public-key`(공개키만), `POST /push/subscriptions`(브라우저 `PushSubscription.toJSON()` 모양 그대로 받음). 사용자 귀속은 `app_user_id()`, 같은 엔드포인트 재구독은 행을 늘리지 않고 키만 갱신(결정 F).
  - **푸시 본문 작성기** — 순수 함수. 일정·인물 이름·생성된 브리핑에서 알림 제목·본문을 만든다(결정 B). 요약 줄·패턴 문장은 싣지 않는다(권장안).
  - **발송기·알림기** — `PushSender` Protocol(실제 `PyWebPushSender` · 테스트용 `FakePushSender`), `WebPushNotifier`(구독 조회 → 발송 → 결과 분류 → 만료 구독 정리 → `push_send` trace), `notifier_from_env(...)`(키 없으면 `NullNotifier`).
  - **연결** — 수동 경로(`POST /briefings/run`)와 1분 주기 경로(`default_run_once`)가 같은 방식으로 알림기를 받게 한다(의존성 `get_notifier()` · 주기 작업 한 자리). `run_briefings()` 자체는 고치지 않는다.
  - **개발·확인 전용 구독 페이지**(결정 A 권장안) — 백엔드가 스위치가 켜졌을 때만 서빙하는 정적 파일 3개(HTML 한 장 · 서비스 워커 · 구독 스크립트).
  - **관측성(원칙9)** — `tool_name="push"`, step `push_send` 1종(결정 F). 어떤 구독에 보냈고 응답 코드가 무엇이었고 어떤 구독을 지웠는지를 남기되 엔드포인트 URL·암호 키·VAPID 키는 남기지 않는다(security §1).
  - **문서** — `docs/RUNNING.md` "웹푸시 켜기·확인하기" 한 절(VAPID 키를 **사용자가** 만드는 명령, 확인 절차), `registry.md` 새 행·비고 확장.
- 이 패키지에서 하지 않는 것 (각 줄 끝이 "왜 안 하는가"):
  - **브리핑 생성 프롬프트·검증기 손질(요약 줄 원문 인용 금지 등)** — `app/briefing/compose.py` 는 P6-briefing 판정 근거 코드다(원칙8). 원문 노출은 이 패키지에서 **알림 본문에 요약 줄을 싣지 않는 것**(결정 B)으로 막고, 화면·응답 쪽 원문 인용 문제는 별도 FIX 후보로 남긴다.
  - **`run_briefings()`·`Notifier` Protocol·`NullNotifier` 시그니처 변경** — 결정 C 권장안이면 알림기가 발송 실패를 예외로 올리지 않으므로 고칠 필요가 없다. 바꾸면 P6-briefing 테스트의 가짜 알림기 전부가 영향을 받는다.
  - **제품 프론트 화면·PWA 서비스 워커·알림 클릭 시 브리핑 화면 열기**(P8-frontend, 원칙5 화면 3개 고정) — 확인 페이지는 제품 화면이 아니다(결정 A). 알림 클릭 동작은 P8 이 브리핑 화면을 만든 뒤 정한다.
  - **구독 해제 API·구독 목록 화면** — backlog 수용 기준은 "구독 저장" 이다. 만료 구독은 발송 결과(404/410)로 정리한다(결정 E). 해제 버튼이 필요하면 P8.
  - **스키마 v2 변경**(같은 엔드포인트 유일 제약, 발송 재시도 상태 열 등) — S3.1 이 권위다. 결정 C(iii)·F(ii) 를 고르면 `/devlog change` CR 이 먼저다.
  - **발송 재시도 큐·백오프** — 저장할 자리가 스키마에 없고 1인 제품 데모 범위를 넘는다(결정 C).
  - **SSM Parameter Store 연동·배포 HTTPS·운영에서 확인 페이지 끄기**(P9-infra, D7) — 이 패키지는 환경변수로 읽는 데까지다. 운영 도메인에서 서비스 워커·푸시는 HTTPS 가 필요하다(로컬 `localhost` 는 브라우저가 보안 컨텍스트로 취급).
  - **VAPID 키 생성·`.env` 기록을 에이전트가 하는 것** — security §1. 에이전트는 명령만 문서에 적고, 키 값은 사용자가 직접 만들어 `.env` 에 넣는다. 키 값이 출력되는 명령도 에이전트가 실행하지 않는다.
  - **실제 푸시 서비스로의 발송을 자동 테스트에서 하는 것** — 테스트는 전부 가짜 발송기로 돈다(결정 G). 실발송은 U8 에서 사용자·메인 세션만.
  - **다중 사용자·여러 기기 관리 UI, 알림 문구 다국어** — 단일 사용자 전제(P5-loop 결정 I 와 같음).
  - **고민 상담·감정 문장·인물 간(A–B) 관계, 음성, 네이티브 앱**(원칙7) — 알림 본문은 기록된 일정과 검증을 통과한 한 줄 제안뿐이다.

## 산출물 (파일 경로)

**새로 만드는 파일**

- `app/push/__init__.py` — 진입점 재export(`WebPushNotifier`·`notifier_from_env`·`save_subscription`·`build_push_payload`·`PushSender`·`FakePushSender`·trace 상수)
- `app/push/types.py` — 상태 어휘(`sent`·`partial`·`failed`·`no_subscription`·`not_configured`·`misconfigured`), trace 어휘(`PUSH_TRACE_TOOL_NAME="push"`, `STEP_PUSH_SEND="push_send"`), `SendResult`, `PushSender` Protocol, `FakePushSender`(호출 기록·응답 코드 표 주입·네트워크 0)
- `app/push/subscriptions.py` — `save_subscription(session, user_id, endpoint, keys)`(같은 사용자·같은 엔드포인트면 키 갱신), `list_subscriptions(session, user_id)`
- `app/push/payload.py` — `build_push_payload(schedule, display_name, composed, now) -> dict`(결정 B, LLM 0·DB 0 순수 함수)
- `app/push/sender.py` — `PyWebPushSender`(`pywebpush` 를 import 하는 **유일한** 모듈, 발송 함수 주입 가능)
- `app/push/notifier.py` — `WebPushNotifier`(결정 C·E·F), `notifier_from_env(session, user_id, now, env=None)`
- `app/push/devpage/index.html` · `app/push/devpage/sw.js` · `app/push/devpage/devpage.js` — 개발·확인 전용 구독 페이지(결정 A)
- `tests/test_push_settings.py` — 상수·VAPID 설정 읽기·스위치
- `tests/test_push_subscriptions.py` — 구독 저장 함수·API·검증 오류·사용자 격리
- `tests/test_push_payload.py` — 본문 규칙(결정 B)·원문 미포함·길이 상한
- `tests/test_push_notifier.py` — 발송 결과 분류·만료 정리·trace·비밀 미기록·네트워크 0
- `tests/test_push_wiring.py` — 수동·주기 두 경로가 알림기를 받는지, 키 없을 때 기존 동작
- `tests/test_push_devpage.py` — 스위치 꺼짐 404 / 켜짐 서빙

**고치는 기존 파일** (registry 에 다른 패키지 행으로 있다 — 새 행이 아니라 비고 확장)

| 파일 | 고치는 내용 | 원래 패키지 |
|------|------------|------------|
| `requirements.txt` | `pywebpush==<U1 설치 버전>` 한 줄 + Refs 주석(전이 의존성은 U1 03-log 에 기록) | P1-schema |
| `app/settings.py` | `vapid_config(env=None)`(세 이름을 읽어 모두 있으면 설정 객체, 하나도 없으면 `None`, 일부만 있으면 "반쪽" 표시 — 값은 반환만), `PUSH_TIMEOUT_SECONDS`·`PUSH_TTL_MAX_SECONDS`·`PUSH_BODY_MAX_CHARS` 코드 상수, `push_dev_page_enabled(env=None)`(비움=꺼짐, `1`/`true`=켜짐, 그 밖 값 `InvalidValue` — `briefing_scheduler_enabled()` 와 같은 규약) | P2-tools |
| `app/api/routes.py` · `app/api/schemas.py` · `app/api/deps.py` | `GET /push/vapid-public-key`, `POST /push/subscriptions`, 요청·응답 스키마, `get_notifier()` 의존성, `run_briefings_endpoint` 가 `notifier=` 를 넘기는 한 줄 | P2-tools / P5-loop / P6-briefing |
| `app/briefing/scheduler.py` | `default_run_once()` 가 같은 세션으로 `notifier_from_env(...)` 를 만들어 `run_briefings(..., notifier=...)` 에 넘기는 한 자리 | P6-briefing |
| `app/main.py` | 확인 페이지 라우트를 스위치가 켜졌을 때만 등록하는 한 자리(꺼져 있으면 경로 자체가 없다) | P2-tools |
| `.env.example` | 한 줄 `PUSH_DEV_PAGE_ENABLED=`(값 비움, 주석 "개발·확인 전용 구독 페이지, 운영에서는 비워 둔다" — 비밀 없음). 31~34행 VAPID 이름 줄은 **그대로** | 하네스(registry 38행) |
| `docs/RUNNING.md` · `docs/wiki/registry.md` | "웹푸시 켜기·확인하기" 한 절 · 행 추가/비고 확장 | — |

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 /commit)

각 단위의 완료 판정 명령은 로컬 기준 `POSTGRES_PORT=5433 .venv/bin/python -m pytest …` 이고 테스트 DB 는 `relationship_test`(FIX-006)다. **모든 자동 테스트는 실제 푸시 서비스로 아무것도 보내지 않는다** — 가짜 발송기(`FakePushSender`)를 쓰고, 푸시 테스트 파일에는 `pywebpush.webpush` 를 "불리면 실패" 로 바꿔 끼우는 픽스처를 둔다(결정 G). 테스트용 VAPID 키는 **테스트 안에서 그 자리에서 생성한 일회용 키**만 쓰고 저장소에 키 문자열을 남기지 않는다. 시간은 `ToolContext.now` 주입으로 고정한다. 출력은 `docs/wiki/packages/P7-push/evidence/<YYYYMMDD-HHMM>-<이름>.txt`. U1~U7 담당은 **backend-agent**, U8 은 **사용자·메인 세션**(실발송 = 외부 전송).

- [ ] U1 골격·의존성·설정 — [backend-agent] `pywebpush` 설치·버전 고정(`requirements.txt` 한 줄, 전이 의존성 목록을 `pip show` 출력으로 03-log 에), `app/push/__init__.py`·`types.py`(상태 어휘 6종·trace 어휘·`SendResult`·`PushSender`·`FakePushSender`), `app/settings.py` 의 `vapid_config()`·상수 3개·`push_dev_page_enabled()`, `.env.example` 한 줄. 도는 발송 코드 없음. 판정: `pytest tests/test_push_settings.py -v`(세 이름 모두/전무/일부만 → 설정·`None`·반쪽, 스위치 기본 꺼짐·`1`/`true` 켜짐·잘못된 값 `InvalidValue`, 설정 객체의 `repr` 에 개인키 값이 나오지 않음) + `python -c "import app.push"` + `git diff 608694b -- .env.example`(추가 1줄뿐, 31~34행 무변경) · 증거 `evidence/*-u1-skeleton.txt` / Refs: P7-push S3.6 R12 원칙9
- [ ] U2 구독 저장 — [backend-agent] `app/push/subscriptions.py`(`save_subscription`: `user_id`+`endpoint` 로 기존 행 조회 → 있으면 `keys` 갱신·같은 id, 없으면 새 행. `list_subscriptions`: `user_id` 조건 필수), `GET /push/vapid-public-key`(설정됨 200 `{public_key}` / 미설정·반쪽 404 `{"detail":{"code":"push_not_configured"}}`), `POST /push/subscriptions`(본문 `{endpoint, keys:{p256dh, auth}, expirationTime?}` — `endpoint` 는 `https://` 로 시작·길이 상한, 키 둘 다 비지 않은 base64url, 그 밖은 422. 응답 `{id, created}`). 엔드포인트·키는 로그에 쓰지 않는다. 판정: `pytest tests/test_push_subscriptions.py -v` · 증거 `evidence/*-u2-subscriptions.txt` / Refs: P7-push S3.1 S3.6 R12
- [ ] U3 푸시 본문 작성기 — [backend-agent] `build_push_payload(schedule, display_name, composed, now) -> {title, body, tag, schedule_id, ttl}`(결정 B 권장안: 제목 `"{display_name} · {schedule.title}"`, 본문 `"{시각(user_timezone, MM/DD HH:MM)} · 제안: {suggestion.text}"`, 제안이 없으면 `"{시각} · 브리핑이 준비됐어요"`. `composed.lines`·`pattern_sentences` 는 **읽지 않는다**. 본문 `PUSH_BODY_MAX_CHARS` 초과 시 자름. `tag = "schedule-{id}"`(같은 일정 알림은 덮어씀). `ttl` = 일정까지 남은 초를 `[60, PUSH_TTL_MAX_SECONDS]` 로 자름). LLM·DB import 없음. 판정: `pytest tests/test_push_payload.py -v` · 증거 `evidence/*-u3-payload.txt` / Refs: P7-push S3.6 원칙7
- [ ] U4 발송기·알림기 — [backend-agent] `PyWebPushSender`(`pywebpush.webpush` 를 기본값으로 받되 주입 가능, 2xx → 성공, 404/410 → `gone`, 그 밖 HTTP 오류 → `failed`(상태 코드 보존), 시간 초과·연결 오류 → `timeout`/`error`(예외 클래스 이름만), **예외를 밖으로 올리지 않는다**), `WebPushNotifier(session, user_id, sender, vapid, now)`(`notify`: 일정 소유 인물의 `display_name` 조회 → 구독 목록 → 0건이면 `no_subscription` → 구독마다 발송 → `gone` 구독 행 삭제(결정 E) → 상태 집계 `sent|partial|failed` → `push_send` trace 1행(결정 F) → 상태 문자열 반환), `notifier_from_env(session, user_id, now, env=None)`(키 없음 `NullNotifier` / 반쪽 `misconfigured` 를 돌려주는 알림기 / 전부 있으면 `WebPushNotifier` + `PyWebPushSender`). 판정: `pytest tests/test_push_notifier.py -v` · 증거 `evidence/*-u4-notifier.txt` / Refs: P7-push S3.6 S3.1 R12 원칙9
- [x] U5 두 경로 연결 — [backend-agent] `app/api/deps.py::get_notifier(session=Depends(get_session), now=Depends(get_now))`(요청과 **같은 세션**), `run_briefings_endpoint` 가 `notifier=` 를 넘김, `scheduler.default_run_once()` 가 같은 `session_scope()` 세션으로 `notifier_from_env(...)` 를 만들어 넘김. `run_briefings()`·`Notifier`·`NullNotifier` 무변경. 판정: `pytest tests/test_push_wiring.py -v` + P6-briefing 회귀 6파일(`tests/test_briefing_*.py tests/test_api_briefings.py` — 키 없는 환경에서 `push == "not_configured"` 그대로) · 증거 `evidence/*-u5-wiring.txt` / Refs: P7-push S3.6 R12
- [x] U6 개발·확인 전용 구독 페이지 — [backend-agent] `app/push/devpage/` 정적 파일 3개와 `app/main.py` 한 자리. 스위치(`PUSH_DEV_PAGE_ENABLED`)가 켜졌을 때만 `GET /push-dev/`(HTML)·`/push-dev/sw.js`(`application/javascript`, 기본 범위 `/push-dev/`)·`/push-dev/devpage.js` 를 등록한다. 페이지 기능은 ① 알림 권한 요청 ② 서비스 워커 등록 ③ `GET /push/vapid-public-key` → `pushManager.subscribe({userVisibleOnly: true, applicationServerKey})` → `POST /push/subscriptions` ④ 서비스 워커가 `push` 이벤트에서 `showNotification(title, {body, tag})` 하고 열린 페이지에 "수신 시각·`schedule_id`·`tag`" 만 전달해 **수신 기록** 줄로 표시(인물 이름·제안 문구는 페이지에 그리지 않는다). 인물·브리핑 데이터를 조회하는 화면 요소 없음. 판정: `pytest tests/test_push_devpage.py -v`(꺼짐: 세 경로 404 / 켜짐: 200·콘텐츠 타입·서비스 워커 파일에 `showNotification`·`push` 리스너 문자열 존재) · 증거 `evidence/*-u6-devpage.txt` / Refs: P7-push S3.6 원칙5
- [x] U7 수용 기준 기계 검증·문서 — [backend-agent] 아래 판정 표 1~25행 실행, 전체 회귀(`POSTGRES_PORT=5433 .venv/bin/python -m pytest -rs`, skip 0), "지킬 불변식" 절 grep 을 그 절 명령 그대로, `alembic check`(스키마 무변경), `python scripts/tools_check.py` 7/7, `git diff --stat 608694b -- app/briefing/run.py app/briefing/select.py app/briefing/inputs.py app/briefing/compose.py app/briefing/types.py app/agent app/memory app/er app/tools`(빈 출력), `docs/RUNNING.md` 한 절(VAPID 키를 사용자가 만드는 방법 — U1 에서 확인한 `pywebpush`/`py-vapid` 공식 사용법 기준, U8 확인 절차), `registry.md` 갱신. 증거 `evidence/*-u7-*.txt` / Refs: P7-push S3.6 R12 원칙8 원칙9
- [ ] U8 데스크톱 Chrome 실발송 확인 — [사용자·메인 세션] (backend-agent 아님 — 실제 푸시 서비스로의 외부 전송이고 VAPID 개인키가 필요하다.) 아래 "수동 확인 절차" 그대로. 사용자가 VAPID 키를 만들어 `.env` 에 넣고, 메인 세션이 서버 기동·DB 조회·`POST /briefings/run` 을 실행해 출력을 증거로 남기고, 사용자가 알림이 보였는지 확인 문장을 준다. 판정 표 26행. 증거 `evidence/*-u8-chrome-manual.txt` / Refs: P7-push S3.6 R12 원칙8

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- 데스크톱 Chrome에서 알림 수신

## 해석 — 수용 기준 (위 한 줄을 판정 가능한 문장으로 — 새 기준을 더하는 것이 아니다)

backlog 항목 본문 "웹푸시 (구독 저장, VAPID 발송)" 이 이 수용 기준의 수단을 정한다. 그래서 "알림 수신" 을 그 수단이 실제로 이어진 결과로 읽는다.

| # | 원문 구절 | 이 계획의 해석 |
|---|----------|--------------|
| ㄱ | (수단) 구독 저장 | 데스크톱 Chrome 이 만든 웹푸시 구독이 `POST /push/subscriptions` 로 `push_subscriptions(user_id, endpoint, keys)` 한 행으로 저장된다. `user_id = app_user_id()`, 같은 엔드포인트는 한 행 |
| ㄴ | (수단) VAPID 발송 | 브리핑이 생기면(수동 `POST /briefings/run`·1분 주기 둘 다, S3.6 "주기 작업 → `get_briefing` → 웹푸시 → `briefed_at`") `WebPushNotifier` 가 그 사용자의 구독마다 VAPID 서명·암호화 푸시를 보내고, 푸시 서비스가 2xx 로 받으면 상태 `sent`. 결과는 응답 `push`·`briefing_compose.output.push`·`push_send` trace 에 남는다(원칙9) |
| ㄷ | 데스크톱 Chrome에서 알림 수신 | 그 푸시가 데스크톱 Chrome 의 서비스 워커에 도착해(`push` 이벤트) OS 알림으로 **사람 눈에 보인다**. 알림 본문은 결정 B 규칙대로이며 사용자 원문(`raw_utterance`)·요약 줄을 담지 않는다. 이 행만은 기계로 판정할 수 없어 사람의 확인 문장 + 앞뒤 기계 증거(구독 행·발송 응답·trace·수신 기록)로 닫는다(판정 표 26행) |

## 판정 방법 (수용 기준을 기계적으로 확인하는 명령)

1~22행은 `POSTGRES_PORT=5433 .venv/bin/python -m pytest <파일>::<테스트> -v` 로 실행하고 출력 파일을 `docs/wiki/packages/P7-push/evidence/` 에 남긴다. 테스트 이름은 U 단위에서 확정하되 아래 뜻을 바꾸지 않는다. 모든 행은 **독립**이다(행마다 새 사용자·인물·일정·구독을 만든다). 발송은 전부 `FakePushSender`(응답 코드 표 주입), VAPID 키는 테스트 안에서 만든 일회용 키다. `T` = 주입한 지금.

| # | 확인할 것 | 케이스 | 기대 출력 | 위치 |
|---|----------|-------|----------|------|
| 1 | ㄱ 구독 저장 양성 | `POST /push/subscriptions` 정상 본문 | 200 `{id, created: true}`, 행 1개 `user_id == app_user_id()`·`keys == {p256dh, auth}` | test_push_subscriptions |
| 2 | ㄱ 같은 엔드포인트 | 같은 본문을 키만 바꿔 두 번 | 행 수 1 유지, 같은 `id`, `created: false`, `keys` 는 두 번째 값 | 〃 |
| 3 | ㄱ 잘못된 본문 | `endpoint` 가 `http://`·빈 문자열 / `keys.auth` 누락 | 422, 행 0 | 〃 |
| 4 | ㄱ 공개키 API | VAPID 설정됨 / 미설정 / 반쪽 | 200 `{public_key}`(설정값과 같음, 응답 본문에 개인키 값 없음) / 404 `push_not_configured` / 404 `push_not_configured` | 〃 |
| 5 | ㄱ 사용자 격리 | 다른 `user_id` 의 구독 1건 + 내 구독 1건, `list_subscriptions(my)` | 내 것 1건만 | 〃 |
| 6 | ㄴ 발송 양성(수동 경로 한 흐름) | 인물·일정 `T+3h`·구독 2, `get_notifier` 를 가짜 발송기 알림기로 오버라이드, `POST /briefings/run` | 응답 `push == "sent"`, 발송 호출 2회(구독마다 1회), 그 일정 `briefed_at == T`, `push_send` trace 1행 | test_push_wiring |
| 7 | ㄴ 주기 경로도 같은 알림기 | `default_run_once` 를 가짜 세션·`notifier_from_env` 주입으로 1회 | `run_briefings` 에 넘어간 `notifier` 가 `WebPushNotifier`(키 있음)/`NullNotifier`(키 없음) | 〃 |
| 8 | ㄴ 키 없을 때 기존 동작 | VAPID 세 이름 비움, `POST /briefings/run` | `push == "not_configured"`, 발송 호출 0, P6-briefing 판정 24행 테스트 그대로 통과 | 〃 |
| 9 | ㄴ 반쪽 설정 | 공개키만 있음 | `push == "misconfigured"`, 발송 호출 0, `briefed_at` 기록 | 〃 |
| 10 | ㄷ 본문 규칙(결정 B) | 제안 있는 `ComposedBriefing`(요약 줄 2·패턴 문장 1) | 제목 `"{display_name} · {title}"`, 본문에 시각·제안 문구 포함, **요약 줄·패턴 문장 텍스트는 어디에도 없음** | test_push_payload |
| 11 | ㄷ 제안 없음 | `suggestion=None`(템플릿 대체 등) | 본문 `"{시각} · 브리핑이 준비됐어요"` | 〃 |
| 12 | ㄷ 원문 미포함(원칙7·security) | 이벤트 `raw_utterance` 를 요약 줄에 글자 그대로 넣은 가짜 브리핑 → 6행 흐름 | 가짜 발송기가 받은 페이로드(JSON) 어디에도 그 원문 문자열 없음 | test_push_notifier |
| 13 | ㄷ 길이·TTL | 제안 80자 + 긴 일정 제목 / 일정 `T+30s`·`T+3h`·`T+30h`(수동 강제) | 본문 ≤ `PUSH_BODY_MAX_CHARS` / `ttl` = 60 · 10800 · `PUSH_TTL_MAX_SECONDS` | test_push_payload |
| 14 | 구독 0건(결정 C) | 구독 없는 사용자 | `push == "no_subscription"`, 발송 0, `briefed_at` 기록, 다음 실행에 다시 선정 안 됨 | test_push_notifier |
| 15 | 만료 구독(결정 E) | 구독 2 중 하나가 410, 하나가 201 | 410 구독 행 삭제·201 구독 행 유지, `push == "partial"`, trace `removed == [그 id]` | 〃 |
| 16 | 만료 404 도 같음 | 유일한 구독이 404 | 행 삭제, `push == "failed"`, `briefed_at` 기록 | 〃 |
| 17 | 일시 오류(결정 C) | 유일한 구독이 503 / 발송 함수가 시간 초과 예외 | 행 유지, `push == "failed"`, **`briefing_error` 0행·`briefed_at` 기록**, 생성기 호출 1회(같은 조건으로 다시 실행해도 재선정 0·생성기 추가 호출 0) | 〃 |
| 18 | 발송기 예외 매핑 | `PyWebPushSender` 에 가짜 발송 함수 주입: 정상 / HTTP 410 예외 / HTTP 500 예외 / 시간 초과 / 임의 예외 | `sent` / `gone` / `failed(500)` / `timeout` / `error(<클래스 이름>)`, 어느 경우도 예외가 밖으로 나오지 않음 | 〃 |
| 19 | 근거 기록(원칙9) | 15행 실행 후 trace | `push_send` 1행: `tool_name="push"`, input `{schedule_id, person_id, subscription_ids}`, output `{schedule_id, status, results[{subscription_id, outcome, status_code}], removed, payload{title, body}, ttl}`, tokens 0/0 | 〃 |
| 20 | 비밀 미기록(security §1) | 19행 trace output·input 과 응답 본문을 JSON 문자열로 | 테스트 구독의 `endpoint`·`p256dh`·`auth` 값, VAPID 개인키·공개키 값이 **한 번도** 나오지 않음 | 〃 |
| 21 | 네트워크 0(결정 G) | 푸시 테스트 파일 전체를 `pywebpush.webpush` "불리면 실패" 픽스처로 | 전부 통과(실제 발송 함수 호출 0) | test_push_notifier·wiring |
| 22 | 확인 페이지 스위치(결정 A) | 스위치 비움 / `1` | 꺼짐: `/push-dev/`·`/push-dev/sw.js`·`/push-dev/devpage.js` 404 / 켜짐: 200, `sw.js` 콘텐츠 타입 `application/javascript`, 파일에 `push` 리스너·`showNotification` | test_push_devpage |
| 23 | 불변식 grep | — | "지킬 불변식" 절 명령 그대로(표 안에서는 파이프 기호가 칸을 나누므로 명령을 다시 적지 않는다) — 전부 기대값 | U7 evidence |
| 24 | 무변경 | `alembic check` · `python scripts/tools_check.py` · `git diff --stat 608694b -- app/briefing/run.py app/briefing/select.py app/briefing/inputs.py app/briefing/compose.py app/briefing/types.py app/agent app/memory app/er app/tools` | "No new upgrade operations detected." · "RESULT: 7/7 ok" · 빈 출력 | U7 evidence |
| 25 | 전체 회귀 | `POSTGRES_PORT=5433 .venv/bin/python -m pytest -rs` | 실패 0·skip 0, 통과 수 ≥ 1724(FIX-017 기준선, CURRENT.md) | U7 evidence |
| 26 | **ㄷ 사람 확인 — 데스크톱 Chrome 알림 수신** | 아래 "수동 확인 절차" ①~⑧ | ③ 구독 행 1개(엔드포인트는 **호스트만**) · ⑤ 응답 `push == "sent"` · ⑥ `push_send` output `results[].status_code` 2xx · ⑦ 확인 페이지 수신 기록 줄(시각·`schedule_id`·`tag`) · ⑧ 사용자 확인 문장. 다섯 개가 전부 한 파일에 있어야 통과 | U8 evidence |

### 수동 확인 절차 (판정 표 26행 — 사용자·메인 세션, 에이전트는 실발송하지 않는다)

스크린샷 대신 **텍스트 증거**를 남긴다(저장소에 이미지 파일을 늘리지 않고, 다른 사람이 같은 명령으로 재현할 수 있게). 증거 파일 하나 `evidence/<ts>-u8-chrome-manual.txt` 에 아래 각 단계의 명령과 출력을 순서대로 붙인다. **어느 단계에서도 VAPID 키 값·구독 엔드포인트 전체 URL·`p256dh`/`auth` 값을 붙이지 않는다**(엔드포인트 URL 은 그 자체로 그 브라우저에 푸시를 보낼 수 있는 주소다).

1. (사용자) `docs/RUNNING.md` 에 적힌 방법으로 VAPID 키 한 쌍을 만들어 `.env` 에 `VAPID_PUBLIC_KEY`·`VAPID_PRIVATE_KEY`·`VAPID_SUBJECT`(본인 `mailto:`)를 넣고 `PUSH_DEV_PAGE_ENABLED=1` 을 켠다. 키가 화면에 나오는 명령은 사용자가 직접(`!`) 실행한다. 메인 세션은 존재 여부만 확인: `test -n "$VAPID_PRIVATE_KEY" && echo set`(security §1 허용 형식).
2. (메인 세션) 서버 기동(`uvicorn app.main:app --port 8000`, `localhost` — 브라우저가 보안 컨텍스트로 취급). 기동 로그 첫 줄들을 붙인다.
3. (사용자) 데스크톱 Chrome 으로 `http://localhost:8000/push-dev/` → "알림 받기" → 권한 허용 → 페이지에 `구독 저장됨 id=N` 표시. (메인 세션) `SELECT id, user_id, split_part(endpoint, '/', 3) AS host, jsonb_object_keys(keys) AS key_name, created_at FROM push_subscriptions;` 출력(호스트 예: `fcm.googleapis.com`, 키는 **이름만**).
4. (메인 세션) 확인용 일정 준비 — 개발 DB 의 기존 확인용 사용자(`brief-u5-check`, P6-briefing 04-review §6-8) 일정을 쓰거나 `POST /chat` 으로 "내일 저녁 7시에 민수랑 저녁 약속" 한 건. 그 `schedule_id` 를 적는다.
5. (메인 세션) `curl -s -X POST localhost:8000/briefings/run -H 'Content-Type: application/json' -d '{"schedule_id": N}'` 응답 전문(로컬 서버 — security §4 허용 범위). 기대: `briefings[0].push == "sent"`.
6. (메인 세션) `SELECT id, session_id, input, output FROM agent_traces WHERE tool_name='push' AND step='push_send' ORDER BY id DESC LIMIT 1;` 기대: `status = "sent"`, `results[].status_code` 2xx(푸시 서비스가 받았다는 기계 증거).
7. (사용자) 확인 페이지의 **수신 기록** 줄(서비스 워커가 `push` 이벤트에서 남긴 시각·`schedule_id`·`tag`)을 복사해 준다 — "브라우저 서비스 워커까지 도착했다" 는 증거.
8. (사용자) 확인 문장 한 줄: `사용자 확인: <시각>, Chrome <버전>(chrome://version), <OS 버전>, 데스크톱 알림 표시됨 — 제목 "<제목>"`. 알림이 안 보이면 그 사실을 그대로 적는다(아래 리스크 "OS 알림 권한" 참고 — ⑥⑦ 이 있고 ⑧ 이 없으면 "전달됨·표시 안 됨" 으로 원인을 분리해 기록한다. 원칙8: 성능 미달도 결과다).
9. (선택·권장, 부정 확인) Chrome 사이트 설정에서 알림을 "차단" 하거나 확인 페이지 구독을 해제한 뒤 ⑤ 를 다시 실행 → 응답 `push` 가 `failed`, `push_send.removed` 에 그 구독 id, ③ 의 조회 결과 0행(만료 구독 정리, 결정 E). 푸시 서비스가 해제 직후 410 을 바로 돌려주지 않을 수 있어 선택으로 둔다.
10. 끝나면 `PUSH_DEV_PAGE_ENABLED` 를 다시 비우는 것을 권장(사용자). 확인용 구독 행은 남겨도 된다(P8 확인에 재사용).

## 기존 산출물 재사용 (registry grep — 중복 구현 금지)

| 쓰는 것 | 위치(registry 행) | 어떻게 |
|--------|------------------|-------|
| `PushSubscription` 모델 | `app/db/models.py`(P1-schema `4dfaf33`, 44행) | 그대로. 열 `id, user_id, endpoint, keys(JSONB), created_at` — 새 열·제약 없음 |
| `Notifier` Protocol · `NullNotifier` | `app/briefing/types.py`(P6-briefing `e2155f9`) | `WebPushNotifier` 가 이 Protocol 을 구현한다. 키 없을 때는 `NullNotifier` 그대로 |
| `run_briefings(ctx, *, composer, notifier, …)` | `app/briefing/run.py`(P6-briefing `e037728`) | **수정 없이** `notifier=` 만 넘긴다. 세이브포인트·`briefing_compose.output.push` 기록은 이 함수가 이미 한다 |
| `default_run_once()` | `app/briefing/scheduler.py`(P6-briefing `a67692e`) | 한 자리만 고쳐 알림기를 넘긴다 |
| `get_session()`·`get_now()`·`build_briefing_ctx()`·지연 생성 규약 | `app/api/deps.py`(P6-briefing U6 `8589e37`) | `get_notifier()` 를 같은 모양으로. 테스트는 `app.dependency_overrides[get_notifier]` |
| 404 공통 매핑·`InvalidValue` 422 | `app/main.py`(P2-tools) | 새 예외 핸들러를 만들지 않는다. `push_not_configured` 는 라우트가 `HTTPException(404)` 로(P5 `resolve_session_id` 422 와 같은 방식) |
| `app_user_id()`·`user_timezone()`·스위치 읽기 규약 | `app/settings.py`(P2-tools·FIX-005·P6-briefing `briefing_scheduler_enabled`) | 구독 귀속·알림 시각 표기·확인 페이지 스위치 |
| `TRACE_MAX_STRING`·`AgentTrace` 기록 관례 | `app/tools/context.py`·`app/briefing/run.py::_record_briefing_error` | `push_send` 행 작성(오류는 예외 클래스 이름만) |
| `session_scope()` | `app/db/session.py` | 주기 작업 경로(이미 `default_run_once` 가 연다) |
| 테스트 픽스처 | `tests/conftest.py`(`db_session`·`dbtest`, FIX-006) | 그대로 |

registry 를 `push`·`PushSubscription`·`VAPID`·`static` 으로 grep 한 결과: `app/db/models.py` 행(44행, 모델만)과 L-003 문서 행(32행, git 푸시 — 무관)뿐이다. `app/push`·`test_push`·`/push/` 엔드포인트·정적 파일 서빙은 0건 — 새 모듈은 중복이 아니다. 저장소에 `frontend/`·`static/` 폴더도 없다(Glob 0건).

## 결정 항목 (사용자가 고른다 — 각 항목 권장안 표시, 확정 아님)

> **확정(사용자, 2026-10-02) — 전부 권장안**: **A(i)** 확인 전용 정적 페이지(`/push-dev/`, `PUSH_DEV_PAGE_ENABLED` 기본 꺼짐 — 원칙5 양립 여부는 verifier 판정) · **B(ii)** 알림 = 인물 이름·일정 제목 + 시각·제안 한 줄(요약 줄·패턴 문장 제외) · **C(i)** 발송 실패는 상태 문자열로만, `briefed_at` 은 항상 기록 · **D(i)** `pywebpush` 하나 버전 고정, VAPID 키는 사용자가 만들어 `.env`(값 출력 금지), 키 없으면 `NullNotifier` · **E(i)** 404/410 구독 행 삭제 + trace 에 id 만 · **F(i)** `GET /push/vapid-public-key`·`POST /push/subscriptions`, 같은 endpoint 는 키만 갱신, trace `tool_name="push"` · **G(i)** 테스트는 가짜 발송기만, 실발송은 U8. 아래 각 항목의 "권장" 이 곧 확정안이다.

### 결정 A · 브라우저 구독을 어디서 만드나 (서비스 워커를 등록할 페이지)

브라우저 구독(`PushManager.subscribe`)은 서비스 워커를 등록한 페이지에서만 만들 수 있다. 제품 프론트는 P8-frontend 몫이고 원칙5 는 화면 3개(채팅·인물 카드·브리핑) 고정이다.

| 선택지 | 무엇 | 장점 | 단점 |
|-------|------|------|------|
| **(i) 개발·확인 전용 페이지를 백엔드가 서빙(스위치 기본 꺼짐)** | `app/push/devpage/` 의 HTML 한 장 + 서비스 워커 + 스크립트. `PUSH_DEV_PAGE_ENABLED=1` 일 때만 `/push-dev/` 경로가 생긴다 | P7 수용 기준을 P7 안에서 닫는다(backlog 순서 P7 → P8 유지). 같은 출처라 CORS 설정 불필요. 새 빌드 도구 0 | 화면 비슷한 것이 하나 생긴다 — 원칙5 와 양립 근거를 verifier 가 판정해야 한다(아래). P8 이 PWA 서비스 워커를 만들면 구독을 그쪽에서 다시 만들어야 한다 |
| (ii) P8 을 먼저 하고 P7 을 그 위에 | PWA 서비스 워커에서 구독 | 확인용 코드를 버릴 일이 없다 | backlog 순서·의존(P7 의존 P6, P8 의존 P5·P6)을 뒤집는다. P8 은 frontend-agent 신설이 먼저라 P7 이 그만큼 멈춘다 |
| (iii) P7 은 백엔드만, 수용 기준은 P8 에서 닫음 | 구독 API·발송만 만들고 "Chrome 수신" 은 미판정 | 프론트 코드 0 | 수용 기준을 못 닫은 채 패키지를 끝내게 된다(04-review `완료` 불가) |
| (iv) 정적 페이지를 백엔드 밖에서(`python -m http.server` 등) 서빙 | 다른 포트의 페이지 | 백엔드에 HTML 이 안 들어간다 | 출처가 달라 CORS 허용 설정을 새로 넣어야 하고, 확인 절차가 한 단계 늘어난다 |

**권장: (i).** 원칙5 와의 양립 근거(verifier 판정 대상): ① 원칙5 는 "제품 프론트 화면" 개수를 고정하는 규칙이고, 이 페이지는 사용자가 쓰는 제품 기능이 아니라 **수용 기준을 사람이 확인하기 위한 장치**다 — 기능은 "알림 권한 요청·구독" 버튼 하나와 수신 기록 줄뿐이며 인물·사건·브리핑 자료를 조회하거나 그리지 않는다. ② 스위치 기본 꺼짐 — 꺼져 있으면 경로 자체가 등록되지 않는다(판정 22행). 운영(P9)에서는 켜지 않는다. ③ P8 인계: PWA 서비스 워커가 같은 `push` 처리(표시·`tag`)를 가져가고, 그때 이 페이지를 지울지는 P8 이 정한다. 예: 데모 당일에는 P8 의 PWA 가 구독을 만들고, 이 페이지는 개발 중 "알림이 정말 오나" 를 볼 때만 켠다.

### 결정 B · 알림 본문에 무엇을 싣나

잠금 화면·알림 센터에 뜨는 글은 옆 사람도 볼 수 있다. P6-briefing 실서버 확인에서 요약 줄이 원문("민수는 고수를 진짜 싫어하더라")을 글자 그대로 옮겼다.

- (i) 최소 — 제목 "다가오는 약속 브리핑", 본문 `"{일정 제목} · {시각}"`. 인물 이름·제안 없음. 노출 최소지만 알림만 보고는 무엇을 준비할지 알 수 없다.
- **(ii) 짧게 + 제안 한 줄** — 제목 `"{display_name} · {일정 제목}"`, 본문 `"{시각} · 제안: {suggestion.text}"`(제안 없으면 `"{시각} · 브리핑이 준비됐어요"`). **요약 줄·패턴 문장은 싣지 않는다.** 제안은 P6-briefing 검증기를 통과한 문장이다(근거 필수·한 줄·80자·금지 표현 14개 — R19). 예: "민수 · 저녁 약속 / 10/03 19:00 · 제안: 고수 없는 식당을 고르세요".
- (iii) 전부 — 요약 줄까지. 원문 인용이 알림으로 그대로 나간다(§6-3 관찰). 알림 크기 제한(수 KB)에도 걸릴 수 있다.
- (ii)+(α) — (ii) 에 더해 이 패키지에서 `compose.py` 프롬프트에 "원문 인용 금지" 를 넣는다. P6-briefing 판정 근거 코드를 바꾸는 것이라 범위가 커진다.

**권장: (ii)**, (α) 는 별도 FIX 후보(화면·응답 쪽 원문 인용은 P8 브리핑 화면에서도 같은 문제라 그때 함께). 원칙7: 알림은 기록된 일정과 사실에서 나온 행동 제안 한 줄뿐이고 감정·고민 문장은 검증기가 이미 거른다. 한계: 제안 문장도 LLM 출력이라 원문 일부를 옮길 수 있다 — 검증기는 원문 인용을 검사하지 않는다(판정 12행은 **요약 줄 경로**가 막혔음을 보일 뿐이다). 인물 이름이 알림에 뜨는 것을 원치 않으면 (i) 을 고른다.

### 결정 C · 푸시가 실패하면 `briefed_at` 을 어떻게 하나

지금 `notify` 가 예외를 내면 그 일정의 세이브포인트가 되돌려져 `briefed_at` 이 비고, 다음 분에 **브리핑을 처음부터 다시 만든다(LLM 재호출)**.

| 선택지 | 무엇 | 장점 | 단점 |
|-------|------|------|------|
| **(i) 발송 결과는 전부 상태 문자열로, `briefed_at` 은 항상 기록(알림기는 발송 실패로 예외를 올리지 않는다)** | 일시 오류(5xx·시간 초과)·영구 오류(404/410)·구독 0건 모두 `failed`/`partial`/`no_subscription` 으로 남기고 브리핑은 확정 | LLM 비용이 쌓이지 않는다. `run_briefings()` 무변경. 브리핑 자체는 trace 에 있어 P8 화면에서 볼 수 있다. 다시 보내려면 `POST /briefings/run {"schedule_id"}` | 일시 오류 한 번이면 그 일정 알림은 자동으로 다시 가지 않는다 |
| (ii) 일시 오류만 예외 → 다음 분 재시도, 영구 오류·0건은 기록 | 일시 오류 때 세이브포인트 롤백 | 네트워크가 잠깐 끊긴 경우 자동 복구 | 푸시 서비스가 오래 죽으면 **매분 LLM 1회 + `briefing_error` 1행**이 쌓인다(최악 24시간 × 60 = 1,440회/일정). 횟수 상한을 둘 저장 자리가 없다 |
| (iii) 발송 재시도 상태를 따로 저장 | `schedules.pushed_at` 같은 열이나 큐 테이블 | 브리핑과 발송을 분리해 재시도 | **스키마 변경 → CR 선행**. 1인 데모 범위를 넘는다 |

**권장: (i).** 예: 노트북 와이파이가 끊긴 순간 1분 주기가 돌았다면 그 약속의 알림은 오지 않지만, 브리핑은 남고 응답·trace 에 `push: "failed"` 와 응답 코드가 남는다. 남는 위험: 알림기 **코드 버그**(예외 매핑 밖 예외)는 여전히 `run.py` 의 격리 경로로 가서 다음 분 재시도된다 — 그래서 발송기는 모든 예외를 `error(<클래스 이름>)` 로 바꾸고(판정 18행), 알림기 자체의 DB 조회 실패만 그대로 올린다(그것은 P6 규약대로 일정 단위 격리가 맞다).

### 결정 D · 새 의존성·VAPID 키·키 없을 때 동작

- **의존성** — **(i) `pywebpush` 하나(버전 고정)**. VAPID JWT 서명과 RFC 8291 암호화(aes128gcm)를 직접 구현하지 않는다(암호 코드를 손으로 쓰지 않는다). 전이 의존성(`cryptography`·`py-vapid`·`http-ece`·HTTP 클라이언트 등)은 U1 에서 실제 설치 목록을 03-log 에 남기고, 기존 고정 버전과 충돌하면 보고하고 멈춘다. (ii) 직접 구현 — 의존성 0 이지만 암호 구현 검증 부담이 이 패키지보다 크다.
- **키 생성** — 사용자가 직접 만든다. `docs/RUNNING.md` 에 U1 에서 공식 문서로 확인한 생성 방법(설치된 `py-vapid` 의 명령 또는 짧은 파이썬 한 줄)을 적되 **키 값이 화면에 나오는 명령은 에이전트·메인 세션이 실행하지 않는다**(security §1 — 출력이 대화 기록에 남는다). 개인키는 `.env`(로컬)·SSM(배포, P9)에만. 코드·문서·`.env.example`·로그·trace·증거 파일에 값 금지.
- **키 없을 때** — **(i) 세 이름 중 공개키·개인키가 모두 비면 `NullNotifier`(`"not_configured"`) — 지금과 똑같다.** 하나만 있으면(반쪽) 발송하지 않고 상태 `"misconfigured"` 로 응답·trace 에 드러낸다(조용히 꺼진 것처럼 보이지 않게). `VAPID_SUBJECT` 가 비어 있으면 반쪽으로 본다. 앱 기동은 막지 않는다(키는 브리핑이 돌 때 지연해서 읽는다 — `get_briefing_composer()` 와 같은 규약). (ii) 반쪽 설정이면 앱 기동 실패 — 더 시끄럽지만 키를 읽는 시점이 기동으로 당겨져 리스크 A(기동 시 외부 의존 없음) 규약과 어긋난다.

**권장: 의존성 (i) · 키는 사용자 생성 · 키 없을 때 (i).**

### 결정 E · 만료 구독(404/410)을 어떻게 하나

- **(i) 그 구독 행을 앱이 삭제하고 `push_send.output.removed` 에 id 를 남긴다.** 푸시 서비스가 404/410 을 돌려주는 것은 "이 구독은 다시는 유효하지 않다" 는 뜻이라(RFC 8030) 남겨 두면 매 브리핑마다 같은 실패가 쌓인다. 이것은 제품 코드의 ORM 삭제(`session.delete(row)`)이고 훅이 막는 셸 `DELETE`/`DROP` 과 다르다(security §4 는 셸 명령 규칙). 같은 일정 세이브포인트 안이라 그 일정 처리가 다른 이유로 되돌려지면 삭제도 함께 되돌려진다.
- (ii) 행을 남기고 표시만 — 표시할 열(`revoked_at` 등)이 없어 스키마 변경(CR).
- (iii) 아무것도 안 함 — 매번 같은 410 을 다시 받는다.

**권장: (i).** 엔드포인트 URL 은 trace 에 쓰지 않으므로 지운 뒤에는 "어느 브라우저였는지" 를 trace 로 알 수 없다 — id·응답 코드만 남는다(비밀 최소화를 우선).

### 결정 F · 구독 API 모양 · 사용자 귀속 · 같은 엔드포인트 · trace 어휘

- **API**: `GET /push/vapid-public-key` → `{public_key}` / 404 `push_not_configured`. `POST /push/subscriptions` ← `{endpoint, keys:{p256dh, auth}, expirationTime?}`(브라우저 `toJSON()` 모양 그대로, `expirationTime` 은 받기만 하고 저장하지 않는다 — 열이 없다) → 200 `{id, created}`. 해제 API 는 만들지 않는다(범위). 발송 시험 전용 엔드포인트도 만들지 않는다 — 기존 `POST /briefings/run {"schedule_id"}` 가 "브리핑 → 푸시" 를 그대로 재현한다.
- **사용자 귀속**: `user_id = app_user_id()`(단일 사용자, `build_chat_ctx()` 와 같음). 구독 조회는 항상 `user_id` 조건(security §5).
- **같은 엔드포인트**: **(i) 앱에서 `(user_id, endpoint)` 로 조회 후 있으면 `keys` 만 갱신** — 스키마 무변경. 한계: 동시에 같은 구독을 두 번 보내면 행이 둘 생길 수 있다(유일 제약이 없다) — 단일 사용자·버튼 한 번이라 실제 피해가 작고, 둘이 생겨도 발송은 중복 알림이 `tag` 로 하나로 합쳐진다. (ii) `(user_id, endpoint)` 유일 인덱스 마이그레이션 — S3.1 은 열만 정의하지만 `alembic check` 가 바뀌는 스키마 변경이라 CR 여부를 verifier 가 판정해야 한다.
- **trace 어휘**: `tool_name = "push"`(`"agent"`·`"er"`·`"memory"`·`"briefing"` 과 같은 층위), step `push_send` 1종, 일정 발송 1회당 1행. `session_id = "push:<uuid4>"` — `Notifier.notify(schedule, composed)` 는 실행의 `session_id` 를 받지 않으므로(Protocol 무변경) **`input.schedule_id` 로 같은 일정의 `briefing_compose` 행과 잇는다**. 구독 저장 API 는 판정이 아니므로 trace 를 남기지 않는다(`GET /health` 와 같은 이유). 응답 `push` 는 계속 상태 문자열 하나(P6 응답 스키마 `push: str` 무변경).
  - 대안 (F-2): `Notifier.notify` 에 `session_id` 키워드를 더해 같은 실행 `session_id` 로 묶는다 — 원칙9 재생은 더 쉬워지지만 `run.py`·`types.py`·P6 테스트의 가짜 알림기들을 고쳐야 한다(가짜가 새 인자를 받지 못하면 `stage="notify"` 오류로 바뀐다).

**권장: API 위 모양 · 귀속 `app_user_id()` · 같은 엔드포인트 (i) · trace `push`/`push_send` + `schedule_id` 연결(F-2 아님).**

### 결정 G · 테스트 방법 (외부 전송 0)

- **(i) 발송기를 Protocol 로 분리하고 테스트는 `FakePushSender`(응답 코드 표 주입·호출 기록)만 쓴다.** 실제 발송기(`PyWebPushSender`)의 예외 매핑은 **발송 함수 자체를 주입**해 시험한다(판정 18행) — `pywebpush` 의 HTTP 클라이언트까지 내려가지 않는다. 푸시 테스트 파일에는 `pywebpush.webpush` 를 "불리면 즉시 실패" 로 바꿔 끼우는 픽스처를 둬서, 실수로 실제 경로를 타면 테스트가 깨진다(판정 21행). VAPID 키는 테스트 안에서 그 자리에서 만든 일회용 키(저장소에 키 문자열 0).
- (ii) 로컬 가짜 푸시 서버(HTTP)를 띄워 실제 `pywebpush` 로 보낸다 — 암호화까지 끝에서 끝으로 돌지만 테스트에 서버 수명 관리가 들어가고 이 패키지 수용 기준(Chrome 수신)을 대신하지 못한다.
- 실발송은 **U8 에서만**, 사용자 키로, 메인 세션·사용자가 실행한다. 자동 테스트·backend-agent 는 실제 푸시 서비스로 보내지 않는다.

**권장: (i).**

## 지킬 불변식 (수용 기준 밖)

- **`pywebpush` 는 한 모듈에서만 import.** `grep -rln "pywebpush" app/` → `app/push/sender.py` 한 줄.
- **키 값 없음.** `grep -rnE "VAPID_PRIVATE_KEY *= *[A-Za-z0-9_-]{20,}" . --include=*.py --include=*.md --include=*.js --include=*.html --include=.env.example` → 0건. `git diff 608694b -- .env.example` → 추가 1줄(`PUSH_DEV_PAGE_ENABLED=`)과 그 주석뿐, 31~34행 무변경.
- **엔드포인트·키를 로그에 쓰지 않는다.** `grep -rnE "logger\.[a-z]+\(.*(endpoint|p256dh|auth|keys|vapid)" app/push/ app/api/` → 0건. 권위 있는 판정은 판정 표 20행.
- **P6-briefing 판정 근거 코드 무변경.** 판정 표 24행 diff 빈 출력(`run.py`·`select.py`·`inputs.py`·`compose.py`·`types.py`).
- **스키마 무변경.** `alembic check` → "No new upgrade operations detected."(결정 C(iii)·E(ii)·F(ii) 를 고르지 않는 한).
- **원문을 알림기에 넘기지 않는다.** `grep -rn "raw_utterance" app/push/` → 0건(주석 포함 — 설명이 필요하면 "원문" 으로 쓴다). 권위 있는 판정은 판정 표 12행.
- **확인 페이지는 인물·브리핑 자료를 조회하지 않는다.** `grep -nE "/chat|/briefings|/persons|/answers" app/push/devpage/*.js app/push/devpage/*.html` → 0건.
- `app/push/` docstring·주석에 "evaluation" 금지: `grep -rn "evaluation" app/push/` → 0건.

## 리스크 · 미결

- **OS 알림 권한(사람 확인 단계)** — macOS 는 "시스템 설정 → 알림 → Google Chrome" 이 꺼져 있거나 집중 모드면 푸시가 **도착해도 화면에 안 보인다**. 그래서 판정 26행은 ⑥(푸시 서비스 2xx)·⑦(서비스 워커 수신 기록)·⑧(사람 눈)을 나눠 남긴다 — 어디서 끊겼는지 구분된다. Chrome 이 완전히 꺼져 있으면 데스크톱 Chrome 은 푸시를 받지 못한다(TTL 안에 켜지면 받는다).
- **발송이 DB 잠금을 쥔 채 네트워크를 탄다** — `notify` 는 `SKIP LOCKED` 로 잡은 일정 행·세이브포인트 안에서 불린다(P6 구조). 시간 초과 `PUSH_TIMEOUT_SECONDS`(권장 10초)×구독 수만큼 그 일정 행 잠금이 길어진다. 단일 사용자·구독 몇 개라 실제 피해는 작고, 같은 1분 안의 수동 지정 요청이 404 를 볼 수 있는 기존 문제(P6-briefing 04-review §6-6)가 조금 커진다.
- **알림 클릭 동작 없음** — P8 브리핑 화면이 생기기 전이라 클릭해도 확인 페이지에 포커스할 뿐이다. P8 인계.
- **원문 인용(결정 B 한계)** — 알림 본문에서 요약 줄을 빼도 제안 문장에 원문 조각이 섞일 수 있다. 측정은 P10-final-eval 표본 점검, 근본 해결(프롬프트·검증기)은 FIX 후보.
- **확인 페이지와 원칙5(결정 A)** — verifier 가 "제품 화면이 아니다" 라는 근거를 받아들이지 않으면 결정 A 는 (iii)(수용 기준을 P8 에서 닫음)으로 바뀌고 이 계획의 U6·U8 이 P8 로 밀린다.
- **`pywebpush` 전이 의존성** — HTTP 클라이언트·암호 라이브러리가 함께 들어온다. 이미 고정된 `openai`·`anthropic`·`google-genai` 의 의존성과 버전이 겹치면 U1 에서 멈추고 보고한다.
- **같은 엔드포인트 경쟁(결정 F(i))** — 유일 제약이 없어 동시 요청에서 중복 행이 생길 수 있다. 결과는 중복 발송(같은 `tag` 라 화면에는 하나).
- **운영 HTTPS(D7, P9-infra)** — 서비스 워커·푸시 구독은 보안 컨텍스트가 필요하다. 로컬 `localhost` 는 예외로 허용되지만 배포 도메인은 CloudFront·Caddy HTTPS 가 전제다. VAPID 키를 SSM 에서 읽는 것도 P9.
- **실 키·실 Chrome 이 있어야 닫힌다** — U8 은 사용자 시간이 필요하다. 그 전까지 이 패키지는 "기계 판정 25행 통과·사람 확인 대기" 상태로 04-review 에 올라갈 수 없다.
- **미결(사용자 결정 필요)**: 결정 A~G 전부(권장안만 표시). 범위가 크게 갈리는 것은 **A(확인 페이지 — 원칙5)·B(알림 본문 — 원문 노출)·C(실패 시 `briefed_at` — LLM 비용)** 셋이다.

## 후행 패키지가 이 패키지에서 기대하는 것

- **P8-frontend**: 구독 API(`GET /push/vapid-public-key`·`POST /push/subscriptions`)를 PWA 서비스 워커에서 그대로 쓴다. 서비스 워커의 `push` 처리(제목·본문·`tag` 표시)는 `app/push/devpage/sw.js` 를 옮겨 쓰고 알림 클릭 시 브리핑 화면 열기를 더한다. 확인 페이지를 지울지 정한다. 응답 `briefings[].push` 상태 어휘 6종.
- **P9-infra**: VAPID 세 값을 SSM 에서 환경변수로 주입, `PUSH_DEV_PAGE_ENABLED` 는 운영에서 비움, HTTPS(D7).
- **P10-final-eval**: 알림 본문(`push_send.output.payload`)에 원문 조각이 섞인 비율 표본 점검.

## 읽은 카드

- `docs/wiki/templates/plan.md` 전문(형식)
- `docs/wiki/specs/S3.6-briefing-push.md` 전문, `docs/wiki/specs/S3.1-schema-v2.md`(`push_subscriptions` 행만 grep — 13행)
- `docs/wiki/decisions/D07-tls-caddy.md` 1~7행(결정·적용 시점 P9-infra)
- `docs/wiki/review-index.md` R12 행(grep, 20행), `docs/wiki/INDEX.md` 전문(패키지 표·태그 어휘), `docs/wiki/CURRENT.md` 전문(FIX-017 회귀 기준선 1724), `docs/backlog.md` 절 제목·P7·P8 행(grep, 82~88행)
- `docs/wiki/security.md` 전문(§1 비밀·§4 외부 전송·§5 VAPID 개인키)
- `docs/wiki/registry.md` grep(`push|푸시|VAPID|PushSubscription|static|StaticFiles`) — 32·44·153·196행
- `docs/wiki/packages/P6-briefing/04-review.md` 전문(§6·§7 인계), `docs/wiki/packages/P6-briefing/01-plan.md` 전문(형식·결정 J·"하지 않는 것" 웹푸시 줄), `docs/wiki/packages/P6-briefing/03-log.md` grep(`원문|고수|P7|notify|Notifier` — U4 관찰 ③④, U6 관찰 127행, U8 인계 176행)
- `.claude/gitlog.md`(2026-10-02 20:54 스냅샷), `.claude/scripts/verify-plan.sh` 전문(형식 요건 — 수용 기준 절의 `- ` 줄·산출물 절 경로·`의존:` 줄)
- 코드 읽기(쓰지 않음): `app/briefing/types.py` 전문(`Notifier`·`NullNotifier`), `app/briefing/run.py` 전문(notify 호출 자리 218행·세이브포인트·예외 격리), `app/briefing/scheduler.py` 전문(`default_run_once`), `app/api/routes.py` 전문, `app/api/deps.py` 전문, `app/main.py` 함수 목록(grep), `app/db/models.py` `Person`(87~106행)·`Schedule`(194~205행)·`PushSubscription`(grep), `alembic/versions/0001_schema_v2.py` `push_subscriptions`(grep — 유일 제약 없음 확인), `.env.example` 전문(31~34행 VAPID 이름 줄), `requirements.txt` 전문(푸시 의존성 없음 확인)
- 열지 않은 것: `docs/resolution-plan.md` §3.6 원문(S3.6 카드가 요약), `docs/proposal.md`, D7 외 D 카드(이 패키지가 기대는 결정 카드 없음)
