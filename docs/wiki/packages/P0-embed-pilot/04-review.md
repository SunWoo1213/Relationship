# P0-embed-pilot · 완료 검토 (04-review)

날짜: 2026-09-03 | 검토자: 메인 세션(Claude), 승인은 사용자

## 1. 기계 검증 출력 (그대로 붙인다)
명령: `bash .claude/scripts/verify-impl.sh P0-embed-pilot | tee docs/wiki/packages/P0-embed-pilot/evidence/20260903-verify-impl.txt`
```
== verify-impl P0-embed-pilot  (20260903-1933) ==
..........                                                               [100%]
10 passed in 0.07s
PASS  pytest 통과 → evidence/20260903-1933-pytest.txt
PASS  compileall 통과 → evidence/20260903-1933-lint.txt
PASS  태그 P0-embed-pilot 커밋 3 건 → evidence/20260903-1933-commits.txt
PASS  커밋에 태그 존재: D4
PASS  커밋에 태그 존재: D5
PASS  커밋에 태그 존재: R5
PASS  커밋에 태그 존재: S3.1
PASS  커밋에 태그 존재: S3.3
PASS  증거 확인:  한국어 짧은 호칭 30개 유사도 행렬 2� ← reports/embed_pilot.md
PASS  증거 확인:  (세부) 호칭 30개 유사도 행렬 2종 — t ← reports/embed_pilot/text-embedding-3-sma
PASS  증거 확인:  (세부) 선택 근거 1문단 — reports/embed_ ← reports/embed_pilot.md
PASS  증거 확인:  (세부) 확정 차원 N 기록 — N=1536, D04 � ← docs/wiki/decisions/D04-embedding-provid
PASS  증거 확인:  (설계 준수) D4 "EmbeddingProvider 인터페� ← scripts/embed_pilot.py, 876a450, evidenc
PASS  registry 에 P0-embed-pilot 행 있음
PASS  작업 단위 모두 완료 표시
== 결과: FAIL=0 WARN=0 → evidence/20260903-1933-summary.txt ==

(1차 실행 evidence/20260903-verify-impl.txt 는 FAIL 1 — 검증 스크립트의 제목 패턴 버그, 소견 F-445cda 로 해소. 위 출력의 깨진 글자는 cut -c 바이트 절단 표시일 뿐이다)
```
FAIL 은 `findings.py … --source verify-impl` 로 05-remediation.md 에 올리고 조치·재검증한다. 열린 [필수] 소견이 있으면 결과는 완료가 될 수 없다.

## 2. 수용 기준 대조
증거 열은 `evidence/` 파일, 커밋 해시(7자 이상), 존재하는 파일 경로 중 하나여야 한다(`verify-impl.sh` 가 실재를 검사한다). 문장만 있는 증거는 FAIL.

| 기준 (backlog 와 동일 문장) | 증거 | 결과 |
|------------------------------|------|------|
| 한국어 짧은 호칭 30개 유사도 행렬 2종, 선택 근거 1문단, 확정 차원 N 기록 | reports/embed_pilot.md | 통과 |
| (세부) 호칭 30개 유사도 행렬 2종 — text-embedding-3-small · text-embedding-3-large | reports/embed_pilot/text-embedding-3-small.json, reports/embed_pilot/text-embedding-3-large.json, evidence/20260903-embed-pilot-run.txt | 통과 |
| (세부) 선택 근거 1문단 — reports/embed_pilot.md "선택 근거 (1문단)" 절 | reports/embed_pilot.md | 통과 |
| (세부) 확정 차원 N 기록 — N=1536, D04 카드·S3.1 카드 반영 | docs/wiki/decisions/D04-embedding-provider.md, docs/wiki/specs/S3.1-schema-v2.md | 통과 |
| (설계 준수) D4 "EmbeddingProvider 인터페이스 뒤에 둔다", 검증 기준 판정 로직 | scripts/embed_pilot.py, 876a450, evidence/20260903-pytest-U1.txt | 통과 |

## 3. 부정 케이스 (되지 말아야 할 것이 안 되는지)
| 케이스 | 명령 | 증거 |
|--------|------|------|
| 키 없이 실행하면 API 를 호출하지 않고 rc=2, 파일을 만들지 않는다 | `python -m pytest -q tests/test_embed_pilot.py -k api_key` | evidence/20260903-pytest-U1.txt (test_main_exits_2_without_api_key) |
| 가족이 직장 호칭보다 가까운 공급자는 필수 기준 FAIL 로 판정된다 | `python -m pytest -q tests/test_embed_pilot.py -k family_is_closer` | evidence/20260903-pytest-U1.txt (test_run_pilot_fails_when_family_is_closer_than_colleague) |
| 임베딩 수가 입력 수와 다르면 예외 | `python -m pytest -q tests/test_embed_pilot.py -k wrong_vector_count` | evidence/20260903-pytest-U1.txt |
| 키 값이 출력·저장되지 않는다 | `grep -c "sk-" docs/wiki/packages/P0-embed-pilot/evidence/20260903-embed-pilot-run.txt reports/embed_pilot/*.json` → 0 | evidence/20260903-embed-pilot-run.txt |

## 4. 닫힌 검증 항목 R (review-index.md 상태를 "구현완료(해시)"로 바꿨는가)
- R5 → "해소(파일럿 확정: OpenAI text-embedding-3-small, N=1536)". 커밋 해시는 U3 커밋 후 `구현완료(<hash>)` 로 갱신.

## 5. registry.md 에 올린 산출물
- 스크립트 scripts/embed_pilot.py (P0-embed-pilot)
- 테스트 tests/test_embed_pilot.py (P0-embed-pilot)
- 리포트 reports/embed_pilot.md, reports/embed_pilot/*.json (P0-embed-pilot)

## 6. 열린 문제 → FIX-nnn / L-nnn / 05-remediation 잔여 소견
- 없음. (관찰: 같은 성씨 다른 직급이 0.74 로 가깝다 — 규칙 필터·LLM 판정 필요. S3.3 설계 그대로이며 새 소견 아님.)

## 7. 다음 패키지에 넘기는 것 (인터페이스·설정값·주의)
- P1-schema: `person_aliases.embedding vector(1536)`. `.env.example` `EMBEDDING_MODEL=text-embedding-3-small`.
- P2-tools/P3-er: `EmbeddingProvider`(embed/dimension) 와 `OpenAIEmbeddingProvider` 를 scripts/embed_pilot.py 에서 백엔드 모듈로 옮긴다(registry 비고). 코사인 유사도 사용. 임계치는 모델별 보정 필요(reports/embed_pilot.md 관찰) — P4-pilot-eval 에서 확정.
- P3-er 규칙 필터: 같은 성씨 다른 직급(김팀장↔김부장 0.74), 대명사(0.3~0.55) 는 임베딩만으로 못 가른다.

결과: 완료
승인: 사용자 (2026-09-03)
