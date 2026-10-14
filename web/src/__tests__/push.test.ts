// U8 푸시 구독(push.ts) · 브리핑 화면 "알림 받기" · 인앱 배너(AppShell).
// 실제 푸시 서비스·네트워크 없음 — Notification·PushManager·navigator.serviceWorker·fetch 전부 가짜 (결정 J).
import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from '@/App'
import { BANNER_NOTICE } from '@/components/AppShell'
import { getPushStatus, subscribeToPush, urlBase64ToUint8Array } from '@/push'
import BriefingScreen, { BRIEFING_NOTICE } from '@/screens/BriefingScreen'
import { installFakeMatchMedia } from './helpers'

type Handler = (url: string, init: RequestInit) => Response | Promise<Response>

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

function installFetch(table: Record<string, Handler>) {
  const fn = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const key = `${init?.method ?? 'GET'} ${String(input)}`
    if (!table[key]) throw new Error(`예상하지 못한 요청: ${key}`)
    return Promise.resolve(table[key](String(input), init ?? {}))
  })
  vi.stubGlobal('fetch', fn)
  return fn
}

function callsTo(fn: ReturnType<typeof installFetch>, method: string, url: string) {
  return fn.mock.calls.filter(([u, init]) => String(u) === url && ((init as RequestInit)?.method ?? 'GET') === method)
}

const VAPID_KEY = 'AQID' // base64url → 바이트 [1, 2, 3]
const SUB_JSON = { endpoint: 'https://push.example/abc', expirationTime: null, keys: { p256dh: 'P256_KEY', auth: 'AUTH_KEY' } }

interface PushWorld {
  order: string[]
  permission: ReturnType<typeof vi.fn>
  register: ReturnType<typeof vi.fn>
  subscribe: ReturnType<typeof vi.fn>
  unsubscribe: ReturnType<typeof vi.fn>
  getSubscription: ReturnType<typeof vi.fn>
  /** 서비스 워커 컨테이너로 메시지를 보낸다(워커가 하는 일). */
  post: (data: unknown) => void
}

/** 웹푸시를 지원하는 브라우저를 흉내 낸다. existing=true 면 이미 구독돼 있다. */
function installPushBrowser(options: { permission?: string; existing?: boolean; subscribeError?: boolean; unsubscribeError?: boolean } = {}): PushWorld {
  const order: string[] = []
  const listeners = new Set<(e: MessageEvent) => void>()
  let current: object | null = null // 브라우저에 남아 있는 구독
  const unsubscribe = vi.fn(() => {
    order.push('unsubscribe')
    if (options.unsubscribeError) return Promise.reject(new Error('unsubscribe failed'))
    current = null
    return Promise.resolve(true)
  })
  const sub = { toJSON: () => SUB_JSON, unsubscribe }
  if (options.existing) current = sub
  const getSubscription = vi.fn(() => {
    order.push('getSubscription')
    return Promise.resolve(current)
  })
  const subscribe = vi.fn(() => {
    order.push('subscribe')
    if (options.subscribeError) return Promise.reject(new Error('denied by push service'))
    current = sub
    return Promise.resolve(sub)
  })
  const registration = { pushManager: { getSubscription, subscribe } }
  const register = vi.fn(() => {
    order.push('register')
    return Promise.resolve(registration)
  })
  const permission = vi.fn(() => {
    order.push('permission')
    return Promise.resolve(options.permission ?? 'granted')
  })
  vi.stubGlobal('Notification', { requestPermission: permission })
  vi.stubGlobal('PushManager', class {})
  Object.defineProperty(navigator, 'serviceWorker', {
    configurable: true,
    value: {
      register,
      ready: Promise.resolve(registration),
      getRegistration: vi.fn(() => Promise.resolve(registration)),
      addEventListener: (_: string, fn: (e: MessageEvent) => void) => listeners.add(fn),
      removeEventListener: (_: string, fn: (e: MessageEvent) => void) => listeners.delete(fn),
    },
  })
  return {
    order,
    permission,
    register,
    subscribe,
    unsubscribe,
    getSubscription,
    post: (data) => {
      act(() => listeners.forEach((fn) => fn({ data } as MessageEvent)))
    },
  }
}

