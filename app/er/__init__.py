"""app/er -- 엔티티 해석 4단계 파이프라인 패키지 (P3-er, 01-plan 결정1).

`.claude/skills/entity-resolution` 의 절차(후보 검색 → 규칙 필터 → LLM
판정 → 확신도 분기)를 모듈 4개로 그대로 옮긴다 -- 한 파일에서 LLM 을
한 번만 부르고 끝내는 지름길을 구조로 막는다(원칙4).

이 파일은 재export 지점이다. U3(이 단위)는 `types`·`dictionary`·`rules`
까지만 만든다 -- `candidates`(1단계)·`judge`(3단계)·`confidence`(4단계)·
`pipeline`(오케스트레이션)은 U4~U6 이 추가하며, 그때 이 파일에
`resolve`·`apply_resolution`·`Judge`·`FakeJudge` 재export 가 채워진다
(01-plan 산출물 목록 24행).
"""

from __future__ import annotations
