# shackled Phase 2C 지시서: OriginalMessageLookup

- **체급**: M
- **산출물 유형**: code
- **코드 대상**: backend (Spring Boot 3 Kotlin + jOOQ)
- **TDD**: Red → Green → Refactor
- **구현 위치**: `~/Work/example/example-stats-billing/stats-consumer/`
- **개요**: `shackled-phase2-00-overview.md`
- **선행 필수**: `shackled-shared-tenant-context-use-block.md` (TenantContext.use API 추가)

---

## 1. 목적

원본 테이블 3종 (`TNT_INTG_MSG_SND` + `TMG_MSG_TGUS` + `TMG_MSG_GRP`) 을 조인 조회하여 `OriginalMessageRecord` 를 반환한다 (설계서 §3).

동일 `messageId` 에 본발송 시도 + 대체발송 시도가 서로 다른 `SVC_KND_CD` 로 누적될 수 있으므로 (composite PK `(message_id, SVC_KND_CD)`), consumer 는 이벤트의 `resultCode` 로 **해당 시도 행** 을 특정한다.

`TNT_INTG_MSG_SND` 1차 조회 → null 이면 `TNT_INTG_MSG_SND_LOG` fallback 2차 조회. 양쪽 모두 null 이면 `OriginalNotFoundException` 던짐 (DLT reason: `ORIGINAL_NOT_FOUND`).

---

## 2. 산출물

### 2.1. `OriginalMessageLookup.kt` (interface)

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/lookup/OriginalMessageLookup.kt`

```kotlin
interface OriginalMessageLookup {
    /**
     * tenant 기반 datasource 에서 (messageId, resultCode) 로 원본 시도 행을 조회.
     * SND → SND_LOG fallback. 양쪽 모두 없으면 OriginalNotFoundException.
     *
     * @param resultCode Kafka 이벤트의 resultCode (= TNT_INTG_MSG_SND.SND_RST_CD). 동일 messageId 에
     *                   본발송/대체발송 시도가 공존할 수 있으므로 시도 단위 매칭 키.
     */
    fun lookup(tenant: String, messageId: String, resultCode: String): OriginalMessageRecord
}
```

### 2.2. `OriginalMessageRecord.kt`

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/lookup/OriginalMessageRecord.kt`

```kotlin
data class OriginalMessageRecord(
    val memberId: String,            // TNT_INTG_MSG_SND.MB_ID
    val originalChannelCode: String?,    // TNT_INTG_MSG_SND.ORG_SVC_KND_CD (nullable, NULL=본발송/NOT NULL=대체발송)
    val registeredAt: LocalDateTime,   // TMG_MSG_GRP.REG_DTT (NOT NULL, LocalDateTime.now())
    val apiInstanceId: String?,     // TMG_MSG_GRP.API_INSTC_ID (nullable)
)
```

> **SUBTXT 3 필드 제거 (2026-04-17 wtth 리뷰 묶음 6+ 반영)**: `is_substitute` 판정이 `originalChannelCode != null` 로 변경되어 `subtxtStsCd` / `subtxtRstCd` / `subtxtStsCzCmt` 는 차원 매핑에 불필요. 설계서 §3.4 / §4.3 참조.
>
> **`channelCode` 필드 제거 (2026-04-17 추가 개정 — RDR-2026-04-17-kafka-payload-passthrough-discovery)**: `channel_type` 차원은 Kafka 이벤트 `StatSendResultEvent.channelCode` (= `SVC_KND_CD`) 에서 직접 주입되므로 lookup 반환 타입에서 불필요. 5필드 → 4필드.

### 2.3. `OriginalMessageLookupImpl.kt`

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/lookup/OriginalMessageLookupImpl.kt`

```kotlin
import com.example.database.primary.Tables.TMG_MSG_GRP
import com.example.database.primary.Tables.TMG_MSG_TGUS
import com.example.database.primary.Tables.TNT_INTG_MSG_SND
import com.example.database.primary.Tables.TNT_INTG_MSG_SND_LOG
import com.example.tenant.routing.TenantContext

