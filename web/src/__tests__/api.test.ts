import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, apiFetch } from '@/api/client'

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

  it('POST 는 JSON 본문과 X-Session-Id 헤더를 보낸다', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, {}))
    vi.stubGlobal('fetch', fetchMock)
    await apiFetch('/chat', { method: 'POST', body: { utterance: '안녕' }, sessionId: 'abc-1' })
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/chat')
    expect(init.method).toBe('POST')
    expect(init.body).toBe('{"utterance":"안녕"}')
    expect(init.headers).toEqual({ 'Content-Type': 'application/json', 'X-Session-Id': 'abc-1' })
  })

  it('sessionId 가 null 이면 헤더를 넣지 않는다', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, {}))
    vi.stubGlobal('fetch', fetchMock)
    await apiFetch('/questions/pending', { sessionId: null })
    expect(fetchMock.mock.calls[0][1].headers).toEqual({})
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
