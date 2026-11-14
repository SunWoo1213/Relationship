# 12 · 공개 종료 체크리스트 — 2026-11-19(목) 18:00 KST (P9-infra U3)

> Refs: P9-infra CR-005 D17 security §1 §4 §5 · `11-ec2-minimal-deploy.md`
> 실행 시각은 사용자 결정 J(2026-11-14). 항목마다 "확인 방법" 과 "실행 시각·결과" 칸을 채운다(값 아닌 이름·상태만). 순서대로 — **1번(백업)이 먼저**, 인스턴스 종료는 3번.
> `down -v`·볼륨 삭제·`DROP` 류는 에이전트가 하지 않는다(security §4). 이 문서의 명령은 전부 사용자가 실행한다.

| # | 할 것 | 확인 방법 | 실행 시각 · 결과 |
|---|------|---------|---------------|
| 1 | **종료 직전 백업** — 서버에서 `docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -Fc -U <POSTGRES_USER> <POSTGRES_DB> > ~/relationship-final.dump` → 사용자 PC 로 `scp -i <키.pem> ubuntu@<EIP>:~/relationship-final.dump .` — **저장소에 넣지 않는다**(제3자 개인정보, security §5) | 로컬 파일 크기 > 0 · `pg_restore --list relationship-final.dump` 가 테이블 목록(persons·events …)을 낸다 | |
| 2 | (선택) `docker compose -f docker-compose.prod.yml down` — 인스턴스 종료로 함께 사라지므로 생략 가능. **`-v` 는 붙이지 않는다** | `docker compose ps` 빈 출력 | |
| 3 | EC2 인스턴스 **종료(terminate)** | 콘솔 상태 `terminated` | |
| 4 | EBS: 볼륨 목록에 이 인스턴스의 `available` 볼륨 **0**(루트 볼륨 "종료 시 삭제" 였는지 포함) · 스냅샷 **0** | 볼륨·스냅샷 화면 | |
| 5 | **Elastic IP 해제(release)** — 연결 안 된 EIP 도 과금된다 | EIP 목록 0 | |
| 6 | 보안 그룹·키 페어 삭제(콘솔) + 사용자 PC 의 `.pem` 삭제 | 목록에서 사라짐 | |
| 7 | 도메인 A 레코드 삭제(sslip.io 를 썼으면 할 일 없음) | `dig +short <호스트명>` 빈 출력(전파 뒤) | |
| 8 | **비밀 회전**: OpenAI 배포용 키 폐기(로컬 `.env` 가 같은 키였다면 새 키로) · 배포용 VAPID 키 폐기(결정 N — 로컬 구독 영향 없음) | OpenAI 대시보드 키 목록 · 로컬 `.env` 갱신 | |
| 9 | **유지하는 것**: AWS Budgets 알림 3개 · 계정(크레딧 잔여 — 6개월 뒤 Free Plan 종료 안내를 확인하고 그때 계정 처리 결정) | Budgets 화면 | |
| 10 | 최종 확인: `curl -sS -m 5 -o /dev/null -w '%{http_code}' https://<호스트명>/` 가 연결 실패(`000`) · **다음 날** Billing 에서 EC2·EBS·퍼블릭 IPv4 사용량이 종료 시각 뒤 증가 0 | 두 출력 | |

## 끝났다는 증거 (04-review·03-log)
3·4·5 번의 콘솔 상태(terminated / 볼륨 0 / EIP 0) · 1 번 백업 파일 크기(값 아닌 바이트 수) · 8 번 회전 완료 — 03-log 에 시각과 함께 한 줄. P9 패키지는 이 문서가 전부 채워진 뒤 04-review `완료`·사용자 확인으로 닫는다.