@Service
class OriginalMessageLookupImpl(
    private val dslContextFactory: DslContextFactory,
) : OriginalMessageLookup {

    override fun lookup(tenant: String, messageId: String, resultCode: String): OriginalMessageRecord =
        TenantContext.use(tenant) {
            val ctx = dslContextFactory.forTenant(tenant)
            queryFromSnd(ctx, messageId, resultCode)
                ?: queryFromSndLog(ctx, messageId, resultCode)
                ?: throw OriginalNotFoundException(tenant, messageId, resultCode)
        }

    private fun queryFromSnd(ctx: DSLContext, messageId: String, resultCode: String): OriginalMessageRecord?
    private fun queryFromSndLog(ctx: DSLContext, messageId: String, resultCode: String): OriginalMessageRecord?
}
```

**조인 쿼리 — SND 기준** (설계서 §3.3):
```
-- channel_type 차원은 Kafka 이벤트 channelCode 직접 주입이라 SELECT 에서 SVC_KND_CD 제외
SELECT
    t.MB_ID, t.ORG_SVC_KND_CD,
    g.REG_DTT, g.API_INSTC_ID
FROM TNT_INTG_MSG_SND t
JOIN TMG_MSG_TGUS tg ON t.message_id = tg.message_id
JOIN TMG_MSG_GRP g ON t.MSG_GRP_NO = g.MSG_GRP_NO
WHERE t.message_id = ?
  AND t.SND_RST_CD = ?
```

**조인 쿼리 — SND_LOG 기준** (재발송 누적 대비 최신 이력만):
```
SELECT
    t.MB_ID, t.ORG_SVC_KND_CD,
    g.REG_DTT, g.API_INSTC_ID
FROM TNT_INTG_MSG_SND_LOG t
JOIN TMG_MSG_TGUS tg ON t.message_id = tg.message_id
JOIN TMG_MSG_GRP g ON t.MSG_GRP_NO = g.MSG_GRP_NO
WHERE t.message_id = ?
  AND t.SND_RST_CD = ?
ORDER BY t.REG_DTT DESC
LIMIT 1
```

**jOOQ 구현 원칙**:
- jOOQ codegen artifact 의 **`com.example.database.primary.Tables.*`** 상수 사용 (공통 G8)
- 문자열 SQL / `DSL.table("...")` 금지 (공통 G1)
- SND 쿼리는 `fetchAny()` — `(message_id, SND_RST_CD)` 가 시도 유일성 보장하지만 방어적으로 `fetchAny` 사용 (다건 발생 시 예외 대신 임의 1건)
- SND_LOG 쿼리는 `limit(1).fetchOne()` — 명시적 1건
- null 시 `?:` 로 fallback
- `into(OriginalMessageRecord::class.java)` 자동 매핑 사용 가능. 필드명 일치 확인 필요시 수동 매핑 폴백

### 2.4. `OriginalNotFoundException.kt`

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/pipeline/exceptions/OriginalNotFoundException.kt`

```kotlin
class OriginalNotFoundException(
    val tenant: String,
    val messageId: String,
    val resultCode: String,
) : RuntimeException(
    "Original message not found: tenant=$tenant, messageId=$messageId, resultCode=$resultCode"
)
```

---

## 3. TDD 순서

### 3.0. 선행 작업 — AbstractIntegrationTest 확장 (wtth 묶음 4 반영)

**위치**: `stats-consumer/src/test/kotlin/com/example/stats/consumer/AbstractIntegrationTest.kt`

현재 `initCoupangDatabases()` 는 `CREATE DATABASE IF NOT EXISTS tenant-a/tenant-b` + `GRANT` 만 수행. Lookup 3테이블 DDL 이 외부 테넌트 DB 에 **없으므로** 2C RED 4 의 INSERT 가 실패한다. 다음과 같이 확장:

```kotlin
// 상수로 Lookup DDL 분리 (schema.sql 의 Lookup 섹션을 Kotlin 상수로 임포트)
private val COUPANG_LOOKUP_DDL: String = javaClass
    .getResource("/secondary-lookup-ddl.sql")!!
    .readText()

private fun initCoupangDatabases(conn: Connection) {
    listOf("tenant-a", "tenant-b").forEach { db ->
        conn.createStatement().use { stmt ->
            stmt.execute("CREATE DATABASE IF NOT EXISTS $db")
            stmt.execute("USE $db")
            COUPANG_LOOKUP_DDL.split(";")
                .map { it.trim() }
                .filter { it.isNotEmpty() }
                .forEach { stmt.execute(it) }
        }
    }
}
```

