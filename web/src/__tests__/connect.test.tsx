// P9b U13 — "AI 연결" 화면(#/connect, CR-008). 실제 네트워크 없음: fetch 는 테스트마다 가짜를 건다 (결정 J).
// 가짜 서버 응답은 01-plan "API 계약 — 개정 4" 표의 모양이다(백엔드 U12 구현 전에도 돈다).
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from '@/App'
import { CONNECT_NOTICE } from '@/screens/ConnectScreen'
import { installFakeMatchMedia } from './helpers'

type Handler = (url: string, init: RequestInit) => Response | Promise<Response>

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

const ME = { id: 'u1', username: 'minji_01', nickname: '민지' }
const TOKEN = 'T0kenForTest_abcdefghijklmnopqrstuvwxyz0123456'
const CREATED = { token: TOKEN, created_at: '2026-11-18T01:00:00+00:00', expires_at: '2026-11-25T01:00:00+00:00' }
const NO_TOKEN = { active: false, created_at: null, expires_at: null, last_used_at: null }
const ACTIVE = { active: true, created_at: '2026-11-17T01:00:00+00:00', expires_at: '2026-11-24T01:00:00+00:00', last_used_at: null }
const EXPIRED = { active: false, created_at: '2026-11-01T01:00:00+00:00', expires_at: '2026-11-08T01:00:00+00:00', last_used_at: '2026-11-05T01:00:00+00:00' }

function install(table: Record<string, Handler>) {
  const defaults: Record<string, Handler> = {
    'GET /api/auth/me': () => json(ME),
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

/** user-event 가 clipboard 를 자기 것으로 갈아 끼우므로, setup 뒤에 우리 가짜를 건다. */
function fakeClipboard(user: ReturnType<typeof userEvent.setup>, reject = false) {
  void user
  const writeText = vi.fn(() => (reject ? Promise.reject(new Error('denied')) : Promise.resolve()))
  Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText } })
  return writeText
}

beforeEach(() => {
  installFakeMatchMedia(1280)
  window.localStorage.clear()
  window.sessionStorage.clear()
  window.history.replaceState(null, '', '#/connect')
})

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
  window.history.replaceState(null, '', '#/chat')
})

async function openConnect(table: Record<string, Handler>) {
  const fn = install(table)
  const user = userEvent.setup()
  render(<App />)
  await waitFor(() => expect(document.querySelector('[data-screen="connect"]')).not.toBeNull())
  return { fn, user }
}

const ORIGIN_COMMAND = (t: string) => `claude mcp add --transport http relmemo ${window.location.origin}/mcp --header "Authorization: Bearer ${t}"`

