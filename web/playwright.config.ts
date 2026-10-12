import { defineConfig } from '@playwright/test'

// U9 에서 E2E 를 채운다. 지금은 설정과 빈 e2e 디렉터리까지만 (브라우저 설치 없음).
// 자동 테스트는 실제 백엔드·LLM·푸시 서비스를 쓰지 않는다 (결정 J) — 가짜 API 는 e2e/fixtures 에서.
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:5173',
  },
})
