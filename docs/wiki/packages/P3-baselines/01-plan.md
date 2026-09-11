# P3-baselines · 계획 (01-plan)

상태: 승인(2026-09-10) · 활성 | 담당: architect(계획) / eval-agent(구현) / verifier(검증) — 승인·커밋은 메인 세션 | 작성: 2026-09-10
태그 — 패키지: P3-baselines · 닫는 검증: 없음(INDEX 패키지 표의 "닫는 R" 열이 `—`) · 기대는 결정: D3 D4 D5 D10 (경계 확인용 D1) · 구현하는 명세: S3.7 (인터페이스 대조용 S3.3, 재사용 대상 S3.2) · 관련 원칙: 원칙1 원칙2 원칙3 원칙4 원칙7 원칙8 원칙9
의존: P1-pilot-dataset (완료 — `04-review.md` `결과: 완료`, U7 f78e9dc / 닫는 커밋 5cac9bf. `data/scenarios/` 40건·5범주와 `scripts/validate_scenarios.py --strict --json` 의 `counts`·`ambiguous_mention_count`·`trap_count` 가 이 패키지가 읽는 입력이다). P3-er (완료 — `04-review.md` `결과: 완료`, U9 b3bcc2d / 닫는 커밋 0527ab8. 비교 대상인 **제안 방식** `app/er/pipeline.resolve()` 가 여기서 나온다). `docs/backlog.md` P3 행의 의존 문구는 "P1 데이터셋" 이며 충족. **P4 게이트는 이 패키지에 해당하지 않는다**(게이트는 P5 이후에만 적용) — 오히려 이 패키지가 그 게이트의 입력을 만든다.

## 목표

`.claude/skills/eval-harness` §3 표("문자열 완전 일치 / 임베딩 유사도 단독 / LLM 단일 프롬프트 / 제안 4단계 하이브리드 — **동일 데이터·동일 지표**")와 S3.7 카드의 "베이스라인 3종 + 제안 방식, 동일 데이터·동일 지표" 한 줄을 코드로 만든다. 기획서 9장의 방어선("그냥 GPT 부른 거 아니냐")은 **같은 데이터에 같은 호출로 네 방식을 돌려 수치를 나란히 놓는 것**으로만 성립하므로, 이 패키지의 산출물은 (a) 네 방식이 구분 없이 호출되는 **공통 인터페이스**, (b) 그 인터페이스를 구현한 **베이스라인 3개**, (c) 제안 방식을 감싼 **어댑터**, (d) 네 방식을 같은 하네스로 호출해 계약이 지켜짐을 보이는 **테스트**다. 오병합률·미검출률·F1·보정표·트레이드오프 곡선을 **재는 일은 P4-pilot-eval** 이며 이 패키지는 잰다는 행위를 가능하게 하는 배관만 놓는다(원칙8 — 구현자가 자기 성능을 재지 않는다). 원칙4("LLM 단일 호출로 하지 않는다")가 금지한 방식을 **일부러 최선의 형태로 구현해 대비군으로 세우는 것**이 베이스라인 3의 존재 이유이고, 원칙8이 요구하는 정직함은 "베이스라인을 약하게 만들지 않는다"로 나타난다.

## 범위

