import AppShell from '@/components/AppShell'
import { Toaster } from '@/components/ui/sonner'
import { useRoute } from '@/routes'
import BriefingScreen from '@/screens/BriefingScreen'
import ChatScreen from '@/screens/ChatScreen'
import PersonCardScreen from '@/screens/PersonCardScreen'

// 화면은 3개로 고정 (원칙5). 새 화면·새 라우트를 더하지 않는다.
export default function App() {
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
