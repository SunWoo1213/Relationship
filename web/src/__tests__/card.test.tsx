// U6 인물 목록·인물 카드·원문 펼치기. 실제 네트워크 없음 — fetch 는 테스트마다 vi.stubGlobal 로 가짜를 건다 (결정 J).
// 날짜는 한낮(UTC 12:00)으로 골라 어느 시간대에서 돌아도 같은 날로 읽히게 한다.
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from '@/App'
import PersonCardScreen, { CARD_NOTICE } from '@/screens/PersonCardScreen'
import { PERSON_LIST_NOTICE } from '@/components/PersonList'
import { notifyPersonsChanged, PersonsProvider } from '@/components/PersonsProvider'
import { SIDEBAR_RECENT_LIMIT } from '@/components/AppShell'
import appShellSource from '@/components/AppShell.tsx?raw'
import cardScreenSource from '@/screens/PersonCardScreen.tsx?raw'
import personGridSource from '@/components/PersonGrid.tsx?raw'
import type {
  EventRawOut,
  FactSourcesOut,
  PersonCardOut,
  PersonListItemOut,
} from '@/api/types'
import { installFakeMatchMedia } from './helpers'

type Handler = (url: string, init: RequestInit) => Response | Promise<Response>

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

function install(handler: Handler) {
  const fn = vi.fn((input: RequestInfo | URL, init?: RequestInit) => Promise.resolve(handler(String(input), init ?? {})))
  vi.stubGlobal('fetch', fn)
  return fn
}

function callsTo(fn: ReturnType<typeof install>, path: string) {
  return fn.mock.calls.filter(([url]) => String(url) === path)
}

function router(table: Record<string, Handler>): Handler {
  return (url, init) => {
    if (table[url]) return table[url](url, init)
    throw new Error(`예상하지 못한 요청: ${url}`)
  }
}

// 서버 순서가 날짜 순이 아니고 null 이 가운데 있다 — 프론트가 재정렬하면 순서가 바뀌어 잡힌다.
const PERSONS: PersonListItemOut[] = [
// 이름순·날짜순·id순 어느 쪽으로 다시 줄 세워도 이 순서와 달라지도록 골랐다.
  // 별칭: 박대리 = display_name 과 같은 것 1개 + 다른 것 3개(상한 2 → "+1"), 철수 = 같은 것뿐, 엄마 = 없음 (결정 B)
  {
    id: 7, display_name: '박대리', relation_tag: '직장', hierarchy: '하', last_contact_at: '2026-09-01T12:00:00Z',
    aliases: ['대리님', '박대리', '박 대리', 'Park'],
  },
  {
    id: 4, display_name: '철수', relation_tag: '친구', hierarchy: '동', last_contact_at: '2026-10-05T12:00:00Z',
    aliases: ['철수'],
  },
  { id: 9, display_name: '엄마', relation_tag: '가족', hierarchy: '상', last_contact_at: null, aliases: [] },
]

// 검색 시험용 — 서버 순서가 이름순이 아니다('선영 과장님' < '최선영' 이므로 이름순으로 줄 세우면 뒤바뀐다).
const SEARCH_PERSONS: PersonListItemOut[] = [
  { id: 30, display_name: '최선영', relation_tag: '친구', hierarchy: '동', last_contact_at: null, aliases: [] },
  {
    id: 21, display_name: '박팀장', relation_tag: '직장', hierarchy: '상', last_contact_at: '2026-10-01T12:00:00Z',
    aliases: ['Boss Kim', '팀장님'],
  },
  {
    id: 25, display_name: '선영 과장님', relation_tag: '직장', hierarchy: '상', last_contact_at: '2026-09-20T12:00:00Z',
    aliases: ['KIM'],
  },
  {
    id: 12, display_name: '가나', relation_tag: '가족', hierarchy: '하', last_contact_at: null,
    aliases: ['엄마친구'],
  },
]

// 사이드바 5명 자르기 시험용 7명 — 서버 순서가 이름순·id순·날짜순 어느 쪽과도 다르다.
// 뒤 두 명(가을·가람)은 이름순으로도 날짜 최신순으로도 앞 5명에 들어가므로, 재정렬 후 자르면 잡힌다.
const SEVEN: PersonListItemOut[] = [
  { id: 51, display_name: '아린', relation_tag: '친구', hierarchy: '동', last_contact_at: '2026-09-10T12:00:00Z', aliases: [] },
  { id: 48, display_name: '다온', relation_tag: '직장', hierarchy: '상', last_contact_at: '2026-10-01T12:00:00Z', aliases: [] },
  { id: 55, display_name: '하준', relation_tag: '지인', hierarchy: '하', last_contact_at: null, aliases: [] },
  { id: 50, display_name: '나래', relation_tag: '가족', hierarchy: '상', last_contact_at: '2026-08-01T12:00:00Z', aliases: [] },
  { id: 53, display_name: '마루', relation_tag: '친구', hierarchy: '동', last_contact_at: '2026-09-30T12:00:00Z', aliases: [] },
  { id: 49, display_name: '가을', relation_tag: '연인', hierarchy: '동', last_contact_at: '2026-10-20T12:00:00Z', aliases: [] },
  { id: 52, display_name: '가람', relation_tag: '직장', hierarchy: '동', last_contact_at: '2026-10-25T12:00:00Z', aliases: [] },
]

// 특수문자·앞뒤 공백·대소문자가 섞인 값 — 화면이 가공하면 textContent 가 달라진다 (원칙7).
const ODD_NAME = ' <b>Ab&C</b> "q" '
const ODD_ALIAS = ' ΩX  yZ '
const ODD_PERSONS: PersonListItemOut[] = [
  { id: 40, display_name: ODD_NAME, relation_tag: '지인', hierarchy: '동', last_contact_at: null, aliases: [ODD_ALIAS] },
  { id: 41, display_name: '다른이', relation_tag: '지인', hierarchy: '동', last_contact_at: null, aliases: [] },
]

function tileIds(): string[] {
  return screen.queryAllByTestId('person-tile').map((t) => t.getAttribute('data-person-id') ?? '')
}