- 포함:
  - **공통 인터페이스 `Resolver`(결정 A·B)** — 네 방식이 같은 인자로 호출되고 같은 형태로 답한다. 잠정 경로 `evaluation/resolvers/base.py`.
    ```python
    DECISIONS = ("merge", "identity", "new_person")     # D10 밴드 어휘와 같은 낱말

    @dataclass(frozen=True)
    class ResolverCandidate:
        person_id: int
        display_name: str
        score: float                  # 그 방식이 이 후보에 준 0~1 점수(없으면 0.0)
        signals: dict[str, float]     # 방식별 원자료(s_emb·s_rule·s_llm·exact 등)

    @dataclass(frozen=True)
    class MentionDecision:
        method: str                   # "proposed" | "exact_match" | "embedding_only" | "llm_single"
        mention: str
        decision: str                 # DECISIONS 중 하나
        person_id: int | None         # decision == "merge" 일 때만 not None
        score: float                  # 그 결정의 근거 점수 0~1 (의미는 method 마다 다르다)
        candidates: list[ResolverCandidate]
        trace_id: int | None = None   # 제안 방식만 채운다(agent_traces 행 id)
        tokens_in: int = 0
        tokens_out: int = 0
        detail: dict[str, Any] = field(default_factory=dict)   # forced_reason·정규화형·모델 등
        def to_dict(self) -> dict[str, Any]: ...

    class Resolver(Protocol):
        name: str
        supported_decisions: tuple[str, ...]
        def resolve_mention(
            self, ctx: ToolContext, mention: str, utterance: str,
            hints: dict[str, str] | None = None, *, config: ERConfig | None = None,
        ) -> MentionDecision: ...
    ```
  - **인터페이스 불변 규약**(네 구현 전부에 적용, 계약 테스트가 단언한다):
    - **부수효과 0** — `persons`·`person_aliases`·`pending_questions` 를 쓰지 않는다. 어떤 방식도 `ask_user`·`create_person`·`update_person`·`apply_resolution` 을 부르지 않는다. "무엇을 할지"만 답하고 실행은 P4 러너/P5 몫이다(제안 방식 `resolve()` 가 이미 그런 계약이므로 그대로 따른다 — P3-er 결정 4).
    - **예외 비대칭 금지** — 후보 0건·판정 실패는 예외가 아니라 `decision="new_person"` 또는 `"identity"` 로 표현하고 이유를 `detail.forced_reason` 에 남긴다. 한 방식만 예외로 죽으면 분모가 달라져 비교가 깨진다(원칙8).
    - **`person_id` 는 `merge` 에서만** — `identity` 는 "사람에게 묻는다"이므로 후보 목록(`candidates`)이 답이고 단일 인물을 고르지 않는다(원칙1·2).
    - **입력 상태는 호출자가 만든다** — resolver 는 주어진 `ctx`(같은 DB·같은 `user_id`·같은 사전 상태)만 본다. 시나리오를 어떻게 적재·초기화할지는 호출자(P4 러너)가 정한다.
    - **`config` 는 `ERConfig` 를 그대로 재사용**(D10) — `t_merge`/`t_new` 를 P4 가 한 프로세스 안에서 스윕한다(S3.7 곡선). 각 방식이 두 값을 어떻게 쓰는지(또는 쓰지 않는지)는 모듈 docstring 에 한 줄로 적는다.
  - **방식 표(`RESOLVERS` 이름→팩토리)와 `get_resolver(name, **kw)`** — P4 러너가 `for name in ALL_METHODS:` 한 줄로 돈다. 이름 문자열은 `reports/metrics.json` 의 키가 되므로 여기서 고정한다.
  - **제안 방식 어댑터 `evaluation/resolvers/proposed.py`(결정 G)** — `app.er.resolve()` 를 호출해 `Resolution` → `MentionDecision` 으로 옮긴다. `band`→`decision`, `matched_person_id`→`person_id`, `confidence`→`score`, `candidates[]`→`ResolverCandidate(signals={s_emb,s_rule})`, `trace_id`·`llm.tokens_*`·`decision.forced_reason`·`relaxed_retry`→`detail`. **`app/er/` 는 한 줄도 고치지 않는다** — 필요한 변환은 전부 어댑터 쪽에서 한다.
  - **베이스라인 1 — 문자열 완전일치 `evaluation/resolvers/exact_match.py`(결정 C)**: 사전 상태의 `person_aliases.alias`(+`persons.display_name`)와 mention 의 **완전일치**만으로 판정. 일치 1건 → `merge`(score 1.0), 일치 2건 이상 → `identity`(동명이인을 임의로 고르지 않는다 — 원칙1), 0건 → `new_person`. 임베딩·LLM·규칙을 쓰지 않는다. 정규화 범위는 결정 C(변형 2종을 함께 내는 안이 권장 — 약한 베이스라인만 보고하지 않기 위해서다, 원칙8).
  - **베이스라인 2 — 임베딩 단독 `evaluation/resolvers/embedding_only.py`(결정 D)**: `app.er.candidates.search_candidates()` 를 **재사용**해(중복 구현 금지, D5 별칭 top-K → 인물별 max) `s_emb` 만으로 판정한다. 규칙 필터·LLM 판정 없음. 밴드는 `app.er.confidence.band_for()` 를 재사용해 `s_emb` 에 `T_merge`/`T_new` 를 그대로 적용(결정 D-i 권장) — 그래야 P4 곡선의 x축이 네 방식에 같은 의미를 갖는다.
  - **베이스라인 3 — LLM 단일 프롬프트 `evaluation/resolvers/llm_single.py`(결정 E)**: 후보 검색·규칙 필터·확신도 결합 **없이** 한 번의 구조화 출력 호출로 **결정까지** 받는다 — `{decision: "merge"|"identity"|"new_person", matched_person_id: int|null, s_llm: 0~1, reason: str}`. 프롬프트에는 사전 상태 인물 목록(표시 이름·별칭·관계 태그·위계)과 발화 맥락을 넣는다(후보를 미리 걸러 주지 않는 것이 이 방식의 정의이고, 동시에 **가장 강한 합리적 형태**다 — 검색으로 후보를 좁혀 주면 그건 이미 제안 방식의 1단계다). 공급자 중립(Claude·OpenAI), 모델·공급자는 제안 방식과 **같은 환경변수**(`LLM_PROVIDER`·`ANTHROPIC_MODEL`)를 읽어 같은 모델로 맞춘다(모델 차이가 방식 차이로 둔갑하지 않게 — 원칙8). 온도는 0 고정, 키는 `os.environ` 으로만 전달하고 프롬프트·로그·예외 메시지에 넣지 않는다(security.md §1).
  - **시나리오 사전 상태 적재기 `evaluation/scenario_state.py`(결정 F)** — P1 04-review §7 인계 2 를 그대로 구현: 시나리오의 `seed_persons` + `persons[].aliases` 를 **있는 그대로** 적재하고 `gold_person_id`(문자열) → 실제 `persons.id` 매핑을 돌려준다. 대화에서 배워야 할 호칭은 넣지 않는다(결정 I). 시나리오 사이 DB 초기화·반복 실행·지표는 P4(§7 인계 1).
  - **계약 테스트(수용 기준의 증명) `tests/test_baseline_parity.py`** — `parametrize` 로 네(또는 다섯) 방식 전부를 **같은 인자·같은 픽스처**로 호출해 반환 타입·필드·값 집합·부수효과 0 을 단언한다. 하나라도 시그니처가 어긋나면 실패한다.
  - **방식별 단위 테스트** — 네트워크 없음(스텁 클라이언트·가짜 임베딩), 실 PostgreSQL(5433) + 롤백 픽스처는 P2·P3-er 방식 그대로.
  - **실호출 스모크 `scripts/baseline_smoke.py`** — 키가 있을 때만 도는 베이스라인 3 의 1회 호출(자동 테스트 아님, 사용자 실행). 출력은 evidence 로 남기고 키·프롬프트 원문은 남기지 않는다.
  - **문서 반영** — `docs/wiki/registry.md` 신규 행, `README.md` 에 베이스라인 실행법 절(환경변수 **이름**만).
