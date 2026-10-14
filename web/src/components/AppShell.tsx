import { useEffect, useState, type ReactNode } from 'react'
import { MenuIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import PersonList from '@/components/PersonList'
import { PersonsProvider } from '@/components/PersonsProvider'
import { useMediaQuery } from '@/hooks/useMediaQuery'
import { briefingHref, HREF, type Route } from '@/routes'

/** 결정 N: 데스크톱은 이 너비부터 사이드바가 항상 보인다. */
export const DESKTOP_QUERY = '(min-width: 1024px)'

const NAV_ITEMS: { key: Route['name']; label: string; href: string }[] = [
  { key: 'chat', label: '채팅', href: HREF.chat },
  { key: 'persons', label: '인물', href: HREF.persons },
  { key: 'briefings', label: '브리핑', href: HREF.briefings },
]

function SidebarContent({ route, onNavigate }: { route: Route; onNavigate: () => void }) {
  return (
    <nav aria-label="주 메뉴" className="flex h-full flex-col gap-4 p-4">
      <ul className="flex flex-col gap-1">
        {NAV_ITEMS.map((item) => (
          <li key={item.key}>
            <a
              href={item.href}
              onClick={onNavigate}
              aria-current={route.name === item.key ? 'page' : undefined}
              className="block rounded-md px-3 py-2 text-body hover:bg-sidebar-accent aria-[current=page]:bg-sidebar-accent aria-[current=page]:font-medium"
            >
              {item.label}
            </a>
          </li>
        ))}
      </ul>
      {/* 인물 목록 — `#/persons` 본문과 같은 컴포넌트 (새 API·새 라우트 없음). */}
      <div aria-label="인물 목록" data-testid="sidebar-persons" className="min-h-0 flex-1 overflow-y-auto">
        <PersonList onNavigate={onNavigate} />
      </div>
    </nav>
  )
}

/** 프론트가 만든 고정 문구(서버 문장이 아니다). 알림 title·body 는 페이지로 오지 않는다. */
export const BANNER_NOTICE = {
  text: '새 브리핑 알림이 도착했어요.',
  open: '브리핑 보기',
  close: '닫기',
} as const

/** 서비스 워커가 보낸 메시지 → 일정 번호. 모양이 다르면 undefined. */
function readWorkerMessage(data: unknown): { type: 'briefing' | 'open-briefing'; scheduleId: number | null } | undefined {
  if (typeof data !== 'object' || data === null) return undefined
  const { type, schedule_id } = data as { type?: unknown; schedule_id?: unknown }
  if (type !== 'briefing' && type !== 'open-briefing') return undefined
  const scheduleId = typeof schedule_id === 'number' && Number.isInteger(schedule_id) && schedule_id > 0 ? schedule_id : null
  return { type, scheduleId }
}

/**
 * 인앱 배너 (결정 H) — 서비스 워커가 `{type:"briefing", schedule_id}` 를 보내면 현재 화면 위에 한 줄.
 * 누르면 `#/briefings?schedule_id=N`. 알림을 눌러 온 `open-briefing` 은 배너 없이 바로 그 주소로 간다.
 * 새 화면이 아니다.
 */
function WorkerMessages() {
  const [banner, setBanner] = useState<{ scheduleId: number | null } | null>(null)

  useEffect(() => {
    const container = typeof navigator === 'undefined' ? undefined : navigator.serviceWorker
    if (!container) return
    const onMessage = (event: MessageEvent) => {
      const message = readWorkerMessage(event.data)
      if (!message) return
      if (message.type === 'open-briefing') {
        setBanner(null)
        window.location.hash = briefingHref(message.scheduleId)
        return
      }
      setBanner({ scheduleId: message.scheduleId })
    }
    container.addEventListener('message', onMessage)
    return () => container.removeEventListener('message', onMessage)
  }, [])

  if (!banner) return null
  return (
    <div
      role="status"
      data-testid="push-banner"
      className="mb-4 flex items-center justify-between gap-3 rounded-md border bg-accent px-3 py-2 text-sm"
    >
      <span>{BANNER_NOTICE.text}</span>
      <span className="flex items-center gap-3">
        <a href={briefingHref(banner.scheduleId)} onClick={() => setBanner(null)} className="font-medium underline">
          {BANNER_NOTICE.open}
        </a>
        <button type="button" onClick={() => setBanner(null)} className="text-muted-foreground">
          {BANNER_NOTICE.close}
        </button>
      </span>
    </div>
  )
}

/**
 * 앱 틀 (결정 N): 모든 폭에서 왼쪽 사이드바.
 * - 데스크톱(≥ 1024px): 항상 보임.
 * - 그 아래: 왼쪽 위 메뉴 버튼으로 여닫는 서랍 — shadcn/ui Sheet(Radix Dialog 기반, side="left").
 *   항목을 고르면·Esc·배경 클릭이면 닫힌다.
 * 열림/닫힘은 이 컴포넌트의 상태일 뿐 라우트도 localStorage 도 아니다. 하단 탭바 없음.
 */
export default function AppShell({ route, children }: { route: Route; children: ReactNode }) {
  const isDesktop = useMediaQuery(DESKTOP_QUERY)
  const [open, setOpen] = useState(false)

  return (
    <PersonsProvider>
    <div className="flex h-dvh bg-background text-foreground">
      {isDesktop ? (
        <aside className="w-64 shrink-0 border-r border-sidebar-border bg-sidebar text-sidebar-foreground">
          <SidebarContent route={route} onNavigate={() => {}} />
        </aside>
      ) : (
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" aria-label="메뉴 열기" className="fixed left-2 top-2 z-30">
              <MenuIcon />
            </Button>
          </SheetTrigger>
          <SheetContent
            side="left"
            showCloseButton={false}
            aria-describedby={undefined}
            className="bg-sidebar p-0 text-sidebar-foreground data-[side=left]:w-64 data-[side=left]:sm:max-w-none"
          >
            <SheetTitle className="sr-only">사이드바</SheetTitle>
            <SidebarContent route={route} onNavigate={() => setOpen(false)} />
          </SheetContent>
        </Sheet>
      )}
      <main className="min-w-0 flex-1 overflow-y-auto p-6 pt-14 lg:pt-6">
        <WorkerMessages />
        {children}
      </main>
    </div>
    </PersonsProvider>
  )
}
