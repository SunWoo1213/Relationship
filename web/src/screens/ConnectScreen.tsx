// "AI 연결" 화면 (P9b U13, CR-008 · D19) — MCP 연결 토큰을 만들고(원문은 발급 응답에서 한 번만), 복사하고, 폐기한다.
// 새 화면의 근거(원칙5): 토큰 43자·명령 약 150자를 복사할 자리가 사이드바 256px 에는 없다.
// 토큰은 이 컴포넌트 state 에만 둔다 — localStorage·sessionStorage·URL·콘솔·모듈 전역에 남기지 않는다(결정 AZ).
// 이 파일이 만드는 문장은 아래 CONNECT_NOTICE 의 고정 안내뿐이다(서버 문장 없음).
import { useEffect, useRef, useState } from 'react'
import { createMcpToken, deleteMcpToken, getMcpToken } from '@/api/client'
import type { McpTokenStatusOut } from '@/api/types'
import { Button } from '@/components/ui/button'

/** 프론트가 만드는 고정 문구 (01-plan "AI 연결 화면 고정 문구" — 글자 그대로). */
export const CONNECT_NOTICE = {
  entry: 'AI 연결',
  title: 'AI 연결',
  intro:
    'Claude Code 같은 AI 도구에서 내 관계 메모리를 읽기 전용으로 조회할 수 있어요. 인물 목록·인물 카드·저장된 브리핑만 열리고, 기록·수정·원문 대화는 열리지 않아요.',
  privacy: '조회한 내용은 연결한 AI 도구의 회사로 전송돼요.',
  scope: 'Claude Code 처럼 연결 토큰을 헤더로 넣는 도구에만 연결돼요. Claude 앱·ChatGPT 앱은 아직 연결할 수 없어요.',
  loading: '불러오는 중…',
  statusNone: '연결 토큰이 없어요.',
  statusActive: '연결 토큰이 있어요.',
  statusExpired: '연결 토큰이 만료됐어요. 새로 만들어 주세요.',
  expiresAt: '만료',
  lastUsedAt: '마지막 사용',
  neverUsed: '아직 쓰지 않았어요.',
  validity: '토큰은 만든 뒤 7일 동안 쓸 수 있어요.',
  create: '연결 토큰 만들기',
  recreate: '새 토큰 만들기',
  recreateWarn: '새로 만들면 지금 토큰은 바로 쓸 수 없게 돼요.',
  onceNotice: '이 토큰은 지금 한 번만 보여요. 화면을 벗어나면 다시 볼 수 없으니 바로 복사해 두세요.',
  tokenLabel: '연결 토큰',
  commandLabel: 'Claude Code 에 붙이는 명령 (내 컴퓨터 터미널에서 실행)',
  copy: '복사',
  copyToken: '토큰 복사',
  copyCommand: '명령 복사',
  copied: '복사했어요.',
  copyFailed: '복사하지 못했어요. 직접 선택해 복사해 주세요.',
  revoke: '토큰 폐기',
  revoked: '토큰을 폐기했어요. 이 토큰으로 연결한 도구는 더 이상 조회할 수 없어요.',
  failed: '처리하지 못했어요. 잠시 후 다시 시도해 주세요.',
} as const

/** 결정 AY — 호스트를 코드에 박지 않고 지금 열린 주소에서 가져온다. */
export function mcpCommand(token: string): string {
  return `claude mcp add --transport http relmemo ${window.location.origin}/mcp --header "Authorization: Bearer ${token}"`
}

/** 이 화면 안에서만 쓰는 시각 표기. */
function fmt(iso: string): string {
  return new Date(iso).toLocaleString('ko-KR')
}

const NONE: McpTokenStatusOut = { active: false, created_at: null, expires_at: null, last_used_at: null }