- 이 패키지에서 하지 않는 것:
  - **평가 실행·지표 계산·곡선·`reports/` 산출물**(`metrics.json`·`calibration.json`·`eval.md`) — 전부 **P4-pilot-eval**. 여기서 `reports/` 아래에 파일을 만들지 않는다.
  - **오병합률·미검출률의 정의와 분모 규칙**(ambiguous 3건 제외, `passing_mentions` 6개 오탐 분자, ask_user 를 제3 범주로 집계) — P1 04-review §7 인계 3·4·6 이 가리키는 **P4 01-plan 몫**. 이 패키지는 mention 하나의 **결정**만 낸다.
  - **골드 라벨 수정·재해석**(P1 04-review §7 인계 9, R-3·H-3) — 베이스라인 수치가 나쁘게(또는 너무 좋게) 나와도 데이터를 손대지 않는다(원칙8).
  - **`app/` 수정** — `app/er/*`·`app/tools/*`·`app/embedding.py` 를 고치지 않는다. 필요한 것은 import 로 재사용하고, 재사용이 불가능한 지점(private 함수 필요 등)은 복제하지 말고 멈춰 사용자 결정으로 올린다.
  - **에이전트 루프·mention 추출** — 발화에서 지칭을 뽑는 일은 P5-loop 이다. 네 방식 모두 `mention` 을 **인자로 받는다**(P3-er 결정 1 의 P3/P5 경계를 그대로 승계).
  - **임계치·가중치 튜닝**(P4 곡선 결과로만), **`ERConfig.top_k` 스윕**(P1 §7 인계 12 — F-bdd6c5 로 무효).
  - **인물 간(A–B) 관계·감정 대화·상담**(원칙7), **일정 라벨 평가**(P10-final-eval, 결정 C).
  - **150건 데이터셋·최종 평가**(P10-final-eval). 40건은 "방향과 실패 유형"만 본다(P1 §7 인계 11).

## 산출물 (파일 경로)

경로의 최상위 디렉터리 이름은 **결정 A** 확정 전까지 잠정으로 `evaluation/` 로 적는다.

- evaluation/__init__.py — 패키지 선언(빈 파일 + 목적 docstring)
- evaluation/resolvers/__init__.py — `Resolver`·`MentionDecision`·`ResolverCandidate`·`get_resolver`·`ALL_METHODS` 재export
- evaluation/resolvers/base.py — 공통 타입·Protocol·`DECISIONS`·불변 규약 docstring
- evaluation/resolvers/registry.py — `RESOLVERS` 이름→팩토리 표, `get_resolver(name, **kw)`
- evaluation/resolvers/proposed.py — 제안 방식 어댑터(`app.er.resolve` 호출, `app/er/` 무수정)
- evaluation/resolvers/exact_match.py — 베이스라인 1(문자열 완전일치, 변형은 결정 C)
- evaluation/resolvers/embedding_only.py — 베이스라인 2(`search_candidates` + `band_for` 재사용)
- evaluation/resolvers/llm_single.py — 베이스라인 3(단일 구조화 출력 호출, 공급자 중립)
- evaluation/scenario_state.py — `seed_persons`+`aliases` 적재기, `gold_person_id` → `persons.id` 매핑
- scripts/baseline_smoke.py — 베이스라인 3 실호출 1회(키 있을 때만, 사용자 실행)
- tests/test_baseline_base.py — 공통 타입 계약(값 집합·frozen·`to_dict`·`person_id` 규약)
- tests/test_baseline_proposed.py — 어댑터 변환(밴드·점수·후보·trace_id·토큰), 실 DB 롤백 + `FakeJudge`
- tests/test_baseline_exact_match.py — 완전일치 판정·동명이인 2건 → `identity`·정규화 변형
- tests/test_baseline_embedding_only.py — `s_emb` 밴드 경계·`embedding_skipped` 처리(가짜 임베딩)
- tests/test_baseline_llm_single.py — 요청 스키마·응답 파싱·실패 분기·키 미노출(스텁 클라이언트, 네트워크 없음)
- tests/test_scenario_state.py — 적재 결과가 `seed_persons`+`aliases` 와 정확히 일치, 그 밖의 행 생성 0
- tests/test_baseline_parity.py — **네(또는 다섯) 방식 동일 하네스 호출**(수용 기준 증명)
- docs/wiki/packages/P3-baselines/evidence/ — pytest 출력·parity 단독 실행·부수효과 0 SQL 조회·스모크 출력
- docs/wiki/registry.md — 신규 행 추가(기존 행은 비고만)
- README.md — 베이스라인 실행법 절

## 작업 단위 (단위 하나 = 커밋 하나 후보. 끝나면 /commit)

