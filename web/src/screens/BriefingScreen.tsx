// 브리핑 화면 (U7, 결정 G·H·K) — 저장된 브리핑(`GET /briefings`)을 서버 순서 그대로 보여 주고, 일정마다 "지금 브리핑" 을 둔다.
// 항목 모양은 기획서 부록 A ③: 머리줄(일정 시각 · 이름 · 일정 제목) → 패턴 문장·요약 줄 → 💡 제안.
// 서버 문자열(sentence · text · title · display_name)은 고치지 않고 그대로 보여 준다 (원칙7). `basis` 는 화면에 쓰지 않는다.
// 이 파일이 만드는 문장은 아래 NOTICE 의 오류·빈 상태 안내와 버튼 글자·구획 제목뿐이다.
// "알림 받기"(U8, 결정 H) 는 PushSubscribe — 구독 절차는 `@/push` 에 있다.
import { useCallback, useEffect, useRef, useState } from 'react'
import { ApiError, getBriefings, postBriefingRun } from '@/api/client'
import type { BriefingRecordOut } from '@/api/types'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { formatDateTime } from '@/lib/format'
import { cn } from '@/lib/utils'
import { getPushStatus, subscribeToPush, type SubscribeOutcome } from '@/push'
import { useScheduleIdParam } from '@/routes'

/** 프론트가 만드는 고정 안내 문장(빈 상태·오류)과 버튼 글자. 서버 메시지가 아니다. */
export const BRIEFING_NOTICE = {
  empty: '아직 만들어진 브리핑이 없어요.',
  listFailed: '브리핑을 불러오지 못했어요.',
  scheduleMissing: '그 일정의 브리핑이 아직 없어요.',
  runNow: '지금 브리핑',
  running: '브리핑 만드는 중',
  runLocked: '잠시 뒤 다시 시도해 주세요.',
  runFailed: '브리핑을 만들지 못했어요. 잠시 후 다시 시도해 주세요.',
  suggestionTitle: '💡 제안',
  scheduleFailed: '그 일정의 브리핑을 불러오지 못했어요.',
  subscribe: '알림 받기',
  subscribing: '알림 켜는 중',
  subscribed: '알림 켜짐',
  pushDenied: '알림 권한이 허용되지 않았어요.',
  pushNotConfigured: '이 서버는 아직 알림을 준비하지 않았어요.',
  pushUnsupported: '이 브라우저는 알림을 지원하지 않아요.',
  pushFailed: '알림을 켜지 못했어요. 잠시 후 다시 시도해 주세요.',
} as const

const PUSH_NOTE: Record<Exclude<SubscribeOutcome, 'subscribed' | 'already'>, string> = {
  denied: BRIEFING_NOTICE.pushDenied,
  not_configured: BRIEFING_NOTICE.pushNotConfigured,
  unsupported: BRIEFING_NOTICE.pushUnsupported,
  failed: BRIEFING_NOTICE.pushFailed,
}

type PushUi = 'idle' | 'running' | 'on'

/** "알림 받기" (결정 H) — 상태 셋: 미구독 · 진행 중 · 켜짐(비활성). 구독 해제는 없다. */
function PushSubscribe() {
  const [state, setState] = useState<PushUi>('idle')
  const [note, setNote] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    void getPushStatus().then((status) => {
      if (!cancelled && status === 'subscribed') setState('on')
    })
    return () => {
      cancelled = true
    }
  }, [])

  const onClick = async () => {
    setState('running')
    setNote(null)
    const outcome = await subscribeToPush()
    if (outcome === 'subscribed' || outcome === 'already') {
      setState('on')
      return
    }
    setState('idle')
    setNote(PUSH_NOTE[outcome])
  }

  return (
    <div data-slot="push-subscribe" className="flex flex-col items-end gap-1">
      <Button type="button" variant="outline" size="sm" disabled={state !== 'idle'} onClick={() => void onClick()}>
        {state === 'on' ? BRIEFING_NOTICE.subscribed : state === 'running' ? BRIEFING_NOTICE.subscribing : BRIEFING_NOTICE.subscribe}
      </Button>
      {note !== null && (
        <p role="status" className="text-sm text-muted-foreground" data-testid="push-note">
          {note}
        </p>
      )}
    </div>
  )
}

type RunState = 'running' | 'locked' | 'failed'
type Lookup = 'none' | 'missing' | 'failed'

function BriefingItem({
  record,
  highlighted,
  runState,
  onRun,
}: {
  record: BriefingRecordOut
  highlighted: boolean
  runState: RunState | undefined
  onRun: (scheduleId: number) => void
}) {
  const { schedule, person } = record
  return (
    <li data-testid={`briefing-${schedule.id}`} data-highlight={highlighted ? 'true' : undefined}>
      <Card className={cn('gap-3 p-4', highlighted && 'bg-accent ring-2 ring-primary')}>
        <h2 className="text-body font-medium" data-field="headline">
          <span aria-hidden="true">📌 </span>
          {formatDateTime(schedule.scheduled_at)} · {person.display_name} · {schedule.title}
        </h2>
        {(record.pattern_sentences.length > 0 || record.lines.length > 0) && (
          <ul className="flex flex-col gap-1" data-field="lines">
            {record.pattern_sentences.map((p) => (
              <li key={p.key} className="flex gap-2">
                <span aria-hidden="true">·</span>
                <span data-field="pattern">{p.sentence}</span>
              </li>
            ))}
            {record.lines.map((l, i) => (
              <li key={i} className="flex gap-2">
                <span aria-hidden="true">·</span>
                <span data-field="line">{l.text}</span>
              </li>
            ))}
          </ul>
        )}
        {record.suggestion && (
          <div data-field="suggestion-block">
            <h3 className="text-sm font-medium">{BRIEFING_NOTICE.suggestionTitle}</h3>
            <p data-field="suggestion">{record.suggestion.text}</p>
          </div>
        )}
        <div className="flex items-center gap-3">
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={runState === 'running'}
            onClick={() => onRun(schedule.id)}
          >
            {runState === 'running' ? BRIEFING_NOTICE.running : BRIEFING_NOTICE.runNow}
          </Button>
          {runState === 'locked' && (
            <p role="status" className="text-sm text-muted-foreground">
              {BRIEFING_NOTICE.runLocked}
            </p>
          )}
          {runState === 'failed' && (
            <p role="alert" className="text-sm text-destructive">
              {BRIEFING_NOTICE.runFailed}
            </p>
          )}
        </div>
      </Card>
    </li>
  )
}

