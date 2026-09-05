"""Refs: P2-tools S3.2 -- 툴 7종 패키지.

U3~U7 이 `search_person`·`create_person`·`update_person`·`add_event`·
`add_schedule`·`get_briefing`·`ask_user`(+ 툴 밖 보조 `answer_question`,
`question_status`)를 `persons.py`·`records.py`·`questions.py`·`briefing.py`
에 구현했다. U7 에서 이 파일이 그것들을 재export 하고 `TOOL_NAMES` 튜플을
정의한다 -- U9 의 `scripts/tools_check.py`·`tests/test_tool_signatures.py`
가 `app.tools` 하나에서 7개 툴을 전부 import 할 수 있게 한다(각 서브모듈
경로를 따로 알 필요가 없다). `answer_question`/`question_status`/
`list_pending` 은 툴 7종이 아니므로(LLM 에 노출하지 않음, 01-plan 범위
21행) `TOOL_NAMES` 에는 넣지 않지만, U8 의 `POST /answers/{question_id}`
가 바로 쓸 수 있도록 함께 재export 한다.
"""

from __future__ import annotations

from app.tools.briefing import get_briefing
from app.tools.persons import create_person, search_person, update_person
from app.tools.questions import answer_question, ask_user, list_pending, question_status
from app.tools.records import add_event, add_schedule

#: 툴 7종(CLAUDE.md "툴 7종" 표 순서 그대로) -- LLM 에 노출되는 이름 집합.
#: `answer_question`/`question_status`/`list_pending` 은 포함하지 않는다
#: (툴 밖 보조 함수, 01-plan 범위 21행).
TOOL_NAMES = (
    "search_person",
    "create_person",
    "update_person",
    "add_event",
    "add_schedule",
    "get_briefing",
    "ask_user",
)

__all__ = [
    "TOOL_NAMES",
    "search_person",
    "create_person",
    "update_person",
    "add_event",
    "add_schedule",
    "get_briefing",
    "ask_user",
    "answer_question",
    "question_status",
    "list_pending",
]
