// 옛 세션 보관(P8 결정 D (i))의 흔적 정리만 남긴다 (P9b U6).
// 대화 세션은 이제 서버가 로그인 계정에서 만든다 — 프론트는 session_id 를 읽지도 보내지도 않는다.
// 예전에 localStorage 에 남은 키는 로그인·가입에 성공할 때 한 번 지운다. 저장소 접근은 막힐 수 있어 try/catch.

export const SESSION_STORAGE_KEY = 'relationship.session_id'

export function clearLegacySessionId(): void {
  try {
    window.localStorage.removeItem(SESSION_STORAGE_KEY)
  } catch {
    // 저장소가 막혀 있으면 지울 것도 없다.
  }
}
