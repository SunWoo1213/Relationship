// 판정 26행 (ㄷ E2E 브리핑) + 27b행 요청 URL 단언 -- 가짜 API, 실제 Chromium, `vite preview` 빌드.
// `#/briefings?schedule_id=N` 을 직접 열면 그 일정이 맨 위·강조, "지금 브리핑" 뒤 목록이 갱신된다.
import { expect, test } from '@playwright/test'
import { expectNoStrayRequests, freezeClock, installFakeApi } from './fixtures.ts'

function record(scheduleId: number, name: string, title: string, scheduledAt: string, lineText: string) {
  return {
    schedule: { id: scheduleId, title, scheduled_at: scheduledAt },
    person: { id: scheduleId, display_name: name },
    generated_at: '2026-10-15T08:00:00+09:00',
    composer: 'template',
    pattern_sentences: [],
    lines: [{ text: lineText, basis: { fact_keys: [], event_ids: [] } }],
    suggestion: { text: `${name}에게 먼저 인사하기`, basis: { fact_keys: [], event_ids: [] } },
    push: 'sent',
    trace_id: scheduleId * 10,
  }
}

test('쿼리의 일정이 맨 위에 강조돼 열리고, 지금 브리핑을 누르면 목록이 다시 읽힌다', async ({ page, baseURL }) => {
  await freezeClock(page)
  // 서버 순서 = 일정 시각 내림차순: 9 가 7 보다 앞. 실행 전/후로 7 의 줄이 달라진다.
  let lineOf7 = '지난 회의에서 일정이 밀렸어요'
  const list = () => [
    record(9, '이서준', '저녁 약속', '2026-10-16T19:00:00+09:00', '서준은 매운 음식을 싫어해요'),
    record(7, '김팀장', '주간 회의', '2026-10-15T10:00:00+09:00', lineOf7),
  ]
  const api = await installFakeApi(page, baseURL!, {
    'GET /api/persons': { json: [] },
    'GET /api/briefings': () => ({ json: list() }),
    'POST /api/briefings/run': () => {
      lineOf7 = '지난 회의 뒤 일정이 다시 잡혔어요'
      return {
        json: { run_id: 'r-1', generated_at: '2026-10-15T09:00:00+09:00', briefings: [], skipped: [] },
      }
    },
  })

  await page.goto('/#/briefings?schedule_id=7')
  await expect(page.locator('[data-screen="briefings"]')).toBeVisible()

  // 서버 순서는 [9, 7] 이지만 쿼리의 7 이 맨 위·강조
  const items = page.getByTestId('briefing-list').locator(':scope > li')
  await expect(items).toHaveCount(2)
  await expect(items.nth(0)).toHaveAttribute('data-testid', 'briefing-7')
  await expect(items.nth(0)).toHaveAttribute('data-highlight', 'true')
  await expect(items.nth(1)).toHaveAttribute('data-testid', 'briefing-9')
  await expect(items.nth(1)).not.toHaveAttribute('data-highlight', 'true')
  await expect(items.nth(0)).toContainText('김팀장 · 주간 회의')
  await expect(items.nth(0)).toContainText('지난 회의에서 일정이 밀렸어요')

  // 지금 브리핑 -> 본문 {schedule_id: 7} -> 목록 다시 읽기 -> 갱신된 줄
  await items.nth(0).getByRole('button', { name: '지금 브리핑' }).click()
  await expect(items.nth(0)).toContainText('지난 회의 뒤 일정이 다시 잡혔어요')
  await expect(items.nth(0)).not.toContainText('지난 회의에서 일정이 밀렸어요')
  await expect(items.nth(0)).toHaveAttribute('data-testid', 'briefing-7')

  const runs = api.callsTo('POST /api/briefings/run')
  expect(runs).toHaveLength(1)
  expect(runs[0].body).toEqual({ schedule_id: 7 })
  expect(api.callsTo('GET /api/briefings')).toHaveLength(2) // 진입 1 + 실행 뒤 다시 읽기 1

  expectNoStrayRequests(api, baseURL!)
})
