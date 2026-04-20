# shackled Phase 2E 지시서: UpsertService (배치)

- **체급**: L
- **산출물 유형**: code
- **코드 대상**: backend (Spring Boot 3 Kotlin + jOOQ)
- **TDD**: Red → Green → Refactor
- **구현 위치**: `~/Work/example/example-stats-billing/stats-consumer/`
- **개요**: `shackled-phase2-00-overview.md`
- **의존**: 2D (`StatsDimensions` 타입, `105acc9` 구현 완료)
- **선행 필수**: `shackled-shared-tenant-context-use-block.md` (TenantContext.use API)
- **참조 RDR**: `example-stats-billing/docs/decisions/reviews/RDR-2026-04-17-stats-consumer-batch-processing-redesign.md`

---

## 1. 목적 + 계약

### 1.1. Consumer 계약 (설계서 §9 인용, 최우선 박제)

> **실시간 통계는 근사치다.** 대사가 불일치를 탐지하고, 사람이 로그 테이블 (`TMG_MSG_TGUS` / `MM_MSG`) 기준으로 stats 를 수정하며, 롤업이 멱등 재실행으로 상위 테이블까지 동기화한다. Consumer 는 **성능 + 포이즌 격리 + 관측가능성** 을 책임진다.

이 계약이 Phase 2E 구현의 모든 트레이드오프를 결정한다:
- **성능**: 같은 차원 N 건은 사전 집계 후 1 UPSERT (count 증분 N) — DB 왕복 축소 + row lock 경합 제거
- **포이즌 격리**: batchUpsert 는 배치 단위 이분법 (전체 성공 / 전체 재시도 / 전체 DLT). 부분 재시도 없음
- **관측가능성**: 구조화 로그 (`tenant/messageId/batchId/reason/stage`, 설계서 §8A.2) + Grafana `onBatch` latency (§8A.1)

### 1.2. 단건 → 배치 전환 사유

이전 2E 초안은 단건 `upsert(dim: StatsDimensions)` + Spring Retry 기반 건별 재시도였다. 아래 RDR-2026-04-17-stats-consumer-batch-processing-redesign §2.1 에 따라 **폐기**:

| 문제 | 단건 처리에서 발생 | 배치 전환 후 |
|---|---|---|
| 처리량 | 1 record = 1 TX + 1 UPSERT | N 건 → 집계 후 M 행 UPSERT (M ≪ N) |
| Row lock 경합 (F-5/F-6 원인) | 같은 `(tenant, channelType, timeSlot)` 동시 UPDATE → deadlock | 집계 단계에서 동일 차원 중복 제거 → 경합 자체 소멸 |
| Exactly-once 실패 모드 | Redis 마킹 → DB 실패 → dedup skip → 누락 | 마킹을 UPSERT 성공 후로 이동 (§5.3, Phase 2F 책임) |

**핵심 판단** (RDR §2.1): F-5 (TC 격리수준 RC) / F-6 (parameter group race) 는 단건 시대의 증상 관리였음. 배치 전환이 상류 해결.

### 1.3. 저장소 원칙 (설계서 §6.1 확정)

> **stats 테이블은 primary RDS 단일 저장소이다.** `event.tenant` 에 관계없이 모든 행은 primary-ds 에 적재되며, tenant 는 `stats_send_group.tenant` **컬럼값** 으로만 구분된다. 다중 tenant 엔트리는 단일 `batchUpsert` 호출 + 단일 트랜잭션으로 primary RDS 에 공존한다.

| 항목 | 값 |
|---|---|
| stats datasource | primary-ds 고정 (`DslContextFactory.forTenant("example-corp")`) |
| 진입 TenantContext | `TenantContext.use("example-corp") { ... }` 고정. 호출자(2F) 책임 |
| tenant 별 분기 | **없음**. `event.tenant` 기반 라우팅 / Map 분리 금지 |
| 다중 tenant 처리 | 한 Map 안에 공존, 단일 트랜잭션 |
| Phase 2C `DslContextFactory.forTenant(tenant)` | 원본 lookup 전용. stats 쓰기 경로와 무관 |

이 원칙은 RED 4 검증의 기반이며, §5.3 "하지 말 것" 리스트의 근거이기도 하다.

### 1.4. 2E 범위 (Phase 2F 와의 경계)

| 항목 | 2E 책임 | 2F 책임 |
|---|---|---|
| 집계 (`groupingBy().eachCount()`) | ❌ | ✅ (배치 오케스트레이션) |
| `filterNew` / `markAll` 호출 | ❌ | ✅ |
| `batchUpsert(aggregated)` 구현 | ✅ | ❌ (소비만) |
| `TenantContext.use("example-corp")` 진입 | ❌ (호출자가 감쌈) | ✅ |
| tenant 별 datasource 라우팅 | — (**애초에 존재하지 않음**, §1.3 참조) | — |
| 배치 트랜잭션 | ✅ | (경계 설정은 2F) |
| UPSERT 실패 → 배치 재시도 / DLT 분기 | ❌ (예외 throw 까지) | ✅ (`DefaultErrorHandler` 배선) |
| Grafana 메트릭 emit | ❌ (interface 만) | ✅ (listener 레벨) |

