import { vi } from 'vitest'

/**
 * 가짜 matchMedia. `(min-width: Npx)` 질의를 현재 가짜 창 너비로 판정하고,
 * setWidth 로 너비를 바꾸면 change 리스너를 부른다.
 */
export function installFakeMatchMedia(initialWidth: number) {
  let width = initialWidth
  const listeners = new Set<() => void>()

  const matchMedia = (query: string) => {
    const m = /\(min-width:\s*(\d+)px\)/.exec(query)
    return {
      get matches() {
        return m ? width >= Number(m[1]) : false
      },
      media: query,
      addEventListener: (_: string, cb: () => void) => listeners.add(cb),
      removeEventListener: (_: string, cb: () => void) => listeners.delete(cb),
    }
  }
  vi.stubGlobal('matchMedia', matchMedia)
  Object.defineProperty(window, 'matchMedia', { value: matchMedia, configurable: true, writable: true })

  return {
    setWidth(next: number) {
      width = next
      listeners.forEach((cb) => cb())
    },
  }
}
