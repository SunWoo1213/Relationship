// U7 브리핑 화면 + 수동 브리핑 버튼. 실제 네트워크 없음 — fetch 는 테스트마다 vi.stubGlobal 로 가짜를 건다 (결정 J).
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import BriefingScreen, { BRIEFING_NOTICE } from '@/screens/BriefingScreen'
import { parseScheduleId } from '@/routes'
import { formatDateTime } from '@/lib/format'
import type { BriefingRecordOut, BriefingRunOut } from '@/api/types'

type Handler = (url: string, init: RequestInit) => Response | Promise<Response>

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

function install(handler: Handler) {
  const fn = vi.fn((input: RequestInfo | URL, init?: RequestInit) => Promise.resolve(handler(String(input), init ?? {})))
  vi.stubGlobal('fetch', fn)
  return fn
}

function router(table: Record<string, Handler>): Handler {
  return (url, init) => {
    const key = `${(init.method ?? 'GET')} ${url}`
    if (table[key]) return table[key](url, init)
    throw new Error(`예상하지 못한 요청: ${key}`)
  }
}

function callsOf(fn: ReturnType<typeof install>, method: string, url: string) {
  return fn.mock.calls.filter(([u, init]) => String(u) === url && ((init as RequestInit)?.method ?? 'GET') === method)
}

const BASIS = { fact_keys: ['basis_fact_key_zz'], event_ids: [987654] }

function record(
  scheduleId: number,
  name: string,
  title: string,
  scheduledAt: string,
  extra: Partial<BriefingRecordOut> = {},
): BriefingRecordOut {
  return {
    schedule: { id: scheduleId, title, scheduled_at: scheduledAt },
    person: { id: scheduleId + 100, display_name: name },
    generated_at: '2026-10-13T00:00:00Z',
    composer: 'template',
    pattern_sentences: [],
    lines: [],
    suggestion: null,
    push: `${name} 브리핑`,
    trace_id: scheduleId * 10,
    ...extra,
  }
}

// 특수문자·꼬리 공백·따옴표·꺾쇠가 든 서버 문장 — 가공(trim·이스케이프·말줄임)이 있으면 달라진다.
const PATTERN = '  최근 3회 모두 <b>공개</b> 석상 지적 & "반복" '
const LINE_1 = '지난 만남(8/21)은 분위기 좋았음, 딸 입시 얘기  '
const LINE_2 = '3월 승진 누락 이후 예민한 시기일 수 있음'
const SUGGESTION = '  지적이 반복되니 회의 전 1:1을 요청해 <사전 공유> & "제안" '

// 서버 순서(일정 시각 내림차순). id 오름차순·이름순·시각 오름차순 어느 쪽으로 다시 줄 세워도 이 순서와 달라진다.
const R5 = record(5, '김팀장', '분기 회의', '2026-10-14T06:00:00Z', {
  pattern_sentences: [{ key: 'pattern:conflict', sentence: PATTERN }],
  lines: [
    { text: LINE_1, basis: BASIS },
    { text: LINE_2, basis: BASIS },
  ],
  suggestion: { text: SUGGESTION, basis: BASIS },
})
const R2 = record(2, '철수', '저녁 약속', '2026-10-13T06:00:00Z', { lines: [{ text: '철수 요약 줄', basis: BASIS }] })
const R9 = record(9, '박대리', '1:1 면담', '2026-10-12T06:00:00Z')
const LIST = [R5, R2, R9]

function ids(): string[] {
  const list = screen.getByTestId('briefing-list')
  return Array.from(list.querySelectorAll(':scope > li')).map((li) => li.getAttribute('data-testid') ?? '')
}

function emptyRun(): BriefingRunOut {
  return { run_id: 'r1', generated_at: '2026-10-13T01:00:00Z', briefings: [], skipped: [] }
}

beforeEach(() => {
  window.history.replaceState(null, '', '#/briefings')
})

afterEach(() => {
  vi.unstubAllGlobals()
  window.history.replaceState(null, '', '#/chat')
})

