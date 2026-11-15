// fetch 래퍼. 기본 경로는 `/api` (결정 C (ii) — 개발 서버·운영 프록시가 접두를 벗긴다).
// 호출 함수(채팅·카드·브리핑)는 U5~U8 이 이 래퍼 위에 만든다. 계정 함수는 P9b U6.

import type {
  AnswerIn,
  AvailabilityOut,
  SignupIn,
  AnswerOut,
  BriefingRecordOut,
  BriefingRunIn,
  BriefingRunOut,
  ChatHistoryItemOut,
  ChatIn,
  ChatOut,
  ChatPendingQuestionOut,
  Credentials,
  EventRawOut,
  FactSourcesOut,
  LogoutIn,
  MeOut,
  PersonCardOut,
  PersonListItemOut,
  PushSubscriptionIn,
  PushSubscriptionOut,
  VapidPublicKeyOut,
} from '@/api/types'

export const API_BASE = '/api'

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
  signal?: AbortSignal
  /**
   * 401 을 받았을 때 전역 "로그아웃됨" 신호를 올릴지(기본 true). 로그인·`/auth/me`·로그아웃은 401 이
   * 정상 응답의 한 갈래라 끈다 — 호출 쪽이 직접 다룬다.
   */
  signalUnauthorized?: boolean
}

// --- 전역 로그아웃됨 신호 (P9b U6) ---
// 로그인한 뒤 쿠키가 만료·삭제되면 어떤 호출이든 401 을 받는다. App 이 이 신호를 구독해 관문(로그인 화면)으로 돌아간다.
const unauthorizedListeners = new Set<() => void>()

/** 401 신호를 구독한다. 해제 함수를 돌려준다. */
export function onUnauthorized(listener: () => void): () => void {
  unauthorizedListeners.add(listener)
  return () => {
    unauthorizedListeners.delete(listener)
  }
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

  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method ?? 'GET',
    headers,
    // 같은 출처 쿠키(로그인 세션)가 실린다. fetch 기본값이지만 의도를 드러내려 명시한다 (P9b 사실 12).
    credentials: 'same-origin',
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
    if (response.status === 401 && options.signalUnauthorized !== false) {
      unauthorizedListeners.forEach((listener) => listener())
    }
    throw new ApiError(response.status, code)
  }
  // 204 는 본문이 없다 — 읽으면 예외가 난다 (P9b R-3).
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

// --- 채팅 (POST /chat · POST /answers/{id} · GET /questions/pending · GET /chat/history) ---

/** 발화를 보낸다. 대화 세션은 서버가 로그인 계정에서 만든다 — 프론트는 세션 id 를 보내지도 보관하지도 않는다. */
export function postChat(utterance: string): Promise<ChatOut> {
  const body: ChatIn = { utterance }
  return apiFetch<ChatOut>('/chat', { method: 'POST', body })
}

/** 마운트 때 불러오는 대화 기록 개수 (P9b 결정 I). 서버가 오래된 것 → 최근 순으로 준다. */
export const CHAT_HISTORY_LIMIT = 50

/** 이 계정의 대화 기록. limit 를 생략하면 결정 I 의 개수. 호출 쪽은 재정렬하지 않는다. */
export function getChatHistory(limit: number = CHAT_HISTORY_LIMIT): Promise<ChatHistoryItemOut[]> {
  return apiFetch<ChatHistoryItemOut[]>(`/chat/history?limit=${limit}`)
}

/** 칩의 글자(= options 의 문자열 그대로)를 답으로 보낸다. */
export function postAnswer(questionId: number, answer: string): Promise<AnswerOut> {
  const body: AnswerIn = { answer }
  return apiFetch<AnswerOut>(`/answers/${questionId}`, { method: 'POST', body })
}

// --- 인물 (GET /persons · /persons/{id} · /events/{id}/raw · /persons/{id}/facts/{fact_id}/sources) ---

/** 서버가 마지막 접촉 내림차순으로 준다 — 호출 쪽은 재정렬하지 않는다. */
export function getPersons(): Promise<PersonListItemOut[]> {
  return apiFetch<PersonListItemOut[]>('/persons')
}

export function getPersonCard(personId: number): Promise<PersonCardOut> {
  return apiFetch<PersonCardOut>(`/persons/${personId}`)
}

