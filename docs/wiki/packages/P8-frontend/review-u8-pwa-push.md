# P8-frontend U8 PWA·푸시 구독 (+ U7 이월 R-U7-1·2·3 · U4 이월 R-U4-4 · 재작업: POST 실패 되돌리기) — 커밋 전 코드 리뷰

검토자: verifier (fable)
결과: 통과 (2026-10-14 20:30) — **[필수] 0, [권고] 3.** 01-plan 99행·결정 H·I·68행(재작업 방어 조건) 계약 16항목 전부 코드 위치 + 값 단언 테스트 + 변이 검출로 충족(§1). 판정 명령 재실행 exit 0(typecheck · 8 files 130 passed · build, 번들 `index-BsQ5cRBT.css`/`index-CQEgzTJp.js` — 구현자 2017·메인 세션 2017 과 동일; `dist/sw.js`·`manifest.webmanifest` 가 `public/` 과 바이트 동일, `-judge.txt`). 서버 페이로드 키(`payload.py` 100~105행 `title`·`body`·`tag`·`schedule_id`·`ttl`)와 워커가 읽는 키(`sw.js` 17·19·20행) 1:1, `tag` 는 `schedule-<id>`, 열린 창에는 `{type, schedule_id}` 만(§2). `app/push/devpage/` 무변경(diff 0, 마지막 커밋 `572045a`), 페이로드 해석 4줄이 그대로 복사됐고 차이는 내 `diff -u` 로 7항목(§3 — 03-log U8 완료 항목에 이 diff 를 적어야 한다, R-U8-2). 되돌리기 방어 조건: `push.ts` 89~99행 POST 실패 → `unsubscribe()` 1회 → `failed`, 되돌리기 실패 삼킴 — 테스트 3건 + M31 내 재실행 3 failed 동일(§4). 이월 R-U7-1·2·3·R-U4-4 전부 닫힘(§5 — 테스트가 내 U7 탐침 P6·P2c·P4 순서 그대로, M19·M20·M24·M25·M26·M29 검출). 구현자 선택 3개 계획 모순 0(§6). 내 변이 5건 중 4건 검출, **V4(`open-briefing` 에 `schedule_id` 없을 때 이동 제거)는 130 passed 로 살아남음** — 결함이 아니라 테스트 틈이라 [권고](R-U8-1). 구현자 M1·M10·M11·M31 재실행이 실패 이름·건수까지 동일(§8). R-U0-3: package·lock 바이트 동일, scripts 7개 무변경, `npm audit --omit=dev` 0, `?raw` 8건 전부 저장소 안 파일(`-deps.txt`). 증거는 전부 `save_evidence.py` 통로, 변이 출력 전체, 스크립트 1차·재작업 둘 다 보존(차이 M31 1줄) — R-U6-3 준수(§9). 보안·범위 위반 0(§10).
대상: 작업 트리(기준 HEAD `46532e7`) — `git diff -- web` 8파일(`index.html` 2/0 · `favicon.svg` 1/1 · `briefing.test.tsx` 68/2 · `card.test.tsx` 27/0 · `client.ts` 14/0 · `AppShell.tsx` 67/3 · `routes.ts` 5/0 · `BriefingScreen.tsx` 67/11 — `git diff --numstat`) + 신규 `web/public/sw.js`(69행)·`manifest.webmanifest`(13행)·`icon-192.svg`·`icon-512.svg`·`web/src/push.ts`(104행)·`web/src/__tests__/sw.test.ts`(200행)·`push.test.ts`(402행) · `docs/wiki/registry.md` U8 행 5개(251~255행) · `01-plan.md` 68행(메인 세션 수정) · 구현 증거 `evidence/20261014-2008-u8-pwa-push.txt`·`-2008-u8-mutation.txt`(M1~M30, 8199행)·`-2008-u8-mutation-script.txt` · 재작업 `-2017-u8-pwa-push-rework.txt`·`-2017-u8-mutation-rework.txt`(M31)·`-2017-u8-mutation-script-rework.txt` · 메인 세션 `-2010-u8-main-recheck.txt`·`-2017-u8-main-recheck2.txt`. `HANDOFF.md`·`journal.md`·`03-log.md` 변경은 대상 아님(03-log 맨 끝 "U8 시작" 항목은 근거 문서 — 구현 결과·구현자 선택 3개·사용자 결정 2개).
근거 문서: `01-plan.md` 99행(U8 원문) · 결정 H(282~287행)·I(289~293행)·M(348행) · 19행·35행(오프라인 제외)·36~49행(하지 않는 것)·52~80행(파일 목록, 68행 아이콘 `.svg`·방어 조건) · 360행(불변식 3 `fetch|caches.` 0건) · `docs/proposal.md` 246행("푸시 3중 안전장치: 웹푸시 / 인앱 배너 / 발표자 수동 트리거 버튼") · `app/push/devpage/sw.js`(39행, 복사 원본)·`devpage.js`(구독 절차 순서) · `app/push/payload.py` 95~105행(페이로드 키) · `app/push/sender.py` 89행(`data=json.dumps(payload)` — `ttl` 도 본문에 들어감) · `app/api/routes.py` 409~430행(`/push/vapid-public-key` 404 `push_not_configured` · `/push/subscriptions`) · `app/api/schemas.py` 252~256행(`VapidPublicKeyOut`)·276~294행(`PushSubscriptionIn` — `endpoint`·`keys{p256dh,auth}`·`expirationTime` 받기만) · `web/src/api/types.ts` 214~232행 · CLAUDE.md 원칙5·7 · `review-u7-briefing.md` R-U7-1·2·3·4 · `review-u4-skeleton.md` R-U4-4 · `review-u0-harness.md` R-U0-3 · `review-u6-card.md` R-U6-3 · `docs/wiki/security.md` §1·§5 · `docs/wiki/verification.md`.

