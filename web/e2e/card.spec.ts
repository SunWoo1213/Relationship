// 판정 25행 (ㄴ E2E 카드 원문·사이드바) + 27b행 요청 URL 단언 -- 가짜 API, 실제 Chromium, `vite preview` 빌드.
// 데스크톱(1280px): 사이드바 인물 클릭 -> 카드 -> 타임라인 펼치기, 사이드바 3개 항목으로 화면 3개 전환.
// 모바일(390px): 처음엔 서랍 닫힘·하단 탭바 없음 -> 메뉴 버튼 -> 서랍에서 "인물" -> 인물 -> 카드.
import { expect, test, type Page } from '@playwright/test'
import { expectNoStrayRequests, freezeClock, installFakeApi } from './fixtures.ts'

const RAW_31 = '어제 김팀장님이\n내 보고서를 칭찬해 주셨다 😀'
// 서버 순서는 이름순·id순과 다르다(최지우 8, 김팀장 3, 이서준 4, 박민수 12, 정하늘 6, 강다온 9).
// 사이드바는 앞 5명(강다온 제외), 그리드는 6명 전원. 김팀장(id 3)은 앞 5명 안.
const PERSONS = [
  { id: 8, display_name: '최지우', relation_tag: '친구', hierarchy: '동', last_contact_at: '2026-10-20T09:00:00+09:00', aliases: [] },
  { id: 3, display_name: '김팀장', relation_tag: '직장', hierarchy: '상', last_contact_at: '2026-10-14T09:00:00+09:00', aliases: ['팀장님', '김 부장'] },
  { id: 4, display_name: '이서준', relation_tag: '친구', hierarchy: '동', last_contact_at: null, aliases: ['서준이'] },
  { id: 12, display_name: '박민수', relation_tag: '지인', hierarchy: '동', last_contact_at: '2026-09-01T09:00:00+09:00', aliases: [] },
  { id: 6, display_name: '정하늘', relation_tag: '가족', hierarchy: '하', last_contact_at: null, aliases: ['하늘이'] },
  { id: 9, display_name: '강다온', relation_tag: '직장', hierarchy: '하', last_contact_at: '2026-08-01T09:00:00+09:00', aliases: ['막내'] },
]
const SIDEBAR_COUNT = 5
const CARD_3 = {
  person: { id: 3, display_name: '김팀장', relation_tag: '직장', hierarchy: '상' },
  aliases: ['팀장님', '김 부장'],
  last_contact_at: '2026-10-14T09:00:00+09:00',
  facts: [{ id: 11, key: 'likes', value: '커피', updated_at: '2026-10-14T09:00:00+09:00', source_count: 1 }],
  patterns: [],
  timeline: [
    { id: 31, type: 'praise', content: '보고서 칭찬', occurred_at: '2026-10-14T09:00:00+09:00' },
    { id: 32, type: 'meal', content: '점심 식사', occurred_at: '2026-10-10T12:00:00+09:00' },
  ],
  upcoming_schedules: [],
}

async function setup(page: Page, baseURL: string) {
  await freezeClock(page)
  return installFakeApi(page, baseURL, {
    'GET /api/persons': { json: PERSONS },
    'GET /api/persons/3': { json: CARD_3 },
    'GET /api/events/31/raw': {
      json: { event_id: 31, person_id: 3, type: 'praise', content: '보고서 칭찬', occurred_at: '2026-10-14T09:00:00+09:00', raw_utterance: RAW_31 },
    },
    'GET /api/questions/pending': { json: [] },
    'GET /api/briefings': { json: [] },
  })
}

const SCREEN = (name: string) => `[data-screen="${name}"]`