/** 결정 F: 원문은 펼칠 때만 한 건씩 가져온다. */
export function getEventRaw(eventId: number): Promise<EventRawOut> {
  return apiFetch<EventRawOut>(`/events/${eventId}/raw`)
}

export function getFactSources(personId: number, factId: number): Promise<FactSourcesOut> {
  return apiFetch<FactSourcesOut>(`/persons/${personId}/facts/${factId}/sources`)
}

// --- 브리핑 (GET /briefings · POST /briefings/run) ---

/**
 * 저장된 브리핑. 서버가 일정 시각 내림차순(7일 창, 상한 20)으로 준다 — 호출 쪽은 재정렬하지 않는다.
 * scheduleId 를 주면 그 일정 1건(기간 무시) 또는 `[]`, 없거나 남의 일정이면 404.
 */
export function getBriefings(scheduleId?: number): Promise<BriefingRecordOut[]> {
  const query = scheduleId === undefined ? '' : `?schedule_id=${scheduleId}`
  return apiFetch<BriefingRecordOut[]>(`/briefings${query}`)
}

/** 수동 브리핑. 404 는 잠금 중(결정 K) — 호출 쪽이 안내만 하고 다시 보내지 않는다. */
export function postBriefingRun(scheduleId: number): Promise<BriefingRunOut> {
  const body: BriefingRunIn = { schedule_id: scheduleId }
  return apiFetch<BriefingRunOut>('/briefings/run', { method: 'POST', body })
}

// --- 푸시 구독 (GET /push/vapid-public-key · POST /push/subscriptions) ---
// 둘 다 미설정이면 404 `push_not_configured` (P7 결정 D·F).

export function getVapidPublicKey(): Promise<VapidPublicKeyOut> {
  return apiFetch<VapidPublicKeyOut>('/push/vapid-public-key')
}

export function postPushSubscription(body: PushSubscriptionIn): Promise<PushSubscriptionOut> {
  return apiFetch<PushSubscriptionOut>('/push/subscriptions', { method: 'POST', body })
}

/** 이 계정의 미답변 질문 전부. */
export function getPendingQuestions(): Promise<ChatPendingQuestionOut[]> {
  return apiFetch<ChatPendingQuestionOut[]>('/questions/pending')
}

// --- 계정 (POST /auth/signup · /auth/login · /auth/logout · GET /auth/me) ---
// 401 은 정상 응답의 한 갈래(로그인 실패·미로그인)라 전역 신호를 끄고 호출 쪽이 다룬다.

/** 가입 — 201 이고 즉시 로그인 쿠키가 실린다 (P9b 결정 G). */
export function signup(body: SignupIn): Promise<MeOut> {
  return apiFetch<MeOut>('/auth/signup', { method: 'POST', body, signalUnauthorized: false })
}

/** 가입 화면의 "중복 확인". 준 키만 쿼리에 싣는다. 로그인 없이 부르는 조회라 401 관문 신호를 내지 않는다. */
export function checkAvailability(q: { username?: string; nickname?: string }): Promise<AvailabilityOut> {
  const params = new URLSearchParams()
  if (q.username !== undefined) params.set('username', q.username)
  if (q.nickname !== undefined) params.set('nickname', q.nickname)
  return apiFetch<AvailabilityOut>(`/auth/availability?${params.toString()}`, { signalUnauthorized: false })
}

export function login(credentials: Credentials): Promise<MeOut> {
  return apiFetch<MeOut>('/auth/login', { method: 'POST', body: credentials, signalUnauthorized: false })
}

/** 지금 로그인한 계정. 미로그인이면 401 ApiError. */
export function getMe(): Promise<MeOut> {
  return apiFetch<MeOut>('/auth/me', { signalUnauthorized: false })
}

/**
 * 로그아웃(204). endpoint 가 있으면 서버가 그 구독 행을 지운다 (P9b 결정 P).
 * 이미 로그아웃된 상태의 401 은 "이미 로그아웃됨" 으로 보고 오류 없이 끝낸다 (F-3).
 */
export async function logout(endpoint?: string): Promise<void> {
  const body: LogoutIn = endpoint ? { endpoint } : {}
  try {
    await apiFetch<void>('/auth/logout', { method: 'POST', body, signalUnauthorized: false })
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return
    throw error
  }
}
