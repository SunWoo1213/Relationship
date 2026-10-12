// 개발 서버 프록시의 경로 변환 (결정 C (ii)): `/api` 접두를 벗겨 백엔드 경로로 만든다.
// vite.config.ts 가 import 하고, Vitest 가 값으로 고정한다.

/** `/api/persons/3` → `/persons/3`, `/api` → `/`, `/api` 로 시작하지 않는 경로는 그대로. */
export function stripApiPrefix(path: string): string {
  if (path !== '/api' && !path.startsWith('/api/') && !path.startsWith('/api?')) return path
  const stripped = path.slice('/api'.length)
  return stripped === '' || stripped.startsWith('?') ? `/${stripped}` : stripped
}
