import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from '@/App'
import { parseHash } from '@/routes'
import { installFakeMatchMedia } from './helpers'

function goto(hash: string) {
  window.history.replaceState(null, '', hash)
}

beforeEach(() => {
  installFakeMatchMedia(1280) // 데스크톱 폭
  window.localStorage.clear()
})

afterEach(() => {
  vi.unstubAllGlobals()
  goto('#/chat')
})

describe('해시 라우팅 3경로 (결정 C)', () => {
  it.each([
    ['#/chat', 'chat', '채팅'],
    ['#/persons', 'persons', '인물'],
    ['#/briefings', 'briefings', '브리핑'],
  ])('%s 는 %s 빈 화면을 그린다', (hash, screenName, title) => {
    goto(hash)
    const { container } = render(<App />)
    const sections = container.querySelectorAll('[data-screen]')
    expect(sections).toHaveLength(1)
    expect(sections[0].getAttribute('data-screen')).toBe(screenName)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(title)
  })

  it('#/persons/:id 는 인물 화면에 id 를 넘긴다', () => {
    goto('#/persons/12')
    const { container } = render(<App />)
    const section = container.querySelector('[data-screen="persons"]')
    expect(section?.getAttribute('data-person-id')).toBe('12')
  })

  it('알 수 없는 해시는 #/chat 으로 보낸다', () => {
    goto('#/nope')
    const { container } = render(<App />)
    expect(container.querySelector('[data-screen="chat"]')).not.toBeNull()
    expect(window.location.hash).toBe('#/chat')
  })

  it('해시가 비어 있어도 #/chat 으로 보낸다', () => {
    goto('/')
    const { container } = render(<App />)
    expect(container.querySelector('[data-screen="chat"]')).not.toBeNull()
    expect(window.location.hash).toBe('#/chat')
  })

  it('parseHash 경계: 숫자가 아닌 id·끝 슬래시·쿼리', () => {
    expect(parseHash('#/persons/abc')).toBeNull()
    expect(parseHash('#/persons/')).toBeNull()
    expect(parseHash('#/chat/extra')).toBeNull()
    expect(parseHash('#/briefings?schedule_id=3')).toEqual({ name: 'briefings' })
    expect(parseHash('#/persons/7')).toEqual({ name: 'persons', personId: 7 })
    expect(parseHash('#/persons')).toEqual({ name: 'persons', personId: null })
  })
})

describe('앱 틀 — 사이드바 (결정 N)', () => {
  it('데스크톱 폭에서는 사이드바가 항상 보이고 메뉴 버튼이 없다', () => {
    goto('#/chat')
    render(<App />)
    const nav = screen.getByRole('navigation', { name: '주 메뉴' })
    const links = Array.from(nav.querySelectorAll('a')).map((a) => [a.textContent, a.getAttribute('href')])
    expect(links).toEqual([
      ['채팅', '#/chat'],
      ['인물', '#/persons'],
      ['브리핑', '#/briefings'],
    ])
    expect(screen.queryByRole('button', { name: '메뉴 열기' })).toBeNull()
    expect(screen.getByTestId('sidebar-persons')).toBeInTheDocument()
  })

  it('지금 화면 항목에 aria-current 가 붙는다', () => {
    goto('#/briefings')
    render(<App />)
    expect(screen.getByRole('link', { name: '브리핑' })).toHaveAttribute('aria-current', 'page')
    expect(screen.getByRole('link', { name: '채팅' })).not.toHaveAttribute('aria-current')
  })

  it('좁은 폭: 기본은 접혀 있고 메뉴 버튼으로 열린다', async () => {
    installFakeMatchMedia(800)
    goto('#/chat')
    render(<App />)
    expect(screen.queryByRole('navigation', { name: '주 메뉴' })).toBeNull()
    await userEvent.click(screen.getByRole('button', { name: '메뉴 열기' }))
    expect(screen.getByRole('navigation', { name: '주 메뉴' })).toBeInTheDocument()
  })

  it('좁은 폭: 항목을 고르면 서랍이 닫히고 그 화면이 보인다', async () => {
    installFakeMatchMedia(800)
    goto('#/chat')
    const { container } = render(<App />)
    await userEvent.click(screen.getByRole('button', { name: '메뉴 열기' }))
    await userEvent.click(screen.getByRole('link', { name: '브리핑' }))
    expect(screen.queryByRole('navigation', { name: '주 메뉴' })).toBeNull()
    await waitFor(() => {
      expect(container.querySelector('[data-screen="briefings"]')).not.toBeNull()
    })
  })

  it('좁은 폭: Esc 와 바깥(배경) 클릭으로도 닫힌다', async () => {
    installFakeMatchMedia(800)
    goto('#/chat')
    render(<App />)
    await userEvent.click(screen.getByRole('button', { name: '메뉴 열기' }))
    await userEvent.keyboard('{Escape}')
    expect(screen.queryByRole('navigation', { name: '주 메뉴' })).toBeNull()

    await userEvent.click(screen.getByRole('button', { name: '메뉴 열기' }))
    // 서랍(shadcn/ui 기성 컴포넌트)의 배경 = data-slot="sheet-overlay"
    await userEvent.click(document.querySelector('[data-slot="sheet-overlay"]')!)
    expect(screen.queryByRole('navigation', { name: '주 메뉴' })).toBeNull()
  })

  it('열림/닫힘은 라우트도 localStorage 도 바꾸지 않는다', async () => {
    installFakeMatchMedia(800)
    goto('#/persons')
    render(<App />)
    await userEvent.click(screen.getByRole('button', { name: '메뉴 열기' }))
    expect(window.location.hash).toBe('#/persons')
    expect(window.localStorage.length).toBe(0)
  })

  it('1024px 경계: 1023 은 서랍형, 1024 는 고정 사이드바', () => {
    installFakeMatchMedia(1023)
    goto('#/chat')
    const first = render(<App />)
    expect(screen.getByRole('button', { name: '메뉴 열기' })).toBeInTheDocument()
    first.unmount()

    installFakeMatchMedia(1024)
    render(<App />)
    expect(screen.queryByRole('button', { name: '메뉴 열기' })).toBeNull()
    expect(screen.getByRole('navigation', { name: '주 메뉴' })).toBeInTheDocument()
  })
})
