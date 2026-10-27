// app/api/schemas.py 의 Out/In 모델을 손으로 옮긴 TS 타입.
// 필드 이름·선택성·null 을 원본과 같게 둔다. datetime 은 JSON 에서 ISO 8601 문자열이다.
// 서버가 준 문자열(reply·options·브리핑 줄)은 가공하지 않고 그대로 보여 준다 (원칙7).

/** ISO 8601 문자열 (pydantic datetime 직렬화). */
export type IsoDateTime = string

// --- 채팅 · 답변 (POST /chat, POST /answers/{question_id}) ---

export interface ChatIn {
  utterance: string
}

export interface StoredOut {
  persons: number
  events: number
  schedules: number
}

export interface ChatPendingQuestionOut {
  question_id: number
  status: string
  kind: string
  question: string
  options: string[]
}

export interface ChatOut {
  reply: string
  session_id: string
  stored: StoredOut
  pending_question: ChatPendingQuestionOut | null
  stop_reason: string | null
  trace_ids: number[]
}

export interface AnswerIn {
  answer: string
}

export interface AnswerOut {
  question_id: number
  status: string
  reply: string
  stored: StoredOut
  pending_question: ChatPendingQuestionOut | null
  stop_reason: string | null
  trace_ids: number[]
}

// --- 인물 목록·카드 (GET /persons, GET /persons/{person_id}) ---

export interface PersonListItemOut {
  id: number
  display_name: string
  relation_tag: string
  hierarchy: string
  last_contact_at: IsoDateTime | null
  // 카드 응답 aliases 와 같은 값·순서(읽기 전용, P8b U0)
  aliases: string[]
}

export interface PersonBasicOut {
  id: number
  display_name: string
  relation_tag: string
  hierarchy: string
}

export interface PersonFactOut {
  id: number
  key: string
  value: string
  updated_at: IsoDateTime
  source_count: number
}

export interface PersonPatternOut {
  id: number
  key: string
  value: string
  source_count: number
}

export interface TimelineEventOut {
  id: number
  type: string
  content: string
  occurred_at: IsoDateTime
}

export interface UpcomingScheduleOut {
  id: number
  title: string
  scheduled_at: IsoDateTime
  briefed_at: IsoDateTime | null
}

export interface PersonCardOut {
  person: PersonBasicOut
  aliases: string[]
  last_contact_at: IsoDateTime | null
  facts: PersonFactOut[]
  patterns: PersonPatternOut[]
  timeline: TimelineEventOut[]
  upcoming_schedules: UpcomingScheduleOut[]
}

// --- 원문 조회 (GET /events/{event_id}/raw, GET /persons/{id}/facts/{fact_id}/sources) ---

export interface EventRawOut {
  event_id: number
  person_id: number
  type: string
  content: string
  occurred_at: IsoDateTime
  raw_utterance: string
}

export interface FactBriefOut {
  id: number
  key: string
  value: string
}

export interface FactSourceEventOut {
  event_id: number
  type: string
  content: string
  occurred_at: IsoDateTime
  raw_utterance: string
}

export interface FactSourcesOut {
  fact: FactBriefOut
  sources: FactSourceEventOut[]
}

// --- 브리핑 (GET /briefings, POST /briefings/run) ---

export interface BriefingBasisOut {
  fact_keys: string[]
  event_ids: number[]
}

export interface BriefingLineOut {
  text: string
  basis: BriefingBasisOut
}

export interface BriefingSuggestionOut {
  text: string
  basis: BriefingBasisOut
}

export interface BriefingPatternSentenceOut {
  key: string
  sentence: string
}

export type BriefingComposer = 'llm' | 'template'

export interface BriefingScheduleOut {
  id: number
  title: string
  scheduled_at: IsoDateTime
}

export interface BriefingPersonOut {
  id: number
  display_name: string
}

/** GET /briefings 항목 하나 (저장된 briefing_compose trace). */
export interface BriefingRecordOut {
  schedule: BriefingScheduleOut
  person: BriefingPersonOut
  generated_at: IsoDateTime
  composer: BriefingComposer
  pattern_sentences: BriefingPatternSentenceOut[]
  lines: BriefingLineOut[]
  suggestion: BriefingSuggestionOut | null
  push: string
  trace_id: number
}

export interface BriefingRunIn {
  schedule_id?: number | null
}

/** POST /briefings/run 응답의 브리핑 하나. */
export interface BriefingItemOut {
  schedule_id: number
  person_id: number
  composer: BriefingComposer
  pattern_sentences: BriefingPatternSentenceOut[]
  lines: BriefingLineOut[]
  suggestion: BriefingSuggestionOut | null
  push: string
}

export interface BriefingSkippedOut {
  schedule_id: number
  reason: string
}

export interface BriefingRunOut {
  run_id: string
  generated_at: IsoDateTime
  briefings: BriefingItemOut[]
  skipped: BriefingSkippedOut[]
}

// --- 푸시 (GET /push/vapid-public-key, POST /push/subscriptions) ---

export interface VapidPublicKeyOut {
  public_key: string
}

export interface PushSubscriptionKeysIn {
  p256dh: string
  auth: string
}

export interface PushSubscriptionIn {
  endpoint: string
  keys: PushSubscriptionKeysIn
  expirationTime?: number | null
}

export interface PushSubscriptionOut {
  id: number
  created: boolean
}
