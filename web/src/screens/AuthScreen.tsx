// 로그인·가입 화면 (P9b U6, 결정 L — 관문). 한 화면에서 로그인/가입을 전환한다. 새 해시 라우트는 없다.
// 이 파일이 만드는 문장은 아래 AUTH_NOTICE 의 폼 안내·오류 안내와 라벨뿐이다(서버 문자열은 쓰지 않는다).
// 비밀번호는 입력 상태로만 들고 있다가 요청 본문으로만 보낸다 — localStorage·로그·콘솔에 남기지 않는다.
import { useRef, useState, type FormEvent } from 'react'
import { ApiError, checkAvailability, login, signup } from '@/api/client'
import type { AvailabilityStatus } from '@/api/types'
import { useAuth } from '@/auth'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

/** 프론트가 만드는 고정 문구. 규칙 숫자는 P9b 결정 A(아이디)·B(비밀번호)와 같다. */
export const AUTH_NOTICE = {
  titleLogin: '로그인',
  titleSignup: '가입',
  username: '아이디',
  nickname: '닉네임',
  check: '중복 확인',
  checkUsername: '아이디 중복 확인',
  checkNickname: '닉네임 중복 확인',
  usernameAvailable: '사용할 수 있는 아이디예요.',
  nicknameAvailable: '사용할 수 있는 닉네임이에요.',
  nicknameTaken: '이미 쓰고 있는 닉네임이에요.',
  invalidNickname: '닉네임은 2~20자의 한글·영문·숫자·밑줄(_)만 쓸 수 있어요.',
  checkFailed: '확인하지 못했어요. 잠시 후 다시 시도해 주세요.',
  password: '비밀번호',
  confirm: '비밀번호 확인',
  submitLogin: '로그인',
  submitSignup: '가입하기',
  toSignup: '계정 만들기',
  toLogin: '이미 계정이 있어요',
  rules: '아이디는 3~20자의 영문 소문자·숫자·밑줄(_), 닉네임은 2~20자의 한글·영문·숫자·밑줄(_), 비밀번호는 8~128자예요.',
  mismatch: '비밀번호가 서로 달라요.',
  invalidUsername: '아이디는 3~20자의 영문 소문자·숫자·밑줄(_)만 쓸 수 있어요.',
  invalidPassword: '비밀번호는 8~128자여야 해요.',
  usernameTaken: '이미 쓰고 있는 아이디예요.',
  invalidCredentials: '아이디 또는 비밀번호가 맞지 않아요.',
  badOrigin: '요청이 거부됐어요. 이 서비스의 주소로 다시 접속해 주세요.',
  failed: '요청을 처리하지 못했어요. 잠시 후 다시 시도해 주세요.',
} as const

type Mode = 'login' | 'signup'
type CheckField = 'username' | 'nickname'
/** 서버 판정 3가지 + 조회 실패(네트워크·5xx). */
type CheckResult = AvailabilityStatus | 'failed'