test.describe('데스크톱 폭 1280px', () => {
  test.use({ viewport: { width: 1280, height: 800 } })

  test('사이드바 인물 목록에서 인물을 눌러 카드를 열고 타임라인 원문을 펼친다', async ({ page, baseURL }) => {
    const api = await setup(page, baseURL!)
    await page.goto('/#/chat')

    // 사이드바는 항상 보이고 메뉴 버튼은 없다
    const sidebar = page.getByRole('navigation', { name: '주 메뉴' })
    await expect(sidebar).toBeVisible()
    await expect(page.getByRole('button', { name: '메뉴 열기' })).toHaveCount(0)

    // 인물 클릭 -> 본문에 그 인물 카드
    await page.getByTestId('sidebar-persons').getByRole('link', { name: /김팀장/ }).click()
    await expect(page).toHaveURL(/#\/persons\/3$/)
    const card = page.getByTestId('person-card')
    await expect(card.getByRole('heading', { name: '김팀장' })).toBeVisible()

    // 사이드바 3개 항목으로 화면 3개 전환 (각 화면 + 주소 + 현재 표시)
    for (const [label, screen, hash] of [
      ['채팅', 'chat', /#\/chat$/],
      ['인물', 'persons', /#\/persons$/],
      ['브리핑', 'briefings', /#\/briefings$/],
    ] as const) {
      await sidebar.getByRole('link', { name: label, exact: true }).click()
      await expect(page.locator(SCREEN(screen))).toBeVisible()
      await expect(page).toHaveURL(hash)
      await expect(sidebar.getByRole('link', { name: label, exact: true })).toHaveAttribute('aria-current', 'page')
    }
    // 항목 3 + 인물 링크 5(서버 순서 앞 5명) + 전체 보기 1 = 9 (R-U2-2)
    await expect(sidebar.getByRole('link')).toHaveCount(3 + SIDEBAR_COUNT + 1)
    await expect(sidebar.getByTestId('sidebar-persons').locator('a[href^="#/persons/"]')).toHaveCount(SIDEBAR_COUNT)
    await expect(sidebar.getByRole('link', { name: /강다온/ })).toHaveCount(0)

    // 전체 보기 -> #/persons 그리드: 6명 전원, 서버 순서 그대로
    await page.getByTestId('sidebar-see-all').click()
    await expect(page).toHaveURL(/#\/persons$/)
    const tiles = page.getByTestId('person-tile')
    await expect(tiles).toHaveCount(PERSONS.length)
    expect(await tiles.evaluateAll((els) => els.map((e) => e.getAttribute('data-person-id')))).toEqual(
      PERSONS.map((p) => String(p.id)),
    )

    // 결정 J: 목록 폭 -- 그리드가 본문(main) 안쪽 폭(좌우 p-6 24px x 2)을 채운다. 가운데 좁은 칸(max-w)이면 실패.
    const gridBox = await page.getByTestId('person-grid').boundingBox()
    const mainBox = await page.locator('main').boundingBox()
    console.log(`[U3 실측] grid.width=${gridBox!.width} main.width=${mainBox!.width} 차=${Math.abs(gridBox!.width - (mainBox!.width - 48))}`)
    expect(Math.abs(gridBox!.width - (mainBox!.width - 48))).toBeLessThanOrEqual(2)

    // 검색 1회(별칭) -> 타일이 줄어든다 -> 타일 클릭 -> 카드
    await page.getByTestId('person-search').fill('팀장님')
    await expect(tiles).toHaveCount(1)
    await expect(tiles.first()).toHaveAttribute('data-person-id', '3')
    await tiles.first().click()
    await expect(page).toHaveURL(/#\/persons\/3$/)
    const tileCard = page.getByTestId('person-card')
    await expect(tileCard.getByRole('heading', { name: '김팀장' })).toBeVisible()

    // 타임라인 펼치기 -> 원문 그대로, 요청은 1회
    await tileCard.getByTestId('timeline-31').getByRole('button', { name: '원문 펼치기' }).click()
    // toHaveText 는 공백을 정규화해 줄바꿈 훼손을 못 잡는다 -- textContent 완전 일치로 단언한다 (R-U9a-1)
    await expect(tileCard.getByTestId('raw-utterance')).toBeVisible()
    expect(await tileCard.getByTestId('raw-utterance').textContent()).toBe(RAW_31)
    expect(api.callsTo('GET /api/events/31/raw')).toHaveLength(1)

    expectNoStrayRequests(api, baseURL!)
  })
})

test.describe('모바일 폭 390px', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  test('서랍은 처음엔 닫혀 있고 하단 탭바가 없다. 메뉴 버튼 -> 인물 -> 인물 -> 카드, 항목을 고르면 서랍이 닫힌다', async ({ page, baseURL }) => {
    const api = await setup(page, baseURL!)
    await page.goto('/#/chat')

    // 처음: 서랍 닫힘, 사이드바 없음, 하단 탭바 없음
    await expect(page.locator(SCREEN('chat'))).toBeVisible()
    await expect(page.getByRole('navigation')).toHaveCount(0)
    await expect(page.getByRole('tablist')).toHaveCount(0)
    const menu = page.getByRole('button', { name: '메뉴 열기' })
    await expect(menu).toBeVisible()

    // 메뉴 버튼 -> 서랍 열림 -> "인물" 선택 -> 서랍 닫히고 인물 화면
    await menu.click()
    const drawer = page.getByRole('navigation', { name: '주 메뉴' })
    await expect(drawer).toBeVisible()
    await drawer.getByRole('link', { name: '인물', exact: true }).click()
    await expect(page.getByRole('navigation')).toHaveCount(0)
    await expect(page.locator(SCREEN('persons'))).toBeVisible()
    await expect(page).toHaveURL(/#\/persons$/)

    // 다시 열어 인물 선택 -> 서랍 닫히고 그 카드
    await menu.click()
    await expect(drawer).toBeVisible()
    await drawer.getByTestId('sidebar-persons').getByRole('link', { name: /김팀장/ }).click()
    await expect(page.getByRole('navigation')).toHaveCount(0)
    await expect(page).toHaveURL(/#\/persons\/3$/)
    await expect(page.getByTestId('person-card').getByRole('heading', { name: '김팀장' })).toBeVisible()
    await expect(page.getByRole('tablist')).toHaveCount(0)

    // 서랍 안 사이드바: 인물 5 + 전체 보기 -> 클릭하면 서랍이 닫히고 그리드가 1열(타일 x 좌표 모두 같음)
    await menu.click()
    await expect(drawer).toBeVisible()
    await expect(drawer.getByTestId('sidebar-persons').locator('a[href^="#/persons/"]')).toHaveCount(SIDEBAR_COUNT)
    await expect(drawer.getByTestId('sidebar-see-all')).toHaveCount(1)
    await drawer.getByTestId('sidebar-see-all').click()
    await expect(page.getByRole('navigation')).toHaveCount(0)
    await expect(page).toHaveURL(/#\/persons$/)
    const tiles = page.getByTestId('person-tile')
    await expect(tiles).toHaveCount(PERSONS.length)
    const xs = (await tiles.evaluateAll((els) => els.map((e) => e.getBoundingClientRect().x)))
    expect(xs).toHaveLength(PERSONS.length)
    expect(new Set(xs).size).toBe(1)
    console.log(`[U3 실측] 모바일 타일 x=${xs.join(',')}`)

    // 라우트는 3경로 그대로 -- 서랍을 열고 닫아도 주소가 바뀌지 않는다
    await menu.click()
    await expect(drawer).toBeVisible()
    await expect(page).toHaveURL(/#\/persons$/)
    await page.keyboard.press('Escape')
    await expect(page.getByRole('navigation')).toHaveCount(0)
    await expect(page).toHaveURL(/#\/persons$/)

    expectNoStrayRequests(api, baseURL!)
  })
})
