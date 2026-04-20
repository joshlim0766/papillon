# shackled Phase 2 개요: stats-consumer 비즈니스 로직 TDD

- **상위 설계서**: `T1-stats-consumer/01-stats-consumer-design.md` §3~§7, §9 Consumer 계약 (최상단), §6A 실패 계층, §8A 관측가능성
- **Phase 1 지시서**: `shackled-phase1-directive.md` (L, 완료)
- **USE 전환 지시서**: `shackled-use-tenant-directive.md` (S, 완료)
- **shared 선행 지시서**: `shackled-shared-tenant-context-use-block.md` (XS, Phase 2 착수 전 필수)
- **1라운드 리뷰 RDR**: `example-stats-billing/docs/decisions/reviews/RDR-2026-04-17-phase2-directive-review.md` (반영 완료)
- **배치 전환 RDR**: `example-stats-billing/docs/decisions/reviews/RDR-2026-04-17-stats-consumer-batch-processing-redesign.md` (2E/2F 재작성 + 설계서 9섹션 개정 근거)
- **페이로드 pass-through RDR**: `example-stats-billing/docs/decisions/reviews/RDR-2026-04-17-kafka-payload-passthrough-discovery.md` (channelCode 승격, dedup 키 축)

이 문서는 Phase 2 **인덱스/공통 가이드** 이며, 각 관심사별 세부 지시서 6개로 분할된다. shackled 는 개별 지시서 1개 단위로 실행한다.

---

## 0. Consumer 계약 (설계서 §9 인용, 최우선 박제)

> **실시간 통계는 근사치다.** 대사가 불일치를 탐지하고, 사람이 로그 테이블 (`TMG_MSG_TGUS` / `MM_MSG`) 기준으로 stats 를 수정하며, 롤업이 멱등 재실행으로 상위 테이블까지 동기화한다. Consumer 는 **성능 + 포이즌 격리 + 관측가능성** 을 책임진다.

이 계약이 Phase 2 전체의 트레이드오프를 결정한다:
- **성능**: Kafka 배치 listener (D-1) + groupBy 사전 집계 (D-2) + UPSERT 성공 후 Redis 마킹 (D-3)
- **포이즌 격리**: record 단위 DLT vs 배치 단위 DLT 분기 (§6A)
- **관측가능성**: MDC `batchId` + 구조화 로그 + Grafana 5 메트릭 (§8A)

Phase 2E (atomic unit) vs Phase 2F (오케스트레이션) 책임 분리:

```
┌─ Phase 2F (오케스트레이션) ──────────────────────────────────────────────┐
│  @KafkaListener(batch=true) → parse → filterNew → lookup/map → groupBy │
│                                                              ↓         │
│                              TenantContext.use("example-corp") {           │
│    ┌─ Phase 2E (atomic unit) ──────────────────────────────────────┐   │
│    │   batchUpsert(Map<StatsDimensions, Long>) @Transactional       │   │
│    │     · Tier 1: resolveGroupIds  · Tier 2: ON DUPLICATE KEY UPDATE│   │
│    └────────────────────────────────────────────────────────────────┘   │
│                              }  ← upsert 성공 후 markAll → ack         │
└─────────────────────────────────────────────────────────────────────────┘
```

Phase 2A/2B/2C/2D 는 순수 함수/서비스로서 2F 배치 오케스트레이션에서 record 단위 호출된다 (변경 없음, 재사용).

---

## 1. Phase 2 목적

Phase 1 에서 구축한 인프라 골격(`StatsPipelineStub`)을 실제 비즈니스 로직으로 대체한다. Kafka 배치 `List<ConsumerRecord>` 를 `dedup filterNew → (EXT 분기 | 원본 Lookup → 차원 매핑) → groupBy 집계 → batchUpsert → markAll → ack` 파이프라인으로 end-to-end 처리한다.

---

## 2. 지시서 6종 (직렬 실행 순서 + 현재 상태)