/** 오류 코드 → 안내 문구. 코드가 규약 밖이면 일반 실패 문구. */
export function authFailureNotice(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.code === 'invalid_username') return AUTH_NOTICE.invalidUsername
    if (error.code === 'invalid_password') return AUTH_NOTICE.invalidPassword
    if (error.code === 'username_taken') return AUTH_NOTICE.usernameTaken
    if (error.code === 'nickname_taken') return AUTH_NOTICE.nicknameTaken
    if (error.code === 'invalid_nickname') return AUTH_NOTICE.invalidNickname
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
  const [nickname, setNickname] = useState('')
  const [notice, setNotice] = useState<string | null>(null)
  const [pending, setPending] = useState(false)
  // "중복 확인" 결과(칸마다). 결과가 어느 값에 대한 것인지는 지금 칸 값과 비교하지 않고, 값이 바뀌면 지운다(R4-6 ②).
  const [checks, setChecks] = useState<Record<CheckField, CheckResult | null>>({ username: null, nickname: null })
  const [checking, setChecking] = useState<Record<CheckField, boolean>>({ username: false, nickname: false })
  // 늦게 온 응답을 버리기 위한 최신 칸 값과 모드 전환 세대(R4-6 ①·③).
  const latestValue = useRef<Record<CheckField, string>>({ username: '', nickname: '' })
  const generation = useRef(0)

  const isSignup = mode === 'signup'

  function switchMode() {
    setMode(isSignup ? 'login' : 'signup')
    setPassword('')
    setConfirm('')
    setNickname('')
    latestValue.current.nickname = ''
    generation.current++
    setChecks({ username: null, nickname: null })
    setChecking({ username: false, nickname: false })
    setNotice(null)
  }

  function onChangeField(field: CheckField, value: string) {
    latestValue.current[field] = value
    setChecks((prev) => ({ ...prev, [field]: null }))
    if (field === 'username') setUsername(value)
    else setNickname(value)
  }

  async function onCheck(field: CheckField) {
    const requested = field === 'username' ? username : nickname
    const mine = generation.current
    setChecking((prev) => ({ ...prev, [field]: true }))
    let result: CheckResult
    try {
      const out = await checkAvailability({ [field]: requested })
      result = out[field] ?? 'failed'
    } catch {
      result = 'failed'
    }
    if (mine !== generation.current) return // 가입↔로그인 전환 — 이미 지운 상태
    setChecking((prev) => ({ ...prev, [field]: false }))
    // 응답이 돌아왔을 때 칸 값이 요청 때와 다르면 그 응답은 버린다.
    if (latestValue.current[field] !== requested) return
    setChecks((prev) => ({ ...prev, [field]: result }))
  }

  function checkNotice(field: CheckField): string | null {
    const result = checks[field]
    if (result === null) return null
    if (result === 'failed') return AUTH_NOTICE.checkFailed
    if (field === 'username') {
      return result === 'available' ? AUTH_NOTICE.usernameAvailable : result === 'taken' ? AUTH_NOTICE.usernameTaken : AUTH_NOTICE.invalidUsername
    }
    return result === 'available' ? AUTH_NOTICE.nicknameAvailable : result === 'taken' ? AUTH_NOTICE.nicknameTaken : AUTH_NOTICE.invalidNickname
  }

  /** 칸 아래의 "중복 확인" 버튼과 결과 한 줄. 라벨 밖에 둔다(라벨 텍스트가 바뀌면 getByLabelText 가 깨진다). */
  function renderCheck(field: CheckField) {
    const value = field === 'username' ? username : nickname
    const text = checkNotice(field)
    return (
      <div className="-mt-2 flex flex-col gap-1">
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="self-start"
          aria-label={field === 'username' ? AUTH_NOTICE.checkUsername : AUTH_NOTICE.checkNickname}
          disabled={value.trim() === '' || checking[field]}
          onClick={() => void onCheck(field)}
        >
          {AUTH_NOTICE.check}
        </Button>
        {text && (
          <p role="status" data-testid={`${field}-check`} className="text-sm text-muted-foreground">
            {text}
          </p>
        )}
      </div>
    )
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
      // 가입 본문 = {username, nickname, password}(확인 칸 제외, 값은 입력 그대로 — 정규화는 서버). 중복 확인을 하지 않아도 막지 않는다(결정 AA).
      const me = await (isSignup ? signup({ username, nickname, password }) : login({ username, password }))
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
              onChange={(e) => onChangeField('username', e.target.value)}
              className={INPUT_CLASS}
            />
          </label>
          {isSignup && renderCheck('username')}
          {isSignup && (
            <label className="flex flex-col gap-1.5 text-sm">
              {AUTH_NOTICE.nickname}
              <input
                type="text"
                name="nickname"
                autoComplete="nickname"
                required
                value={nickname}
                onChange={(e) => onChangeField('nickname', e.target.value)}
                className={INPUT_CLASS}
              />
            </label>
          )}
          {isSignup && renderCheck('nickname')}
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