내 증거(전부 `save_evidence.py` 통로, `docs/wiki/packages/P8-frontend/evidence/`):
- `20261014-2024-verifier-u8-judge.txt` — `cd web && npm run typecheck && npm test -- --run && npm run build && ls dist …` exit 0, 8 files · 130 passed, 번들 해시 구현자·메인 세션과 동일, `dist/` 에 `sw.js`·`manifest.webmanifest`·`icon-192/512.svg`·`favicon.svg`, `cmp public/sw.js dist/sw.js`·manifest 바이트 동일.
- `20261014-2024-verifier-u8-deps.txt` — package.json·lock `git diff --quiet` exit 0, scripts 7개 HEAD 와 동일, `npm audit --omit=dev` "found 0 vulnerabilities", `?raw` 8건(U6 2 + U8 6) 대상 파일 전부 저장소 안(`ls -l`), 새 파일 5개의 import 목록(새 패키지·새 `ui/` 부품 0).
- `20261014-2024-verifier-u8-diff.txt` — `app/push/devpage/` diff 0·status 빈 출력·마지막 커밋 `572045a` · `diff -u app/push/devpage/sw.js web/public/sw.js` 전체 · 복사된 페이로드 해석 줄 대조(원본 7·11·12·15행 ↔ 제품 9·17·19·20행) · `devpage.js` 구독 절차 순서 ↔ `push.ts` 56·60·78~80행.
- `20261014-2024-verifier-u8-grep.txt` — 범위(`app alembic tests .github` diff·untracked 빈 출력) · 삭제 0 · 결정 I(`sw.js` 에 `fetch|caches|Cache|importScripts|XMLHttpRequest|http` 0, 리스너 4개 install·activate·push·notificationclick) · API 응답 캐시 0(`localStorage` 는 U5 `session.ts` 의 session_id 뿐) · 페이로드 키 대조 · `postMessage` 인자 2곳 · 페이지가 읽는 필드(`type`·`schedule_id`) · 비밀 grep(적중은 테스트의 3바이트 더미 `'AQID'` 와 주석뿐) · `/push-dev/`·`innerHTML`·외부 URL 0 · `test-setup.ts` diff 0·`throw` 유지 · 원칙5(`HREF` 3·`data-screen` 3·`App.tsx` diff 0·`routes.ts` 추가분 = `briefingHref` 1함수) · `unsubscribe` 사용처 = `push.ts` 94행 1곳 · `BRIEFING_NOTICE` 16·`BANNER_NOTICE` 3 · 이월(`loadRef` 3곳·`scheduleFailed` 2곳·`ring-2` 코드 1+테스트 3·favicon `863bff` 0) · registry U8 행.
- `20261014-2024-verifier-u8-mutation.txt`(2855행) — V0 대조군 + 내 변이 V1~V5 + 구현자 M1·M10·M11·M31 재실행 = 10회, 매회 vitest 출력 전체(`DEBUG_PRINT_LIMIT=0` 으로 DOM 덤프만 끔) + 끝에 `git status --short -- web`(10회 모두 U8 작업 트리 그대로, 저장소 무수정).
- `20261014-2025-verifier-u8-scripts.txt` — 내 변이 스크립트 `vmut_u8.mjs` 원문(스크래치패드 사본 복사·한 곳 치환·vitest 전체 출력).

## 1. 01-plan 99행 · 결정 H·I · 68행(재작업) 계약 대조

