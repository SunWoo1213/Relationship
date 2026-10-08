// Refs: P7-push U6 결정 A -- 개발·확인 전용 서비스 워커(범위 /push-dev/).
// push 이벤트에서 알림을 띄우고, 열린 페이지에는 수신 시각·schedule_id·tag 만 알린다.
// 인물 이름·제안 문구(title/body)는 페이지로 보내지 않는다.
self.addEventListener("push", function (event) {
  var data = {};
  try {
    data = event.data ? event.data.json() : {};
  } catch (e) {
    data = {};
  }
  var title = data.title || "알림";
  var options = { body: data.body || "", tag: data.tag };
  var info = {
    received_at: new Date().toISOString(),
    schedule_id: data.schedule_id === undefined ? null : data.schedule_id,
    tag: data.tag === undefined ? null : data.tag
  };
  event.waitUntil(
    self.registration.showNotification(title, options).then(function () {
      return self.clients.matchAll({ type: "window", includeUncontrolled: true });
    }).then(function (list) {
      list.forEach(function (client) {
        client.postMessage(info);
      });
    })
  );
});

self.addEventListener("notificationclick", function (event) {
  event.notification.close();
  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(function (list) {
      if (list.length > 0) {
        return list[0].focus();
      }
      return self.clients.openWindow("/push-dev/");
    })
  );
});