- [x] U1 공통 인터페이스·방식 표: `evaluation/__init__.py`·`evaluation/resolvers/{__init__,base,registry}.py` — `DECISIONS`·`ResolverCandidate`·`MentionDecision`(`to_dict()` 포함)·`Resolver` Protocol·`supported_decisions`·`RESOLVERS`/`get_resolver`/`ALL_METHODS`. 불변 규약(부수효과 0·예외 비대칭 금지·`person_id` 는 merge 에서만·`config`=`ERConfig`)을 모듈 docstring 에 명문화한다. `tests/test_baseline_base.py` — `decision ∈ DECISIONS`, `merge` 아닌데 `person_id` 가 있으면 거부, `score` 범위 `[0,1]`, frozen, 알 수 없는 이름으로 `get_resolver` 호출 시 명확한 오류 / Refs: P3-baselines S3.7 D10 원칙2 원칙8
- [x] U2 제안 방식 어댑터: `evaluation/resolvers/proposed.py` — `app.er.resolve(ctx, mention, utterance, hints, judge=…, config=…)` 결과를 `MentionDecision` 으로 변환(`band`→`decision`, `confidence`→`score`, `candidates[].s_emb/s_rule`→`signals`, `trace_id`·`forced_reason`·`relaxed_retry`·`llm.provider/model`→`detail`, `llm.tokens_*`→`tokens_*`). `judge` 주입 경로를 팩토리 인자로 열어 둔다(테스트는 `FakeJudge`). `tests/test_baseline_proposed.py` — 세 밴드 각각이 그대로 옮겨지는지, `apply_resolution` 을 부르지 않아 `person_aliases`·`pending_questions` 행 수가 그대로인지, `app/` 변경 0(`git diff --name-only` 에 `app/` 없음) / Refs: P3-baselines S3.3 D3 D10 원칙1 원칙9
- [x] U3 베이스라인 1(문자열 완전일치): `evaluation/resolvers/exact_match.py` — 사전 상태 별칭·표시 이름 조회 + 완전일치 판정(순수 함수 `match_exact(mention, persons) -> list[int]` 와 DB 조회를 분리해 DB 없이도 단위 테스트 가능하게). 일치 1 → `merge`, 2 이상 → `identity`, 0 → `new_person`. 결정 C 대로 정규화 변형을 함께 등록한다면 `RESOLVERS` 에 두 이름으로 올린다. `tests/test_baseline_exact_match.py` — 동명이인 2건이 `identity` 로 가고 임의로 하나를 고르지 않는다(원칙1), 승진 호칭("부장님")은 사전 상태에 없으므로 `new_person`(P1 결정 I 가 만든 성질을 그대로 확인) / Refs: P3-baselines S3.7 원칙1 원칙8
- [x] U4 베이스라인 2(임베딩 단독): `evaluation/resolvers/embedding_only.py` — `app.er.candidates.search_candidates()` 재사용(별칭 top-K → 인물별 max, D5), 규칙·LLM 없이 `s_emb` 최고 후보에 `band_for()`(D10 두 임계치) 적용. `embedding_skipped`(공급자 없음) 이면 `s_emb=0` → `new_person` 이고 그 사실을 `detail.embedding_skipped` 에 남긴다. `tests/test_baseline_embedding_only.py` — 경계값(`s_emb` 가 정확히 `T_merge`·`T_new`), 후보 0건, `grouped_embedder` 로 통제한 유사도에서 "팀장↔부장님 > 팀장↔이모"(D4 검증 기준)가 밴드에 반영되는지 / Refs: P3-baselines S3.7 D4 D5 D10 원칙2
- [x] U5 베이스라인 3(LLM 단일 프롬프트): `evaluation/resolvers/llm_single.py` — 사전 상태 전체 인물 목록 + 발화를 한 번의 강제 구조화 출력으로 보내 `{decision, matched_person_id, s_llm, reason}` 을 받는다(공급자 중립: Claude·OpenAI, `LLM_PROVIDER`·`ANTHROPIC_MODEL` 재사용, temperature 0, 타임아웃·1회 재시도). 반환 `decision` 이 어휘 밖이거나 `matched_person_id` 가 사전 상태 밖이면 `identity` 로 강등하고 `detail.forced_reason` 에 이유를 남긴다(예외로 죽지 않는다). 키·프롬프트 원문 미출력. `scripts/baseline_smoke.py`(키 없으면 종료 코드 2). `tests/test_baseline_llm_single.py` — 스텁 클라이언트로 요청 본문·파싱·오류 매핑·강등·키 미노출(네트워크 0) / Refs: P3-baselines S3.7 D3 원칙4 원칙8
- [x] U6 시나리오 사전 상태 적재기: `evaluation/scenario_state.py` — `load_scenario_state(ctx, scenario) -> ScenarioState{person_id_map, created_person_ids}`. `seed_persons` 에 있는 인물만, `persons[].aliases` 를 그대로(추가·추론 금지, P1 결정 I), `events`·`schedules`·`pending_questions` 는 만들지 않는다. 임베딩 생성 여부는 결정 H. `tests/test_scenario_state.py` — 실제 `data/scenarios/*.json` 1건을 적재해 `persons`/`person_aliases` 행 수가 라벨과 정확히 일치하고 그 밖의 테이블 증가가 0 / Refs: P3-baselines P1-pilot-dataset D5 원칙8
- [x] U7 **동일 인터페이스 계약 테스트**(수용 기준): `tests/test_baseline_parity.py` — `@pytest.mark.parametrize("name", ALL_METHODS)` 로 네(결정 C 채택 시 다섯) 방식을 **같은 `ctx`·같은 mention·같은 utterance·같은 `ERConfig`** 로 호출해 (i) 반환이 `MentionDecision` 이고 (ii) `decision ∈ supported_decisions ⊆ DECISIONS` 이며 (iii) `merge` 일 때만 `person_id` 가 있고 (iv) 호출 전후 `persons`·`person_aliases`·`pending_questions` 행 수가 모두 같고 (v) 같은 입력을 두 번 호출하면 같은 결정이 나오는지(LLM 방식은 스텁으로 고정) 를 단언한다. 적재는 U6 을 쓴다 / Refs: P3-baselines S3.7 S3.3 D10 원칙8
- [x] U8 수용 기준 기계 검증 + 문서: 전체 `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs`, parity 단독 실행, 부수효과 0 을 보이는 SQL 조회 출력, `python scripts/tools_check.py` 7/7 유지(툴 시그니처 무변경), `POSTGRES_PORT=5433 python -m alembic check` 무변경, `python scripts/validate_scenarios.py --strict --json` rc=0(데이터 무변경 증거) 을 evidence 로 남긴다. `docs/wiki/registry.md` 신규 행, `README.md` 베이스라인 실행법 절 / Refs: P3-baselines S3.7 원칙8 원칙9

