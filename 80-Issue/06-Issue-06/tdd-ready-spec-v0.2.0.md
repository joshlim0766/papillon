# TDD-ready 설계서 규격 v0.2.0

## Context
- **Parent:** [Issue-06](./00-index-issue-06.md)
- **Related:**
  - [02-common-spec.md](../../01-Planning/02-common-spec.md) — v1.0 안정화 시 §14로 흡수 또는 분할 후 편입
  - [04-wtth/02-design/02-review-design.md](../../01-Planning/04-wtth/02-design/02-review-design.md) — testability invariant 반영 대상 (Issue-06 #3)
  - [06-shackled/02-design/](../../01-Planning/06-shackled/02-design/) — `tdd_mode` 소비 + 세션 분할 (Issue-06 #4)
  - [05-inquisition/02-design/](../../01-Planning/05-inquisition/02-design/) — `tdd_mode` 질문 추가 (Issue-06 #2)
  - [session-split-design-v0.1.0-draft.md](./session-split-design-v0.1.0-draft.md) — 시간축·공간축 분할 메커니즘
  - [tracing-2e-2026-04-20.md](./tracing-2e-2026-04-20.md) / [tracing-2f-2026-04-20.md](./tracing-2f-2026-04-20.md) — v0.2.0 환류 근거
- **Status:**
  - Work: **Stable (v0.2.0)**
  - Review: None
  - 차기 재검토 조건: 추가 exemplar 3건 이상 shackled 실측 후 (예: 배치 엔진 개발 시), 또는 6개월 경과 시점.

---

## 0. 변경 이력

| 버전 | 시점 | 근거 | 주요 변경 |
|---|---|---|---|
| v0.1.0-draft | 2026-04-17 | 연역적 가설 (샘플 실측 전) | 초판 — 신호 8개, MUST 4+1, SHOULD 3, AP 2+1 |
| **v0.2.0** | **2026-04-20** | **2e + 2f 실측 2건** (L 체급 shackled TDD 완료) | **§상세** |

### v0.2.0 주요 변경

**신호 신설 (NEW MUST)**:
- **#9 실패 경로 계약**: 2f 3라운드 P0/P1 재귀 패턴 분석에서 드러남. "지시서가 성공 경로만 명시하여 실패 경로 계약이 매 라운드 공백" 문제 해결.

**기존 신호 확장**:
- **#2 I/O 계약**: "예외 타입 카탈로그" 포함 요건 추가 (2e `TenantContextMismatchException` 미열거 근거).
- **#7B 공통 제약**: "예외는 단서조항으로 명시" 메커니즘 추가 (2e G12 JooqConfig 단서조항 근거).
- **#8 상태/부작용 경계**: "권위 소스 교차 참조" 요건 추가 (2e §2.4 UNIQUE KEY 오탈자 근거).

**신규 섹션**:
- **§6 실패 경로 계약 표 템플릿** — 신호 #9 부속.
- **§8 지시서 분할 요건** — 공간축 (`session-split-design` 참조).
- **§9 체계 개선** — 품질 경계 4 지표 + 실용 노선 휴리스틱.

**Anti-pattern 확장**:
- **AP-1 학습 케이스**: 2e RED 7 3단계 전환사 박제.
- **AP-2 학습 케이스**: 2e Transaction Integration Test 교정 사례 박제.

**v0.1.0-draft 가설 중 유지된 것**: 신호 #1/#5/#7 MUST, #3/#4/#6 SHOULD 분류, AP-1/AP-2 리스트.

**v0.1.0-draft 가설 중 보류**: #3 에러 타입 응집 MUST 승격 — 2e 1건에서 승격 근거 있었으나 2f 에서 신호 #9 의 실증으로 우선순위 밀림. v0.3.0 재검토.

---

## 1. 용어 정의

### 1.1. 두 축 분리

| 축 | 성격 | 주체 | 기록 위치 |
|---|---|---|---|
| `tdd_mode` | "이 태스크를 TDD로 갈 것인가" — 방법론 선택 | **사람** (Gate 등급) | 인퀴지션 `00-summary.md` |
| `tdd_ready` | "설계서가 TDD를 받쳐줄 수 있는가" — 품질 체크 | **AI** (wtth 설계 리뷰) | RDR |

### 1.2. 연동 규칙

- `tdd_mode = yes` → `tdd_ready`는 **게이트**. MUST 신호 1건이라도 미충족이면 설계서 수정 요구. 수정 전 shackled 진입 금지.
- `tdd_mode = no` → `tdd_ready`는 **informational**. 미충족 시 경고 기록, 진행 허용.
- `tdd_mode` 미결정 상태에서 wtth 설계 리뷰 진입 금지 (인퀴지션 선결 조건).

### 1.3. 조작적 정의

TDD-ready = "shackled `tdd` 모드 투입 시 P0/P1 누적 발생이 수렴 가능하며, 누적 P0/P1 원인이 구조적 공백이 아닌 구현 품질·테스트 격리 수준으로 진화한다고 기대되는 설계서 상태". 본 스펙의 신호·anti-pattern·실패 경로 계약 요건은 이 기대를 induce 하기 위한 구조적 요건이다.

**v0.2.0 정의 변경 주의**: v0.1.0-draft 의 "P0/P1 미발생 기대" 는 2f 실측에서 과도한 기대로 판명. 4라운드 수렴 패턴이 현실이며 이를 전제로 재정의.

---

## 2. 판정 기준축

신호·anti-pattern의 분류는 **"자동·구조적 판정 가능성"** 단일 축으로 분기한다.

| 판정 성격 | 배치 | 책임 |
|---|---|---|
| 구조·키워드·섹션 존재 여부로 판정 가능 | **MUST 신호** (양의 요건) 또는 **금기** (음의 요건) | 게이트 — 자동 검증 가능 |
| 의미론적 판단 필요, false positive 리스크 존재 | **SHOULD 신호** 또는 **체크리스트** | reviewer 재량 — 도메인 판단 동반 |

**v0.2.0 환류 반영**: 2e + 2f 실측 결과 이 축이 유효함 확인. 단 MUST 중 일부(#9 실패 경로 계약)는 "표 존재 여부" 는 자동 판정 가능하나 "표 내용의 적절성" 은 reviewer 재량 — **2-계층 판정** 필요.

---

## 3. MUST 신호 (6건 + 조건부 1건)

### 신호 #1: RED 시나리오 번호 명시 (MUST)

- **정의**: "RED 1 ~ N" 블록이 존재하고, 각 블록이 입력·실행·검증 사전 조건을 열거한다.
- **판정 방법**: "RED \d+" 헤딩 패턴 존재 + 각 블록 내 입력/실행/검증 구분 존재 여부.
- **원본 근거**: 2a(RED 4) / 2c(RED 6) / 2d(RED 8) / 2e(RED 9) / 2f(RED 12).
- **위반 시 실패 모드**: shackled tdd 진입 시 "무엇을 RED로 작성할지" 미정 → 루프 시작 불가.
- **실측 확인 (v0.2.0)**: 2e/2f 모두 이 신호가 RED 번호대로 순차 구현을 가능케 함. 단 RED 수 > 6 시 공간축 분할(§8) 동반 필요.

### 신호 #2: I/O 계약 + 예외 타입 카탈로그 (MUST, v0.2.0 확장)

- **정의**: 
  - **(a)** 주 메서드 입력·출력 타입이 필드 단위까지 명시된 data class 또는 동급 구조로 제시된다.
  - **(b, v0.2.0 추가)** 해당 컴포넌트가 **던질 수 있는 예외 타입** 이 사전 열거되며, 각 예외의 발생 조건·응집 패키지가 명시된다.
- **판정 방법**: §I/O 섹션 존재 + 필드 타입·제약 기술 + §예외 카탈로그 섹션 또는 시그니처 근처 `throws` 열거.
- **원본 근거**: 
  - v0.1.0: `OriginalMessageRecord` 4 필드, `StatsDimensions` 9차원 (2c/2d).
  - **v0.2.0 추가 근거**: 2e `TenantContextMismatchException` 미열거 → 구현 중 wtth ARCH P1-4 로 신규 타입 필요성 포착. 카탈로그가 있었다면 사전 식별 가능.
- **위반 시 실패 모드**: 
  - (a) 테스트 입력 형태 모호 → RED 작성 시 재량 과다.
  - (b) 방어 예외 타입 누락 → 구현 중 신규 타입 추가 필요성 뒤늦게 발견 → 2F `DefaultErrorHandler` 등 상위 오케스트레이션의 retryable/non-retryable 분류 공백.

### 신호 #5: TDD 플래그를 지시서 헤더에 명시 (MUST)

- **정의**: 지시서 상단에 "TDD: Red → Green → Refactor" 또는 "TDD: 없음" 등 machine-readable 플래그 존재.
- **판정 방법**: 헤더 영역(상위 20줄) TDD 플래그 정규식 매치.
- **원본 근거**: Phase 2 overview 공통 + 2a~2f 지시서 헤더 전부.
- **위반 시 실패 모드**: `tdd_mode` 전파 실패 → shackled 가 normal/tdd 분기 판정 불가.

### 신호 #7: TDD 구현 규율 (MUST — 통합 신호, sub-requirement 2개)

#### 7A: TDD 역순 구현 금지

- **정의**: overview 또는 지시서 공통 제약에 "RED 먼저, 역순 금지" 명시.
- **판정**: 정규식 매치 ("역순", "Red 먼저", "reverse" 등).
- **원본 근거**: Phase 2 overview §5 G6.
- **실측 확인 (v0.2.0)**: 2e/2f 모두 7A 준수. 단독 신호로 명확 기능.

#### 7B: 공통 제약 + 단서조항 메커니즘 (v0.2.0 확장)

- **정의 (v0.2.0)**: 
  - **(a)** 선결 환경 작업(L0/배선/사전조건)이 TDD 루프 밖으로 명시 분리되거나, TDD 플래그 N/A 범위가 표기된다.
  - **(b, v0.2.0 추가)** 공통 제약(G1~GN)의 **예외가 발생할 수 있음을 전제** 로, 예외 사례는 지시서 본문에 "단서조항" 블록으로 박제한다.
- **판정**: §L0 또는 §사전조건 + TDD 플래그 N/A 표기 + (b) 단서조항 섹션 존재 또는 공통 제약 각 항목의 예외 슬롯 명시.
- **원본 근거**: 
  - (a) 2c §3.0 선행 작업 분리 / 2e §2.1 선행 자산 재사용.
  - **(b) v0.2.0 추가 근거**: 2e §4.4 단서조항 — 공통 제약 G12 "JooqConfig 수정 금지" 의 Spring+jOOQ 트랜잭션 연동 예외.
- **환류 재분리 판단 (v0.1.0 예고)**: 2e/2f 실측에서 7A/7B 가 다른 실패 패턴으로 잡히지 않음. 통합 유지.

### 신호 #8: 상태/부작용 경계 + 권위 소스 교차 참조 (MUST, v0.2.0 확장)

- **정의 (v0.2.0)**: 
  - **(a)** "stateless", "특정 DataSource 전용", "TenantContext 중첩 금지" 류 상태·부작용 제약이 지시서에 명시된다.
  - **(b, v0.2.0 추가)** DDL / 스키마 / 상수 / UNIQUE KEY 등의 **권위 소스** (예: `02-Design/02-table-schema.md`) 가 별도 존재할 때, 지시서는 해당 권위 소스 경로를 **교차 참조** 로 명시한다.
- **판정**: §제약 또는 §부작용 섹션 + (b) DDL/스키마 인용 시 권위 소스 경로 참조 존재.
- **원본 근거**: 
  - (a) 2a/2c/2d/2e/2f 전부.
  - **(b) v0.2.0 추가 근거**: 2e §2.4 `stats_send_detail` UNIQUE KEY 5 컬럼 정의에 권위 소스(`02-Design §7.2`)와 **불일치** 오탈자 존재. shackled 구현 중 발견·정정. 권위 소스 참조가 박제됐다면 자동 검증 가능했음.
- **위반 시 실패 모드**: 
  - (a) RED 가 context-laden 이 되어 격리 불가.
  - (b) **지시서 오탈자 미발견** → 잘못된 UNIQUE KEY 기반 RED → 잘못된 GREEN 통과 가능.

### 신호 #9: 실패 경로 계약 (NEW MUST, v0.2.0 신설)

- **정의**: 각 주요 컴포넌트에 대해 **"when X fails → then Y"** 표가 지시서에 포함된다. 표는 ① 실패 시나리오 ② 기대 동작 ③ 지표/알람 3 축을 담는다.
- **판정 방법**: 
  - **2-계층 판정** (§2 주의).
  - (1계층, 자동) §실패 계약 / §Failure Contract / §실패 경로 섹션 존재 여부 + 표 구조 검증.
  - (2계층, reviewer) 표 내용의 적절성 — 상위 오케스트레이션이 소비하는 실패 분류 체계 (DLT reason / retryable / 재시도 정책) 와 일치하는지.
- **원본 근거 (v0.2.0 신설 전환)**: 
  - 2f 3라운드 P0/P1 재귀 패턴 (`tracing-2f-2026-04-20.md` 관찰 3). 1R→2R→3R 각 라운드 수정이 새 실패 경로를 여는데 지시서는 성공 경로만 명시.
  - 4R AB-2 구체 실증: `DltErrorReason.from` 에 `IllegalArgumentException → LOGIC_ERROR` 매핑 1줄. 사전에 실패 계약 표로 박제됐으면 1R 에 사전 결정 가능.
- **위반 시 실패 모드**: 코드 리뷰 라운드가 증가할수록 새 실패 경로 계약 공백 누적. 최종적으로 프로덕션 알람 오진·리소스 누수·재시도 루프 발생 위험.
- **§6 에 표 템플릿 별도 박제**.

### 신호 #4: 의존 DAG 명시 (조건부 MUST, 다중 태스크 overview)

- **정의**: 복수 태스크로 구성된 Phase 에서 태스크 간 의존 관계가 명시된다 ("2D 가 2B·2C 의존" 류).
- **판정**: overview §의존 또는 §DAG 섹션 존재.
- **원본 근거**: Phase 2 overview §2 (ASCII 다이어그램).
- **조건**: 다중 태스크 Phase overview 에서는 MUST. 단일 태스크 지시서에서는 SHOULD (§4 참조).

---

## 4. SHOULD 신호 (3건)

### 신호 #3: 에러 경로가 타입으로 응집 (SHOULD)

- **정의**: 에러 종류가 전용 패키지·enum·sealed class 로 응집되고, 각 에러와 비즈니스 경로의 매핑이 명시된다.
- **판정**: `exceptions/` 또는 `errors/` 패키지 언급 + 에러 enum/sealed class 참조.
- **원본 근거**: `pipeline/exceptions/` 패키지, `DltErrorReason` 매핑 (2e/2f).
- **v0.2.0 환류 주의**: 2e 에서 MUST 승격 후보로 기록됐으나 2f 에서 신호 #9 의 실증 우선순위에 밀려 보류. v0.3.0 재검토. 신호 #9 의 실패 경로 계약 표가 에러 타입 응집을 자연스레 유도하므로 #3 은 #9 의 하위 신호로 재분류 가능성.

### 신호 #4 (단일 태스크 버전): 의존 DAG 명시 (SHOULD)

- §3 신호 #4 의 조건부 MUST 와 동일. 단일 태스크에서는 SHOULD.

### 신호 #6: 테스트 파일 경로 사전 지정 (SHOULD)

- **정의**: 지시서 §테스트 섹션에 테스트 파일 경로가 사전 지정된다.
- **판정**: §테스트 또는 §6 섹션에 경로 패턴 매치.
- **원본 근거**: 2a~2f 지시서 §6.
- **v0.2.0 실측**: shackled 가 지시서 대로 파일 생성. 구현 중 추가 테스트 파일 (예: 2e `UpsertServiceTransactionIntegrationTest`) 발생 가능 — SHOULD 유지 + "테스트 파일 경로는 예측 가능 범위만 지정, 추가 발생은 자연스러움" 부연.

---

## 5. Anti-pattern (2건 + v0.2.0 학습 케이스)

### AP-1: 비결정적 RED 금지

- **정의**: 타이밍·환경·외부 상태 의존 RED 는 금지. 재현 실패 가능한 테스트는 TDD 루프에 부적합.
- **권고**: 번역·매핑 경로 검증이면 mock 으로 축약. 실측이 필요하면 별도 §Verification 섹션에 TDD 루프와 분리해 기재.
- **heuristic 힌트**: "실제 X 유발", "sleep", "wait", "race", "timing" 류 키워드.
- **판정 성격**: 의미론 판단 — reviewer 재량. 심각 시 RDR P0.

#### v0.2.0 학습 케이스 — 2e RED 7 3단계 전환사

exemplar 로 보존:

1. **단건 시대 (v0 초안)**: "RED 7 — 실제 MySQL 데드락 유발" — AP-1 위반 (타이밍 의존).
2. **배치 재작성 (RDR 2026-04-17)**: 배치 groupBy 사전 집계로 deadlock 자체 상류 해소 → RED 7 의미가 "deadlock 유발" 에서 "race 해소 회귀 증명" 으로 전환.
3. **wtth 코드 리뷰 (2e P0-3 수용)**: 범위 축소 — "ROW LOCK 직렬화 sanity" 로 재정직화.

**학습 포인트**: AP-1 위반은 한 번에 해결되지 않음. (a) 상류 설계 변경으로 문제 자체 소멸 → (b) 축소·정직화 → (c) 운영 관측 이관(F-15) 의 3 단계 전환이 정석.

### AP-2: 구현 상세 검증 RED 금지

- **정의**: 내부 구조(class 분리, annotation, self-injection 등) 에 종속된 RED 는 금지. behavior 기반으로 작성.
- **권고**: 관찰 가능한 behavior 로 치환 ("첫 시도 rollback 후 두 번째 시도 성공" 류).
- **heuristic 힌트**: "증명", "확인한다" + 내부 구조 용어 (annotation / self-injection / private method / internal).
- **판정 성격**: 의미론·도메인 판단 — reviewer 재량.

#### v0.2.0 학습 케이스 — 2e Transaction Test identityHashCode 교정

exemplar 로 보존:

1. **초기 설계 (AP-2 경향)**: Transaction Integration Test 에서 `System.identityHashCode(ctx.connection())` 로 Connection wrapper 동일성 검증 시도.
2. **실행 결과**: `TransactionAwareDataSourceProxy` 가 호출마다 새 JDK proxy wrapper 반환 → **FAIL**.
3. **교정 (wtth ARCH P0-2 수용)**: 물리 `HikariDataSource.getConnection()` 카운트로 behavior 기반 전환 → GREEN.

**학습 포인트**: AP-2 위반은 구현 실패로 자동 감지될 수 있는 드문 케이스. "객체 동일성 → 관찰 가능한 효과" 치환이 정석.

---

## 6. 실패 경로 계약 표 템플릿 (신호 #9 부속)

신호 #9 준수를 위해 지시서 §실패 계약 섹션에 아래 템플릿을 채운다.

### 6.1. 표 스키마

```
| 컴포넌트                | 실패 시나리오                    | 기대 동작                             | 지표/알람                 |
|---|---|---|---|
| {메서드·클래스·서비스}  | {실패 트리거 조건}               | {예외 타입 / 로그 / 재시도·커밋 여부} | {메트릭·태그·알람 키}      |
```

### 6.2. 작성 범위 가이드 (v0.2.0 체계 개선 §9.1 과 연계)

- **MUST 포함**: 프로덕션 알람 품질 / 리소스 누수 / 재시도 루프 등 **관측 가능한 운영 피해** 를 초래하는 실패.
- **SHOULD 포함**: 도메인 비즈니스 로직의 분기 실패 (예: `ORIGINAL_NOT_FOUND`, `BMS_OPTIONAL_FIELD_NULL`).
- **운영 피드백 후 추가**: 특정 인프라 조합 / 희귀 타이밍 / 부하 패턴 별 edge case (§9.1 실용 노선 휴리스틱).

### 6.3. 2e / 2f 근거 예시

```
| DltErrorReason.from        | 예외 타입이 cause 체인에 unmapped  | LOGIC_ERROR 반환                      | dlt.published{reason=LOGIC_ERROR} |
| DltPublisher.send          | Kafka broker under-min-ISR        | .get(5s) TimeoutException 전파        | n/a (Recoverer 가 catch)           |
| Recoverer                  | dltPublisher 내부 TimeoutException | swallow + counter + ERROR log + 커밋 | dlt.send.failed                   |
| StatsBatchPipelineImpl     | dimensions 공백                    | markAll(newEvents) 호출 후 return     | n/a                               |
```

이 4 항목이 2f 1R 이전에 박제됐다면 4라운드 누적 P0/P1 전체를 사전 결정 가능했음 (tracing-2f 관찰 3).

---

## 7. 게이트 판정 절차 (wtth 설계 리뷰 integration)

`tdd_mode = yes`일 때 wtth 설계 모드에서 수행:

1. **MUST 신호 전수 검사** — #1, #2(a+b), #5, #7(7A+7B), #8(a+b), **#9(1계층)**. 1건이라도 미충족 시 P0 finding.
2. **신호 #9 2계층 검증** — 표 내용 적절성을 reviewer 재량 판단. 상위 오케스트레이션 소비 체계와 불일치 시 P0~P1.
3. **조건부 MUST (#4 다중 태스크)** — 해당 시만 적용.
4. **SHOULD 신호 샘플링** — #3, #4(단일 태스크), #6. 미충족 시 P1~P2.
5. **Anti-pattern 체크리스트** — AP-1, AP-2 + 학습 케이스 참조. reviewer 재량 판정. 심각 시 P0~P1.
6. **지시서 분할 요건 (§8)** — 줄 수 / RED 수 기반 휴리스틱 체크. 초과 시 P1 권고.

`tdd_mode = no`일 때:

- 위 절차 수행하되 모든 finding 을 P2 이하로 강등 (informational). 진행 차단 없음.

---

## 8. 지시서 분할 요건 (공간축, v0.2.0 신설)

TDD-ready 설계서 규격의 공간 축 보완. 상세 설계는 [session-split-design-v0.1.0-draft.md](./session-split-design-v0.1.0-draft.md).

### 8.1. L1 분할 (지시서 → 태스크)

- **휴리스틱**: 지시서 > 500줄 또는 "관측·환경·프로파일" 섹션 > 15% 분량 시 분할 권고.
- **분할 축**: 관심사 분해 (인프라 선제 / 메인 조립 / 운영 보강) + TDD 적합성 (tdd / normal).
- **상태 파일**: `.shackled-state.json` `tasks[*]` 에 `concern` / `size_estimate_lines` / `l2_required` / `workaround_notes` 필드 신설.

### 8.2. L2 분할 (태스크 → RED 그룹)

- **휴리스틱**: 태스크 내 RED > 6 시 L2 분할 권고.
- **분할 단위**: 하이브리드 C→A (RED 1 → GREEN+REFACTOR 1 반복, 의존 독립 RED 2~3개 그룹화).
- **세션 분할**: 각 그룹의 RED 작성 완료 후 세션 종료, GREEN+REFACTOR 는 새 세션.

### 8.3. 실측 근거

- 2e 지시서 636줄 / 2f 765줄 — L1 분할 임계 근처.
- 2f TASK-2F-02 (RED 1~12 몰림) 에서 Full GC 발생 — L2 필요성 실증.

---

## 9. 체계 개선 (v0.2.0 신설)

### 9.1. 실용 노선 휴리스틱 — 실패 경로 계약 확장 원칙

실패 경로 계약 표(§6) 를 **초기 지시서에 모두 박제하는 것은 오버엔지니어링**. 운영 피드백 기반 점진 확장 원칙:

| 단계 | 근거 | 행동 |
|---|---|---|
| 초기 (MUST 수준) | 프로덕션 피해 예측 명확 | 지시서 §실패 계약 표 박제 |
| 운영 피드백 후 (SHOULD 승격) | 실제 인시던트 발생 | 추가 행 박제 + RDR 링크 |
| 영구 위임 | 발생 빈도 < 임계 | 체크리스트에만 기록, 지시서 미반영 |

**판정 기준**: "1줄 수정 + 운영 피해 > 수정 비용" 시 즉시 반영. 아니면 운영 피드백 대기.

**근거**: 2f 4R AB-1/4/5 운영 위임 사례.

### 9.2. 품질 경계 4 지표 (wtth 수렴 판정 실측 휴리스틱)

wtth 설계 리뷰 또는 코드 리뷰의 "사인오프" 전환 조건으로 사용 가능한 실측 휴리스틱. 4 지표 동시 충족 시 수렴 판정:

1. **P0 0건 연속 유지** — 직전 1 라운드 이상 P0 없음.
2. **P1 성격 수렴** — 테스트 커버리지 / 리소스 레벨로 이동. 계약 자체의 공백 아닌 보완 레벨.
3. **건수 감소 곡선** — 라운드별 finding 수가 단조 감소.
4. **대안 선택지 가용** — "지금 고치기 vs 운영 후 고치기" ROI 비교 가능 단계.

**근거**: 2f 4라운드 수렴 실측 (1R 11건 → 2R 다수 → 3R 단일 → 4R 선별 2건).

**연계 대상**: `02-common-spec.md` §1 심각도 기준, `04-wtth/02-design/00-core.md` §4.1 수렴 메커니즘.

---

## 10. 반영 대상 매핑

| Issue-06 실행 계획 | 이 스펙의 반영 지점 |
|---|---|
| #2 인퀴지션 `tdd_mode` 질문 | §1.1, §1.2 |
| #3 wtth testability invariant | §3~§7 (MUST·SHOULD·anti-pattern·게이트 절차) + §9.2 |
| #4 shackled `tdd_mode` 소비 + 세션 분할 | §1.2, §8 (§session-split-design) |
| #5 exemplar 링크 등록 | §0, §각 신호 원본 근거, §6.3 |

---

## 11. 환류 프로토콜 (v0.2.0 → v0.3.0)

### 11.1. 본 버전 환류 완료 데이터

- **tracing-2e-2026-04-20.md**: 2e 실측 (L 체급, RED 9, 완전 사이클 완료).
- **tracing-2f-2026-04-20.md**: 2f 실측 (L 체급, RED 12, 4라운드 수렴 103/103 GREEN).
- **§8 "최소 3건" 기준**: 현재 2건. L 체급 2건이 깊이 있는 실측이라 실질 근거 충분. 차기 배치 엔진 1건 추가 시 명목 기준 도달.

### 11.2. v0.3.0 재검토 트리거

아래 중 하나 이상 발생 시:

1. 배치 엔진 등 추가 exemplar 3건 이상 shackled TDD 실측 완료.
2. 6개월 경과 (최종 갱신 후).
3. 신호 #9 실패 경로 계약 표 운영 반영 결과 → 휴리스틱 §9.1 재조정 필요.
4. Issue-06 #2/#3/#4 의 구체 구현 진행 중 스펙 공백 발견.

### 11.3. 차기 재검토 후보 항목

- **신호 #3 에러 타입 응집** — MUST 승격 여부. 신호 #9 하위 신호로 재분류 가능성.
- **신호 #9 2계층 판정** — 2계층 reviewer 재량을 구조화할 방법 (예: 실패 계약 표 자체 린터).
- **세션 분할 메커니즘** — session-split-design v0.2.0 통합 후 본 스펙 §8 확장.
- **실용 노선 휴리스틱 임계값** — §9.1 의 "1줄 + 운영 피해 > 수정 비용" 판정을 더 구조화.

---

## References

- Issue-06: [80-Issue/06-Issue-06/00-index-issue-06.md](./00-index-issue-06.md)
- v0.1.0-draft (보존): [tdd-ready-spec-v0.1.0-draft.md](./tdd-ready-spec-v0.1.0-draft.md)
- 재평가 메모: [tdd-ready-evaluation-memo-2026-04-20.md](./tdd-ready-evaluation-memo-2026-04-20.md)
- tracing-2e: [tracing-2e-2026-04-20.md](./tracing-2e-2026-04-20.md)
- tracing-2f: [tracing-2f-2026-04-20.md](./tracing-2f-2026-04-20.md)
- session-split-design: [session-split-design-v0.1.0-draft.md](./session-split-design-v0.1.0-draft.md)
- 02-common-spec.md §1 (심각도 P0~P3) / §13 (파일럿 정량 지표)
- 04-wtth 설계 모드: [01-Planning/04-wtth/02-design/02-review-design.md](../../01-Planning/04-wtth/02-design/02-review-design.md)
- 06-shackled 설계: [01-Planning/06-shackled/02-design/](../../01-Planning/06-shackled/02-design/)
- exemplar (익명화 복제): [exemplar/](./exemplar/)
- 원본 exemplar (외부): `~/Work/megabird/megabird-work-plan/QLSN-476/QLSN-478/50-pipeline/T1-stats-consumer/shackled-*.md`
- PRD G3 (사람 결정권) / G5 (암시 제약 명시화)
- Issue-02 #3 (사람 개입 3등급)
