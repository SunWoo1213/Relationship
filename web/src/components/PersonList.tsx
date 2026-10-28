// 사이드바 전용 인물 목록(결정 N·D15 결정 4): `#/persons` 본문은 `PersonGrid` 가 맡는다.
// 서버 순서 그대로 앞 `limit` 명 — 재정렬·필터·검색 없음. 새 API 없음(GET /persons).
import { usePersons } from '@/components/PersonsProvider'
import { formatDate } from '@/lib/format'
import { HREF } from '@/routes'

/** 프론트가 만드는 고정 안내 문장(빈 상태·오류·표시할 값 없음). 서버 메시지가 아니다. */
export const PERSON_LIST_NOTICE = {
  empty: '아직 기록된 인물이 없어요.',
  failed: '인물 목록을 불러오지 못했어요.',
  noContact: '기록 없음',
  // 인물 화면 그리드 검색 (P8b 결정 D)
  searchEmpty: '찾는 인물이 없어요.',
  searchPlaceholder: '이름이나 별칭으로 찾기',
  searchLabel: '인물 검색',
} as const

/** `limit` 이 없으면 전원. 사이드바는 항상 `SIDEBAR_RECENT_LIMIT` 를 넘긴다. */
export default function PersonList({ onNavigate, limit }: { onNavigate?: () => void; limit?: number }) {
  // 조회는 AppShell 의 PersonsProvider 가 한 번만 한다 — 여기서는 받은 값을 그릴 뿐이다.
  const { persons, failed } = usePersons()

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
  const shown = limit === undefined ? persons : persons.slice(0, limit)
  return (
    <>
    <ul className="flex flex-col gap-1" data-testid="person-list">
      {shown.map((p) => (
        <li key={p.id}>
          <a
            href={`${HREF.persons}/${p.id}`}
            onClick={onNavigate}
            className="block rounded-md px-3 py-2 hover:bg-sidebar-accent"
          >
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
          </a>
        </li>
      ))}
    </ul>
    <a
      href={HREF.persons}
      onClick={onNavigate}
      data-testid="sidebar-see-all"
      className="mt-1 block rounded-md px-3 py-2 text-sm font-medium hover:bg-sidebar-accent"
    >
      전체 보기 →
    </a>
    </>
  )
}
