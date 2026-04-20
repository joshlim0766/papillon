# TDD-ready Exemplar 독립 재평가 메모 (2026-04-20 회사 세션)

## 목적

회사 세션에서 shackled 실측 + exemplar 익명화 복제 + v0.2.0 환류를 진행하기 전에, **실측 없이 독립 판정 가능한 부분만 먼저 박제**한다. 이 메모는 환류 프로토콜 §8의 "tracing 4건" 중 *신호·AP가 구조적으로 충족/위반되었는가* 축의 사전 데이터로 재활용한다.

**박제 회피 원칙**: shackled TDD 실측은 2f 진입 시점부터 관측 가능(2e는 지시서 wtth 리뷰까지 완료된 상태이나 shackled 실행은 2f와 함께 진행)이므로 이 메모는 **MUST/SHOULD 재분류를 확정하지 않는다**. 구조적 신호 충족 여부만 기록하고, "이 신호가 없었다면 shackled가 실패했을 곳" 판정은 실측 후로 미룬다.

## 평가 기준

- 8개 신호 (Issue-06 #1 v0.1.0-draft §4 기준): #1 RED 번호 / #2 I/O data class / #3 에러 타입 응집 / #4 의존 DAG / #5 TDD 플래그 헤더 / #6 테스트 파일 경로 / #7 TDD 구현 규율 (7A+7B) / #8 상태·부작용 경계
- 3개 anti-pattern: AP-1 비결정적 RED / AP-2 구현 상세 검증 / AP-3 선결 환경 vs TDD 범위 분리

## 전수 평가 (10개 파일)

원본 위치: `~/Work/megabird/megabird-work-plan/QLSN-476/QLSN-478/50-pipeline/T1-stats-consumer/`

| 파일 | 체급 | 적합도 | 인덱스 기존 | 변동 |
|---|---|---|---|---|
| `shackled-phase1-directive.md` | L | **N/A ★★★★★** | ✅ N/A | 유지 — "TDD 없음" 플래그 명시가 AP-3 분리의 모범 |
| `shackled-phase2-00-overview.md` | — | **공통 ★★★★★** | ✅ 공통 제약 | 유지 — G6(TDD 역순 금지) + ASCII 의존 DAG + `pipeline/exceptions/` 응집 근거 박제 |
| `shackled-phase2a-bms-validator.md` | S | **★★★★★** | ✅ ★★★★★ | 유지 |
| `shackled-phase2b-channel-type-code.md` | S | **★★★★★** | ❌ 미등재 | **신규 exemplar 후보**. L3 "비즈니스에서 import 금지" 경계 선언 (신호 #8 모범) + RED 6건 경계값 |
| `shackled-phase2c-original-lookup.md` | M | **★★★★★ (상향)** | ✅ ★★★★ | §3.0 "선행 작업" 섹션이 AP-3 모범 → 상향 제안 |
| `shackled-phase2d-dimension-mapper.md` | S | **★★★★★** | ❌ 미등재 | **신규 exemplar 후보**. 의존 DAG 헤더 명시 + BMS 방어 `?: throw` 패턴 |
| `shackled-phase2e-upsert-service.md` | L | **★★★★ (상향)** | ✅ ★★★☆ | 배치 재작성(RDR 2026-04-17)으로 기존 AP-1(실제 MySQL 데드락) **상류 해소** → 상향. 단 RED 7 race / RED 9 성능 sanity는 환경 의존 잔존 |
| `shackled-phase2f-pipeline-assembly.md` | L | **★★★★★** | ❌ 미등재 | **신규 exemplar 후보 (L급 모범)**. RED 12건 + `DltErrorReason.from` cause 체인 매핑 + L9~L12 경계 선언 |
| `shackled-shared-tenant-context-use-block.md` | XS | **★★★★☆** | ❌ 미등재 | XS급 선행 exemplar. RED 4건(중첩/예외/반환값). 공통 G6 참조 부재는 shared 모듈 맥락상 타당 |
| `shackled-use-tenant-directive.md` | S | **★★★★** | ❌ 미등재 | RED 1의 `verify: stmt.execute("USE...")` mock verify가 **AP-2 경계 사례**. RED 2 SELECT DATABASE() behavior 검증이 있어 정화 여지 |

## 핵심 발견

### 발견 1 — 인덱스 stale (실측 없이도 확정)

- phase2c: §3.0 "선행 작업 — AbstractIntegrationTest 확장" 섹션이 AP-3(TDD 루프 밖 선결 분리) 모범. 기존 ★★★★ → **★★★★★ 상향 근거**.
- phase2e: 2026-04-17 RDR-stats-consumer-batch-processing-redesign §2.1로 단건 시대 AP-1(실제 MySQL 데드락 RED) **상류 해소**. 새 RED 7은 "배치 전환이 race를 해결함" 회귀 증명으로 바뀜. 기존 ★★★☆ → **★★★★ 상향 근거**.
- 미등재 5건(phase2b/phase2d/phase2f/use-block/use-tenant) 각자 다른 신호의 모범을 보여 exemplar 스코프 확장 강력 권고.

**환류 시 적용**: v0.2.0 draft §참조 샘플 테이블 재작성.

### 발견 2 — exemplar 스코프 5건 → 10건 확장 시 효과

현 인덱스는 3건(2a/2c/2e)만 중심 샘플. 10건 전체를 exemplar로 취하면:
- **v0.2.0 발행 기준 "최소 3개 exemplar 분석"** (Issue-06 §8) 초과 달성.
- 체급 다양성 확보: XS(use-block) / S(2a,2b,2d,use-tenant) / M(2c) / L(1,2e,2f) / 공통(overview).
- 신호별 모범 분포: #2 data class 모범(2a/2c/2d/2e/2f), #3 에러 응집 극상(2f `DltErrorReason.from`), #4 의존 DAG 모범(overview + 2d/2e/2f 헤더), #8 경계 극상(2b L3, 2e §1.3+§5.3, 2f L9~L12).

### 발견 3 — 학습 케이스 2건 (anti-pattern 교정 방향)

v0.2.0에서 anti-pattern 섹션에 보존 가치 있는 사례:
- **phase2e RED 7 전환사** (단건 시대 "실제 MySQL 데드락 유발" → 배치 시대 "race 상류 해소 회귀 증명"): AP-1 해소 방향의 모범.
- **use-tenant RED 1** (`verify: stmt.execute("USE...")` mock verify): AP-2 경계 사례. RED 2 `SELECT DATABASE()` behavior 검증이 병존하므로 "RED 1을 behavior 검증으로 합칠 수 있다"는 리팩토링 권고 예시로 활용.

## 회사 세션 착수 체크리스트 (이 메모 재진입)

- [ ] exemplar 익명화 복제 — QLSN/T1/megabird-ds/BMS/TMG_MSG_TGUS 등 고유명 마스킹 규칙 확정 후 `80-Issue/06-Issue-06/exemplar/` 배치
- [ ] shackled 실측 데이터 수집 — 2f 진입 후 2e·2f TDD 실행 결과 (P0/P1 건수, TDD 루프 이탈 여부, 실패 지점). 2e 지시서는 이미 wtth 리뷰 반영본
- [ ] 환류 프로토콜 §8 tracing 4건 수행 (이 메모의 구조적 평가 + 실측 데이터 결합)
- [ ] v0.2.0 draft 갱신:
  - §참조 샘플 테이블 재작성 (10건 반영)
  - §TDD-ready 신호 재분류 (MUST/SHOULD 확정 또는 유지)
  - §anti-pattern 학습 케이스 2건 추가 (위 발견 3)
- [ ] v0.2.0 발행

## 안전성 메모

- 이 메모는 원본 파일 **읽기만** 수행한 결과. 원본 megabird 레포 무변경.
- 원본 파일 수정·복제는 향후에도 금지 유지. 복제 방향은 `~/Work/megabird/... → improve-review-hell/.../exemplar/` 일방.
- 회사 세션에서 shackled 실측 완료 후 익명화 복제 착수.

## 참조

- Issue-06 #1 draft: `80-Issue/06-Issue-06/tdd-ready-spec-v0.1.0-draft.md`
- Issue-06 개설 인덱스: `80-Issue/06-Issue-06/00-index-issue-06.md`
- 원본 exemplar: `~/Work/megabird/megabird-work-plan/QLSN-476/QLSN-478/50-pipeline/T1-stats-consumer/shackled-*.md`
- 배치 전환 RDR: `megabird-stats-billing/docs/decisions/reviews/RDR-2026-04-17-stats-consumer-batch-processing-redesign.md` (phase2e AP-1 상류 해소 근거)
