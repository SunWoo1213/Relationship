// P9b U6 — 로그인·가입 관문, 로그아웃, 401 처리. 실제 네트워크 없음: fetch 는 테스트마다 vi.stubGlobal 로 가짜를 건다 (결정 J).
// 가짜 서버 응답은 01-plan "API 계약" 표의 모양이다(백엔드 U2 구현 전에도 돈다).
import { act, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App, { GATE_NOTICE } from '@/App'
import { ACCOUNT_NOTICE, BANNER_NOTICE } from '@/components/AppShell'
import { BRIEFING_NOTICE } from '@/screens/BriefingScreen'
import { AUTH_NOTICE } from '@/screens/AuthScreen'
import { SESSION_STORAGE_KEY } from '@/session'
import { installFakeMatchMedia } from './helpers'

type Handler = (url: string, init: RequestInit) => Response | Promise<Response>

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

const UNAUTH = () => json({ detail: { code: 'unauthenticated' } }, 401)
const ME = { id: 'u1', username: 'minji_01' }

/** 표의 키는 `메서드 경로`. 표에 없는 요청은 실패시킨다(테스트가 모르는 요청이 나가면 눈에 띈다). 기본: 대화 기록·질문·인물·브리핑은 빈 목록. */
function install(table: Record<string, Handler>) {
  const defaults: Record<string, Handler> = {
    'GET /api/chat/history?limit=50': () => json([]),
    'GET /api/questions/pending': () => json([]),
    'GET /api/persons': () => json([]),
    'GET /api/briefings': () => json([]),
  }
  const merged = { ...defaults, ...table }
  const fn = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const key = `${init?.method ?? 'GET'} ${String(input)}`
    if (!merged[key]) throw new Error(`예상하지 못한 요청: ${key}`)
    return Promise.resolve(merged[key](String(input), init ?? {}))
  })
  vi.stubGlobal('fetch', fn)
  return fn
}

function callsTo(fn: ReturnType<typeof install>, key: string) {
  return fn.mock.calls.filter(([url, init]) => `${(init as RequestInit)?.method ?? 'GET'} ${String(url)}` === key)
}

function bodyOf(call: unknown[]): unknown {
  return JSON.parse((call[1] as RequestInit).body as string)
}

/** 웹푸시를 지원하는 브라우저 — 현재 구독 endpoint 만 돌려준다. */
function installPushBrowser(endpoint: string | null) {
  const registration = {
    pushManager: { getSubscription: vi.fn(() => Promise.resolve(endpoint ? { endpoint } : null)) },
  }
  vi.stubGlobal('Notification', { requestPermission: vi.fn() })
  vi.stubGlobal('PushManager', class {})
  Object.defineProperty(navigator, 'serviceWorker', {
    configurable: true,
    value: {
      getRegistration: vi.fn(() => Promise.resolve(registration)),
      addEventListener: () => {},
      removeEventListener: () => {},
    },
  })
}

beforeEach(() => {
  installFakeMatchMedia(1280)
  window.localStorage.clear()
  window.history.replaceState(null, '', '#/chat')
})

afterEach(() => {
  vi.unstubAllGlobals()
  Reflect.deleteProperty(navigator, 'serviceWorker')
  vi.restoreAllMocks()
  window.history.replaceState(null, '', '#/chat')
})

async function fillAndSubmit(opts: { username?: string; password?: string; confirm?: string; submit: string }) {
  const user = userEvent.setup()
  if (opts.username !== undefined) await user.type(screen.getByLabelText(AUTH_NOTICE.username), opts.username)
  if (opts.password !== undefined) await user.type(screen.getByLabelText(AUTH_NOTICE.password, { exact: true }), opts.password)
  if (opts.confirm !== undefined) await user.type(screen.getByLabelText(AUTH_NOTICE.confirm), opts.confirm)
  await user.click(screen.getByRole('button', { name: opts.submit }))
  return user
}