즉 2E 는 **순수하게 `batchUpsert(Map<StatsDimensions, Long>) → Unit / throws`** 의 원자 동작만 책임진다. 실패는 예외로 전파, 상위 (2F) 가 분류·라우팅.

> 본 지시서의 저장소 원칙 (§1.3) 은 설계서 §6.1 + T-2 `01-stats-batch-design.md` §4.1 (stats 쿼리: primary RDS — tenant 별 실행) 가 함께 박제한 "stats 단일 DB 전제" 의 직접 반영이다. 이 전제가 변경될 경우 본 지시서 + Phase 2F 지시서 재개정 필요.

---

## 2. 선행 조건

### 2.1. Phase 2A~2D 자산 (재사용, 변경 금지)

| 자산 | 경로 | 용도 |
|---|---|---|
| `StatsDimensions` | `stats-consumer/.../mapper/StatsDimensions.kt` | 9차원 키 (Map 키) |
| `TenantContext.use("example-corp") { ... }` | `shared/tenant-routing-core` | primary-ds 연결 활성화 (호출자=2F 책임). 본 서비스는 진입 시점에 고정 "example-corp" 전제 |
| `DslContextFactory.forTenant("example-corp")` | `stats-consumer/.../config/JooqConfig.kt` | primary-ds 용 jOOQ DSLContext 획득. 인자 고정 ("example-corp") |
| `TenantCode.PRIMARY` | `stats-consumer/.../code/TenantCode.kt` | "example-corp" 상수 (리터럴 산재 방지) |
| `SchemaAwareDataSource` | 기존 배선 | primary RDS 는 schema 가 database 명에 고정되어 스위칭 없음. stats 쓰기 경로에는 사실상 no-op |

### 2.2. jOOQ 의존성 전제

- `com.example.database:jooq-{env}-java21:1.20260417.3` 이상 (Phase 2C 에서 확정)
- **`Settings.withRenderSchema(false)` 추가 금지** — `1.20260417.3` 의 `isOutputSchemaToDefault=true` 로 이미 해소. `JooqConfig.kt` 현 상태 유지
- 테이블 상수: `com.example.database.primary.Tables.STATS_SEND_GROUP`, `STATS_SEND_DETAIL`

### 2.3. TestContainers 설정 전제

- `AbstractIntegrationTest` 가 primary DB 에 `schema.sql` (stats 테이블 포함) 적용하고 있음 (Phase 2C 에서 확장 완료)
- MySQL 격리수준: RC (기본) 유지. 앱 레벨 `@Transactional(isolation=...)` 강제 금지

### 2.4. stats 테이블 DDL 전제 (설계서 §6.3)

```sql
stats_send_group  UNIQUE KEY (tenant, send_date, member_id, channel_type)
stats_send_detail UNIQUE KEY (group_id, is_substitute, original_channel_type,
                              result_code, send_system_type)
                  send_count BIGINT NOT NULL DEFAULT 1
```

`ON DUPLICATE KEY UPDATE send_count = send_count + VALUES(send_count)` 가 정확히 이 UNIQUE KEY 에 매칭됨. `result_category` 는 UNIQUE 제외 (02-Design/02-table-schema.md §7.2 권위 소스) — `result_code` 와 1:1 고정 매핑이므로 INSERT 시점 값 세팅만 필요, 충돌 시 업데이트 대상 아님.

---

## 3. RED 케이스 상세

총 **9 케이스** (L급 체급 반영). 테스트 파일 2분할:

- `UpsertServiceBatchIntegrationTest.kt` — RED 1~4, 6, 8, 9 (TestContainers MySQL 통합)
- `UpsertServiceRaceTest.kt` — RED 7 (병렬 2세션)
- `UpsertServiceEmptyTest.kt` (또는 위 파일에 포함) — RED 5

### RED 1: 신규 차원 1건 (example-corp)

```
Given: stats_send_group / stats_send_detail 비어있음
       TenantContext = "example-corp"
       aggregated = { dim1 : 3L }   // dim1 = (example-corp, 2026-04-17, m1, SMS, NONE, false, 0000, SUCCESS, WEB)
When:  upsertService.batchUpsert(aggregated)
Then:
  - stats_send_group 1행 신설, group_id 자동 생성
  - stats_send_detail 1행 신설, send_count = 3
```

### RED 2: 기존 차원 누적 (같은 PK 재방문)

