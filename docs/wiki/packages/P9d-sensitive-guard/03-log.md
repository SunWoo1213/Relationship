# P9d-sensitive-guard · 구현 로그 (03-log)

> /commit 이 커밋마다 항목 하나를 **아래에** 붙인다(LLM 작성). 이어서 작업하는 에이전트는 마지막 두 항목만 읽으면 된다.
> 형식은 고정. 지우거나 고쳐 쓰지 않는다.

## 2026-11-22 17:35 · docs(P9d-sensitive-guard): 민감 정보 가드레일 계획을 검증까지 마치고 활성화한다 · 947c12c
- 변경: `01-plan.md`(architect 초안 → 개정 1 → 개정 2 + 3회차 권고 P3-R1~R7 반영), `02-plan-verify.md`(verifier 1차 보류 M1~M4 → 2차 보류 M2-잔여·M5 → 3차 **통과**, 점검표 8/8, [필수] 0), verify-plan 증거(마지막 `evidence/20261122-1732-verify-plan-r3-confirm.txt` FAIL 0 · 보류 0 · WARN 57 = registry "다른 패키지로 이미 있음"), 사용자 결정 22(N7)·D-1~D-4 를 `CR-009.md`·`D20`·`S3.2`·`backlog` 에 반영, `CURRENT.md` `active: P9d-sensitive-guard`(P9b-auth 보류 메모).
- 이유(기획서·카드 연결): CR-009 · D20 — 졸업평가(11-18)에서 받은 민감 정보 피드백을 해결한다. 식별·인증 정보는 LLM 전에 가리고, 민감 범주는 칩 동의 뒤에만 처리·저장하며, 가입 때 OpenAI API 전송을 고지한다. 사용자 결정은 AskUserQuestion 9회(22건 + D-1~D-4)로 모두 확정했다.
- 정합성 확인: 원칙 1·2·4(이름 규칙은 병합·생성·질문 0 — D20 R-7)·6·7(가드레일은 상담이 아니다)·8(test 세트 동결)·9(거절·만료 원문 삭제 예외) / D20 ① 표 1~17·② R-1~R-12 / S3.1(0006)·S3.2(툴 7종 시그니처 불변)·S3.4·S3.5·S3.6 / security §5 — 위반 없음(verifier 3회차 점검표 8행 통과).
- 남은 것 · 다음 단위: U1(eval-agent — 시험 세트, test 동결) ∥ U3(backend-agent — 리비전 0006) → U2 ∥ U4 → U5a → U5b → U5c → U6 → U7a → U7b → U8, U9a 는 U4 뒤 병행, U9b·U10 → U11 완료 검토 → U12 운영 반영(메인 SSH, 백업 먼저 — 운영에서 되돌릴 수 있는 것은 민감 칩에 답이 달리기 전까지). 단위마다 verifier 커밋 전 리뷰. 목록 밖 시험이 깨지면 구현자는 고치지 않고 멈춰 보고한다. 미리 셀 수 없는 것: U2 낱말 목록이 기존 채팅 시험 발화에 걸릴 수 있다(U5a·U5b 에서 드러남).
- Refs: P9d-sensitive-guard CR-009 D20 S3.1 S3.2 S3.4 S3.5 S3.6 S3.7 원칙7 원칙8 원칙9