describe('관문 — GET /auth/me 두 갈래 (결정 L)', () => {
  it('me 401 이면 로그인 화면이 뜨고 앱 틀은 그려지지 않는다', async () => {
    const fetchFn = install({ 'GET /api/auth/me': UNAUTH })
    render(<App />)
    expect(await screen.findByRole('heading', { level: 1, name: AUTH_NOTICE.titleLogin })).toBeInTheDocument()
    expect(document.querySelector('[data-screen="auth"]')).not.toBeNull()
    expect(screen.queryByRole('navigation', { name: '주 메뉴' })).toBeNull()
    // 관문 앞에서는 /auth/me 외의 API 를 부르지 않는다
    expect(fetchFn.mock.calls.map(([u]) => String(u))).toEqual(['/api/auth/me'])
  })

  it('me 200 이면 앱 틀(채팅)이 열리고 사이드바에 "<아이디> · 로그아웃" 한 줄이 있다', async () => {
    install({ 'GET /api/auth/me': () => json(ME) })
    render(<App />)
    await screen.findByRole('textbox', { name: '메시지 입력' })
    expect(document.querySelector('[data-screen="auth"]')).toBeNull()
    const row = screen.getByTestId('sidebar-account')
    expect(within(row).getByTestId('sidebar-username')).toHaveTextContent('minji_01')
    expect(within(row).getByRole('button', { name: ACCOUNT_NOTICE.logout })).toBeInTheDocument()
    // 채팅방 목록은 없다 (원칙7) — 사이드바 링크는 화면 3개 + 인물 목록 자리뿐
    const nav = screen.getByRole('navigation', { name: '주 메뉴' })
    expect(Array.from(nav.querySelectorAll('a')).map((a) => a.getAttribute('href'))).toEqual(['#/chat', '#/persons', '#/briefings'])
  })

  it('me 가 401 도 200 도 아니면(서버 연결 실패) 로그인 화면 대신 한 줄 안내와 다시 시도 — 누르면 다시 /auth/me', async () => {
    let n = 0
    const fetchFn = install({
      'GET /api/auth/me': () => {
        if (n++ === 0) throw new TypeError('Failed to fetch')
        return json(ME)
      },
    })
    render(<App />)
    expect(await screen.findByRole('alert')).toHaveTextContent(GATE_NOTICE.unreachable)
    expect(document.querySelector('[data-screen="auth"]')).toBeNull()
    await userEvent.setup().click(screen.getByRole('button', { name: GATE_NOTICE.retry }))
    await screen.findByRole('textbox', { name: '메시지 입력' })
    expect(callsTo(fetchFn, 'GET /api/auth/me')).toHaveLength(2)
  })
})