## 수용 기준 (`docs/backlog.md`의 해당 항목과 글자 그대로 같아야 한다)

- [eval-agent] 베이스라인 3종 (문자열 완전일치·임베딩 단독·LLM 단일 프롬프트) / 의존: P1 데이터셋 / 수용기준: 제안 방식과 동일 인터페이스로 호출 가능

  해석(기계 판정 방법, 위 문장을 바꾸지 않는다):
  - "베이스라인 3종" → `ALL_METHODS` 에 `exact_match`·`embedding_only`·`llm_single` 셋이 모두 있고 각각 `RESOLVERS` 팩토리로 인스턴스가 만들어진다(`tests/test_baseline_parity.py` 의 parametrize 목록이 그 셋 + `proposed` 를 포함).
  - "(문자열 완전일치·임베딩 단독·LLM 단일 프롬프트)" → 세 모듈이 각각 존재하고, 방식별 단위 테스트가 그 방식의 **정의**를 단언한다: 완전일치는 임베딩·LLM 호출 0회, 임베딩 단독은 LLM 호출 0회·규칙 필터 미사용, LLM 단일 프롬프트는 LLM 호출 **정확히 1회**(스텁 호출 카운터로 확인).
  - "의존: P1 데이터셋" → `tests/test_scenario_state.py`·`tests/test_baseline_parity.py` 가 `data/scenarios/` 실물 파일을 읽어 돈다(픽스처를 지어내지 않는다).
  - "제안 방식과 동일 인터페이스로 호출 가능" → `POSTGRES_PORT=5433 python -m pytest tests/test_baseline_parity.py -q -rs` 가 **같은 테스트 함수**에서 `proposed` 를 포함한 전 방식을 같은 인자로 호출해 통과한다(방식별 분기 `if name == …` 가 테스트 본문에 없다는 것도 함께 확인). 실패 시 이 수용 기준은 미충족이다.

## 판정 방법 (수용 기준을 기계적으로 확인하는 명령)

로컬 컨테이너는 5433 이므로 포트를 셸 변수로 넘긴다(`.env` 는 읽지 않는다, security.md §1).

| 무엇 | 명령 | 기대 출력 |
|------|------|-----------|
| **동일 인터페이스로 호출 가능** | `POSTGRES_PORT=5433 python -m pytest tests/test_baseline_parity.py -q -rs` | 전 방식 parametrize 통과, skip 0. 방식 수 = 4(결정 C 채택 시 5) |
| 방식 목록 | `python -c "from evaluation.resolvers import ALL_METHODS; print(ALL_METHODS)"` | `proposed`·`exact_match`·`embedding_only`·`llm_single` 포함 |
| 부수효과 0 | parity 테스트 안에서 `SELECT count(*) FROM persons/person_aliases/pending_questions` 호출 전후 비교 | 세 테이블 모두 증분 0(제안 방식만 `agent_traces` +1) — **정정 각주(04-review §2b, 판정 (a) 계획 문언 오차)**: 실측 `agent_traces` 증분은 `proposed` +2(`er_resolve`+`search_person`)·`embedding_only` +1(`search_person`)·나머지 0, evidence `20260911-1215-u8-side-effects.txt` |
| 베이스라인 정의 준수 | `python -m pytest tests/test_baseline_exact_match.py tests/test_baseline_embedding_only.py tests/test_baseline_llm_single.py -q` | 완전일치: 임베딩·LLM 호출 0 / 임베딩 단독: LLM 호출 0 / 단일 프롬프트: LLM 호출 1 |
| 제안 방식 무변경 | `git diff --name-only <U1 직전 해시>..HEAD -- app/` | 출력 0줄 — **예외(결정 J)**: `app/er/judge.py` 1건, diff 는 오류 매핑 함수의 공개 승격(이름)뿐 |
| 데이터셋 무변경 | `python scripts/validate_scenarios.py --strict --json` | rc=0, `total` 40·`counts` 5범주 그대로(원칙8 — 라벨을 고치지 않았다) |
| 스키마·툴 무변경 | `POSTGRES_PORT=5433 python -m alembic check` · `python scripts/tools_check.py` | `No new upgrade operations detected.` · `7/7 ok` |
| 실 LLM 1회(키 있을 때만 · 사용자 실행) | `python scripts/baseline_smoke.py` | `provider`·`model`·`decision`·`s_llm`·`tokens_*` 출력, 키·프롬프트 원문 미출력. 키 없으면 종료 코드 2 |
| 전체 | `POSTGRES_PORT=5433 python -m pytest tests/ -q -rs` | 기존 전건 + 신규 전부 통과, 실패 0, skip 0 |

- 증거 경로: `docs/wiki/packages/P3-baselines/evidence/`. Docker Desktop 이 꺼져 있거나 API 키가 없으면 **우회하지 않고** 사용자에게 명령을 보여 주고 멈춘다(security.md §6).

