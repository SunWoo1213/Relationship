# D10 · 임계치는 두 개 (T_merge, T_new)

상태: 유효 | 해결하는 검증: R3 | 원문: `docs/resolution-plan.md` §1 D10, §3.3, §3.7

**결정**
- `confidence ≥ T_merge` → 자동 연결
- `[T_new, T_merge)` → `ask_user(kind="identity")`
- `< T_new` → `ask_user(kind="new_person")` (D1)
- 초기값 `T_merge=0.8`, `T_new=0.3`. 파일럿 곡선으로 확정.

**방향 (기획서 5.2 문장 정정)** T_merge를 **높이면** 오병합↓ 질문↑. 곡선 x축 = T_merge ∈ {0.5,…,0.95}, T_new 고정.

**코드에서 지켜야 할 것** 임계치 하나로 구현하지 않는다. 두 값 모두 설정값이며 trace `decision`에 어느 구간이었는지 남긴다.
