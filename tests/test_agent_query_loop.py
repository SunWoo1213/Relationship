"""Refs: P5b-query-turn CR-004 D16 S3.4 D1 D2 D10 원칙1 원칙2 원칙4 원칙7 원칙9 R19 --
U4 루프 조회 분기(`app/agent/loop.py::run_turn` -> `_run_query_turn`) 테스트.

`FakeProposer(intents=...)`·`FakeJudge`·`fake_embedder`·`FakeQueryAnswerer` 로
네트워크 0. 조회 턴은 **저장 0**이어야 한다 -- 모든 케이스가 `_counts()` 전후
비교(`assert_no_writes`)와 기록 툴 `tool_call` 행 0 을 함께 본다(identity 되묻기
질문 1행만 예외). 실 PostgreSQL(로컬 5433) 롤백 픽스처를 쓴다(`dbtest`).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select, text

import app.agent.loop as loop_module
from app.agent.loop import run_turn
from app.agent.propose import FakeProposer
from app.agent.respond import (
    QUERY_MORE_HINT,
    QUERY_ONE_AT_A_TIME_HINT,
    FakeQueryAnswerer,
    QueryAnswer,
    build_query_answer_prompt,
    no_mention_reply,
    no_record_reply,
    template_query_answer,
)
from app.api.read import get_person_card
from app.db.models import (
    ALIAS_SOURCES,
    AgentTrace,
    Event,
    PendingQuestion,
    Person,
    PersonAlias,
    PersonFact,
    Schedule,
)
from app.er.judge import FakeJudge
from app.settings import LOOP_MAX_MENTIONS, QUERY_TIMELINE_LIMIT
from app.tools.context import ToolContext
from sqlalchemy.exc import SQLAlchemyError

from app.agent.loop import resume_turn
from app.agent.types import ResumeInput
from app.api.deps import load_resume_input
from app.tools.questions import answer_question
from app.tools.types import PersonNotFound

pytestmark = pytest.mark.dbtest

WRITE_TOOL_NAMES = ("add_event", "add_schedule", "update_person", "create_person")
ANSWER_TEXT = "민수 팀장님과 최근에 식사를 했어요."
RAW_SECRET = "절대노출금지원문"


# ---------------------------------------------------------------------------
# 공용 헬퍼
# ---------------------------------------------------------------------------


def _counts(db_session, user_id: str) -> dict[str, int]:
    """저장 0 단언용 -- 7개 테이블의 (이 사용자) 행 수. `pending_questions` 는
    사용자 열이 없어 전체 행 수다(롤백 픽스처라 전후 비교에는 충분하다)."""

    def one(sql: str) -> int:
        return db_session.execute(text(sql), {"u": user_id}).scalar_one()

    return {
        "persons": one("SELECT count(*) FROM persons WHERE user_id = :u"),
        "person_aliases": one(
            "SELECT count(*) FROM person_aliases a JOIN persons p ON p.id = a.person_id "
            "WHERE p.user_id = :u"
        ),
        "events": one(
            "SELECT count(*) FROM events e JOIN persons p ON p.id = e.person_id WHERE p.user_id = :u"
        ),
        "schedules": one(
            "SELECT count(*) FROM schedules s JOIN persons p ON p.id = s.person_id "
            "WHERE p.user_id = :u"
        ),
        "person_facts": one(
            "SELECT count(*) FROM person_facts f JOIN persons p ON p.id = f.person_id "
            "WHERE p.user_id = :u"
        ),
        "fact_sources": one(
            "SELECT count(*) FROM fact_sources s JOIN person_facts f ON f.id = s.fact_id "
            "JOIN persons p ON p.id = f.person_id WHERE p.user_id = :u"
        ),
        "pending_questions": db_session.execute(
            text("SELECT count(*) FROM pending_questions")
        ).scalar_one(),
    }


def assert_no_writes(before: dict[str, int], after: dict[str, int]) -> None:
    assert after == before


def _make_person(db_session, display_name: str, *, user_id: str = "local") -> Person:
    person = Person(
        user_id=user_id, display_name=display_name, relation_tag="직장", hierarchy="동"
    )
    db_session.add(person)
    db_session.flush()
    return person


def _add_alias(db_session, person: Person, alias: str, fake_embedder) -> None:
    db_session.add(
        PersonAlias(
            person_id=person.id,
            alias=alias,
            source=ALIAS_SOURCES[0],
            embedding=fake_embedder([alias])[0],
        )
    )
    db_session.flush()


def _seed_person(
    db_session,
    fake_embedder,
    *,
    name: str = "김민수",
    alias: str = "팀장",
    events: int = 8,
    facts: int = 3,
    schedules: int = 2,
    raw: str = "원문",
) -> Person:
    person = _make_person(db_session, name)
    _add_alias(db_session, person, alias, fake_embedder)
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(events):
        db_session.add(
            Event(
                person_id=person.id,
                type="meal",
                content=f"식사{i}",
                raw_utterance=raw,
                occurred_at=base + timedelta(days=i),
            )
        )
    for i in range(facts):
        db_session.add(PersonFact(person_id=person.id, key=f"k{i}", value=f"v{i}", confidence=0.9))
    future = datetime.now(timezone.utc) + timedelta(days=3)
    for i in range(schedules):
        db_session.add(
            Schedule(person_id=person.id, title=f"일정{i}", scheduled_at=future + timedelta(days=i))
        )
    db_session.flush()
    return person


@dataclass
class _RecordingAnswerer(FakeQueryAnswerer):
    """`FakeQueryAnswerer` + 받은 입력(프롬프트 user_text)을 남긴다."""

    seen: list[str] = field(default_factory=list)

    def answer(self, question, evidence, now):
        self.seen.append(build_query_answer_prompt(question, evidence, now)[1])
        return super().answer(question, evidence, now)


class _ByMentionJudge:
    """언급 문자열별로 연결할 인물을 정하는 결정적 판정기(없으면 s_llm 0)."""

    def __init__(self, by_mention: dict[str, int]):
        self.by_mention = by_mention

    def judge(self, mention, utterance, candidates):
        pid = self.by_mention.get(mention)
        judge = FakeJudge(table={pid: 0.95}) if pid is not None else FakeJudge()
        return judge.judge(mention, utterance, candidates)


def _queries(*mentions: str, tool: str = "search_person"):
    key = "query" if tool == "search_person" else "person"
    return [{"name": tool, "args": {key: m}} for m in mentions]


def _run(
    db_session,
    fake_embedder,
    utterance: str,
    calls,
    *,
    judge=None,
    answerer=None,
    session_id: str = "q-u4",
    intent: str | None = "query",
    **kw,
):
    ctx = ToolContext(session=db_session, session_id=session_id, embedder=fake_embedder)
    intents = {utterance: intent} if intent is not None else {}
    proposer = FakeProposer(table={utterance: calls}, intents=intents)
    result = run_turn(
        ctx, utterance, proposer=proposer, judge=judge, answerer=answerer, **kw
    )
    return result, ctx


def _rows(db_session, session_id: str, step: str) -> list[AgentTrace]:
    return (
        db_session.execute(
            select(AgentTrace)
            .where(AgentTrace.session_id == session_id, AgentTrace.step == step)
            .order_by(AgentTrace.id)
        )
        .scalars()
        .all()
    )


def _write_tool_rows(db_session, session_id: str) -> int:
    return db_session.execute(
        text(
            "SELECT count(*) FROM agent_traces WHERE session_id = :s AND step = 'tool_call' "
            "AND tool_name IN ('add_event','add_schedule','update_person','create_person')"
        ),
        {"s": session_id},
    ).scalar_one()


def _query_out(db_session, session_id: str) -> dict:
    rows = _rows(db_session, session_id, "loop_query")
    assert len(rows) == 1
    return rows[0].output


def _template_for(db_session, person: Person) -> str:
    now = datetime.now(timezone.utc)
    return template_query_answer(get_person_card(db_session, "local", person.id, now), now)


# ---------------------------------------------------------------------------
# (a) merge -- 카드 근거로 답하고 저장 0
# ---------------------------------------------------------------------------


def test_a_merge_answers_from_card_and_writes_nothing(db_session, fake_embedder, monkeypatch):
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분이었지?"
    answerer = _RecordingAnswerer(table={utt: ANSWER_TEXT})
    spy_calls: list[int] = []
    import app.api.read as read_module

    real = read_module.get_person_card
    monkeypatch.setattr(
        read_module,
        "get_person_card",
        lambda *a, **k: (spy_calls.append(a[2]), real(*a, **k))[1],
    )
    before = _counts(db_session, "local")

    result, ctx = _run(
        db_session,
        fake_embedder,
        utt,
        _queries("팀장"),
        judge=FakeJudge(table={person.id: 0.95}),
        answerer=answerer,
        session_id="q-a",
    )

    assert_no_writes(before, _counts(db_session, "local"))
    assert _write_tool_rows(db_session, "q-a") == 0
    assert spy_calls == [person.id]
    assert result.reply == f"{ANSWER_TEXT}\n{QUERY_MORE_HINT}"
    assert result.stored.to_dict() == {"persons": 0, "events": 0, "schedules": 0}
    assert result.pending_question is None
    out = _query_out(db_session, "q-a")
    assert out["answer_source"] == "llm"
    assert out["person_id"] == person.id
    assert out["evidence_counts"] == {"facts": 3, "patterns": 0, "timeline": 5, "schedules": 2}
    # 답 생성기가 받은 입력(U3 프롬프트 층을 거친 user_text): 타임라인 <= 5, 사실·일정 전부
    assert answerer.call_count == 1
    seen = answerer.seen[0]
    assert sum(1 for ln in seen.splitlines() if ln.startswith("- [meal]")) == QUERY_TIMELINE_LIMIT
    assert sum(1 for ln in seen.splitlines() if ln.startswith("- k")) == 3
    assert sum(1 for ln in seen.splitlines() if ln.startswith("- 일정")) == 2
    # ER 은 resolve 만 -- 적용 안 함(결정 I (a))
    er = _rows(db_session, "q-a", "er_resolve")[0].output
    assert er["decision"]["applied"] is False
    assert out["resolutions"][0]["applied"] is False
    assert out["resolutions"][0]["er_trace_id"] == _rows(db_session, "q-a", "er_resolve")[0].id
    # trace_ids = [extract, gate, query]
    assert result.trace_ids == [
        _rows(db_session, "q-a", "loop_extract")[0].id,
        _rows(db_session, "q-a", "loop_gate")[0].id,
        _rows(db_session, "q-a", "loop_query")[0].id,
    ]
    assert len(_rows(db_session, "q-a", "loop_turn")) == 1
    assert _rows(db_session, "q-a", "loop_record") == []


# ---------------------------------------------------------------------------
# (b) 빈 DB -- new_person: 질문 행 0, ask_user 0
# ---------------------------------------------------------------------------


def test_b_new_person_asks_nothing_and_says_no_record(db_session, fake_embedder):
    answerer = FakeQueryAnswerer()
    before = _counts(db_session, "local")

    result, _ = _run(
        db_session,
        fake_embedder,
        "김철수 어떤 사람이야?",
        _queries("김철수"),
        judge=FakeJudge(),
        answerer=answerer,
        session_id="q-b",
    )

    assert_no_writes(before, _counts(db_session, "local"))
    assert (
        db_session.execute(
            text("SELECT count(*) FROM agent_traces WHERE session_id='q-b' AND tool_name='ask_user'")
        ).scalar_one()
        == 0
    )
    assert result.reply == no_record_reply(["김철수"])
    assert result.pending_question is None
    assert answerer.call_count == 0
    out = _query_out(db_session, "q-b")
    assert out["answer_source"] == "no_record"
    assert out["resolutions"][0]["band"] == "new_person"
    assert out["resolutions"][0]["applied"] is False
    assert out["person_id"] is None


# ---------------------------------------------------------------------------
# (c) 후보 2명 동점 -- identity 되묻기
# ---------------------------------------------------------------------------


def test_c_identity_asks_with_query_resume(db_session, fake_embedder):
    a = _make_person(db_session, "김민수")
    b = _make_person(db_session, "김민호")
    _add_alias(db_session, a, "팀장", fake_embedder)
    _add_alias(db_session, b, "팀장", fake_embedder)
    utt = "팀장님 어떤 분?"
    calls = _queries("팀장")
    answerer = FakeQueryAnswerer()
    judge = FakeJudge(fail="timeout")  # 판정 실패 -> 규칙 통과 후보가 있으면 identity

    # ER 원본 options 는 같은 입력의 resolve() 결과에서 읽는다.
    er_ctx = ToolContext(session=db_session, session_id="q-c-er", embedder=fake_embedder)
    original = loop_module.resolve(er_ctx, "팀장", utt, None, judge=judge)
    assert original.band == "identity"
    before = _counts(db_session, "local")

    result, _ = _run(
        db_session, fake_embedder, utt, calls, judge=judge, answerer=answerer, session_id="q-c"
    )

    after = _counts(db_session, "local")
    assert after["pending_questions"] == before["pending_questions"] + 1
    assert {k: v for k, v in after.items() if k != "pending_questions"} == {
        k: v for k, v in before.items() if k != "pending_questions"
    }
    assert result.stop_reason == "ask_user"
    assert result.pending_question is not None
    assert result.pending_question.kind == "identity"
    assert result.pending_question.options == original.ask_payload["options"]
    assert result.reply == result.pending_question.question
    row = db_session.get(PendingQuestion, result.pending_question.question_id)
    assert row.context["resume"]["intent"] == "query"
    assert row.context["resume"]["pending_calls"] == []
    assert row.options == original.ask_payload["options"]
    assert answerer.call_count == 0
    out = _query_out(db_session, "q-c")
    assert out["answer_source"] == "ask"
    assert out["person_id"] is None
    assert out["resolutions"][0]["applied"] is True
    assert out["resolutions"][0]["question_id"] == row.id
    assert _write_tool_rows(db_session, "q-c") == 0


# ---------------------------------------------------------------------------
# (d) 금지 표현 / (e) 공급자 오류 -- 템플릿 폴백
# ---------------------------------------------------------------------------


def test_d_forbidden_expression_falls_back_to_template(db_session, fake_embedder):
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 요즘 어때?"
    bad = "요즘 많이 힘들어 보여요"

    result, _ = _run(
        db_session,
        fake_embedder,
        utt,
        _queries("팀장"),
        judge=FakeJudge(table={person.id: 0.95}),
        answerer=FakeQueryAnswerer(table={utt: bad}),
        session_id="q-d",
    )

    assert result.reply == _template_for(db_session, person)
    out = _query_out(db_session, "q-d")
    assert out["answer_source"] == "template"
    assert out["fallback_reason"] == "forbidden_expression"
    assert out["rejected_answer"] == bad


def test_e_answerer_unavailable_falls_back_without_raising(db_session, fake_embedder):
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분?"

    result, _ = _run(
        db_session,
        fake_embedder,
        utt,
        _queries("팀장"),
        judge=FakeJudge(table={person.id: 0.95}),
        answerer=FakeQueryAnswerer(fail="timeout"),
        session_id="q-e",
    )

    assert result.reply == _template_for(db_session, person)
    out = _query_out(db_session, "q-e")
    assert out["answer_source"] == "template"
    assert out["fallback_reason"] == "answerer_error:timeout"
    assert out["rejected_answer"] is None
    assert _rows(db_session, "q-e", "loop_error") == []
    assert _rows(db_session, "q-e", "tool_error") == []


# ---------------------------------------------------------------------------
# (f) 근거 0건 -- LLM 호출 0
# ---------------------------------------------------------------------------


def test_f_no_evidence_skips_llm(db_session, fake_embedder):
    person = _seed_person(db_session, fake_embedder, events=0, facts=0, schedules=0)
    utt = "팀장님 어떤 분?"
    answerer = FakeQueryAnswerer(table={utt: ANSWER_TEXT})

    result, _ = _run(
        db_session,
        fake_embedder,
        utt,
        _queries("팀장"),
        judge=FakeJudge(table={person.id: 0.95}),
        answerer=answerer,
        session_id="q-f",
    )

    assert answerer.call_count == 0
    assert result.reply == _template_for(db_session, person)
    out = _query_out(db_session, "q-f")
    assert out["answer_source"] == "template"
    assert out["fallback_reason"] == "no_evidence"
    assert out["evidence_counts"] == {"facts": 0, "patterns": 0, "timeline": 0, "schedules": 0}
    assert (out_tokens := db_session.execute(
        select(AgentTrace.tokens_in, AgentTrace.tokens_out).where(
            AgentTrace.session_id == "q-f", AgentTrace.step == "loop_query"
        )
    ).one()) == (0, 0), out_tokens


# ---------------------------------------------------------------------------
# (g) 혼합 발화 -- 기록 제안은 실행 0
# ---------------------------------------------------------------------------


def test_g_mixed_utterance_does_not_execute_write(db_session, fake_embedder):
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분이야? 어제 같이 점심 먹었어"
    calls = [
        {"name": "search_person", "args": {"query": "팀장"}},
        {
            "name": "add_event",
            "args": {
                "person": "팀장",
                "type": "meal",
                "content": "점심",
                "occurred_at": datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc).isoformat(),
            },
        },
    ]
    before = _counts(db_session, "local")

    result, _ = _run(
        db_session,
        fake_embedder,
        utt,
        calls,
        judge=FakeJudge(table={person.id: 0.95}),
        answerer=FakeQueryAnswerer(table={utt: ANSWER_TEXT}),
        session_id="q-g",
    )

    assert_no_writes(before, _counts(db_session, "local"))
    assert _write_tool_rows(db_session, "q-g") == 0
    gate = _rows(db_session, "q-g", "loop_gate")[0].output
    assert {"index": 1, "name": "add_event", "reason": "query_turn_no_write"} in gate["rejected"]
    assert result.stored.events == 0


# ---------------------------------------------------------------------------
# (h) trace 368 재현 -- 호칭 + "나" 가 함께 오는 제안
# ---------------------------------------------------------------------------


def test_h_trace368_title_then_me_resolves_first_only(db_session, fake_embedder, monkeypatch):
    person = _seed_person(db_session, fake_embedder, alias="박선우 과장님", name="박선우")
    utt = "박선우 과장님에 대해 알려줘"
    resolved: list[str] = []
    real = loop_module.resolve
    monkeypatch.setattr(
        loop_module, "resolve", lambda ctx, m, *a, **k: (resolved.append(m), real(ctx, m, *a, **k))[1]
    )
    before = _counts(db_session, "local")

    result, _ = _run(
        db_session,
        fake_embedder,
        utt,
        _queries("박선우 과장님", "나"),
        judge=FakeJudge(table={person.id: 0.95}),
        answerer=FakeQueryAnswerer(table={utt: ANSWER_TEXT}),
        session_id="q-h",
    )

    assert_no_writes(before, _counts(db_session, "local"))
    assert resolved == ["박선우 과장님"]  # 결정 J -- merge 뒤 남은 언급은 해석하지 않는다
    out = _query_out(db_session, "q-h")
    assert out["mentions"] == ["박선우 과장님", "나"]
    assert out["mentions_dropped"] == 1
    assert out["person_id"] == person.id
    assert result.reply.splitlines()[-2:] == [QUERY_ONE_AT_A_TIME_HINT, QUERY_MORE_HINT]


def test_h2_me_first_asks_identity_and_stops(db_session, fake_embedder, monkeypatch):
    """"나" 가 먼저 와도(후보가 있고 판정이 못 고르면 identity) 그 자리에서 되묻고
    턴을 끝낸다 -- 뒤 언급은 해석하지 않는다(결정 J). 루프는 확신도를 읽지 않는다."""
    person = _seed_person(db_session, fake_embedder, alias="박선우 과장님", name="박선우")
    utt = "나랑 박선우 과장님 이야기"
    resolved: list[str] = []
    real = loop_module.resolve
    monkeypatch.setattr(
        loop_module, "resolve", lambda ctx, m, *a, **k: (resolved.append(m), real(ctx, m, *a, **k))[1]
    )
    before = _counts(db_session, "local")

    result, _ = _run(
        db_session,
        fake_embedder,
        utt,
        _queries("나", "박선우 과장님"),
        judge=_ByMentionJudge({"박선우 과장님": person.id}),
        answerer=FakeQueryAnswerer(table={utt: ANSWER_TEXT}),
        session_id="q-h2",
    )

    after = _counts(db_session, "local")
    assert after["pending_questions"] == before["pending_questions"] + 1
    assert resolved == ["나"]
    out = _query_out(db_session, "q-h2")
    assert out["answer_source"] == "ask"
    assert out["mentions_dropped"] == 1
    assert QUERY_ONE_AT_A_TIME_HINT not in result.reply  # ask 에는 붙이지 않는다
    assert result.stop_reason == "ask_user"


def test_h3_mention_source_rule(db_session, fake_embedder):
    """결정 B-3 (b): search_person 은 query, 그 밖은 person; strip·빈 값 제외·중복 제거."""
    from app.agent.types import Proposal, ToolCallProposal

    proposal = Proposal(
        tool_calls=[
            ToolCallProposal(name="search_person", args={"query": " 가 "}),
            ToolCallProposal(name="add_event", args={"person": "나"}),
            ToolCallProposal(name="search_person", args={"query": "가"}),
            ToolCallProposal(name="search_person", args={"query": "  "}),
            ToolCallProposal(name="search_person", args={"person": "무시"}),
            ToolCallProposal(name="add_schedule", args={"person": "다"}),
        ],
        raw={},
    )
    assert loop_module._query_mentions(proposal) == ["가", "나", "다"]


# ---------------------------------------------------------------------------
# (i) 언급 0 / (m) R-U3-2
# ---------------------------------------------------------------------------


def test_i_m_no_mention(db_session, fake_embedder, monkeypatch):
    called: list[list[str]] = []
    monkeypatch.setattr(loop_module, "no_record_reply", lambda m: called.append(m) or "X")
    resolved: list[str] = []
    monkeypatch.setattr(loop_module, "resolve", lambda *a, **k: resolved.append("x"))
    answerer = FakeQueryAnswerer()
    before = _counts(db_session, "local")

    result, _ = _run(
        db_session, fake_embedder, "그분 어때?", [], judge=FakeJudge(), answerer=answerer, session_id="q-i"
    )

    assert_no_writes(before, _counts(db_session, "local"))
    assert result.reply == no_mention_reply()
    assert called == []  # R-U3-2 -- no_record_reply([]) 를 부르지 않는다
    assert resolved == []
    assert answerer.call_count == 0
    out = _query_out(db_session, "q-i")
    assert out["answer_source"] == "no_mention"
    assert out["mentions"] == []
    assert out["mentions_dropped"] == 0


# ---------------------------------------------------------------------------
# (j) 기록 턴은 조회 분기를 타지 않는다
# ---------------------------------------------------------------------------


def test_j_record_turn_does_not_enter_query_branch(db_session, fake_embedder, monkeypatch):
    person = _seed_person(db_session, fake_embedder, events=0, facts=0, schedules=0)
    entered: list[int] = []
    monkeypatch.setattr(loop_module, "_run_query_turn", lambda *a, **k: entered.append(1))
    utt = "어제 팀장이랑 저녁 먹었어"
    calls = [
        {
            "name": "add_event",
            "args": {
                "person": "팀장",
                "type": "meal",
                "content": "저녁",
                "occurred_at": datetime(2026, 9, 23, 19, 0, tzinfo=timezone.utc).isoformat(),
            },
        }
    ]

    result, _ = _run(
        db_session,
        fake_embedder,
        utt,
        calls,
        judge=FakeJudge(table={person.id: 0.95}),
        intent=None,
        session_id="q-j",
    )

    assert entered == []
    assert result.stored.events == 1
    assert _rows(db_session, "q-j", "loop_query") == []
    assert len(_rows(db_session, "q-j", "loop_record")) == 1


# ---------------------------------------------------------------------------
# (k) loop_query 스키마
# ---------------------------------------------------------------------------


def test_k_loop_query_output_schema(db_session, fake_embedder):
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분?"

    _run(
        db_session,
        fake_embedder,
        utt,
        _queries("팀장"),
        judge=FakeJudge(table={person.id: 0.95}),
        answerer=FakeQueryAnswerer(table={utt: ANSWER_TEXT}),
        session_id="q-k",
    )

    out = _query_out(db_session, "q-k")
    assert set(out) == {
        "intent",
        "mentions",
        "mentions_dropped",
        "resolutions",
        "person_id",
        "evidence_counts",
        "answer_source",
        "fallback_reason",
        "rejected_answer",
        "reply",
    }
    assert out["intent"] == "query"
    assert set(out["resolutions"][0]) == {
        "mention",
        "band",
        "person_id",
        "er_trace_id",
        "applied",
        "question_id",
    }
    assert set(out["evidence_counts"]) == {"facts", "patterns", "timeline", "schedules"}
    assert out["answer_source"] in {"llm", "template", "no_record", "no_mention", "ask"}
    row = _rows(db_session, "q-k", "loop_query")[0]
    assert row.tool_name == "agent"


def test_k2_tokens_come_from_answer(db_session, fake_embedder):
    """`trace_tokens()` 가 loop_query 행의 tokens_in/out 이 된다."""
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분?"

    class _Tok(FakeQueryAnswerer):
        def answer(self, question, evidence, now):
            return QueryAnswer(text=ANSWER_TEXT, tokens_in=11, tokens_out=7)

    _run(
        db_session,
        fake_embedder,
        utt,
        _queries("팀장"),
        judge=FakeJudge(table={person.id: 0.95}),
        answerer=_Tok(),
        session_id="q-k2",
    )

    row = _rows(db_session, "q-k2", "loop_query")[0]
    assert (row.tokens_in, row.tokens_out) == (11, 7)


# ---------------------------------------------------------------------------
# (l) R-U3-1 원문 비노출
# ---------------------------------------------------------------------------


def test_l_raw_utterance_never_exposed(db_session, fake_embedder):
    person = _seed_person(db_session, fake_embedder, raw=RAW_SECRET)
    utt = "팀장님 어떤 분?"
    answerer = _RecordingAnswerer(table={utt: ANSWER_TEXT})

    result, _ = _run(
        db_session,
        fake_embedder,
        utt,
        _queries("팀장"),
        judge=FakeJudge(table={person.id: 0.95}),
        answerer=answerer,
        session_id="q-l",
    )

    assert RAW_SECRET not in result.reply
    assert RAW_SECRET not in json.dumps(_query_out(db_session, "q-l"), ensure_ascii=False)
    assert answerer.seen and all(RAW_SECRET not in s for s in answerer.seen)


# ---------------------------------------------------------------------------
# (n) QUERY_MORE_HINT 는 llm 답에만
# ---------------------------------------------------------------------------


def test_n_more_hint_only_on_llm(db_session, fake_embedder):
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분?"
    judge = FakeJudge(table={person.id: 0.95})

    llm, _ = _run(
        db_session, fake_embedder, utt, _queries("팀장"), judge=judge,
        answerer=FakeQueryAnswerer(table={utt: ANSWER_TEXT}), session_id="q-n1",
    )
    tmpl, _ = _run(
        db_session, fake_embedder, utt, _queries("팀장"), judge=judge,
        answerer=FakeQueryAnswerer(fail="timeout"), session_id="q-n2",
    )
    none, _ = _run(
        db_session, fake_embedder, "김철수?", _queries("김철수"), judge=FakeJudge(),
        answerer=FakeQueryAnswerer(), session_id="q-n3",
    )

    assert llm.reply.endswith(f"\n{QUERY_MORE_HINT}") and llm.reply.count(QUERY_MORE_HINT) == 1
    assert tmpl.reply == _template_for(db_session, person)  # 템플릿은 자기 문구뿐 -- 루프가 더 붙이지 않는다
    assert tmpl.reply.count(QUERY_MORE_HINT) == 1
    assert QUERY_MORE_HINT not in none.reply


# ---------------------------------------------------------------------------
# (o) merge 뒤 남은 언급 / (p) 상한
# ---------------------------------------------------------------------------


def test_o_remaining_mentions_after_merge_are_not_resolved(db_session, fake_embedder, monkeypatch):
    p1 = _seed_person(db_session, fake_embedder, name="김민수", alias="팀장")
    _add_alias(db_session, _make_person(db_session, "이영희"), "과장", fake_embedder)
    utt = "팀장이랑 과장 어떤 분들?"
    resolved: list[str] = []
    real = loop_module.resolve
    monkeypatch.setattr(
        loop_module, "resolve", lambda ctx, m, *a, **k: (resolved.append(m), real(ctx, m, *a, **k))[1]
    )

    result, _ = _run(
        db_session, fake_embedder, utt, _queries("팀장", "과장"),
        judge=FakeJudge(table={p1.id: 0.95}), answerer=FakeQueryAnswerer(table={utt: ANSWER_TEXT}),
        session_id="q-o",
    )

    assert resolved == ["팀장"]
    out = _query_out(db_session, "q-o")
    assert out["mentions_dropped"] == 1
    assert result.reply.splitlines()[-2] == QUERY_ONE_AT_A_TIME_HINT
    assert result.reply.splitlines()[-1] == QUERY_MORE_HINT


def test_p_mention_cap(db_session, fake_embedder, monkeypatch):
    resolved: list[str] = []
    real = loop_module.resolve
    monkeypatch.setattr(
        loop_module, "resolve", lambda ctx, m, *a, **k: (resolved.append(m), real(ctx, m, *a, **k))[1]
    )
    names = [f"낯선{i}" for i in range(LOOP_MAX_MENTIONS + 1)]
    utt = "다들 누구야?"
    before = _counts(db_session, "local")

    result, _ = _run(
        db_session, fake_embedder, utt, _queries(*names), judge=FakeJudge(),
        answerer=FakeQueryAnswerer(), session_id="q-p",
    )

    assert_no_writes(before, _counts(db_session, "local"))
    assert resolved == names[:LOOP_MAX_MENTIONS]
    out = _query_out(db_session, "q-p")
    assert out["mentions_dropped"] == 1
    assert len(out["mentions"]) == LOOP_MAX_MENTIONS + 1
    assert result.reply == (
        f"{no_record_reply(names[:LOOP_MAX_MENTIONS])}\n{QUERY_ONE_AT_A_TIME_HINT}"
    )


# ---------------------------------------------------------------------------
# (q) stop_reason
# ---------------------------------------------------------------------------


def test_q_answered_turn_stop_reason_is_none(db_session, fake_embedder):
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분?"

    result, _ = _run(
        db_session, fake_embedder, utt, _queries("팀장"), judge=FakeJudge(table={person.id: 0.95}),
        answerer=FakeQueryAnswerer(table={utt: ANSWER_TEXT}), session_id="q-q",
    )

    assert result.stop_reason is None
    assert result.reply.strip()


# ---------------------------------------------------------------------------
# (r)(s) answerer=None -- 지연 해소 (결정 K R-1)
# ---------------------------------------------------------------------------


def test_r_lazy_resolution_not_called_without_evidence(db_session, fake_embedder, monkeypatch):
    person = _seed_person(db_session, fake_embedder, events=0, facts=0, schedules=0)
    called: list[int] = []
    monkeypatch.setattr(
        "app.agent.respond.answerer_from_env", lambda env=None: called.append(1) or None
    )

    result, _ = _run(
        db_session, fake_embedder, "팀장님 어떤 분?", _queries("팀장"),
        judge=FakeJudge(table={person.id: 0.95}), session_id="q-r",
    )

    assert called == []
    assert result.reply == _template_for(db_session, person)


def test_s_lazy_resolution_uses_module_attribute(db_session, fake_embedder, monkeypatch):
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분?"
    monkeypatch.setattr(
        "app.agent.respond.answerer_from_env",
        lambda env=None: FakeQueryAnswerer(table={utt: ANSWER_TEXT}),
    )

    result, _ = _run(
        db_session, fake_embedder, utt, _queries("팀장"),
        judge=FakeJudge(table={person.id: 0.95}), session_id="q-s",
    )

    assert result.reply == f"{ANSWER_TEXT}\n{QUERY_MORE_HINT}"
    assert _query_out(db_session, "q-s")["answer_source"] == "llm"


# ---------------------------------------------------------------------------
# 부정: 조회 턴에서 부르지 않는 것
# ---------------------------------------------------------------------------


def test_forbidden_callees_are_never_called(db_session, fake_embedder, monkeypatch):
    person = _seed_person(db_session, fake_embedder)

    def boom(*a, **k):
        raise AssertionError("조회 턴이 부르면 안 되는 함수")

    for name in ("resolve_mentions", "_record", "_record_impl", "after_record", "apply_resolution"):
        monkeypatch.setattr(loop_module, name, boom)
    for tool in ("add_event", "add_schedule", "update_person", "create_person"):
        monkeypatch.setattr(loop_module.app_tools, tool, boom)
    utt = "팀장님 어떤 분?"

    result, _ = _run(
        db_session, fake_embedder, utt, _queries("팀장"), judge=FakeJudge(table={person.id: 0.95}),
        answerer=FakeQueryAnswerer(table={utt: ANSWER_TEXT}), session_id="q-neg",
    )

    assert result.reply.startswith(ANSWER_TEXT)


def test_other_user_person_is_not_visible(db_session, fake_embedder):
    """다른 사용자 소유 인물은 같은 별칭이어도 후보가 되지 않아 기록 없음이다."""
    other = _make_person(db_session, "남의사람", user_id="other-user")
    _add_alias(db_session, other, "팀장", fake_embedder)
    answerer = FakeQueryAnswerer()

    result, _ = _run(
        db_session, fake_embedder, "팀장님?", _queries("팀장"), judge=FakeJudge(table={other.id: 0.95}),
        answerer=answerer, session_id="q-user",
    )

    assert result.reply == no_record_reply(["팀장"])
    assert answerer.call_count == 0


# ===========================================================================
# U5 -- 재개(`resume_turn`): 조회 턴 identity 되묻기 뒤 답하기 (결정 G (a))
# ===========================================================================


def _ask_identity(db_session, fake_embedder, utt: str, session_id: str, *, alias: str = "팀장"):
    """후보 2명(같은 별칭) + 판정 실패 -> 조회 턴이 identity 질문을 저장한다.
    반환: (두 인물, 저장된 질문 행, 질문을 낸 ctx)."""

    a = _seed_person(db_session, fake_embedder, name="김민수", alias=alias)
    b = _seed_person(db_session, fake_embedder, name="김민호", alias=alias)
    result, ctx = _run(
        db_session, fake_embedder, utt, _queries("팀장"),
        judge=FakeJudge(fail="timeout"), answerer=FakeQueryAnswerer(), session_id=session_id,
    )
    assert result.pending_question is not None and result.pending_question.kind == "identity"
    row = db_session.get(PendingQuestion, result.pending_question.question_id)
    return a, b, row, ctx


def _answer_and_load(ctx, row, answer: str) -> ResumeInput:
    answer_question(ctx, row.id, answer)
    return load_resume_input(ctx.session, row.id)


def _reject_option(row) -> str:
    rejects = [o for o in row.options if o not in row.context["candidate_ids"]]
    assert len(rejects) == 1
    return rejects[0]


def _count_step(db_session, session_id: str, step: str) -> int:
    return len(_rows(db_session, session_id, step))


@pytest.mark.parametrize("pick", ["김민수", "김민호"])
def test_t_resume_candidate_answer_replies_from_that_card_and_writes_nothing(
    db_session, fake_embedder, monkeypatch, pick
):
    sid = f"q-t-{pick}"
    utt = "팀장님 어떤 분이었지?"
    a, b, row, ctx = _ask_identity(db_session, fake_embedder, utt, sid)
    chosen, other = (a, b) if pick == "김민수" else (b, a)
    assert row.context["candidate_ids"][pick] == chosen.id
    assert row.context["utterance"] == utt
    resume_input = _answer_and_load(ctx, row, pick)

    answerer = _RecordingAnswerer(table={utt: ANSWER_TEXT})
    calls: dict[str, int] = {"apply": 0, "resolve": 0, "followup": 0, "update_person": 0}
    monkeypatch.setattr(
        loop_module, "apply_resolution", lambda *a_, **k: calls.__setitem__("apply", calls["apply"] + 1)
    )
    monkeypatch.setattr(
        loop_module, "resolve", lambda *a_, **k: calls.__setitem__("resolve", calls["resolve"] + 1)
    )
    monkeypatch.setattr(
        loop_module,
        "_followup_new_person_turn",
        lambda *a_, **k: calls.__setitem__("followup", calls["followup"] + 1),
    )
    real_update = loop_module.app_tools.update_person
    monkeypatch.setattr(
        loop_module.app_tools,
        "update_person",
        lambda *a_, **k: (calls.__setitem__("update_person", calls["update_person"] + 1), real_update(*a_, **k))[1],
    )
    before = _counts(db_session, "local")
    q_before = _count_step(db_session, sid, "loop_query")
    t_before = _count_step(db_session, sid, "loop_turn")

    result = resume_turn(ctx, resume_input, question_id=row.id, answerer=answerer)

    assert_no_writes(before, _counts(db_session, "local"))  # person_aliases 포함 불변
    assert _write_tool_rows(db_session, sid) == 0
    assert calls == {"apply": 0, "resolve": 0, "followup": 0, "update_person": 0}
    assert result.reply == f"{ANSWER_TEXT}\n{QUERY_MORE_HINT}"
    assert answerer.call_count == 1
    seen = answerer.seen[0]
    assert chosen.display_name in seen and other.display_name not in seen
    assert result.stop_reason is None
    assert result.pending_question is None
    assert result.stored.to_dict() == {"persons": 0, "events": 0, "schedules": 0}
    assert _count_step(db_session, sid, "loop_query") == q_before + 1
    assert _count_step(db_session, sid, "loop_turn") == t_before + 1
    assert _rows(db_session, sid, "loop_resolve_done") == []
    assert _rows(db_session, sid, "loop_record") == []
    resume_rows = _rows(db_session, sid, "loop_resume")
    assert len(resume_rows) == 1
    query_row = _rows(db_session, sid, "loop_query")[-1]
    assert result.trace_ids == [resume_rows[0].id, query_row.id]
    out = query_row.output
    assert out["mentions"] == ["팀장"]
    assert out["mentions_dropped"] == 0
    assert out["person_id"] == chosen.id
    assert out["answer_source"] == "llm"
    assert out["resolutions"] == [
        {
            "mention": "팀장",
            "band": "identity",
            "person_id": chosen.id,
            "er_trace_id": None,
            "applied": True,
            "question_id": row.id,
        }
    ]


def test_u_resume_reject_answer_says_no_record_and_asks_nothing(db_session, fake_embedder, monkeypatch):
    sid = "q-u"
    utt = "팀장님 어떤 분이었지?"
    a, b, row, ctx = _ask_identity(db_session, fake_embedder, utt, sid)
    reject = _reject_option(row)
    resume_input = _answer_and_load(ctx, row, reject)
    followup: list[int] = []
    monkeypatch.setattr(
        loop_module, "_followup_new_person_turn", lambda *a_, **k: followup.append(1)
    )
    answerer = FakeQueryAnswerer(table={utt: ANSWER_TEXT})
    before = _counts(db_session, "local")

    result = resume_turn(ctx, resume_input, question_id=row.id, answerer=answerer)

    assert_no_writes(before, _counts(db_session, "local"))  # pending_questions +0 포함
    assert followup == []
    assert _write_tool_rows(db_session, sid) == 0
    assert result.reply == no_record_reply(["팀장"])
    assert result.pending_question is None
    assert result.stop_reason is None
    assert answerer.call_count == 0
    resume_rows = _rows(db_session, sid, "loop_resume")
    query_row = _rows(db_session, sid, "loop_query")[-1]
    assert result.trace_ids == [resume_rows[0].id, query_row.id]
    out = query_row.output
    assert out["answer_source"] == "no_record"
    assert out["person_id"] is None
    assert out["resolutions"] == [
        {
            "mention": "팀장",
            "band": "identity",
            "person_id": None,
            "er_trace_id": None,
            "applied": False,
            "question_id": row.id,
        }
    ]
    assert _rows(db_session, sid, "loop_resolve_done") == []
    assert _rows(db_session, sid, "loop_record") == []


def test_v_resume_without_intent_key_keeps_record_path(db_session, fake_embedder):
    """하위 호환 -- P5-loop 형식(기록 턴이 만든 identity 행: `resume.intent` 키 없음)."""

    sid = "q-v"
    utt = "팀장이랑 저녁 먹었어"
    person = _make_person(db_session, "김민수")
    _add_alias(db_session, person, "팀장님", fake_embedder)
    ctx = ToolContext(session=db_session, session_id=sid, embedder=fake_embedder)
    call = {
        "name": "add_event",
        "args": {
            "person": "팀장", "type": "meal", "content": "저녁",
            "occurred_at": datetime(2026, 3, 1, tzinfo=timezone.utc).isoformat(),
        },
    }
    first = run_turn(
        ctx, utt, proposer=FakeProposer(table={utt: [call]}), judge=FakeJudge(fail="timeout")
    )
    assert first.pending_question is not None and first.pending_question.kind == "identity"
    row = db_session.get(PendingQuestion, first.pending_question.question_id)
    assert "intent" not in row.context["resume"]
    resume_input = _answer_and_load(ctx, row, "김민수")
    before = _counts(db_session, "local")
    q_before = _count_step(db_session, sid, "loop_query")
    r_before = _count_step(db_session, sid, "loop_record")

    result = resume_turn(ctx, resume_input, question_id=row.id)

    after = _counts(db_session, "local")
    rows = db_session.execute(
        text(
            "SELECT count(*) FROM agent_traces WHERE session_id = :s AND step = 'tool_call' "
            "AND tool_name = 'update_person'"
        ),
        {"s": sid},
    ).scalar_one()
    assert rows == 1
    assert after["person_aliases"] == before["person_aliases"] + 1
    assert after["events"] == before["events"] + 1
    assert result.stored.events == 1
    assert _count_step(db_session, sid, "loop_query") == q_before  # 조회 경로 아님
    assert _count_step(db_session, sid, "loop_record") == r_before + 1


@pytest.mark.parametrize("kind", ["new_person", "schedule"])
def test_w_other_kinds_ignore_intent(db_session, fake_embedder, monkeypatch, kind):
    called: list[int] = []
    monkeypatch.setattr(
        loop_module, "_resume_query_turn", lambda *a_, **k: called.append(1)
    )
    ctx = ToolContext(session=db_session, session_id=f"q-w-{kind}", embedder=fake_embedder)
    resume_input = ResumeInput(
        kind=kind,
        context={
            "utterance": "발화",
            "mention": "이모",
            "resume": {"intent": "query", "pending_calls": []},
        },
        answer="아니요",
    )

    result = resume_turn(ctx, resume_input, question_id=1)

    assert called == []
    assert result.pending_question is None
    assert _rows(db_session, f"q-w-{kind}", "loop_query") == []
    assert len(_rows(db_session, f"q-w-{kind}", "loop_record")) == 1


# ---------------------------------------------------------------------------
# R-U4-2 -- 생존 변이를 닫는 테스트(코드는 맞고 테스트 공백이었다)
# ---------------------------------------------------------------------------


def test_x_answer_is_stripped_but_rejected_answer_is_verbatim(db_session, fake_embedder):
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분?"
    judge = FakeJudge(table={person.id: 0.95})

    padded = f"  {ANSWER_TEXT}  \n"
    ok, _ = _run(
        db_session, fake_embedder, utt, _queries("팀장"), judge=judge,
        answerer=FakeQueryAnswerer(table={utt: padded}), session_id="q-x1",
    )
    assert ok.reply == f"{ANSWER_TEXT}\n{QUERY_MORE_HINT}"
    out_ok = _query_out(db_session, "q-x1")
    assert out_ok["answer_source"] == "llm"
    assert out_ok["rejected_answer"] is None

    bad_padded = "  요즘 많이 힘들어 보여요  \n"
    bad, _ = _run(
        db_session, fake_embedder, utt, _queries("팀장"), judge=judge,
        answerer=FakeQueryAnswerer(table={utt: bad_padded}), session_id="q-x2",
    )
    out_bad = _query_out(db_session, "q-x2")
    assert out_bad["answer_source"] == "template"
    assert out_bad["rejected_answer"] == bad_padded  # strip 안 한 원문 그대로
    assert bad.reply == _template_for(db_session, person)


def test_y_person_not_found_on_card_read_says_no_record(db_session, fake_embedder, monkeypatch):
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분?"
    answerer = FakeQueryAnswerer(table={utt: ANSWER_TEXT})
    import app.api.read as read_module

    def _raise(*a_, **k):
        raise PersonNotFound("gone")

    monkeypatch.setattr(read_module, "get_person_card", _raise)

    result, _ = _run(
        db_session, fake_embedder, utt, _queries("팀장"),
        judge=FakeJudge(table={person.id: 0.95}), answerer=answerer, session_id="q-y",
    )

    assert result.reply == no_record_reply(["팀장"])
    out = _query_out(db_session, "q-y")
    assert out["person_id"] is None
    assert out["answer_source"] == "no_record"
    assert answerer.call_count == 0


def test_z_merge_resolution_entry_carries_person_id(db_session, fake_embedder):
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분이었지?"
    _run(
        db_session, fake_embedder, utt, _queries("팀장"),
        judge=FakeJudge(table={person.id: 0.95}),
        answerer=FakeQueryAnswerer(table={utt: ANSWER_TEXT}), session_id="q-z",
    )

    out = _query_out(db_session, "q-z")
    assert out["resolutions"][0]["band"] == "merge"
    assert out["resolutions"][0]["person_id"] == person.id


class _DbErrorAnswerer:
    def answer(self, question, evidence, now):
        raise SQLAlchemyError("db down")


def test_aa_db_errors_propagate_out_of_run_turn(db_session, fake_embedder, monkeypatch):
    person = _seed_person(db_session, fake_embedder)
    utt = "팀장님 어떤 분?"
    judge = FakeJudge(table={person.id: 0.95})

    with pytest.raises(SQLAlchemyError):
        _run(
            db_session, fake_embedder, utt, _queries("팀장"), judge=judge,
            answerer=_DbErrorAnswerer(), session_id="q-aa1",
        )

    import app.api.read as read_module

    def _raise(*a_, **k):
        raise SQLAlchemyError("db down")

    monkeypatch.setattr(read_module, "get_person_card", _raise)
    with pytest.raises(SQLAlchemyError):
        _run(
            db_session, fake_embedder, utt, _queries("팀장"), judge=judge,
            answerer=FakeQueryAnswerer(table={utt: ANSWER_TEXT}), session_id="q-aa2",
        )
