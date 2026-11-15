// 로그인 상태 (P9b U6, 결정 L — 관문 방식). 해시 라우트를 더하지 않고, `GET /auth/me` 결과로 화면을 가른다.
// 200 → 지금의 앱 틀(채팅·인물·브리핑), 401 → 로그인·가입 화면. 로그인 뒤에 어떤 요청이든 401 을 받으면
// (쿠키 만료·삭제) 같은 관문으로 돌아온다. 비밀번호는 이 파일을 지나가지 않는다 — 화면 컴포넌트의 입력 상태뿐이다.
import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from 'react'
import { ApiError, getMe, logout, onUnauthorized } from '@/api/client'
import type { MeOut } from '@/api/types'
import { getCurrentPushEndpoint } from '@/push'
import { clearLegacySessionId } from '@/session'

export type AuthState =
  | { status: 'loading' }
  | { status: 'anonymous' }
  /** `/auth/me` 가 401 도 200 도 아니다(서버 연결 실패·5xx) — 로그인 화면을 보이지 않고 다시 시도하게 한다. */
  | { status: 'error' }
  | { status: 'user'; username: string }

export interface AuthApi {
  state: AuthState
  /** 로그인·가입이 성공했다 — 관문을 연다. 옛 localStorage 세션 키도 이때 한 번 지운다. */
  signedIn: (me: MeOut) => void
  /** 로그아웃. 푸시 구독이 있으면 endpoint 를 함께 보낸다. 서버가 401 이어도 "이미 로그아웃됨" 으로 관문. 그 밖의 실패는 던진다. */
  signOut: () => Promise<void>
  /** `error` 상태에서 `/auth/me` 를 다시 부른다. */
  retry: () => void
}

const AuthContext = createContext<AuthApi | null>(null)

export function useAuth(): AuthApi {
  const api = useContext(AuthContext)
  if (!api) throw new Error('AuthProvider 안에서만 쓸 수 있다')
  return api
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ status: 'loading' })
  // 먼저 보낸 요청의 늦은 응답이 나중 상태를 덮지 않게 한다.
  const latest = useRef(0)

  const fetchMe = useCallback(() => {
    const mine = ++latest.current
    getMe().then(
      (me) => {
        if (mine === latest.current) setState({ status: 'user', username: me.username })
      },
      (error: unknown) => {
        if (mine !== latest.current) return
        setState(error instanceof ApiError && error.status === 401 ? { status: 'anonymous' } : { status: 'error' })
      },
    )
  }, [])

  useEffect(() => {
    fetchMe()
  }, [fetchMe])

  // 로그인한 뒤 어떤 호출이든 401 을 받으면 관문으로.
  useEffect(
    () =>
      onUnauthorized(() => {
        latest.current++ // 진행 중이던 `/auth/me` 응답이 이 상태를 덮지 않게
        setState({ status: 'anonymous' })
      }),
    [],
  )

  const signedIn = useCallback((me: MeOut) => {
    clearLegacySessionId()
    latest.current++
    setState({ status: 'user', username: me.username })
  }, [])

  const signOut = useCallback(async () => {
    const endpoint = await getCurrentPushEndpoint()
    await logout(endpoint)
    latest.current++
    setState({ status: 'anonymous' })
  }, [])

  const retry = useCallback(() => {
    setState({ status: 'loading' })
    fetchMe()
  }, [fetchMe])

  return <AuthContext.Provider value={{ state, signedIn, signOut, retry }}>{children}</AuthContext.Provider>
}
