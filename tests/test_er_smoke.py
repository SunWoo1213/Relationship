"""Refs: P3-er 01-plan U8 결정9 원칙8 -- scripts/er_smoke.py 단위 테스트.

실 LLM 호출 없음(원칙8 -- LLM 출력은 재현 불가능하므로 자동 테스트에
넣지 않는다). `run_smoke()` 를 `FakeJudge` 로 검증하고, `main()` 의 키
없음/`JudgeUnavailable` 분기만 monkeypatch 로 확인한다.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import er_smoke  # noqa: E402

from app.er.judge import FakeJudge, judge_from_env  # noqa: E402
from app.er.types import JudgeUnavailable  # noqa: E402
from app.settings import er_config  # noqa: E402

#: 테스트 전용 가짜 키 값 -- 실제 API 키 형식이 아니다(값 노출 검사의
#: 대조군일 뿐, secret-guard 회피 목적이 아니다).
_FAKE_KEY_MARKER = "FAKE-TEST-ONLY-NOT-A-REAL-KEY-4f21"

_EXPECTED_KEYS = {
    "provider",
    "model",
    "tokens_in",
    "tokens_out",
    "s_llm",
    "matched_person_id",
    "reason",
    "confidence",
    "band",
}


# ---------- run_smoke(): FakeJudge 주입, 실 호출 없음 ----------


def test_run_smoke_output_keys_match_expected_schema():
    judge = FakeJudge(table={1: 0.95}, pick=1)
    result = er_smoke.run_smoke(judge, er_smoke._sample_candidates(), er_config())

    assert set(result.keys()) == _EXPECTED_KEYS
    assert result["provider"] == "fake"
    assert result["matched_person_id"] == 1


def test_run_smoke_merge_band_matches_combine():
    # s_llm=0.95, s_emb=0.85, s_rule=0.667 -> 0.5*0.95+0.3*0.85+0.2*0.667
    # = 0.8634 >= T_merge(0.8) -> merge (결정9 승진 회귀와 같은 수치대).
    judge = FakeJudge(table={1: 0.95}, pick=1)
    result = er_smoke.run_smoke(judge, er_smoke._sample_candidates(), er_config())

    assert result["confidence"] == pytest.approx(0.8634, abs=1e-6)
    assert result["band"] == "merge"


def test_run_smoke_null_matched_person_uses_zero_signals():
    judge = FakeJudge(table={})  # 교집합 없음 -> matched_person_id=None, s_llm=0.0
    result = er_smoke.run_smoke(judge, er_smoke._sample_candidates(), er_config())

    assert result["matched_person_id"] is None
    assert result["confidence"] == 0.0
    assert result["band"] == "new_person"


def test_run_smoke_does_not_leak_prompt_or_candidate_dump():
    judge = FakeJudge(table={2: 0.5}, pick=2)
    result = er_smoke.run_smoke(judge, er_smoke._sample_candidates(), er_config())
    dumped = json.dumps(result, ensure_ascii=False)

    # 시스템 프롬프트 원문이 결과 JSON 에 섞여 나오지 않는다.
    assert "report_judgement" not in dumped
    assert "후보 목록" not in dumped


# ---------- main(): 키 없음 -> 2, 키 미노출 ----------


def test_main_missing_anthropic_key_returns_2(monkeypatch, capsys):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    rc = er_smoke.main([])

    assert rc == 2
    captured = capsys.readouterr()
    assert "ANTHROPIC_API_KEY" in captured.out
    assert _FAKE_KEY_MARKER not in captured.out


def test_main_missing_openai_key_returns_2_with_provider_flag(monkeypatch, capsys):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    rc = er_smoke.main(["--provider", "openai"])

    assert rc == 2
    captured = capsys.readouterr()
    assert "OPENAI_API_KEY" in captured.out


# ---------- main(): 정상 경로(judge_from_env monkeypatch, 실 호출 없음) ----------


def test_main_success_path_prints_expected_json(monkeypatch, capsys):
    monkeypatch.setenv("ANTHROPIC_API_KEY", _FAKE_KEY_MARKER)
    monkeypatch.setattr(
        er_smoke, "judge_from_env", lambda env=None: FakeJudge(table={1: 0.9}, pick=1)
    )

    rc = er_smoke.main([])

    assert rc == 0
    captured = capsys.readouterr()
    parsed = json.loads(captured.out.strip())
    assert set(parsed.keys()) == _EXPECTED_KEYS
    assert _FAKE_KEY_MARKER not in captured.out
    assert "너는 한국어 대화" not in captured.out  # 시스템 프롬프트 원문 미노출


# ---------- main(): JudgeUnavailable -> 3 ----------


def test_main_judge_unavailable_returns_3(monkeypatch, capsys):
    monkeypatch.setenv("ANTHROPIC_API_KEY", _FAKE_KEY_MARKER)

    def _raise(env=None):
        raise JudgeUnavailable("timeout")

    monkeypatch.setattr(er_smoke, "judge_from_env", _raise)

    rc = er_smoke.main([])

    assert rc == 3
    captured = capsys.readouterr()
    parsed = json.loads(captured.out.strip())
    assert parsed == {"error": "timeout"}


# ---------- judge_from_env 재노출 sanity(실 함수 그대로 재export 하는지) ----------


def test_er_smoke_reexports_real_judge_from_env():
    assert er_smoke.judge_from_env is judge_from_env