## 2026-11-22 18:05 · feat(P9d-sensitive-guard): 민감 표시와 고지 동의를 담을 컬럼을 더한다 (U3) · 61a5241
- 변경: `alembic/versions/0006_sensitive_guard.py`(새 컬럼 6 — events 2 · person_facts 1 · schedules 1 · users 2, 범주 CHECK 3, kind CHECK 4종. 테이블·인덱스·UNIQUE·FK 추가 0), `app/db/models.py`(`QUESTION_KINDS` 4종, `SENSITIVE_CATEGORIES`, 새 컬럼·CHECK), 새 `tests/test_migration_0006.py` 19건, 닫힌 목록 6파일의 고정 단언(총 컬럼 79→85 · nullable 7→11 · CHECK 5→8 · kind 3→4 · head `0006`). 개발 DB 를 0005 → 0006 으로 올렸고 13개 테이블 행 수는 전후 같다.
- 이유(기획서·카드 연결): D20 ① 표 #14 · S3.1 리비전 0006 보충 — 뒤 단위(U4 고지, U5b 동의 질문, U7a 표시 전파)가 쓸 자리를 먼저 만든다. 사용자 결정 9(소급하지 않음)에 따라 기존 행은 하나도 바꾸지 않는다. downgrade 는 민감 행·민감 동의 질문·동의 참조가 하나라도 있으면 개수만 담아 실패한다(표시가 컬럼과 함께 사라지면 민감 기록이 일반 기록으로 바뀌므로).
- 정합성 확인: 원칙 9(판정 근거 — 이 단위는 trace 무변경) / D20 #14·R-5·5절 / S3.1(스키마 v2 + 0006)·S3.2(툴 7종 7/7, `app/er/` 무변경) / 보안 §4(DELETE·UPDATE·TRUNCATE·DROP TABLE 없음, 오류 메시지에 원문 0) — 위반 없음. verifier `review-u3.md` **통과**([필수] 0).
- 계획에 없이 구현자가 정한 것 3가지(verifier 타당 판정): ① 새 문자열 컬럼 타입 `sa.String()`(S3.1 문언 "VARCHAR NULL" 그대로, 기존 컬럼 대부분은 Text) ② CHECK 이름 `ck_{표}_sensitive_category_valid` 와 문장 `sensitive_category IN (…5종)`(기존 `kind_valid` 규약) ③ `SENSITIVE_CATEGORIES` 를 `app/db/models.py` 에 둠.
- 남은 것 · 다음 단위: U4(backend-agent — 고지 API·403·주기 브리핑 건너뜀). 열린 권고(review-u3): **R-2** `test_upgrade_changes_no_existing_data` 스냅샷에 시각 컬럼이 없어 verifier 변이 2건 통과 → U4 위임에 함께 넣는다 · **R-3** U2 는 범주 상수를 따로 정의하지 않고 `app.db.models.SENSITIVE_CATEGORIES` 를 가져온다(동등 단언 포함) · **R-4** downgrade 가드의 세기와 DDL 사이 틈 → U12 문서 J절에 "백엔드를 내린 뒤 downgrade" 를 적는다. U1(eval-agent)은 진행 중이고 그 산출물(`evaluation/sensitive_guard/`·`scripts/validate_sensitive_set.py`·`evidence/*-u1-*`)은 이 커밋에 넣지 않는다.
- Refs: P9d-sensitive-guard CR-009 D20 S3.1 원칙9

