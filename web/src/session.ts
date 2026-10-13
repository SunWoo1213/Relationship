// 세션 보관 (결정 D (i)): 서버가 발급한 session_id 를 localStorage 에 두고 요청마다 재전송한다.
// 프론트는 사용자 id 를 만들지도 보내지도 않는다. 저장소 접근은 막힐 수 있어(사생활 모드 등) 전부 try/catch.

export const SESSION_STORAGE_KEY = 'relationship.session_id'

export function getSessionId(): string | null {
  try {
    return window.localStorage.getItem(SESSION_STORAGE_KEY) || null
  } catch {
    return null
  }
}

export function setSessionId(sessionId: string): void {
  try {
    window.localStorage.setItem(SESSION_STORAGE_KEY, sessionId)
  } catch {
    // 저장 실패는 조용히 넘긴다 — 다음 요청이 헤더 없이 가면 서버가 새로 발급한다.
  }
}

export function clearSessionId(): void {
  try {
    window.localStorage.removeItem(SESSION_STORAGE_KEY)
  } catch {
    // 위와 같다.
  }
}