| # | 계약(99행 / 결정 / 68행) | 구현 | 테스트·변이 | 판정 |
|---|---|---|---|---|
| 1 | manifest: 이름 · 아이콘 2종 · `start_url` `/#/chat` · `display: standalone` | `manifest.webmanifest` 2~3행 `name`/`short_name` "관계 메모리"(= `index.html` `<title>`), 4행 `start_url "/#/chat"`, 6행 `standalone`, 9~12행 `icon-192.svg`·`icon-512.svg`(`sizes` 192x192·512x512, `type image/svg+xml`, 경로 `/` 시작) · `index.html` 6행 `<link rel="manifest">`·7행 `theme-color #171717`(= `tokens.css` 78행 `--primary: oklch(0.205 0 0)`) | `sw.test` "start_url 은 /#/chat, display 는 standalone" · "이름은 index.html <title> 과 같고 …" · "아이콘은 192·512 두 개이고 각각 실제 파일이다" · "index.html 이 manifest 를 연결하고 …" · 구현자 M27·M28·M30 검출 · **내 V5**(`icons: []`) 1 failed | ✓ — 아이콘은 68행 사용자 확정(SVG, PNG 는 U10 확인 뒤) |
| 2 | `sw.js` 범위 `/` | `push.ts` 7행 `SERVICE_WORKER_URL = '/sw.js'`, 60행 `register(SERVICE_WORKER_URL)`(scope 미지정 = 스크립트 위치 `/`) · `public/sw.js` 는 빌드 시 `dist/sw.js` 로 바이트 동일 복사(`-judge.txt` `cmp`) | `push.test` "새 구독: … 등록(/sw.js) …"(`register` 인자 `'/sw.js'`) · 구현자 M16(`/push-dev/sw.js`) 검출 | ✓ |
| 3 | `push` → `showNotification(title, {body, tag, data:{schedule_id}})` — 페이로드 해석은 `devpage/sw.js` 복사 | `sw.js` 7~13행 `readPayload`(원본 6~10행 try/catch 그대로), 16~23행 `notificationFor`: `title: data.title \|\| "알림"`(원본 11행), `body: data.body \|\| ""`·`tag: data.tag`(원본 12행), `schedule_id === undefined ? null`(원본 15행), `data: { schedule_id }` 추가; 41~44행 `push` → `showNotification(shown.title, shown.options)` | `sw.test` "페이로드를 showNotification(title, {body, tag, data:{schedule_id}}) 로 그대로 넘긴다"(앞뒤 공백·`&`·따옴표 포함 완전 일치) · "schedule_id 가 빠진 페이로드면 … null" · "JSON 을 못 읽거나 데이터가 없으면 기본 제목 '알림'" · 구현자 M3·M8·M9 검출 · **내 V1**(`body` 를 제목으로) 2 failed | ✓ |
| 4 | `notificationclick` → 열린 창 포커스 후 `#/briefings?schedule_id=N`, 없으면 `clients.openWindow` | 54~69행: `event.notification.data.schedule_id` → 창 있으면 `list[0].focus()` 뒤 `postMessage({type:"open-briefing", schedule_id})` / 없으면 `openWindow(targetHashFor(scheduleId))`; 26~31행 `targetHashFor` 는 양의 정수만 `?schedule_id=N`, 아니면 `/#/briefings` · `AppShell.tsx` 74~78행 `open-briefing` → 76행 `window.location.hash = briefingHref(scheduleId)` | `sw.test` "열린 창이 있으면 알림을 닫고 첫 창을 focus 한 뒤 {type:'open-briefing', schedule_id} 를 보낸다(새 창 없음)" · "열린 창이 없으면 openWindow('/#/briefings?schedule_id=N')" · "schedule_id 가 없거나 양의 정수가 아니면 일정 없는 브리핑 화면 주소"(null·`{}`·0·`'12'`·1.5) · `push.test` "알림을 눌러 온 {type:'open-briefing'} 은 배너 없이 바로 그 일정 주소로 간다" · 구현자 M5·M6·M7·M22 검출 · **내 V2**(`?schedule_id=undefined`) 1 failed · **내 V4**(null 이면 이동 안 함) **살아남음** → R-U8-1 | ✓ (구현자 선택 ① — §6) |
| 5 | 열린 창에 `postMessage({type:"briefing", schedule_id})` → 인앱 배너(기획서 246행 두 번째 안전장치) | `sw.js` 45~49행 `matchAll({type:"window", includeUncontrolled:true})` → 모든 창에 `{type:"briefing", schedule_id}` · `AppShell.tsx` 52~58행 `readWorkerMessage`(모양 검사, 양의 정수만), 65~103행 `WorkerMessages` → 79행 `setBanner`, 86~102행 `role="status"` `data-testid="push-banner"` 한 줄 + `<a href={briefingHref(...)}>` + 닫기; 141~142행 `<main>` 안 `children` 위 | `sw.test` "열린 모든 창에 {type:'briefing', schedule_id} 만 보낸다(title·body 는 보내지 않는다)" · `push.test` 배너 4건(배너→링크 href→누른 뒤 사라짐 / 닫기 / `schedule_id` 없음·모양 다른 메시지 무시 / `open-briefing`) · 구현자 M4·M21·M23 검출 | ✓ — 새 화면 아님(`data-screen` 3 그대로, `-grep.txt` 7절) |
| 6 | 결정 I: 캐시 없음 · `fetch` 리스너 없음 · API 응답 캐시 0 | `sw.js` 에 `fetch|caches|Cache|importScripts|XMLHttpRequest|http` 0건, `addEventListener` 4개(33·37·41·54행), `install` = `skipWaiting`·`activate` = `clients.claim` 만 · `web/src` 에 Cache API·`indexedDB` 0, `localStorage` 는 `session.ts` session_id 뿐(`-grep.txt` 2·2b·2c절 — 01-plan 360행 불변식 3) | `sw.test` "등록되는 리스너는 install · activate · push · notificationclick 넷뿐이다" · "install 은 skipWaiting, activate 는 clients.claim 만 한다" · "코드에 요청 가로채기 리스너·캐시 API 호출이 없다" · 구현자 M1·M2 검출(M1 내 재실행 2 failed 동일) | ✓ |
| 7 | `push.ts`: 권한 → `register('/sw.js')` → `GET /api/push/vapid-public-key` → `subscribe({userVisibleOnly:true, applicationServerKey})` → `POST /api/push/subscriptions` | 52~104행 `subscribeToPush`: 56행 `Notification.requestPermission()` → 60~61행 `register`+`ready` → 66행 `getVapidPublicKey().public_key` → 75행 기존 구독 검사 → 78~81행 `subscribe({userVisibleOnly:true, applicationServerKey: urlBase64ToUint8Array(publicKey)})` → 82~90행 `toJSON()` → `postPushSubscription({endpoint, keys{p256dh,auth}, expirationTime})`(= `PushSubscriptionIn` 282~284행·`types.ts` 223~227행) · `client.ts` 144~150행 두 함수(`apiFetch` 경유, `/api` 접두·세션 헤더 그대로) · 순서는 `devpage.js` 44·50·56·64·70행과 동일(`-diff.txt` 4절) | `push.test` "새 구독: 권한 → 등록(/sw.js) → 공개키 → 구독 → 서버 저장 순서이고, 본문은 PushSubscriptionIn 필드 그대로"(`order` 배열 완전 일치, `applicationServerKey` 바이트 `[1,2,3]`, POST 본문 JSON 완전 일치) · "urlBase64ToUint8Array"(`-`/`_`/패딩) · 구현자 M12·M13·M14·M15 검출 · **내 V3**(문자열 그대로 전달) 1 failed | ✓ |
| 8 | 404 `push_not_configured` → 안내 한 줄 | `push.ts` 67~72행 `ApiError && status === 404 && code === 'push_not_configured'` → `'not_configured'`(다른 404·5xx 는 `'failed'`) · `BriefingScreen.tsx` 36~41행 `PUSH_NOTE` → 31행 `pushNotConfigured` "이 서버는 아직 알림을 준비하지 않았어요." → 76~80행 `data-testid="push-note"` `role="status"` 한 줄 | `push.test` "404 push_not_configured 면 'not_configured' — 구독·저장 없이 멈춘다"(`getSubscription`·`subscribe` 0, fetch 1회) · "다른 404(코드가 다름)나 5xx 는 … 'failed'" · "안내 한 줄: 권한 거부 · 서버 미설정 · 미지원 · 실패"(버튼 다시 활성) · 구현자 M11 검출(내 재실행 2 failed 동일) | ✓ |
| 9 | 이미 구독돼 있으면 "알림 켜짐" | `push.ts` 41~50행 `getPushStatus`(`getRegistration` → `getSubscription`, 권한 창·네트워크 0) · 75행 클릭 경로에서도 기존 구독이면 `'already'`(POST 0) · `BriefingScreen.tsx` 50~58행 진입 시 `subscribed` → `'on'`, 64~67행 `already` → `'on'`; 74행 `disabled={state !== 'idle'}`, 75행 글자 `subscribed` "알림 켜짐" | `push.test` "이미 구독돼 있으면 'already' — 구독도 서버 저장(POST)도 하지 않는다" · "들어올 때 이미 구독돼 있으면 곧바로 '알림 켜짐'(비활성) — 클릭 없이, 서버 저장 없이" · "getPushStatus: 미지원·구독 없음·구독 있음"(`permission`·`register` 0) · 구현자 M10·M17·M18 검출(M10 내 재실행 1 failed 동일) | ✓ |
| 10 | 결정 H: 구독 버튼은 브리핑 화면 상단 "알림 받기" 한 줄 · 3상태 | `BriefingScreen.tsx` 244행 `<PushSubscribe />`(U7 의 `data-slot="push-subscribe"` 자리, 73행 유지) · 46~83행 `idle`/`running`/`on` → "알림 받기"/"알림 켜는 중"/"알림 켜짐", `running`·`on` 비활성 | `push.test` "미구독 → 진행 중(비활성) → 켜짐(비활성) 세 상태"(POST 가 나간 뒤에도 진행 중) · `briefing.test` "… 알림 받기 버튼이 활성이며 /push-dev/ 링크가 없다" | ✓ |
| 11 | 결정 H: 구독 해제 없음 | `unsubscribe` 사용처는 `push.ts` 94행(되돌리기) 1곳뿐, 해제 버튼·`DELETE` 호출 0(`-grep.txt` 8절) | — (부재 확인은 grep) | ✓ |
| 12 | 결정 I: `/push-dev/sw.js` 와 별개 등록, 원본 무변경, 차이는 03-log 에 diff | `app/push/devpage/` diff 0·status 빈 출력(`-diff.txt` 1절) · 제품 워커 범위 `/`, 등록 경로 `/sw.js` · 제품 코드·`public/` 에 `push-dev` 0 | 구현자 M16 검출 | ✓ 코드 / **03-log 에 diff 아직 없음**(03-log 140행 "차이 보고됨" 뿐) → R-U8-2 |
| 13 | 68행 방어 조건(재작업): `POST /push/subscriptions` 실패 시 `subscription.unsubscribe()` 로 되돌려 다음 클릭이 처음부터 | `push.ts` 89~99행: `postPushSubscription` 실패(어떤 오류든) → `try { await subscription.unsubscribe() } catch {}` → `'failed'` | `push.test` "서버 저장(POST)이 실패하면 브라우저 구독을 unsubscribe 1회로 되돌리고 'failed'"(500·404 두 경우) · "저장 실패 뒤 다음 클릭은 처음부터 다시 — subscribe 재호출·POST 재시도(이번엔 성공)"(`'already'` 로 끝나지 않음, `subscribe` 2회·POST 2회) · "unsubscribe 자체가 실패해도 예외 없이 'failed'" · 구현자 M31 검출(내 재실행 3 failed 동일) | ✓ — §4 |
| 14 | 원칙7: 알림 title·body 는 서버 문장 그대로, 프론트 고정 문구만 추가 | `sw.js` 19~20행 변환 0(`trim`·치환 없음) · 배너 문구 `BANNER_NOTICE` 3개는 프론트 고정("새 브리핑 알림이 도착했어요." 등), 알림 본문은 페이지로 오지 않음 | `sw.test` 완전 일치 단언 · 구현자 M9(`trim`) 검출 | ✓ |
| 15 | 원칙5: 새 화면·새 라우트 0 | `HREF` 3·`Route` 3·`data-screen` 3·`App.tsx` diff 0, `routes.ts` 추가분은 `briefingHref` 1함수(`-grep.txt` 7절) | `push.test` 배너 테스트가 `App` 전체로 렌더해 배너가 `<main>` 안 한 줄임을 확인 | ✓ |
| 16 | 판정 `npm test -- --run src/__tests__/sw.test.ts src/__tests__/push.test.ts` · 증거 `*-u8-pwa-push.txt` | 구현자 `-2008-u8-pwa-push.txt`(31 passed + 127 + build) · 재작업 `-2017-u8-pwa-push-rework.txt`(130) · 메인 `-2010`·`-2017-main-recheck2` · 내 `-judge.txt` 130 passed | — | ✓ |

