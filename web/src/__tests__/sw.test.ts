// U8 서비스 워커(web/public/sw.js). 워커 파일을 ?raw 로 읽어 가짜 self(listeners·registration·clients) 안에서 평가한다.
// 실제 워커·푸시 서비스·네트워크는 쓰지 않는다 (결정 J).
import { describe, expect, it, vi } from 'vitest'
import swSource from '../../public/sw.js?raw'
import manifestSource from '../../public/manifest.webmanifest?raw'
import indexHtml from '../../index.html?raw'
import favicon from '../../public/favicon.svg?raw'
import icon192 from '../../public/icon-192.svg?raw'
import icon512 from '../../public/icon-512.svg?raw'

type Listener = (event: FakeEvent) => void

interface FakeClient {
  focus: ReturnType<typeof vi.fn>
  postMessage: ReturnType<typeof vi.fn>
}

interface FakeEvent {
  data?: { json: () => unknown } | null
  notification?: { close: ReturnType<typeof vi.fn>; data: unknown }
  waitUntil: (p: Promise<unknown>) => void
}

function makeClient(): FakeClient {
  return { focus: vi.fn(() => Promise.resolve()), postMessage: vi.fn() }
}

/** 워커 코드를 가짜 self 로 평가한다. matchAll 이 돌려줄 창 목록을 인자로 받는다. */
function loadWorker(windows: FakeClient[]) {
  const listeners = new Map<string, Listener[]>()
  const self = {
    addEventListener: (type: string, fn: Listener) => {
      listeners.set(type, [...(listeners.get(type) ?? []), fn])
    },
    skipWaiting: vi.fn(),
    registration: { showNotification: vi.fn(() => Promise.resolve()) },
    clients: {
      matchAll: vi.fn(() => Promise.resolve(windows)),
      claim: vi.fn(() => Promise.resolve()),
      openWindow: vi.fn(() => Promise.resolve(null)),
    },
  }
  new Function('self', swSource)(self)

  /** 이벤트를 발사하고 waitUntil 에 넘긴 약속이 끝날 때까지 기다린다. */
  async function fire(type: string, event: Partial<FakeEvent> = {}) {
    let pending: Promise<unknown> = Promise.resolve()
    const full: FakeEvent = { waitUntil: (p) => (pending = p), ...event }
    for (const fn of listeners.get(type) ?? []) fn(full)
    await pending
  }
  return { self, listeners, fire }
}

function pushEvent(payload: unknown): Partial<FakeEvent> {
  return { data: { json: () => payload } }
}

function clickEvent(data: unknown) {
  const notification = { close: vi.fn(), data }
  return { notification, event: { notification } as Partial<FakeEvent> }
}

describe('push 이벤트', () => {
  it('페이로드를 showNotification(title, {body, tag, data:{schedule_id}}) 로 그대로 넘긴다', async () => {
    const w = loadWorker([])
    await w.fire('push', pushEvent({ title: '  김팀장 회의 30분 전 ', body: ' 지난번 지적 반복 & "제안" ', tag: 'schedule-12', schedule_id: 12, ttl: 600 }))
    expect(w.self.registration.showNotification).toHaveBeenCalledTimes(1)
    expect(w.self.registration.showNotification).toHaveBeenCalledWith('  김팀장 회의 30분 전 ', {
      body: ' 지난번 지적 반복 & "제안" ',
      tag: 'schedule-12',
      data: { schedule_id: 12 },
    })
  })

  it('열린 모든 창에 {type:"briefing", schedule_id} 만 보낸다(title·body 는 보내지 않는다)', async () => {
    const a = makeClient()
    const b = makeClient()
    const w = loadWorker([a, b])
    await w.fire('push', pushEvent({ title: '제목', body: '본문', tag: 'schedule-7', schedule_id: 7 }))
    expect(w.self.clients.matchAll).toHaveBeenCalledWith({ type: 'window', includeUncontrolled: true })
    for (const c of [a, b]) {
      expect(c.postMessage).toHaveBeenCalledTimes(1)
      expect(c.postMessage).toHaveBeenCalledWith({ type: 'briefing', schedule_id: 7 })
    }
  })

  it('schedule_id 가 빠진 페이로드면 data.schedule_id 와 메시지 모두 null', async () => {
    const c = makeClient()
    const w = loadWorker([c])
    await w.fire('push', pushEvent({ title: '제목', body: '본문', tag: 't' }))
    expect(w.self.registration.showNotification).toHaveBeenCalledWith('제목', { body: '본문', tag: 't', data: { schedule_id: null } })
    expect(c.postMessage).toHaveBeenCalledWith({ type: 'briefing', schedule_id: null })
  })

  it('JSON 을 못 읽거나 데이터가 없으면 기본 제목 "알림"·빈 본문으로 띄운다', async () => {
    const w = loadWorker([])
    await w.fire('push', { data: { json: () => { throw new SyntaxError('bad') } } })
    await w.fire('push', { data: null })
    expect(w.self.registration.showNotification).toHaveBeenNthCalledWith(1, '알림', { body: '', tag: undefined, data: { schedule_id: null } })
    expect(w.self.registration.showNotification).toHaveBeenNthCalledWith(2, '알림', { body: '', tag: undefined, data: { schedule_id: null } })
  })
})

