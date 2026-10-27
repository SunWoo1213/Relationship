// 인물 카드 화면 (U6, 결정 F·L·N) — `#/persons`(목록) 와 `#/persons/:id`(카드) 가 이 화면 하나를 쓴다.
// 섹션 순서는 기획서 부록 A ② 그대로: 머리 → 별칭 → 마지막 접촉 → 알고 있는 것 → 반복 패턴 → 타임라인 → 다가오는 일정.
// 서버 문자열(key · value · content · raw_utterance · title)은 고치지 않고 그대로 보여 준다 (원칙7).
// 원문(raw_utterance)은 펼칠 때만 가져오고(1회), 같은 항목을 다시 펼쳐도 다시 요청하지 않는다 — 항목 컴포넌트 상태에 캐시.
import { useCallback, useEffect, useState, type ReactNode } from 'react'
import { ChevronDownIcon, TriangleAlertIcon } from 'lucide-react'
import { ApiError, getEventRaw, getFactSources, getPersonCard } from '@/api/client'
import type {
  FactSourceEventOut,
  PersonCardOut,
  PersonFactOut,
  PersonPatternOut,
  TimelineEventOut,
} from '@/api/types'
import PersonGrid from '@/components/PersonGrid'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Skeleton } from '@/components/ui/skeleton'
import { formatDate, formatDateTime } from '@/lib/format'
import { cn } from '@/lib/utils'
import { HREF } from '@/routes'

/** 프론트가 만드는 고정 안내 문장(빈 상태·오류)과 버튼 글자. 서버 메시지가 아니다. */
export const CARD_NOTICE = {
  notFound: '인물을 찾을 수 없어요.',
  loadFailed: '인물 카드를 불러오지 못했어요.',
  backToList: '인물 목록으로',
  aliasesLabel: '별칭',
  aliasesNone: '없음',
  lastContactLabel: '마지막 접촉',
  lastContactNone: '기록 없음',
  factsTitle: '알고 있는 것',
  factsEmpty: '아직 알고 있는 것이 없어요.',
  patternsTitle: '반복 패턴',
  patternsEmpty: '반복 패턴이 없어요.',
  timelineTitle: '타임라인',
  timelineEmpty: '기록이 없어요.',
  schedulesTitle: '다가오는 일정',
  schedulesEmpty: '다가오는 일정이 없어요.',
  showSources: '근거 보기',
  hideSources: '근거 접기',
  showRaw: '원문 펼치기',
  hideRaw: '원문 접기',
  loading: '불러오는 중',
  detailFailed: '원문을 불러오지 못했어요. 다시 눌러 주세요.',
} as const

// --- 한 번만 가져오는 펼침 (원문 · 근거 공통) ---

type Fetched<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'done'; data: T }
  | { status: 'error' }

/**
 * 펼침 상태 + 지연 조회. 처음 펼칠 때 `load` 를 1회 부르고, 성공하면 그 값을 상태에 보관해
 * 접었다 다시 펼쳐도 부르지 않는다. 실패는 이 항목에만 남고, 다시 누르면 재시도한다.
 */
function useLazyDetail<T>(load: () => Promise<T>) {
  const [open, setOpen] = useState(false)
  const [state, setState] = useState<Fetched<T>>({ status: 'idle' })

  const run = useCallback(() => {
    setState({ status: 'loading' })
    load().then(
      (data) => setState({ status: 'done', data }),
      () => setState({ status: 'error' }),
    )
  }, [load])

  const toggle = () => {
    // 실패 안내가 떠 있으면 누르는 것이 재시도. 로딩 중 접었다가 실패한 경우도 열어 준다(R-U6-1).
    if (state.status === 'error') {
      setOpen(true)
      return run()
    }
    if (open) return setOpen(false)
    setOpen(true)
    if (state.status === 'idle') run()
  }

  return { open, state, toggle }
}

