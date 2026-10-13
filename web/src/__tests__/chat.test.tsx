// U5 채팅 화면 + 확인 칩. 실제 네트워크 없음 — fetch 는 테스트마다 vi.stubGlobal 로 가짜를 건다 (결정 J).
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import ChatScreen, { NOTICE } from '@/screens/ChatScreen'
import { SESSION_STORAGE_KEY } from '@/session'
import type { AnswerOut, ChatOut, ChatPendingQuestionOut } from '@/api/types'

type Handler = (url: string, init: RequestInit) => Response | Promise<Response>

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

function install(handler: Handler) {
  const fn = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    return Promise.resolve(handler(String(input), init ?? {}))
  })
  vi.stubGlobal('fetch', fn)
  return fn
}

function callsTo(fn: ReturnType<typeof install>, path: string) {
  return fn.mock.calls.filter(([url]) => String(url) === path)
}

function headersOf(call: unknown[]): Record<string, string> {
  return (call[1] as RequestInit).headers as Record<string, string>
}

const NO_STORE = { persons: 0, events: 0, schedules: 0 }

function chatOut(patch: Partial<ChatOut> = {}): ChatOut {
  return {
    reply: '응답입니다',
    session_id: 'sess-1',
    stored: NO_STORE,
    pending_question: null,
    stop_reason: null,
    trace_ids: [],
    ...patch,
  }
}

function answerOut(patch: Partial<AnswerOut> = {}): AnswerOut {
  return {
    question_id: 7,
    status: 'answered',
    reply: '답을 반영했습니다',
    stored: NO_STORE,
    pending_question: null,
    stop_reason: null,
    trace_ids: [],
    ...patch,
  }
}

function pq(id: number, options: string[], question = `질문 ${id}`): ChatPendingQuestionOut {
  return { question_id: id, status: 'pending', kind: 'identity', question, options }
}

/** 기본 라우터: 진입 시 복원은 빈 목록. */
function routerWith(overrides: Record<string, Handler>): Handler {
  return (url, init) => {
    if (overrides[url]) return overrides[url](url, init)
    if (url === '/api/questions/pending') return json([])
    throw new Error(`예상하지 못한 요청: ${url}`)
  }
}

async function type(text: string) {
  const user = userEvent.setup()
  await user.type(screen.getByRole('textbox', { name: '메시지 입력' }), text)
  return user
}

async function sendText(text: string) {
  const user = await type(text)
  await user.click(screen.getByRole('button', { name: '보내기' }))
  return user
}

beforeEach(() => {
  window.localStorage.clear()
})

afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe('전송과 세션 (결정 D)', () => {
  it('발화를 POST /api/chat 으로 보내고 내 말풍선과 reply 를 보여 준다', async () => {
    const fetchFn = install(routerWith({ '/api/chat': () => json(chatOut({ reply: '서버가 준 응답' })) }))
    render(<ChatScreen />)
    await sendText('민수랑 점심 먹었어')

    expect(await screen.findByText('서버가 준 응답')).toBeInTheDocument()
    expect(screen.getByText('민수랑 점심 먹었어')).toHaveAttribute('data-role', 'user')
    const [call] = callsTo(fetchFn, '/api/chat')
    expect((call[1] as RequestInit).method).toBe('POST')
    expect(JSON.parse((call[1] as RequestInit).body as string)).toEqual({ utterance: '민수랑 점심 먹었어' })
  })

  it('첫 요청에는 X-Session-Id 가 없고, 응답 session_id 를 저장해 두 번째 요청에 보낸다', async () => {
    const fetchFn = install(routerWith({ '/api/chat': () => json(chatOut({ session_id: 'sess-abc' })) }))
    render(<ChatScreen />)
    await sendText('첫째')
    await screen.findAllByText('응답입니다')

    const first = callsTo(fetchFn, '/api/chat')[0]
    expect(headersOf(first)['X-Session-Id']).toBeUndefined()
    expect(window.localStorage.getItem(SESSION_STORAGE_KEY)).toBe('sess-abc')

    const user = await type('둘째')
    await user.click(screen.getByRole('button', { name: '보내기' }))
    await waitFor(() => expect(callsTo(fetchFn, '/api/chat')).toHaveLength(2))
    expect(headersOf(callsTo(fetchFn, '/api/chat')[1])['X-Session-Id']).toBe('sess-abc')
  })

  it('저장된 세션이 있으면 진입 시 복원 요청에도 헤더를 보낸다', async () => {
    window.localStorage.setItem(SESSION_STORAGE_KEY, 'sess-old')
    const fetchFn = install(routerWith({}))
    render(<ChatScreen />)
    await waitFor(() => expect(callsTo(fetchFn, '/api/questions/pending')).toHaveLength(1))
    expect(headersOf(callsTo(fetchFn, '/api/questions/pending')[0])['X-Session-Id']).toBe('sess-old')
  })

  it('422 invalid_session_id 면 저장된 세션을 버리고 다음 요청은 헤더 없이 간다', async () => {
    window.localStorage.setItem(SESSION_STORAGE_KEY, 'sess-bad')
    let n = 0
    const fetchFn = install(
      routerWith({
        '/api/chat': () => (n++ === 0 ? json({ detail: { code: 'invalid_session_id' } }, 422) : json(chatOut())),
      }),
    )
    render(<ChatScreen />)
    const user = await sendText('안녕')
    expect(await screen.findByText(NOTICE.sessionReset)).toBeInTheDocument()
    expect(window.localStorage.getItem(SESSION_STORAGE_KEY)).toBeNull()

    await user.type(screen.getByRole('textbox', { name: '메시지 입력' }), '다시')
    await user.click(screen.getByRole('button', { name: '보내기' }))
    await waitFor(() => expect(callsTo(fetchFn, '/api/chat')).toHaveLength(2))
    expect(headersOf(callsTo(fetchFn, '/api/chat')[1])['X-Session-Id']).toBeUndefined()
  })
})

describe('입력창', () => {
  it('Enter 는 전송, Shift+Enter 는 줄바꿈', async () => {
    const fetchFn = install(routerWith({ '/api/chat': () => json(chatOut()) }))
    render(<ChatScreen />)
    const user = userEvent.setup()
    const box = screen.getByRole('textbox', { name: '메시지 입력' })
    await user.type(box, '한 줄{Shift>}{Enter}{/Shift}두 줄')
    expect(callsTo(fetchFn, '/api/chat')).toHaveLength(0)
    expect(box).toHaveValue('한 줄\n두 줄')
    await user.keyboard('{Enter}')
    await waitFor(() => expect(callsTo(fetchFn, '/api/chat')).toHaveLength(1))
    expect(JSON.parse((callsTo(fetchFn, '/api/chat')[0][1] as RequestInit).body as string)).toEqual({
      utterance: '한 줄\n두 줄',
    })
  })

  it('빈 입력은 보낼 수 없다', async () => {
    install(routerWith({}))
    render(<ChatScreen />)
    expect(screen.getByRole('button', { name: '보내기' })).toBeDisabled()
    await type('   ')
    expect(screen.getByRole('button', { name: '보내기' })).toBeDisabled()
  })

  it('응답을 기다리는 동안 타이핑 점이 보이고 끝나면 사라진다', async () => {
    let release: (r: Response) => void = () => {}
    install(
      routerWith({
        '/api/chat': () => new Promise<Response>((resolve) => (release = resolve)) as unknown as Response,
      }),
    )
    render(<ChatScreen />)
    await sendText('기다려')
    expect(await screen.findByTestId('typing')).toBeInTheDocument()
    release(json(chatOut()))
    await screen.findByText('응답입니다')
    expect(screen.queryByTestId('typing')).toBeNull()
  })

  it('확인 칩이 떠 있어도 입력은 막히지 않는다 (결정 E)', async () => {
    install(
      routerWith({ '/api/chat': () => json(chatOut({ pending_question: pq(7, ['네', '다른 사람이에요']) })) }),
    )
    render(<ChatScreen />)
    await sendText('민수 만났어')
    await screen.findByRole('button', { name: '네' })
    const box = screen.getByRole('textbox', { name: '메시지 입력' })
    expect(box).toBeEnabled()
    await userEvent.setup().type(box, '계속 말해도 돼')
    expect(box).toHaveValue('계속 말해도 돼')
  })
})

