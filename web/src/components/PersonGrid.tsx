// 인물 화면(`#/persons`) 본문 — 카드 그리드 + 이름·별칭 검색 (D15·CR-003, P8b 결정 A~D·G~I).
// 순서는 서버가 준 그대로, 검색은 거르기만 한다(재정렬·하이라이트·서버 문자열 가공 없음, 원칙7).
import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { PERSON_LIST_NOTICE } from '@/components/PersonList'
import { usePersons } from '@/components/PersonsProvider'
import { formatDate } from '@/lib/format'
import { HREF } from '@/routes'

/** 타일에 보일 별칭 상한 (결정 B). */
const ALIAS_LIMIT = 2

/** 검색 비교용 정규화 (결정 C) — 비교 안에서만 쓰고 화면 표시에는 쓰지 않는다. */
function normalizeForMatch(s: string): string {
  return s.trim().toLowerCase().replace(/\s+/g, '')
}

/** 결정 B: display_name 과 글자가 완전히 같은 별칭은 빼고, 서버 순서로 최대 2개, 넘치면 남은 개수. */
function tileAliases(displayName: string, aliases: string[]) {
  const rest = aliases.filter((a) => a !== displayName)
  return { shown: rest.slice(0, ALIAS_LIMIT), more: rest.length - ALIAS_LIMIT }
}

export default function PersonGrid() {
  const { persons, failed } = usePersons()
  const [query, setQuery] = useState('') // 결정 G: 컴포넌트 상태만

  if (failed) {
    return (
      <p role="status" className="px-3 py-2 text-sm text-muted-foreground">
        {PERSON_LIST_NOTICE.failed}
      </p>
    )
  }
  if (persons === null) return null
  if (persons.length === 0) {
    return <p className="px-3 py-2 text-sm text-muted-foreground">{PERSON_LIST_NOTICE.empty}</p>
  }

  const q = normalizeForMatch(query)
  const visible = q
    ? persons.filter((p) => [p.display_name, ...p.aliases].some((t) => normalizeForMatch(t).includes(q)))
    : persons

  return (
    <div className="flex flex-col gap-4">
      <input
        type="search"
        data-testid="person-search"
        aria-label={PERSON_LIST_NOTICE.searchLabel}
        placeholder={PERSON_LIST_NOTICE.searchPlaceholder}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
      />
      {visible.length === 0 ? (
        <p data-testid="person-grid-empty" className="px-3 py-2 text-sm text-muted-foreground">
          {PERSON_LIST_NOTICE.searchEmpty}
        </p>
      ) : (
        <div data-testid="person-grid" className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {visible.map((p) => {
            const { shown, more } = tileAliases(p.display_name, p.aliases)
            return (
              <a
                key={p.id}
                href={`${HREF.persons}/${p.id}`}
                data-testid="person-tile"
                data-person-id={p.id}
                className="block rounded-xl focus-visible:outline-2 focus-visible:outline-ring"
              >
                <Card size="sm" className="h-full hover:bg-accent">
                  <div className="flex flex-col gap-1 px-(--card-spacing)">
                    <span className="block font-medium" data-field="name">
                      {p.display_name}
                    </span>
                    <span className="block text-sm text-muted-foreground">
                      <span data-field="tag">{p.relation_tag}</span>
                      {' · '}
                      <span data-field="hierarchy">{p.hierarchy}</span>
                    </span>
                    <span className="block text-sm text-muted-foreground" data-field="last-contact">
                      {p.last_contact_at ? formatDate(p.last_contact_at) : PERSON_LIST_NOTICE.noContact}
                    </span>
                    {shown.length > 0 && (
                      <span className="block text-sm text-muted-foreground" data-field="aliases">
                        {shown.join(' · ')}
                        {more > 0 ? ` +${more}` : ''}
                      </span>
                    )}
                  </div>
                </Card>
              </a>
            )
          })}
        </div>
      )}
    </div>
  )
}
