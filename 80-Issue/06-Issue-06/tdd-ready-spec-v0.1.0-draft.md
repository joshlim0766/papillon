# TDD-ready 설계서 규격 v0.1.0-draft

## Context
- **Parent:** [Issue-06](./00-index-issue-06.md)
- **Related:**
  - [02-common-spec.md](../../01-Planning/02-common-spec.md) — v1.0 안정화 시 §14로 흡수 또는 분할 후 편입
  - [04-wtth/02-design/02-review-design.md](../../01-Planning/04-wtth/02-design/02-review-design.md) — testability invariant 반영 대상 (Issue-06 #3)
  - [06-shackled/02-design/](../../01-Planning/06-shackled/02-design/) — `tdd_mode` 소비 (Issue-06 #4)
  - [05-inquisition/02-design/](../../01-Planning/05-inquisition/02-design/) — `tdd_mode` 질문 추가 (Issue-06 #2)
- **Status:**
  - Work: **Draft (v0.1.0-draft)**
  - Review: None
  - 환류 예정: 회사 exemplar shackled 실측 분석 → v0.2.0

---

## 0. Draft 경고 (반드시 읽을 것)

이 문서는 exemplar 실측 **전** 작성된 **연역적 가설 스펙**이다. 회사 exemplar(`~/Work/megabird/megabird-work-plan/QLSN-476/QLSN-478/50-pipeline/T1-stats-consumer/shackled-phase2*.md`)에서 shackled(Sonnet) 실행 시 P0/P1 0건 달성한 실증 데이터가 v0.2.0 환류의 근거가 된다.

**환류 가능 항목 (v0.2.0에서 변경 예상 범위):**
- 신호 MUST/SHOULD 재분류 (예: #3 또는 #6의 MUST 승격)
- AP-3의 신호 #7 통합 해제 여부 (sub-requirement 7A/7B가 exemplar에서 다른 실패 패턴으로 나타나면 재분리)
- 판정 기준축 재검토 (단일 축 "자동·구조적 판정 가능성"이 불충분할 경우 두 번째 축 도입)
- 신호·anti-pattern 신규 발굴 또는 폐기

Draft를 stable로 굳히지 말 것. v0.2.0 환류 전에는 외부 인용 비권장.

---

## 1. 용어 정의

### 1.1 두 축 분리

| 축 | 성격 | 주체 | 기록 위치 |
|---|---|---|---|
| `tdd_mode` | "이 태스크를 TDD로 갈 것인가" — 방법론 선택 | **사람** (Gate 등급) | 인퀴지션 `00-summary.md` |
| `tdd_ready` | "설계서가 TDD를 받쳐줄 수 있는가" — 품질 체크 | **AI** (wtth 설계 리뷰) | RDR |

### 1.2 연동 규칙

- `tdd_mode = yes` → `tdd_ready`는 **게이트**. MUST 신호 1건이라도 미충족이면 설계서 수정 요구. 수정 전 shackled 진입 금지.
- `tdd_mode = no` → `tdd_ready`는 **informational**. 미충족 시 경고 기록, 진행 허용.
- `tdd_mode` 미결정 상태에서 wtth 설계 리뷰 진입 금지 (인퀴지션 선결 조건).

### 1.3 조작적 정의 (operational)

TDD-ready = "shackled `tdd` 모드 투입 시 P0/P1 미발생이 기대되는 설계서 상태". 스펙이 기술하는 신호·anti-pattern은 이 기대를 induce하기 위한 구조적 요건이다.

---

## 2. 판정 기준축

신호·anti-pattern의 분류는 **"자동·구조적 판정 가능성"** 단일 축으로 분기한다.

| 판정 성격 | 배치 | 책임 |
|---|---|---|
| 구조·키워드·섹션 존재 여부로 판정 가능 | **MUST 신호** (양의 요건) 또는 **금기** (음의 요건) | 게이트 — 자동 검증 가능 |
| 의미론적 판단 필요, false positive 리스크 존재 | **SHOULD 신호** 또는 **체크리스트** | reviewer 재량 — 도메인 판단 동반 |

**환류 주의**: 이 축은 가설이다. exemplar 실측에서 "자동 판정 가능하다고 분류했으나 실제 오탐 많음" 또는 "reviewer 재량 분류했으나 간단한 정규식으로 판정 가능" 사례가 발견되면 v0.2.0에서 축 재조정.

---

## 3. MUST 신호 (4건 + 조건부 1건)

### 신호 #1: RED 시나리오 번호 명시 (MUST)

- **정의**: "RED 1 ~ N" 블록이 존재하고, 각 블록이 입력·실행·검증 사전 조건을 열거한다.
- **판정 방법**: "RED \d+" 헤딩 패턴 존재 여부 + 각 블록 내 입력/실행/검증 구분 존재 여부.
- **원본 근거**: Phase 2A/2C/2E 전부. (RED 4/6/8건)
- **위반 시 실패 모드**: shackled tdd 진입 시 "무엇을 RED로 작성할지" 미정 → 루프 시작 불가.

### 신호 #2: I/O 계약을 data class 수준으로 정의 (MUST)

- **정의**: 입력·출력 타입이 필드 단위까지 명시된 data class 또는 동급 구조로 제시된다.
- **판정 방법**: §I/O 섹션 존재 + 각 필드 타입·제약 기술 여부.
- **원본 근거**: `OriginalMessageRecord` 5 필드, `StatsDimensions` 9차원 (Phase 2C/2E).
- **위반 시 실패 모드**: 테스트 입력 형태 모호 → RED 작성 시 재량 과다 → 테스트가 설계 의도에서 이탈.

### 신호 #5: TDD 플래그를 지시서 헤더에 명시 (MUST)

- **정의**: 지시서 상단에 "TDD: Red → Green → Refactor" 또는 "TDD: 없음" 등 machine-readable 플래그 존재.
- **판정 방법**: 헤더 영역(상위 20줄) TDD 플래그 정규식 매치.
- **원본 근거**: Phase 2 overview 공통.
- **위반 시 실패 모드**: `tdd_mode` 전파 실패 → shackled가 normal/tdd 분기 판정 불가 (인퀴지션 summary 이중 기록은 별개 안전장치).

### 신호 #8: 상태/부작용 경계 명시 (MUST)

- **정의**: "stateless", "특정 DataSource 전용", "TenantContext.use 중첩 금지" 류 상태·부작용 제약이 지시서에 명시된다.
- **판정 방법**: §제약 또는 §부작용 섹션 존재 + 키워드 매치 (stateless / 전용 / 금지 / isolation 등).
- **원본 근거**: Phase 2A/2C/2E 전부.
- **위반 시 실패 모드**: RED가 context-laden이 되어 격리 불가 → flaky 또는 false positive 발생.

### 신호 #7: TDD 구현 규율 (MUST — 통합 신호, sub-requirement 2개)

AP-3(선결 환경 작업 vs TDD 범위 혼재 금지)를 통합한 신호. 내부 분할:

- **7A (공통 제약: TDD 역순 구현 금지)**
  - 정의: overview 또는 지시서 공통 제약에 "RED 먼저, 역순 금지" 명시.
  - 판정: 정규식 매치 ("역순", "Red 먼저", "reverse" 등).
  - 원본 근거: Phase 2 overview §5 G6.

- **7B (선결 환경 작업 vs TDD 범위 분리 명시)**
  - 정의: TDD 루프 밖 선결 작업(L0/배선/사전조건)이 별도 섹션으로 분리되거나, TDD 플래그가 N/A인 범위가 명시된다.
  - 판정: §L0 또는 §사전조건 또는 §선결 섹션 존재 + TDD 플래그 N/A 표기.
  - 원본 근거: Phase 2E L0 (ExceptionTranslator 배선) 분리 실패 사례 기반.

- **환류 주의**: exemplar 실측에서 7A와 7B가 **다른 실패 패턴**으로 잡히면 v0.2.0에서 독립 신호 #9로 재분리. 단일 신호로 두면 원인 tracing 모호 → draft 단계에서 sub-requirement로 분할 유지 필수.

---

## 4. SHOULD 신호 (3건)

### 신호 #3: 에러 경로가 타입으로 응집 (SHOULD)

- **정의**: 에러 종류가 전용 패키지·enum·sealed class로 응집되고, 각 에러와 비즈니스 경로의 매핑이 명시된다.
- **판정 방법**: `exceptions/` 또는 `errors/` 패키지 언급 + 에러 enum/sealed class 참조.
- **원본 근거**: `pipeline/exceptions/` 패키지, `DltErrorReason` 매핑 (Phase 2E).
- **미준수 시 영향**: 에러 경로 RED를 case-by-case로 작성 가능하나 일관성 떨어짐. 리팩토링 시 테스트 깨짐 위험.
- **환류 후보**: exemplar에서 "에러 응집 없어도 RED 작성 가능" 확인되면 SHOULD 유지. "응집 없으면 RED 품질 급락" 확인되면 MUST 승격.

### 신호 #4: 의존 DAG 명시 (SHOULD — 다중 태스크 overview면 MUST 승격)

- **정의**: 복수 태스크로 구성된 Phase에서 태스크 간 의존 관계가 명시된다 ("2D가 2B·2C 의존" 류).
- **판정 방법**: overview §의존 또는 §DAG 섹션 존재.
- **원본 근거**: Phase 2 overview §2.
- **미준수 시 영향**: 병렬 착수 가능 여부 판정 불가. 단일 태스크는 N/A.
- **조건부 승격**: 다중 태스크 Phase overview에서는 MUST 성격. 단일 태스크 지시서에서는 불요.

### 신호 #6: 테스트 파일 경로 사전 지정 (SHOULD)

- **정의**: 지시서 §테스트 섹션에 테스트 파일 경로가 사전 지정된다.
- **판정 방법**: §테스트 또는 §6 섹션에 경로 패턴 매치.
- **원본 근거**: Phase 2 지시서 §6.
- **미준수 시 영향**: shackled가 런타임 결정 가능. 단, 구현 의존성 조기 포착 기회 상실.
- **환류 후보**: exemplar에서 경로 사전 지정이 shackled의 "어디에 테스트 쓸지" 의사결정 비용을 실제로 줄이는지 측정. 효과 크면 MUST 승격.

---

## 5. Anti-pattern 체크리스트 (2건)

### AP-1: 비결정적 RED 금지

- **정의**: 타이밍·환경·외부 상태 의존 RED는 금지. 재현 실패 가능한 테스트는 TDD 루프에 부적합.
- **원본 근거**: Phase 2E RED 7 "실제 MySQL 데드락 유발" — 타이밍 의존으로 재현 실패 가능.
- **권고**: 번역·매핑 경로 검증이면 mock으로 축약. 실측이 필요하면 별도 §Verification 섹션에 TDD 루프와 분리해 기재.
- **heuristic 힌트** (reviewer 보조): "실제 X 유발", "sleep", "wait", "race", "timing" 류 키워드.
- **판정 성격**: 의미론 판단 필요 — reviewer 재량. 심각 시 RDR에서 P0 태깅.

### AP-2: 구현 상세 검증 RED 금지

- **정의**: 내부 구조(class 분리, annotation, self-injection 등)에 종속된 RED는 금지. behavior 기반으로 작성.
- **원본 근거**: Phase 2E RED 8 "새 트랜잭션 증명" — self-injection + 메서드 분리 패턴에 종속.
- **권고**: 관찰 가능한 behavior로 치환 ("첫 시도 rollback 후 두 번째 시도 성공" 류).
- **heuristic 힌트**: "증명", "확인한다" + 내부 구조 용어 (annotation / self-injection / private method / internal).
- **판정 성격**: 의미론·도메인 판단 필요 — reviewer 재량.

---

## 6. 게이트 판정 절차 (wtth 설계 리뷰 integration)

`tdd_mode = yes`일 때 wtth 설계 모드에서 수행:

1. **MUST 신호 전수 검사** — 신호 #1, #2, #5, #7(7A + 7B), #8. 1건이라도 미충족 시 P0 finding 발생.
2. **조건부 MUST (#4)** — 다중 태스크 overview일 때만 적용.
3. **SHOULD 신호 샘플링** — #3, #4(단일 태스크), #6. 미충족 시 P1~P2 finding.
4. **Anti-pattern 체크리스트** — AP-1, AP-2. reviewer가 RED 시나리오 전수 훑고 판정. 심각 시 P0~P1.

`tdd_mode = no`일 때:

- 위 절차 수행하되 모든 finding을 P2 이하로 강등 (informational). 진행 차단 없음.

---

## 7. 반영 대상 매핑 (후속 작업)

| Issue-06 실행 계획 | 이 스펙의 반영 지점 |
|---|---|
| #2 인퀴지션 `tdd_mode` 질문 | §1.1, §1.2 (Gate 등급) |
| #3 wtth testability invariant | §3~§6 (MUST·SHOULD·anti-pattern·게이트 절차) |
| #4 shackled `tdd_mode` 소비 | §1.2 (연동 규칙), §신호 #5 (헤더 플래그 전파) |
| #5 exemplar 링크 등록 | §0 (draft 경고), §각 신호 원본 근거 |

---

## 8. 환류 프로토콜 (v0.2.0 착수 시)

회사 세션에서 exemplar shackled 실측 데이터 확보 후:

1. **tracing 대상**:
   - MUST 신호별 "exemplar에서 실제 이 신호가 없었다면 shackled가 실패했을 곳" 확인.
   - SHOULD 신호별 "신호 유무가 shackled 결과에 영향 준 정도" 측정.
   - AP-1/AP-2별 "exemplar RED에서 실제로 이 anti-pattern 위반이 있었는지, 있었다면 shackled 결과가 어떻게 됐는지" 확인.
   - 신호 #7 7A/7B별 tracing (재분리 판단 근거).

2. **의사결정 항목**:
   - 재분류 (SHOULD→MUST 또는 역방향)
   - AP-3(#7) 재분리 여부
   - 판정 기준축 보강 필요성
   - 신호·anti-pattern 신규 항목

3. **v0.2.0 발행 기준**: 최소 3개 exemplar 분석 완료 + 재분류 결정 확정 + 환류 근거 문서화.

---

## References

- Issue-06: [80-Issue/06-Issue-06/00-index-issue-06.md](./00-index-issue-06.md)
- 02-common-spec.md §1 (심각도 P0~P3) / §13 (파일럿 정량 지표)
- 04-wtth 설계 모드: [01-Planning/04-wtth/02-design/02-review-design.md](../../01-Planning/04-wtth/02-design/02-review-design.md)
- 06-shackled 설계서 (normal/tdd 분기): [01-Planning/06-shackled/02-design/](../../01-Planning/06-shackled/02-design/)
- exemplar (외부 레포): `~/Work/megabird/megabird-work-plan/QLSN-476/QLSN-478/50-pipeline/T1-stats-consumer/shackled-phase2*.md`
- PRD G3 (사람 결정권) / G5 (암시 제약 명시화)
- Issue-02 #3 (사람 개입 3등급)
