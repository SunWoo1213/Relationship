import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// 자동 테스트는 실제 네트워크를 쓰지 않는다 (결정 J) — fetch 가 불리면 즉시 실패시킨다.
afterEach(() => {
  cleanup()
})

globalThis.fetch = (() => {
  throw new Error('테스트에서 실제 네트워크 요청은 허용되지 않는다 (결정 J)')
}) as typeof fetch