## 2. 서버 페이로드 ↔ 워커 키 · 열린 창으로 가는 것 (security §5)

- `payload.py` 100~105행이 만드는 키: `title`·`body`·`tag`(`f"schedule-{schedule.id}"`)·`schedule_id`·`ttl`. `sender.py` 89행 `data=json.dumps(payload)` — 다섯 키 전부 본문에 실린다. 워커가 읽는 것: `data.title`(19행)·`data.body`·`data.tag`(20행)·`data.schedule_id`(17행). `ttl` 은 읽지 않는다(발송 TTL 은 `notifier.py` 167행이 헤더로 따로 준다) — 문제 없음.
- `tag` 는 그대로 `showNotification` 옵션으로 — 같은 일정의 알림은 덮어쓴다(P7 51행 주석과 같은 뜻). `data.schedule_id` 는 정수(`schedule.id`)라 `targetHashFor` 의 양의 정수 검사를 통과한다.
- 열린 창에는 `{type:"briefing", schedule_id}`(48행)·`{type:"open-briefing", schedule_id}`(63행) 뿐 — `title`(인물 이름 포함)·`body`(제안 문장)는 페이지로 가지 않는다(`sw.test` "title·body 는 보내지 않는다" 단언). 원본 `devpage/sw.js` 의 `received_at`·`tag` 도 뺐다(더 줄였다). 페이지는 `type`·`schedule_id` 만 읽는다(`AppShell.tsx` 54~56행). 기기에 남는 개인정보 증가 0(결정 I 문장 "API 응답을 캐시하면 … 개인정보가 늘고" 와 정합).
- 프론트에 가는 키는 공개키뿐(`VapidPublicKeyOut.public_key`), 개인키 문자열 0(`-grep.txt` 4절).

