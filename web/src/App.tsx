import { AuthProvider, useAuth } from '@/auth'
import AppShell from '@/components/AppShell'
import { Button } from '@/components/ui/button'
import { Toaster } from '@/components/ui/sonner'
import { useRoute } from '@/routes'
import AuthScreen from '@/screens/AuthScreen'
import BriefingScreen from '@/screens/BriefingScreen'
import ChatScreen from '@/screens/ChatScreen'
import PersonCardScreen from '@/screens/PersonCardScreen'

/** 프론트가 만드는 고정 문구(오류 안내). 서버 문장이 아니다. */
export const GATE_NOTICE = {
  unreachable: '서버에 연결하지 못했어요.',
  retry: '다시 시도',
} as const

// 핵심 화면은 채팅·인물 카드·브리핑이다. 화면 수는 고정하지 않는다(원칙5 개정, CR-006):
// 로그인·가입 화면(AuthScreen)은 P9b U6 이 근거와 함께 더한 화면으로, 해시 라우트가 아니라 로그인 상태가 가르는 관문이다.
// 채팅방 목록은 만들지 않는다(원칙7).
function SignedInApp() {
  const route = useRoute()
  return (
    <AppShell route={route}>
      {route.name === 'chat' && <ChatScreen />}
      {route.name === 'persons' && <PersonCardScreen personId={route.personId} />}
      {route.name === 'briefings' && <BriefingScreen />}
      <Toaster />
    </AppShell>
  )
}

function Gate() {
  const { state, retry } = useAuth()
  if (state.status === 'loading') return <div aria-busy="true" className="min-h-dvh bg-background" />
  if (state.status === 'error') {
    return (
      <main className="flex min-h-dvh flex-col items-center justify-center gap-4 bg-background p-6 text-foreground">
        <p role="alert">{GATE_NOTICE.unreachable}</p>
        <Button type="button" variant="outline" onClick={retry}>
          {GATE_NOTICE.retry}
        </Button>
      </main>
    )
  }
  if (state.status === 'anonymous') return <AuthScreen />
  return <SignedInApp />
}

export default function App() {
  return (
    <AuthProvider>
      <Gate />
    </AuthProvider>
  )
}
