// 날짜 표기 — 서버가 준 ISO 문자열을 보기 좋게만 바꾼다(사용자 기기 시간대). 서버 문장은 건드리지 않는다.
const DATE = new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium' })
const DATE_TIME = new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium', timeStyle: 'short' })

/** 날짜로 읽을 수 없는 값이면 받은 문자열을 그대로 돌려준다. */
export function formatDate(iso: string): string {
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? iso : DATE.format(d)
}

export function formatDateTime(iso: string): string {
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? iso : DATE_TIME.format(d)
}