## 3. `app/push/devpage/sw.js` → `web/public/sw.js` (결정 I "페이로드 해석만 복사, 원본 무변경")

원본 무변경: `git diff --stat -- app/push/devpage/` 빈 출력, `git status` 빈 출력, 마지막 커밋 `572045a`(P7)(`-diff.txt` 1절). 복사된 줄(원본 7·11·12·15행 ↔ 제품 9·19·20·17행): `event.data ? event.data.json() : {}` + try/catch, `data.title || "알림"`, `data.body || ""`·`tag: data.tag`, `data.schedule_id === undefined ? null : data.schedule_id` — 전부 글자 그대로. 03-log 140행은 "차이 보고됨" 이라고만 적었고 **차이 목록이 위키 어디에도 없다**(구현자 보고는 메인 세션 대화에만). 내 `diff -u`(`-diff.txt` 2절)로 센 차이 **7항목**:

| # | 차이 | 뜻 |
|---|---|---|
| 1 | 머리 주석 5줄(Refs·결정 H·I·원칙7) | 문서 |
| 2 | 인라인 코드를 `readPayload`·`notificationFor`·`targetHashFor` 세 함수로 분리 | 구조(동작 동일 — §1 3행 테스트) |
| 3 | `showNotification` 옵션에 `data: { schedule_id }` 추가 | 클릭 때 일정 번호를 쓰기 위해(99행 계약) |
| 4 | 창에 보내는 메시지 `{received_at, schedule_id, tag}` → `{type:"briefing", schedule_id}` | `received_at`·`tag` 제거, `type` 추가(배너 식별) |
| 5 | `notificationclick`: `list[0].focus()` 만 → `focus()` 뒤 `postMessage({type:"open-briefing", schedule_id})` | 열린 창을 그 일정으로 보내기(구현자 선택 ①) |
| 6 | 창 없을 때 `openWindow("/push-dev/")` → `openWindow(targetHashFor(scheduleId))` | 제품 주소 |
| 7 | `install`(`skipWaiting`)·`activate`(`clients.claim`) 리스너 추가 | 새 워커 즉시 활성(캐시가 없어 안전) |

→ 03-log U8 완료 항목에 이 표(또는 `-diff.txt` 참조)를 적어야 결정 I 의 "차이는 03-log U8 에 diff 로" 가 닫힌다(R-U8-2).

## 4. 되돌리기 방어 조건 (68행, 재작업) — 코드 · 테스트 · 변이

- 코드 `push.ts` 89~99행: `postPushSubscription` 을 감싼 `try/catch` 가 **모든** 오류(5xx·404·네트워크·비-JSON)를 잡아 `subscription.unsubscribe()` 를 **한 번** 부르고, 그 호출이 거부돼도 안쪽 `catch {}` 가 삼킨 뒤 `'failed'`. `unsubscribe()` 가 `pushManager.getSubscription()` 을 비우므로 다음 클릭의 75행 검사가 `'already'` 로 끝나지 않는다.
- 테스트 3건(`push.test` 201~235행): ① 500 과 404 `push_not_configured` 두 경우 모두 `unsubscribe` 1회 + `'failed'` ② 첫 클릭 실패 → 둘째 클릭 `'subscribed'`(`subscribe` 2회·POST 2회 — "`'already'` 로 끝나지 않는다") ③ `unsubscribe` 거부 → 예외 없이 `'failed'`, 호출 1회. 가짜 브라우저(`installPushBrowser`)가 `current` 로 "브라우저에 남은 구독" 을 흉내 내므로 ②가 실제 되돌리기 효과를 가른다(M31 에서 ②가 실패한다 — 실제 조건 검사).
- 변이 M31(`await subscription.unsubscribe()` → `void subscription`): 구현자 재작업 증거 3 failed, 내 재실행 3 failed 이름 동일(§8).
- 68행 기록과 일치: "POST 실패 시 `subscription.unsubscribe()` 로 브라우저 구독을 되돌려 다음 클릭이 처음부터 다시 하게" — 코드·테스트가 그 문장 그대로다. 기록: POST 단계의 404 `push_not_configured` 는 `'not_configured'` 가 아니라 `'failed'` 로 끝난다 — 실제 서버의 `POST /push/subscriptions`(routes.py 420~430행)는 설정을 검사하지 않아 그 응답이 나오지 않으므로(공개키 GET 에서 이미 걸러짐) 영향 0. `client.ts` 142행 주석 "둘 다 미설정이면 404" 는 routes.py 86행의 "둘 다"(전무·반쪽)를 GET·POST 둘로 잘못 옮긴 것 — 주석 한 줄(R-U8-2 ⑤).

## 5. 이월 닫힘 — R-U7-1 · R-U7-2 · R-U7-3 · R-U4-4

