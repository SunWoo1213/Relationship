// Refs: P8-frontend U8 결정 H·I -- 제품 서비스 워커(범위 /). 단일 파일이라 빌드에 그대로 복사된다.
// 하는 일은 셋뿐이다: push 를 받아 알림을 띄우고, 알림을 누르면 그 일정의 브리핑으로 가고, 열린 창에 알린다.
// 캐시를 쓰지 않고 요청 가로채기 리스너도 없다(결정 I) -- 화면·API 응답은 항상 네트워크에서 온다.
// 페이로드 해석은 app/push/devpage/sw.js 에서 복사했다(원본은 고치지 않는다).
// 알림 title·body 는 서버가 만든 문장 그대로 쓴다(원칙7). 열린 창에는 schedule_id 만 알린다.

function readPayload(event) {
  try {
    return event.data ? event.data.json() : {};
  } catch (e) {
    return {};
  }
}

// 서버 페이로드({title, body, tag, schedule_id}) -> showNotification 인자.
function notificationFor(data) {
  var scheduleId = data.schedule_id === undefined ? null : data.schedule_id;
  return {
    title: data.title || "알림",
    options: { body: data.body || "", tag: data.tag, data: { schedule_id: scheduleId } },
    scheduleId: scheduleId
  };
}

// 알림을 눌렀을 때 새 창이 열 주소. schedule_id 가 양의 정수가 아니면 일정 없이 브리핑 화면.
function targetHashFor(scheduleId) {
  if (typeof scheduleId === "number" && Number.isInteger(scheduleId) && scheduleId > 0) {
    return "/#/briefings?schedule_id=" + scheduleId;
  }
  return "/#/briefings";
}

self.addEventListener("install", function () {
  self.skipWaiting();
});

self.addEventListener("activate", function (event) {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("push", function (event) {
  var shown = notificationFor(readPayload(event));
  event.waitUntil(
    self.registration.showNotification(shown.title, shown.options).then(function () {
      return self.clients.matchAll({ type: "window", includeUncontrolled: true });
    }).then(function (list) {
      list.forEach(function (client) {
        client.postMessage({ type: "briefing", schedule_id: shown.scheduleId });
      });
    })
  );
});

self.addEventListener("notificationclick", function (event) {
  event.notification.close();
  var info = event.notification.data;
  var scheduleId = info && info.schedule_id !== undefined ? info.schedule_id : null;
  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(function (list) {
      // includeUncontrolled 는 같은 출처 창을 전부 준다 -- 앱이 아닌 창(개발용 확인 페이지 · /api/docs 등)은
      // 건너뛰고 앱 창(경로가 "/" 인 창)만 고른다. 앱 창이 없으면 새 창을 연다(R-U8-3).
      var client = list.find(function (c) {
        return new URL(c.url).pathname === "/";
      });
      if (client) {
        return Promise.resolve(client.focus()).then(function () {
          client.postMessage({ type: "open-briefing", schedule_id: scheduleId });
        });
      }
      return self.clients.openWindow(targetHashFor(scheduleId));
    })
  );
});
