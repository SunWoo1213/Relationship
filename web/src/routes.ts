// 해시 라우팅 3경로 (결정 C, 원칙5 — 화면 3개 고정). 새 경로를 더하지 않는다.
import { useEffect, useSyncExternalStore } from 'react'

export type Route =
  | { name: 'chat' }
  | { name: 'persons'; personId: number | null }
  | { name: 'briefings' }

export const HREF = {
  chat: '#/chat',
  persons: '#/persons',
  briefings: '#/briefings',
} as const

export const DEFAULT_HASH = HREF.chat

/** `#/persons/12?x=1` → `/persons/12` (쿼리·앞 `#` 제거). */
function pathOf(hash: string): string {
  const withoutHash = hash.startsWith('#') ? hash.slice(1) : hash
  const q = withoutHash.indexOf('?')
  return q === -1 ? withoutHash : withoutHash.slice(0, q)
}

/** 알 수 없는 해시는 null — 호출 쪽이 `#/chat` 으로 보낸다. */
export function parseHash(hash: string): Route | null {
  const path = pathOf(hash)
  if (path === '/chat') return { name: 'chat' }
  if (path === '/briefings') return { name: 'briefings' }
  if (path === '/persons') return { name: 'persons', personId: null }
  const m = /^\/persons\/(\d+)$/.exec(path)
  if (m) return { name: 'persons', personId: Number(m[1]) }
  return null
}

function subscribe(onChange: () => void): () => void {
  window.addEventListener('hashchange', onChange)
  return () => window.removeEventListener('hashchange', onChange)
}

function snapshot(): string {
  return window.location.hash
}

/** 현재 해시를 구독한다. 알 수 없는 해시면 주소를 `#/chat` 으로 바꾸고 chat 을 돌려준다. */
export function useRoute(): Route {
  const hash = useSyncExternalStore(subscribe, snapshot)
  const route = parseHash(hash)
  const unknown = route === null
  useEffect(() => {
    if (!unknown) return
    // history.replaceState 로 — 뒤로 가기 기록을 늘리지 않는다. replaceState 는 hashchange 를
    // 일으키지 않으므로 구독자가 새 해시를 읽도록 이벤트를 직접 알린다.
    window.history.replaceState(null, '', DEFAULT_HASH)
    window.dispatchEvent(new HashChangeEvent('hashchange'))
  }, [unknown])
  return route ?? { name: 'chat' }
}