describe('notificationclick 이벤트', () => {
  it('열린 창이 있으면 알림을 닫고 첫 창을 focus 한 뒤 {type:"open-briefing", schedule_id} 를 보낸다(새 창 없음)', async () => {
    const first = makeClient()
    const second = makeClient()
    const w = loadWorker([first, second])
    const { notification, event } = clickEvent({ schedule_id: 12 })
    await w.fire('notificationclick', event)
    expect(notification.close).toHaveBeenCalledTimes(1)
    expect(first.focus).toHaveBeenCalledTimes(1)
    expect(first.postMessage).toHaveBeenCalledWith({ type: 'open-briefing', schedule_id: 12 })
    expect(second.focus).not.toHaveBeenCalled()
    expect(second.postMessage).not.toHaveBeenCalled()
    expect(w.self.clients.openWindow).not.toHaveBeenCalled()
  })

  it('열린 창이 없으면 openWindow("/#/briefings?schedule_id=N")', async () => {
    const w = loadWorker([])
    await w.fire('notificationclick', clickEvent({ schedule_id: 12 }).event)
    expect(w.self.clients.openWindow).toHaveBeenCalledTimes(1)
    expect(w.self.clients.openWindow).toHaveBeenCalledWith('/#/briefings?schedule_id=12')
  })

  it('schedule_id 가 없거나 양의 정수가 아니면 일정 없는 브리핑 화면 주소', async () => {
    for (const data of [null, {}, { schedule_id: null }, { schedule_id: 0 }, { schedule_id: '12' }, { schedule_id: 1.5 }]) {
      const w = loadWorker([])
      await w.fire('notificationclick', clickEvent(data).event)
      expect(w.self.clients.openWindow).toHaveBeenCalledWith('/#/briefings')
    }
  })
})

describe('manifest · index.html · 아이콘', () => {
  const manifest = JSON.parse(manifestSource) as {
    name: string
    short_name: string
    start_url: string
    display: string
    theme_color: string
    background_color: string
    icons: { src: string; sizes: string; type: string }[]
  }

  it('start_url 은 /#/chat, display 는 standalone', () => {
    expect(manifest.start_url).toBe('/#/chat')
    expect(manifest.display).toBe('standalone')
  })

  it('이름은 index.html <title> 과 같고, 색은 tokens.css 의 primary(#171717)·background(#ffffff)', () => {
    const title = /<title>([^<]*)<\/title>/.exec(indexHtml)?.[1]
    expect(manifest.name).toBe(title)
    expect(manifest.short_name).toBe(title)
    expect(manifest.theme_color).toBe('#171717')
    expect(manifest.background_color).toBe('#ffffff')
    expect(indexHtml).toContain('<meta name="theme-color" content="#171717" />')
  })

  it('아이콘은 192·512 두 개이고 각각 실제 파일이다(외부 주소 없음)', () => {
    expect(manifest.icons.map((i) => [i.sizes, i.src])).toEqual([
      ['192x192', '/icon-192.svg'],
      ['512x512', '/icon-512.svg'],
    ])
    expect(manifest.icons.every((i) => i.type === 'image/svg+xml' && i.src.startsWith('/'))).toBe(true)
    expect(icon192).toContain('width="192"')
    expect(icon512).toContain('width="512"')
  })

  it('index.html 이 manifest 를 연결하고, favicon 은 같은 아이콘이다(템플릿 로고 아님)', () => {
    expect(indexHtml).toContain('<link rel="manifest" href="/manifest.webmanifest" />')
    expect(favicon).toContain('fill="#171717"')
    expect(favicon).toContain('>관</text>')
    expect(favicon).not.toContain('#863bff') // Vite 템플릿 로고 색
  })
})

describe('결정 I — 캐시 없음·fetch 리스너 없음', () => {
  it('등록되는 리스너는 install · activate · push · notificationclick 넷뿐이다', () => {
    const w = loadWorker([])
    expect([...w.listeners.keys()].sort()).toEqual(['activate', 'install', 'notificationclick', 'push'])
  })

  it('install 은 skipWaiting, activate 는 clients.claim 만 한다', async () => {
    const w = loadWorker([])
    await w.fire('install')
    await w.fire('activate')
    expect(w.self.skipWaiting).toHaveBeenCalledTimes(1)
    expect(w.self.clients.claim).toHaveBeenCalledTimes(1)
  })

  it('코드에 요청 가로채기 리스너·캐시 API 호출이 없다', () => {
    expect(swSource).not.toMatch(/addEventListener\(\s*["']fetch["']/)
    expect(swSource).not.toMatch(/\bonfetch\b/)
    expect(swSource).not.toMatch(/\bcaches\b/)
    expect(swSource).not.toMatch(/\bCache\b/)
    expect(swSource).not.toMatch(/\bfetch\s*\(/)
  })
})