```
Given: RED 1 실행 후 stats_send_group 1행 + stats_send_detail 1행 (send_count=3)
When:  upsertService.batchUpsert({ dim1 : 2L })  // 같은 dim1
Then:
  - stats_send_group 1행 유지 (INSERT 없음)
  - stats_send_detail send_count = 3 + 2 = 5
  - ON DUPLICATE KEY UPDATE send_count = send_count + VALUES(send_count) 검증
```

### RED 3: 배치 내 사전 집계 검증 (D-2 핵심)

```
Given: 빈 상태
       aggregated = { dim1 : 10L, dim2 : 5L, dim3 : 2L }   // 3개 차원
       (호출자가 Map<StatsDimensions, Long> 로 이미 집계한 상태로 전달)
When:  upsertService.batchUpsert(aggregated)
Then:
  - stats_send_group: 3행 (각 (tenant, send_date, memberId, channelType) 유니크 조합)
  - stats_send_detail: 3행, 각 send_count = 10 / 5 / 2
  - SQL 실행 횟수 검증 (jOOQ ExecuteListener 스파이):
    · Tier 1 group lookup/insert: 최대 3회 (차원 수)
    · Tier 2 detail UPSERT: batch 1회 (총 17 record 가 17 UPSERT 가 아닌 1 batch statement 로 실행됨)
  - "N번 반복 UPDATE 가 아님" 이 핵심 검증
```

### RED 4: 다중 tenant 혼합 → primary RDS 단일 저장 + tenant 컬럼 공존

설계서 §6.1 확정: **stats DB = primary RDS 동일 인스턴스 고정**. tenant 는 라우팅 축이 아니라 `stats_send_group.tenant` **컬럼값** 으로만 구분된다. 따라서 한 배치의 다중 tenant 엔트리는 **단일 `batchUpsert` 호출 + 단일 트랜잭션** 으로 primary RDS 에 공존 적재된다.

```
Given: primary RDS 의 stats_send_group / stats_send_detail 빈 상태
       tenant-a / tenant-b 등 다른 tenant DB 의 stats 테이블은 본 서비스 책임 밖 (무변경이어야 함)
       aggregated = {
         dimMegabird : 5L,    // tenant="example-corp", memberId=mM, channelType=SMS, ...
         dimCoupang  : 3L,    // tenant="tenant-a",  memberId=mC, channelType=LMS, ...
         dimCes      : 2L,    // tenant="tenant-b",      memberId=mX, channelType=TKA, ...
       }
       // 3 엔트리는 StatsDimensions 9차원 중 tenant 컬럼만 다른 서로 다른 키
When:  batchUpsert(aggregated)   // 단 1회 호출, 단일 트랜잭션, 단일 datasource (primary-ds)
Then:
  - **primary RDS** 의 stats_send_group: 3행
      · (tenant=example-corp, ..., channel_type=SMS) 1행
      · (tenant=tenant-a,  ..., channel_type=LMS) 1행
      · (tenant=tenant-b,      ..., channel_type=TKA) 1행
  - **primary RDS** 의 stats_send_detail: 3행, 각 send_count = 5 / 3 / 2
  - **tenant-a DB / tenant-b DB 의 stats 테이블 무변경** (애초에 쓰지 않음)
  - 실행된 SQL 이 모두 primary-ds 로 귀속되었는지 jOOQ ExecuteListener 스파이로 검증
```

**핵심 검증 포인트**:
- 단 1회 `batchUpsert` 호출로 다중 tenant 엔트리 전부 처리 (tenant 별 호출 분리 없음)
- 호출자 (2F) 는 `TenantContext.use("example-corp") { ... }` 로 감싸 진입 — event.tenant 기반 분기 없음
- 본 서비스는 내부에서 tenant 별 라우팅 / Map 분리 / DB 스위칭을 수행하지 않는다

### RED 5: 빈 map 입력 → no-op

```
Given: aggregated = emptyMap<StatsDimensions, Long>()
When:  upsertService.batchUpsert(aggregated)
Then:
  - 예외 없음 (assertDoesNotThrow)
  - stats_send_group / stats_send_detail 무변경
  - 트랜잭션 열지 않음 검증 (선택): TransactionSynchronizationManager 스파이 또는 쿼리 카운트 = 0
  - 로그: `log.debug("batchUpsert skipped: empty aggregated")` 정도의 가벼운 로그만
```

### RED 6: 트랜잭션 실패 시 rollback (의도 예외 주입)

```
Given: 빈 상태
       aggregated = { dim1 : 5L, dim2 : 3L }
       Tier 2 UPSERT 직전에 예외 던지는 hook 주입 (jOOQ ExecuteListener.exception 또는 mock)
When:  upsertService.batchUpsert(aggregated) → 예외 전파 기대
Then:
  - RuntimeException (또는 DataAccessException) 전파
  - stats_send_group: 0행 (Tier 1 INSERT 도 rollback 됨)
  - stats_send_detail: 0행
  - "배치 전체가 단일 트랜잭션" 증명
```

### RED 7: F-5 race 검증 (동일 PK 동시 UPDATE 2 세션)