describe('확인 칩 (결정 E)', () => {
  const OPTIONS = ['네, 같은 사람이에요', '아니요, 다른 사람이에요', '잘 모르겠어요']

  it('칩 글자와 순서가 options 와 같다 (reply 바로 아래)', async () => {
    install(routerWith({ '/api/chat': () => json(chatOut({ reply: '확인 부탁', pending_question: pq(7, OPTIONS) })) }))
    render(<ChatScreen />)
    await sendText('민수')
    const group = await screen.findByTestId('chips-7')
    const labels = within(group)
      .getAllByRole('button')
      .map((b) => b.textContent)
    expect(labels).toEqual(OPTIONS)
    const bot = screen.getByText('확인 부탁').closest('[data-role="bot"]') as HTMLElement
    expect(bot).toContainElement(group)
  })

  it('칩을 누르면 POST /api/answers/{id} 에 그 문자열이 {answer} 로 가고, 선택 고정·나머지 비활성', async () => {
    const fetchFn = install(
      routerWith({
        '/api/chat': () => json(chatOut({ pending_question: pq(7, OPTIONS) })),
        '/api/answers/7': () => json(answerOut()),
      }),
    )
    render(<ChatScreen />)
    await sendText('민수')
    const user = userEvent.setup()
    await user.click(await screen.findByRole('button', { name: OPTIONS[1] }))

    await waitFor(() => expect(callsTo(fetchFn, '/api/answers/7')).toHaveLength(1))
    const [call] = callsTo(fetchFn, '/api/answers/7')
    expect((call[1] as RequestInit).method).toBe('POST')
    expect(JSON.parse((call[1] as RequestInit).body as string)).toEqual({ answer: OPTIONS[1] })

    const chosen = screen.getByRole('button', { name: OPTIONS[1] })
    expect(chosen).toHaveAttribute('aria-pressed', 'true')
    for (const other of [OPTIONS[0], OPTIONS[2]]) {
      const b = screen.getByRole('button', { name: other })
      expect(b).toHaveAttribute('aria-pressed', 'false')
      expect(b).toBeDisabled()
    }
    expect(chosen).toBeDisabled()
  })

  it('답 응답의 reply 가 이어 붙고, 새 pending_question 이면 그 아래 새 칩', async () => {
    install(
      routerWith({
        '/api/chat': () => json(chatOut({ reply: '첫 질문', pending_question: pq(7, ['예', '아니오']) })),
        '/api/answers/7': () =>
          json(answerOut({ reply: '이어지는 응답', pending_question: pq(8, ['오늘', '내일', '모레'], '언제인가요') })),
      }),
    )
    render(<ChatScreen />)
    await sendText('x')
    await userEvent.setup().click(await screen.findByRole('button', { name: '예' }))

    const next = await screen.findByText('이어지는 응답')
    const group = await screen.findByTestId('chips-8')
    expect(
      within(group)
        .getAllByRole('button')
        .map((b) => b.textContent),
    ).toEqual(['오늘', '내일', '모레'])
    // 새 칩은 이어 붙은 reply 의 말풍선 안에 있고, 앞 질문 칩은 그대로 고정돼 있다.
    expect(next.closest('[data-role="bot"]')).toContainElement(group)
    expect(screen.getByRole('button', { name: '예' })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByText('첫 질문')).toBeInTheDocument()
  })

  it('진입 시 GET /api/questions/pending 으로 미답변 전부를 질문별로 복원한다', async () => {
    const fetchFn = install(
      routerWith({
        '/api/questions/pending': () => json([pq(3, ['가', '나'], '첫째 질문'), pq(4, ['다', '라', '마'], '둘째 질문')]),
      }),
    )
    render(<ChatScreen />)
    const g3 = await screen.findByTestId('chips-3')
    const g4 = await screen.findByTestId('chips-4')
    expect(within(g3).getAllByRole('button').map((b) => b.textContent)).toEqual(['가', '나'])
    expect(within(g4).getAllByRole('button').map((b) => b.textContent)).toEqual(['다', '라', '마'])
    expect(screen.getByText('첫째 질문')).toBeInTheDocument()
    expect(screen.getByText('둘째 질문')).toBeInTheDocument()
    expect(callsTo(fetchFn, '/api/questions/pending')).toHaveLength(1)
  })

  it.each(['already_answered', 'expired'])('답할 때 409 %s 면 그 질문 칩을 모두 비활성으로 두고 한 줄 안내', async (code) => {
    const fetchFn = install(
      routerWith({
        '/api/questions/pending': () => json([pq(3, ['가', '나']), pq(4, ['다', '라'])]),
        '/api/answers/3': () => json({ detail: { code } }, 409),
      }),
    )
    render(<ChatScreen />)
    await userEvent.setup().click(await screen.findByRole('button', { name: '가' }))
    expect(await screen.findByText(NOTICE.questionClosed)).toBeInTheDocument()

    const g3 = screen.getByTestId('chips-3')
    for (const b of within(g3).getAllByRole('button')) {
      expect(b).toBeDisabled()
      expect(b).toHaveAttribute('aria-pressed', 'false')
    }
    // 다른 질문의 칩은 영향이 없다. 재시도도 없다.
    for (const b of within(screen.getByTestId('chips-4')).getAllByRole('button')) expect(b).toBeEnabled()
    expect(callsTo(fetchFn, '/api/answers/3')).toHaveLength(1)
  })

  it('답 전송이 5xx 로 실패하면 안내 한 줄을 띄우고 칩은 다시 누를 수 있다', async () => {
    install(
      routerWith({
        '/api/questions/pending': () => json([pq(3, ['가', '나'])]),
        '/api/answers/3': () => json({ detail: { code: 'internal_error' } }, 500),
      }),
    )
    render(<ChatScreen />)
    await userEvent.setup().click(await screen.findByRole('button', { name: '가' }))
    expect(await screen.findByText(NOTICE.failed)).toBeInTheDocument()
    for (const b of within(screen.getByTestId('chips-3')).getAllByRole('button')) expect(b).toBeEnabled()
  })
})