**신규 리소스**: `stats-consumer/src/test/resources/secondary-lookup-ddl.sql` — `schema.sql` 의 Lookup 4 테이블 (`TMG_MSG_GRP`, `TMG_MSG_TGUS`, `TNT_INTG_MSG_SND`, `TNT_INTG_MSG_SND_LOG`) CREATE TABLE 구문 복제. RDR-2026-04-16 P3-① 결정 (init-schemas.sql 재생성 금지) 을 준수하는 리소스 분리 방식 — Kotlin 코드가 classpath 리소스로 읽어 실행.

### RED 1: SND 조회 성공 (본발송 시도, 본사 경로)
```
준비: primary DB 에 TMG_MSG_GRP 1행 + TMG_MSG_TGUS 1행 + TNT_INTG_MSG_SND 1행 삽입
     SND 행: message_id="msg-001", SVC_KND_CD="TKA", ORG_SVC_KND_CD=null, SND_RST_CD="0000"
실행: lookup("example-corp", "msg-001", "0000")
검증: OriginalMessageRecord(memberId, originalChannelCode=null, registeredAt, apiInstanceId)
     4개 필드 예상 값 일치 (channelCode 는 이벤트에서 직접 주입되므로 lookup 반환 타입에 없음)
```

### RED 2: SND 없고 SND_LOG 있음 → fallback 성공
```
준비: SND 비움, SND_LOG 에 1행 (message_id="msg-002", SND_RST_CD="9001", REG_DTT=2026-04-17T10:00)
실행: lookup("example-corp", "msg-002", "9001")
검증: OriginalMessageRecord 정상 반환 (SND_LOG 기준)
```

### RED 3: 양쪽 모두 없음 → 예외
```
준비: primary DB 비움
실행: lookup("example-corp", "msg-missing", "0000")
검증: OriginalNotFoundException(tenant="example-corp", messageId="msg-missing", resultCode="0000")
```

### RED 4: 외부 tenant-b 테넌트 경로 (multi-DB 검증, §3.0 선행 의존)
```
준비: tenant-b DB 에 Lookup 3테이블 각 1행 삽입 (tenant-a DB 는 비움)
실행: lookup("tenant-b", "msg-tenant-b-001", "0000")
검증: OriginalMessageRecord 정상 반환 (TenantContext.use → SchemaAwareDataSource → tenant-b DB 접근 경로 검증)
```

### RED 5: 동일 messageId + 다른 SND_RST_CD 2행 → resultCode 로 정확 매칭 (wtth 묶음 6 반영)
```
준비: SND 에 동일 messageId="msg-sub-001" 2행:
  행 1: SVC_KND_CD="TKA", ORG_SVC_KND_CD=null, SND_RST_CD="9001" (알림톡 실패)
  행 2: SVC_KND_CD="SMS", ORG_SVC_KND_CD="TKA", SND_RST_CD="0000" (SMS 대체 성공)
실행 1: lookup("example-corp", "msg-sub-001", "9001")
검증 1: originalChannelCode=null (본발송 시도)
실행 2: lookup("example-corp", "msg-sub-001", "0000")
검증 2: originalChannelCode="TKA" (대체발송 시도)

참고: SVC_KND_CD 는 반환 타입에 없으므로 channelCode 검증 항목 없음. 시도 구분은 originalChannelCode 값으로 검증.
```

### RED 6: SND_LOG 에 동일 messageId 다건 누적 → 최신 REG_DTT 1건만 반환
```
준비: SND_LOG 에 동일 (message_id="msg-log-001", SND_RST_CD="0000") 2행:
  행 1: REG_DTT=2026-04-10T10:00
  행 2: REG_DTT=2026-04-15T10:00
실행: lookup("example-corp", "msg-log-001", "0000")
검증: registeredAt=2026-04-15T10:00 (최신 행)
```

### GREEN
- `OriginalMessageRecord` data class (4 필드 — channelCode 제거됨, RDR-2026-04-17-kafka-payload-passthrough-discovery)
- `OriginalMessageLookup` interface + `OriginalMessageLookupImpl` (jOOQ 구현, resultCode 필터)
- `OriginalNotFoundException` (tenant, messageId, resultCode)
- §3.0 AbstractIntegrationTest 확장 + `secondary-lookup-ddl.sql` 리소스
- 위 6 RED 통과

### REFACTOR
- SND/SND_LOG 쿼리의 공통 SELECT 절은 private 헬퍼로 추출 (DRY)
- 쿼리 로깅 (debug 레벨) 추가
- 예외 메시지 포맷 일관화

---

## 4. 제약 조건

