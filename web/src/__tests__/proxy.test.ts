import { describe, expect, it } from 'vitest'
import { stripApiPrefix } from '@/proxy'

describe('vite.config.ts 프록시 연결 (결정 C (ii))', () => {
  it('/api 프록시가 stripApiPrefix 로 접두를 벗기고 대상 기본값은 http://localhost:8000', async () => {
    const mod = await import('../../vite.config')
    const factory = mod.default as unknown as (env: { mode: string; command: string }) => {
      server: { proxy: Record<string, { target: string; rewrite: (p: string) => string }> }
    }
    const rule = factory({ mode: 'test', command: 'serve' }).server.proxy['/api']
    expect(rule.rewrite).toBe(stripApiPrefix)
    expect(rule.rewrite('/api/persons/3')).toBe('/persons/3')
    expect(rule.target).toBe('http://localhost:8000')
  })
})

describe('개발 서버 프록시 경로 변환 (결정 C (ii))', () => {
  it('/api 접두를 벗긴다', () => {
    expect(stripApiPrefix('/api/persons/3')).toBe('/persons/3')
    expect(stripApiPrefix('/api/chat')).toBe('/chat')
    expect(stripApiPrefix('/api/briefings?schedule_id=4')).toBe('/briefings?schedule_id=4')
  })

  it('/api 만 오면 루트 /', () => {
    expect(stripApiPrefix('/api')).toBe('/')
    expect(stripApiPrefix('/api?x=1')).toBe('/?x=1')
  })

  it('/api 로 시작하지 않는 경로는 그대로 (접두가 비슷한 /apix 포함)', () => {
    expect(stripApiPrefix('/other')).toBe('/other')
    expect(stripApiPrefix('/apix/persons')).toBe('/apix/persons')
    expect(stripApiPrefix('/x/api/persons')).toBe('/x/api/persons')
  })
})
