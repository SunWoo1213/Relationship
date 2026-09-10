# 02 · AWS Budgets 비용 알림 ($10 / $30 / $50)

## 언제 필요한가
CLAUDE.md "첫날 필수". `docs/backlog.md` 13행 `[사용자]` 항목이 아직 `[ ]`. 실서버(P9) 전에는 반드시, 지금 해 두면 좋다. `SERVER-CHECKLIST.md` 0-5 가 승격 전 점검 항목으로도 본다.

## 왜 사용자 몫인가
AWS 콘솔 로그인·결제 정보는 에이전트가 접근하지 않는다(`security.md` §4). Terraform 으로 코드화하는 것은 P9 에서 검토하되, 알림 자체는 지금 콘솔에서 켠다.

## 절차 (콘솔, 10분)
1. AWS 콘솔 → Billing and Cost Management → **Budgets** → Create budget.
2. Budget type: Cost budget. Period: Monthly. Budgeted amount: **10** USD. 이름 예: `capstone2-10`.
3. Alert threshold: Actual 100% → 이메일(본인 주소). 저장.
4. 같은 방식으로 **30**, **50** USD 예산을 각각 만든다(총 3개). 한 예산에 임계치 3개로 만들어도 되지만, 수용 기준 문장이 "알림 3개 활성"이므로 3개가 명확하다.
5. Credits 페이지에서 크레딧 잔액을 확인하고 아래 "증거"에 메모한다.
6. (선택) Cost Anomaly Detection 도 켠다.

## 끝났다는 증거
- 수용 기준(backlog 13행): "알림 3개 활성, 잔액 메모 또는 스크린샷".
- 스크린샷은 저장소에 넣지 않는다(계정 정보 노출). 이 파일 아래에 날짜·예산 이름 3개·잔액만 적는다.

| 날짜 | 예산 이름 3개 | 크레딧 잔액 | 비고 |
|------|--------------|------------|------|
| | | | |

## 끝난 뒤 에이전트에게
"AWS Budgets 3개 켰어, 잔액 ○○" → 에이전트가 backlog 13행 `[x]` 와 이 표 갱신을 커밋 초안으로 올린다.
