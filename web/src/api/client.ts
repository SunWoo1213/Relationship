// fetch 래퍼. 기본 경로는 `/api` (결정 C (ii) — 개발 서버·운영 프록시가 접두를 벗긴다).
// 호출 함수(채팅·카드·브리핑)는 U5~U8 이 이 래퍼 위에 만든다.

import { clearSessionId, getSessionId, setSessionId } from '@/session'
import type {
  AnswerIn,
  AnswerOut,
  BriefingRecordOut,
  BriefingRunIn,
  BriefingRunOut,
  ChatIn,
  ChatOut,
  ChatPendingQuestionOut,
  EventRawOut,
  FactSourcesOut,
  PersonCardOut,
  PersonListItemOut,
} from '@/api/types'

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
  /** 생략하면 보관된 세션(localStorage)을 `X-Session-Id` 로 보낸다 (결정 D). null 이면 헤더 없이 보낸다. */
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
  const sessionId = options.sessionId === undefined ? getSessionId() : options.sessionId
  if (sessionId) headers[SESSION_HEADER] = sessionId

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
    // 서버가 세션을 알아보지 못하면(P5 422) 저장된 세션을 버린다 — 다음 요청은 헤더 없이 가서 새로 발급받는다.
    if (response.status === 422 && code === 'invalid_session_id') clearSessionId()
    throw new ApiError(response.status, code)
  }
  return (await response.json()) as T
}

// --- 채팅 (POST /chat · POST /answers/{id} · GET /questions/pending) ---

/** 발화를 보내고, 응답의 session_id 를 보관한다 (결정 D). */
export async function postChat(utterance: string): Promise<ChatOut> {
  const body: ChatIn = { utterance }
  const out = await apiFetch<ChatOut>('/chat', { method: 'POST', body })
  if (out.session_id) setSessionId(out.session_id)
  return out
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

/** 이 세션의 미답변 질문 전부. 세션이 없으면 서버가 빈 목록을 준다. */
export function getPendingQuestions(): Promise<ChatPendingQuestionOut[]> {
  return apiFetch<ChatPendingQuestionOut[]>('/questions/pending')
}