describe('브리핑 목록', () => {
  it('서버 순서 그대로(재정렬 없음), 머리줄은 일정 시각 · 이름 · 일정 제목', async () => {
    install(router({ 'GET /api/briefings': () => json(LIST) }))
    render(<BriefingScreen />)
    await screen.findByTestId('briefing-list')
    expect(ids()).toEqual(['briefing-5', 'briefing-2', 'briefing-9'])
    const heads = screen.getAllByRole('heading', { level: 2 }).map((h) => h.textContent)
    expect(heads).toEqual([
      `📌 ${formatDateTime(R5.schedule.scheduled_at)} · 김팀장 · 분기 회의`,
      `📌 ${formatDateTime(R2.schedule.scheduled_at)} · 철수 · 저녁 약속`,
      `📌 ${formatDateTime(R9.schedule.scheduled_at)} · 박대리 · 1:1 면담`,
    ])
  })

  it('패턴 문장·요약 줄·제안이 서버 문자열 그대로이고 순서(패턴 → 줄 → 제안)를 지킨다', async () => {
    install(router({ 'GET /api/briefings': () => json(LIST) }))
    render(<BriefingScreen />)
    const first = await screen.findByTestId('briefing-5')
    const texts = Array.from(first.querySelectorAll('[data-field="pattern"], [data-field="line"]')).map((n) => n.textContent)
    expect(texts).toEqual([PATTERN, LINE_1, LINE_2])
    expect(first.querySelector('[data-field="suggestion"]')?.textContent).toBe(SUGGESTION)
    expect(within(first).getByRole('heading', { level: 3 })).toHaveTextContent(BRIEFING_NOTICE.suggestionTitle)
  })

  it('basis 는 화면에 나오지 않는다', async () => {
    install(router({ 'GET /api/briefings': () => json(LIST) }))
    render(<BriefingScreen />)
    await screen.findByTestId('briefing-list')
    expect(document.body.textContent).not.toContain('basis_fact_key_zz')
    expect(document.body.textContent).not.toContain('987654')
  })

  it('제안이 없으면 제안 구획이 없다', async () => {
    install(router({ 'GET /api/briefings': () => json(LIST) }))
    render(<BriefingScreen />)
    const third = await screen.findByTestId('briefing-9')
    expect(third.querySelector('[data-field="suggestion-block"]')).toBeNull()
    expect(within(third).queryByRole('heading', { level: 3 })).toBeNull()
  })

  it('빈 목록이면 빈 상태 문구 하나', async () => {
    install(router({ 'GET /api/briefings': () => json([]) }))
    render(<BriefingScreen />)
    expect(await screen.findByText(BRIEFING_NOTICE.empty)).toBeInTheDocument()
    expect(screen.queryByTestId('briefing-list')).toBeNull()
  })

  it('목록 조회가 실패하면 한 줄 안내(빈 상태 문구는 아님)', async () => {
    install(router({ 'GET /api/briefings': () => json({ detail: { code: 'x' } }, 500) }))
    render(<BriefingScreen />)
    expect(await screen.findByText(BRIEFING_NOTICE.listFailed)).toBeInTheDocument()
    expect(screen.queryByText(BRIEFING_NOTICE.empty)).toBeNull()
  })

  it('항목마다 "지금 브리핑" 버튼이 있고, 알림 받기는 자리만(비활성)이며 /push-dev/ 링크가 없다', async () => {
    install(router({ 'GET /api/briefings': () => json(LIST) }))
    render(<BriefingScreen />)
    await screen.findByTestId('briefing-list')
    expect(screen.getAllByRole('button', { name: BRIEFING_NOTICE.runNow })).toHaveLength(3)
    expect(screen.getByRole('button', { name: BRIEFING_NOTICE.subscribe })).toBeDisabled()
    expect(document.querySelector('a[href*="push-dev"]')).toBeNull()
  })
})