describe('AI 연결 화면 (CR-008 U13)', () => {
  it('① #/connect 가 화면을 열고, 사이드바 버튼은 sidebar-account 밖의 <button> 이며 nav 링크 목록은 그대로 3개', async () => {
    window.history.replaceState(null, '', '#/chat')
    install({ 'GET /api/auth/mcp-token': () => json(NO_TOKEN) })
    const user = userEvent.setup()
    render(<App />)
    await screen.findByRole('textbox', { name: '메시지 입력' })
    const entry = screen.getByTestId('sidebar-connect')
    expect(entry.tagName).toBe('BUTTON')
    expect(entry).toHaveTextContent(CONNECT_NOTICE.entry)
    expect(screen.getByTestId('sidebar-account').contains(entry)).toBe(false)
    const nav = screen.getByRole('navigation', { name: '주 메뉴' })
    expect(Array.from(nav.querySelectorAll('a')).map((a) => a.getAttribute('href'))).toEqual(['#/chat', '#/persons', '#/briefings'])
    await user.click(entry)
    expect(window.location.hash).toBe('#/connect')
    await waitFor(() => expect(document.querySelector('[data-screen="connect"]')).not.toBeNull())
    expect(screen.getByRole('heading', { name: CONNECT_NOTICE.title })).toBeInTheDocument()
    expect(screen.getByText(CONNECT_NOTICE.intro)).toBeInTheDocument()
    expect(screen.getByText(CONNECT_NOTICE.privacy)).toBeInTheDocument()
    expect(screen.getByText(CONNECT_NOTICE.scope)).toBeInTheDocument()
    expect(screen.getByText(CONNECT_NOTICE.validity)).toBeInTheDocument()
  })

  it('② 없음 — statusNone, create 만(recreate·경고·폐기 없음), GET 1회', async () => {
    const { fn } = await openConnect({ 'GET /api/auth/mcp-token': () => json(NO_TOKEN) })
    await screen.findByText(CONNECT_NOTICE.statusNone)
    expect(screen.getByRole('button', { name: CONNECT_NOTICE.create })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: CONNECT_NOTICE.recreate })).toBeNull()
    expect(screen.queryByRole('button', { name: CONNECT_NOTICE.revoke })).toBeNull()
    expect(screen.queryByText(CONNECT_NOTICE.recreateWarn)).toBeNull()
    expect(callsTo(fn, 'GET /api/auth/mcp-token')).toHaveLength(1)
  })

  it('② 활성 — statusActive·만료·마지막 사용, recreate·recreateWarn·revoke', async () => {
    await openConnect({ 'GET /api/auth/mcp-token': () => json(ACTIVE) })
    await screen.findByText(CONNECT_NOTICE.statusActive)
    const status = screen.getByTestId('mcp-status')
    expect(status).toHaveTextContent(`${CONNECT_NOTICE.expiresAt}: ${new Date(ACTIVE.expires_at).toLocaleString('ko-KR')}`)
    expect(status).toHaveTextContent(`${CONNECT_NOTICE.lastUsedAt}: ${CONNECT_NOTICE.neverUsed}`)
    expect(screen.getByRole('button', { name: CONNECT_NOTICE.recreate })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: CONNECT_NOTICE.create })).toBeNull()
    expect(screen.getByText(CONNECT_NOTICE.recreateWarn)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: CONNECT_NOTICE.revoke })).toBeInTheDocument()
  })

  it('② 만료 — statusExpired, create 버튼만(폐기 없음)', async () => {
    await openConnect({ 'GET /api/auth/mcp-token': () => json(EXPIRED) })
    await screen.findByText(CONNECT_NOTICE.statusExpired)
    expect(screen.getByRole('button', { name: CONNECT_NOTICE.create })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: CONNECT_NOTICE.revoke })).toBeNull()
    expect(screen.queryByText(CONNECT_NOTICE.statusActive)).toBeNull()
  })

  it('③ 만들기 — POST 정확히 1회, 토큰·명령 정확 일치, onceNotice, 상태 statusActive(아직 쓰지 않음)', async () => {
    const { fn, user } = await openConnect({
      'GET /api/auth/mcp-token': () => json(NO_TOKEN),
      'POST /api/auth/mcp-token': () => json(CREATED, 201),
    })
    await user.click(await screen.findByRole('button', { name: CONNECT_NOTICE.create }))
    await screen.findByTestId('mcp-token')
    expect(callsTo(fn, 'POST /api/auth/mcp-token')).toHaveLength(1)
    expect(screen.getByTestId('mcp-token').textContent).toBe(TOKEN)
    expect(screen.getByTestId('mcp-command').textContent).toBe(ORIGIN_COMMAND(TOKEN))
    expect(screen.getByTestId('mcp-command').textContent).toContain(`Bearer ${TOKEN}`)
    expect(screen.getByText(CONNECT_NOTICE.onceNotice)).toBeInTheDocument()
    expect(screen.getByText(CONNECT_NOTICE.tokenLabel)).toBeInTheDocument()
    expect(screen.getByText(CONNECT_NOTICE.commandLabel)).toBeInTheDocument()
    const status = screen.getByTestId('mcp-status')
    expect(status).toHaveTextContent(CONNECT_NOTICE.statusActive)
    expect(status).toHaveTextContent(`${CONNECT_NOTICE.expiresAt}: ${new Date(CREATED.expires_at).toLocaleString('ko-KR')}`)
    expect(status).toHaveTextContent(CONNECT_NOTICE.neverUsed)
    // 이제 활성이라 recreate·revoke
    expect(screen.getByRole('button', { name: CONNECT_NOTICE.recreate })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: CONNECT_NOTICE.revoke })).toBeInTheDocument()
  })

  it('④ 복사 — 토큰·명령 문자열로 writeText 1회씩, 거부되면 copyFailed', async () => {
    const { user } = await openConnect({
      'GET /api/auth/mcp-token': () => json(NO_TOKEN),
      'POST /api/auth/mcp-token': () => json(CREATED, 201),
    })
    const writeText = fakeClipboard(user)
    await user.click(await screen.findByRole('button', { name: CONNECT_NOTICE.create }))
    await screen.findByTestId('mcp-token')
    await user.click(screen.getByRole('button', { name: CONNECT_NOTICE.copyToken }))
    expect(writeText).toHaveBeenCalledTimes(1)
    expect(writeText).toHaveBeenLastCalledWith(TOKEN)
    expect(await screen.findByRole('status')).toHaveTextContent(CONNECT_NOTICE.copied)
    await user.click(screen.getByRole('button', { name: CONNECT_NOTICE.copyCommand }))
    expect(writeText).toHaveBeenCalledTimes(2)
    expect(writeText).toHaveBeenLastCalledWith(ORIGIN_COMMAND(TOKEN))
    // 거부
    const denied = fakeClipboard(user, true)
    await user.click(screen.getByRole('button', { name: CONNECT_NOTICE.copyToken }))
    expect(denied).toHaveBeenCalledTimes(1)
    expect(await screen.findByText(CONNECT_NOTICE.copyFailed)).toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent(CONNECT_NOTICE.copyFailed)
  })

  it('⑤ 만든 뒤 localStorage·sessionStorage 의 어떤 키·값에도 토큰이 없고, 콘솔·주소에도 없다', async () => {
    const spies = (['log', 'info', 'warn', 'error', 'debug'] as const).map((m) => vi.spyOn(console, m).mockImplementation(() => {}))
    const { user } = await openConnect({
      'GET /api/auth/mcp-token': () => json(NO_TOKEN),
      'POST /api/auth/mcp-token': () => json(CREATED, 201),
    })
    await user.click(await screen.findByRole('button', { name: CONNECT_NOTICE.create }))
    await screen.findByTestId('mcp-token')
    for (const store of [window.localStorage, window.sessionStorage]) {
      for (let i = 0; i < store.length; i++) {
        const key = store.key(i) as string
        expect(key).not.toContain(TOKEN)
        expect(store.getItem(key)).not.toContain(TOKEN)
      }
    }
    expect(window.location.href).not.toContain(TOKEN)
    for (const s of spies) expect(JSON.stringify(s.mock.calls)).not.toContain(TOKEN)
  })

  it('⑥ 다른 화면으로 갔다가 돌아오면 토큰은 안 보이고 GET 이 다시 1회 나간다', async () => {
    const { fn, user } = await openConnect({
      'GET /api/auth/mcp-token': () => json(ACTIVE),
      'POST /api/auth/mcp-token': () => json(CREATED, 201),
    })
    await user.click(await screen.findByRole('button', { name: CONNECT_NOTICE.recreate }))
    await screen.findByTestId('mcp-token')
    expect(callsTo(fn, 'GET /api/auth/mcp-token')).toHaveLength(1)
    await user.click(screen.getByRole('link', { name: '채팅' }))
    await screen.findByRole('textbox', { name: '메시지 입력' })
    expect(document.querySelector('[data-screen="connect"]')).toBeNull()
    await user.click(screen.getByTestId('sidebar-connect'))
    await screen.findByText(CONNECT_NOTICE.statusActive)
    expect(screen.queryByTestId('mcp-token')).toBeNull()
    expect(screen.queryByTestId('mcp-command')).toBeNull()
    expect(callsTo(fn, 'GET /api/auth/mcp-token')).toHaveLength(2)
  })

  it('⑦ 폐기 — DELETE 정확히 1회, revoked·토큰 사라짐·상태 statusNone', async () => {
    const { fn, user } = await openConnect({
      'GET /api/auth/mcp-token': () => json(NO_TOKEN),
      'POST /api/auth/mcp-token': () => json(CREATED, 201),
      'DELETE /api/auth/mcp-token': () => new Response(null, { status: 204 }),
    })
    await user.click(await screen.findByRole('button', { name: CONNECT_NOTICE.create }))
    await screen.findByTestId('mcp-token')
    await user.click(screen.getByRole('button', { name: CONNECT_NOTICE.revoke }))
    await screen.findByText(CONNECT_NOTICE.revoked)
    expect(callsTo(fn, 'DELETE /api/auth/mcp-token')).toHaveLength(1)
    expect(callsTo(fn, 'POST /api/auth/mcp-token')).toHaveLength(1)
    expect(screen.queryByTestId('mcp-token')).toBeNull()
    expect(screen.queryByTestId('mcp-command')).toBeNull()
    expect(screen.getByTestId('mcp-status')).toHaveTextContent(CONNECT_NOTICE.statusNone)
    expect(screen.queryByRole('button', { name: CONNECT_NOTICE.revoke })).toBeNull()
    expect(screen.getByRole('button', { name: CONNECT_NOTICE.create })).toBeInTheDocument()
  })

  it('⑧ POST 500 — failed(role=alert), 토큰 표시 0', async () => {
    const { user } = await openConnect({
      'GET /api/auth/mcp-token': () => json(NO_TOKEN),
      'POST /api/auth/mcp-token': () => json({ detail: { code: 'internal' } }, 500),
    })
    await user.click(await screen.findByRole('button', { name: CONNECT_NOTICE.create }))
    expect(await screen.findByRole('alert')).toHaveTextContent(CONNECT_NOTICE.failed)
    expect(screen.queryByTestId('mcp-token')).toBeNull()
    expect(screen.queryByTestId('mcp-command')).toBeNull()
    expect(screen.getByTestId('mcp-status')).toHaveTextContent(CONNECT_NOTICE.statusNone)
  })

  it('⑨ 진행 중 두 번 눌러도 POST 는 1회(버튼 disabled)', async () => {
    let release: (r: Response) => void = () => {}
    const pending = new Promise<Response>((resolve) => {
      release = resolve
    })
    const { fn, user } = await openConnect({
      'GET /api/auth/mcp-token': () => json(NO_TOKEN),
      'POST /api/auth/mcp-token': () => pending,
    })
    const button = await screen.findByRole('button', { name: CONNECT_NOTICE.create })
    await user.click(button)
    await user.click(button)
    expect(button).toBeDisabled()
    expect(callsTo(fn, 'POST /api/auth/mcp-token')).toHaveLength(1)
    release(json(CREATED, 201))
    await screen.findByTestId('mcp-token')
    expect(callsTo(fn, 'POST /api/auth/mcp-token')).toHaveLength(1)
    // 끝나면 다시 누를 수 있다(recreate)
    expect(within(screen.getByTestId('mcp-status').parentElement as HTMLElement).getByRole('button', { name: CONNECT_NOTICE.recreate })).toBeEnabled()
  })
})
