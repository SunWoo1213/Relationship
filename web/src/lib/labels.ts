// 표시 이름 표 (FIX-039) — 서버가 준 사실 키·사건 종류·패턴 키를 한글 이름으로만 바꿔 보여 준다.
// 서버 값(value · content · 원문 · 제목 · sentence)은 건드리지 않는다. 표에 없는 문자열은 받은 그대로 돌려준다.
// 원본: 사실 키 9종 = app/memory/types.py::FACT_KEYS, 사건 종류 7종 = app/db/models.py::EVENT_TYPES.

export const FACT_KEY_LABELS: Readonly<Record<string, string>> = {
  job: '직업',
  workplace: '소속',
  family: '가족',
  hobby: '취미',
  likes: '좋아하는 것',
  dislikes: '싫어하는 것',
  health: '건강',
  life_event: '근황',
  contact_note: '연락·만남 메모',
}

export const EVENT_TYPE_LABELS: Readonly<Record<string, string>> = {
  conflict: '갈등',
  praise: '칭찬',
  meal: '식사',
  meeting: '만남',
  personal_share: '개인 이야기',
  favor: '도움',
  other: '기타',
}

const PATTERN_PREFIX = 'pattern:'

// 표 조회는 자기 속성만(`toString` 같은 상속 키가 걸리지 않게).
function lookup(table: Readonly<Record<string, string>>, key: string): string | undefined {
  return Object.prototype.hasOwnProperty.call(table, key) ? table[key] : undefined
}

/** 사건 종류(타임라인 배지) 표시 이름. 모르는 종류는 받은 문자열 그대로. */
export function eventTypeLabel(type: string): string {
  return lookup(EVENT_TYPE_LABELS, type) ?? type
}

/**
 * 사실 줄·패턴 줄의 키 표시 이름.
 * `pattern:<type>` 은 `<사건 종류 한글>`(접두사 숨김), 모르는 type 이면 키 전체를 그대로.
 */
export function factKeyLabel(key: string): string {
  if (key.startsWith(PATTERN_PREFIX)) {
    const label = lookup(EVENT_TYPE_LABELS, key.slice(PATTERN_PREFIX.length))
    return label ?? key
  }
  return lookup(FACT_KEY_LABELS, key) ?? key
}