// 특수문자·꼬리 공백·연속 개행이 든 원문 — 가공(trim·개행 접기·이스케이프)이 있으면 달라진다.
const RAW_A = '  팀장님이\n"전체회의"에서 <b>지적</b> & 했다 \t끝  \n\n'
const RAW_B = '두번째\n\n\n  줄바꿈 셋 &amp; 그대로'
const RAW_C = '점심 같이 함, 딸 얘기'

const CARD: PersonCardOut = {
  person: { id: 3, display_name: '김팀장', relation_tag: '직장', hierarchy: '상' },
  aliases: ['팀장', '우리 팀장님', '부장님'],
  last_contact_at: '2026-09-03T12:00:00Z',
  facts: [
    { id: 11, key: 'child', value: '딸 대학 입시 중', updated_at: '2026-09-03T12:00:00Z', source_count: 2 },
    { id: 12, key: 'hobby', value: '골프 안 침', updated_at: '2026-08-01T12:00:00Z', source_count: 0 },
  ],
  patterns: [{ id: 21, key: 'pattern:conflict', value: '공개 석상에서 지적 — 3회', source_count: 3 }],
  // 서버가 준 순서(날짜 순이 아님)를 그대로 보여야 한다.
  timeline: [
    { id: 5, type: 'meal', content: '점심 같이 함', occurred_at: '2026-08-21T12:00:00Z' },
    { id: 9, type: 'conflict', content: '회의에서 보고서 공개 지적', occurred_at: '2026-09-03T12:00:00Z' },
    { id: 2, type: 'conflict', content: '전체회의에서 지적당함', occurred_at: '2026-07-28T12:00:00Z' },
  ],
  upcoming_schedules: [{ id: 1, title: '분기 회의', scheduled_at: '2026-09-10T12:00:00Z', briefed_at: null }],
}

function rawOut(id: number, raw: string): EventRawOut {
  return { event_id: id, person_id: 3, type: 'conflict', content: 'x', occurred_at: '2026-09-03T12:00:00Z', raw_utterance: raw }
}

const SOURCES_11: FactSourcesOut = {
  fact: { id: 11, key: 'child', value: '딸 대학 입시 중' },
  sources: [
    { event_id: 5, type: 'meal', content: '점심 같이 함', occurred_at: '2026-08-21T12:00:00Z', raw_utterance: RAW_C },
    { event_id: 9, type: 'conflict', content: '보고서 지적', occurred_at: '2026-09-03T12:00:00Z', raw_utterance: RAW_B },
  ],
}

function cardRouter(extra: Record<string, Handler> = {}) {
  return router({ '/api/persons/3': () => json(CARD), ...extra })
}

beforeEach(() => {
  window.localStorage.clear()
  installFakeMatchMedia(1280)
})

afterEach(() => {
  vi.unstubAllGlobals()
  window.history.replaceState(null, '', '#/chat')
})

function renderGrid(list: PersonListItemOut[] = PERSONS) {
  const fetchFn = install(router({ '/api/persons': () => json(list) }))
  const view = render(<PersonCardScreen personId={null} />, { wrapper: PersonsProvider })
  return { fetchFn, ...view }
}

function hasWidthClass(el: Element): boolean {
  return Array.from(el.classList).some((c) => c === 'mx-auto' || c.startsWith('max-w-') || c.startsWith('md:w-'))
}