beforeEach(() => {
  window.history.replaceState(null, '', '#/briefings')
})

afterEach(() => {
  vi.unstubAllGlobals()
  Reflect.deleteProperty(navigator, 'serviceWorker')
  window.history.replaceState(null, '', '#/chat')
})

describe('urlBase64ToUint8Array', () => {
  it('base64url(-, _, 패딩 없음)을 바이트로 바꾼다', () => {
    expect(Array.from(urlBase64ToUint8Array('AQID'))).toEqual([1, 2, 3])
    expect(Array.from(urlBase64ToUint8Array('AQI'))).toEqual([1, 2]) // 패딩 1칸 보충
    expect(Array.from(urlBase64ToUint8Array('-__-'))).toEqual([251, 255, 254]) // - → +, _ → /
  })
})

describe('subscribeToPush 절차', () => {
  it('새 구독: 권한 → 등록(/sw.js) → 공개키 → 구독 → 서버 저장 순서이고, 본문은 PushSubscriptionIn 필드 그대로', async () => {
    const world = installPushBrowser()
    const fetchFn = installFetch({
      'GET /api/push/vapid-public-key': () => {
        world.order.push('GET key')
        return json({ public_key: VAPID_KEY })
      },
      'POST /api/push/subscriptions': () => {
        world.order.push('POST subscription')
        return json({ id: 1, created: true })
      },
    })
    expect(await subscribeToPush()).toBe('subscribed')
    expect(world.order).toEqual(['permission', 'register', 'GET key', 'getSubscription', 'subscribe', 'POST subscription'])
    expect(world.register).toHaveBeenCalledWith('/sw.js')
    const arg = world.subscribe.mock.calls[0][0] as { userVisibleOnly: boolean; applicationServerKey: Uint8Array }
    expect(arg.userVisibleOnly).toBe(true)
    expect(Array.from(arg.applicationServerKey)).toEqual([1, 2, 3])
    const posts = callsTo(fetchFn, 'POST', '/api/push/subscriptions')
    expect(posts).toHaveLength(1)
    expect(JSON.parse(String((posts[0][1] as RequestInit).body))).toEqual({
      endpoint: 'https://push.example/abc',
      keys: { p256dh: 'P256_KEY', auth: 'AUTH_KEY' },
      expirationTime: null,
    })
  })

  it('이미 구독돼 있으면 "already" — 구독도 서버 저장(POST)도 하지 않는다', async () => {
    const world = installPushBrowser({ existing: true })
    const fetchFn = installFetch({ 'GET /api/push/vapid-public-key': () => json({ public_key: VAPID_KEY }) })
    expect(await subscribeToPush()).toBe('already')
    expect(world.subscribe).not.toHaveBeenCalled()
    expect(callsTo(fetchFn, 'POST', '/api/push/subscriptions')).toHaveLength(0)
  })

  it('권한이 허용되지 않으면 "denied" — 등록·공개키·구독이 없다', async () => {
    const world = installPushBrowser({ permission: 'denied' })
    const fetchFn = installFetch({})
    expect(await subscribeToPush()).toBe('denied')
    expect(world.register).not.toHaveBeenCalled()
    expect(world.subscribe).not.toHaveBeenCalled()
    expect(fetchFn).not.toHaveBeenCalled()
  })

  it('404 push_not_configured 면 "not_configured" — 구독·저장 없이 멈춘다', async () => {
    const world = installPushBrowser()
    const fetchFn = installFetch({
      'GET /api/push/vapid-public-key': () => json({ detail: { code: 'push_not_configured' } }, 404),
    })
    expect(await subscribeToPush()).toBe('not_configured')
    expect(world.getSubscription).not.toHaveBeenCalled()
    expect(world.subscribe).not.toHaveBeenCalled()
    expect(fetchFn).toHaveBeenCalledTimes(1)
  })

  it('다른 404(코드가 다름)나 5xx 는 "not_configured" 가 아니라 "failed"', async () => {
    for (const [status, code] of [[404, 'not_found'], [500, 'push_not_configured']] as const) {
      installPushBrowser()
      installFetch({ 'GET /api/push/vapid-public-key': () => json({ detail: { code } }, status) })
      expect(await subscribeToPush()).toBe('failed')
      vi.unstubAllGlobals()
    }
  })

  it('구독 실패·서버 저장 실패는 "failed"', async () => {
    installPushBrowser({ subscribeError: true })
    installFetch({ 'GET /api/push/vapid-public-key': () => json({ public_key: VAPID_KEY }) })
    expect(await subscribeToPush()).toBe('failed')
    vi.unstubAllGlobals()

    installPushBrowser()
    installFetch({
      'GET /api/push/vapid-public-key': () => json({ public_key: VAPID_KEY }),
      'POST /api/push/subscriptions': () => json({ detail: { code: 'x' } }, 500),
    })
    expect(await subscribeToPush()).toBe('failed')
  })

  it('서버 저장(POST)이 실패하면 브라우저 구독을 unsubscribe 1회로 되돌리고 "failed" — 404 push_not_configured 도 같다', async () => {
    for (const [status, code] of [[500, 'x'], [404, 'push_not_configured']] as const) {
      const world = installPushBrowser()
      installFetch({
        'GET /api/push/vapid-public-key': () => json({ public_key: VAPID_KEY }),
        'POST /api/push/subscriptions': () => json({ detail: { code } }, status),
      })
      expect(await subscribeToPush()).toBe('failed')
      expect(world.unsubscribe).toHaveBeenCalledTimes(1)
      vi.unstubAllGlobals()
    }
  })

  it('저장 실패 뒤 다음 클릭은 처음부터 다시 — subscribe 재호출·POST 재시도(이번엔 성공)', async () => {
    const world = installPushBrowser()
    let n = 0
    const fetchFn = installFetch({
      'GET /api/push/vapid-public-key': () => json({ public_key: VAPID_KEY }),
      'POST /api/push/subscriptions': () => (n++ === 0 ? json({ detail: { code: 'x' } }, 500) : json({ id: 1, created: true })),
    })
    expect(await subscribeToPush()).toBe('failed')
    expect(await subscribeToPush()).toBe('subscribed') // "already" 로 끝나지 않는다
    expect(world.subscribe).toHaveBeenCalledTimes(2)
    expect(callsTo(fetchFn, 'POST', '/api/push/subscriptions')).toHaveLength(2)
  })

  it('unsubscribe 자체가 실패해도 예외 없이 "failed"', async () => {
    const world = installPushBrowser({ unsubscribeError: true })
    installFetch({
      'GET /api/push/vapid-public-key': () => json({ public_key: VAPID_KEY }),
      'POST /api/push/subscriptions': () => json({ detail: { code: 'x' } }, 500),
    })
    expect(await subscribeToPush()).toBe('failed')
    expect(world.unsubscribe).toHaveBeenCalledTimes(1)
  })

  it('미지원 브라우저(serviceWorker·PushManager·Notification 없음)면 "unsupported" — 네트워크 0', async () => {
    const fetchFn = installFetch({})
    expect(await subscribeToPush()).toBe('unsupported')
    expect(fetchFn).not.toHaveBeenCalled()
  })
})

