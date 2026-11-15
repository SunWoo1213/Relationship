// P9b U6 — 로그인 관문 E2E (가짜 API, 실제 Chromium, `vite preview` 빌드).
// me 401 → 로그인 화면 → 로그인 → 앱 틀 → 로그아웃 → 다시 로그인 화면. 판정 27b 요청 URL 단언 포함.
import { expect, test } from '@playwright/test'
import { expectNoStrayRequests, freezeClock, installFakeApi } from './fixtures.ts'

test('로그인 화면에서 로그인하면 앱 틀이 열리고, 로그아웃하면 다시 로그인 화면이 된다', async ({ page, baseURL }) => {
  await freezeClock(page)
  let loggedIn = false
  const api = await installFakeApi(page, baseURL!, {
    'GET /api/auth/me': () => (loggedIn ? { json: { id: 'u1', username: 'minji_01', nickname: '민지' } } : { status: 401, json: { detail: { code: 'unauthenticated' } } }),
    'POST /api/auth/login': () => {
      loggedIn = true
      return { json: { id: 'u1', username: 'minji_01', nickname: '민지' } }
    },
    'POST /api/auth/logout': () => {
      loggedIn = false
      return { status: 204, json: null }
    },
    'GET /api/persons': { json: [] },
    'GET /api/questions/pending': { json: [] },
  })

  await page.goto('/#/chat')
  await expect(page.locator('[data-screen="auth"]')).toBeVisible()
  await expect(page.getByLabel('비밀번호', { exact: true })).toHaveAttribute('type', 'password')

  await page.getByLabel('아이디').fill('minji_01')
  await page.getByLabel('비밀번호', { exact: true }).fill('correct-horse-9')
  await page.getByRole('button', { name: '로그인' }).click()

  await expect(page.locator('[data-screen="chat"]')).toBeVisible()
  await expect(page.getByTestId('sidebar-username')).toHaveText('minji_01')
  expect(api.callsTo('POST /api/auth/login')[0].body).toEqual({ username: 'minji_01', password: 'correct-horse-9' })

  await page.getByRole('button', { name: '로그아웃' }).click()
  await expect(page.locator('[data-screen="auth"]')).toBeVisible()
  expect(api.callsTo('POST /api/auth/logout')).toHaveLength(1)

  expectNoStrayRequests(api, baseURL!)
})
