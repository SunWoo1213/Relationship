"""Refs: P9b-auth U2 D18 CR-006 -- 인증 코어 패키지.

- `passwords` -- 비밀번호 해시·검증(결정 C, `hashlib.scrypt`)
- `sessions`  -- 세션 토큰 발급·조회·폐기, 쿠키 이름·속성(결정 D·E·F)
- `deps`      -- `current_user` 로그인 의존성
- `origin`    -- 상태 변경 요청의 Origin 검사(결정 T)
- `routes`    -- `/auth/signup`·`/auth/login`·`/auth/logout`·`/auth/me`

이 `__init__` 은 아무것도 import 하지 않는다 -- 서브모듈이 `app.api.deps`
(→ `app.api` 패키지 초기화)를 끌어오므로, 여기서 모으면 순환 import 가 생긴다.
"""
