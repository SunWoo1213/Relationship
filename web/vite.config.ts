import path from 'node:path'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { loadEnv } from 'vite'
import { defineConfig } from 'vitest/config'
import { resolveApiTarget, stripApiPrefix } from './src/proxy.ts'

// 결정 C (ii): 같은 출처 `/api` 접두를 개발 서버 프록시가 벗겨 백엔드로 넘긴다.
// 대상 주소는 VITE_API_TARGET (기본 http://localhost:8000, web/.env.example).
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const target = resolveApiTarget(env)
  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: { '@': path.resolve(import.meta.dirname, 'src') },
    },
    build: {
      // 이전 산출물 지우기는 셸 명령이 아니라 Vite 옵션으로 한다 (Mac·Windows 공통).
      emptyOutDir: true,
    },
    server: {
      proxy: {
        '/api': {
          target,
          changeOrigin: true,
          rewrite: stripApiPrefix,
        },
      },
    },
    test: {
      environment: 'jsdom',
      globals: true,
      setupFiles: ['./src/test-setup.ts'],
      include: ['src/**/*.test.{ts,tsx}'],
    },
  }
})
