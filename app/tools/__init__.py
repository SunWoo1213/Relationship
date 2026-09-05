"""Refs: P2-tools S3.2 -- 툴 7종 패키지.

U3~U7 이 `search_person`·`create_person`·`update_person`·`add_event`·
`add_schedule`·`get_briefing`·`ask_user`(+ 툴 밖 보조 `answer_question`,
`question_status`)를 `persons.py`·`records.py`·`questions.py`·`briefing.py`
에 구현하면, 이 파일이 그것들을 재export 하고 `TOOL_NAMES` 튜플을 정의한다
(`scripts/tools_check.py`·`tests/test_tool_signatures.py` 가 그 시점에
여기서 import 한다). U2 시점에는 툴 함수가 아직 없으므로 재export 자리만
비워 둔다.
"""

from __future__ import annotations