| 이월 | 처방 | 구현 | 테스트 | 변이 | 판정 |
|---|---|---|---|---|---|
| R-U7-1 `run` 이 클릭 시점 `load` 를 붙잡음 | `load` 를 ref 로 최신 유지 | `BriefingScreen.tsx` 197행 `loadRef = useRef(load)`, 199행 effect 에서 갱신, 217행 `await loadRef.current()`, `run` 의존성 `[]` | `briefing.test` "R-U7-1: 수동 브리핑이 진행 중일 때 쿼리가 바뀌면, 끝난 뒤 재조회는 바뀐 일정(최신) 기준이다" — 내 소견의 재현 순서 그대로(77 진입 → POST 보류 → 해시 88 → POST 완료 → `ids()` `[88,5,2,9]`, 77 없음, 88 강조) | 구현자 M19(되돌리기) 1 failed | 닫힘 |
| R-U7-2 ① 강조 `ring-2` | 탐침 P6 | — | "목록 안에 있으면 맨 위로 …" 테스트 178~180행에 `card('briefing-9').className` `ring-2` 포함·5·2 미포함(P6 와 같은 단언) | M24(V3 재현) 1 failed | 닫힘 |
| R-U7-2 ② Provider 늦은 응답 | 탐침 P2c | — | `card.test` "R-U7-2 (탐침 P2c): 먼저 보낸 느린 조회가 나중 조회보다 늦게 도착해도 사이드바는 나중 조회 값이다" — P2c 순서 그대로(느린 1차 보류 → `notifyPersonsChanged()` → 2차 표시 → 1차 뒤늦게 resolve → 2차 유지) | M25(V4 재현) 1 failed | 닫힘 |
| R-U7-2 ③ 재조회 실패 시 목록 유지 | 탐침 P4 | — | `briefing.test` "R-U7-2 (탐침 P4): 수동 브리핑은 성공했는데 재조회가 실패하면 이전 목록 3건을 그대로 두고 실패 한 줄만 더한다" — P4 와 동일 | M26 1 failed | 닫힘 |
| R-U7-3 단건 비-404 실패 문구 | 문구 1개 분리 | 26행 `scheduleFailed: '그 일정의 브리핑을 불러오지 못했어요.'`, 256~259행 `lookup === 'failed'` → `data-testid="schedule-failed"` | "R-U7-3: 단건 조회가 404 가 아닌 오류로 실패하면 목록 실패 문구가 아니라 '그 일정' 문구 — 목록은 그대로" | M20 1 failed | 닫힘(결정 L 수정 1회 안) |
| R-U4-4 favicon 템플릿 잔재 | 아이콘 2종과 같은 도안으로 교체 | `favicon.svg` 1행 — `icon-*.svg` 와 같은 도안(`#171717` 둥근 사각 + "관", `width` 만 64), 9.5 kB → 340 B, `863bff` 0(`-grep.txt` 10절) | `sw.test` "… favicon 은 같은 아이콘이다(템플릿 로고 아님)"(`#171717`·`>관</text>` 포함, `#863bff` 미포함) | M29 1 failed | 닫힘 |

## 6. 구현자 선택 3개 (03-log 140행) + 고정 문구

| # | 선택 | 계획과의 관계 · 실측 | 판정 |
|---|---|---|---|
| ① | 알림 클릭 시 열린 창에 `client.navigate()` 대신 `postMessage({type:"open-briefing"})` → 페이지가 해시 이동 | 99행 "열린 창 포커스 후 `#/briefings?schedule_id=N`" — 수단 미지정, 위임 문구 "navigate 또는 postMessage" 안. `navigate()` 는 **이 워커가 제어하는** 창에만 되고 전체 재로드(SPA 상태 소실)인 반면 `postMessage` 는 해시만 바꿔 현재 화면을 유지한다. 앱이 아직 로드되지 않은 창: 서비스 워커 스펙의 클라이언트 메시지 큐가 `message` 리스너가 붙을 때까지 메시지를 보관하므로 `WorkerMessages` effect 가 붙은 뒤 처리될 것으로 본다 — **코드 읽기 소견이지 실측이 아니다**(U10 사람 점검 "앱 탭 로딩 중 알림 클릭" 으로 확인). 단, 같은 출처의 **앱이 아닌** 창(`PUSH_DEV_PAGE_ENABLED` 가 켜진 개발 환경의 `/push-dev/`, `/api/docs`)이 `list[0]` 이면 focus 만 되고 이동하지 않는다(`includeUncontrolled:true` 가 같은 출처 창을 전부 돌려주기 때문). 운영은 dev 페이지가 꺼져 있어 영향 0. | 적합 — [권고] R-U8-3(창 고르기 조건 또는 U10 점검 항목) |
| ② | 미지원 안내를 진입 시가 아니라 클릭 때 | `getPushStatus()` 의 `'unsupported'` 를 `PushSubscribe` 가 쓰지 않는다(50~58행은 `subscribed` 만). iOS Safari(미설치) 등에서 버튼이 활성으로 보이고 누르면 "이 브라우저는 알림을 지원하지 않아요." 99행·결정 H 에 시점 규정 없음. 기획서 257행 "iOS 웹푸시 제약 — 데모는 안드로이드/데스크톱". | 적합 — 기록(U10 에서 사용자가 보고 진입 시 비활성+안내로 바꿀지 정한다, 결정 L 1회 안) |
| ③ | 배너는 마지막 알림 하나(새 메시지가 이전 배너를 대체) | 결정 H "현재 화면 상단 한 줄" — 한 줄이 맞다. 알림 자체는 OS 알림 센터에 `tag` 별로 남는다. | 적합 — 기록 |
| — | 고정 문구 +10: `BRIEFING_NOTICE` 7(`scheduleFailed`·`subscribing`·`subscribed`·`pushDenied`·`pushNotConfigured`·`pushUnsupported`·`pushFailed`) → 16, `BANNER_NOTICE` 3 | 전부 버튼 글자·상태 안내(`-grep.txt` 9절). 서버 문장 대체 0, 상담·감정 어휘 0. 알림 title·body(서버 문장)는 변환 없이 OS 알림으로만. | 원칙7 적합 |

## 7. R-U0-3 고정 점검 (`-deps.txt`)

`package.json`·`package-lock.json` `git diff --quiet` exit 0(바이트 동일) · scripts 7개 HEAD 와 동일(삭제 명령 0) · `npm audit --omit=dev` "found 0 vulnerabilities" · `?raw` 8건(`card.test` 2 + `sw.test` 6) 대상 전부 저장소 안 파일(`ls -l` 존재) · 새 파일 5개 import 는 기존 `@/api/*`·`@/components/ui/*`·`@/routes`·`@/push`·vitest·testing-library 뿐(새 패키지·새 `ui/` 부품 0).

