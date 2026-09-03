# 대화형 관계 메모리 에이전트 — 개발 하네스

> 이 파일은 Claude Code가 매 세션 읽는 프로젝트 규칙이다. 범위·역할·불변 원칙을 여기서 관리한다.

## 이 프로젝트가 만드는 것

사용자가 평소처럼 대화하면, 제품 속 **관계 메모리 에이전트**가 인물·사건·일정을 스스로 추출·해석해 장기 메모리를 구축하고, 만남 직전에 필요한 맥락만 요약(브리핑)한다.

확정 제목(D8): **대화형 관계 메모리 에이전트 — 자연어 대화에서 자동 구축되는 개인 관계 메모리 기반 브리핑 시스템**
(기획서 원본의 "관계 그래프"는 "관계 메모리"로 변경 확정. 저장되는 것은 사용자–인물 관계뿐이다.)

## ★ 에이전트가 두 종류다 (헷갈리지 말 것)

| 구분 | 무엇인가 | 어디에 있나 |
|------|---------|-----------|
| **제품 속 에이전트** | 툴 7종을 호출하고 엔티티 해석을 수행하는 런타임 에이전트 | 우리가 **코드로 작성**하는 산출물 |
| **개발 하네스** | 그 제품을 만드는 걸 돕는 Claude Code 팀 | `.claude/agents`, `.claude/skills` |

이 문서와 `.claude/`는 **개발 하네스**다. 제품 속 에이전트는 이 팀이 작성하는 결과물이다.

## 팀 구성 (현재 활성 4) — 역할별 모델 분리 (L-002)

| 에이전트 | 역할 | 모델 | 이유 |
|---------|------|------|------|
| `.claude/agents/architect.md` | 계획. 기획서를 작업으로 분해, 01-plan 초안, backlog | opus | 문서·의존성 분해 |
| `.claude/agents/backend-agent.md` | 구현. 툴 7종·에이전트 루프·엔티티 해석 4단계 | sonnet | 코드 생산, 비용 |
| `.claude/agents/eval-agent.md` | 평가 데이터·지표. 한국어 대화 150건 데이터셋·베이스라인 | opus | 라벨 품질, 구현자와 다른 모델 |
| `.claude/agents/verifier.md` | **검증 전담.** 02-plan-verify 점검표·04-review·코드 리뷰 | fable | 가장 강한 모델을 가장 비판적인 자리에. 구현자와 다른 모델·새 컨텍스트 |

- **같은 컨텍스트·같은 모델이 계획→구현→검증을 다 하면 평가가 후해진다.** 그래서 점검표·완료 검토는 verifier 만 쓰고, `verify-plan.sh`/`verify-impl.sh` 가 `검증자:`/`검토자:` 줄에 `verifier` 가 없으면 FAIL 한다. 메인 세션은 조율·승인·커밋만 한다.

> `db-agent`, `frontend-agent`, `infra-agent`는 아직 만들지 않았다. 필요해지면 architect가 청사진의 역할표를 근거로 추가한다.

## 불변 원칙 (범위 통제)

1. **오병합(False Merge)은 미검출보다 훨씬 나쁘다.** 확신도가 임계치 미만이면 절대 자동 병합하지 말고 `ask_user`를 호출한다. 이 비대칭 비용이 엔티티 해석 설계의 뿌리다.
2. **임계치는 두 개다(T_merge, T_new).** 확신도 ≥ `T_merge`만 자동 연결한다. 그 미만은 반드시 `ask_user`다 — `[T_new, T_merge)`는 `kind="identity"`, `< T_new`는 `kind="new_person"`. 초기값 `T_merge = 0.8`, `T_new = 0.3` (파일럿 평가로 확정).
3. **확신도는 3신호 결합이다.** `confidence = 0.5·s_llm + 0.3·s_emb + 0.2·s_rule`. `s_llm`은 LLM이 **구조화 출력으로 자기보고한 0~1 점수**이며, **LLM 로그 확률은 쓰지 않는다**(Claude API가 제공하지 않는다). 자기보고 점수는 보정표(`reports/calibration.json`)로 뒷받침한다.
4. **엔티티 해석은 LLM 단일 호출로 하지 않는다.** 반드시 4단계(후보검색 → 규칙필터 → LLM판정 → 확신도 미달 시 ask_user). 이유는 `.claude/skills/entity-resolution` 참조.
5. **프론트 화면은 3개로 고정**: 채팅 / 인물 카드 / 브리핑. UI에 시간을 쓰지 않는다.
6. **포함 범위에 명시**: 반복 패턴 감지(규칙 기반, D9) — 같은 인물의 같은 `events.type`이 90일 내 3회 이상이면 `person_facts(key="pattern:{type}")`를 생성한다. LLM은 패턴 문장화만 한다.
7. **의도적으로 제외한 것**: 고민 상담, 인물 간(A–B) 관계 저장, 상담 페르소나, 음성 입력, 네이티브 앱. "왜 안 했는가"를 설명할 수 있는 것이 범위 통제 능력이다.
   - 경계 문장: **브리핑의 "제안"은 기록된 사실에서 도출되는 한 줄 행동 제안으로 한정한다.** 감정·고민에 대한 대화는 하지 않는다 — 고민 상담이 아니다.
