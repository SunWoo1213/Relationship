// 채팅 화면 (U5, 결정 D·E·L) — 챗봇형 대화 UI + 응답 아래 확인 칩.
// 서버가 준 문자열(reply · question · options)은 고치지 않고 그대로 보여 준다 (원칙7).
// 이 파일이 만드는 문장은 아래 NOTICE 의 오류·빈 상태 안내와 링크 글자뿐이다.
// 대화 기록은 React 상태에만 둔다 — 새로고침하면 지워진다(서버에 대화 이력 API 없음).
import { useCallback, useEffect, useRef, useState, type KeyboardEvent } from 'react'
import { SendIcon } from 'lucide-react'
import { ApiError, getPendingQuestions, postAnswer, postChat } from '@/api/client'
import type { ChatPendingQuestionOut, StoredOut } from '@/api/types'
import { notifyPersonsChanged } from '@/components/PersonsProvider'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { HREF } from '@/routes'

/** 프론트가 만드는 고정 안내 문장(오류·빈 상태). 서버 메시지가 아니다. */
export const NOTICE = {
  empty: '메시지를 입력해 대화를 시작하세요.',
  failed: '요청을 처리하지 못했어요. 잠시 후 다시 시도해 주세요.',
  questionClosed: '이미 답했거나 만료된 질문이에요.',
  sessionReset: '세션이 초기화됐어요. 다시 보내 주세요.',
  restoreFailed: '이전에 남은 질문을 불러오지 못했어요.',
  personsLink: '인물 카드 보기',
} as const

/** 입력창 자동 높이의 상한(px). */
const INPUT_MAX_HEIGHT = 160

interface QuestionState {
  id: number
  options: string[]
  /** 누른 칩(= options 의 문자열). 없으면 아직 안 눌림. */
  selected: string | null
  /** 409 로 닫힌 질문 — 칩 전부 비활성. */
  closed: boolean
  notice: string | null
}

interface Message {
  key: number
  role: 'user' | 'bot'
  text: string
  question?: QuestionState
  /** 카드 화면으로 가는 링크를 붙일지(저장된 인물·사건이 있을 때). */
  link?: boolean
}

function hasStored(stored: StoredOut): boolean {
  return stored.persons > 0 || stored.events > 0
}

function toQuestion(q: ChatPendingQuestionOut): QuestionState {
  return { id: q.question_id, options: q.options, selected: null, closed: false, notice: null }
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 py-2" role="status" aria-label="응답 대기 중" data-testid="typing">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="size-1.5 animate-bounce rounded-full bg-muted-foreground"
          style={{ animationDelay: `${i * 150}ms` }}
        />
      ))}
    </div>
  )
}

function QuestionChips({
  question,
  onPick,
}: {
  question: QuestionState
  onPick: (questionId: number, option: string) => void
}) {
  const locked = question.closed || question.selected !== null
  return (
    <div className="mt-2" data-testid={`chips-${question.id}`}>
      <div className="flex flex-wrap gap-2">
        {question.options.map((option, i) => {
          const pressed = question.selected === option
          return (
            <Button
              key={`${i}-${option}`}
              type="button"
              size="sm"
              variant={pressed ? 'default' : 'outline'}
              aria-pressed={pressed}
              disabled={locked}
              onClick={() => onPick(question.id, option)}
            >
              {option}
            </Button>
          )
        })}
      </div>
      {question.notice && (
        <p role="status" className="mt-1 text-sm text-muted-foreground">
          {question.notice}
        </p>
      )}
    </div>
  )
}

