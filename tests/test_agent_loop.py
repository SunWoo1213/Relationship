"""Refs: P5-loop D1 D2 D12 D13 S3.3 S3.4 원칙1 원칙2 원칙4 -- U4 해석 단계
(`app/agent/loop.py::resolve_mentions`) 테스트.

실 PostgreSQL(로컬, `POSTGRES_PORT` 기본 5433) + 롤백 픽스처(`db_session`) +
`FakeJudge`(네트워크 0, `app/er/judge.py` 무수정 import) + `fake_embedder`
(스텁 임베더). 제안·게이트는 손으로 만들지 않고 실제 `app.agent.gate.check()`
를 거쳐 `GateVerdict` 를 만든다 -- 게이트·해석 경계가 실제 그대로 맞물리는지
함께 확인한다(U3 산출물 재사용, 중복 구현 금지).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

import app.agent.loop as loop_module
from app.agent.gate import check
from app.agent.loop import resolve_mentions
from app.agent.types import NEW_PERSON_TAG_OPTIONS, Proposal, ToolCallProposal
from app.db.models import ALIAS_SOURCES, PendingQuestion, Person, PersonAlias
from app.er import AlreadyApplied, apply_resolution
from app.er.judge import FakeJudge
from app.tools.context import ToolContext
from app.tools.types import AFFIRMATIVE_KEY

pytestmark = pytest.mark.dbtest

NOW = datetime(2026, 9, 24, 19, 0, 0, tzinfo=timezone.utc)


def _make_person(
    db_session, *, display_name: str, relation_tag: str = "직장", hierarchy: str = "동", user_id: str = "local"
) -> Person:
    person = Person(
        user_id=user_id, display_name=display_name, relation_tag=relation_tag, hierarchy=hierarchy
    )
    db_session.add(person)
    db_session.flush()
    return person


def _add_alias(
    db_session, person: Person, alias: str, *, embedding=None, source: str = ALIAS_SOURCES[0]
) -> PersonAlias:
    row = PersonAlias(person_id=person.id, alias=alias, source=source, embedding=embedding)
    db_session.add(row)
    db_session.flush()
    return row


def _ctx(db_session, *, session_id: str, embedder=None) -> ToolContext:
    return ToolContext(session=db_session, session_id=session_id, embedder=embedder)


def _call(name: str, **args) -> ToolCallProposal:
    return ToolCallProposal(name=name, args=args)


def _verdict_for(*calls: ToolCallProposal) -> tuple[Proposal, "GateVerdict"]:
    proposal = Proposal(tool_calls=list(calls), raw={})
    return proposal, check(proposal)


# ---------------------------------------------------------------------------
# merge -- 언급이 기존 인물로 연결되고 person_id 가 확정된다
# ---------------------------------------------------------------------------


def test_merge_connects_to_existing_person_and_returns_person_id(db_session, fake_embedder):
    session_id = "loop-u4-merge"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content="저녁", occurred_at=NOW)
    )

    outcome = resolve_mentions(
        ctx, proposal, verdict, "어제 팀장이랑 저녁 먹었어", judge=FakeJudge(table={person.id: 0.95})
    )

    assert outcome.stopped is False
    assert outcome.pending_question_id is None
    assert outcome.person_ids == {"팀장": person.id}
    assert len(outcome.decisions) == 1
    assert outcome.decisions[0].band == "merge"
    assert outcome.decisions[0].person_id == person.id
    assert outcome.decisions[0].trace_id is not None


# ---------------------------------------------------------------------------
# identity -- 되묻기로 턴이 끝나고, 저장된 options 는 ER 원본 그대로다
# ---------------------------------------------------------------------------


def test_identity_ends_turn_with_er_original_options(db_session, fake_embedder):
    session_id = "loop-u4-identity"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content="저녁", occurred_at=NOW)
    )

    # FakeJudge(fail=...) -> llm_failed -> identity 로 강제 확정(규칙 통과
    # 후보가 있으므로 new_person 이 아니다, app/er/pipeline.py 의 같은 경로를
    # tests/test_er_pipeline.py::test_resolve_llm_failed_forces_identity_band_llm_failed
    # 가 이미 검증한다 -- 여기서는 "루프가 그 옵션을 그대로 저장하는가"만 본다).
    outcome = resolve_mentions(ctx, proposal, verdict, "발화", judge=FakeJudge(fail="timeout"))

    assert outcome.stopped is True
    assert outcome.person_ids == {}
    assert outcome.pending_question_id is not None

    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    assert row.kind == "identity"
    assert row.options == ["김민수", "아니요, 다른 사람이에요"]
    assert row.context[AFFIRMATIVE_KEY] == ["김민수"]


# ---------------------------------------------------------------------------
# new_person -- M-1(d)·M-3 안 A: 힌트 유무와 관계없이 항상 태그 옵션으로 묻는다
# ---------------------------------------------------------------------------


def test_new_person_uses_tag_options_without_hint(db_session, fake_embedder):
    session_id = "loop-u4-new-person-no-hint"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    # "이모"는 호칭 사전 표제어라 규칙 필터가 유일한 후보를 배제한다
    # (dictionary_conflict) -- 규칙 통과 후보 0건이라 LLM 을 부르지 않고
    # new_person 으로 강제 확정된다(D13, tests/test_er_pipeline.py 의
    # no_candidates 케이스와 같은 설정).
    proposal, verdict = _verdict_for(
        _call("add_event", person="이모", type="meal", content="저녁", occurred_at=NOW)
    )

    outcome = resolve_mentions(ctx, proposal, verdict, "발화", judge=FakeJudge(table={}))

    assert outcome.stopped is True
    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    assert row.kind == "new_person"
    tags = list(NEW_PERSON_TAG_OPTIONS)
    assert row.options == tags + ["아니요"]
    assert row.context[AFFIRMATIVE_KEY] == tags


def test_new_person_uses_tag_options_even_with_hint_present(db_session, fake_embedder):
    """M-3 안 A -- LLM 힌트(`relation_tag`)가 있어도 태그 옵션은 그대로
    6개다. `hints` 는 위계 판단에만 쓰이고 `relation_tag` 는 항상 답에서
    온다(재개, U7 몫이라 여기서는 저장된 옵션·긍정 목록만 본다)."""

    session_id = "loop-u4-new-person-hint"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="이모", type="meal", content="저녁", occurred_at=NOW),
        _call(
            "create_person",
            display_name="이모",
            aliases=["이모"],
            relation_tag="가족",
            hierarchy="상",
        ),
    )

    outcome = resolve_mentions(ctx, proposal, verdict, "발화", judge=FakeJudge(table={}))

    assert outcome.stopped is True
    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    tags = list(NEW_PERSON_TAG_OPTIONS)
    assert row.options == tags + ["아니요"]
    assert row.context[AFFIRMATIVE_KEY] == tags

    resume = row.context["resume"]
    assert resume["hints"] == {"relation_tag": "가족", "hierarchy": "상"}
    assert resume["tag_by_answer"] == dict(zip(tags, ["가족", "연인", "친구", "직장", "지인"]))


# ---------------------------------------------------------------------------
# AlreadyApplied -- 같은 Resolution 을 두 번째로 apply_resolution 하면 거부된다
# ---------------------------------------------------------------------------


def test_already_applied_rejects_second_apply_resolution_call(db_session, fake_embedder):
    session_id = "loop-u4-already-applied"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content="저녁", occurred_at=NOW)
    )

    outcome = resolve_mentions(ctx, proposal, verdict, "발화", judge=FakeJudge(fail="timeout"))
    resolution = outcome.decisions[-1].resolution
    assert resolution is not None

    with pytest.raises(AlreadyApplied):
        apply_resolution(ctx, resolution)


# ---------------------------------------------------------------------------
# 루프는 확신도·임계치를 참조하지 않는다 (판정 표 6행의 pytest 화)
# ---------------------------------------------------------------------------


def test_loop_module_source_never_mentions_thresholds_or_confidence_literal():
    source = Path(loop_module.__file__).read_text(encoding="utf-8")
    for token in ("T_merge", "t_merge", "T_new", "t_new", "confidence"):
        assert token not in source, f"금지 토큰 발견: {token}"


# ---------------------------------------------------------------------------
# 확장된 context["resume"] 가 저장된 행에서 읽힌다 (M-0 크기 통제)
# ---------------------------------------------------------------------------


def test_extended_context_resume_round_trips_from_stored_row(db_session, fake_embedder):
    session_id = "loop-u4-resume-roundtrip"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content="저녁", occurred_at=NOW),
        _call("add_schedule", person="팀장", title="약속", scheduled_at=NOW),
    )

    outcome = resolve_mentions(ctx, proposal, verdict, "발화", judge=FakeJudge(fail="timeout"))

    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    resume = row.context["resume"]
    assert resume["mention"] == "팀장"
    assert resume["dropped"] == 0
    assert {c["name"] for c in resume["pending_calls"]} == {"add_event", "add_schedule"}
    # S3.4 13행 "전체 대화 이력 저장 금지" -- 발화 원문은 ER 이 이미 넣은
    # context["utterance"] 하나뿐이고 resume 에는 다시 넣지 않는다.
    assert "utterance" not in resume


def test_pending_calls_excludes_already_merged_mentions(db_session, fake_embedder):
    """결정 C(i)·D(i) -- 먼저 merge 로 확정된 언급의 제안은 재개 재료에
    담기지 않고, 되묻기를 일으킨(그리고 그 이후) 언급의 제안만 담긴다."""

    session_id = "loop-u4-mixed-mentions"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content="저녁1", occurred_at=NOW),
        _call("add_event", person="이모", type="meal", content="저녁2", occurred_at=NOW),
    )

    outcome = resolve_mentions(
        ctx, proposal, verdict, "발화", judge=FakeJudge(table={person.id: 0.95})
    )

    assert outcome.stopped is True
    assert outcome.person_ids == {"팀장": person.id}

    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    resume = row.context["resume"]
    assert [c["index"] for c in resume["pending_calls"]] == [1]


# ---------------------------------------------------------------------------
# LOOP_MAX_RESUME_BYTES 초과 -- held_drafts 는 버리고 pending_calls 는 유지
# ---------------------------------------------------------------------------


def test_resume_byte_limit_drops_held_drafts_but_keeps_pending_calls(db_session, fake_embedder):
    session_id = "loop-u4-byte-limit"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    long_content = "긴 내용 " * 100
    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content=long_content, occurred_at=NOW)
    )

    outcome = resolve_mentions(
        ctx,
        proposal,
        verdict,
        "발화",
        judge=FakeJudge(fail="timeout"),
        resume_byte_limit=50,
    )

    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    resume = row.context["resume"]
    assert resume["held_drafts"] == []
    assert resume["dropped"] == 1
    assert len(resume["pending_calls"]) == 1
    assert resume["pending_calls"][0]["args"]["content"] == long_content


def test_resume_within_byte_limit_keeps_held_drafts(db_session, fake_embedder):
    """대조군 -- 기본 상한(`app.settings.LOOP_MAX_RESUME_BYTES`)에서는
    `held_drafts` 가 버려지지 않는다(정상 크기의 되묻기)."""

    session_id = "loop-u4-byte-limit-ok"
    person = _make_person(db_session, display_name="김민수")
    _add_alias(db_session, person, "팀장", embedding=fake_embedder(["팀장"])[0])
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)

    proposal, verdict = _verdict_for(
        _call("add_event", person="팀장", type="meal", content="짧은 내용", occurred_at=NOW)
    )

    outcome = resolve_mentions(ctx, proposal, verdict, "발화", judge=FakeJudge(fail="timeout"))

    row = db_session.get(PendingQuestion, outcome.pending_question_id)
    resume = row.context["resume"]
    assert resume["dropped"] == 0
    assert resume["held_drafts"] == [{"name": "add_event", "content": "짧은 내용"}]