describe('로그인 (POST /auth/login)', () => {
  it('입력란 속성: 아이디 autocomplete=username, 비밀번호 type=password autocomplete=current-password', async () => {
    install({ 'GET /api/auth/me': UNAUTH })
    render(<App />)
    await screen.findByRole('heading', { name: AUTH_NOTICE.titleLogin })
    const username = screen.getByLabelText(AUTH_NOTICE.username)
    const password = screen.getByLabelText(AUTH_NOTICE.password, { exact: true })
    expect(username).toHaveAttribute('autocomplete', 'username')
    expect(password).toHaveAttribute('type', 'password')
    expect(password).toHaveAttribute('autocomplete', 'current-password')
    expect(screen.queryByLabelText(AUTH_NOTICE.confirm)).toBeNull()
  })

  it('성공하면 앱 틀이 열린다 — 본문은 {username, password}, 예전 세션 키는 지워진다, 비밀번호는 저장·로그되지 않는다', async () => {
    window.localStorage.setItem(SESSION_STORAGE_KEY, 'sess-old')
    const logSpies = (['log', 'info', 'warn', 'error', 'debug'] as const).map((m) => vi.spyOn(console, m))
    const fetchFn = install({
      'GET /api/auth/me': UNAUTH,
      'POST /api/auth/login': () => json(ME),
    })
    render(<App />)
    await screen.findByRole('heading', { name: AUTH_NOTICE.titleLogin })
    await fillAndSubmit({ username: 'minji_01', password: 'correct-horse-9', submit: AUTH_NOTICE.submitLogin })

    await screen.findByRole('textbox', { name: '메시지 입력' })
    expect(screen.getByTestId('sidebar-username')).toHaveTextContent('minji_01')
    const login = callsTo(fetchFn, 'POST /api/auth/login')
    expect(login).toHaveLength(1)
    expect(bodyOf(login[0])).toEqual({ username: 'minji_01', password: 'correct-horse-9' })
    expect(window.localStorage.getItem(SESSION_STORAGE_KEY)).toBeNull()
    expect(JSON.stringify({ ...window.localStorage })).not.toContain('correct-horse-9')
    for (const spy of logSpies) expect(spy).not.toHaveBeenCalled()
  })

  it('401 invalid_credentials 면 안내 한 줄만 — 로그인 화면에 남는다', async () => {
    install({
      'GET /api/auth/me': UNAUTH,
      'POST /api/auth/login': () => json({ detail: { code: 'invalid_credentials' } }, 401),
    })
    render(<App />)
    await screen.findByRole('heading', { name: AUTH_NOTICE.titleLogin })
    await fillAndSubmit({ username: 'minji_01', password: 'wrong-password', submit: AUTH_NOTICE.submitLogin })
    expect(await screen.findByRole('alert')).toHaveTextContent(AUTH_NOTICE.invalidCredentials)
    expect(document.querySelector('[data-screen="auth"]')).not.toBeNull()
    expect(screen.getByRole('button', { name: AUTH_NOTICE.submitLogin })).toBeEnabled()
  })

  it('403 bad_origin 과 코드 없는 5xx 도 각자의 안내 한 줄', async () => {
    let n = 0
    install({
      'GET /api/auth/me': UNAUTH,
      'POST /api/auth/login': () => (n++ === 0 ? json({ detail: { code: 'bad_origin' } }, 403) : json('boom', 500)),
    })
    render(<App />)
    await screen.findByRole('heading', { name: AUTH_NOTICE.titleLogin })
    const user = await fillAndSubmit({ username: 'minji_01', password: 'password-1', submit: AUTH_NOTICE.submitLogin })
    expect(await screen.findByRole('alert')).toHaveTextContent(AUTH_NOTICE.badOrigin)
    await user.click(screen.getByRole('button', { name: AUTH_NOTICE.submitLogin }))
    await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent(AUTH_NOTICE.failed))
  })

  it('알림 클릭 주소(#/briefings?schedule_id=N)는 관문을 통과한 뒤에도 그대로 열린다', async () => {
    window.history.replaceState(null, '', '#/briefings?schedule_id=5')
    install({
      'GET /api/auth/me': UNAUTH,
      'POST /api/auth/login': () => json(ME),
      'GET /api/briefings?schedule_id=5': () => json([]),
    })
    render(<App />)
    await screen.findByRole('heading', { name: AUTH_NOTICE.titleLogin })
    expect(window.location.hash).toBe('#/briefings?schedule_id=5')
    await fillAndSubmit({ username: 'minji_01', password: 'password-1', submit: AUTH_NOTICE.submitLogin })
    await waitFor(() => expect(document.querySelector('[data-screen="briefings"]')).not.toBeNull())
    expect(window.location.hash).toBe('#/briefings?schedule_id=5')
  })
})