| # | 파일 | 체급 | 관심사 | 상태 |
|---|---|---|---|---|
| 2A | `shackled-phase2a-bms-validator.md` | S | `__ext__` optional 6 필드 NOT NULL 검증 | **완료** (`8931ee4` + `4e66541`) |
| 2B | `shackled-phase2b-channel-type-code.md` | S | `SVC_KND_CD` → `channel_type` String 정규화 + `KnownChannel` 관측 helper | **완료** (`8a9e7f5` + `2b54580` + `b4c9941`) |
| 2C | `shackled-phase2c-original-lookup.md` | M | 3테이블 조인 + `SND_LOG` fallback (jOOQ) + OriginalMessageRecord 4필드 | **완료** (stats-billing HEAD 추적) |
| 2D | `shackled-phase2d-dimension-mapper.md` | S | 9차원 매핑 (본사 + EXT) + StatSendResultEvent `channelCode` 승격 동반 | **완료** (`105acc9` + `4ef4db4`) |
| 2E | `shackled-phase2e-upsert-service.md` | L | 배치 `batchUpsert(Map<StatsDimensions, Long>)` atomic unit, Tier 1 race + batch INSERT ... ON DUPLICATE KEY UPDATE | **지시서 재작성 완료** (shackled 착수 대기) |
| 2F | `shackled-phase2f-pipeline-assembly.md` | L | 배치 오케스트레이션 + 실패 계층 + DLT publisher + Kafka 배치 listener + Redis dedup 배치 API | **지시서 개정 완료** (shackled 착수 대기) |

의존 관계:

```
2A (완료) ─┐
2B (완료) ─┤─→ 2D (완료) ─→ 2E (재작성 완료) ─→ 2F (개정 완료)
2C (완료) ─┘
```

**shackled 진입 순서 확정 (직렬, 1인 세션 원칙)**: **2E → 2F**. 2E 완료 + 회귀 확인 후 2F 착수. 각 지시서 완료 시 커밋 + 회귀 확인 후 다음으로 진행.

---

## 3. 공통 선결 조건

### 3.1. 완료 (Phase 1 + 선행 작업)

| 항목 | 근거 커밋 |
|---|---|
| Spring Boot 3 + Kotlin 2.0.21 + jOOQ 3.20.4 배선 | `1a3fd51` |
| `TenantRoutingDataSource` + `LazyConnectionDataSourceProxy` | `1a3fd51` + `87f4c49` |
| 외부 RDS 동적 schema 전환 (`SchemaAwareDataSource`) | `87f4c49` |
| `DslContextFactory.forTenant(tenant)` + `TenantAssertingListener` | `1a3fd51` |
| `RedisDedupService` (`SET NX EX 10800`, 단건 — **2F 에서 배치 API 로 교체 예정**) | `1a3fd51` |
| Kafka Consumer + DLT 라우팅 (`DefaultErrorHandler` + `DeadLetterPublishingRecoverer`, 단건 — **2F 에서 배치 listener 로 교체 예정**) | `1a3fd51` |
| `StatsPipeline` interface + `StatsPipelineStub` (**2F 에서 제거 예정**) | `1a3fd51` |
| TestContainers 베이스 (Kafka + Redis + MySQL multi-DB) | `87f4c49` |
| `schema.sql` (Lookup 3 + stats 2) | `87f4c49` |
| `StatSendResultEvent` + `ResultType` enum + `EXT_TENANT` 상수 | `bd18d82` |
| `StatSendResultEvent.channelCode` 기본 6필드 승격 (DTO 실물 반영) | `4ef4db4` (Phase 2D 동반) |
| jOOQ codegen `1.20260417.3` 업그레이드 (schema qualifier 원천 해소) | stats-billing HEAD |

### 3.2. Phase 2 착수 전 선행 필요 (완료 상태)

