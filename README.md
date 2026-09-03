# 대화형 관계 메모리 에이전트

> 자연어 대화에서 자동 구축되는 개인 관계 메모리 기반 브리핑 시스템 — 1인 개발 캡스톤 프로젝트

사용자가 평소처럼 대화하면, 제품 속 **관계 메모리 에이전트**가 인물·사건·일정을 스스로 추출·해석해 장기 메모리를 쌓고, 만남 직전에 필요한 맥락만 요약(브리핑)해 준다. 입력을 요구하지 않는다는 점에서 수동 기록 도구와 다르고, 세션을 넘어 축적되며 같은 인물의 호칭 변이를 하나로 묶는다는 점에서 범용 LLM 채팅과 다르다.

## 왜 어려운가 — 핵심 기여

한국어 대화는 사람을 이름으로 부르지 않는다. 같은 인물이 이렇게 등장한다.

```
팀장 → 김팀장 → 우리 팀장님 → 그 사람 → 걔 → 부장님(승진 후) → 김선배
```

이를 한 인물로 묶는 **엔티티 해석(Entity Resolution)** 이 시스템 전체 성능을 좌우한다. 잘못 병합하면 신뢰가 즉시 무너지고(오병합), 못 묶으면 메모리가 파편화된다(미검출). 이 프로젝트는 **오병합이 미검출보다 훨씬 나쁘다**는 비대칭 비용을 설계의 뿌리로 삼는다.

- **4단계 해석 파이프라인**: 후보 검색(별칭 임베딩 top-K) → 규칙 필터(호칭 사전·위계·관계 태그) → LLM 판정(구조화 출력) → 확신도 미달 시 사용자에게 묻기. LLM 단일 호출로 해석하지 않는다.
- **확신도 3신호 결합**: `confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule`. LLM 로그 확률은 쓰지 않고, 자기보고 점수를 보정표로 뒷받침한다.
- **임계치 2개**: `T_merge`(초기 0.8) 이상만 자동 연결. 그 미만은 반드시 `ask_user` — 애매하면 "김팀장님 말씀이신가요?", 매우 낮으면 "새로 기억해둘까요?".
- **`ask_user`는 별도 툴**: "모른다"를 에이전트가 스스로 판단하는 행동으로 두고, 비동기 대기 질문(칩 응답 후 루프 재개)으로 구현한다.
- **모든 판정에 근거를 남긴다**: 후보·확신도 분해·툴 호출·토큰을 `agent_traces`에 기록한다.

## 무엇을 만드는가

| 화면 (3개 고정) | 툴 7종 (LLM이 선택·호출) |
|---|---|
| 채팅 | `search_person`, `create_person`, `update_person` |
| 인물 카드 (사실 · 타임라인 · 마지막 접촉) | `add_event`, `add_schedule` |
| 브리핑 | `get_briefing`, `ask_user` |

- **3계층 메모리**: 작업 메모리(최근 N턴) → 에피소드(`events`, 원문 보존) → 시맨틱(`person_facts`, 근거 이벤트 링크 `fact_sources`).
- **반복 패턴 감지(규칙)**: 같은 인물의 같은 사건 유형이 90일 내 3회 이상이면 패턴 사실을 만든다. LLM은 문장화만 한다.
- **브리핑**: 일정 24시간 전에 웹푸시. "제안"은 기록된 사실에서 나오는 한 줄 행동 제안으로 한정한다(고민 상담이 아니다).

**의도적으로 제외한 것**: 고민 상담, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성 입력, 네이티브 앱, 관계 태그 필터링. "왜 안 했는가"를 설명할 수 있는 것이 범위 통제다.

### 데모 시나리오 (3분)

1. "오늘 김팀장이랑 또 부딪혔어" → 인물 인식, "김팀장을 기억해둘까요?"
2. 몇 턴 대화 → 인물 카드가 실시간으로 채워진다
3. "다음 주 화요일에 그 사람이랑 회의 있어" → 일정 자동 추출
4. ★ "부장님이 또 그러시더라" → "김팀장님 말씀이신가요? 승진하셨다면 반영할게요"
5. 브리핑: "내일 15시 김부장 회의 — 최근 3회 모두 공개 석상 지적 패턴. 1:1 요청을 제안합니다"

## 기술 스택

