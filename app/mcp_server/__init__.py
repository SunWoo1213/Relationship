"""Refs: P9b-auth U12 CR-008 D19 -- MCP 읽기 전용 서버(공식 Python SDK `mcp`, 무상태·JSON 응답).

- `tools`  -- 도구 본체 4개(SDK import 0 -- 순수 함수. 조회는 `app.api.read` 의 세 함수만)
- `auth`   -- `/mcp` Bearer 토큰 인증 ASGI 래퍼(헤더만 읽는다)
- `server` -- SDK import 는 이 파일에만. 서버 생성·도구 등록·세션 관리자 반환

패키지 이름을 `app/mcp/` 로 하지 않는다 -- PyPI 패키지 `mcp` 와 이름이 겹쳐 헷갈린다.
이 `__init__` 은 아무것도 import 하지 않는다(`MCP_ENABLED` 가 꺼진 앱은 SDK 를 import 하지 않는다 --
D19 지킬 것 8).

금지 import(D19 지킬 것 5): `app.tools`(툴 7종)·`app.agent`·`app.er`·`app.briefing`·`app.embedding`·
LLM 공급자 SDK(`openai`·`anthropic`·`google`). `tests/test_mcp_tools.py` 가 이 디렉터리 원문을 정규식으로 본다.
"""
