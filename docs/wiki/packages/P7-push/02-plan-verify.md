# P7-push · 계획 검증 (02-plan-verify)

대상: 01-plan.md | 검증자: verifier (fable) — 계획 작성자와 다른 모델·컨텍스트(L-002) | 날짜: 2026-10-02

## 1. 기계 검증 출력 (그대로 붙인다 — 요약 금지)
명령: `bash .claude/scripts/verify-plan.sh P7-push | tee docs/wiki/packages/P7-push/evidence/20261002-2119-verify-plan.txt` (1차 — 이 문서를 쓰기 전. "02-plan-verify 없음" FAIL 1 은 그 시점에 정상)
```
== verify-plan P7-push  (2026-10-02 21:19) ==
PASS  존재: docs/wiki/packages/P7-push/01-plan.md
FAIL  없음: docs/wiki/packages/P7-push/02-plan-verify.md
PASS  카드 존재: D7
PASS  패키지 id 등록됨: P1-schema
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P7-push
PASS  패키지 id 등록됨: P8-frontend
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R12
PASS  검증 항목 존재: R19
PASS  Refs 있음: - [ ] U1 골격·의존성·설정 — [backend-agent] `pywebpush` 설치·버전 고정(`r
PASS  Refs 있음: - [ ] U2 구독 저장 — [backend-agent] `app/push/subscriptions.py`
PASS  Refs 있음: - [ ] U3 푸시 본문 작성기 — [backend-agent] `build_push_payload(sch
PASS  Refs 있음: - [ ] U4 발송기·알림기 — [backend-agent] `PyWebPushSender`(`pywebp
PASS  Refs 있음: - [ ] U5 두 경로 연결 — [backend-agent] `app/api/deps.py::get_not
PASS  Refs 있음: - [ ] U6 개발·확인 전용 구독 페이지 — [backend-agent] `app/push/devpage
PASS  Refs 있음: - [ ] U7 수용 기준 기계 검증·문서 — [backend-agent] 아래 판정 표 1~25행 실행, 
PASS  Refs 있음: - [ ] U8 데스크톱 Chrome 실발송 확인 — [사용자·메인 세션] (backend-agent 아님 
PASS  backlog 일치: 데스크톱 Chrome에서 알림 수신
PASS  의존 완료: P6-briefing
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  registry 중복 없음: app/push/__init__.py
PASS  registry 중복 없음: app/push/types.py
PASS  registry 중복 없음: app/push/subscriptions.py
PASS  registry 중복 없음: app/push/payload.py
PASS  registry 중복 없음: app/push/sender.py
PASS  registry 중복 없음: app/push/notifier.py
PASS  registry 중복 없음: app/push/devpage/index.html
PASS  registry 중복 없음: app/push/devpage/sw.js
PASS  registry 중복 없음: app/push/devpage/devpage.js
PASS  registry 중복 없음: tests/test_push_settings.py
PASS  registry 중복 없음: tests/test_push_subscriptions.py
PASS  registry 중복 없음: tests/test_push_payload.py
PASS  registry 중복 없음: tests/test_push_notifier.py
PASS  registry 중복 없음: tests/test_push_wiring.py
PASS  registry 중복 없음: tests/test_push_devpage.py
== 결과: FAIL=1 WARN=0 ==
```
이전 실행(architect 작성 직후, 메인 세션): `evidence/20261002-2112-verify-plan.txt` — 같은 내용, FAIL=1(02 없음) WARN=0.

2차 — 이 문서를 쓴 뒤 다시 실행: 아래 "1-2. 기계 검증 2차 출력" 절.

FAIL 이 하나라도 있으면 아래 결과는 통과가 될 수 없다. FAIL/WARN 은 `python .claude/scripts/findings.py <id> evidence/<ts>-verify-plan.txt --source verify-plan` 으로 05-remediation.md 에 소견으로 올리고, 조치 후 다시 실행한다. (1차의 FAIL 1 은 이 문서의 부재 자체이므로 소견으로 올리지 않는다 — 2차에서 해소를 확인한다.)

### 1-1. git log (근거 해시 — `bash .claude/scripts/gitlog.sh P7-push R12 S3.6`, 2026-10-02 21:16)
- 브랜치: `dev2` HEAD `608694b`(FIX-017) = origin/dev2 · `dev` = `f9500fe`(P6-briefing 완료 처리) · `main` = `f05d017`. 01-plan 7~8행의 해시와 일치. **시작 해시 `608694b`** 확인.
- 태그 `P7-push` grep: `7c94aad`(2026-09-05, P2-tools U7 `get_briefing`) 1건 — P2 커밋 메시지가 P7-push 를 인계로 언급한 것이지 P7 작업 단위가 아니다. 01-plan 9행 "스냅샷에서 확인되지 않는다" 는 `.claude/gitlog.md` 의 최근 20건 기준 서술이라 틀린 말은 아니나, U1 03-log 에 이 1건을 "P7 단위 아님" 으로 적어 두는 편이 좋다(R-5).
- 태그 `R12`: `688c4a4`·`e2155f9`·`db3c645`·`e037728`·`8589e37`·`a67692e`·`e2cca80`·`f9500fe`(전부 P6-briefing). 태그 `S3.6`: 위 + `cfb55ea`·`a2f032d`·`7c94aad`. 01-plan 7행의 P6 단위 해시 8개(U1~U8)와 전부 일치.
- 미커밋 변경(검증 시점 `git status`): `docs/wiki/HANDOFF.md`·`docs/wiki/journal.md` 수정, `docs/wiki/packages/P7-push/` 미추적. 제품 코드 변경 0 — 01-plan 8행 "제품 코드는 0" 과 일치.

## 2. 정합성 점검표 (기준: `.claude/skills/devlog/SKILL.md` "정합성 점검표")
근거 열에는 **카드 파일명 + 인용 문장**을 쓴다. "확인함" 같은 문구는 빈 것으로 간주한다.

| # | 항목 | 결과 | 근거(카드·절·인용) |
|---|------|------|--------------------|
| 1 | 범위 — 기획서 2장 제외 목록(상담·A–B·음성·네이티브·페르소나·태그 필터) 침범 없음 | 통과 | `docs/proposal.md` 2장 표 "제외 (의도적): 고민 상담 기능 / 인물 간(A–B) 관계 저장 / 관계 태그 필터링 / 상담 페르소나·톤 설정 / 음성 입력 / 네이티브 앱", 포함 열 "반응형 웹 + PWA"·"만남 전 브리핑 생성"; 같은 문서 "되는 것 / 안 되는 것" 표 "❌ iOS 푸시 알림 (조건부만)", 9장 리스크 "iOS 웹푸시 제약 … 데모는 안드로이드/데스크톱". 01-plan "하지 않는 것" 마지막 줄 "고민 상담·감정 문장·인물 간(A–B) 관계, 음성, 네이티브 앱(원칙7) — 알림 본문은 기록된 일정과 검증을 통과한 한 줄 제안뿐이다"; 결정 B(ii) "요약 줄·패턴 문장은 싣지 않는다"; 수용 기준 대상이 "데스크톱 Chrome"(iOS 아님). 알림 본문 = `display_name`·`schedule.title`·시각·`suggestion.text` 뿐이고 제안은 P6 검증기(`BRIEFING_FORBIDDEN_EXPRESSIONS` 14개, `app/briefing/compose.py`)를 통과한 문장 — 제외 항목 6개 어느 것도 들어오지 않는다. 확인 페이지(결정 A)는 "관계 태그 필터"·"상담" 같은 제품 기능이 아니다(2행 원칙5 판정 참조) |
| 2 | 불변 원칙 1~9 위반 없음 | 통과 | `CLAUDE.md` 원칙5 "프론트 화면은 3개로 고정: 채팅 / 인물 카드 / 브리핑. UI에 시간을 쓰지 않는다" — **결정 A(i) 판정: 양립(해석), CR 불필요.** 근거: ① 원칙5 와 `docs/proposal.md` "화면은 셋입니다" 는 **제품 프론트(React+PWA, S3+CloudFront)** 의 화면 수를 고정하는 규칙이다. `/push-dev/` 는 백엔드가 서빙하는 확인용 정적 파일 3개로, 01-plan U6 "인물·브리핑 데이터를 조회하는 화면 요소 없음", 불변식 "`grep -nE "/chat∣/briefings∣/persons∣/answers" app/push/devpage/*` → 0건"(∣ 는 파이프) — 제품 자료를 그리지 않으므로 `scripts/tools_check.py` 와 같은 **검증 도구**다. ② "스위치(`PUSH_DEV_PAGE_ENABLED`)가 켜졌을 때만 … 등록한다(꺼져 있으면 경로 자체가 없다)"(산출물 표 `app/main.py` 행, 판정 22행), "후행 패키지 … P9-infra: `PUSH_DEV_PAGE_ENABLED` 는 운영에서 비움" — 운영 화면이 아니다. ③ `.claude/skills/devlog/SKILL.md` 가 CR 조건으로 두는 것은 "기획서가 바뀔 때" 인데 기획서 2장·"화면은 셋입니다" 본문은 바뀌지 않는다(P6-briefing 02-plan-verify H-2 와 같은 "카드 보충 수준" 판단). 단, 양립은 위 ①②③ 세 조건이 **코드로 유지될 때만** 성립한다 — 확인 페이지에 인물·브리핑 조회가 들어오거나 제품 화면에서 링크되거나 운영에서 켜지면 그 순간 원칙5 위반이 되므로 04-review 에서 불변식 grep·판정 22행을 반드시 증거로 받는다. 원칙7: 위 1행. 원칙8: 판정 표 1~25행이 명령·기대값으로 적혀 있고 26행은 ⑥(푸시 서비스 2xx)·⑦(서비스 워커 수신 기록)·⑧(사람 확인)으로 **끊긴 지점을 분리**해 기록하며 "알림이 안 보이면 그 사실을 그대로 적는다 … 원칙8: 성능 미달도 결과다"(수동 확인 절차 ⑧) — `docs/wiki/verification.md` "증거로 인정하는 것" 표(명령 재현 출력·SQL 조회+결과 행·trace 행·파일 경로)에 ③⑤⑥ 이 들어가고, ⑧ 단독으로는 "인정하지 않는 것('정상 동작 확인')" 에 해당하나 계획이 "다섯 개가 전부 한 파일에 있어야 통과" 로 ⑧ 단독 통과를 막았다 → 통과(R-4·R-9 참고). 원칙9: 결정 F "trace `tool_name = "push"` … step `push_send` 1종, 일정 발송 1회당 1행", 판정 19행 "input `{schedule_id, person_id, subscription_ids}`, output `{schedule_id, status, results[…], removed, payload{title, body}, ttl}`, tokens 0/0" — `CLAUDE.md` 원칙9 "step·입력·출력·툴·토큰(in/out)" 전부 있음. 원칙1~4·6 은 ER·패턴을 건드리지 않아 해당 없음(판정 24행 `scripts/tools_check.py` 7/7·`app/er app/memory` diff 빈 출력으로 확인) |
| 3 | 인용한 D 카드의 "코드에서 지켜야 할 것"과 충돌 없음 | 통과 | 01-plan 4행 "기대는 결정: 없음(D7 은 배포 HTTPS — 운영 푸시의 보안 컨텍스트 조건으로 P9-infra 에 넘긴다)". `docs/wiki/decisions/D07-tls-caddy.md` "**적용 시점** P9-infra." — 이 패키지가 D7 코드를 쓸 일이 없고, 01-plan "하지 않는 것" 에 "SSM Parameter Store 연동·배포 HTTPS·운영에서 확인 페이지 끄기(P9-infra, D7)" 로 명시. 리스크 "운영 HTTPS(D7, P9-infra) — 로컬 `localhost` 는 예외로 허용되지만 배포 도메인은 CloudFront·Caddy HTTPS 가 전제" 는 D7 과 같은 방향. 그 밖에 인용한 D 카드 없음(D12·D13·D14 는 ER·패턴 — 이 패키지 diff 범위 밖) |
| 4 | S 카드와 일치 (스키마·시그니처 v2, 임계치 2개, ask_user 비동기) | 통과 | `docs/wiki/specs/S3.1-schema-v2.md` 13행 "`push_subscriptions(id, user_id, endpoint, keys, created_at)`" = `app/db/models.py` 235~244행 `PushSubscription`(`id, user_id, endpoint, keys(JSONB), created_at`) = `alembic/versions/0001_schema_v2.py` 148~160행(PK 만, 유일 제약 없음 — 01-plan 결정 F(i) "유일 제약이 없다" 사실과 일치). 01-plan 결정 F "`expirationTime` 은 받기만 하고 저장하지 않는다 — 열이 없다", "하지 않는 것: 스키마 v2 변경 … S3.1 이 권위다", 판정 24행 "`alembic check` → No new upgrade operations detected." — 스키마 무변경. `docs/wiki/specs/S3.6-briefing-push.md` 5행 "주기 작업(컨테이너 내, 1분): … → `get_briefing` → 웹푸시 → `briefed_at`", 9행 "푸시 구독은 `push_subscriptions`. VAPID 키는 SSM/환경변수, 코드·저장소에 두지 않는다" — 01-plan 목표가 이 두 문장을 글자 그대로 인용하고, 결정 D "개인키는 `.env`(로컬)·SSM(배포, P9)에만. 코드·문서·`.env.example`·로그·trace·증거 파일에 값 금지", 불변식 "`grep -rnE "VAPID_PRIVATE_KEY *= *[A-Za-z0-9_-]{20,}" …` → 0건" 으로 집행. `docs/wiki/specs/S3.2-tools-v2.md` 툴 7종 시그니처(`get_briefing (person_id, schedule_id?) → Briefing`, `ask_user … D2 비동기. 독립 툴 유지`) — 이 패키지는 툴을 고치지 않고 `WebPushNotifier` 는 툴이 아니라 `app/briefing/types.py` 264~272행 `Notifier` Protocol(`notify(self, schedule: Any, composed: ComposedBriefing) -> str`) 구현체다. 판정 24행 `python scripts/tools_check.py` "RESULT: 7/7 ok" 로 시그니처 불변 확인. 임계치 2개·ask_user 비동기는 `app/er`·`app/agent` 무변경(판정 24행 diff 빈 출력)이라 해당 없음. **코드 직접 확인(위임 항목 4)**: `app/briefing/run.py` 197행 `with run_ctx.session.begin_nested():` 안 217~218행 `stage = _STAGE_NOTIFY` / `push_status = notifier.notify(schedule, composed)`, 251행 `"push": push_status` 로 trace 에 실림, 283~289행 `except Exception` 이 세이브포인트 롤백 뒤 `_record_briefing_error(stage=…)` — 알림기가 예외를 올리지 않으면(결정 C(i)) `briefed_at`(`build_briefing_input` 이 기록)이 그대로 남고 `run.py` 를 고칠 필요가 없다는 01-plan 주장이 코드와 맞는다. `app/briefing/scheduler.py` 98행 `run_briefings(ctx, composer=composer_from_env(), trigger="scheduler")`, `app/api/routes.py` 349행 `run_briefings(ctx, composer=composer, schedule_id=schedule_id, trigger="manual")` — 둘 다 `notifier=` 를 넘기지 않아 기본 `NullNotifier()`(`run.py` 170행)가 쓰인다는 01-plan 10행 ④ 와 일치 |
| 5 | 의존성 순서 — 선행 P 완료, P4 게이트 | 통과 | `docs/backlog.md` 84행 "웹푸시 (구독 저장, VAPID 발송) / 의존: P6 / 수용기준: 데스크톱 Chrome에서 알림 수신". `docs/wiki/packages/P6-briefing/04-review.md` 267행 "결과: 완료", 완료 처리 커밋 `f9500fe`(gitlog "docs(P6-briefing): 브리핑 패키지를 완료로 닫는다"), 단위 커밋 `e2155f9`~`e2cca80` 8개(1-1절). P4 게이트: 기계 검증 "PASS P4 게이트 통과 (P4b-er-redesign)", `docs/wiki/CURRENT.md` "P4b-er-redesign 완료(2026-09-23, verifier 04-review `완료`, 사용자 승인) … P5 착수 가능". 01-plan 5행 "의존: P6-briefing(04-review `결과: 완료`, 완료 처리 `f9500fe`) · 선행 게이트 P4b-er-redesign(04-review `결과: 완료`)" 과 일치. `CURRENT.md` "active: none / frozen: none" — 동결 없음, 활성 패키지 없음. P6 04-review §7 "푸시 자리(P7): `Notifier.notify(schedule: app.db.models.Schedule, composed: ComposedBriefing) -> str` … `briefed_at` 을 푸시 실패 시 남길지는 P7 결정" 을 결정 C 가 받았고, §6-3 "요약 줄이 `raw_utterance` 원문을 글자 그대로 옮긴다 … 푸시 본문에 실리기 전에 P7 이 … 정한다" 를 결정 B(ii)·판정 12행이 받았다 |
| 6 | 수용 기준이 backlog 와 글자 그대로 동일 | 통과 | `docs/backlog.md` 84행 "수용기준: 데스크톱 Chrome에서 알림 수신" = 01-plan "## 수용 기준" 절 "- 데스크톱 Chrome에서 알림 수신"(기계 검증 "PASS backlog 일치: 데스크톱 Chrome에서 알림 수신"). "해석" 표 ㄱ·ㄴ·ㄷ 는 backlog 본문 "웹푸시 (구독 저장, VAPID 발송)" 의 수단 두 개 + 결과 한 개로 나눈 것이고 새 기준을 더하지 않았다(01-plan "새 기준을 더하는 것이 아니다") |
| 7 | 작업 단위마다 Refs 태그 | 통과 | 기계 검증 "PASS Refs 있음" U1~U8 8줄. U1 `P7-push S3.6 R12 원칙9` · U2 `P7-push S3.1 S3.6 R12` · U3 `P7-push S3.6 원칙7` · U4 `P7-push S3.6 S3.1 R12 원칙9` · U5 `P7-push S3.6 R12` · U6 `P7-push S3.6 원칙5` · U7 `P7-push S3.6 R12 원칙8 원칙9` · U8 `P7-push S3.6 R12 원칙8`. `docs/wiki/review-index.md` 20행 "R12 … 구현완료(절반 — 브리핑 트리거: P6-briefing e2155f9…e2cca80 … 푸시 구독 저장·발송은 P7-push) … S3.6 → P6-briefing, P7-push" — 태그 R12·S3.6 이 이 패키지의 것이고 1-1절 `git log --grep R12` 8건이 전부 P6 커밋이므로 P7 단위 커밋이 들어가면 역추적이 이어진다. 단위마다 담당·판정 명령·증거 파일 이름이 있다. 크기: U4(발송기+알림기+`notifier_from_env`, 판정 14~21행)가 가장 크지만 한 모듈 묶음이라 커밋 하나로 설명 가능 |
| 8 | 보안 카드(`security.md`) — 비밀·외부 전송·삭제 규칙 위반 없음 | 통과 | **비밀** — `docs/wiki/security.md` §1 "`.env` … 에이전트가 읽지도 쓰지도 않는다 / 사용자가 직접 만든다. 에이전트는 `.env.example`에 이름만 적는다", "KEY/SECRET 변수 echo 금지 / 존재 여부만: `test -n "$OPENAI_API_KEY" && echo set` 는 허용", "로그·trace에 키·비밀을 남기지 않는다". 01-plan: "하지 않는 것: VAPID 키 생성·`.env` 기록을 에이전트가 하는 것 — security §1 … 키 값이 출력되는 명령도 에이전트가 실행하지 않는다", 수동 절차 ① "메인 세션은 존재 여부만 확인: `test -n "$VAPID_PRIVATE_KEY" && echo set`", `.env.example` 변경은 "`PUSH_DEV_PAGE_ENABLED=`(값 비움) … 31~34행 VAPID 이름 줄은 그대로"(현재 `.env.example` 31~34행 `VAPID_PUBLIC_KEY=`·`VAPID_PRIVATE_KEY=`·`VAPID_SUBJECT=mailto:you@example.com` 확인), 테스트 키는 "테스트 안에서 그 자리에서 생성한 일회용 키", trace·응답·증거에서 엔드포인트·`p256dh`·`auth`·VAPID 값 금지(판정 20행, 수동 절차 "어느 단계에서도 … 붙이지 않는다", ③ SQL 은 `split_part(endpoint,'/',3)` 호스트·`jsonb_object_keys(keys)` 이름만), 결정 E "엔드포인트 URL 은 trace 에 쓰지 않으므로 … id·응답 코드만", 발송기 오류는 "예외 클래스 이름만"(판정 18행 — `WebPushException` 메시지에 엔드포인트·응답 본문이 섞이는 것을 막는다, R-8). §5 "웹푸시 VAPID 개인키는 환경변수/SSM. 프론트에는 공개키만" = `GET /push/vapid-public-key` 가 `{public_key}` 만(판정 4행 "응답 본문에 개인키 값 없음"). **외부 전송** — §4 "로컬 서버 이외로 데이터 전송(`curl -d/-F/-T`, `scp`, `rclone`) 금지 / 외부 API 호출은 코드(SDK)로, 키는 환경변수": 자동 테스트는 "모든 자동 테스트는 실제 푸시 서비스로 아무것도 보내지 않는다"(결정 G, 판정 21행 "`pywebpush.webpush` 불리면 실패 픽스처"), 실발송은 서버 프로세스가 `pywebpush`(SDK)로 환경변수 키를 써서 보내고, 메인 세션의 명령은 `curl -s -X POST localhost:8000/briefings/run …`(로컬 서버 — §4 허용) 뿐이다. U8 담당을 "사용자·메인 세션" 으로 두어 backend-agent 가 외부 전송을 하지 않는다. **삭제** — 결정 E(i) "제품 코드의 ORM 삭제(`session.delete(row)`)이고 훅이 막는 셸 `DELETE`/`DROP` 과 다르다": `.claude/hooks/safety-guard.sh` 129행이 막는 것은 `drop (database∣schema∣table∣extension)`·`truncate table` 셸 명령뿐이고 `secret-guard.sh` 에 delete 패턴 없음(grep 0건); `security.md` §5 는 오히려 제품 코드의 "인물 단위 완전 삭제 API(`DELETE /persons/{id}` → CASCADE)" 를 요구한다 — 앱 ORM 삭제는 규정과 충돌하지 않는다. 수동 절차 ⑨·⑩ 에 셸 DELETE 없음("확인용 구독 행은 남겨도 된다"). §3 재귀 삭제·§2 git 규칙에 닿는 단계 없음 |

### 2-1. 위임 프롬프트가 따로 판정하라고 한 7개 항목 (요약 — 근거는 위 표)
1. 결정 A(i) 확인 페이지 vs 원칙5 → **양립(해석), CR 불필요** — 2행. 조건 세 개(제품 자료 조회 0·스위치 기본 꺼짐·운영 미사용)가 코드·불변식·P9 인계로 유지될 때만.
2. 실발송 외부 전송·비밀 보호 → **통과** — 8행. 자동 테스트 네트워크 0, 실발송은 SDK+환경변수(§4 허용 형식), 메인 세션 명령은 localhost 만.
3. `pywebpush`·VAPID 키 생성·보관 → **통과** — 4·8행. S3.6 9행 그대로. 키 생성은 사용자, 에이전트는 명령만 문서에, 값 출력 명령 실행 금지.
4. P6 코드 무변경 + 결정 C(i) vs `run.py` 구조 → **통과(코드 직접 확인)** — 4행. `run.py` 197·217~218·251·283~289행.
5. 결정 E 삭제 vs security·훅 → **통과** — 8행. `safety-guard.sh` 129행 범위 밖, §5 와 같은 방향.
6. 수동 확인 행(26행) 증거 설계 vs 원칙8·verification.md → **통과(조건부)** — 2행 원칙8 항목. ⑧ 단독 통과 금지가 계획에 명시돼 있다. 권고 R-4·R-9.
7. 사실 주장 표본 대조 → **일치** — 해시 11개(`608694b`·`f9500fe`·`f05d017`·P6 U1~U8), `run.py` 218행, `Person` 87행·`Schedule` 194행·`PushSubscription` 235행, `deps.py` `get_briefing_composer` 292·`get_now` 303·`build_briefing_ctx` 312행, `scheduler.py` 98행, `routes.py` 349행, `.env.example` 31~34행, `requirements.txt`(푸시 의존성 0), `TRACE_MAX_STRING`(`app/tools/context.py` 86행), `session_scope`(`app/db/session.py` 79행), `tests/conftest.py` `db_session` 120행, `briefing_scheduler_enabled`(`app/settings.py` 291행, `InvalidValue` 규약), `app/main.py` `InvalidValue`·404 핸들러(152~156행), backlog 82~88행, S3.1 13행, review-index 20행, CURRENT 기준선 1724, P6 04-review 267행·§6-3·§6-8·§7, P6 03-log 127행 "민수는 고수를 진짜 싫어하더라", P6 회귀 파일 6개 실재. 어긋난 것 1건(경미): 01-plan 160행 "registry grep 결과 … 44행과 32행뿐" 과 273행 "32·44·153·196행" 이 서로 다르다 — 153행(GitHub Actions)·196행(`push == "not_configured"` 문자열)은 무관한 매치라 결론(중복 아님)은 그대로(R-5).

## 3. 보류 소견과 조치 (있으면 05-remediation.md 의 F-id 를 적는다)
- [필수] 보류 없음. 기계 검증 1차 FAIL 1 은 이 문서의 부재이며 2차에서 해소(1-2절). 05-remediation.md 소견 생성 없음.

### 권고 (구현·04-review 에서 반영 — 계획 개정 불요)
- **R-1 (U5·판정 6행)** `app.dependency_overrides[get_notifier]` 로 넣는 가짜 알림기는 **요청과 같은 세션**을 받아야 한다. `tests/test_api_briefings.py` 55행의 `lambda: FakeBriefingComposer()` 방식은 생성기가 세션을 안 쓰기 때문에 되는 것이고, `WebPushNotifier` 는 세션으로 구독·인물을 읽고 trace 를 쓴다. 오버라이드 함수가 `session: Session = Depends(get_session)` 를 선언해 같은 세션을 공유하게 하라(FastAPI 는 오버라이드 함수의 의존성도 해석한다). 다른 세션이면 6행의 `briefed_at == T`·trace 1행 단언이 커밋 시점에 따라 흔들린다.
- **R-2 (U4·판정 21행)** `app/push/sender.py` 가 `from pywebpush import webpush` 로 이름을 **import 시점에 묶으면** "`pywebpush.webpush` 불리면 실패" 픽스처가 기본 경로를 잡지 못한다(이미 묶인 이름은 패치되지 않는다). 발송 함수를 호출 시점에 `pywebpush.webpush` 속성으로 찾거나, 픽스처가 `app.push.sender` 쪽 이름도 함께 패치하라. 판정 21행의 "실수로 실제 경로를 타면 테스트가 깨진다" 가 실제로 성립하는지 부정 확인(픽스처를 끄고 `PyWebPushSender()` 기본값으로 호출 → 실패)을 U4 evidence 에 남겨라.
- **R-3 (U5·판정 7행)** `default_run_once()` 는 인자 없는 함수다(`scheduler.py` 88행). 주입은 `tests/test_briefing_scheduler.py` 71행처럼 `monkeypatch.setattr(scheduler_module, …)` 로 `session_scope`·`run_briefings`·`notifier_from_env` 를 바꿔 끼우고, **시그니처는 바꾸지 말라**(P6 테스트 5건이 모듈 속성 패치에 기대고 있다).
- **R-4 (U8 ②)** 코드는 `.env` 를 읽지 않는다(security §1, `verification.md` FIX-011 주). 서버 기동 전 `set -a; . ./.env; set +a` 를 메인 세션 셸에서 하고(값 출력 없이), 그 줄을 증거 파일에 명령으로만 적어라. 이것이 없으면 `PUSH_DEV_PAGE_ENABLED`·VAPID 가 프로세스에 안 보여 `/push-dev/` 404·`push == "not_configured"` 로 끝난다.
- **R-5 (문서 정합)** 01-plan 160행과 273행의 registry grep 행 목록 불일치, gitlog `P7-push` grep 의 `7c94aad`(P2-tools) — U1 03-log 첫 줄에 "P7 단위 아님" 과 함께 적어 두면 04-review 태그 역추적(`verify-impl.sh` 5번)에서 헷갈리지 않는다.
- **R-6 (U4, security §5)** `WebPushNotifier.notify` 가 구독을 `self.user_id` 로 읽을 때 일정 소유 인물의 `persons.user_id` 와 같은지 한 줄 단언(`select_due_schedules` 는 `Person.user_id == ctx.user_id` 로 고른다 — `app/briefing/select.py` 61행). 단일 사용자라 지금은 같지만 §5 "모든 조회는 `user_id` 조건" 을 알림기도 지키는 증거가 된다(판정 5행은 `list_subscriptions` 만 본다).
- **R-7 (U6·registry)** 확인 페이지의 registry 행 유형을 "화면" 이 아니라 "확인 도구(제품 화면 아님, 스위치 기본 꺼짐)" 로 적고, P8 인계에 "제품 화면에서 `/push-dev/` 를 링크하지 않는다" 를 넣어라 — 2행 양립 조건 ①②③ 의 문서 쪽 집행.
- **R-8 (U4·판정 18·20행)** 예외 매핑 테스트에서 주입하는 가짜 예외의 메시지에 **감시 문자열**(예: 가짜 엔드포인트 URL·`p256dh` 값)을 넣고, trace output·`SendResult` 어디에도 그 문자열이 없음을 단언하라. `pywebpush.WebPushException` 은 `str(exc)` 에 응답 본문·엔드포인트가 들어갈 수 있어 "클래스 이름만" 규칙이 실제로 지켜지는지는 이 부정 케이스로만 증명된다.
- **R-9 (U8 ⑦)** 서비스 워커가 남기는 수신 기록 줄에 ISO 시각·`schedule_id`·`tag` 를 기계가 만든 형식으로 두고, 04-review 에서 ⑥ trace 의 `schedule_id`·`payload.title` 과 ⑦·⑧ 의 제목이 **같은 값**인지 대조해 적어라. `verification.md` 는 스크린샷 `.png` 도 증거로 인정하므로 사용자가 원하면 텍스트에 더해 `.png` 한 장을 추가해도 된다(필수 아님).
- **R-10 (U3)** `build_push_payload` 의 시각 표기 `MM/DD HH:MM` 는 `user_timezone()`(FIX-005, `app/settings.py` 382행) 으로 변환한 값이어야 한다 — 판정 13행에 `APP_TIMEZONE` 을 UTC 가 아닌 값으로 고정한 케이스가 없다. 10행 또는 13행에 한 케이스 추가를 권한다(수용 기준 밖, 증거 질 향상).

## 4. 결정
결과: 통과
승인: (사용자 승인 전 비워 둔다 → "사용자 (YYYY-MM-DD)")

## 1-2. 기계 검증 2차 출력 (이 문서 작성 뒤 — 그대로 붙인다)
명령: `bash .claude/scripts/verify-plan.sh P7-push | tee docs/wiki/packages/P7-push/evidence/20261002-2123-verify-plan-2.txt`
```
== verify-plan P7-push  (2026-10-02 21:23) ==
PASS  존재: docs/wiki/packages/P7-push/01-plan.md
PASS  존재: docs/wiki/packages/P7-push/02-plan-verify.md
PASS  카드 존재: D7
PASS  패키지 id 등록됨: P1-schema
PASS  패키지 id 등록됨: P10-final-eval
PASS  패키지 id 등록됨: P2-tools
PASS  패키지 id 등록됨: P5-loop
PASS  패키지 id 등록됨: P6-briefing
PASS  패키지 id 등록됨: P7-push
PASS  패키지 id 등록됨: P8-frontend
PASS  패키지 id 등록됨: P9-infra
PASS  검증 항목 존재: R12
PASS  검증 항목 존재: R19
PASS  Refs 있음: - [ ] U1 골격·의존성·설정 — [backend-agent] `pywebpush` 설치·버전 고정(`r
PASS  Refs 있음: - [ ] U2 구독 저장 — [backend-agent] `app/push/subscriptions.py`
PASS  Refs 있음: - [ ] U3 푸시 본문 작성기 — [backend-agent] `build_push_payload(sch
PASS  Refs 있음: - [ ] U4 발송기·알림기 — [backend-agent] `PyWebPushSender`(`pywebp
PASS  Refs 있음: - [ ] U5 두 경로 연결 — [backend-agent] `app/api/deps.py::get_not
PASS  Refs 있음: - [ ] U6 개발·확인 전용 구독 페이지 — [backend-agent] `app/push/devpage
PASS  Refs 있음: - [ ] U7 수용 기준 기계 검증·문서 — [backend-agent] 아래 판정 표 1~25행 실행, 
PASS  Refs 있음: - [ ] U8 데스크톱 Chrome 실발송 확인 — [사용자·메인 세션] (backend-agent 아님 
PASS  backlog 일치: 데스크톱 Chrome에서 알림 수신
PASS  의존 완료: P6-briefing
PASS  P4 게이트 통과 (P4b-er-redesign)
PASS  검증자 = verifier (L-002)
PASS  점검표 8행 존재
PASS  점검표 모든 행에 판정(통과/보류) 있음
PASS  보류 0건
PASS  결과: 줄 존재
PASS  점검표 모든 행에 근거 있음
PASS  registry 중복 없음: app/push/__init__.py
PASS  registry 중복 없음: app/push/types.py
PASS  registry 중복 없음: app/push/subscriptions.py
PASS  registry 중복 없음: app/push/payload.py
PASS  registry 중복 없음: app/push/sender.py
PASS  registry 중복 없음: app/push/notifier.py
PASS  registry 중복 없음: app/push/devpage/index.html
PASS  registry 중복 없음: app/push/devpage/sw.js
PASS  registry 중복 없음: app/push/devpage/devpage.js
PASS  registry 중복 없음: tests/test_push_settings.py
PASS  registry 중복 없음: tests/test_push_subscriptions.py
PASS  registry 중복 없음: tests/test_push_payload.py
PASS  registry 중복 없음: tests/test_push_notifier.py
PASS  registry 중복 없음: tests/test_push_wiring.py
PASS  registry 중복 없음: tests/test_push_devpage.py
== 결과: FAIL=0 WARN=0 ==
```