export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>([])
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [waiting, setWaiting] = useState(0)
  const [notice, setNotice] = useState<string | null>(null)
  const nextKey = useRef(1)
  const listRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const newKey = () => nextKey.current++

  const patchQuestion = useCallback((questionId: number, patch: Partial<QuestionState>) => {
    setMessages((prev) =>
      prev.map((m) =>
        m.question && m.question.id === questionId ? { ...m, question: { ...m.question, ...patch } } : m,
      ),
    )
  }, [])

  // 진입 시 미답변 질문 전부를 질문별로 복원한다 (결정 E).
  useEffect(() => {
    let alive = true
    getPendingQuestions()
      .then((list) => {
        if (!alive) return
        setMessages((prev) => {
          const have = new Set(prev.flatMap((m) => (m.question ? [m.question.id] : [])))
          const restored = list
            .filter((q) => !have.has(q.question_id))
            .map<Message>((q) => ({ key: newKey(), role: 'bot', text: q.question, question: toQuestion(q) }))
          return restored.length ? [...restored, ...prev] : prev
        })
      })
      .catch(() => {
        // 복원 실패는 한 줄로 알린다(R-U5-2) — 대화는 새 발화로 계속할 수 있다.
        if (alive) setNotice(NOTICE.restoreFailed)
      })
    return () => {
      alive = false
    }
  }, [])

  // 새 메시지·타이핑 점이 생기면 맨 아래로.
  useEffect(() => {
    const el = listRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [messages, waiting])

  const resizeInput = () => {
    const el = inputRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, INPUT_MAX_HEIGHT)}px`
  }

  function failureNotice(error: unknown): string {
    if (error instanceof ApiError && error.status === 422 && error.code === 'invalid_session_id') {
      return NOTICE.sessionReset
    }
    return NOTICE.failed
  }

  async function send() {
    const text = draft.trim()
    if (!text || sending) return
    setDraft('')
    requestAnimationFrame(resizeInput)
    setNotice(null)
    setMessages((prev) => [...prev, { key: newKey(), role: 'user', text }])
    setSending(true)
    setWaiting((n) => n + 1)
    try {
      const out = await postChat(text)
      if (out.stored.persons > 0) notifyPersonsChanged() // 사이드바 인물 목록 다시 읽기 (R-U6-2)
      setMessages((prev) => [
        ...prev,
        {
          key: newKey(),
          role: 'bot',
          text: out.reply,
          question: out.pending_question ? toQuestion(out.pending_question) : undefined,
          link: hasStored(out.stored),
        },
      ])
    } catch (error) {
      setNotice(failureNotice(error))
    } finally {
      setSending(false)
      setWaiting((n) => n - 1)
    }
  }

  async function pick(questionId: number, option: string) {
    setNotice(null)
    patchQuestion(questionId, { selected: option, notice: null })
    setWaiting((n) => n + 1)
    try {
      const out = await postAnswer(questionId, option)
      if (out.stored.persons > 0) notifyPersonsChanged()
      setMessages((prev) => [
        ...prev,
        {
          key: newKey(),
          role: 'bot',
          text: out.reply,
          question: out.pending_question ? toQuestion(out.pending_question) : undefined,
          link: hasStored(out.stored),
        },
      ])
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        // already_answered · expired — 그 질문의 칩을 비활성으로 두고 재시도하지 않는다 (결정 E).
        patchQuestion(questionId, { selected: null, closed: true, notice: NOTICE.questionClosed })
      } else {
        patchQuestion(questionId, { selected: null })
        setNotice(failureNotice(error))
      }
    } finally {
      setWaiting((n) => n - 1)
    }
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    // 한글 조합 중 Enter 는 전송이 아니다. Shift+Enter 는 줄바꿈.
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      void send()
    }
  }

  return (
    <section aria-labelledby="screen-title" data-screen="chat" className="mx-auto flex h-full max-w-3xl flex-col">
      <h1 id="screen-title" className="sr-only">
        채팅
      </h1>

      <div ref={listRef} className="min-h-0 flex-1 space-y-4 overflow-y-auto pb-4" data-testid="message-list">
        {messages.length === 0 && waiting === 0 && (
          <p className="pt-8 text-center text-muted-foreground">{NOTICE.empty}</p>
        )}
        {messages.map((m) =>
          m.role === 'user' ? (
            <div key={m.key} className="flex justify-end">
              <div
                data-role="user"
                className="max-w-[80%] whitespace-pre-wrap rounded-2xl bg-primary px-4 py-2 text-primary-foreground"
              >
                {m.text}
              </div>
            </div>
          ) : (
            <div key={m.key} data-role="bot" className="max-w-[90%]">
              <p className="whitespace-pre-wrap">{m.text}</p>
              {m.link && (
                <a href={HREF.persons} className="mt-1 inline-block text-sm text-primary underline">
                  {NOTICE.personsLink}
                </a>
              )}
              {m.question && <QuestionChips question={m.question} onPick={(id, o) => void pick(id, o)} />}
            </div>
          ),
        )}
        {waiting > 0 && <TypingDots />}
      </div>

      <div className="shrink-0 pt-2">
        {notice && (
          <p role="alert" className="pb-2 text-sm text-destructive">
            {notice}
          </p>
        )}
        <div className="flex items-end gap-2 rounded-2xl border bg-card p-2">
          <textarea
            ref={inputRef}
            value={draft}
            rows={1}
            aria-label="메시지 입력"
            onChange={(e) => {
              setDraft(e.target.value)
              resizeInput()
            }}
            onKeyDown={onKeyDown}
            className={cn(
              'max-h-40 min-h-9 flex-1 resize-none bg-transparent px-2 py-1.5 outline-none',
              'placeholder:text-muted-foreground',
            )}
          />
          <Button
            type="button"
            size="icon"
            aria-label="보내기"
            disabled={sending || draft.trim() === ''}
            onClick={() => void send()}
          >
            <SendIcon />
          </Button>
        </div>
      </div>
    </section>
  )
}