| 영역 | 선택 |
|---|---|
| 백엔드 | FastAPI (Python), Docker |
| LLM | Claude API (제품 속 에이전트 · 평가) |
| 임베딩 | OpenAI `text-embedding-3-small`, **1536차원** (파일럿으로 확정 — `reports/embed_pilot.md`) |
| DB | PostgreSQL + pgvector (RDS). 별도 벡터 DB 없이 별칭 테이블과 임베딩을 같은 DB에서 조인 |
| 프론트 | React + PWA (S3 + CloudFront) |
| 인프라 | Terraform, GitHub Actions, SSM Parameter Store, EC2 + Caddy(Let's Encrypt) |

데이터 모델(스키마 v2): `persons`, `person_aliases`(별칭 단위 임베딩), `person_facts`, `fact_sources`, `events`, `schedules`, `pending_questions`, `push_subscriptions`, `agent_traces`. 권위 있는 정의는 `CLAUDE.md`와 `docs/wiki/specs/S3.1-schema-v2.md`.

## 평가

- 한국어 대화 150건 데이터셋(승진·대명사·별칭·정상·신규 인물 케이스)으로 P/R/F1, **오병합률**(핵심), 미검출률, 추출 F1, 툴 호출 정확도, `ask_user` 비율, 보정도를 측정한다.
- 베이스라인 3종과 같은 데이터·같은 지표로 비교하고, `T_merge`를 0.5~0.95로 바꾸며 오병합률·질문율·미검출률 트레이드오프 곡선을 그린다.
- 수치는 재현 가능해야 한다. 성능 미달도 결과이며, 재시도 대신 실패 케이스 분석을 산출물로 남긴다. 산출물은 `reports/`.

## 진행 상태

| 단계 | 내용 | 상태 |
|---|---|---|
| P0 | 임베딩 공급자 파일럿 (D4) | **완료** — small/large 모두 기준 통과, `text-embedding-3-small` N=1536 확정 |
| P0 | 로컬 docker-compose (pgvector) | 계획 검증 중 |
| P0 | LLM 비용 실측 | 대기 |
| P1 | 스키마 v2 마이그레이션 · 파일럿 데이터셋 | 대기 |
| P2~P3 | 툴 7종 · 엔티티 해석 4단계 · 베이스라인 | 대기 |
| P4 | **파일럿 평가(게이트)** — 여기서 임계치·보정표 확정 | 대기 |
| P5~P9 | 에이전트 루프 · 메모리 · 브리핑 · 푸시 · 프론트 · 인프라 | P4 통과 후 |

최신 상태는 `docs/wiki/HANDOFF.md`(지금 어디, 다음 무엇)와 `docs/wiki/journal.md`(시간순)에 있다.

## 저장소 구조

```
CLAUDE.md                 프로젝트 규칙 — 불변 원칙 9개, 툴 시그니처 v2, 스키마 v2, 개발 프로세스
docs/proposal.md          기획서 원본 (본문 불변)
docs/proposal-review.md   기획서 검증 20항목
docs/resolution-plan.md   결정 D1~D10 · 설계 명세 S3.1~S3.7 · 구현 순서 P0~P11
docs/backlog.md           작업 목록 (수용 기준의 권위)
docs/wiki/                개발 위키: 검증(R)→결정(D)→명세(S)→패키지(P) 카드, 교훈(L), HANDOFF·journal·registry
scripts/                  결정용 스크립트 (embed_pilot.py — 임베딩 파일럿)
tests/                    단위 테스트
reports/                  평가·파일럿 산출물 (embed_pilot.md, 이후 eval.md · metrics.json · calibration.json)
.claude/                  개발 하네스: 에이전트 4종, 스킬, 훅, 검증 스크립트
```

## 개발 방식 — 코딩 에이전트 하네스

이 저장소는 Claude Code로 개발하며, 에이전트가 기획서 의도에서 벗어나지 않도록 절차를 훅으로 강제한다.

- **계획 → 기계 검증 → 승인 → 구현 → 증거 검증 → 승인 커밋**. 제품 코드는 활성 패키지가 등록된 뒤에만 쓸 수 있다.
- **역할별 모델 분리**: 계획(architect, opus) · 구현(backend-agent, sonnet) · 평가 데이터(eval-agent, opus) · 검증(verifier, fable). 같은 컨텍스트·같은 모델이 자기 결과를 평가하지 않는다.
- **검증은 증거로만**: 스크립트 출력 파일, 테스트 출력, 커밋 해시만 증거다. "확인했습니다"는 검증이 아니다.
- **브랜치**: 작업·푸시는 `dev`, 배포는 `main`. dev를 실서버에서 확인한 뒤에만 승격하고, 그 결정 전에는 다음 작업을 시작하지 않는다.
- **보안**: `.env`·키 파일은 에이전트가 읽지도 쓰지도 않는다. 강제 푸시·이력 파괴·재귀 삭제·외부 전송은 훅이 막는다.

자세한 규칙은 `CLAUDE.md`, 절차는 `.claude/skills/devlog`·`.claude/skills/commit`, 교훈은 `docs/wiki/lessons/`.

## 로컬에서 해 보기

```bash
# 1. 환경변수 — 키 이름만 적힌 .env.example 을 복사해 값을 채운다 (.env 는 git 제외)
cp .env.example .env

# 2. 의존성 (Python 3.13)
pip install openai numpy python-dotenv pytest

# 3. 단위 테스트 (네트워크 불필요)
python -m pytest -q tests/

# 4. 임베딩 파일럿 재현 (OPENAI_API_KEY 필요, 호칭 30개 × 모델 2개 ≈ 240 토큰)
python scripts/embed_pilot.py
```

로컬 DB(docker-compose + pgvector)와 백엔드 서버 실행 방법은 해당 패키지가 완료되면 이 절에 추가한다.

## 문서 안내

| 알고 싶은 것 | 보는 곳 |
|---|---|
| 왜 이렇게 설계했나 | `docs/wiki/decisions/D01~D10` |
| 스키마·툴·해석 파이프라인·평가 명세 | `docs/wiki/specs/S3.1~S3.7` |
| 기획서에서 무엇이 바뀌었나 | `docs/proposal.md` 상단 안내문, `docs/wiki/review-index.md` |
| 지금 어디까지 왔나 | `docs/wiki/HANDOFF.md`, `docs/wiki/journal.md` |
| 무엇이 이미 만들어져 있나 | `docs/wiki/registry.md` |