## 8. 변이 시험 (`-mutation.txt`, 저장소 무수정 — 10회 전부 끝의 `git status --short -- web` 이 U8 작업 트리 그대로)

| 변이 | 결과 | 실패 테스트 | 뜻 |
|---|---|---|---|
| V0 대조군 | 130 passed | — | 사본 기준선(복사·심볼릭 링크 정상) |
| **V1** 워커가 `data.body` 를 제목으로 | **2 failed** | "페이로드를 showNotification(...) 로 그대로 넘긴다" · "schedule_id 가 빠진 페이로드면 …" | 검출 — 제목 완전 일치 단언 |
| **V2** `targetHashFor` 가 무조건 `?schedule_id=` + 값(→ `undefined`·`null`) | **1 failed** | "schedule_id 가 없거나 양의 정수가 아니면 일정 없는 브리핑 화면 주소" | 검출 — 경계 6경우 루프 |
| **V3** `applicationServerKey: publicKey`(문자열 그대로) | **1 failed** | "새 구독: … 본문은 PushSubscriptionIn 필드 그대로"(`Array.from` `[1,2,3]` 불일치) | 검출 |
| **V4** `open-briefing` 에 `schedule_id` 가 null 이면 해시 이동 생략 | **130 passed — 살아남음** | — | 테스트 틈: `open-briefing` 테스트는 `schedule_id: 12` 한 경우뿐(`push.test` 389~401행). 워커는 페이로드에 `schedule_id` 가 없으면 null 을 보내므로(§1 3행) 그때 페이지가 `#/briefings` 로 가야 한다는 단언이 없다. R-U8-1 |
| **V5** manifest `icons: []` | **1 failed** | "아이콘은 192·512 두 개이고 각각 실제 파일이다" | 검출 |
| M1 재실행(`fetch` 리스너 주입) | 2 failed | 구현자 2008 표와 이름·건수 동일("리스너 넷뿐"·"캐시 API 호출 없음") | 구현자 표 신뢰 |
| M10 재실행(기존 구독에도 POST) | 1 failed | "이미 구독돼 있으면 'already'" — 동일 | 〃 |
| M11 재실행(404 → 일반 실패) | 2 failed | "404 push_not_configured 면 'not_configured'"·"안내 한 줄" — 동일 | 〃 |
| M31 재실행(되돌리기 제거) | 3 failed | 재작업 증거 2017 과 이름·건수 동일 | 〃 (1차 2008 과의 합계 차 127→130 은 재작업 테스트 3건 추가 때문) |

## 9. 증거 규칙 (c) · R-U6-3 · registry · 03-log

- 구현자 증거 8파일 전부 `save_evidence.py` 머리줄 5개 + `# exit`(Write 옮겨 적기 0). 변이 출력은 vitest 전체(변이당 ~250~350행, `FAIL` 블록·스택 포함) — R-U6-3 "요약 없이" 충족. 스크립트 원문은 1차(`-2008-…-script.txt`, M1~M30)와 재작업(`-2017-…-script-rework.txt`, M31 추가) 둘 다 보존 — 두 파일 diff 는 M31 정의 1줄뿐(`-mutation-rework.txt` 가 M31 만 담는 것과 정합).
- registry U8 행 5개(251~255행) — 코드와 대조: 워커 동작·리스너·캐시 0 ✓ · manifest 값·아이콘·favicon·`index.html` ✓ · `push.ts` 절차·`already`·되돌리기·결과 코드 6종·`client.ts` 2·`briefingHref` ✓ · `PushSubscribe` 3상태·`BRIEFING_NOTICE` 16·R-U7-1·3·`WorkerMessages`·`BANNER_NOTICE` ✓ · 테스트 14+20+4 ✓. **어긋남 2곳**: 255행 끝 "→ 총 127건" 은 130(같은 칸 앞쪽은 "총 130건" 이라 자기모순) · "변이 30건" 은 M31 포함 31건(스크립트 `-rework` 경로도 함께). 248행 U7 행의 "알림 받기" 비활성 자리(U8)" 는 U8 이 채웠으므로 문구 갱신. R-U8-2.
- 03-log 140행 구현 결과 문단 — 내 확인과 일치하되 재작업 전 수치(`push.test.ts` 17 → 20, 127 → 130, 변이 30 → 31)이고 `devpage/sw.js` 차이 목록이 없다. 완료 항목에 적을 것은 R-U8-2.

## 10. 보안·범위

- `app/`·`alembic/`·`tests/`·`.github/` diff·untracked 빈 출력(`-grep.txt` 1절). 삭제 0(favicon 은 수정). `web/` 밖 변경은 위키 문서뿐.
- 비밀: VAPID 개인키·`BEGIN PRIVATE`·60자 이상 base64 문자열 0 — 적중은 테스트 더미 `'AQID'`(3바이트)와 주석(`-grep.txt` 4절). 외부 URL 0(`xmlns`·U4 `proxy.ts` 기존 제외). `/push-dev/`·`innerHTML`·`dangerouslySetInnerHTML` 0. `test-setup.ts` diff 0, `throw` 유지(결정 J 차단).
- 결정 I: API 응답 캐시 0, 워커 `fetch`·Cache API 0(§1 6행). security §5 "프론트에는 공개키만" ✓, 페이지로 가는 개인정보 0(§2).
- 원칙5: 화면 3·라우트 3 그대로(§1 15행). 원칙7: 서버 문장 변환 0(§1 14행), 경계 문장(상담 아님) 위반 어휘 0.

## 11. 소견