describe('가입 (POST /auth/signup)', () => {
  async function openSignup() {
    install({ 'GET /api/auth/me': UNAUTH })
    render(<App />)
    await screen.findByRole('heading', { name: AUTH_NOTICE.titleLogin })
    await userEvent.setup().click(screen.getByRole('button', { name: AUTH_NOTICE.toSignup }))
    await screen.findByRole('heading', { name: AUTH_NOTICE.titleSignup })
  }

  it('가입 화면에는 비밀번호 확인 칸·규칙 안내 한 줄이 있고 비밀번호 칸은 new-password', async () => {
    await openSignup()
    expect(screen.getByLabelText(AUTH_NOTICE.password, { exact: true })).toHaveAttribute('autocomplete', 'new-password')
    expect(screen.getByLabelText(AUTH_NOTICE.confirm)).toHaveAttribute('type', 'password')
    expect(screen.getByLabelText(AUTH_NOTICE.confirm)).toHaveAttribute('autocomplete', 'new-password')
    expect(screen.getByText(AUTH_NOTICE.rules)).toBeInTheDocument()
  })

  it('비밀번호 확인이 다르면 요청을 한 번도 보내지 않고 안내만 띄운다', async () => {
    const fetchFn = install({ 'GET /api/auth/me': UNAUTH, 'POST /api/auth/signup': () => json(ME, 201) })
    render(<App />)
    await screen.findByRole('heading', { name: AUTH_NOTICE.titleLogin })
    await userEvent.setup().click(screen.getByRole('button', { name: AUTH_NOTICE.toSignup }))
    await fillAndSubmit({ username: 'minji_01', password: 'password-1', confirm: 'password-2', submit: AUTH_NOTICE.submitSignup })
    expect(await screen.findByRole('alert')).toHaveTextContent(AUTH_NOTICE.mismatch)
    expect(callsTo(fetchFn, 'POST /api/auth/signup')).toHaveLength(0)
  })

  it('409 username_taken 이면 그 안내를 보인다', async () => {
    install({
      'GET /api/auth/me': UNAUTH,
      'POST /api/auth/signup': () => json({ detail: { code: 'username_taken' } }, 409),
    })
    render(<App />)
    await screen.findByRole('heading', { name: AUTH_NOTICE.titleLogin })
    await userEvent.setup().click(screen.getByRole('button', { name: AUTH_NOTICE.toSignup }))
    await fillAndSubmit({ username: 'minji_01', password: 'password-1', confirm: 'password-1', submit: AUTH_NOTICE.submitSignup })
    expect(await screen.findByRole('alert')).toHaveTextContent(AUTH_NOTICE.usernameTaken)
    expect(document.querySelector('[data-screen="auth"]')).not.toBeNull()
  })

  it.each([
    ['invalid_username', AUTH_NOTICE.invalidUsername],
    ['invalid_password', AUTH_NOTICE.invalidPassword],
  ])('422 %s 면 그 규칙 안내를 보인다', async (code, expected) => {
    install({
      'GET /api/auth/me': UNAUTH,
      'POST /api/auth/signup': () => json({ detail: { code } }, 422),
    })
    render(<App />)
    await screen.findByRole('heading', { name: AUTH_NOTICE.titleLogin })
    await userEvent.setup().click(screen.getByRole('button', { name: AUTH_NOTICE.toSignup }))
    await fillAndSubmit({ username: 'x', password: 'short', confirm: 'short', submit: AUTH_NOTICE.submitSignup })
    expect(await screen.findByRole('alert')).toHaveTextContent(expected)
  })

  it('201 이면 가입 즉시 로그인된 앱 틀이 열린다 — 본문은 {username, password}(확인 칸은 보내지 않는다)', async () => {
    const fetchFn = install({
      'GET /api/auth/me': UNAUTH,
      'POST /api/auth/signup': () => json(ME, 201),
    })
    render(<App />)
    await screen.findByRole('heading', { name: AUTH_NOTICE.titleLogin })
    await userEvent.setup().click(screen.getByRole('button', { name: AUTH_NOTICE.toSignup }))
    await fillAndSubmit({ username: 'minji_01', password: 'password-1', confirm: 'password-1', submit: AUTH_NOTICE.submitSignup })
    await screen.findByRole('textbox', { name: '메시지 입력' })
    expect(bodyOf(callsTo(fetchFn, 'POST /api/auth/signup')[0])).toEqual({ username: 'minji_01', password: 'password-1' })
  })
})

describe('401 처리 — 로그인한 뒤 어떤 API 든 401 이면 관문으로 (V6-1)', () => {
  it('대화 기록 조회가 401 이면 로그인 화면으로 돌아온다', async () => {
    install({
      'GET /api/auth/me': () => json(ME),
      'GET /api/chat/history?limit=50': UNAUTH,
    })
    render(<App />)
    expect(await screen.findByRole('heading', { level: 1, name: AUTH_NOTICE.titleLogin })).toBeInTheDocument()
    expect(screen.queryByRole('navigation', { name: '주 메뉴' })).toBeNull()
  })

  it('발화 전송이 401 이면 로그인 화면으로 돌아온다', async () => {
    install({
      'GET /api/auth/me': () => json(ME),
      'POST /api/chat': UNAUTH,
    })
    render(<App />)
    const user = userEvent.setup()
    await user.type(await screen.findByRole('textbox', { name: '메시지 입력' }), '안녕')
    await user.click(screen.getByRole('button', { name: '보내기' }))
    expect(await screen.findByRole('heading', { level: 1, name: AUTH_NOTICE.titleLogin })).toBeInTheDocument()
  })
})