## 리스크 · 미결

**사용자 결정이 필요한 항목(결정은 메인 세션·사용자가 한다. U1 착수 전에 필요)**

- 결정 A — **코드 위치와 패키지 이름.** (i) `evaluation/` 최상위 패키지(**권장** — 평가 장치는 제품 런타임이 아니다. P4 러너·지표 계산기도 같은 패키지에 들어와 `app/` 을 깨끗하게 유지한다) / (ii) `eval/`(짧지만 파이썬 빌트인 `eval` 과 이름이 겹쳐 린터 경고·혼동 위험) / (iii) `app/baselines/`(제품 패키지에 평가 전용 코드가 섞인다). 어느 쪽이든 registry 에 새 최상위 항목이 생기므로 U1 커밋에서 등록한다.
- 결정 B — **베이스라인이 `identity`(=사람에게 묻는다)를 낼 수 있는가.** (i) 세 밴드 어휘를 공통으로 쓰되 방식마다 `supported_decisions` 로 실제로 낼 수 있는 집합을 선언한다(**권장** — 완전일치도 "동명이인 2건"에서는 고를 수 없으므로 `identity` 가 자연스럽고, 임의로 하나를 고르게 하면 오병합률이 인위적으로 부풀어 베이스라인을 약하게 만드는 셈이 된다, 원칙8) / (ii) 베이스라인은 `merge`/`new_person` 2값만 내고 `identity` 는 제안 방식 전용으로 둔다(대비는 선명해지지만 원칙8 위반 소지) / (iii) 방식마다 다르게(완전일치만 2값).
- 결정 C — **문자열 완전일치의 정규화 범위.** (i) 앞뒤 공백·대소문자만 정리한 순수 완전일치(**기본**) / (ii) `app.er.dictionary.normalize()`(님/씨 접미·성씨 1글자 접두 제거) 재사용 변형 — 호칭 사전은 제안 방식의 구성요소라 베이스라인 1 에 주면 "문자열 완전일치"라는 이름과 어긋나지만, 주지 않으면 베이스라인이 부당하게 약해진다 / (iii) **두 변형을 모두 구현해 `exact_match`·`exact_match_normalized` 두 이름으로 등록하고 P4 가 둘 다 보고한다**(**권장** — 둘 다 네트워크 0·비용 0 이고, 강한 변형을 함께 내는 것이 원칙8 이 요구하는 정직한 비교다).
- 결정 D — **임베딩 단독의 임계치.** (i) `T_merge`/`T_new` 두 임계치를 `s_emb` 에 그대로 적용하고 `band_for()` 를 재사용한다(**권장** — P4 곡선의 x축이 네 방식에 같은 의미를 갖는다) / (ii) 단일 임계치 τ 로 `merge`/`new_person` 2값 / (iii) 베이스라인 전용 τ 를 따로 두고 P4 가 별도 스윕(비교 축이 둘로 늘어 곡선 해석이 복잡해진다).
- 결정 E — **LLM 단일 프롬프트의 형태.** (i) `app/er/judge.py` 의 `ClaudeJudge`/`OpenAIJudge` 를 그대로 재사용하고 후보만 "전체 인물"로 바꾼다(코드 재사용 최대. 그러나 최종 결정은 여전히 바깥의 임계치 분기가 하므로 사실상 **부분 절제(ablation)** 이지 "LLM 단일 프롬프트"가 아니다) / (ii) 결정 어휘까지 LLM 이 한 번에 내는 별도 프롬프트를 새로 쓴다(**권장** — 원칙4 가 금지한 "LLM 한 번 부르고 끝"의 정확한 재현이고 S3.7 표의 의도다. 구조화 출력 스키마만 다르고 공급자 호출부는 같은 형태로 새 모듈에 둔다) / (iii) 둘 다 만들어 `llm_single`·`llm_judge_only` 두 이름으로 등록(비교는 풍부해지지만 P4 LLM 비용이 2배).
- 결정 F — **시나리오 사전 상태 적재기의 소유.** (i) 이 패키지가 최소 적재기를 만들고 P4 러너가 재사용한다(**권장** — parity 테스트가 실물 데이터로 돌려면 어차피 필요하고, P4 가 따로 만들면 테스트와 평가가 서로 다른 적재를 쓰게 된다) / (ii) P4 몫으로 미루고 이 패키지는 테스트 픽스처만 손으로 만든다(범위는 깨끗하지만 "동일 조건" 증명이 P4 까지 미뤄진다).
- 결정 G — **상태 저장소.** (i) 네 방식 모두 실 PostgreSQL 을 같은 `ToolContext` 로 공유한다(**권장** — 제안 방식이 DB·pgvector 를 요구하므로 베이스라인만 메모리로 돌리면 "동일 조건"이 성립하지 않는다) / (ii) 베이스라인은 메모리 인물 목록으로 돌리고 제안 방식만 DB(테스트는 빨라지지만 비교 전제가 깨진다).
- 결정 H — **적재 시 별칭 임베딩을 실제로 만드는가.** (i) 이 패키지의 테스트는 결정적 가짜 임베딩(`grouped_embedder`)으로만 돌고, 실제 OpenAI 임베딩 생성은 P4 실행 시점에 한다(**권장** — 여기서는 네트워크 0·비용 0 을 유지) / (ii) 적재기가 기본으로 실 임베딩을 만든다(테스트가 키·네트워크를 요구하게 되어 재현성이 떨어진다) / (iii) 적재기에 `embedder` 인자를 열어 두고 기본값은 `None`(사실상 (i) + P4 가 주입).