export default function ConnectScreen() {
  const [status, setStatus] = useState<McpTokenStatusOut | null>(null) // null = 불러오는 중
  const [token, setToken] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const busyRef = useRef(false)
  const [note, setNote] = useState<string | null>(null) // copied · copyFailed · revoked
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    let cancelled = false
    getMcpToken().then(
      (s) => {
        if (!cancelled) setStatus(s)
      },
      () => {
        if (!cancelled) {
          setStatus(NONE)
          setFailed(true)
        }
      },
    )
    return () => {
      cancelled = true
    }
  }, [])

  async function run(action: () => Promise<void>) {
    if (busyRef.current) return
    busyRef.current = true
    setBusy(true)
    setFailed(false)
    setNote(null)
    try {
      await action()
    } catch {
      setFailed(true)
    } finally {
      busyRef.current = false
      setBusy(false)
    }
  }

  const onCreate = () =>
    run(async () => {
      const out = await createMcpToken()
      setToken(out.token)
      setStatus({ active: true, created_at: out.created_at, expires_at: out.expires_at, last_used_at: null })
    })

  const onRevoke = () =>
    run(async () => {
      await deleteMcpToken()
      setToken(null)
      setStatus(NONE)
      setNote(CONNECT_NOTICE.revoked)
    })

  async function copy(text: string) {
    try {
      await navigator.clipboard.writeText(text)
      setNote(CONNECT_NOTICE.copied)
    } catch {
      setNote(CONNECT_NOTICE.copyFailed)
    }
  }

  return (
    <section data-screen="connect" className="mx-auto flex w-full max-w-2xl flex-col gap-4 p-4 text-sm">
      <h1 className="text-lg font-semibold">{CONNECT_NOTICE.title}</h1>
      <p>{CONNECT_NOTICE.intro}</p>
      <p>{CONNECT_NOTICE.privacy}</p>
      <p>{CONNECT_NOTICE.scope}</p>
      <p>{CONNECT_NOTICE.validity}</p>

      {status === null ? (
        <p>{CONNECT_NOTICE.loading}</p>
      ) : (
        <>
          <div data-testid="mcp-status" className="flex flex-col gap-1">
            {status.active ? (
              <>
                <span>{CONNECT_NOTICE.statusActive}</span>
                {status.expires_at && (
                  <span>
                    {CONNECT_NOTICE.expiresAt}: {fmt(status.expires_at)}
                  </span>
                )}
                <span>
                  {CONNECT_NOTICE.lastUsedAt}: {status.last_used_at ? fmt(status.last_used_at) : CONNECT_NOTICE.neverUsed}
                </span>
              </>
            ) : status.expires_at ? (
              <span>{CONNECT_NOTICE.statusExpired}</span>
            ) : (
              <span>{CONNECT_NOTICE.statusNone}</span>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Button type="button" onClick={() => void onCreate()} disabled={busy}>
              {status.active ? CONNECT_NOTICE.recreate : CONNECT_NOTICE.create}
            </Button>
            {status.active && <span>{CONNECT_NOTICE.recreateWarn}</span>}
            {status.active && (
              <Button type="button" variant="outline" onClick={() => void onRevoke()} disabled={busy}>
                {CONNECT_NOTICE.revoke}
              </Button>
            )}
          </div>

          {token !== null && (
            <div className="flex flex-col gap-2">
              <p>{CONNECT_NOTICE.onceNotice}</p>
              <span>{CONNECT_NOTICE.tokenLabel}</span>
              <code data-testid="mcp-token" className="break-all rounded-md bg-muted p-2">
                {token}
              </code>
              <div>
                <Button type="button" variant="outline" aria-label={CONNECT_NOTICE.copyToken} onClick={() => void copy(token)}>
                  {CONNECT_NOTICE.copy}
                </Button>
              </div>
              <span>{CONNECT_NOTICE.commandLabel}</span>
              <code data-testid="mcp-command" className="break-all rounded-md bg-muted p-2">
                {mcpCommand(token)}
              </code>
              <div>
                <Button type="button" variant="outline" aria-label={CONNECT_NOTICE.copyCommand} onClick={() => void copy(mcpCommand(token))}>
                  {CONNECT_NOTICE.copy}
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      {note !== null && <p role="status">{note}</p>}
      {failed && <p role="alert">{CONNECT_NOTICE.failed}</p>}
    </section>
  )
}
