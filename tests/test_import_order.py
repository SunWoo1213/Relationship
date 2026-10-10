"""Refs: FIX-029 P7-push S3.6 -- import 순서와 상관없이 각 모듈이 단독으로
import 되는지 확인하는 회귀 테스트(F-c7c1e5).

## 무엇을 확인하나

`app.push` 계열 모듈을 **새 인터프리터에서 먼저** import 해도 순환 import 로
실패하지 않는다. 예전에는 `app.push` -> `app.push.notifier` ->
`app.briefing.types`(패키지 `app.briefing` 실행) -> `app.briefing.scheduler`
-> `app.push.notifier`(아직 절반만 올라온 모듈) 로 돌아 `ImportError` 가
났다.

## 왜 서브프로세스인가

같은 프로세스에서 `import app.push` 를 부르면 `tests/conftest.py` 가 이미
`app.main`/`app.briefing` 을 올려 둔 뒤라 순환이 가려진다. 그래서 모듈마다
**새 파이썬 프로세스**(`sys.executable -c "import <m>"`)를 띄워 returncode 를
본다. 환경변수는 부모 것을 그대로 넘기고, DB·네트워크는 쓰지 않는다(import
만 한다).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

#: 저장소 루트 -- `app` 패키지가 보이는 작업 디렉터리.
REPO_ROOT = Path(__file__).resolve().parent.parent

#: 단독 import 를 확인할 모듈(FIX-029 표 A 의 루프 명령과 같은 목록).
MODULES = [
    "app.push",
    "app.push.notifier",
    "app.push.sender",
    "app.push.payload",
    "app.push.subscriptions",
    "app.push.types",
    "app.briefing",
    "app.briefing.scheduler",
    "app.main",
]


@pytest.mark.parametrize("module", MODULES)
def test_모듈을_새_프로세스에서_먼저_import_해도_성공한다(module: str) -> None:
    proc = subprocess.run(
        [sys.executable, "-c", f"import {module}"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    tail = "\n".join(proc.stderr.strip().splitlines()[-5:])
    assert proc.returncode == 0, f"`import {module}` 가 실패했다(순환 import 의심):\n{tail}"