```
Given: stats_send_group 1행 + stats_send_detail 1행 (dim1, send_count=10) 사전 적재
       TestContainers MySQL 에서 2개 별도 connection 획득
When:
  - 세션 A: batchUpsert({ dim1 : 5L })  // UPDATE count = 10+5 시도
  - 세션 B: batchUpsert({ dim1 : 7L })  // UPDATE count = 10+7 시도
  - 두 세션 병렬 실행 (CountDownLatch 로 동시 시작)
Then:
  - 두 세션 모두 정상 커밋 (MySQL InnoDB ROW LOCK 직렬화)
  - 최종 send_count = 10 + 5 + 7 = 22 (순서 무관)
  - Deadlock 예외 없음 (배치 집계 덕분에 같은 row 경합이 2회로 축소 → 단순 직렬화)
  - 단건 시대의 N회 경합 시나리오는 집계 단계에서 이미 제거됨

주의: 이 테스트는 "배치 전환이 F-5 race 를 상류에서 해결함" 의 회귀 증명이다.
     Deadlock 이 발생하면 배치 전환 전제가 깨진 것 → 설계 재검토 필요.
```

### RED 8: EXT 경로 (`tenant = "__ext__"`)

```
Given: 빈 상태
       aggregated = { bmsDim : 4L }
       bmsDim = (__ext__, 2026-04-17, __ext__g1_c1, EXT_A, NONE, false, 9001, FAILURE, EXT)
       (Phase 2D mapExt 결과물, lookup 스킵된 상태)
       TenantContext = "example-corp" (EXT stats 는 primary-ds 에 적재, 설계서 §6.1)
When:  upsertService.batchUpsert(aggregated)
Then:
  - primary DB 의 stats_send_group: 1행 (tenant="__ext__" 컬럼 값 확인)
  - stats_send_detail: 1행, send_count = 4, send_system_type = "EXT"
  - batchUpsert 는 tenant 값에 무관하게 동일 SQL 경로 (분기 없음) — EXT 처리 로직은 2F 책임
```

### RED 9: 대량 batch sanity (1000 엔트리)

```
Given: 빈 상태
       aggregated = 1000개 서로 다른 StatsDimensions, 각 count = Random 1~10
When:  assertTimeoutPreemptively(Duration.ofSeconds(5)) {
           upsertService.batchUpsert(aggregated)
       }
Then:
  - stats_send_group: 1000행
  - stats_send_detail: 1000행, send_count 합 = 입력 count 합
  - 5초 timeout 내 완료 (개발 환경 sanity. 운영 튜닝은 §8A.1 F-11 로 위임)

주의: 이 테스트는 성능 회귀 조기 감지용. 절대 임계값이 아님.
     CI 환경 변동성 큰 경우 @Tag("performance") 로 분리하거나 timeout 완화 가능.
```

---

## 4. GREEN 구현 스펙

### 4.1. `UpsertService.kt` (interface)

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/upsert/UpsertService.kt`

```kotlin
interface UpsertService {
    /**
     * 배치 집계 결과를 primary RDS 단일 트랜잭션으로 UPSERT.
     *
     * 저장소 계약 (설계서 §6.1 확정):
     * - stats DB 위치는 **primary RDS 고정**. event.tenant 값에 관계없이 모든 행은 primary-ds 에 적재
     * - 다중 tenant 엔트리는 단일 Map 에 공존 가능. 구분은 `stats_send_group.tenant` 컬럼값으로만 수행
     * - 본 서비스는 tenant 기반 라우팅을 하지 않는다 (Phase 2C `DslContextFactory.forTenant` 는
     *   원본 lookup 용, stats 쓰기 경로와 무관)
     *
     * 호출자 계약:
     * - aggregated 는 호출자 (Phase 2F) 가 이미 groupingBy().eachCount() 로 집계한 상태
     * - 호출자는 이 호출을 `TenantContext.use("example-corp") { ... }` 블록으로 감싸 진입
     * - 입력이 비어있으면 no-op (트랜잭션 열지 않음)
     *
     * 예외 계약:
     * - 성공 시 Unit 반환
     * - 실패 시 예외 전파 (DataAccessException 계열). 상위(2F) 가 분류해 배치 재시도 or DLT
     * - 이 서비스는 재시도하지 않는다 (Phase 2F 의 DefaultErrorHandler 책임)
     */
    fun batchUpsert(aggregated: Map<StatsDimensions, Long>)
}
```

### 4.2. `UpsertServiceImpl.kt`

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/upsert/UpsertServiceImpl.kt`

