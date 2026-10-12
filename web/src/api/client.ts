// fetch 래퍼. 기본 경로는 `/api` (결정 C (ii) — 개발 서버·운영 프록시가 접두를 벗긴다).
// 호출 함수(채팅·카드·브리핑)는 U5~U8 이 이 래퍼 위에 만든다.

export const API_BASE = '/api'
export const SESSION_HEADER = 'X-Session-Id'

/** P5 오류 규약: 4xx/5xx 본문은 `{"detail": {"code": "..."}}` (예: 404 not_found, 409 already_answered). */
export interface ApiErrorBody {
  detail: { code: string }
}

export class ApiError extends Error {
  readonly status: number
  /** `detail.code`. 규약 밖 본문(예: 422 검증 목록, 5xx 비-JSON)이면 null. */
  readonly code: string | null

  constructor(status: number, code: string | null) {
    super(code ? `API ${status} ${code}` : `API ${status}`)
    this.name = 'ApiError'
    this.status = status
    this.code = code
  }
}

export interface RequestOptions {
  method?: 'GET' | 'POST'
  /** JSON 으로 직렬화해 보낸다. */
  body?: unknown
  /** 있으면 `X-Session-Id` 헤더로 보낸다 (결정 D — 세션 보관은 U5). */
  sessionId?: string | null
  signal?: AbortSignal
}

function readErrorCode(body: unknown): string | null {
  if (typeof body !== 'object' || body === null || !('detail' in body)) return null
  const detail = (body as { detail: unknown }).detail
  if (typeof detail !== 'object' || detail === null || !('code' in detail)) return null
  const code = (detail as { code: unknown }).code
  return typeof code === 'string' ? code : null
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {}
  if (options.body !== undefined) headers['Content-Type'] = 'application/json'
  if (options.sessionId) headers[SESSION_HEADER] = options.sessionId

  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method ?? 'GET',
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
    signal: options.signal,
  })

  if (!response.ok) {
    let code: string | null = null
    try {
      code = readErrorCode(await response.json())
    } catch {
      code = null
    }
    throw new ApiError(response.status, code)
  }
  return (await response.json()) as T
}
