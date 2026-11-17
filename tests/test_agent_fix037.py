"""Refs: FIX-037 P5-loop P5b-query-turn D14 D16 S3.4 원칙7 원칙8 -- 인식 프롬프트의
의도·이벤트 유형 문구, 조회 답 프롬프트의 근황 문구, 거부 알림 문장 테스트.

네트워크 없음. 루프 테스트는 `FakeProposer`·`db_session` 만 쓴다.
프롬프트 예시에 시연·표본 발화를 쓰지 않았음도 확인한다(원칙8)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

import app.agent.loop as loop_module
from app.agent.gate import GATE_REJECTION_REASONS, REASON_BAD_ARGS
from app.agent.loop import run_turn
from app.agent.types import GateVerdict, RejectedProposal
from app.agent.propose import EVENT_TYPE_DESCRIPTIONS, FakeProposer, build_propose_prompt
from app.agent.respond import build_reply
from app.db.models import EVENT_TYPES
from app.er.judge import FakeJudge
from app.tools.context import ToolContext
from app.tools.types import PendingQuestionOut

NOW = datetime(2026, 11, 17, 12, 0, 0, tzinfo=timezone.utc)

REJECTED_SENTENCE = "말씀하신 내용을 기록하지 못했어요. 다시 한 번 말씀해 주시겠어요?"
NOTHING_SENTENCE = "이번 발화에서는 새로 기억한 것이 없어요."


# --- 유형 설명 상수 -----------------------------------------------------------


def test_event_type_descriptions_keys_equal_event_types_exactly():
    assert tuple(EVENT_TYPE_DESCRIPTIONS) == tuple(EVENT_TYPES)
    assert len(EVENT_TYPE_DESCRIPTIONS) == 7
    assert all(desc.strip() for desc in EVENT_TYPE_DESCRIPTIONS.values())


def test_prompt_contains_every_event_type_and_its_description_line():
    system, user_text = build_propose_prompt("u", NOW)
    for key, desc in EVENT_TYPE_DESCRIPTIONS.items():
        assert f"- {key}: {desc}" in user_text


def test_prompt_event_type_priority_and_closed_set_sentences():
    system, _ = build_propose_prompt("u", NOW)
    assert "일곱 개 밖의 값은 쓰지 마라" in system
    assert "conflict, favor, praise, personal_share 를 meeting·meal 보다 먼저" in system
    assert "other 를 쓴다" in system


def test_conflict_description_wins_over_meeting_and_meal_setting():
    assert "회의나 식사 자리에서 생겼어도 이 유형" in EVENT_TYPE_DESCRIPTIONS["conflict"]
    assert "conflict" in EVENT_TYPE_DESCRIPTIONS["meeting"]
    assert "conflict" in EVENT_TYPE_DESCRIPTIONS["meal"]


# --- 의도 문구 ----------------------------------------------------------------


def test_prompt_intent_sentences_query_only_when_asking_and_statement_is_record():
    system, _ = build_propose_prompt("u", NOW)
    assert "묻는 형태(의문형·물음표·알려 달라는 요청)" in system
    assert "일 때만 intent 를 query 로" in system
    assert "평서문은 물음표가 없으면 record 로" in system
    # D16 결정 6 -- 그대로.
    assert "둘이 섞이면 query 다." in system


def test_prompt_r2_fact_only_when_lasting_info_is_stated():
    """R2 -- 사건과 사실 동시 제안은 지속되는 정보를 실제로 말할 때에만."""

    system, _ = build_propose_prompt("u", NOW)
    assert "일어난 일(누가 무엇을 했다·말했다·털어놓았다)을 말하는 발화는 반드시 add_event 로 제안한다" in system
    assert "인물 사실은 사건을 대신하지 못한다 -- 사건의 내용을 사실로 옮겨 적지 마라" in system
    assert "계속 참인 정보(선호·직업·가족·사는 곳 등)가 발화에 명시돼 있을 때에만 더한다" in system
    assert "일어난 일 없이 그런 정보만 말하는 평서문은 update_person 만 제안한다" in system
    assert "근황 등" not in system  # 털어놓은 근황은 사건이다
    assert "호칭·직함만 보고 사실을 만들지 말고, 사건 내용을 사실로 다시 적지 마라" in system
    assert "사실이 없으면 update_person 을 제안하지 마라" in system
    assert "둘 다 제안하라" not in system


def test_prompt_r1_future_events_go_to_add_schedule():
    system, user_text = build_propose_prompt("u", NOW)
    assert "아직 일어나지 않은 약속·회의·면담처럼 앞으로 있을 일은 add_event 가 아니라 add_schedule 로만 제안한다" in system
    assert "add_event 는 이미 일어난 일에만 쓴다" in system
    assert EVENT_TYPE_DESCRIPTIONS["meal"].startswith("이미 있었던 ")
    assert EVENT_TYPE_DESCRIPTIONS["meeting"].startswith("이미 있었던 ")
    assert "- meeting: 이미 있었던 " in user_text


def test_prompt_r3_intent_must_be_filled():
    system, _ = build_propose_prompt("u", NOW)
    assert "intent 는 반드시 채워라(query 또는 record)" in system


def test_build_reply_r4_no_rejected_sentence_when_pending_question_exists():
    """R4 -- 확인 칩이 함께 나가는 턴에는 거부 알림을 붙이지 않는다."""

    question = PendingQuestionOut(question_id=7, status="pending", kind="new_person", question="기억해둘까요?", options=["예"])
    reply = build_reply(stored_events=0, stored_schedules=0, rejected_bad_args=True, pending_question=question)
    assert reply == NOTHING_SENTENCE + "\n기억해둘까요?"
    assert REJECTED_SENTENCE not in reply


# --- 거부 알림 문장 -------------------------------------------------------------


def test_build_reply_bad_args_flag_replaces_sentence_only_when_nothing_stored():
    assert build_reply(stored_events=0, stored_schedules=0, rejected_bad_args=True) == REJECTED_SENTENCE
    # 기본값(False)은 기존 문장 그대로.
    assert build_reply(stored_events=0, stored_schedules=0) == NOTHING_SENTENCE
    assert build_reply(stored_events=0, stored_schedules=0, rejected_bad_args=False) == NOTHING_SENTENCE
    # 저장된 것이 있으면 플래그가 있어도 저장 문장.
    assert build_reply(stored_events=1, stored_schedules=0, rejected_bad_args=True) == "기억했어요: 이벤트 1건."
    assert build_reply(stored_events=0, stored_schedules=0, stored_facts=1, rejected_bad_args=True) == (
        "기억했어요: 사실 1건."
    )


def _ctx(db_session, *, session_id: str, embedder) -> ToolContext:
    return ToolContext(session=db_session, user_id="fix037-user", session_id=session_id, embedder=embedder)


def _run(db_session, fake_embedder, session_id: str, utterance: str, calls: list[dict]):
    ctx = _ctx(db_session, session_id=session_id, embedder=fake_embedder)
    return run_turn(
        ctx,
        utterance,
        proposer=FakeProposer(table={utterance: calls}),
        judge=FakeJudge(table={}),
    )


def test_run_turn_bad_args_rejection_gives_rejected_sentence(db_session, fake_embedder):
    """`type` 이 7종 밖(`health`)이면 게이트가 `bad_args` 로 버린다 -> 거부 알림."""

    calls = [
        {
            "name": "add_event",
            "args": {"person": "누구", "type": "health", "content": "내용", "occurred_at": NOW.isoformat()},
        }
    ]
    result = _run(db_session, fake_embedder, "fix037-bad-args", "기록할 말", calls)

    assert result.stored.events == 0
    assert result.reply == REJECTED_SENTENCE


def test_run_turn_without_proposal_keeps_nothing_stored_sentence(db_session, fake_embedder):
    result = _run(db_session, fake_embedder, "fix037-no-proposal", "기록할 말", [])
    assert result.reply == NOTHING_SENTENCE


def test_run_turn_non_bad_args_rejection_keeps_nothing_stored_sentence(db_session, fake_embedder):
    """`unknown_tool` 거부는 `bad_args` 가 아니므로 문장이 바뀌지 않는다."""

    calls = [{"name": "no_such_tool", "args": {}}]
    result = _run(db_session, fake_embedder, "fix037-unknown-tool", "기록할 말", calls)
    assert result.reply == NOTHING_SENTENCE


def _force_rejections(monkeypatch, *pairs: tuple[str, str]) -> None:
    """게이트 판정을 `(툴 이름, 거부 사유)` 목록으로 고정한다(통과 0건)."""

    verdict = GateVerdict(
        accepted=[],
        rejected=[RejectedProposal(index=i, name=name, reason=reason) for i, (name, reason) in enumerate(pairs)],
    )
    monkeypatch.setattr(loop_module, "gate_check", lambda proposal: verdict)


@pytest.mark.parametrize("reason", [r for r in GATE_REJECTION_REASONS if r != REASON_BAD_ARGS])
def test_run_turn_every_non_bad_args_reason_keeps_nothing_stored_sentence(
    db_session, fake_embedder, monkeypatch, reason
):
    """R-37-4 -- `bad_args` 외 거부 사유(`unknown_tool`·`not_callable_by_llm`·`person_id_from_llm`·
    `needs_confirmation`·`limit`·`query_turn_no_write`)는 전부 기존 문장."""

    _force_rejections(monkeypatch, ("add_event", reason))
    result = _run(db_session, fake_embedder, f"fix037-reason-{reason}", "기록할 말", [])
    assert result.reply == NOTHING_SENTENCE


@pytest.mark.parametrize("tool", ["add_event", "update_person", "add_schedule", "create_person"])
def test_run_turn_bad_args_on_any_tool_gives_rejected_sentence(db_session, fake_embedder, monkeypatch, tool):
    """`bad_args` 는 어느 툴이든(`create_person` 만 거부돼도) 저장 0건·대기 질문 없음이면 거부 알림."""

    _force_rejections(monkeypatch, (tool, REASON_BAD_ARGS))
    result = _run(db_session, fake_embedder, f"fix037-bad-{tool}", "기록할 말", [])
    assert result.pending_question is None
    assert result.reply == REJECTED_SENTENCE


# --- 문장 정확 일치 (R-37-5) -----------------------------------------------------

_INTENT_SENTENCES = (
    "발화가 묻는 형태(의문형·물음표·알려 달라는 요청)이고 이미 기록된 "
    "인물 정보를 묻는 것일 때만 intent 를 query 로, 인물에 대해 새 "
    "사실·사건·일정을 알려 주는 평서문은 물음표가 없으면 record 로 "
    "답하라. 둘이 섞이면 query 다. "
    "intent 는 반드시 채워라(query 또는 record). "
    "아직 일어나지 않은 약속·회의·면담처럼 앞으로 있을 일은 add_event 가 "
    "아니라 add_schedule 로만 제안한다. add_event 는 이미 일어난 일에만 쓴다. "
    "일어난 일(누가 무엇을 했다·말했다·털어놓았다)을 말하는 발화는 "
    "반드시 add_event 로 제안한다. 인물 사실은 사건을 대신하지 못한다 -- "
    "사건의 내용을 사실로 옮겨 적지 마라. 사실(update_person 의 facts)은 "
    "사건과 별개로, 그 인물에 대해 계속 참인 정보(선호·직업·가족·사는 곳 "
    "등)가 발화에 명시돼 있을 때에만 더한다. 일어난 일 없이 그런 정보만 "
    "말하는 평서문은 update_person 만 제안한다. 호칭·직함만 보고 사실을 만들지 말고, 사건 내용을 사실로 "
    "다시 적지 마라. 값이 비었거나 '기타'·'모름' 같은 자리 채우기이거나 "
    "호칭·직함·역할 이름뿐이면 그 사실은 제안하지 않는다. 사실이 없으면 "
    "update_person 을 제안하지 마라. "
    "add_event 의 type 은 아래 일곱 가지 중 하나만 쓰고, 이 일곱 개 밖의 "
    "값은 쓰지 마라. 둘 이상에 걸치면 conflict, favor, praise, "
    "personal_share 를 meeting·meal 보다 먼저 고르고, 어느 것도 아니면 "
    "other 를 쓴다. "
)


def test_prompt_intent_to_type_block_exact():
    system, _ = build_propose_prompt("u", NOW)
    assert _INTENT_SENTENCES in system


def test_event_type_descriptions_exact_values():
    assert EVENT_TYPE_DESCRIPTIONS == {
        "conflict": "다툼·언쟁·지적받음·의견 충돌·부딪힘. 회의나 식사 자리에서 생겼어도 이 유형",
        "praise": "칭찬·인정·감사를 받거나 한 일",
        "meal": "이미 있었던 식사·술·커피처럼 함께 먹고 마신 일(그 자리에서 다툼이 있었다면 conflict)",
        "meeting": "이미 있었던 만남·회의·면담처럼 함께 모인 일(그 자리에서 다툼이 있었다면 conflict)",
        "personal_share": "상대가 본인의 신상·근황·사정을 털어놓은 일",
        "favor": "도움이나 부탁을 주고받은 일",
        "other": "위 여섯 가지 어느 것도 아닐 때",
    }


def test_prompt_r2_names_empty_placeholder_and_title_values():
    """R-37-1 -- 빈 값·자리 채우기 값·호칭으로 사실을 만들지 말라는 뜻."""

    system, _ = build_propose_prompt("u", NOW)
    assert "값이 비었거나 '기타'·'모름' 같은 자리 채우기이거나 호칭·직함·역할 이름뿐이면 그 사실은 제안하지 않는다" in system


def test_meeting_and_meal_descriptions_have_no_future_word():
    """R-37-2 -- 미래를 끌어오던 낱말 "약속" 이 유형 설명에 없다."""

    for desc in EVENT_TYPE_DESCRIPTIONS.values():
        assert "약속" not in desc