describe('getPushStatus', () => {
  it('미지원 · 구독 없음 · 구독 있음을 가른다(권한 창·네트워크 없음)', async () => {
    expect(await getPushStatus()).toBe('unsupported')
    installPushBrowser()
    expect(await getPushStatus()).toBe('unsubscribed')
    vi.unstubAllGlobals()
    Reflect.deleteProperty(navigator, 'serviceWorker')
    const world = installPushBrowser({ existing: true })
    expect(await getPushStatus()).toBe('subscribed')
    expect(world.permission).not.toHaveBeenCalled()
    expect(world.register).not.toHaveBeenCalled()
  })
})

describe('브리핑 화면 "알림 받기" 버튼', () => {
  function briefingFetch(extra: Record<string, Handler> = {}) {
    return installFetch({ 'GET /api/briefings': () => json([]), ...extra })
  }

  it('미구독 → 진행 중(비활성) → 켜짐(비활성) 세 상태', async () => {
    installPushBrowser()
    let finish: () => void = () => {}
    const fetchFn = briefingFetch({
      'GET /api/push/vapid-public-key': () => json({ public_key: VAPID_KEY }),
      'POST /api/push/subscriptions': () =>
        new Promise<Response>((resolve) => {
          finish = () => resolve(json({ id: 1, created: true }))
        }),
    })
    render(createElement(BriefingScreen))
    const button = await screen.findByRole('button', { name: BRIEFING_NOTICE.subscribe })
    expect(button).toBeEnabled()
    await userEvent.click(button)
    const busy = await screen.findByRole('button', { name: BRIEFING_NOTICE.subscribing })
    expect(busy).toBeDisabled()
    await waitFor(() => expect(callsTo(fetchFn, 'POST', '/api/push/subscriptions')).toHaveLength(1)) // 저장 요청이 나간 뒤에도 진행 중
    expect(screen.getByRole('button', { name: BRIEFING_NOTICE.subscribing })).toBeDisabled()
    await act(async () => finish())
    const on = await screen.findByRole('button', { name: BRIEFING_NOTICE.subscribed })
    expect(on).toBeDisabled()
    expect(screen.queryByRole('button', { name: BRIEFING_NOTICE.subscribe })).toBeNull()
  })

  it('들어올 때 이미 구독돼 있으면 곧바로 "알림 켜짐"(비활성) — 클릭 없이, 서버 저장 없이', async () => {
    installPushBrowser({ existing: true })
    const fetchFn = briefingFetch()
    render(createElement(BriefingScreen))
    expect(await screen.findByRole('button', { name: BRIEFING_NOTICE.subscribed })).toBeDisabled()
    expect(callsTo(fetchFn, 'POST', '/api/push/subscriptions')).toHaveLength(0)
  })

  it('안내 한 줄: 권한 거부 · 서버 미설정 · 미지원 · 실패 — 버튼은 다시 "알림 받기"(활성)', async () => {
    const cases: { setup: () => void; notice: string }[] = [
      { setup: () => installPushBrowser({ permission: 'denied' }), notice: BRIEFING_NOTICE.pushDenied },
      {
        setup: () => {
          installPushBrowser()
          briefingFetch({ 'GET /api/push/vapid-public-key': () => json({ detail: { code: 'push_not_configured' } }, 404) })
        },
        notice: BRIEFING_NOTICE.pushNotConfigured,
      },
      {
        setup: () => {
          installPushBrowser()
          briefingFetch({ 'GET /api/push/vapid-public-key': () => json({ detail: { code: 'x' } }, 500) })
        },
        notice: BRIEFING_NOTICE.pushFailed,
      },
      { setup: () => undefined, notice: BRIEFING_NOTICE.pushUnsupported }, // jsdom 기본 = 미지원
    ]
    for (const c of cases) {
      c.setup()
      if (!vi.isMockFunction(globalThis.fetch)) briefingFetch()
      const { unmount } = render(createElement(BriefingScreen))
      await userEvent.click(await screen.findByRole('button', { name: BRIEFING_NOTICE.subscribe }))
      expect(await screen.findByTestId('push-note')).toHaveTextContent(c.notice)
      expect(screen.getByRole('button', { name: BRIEFING_NOTICE.subscribe })).toBeEnabled()
      unmount()
      vi.unstubAllGlobals()
      Reflect.deleteProperty(navigator, 'serviceWorker')
    }
  })

  it('/push-dev/ 링크가 없다', async () => {
    installPushBrowser()
    briefingFetch()
    render(createElement(BriefingScreen))
    await screen.findByRole('button', { name: BRIEFING_NOTICE.subscribe })
    expect(document.querySelector('a[href*="push-dev"]')).toBeNull()
  })
})

