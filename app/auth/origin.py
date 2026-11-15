"""Refs: P9b-auth U2 D18 결정 T F-7 -- 상태 변경 요청의 Origin 검사(앱 전역 한 곳).

배포 호스트 `*.sslip.io` 는 공개 접미사 목록에 없어 다른 `*.sslip.io` 가 우리와 **같은
사이트**다 -- `SameSite=Lax` 쿠키만으로는 그 호스트에서 오는 POST 를 막지 못한다. 그래서
POST·PUT·PATCH·DELETE 에 `Origin` 헤더가 있으면 그 호스트(:포트)가 접속 호스트와 같을 때만
통과시키고, 다르면 **403 `bad_origin`** 을 돌려준다.

규칙(결정 T, R2-1 ①):
- 접속 호스트 = `X-Forwarded-Host`(있으면, 쉼표가 있으면 첫 값) 아니면 `Host`.
  Caddy 는 `Host` 를 원래 값으로 전달하고(사실 10), Vite 개발 프록시는 `xfwd` 로
  `X-Forwarded-Host` 를 더한다(사실 14).
- 비교는 소문자로, `Origin` 스킴의 기본 포트(`https`→443, `http`→80)는 양쪽에서 떼고.
- `Origin` 헤더가 없으면 통과(curl·테스트 클라이언트는 브라우저 교차 요청이 아니다).
  `Origin: null` 이나 호스트를 읽을 수 없는 값은 **다름**으로 본다.
- 안전한 메서드(GET·HEAD·OPTIONS)는 검사하지 않는다.

ASGI 미들웨어로 앱 전체에 한 번 건다(`create_app()` 에서 등록) -- 라우트마다 흩뿌리지
않는다. 라우트 의존성보다 앞에서 막으므로 DB 세션도 열리지 않는다.
"""

from __future__ import annotations

from urllib.parse import urlsplit

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

#: 검사 대상(상태를 바꾸는) 메서드.
UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})

_DEFAULT_PORTS = {"https": "443", "http": "80"}


def _strip_default_port(hostport: str, scheme: str) -> str:
    """`scheme` 의 기본 포트(`:443`/`:80`)를 뗀 소문자 `host[:port]`."""
    value = hostport.strip().lower()
    port = _DEFAULT_PORTS.get(scheme)
    if port is not None and value.endswith(":" + port):
        value = value[: -(len(port) + 1)]
    return value


def origin_matches(origin: str, host: str, forwarded_host: str | None) -> bool:
    """`Origin` 헤더 값이 접속 호스트와 같은 출처인지."""
    try:
        parts = urlsplit(origin.strip())
    except ValueError:
        return False
    scheme = parts.scheme.lower()
    if scheme not in _DEFAULT_PORTS or not parts.netloc:
        return False  # `null`·스킴 없음·알 수 없는 스킴 → 다름
    target = host
    if forwarded_host:
        first = forwarded_host.split(",")[0].strip()
        if first:
            target = first
    return _strip_default_port(parts.netloc, scheme) == _strip_default_port(target, scheme)


class OriginCheckMiddleware:
    """순수 ASGI 미들웨어(`BaseHTTPMiddleware` 의 예외·본문 읽기 부작용을 피한다)."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["method"] not in UNSAFE_METHODS:
            await self.app(scope, receive, send)
            return
        origin: str | None = None
        host = ""
        forwarded_host: str | None = None
        for name, value in scope["headers"]:
            if name == b"origin" and origin is None:
                origin = value.decode("latin-1")
            elif name == b"host" and not host:
                host = value.decode("latin-1")
            elif name == b"x-forwarded-host" and forwarded_host is None:
                forwarded_host = value.decode("latin-1")
        if origin is not None and not origin_matches(origin, host, forwarded_host):
            response = JSONResponse(status_code=403, content={"detail": {"code": "bad_origin"}})
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)