| # | 제약 |
|---|---|
| L1 | 모든 쿼리는 `DslContextFactory.forTenant(tenant)` 경유 → `TenantAssertingListener` 필수 적용 (공통 G2) |
| L2 | jOOQ codegen 상수는 `com.example.database.primary.Tables.*` 경로 사용 (공통 G8). 문자열 SQL / `DSL.table("...")` 금지 (공통 G1) |
| L3 | `lookup()` 호출자가 `TenantContext.use(tenant)` 를 걸어줄 것으로 기대하지 말고, **이 메서드 내부에서 자체적으로 `TenantContext.use` 블록 설정** (호출자 단순화) |
| L4 | `registeredAt` 는 `TMG_MSG_GRP.REG_DTT` 기준 (설계서 §3.3 SELECT 절). `TNT_INTG_MSG_SND.REG_DTT` 사용 금지 |
| L5 | `OriginalNotFoundException` 은 RuntimeException 상속 (언체크 예외) — Kotlin 함수 시그니처에 `throws` 선언 불필요 |
| L6 | composite PK `(message_id, SVC_KND_CD)` 로 인해 동일 messageId 다행 가능. `(message_id, SND_RST_CD)` 조합이 시도 단위 유일성을 보장 (T-3 발행 계약). SND_LOG 는 재발송 누적 대비 `ORDER BY REG_DTT DESC LIMIT 1` 방어 필수 |
| L7 | SND 쿼리는 `fetchAny()` 사용 (유일성 전제지만 방어적). SND_LOG 쿼리는 `limit(1).fetchOne()` 사용 |
| L8 | 공통 제약 G1, G2, G6, G8, G9 적용 |

---

## 5. 성공 기준

- ✅ §3.0 선행 작업: `secondary-lookup-ddl.sql` 리소스 생성 + `AbstractIntegrationTest.initCoupangDatabases` 확장
- ✅ RED 1 → GREEN: 본사 본발송 SND 경로 성공
- ✅ RED 2 → GREEN: 본사 SND_LOG fallback 성공
- ✅ RED 3 → GREEN: 양쪽 없음 → 예외 (resultCode 포함)
- ✅ RED 4 → GREEN: tenant-b 테넌트 → multi-DB 경로 성공
- ✅ RED 5 → GREEN: 동일 messageId 본발송+대체 2행 → resultCode 로 각각 정확 매칭
- ✅ RED 6 → GREEN: SND_LOG 다건 누적 → 최신 REG_DTT 1건 반환
- ✅ Phase 1 + USE 전환 기존 테스트 회귀 통과
- ✅ `DslContextFactory` + `TenantAssertingListener` 정상 작동 (기존 구조 변경 없음)

---

## 6. 테스트 파일 위치

`stats-consumer/src/test/kotlin/com/example/stats/consumer/lookup/OriginalMessageLookupIntegrationTest.kt`

- `AbstractIntegrationTest` 상속 (§3.0 확장 완료 상태, TestContainers MySQL multi-DB + Redis + Kafka)
- 각 테스트 `@BeforeEach` 로 원본 테이블 데이터 클린업 + 삽입
- init-schemas.sql 재생성 금지 (RDR-2026-04-16 P3-①) — Kotlin 헬퍼 + classpath 리소스 (`secondary-lookup-ddl.sql`) 방식만 사용

---

## 7. 참조

- 설계서: `01-stats-consumer-design.md` §3 (전체), §3.3 (조인 쿼리 + resultCode 필터), §3.4 (결과 타입, SUBTXT 필드 제거)
- wtth 1라운드 RDR: `example-stats-billing/docs/decisions/reviews/RDR-2026-04-17-phase2-directive-review.md` (묶음 4, 6+, 8, 12 반영)
- USE 전환 RDR: `example-stats-billing/docs/decisions/reviews/RDR-2026-04-16-schema-aware-datasource.md` (init-schemas.sql 재생성 금지 결정)
- schema.sql: `stats-consumer/src/test/resources/schema.sql` (TMG_MSG_GRP, TMG_MSG_TGUS, TNT_INTG_MSG_SND, TNT_INTG_MSG_SND_LOG)
- jOOQ artifact: `com.example.database:jooq-{env}-java21:1.20260416.1` (패키지: `com.example.database.primary.*`)
- DslContextFactory: `config/JooqConfig.kt` (Phase 2E L0 에서 ExceptionTranslator 배선 추가 예정)
- TenantContext.use: `shackled-shared-tenant-context-use-block.md` (선행 지시서)
- 개요: `shackled-phase2-00-overview.md`