```kotlin
import com.example.database.primary.Tables.STATS_SEND_GROUP
import com.example.database.primary.Tables.STATS_SEND_DETAIL
import com.example.stats.consumer.code.TenantCode

@Service
class UpsertServiceImpl(
    private val dslContextFactory: DslContextFactory,
) : UpsertService {

    private val log = LoggerFactory.getLogger(UpsertServiceImpl::class.java)

    @Transactional
    override fun batchUpsert(aggregated: Map<StatsDimensions, Long>) {
        if (aggregated.isEmpty()) {
            log.debug("batchUpsert skipped: empty aggregated")
            return
        }

        // stats 테이블은 primary RDS 고정 (설계서 §6.1). event.tenant 와 무관하게 항상 primary-ds.
        // 호출자(2F)가 TenantContext.use("example-corp") { ... } 로 감싸 진입한 상태를 전제로 한다.
        // 방어 체크: 잘못된 TenantContext 로 진입하지 않았는지 확인.
        val tenant = TenantContext.get()
        check(tenant == TenantCode.PRIMARY.code()) {
            "batchUpsert must be invoked under TenantContext.use(\"example-corp\"); actual=$tenant"
        }
        val ctx = dslContextFactory.forTenant(TenantCode.PRIMARY.code())

        // Tier 1: 차원별 group_id 획득 (batch SELECT + batch INSERT)
        val groupIds: Map<StatsDimensions, Long> = resolveGroupIds(ctx, aggregated.keys)

        // Tier 2: batch UPSERT send_count = send_count + VALUES(send_count)
        batchUpsertDetail(ctx, groupIds, aggregated)

        log.debug(
            "batchUpsert completed: dimensions={} totalCount={} stage=upsert",
            aggregated.size, aggregated.values.sum()
        )
    }

    // -------------------------------------------------------------------------
    // Tier 1: resolveGroupIds — SELECT 일괄 → 미존재만 INSERT batch → id 회수
    // -------------------------------------------------------------------------

    /**
     * 전략:
     *   1. 모든 차원의 (tenant, send_date, member_id, channel_type) 를 WHERE IN 튜플로 일괄 SELECT
     *   2. 조회 결과 dimensions → groupId Map 구성
     *   3. 누락된 차원들만 batch INSERT (ON DUPLICATE KEY UPDATE id = id 로 race 방어)
     *      또는 INSERT IGNORE + re-SELECT 전략 택일
     *   4. 최종 SELECT 로 전체 id 확정
     *
     * race 처리 (설계서 §6.2 단건 알고리즘을 배치로 확장):
     *   - batch INSERT 후 일부 행이 중복 키 예외 → 해당 차원은 상대 세션이 먼저 INSERT 한 것
     *   - 재SELECT 로 id 회수 (READ COMMITTED 격리수준 전제, 설계서 §6.2 인프라 전제)
     *   - 3회 시도 후에도 누락된 차원이 있으면 GroupLookupRaceFailureException 던짐
     */
    private fun resolveGroupIds(
        ctx: DSLContext,
        dimensions: Set<StatsDimensions>,
    ): Map<StatsDimensions, Long>

    // -------------------------------------------------------------------------
    // Tier 2: batchUpsertDetail — batch INSERT ... ON DUPLICATE KEY UPDATE
    // -------------------------------------------------------------------------

    /**
     * jOOQ batch API:
     *   ctx.batch(
     *     aggregated.map { (dim, count) ->
     *       ctx.insertInto(STATS_SEND_DETAIL, ...)
     *         .values(groupIds[dim], ..., count)
     *         .onDuplicateKeyUpdate()
     *         .set(STATS_SEND_DETAIL.SEND_COUNT,
     *              STATS_SEND_DETAIL.SEND_COUNT.plus(DSL.value(count)))
     *     }
     *   ).execute()
     *
     * 또는 단일 multi-row INSERT 로 묶어 SEND_COUNT + VALUES(SEND_COUNT) 활용:
     *   ctx.insertInto(STATS_SEND_DETAIL, columns...)
     *     .valuesOfRecords(records)
     *     .onDuplicateKeyUpdate()
     *     .set(STATS_SEND_DETAIL.SEND_COUNT,
     *          STATS_SEND_DETAIL.SEND_COUNT.plus(
     *              DSL.field("VALUES({0})", Long::class.java, STATS_SEND_DETAIL.SEND_COUNT)
     *          ))
     *     .execute()
     *
     * jOOQ 3.20.4 VALUES() 함수 직접 지원 여부 확인 후 선택. 최악의 경우 GREEN 에서 전자 사용.
     *
     * IS_SUBSTITUTE 타입 주의: jOOQ codegen 이 TINYINT(1) 를 Byte 로 반환하므로
     *   val isSubstituteByte: Byte = if (dim.isSubstitute) 1 else 0
     * 변환 후 바인딩.
     */
    private fun batchUpsertDetail(
        ctx: DSLContext,
        groupIds: Map<StatsDimensions, Long>,
        aggregated: Map<StatsDimensions, Long>,
    )
}
```