## 2026-11-22 19:50 · feat(P9d-sensitive-guard): 전송 고지에 동의해야 대화를 보낼 수 있게 한다 (U4) · 5fc2b79
- 변경: `app/settings.py`(`PRIVACY_NOTICE_VERSION = 1`), `app/auth/deps.py`(`notice_required`·`require_notice` 403), `app/auth/routes.py`(가입 422 `notice_required` — 형식 3종 뒤·409 앞, 가입 때 판 번호·시각 기록, `POST /auth/privacy-notice` 204), `app/api/schemas.py`(`SignupIn.privacy_notice_accepted`·`MeOut.notice_required`), `app/api/routes.py`(`/chat`·`/answers/{id}`·`/briefings/run` 의존성을 `require_notice` 로), `app/briefing/scheduler.py`(`_due_user_ids` 가 `users` 조인 — 미동의·계정 없는 인물 건너뜀). 새 `tests/test_privacy_notice.py` 20건, 기존 단언 7줄(계획 VR3 예외)과 가입 본문·계정 준비 줄, `evaluation/recognition/probe.py` 가입 본문. 함께: `tests/test_migration_0006.py` 스냅샷에 시각 컬럼(review-u3 R-2 닫음). 사용자 결정 23~26(범주 경계)을 `D20` 에 기록.
- 이유(기획서·카드 연결): D20 고지 행 · D18 CR-009 보충 · 사용자 결정 5·16·17·21 — 가입 때 OpenAI API 전송에 동의를 받고, 기존 가입자는 동의 전까지 대화·칩 답·수동 브리핑이 403 이며 주기 브리핑·푸시도 건너뛴다. 403 을 의존성으로 건 것은 LLM·임베딩 의존성보다 먼저 풀려 전송 0 을 구조로 보장하기 때문이다.
- 정합성 확인: 원칙 7(가드 문구에 감정·평가 없음 — 이 단위는 문구를 싣지 않는다)·9(건너뛴 계정 trace 0 은 계획 VR7) / D20 · D18(로그인 없이 열린 예외 불변 — 새 라우트는 로그인 필수) / S3.4·S3.6 / S3.2(툴 7종 7/7, `app/er/` 무변경) / 보안 — 위반 없음. verifier `review-u4.md` **통과**([필수] 0 · [권고] 4).
- 계획에 없이 구현자가 정한 것 2가지(verifier 타당 판정): ① 동의 시각은 `get_auth_now`(가입이 이미 받는 시계) ② `test_briefing_scheduler_users.py` 의 계정 준비를 `_person` 도우미 안 한 줄로.
- 남은 것 · 다음 단위: **U4 보강**(backend-agent, review-u4 R-2 가입 동의 값을 엄격한 불리언으로 · R-3 "현재보다 높은 판" 계정 시험 · R-4 낡은 docstring 3곳) → verifier 확인 → 커밋. U9a(frontend-agent — 가입 고지 체크·재고지 모달). 이 커밋부터 U9a 전까지 로컬 프론트의 가입은 422 `notice_required` 다(운영은 끝난 뒤 한 번에 반영하므로 영향 없음). U1 은 리뷰 보류 — 사용자 결정 23~26 반영 재작업 뒤 2회차. U12 점검에 "계정 없는 인물 수" 질의 한 줄을 넣는다(review-u4 N-6).
- Refs: P9d-sensitive-guard CR-009 D20 D18 S3.4 S3.6 원칙7 원칙9

## 2026-11-22 20:35 · fix(P9d-sensitive-guard): 가입 동의는 불리언 true 일 때만 받는다 (U4 보강) · 2a9b65d
- 변경: `app/api/schemas.py`(`SignupIn.privacy_notice_accepted` 를 `bool | None` → `Any = None` — 값을 바꾸지 않고 받아 라우트의 `is not True` 가 판정), `tests/test_privacy_notice.py`(가입 "동의 없음" 매개변수 3 → 10, 높은 판 계정 시험 2건), docstring 3곳(`app/briefing/scheduler.py`·`app/api/routes.py`·`app/auth/__init__.py` — 동작 변경 없음).
- 이유(기획서·카드 연결): D20 고지 행 — 동의는 사용자가 체크했다는 뜻이어야 하는데, 보강 전에는 문자열 `"true"`·숫자 `1` 도 동의로 기록됐다(review-u4 R-2). 메인 세션은 `StrictBool` 을 요청했으나 구현자가 `Any` 를 골랐다: `StrictBool` 이면 불리언이 아닌 값이 detail 목록 422 로 나가고 아이디 형식 오류보다 먼저 나가, 계획 U4 의 "목록 모양 detail 0"·"형식 → 동의 → 409 순서"가 깨진다. verifier 가 런타임 치환으로 확인(14종이 목록 422).
- 정합성 확인: D20 · D18 · 계획 U4 가입 검사 순서 / S3.2(툴 7종 7/7) — 위반 없음. verifier `review-u4b.md` **통과**([필수] 0 · [권고] 2). review-u4 R-2·R-3·R-4 닫힘.
- 하네스 메모: 구현자가 저장소 밖 사본을 만들지 못해(복사 명령 권한 거부) **변이 시험을 저장소 파일을 고쳤다 되돌리는 방식으로 돌렸다** — 규칙 밖. verifier 가 잔재 0 을 확인했다(`evidence/20261122-1950-verifier-u4b-residue.txt`). 뒤 단위 위임 프롬프트에 "복사가 안 되면 런타임 치환(import 시점 치환), 저장소 파일 수정 금지"를 넣는다.
- 남은 것 · 다음 단위: U9a 리뷰 중 · U1 재작업 중. `app/auth/routes.py` 155~156행 주석("없음·false 모두")은 다음에 그 파일을 고칠 때 맞춘다(review-u4b N-3).
- Refs: P9d-sensitive-guard CR-009 D20 D18

