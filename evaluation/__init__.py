"""Refs: P3-baselines S3.7 D10 원칙2 원칙8 -- 평가 장치 패키지(제품 런타임이 아니다).

`evaluation/` 는 **평가를 위한 코드만** 담는다(01-plan 결정 A(i)):
베이스라인 3종·제안 방식 어댑터·시나리오 사전 상태 적재기(P3-baselines),
그리고 앞으로 올 러너·지표 계산기(P4-pilot-eval). 제품 런타임은 `app/` 이고
둘의 의존 방향은 **한쪽뿐**이다.

## 의존 방향 (R-2, 02-plan-verify §3)

    evaluation/  --import->  app/          (허용: 어댑터가 `app.er.resolve` 를 부른다)
    app/         --import->  evaluation/   (금지)

`app/` 아래 어떤 모듈도 이 패키지를 import 하지 않는다. 그래야 원칙4
("엔티티 해석은 LLM 단일 호출로 하지 않는다")가 금지한 대비군(베이스라인 3
= LLM 단일 프롬프트)이 제품 코드 경로에 섞이지 않는다. 이 방향은
`tests/test_baseline_base.py` 가 `app/` 아래 `.py` 를 순회해 단언한다.

## 이 패키지가 하지 않는 것

- **지표를 재지 않는다.** 오병합률·미검출률·F1·보정표·트레이드오프 곡선과
  `reports/` 산출물은 P4-pilot-eval 몫이다(01-plan "이 패키지에서 하지
  않는 것"). 여기 있는 resolver 들은 mention 하나의 **결정**만 낸다.
- **DB 를 바꾸지 않는다.** 어떤 방식도 `create_person`·`update_person`·
  `ask_user`·`apply_resolution` 을 부르지 않는다(부수효과 0, 원칙1·2).
"""
