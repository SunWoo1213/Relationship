// 푸시 구독 (결정 H) — 브리핑 화면 "알림 받기" 가 부른다. 화면을 만들지 않는 순수 로직이다.
// 절차(app/push/devpage/devpage.js 와 같은 순서): 권한 → 서비스 워커 등록 → 공개키 → 구독 → 서버 저장.
// 구독 해제는 만들지 않는다(결정 H). 서버가 준 문장은 쓰지 않는다 — 결과는 코드(outcome)로만 돌려준다.
import { ApiError, getVapidPublicKey, postPushSubscription } from '@/api/client'
import type { PushSubscriptionIn } from '@/api/types'

export const SERVICE_WORKER_URL = '/sw.js'

/** 진입 시 상태. 'unsupported' 는 이 브라우저가 웹푸시를 못 쓴다는 뜻. */
export type PushStatus = 'unsupported' | 'unsubscribed' | 'subscribed'

export type SubscribeOutcome =
  | 'subscribed' // 새로 구독하고 서버에 저장했다
  | 'already' // 브라우저에 이미 구독이 있다 — 서버 재등록은 하지 않는다
  | 'denied' // 알림 권한이 허용되지 않았다
  | 'not_configured' // 404 push_not_configured
  | 'unsupported'
  | 'failed'

export function isPushSupported(): boolean {
  return (
    typeof navigator !== 'undefined' &&
    'serviceWorker' in navigator &&
    typeof window !== 'undefined' &&
    'PushManager' in window &&
    'Notification' in window
  )
}

/** VAPID 공개키(base64url) → applicationServerKey. devpage.js 의 변환을 옮겼다. */
export function urlBase64ToUint8Array(base64url: string): Uint8Array<ArrayBuffer> {
  const padding = '='.repeat((4 - (base64url.length % 4)) % 4)
  const base64 = (base64url + padding).replace(/-/g, '+').replace(/_/g, '/')
  const raw = atob(base64)
  const out = new Uint8Array(raw.length)
  for (let i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i)
  return out
}

/** 화면에 들어올 때 이미 구독돼 있는지만 본다(권한 창·등록·네트워크 없음). */
export async function getPushStatus(): Promise<PushStatus> {
  if (!isPushSupported()) return 'unsupported'
  try {
    const registration = await navigator.serviceWorker.getRegistration()
    if (!registration) return 'unsubscribed'
    return (await registration.pushManager.getSubscription()) ? 'subscribed' : 'unsubscribed'
  } catch {
    return 'unsubscribed'
  }
}

export async function subscribeToPush(): Promise<SubscribeOutcome> {
  if (!isPushSupported()) return 'unsupported'
  try {
    // ① 권한
    const permission = await Notification.requestPermission()
    if (permission !== 'granted') return 'denied'

    // ② 서비스 워커 등록(범위 /)
    const registration = await navigator.serviceWorker.register(SERVICE_WORKER_URL)
    await navigator.serviceWorker.ready

    // ③ 공개키 — 서버에 푸시 설정이 없으면 404 push_not_configured
    let publicKey: string
    try {
      publicKey = (await getVapidPublicKey()).public_key
    } catch (error) {
      if (error instanceof ApiError && error.status === 404 && error.code === 'push_not_configured') {
        return 'not_configured'
      }
      return 'failed'
    }

    // ④ 이미 구독돼 있으면 켜진 상태로 본다(서버 재등록 없음)
    if (await registration.pushManager.getSubscription()) return 'already'

    // ⑤ 새 구독 → 서버 저장(PushSubscriptionIn 필드 그대로)
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(publicKey),
    })
    const json = subscription.toJSON()
    if (!json.endpoint || !json.keys?.p256dh || !json.keys.auth) return 'failed'
    const body: PushSubscriptionIn = {
      endpoint: json.endpoint,
      keys: { p256dh: json.keys.p256dh, auth: json.keys.auth },
      expirationTime: json.expirationTime ?? null,
    }
    try {
      await postPushSubscription(body)
    } catch {
      // 서버 저장이 실패하면 브라우저 구독을 되돌린다 — 다음 클릭이 처음부터 다시 하게(저장 안 된 구독이 "이미 켜짐"으로 남지 않게).
      try {
        await subscription.unsubscribe()
      } catch {
        // 되돌리기 실패는 삼킨다(안내는 그대로 failed)
      }
      return 'failed'
    }
    return 'subscribed'
  } catch {
    return 'failed'
  }
}