## 2026-11-22 21:50 · eval(P9d-sensitive-guard): 민감 가드 시험 세트를 만들고 test 를 동결한다 (U1) · pending
- 변경: `evaluation/sensitive_guard/dev.jsonl`·`test.jsonl`(각 315줄 — 범주·유형 11개 × 15, 동의 범주마다 조회형 2, 평범 100, 함정 30, 우회 20), `README.md`(한 줄 형식·범주 정의·함정 종류·누출 경로·한계·해시), `scripts/validate_sensitive_set.py`(형식 검사기), 새 `tests/test_validate_sensitive_set.py` 28건.
- 이유(기획서·카드 연결): D20 · S3.7 CR-009 보충 · 사용자 결정 12(세트 크기) — 규칙 모듈(U2)을 만들기 **전에** 시험 세트를 고정한다(원칙8). U2 는 dev 만 보고, test 는 U10 에서만 연다.
- 검수 경과(verifier, 3회): **1차 보류**(630줄 전수 — 라벨은 깨끗, 그러나 README 가 test 전용 낱말 13개를 실음 · 이름만 다른 dev/test 쌍 6 · `test-029` · 범주 정의가 사용자 결정 전) → **사용자 결정 23~26**(노조 = 민감 · 금융 = 빚·연체·파산·추심만 · 인물 없는 화제도 낱말이 있으면 묻기 · 외도 = 민감) → 2차 판(dev 8줄 · test 17줄) → **2회차 보류**(결정 25 를 재는 줄 0) → 3차 판(dev-011·028·071, test-013·023·068) → **3회차 통과**. 판마다 label·group 이 바뀐 줄은 0 이고 text·note·trap 만 바뀌었다.
- **test 동결**: sha256 `62be9136f98ecc87b94f6791c07930c59bd1f4da3516b2a0ae045db492484223`(dev `7dc6f96577265fb9469a46b1efdfd9e2dcb8e6aa204e73a591f35d2c0aac92c3`). 동결 커밋 = 이 커밋(`git log --diff-filter=A --format=%H -- evaluation/sensitive_guard/test.jsonl`). 앞 판 해시: 1차 test `eeaf7847…aa915`, 2차 test `b0b2e1e8…e7dd2b`(둘 다 커밋된 적 없음).
- 정합성 확인: 원칙 7(문장이 감정·상담을 유도하지 않음)·8(test 동결, dev/test 닮음 수치를 한계로 공개) / D20 결정 1·2·6·12·23~26·R-12(식별번호는 지어낸 값 — 주민번호 검증 숫자 불일치, 카드는 공개 시험 번호) / S3.7 — 위반 없음. `app/`·`reports/`·기존 ER 데이터셋 무변경.
- 계획 밖: 검사기 시험 파일은 계획 U1 파일 목록에 없었고 검수 권고(R-3)로 더했다. 메인 세션이 결정 2 에서 이은 것 — 만성질환·수술·입원은 `none`(dev-268·289, test-268·289 가 여기에 달림. 사용자에게 보고함, 다르게 정해지면 동결 뒤 수정 절차).
- 남은 것 · 다음 단위: **U2**(backend-agent — 규칙 모듈. dev 만 본다 · 범주 상수는 `app.db.models.SENSITIVE_CATEGORIES` 를 가져온다(review-u3 R-3) · "인물 없는 문장도 범주 낱말이 있으면 건다, 문맥 낱말 허용 목록 0"을 단위 시험으로(review-u1 R3-3) · README·카드에서 온 낱말과 dev 에서 귀납한 낱말을 구분해 보고). U10 보고서에: 결정 25 줄은 파일마다 2줄이라 건수로 보고 · 평범·함정 오탐률은 dev 와 독립이 아닌 문장에서 잰 값(R3-2·R-7). 검사기 남은 빈틈(R2-5). 01-plan 의 U1 체크는 architect 가 그 파일을 개정 중이라 다음 커밋에서 한다.
- Refs: P9d-sensitive-guard CR-009 D20 S3.7 원칙7 원칙8
