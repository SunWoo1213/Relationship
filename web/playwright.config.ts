import { defineConfig } from '@playwright/test'

// E2E 는 개발 서버가 아니라 `vite preview` 로 띄운 빌드 산출물을 대상으로 한다 (결정 J, R-U4-8).
// 포트 4173 은 vite preview 기본값이다 -- webServer 가 직접 띄우므로 따로 켜 둘 필요가 없다.
// API 는 e2e/fixtures.ts 의 가짜 표가 대신 답한다 -- 실제 백엔드·LLM·푸시 서비스를 쓰지 않는다 (결정 J).
const PREVIEW_PORT = 4173
const PREVIEW_URL = `http://localhost:${PREVIEW_PORT}`

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: PREVIEW_URL,
    // page.route 는 서비스 워커 요청을 가로채지 못한다 -- 워커를 막아 27b 가 뚫리지 않게 한다 (R-U9a-2)
    serviceWorkers: 'block',
  },
  webServer: {
    // 빌드를 먼저 해 항상 현재 소스의 산출물을 본다. `&&` 는 Mac(zsh)·Windows(cmd) 모두 같은 뜻이다.
    command: `npm run build && npm run preview -- --port ${PREVIEW_PORT} --strictPort`,
    url: PREVIEW_URL,
    reuseExistingServer: false,
    timeout: 120_000,
  },
})