describe('로그아웃 (POST /auth/logout)', () => {
  it('푸시 구독이 있으면 그 endpoint 를 함께 보내고 로그인 화면으로 간다', async () => {
    installPushBrowser('https://push.example/ep-1')
    const fetchFn = install({
      'GET /api/auth/me': () => json(ME),
      'POST /api/auth/logout': () => new Response(null, { status: 204 }),
    })
    render(<App />)
    await userEvent.setup().click(await screen.findByRole('button', { name: ACCOUNT_NOTICE.logout }))
    expect(await screen.findByRole('heading', { level: 1, name: AUTH_NOTICE.titleLogin })).toBeInTheDocument()
    const out = callsTo(fetchFn, 'POST /api/auth/logout')
    expect(out).toHaveLength(1)
    expect(bodyOf(out[0])).toEqual({ endpoint: 'https://push.example/ep-1' })
    expect(screen.queryByRole('navigation', { name: '주 메뉴' })).toBeNull()
  })

  it('구독이 없으면 endpoint 없이 빈 본문 — 204 에서도 예외·오류 안내 없이 관문', async () => {
    installPushBrowser(null)
    const fetchFn = install({
      'GET /api/auth/me': () => json(ME),
      'POST /api/auth/logout': () => new Response(null, { status: 204 }),
    })
    render(<App />)
    await userEvent.setup().click(await screen.findByRole('button', { name: ACCOUNT_NOTICE.logout }))
    await screen.findByRole('heading', { level: 1, name: AUTH_NOTICE.titleLogin })
    expect(bodyOf(callsTo(fetchFn, 'POST /api/auth/logout')[0])).toEqual({})
    expect(screen.queryByRole('alert')).toBeNull()
  })

  it('웹푸시를 못 쓰는 브라우저(jsdom 기본)에서도 로그아웃된다', async () => {
    const fetchFn = install({
      'GET /api/auth/me': () => json(ME),
      'POST /api/auth/logout': () => new Response(null, { status: 204 }),
    })
    render(<App />)
    await userEvent.setup().click(await screen.findByRole('button', { name: ACCOUNT_NOTICE.logout }))
    await screen.findByRole('heading', { level: 1, name: AUTH_NOTICE.titleLogin })
    expect(bodyOf(callsTo(fetchFn, 'POST /api/auth/logout')[0])).toEqual({})
  })

  it('로그아웃이 401 을 받아도(이미 로그아웃됨) 오류 표시 없이 관문으로 간다 (F-3)', async () => {
    install({
      'GET /api/auth/me': () => json(ME),
      'POST /api/auth/logout': UNAUTH,
    })
    render(<App />)
    await userEvent.setup().click(await screen.findByRole('button', { name: ACCOUNT_NOTICE.logout }))
    await screen.findByRole('heading', { level: 1, name: AUTH_NOTICE.titleLogin })
    expect(screen.queryByRole('alert')).toBeNull()
    expect(screen.queryByText(ACCOUNT_NOTICE.logoutFailed)).toBeNull()
  })

  it('로그아웃이 5xx 로 실패하면 앱 틀에 남고 안내 한 줄', async () => {
    install({
      'GET /api/auth/me': () => json(ME),
      'POST /api/auth/logout': () => json({ detail: { code: 'internal_error' } }, 500),
    })
    render(<App />)
    await userEvent.setup().click(await screen.findByRole('button', { name: ACCOUNT_NOTICE.logout }))
    expect(await screen.findByText(ACCOUNT_NOTICE.logoutFailed)).toBeInTheDocument()
    expect(screen.getByTestId('sidebar-username')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: ACCOUNT_NOTICE.logout })).toBeEnabled()
  })

  it('로그아웃 뒤 다시 로그인하면 이전 계정의 화면 상태가 남지 않는다 (같은 브라우저 두 계정)', async () => {
    const history = [{ id: 1, role: 'user', content: '첫 계정의 발화', question_id: null, created_at: '2026-11-15T09:00:00Z' }]
    let who = 0
    install({
      'GET /api/auth/me': () => json(ME),
      'GET /api/chat/history?limit=50': () => json(who === 0 ? history : []),
      'POST /api/auth/logout': () => new Response(null, { status: 204 }),
      'POST /api/auth/login': () => {
        who = 1
        return json({ id: 'u2', username: 'second_user' })
      },
    })
    render(<App />)
    await screen.findByText('첫 계정의 발화')
    await userEvent.setup().click(screen.getByRole('button', { name: ACCOUNT_NOTICE.logout }))
    await screen.findByRole('heading', { level: 1, name: AUTH_NOTICE.titleLogin })
    await fillAndSubmit({ username: 'second_user', password: 'password-2', submit: AUTH_NOTICE.submitLogin })
    await screen.findByRole('textbox', { name: '메시지 입력' })
    expect(screen.getByTestId('sidebar-username')).toHaveTextContent('second_user')
    expect(screen.queryByText('첫 계정의 발화')).toBeNull()
  })
})

