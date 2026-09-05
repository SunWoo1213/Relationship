"""Refs: P1-schema S3.1 -- 저장소 루트를 sys.path 에 등록해 `app` 을 임포트 가능하게 한다."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