describe('오류 안내', () => {
  it('POST /api/chat 이 5xx 면 안내 한 줄', async () => {
    install(routerWith({ '/api/chat': () => json({ detail: { code: 'internal_error' } }, 500) }))
    render(<ChatScreen />)
    await sendText('안녕')
    expect(await screen.findByText(NOTICE.failed)).toBeInTheDocument()
    expect(screen.getByText('안녕')).toBeInTheDocument()
  })

  it('네트워크 실패(fetch 거부)면 안내 한 줄', async () => {
    install(
      routerWith({
        '/api/chat': () => {
          throw new TypeError('Failed to fetch')
        },
      }),
    )
    render(<ChatScreen />)
    await sendText('안녕')
    expect(await screen.findByText(NOTICE.failed)).toBeInTheDocument()
  })

  it('진입 시 복원 요청이 실패해도 화면은 빈 상태 안내로 남는다', async () => {
    install(() => {
      throw new TypeError('Failed to fetch')
    })
    render(<ChatScreen />)
    expect(await screen.findByText(NOTICE.empty)).toBeInTheDocument()
    expect(screen.queryByRole('alert')).toBeNull()
  })
})

describe('인물 카드 링크', () => {
  it('stored.persons > 0 이면 #/persons 링크가 붙는다', async () => {
    install(routerWith({ '/api/chat': () => json(chatOut({ stored: { persons: 1, events: 0, schedules: 0 } })) }))
    render(<ChatScreen />)
    await sendText('x')
    expect(await screen.findByRole('link', { name: NOTICE.personsLink })).toHaveAttribute('href', '#/persons')
  })

  it('stored.events > 0 이어도 링크가 붙는다', async () => {
    install(routerWith({ '/api/chat': () => json(chatOut({ stored: { persons: 0, events: 2, schedules: 0 } })) }))
    render(<ChatScreen />)
    await sendText('x')
    expect(await screen.findByRole('link', { name: NOTICE.personsLink })).toBeInTheDocument()
  })

  it('저장된 인물·사건이 없으면(일정만 있어도) 링크가 없다', async () => {
    install(routerWith({ '/api/chat': () => json(chatOut({ stored: { persons: 0, events: 0, schedules: 3 } })) }))
    render(<ChatScreen />)
    await sendText('x')
    await screen.findByText('응답입니다')
    expect(screen.queryByRole('link')).toBeNull()
  })
})