- **[권고] R-U8-1 · 테스트 틈 1개(내 변이 V4 생존).** `AppShell.tsx` 74~78행 `open-briefing` 분기에서 `scheduleId === null` 일 때 이동을 빼도 130 passed — `push.test` "알림을 눌러 온 {type:'open-briefing'}" 테스트(389~401행)가 `schedule_id: 12` 한 경우만 본다. 워커는 페이로드에 `schedule_id` 가 없으면 null 을 보내고(§1 3행) 새 창 경로는 `/#/briefings` 로 간다(`targetHashFor`)는데, 열린 창 경로의 같은 경계가 단언되지 않았다. 처방: 그 테스트에 `world.post({ type: 'open-briefing', schedule_id: null })` → `hash === '#/briefings'`·배너 없음 한 경우를 더한다(`briefingHref(null)` 경계를 배너 쪽은 이미 단언하고 있다, 375~387행). 커밋을 막지 않는다.
- **[권고] R-U8-2 · 03-log U8 완료 항목·registry·주석에 적을 것.** ① `devpage/sw.js` ↔ `public/sw.js` 차이 7항목(§3 표 또는 `-2024-verifier-u8-diff.txt` 2절 참조) — 결정 I "차이는 03-log U8 에 diff 로" 가 아직 비어 있다 ② registry 255행 "총 127건" → 130, "변이 30건" → 31(M31, 스크립트 `-script-rework.txt`), 248행 U7 행 "'알림 받기' 비활성 자리(U8)" → "U8 이 `PushSubscribe` 로 채움" ③ 03-log 140행 수치(`push.test.ts` 17 → 20, 127 → 130, 변이 30 → 31) ④ 구현자 선택 ①~③ 과 이 리뷰 판정(§6), R-U7-1·2·3·R-U4-4 닫힘(§5), R-U6-3 준수 ⑤ `client.ts` 142행 주석 "둘 다 미설정이면 404 `push_not_configured`" → GET 만 404(routes.py 86행 "둘 다" 는 전무·반쪽을 뜻한다; POST 420~430행은 설정 검사 없음) — 주석 1줄, 동작 영향 0 ⑥ 내 증거 6파일 경로 ⑦ "(U8 미커밋)" 5칸 → 해시 ⑧ Refs `P8-frontend U8 S3.6 R12 원칙5 원칙7 D7 R-U7-1 R-U7-2 R-U7-3 R-U4-4 R-U6-3 FIX-034`.
- **[권고] R-U8-3 · `notificationclick` 의 `list[0]` 이 앱이 아닌 같은 출처 창일 수 있다**(`sw.js` 59~65행, `includeUncontrolled:true`). 개발 환경에서 `/push-dev/`(`PUSH_DEV_PAGE_ENABLED`)나 `/api/docs` 탭이 가장 최근 포커스 창이면 그 창이 포커스되고 `open-briefing` 메시지는 그 페이지가 무시해 이동이 일어나지 않는다(devpage.js 36행은 메시지를 로그 줄로 찍을 뿐). 운영(dev 페이지 꺼짐)은 영향 0. 처방(택1): `list.find(c => !/\/push-dev\/|\/api\//.test(c.url))` 로 창을 고르고 없으면 `openWindow`, 또는 U10 사람 점검 항목 "알림 클릭 — 앱 탭·다른 탭·창 없음 3경우" 로 둔다. 커밋을 막지 않는다.
- 기록(소견 아님): ⓐ 구현자 선택 ② 미지원 안내가 클릭 때 — U10 에서 사용자가 보고 정한다(진입 시 `unsupported` → 버튼 비활성+안내로 바꾸는 것은 `PushSubscribe` 효과 1줄) ⓑ 서버 설정이 없을 때(404) 워커는 이미 등록된 채 남는다 — 캐시가 없어 해롭지 않다 ⓒ 기존 구독이 있으면 클릭 경로는 공개키 GET 1회 뒤 `'already'` — 진입 시 버튼이 비활성이라 실제로는 눌리지 않는다 ⓓ 개발 중 DB 를 비우거나 VAPID 키를 바꾸면 브라우저 구독만 남아 "알림 켜짐" 이지만 알림이 오지 않는다(99행 "이미 구독돼 있으면 알림 켜짐" 그대로이고 P7 만료 정리가 서버 쪽을 지운다; 사용자는 사이트 데이터 삭제로 푼다) — U10 점검 안내에 한 줄 ⓔ 아이콘 SVG 의 "관" 글자는 기기 글꼴(`Apple SD Gothic Neo`/`Malgun Gothic`/sans-serif)에 의존한다 — 68행대로 Chrome Application → Manifest 에서 U10 확인 ⓕ `sw.test` 설명의 "tokens.css 의 primary(#171717)" 는 `tokens.css` 78행 `oklch(0.205 0 0)` 의 hex 근사이고 단언은 manifest 값에만 — 문제 없음.

## 12. 판정 근거 요약

- 판정 명령 재실행 exit 0, 130 passed, 번들 해시 구현자 재작업·메인 세션 2017 과 동일, `dist/` 워커·manifest 가 `public/` 과 바이트 동일(`-judge.txt`).
- 99행·결정 H·I·68행 계약 16항목 전부 코드 위치 + 값 단언 테스트 + 변이 검출(§1). 서버 페이로드 키 1:1·`tag` 형식·열린 창에는 `schedule_id` 만(§2). 원본 무변경·복사 줄 동일·차이 7항목(§3). 되돌리기 코드·테스트 3·M31(§4). 이월 4건 닫힘(§5). 구현자 선택 3개 계획 모순 0(§6).
- 내 변이 5건 중 4건 검출, V4 생존은 테스트 틈(R-U8-1). 구현자 M1·M10·M11·M31 재실행 동일(§8).
- R-U0-3 충족(§7), 증거 통로·R-U6-3 준수(§9), 보안·범위 위반 0(§10).
- **[필수] 0 → 통과.** R-U8-1(테스트 1경우)·R-U8-3(창 고르기 1줄 또는 U10 항목)은 이 커밋에서 고쳐도, U9·U10 에 끼워도 된다. R-U8-2 는 03-log 완료 항목·registry 갱신(메인 세션).
