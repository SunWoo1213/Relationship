import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, apiFetch, CHAT_HISTORY_LIMIT, getChatHistory, login, logout, onUnauthorized } from '@/api/client'

function jsonResponse(status: number, body: unknown) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

/** 실패해야 하는 호출의 ApiError 를 돌려준다. 성공하면 테스트를 실패시킨다. */
async function failureOf(call: Promise<unknown>): Promise<ApiError> {
  try {
    await call
  } catch (e) {
    return e as ApiError
  }
  throw new Error('호출이 실패해야 한다')
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('API 클라이언트 래퍼 (결정 C (ii))', () => {
  it('기본 경로는 /api 이고 GET 은 본문·Content-Type 이 없다', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, { ok: 1 }))
    vi.stubGlobal('fetch', fetchMock)
    const out = await apiFetch<{ ok: number }>('/persons')
    expect(out).toEqual({ ok: 1 })
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/persons')
    expect(init.method).toBe('GET')
    expect(init.body).toBeUndefined()
    expect(init.headers).toEqual({})
  })

  it('POST 는 JSON 본문과 Content-Type 만 보낸다 — X-Session-Id 헤더는 없다 (P9b)', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, {}))
    vi.stubGlobal('fetch', fetchMock)
    // 예전 세션 키가 남아 있어도 보내지 않는다.
    window.localStorage.setItem('relationship.session_id', 'sess-old')
    await apiFetch('/chat', { method: 'POST', body: { utterance: '안녕' } })
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/chat')
    expect(init.method).toBe('POST')
    expect(init.body).toBe('{"utterance":"안녕"}')
    expect(init.headers).toEqual({ 'Content-Type': 'application/json' })
    expect(Object.keys(init.headers).map((k) => k.toLowerCase())).not.toContain('x-session-id')
    window.localStorage.clear()
  })

  it("모든 요청이 credentials: 'same-origin' 을 명시한다 (GET·POST)", async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(jsonResponse(200, {})))
    vi.stubGlobal('fetch', fetchMock)
    await apiFetch('/persons')
    await apiFetch('/chat', { method: 'POST', body: {} })
    expect(fetchMock.mock.calls[0][1].credentials).toBe('same-origin')
    expect(fetchMock.mock.calls[1][1].credentials).toBe('same-origin')
  })

  it('204 응답은 본문을 읽지 않는다 — json() 을 부르지 않고 undefined 를 돌려준다 (R-3)', async () => {
    const response = new Response(null, { status: 204 })
    const jsonSpy = vi.spyOn(response, 'json')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response))
    await expect(apiFetch('/auth/logout', { method: 'POST', body: {} })).resolves.toBeUndefined()
    expect(jsonSpy).not.toHaveBeenCalled()
  })

  it('401 이면 전역 로그아웃됨 신호를 한 번 올리고 ApiError 도 던진다', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(401, { detail: { code: 'unauthenticated' } })))
    const listener = vi.fn()
    const off = onUnauthorized(listener)
    const err = await failureOf(apiFetch('/persons'))
    off()
    expect(err.status).toBe(401)
    expect(err.code).toBe('unauthenticated')
    expect(listener).toHaveBeenCalledTimes(1)
  })

  it('401 이 아닌 오류와 signalUnauthorized:false 인 401 은 신호를 올리지 않는다', async () => {
    const listener = vi.fn()
    const off = onUnauthorized(listener)
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(403, { detail: { code: 'bad_origin' } })))
    await failureOf(apiFetch('/chat', { method: 'POST', body: {} }))
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(401, { detail: { code: 'invalid_credentials' } })))
    await failureOf(apiFetch('/auth/login', { method: 'POST', body: {}, signalUnauthorized: false }))
    off()
    expect(listener).not.toHaveBeenCalled()
  })

  it('로그인 401(invalid_credentials)은 전역 신호 없이 code 로 올라온다', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(401, { detail: { code: 'invalid_credentials' } })))
    const listener = vi.fn()
    const off = onUnauthorized(listener)
    const err = await failureOf(login({ username: 'a', password: 'b' }))
    off()
    expect(err.code).toBe('invalid_credentials')
    expect(listener).not.toHaveBeenCalled()
  })

  it('logout 은 endpoint 가 있으면 본문에 담고 없으면 빈 객체를 보낸다 (204)', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response(null, { status: 204 })))
    vi.stubGlobal('fetch', fetchMock)
    await logout('https://push.example/ep1')
    await logout()
    expect(fetchMock.mock.calls[0][0]).toBe('/api/auth/logout')
    expect(fetchMock.mock.calls[0][1].method).toBe('POST')
    expect(fetchMock.mock.calls[0][1].body).toBe('{"endpoint":"https://push.example/ep1"}')
    expect(fetchMock.mock.calls[1][1].body).toBe('{}')
  })

  it('getChatHistory 는 limit 를 쿼리로 보낸다 — 기본은 결정 I 의 50', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(jsonResponse(200, [])))
    vi.stubGlobal('fetch', fetchMock)
    await getChatHistory()
    await getChatHistory(7)
    expect(CHAT_HISTORY_LIMIT).toBe(50)
    expect(fetchMock.mock.calls[0][0]).toBe('/api/chat/history?limit=50')
    expect(fetchMock.mock.calls[1][0]).toBe('/api/chat/history?limit=7')
  })

  it('P5 오류 규약 {"detail":{"code"}} 를 ApiError 로 올린다', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(409, { detail: { code: 'already_answered' } })))
    const err = await failureOf(apiFetch('/answers/1', { method: 'POST', body: { answer: 'x' } }))
    expect(err).toBeInstanceOf(ApiError)
    expect(err.status).toBe(409)
    expect(err.code).toBe('already_answered')
  })

  it('규약 밖 본문(422 검증 목록, 비-JSON 5xx)은 code 가 null', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse(422, { detail: [{ msg: 'x' }] })))
    const e422 = await failureOf(apiFetch('/chat'))
    expect(e422.status).toBe(422)
    expect(e422.code).toBeNull()

    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('boom', { status: 500 })))
    const e500 = await failureOf(apiFetch('/chat'))
    expect(e500.status).toBe(500)
    expect(e500.code).toBeNull()
  })

  it('테스트 환경의 기본 fetch 는 실제 네트워크를 쓰지 않고 실패한다 (결정 J)', async () => {
    await expect(apiFetch('/persons')).rejects.toThrow('실제 네트워크')
  })
})