8. **평가 수치는 재현 가능해야 한다.** 데이터셋·라벨·베이스라인을 조작하지 않는다. 성능 미달도 결과다 — 실패 케이스 분석을 산출물로 남긴다.
9. **모든 판정에는 근거를 남긴다.** `agent_traces`에 step·입력·출력·툴·토큰(in/out)·후보·확신도 분해를 기록한다.

## 기술 스택

- 백엔드: FastAPI (Python), Docker
- 프론트: React + PWA (S3 + CloudFront)
- DB: PostgreSQL + pgvector (RDS). 별도 벡터 DB 미도입 — 인물·별칭 테이블과 임베딩을 같은 DB에서 조인.
- 임베딩: 별도 공급자 필요(Claude API에는 임베딩 엔드포인트가 없다). 공급자·차원은 임베딩 파일럿(D4) 후 확정.
- 인프라: Terraform, GitHub Actions, SSM Parameter Store. CloudFront → EC2 구간은 EC2의 Caddy(Let's Encrypt)로 HTTPS, ALB 미사용(D7).
- 첫날 필수: AWS Budgets 알림($10 / $30 / $50)

## 툴 7종 (제품 속 에이전트가 호출) — 시그니처 v2

| 툴 | 시그니처 |
|----|----------|
| `search_person` | `(query: str, hints?: {hierarchy?, relation_tag?}) → Candidate[]` |
| `create_person` | `(display_name, aliases: str[], relation_tag, hierarchy) → Person` |
| `update_person` | `(person_id, facts?: {key,value}[], new_alias?: str, display_name?: str) → Person` |
| `add_event` | `(person_id, type, content, occurred_at, raw_utterance) → Event` |
| `add_schedule` | `(person_id, title, scheduled_at) → Schedule` |
| `get_briefing` | `(person_id, schedule_id?) → Briefing` |
| `ask_user` | `(kind, question, options, context) → PendingQuestion` |

- `Candidate` = `{person, similarity, aliases_matched, rule_flags}` — 3단계 LLM 판정의 입력.
- `ask_user`는 "에이전트가 모른다를 스스로 판단하는 행동"이다. 반드시 별도 툴로 유지한다.
- **`ask_user`는 비동기 대기 질문 모델이다**: 질문을 `pending_questions`에 저장하고 `{question_id, status:"pending"}`을 반환한 뒤 그 턴을 종료한다. 사용자가 칩을 누르면 `POST /answers/{question_id}`가 저장된 context로 루프를 재개한다. `kind`는 `identity` / `new_person` / `schedule`.

## 데이터 모델 (권위 있는 정의 — 스키마 v2)

```sql
persons(id, user_id, display_name, relation_tag, hierarchy, created_at, updated_at)
person_aliases(id, person_id, alias, source, embedding vector(N), confirmed_at)  -- N은 임베딩 파일럿(D4) 후 확정
person_facts(id, person_id, key, value, confidence, updated_at)
fact_sources(fact_id, event_id)                          -- 시맨틱 사실 → 근거 원문 링크
events(id, person_id, type, content, raw_utterance, occurred_at, created_at)
schedules(id, person_id, title, scheduled_at, briefed_at)
pending_questions(id, session_id, kind, question, options, context, answer, created_at, answered_at)
push_subscriptions(id, user_id, endpoint, keys, created_at)
agent_traces(id, session_id, step, tool_name, input, output, tokens_in, tokens_out, created_at)
```

- **`person_embeddings` 테이블은 없다.** 임베딩은 **별칭 단위**로 `person_aliases.embedding`에 둔다. 후보 검색은 별칭 top-K → 인물별 max 유사도로 집계한다.
- `events.type` 고정 집합: `conflict / praise / meal / meeting / personal_share / favor / other`. 추출 F1의 라벨 집합이 된다.
- ER 단계의 `agent_traces.output`에는 `candidates[]`, `confidence_breakdown{}`, `decision`을 JSON으로 넣는다.

관계 태그: 가족 / 연인 / 친구 / 직장 / 지인 × 위계 상 / 동 / 하. 사용자가 고르지 않고 대화에서 자동 추론한다.

## 산출물 위치

- `docs/proposal.md` — 기획서 원본(본문 수정 금지, 상단 안내문만 갱신)
- `docs/proposal-review.md` — 기획서 검증 결과 20항목과 처리 상태
- `docs/resolution-plan.md` — 결정 사항(D1~D10)·설계 명세·구현 순서(P1~P11)
- `docs/backlog.md` — architect가 관리하는 작업 목록
- `reports/` — eval-agent의 평가 산출물(`eval.md`, `metrics.json`, `calibration.json`)

## 사용법

- 감독에게 맡기기: `architect` 에이전트에게 "다음 작업 패키지를 backlog로 쪼개줘"
- 엔티티 해석 구현: `backend-agent`에게 위임 (자동으로 `entity-resolution` 스킬 참조)
- 평가 실행: `eval-agent`에게 "150건 데이터셋으로 오병합률 측정하고 베이스라인과 비교해줘"

## 개발 프로세스 (하네스 규칙 — 훅이 강제한다)

- **위키는 꺼내 보는 참고자료다.** 세션 시작 시 `docs/wiki/HANDOFF.md`(자동 주입)와 `docs/wiki/INDEX.md`·`CURRENT.md`만 읽고, 태그(P/D/R/S/원칙)가 가리키는 카드만 연다. 원문 전체를 읽지 않는다.
- **재개 규칙**: 중단된 작업이나 커밋 안 된 변경이 있으면 **다른 어떤 일보다 먼저** 사용자에게 목록을 보이고 우선순위(이어서 완료 / 보류 / 폐기)를 묻는다 (`/devlog resume`).
- **제품 코드는 활성 작업이 있어야 쓸 수 있다.** `/devlog start <id>` → 01-plan → 02-plan-verify(기계 검증 `verify-plan.sh` + 점검표 8행 + 카드 인용) → 사용자 승인 → `CURRENT.md active`. `stage-gate.sh`가 막는다. 한 번에 활성 패키지 하나. P4 파일럿 평가 전에 P5 이후 시작 금지.
- **작업 단위(사소한 수정 포함)마다 `/commit`.** LLM이 초안(변경·이유·정합성·검증·Refs)을 쓰고 사용자가 AskUserQuestion으로 승인한 뒤에만 커밋한다. `git add`는 명시 경로만. 푸시도 승인 필요. 서브에이전트는 커밋하지 않는다.
- **계획·검증·구현은 모두 위키에 남긴다.** `packages/<id>/01~05`, `registry.md`(무엇이 있는가 — 단위 시작 전 grep, 중복 구현 금지), `journal.md`(시간순), `HANDOFF.md`(지금 어디·다음 무엇).
- **검증은 가시적 증거로만.** "확인했습니다"는 검증이 아니다. `verify-plan.sh`/`verify-impl.sh` 출력 파일, 테스트 출력, 재현 명령 출력, 커밋 해시, 존재하는 파일 경로만 증거다(`docs/wiki/verification.md`). FAIL/WARN은 `findings.py`로 `05-remediation.md` 소견이 되고, 소견마다 원인·해결 단계·완료 판정 명령·재검증을 채워 닫는다. 같은 소견이 3회 재검증 후에도 열려 있으면 사용자에게 보고한다(재시도 남발 금지, 원칙8).
- **기획서가 바뀌면 `/devlog change`.** CR 문서 → 태그로 영향 범위(R→D→S→P→`git log --grep`) → 사용자 결정 → `CURRENT.md frozen` 동결 → 카드·CLAUDE.md·backlog 갱신 → 코드 revert/FIX → 해제. 기획서 본문은 원본 유지, 상단 안내문에만 한 줄.
- **컨텍스트 소진 대비.** 작업 단위 종료·큰 읽기 전·대화가 길어졌을 때 `HANDOFF.md`를 갱신한다. Stop 훅이 변경 파일보다 오래된 HANDOFF를 막는다. 남은 토큰 표시가 20% 미만이면 새 단위를 시작하지 않고 마무리·HANDOFF·`/commit`만 한다.
- **보안**: `docs/wiki/security.md`. 비밀 파일 읽기·쓰기, 키 문자열 삽입, 강제 푸시, 이력 파괴, 재귀 삭제, `sudo`, destroy/prune/DROP, 외부 전송은 훅이 막는다. 막히면 우회하지 않고 사용자에게 명령을 보여 직접 실행을 요청한다.
- 저장소: `https://github.com/SunWoo1213/Relationship.git`. **브랜치 전략(L-001)**: 작업·푸시는 `dev`로만, `main`은 배포 브랜치. dev를 실서버에서 검증한 뒤 `/commit release`(사용자 승인 → `git push origin dev:main`)로만 승격한다. 훅이 main 직접 푸시를 막는다. **dev 푸시 뒤에는 멈춘다(L-003)**: 사용자가 승격/수정을 정하기 전에는 다음 작업·커밋을 시작하지 않는다(`.claude/.awaiting-decision` 마커를 훅이 강제). 임베딩은 OpenAI로 시작(D4), 추후 다른 공급자와 비교.
- **git log 연동**: 세션 시작·커밋마다 훅이 `.claude/gitlog.md`(최근 커밋·태그별 커밋·마지막 커밋 파일 목록)를 갱신한다. Bash가 없는 에이전트(architect)는 이 파일을 읽고, Bash가 있는 에이전트는 `bash .claude/scripts/gitlog.sh [태그]`를 직접 실행한다. 계획(01-plan)·계획 검증(02-plan-verify)·구현 전에 반드시 본다.