### 4.3. `GroupLookupRaceFailureException.kt`

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/pipeline/exceptions/GroupLookupRaceFailureException.kt`

```kotlin
/**
 * resolveGroupIds 가 3회 재시도 후에도 일부 차원의 group_id 를 회수하지 못한 경우.
 * DLT reason: GROUP_LOOKUP_RACE_FAILURE (설계서 §7.3).
 *
 * 실제 운영에서 발생하면 MySQL 격리수준 설정 (RC 전제) 또는 parameter group 이
 * 설계 전제와 불일치할 가능성 → 인프라 점검 트리거.
 */
class GroupLookupRaceFailureException(
    val missingDimensions: Collection<StatsDimensions>,
) : RuntimeException(
    "Group lookup race failed after retry: missingCount=${missingDimensions.size}"
)
```

### 4.4. JooqConfig 변경 제한

**중요**: Phase 2C 에서 `Settings.withRenderSchema(false)` 워크어라운드가 `example-database 1.20260417.3` 업그레이드로 해소되어 롤백됨. 본 Phase 2E 에서 **`Settings.withRenderSchema(false)` 재도입 금지 / Spring Retry 재도입 금지 / ExceptionTranslator 배선 추가 금지** (배치 재시도는 2F 의 Kafka `DefaultErrorHandler` 책임).

**단서 (2026-04-20 추가)**: 다중 statement 배치 트랜잭션 (Tier 1 + Tier 2 atomicity, §1.4) 충족을 위해 **Spring 트랜잭션 연동용 `TransactionAwareDataSourceProxy` 래핑은 허용**한다. Phase 2C 시점은 read-only 경로라 미노출됐던 구조적 요구이며, `DslContextFactory` 내 1회 래핑(≤5줄)에 국한한다. 예외 번역 / 재시도 / Settings 관련 변경은 금지 유지.

### 4.5. SQL 최종 형태 (설계서 §6.3 배치 확장)

```sql
-- Tier 1: 차원별 group_id 확보 (pseudo)
--   Step A. WHERE IN 튜플 SELECT (1 query)
SELECT id, tenant, send_date, member_id, channel_type
FROM stats_send_group
WHERE (tenant, send_date, member_id, channel_type) IN ((?,?,?,?), (?,?,?,?), ...);

--   Step B. 누락된 차원만 batch INSERT
INSERT INTO stats_send_group (tenant, send_date, member_id, channel_type)
VALUES (?,?,?,?), (?,?,?,?), ...;
-- 일부 중복 키 예외 발생 시 해당 차원은 상대 세션이 커밋 → Step C 로

--   Step C. 재SELECT (최대 3회 루프)
--   그래도 누락 → GroupLookupRaceFailureException

-- Tier 2: batch UPSERT (1 query, multi-row VALUES)
INSERT INTO stats_send_detail
  (group_id, is_substitute, original_channel_type, result_code, result_category,
   send_system_type, send_count)
VALUES
  (?,?,?,?,?,?,?), (?,?,?,?,?,?,?), ...
ON DUPLICATE KEY UPDATE
  send_count = send_count + VALUES(send_count);
```

**중요**: Tier 1 의 multi-row `INSERT ... ON DUPLICATE KEY UPDATE id = id` 트릭으로 group_id 를 한 번에 회수하는 방식도 후보. GREEN 구현 시 jOOQ 3.20 의 `insertInto().valuesOfRecords().onDuplicateKeyUpdate()` + `returning()` API 가 MySQL multi-row return 을 지원하는지 검증해 선택. 지원 안 되면 "SELECT → INSERT 누락만 → 재SELECT" 3단계로 확정.

---

## 5. REFACTOR 지침

### 5.1. 헬퍼 분리 (readability)

- `resolveGroupIds` 내부: `loadExisting(ctx, dims)`, `insertMissing(ctx, missing)`, `reSelect(ctx, missing)` 3단계 private 헬퍼 추출
- `batchUpsertDetail` 내부: `buildDetailRows(aggregated, groupIds)` 와 `executeBatchUpsert(ctx, rows)` 로 분리
- Byte 변환 (`IS_SUBSTITUTE`) 은 전용 확장 함수: `fun Boolean.toMySqlByte(): Byte = if (this) 1 else 0`

### 5.2. 관측가능성 로깅 (설계서 §8A.2 계약)

모든 에러 로그는 구조화 필드 필수:

```kotlin
// 정상 경로 (debug)
log.debug(
    "batchUpsert completed: tenant={} dimensions={} totalCount={} stage={}",
    tenant, aggregated.size, aggregated.values.sum(), "upsert"
)

