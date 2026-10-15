// 판정 27b행 (R-5) — 자동 테스트의 실 네트워크 0 규칙 자체를 시험한다.
// test-setup.ts 가 전역 fetch 를 "불리면 실패" 로 바꿔 두므로, 가짜 표 없이 부른 요청은 모두 실패해야 한다.
// 이 안전망이 풀리면(예: setup 에서 fetch 교체가 빠지면) 다른 테스트가 모르는 새 실제 요청이 나가도 조용히 통과한다.
import { describe, expect, it } from 'vitest'
import { apiFetch } from '@/api/client'

describe('실 네트워크 0 (setup 의 가짜 fetch)', () => {
  it('표에 없는 바깥 주소 fetch("https://example.invalid") 는 실패한다', async () => {
    await expect((async () => fetch('https://example.invalid'))()).rejects.toThrow('실제 네트워크 요청은 허용되지 않는다')
  })

  it('가짜 표 없이 앱 API 를 부르면(apiFetch → /api/persons) 응답 대신 실패한다', async () => {
    await expect(apiFetch('/persons')).rejects.toThrow('실제 네트워크 요청은 허용되지 않는다')
  })
})