describe('?schedule_id= 강조 (사용자 결정 (가))', () => {
  it('쿼리가 없으면 서버 순서 그대로이고 단건 요청은 0', async () => {
    const fn = install(router({ 'GET /api/briefings': () => json(LIST) }))
    render(<BriefingScreen />)
    await screen.findByTestId('briefing-list')
    expect(fn.mock.calls.map(([u]) => String(u))).toEqual(['/api/briefings'])
    expect(document.querySelector('[data-highlight]')).toBeNull()
  })

  it('목록 안에 있으면 맨 위로 올리고 강조하며(나머지는 서버 순서) 단건 요청은 0', async () => {
    window.history.replaceState(null, '', '#/briefings?schedule_id=9')
    const fn = install(router({ 'GET /api/briefings': () => json(LIST) }))
    render(<BriefingScreen />)
    await screen.findByTestId('briefing-list')
    expect(ids()).toEqual(['briefing-9', 'briefing-5', 'briefing-2'])
    expect(screen.getByTestId('briefing-9')).toHaveAttribute('data-highlight', 'true')
    expect(document.querySelectorAll('[data-highlight]')).toHaveLength(1)
    expect(fn.mock.calls.map(([u]) => String(u))).toEqual(['/api/briefings'])
  })

  it('목록에 없으면 GET /briefings?schedule_id=N 을 1회 더 불러 맨 위에 붙이고 강조한다', async () => {
    window.history.replaceState(null, '', '#/briefings?schedule_id=77')
    const old = record(77, '엄마', '생신 식사', '2026-09-01T06:00:00Z', { lines: [{ text: '창 밖 일정 줄', basis: BASIS }] })
    const fn = install(
      router({
        'GET /api/briefings': () => json(LIST),
        'GET /api/briefings?schedule_id=77': () => json([old]),
      }),
    )
    render(<BriefingScreen />)
    await screen.findByTestId('briefing-77')
    expect(ids()).toEqual(['briefing-77', 'briefing-5', 'briefing-2', 'briefing-9'])
    expect(screen.getByTestId('briefing-77')).toHaveAttribute('data-highlight', 'true')
    expect(document.querySelectorAll('[data-highlight]')).toHaveLength(1)
    expect(fn.mock.calls.map(([u]) => String(u))).toEqual(['/api/briefings', '/api/briefings?schedule_id=77'])
  })

  it('단건이 404 이거나 [] 이면 안내 한 줄 + 나머지 목록 그대로', async () => {
    for (const reply of [() => json({ detail: { code: 'not_found' } }, 404), () => json([])]) {
      window.history.replaceState(null, '', '#/briefings?schedule_id=77')
      install(
        router({
          'GET /api/briefings': () => json(LIST),
          'GET /api/briefings?schedule_id=77': reply,
        }),
      )
      const { unmount } = render(<BriefingScreen />)
      expect(await screen.findByText(BRIEFING_NOTICE.scheduleMissing)).toBeInTheDocument()
      expect(ids()).toEqual(['briefing-5', 'briefing-2', 'briefing-9'])
      expect(document.querySelector('[data-highlight]')).toBeNull()
      unmount()
      vi.unstubAllGlobals()
    }
  })

  it('parseScheduleId: 양의 정수만 인정한다', () => {
    expect(parseScheduleId('#/briefings?schedule_id=12')).toBe(12)
    expect(parseScheduleId('#/briefings')).toBeNull()
    expect(parseScheduleId('#/briefings?schedule_id=0')).toBeNull()
    expect(parseScheduleId('#/briefings?schedule_id=abc')).toBeNull()
    expect(parseScheduleId('#/briefings?schedule_id=1.5')).toBeNull()
    expect(parseScheduleId('#/briefings?x=1&schedule_id=3')).toBe(3)
  })
})

