// 로그인·가입 화면 (P9b U6, 결정 L — 관문). 한 화면에서 로그인/가입을 전환한다. 새 해시 라우트는 없다.
// 이 파일이 만드는 문장은 아래 AUTH_NOTICE 의 폼 안내·오류 안내와 라벨뿐이다(서버 문자열은 쓰지 않는다).
// 비밀번호는 입력 상태로만 들고 있다가 요청 본문으로만 보낸다 — localStorage·로그·콘솔에 남기지 않는다.
import { useState, type FormEvent } from 'react'
import { ApiError, login, signup } from '@/api/client'
import { useAuth } from '@/auth'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

/** 프론트가 만드는 고정 문구. 규칙 숫자는 P9b 결정 A(아이디)·B(비밀번호)와 같다. */
export const AUTH_NOTICE = {
  titleLogin: '로그인',
  titleSignup: '가입',
  username: '아이디',
  password: '비밀번호',
  confirm: '비밀번호 확인',
  submitLogin: '로그인',
  submitSignup: '가입하기',
  toSignup: '계정 만들기',
  toLogin: '이미 계정이 있어요',
  rules: '아이디는 3~20자의 영문 소문자·숫자·밑줄(_), 비밀번호는 8~128자예요.',
  mismatch: '비밀번호가 서로 달라요.',
  invalidUsername: '아이디는 3~20자의 영문 소문자·숫자·밑줄(_)만 쓸 수 있어요.',
  invalidPassword: '비밀번호는 8~128자여야 해요.',
  usernameTaken: '이미 쓰고 있는 아이디예요.',
  invalidCredentials: '아이디 또는 비밀번호가 맞지 않아요.',
  badOrigin: '요청이 거부됐어요. 이 서비스의 주소로 다시 접속해 주세요.',
  failed: '요청을 처리하지 못했어요. 잠시 후 다시 시도해 주세요.',
} as const

type Mode = 'login' | 'signup'

/** 오류 코드 → 안내 문구. 코드가 규약 밖이면 일반 실패 문구. */
export function authFailureNotice(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.code === 'invalid_username') return AUTH_NOTICE.invalidUsername
    if (error.code === 'invalid_password') return AUTH_NOTICE.invalidPassword
    if (error.code === 'username_taken') return AUTH_NOTICE.usernameTaken
    if (error.code === 'invalid_credentials') return AUTH_NOTICE.invalidCredentials
    if (error.code === 'bad_origin') return AUTH_NOTICE.badOrigin
  }
  return AUTH_NOTICE.failed
}

const INPUT_CLASS = cn(
  'h-9 w-full rounded-md border bg-background px-3 text-sm outline-none',
  'focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50',
)

export default function AuthScreen() {
  const { signedIn } = useAuth()
  const [mode, setMode] = useState<Mode>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [notice, setNotice] = useState<string | null>(null)
  const [pending, setPending] = useState(false)

  const isSignup = mode === 'signup'

  function switchMode() {
    setMode(isSignup ? 'login' : 'signup')
    setPassword('')
    setConfirm('')
    setNotice(null)
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (pending) return
    // 확인 칸이 다르면 요청을 보내지 않는다.
    if (isSignup && password !== confirm) {
      setNotice(AUTH_NOTICE.mismatch)
      return
    }
    setNotice(null)
    setPending(true)
    try {
      const me = await (isSignup ? signup : login)({ username, password })
      signedIn(me)
    } catch (error) {
      setNotice(authFailureNotice(error))
      setPending(false)
    }
  }

  return (
    <main className="flex min-h-dvh items-center justify-center bg-background p-6 text-foreground">
      <section aria-labelledby="auth-title" data-screen="auth" className="w-full max-w-sm">
        <h1 id="auth-title" className="mb-6 text-2xl font-semibold">
          {isSignup ? AUTH_NOTICE.titleSignup : AUTH_NOTICE.titleLogin}
        </h1>
        <form onSubmit={(e) => void onSubmit(e)} className="flex flex-col gap-4">
          <label className="flex flex-col gap-1.5 text-sm">
            {AUTH_NOTICE.username}
            <input
              type="text"
              name="username"
              autoComplete="username"
              autoCapitalize="none"
              autoCorrect="off"
              spellCheck={false}
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={INPUT_CLASS}
            />
          </label>
          <label className="flex flex-col gap-1.5 text-sm">
            {AUTH_NOTICE.password}
            <input
              type="password"
              name="password"
              autoComplete={isSignup ? 'new-password' : 'current-password'}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={INPUT_CLASS}
            />
          </label>
          {isSignup && (
            <label className="flex flex-col gap-1.5 text-sm">
              {AUTH_NOTICE.confirm}
              <input
                type="password"
                name="password_confirm"
                autoComplete="new-password"
                required
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                className={INPUT_CLASS}
              />
            </label>
          )}
          {isSignup && <p className="text-sm text-muted-foreground">{AUTH_NOTICE.rules}</p>}
          {notice && (
            <p role="alert" className="text-sm text-destructive">
              {notice}
            </p>
          )}
          <Button type="submit" disabled={pending}>
            {isSignup ? AUTH_NOTICE.submitSignup : AUTH_NOTICE.submitLogin}
          </Button>
          <Button type="button" variant="ghost" onClick={switchMode}>
            {isSignup ? AUTH_NOTICE.toLogin : AUTH_NOTICE.toSignup}
          </Button>
        </form>
      </section>
    </main>
  )
}