| 항목 | 지시서 | 목적 |
|---|---|---|
| `TenantContext.use(tenant) { block }` inline 함수 추가 | `shackled-shared-tenant-context-use-block.md` (XS, 완료) | 2C/2F 의 중첩 컨텍스트 전환 안전 확보. wtth 묶음 1 (P0) 해소 |
| `TNT_INTG_MSG_SND.ORG_SVC_KND_CD` null 여부가 `is_substitute` 판정 근거임을 확인 | 설계서 §4.3 (수정 완료) | 2C/2D 의 `is_substitute` 매핑 규칙 |
| 설계서 §9 Consumer 계약 / §1.1 배치 흐름 / §6A 실패 계층 / §8A 관측가능성 박제 | 설계서 1차 개정 (HEAD `b642a3c`) | 2E/2F 재작성 근거 |

### 3.3. 인프라 전제

| 전제 | 영향 |
|---|---|
| example-corp MySQL cluster parameter group `transaction_isolation = READ-COMMITTED` | 2E `resolveGroupIds` race 알고리즘의 "sleep 후 재조회" 가 상대 COMMIT 관찰 가능. 앱 레벨 격리수준 강제 불필요 |
| stats DB 위치 = primary RDS **단일 저장소** 고정 (설계서 §6.1 + T-2 §4.1) | 2E 는 `TenantContext.use("example-corp")` 고정. event.tenant 기반 라우팅 없음. tenant 는 `stats_send_group.tenant` 컬럼값 |

---

## 4. 공통 기술 스택 (Phase 1 상속 + 추가)

Phase 1 지시서 §2 모두 상속. 추가:

| 항목 | 용도 | 도입 지시서 |
|---|---|---|
| Jakarta Bean Validation (`spring-boot-starter-validation`) | DTO 기본 6 필드 런타임 검증 (`channelCode` 승격 반영, Phase 2F parse 단계) | 2A (완료) + 2F (listener 레벨 parse) |
| Spring Kafka 배치 listener (`ConcurrentKafkaListenerContainerFactory.isBatchListener=true`) | 배치 전환 (RDR D-1) | 2F |
| Micrometer Timer/Counter | Grafana 5 메트릭 (§8A.1) | 2F |

> **변경 사항 (Phase 2E/2F 재설계 반영)**: `Spring Retry (spring-retry)` 도입 **삭제**. 기존 단건 지시서의 `@Retryable(CannotAcquireLockException)` 전략은 배치 전환으로 폐기되고, 배치 재시도는 Kafka `DefaultErrorHandler` 로 이관 (2F).

---

## 5. 공통 제약 (모든 지시서 공통 적용)

| # | 제약 |
|---|---|
| G1 | jOOQ 쿼리는 codegen artifact 의 테이블/컬럼 상수 사용. 문자열 SQL 금지 |
| G2 | 원본 테이블 조회는 반드시 `DslContextFactory.forTenant(tenant)` 경유 — `TenantAssertingListener` 가 `TenantContext.get() == expected` 강제 검증 |
| G3 | stats upsert 는 `TenantContext` 를 `"example-corp"` 로 전환한 블록 내에서 수행 (stats = primary RDS 단일 저장소, 설계서 §6.1) |
| G4 | DLT 메시지에 `x-error-reason` 헤더 필수. reason 상수는 `DltErrorReason` 오브젝트에서 중앙 관리 (2F 에서 정의). DLT 토픽 = `example-corp.stat.send-result-dlt.json` (T-4 확정) |
| G5 | 기존 테스트 (Phase 1 + 2A~2D 누적) 회귀 통과 |
| G6 | 모든 신규 테스트는 TDD (RED 먼저 작성 → GREEN). 역순 구현 금지 |
| G7 | `StatsPipelineStub` 및 기존 단건 `StatsSendResultListener` 는 **2F 에서만 제거**. 2A~2E 는 stub 유지 — 중간 단계 회귀 방어 |
| G8 | 원본/stats 테이블 jOOQ import 는 `com.example.database.primary.Tables.*` 경로 사용 |
| G9 | `TenantContext` 블록 전환은 `TenantContext.use(tenant) { ... }` inline 함수 사용. 수동 `set`/`clear` try-finally 패턴 금지 |
| **G10** | **markAll 호출은 `batchUpsert` 성공 후에만** (RDR D-3). 마킹 순서 뒤집기 금지. markAll 실패는 silent skip + 경고 로그 (§9 best-effort 계약) |
| **G11** | **재시도 금지 영역**: `Spring Retry` / `@Retryable` 도입 금지. 배치 재시도는 Kafka `DefaultErrorHandler` 일원화 |
| **G12** | `JooqConfig.kt` 수정 금지 — example-database `1.20260417.3` 이상으로 schema qualifier 이슈 해소. `Settings.withRenderSchema(false)` 추가 금지 |