// 실패 경로 (error)
log.error(
    "batchUpsert failed: tenant={} dimensions={} stage={} reason={}",
    tenant, aggregated.size, "upsert", ex.javaClass.simpleName, ex
)
```

`stage` 값은 `resolveGroupIds` / `batchUpsertDetail` 중 어느 단계에서 실패했는지 구분. `batchId` / `messageId` 필드는 2F 의 listener 가 MDC 에 주입 후 이 로그가 자동 포함되므로 여기서는 명시 바인딩 불요.

Micrometer timer 는 2F 의 listener 레벨에서 (`onBatch` latency, §8A.1). 본 서비스는 timer emit 하지 않음 (단위 재사용성 우선).

### 5.3. 하지 말 것

- `@Retryable` / Spring Retry 도입 금지 (1.3 분기 — 재시도는 2F 의 `DefaultErrorHandler`)
- `Settings.withRenderSchema(false)` 추가 금지 (2.2)
- `TenantContext.use` 중첩 금지 — 호출자가 이미 감싸놓은 상태 (2F 책임)
- **`batchUpsert` 내부에서 `event.tenant` 기반 `TenantContext.use(event.tenant)` 호출 금지** — stats 는 primary RDS 단일 저장소이며 tenant 컬럼 기반 구분. tenant 별 라우팅 아님 (설계서 §6.1)
- **stats 테이블이 각 tenant DB 에 별도 존재한다는 가정 금지** — 설계서 §6.1 및 T-2 §4.1 모두 primary RDS 단일 DB 전제. `DslContextFactory.forTenant("example-corp")` 고정 호출
- 다중 tenant 엔트리를 tenant 별 Map 으로 분리해서 N회 호출 금지 — 2F 도 분리하지 않는다. 한 배치 = 한 Map = 한 `batchUpsert` 호출 = 한 트랜잭션 (RED 4 의 형태)

---

## 6. DoD (Definition of Done)

### 6.1. 코드 산출물

- [ ] `UpsertService` interface 정의 완료
- [ ] `UpsertServiceImpl` 구현 완료 (`@Transactional`, `resolveGroupIds`, `batchUpsertDetail`)
- [ ] `GroupLookupRaceFailureException` 정의 완료
- [ ] `JooqConfig.kt` **미변경** 확인

### 6.2. 테스트

- [ ] RED 1~9 모두 GREEN (9/9)
- [ ] Phase 2A/2B/2C/2D 회귀 테스트 전체 통과 (최소 82 tests pass 유지)
- [ ] RED 7 병렬 race 테스트에서 deadlock 미발생 검증
- [ ] RED 9 성능 sanity: 1000 엔트리 5초 내 완료 (개발 환경)

### 6.3. 설계서 정합성

- [ ] §6.1 저장소 단일 DB 전제 준수: `DslContextFactory.forTenant(TenantCode.PRIMARY.code())` 고정 호출, `event.tenant` 기반 라우팅 부재 확인 (RED 4 로 회귀 감지)
- [ ] §6.5 `batchUpsert(Map<StatsDimensions, Long>)` 계약 충족
- [ ] §6A.1 UPSERT 실패 시 예외 전파 (상위 재시도 트리거)
- [ ] §8A.2 구조화 로그 필드 계약 준수 (`tenant/stage/reason`)

### 6.4. 문서

- [ ] 이 지시서의 "하지 말 것" (§5.3) 리스트 전수 미적용 확인
- [ ] 커밋 메시지에 RDR-2026-04-17-stats-consumer-batch-processing-redesign 참조

---

## 7. 영향받는 파일 리스트

### 7.1. 신규 생성

| 파일 | 내용 |
|---|---|
| `stats-consumer/src/main/kotlin/com/example/stats/consumer/upsert/UpsertService.kt` | interface |
| `stats-consumer/src/main/kotlin/com/example/stats/consumer/upsert/UpsertServiceImpl.kt` | `@Service` 구현 |
| `stats-consumer/src/main/kotlin/com/example/stats/consumer/pipeline/exceptions/GroupLookupRaceFailureException.kt` | custom exception |
| `stats-consumer/src/test/kotlin/com/example/stats/consumer/upsert/UpsertServiceBatchIntegrationTest.kt` | RED 1~4, 6, 8, 9 |
| `stats-consumer/src/test/kotlin/com/example/stats/consumer/upsert/UpsertServiceRaceTest.kt` | RED 7 (병렬 2세션) |

### 7.2. 변경 없음 (재사용)

| 파일 | 사유 |
|---|---|
| `JooqConfig.kt` | jOOQ 1.20260417.3 으로 schema qualifier 이슈 해소 |
| `DslContextFactory.kt` | 변경 없음 |
| `StatsDimensions.kt` (Phase 2D) | 2D 에서 확정된 9차원 data class 그대로 사용 |
| `TenantContext.use` | shared 모듈 그대로 |
| `SchemaAwareDataSource.kt` | Phase 2C 배선 그대로 |

### 7.3. 의존 artifact

- `com.example.database:jooq-dev-java21:1.20260417.3` 이상 (`build.gradle.kts` 이미 반영)

---

## 8. 후속 연계 (Phase 2F 와의 경계)

### 8.1. 2F 가 수행할 오케스트레이션

**주의**: stats 는 primary RDS 단일 저장소 (§1.3). Phase 2F 도 tenant 별 분리를 하지 않는다. 한 배치 = 한 Map = 한 `batchUpsert` 호출 = 한 트랜잭션.

```kotlin
// Phase 2F 의사코드 (이 지시서 범위 아님, 참고용)
@KafkaListener(batch = "true", ...)
fun onBatch(records: List<ConsumerRecord<String, String>>, ack: Acknowledgment) {
    val batchId = UUID.randomUUID().toString()
    MDC.put("batchId", batchId)

    try {
        val events = parseAndValidate(records)                    // record DLT
        val newEvents = dedupService.filterNew(events)            // 배치 Redis

        // 원본 조회는 event.tenant 별 DB 에서 (Phase 2C 의 DslContextFactory.forTenant(tenant)).
        // lookup 구간에서만 TenantContext.use(event.tenant) 로 감싸고,
        // 그 결과를 모아 StatsDimensions Map 으로 집계한다.
        val dims: List<StatsDimensions> = newEvents.map { event ->
            TenantContext.use(event.tenant) {
                mapDimension(event)  // 2D: 본사 경로 lookup or EXT mapExt
            }
        }
        val aggregated: Map<StatsDimensions, Long> =
            dims.groupingBy { it }.eachCount().mapValues { it.value.toLong() }

        // stats 쓰기는 단일 저장소 (primary RDS). tenant 별 분리 없이 한 번에 호출.
        TenantContext.use(TenantCode.PRIMARY.code()) {
            upsertService.batchUpsert(aggregated)                 // ← 2E 진입점
        }

        dedupService.markAll(newEvents)                           // UPSERT 성공 후 마킹 (D-3)
        ack.acknowledge()
    } catch (e: DataAccessException) {
        throw e  // → DefaultErrorHandler 배치 재시도 → 초과 시 배치 전체 DLT
    } finally {
        MDC.clear()
    }
}
```

### 8.2. 2E 가 노출하지 않는 것 (2F 자유)

- 배치 재시도 정책 (`FixedBackOff`, max attempts)
- Kafka `DefaultErrorHandler` 배선
- DLT publisher (`DltPublisher` 신규)
- Micrometer timer / meter 등록
- `TenantContext.use("example-corp")` 로 감싸는 동작
- lookup 구간의 tenant 별 `TenantContext.use(event.tenant)` (2C 의 라우팅과 정합)
- MDC batchId 주입

### 8.3. 2E 가 보장하는 계약 (2F 소비)

- `batchUpsert(aggregated)` 는 **atomic** — 전체 성공 또는 전체 rollback
- tenant 가 혼합된 Map 도 단일 트랜잭션으로 primary RDS 에 공존 적재 (§1.3)
- `aggregated.isEmpty()` 일 때 안전한 no-op (트랜잭션 열지 않음)
- 실패 시 예외 전파 (2F 의 `DefaultErrorHandler` 가 분류)
- 진입 TenantContext 는 호출자 책임. 본 서비스는 `TenantContext.get() == "example-corp"` 방어 체크 (잘못된 진입 시 `IllegalStateException`)

---

## 9. 참조

- 설계서: `01-stats-consumer-design.md`
  - §9 (Consumer 계약, 최우선 박스)
  - **§6.1 (stats DB 위치 = primary RDS 고정 — 본 지시서 §1.3 저장소 원칙의 근거)**
  - §6.2~§6.5 (UPSERT 흐름 + batchUpsert 계약)
  - §6A (실패 계층)
  - §8A (관측가능성)
- T-2 설계서: `50-pipeline/T2-stats-batch/01-stats-batch-design.md` §4.1 (stats 쿼리: primary RDS — tenant별 실행. 저장소 단일 DB 전제 이중 박제)
- RDR: `RDR-2026-04-17-stats-consumer-batch-processing-redesign.md` (D-1 ~ D-5 전체)
- RDR (선행): `RDR-2026-04-17-kafka-payload-passthrough-discovery.md` (channelCode 승격, dedup 키 축)
- wtth 1라운드 RDR: `RDR-2026-04-17-phase2-directive-review.md` (묶음 7, 12, 13 유지)
- schema.sql: `stats-consumer/src/test/resources/schema.sql` (`stats_send_group`, `stats_send_detail`)
- jOOQ artifact: `com.example.database:jooq-{env}-java21:1.20260417.3+`
- jOOQ import 경로: `com.example.database.primary.Tables.*`
- `StatsDimensions` (Phase 2D `105acc9`)
- `TenantCode` (`stats-consumer/.../code/TenantCode.kt`, `PRIMARY.code() == "example-corp"`)
- `TenantContext.use`: `shackled-shared-tenant-context-use-block.md` (선행)
- Phase 2F 지시서 (개정 예정): `shackled-phase2f-pipeline-assembly.md`
- 개요: `shackled-phase2-00-overview.md`