describe('인앱 배너 (결정 H)', () => {
  beforeEach(() => {
    installFakeMatchMedia(1280) // 데스크톱 폭 — 사이드바 고정, 서랍 없음
  })

  function appFetch() {
    return installFetch({ 'GET /api/briefings': () => json([]), 'GET /api/persons': () => json([]) })
  }

  it('{type:"briefing", schedule_id} 를 받으면 한 줄 배너 — 누르면 #/briefings?schedule_id=N, 누른 뒤 사라진다', async () => {
    const world = installPushBrowser()
    appFetch()
    render(createElement(App))
    await screen.findByRole('button', { name: BRIEFING_NOTICE.subscribe })
    expect(screen.queryByTestId('push-banner')).toBeNull()

    world.post({ type: 'briefing', schedule_id: 9 })
    const banner = await screen.findByTestId('push-banner')
    expect(banner).toHaveTextContent(BANNER_NOTICE.text)
    const link = screen.getByRole('link', { name: BANNER_NOTICE.open })
    expect(link).toHaveAttribute('href', '#/briefings?schedule_id=9')

    await userEvent.click(link)
    await waitFor(() => expect(window.location.hash).toBe('#/briefings?schedule_id=9'))
    await waitFor(() => expect(screen.queryByTestId('push-banner')).toBeNull())
  })

  it('닫기 버튼으로 닫는다(주소는 그대로)', async () => {
    const world = installPushBrowser()
    appFetch()
    render(createElement(App))
    await screen.findByRole('button', { name: BRIEFING_NOTICE.subscribe })
    world.post({ type: 'briefing', schedule_id: 3 })
    await screen.findByTestId('push-banner')
    await userEvent.click(screen.getByRole('button', { name: BANNER_NOTICE.close }))
    expect(screen.queryByTestId('push-banner')).toBeNull()
    expect(window.location.hash).toBe('#/briefings')
  })

  it('schedule_id 가 없으면 일정 없는 브리핑 주소, 모양이 다른 메시지는 무시한다', async () => {
    const world = installPushBrowser()
    appFetch()
    render(createElement(App))
    await screen.findByRole('button', { name: BRIEFING_NOTICE.subscribe })
    world.post({ type: 'other', schedule_id: 1 })
    world.post('briefing')
    world.post(null)
    expect(screen.queryByTestId('push-banner')).toBeNull()
    world.post({ type: 'briefing', schedule_id: null })
    await screen.findByTestId('push-banner')
    expect(screen.getByRole('link', { name: BANNER_NOTICE.open })).toHaveAttribute('href', '#/briefings')
  })

  it('알림을 눌러 온 {type:"open-briefing"} 은 배너 없이 바로 그 일정 주소로 간다', async () => {
    const world = installPushBrowser()
    window.history.replaceState(null, '', '#/chat')
    installFetch({
      'GET /api/briefings': () => json([]),
      'GET /api/persons': () => json([]),
      'GET /api/questions/pending': () => json([]),
    })
    render(createElement(App))
    world.post({ type: 'open-briefing', schedule_id: 12 })
    await waitFor(() => expect(window.location.hash).toBe('#/briefings?schedule_id=12'))
    expect(screen.queryByTestId('push-banner')).toBeNull()
  })
})