describe('알림 클릭 open-briefing — 관문 위에서 해시만 바꾼다 (C-2)', () => {
  /** 메시지를 보낼 수 있는 서비스 워커 컨테이너. 리스너가 붙었는지 확인할 수 있다. */
  function installWorker() {
    const listeners = new Set<(e: MessageEvent) => void>()
    Object.defineProperty(navigator, 'serviceWorker', {
      configurable: true,
      value: {
        getRegistration: vi.fn(() => Promise.resolve(undefined)),
        addEventListener: (_: string, fn: (e: MessageEvent) => void) => listeners.add(fn),
        removeEventListener: (_: string, fn: (e: MessageEvent) => void) => listeners.delete(fn),
      },
    })
    return {
      hasListener: () => listeners.size > 0,
      post: (data: unknown) => act(() => listeners.forEach((fn) => fn({ data } as MessageEvent))),
    }
  }
  const BRIEFING_ROUTE = '#/briefings?schedule_id=12'

  it('(c) /auth/me 응답 전에 받아도 유실되지 않는다 — 응답 200 뒤 그 브리핑 화면이 열린다', async () => {
    const worker = installWorker()
    let answerMe: (r: Response) => void = () => {}
    install({ 'GET /api/auth/me': () => new Promise<Response>((resolve) => (answerMe = resolve)) })
    render(<App />)
    await waitFor(() => expect(worker.hasListener()).toBe(true))
    expect(screen.queryByRole('textbox', { name: '메시지 입력' })).toBeNull() // 관문은 아직 loading
    worker.post({ type: 'open-briefing', schedule_id: 12 })
    expect(window.location.hash).toBe(BRIEFING_ROUTE)

    await act(async () => answerMe(json(ME)))
    await screen.findByRole('button', { name: BRIEFING_NOTICE.subscribe })
    expect(window.location.hash).toBe(BRIEFING_ROUTE)
    expect(screen.queryByRole('textbox', { name: '메시지 입력' })).toBeNull()
  })

  it('(d) 로그인 화면에서 받으면 해시만 바뀌고 로그인 화면은 그대로 — 로그인 성공 뒤 그 브리핑 화면', async () => {
    const worker = installWorker()
    install({ 'GET /api/auth/me': UNAUTH, 'POST /api/auth/login': () => json(ME) })
    render(<App />)
    await screen.findByRole('heading', { name: AUTH_NOTICE.titleLogin })
    await waitFor(() => expect(worker.hasListener()).toBe(true))
    worker.post({ type: 'open-briefing', schedule_id: 12 })
    expect(window.location.hash).toBe(BRIEFING_ROUTE)
    expect(screen.getByRole('heading', { name: AUTH_NOTICE.titleLogin })).toBeInTheDocument()

    await fillAndSubmit({ username: 'minji_01', password: 'correct-horse-9', submit: AUTH_NOTICE.submitLogin })
    await screen.findByRole('button', { name: BRIEFING_NOTICE.subscribe })
    expect(window.location.hash).toBe(BRIEFING_ROUTE)
  })

  it('로그인 화면에서 type:"briefing" 메시지가 와도 배너·문구·해시 이동이 없다', async () => {
    const worker = installWorker()
    install({ 'GET /api/auth/me': UNAUTH })
    render(<App />)
    await screen.findByRole('heading', { name: AUTH_NOTICE.titleLogin })
    await waitFor(() => expect(worker.hasListener()).toBe(true))
    worker.post({ type: 'briefing', schedule_id: 9 })
    expect(screen.queryByTestId('push-banner')).toBeNull()
    expect(screen.queryByText(BANNER_NOTICE.text)).toBeNull()
    expect(window.location.hash).toBe('#/chat')
  })
})