**결정 확정 — 사용자 (2026-09-10, 메인 세션 AskUserQuestion 2회, 전 항목 architect 권장안 채택)**

- 결정 A → (i) `evaluation/` 최상위 패키지. `app/` 은 제품 런타임만, 평가 장치(러너·지표 계산기 포함)는 전부 `evaluation/`.
- 결정 B → (i) 세 밴드 어휘(`merge`/`identity`/`new_person`) 공통 + 방식마다 `supported_decisions` 선언. 완전일치의 동명이인 2건 이상은 `identity`(임의 선택 금지, 원칙1·원칙8).
- 결정 C → (iii) 완전일치 두 변형 모두 등록 — `exact_raw`(공백·대소문자만)와 `exact_norm`(`app.er.dictionary.normalize()` 재사용). P4 가 둘 다 보고한다.
- 결정 D → (i) `T_merge`/`T_new` 를 `s_emb` 에 그대로 적용, `app.er.confidence.band_for()` 재사용. 전용 τ 스윕 없음.
- 결정 E → (ii) 결정까지 LLM 이 내는 **새 프롬프트**(후보 검색·규칙·확신도 결합 없음, 인물 목록 전체 제공, 구조화 출력 `{decision, matched_person_id, s_llm, reason}`). `ClaudeJudge` 재사용(ablation)은 하지 않는다. 공급자·모델은 제안 방식과 같은 환경변수.
- 결정 F → (i) 사전 상태 적재기 `evaluation/scenario_state.py` 는 이 패키지가 만들고 P4 러너가 재사용한다. 시나리오 사이 초기화는 P4.
- 결정 G → (i) 네 방식 모두 실 PostgreSQL 을 같은 `ToolContext` 로 공유(동일 조건).
- 결정 H → (i) 이 패키지 테스트는 결정적 가짜 임베딩만(네트워크 0). 실 임베딩 생성은 P4 실행 시. 적재기는 `embedder` 인자를 받는다.

**결정 확정 2 — 사용자 (2026-09-10, 계획 승인과 함께, verifier 02-plan-verify 권고 R-3·R-5)**

- 결정 I (R-3) → 베이스라인 3(`llm_single`)의 응답 스키마에 `candidate_person_ids: int[]` 를 추가한다. `decision="identity"` 일 때 그 배열(사전 상태 안의 id 만, 밖의 id 는 버리고 `detail.dropped_ids` 에 기록)이 `candidates` 가 된다. 비어 있으면 `forced_reason="identity_without_candidates"`. U5 에서 구현.
- 결정 J (R-5) → `app/er/judge.py` 의 `_call_with_error_mapping` 을 **공개 이름으로 승격**(밑줄 제거 또는 `__all__` 추가, 호출부 갱신 — 동작 무변경). **`app/` 변경은 이 1건뿐**이며 판정 표 "제안 방식 무변경" 행의 예외로 명시한다(`git diff --name-only … -- app/` 출력이 `app/er/judge.py` 1줄이고 diff 가 이름 변경뿐임을 evidence 로). 오류 어휘(`llm.error`)가 네 방식에 동일해진다. U5 에서 구현, 기존 `tests/test_er_judge.py` 무수정 통과가 조건.

**리스크(결정이 아니라 지켜볼 것)**

- **베이스라인을 약하게 만들 유혹**(원칙8, 이 패키지의 최대 위험). 각 방식은 "그 방식이 낼 수 있는 최선의 합리적 구현"이어야 한다 — 완전일치에 정규화 변형을 함께 두고(결정 C), 임베딩 단독에 두 임계치를 주고(결정 D), 단일 프롬프트에 사전 상태 **전체**를 보여 주고 제안 방식과 **같은 모델**을 쓰는 것이 그 표현이다. 반대 위험도 있다: 베이스라인이 제안 방식과 비슷하게 나오는 것도 **결과**이며, 그때 데이터·구현을 손대지 않고 실패 케이스 분석으로 간다(P4 미달 시 절차와 같다).
- **재현성**(원칙8). 베이스라인 3 은 LLM 호출이므로 같은 입력에 같은 출력이 보장되지 않는다. temperature 0 고정 + P4 가 응답을 `metrics.json`/캐시로 보존하는 것으로 완화하되, 이 패키지의 자동 테스트는 **전부 스텁**으로 결정적이어야 한다.
- **`app/er/` 무수정 원칙과 재사용의 경계.** `search_candidates`·`band_for`·`normalize` 는 공개 함수라 import 로 충분하다. 만약 private 함수(`_call_with_error_mapping` 등)가 필요해지면 **복제하지 말고** 멈춰 사용자 결정으로 올린다(중복 구현 금지, registry 규칙).
- **trace 비대칭.** 제안 방식만 `agent_traces` 행을 남기고 베이스라인은 남기지 않는다. P4 가 방식별 지표를 한 곳에서 읽으려 하면 어긋나므로, **`MentionDecision` 반환값이 방식별 원자료의 단일 출처**이고 그것을 어디에 적재할지는 P4 가 정한다(원칙9 는 제품 에이전트의 판정에 대한 요구이며 베이스라인은 제품이 아니다).
- **표본 크기 40건**(P1 §7 인계 11) — 이 패키지가 만드는 것은 배관이라 표본 수와 무관하지만, 수치 해석은 P4·P10 몫임을 04-review 에도 적는다.
- **비용.** 이 패키지는 **네트워크 호출 0**(스텁·가짜 임베딩)으로 끝난다. 실제 비용은 P4 실행 시 발생한다 — 40 시나리오 × mention × (제안 방식 1회 + 베이스라인 3 1회) LLM 호출 + 별칭·mention 임베딩. `P0-cost` 가 미착수이므로 **베이스라인 3 의 프롬프트 길이(사전 상태 전체 인물 목록)가 제안 방식보다 길다**는 사실을 P4 비용 추정에 넘긴다.
- **Windows 경로·인코딩** — 기존 테스트 관행(UTF-8, LF)을 그대로 따른다. 새 최상위 패키지가 생기므로 `pytest` 수집 경로·`sys.path` 는 저장소 루트 기준으로 동작하는지 U1 에서 확인한다(현재 저장소에 `pyproject.toml` 이 없다).