function DetailStatus<T>({ state, children }: { state: Fetched<T>; children: (data: T) => ReactNode }) {
  if (state.status === 'loading') return <Skeleton className="mt-2 h-10 w-full" aria-label={CARD_NOTICE.loading} />
  if (state.status === 'error') {
    return (
      <p role="alert" className="mt-2 text-sm text-destructive">
        {CARD_NOTICE.detailFailed}
      </p>
    )
  }
  if (state.status === 'done') return <>{children(state.data)}</>
  return null
}

/** 원문 발화 — 글자 그대로(가공 0). 줄바꿈·공백은 CSS 로만 보존한다. */
function RawText({ text }: { text: string }) {
  return (
    <p className="whitespace-pre-wrap rounded-md bg-muted p-3 text-sm" data-testid="raw-utterance">
      {text}
    </p>
  )
}

// --- 타임라인 항목 ---

function TimelineItem({ event }: { event: TimelineEventOut }) {
  const load = useCallback(() => getEventRaw(event.id), [event.id])
  const { open, state, toggle } = useLazyDetail(load)
  return (
    <li data-testid={`timeline-${event.id}`}>
      <Collapsible open={open}>
        <div className="flex items-start gap-2">
          <span className="w-28 shrink-0 text-sm text-muted-foreground">{formatDate(event.occurred_at)}</span>
          <Badge variant="outline">{event.type}</Badge>
          <span className="min-w-0 flex-1">{event.content}</span>
          <CollapsibleTrigger asChild>
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              aria-label={open ? CARD_NOTICE.hideRaw : CARD_NOTICE.showRaw}
              onClick={toggle}
            >
              <ChevronDownIcon className={cn('transition-transform', open && 'rotate-180')} />
            </Button>
          </CollapsibleTrigger>
        </div>
        <CollapsibleContent>
          <DetailStatus state={state}>{(raw) => <RawText text={raw.raw_utterance} />}</DetailStatus>
        </CollapsibleContent>
      </Collapsible>
    </li>
  )
}

// --- 사실·패턴의 근거 ---

function SourcesToggle({
  personId,
  factId,
  sourceCount,
}: {
  personId: number
  factId: number
  sourceCount: number
}) {
  const load = useCallback(async () => (await getFactSources(personId, factId)).sources, [personId, factId])
  const { open, state, toggle } = useLazyDetail<FactSourceEventOut[]>(load)
  if (sourceCount <= 0) return null // 근거가 없으면 버튼도 없다
  return (
    <Collapsible open={open} className="mt-1">
      <CollapsibleTrigger asChild>
        <Button type="button" variant="link" size="sm" className="h-auto p-0" onClick={toggle}>
          {open ? CARD_NOTICE.hideSources : CARD_NOTICE.showSources}
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <DetailStatus state={state}>
          {(sources) => (
            <ul className="mt-2 space-y-3" data-testid={`sources-${factId}`}>
              {sources.map((s) => (
                <li key={s.event_id}>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(s.occurred_at)} · {s.content}
                  </p>
                  <RawText text={s.raw_utterance} />
                </li>
              ))}
            </ul>
          )}
        </DetailStatus>
      </CollapsibleContent>
    </Collapsible>
  )
}

// --- 섹션 ---

function Section({
  name,
  title,
  icon,
  className,
  children,
}: {
  name: string
  title: string
  icon?: ReactNode
  className?: string
  children: ReactNode
}) {
  return (
    <section data-section={name} aria-label={title} className={className}>
      <h2 className="mb-2 flex items-center gap-2 font-semibold">
        <span aria-hidden="true">▸</span>
        {title}
        {icon}
      </h2>
      {children}
    </section>
  )
}

function Empty({ children }: { children: ReactNode }) {
  return <p className="text-sm text-muted-foreground">{children}</p>
}

function FactRow({ personId, fact }: { personId: number; fact: PersonFactOut | PersonPatternOut }) {
  return (
    <li data-testid={`fact-${fact.id}`}>
      <span className="text-sm text-muted-foreground">{fact.key}</span> <span>{fact.value}</span>
      <SourcesToggle personId={personId} factId={fact.id} sourceCount={fact.source_count} />
    </li>
  )
}

