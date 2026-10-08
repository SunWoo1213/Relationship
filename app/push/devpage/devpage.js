// Refs: P7-push U6 결정 A -- 개발·확인 전용 구독 스크립트(제품 화면 아님).
// 흐름: 버튼 클릭 -> 알림 권한 -> 서비스 워커 등록 -> 공개키 조회 -> 구독 -> 서버 저장.
(function () {
  "use strict";

  var statusEl = document.getElementById("status");
  var logEl = document.getElementById("log");
  var button = document.getElementById("subscribe");

  function setStatus(text) {
    statusEl.textContent = text;
  }

  function urlBase64ToUint8Array(base64url) {
    var padding = "=".repeat((4 - (base64url.length % 4)) % 4);
    var base64 = (base64url + padding).replace(/-/g, "+").replace(/_/g, "/");
    var raw = atob(base64);
    var out = new Uint8Array(raw.length);
    for (var i = 0; i < raw.length; i++) {
      out[i] = raw.charCodeAt(i);
    }
    return out;
  }

  function addLog(info) {
    var li = document.createElement("li");
    li.textContent =
      info.received_at + " schedule_id=" + info.schedule_id + " tag=" + info.tag;
    logEl.appendChild(li);
  }

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.addEventListener("message", function (event) {
      addLog(event.data || {});
    });
  }

  async function subscribe() {
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
      setStatus("이 브라우저는 웹푸시를 지원하지 않습니다.");
      return;
    }
    setStatus("알림 권한을 요청하는 중");
    var permission = await Notification.requestPermission();
    if (permission !== "granted") {
      setStatus("알림 권한이 허용되지 않았습니다: " + permission);
      return;
    }
    setStatus("서비스 워커를 등록하는 중");
    var registration = await navigator.serviceWorker.register("/push-dev/sw.js", {
      scope: "/push-dev/"
    });
    await navigator.serviceWorker.ready;

    setStatus("공개키를 가져오는 중");
    var keyResponse = await fetch("/push/vapid-public-key");
    if (!keyResponse.ok) {
      setStatus("공개키를 가져오지 못했습니다. 상태 코드: " + keyResponse.status);
      return;
    }
    var keyBody = await keyResponse.json();

    setStatus("구독을 만드는 중");
    var subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(keyBody.public_key)
    });

    setStatus("구독을 저장하는 중");
    var saveResponse = await fetch("/push/subscriptions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(subscription.toJSON())
    });
    if (!saveResponse.ok) {
      setStatus("구독을 저장하지 못했습니다. 상태 코드: " + saveResponse.status);
      return;
    }
    setStatus("구독 완료. 알림을 기다리는 중");
  }

  button.addEventListener("click", function () {
    subscribe().catch(function (error) {
      setStatus("오류: " + (error && error.name ? error.name : "unknown"));
    });
  });
})();