**P4-pilot-eval 로 넘기는 것**

1. 시나리오 사이 **DB 초기화**와 반복 실행(P1 §7 인계 1) — 적재기는 이 패키지, 초기화·러너는 P4.
2. **분모 규칙**: `ambiguous: true` mention 3개 제외, `passing_mentions` 6개 = 오탐 분자, `ask_user` 로 간 mention 은 제3 범주(P1 §7 인계 3·4·6).
3. **지표·곡선·보정표**: 오병합률·미검출률·F1·`ask_user_rate_by_kind`·`calibration`, x축 `T_merge` ∈ {0.5,…,0.95}·`T_new`=0.3 고정(S3.7, D10). `ERConfig(t_merge=…)` 인자 주입으로 네 방식 모두 스윕 가능하다는 것이 이 패키지의 인터페이스 약속이다. `top_k` 는 스윕하지 않는다(P1 §7 인계 12).
4. **`RESOLVERS` 이름 문자열 = `metrics.json` 키** — 방식 이름을 바꾸면 P4 산출물 스키마가 바뀐다.
5. **판정 모델별 재기록**(P1 §7 인계 8): 베이스라인 3 을 어느 공급자·모델로 돌렸는지 P4 evidence 에 적는다.
6. **실 임베딩·실 LLM 특성은 P4 가 처음 본다**(P3-er §7 과 같은 한계 — 이 패키지도 스텁까지만 검증한다).

## 읽은 카드

- `docs/wiki/INDEX.md` — 패키지 표(59~79행: `P3-baselines | 베이스라인 3종 | eval-agent | —`, "P4 이전에 P5 이후를 시작하지 않는다"), 태그 표
- `docs/wiki/CURRENT.md` — `active: none`, 메모(P1 완료·다음 후보)
- `.claude/gitlog.md` — 브랜치(dev 5b93dce, main 4f73b07, 승격 대기 1)·최근 커밋 20건(f78e9dc·5cac9bf·b3bcc2d·0527ab8 확인, L-001)
- `docs/wiki/specs/S3.7-eval-spec.md` — 전문(지표·곡선·"베이스라인 3종 + 제안 방식, 동일 데이터·동일 지표"·산출물)
- `docs/wiki/specs/S3.3-er-pipeline.md` — 전문(4단계 표·두 임계치·"LLM 단일 호출로 대체 금지")
- `docs/wiki/decisions/D03-confidence-formula.md`, `D04-embedding-provider.md`(확정 N=1536·`EmbeddingProvider` 인터페이스), `D05-alias-level-embedding.md`(별칭 top-K → 인물별 max), `D10-two-thresholds.md`(밴드 어휘·곡선 방향) — 전문, 특히 "코드에서 지켜야 할 것"
- `docs/wiki/registry.md` 75~94행(P3-er 모듈·테스트)·95~107행(P1 데이터셋·검증기) — 재사용 대상과 중복 금지 확인
- `docs/wiki/packages/P3-er/04-review.md` §7 — P4 인계(재계산 입력 계약·곡선 인자 주입·`top_k` 스윕 금지·실호출 미검증)
- `docs/wiki/packages/P1-pilot-dataset/04-review.md` §7 — P4 인계 1~13·P10 인계 1~5(적재 방식·분모 규칙·라벨 재해석 금지·표본 크기)
- `docs/wiki/packages/P3-er/01-plan.md` 1~129행 — 형식·작업 단위 크기·판정 방법 표 형식
- `docs/wiki/packages/P1-pilot-dataset/01-plan.md` 50~89행 — 수용 기준 "해석(기계 판정 방법)" 블록 형식, 결정 A~P
- `.claude/skills/eval-harness/SKILL.md` §2~§5 — 지표·베이스라인 3종 표·곡선·재현성/비용
- `docs/wiki/verification.md` — 증거로 인정하는 것, 계획 검증 기법 1~5
- `docs/wiki/templates/plan.md` — 이 문서의 형식
- `.claude/scripts/verify-plan.sh` — 기계 검증 항목(태그 카드 존재·단위마다 Refs·수용 기준 글자 일치·의존 완료·registry 중복)
- `app/er/types.py`(전문)·`app/er/pipeline.py` `resolve()` 시그니처·`app/er/candidates.py` `search_candidates()`·`app/er/judge.py` 공개 심볼·`app/tools/persons.py` `search_person()` 시그니처·`app/tools/context.py` `ToolContext` 필드 — 어댑터와 재사용 지점 확인(읽기만, 수정 없음)
- `docs/backlog.md` 38~45행 — P3·P4 항목 원문
- CLAUDE.md — 불변 원칙 1~9, 툴 7종 표, 개발 프로세스
- `docs/proposal.md` — 열지 않음(S3.7·S3.3 카드가 이번 결정에 필요한 문장을 모두 담고 있어 원문 참조가 필요 없었다)