function CardView({ personId }: { personId: number }) {
  const [card, setCard] = useState<PersonCardOut | null>(null)
  const [error, setError] = useState<'not_found' | 'failed' | null>(null)

  useEffect(() => {
    let alive = true
    getPersonCard(personId).then(
      (c) => alive && setCard(c),
      (e: unknown) => alive && setError(e instanceof ApiError && e.status === 404 ? 'not_found' : 'failed'),
    )
    return () => {
      alive = false
    }
  }, [personId])

  if (error) {
    return (
      <div>
        <p role="alert">{error === 'not_found' ? CARD_NOTICE.notFound : CARD_NOTICE.loadFailed}</p>
        <a href={HREF.persons} className="mt-2 inline-block text-primary underline">
          {CARD_NOTICE.backToList}
        </a>
      </div>
    )
  }
  if (!card) return <Skeleton className="h-64 w-full" aria-label={CARD_NOTICE.loading} />

  const { person } = card
  return (
    <Card className="gap-6 p-6" data-testid="person-card">
      <div data-section="header" className="flex items-center justify-between gap-2">
        <h2 className="text-title font-semibold">{person.display_name}</h2>
        <Badge variant="secondary">{`${person.relation_tag} · ${person.hierarchy}`}</Badge>
      </div>

      <p data-section="aliases" className="text-sm">
        {CARD_NOTICE.aliasesLabel}: {card.aliases.length ? card.aliases.join(', ') : CARD_NOTICE.aliasesNone}
      </p>

      <p data-section="last-contact" className="text-sm">
        {CARD_NOTICE.lastContactLabel}:{' '}
        {card.last_contact_at ? formatDate(card.last_contact_at) : CARD_NOTICE.lastContactNone}
      </p>

      <Section name="facts" title={CARD_NOTICE.factsTitle}>
        {card.facts.length ? (
          <ul className="space-y-2">
            {card.facts.map((f) => (
              <FactRow key={f.id} personId={person.id} fact={f} />
            ))}
          </ul>
        ) : (
          <Empty>{CARD_NOTICE.factsEmpty}</Empty>
        )}
      </Section>

      <Section
        name="patterns"
        title={CARD_NOTICE.patternsTitle}
        icon={<TriangleAlertIcon className="size-4 text-warning" aria-hidden="true" />}
      >
        {card.patterns.length ? (
          <ul className="space-y-2 border-l-2 border-warning pl-3">
            {card.patterns.map((p) => (
              <FactRow key={p.id} personId={person.id} fact={p} />
            ))}
          </ul>
        ) : (
          <Empty>{CARD_NOTICE.patternsEmpty}</Empty>
        )}
      </Section>

      <Section name="timeline" title={CARD_NOTICE.timelineTitle}>
        {card.timeline.length ? (
          <ul className="space-y-3">
            {card.timeline.map((e) => (
              <TimelineItem key={e.id} event={e} />
            ))}
          </ul>
        ) : (
          <Empty>{CARD_NOTICE.timelineEmpty}</Empty>
        )}
      </Section>

      <Section name="schedules" title={CARD_NOTICE.schedulesTitle}>
        {card.upcoming_schedules.length ? (
          <ul className="space-y-1">
            {card.upcoming_schedules.map((s) => (
              <li key={s.id}>
                <span className="text-sm text-muted-foreground">{formatDateTime(s.scheduled_at)}</span> {s.title}
              </li>
            ))}
          </ul>
        ) : (
          <Empty>{CARD_NOTICE.schedulesEmpty}</Empty>
        )}
      </Section>
    </Card>
  )
}

export default function PersonCardScreen({ personId }: { personId: number | null }) {
  return (
    <section
      aria-labelledby="screen-title"
      data-screen="persons"
      data-person-id={personId ?? undefined}
    >
      <h1 id="screen-title" className={cn('text-title font-semibold', personId !== null && 'sr-only')}>
        인물
      </h1>
      {personId === null ? (
        <div className="mt-4">
          <PersonGrid />
        </div>
      ) : (
        <div data-testid="card-wrap" className="mx-auto w-full md:w-3/4">
          <CardView key={personId} personId={personId} />
        </div>
      )}
    </section>
  )
}
