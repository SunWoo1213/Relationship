// E2E 공통 가짜 API (결정 J, 판정 27b행) -- 실제 백엔드·LLM·푸시 서비스로 아무것도 보내지 않는다.
// - `/api/` 요청은 전부 아래 표가 대신 답한다. 표에 없는 요청은 중단시키고 unexpected 에 남긴다.
// - preview 호스트 밖으로 나가는 요청(외부 CDN·글꼴 등)도 중단시킨다.
// - 브라우저가 낸 요청 URL 을 전부 모아 두었다가, 각 spec 끝에서 "앱 파일 또는 /api/ 경로뿐" 인지 단언한다.
import { expect, type Page } from '@playwright/test'

export interface ApiCall {
  method: string
  /** 경로 + 쿼리 (예: `/api/briefings?schedule_id=7`) */
  path: string
  headers: Record<string, string>
  body: unknown
}

export interface FakeReply {
  status?: number
  json: unknown
}

/** 표의 키는 `"GET /api/persons"` 처럼 `메서드 경로(쿼리 포함)`. 값이 함수면 요청마다 새로 답한다(상태가 있는 가짜). */
export type ApiTable = Record<string, FakeReply | ((call: ApiCall) => FakeReply)>

export interface FakeApi {
  /** 브라우저가 낸 모든 요청 URL (앱 파일 포함, 중단된 것 포함). */
  requests: string[]
  /** `/api/` 로 간 요청, 도착 순서대로. */
  calls: ApiCall[]
  /** 표에 없어서 중단시킨 `/api/` 요청 (`메서드 경로`). 비어 있어야 한다. */
  unexpected: string[]
  /** 지정한 키로 들어온 요청만. */
  callsTo: (key: string) => ApiCall[]
}

/** 시간을 고정한다 -- 화면의 날짜 표기가 실행 시각에 흔들리지 않게(결정 J). */
export async function freezeClock(page: Page) {
  await page.clock.setFixedTime(new Date('2026-10-15T09:00:00+09:00'))
}

/**
 * 로그인 관문(P9b U6)을 통과시키는 기본 응답. 표에 같은 키가 있으면 표가 우선한다.
 * - `/auth/me` 200: 앱 틀이 열린다.
 * - `/chat/history?limit=50`: 채팅 화면이 마운트 때 부르는 기록 조회 — 기본은 빈 기록.
 */
const SESSION_DEFAULTS: ApiTable = {
  'GET /api/auth/me': { json: { id: 'u-e2e', username: 'e2e_user' } },
  'GET /api/chat/history?limit=50': { json: [] },
}

export async function installFakeApi(page: Page, baseURL: string, givenTable: ApiTable): Promise<FakeApi> {
  const table: ApiTable = { ...SESSION_DEFAULTS, ...givenTable }
  const requests: string[] = []
  const calls: ApiCall[] = []
  const unexpected: string[] = []
  const origin = new URL(baseURL).origin

  page.on('request', (request) => requests.push(request.url()))

  // 1) 이 호스트 밖으로 나가는 요청은 전부 중단 (먼저 등록 -- 아래 /api/ 규칙이 더 나중이라 우선한다).
  await page.route(
    (url) => url.origin !== origin,
    (route) => route.abort('blockedbyclient'),
  )

  // 2) /api/ 는 표가 답한다. 표에 없으면 중단 + 기록.
  await page.route('**/api/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    const path = url.pathname + url.search
    const key = `${request.method()} ${path}`
    let body: unknown = undefined
    const raw = request.postData()
    if (raw) body = JSON.parse(raw)
    const call: ApiCall = { method: request.method(), path, headers: request.headers(), body }
    const entry = table[key]
    if (entry === undefined) {
      unexpected.push(key)
      await route.abort('failed')
      return
    }
    calls.push(call)
    const reply = typeof entry === 'function' ? entry(call) : entry
    const status = reply.status ?? 200
    // 204 는 본문이 없다(로그아웃 — 계약 표).
    if (status === 204) {
      await route.fulfill({ status })
      return
    }
    await route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify(reply.json),
    })
  })

  return {
    requests,
    calls,
    unexpected,
    callsTo: (key) => calls.filter((c) => `${c.method} ${c.path}` === key),
  }
}

/** 앱이 스스로 읽는 정적 파일 경로(빌드 산출물). 이 밖의 경로는 앱 파일이 아니다. */
const APP_FILE = /^\/(assets\/[^/]+|index\.html|favicon\.svg|icon-\d+\.svg|manifest\.webmanifest)?$/

/** 판정 27b -- 요청 URL 전부가 preview 호스트의 앱 파일 또는 `/api/` 경로이고, 표에 없는 요청이 없었다. */
export function expectNoStrayRequests(api: FakeApi, baseURL: string) {
  const origin = new URL(baseURL).origin
  const strays = api.requests.filter((href) => {
    const url = new URL(href)
    if (url.origin !== origin) return true
    return !(url.pathname.startsWith('/api/') || APP_FILE.test(url.pathname))
  })
  expect(strays, '앱 파일·/api/ 밖으로 나간 요청').toEqual([])
  expect(api.unexpected, '가짜 표에 없는 /api/ 요청').toEqual([])
  expect(api.requests.length, '요청을 하나도 모으지 못했다').toBeGreaterThan(0)
}
