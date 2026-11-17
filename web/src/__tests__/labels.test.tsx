// FIX-039 표시 이름 — 사실 키·사건 종류·패턴 키를 한글로 보여 준다. 실제 네트워크 없음(fetch 가짜, 결정 J).
import { render, screen, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { eventTypeLabel, factKeyLabel } from '@/lib/labels'
import BriefingScreen from '@/screens/BriefingScreen'
import PersonCardScreen from '@/screens/PersonCardScreen'
import type { BriefingRecordOut, PersonCardOut } from '@/api/types'
import { installFakeMatchMedia } from './helpers'

// app/memory/types.py::FACT_KEYS 9종(순서 그대로)과 app/db/models.py::EVENT_TYPES 7종의 정해진 한글.
const FACT_CASES: [string, string][] = [
  ['job', '직업'],
  ['workplace', '소속'],
  ['family', '가족'],
  ['hobby', '취미'],
  ['likes', '좋아하는 것'],
  ['dislikes', '싫어하는 것'],
  ['health', '건강'],
  ['life_event', '근황'],
  ['contact_note', '연락·만남 메모'],
]
const EVENT_CASES: [string, string][] = [
  ['conflict', '갈등'],
  ['praise', '칭찬'],
  ['meal', '식사'],
  ['meeting', '만남'],
  ['personal_share', '개인 이야기'],
  ['favor', '도움'],
  ['other', '기타'],
]

function installFetch(body: unknown) {
  vi.stubGlobal(
    'fetch',
    vi.fn(() =>
      Promise.resolve(new Response(JSON.stringify(body), { status: 200, headers: { 'Content-Type': 'application/json' } })),
    ),
  )
}

function card(over: Partial<PersonCardOut>): PersonCardOut {
  return {
    person: { id: 3, display_name: '김팀장', relation_tag: '직장', hierarchy: '상' },
    aliases: [],
    last_contact_at: null,
    facts: [],
    patterns: [],
    timeline: [],
    upcoming_schedules: [],
    ...over,
  }
}

function section(container: HTMLElement, name: string) {
  return container.querySelector(`[data-section="${name}"]`) as HTMLElement
}

beforeEach(() => installFakeMatchMedia(1280))
afterEach(() => vi.unstubAllGlobals())

describe('FIX-039 표시 이름 함수', () => {
  it.each(FACT_CASES)('사실 키 %s → %s', (key, label) => {
    expect(factKeyLabel(key)).toBe(label)
  })
  it.each(EVENT_CASES)('사건 종류 %s → %s', (type, label) => {
    expect(eventTypeLabel(type)).toBe(label)
    expect(factKeyLabel(`pattern:${type}`)).toBe(label)
  })
  it('표에 없는 키·종류·패턴은 받은 문자열 그대로(상속 키 포함)', () => {
    expect(factKeyLabel('child')).toBe('child')
    expect(factKeyLabel('pattern:zzz')).toBe('pattern:zzz')
    expect(factKeyLabel('toString')).toBe('toString')
    expect(eventTypeLabel('zzz')).toBe('zzz')
    expect(eventTypeLabel('constructor')).toBe('constructor')
    expect(factKeyLabel('')).toBe('')
  })
})

describe('FIX-039 인물 카드 화면', () => {
  it('사실 키 9종이 각각 정해진 한글로 보이고 영문 키는 보이지 않는다', async () => {
    installFetch(
      card({
        facts: FACT_CASES.map(([key], i) => ({
          id: 100 + i,
          key,
          value: `값-${key}`,
          updated_at: '2026-09-03T12:00:00Z',
          source_count: 0,
        })),
      }),
    )
    const { container } = render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    FACT_CASES.forEach(([key, label], i) => {
      const row = screen.getByTestId(`fact-${100 + i}`)
      expect(row.textContent).toBe(`${label} 값-${key}`)
    })
    // 영문 키가 단독 글자로 나오지 않는다(값 `값-job` 의 일부는 제외하고 키 칸만 본다).
    const keySpans = Array.from(section(container, 'facts').querySelectorAll('li > span:first-child')).map((n) => n.textContent)
    expect(keySpans).toEqual(FACT_CASES.map(([, label]) => label))
  })

  it('타임라인 사건 종류 7종이 각각 정해진 한글 배지로 보이고 content 는 그대로다', async () => {
    installFetch(
      card({
        timeline: EVENT_CASES.map(([type], i) => ({
          id: 200 + i,
          type,
          content: ` 내용 <${type}> & "그대로" `,
          occurred_at: '2026-09-03T12:00:00Z',
        })),
      }),
    )
    render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    EVENT_CASES.forEach(([type, label], i) => {
      const item = screen.getByTestId(`timeline-${200 + i}`)
      expect(within(item).getByText(label)).toBeInTheDocument()
      expect(item.textContent).toContain(` 내용 <${type}> & "그대로" `)
      expect(within(item).queryByText(type)).toBeNull() // 영문 종류 배지는 없다
    })
  })

  it('패턴 줄에 pattern: 글자가 없고 한글 이름 + 서버 value 그대로다', async () => {
    installFetch(
      card({
        patterns: [
          { id: 301, key: 'pattern:meeting', value: ' 5회 (2026-11-09) ', source_count: 0 },
          { id: 302, key: 'pattern:conflict', value: '6회', source_count: 0 },
        ],
      }),
    )
    const { container } = render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    expect(section(container, 'patterns').textContent).not.toContain('pattern:')
    expect(screen.getByTestId('fact-301').textContent).toBe('만남  5회 (2026-11-09) ')
    expect(screen.getByTestId('fact-302').textContent).toBe('갈등 6회')
  })

  it('표에 없는 키·종류·패턴은 받은 문자열 그대로 보인다', async () => {
    installFetch(
      card({
        facts: [{ id: 401, key: 'child', value: '딸', updated_at: '2026-09-03T12:00:00Z', source_count: 0 }],
        patterns: [{ id: 402, key: 'pattern:zzz', value: '2회', source_count: 0 }],
        timeline: [{ id: 403, type: 'zzz', content: '내용', occurred_at: '2026-09-03T12:00:00Z' }],
      }),
    )
    render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    expect(screen.getByTestId('fact-401').textContent).toBe('child 딸')
    expect(screen.getByTestId('fact-402').textContent).toBe('pattern:zzz 2회')
    expect(within(screen.getByTestId('timeline-403')).getByText('zzz')).toBeInTheDocument()
  })
})

describe('FIX-039 브리핑 화면', () => {
  it('패턴 줄이 `<한글 이름> <sentence>` 이고 sentence 는 그대로, lines 는 건드리지 않는다', async () => {
    const rec: BriefingRecordOut = {
      schedule: { id: 7, title: '분기 회의', scheduled_at: '2026-10-14T06:00:00Z' },
      person: { id: 107, display_name: '김팀장' },
      generated_at: '2026-10-13T00:00:00Z',
      composer: 'template',
      pattern_sentences: [
        { key: 'pattern:meeting', sentence: '3회 (2026-11-09, 2026-11-16, 2026-11-16)' },
        { key: 'pattern:zzz', sentence: '2회' },
      ],
      lines: [{ text: 'pattern:conflict 줄은 그대로', basis: { fact_keys: [], event_ids: [] } }],
      suggestion: null,
      push: 'x',
      trace_id: 70,
    }
    installFetch([rec])
    render(<BriefingScreen />)
    const item = await screen.findByTestId('briefing-7')
    const patterns = Array.from(item.querySelectorAll('[data-field="pattern"]')).map((n) => n.textContent)
    expect(patterns).toEqual(['만남 3회 (2026-11-09, 2026-11-16, 2026-11-16)', 'pattern:zzz 2회'])
    expect(Array.from(item.querySelectorAll('[data-field="line"]')).map((n) => n.textContent)).toEqual([
      'pattern:conflict 줄은 그대로',
    ])
  })
})