---

## 6. 공통 패키지 구조 (Phase 1 확장)

```
stats-consumer/src/main/kotlin/com/example/stats/consumer/
├── code/
│   ├── TenantCode.kt               (기존)
│   ├── ChannelType.kt              [2B 완료]  (비즈니스 — String 정규화)
│   └── KnownChannel.kt             [2B 완료]  (관측 helper — enum)
├── dedup/
│   ├── DedupService.kt             (2F 에서 배치 API 로 개정: filterNew + markAll)
│   └── RedisDedupService.kt        (2F 에서 pipeline/MSETNX 기반으로 개정)
├── dlt/
│   ├── DltErrorReason.kt           [2F]  (PARSE_FAIL / LOGIC_ERROR / UPSERT_FAIL 등 추가)
│   └── DltPublisher.kt             [2F 신규]  (§6A.2 메시지 스키마)
├── lookup/                          [2C 완료]
│   ├── OriginalMessageLookup.kt    (interface)
│   ├── OriginalMessageRecord.kt    (4필드)
│   └── OriginalMessageLookupImpl.kt (jOOQ)
├── mapper/                          [2D 완료]
│   ├── DimensionMapper.kt
│   └── StatsDimensions.kt
├── upsert/                          [2E]
│   ├── UpsertService.kt            (interface — batchUpsert)
│   └── UpsertServiceImpl.kt        (@Transactional + batch SQL)
├── listener/
│   └── StatsSendResultListener.kt  (2F 에서 배치 listener 로 교체)
├── config/
│   ├── JooqConfig.kt               (변경 없음 — G12)
│   ├── KafkaConfig.kt              (2F 에서 배치 ContainerFactory + DefaultErrorHandler 추가)
│   └── DataSourceConfig.kt         (기존)
└── pipeline/
    ├── StatsPipeline.kt            (2F 에서 제거 검토 — 단건 interface)
    ├── StatsPipelineStub.kt        (2F 에서 삭제)
    ├── StatsBatchPipeline.kt       [2F 신규]
    ├── StatsBatchPipelineImpl.kt   [2F 신규]
    ├── ExtEventValidator.kt        [2A 완료]
    ├── TenantRegistry.kt           [2F 존치]
    └── exceptions/                 # 파이프라인 경계 예외를 DltErrorReason 매핑 대상으로 응집 배치
        ├── ExtOptionalFieldNullException.kt       [2A 완료]
        ├── OriginalNotFoundException.kt           [2C 완료]
        ├── UnknownTenantException.kt              [2F]
        └── GroupLookupRaceFailureException.kt     [2E]
```

> **설계 의도 (배치 근거)**: 4개 exception 은 모두 파이프라인 경계 예외 (DLT reason 매핑 대상) 이며, 기능 패키지 (`lookup/`, `upsert/`) 대신 `pipeline/exceptions/` 에 응집해 `DltErrorReason.from` 매핑 테이블과의 물리적 근접성을 유지한다. 각 개별 지시서는 이 위치를 고정으로 사용한다.

---

## 7. 전체 성공 기준 (6개 지시서 누적)

