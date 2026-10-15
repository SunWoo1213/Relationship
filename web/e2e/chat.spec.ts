// 판정 24행 (ㄱ E2E 채팅 칩) + 27b행 요청 URL 단언 -- 가짜 API, 실제 Chromium, `vite preview` 빌드.
// 발화 -> 칩 -> 클릭 -> 재개 응답(새 칩) -> 새로고침 -> 대기 질문 칩 복원.
import { expect, test } from '@playwright/test'
import { expectNoStrayRequests, freezeClock, installFakeApi, type ApiCall } from './fixtures.ts'

const stored0 = { persons: 0, events: 0, schedules: 0 }

test('발화를 보내면 칩이 뜨고, 눌러 재개된 reply 가 보이며, 새로고침하면 남은 질문 칩이 복원된다', async ({ page, baseURL }) => {
  await freezeClock(page)
  // 서버가 들고 있는 미답변 질문 -- 상태가 있는 가짜
  let pending: unknown[] = []
  const q7 = { question_id: 7, status: 'pending', kind: 'identity', question: '어떤 관계인가요?', options: ['직장', '친구', '아니요'] }
  const q8 = { question_id: 8, status: 'pending', kind: 'schedule', question: '일정으로 저장할까요?', options: ['예', '나중에'] }

  const api = await installFakeApi(page, baseURL!, {
    'GET /api/persons': { json: [] },
    'GET /api/questions/pending': () => ({ json: pending }),
    'POST /api/chat': () => {
      pending = [q7]
      return { json: { reply: '민지가 누구인지 확인할게요.', session_id: 's-1', stored: stored0, pending_question: q7, stop_reason: 'ask_user', trace_ids: [1] } }
    },
    'POST /api/answers/7': () => {
      pending = [q8]
      return { json: { question_id: 7, status: 'answered', reply: '친구로 기록했어요.', stored: stored0, pending_question: q8, stop_reason: 'ask_user', trace_ids: [2] } }
    },
    'POST /api/answers/8': (_call: ApiCall) => {
      pending = []
      return { json: { question_id: 8, status: 'answered', reply: '일정으로 저장했어요.', stored: stored0, pending_question: null, stop_reason: null, trace_ids: [3] } }
    },
  })

  await page.goto('/#/chat')
  await expect(page.locator('[data-screen="chat"]')).toBeVisible()

  // 발화 -> 응답 바로 아래에 칩 3개(글자·순서 그대로)
  await page.getByRole('textbox', { name: '메시지 입력' }).fill('어제 민지랑 점심 먹었어')
  await page.getByRole('textbox', { name: '메시지 입력' }).press('Enter')
  await expect(page.getByText('민지가 누구인지 확인할게요.')).toBeVisible()
  const chips7 = page.getByTestId('chips-7')
  await expect(chips7.getByRole('button')).toHaveText(['직장', '친구', '아니요'])

  // 칩 클릭 -> 눌린 칩은 선택 상태, 나머지는 비활성, 재개 reply 와 새 칩(8)
  await chips7.getByRole('button', { name: '친구' }).click()
  await expect(page.getByText('친구로 기록했어요.')).toBeVisible()
  await expect(chips7.getByRole('button', { name: '친구' })).toHaveAttribute('aria-pressed', 'true')
  await expect(chips7.getByRole('button', { name: '직장' })).toBeDisabled()
  await expect(chips7.getByRole('button', { name: '아니요' })).toBeDisabled()
  await expect(page.getByTestId('chips-8').getByRole('button')).toHaveText(['예', '나중에'])

  // 새로고침 -> 화면 메모리는 지워지고, 미답변 질문 8 만 GET /api/questions/pending 으로 복원된다
  const pendingBefore = api.callsTo('GET /api/questions/pending').length
  await page.reload()
  await expect(page.getByTestId('chips-8').getByRole('button')).toHaveText(['예', '나중에'])
  await expect(page.getByText('일정으로 저장할까요?')).toBeVisible()
  await expect(page.getByText('친구로 기록했어요.')).toHaveCount(0)
  expect(api.callsTo('GET /api/questions/pending').length).toBe(pendingBefore + 1)

  // 복원된 칩으로 이어서 답한다
  await page.getByTestId('chips-8').getByRole('button', { name: '예' }).click()
  await expect(page.getByText('일정으로 저장했어요.')).toBeVisible()

  // 요청 본문·세션 헤더: 첫 /chat 에는 세션이 없고, 이후는 응답이 준 s-1 을 보낸다
  const chat = api.callsTo('POST /api/chat')
  expect(chat).toHaveLength(1)
  expect(chat[0].body).toEqual({ utterance: '어제 민지랑 점심 먹었어' })
  expect(chat[0].headers['x-session-id']).toBeUndefined()
  const a7 = api.callsTo('POST /api/answers/7')
  expect(a7).toHaveLength(1)
  expect(a7[0].body).toEqual({ answer: '친구' })
  expect(a7[0].headers['x-session-id']).toBe('s-1')
  const a8 = api.callsTo('POST /api/answers/8')
  expect(a8).toHaveLength(1)
  expect(a8[0].body).toEqual({ answer: '예' })
  // 새로고침 뒤에도 세션이 localStorage 에 남아 복원 요청에 실린다
  const restore = api.callsTo('GET /api/questions/pending').at(-1)!
  expect(restore.headers['x-session-id']).toBe('s-1')

  // 판정 27b: 요청 URL 전부가 preview 호스트의 앱 파일 또는 /api/ 경로
  expectNoStrayRequests(api, baseURL!)
})
