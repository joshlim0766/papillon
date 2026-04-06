# Issue-01: papillon 설계서(03-design-papillon.md) 리뷰

**리뷰 일시:** 2026-04-07
**대상:** 01-Planning/03-design-papillon.md
**리뷰어:** Opus (교차 리뷰)

## 높음 (6건)

| # | 파일 | 분류 | 요약 | 상태 |
|---|---|---|---|---|
| 1-1 | [01-section-numbering.md](./01-section-numbering.md) | 구조 | 섹션 번호 충돌 (`## 3.`이 두 번 등장) | **Closed** |
| 2-1 | [02-s-weight-code-review.md](./02-s-weight-code-review.md) | 공백 | S 체급 코드 리뷰 시 설계서 없는 상태의 검증 기준 미정의 | **Closed** |
| 3-1 | [03-prd-outputs-missing.md](./03-prd-outputs-missing.md) | 참조 | PRD 산출물에 inquisition, shackled 누락 | **Closed** |
| 4-1 | [04-model-name-coupling.md](./04-model-name-coupling.md) | 모순 | 다이어그램에 모델명(Opus/Sonnet) 노출 — 독립성 위배 | Open |
| 5-1 | [05-shackled-interface.md](./05-shackled-interface.md) | 누락 | shackled 호출 인터페이스 미정의 | Open |
| 5-2 | [06-error-handling.md](./06-error-handling.md) | 누락 | 에러/실패 처리 전략 부재 | Open |

## 중간 (9건)

| # | 파일 | 분류 | 요약 | 상태 |
|---|---|---|---|---|
| 1-2 | [07-ml-escalation-detail.md](./07-ml-escalation-detail.md) | 구조 | M→L 승격 안전망이 Phase 2 상세에 누락 | Open |
| 2-2 | [08-4b-code-review-skip.md](./08-4b-code-review-skip.md) | 공백 | 4-B에 코드 변경 포함 시 코드 리뷰 스킵 의도 미명시 | Open |
| 2-3 | [09-xl-prd-review-mode.md](./09-xl-prd-review-mode.md) | 공백 | XL의 Phase 2가 PRD 리뷰 모드로 동작하는 분기 없음 | Open |
| 2-4 | [10-phase4-rollback-artifacts.md](./10-phase4-rollback-artifacts.md) | 공백 | Phase 4 롤백 시 기존 산출물 처리 미정의 | Open |
| 3-2 | [11-papillon-josa.md](./11-papillon-josa.md) | 용어 | "papillon가" 조사 불일치 | Open |
| 3-3 | [12-common-spec-namespace.md](./12-common-spec-namespace.md) | 참조 | common-spec 네임스페이스에 shackled 누락 | Open |
| 4-2 | [13-step3-draft-owner.md](./13-step3-draft-owner.md) | 모순 | Step 3 Draft 생성 주체와 모델 전환 근거 불명확 | Open |
| 5-3 | [14-inquisition-interface.md](./14-inquisition-interface.md) | 누락 | inquisition 호출 인터페이스 미정의 | Open |
| 5-4 | [15-phase-io-mapping.md](./15-phase-io-mapping.md) | 누락 | Phase 간 산출물 전달(입력/출력) 매핑 미정의 | Open |

## 낮음 (4건)

| # | 파일 | 분류 | 요약 | 상태 |
|---|---|---|---|---|
| 1-3 | [16-shackled-namespace.md](./16-shackled-namespace.md) | 구조 | shackled 네임스페이스 호출 방식 미기재 | Open |
| 2-5 | [17-phase6-to-phase1-context.md](./17-phase6-to-phase1-context.md) | 공백 | Phase 6→Phase 1 복귀 시 컨텍스트 전달 미정의 | Open |
| 3-4 | [18-shackled-naming.md](./18-shackled-naming.md) | 용어 | shackled "페어 프로그래밍 스킬" 명칭 vs 실제 역할 괴리 | Open |
| 5-5 | [19-l-weight-integration.md](./19-l-weight-integration.md) | 누락 | L 체급 인테그레이션 태스크 생성 기준 미정의 | Open |

## PRD 재리뷰 추가분 (2026-04-07)

중복 건: X-1 → 기존 3-3(12번)에 메모 추가, M-1 → 기존 5-2(06번)에 메모 추가

### 중간 (4건)

| # | 파일 | 분류 | 요약 | 상태 |
|---|---|---|---|---|
| X-2 | [20-design-shackled-link.md](./20-design-shackled-link.md) | 참조 | 설계서 Context Related에 shackled 설계서 링크 부재 | Open |
| X-3 | [21-shackled-persona-roles.md](./21-shackled-persona-roles.md) | 참조 | shackled 페르소나 역할 분담(작성자/크로스 체커) 미반영 | Open |
| M-2 | [22-context-window-constraint.md](./22-context-window-constraint.md) | 누락 | 컨텍스트 윈도우 제약 미언급 | Open |
| O-1 | [23-prd-reapproval.md](./23-prd-reapproval.md) | outdated | PRD Status "Approved" 이후 스코프 변경 — re-approve 필요 | Open |

### 낮음 (4건)

| # | 파일 | 분류 | 요약 | 상태 |
|---|---|---|---|---|
| I-2 | [24-filename-notation.md](./24-filename-notation.md) | 용어 | 파일명 표기(`papillon:x.md` vs `x.md`) 혼재 | Open |
| X-4 | [25-r3-wording.md](./25-r3-wording.md) | 용어 | R3 제약 "기본/우선" vs common-spec "대신" 미세 차이 | Open |
| M-3 | [26-migration-plan.md](./26-migration-plan.md) | 누락 | 기존 wtth → papillon 전환 계획 미명시 | Open |
| O-2 | [27-cyberpink-version.md](./27-cyberpink-version.md) | outdated | cyberpink 참조 경로 버전 하드코딩 | Open |