- ✅ Phase 2A/2B/2C/2D 완료 (~40+ 테스트 pass 확인)
- ✅ 2E RED 1~9 GREEN (9 tests)
- ✅ 2F RED 1~12 GREEN (12 tests)
- ✅ Phase 1 기존 테스트 회귀 통과 (단건 listener → 배치 listener 교체 감안)
- ✅ `./gradlew :stats-consumer:test` 전체 통과
- ✅ 본사 이벤트 3건 → `stats_send_group` + `stats_send_detail` 정상 적재 (배치 단위)
- ✅ 동일 messageId 2회 → dedup 에 의해 1회만 반영, 다른 channelCode 는 2건 모두 처리 (축 분리)
- ✅ EXT 이벤트 (optional 6 완비) → lookup 스킵 + stats 반영
- ✅ SND/SND_LOG 양쪽 없음 → DLT `x-error-reason: ORIGINAL_NOT_FOUND` (record 격리, 배치 진행)
- ✅ batchUpsert 예외 → FixedBackOff 재시도 → 초과 시 배치 전체 DLT
- ✅ Redis markAll 실패 → silent skip + 경고 로그 (best-effort 계약)
- ✅ `StatsPipelineImpl` / 구 단건 listener / `StatsPipelineStub` 코드베이스에서 완전 제거
- ✅ `application-{prod,dev}.yml` Kafka 프로파일 분리 (1000/64KB/200ms vs 100/8KB/100ms)
- ✅ DLT 메시지에 §6A.2 스키마 (`tenant + messageId + batchId + reason + originalPayload + failedAt`) + `x-error-reason` 헤더

---

## 8. 범위 밖 (별도 트랙)

- **F-1**: `SchemaAwareDataSource` shared 모듈 승격 (stats-batch / billing 진입 시)
- **F-2**: `TenantRoutingDataSource` 미등록 테넌트 폴백 정책 재검토 (2F 진입 전 결정)
- **F-3**: `@Testcontainers` 관용 패턴 전환 (테스트 확장 시점)
- **F-4**: 코드 스타일 소소 DRY
- **F-5/F-6**: TC MySQL race 후속 액션 — **배치 전환으로 상류 해결됨** (RDR §2.1). 운영 투입 후 F-14 로 재평가
- **F-11**: Kafka 파라미터 실측 튜닝 (4 메트릭 기반, 운영 투입 후 H)
- **F-12**: Grafana 대시보드 신설 (5 메트릭, T-1 배포 전 H)
- **F-13**: DLT 운영 도구 (재처리 CLI? kafka-ui 수동?) 결정 — 2F 진입 시 M
- **F-14**: 배치 groupBy 전환 후 race 잔존 여부 재평가 — 운영 투입 후 H
- **Phase 3**: 메트릭, 헬스체크, 로그 포맷 표준화, ArgoCD manifest

---

## 9. 참조

- 설계서: `01-stats-consumer-design.md`
  - §9 (Consumer 계약)
  - §1 (흐름 — 배치 파이프라인)
  - §3 (Lookup)
  - §4 (차원)
  - §5 (Dedup — 배치 API)
  - §6 (Upsert — batchUpsert 계약)
  - §6A (실패 계층)
  - §7 (에러 카탈로그)
  - §8.1 (Kafka 프로파일 분리)
  - §8A (관측가능성)
- Phase 1 지시서: `shackled-phase1-directive.md`
- USE 전환 지시서: `shackled-use-tenant-directive.md`
- canonical-model: `shared/canonical-model/src/main/kotlin/com/example/canonical/stats/StatSendResultEvent.kt` (기본 6필드 + EXT optional 6필드)
- TenantContext / TenantRoutingDataSource: `shared/tenant-routing-core`, `shared/tenant-routing-spring-boot3`
- jOOQ artifact: `com.example.database:jooq-{env}-java21:1.20260417.3+` (Nexus)
- schema.sql: `stats-consumer/src/test/resources/schema.sql` (+ `secondary-lookup-ddl.sql` for 2C multi-DB)
- RDR (배치 전환): `example-stats-billing/docs/decisions/reviews/RDR-2026-04-17-stats-consumer-batch-processing-redesign.md`
- RDR (pass-through): `example-stats-billing/docs/decisions/reviews/RDR-2026-04-17-kafka-payload-passthrough-discovery.md`
- RDR (1라운드 리뷰): `example-stats-billing/docs/decisions/reviews/RDR-2026-04-17-phase2-directive-review.md`
- T-2 대사: `50-pipeline/T2-stats-batch/01-stats-batch-design.md` §4.3 (§9 best-effort 복원 축)