export default function BriefingScreen() {
  const scheduleId = useScheduleIdParam()
  const [list, setList] = useState<BriefingRecordOut[] | null>(null)
  const [extra, setExtra] = useState<BriefingRecordOut | null>(null) // 7일 창 밖 일정의 단건
  const [lookup, setLookup] = useState<Lookup>('none')
  const [failed, setFailed] = useState(false)
  const [runStates, setRunStates] = useState<Record<number, RunState>>({})
  const latest = useRef(0)

  /** 목록 1회 + (쿼리의 일정이 목록에 없으면) 단건 1회. 응답을 직접 끼워 넣지 않고 항상 이 경로로 다시 읽는다. */
  const load = useCallback(async () => {
    const mine = ++latest.current
    const stale = () => mine !== latest.current
    let records: BriefingRecordOut[]
    try {
      records = await getBriefings()
    } catch {
      if (!stale()) setFailed(true)
      return
    }
    if (stale()) return
    setFailed(false)
    setList(records)
    if (scheduleId === null || records.some((r) => r.schedule.id === scheduleId)) {
      setExtra(null)
      setLookup('none')
      return
    }
    try {
      const one = await getBriefings(scheduleId)
      if (stale()) return
      setExtra(one[0] ?? null)
      setLookup(one.length === 0 ? 'missing' : 'none')
    } catch (error) {
      if (stale()) return
      setExtra(null)
      setLookup(error instanceof ApiError && error.status === 404 ? 'missing' : 'failed')
    }
  }, [scheduleId])

  // R-U7-1: `run` 이 클릭 시점의 옛 `load` 가 아니라 항상 최신 `load`(최신 scheduleId)를 부르게 한다.
  const loadRef = useRef(load)
  useEffect(() => {
    loadRef.current = load
    void load()
    return () => {
      latest.current++ // 언마운트·쿼리 변경 뒤 늦은 응답 무시
    }
  }, [load])

  const run = useCallback(
    async (id: number) => {
      setRunStates((s) => ({ ...s, [id]: 'running' }))
      try {
        await postBriefingRun(id)
      } catch (error) {
        // 404 = 잠금 중(결정 K) — 안내만, 자동 재시도 없음. 그 밖은 한 줄 실패.
        const state: RunState = error instanceof ApiError && error.status === 404 ? 'locked' : 'failed'
        setRunStates((s) => ({ ...s, [id]: state }))
        return
      }
      await loadRef.current()
      setRunStates((s) => {
        const { [id]: _done, ...rest } = s
        return rest
      })
    },
    [],
  )

  // 쿼리의 일정이 목록에 있으면 그것을 맨 위로(나머지는 서버 순서 그대로), 없으면 단건을 맨 위에 붙인다.
  const inList = scheduleId !== null && list !== null && list.some((r) => r.schedule.id === scheduleId)
  const items: { record: BriefingRecordOut; highlighted: boolean }[] = []
  if (list !== null) {
    if (inList) {
      const top = list.find((r) => r.schedule.id === scheduleId)!
      items.push({ record: top, highlighted: true })
      list.forEach((r) => r !== top && items.push({ record: r, highlighted: false }))
    } else {
      if (extra) items.push({ record: extra, highlighted: true })
      list.forEach((r) => items.push({ record: r, highlighted: false }))
    }
  }

  return (
    <section aria-labelledby="screen-title" data-screen="briefings" className="flex flex-col gap-4">
      <div className="flex items-center justify-between gap-3">
        <h1 id="screen-title" className="text-title font-semibold">브리핑</h1>
        <PushSubscribe />
      </div>
      {failed && (
        <p role="status" className="text-sm text-muted-foreground">
          {BRIEFING_NOTICE.listFailed}
        </p>
      )}
      {lookup === 'missing' && (
        <p role="status" className="text-sm text-muted-foreground" data-testid="schedule-missing">
          {BRIEFING_NOTICE.scheduleMissing}
        </p>
      )}
      {lookup === 'failed' && (
        <p role="status" className="text-sm text-muted-foreground" data-testid="schedule-failed">
          {BRIEFING_NOTICE.scheduleFailed}
        </p>
      )}
      {list !== null && items.length === 0 && (
        <p className="text-sm text-muted-foreground">{BRIEFING_NOTICE.empty}</p>
      )}
      {items.length > 0 && (
        <ul className="flex flex-col gap-3" data-testid="briefing-list">
          {items.map(({ record, highlighted }) => (
            <BriefingItem
              key={record.schedule.id}
              record={record}
              highlighted={highlighted}
              runState={runStates[record.schedule.id]}
              onRun={run}
            />
          ))}
        </ul>
      )}
    </section>
  )
}