describe('인물 목록 — 카드 그리드 (D15, P8b U1)', () => {
  it('#/persons 진입 시 GET /api/persons 1회, 타일 필드(이름·태그·위계·마지막 접촉)가 서버 값·서버 순서 그대로', async () => {
    window.history.replaceState(null, '', '#/persons')
    const fetchFn = install(router({ '/api/persons': () => json(PERSONS) }))
    render(<App />)
    await screen.findByTestId('person-grid')
    expect(callsTo(fetchFn, '/api/persons')).toHaveLength(1)
    expect(fetchFn.mock.calls.map(([u]) => String(u))).toEqual(['/api/persons'])
    const tiles = screen.getAllByTestId('person-tile')
    const f = (name: string) => tiles.map((t) => t.querySelector(`[data-field="${name}"]`)?.textContent)
    expect(f('name')).toEqual(['박대리', '철수', '엄마'])
    expect(f('tag')).toEqual(['직장', '친구', '가족'])
    expect(f('hierarchy')).toEqual(['하', '동', '상'])
    expect(f('last-contact')).toEqual(['2026. 9. 1.', '2026. 10. 5.', PERSON_LIST_NOTICE.noContact])
    expect(tileIds()).toEqual(['7', '4', '9'])
  })

  it('데스크톱 열·간격 클래스(결정 A)이고 사이드바 5명 자르기와 무관하게 7명 전원이 그려진다', async () => {
    const seven = Array.from({ length: 7 }, (_, i) => ({
      id: 100 + i, display_name: `사람${i}`, relation_tag: '지인', hierarchy: '동', last_contact_at: null, aliases: [],
    }))
    renderGrid(seven)
    const grid = await screen.findByTestId('person-grid')
    for (const c of ['grid', 'grid-cols-1', 'md:grid-cols-2', 'xl:grid-cols-3', 'gap-4']) {
      expect(grid.classList.contains(c)).toBe(true)
    }
    expect(tileIds()).toEqual(seven.map((p) => String(p.id)))
  })

  it('타일 별칭(결정 B): display_name 과 같은 별칭 제외 · 서버 순서 · 최대 2개 · 넘치면 "+n" · 없으면 칸 없음', async () => {
    const two = { id: 50, display_name: '둘', relation_tag: '지인', hierarchy: '동', last_contact_at: null, aliases: ['가', '나'] }
    renderGrid([...PERSONS, two])
    await screen.findByTestId('person-grid')
    const alias = (id: string) =>
      document.querySelector(`[data-testid="person-tile"][data-person-id="${id}"] [data-field="aliases"]`)
    // 박대리: ['대리님','박대리'(제외),'박 대리','Park'] → 앞 2개 + 남은 1개
    expect(alias('7')?.textContent).toBe('대리님 · 박 대리 +1')
    expect(alias('4')).toBeNull() // 같은 별칭뿐 → 칸 없음
    expect(alias('9')).toBeNull()
    expect(alias('50')?.textContent).toBe('가 · 나') // 정확히 2개면 "+n" 없음
  })

  it('목록 상태는 본문 폭 전체를 쓴다 — 그리드부터 main 까지 모든 조상과 그리드 자신, section 안 그리드를 감싼 요소에 mx-auto·max-w-*·md:w-* 가 없다 (R-U10C-3)', async () => {
    window.history.replaceState(null, '', '#/persons')
    install(router({ '/api/persons': () => json(PERSONS) }))
    render(<App />)
    const grid = await screen.findByTestId('person-grid')
    const main = document.querySelector('main')!
    const section = document.querySelector('[data-screen="persons"]')!
    expect(main.contains(grid)).toBe(true)
    const chain: Element[] = [grid]
    for (let el: Element | null = grid.parentElement; el; el = el.parentElement) {
      chain.push(el)
      if (el === main) break
    }
    expect(chain[chain.length - 1]).toBe(main)
    const wrappers = Array.from(section.querySelectorAll('*')).filter((el) => el.contains(grid))
    expect(wrappers.length).toBeGreaterThanOrEqual(2) // 바깥 div.mt-4 + PersonGrid 안쪽 래퍼
    for (const el of new Set([...chain, ...wrappers, section])) {
      expect(hasWidthClass(el)).toBe(false)
    }
    expect(screen.queryByTestId('card-wrap')).toBeNull()
  })

  it('상세 상태는 가운데 정렬이고 폭이 본문의 75%(md 이상), 모바일은 100% 이다 (U10 화면 점검)', async () => {
    install(cardRouter())
    const { container } = render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    const section = container.querySelector('[data-screen="persons"]')!
    expect(Array.from(section.classList).includes('mx-auto')).toBe(false)
    const wrap = screen.getByTestId('card-wrap')
    expect(wrap.contains(screen.getByTestId('person-card'))).toBe(true)
    for (const c of ['mx-auto', 'w-full', 'md:w-3/4']) expect(wrap.classList.contains(c)).toBe(true)
  })

  it('컨트롤은 검색창 1개뿐이다(태그·위계 필터 없음) — 문구·aria-label 은 결정 D', async () => {
    renderGrid()
    await screen.findByTestId('person-grid')
    expect(screen.getAllByRole('searchbox')).toHaveLength(1)
    for (const role of ['combobox', 'listbox', 'radio', 'checkbox', 'switch']) {
      expect(screen.queryAllByRole(role)).toHaveLength(0)
    }
    const box = screen.getByTestId('person-search')
    expect(box).toHaveAttribute('type', 'search')
    expect(box).toHaveAttribute('aria-label', '인물 검색')
    expect(box).toHaveAttribute('placeholder', '이름이나 별칭으로 찾기')
    expect(box).toBe(screen.getByRole('searchbox'))
  })

  it('검색: 이름 일부 → 그 타일만, 서버 순서 유지(이름순 재정렬 없음)', async () => {
    renderGrid(SEARCH_PERSONS)
    await screen.findByTestId('person-grid')
    expect(tileIds()).toEqual(['30', '21', '25', '12'])
    await userEvent.type(screen.getByTestId('person-search'), '선영')
    // 최선영(30)이 선영 과장님(25)보다 서버에서 앞이다 — 이름순이면 25 가 먼저 온다.
    expect(tileIds()).toEqual(['30', '25'])
  })

  it('검색: 별칭 일부만 맞아도 그 인물이 나온다(이름에는 없는 글자)', async () => {
    renderGrid(SEARCH_PERSONS)
    await screen.findByTestId('person-grid')
    await userEvent.type(screen.getByTestId('person-search'), '엄마친')
    expect(tileIds()).toEqual(['12'])
  })

  it('검색: 태그·위계 글자로는 찾지 않는다(이름·별칭만)', async () => {
    renderGrid(SEARCH_PERSONS)
    await screen.findByTestId('person-grid')
    const box = screen.getByTestId('person-search')
    await userEvent.type(box, '직장')
    expect(tileIds()).toEqual([])
    await userEvent.clear(box)
    await userEvent.type(box, '친구') // 최선영의 태그 — 별칭 '엄마친구' 에는 '친구' 가 들어 있어 12 만 남는다
    expect(tileIds()).toEqual(['12'])
  })

  it('검색 정규화(결정 C): 앞뒤 공백·영문 대소문자·안쪽 공백을 무시하고 비교한다', async () => {
    renderGrid(SEARCH_PERSONS)
    await screen.findByTestId('person-grid')
    const box = screen.getByTestId('person-search')
    const search = async (q: string) => {
      await userEvent.clear(box)
      await userEvent.type(box, q)
      return tileIds()
    }
    expect(await search('  선영 ')).toEqual(['30', '25']) // 앞뒤 공백
    expect(await search('선영과장님')).toEqual(['25']) // 이름 '선영 과장님' 의 안쪽 공백
    expect(await search('선영 과장')).toEqual(['25']) // 질의의 안쪽 공백
    expect(await search('BOSS')).toEqual(['21']) // 질의 대문자 ↔ 별칭 'Boss Kim'
    expect(await search('bosskim')).toEqual(['21']) // 별칭 안쪽 공백
    expect(await search('kim')).toEqual(['21', '25']) // 별칭 'KIM' 대문자 ↔ 질의 소문자
  })

  it('빈 검색어·공백뿐인 검색어는 전원, 지우면 원래 목록으로 돌아온다', async () => {
    renderGrid(SEARCH_PERSONS)
    await screen.findByTestId('person-grid')
    const box = screen.getByTestId('person-search')
    await userEvent.type(box, '   ')
    expect(tileIds()).toEqual(['30', '21', '25', '12'])
    await userEvent.clear(box)
    await userEvent.type(box, '선영')
    expect(tileIds()).toHaveLength(2)
    await userEvent.clear(box)
    expect(tileIds()).toEqual(['30', '21', '25', '12'])
  })

  it('0건이면 결정 D 문구 한 줄만 보이고 그리드는 사라진다', async () => {
    renderGrid(SEARCH_PERSONS)
    await screen.findByTestId('person-grid')
    expect(screen.queryByTestId('person-grid-empty')).toBeNull()
    await userEvent.type(screen.getByTestId('person-search'), '없는사람')
    expect(screen.getAllByTestId('person-grid-empty')).toHaveLength(1)
    expect(screen.getByTestId('person-grid-empty').textContent).toBe('찾는 인물이 없어요.')
    expect(screen.queryByTestId('person-grid')).toBeNull()
    expect(screen.getByTestId('person-search')).toBeInTheDocument() // 검색창은 남는다
  })

  it('검색어는 컴포넌트 상태뿐이다 — localStorage·해시에 남지 않는다 (결정 G)', async () => {
    renderGrid(SEARCH_PERSONS)
    await screen.findByTestId('person-grid')
    const before = window.location.hash
    await userEvent.type(screen.getByTestId('person-search'), '선영')
    expect(window.location.hash).toBe(before)
    expect(window.localStorage.length).toBe(0)
  })

  it('서버 문자열은 가공 없이 보인다 — 특수문자·앞뒤 공백·대소문자 textContent 일치, 검색 중에도 이름 칸 자식 요소 0 (원칙7)', async () => {
    renderGrid(ODD_PERSONS)
    await screen.findByTestId('person-grid')
    const check = () => {
      const tile = document.querySelector('[data-testid="person-tile"][data-person-id="40"]')!
      const name = tile.querySelector('[data-field="name"]')!
      expect(name.textContent).toBe(ODD_NAME)
      expect(name.children).toHaveLength(0)
      expect(tile.querySelector('[data-field="aliases"]')!.textContent).toBe(ODD_ALIAS)
    }
    check()
    await userEvent.type(screen.getByTestId('person-search'), 'ab')
    expect(tileIds()).toEqual(['40'])
    check()
    await userEvent.clear(screen.getByTestId('person-search'))
    await userEvent.type(screen.getByTestId('person-search'), 'ωx')
    expect(tileIds()).toEqual(['40'])
    check()
  })

  it('PersonGrid 소스: 대소문자·공백 가공은 비교 함수 한 곳에만 있다 (toUpperCase 0 · toLowerCase 1 · trim 1)', () => {
    expect(personGridSource.match(/toUpperCase/g)).toBeNull()
    expect(personGridSource.match(/toLowerCase/g)).toHaveLength(1)
    expect(personGridSource.match(/\.trim\(/g)).toHaveLength(1)
    expect(personGridSource.match(/replace\(/g)).toHaveLength(1)
    const fn = personGridSource.slice(
      personGridSource.indexOf('function normalizeForMatch'),
      personGridSource.indexOf('/** 결정 B'),
    )
    for (const t of ['toLowerCase', '.trim(', 'replace(']) expect(fn).toContain(t)
    expect(personGridSource).not.toMatch(/\.sort\(/)
  })

  it('빈 목록이면 빈 상태 문구 하나(검색창 없음)', async () => {
    renderGrid([])
    expect(await screen.findByText(PERSON_LIST_NOTICE.empty)).toBeInTheDocument()
    expect(screen.queryByTestId('person-grid')).toBeNull()
    expect(screen.queryByTestId('person-search')).toBeNull()
  })

  it('목록 조회가 실패하면 한 줄 안내', async () => {
    install(router({ '/api/persons': () => json({ detail: { code: 'x' } }, 500) }))
    render(<PersonCardScreen personId={null} />, { wrapper: PersonsProvider })
    expect(await screen.findByText(PERSON_LIST_NOTICE.failed)).toBeInTheDocument()
    expect(screen.queryByTestId('person-grid')).toBeNull()
    expect(screen.queryByTestId('person-search')).toBeNull()
  })

  it('타일 href 는 서버 순서의 #/persons/:id, 누르면 해시가 바뀐다', async () => {
    renderGrid()
    const tiles = await screen.findAllByTestId('person-tile')
    expect(tiles.map((t) => t.getAttribute('href'))).toEqual(['#/persons/7', '#/persons/4', '#/persons/9'])
    expect(tiles.every((t) => t.tagName === 'A')).toBe(true)
    await userEvent.click(tiles[1])
    expect(window.location.hash).toBe('#/persons/4')
  })

  it('키보드: Tab 으로 검색창 → 첫 타일 포커스, Enter 로 그 인물로 이동', async () => {
    renderGrid()
    const tiles = await screen.findAllByTestId('person-tile')
    const user = userEvent.setup()
    await user.tab()
    expect(document.activeElement).toBe(screen.getByTestId('person-search'))
    await user.tab()
    expect(document.activeElement).toBe(tiles[0])
    await user.tab()
    expect(document.activeElement).toBe(tiles[1])
    await user.keyboard('{Enter}')
    expect(window.location.hash).toBe('#/persons/4')
  })
})

describe('사이드바의 인물 목록 (결정 N)', () => {
  it('#/persons 에서 사이드바에는 목록이, 본문에는 같은 순서의 그리드가 그려진다 (P8b U1: 본문은 PersonGrid)', async () => {
    window.history.replaceState(null, '', '#/persons')
    install(router({ '/api/persons': () => json(PERSONS) }))
    render(<App />)
    await screen.findByTestId('person-grid')
    const a = screen.getByTestId('person-list')
    const inSidebar = screen.getByTestId('sidebar-persons').querySelectorAll('[data-testid="person-list"]')
    const inScreen = document.querySelectorAll('[data-screen="persons"] [data-testid="person-list"]')
    expect(inSidebar).toHaveLength(1)
    expect(inScreen).toHaveLength(0)
    expect(tileIds()).toEqual(['7', '4', '9'])
    expect(within(a).getAllByRole('link').map((l) => l.getAttribute('href'))).toEqual([
      '#/persons/7',
      '#/persons/4',
      '#/persons/9',
    ])
    expect(within(a).getAllByRole('link').map((l) => l.textContent)).toEqual([
      '박대리직장 · 하2026. 9. 1.',
      '철수친구 · 동2026. 10. 5.',
      `엄마가족 · 상${PERSON_LIST_NOTICE.noContact}`,
    ])
  })

  it('R-U6-2: 앱을 열면 GET /persons 는 1회(사이드바·본문이 한 번 받은 값을 같이 쓴다)', async () => {
    window.history.replaceState(null, '', '#/persons')
    const fetchFn = install(router({ '/api/persons': () => json(PERSONS) }))
    render(<App />)
    await screen.findByTestId('person-grid')
    await screen.findByTestId('person-list')
    expect(callsTo(fetchFn, '/api/persons')).toHaveLength(1)
  })

  it('R-U6-2: 해시 라우트가 바뀌면 다시 읽어 새 인물이 사이드바에 보인다', async () => {
    window.history.replaceState(null, '', '#/chat')
    let body: PersonListItemOut[] = [PERSONS[0]]
    const fetchFn = install(
      router({ '/api/persons': () => json(body), '/api/questions/pending': () => json([]) }),
    )
    render(<App />)
    const side = screen.getByTestId('sidebar-persons')
    await within(side).findByText('박대리')
    expect(within(side).queryByText('철수')).toBeNull()

    body = [PERSONS[1], PERSONS[0]]
    window.location.hash = '#/persons'
    expect(await within(side).findByText('철수')).toBeInTheDocument()
    expect(callsTo(fetchFn, '/api/persons')).toHaveLength(2)
  })

  it('R-U6-2: 채팅 응답 stored.persons > 0 이면 다시 읽고, 0 이면 읽지 않는다', async () => {
    window.history.replaceState(null, '', '#/chat')
    let body: PersonListItemOut[] = [PERSONS[0]]
    const fetchFn = install(
      router({
        '/api/persons': () => json(body),
        '/api/questions/pending': () => json([]),
        '/api/chat': () => {
          body = [PERSONS[1], PERSONS[0]]
          return json({
            reply: 'ok',
            session_id: 's1',
            stored: { persons: 1, events: 0, schedules: 0 },
            pending_question: null,
            stop_reason: null,
            trace_ids: [],
          })
        },
      }),
    )
    render(<App />)
    const side = screen.getByTestId('sidebar-persons')
    await within(side).findByText('박대리')
    const user = userEvent.setup()
    await user.type(screen.getByRole('textbox'), '철수 만났어')
    await user.keyboard('{Enter}')
    expect(await within(side).findByText('철수')).toBeInTheDocument()
    expect(callsTo(fetchFn, '/api/persons')).toHaveLength(2)
  })

  it('R-U6-2: 채팅 응답 stored.persons 가 0 이면(사건만 저장) 인물 목록을 다시 읽지 않는다', async () => {
    window.history.replaceState(null, '', '#/chat')
    const fetchFn = install(
      router({
        '/api/persons': () => json([PERSONS[0]]),
        '/api/questions/pending': () => json([]),
        '/api/chat': () =>
          json({
            reply: 'ok',
            session_id: 's1',
            stored: { persons: 0, events: 2, schedules: 0 },
            pending_question: null,
            stop_reason: null,
            trace_ids: [],
          }),
      }),
    )
    render(<App />)
    await within(screen.getByTestId('sidebar-persons')).findByText('박대리')
    const user = userEvent.setup()
    await user.type(screen.getByRole('textbox'), '점심 먹었어')
    await user.keyboard('{Enter}')
    await screen.findByText('ok')
    await new Promise((r) => setTimeout(r, 50))
    expect(callsTo(fetchFn, '/api/chat')).toHaveLength(1)
    expect(callsTo(fetchFn, '/api/persons')).toHaveLength(1)
  })

  it('R-U6-2: 알림 이벤트(persons-changed)만으로도 다시 읽는다', async () => {
    window.history.replaceState(null, '', '#/persons')
    const fetchFn = install(router({ '/api/persons': () => json(PERSONS) }))
    render(<App />)
    await screen.findByTestId('person-grid')
    notifyPersonsChanged()
    await waitFor(() => expect(callsTo(fetchFn, '/api/persons')).toHaveLength(2))
  })

  it('R-U7-2 (탐침 P2c): 먼저 보낸 느린 조회가 나중 조회보다 늦게 도착해도 사이드바는 나중 조회 값이다', async () => {
    window.history.replaceState(null, '', '#/persons')
    const releases: (() => void)[] = []
    let n = 0
    install(
      router({
        '/api/persons': () => {
          const mine = n++
          if (mine === 0) {
            // 첫째: 옛 값을 늦게 돌려준다
            return new Promise<Response>((resolve) => releases.push(() => resolve(json([PERSONS[0]]))))
          }
          return json([PERSONS[1]]) // 둘째: 새 값을 바로
        },
      }),
    )
    render(<App />)
    await waitFor(() => expect(n).toBe(1))
    notifyPersonsChanged()
    const side = screen.getByTestId('sidebar-persons')
    await within(side).findByText('철수')
    releases[0]() // 첫째가 뒤늦게 도착
    await new Promise((r) => setTimeout(r, 50))
    expect(within(side).getByText('철수')).toBeInTheDocument()
    expect(within(side).queryByText('박대리')).toBeNull()
  })

  it('본문은 PersonGrid, 사이드바는 PersonList 를 import 한다 (P8b U1)', () => {
    expect(appShellSource).toContain("import PersonList from '@/components/PersonList'")
    expect(cardScreenSource).toContain("import PersonGrid from '@/components/PersonGrid'")
    expect(cardScreenSource).not.toContain("import PersonList from")
    expect(cardScreenSource).toContain('<PersonGrid />')
  })

  it('P8b U2 (결정 E): 7명이면 사이드바는 서버 순서의 앞 5명만, 마지막 링크는 전체 보기 → (href #/persons)', async () => {
    expect(SIDEBAR_RECENT_LIMIT).toBe(5)
    window.history.replaceState(null, '', '#/chat')
    install(router({ '/api/persons': () => json(SEVEN), '/api/questions/pending': () => json([]) }))
    render(<App />)
    const side = screen.getByTestId('sidebar-persons')
    await within(side).findByText('아린')
    const links = within(side).getAllByRole('link')
    expect(links.map((l) => l.getAttribute('href'))).toEqual([
      '#/persons/51',
      '#/persons/48',
      '#/persons/55',
      '#/persons/50',
      '#/persons/53',
      '#/persons',
    ])
    expect(links[5].textContent).toBe('전체 보기 →')
    expect(links[5]).toBe(screen.getByTestId('sidebar-see-all'))
    expect(within(side).queryByText('가을')).toBeNull()
    expect(within(side).queryByText('가람')).toBeNull()
  })

  it('P8b U2: 인물이 5명 이하(3명)이면 3명 + 전체 보기 →', async () => {
    window.history.replaceState(null, '', '#/chat')
    install(router({ '/api/persons': () => json(PERSONS), '/api/questions/pending': () => json([]) }))
    render(<App />)
    const side = screen.getByTestId('sidebar-persons')
    await within(side).findByText('박대리')
    expect(within(side).getAllByRole('link').map((l) => l.getAttribute('href'))).toEqual([
      '#/persons/7',
      '#/persons/4',
      '#/persons/9',
      '#/persons',
    ])
    expect(screen.getByTestId('sidebar-see-all').textContent).toBe('전체 보기 →')
  })

  it('P8b U2: 정확히 5명이면 5명 모두 + 전체 보기 → (경계)', async () => {
    window.history.replaceState(null, '', '#/chat')
    install(router({ '/api/persons': () => json(SEVEN.slice(0, 5)), '/api/questions/pending': () => json([]) }))
    render(<App />)
    const side = screen.getByTestId('sidebar-persons')
    await within(side).findByText('마루')
    expect(within(side).getAllByRole('link')).toHaveLength(6)
  })

  it('P8b U2: 인물 0명이면 전체 보기 없음', async () => {
    window.history.replaceState(null, '', '#/chat')
    install(router({ '/api/persons': () => json([]), '/api/questions/pending': () => json([]) }))
    render(<App />)
    const side = screen.getByTestId('sidebar-persons')
    await within(side).findByText(PERSON_LIST_NOTICE.empty)
    expect(screen.queryByTestId('sidebar-see-all')).toBeNull()
    expect(within(side).queryByText('전체 보기 →')).toBeNull()
  })

  it('P8b U2: 조회 실패면 전체 보기 없음', async () => {
    window.history.replaceState(null, '', '#/chat')
    install(
      router({
        '/api/persons': () => json({ detail: { code: 'x' } }, 500),
        '/api/questions/pending': () => json([]),
      }),
    )
    render(<App />)
    const side = screen.getByTestId('sidebar-persons')
    await within(side).findByText(PERSON_LIST_NOTICE.failed)
    expect(screen.queryByTestId('sidebar-see-all')).toBeNull()
  })

  it('P8b U2: #/persons 본문 그리드는 7명 전원을 서버 순서로 그린다(사이드바 자르기가 번지지 않는다)', async () => {
    window.history.replaceState(null, '', '#/persons')
    install(router({ '/api/persons': () => json(SEVEN) }))
    render(<App />)
    await screen.findByTestId('person-grid')
    expect(tileIds()).toEqual(['51', '48', '55', '50', '53', '49', '52'])
    expect(within(screen.getByTestId('sidebar-persons')).getAllByRole('link')).toHaveLength(6)
  })

  it('P8b U2: 좁은 폭 서랍에서 전체 보기 → 를 누르면 #/persons 로 가고 서랍이 닫힌다', async () => {
    installFakeMatchMedia(800)
    window.history.replaceState(null, '', '#/chat')
    install(router({ '/api/persons': () => json(SEVEN), '/api/questions/pending': () => json([]) }))
    render(<App />)
    await userEvent.click(screen.getByRole('button', { name: '메뉴 열기' }))
    const nav = screen.getByRole('navigation', { name: '주 메뉴' })
    await userEvent.click(await within(nav).findByTestId('sidebar-see-all'))
    expect(window.location.hash).toBe('#/persons')
    await waitFor(() => expect(screen.queryByRole('navigation', { name: '주 메뉴' })).toBeNull())
  })

  it('좁은 폭: 서랍에서 항목을 고르면 서랍이 닫힌다', async () => {
    installFakeMatchMedia(800)
    window.history.replaceState(null, '', '#/chat')
    install(
      router({
        '/api/persons': () => json(PERSONS),
        '/api/questions/pending': () => json([]),
      }),
    )
    render(<App />)
    await userEvent.click(screen.getByRole('button', { name: '메뉴 열기' }))
    const nav = screen.getByRole('navigation', { name: '주 메뉴' })
    await userEvent.click(await within(nav).findByRole('link', { name: /철수/ }))
    expect(window.location.hash).toBe('#/persons/4')
    await waitFor(() => expect(screen.queryByRole('navigation', { name: '주 메뉴' })).toBeNull())
  })
})

describe('인물 카드 — 섹션과 값', () => {
  it('섹션 7개가 부록 A ② 순서로 놓인다', async () => {
    install(cardRouter())
    const { container } = render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    const names = Array.from(container.querySelectorAll('[data-section]')).map((s) => s.getAttribute('data-section'))
    expect(names).toEqual(['header', 'aliases', 'last-contact', 'facts', 'patterns', 'timeline', 'schedules'])
    const headings = within(screen.getByTestId('person-card'))
      .getAllByRole('heading', { level: 2 })
      .map((h) => h.textContent)
    expect(headings).toEqual([
      '김팀장',
      `▸${CARD_NOTICE.factsTitle}`,
      `▸${CARD_NOTICE.patternsTitle}`,
      `▸${CARD_NOTICE.timelineTitle}`,
      `▸${CARD_NOTICE.schedulesTitle}`,
    ])
  })

  it('각 섹션의 값이 서버가 준 그대로 나온다', async () => {
    install(cardRouter())
    const { container } = render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    const sec = (n: string) => container.querySelector(`[data-section="${n}"]`) as HTMLElement
    expect(sec('header')).toHaveTextContent('김팀장')
    expect(sec('header')).toHaveTextContent('직장 · 상')
    expect(sec('aliases').textContent).toBe('별칭: 팀장, 우리 팀장님, 부장님')
    expect(sec('last-contact').textContent).toBe('마지막 접촉: 2026. 9. 3.')
    expect(within(sec('facts')).getByText('딸 대학 입시 중')).toBeInTheDocument()
    expect(within(sec('facts')).getByText('child')).toBeInTheDocument()
    expect(within(sec('facts')).getByText('골프 안 침')).toBeInTheDocument()
    expect(within(sec('patterns')).getByText('공개 석상에서 지적 — 3회')).toBeInTheDocument()
    expect(within(sec('patterns')).getByText('pattern:conflict')).toBeInTheDocument()
    expect(within(sec('schedules')).getByText('분기 회의')).toBeInTheDocument()
    expect(sec('schedules').textContent).toMatch(/2026\. 9\. 10\./)
  })

  it('타임라인은 서버 순서 그대로, 항목마다 날짜·type·content', async () => {
    install(cardRouter())
    const { container } = render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    const items = Array.from(container.querySelectorAll('[data-testid^="timeline-"]'))
    expect(items.map((i) => i.getAttribute('data-testid'))).toEqual(['timeline-5', 'timeline-9', 'timeline-2'])
    expect(items[0].textContent).toContain('2026. 8. 21.')
    expect(items[0].textContent).toContain('meal')
    expect(items[0].textContent).toContain('점심 같이 함')
    expect(items[1].textContent).toContain('conflict')
    expect(items[1].textContent).toContain('회의에서 보고서 공개 지적')
  })

  it('source_count 가 0 이면 근거 보기 버튼이 없고, 양수면 있다', async () => {
    install(cardRouter())
    render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    expect(within(screen.getByTestId('fact-11')).getByRole('button', { name: CARD_NOTICE.showSources })).toBeInTheDocument()
    expect(within(screen.getByTestId('fact-12')).queryByRole('button')).toBeNull()
    expect(within(screen.getByTestId('fact-21')).getByRole('button', { name: CARD_NOTICE.showSources })).toBeInTheDocument()
  })

  it('비어 있는 섹션은 짧은 빈 문구를 보여 준다', async () => {
    install(
      router({
        '/api/persons/3': () =>
          json({ ...CARD, aliases: [], last_contact_at: null, facts: [], patterns: [], timeline: [], upcoming_schedules: [] }),
      }),
    )
    const { container } = render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    const sec = (n: string) => container.querySelector(`[data-section="${n}"]`) as HTMLElement
    expect(sec('aliases').textContent).toBe(`별칭: ${CARD_NOTICE.aliasesNone}`)
    expect(sec('last-contact').textContent).toBe(`마지막 접촉: ${CARD_NOTICE.lastContactNone}`)
    expect(sec('facts')).toHaveTextContent(CARD_NOTICE.factsEmpty)
    expect(sec('patterns')).toHaveTextContent(CARD_NOTICE.patternsEmpty)
    expect(sec('timeline')).toHaveTextContent(CARD_NOTICE.timelineEmpty)
    expect(sec('schedules')).toHaveTextContent(CARD_NOTICE.schedulesEmpty)
  })

  it('404 면 안내 한 줄과 목록으로 가는 링크', async () => {
    install(router({ '/api/persons/3': () => json({ detail: { code: 'not_found' } }, 404) }))
    render(<PersonCardScreen personId={3} />)
    expect(await screen.findByRole('alert')).toHaveTextContent(CARD_NOTICE.notFound)
    expect(screen.getByRole('link', { name: CARD_NOTICE.backToList })).toHaveAttribute('href', '#/persons')
    expect(screen.queryByTestId('person-card')).toBeNull()
  })

  it('404 가 아닌 실패는 다른 안내 문장', async () => {
    install(router({ '/api/persons/3': () => json({ detail: { code: 'x' } }, 500) }))
    render(<PersonCardScreen personId={3} />)
    expect(await screen.findByRole('alert')).toHaveTextContent(CARD_NOTICE.loadFailed)
  })
})

describe('원문 펼치기 (결정 F)', () => {
  it('카드·목록 응답에 원문이 없으면 아무 데도 원문이 보이지 않고, 원문 요청도 없다', async () => {
    const fetchFn = install(cardRouter())
    render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    expect(screen.queryByTestId('raw-utterance')).toBeNull()
    expect(document.body.textContent).not.toContain('팀장님이')
    expect(fetchFn.mock.calls.map(([u]) => String(u))).toEqual(['/api/persons/3'])
  })

  it('첫 펼침에 GET /events/{id}/raw 1회, 원문은 글자 그대로, 접었다 다시 펼쳐도 요청은 1회', async () => {
    const fetchFn = install(cardRouter({ '/api/events/9/raw': () => json(rawOut(9, RAW_A)) }))
    render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    const item = screen.getByTestId('timeline-9')
    const user = userEvent.setup()

    await user.click(within(item).getByRole('button', { name: CARD_NOTICE.showRaw }))
    const raw = await within(item).findByTestId('raw-utterance')
    expect(raw.textContent).toBe(RAW_A)
    expect(callsTo(fetchFn, '/api/events/9/raw')).toHaveLength(1)
    expect((callsTo(fetchFn, '/api/events/9/raw')[0][1] as RequestInit).method).toBe('GET')

    await user.click(within(item).getByRole('button', { name: CARD_NOTICE.hideRaw }))
    expect(within(item).queryByTestId('raw-utterance')).toBeNull()

    await user.click(within(item).getByRole('button', { name: CARD_NOTICE.showRaw }))
    expect((await within(item).findByTestId('raw-utterance')).textContent).toBe(RAW_A)
    expect(callsTo(fetchFn, '/api/events/9/raw')).toHaveLength(1)
  })

  it('다른 항목은 각자 한 번씩 요청한다', async () => {
    const fetchFn = install(
      cardRouter({
        '/api/events/9/raw': () => json(rawOut(9, RAW_A)),
        '/api/events/2/raw': () => json(rawOut(2, RAW_B)),
      }),
    )
    render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    const user = userEvent.setup()
    await user.click(within(screen.getByTestId('timeline-9')).getByRole('button', { name: CARD_NOTICE.showRaw }))
    await user.click(within(screen.getByTestId('timeline-2')).getByRole('button', { name: CARD_NOTICE.showRaw }))
    expect((await within(screen.getByTestId('timeline-2')).findByTestId('raw-utterance')).textContent).toBe(RAW_B)
    expect(callsTo(fetchFn, '/api/events/9/raw')).toHaveLength(1)
    expect(callsTo(fetchFn, '/api/events/2/raw')).toHaveLength(1)
  })

  it('조회 실패는 그 항목 안에만 안내가 뜨고, 다시 누르면 재시도(요청 2회)해 원문이 나온다', async () => {
    let n = 0
    const fetchFn = install(
      cardRouter({
        '/api/events/9/raw': () => (n++ === 0 ? json({ detail: { code: 'x' } }, 500) : json(rawOut(9, RAW_A))),
      }),
    )
    render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    const item = screen.getByTestId('timeline-9')
    const user = userEvent.setup()

    await user.click(within(item).getByRole('button', { name: CARD_NOTICE.showRaw }))
    expect(await within(item).findByRole('alert')).toHaveTextContent(CARD_NOTICE.detailFailed)
    // 화면 전체 안내가 아니다: 알림은 이 항목 안의 하나뿐이고, 카드와 다른 항목은 그대로다.
    expect(screen.getAllByRole('alert')).toHaveLength(1)
    expect(screen.getByTestId('person-card')).toBeInTheDocument()
    expect(within(screen.getByTestId('timeline-5')).queryByRole('alert')).toBeNull()
    expect(callsTo(fetchFn, '/api/events/9/raw')).toHaveLength(1)

    await user.click(within(item).getByRole('button'))
    expect((await within(item).findByTestId('raw-utterance')).textContent).toBe(RAW_A)
    expect(callsTo(fetchFn, '/api/events/9/raw')).toHaveLength(2)
    expect(screen.queryByRole('alert')).toBeNull()
  })

  it('R-U6-1: 로딩 중 접기 → 요청 실패 → 다시 펼치면 열리고 재시도해 원문이 나온다', async () => {
    let rejectFirst: () => void = () => {}
    let n = 0
    const fetchFn = install(
      cardRouter({
        '/api/events/9/raw': () => {
          if (n++ === 0) {
            return new Promise<Response>((resolve) => {
              rejectFirst = () => resolve(json({ detail: { code: 'x' } }, 500))
            })
          }
          return json(rawOut(9, RAW_A))
        },
      }),
    )
    render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    const item = screen.getByTestId('timeline-9')
    const user = userEvent.setup()

    await user.click(within(item).getByRole('button', { name: CARD_NOTICE.showRaw })) // 1) 펼침(로딩)
    await user.click(within(item).getByRole('button', { name: CARD_NOTICE.hideRaw })) // 2) 로딩 중 접음
    rejectFirst() // 3) 요청 실패
    await waitFor(() => expect(callsTo(fetchFn, '/api/events/9/raw')).toHaveLength(1))
    await user.click(within(item).getByRole('button', { name: CARD_NOTICE.showRaw })) // 4) 다시 펼침

    expect((await within(item).findByTestId('raw-utterance')).textContent).toBe(RAW_A)
    expect(callsTo(fetchFn, '/api/events/9/raw')).toHaveLength(2)
    expect(within(item).getByRole('button', { name: CARD_NOTICE.hideRaw })).toBeInTheDocument()
  })

  it('근거 보기: sources 요청 1회, 항목 수·날짜·content·원문이 그대로, 접기, 다시 펼쳐도 재요청 없음', async () => {
    const fetchFn = install(cardRouter({ '/api/persons/3/facts/11/sources': () => json(SOURCES_11) }))
    render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    const fact = screen.getByTestId('fact-11')
    const user = userEvent.setup()

    await user.click(within(fact).getByRole('button', { name: CARD_NOTICE.showSources }))
    const list = await within(fact).findByTestId('sources-11')
    const items = within(list).getAllByRole('listitem')
    expect(items).toHaveLength(2)
    expect(items[0].textContent).toContain('2026. 8. 21. · 점심 같이 함')
    expect(items[1].textContent).toContain('2026. 9. 3. · 보고서 지적')
    expect(within(items[0]).getByTestId('raw-utterance').textContent).toBe(RAW_C)
    expect(within(items[1]).getByTestId('raw-utterance').textContent).toBe(RAW_B)
    expect(callsTo(fetchFn, '/api/persons/3/facts/11/sources')).toHaveLength(1)

    await user.click(within(fact).getByRole('button', { name: CARD_NOTICE.hideSources }))
    expect(within(fact).queryByTestId('sources-11')).toBeNull()
    await user.click(within(fact).getByRole('button', { name: CARD_NOTICE.showSources }))
    expect(await within(fact).findByTestId('sources-11')).toBeInTheDocument()
    expect(callsTo(fetchFn, '/api/persons/3/facts/11/sources')).toHaveLength(1)
  })

  it('패턴의 근거 보기도 그 패턴 id 로 요청한다', async () => {
    const fetchFn = install(
      cardRouter({
        '/api/persons/3/facts/21/sources': () =>
          json({ fact: { id: 21, key: 'pattern:conflict', value: 'v' }, sources: SOURCES_11.sources.slice(1) }),
      }),
    )
    render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    await userEvent.click(within(screen.getByTestId('fact-21')).getByRole('button', { name: CARD_NOTICE.showSources }))
    expect((await screen.findByTestId('sources-21')).textContent).toContain(RAW_B.slice(0, 3))
    expect(callsTo(fetchFn, '/api/persons/3/facts/21/sources')).toHaveLength(1)
  })

  it('근거 조회 실패는 그 사실 안에만 안내, 다시 누르면 재시도(요청 2회)', async () => {
    let n = 0
    const fetchFn = install(
      cardRouter({
        '/api/persons/3/facts/11/sources': () => (n++ === 0 ? json({ detail: { code: 'x' } }, 500) : json(SOURCES_11)),
      }),
    )
    render(<PersonCardScreen personId={3} />)
    await screen.findByTestId('person-card')
    const fact = screen.getByTestId('fact-11')
    const user = userEvent.setup()
    await user.click(within(fact).getByRole('button', { name: CARD_NOTICE.showSources }))
    expect(await within(fact).findByRole('alert')).toHaveTextContent(CARD_NOTICE.detailFailed)
    expect(screen.getAllByRole('alert')).toHaveLength(1)
    expect(within(screen.getByTestId('fact-21')).queryByRole('alert')).toBeNull()

    await user.click(within(fact).getByRole('button'))
    expect(await within(fact).findByTestId('sources-11')).toBeInTheDocument()
    expect(callsTo(fetchFn, '/api/persons/3/facts/11/sources')).toHaveLength(2)
  })
})