describe('"지금 브리핑" (결정 K)', () => {
  it('POST 본문은 {schedule_id} 이고, 성공하면 응답을 끼우지 않고 GET /briefings 를 다시 읽어 갱신한다', async () => {
    let n = 0
    const fn = install(
      router({
        'GET /api/briefings': () => json(n++ === 0 ? LIST : [record(2, '철수', '저녁 약속', '2026-10-13T06:00:00Z', { lines: [{ text: '새로 만든 줄', basis: BASIS }] }), R9]),
        'POST /api/briefings/run': () => json(emptyRun()),
      }),
    )
    render(<BriefingScreen />)
    const item = await screen.findByTestId('briefing-2')
    await userEvent.click(within(item).getByRole('button', { name: BRIEFING_NOTICE.runNow }))

    await waitFor(() => expect(callsOf(fn, 'GET', '/api/briefings')).toHaveLength(2))
    const posts = callsOf(fn, 'POST', '/api/briefings/run')
    expect(posts).toHaveLength(1)
    expect(JSON.parse(String((posts[0][1] as RequestInit).body))).toEqual({ schedule_id: 2 })
    expect(await screen.findByText('새로 만든 줄')).toBeInTheDocument()
    expect(ids()).toEqual(['briefing-2', 'briefing-9'])
  })

  it('진행 중에는 그 버튼이 비활성(진행 표시)이고, 끝나면 다시 활성', async () => {
    let finish: () => void = () => {}
    install(
      router({
        'GET /api/briefings': () => json(LIST),
        'POST /api/briefings/run': () =>
          new Promise<Response>((resolve) => {
            finish = () => resolve(json(emptyRun()))
          }),
      }),
    )
    render(<BriefingScreen />)
    const item = await screen.findByTestId('briefing-2')
    await userEvent.click(within(item).getByRole('button', { name: BRIEFING_NOTICE.runNow }))
    const busy = await within(item).findByRole('button', { name: BRIEFING_NOTICE.running })
    expect(busy).toBeDisabled()
    // 다른 항목 버튼은 그대로 활성
    expect(within(screen.getByTestId('briefing-9')).getByRole('button', { name: BRIEFING_NOTICE.runNow })).toBeEnabled()
    finish()
    expect(await within(item).findByRole('button', { name: BRIEFING_NOTICE.runNow })).toBeEnabled()
  })

  it('404(잠금 중)이면 "잠시 뒤 다시 시도" 안내만 — 자동 재시도 없음(POST 1회), 목록 재요청도 없고 버튼은 다시 활성', async () => {
    const fn = install(
      router({
        'GET /api/briefings': () => json(LIST),
        'POST /api/briefings/run': () => json({ detail: { code: 'not_found' } }, 404),
      }),
    )
    render(<BriefingScreen />)
    const item = await screen.findByTestId('briefing-2')
    await userEvent.click(within(item).getByRole('button', { name: BRIEFING_NOTICE.runNow }))
    expect(await within(item).findByText(BRIEFING_NOTICE.runLocked)).toBeInTheDocument()
    expect(within(item).getByRole('button', { name: BRIEFING_NOTICE.runNow })).toBeEnabled()
    await new Promise((r) => setTimeout(r, 50))
    expect(callsOf(fn, 'POST', '/api/briefings/run')).toHaveLength(1)
    expect(callsOf(fn, 'GET', '/api/briefings')).toHaveLength(1)
    // 다른 항목에는 안내가 없다
    expect(within(screen.getByTestId('briefing-9')).queryByText(BRIEFING_NOTICE.runLocked)).toBeNull()
  })

  it('5xx 이면 한 줄 실패 안내(잠금 문구가 아님), 버튼은 다시 활성이고 누르면 다시 보낸다', async () => {
    let n = 0
    const fn = install(
      router({
        'GET /api/briefings': () => json(LIST),
        'POST /api/briefings/run': () => (n++ === 0 ? json({ detail: { code: 'x' } }, 500) : json(emptyRun())),
      }),
    )
    render(<BriefingScreen />)
    const item = await screen.findByTestId('briefing-2')
    const user = userEvent.setup()
    await user.click(within(item).getByRole('button', { name: BRIEFING_NOTICE.runNow }))
    expect(await within(item).findByRole('alert')).toHaveTextContent(BRIEFING_NOTICE.runFailed)
    expect(within(item).queryByText(BRIEFING_NOTICE.runLocked)).toBeNull()
    expect(within(item).getByRole('button', { name: BRIEFING_NOTICE.runNow })).toBeEnabled()

    await user.click(within(item).getByRole('button', { name: BRIEFING_NOTICE.runNow }))
    await waitFor(() => expect(callsOf(fn, 'GET', '/api/briefings')).toHaveLength(2))
    expect(callsOf(fn, 'POST', '/api/briefings/run')).toHaveLength(2)
    await waitFor(() => expect(within(item).queryByRole('alert')).toBeNull())
  })
})
