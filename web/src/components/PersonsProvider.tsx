// 인물 목록 단일 조회 (R-U6-2 (iii)) — AppShell 이 `GET /persons` 를 한 번만 불러 사이드바·`#/persons` 본문의
// PersonList 두 곳에 내려준다(컨텍스트). 새 API·새 라우트 없음.
// 다시 읽는 때: ① 해시 라우트가 바뀔 때 ② 채팅 응답 `stored.persons > 0` 일 때(`notifyPersonsChanged`).
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { getPersons } from '@/api/client'
import type { PersonListItemOut } from '@/api/types'

/** ChatScreen → AppShell 알림 경로. 창 이벤트라 두 컴포넌트가 서로를 import 하지 않는다. */
export const PERSONS_CHANGED_EVENT = 'relationship:persons-changed'

export function notifyPersonsChanged(): void {
  window.dispatchEvent(new CustomEvent(PERSONS_CHANGED_EVENT))
}

export interface PersonsFeed {
  /** null = 아직 못 받음 */
  persons: PersonListItemOut[] | null
  failed: boolean
}

const PersonsContext = createContext<PersonsFeed | null>(null)

export function usePersons(): PersonsFeed {
  const feed = useContext(PersonsContext)
  if (!feed) throw new Error('PersonsProvider 안에서만 쓸 수 있다')
  return feed
}

export function PersonsProvider({ children }: { children: ReactNode }) {
  const [persons, setPersons] = useState<PersonListItemOut[] | null>(null)
  const [failed, setFailed] = useState(false)
  // 먼저 보낸 요청의 늦은 응답이 나중 응답을 덮지 않게 한다.
  const latest = useRef(0)

  const load = useCallback(() => {
    const mine = ++latest.current
    getPersons().then(
      (list) => {
        if (mine !== latest.current) return
        setPersons(list)
        setFailed(false)
      },
      () => {
        if (mine === latest.current) setFailed(true)
      },
    )
  }, [])

  useEffect(() => {
    load() // 마운트 직후 1회
    window.addEventListener('hashchange', load)
    window.addEventListener(PERSONS_CHANGED_EVENT, load)
    return () => {
      latest.current++ // 언마운트 뒤 응답 무시
      window.removeEventListener('hashchange', load)
      window.removeEventListener(PERSONS_CHANGED_EVENT, load)
    }
  }, [load])

  const value = useMemo(() => ({ persons, failed }), [persons, failed])
  return <PersonsContext.Provider value={value}>{children}</PersonsContext.Provider>
}
