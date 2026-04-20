# shackled Phase 2F 지시서: 배치 오케스트레이션 + 실패 계층 + DLT

- **체급**: L
- **산출물 유형**: code
- **코드 대상**: backend (Spring Boot 3 Kotlin + Spring Kafka)
- **TDD**: Red → Green → Refactor
- **구현 위치**: `~/Work/example/example-stats-billing/stats-consumer/`
- **개요**: `shackled-phase2-00-overview.md`
- **의존**: 2A, 2B, 2C, 2D, 2E (전체 선행)
- **선행 필수**: `shackled-shared-tenant-context-use-block.md`
- **참조 RDR**: `example-stats-billing/docs/decisions/reviews/RDR-2026-04-17-stats-consumer-batch-processing-redesign.md`

---

## 1. 목적 + 계약

### 1.1. Consumer 계약 (설계서 §9 인용)

> **실시간 통계는 근사치다.** 대사가 불일치를 탐지하고, 사람이 로그 테이블 (`TMG_MSG_TGUS` / `MM_MSG`) 기준으로 stats 를 수정하며, 롤업이 멱등 재실행으로 상위 테이블까지 동기화한다. Consumer 는 **성능 + 포이즌 격리 + 관측가능성** 을 책임진다.

Phase 2F 는 이 계약을 **오케스트레이션 레이어** 에서 구현한다:
- **성능**: Kafka 배치 listener + groupBy 사전 집계 + UPSERT 성공 후 Redis 마킹 (RDR D-1~D-3)
- **포이즌 격리**: record 단위 DLT vs 배치 단위 DLT 분기 (설계서 §6A)
- **관측가능성**: MDC `batchId` 주입 + 구조화 로그 + Grafana 5 메트릭 (설계서 §8A)

### 1.2. 2E (atomic unit) vs 2F (오케스트레이션) 경계

| 항목 | 2E 책임 | 2F 책임 (본 지시서) |
|---|---|---|
| Kafka listener (`@KafkaListener(batch=true)`) | ❌ | ✅ |
| parse / validate (record DLT) | ❌ | ✅ |
| `DedupService.filterNew` / `markAll` 호출 | ❌ | ✅ |
| `OriginalMessageLookup.lookup` 호출 + 실패 시 record DLT | ❌ | ✅ |
| `DimensionMapper.map` / `mapExt` 호출 | ❌ | ✅ |
| `groupingBy().eachCount()` 집계 | ❌ | ✅ |
| `TenantContext.use("example-corp")` 로 감싸 `UpsertService.batchUpsert` 진입 | ❌ | ✅ |
| `batchUpsert` 실행 내부 (트랜잭션, jOOQ, UPSERT SQL) | ✅ | — (소비만) |
| `DefaultErrorHandler` 재시도 + 배치 DLT | ❌ | ✅ |
| DLT publisher + `x-error-reason` 헤더 | ❌ | ✅ |
| MDC / Micrometer timer / Grafana 메트릭 | ❌ | ✅ |

2F 는 **파이프라인 조립자** 이다. Phase 2A~2E 의 순수 함수/서비스를 배치 단위로 엮고, 실패 계층 (record DLT vs 배치 DLT vs 배치 재시도) 을 라우팅한다.

### 1.3. 기존 2F (단건 초안) 폐기 범위

이전 2F 초안은 단건 `StatsPipelineImpl.process(event)` + `DedupService.tryAcquire(tenant, messageId, channelCode)` 였다. RDR D-1~D-3 에 따라 **파이프라인 진입점이 배치 listener 로 이전**:
- `StatsPipelineImpl.process(event)` → `StatsBatchPipeline.processBatch(records)` 로 책임 이동
- `DedupService.tryAcquire(...)` → `filterNew(events)` + `markAll(messageIds)` 2분할
- `StatsUpsertService.upsert(dim)` + `@Retryable` → `UpsertService.batchUpsert(aggregated)` + Kafka `DefaultErrorHandler` (2E 완료)

존치 자산 (사고 모델 재활용):
- `TenantRegistry` (본사/외부 테넌트 판정, `__ext__` 는 별도 분기)
- `UnknownTenantException` / `DltErrorReason` 상수 + `from(Throwable)` 매핑
- KafkaConfig `addNotRetryableExceptions` + `addHeadersFunction` 아이디어 (배치 레벨로 확장)

`StatsPipelineStub` 완전 제거는 본 단계에서 수행 (이전 초안과 동일).

---

## 2. 산출물

### 2.1. `StatsBatchPipeline.kt` (interface)

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/pipeline/StatsBatchPipeline.kt`

```kotlin
interface StatsBatchPipeline {
    /**
     * 한 Kafka poll 의 배치를 end-to-end 처리한다.
     *
     * 내부 단계:
     *   1) parse + validate (record 단위 격리; 실패 → record DLT)
     *   2) dedupService.filterNew(events) (배치 Redis 1~2 RTT)
     *   3) lookup (tenant 별 TenantContext.use; 실패 → record DLT)
     *   4) map / mapExt (record 단위 격리; BmsOptionalFieldNull → record DLT)
     *   5) groupingBy().eachCount() 집계
     *   6) TenantContext.use("example-corp") { batchUpsert(aggregated) }
     *   7) dedupService.markAll(newEvents)
     *
     * 예외 계약:
     *   - 1~4 단계: 해당 record 만 DLT publish 후 나머지 진행 (포이즌 격리)
     *   - 5~6 단계: 예외 상위 전파 → DefaultErrorHandler 배치 재시도 or 배치 전체 DLT
     *   - 7 실패 (Redis 장애): **silent skip + 경고 로그**. 재처리 시 count 이중 집계 가능
     *     → T-2 대사 (§4.3) 가 탐지하고 사람이 stats 수동 보정 (§9 Consumer 계약)
     */
    fun processBatch(records: List<ConsumerRecord<String, String>>)
}
```

### 2.2. `StatsBatchPipelineImpl.kt`

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/pipeline/StatsBatchPipelineImpl.kt`

```kotlin
import com.example.canonical.stats.StatSendResultEvent
import com.example.stats.consumer.code.TenantCode
import com.example.stats.consumer.dedup.DedupService
import com.example.stats.consumer.dlt.DltErrorReason
import com.example.stats.consumer.dlt.DltPublisher
import com.example.stats.consumer.lookup.OriginalMessageLookup
import com.example.stats.consumer.mapper.DimensionMapper
import com.example.stats.consumer.mapper.StatsDimensions
import com.example.stats.consumer.pipeline.exceptions.*
import com.example.stats.consumer.upsert.UpsertService
import com.example.tenant.routing.TenantContext
import org.apache.kafka.clients.consumer.ConsumerRecord
import org.slf4j.LoggerFactory
import org.slf4j.MDC
import org.springframework.stereotype.Service
import java.util.UUID

@Service
@Primary
class StatsBatchPipelineImpl(
    private val objectMapper: ObjectMapper,
    private val validator: Validator,                   // Jakarta Bean Validation
    private val dedupService: DedupService,
    private val bmsValidator: ExtEventValidator,        // Phase 2A
    private val lookup: OriginalMessageLookup,          // Phase 2C
    private val mapper: DimensionMapper,                // Phase 2D
    private val upsertService: UpsertService,           // Phase 2E
    private val tenantRegistry: TenantRegistry,         // 존치
    private val dltPublisher: DltPublisher,
) : StatsBatchPipeline {

    private val log = LoggerFactory.getLogger(StatsBatchPipelineImpl::class.java)

    override fun processBatch(records: List<ConsumerRecord<String, String>>) {
        val batchId = UUID.randomUUID().toString()
        MDC.put("batchId", batchId)
        try {
            doProcessBatch(records, batchId)
        } finally {
            MDC.remove("batchId")
        }
    }

    private fun doProcessBatch(records: List<ConsumerRecord<String, String>>, batchId: String) {
        // 1) parse + validate (record 단위 격리)
        val parsed: List<StatSendResultEvent> = records.mapNotNull { record ->
            parseAndValidate(record, batchId)
        }
        if (parsed.isEmpty()) return

        // 2) dedup filter (배치)
        val newEvents: List<StatSendResultEvent> = dedupService.filterNew(parsed)
        if (newEvents.isEmpty()) return

        // 3 + 4) lookup + map (record 단위 격리)
        val dimensions: List<StatsDimensions> = newEvents.mapNotNull { event ->
            mapToDimension(event, batchId)
        }
        if (dimensions.isEmpty()) {
            dedupService.markAll(newEvents.map { it.messageId })
            return
        }

        // 5) groupingBy 집계 (클라이언트 측 사전 합산)
        val aggregated: Map<StatsDimensions, Long> =
            dimensions.groupingBy { it }.eachCount().mapValues { it.value.toLong() }

        // 6) upsert (TenantContext.use("example-corp") 감싸 진입; 2E 계약)
        //    이 단계 예외는 상위 Kafka ErrorHandler 로 전파 → 배치 재시도 or 배치 DLT
        TenantContext.use(TenantCode.PRIMARY.code()) {
            upsertService.batchUpsert(aggregated)
        }

        // 7) dedup 마킹 (UPSERT 성공 후, RDR D-3)
        markWithFallback(newEvents)
    }

    // --- 1) parse + validate ---------------------------------------------------
    private fun parseAndValidate(
        record: ConsumerRecord<String, String>,
        batchId: String,
    ): StatSendResultEvent? =
        try {
            val event = objectMapper.readValue(record.value(), StatSendResultEvent::class.java)
            val violations = validator.validate(event)
            if (violations.isNotEmpty()) {
                dltPublisher.publish(record, batchId, DltErrorReason.PARSE_FAIL,
                    RuntimeException("validation violations=${violations.size}"))
                null
            } else {
                event
            }
        } catch (e: Exception) {
            dltPublisher.publish(record, batchId, DltErrorReason.PARSE_FAIL, e)
            null
        }

    // --- 3 + 4) lookup + map ---------------------------------------------------
    private fun mapToDimension(
        event: StatSendResultEvent,
        batchId: String,
    ): StatsDimensions? =
        try {
            when {
                event.tenant == StatSendResultEvent.EXT_TENANT -> {
                    bmsValidator.validate(event)   // ExtOptionalFieldNullException 가능
                    mapper.mapExt(event)
                }
                tenantRegistry.isKnown(event.tenant) -> {
                    // lookup 은 원본 DB 라우팅용 — tenant 별 TenantContext.use 필요 (2C L3 내부 처리)
                    val record = lookup.lookup(event.tenant, event.messageId, event.resultCode)
                    mapper.map(event, record)
                }
                else -> throw UnknownTenantException(event.tenant)
            }
        } catch (e: OriginalNotFoundException) {
            dltPublisher.publishEvent(event, batchId, DltErrorReason.ORIGINAL_NOT_FOUND, e)
            null
        } catch (e: ExtOptionalFieldNullException) {
            dltPublisher.publishEvent(event, batchId, DltErrorReason.EXT_OPTIONAL_FIELD_NULL, e)
            null
        } catch (e: UnknownTenantException) {
            dltPublisher.publishEvent(event, batchId, DltErrorReason.UNKNOWN_TENANT, e)
            null
        }

    // --- 7) dedup 마킹 (Redis 장애 허용) ---------------------------------------
    private fun markWithFallback(events: List<StatSendResultEvent>) {
        try {
            dedupService.markAll(events.map { it.messageId })
        } catch (e: Exception) {
            // §9 Consumer 계약: 실시간 통계는 best-effort. 마킹 실패 시 재처리 후 count 이중 집계
            // 가능성 있으나 T-2 대사 + 사람 보정 + 롤업 재실행 3축으로 복원.
            log.warn("dedup markAll failed — duplicates possible on retry. count={}, stage=markAll reason={}",
                events.size, e.javaClass.simpleName, e)
        }
    }
}
```

**key 주의점**:
- `@Transactional` **부착 금지** — 내부 단계는 Redis/Kafka/외부 DB 혼재이며, `upsertService.batchUpsert` 가 자체 @Transactional 로 DB 원자성 담당 (2E 책임)
- `TenantContext.use(event.tenant)` 는 `lookup.lookup` 내부 (2C L3) 에서 처리되므로 본 서비스는 lookup 호출 감싸지 않음
- `TenantContext.use("example-corp")` 는 upsert 진입점에만 감싸기 (stats 단일 저장소, 2E §1.3)

### 2.3. `StatsSendResultListener.kt` (배치 리스너, 기존 단건 listener 교체)

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/listener/StatsSendResultListener.kt`

```kotlin
@Component
class StatsSendResultListener(
    private val pipeline: StatsBatchPipeline,
) {
    @KafkaListener(
        topics = ["\${stats.topic}"],
        containerFactory = "batchKafkaListenerContainerFactory",
    )
    fun onBatch(records: List<ConsumerRecord<String, String>>, ack: Acknowledgment) {
        try {
            pipeline.processBatch(records)
            ack.acknowledge()
        } catch (e: Exception) {
            // 배치 단위 실패 (5~6 단계) — DefaultErrorHandler 로 위임
            // ack 하지 않음 → poll 재시도 또는 배치 DLT
            throw e
        }
    }
}
```

**기존 단건 listener 는 삭제.** `batchListener = true` 인 새 container factory 를 참조.

### 2.4. `KafkaConfig.kt` 개정 — 배치 listener + ErrorHandler

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/config/KafkaConfig.kt`

```kotlin
@Configuration
class KafkaConfig {

    @Bean("batchKafkaListenerContainerFactory")
    fun batchKafkaListenerContainerFactory(
        consumerFactory: ConsumerFactory<String, String>,
        errorHandler: CommonErrorHandler,
    ): ConcurrentKafkaListenerContainerFactory<String, String> =
        ConcurrentKafkaListenerContainerFactory<String, String>().apply {
            setConsumerFactory(consumerFactory)
            isBatchListener = true                                 // ★ 배치 모드
            containerProperties.ackMode = AckMode.MANUAL           // 배치 처리 후 수동 ack
            setCommonErrorHandler(errorHandler)
        }

    @Bean
    fun errorHandler(
        batchDltPublisher: KafkaTemplate<String, String>,
        dltPublisher: DltPublisher,
    ): DefaultErrorHandler {
        // 배치 전체 실패 시 배치 레코드 전부 DLT 에 개별 발행 (reason 동일)
        val recoverer = ConsumerRecordRecoverer { record, ex ->
            dltPublisher.publishRaw(record, DltErrorReason.from(ex), ex)
        }

        // 배치 재시도 정책: FixedBackOff(1_000L, 2L) — 1초 간격, 최대 2회 재시도 → 총 3회 시도 (~3초)
        val backOff = FixedBackOff(1_000L, 2L)
        return DefaultErrorHandler(recoverer, backOff).apply {
            // 재시도 불가 예외는 즉시 DLT 직행
            addNotRetryableExceptions(
                com.fasterxml.jackson.core.JsonProcessingException::class.java,
                UnknownTenantException::class.java,
                ExtOptionalFieldNullException::class.java,
                OriginalNotFoundException::class.java,
                GroupLookupRaceFailureException::class.java,
            )
        }
    }
}
```

> **재시도 정책 확정 근거** (주인님 확정, 2026-04-17): deadlock / timeout 등 일시 장애는 대부분 수 초 내 회복되는 전제. `max.poll.interval.ms = 5분` (설계서 §8.1) 여유 대비 총 지연 ~3초 는 경합 없음. 대안 (Exponential backoff / 재시도 없음) 은 F-11 (Kafka 파라미터 실측 튜닝, 운영 투입 후 H) 후속 검토 대상.

### 2.5. `DedupService` 시그니처 개정 — 배치 API

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/dedup/DedupService.kt` + `RedisDedupService.kt`

```kotlin
interface DedupService {
    /**
     * 배치 중 신규 이벤트만 반환. Redis pipeline/MSETNX 로 1~2 RTT 처리.
     * 이 시점에는 **마킹하지 않는다** — 마킹은 UPSERT 성공 후 markAll() 로 (RDR D-3).
     */
    fun filterNew(events: List<StatSendResultEvent>): List<StatSendResultEvent>

    /**
     * UPSERT 성공이 확정된 이벤트 집합을 Redis 에 마킹 (TTL 3시간).
     * Redis 장애 시 예외 전파 — 호출자가 경고 로그 후 silent skip (§9 계약).
     */
    fun markAll(messageIds: List<String>)
}
```

**RedisDedupService 구현 힌트**:
```kotlin
override fun filterNew(events: List<StatSendResultEvent>): List<StatSendResultEvent> {
    if (events.isEmpty()) return emptyList()
    val keys = events.map { keyOf(it) }
    // MGET 으로 기존 키 존재 여부 일괄 조회 (1 RTT)
    val existing = redisTemplate.opsForValue().multiGet(keys) ?: return events
    return events.filterIndexed { idx, _ -> existing[idx] == null }
}

override fun markAll(messageIds: List<String>) {
    if (messageIds.isEmpty()) return
    // SETNX + EXPIRE pipeline (or Lua script). TTL 10800s (3시간).
    redisTemplate.executePipelined { conn ->
        messageIds.forEach { msgId ->
            // 실제 키는 tenant+channelCode 도 포함 (§5.2) — 호출자가 StatSendResultEvent 전체를
            // 넘기거나, markAll 인자를 List<Pair<...>> 로 확장할지 GREEN 구현 시 결정
        }
        null
    }
}

private fun keyOf(e: StatSendResultEvent) =
    "preventDuplicateResult:${e.tenant}:${e.messageId}:${e.channelCode}"
```

**설계서 §5.2 키 패턴 유지**: `preventDuplicateResult:{tenant}:{messageId}:{channelCode}`. `markAll(messageIds)` 시그니처가 `List<String>` 인지 `List<StatSendResultEvent>` 인지는 GREEN 구현 선택 — 키 재구성 편의성 기준으로 결정. 본 지시서는 interface 에서 `List<String>` 로 제시했으나 GREEN 시 재검토 가능.

### 2.6. `DltPublisher.kt` (신규)

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/dlt/DltPublisher.kt`

```kotlin
/**
 * DLT 메시지 발행자. 설계서 §6A.2 스키마 준수:
 *   tenant + messageId + batchId + reason + originalPayload + failedAt + stackTrace?
 *
 * 메시지 형식: JSON 페이로드 + Kafka 헤더 `x-error-reason`.
 */
@Component
class DltPublisher(
    @Value("\${stats.dlt-topic}") private val dltTopic: String,
    private val kafkaTemplate: KafkaTemplate<String, String>,
    private val objectMapper: ObjectMapper,
) {
    /** Kafka record 단위 DLT (parse 단계 실패). */
    fun publish(record: ConsumerRecord<String, String>, batchId: String, reason: String, cause: Throwable)

    /** StatSendResultEvent 단위 DLT (lookup / map 단계 실패). */
    fun publishEvent(event: StatSendResultEvent, batchId: String, reason: String, cause: Throwable)

    /** DefaultErrorHandler 의 Recoverer 에서 호출 (배치 단위 실패). */
    fun publishRaw(record: ConsumerRecord<*, *>, reason: String, cause: Throwable)
}
```

DLT 페이로드 JSON 스키마:
```json
{
  "tenant": "example-corp",
  "messageId": "msg-xyz",
  "batchId": "0e9f...-uuid",
  "reason": "ORIGINAL_NOT_FOUND",
  "originalPayload": "{...원본 Kafka value...}",
  "failedAt": "2026-04-17T13:42:15+09:00",
  "stackTrace": "...optional..."
}
```

Kafka 헤더: `x-error-reason`: reason 문자열. 기존 Spring DLT 표준 헤더 (`kafka_dlt-*`, `__typeid__`) 와 병존.

### 2.7. `TenantRegistry.kt` (존치)

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/pipeline/TenantRegistry.kt`

```kotlin
/**
 * 본사 경로 tenant 판정기.
 *
 * ⚠️ EXT_TENANT("__ext__") 는 known set 에 포함되지 않는다.
 *    EXT 분기는 StatsBatchPipelineImpl.mapToDimension 의 when 최상단에서 별도 처리.
 */
@Component
class TenantRegistry {
    private val known: Set<String> = TenantCode.entries.map { it.code() }.toSet()
    fun isKnown(tenant: String): Boolean = tenant in known
}
```

### 2.8. `UnknownTenantException.kt` (존치)

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/pipeline/exceptions/UnknownTenantException.kt`

```kotlin
class UnknownTenantException(
    val tenant: String,
) : RuntimeException("Unknown tenant: $tenant")
```

### 2.9. `DltErrorReason.kt` (배치 reason 추가)

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/dlt/DltErrorReason.kt`

```kotlin
object DltErrorReason {
    // record 단위 격리 (설계서 §6A.1)
    const val PARSE_FAIL = "PARSE_FAIL"
    const val ORIGINAL_NOT_FOUND = "ORIGINAL_NOT_FOUND"
    const val UNKNOWN_TENANT = "UNKNOWN_TENANT"
    const val EXT_OPTIONAL_FIELD_NULL = "EXT_OPTIONAL_FIELD_NULL"

    // 배치 단위 이분법
    const val LOGIC_ERROR = "LOGIC_ERROR"
    const val UPSERT_FAIL = "UPSERT_FAIL"
    const val GROUP_LOOKUP_RACE_FAILURE = "GROUP_LOOKUP_RACE_FAILURE"

    /**
     * 예외 타입 → reason 문자열 매핑. cause 체인 순회 (Spring Kafka 래핑 대응).
     */
    fun from(e: Throwable): String {
        var cur: Throwable? = e
        while (cur != null) {
            when (cur) {
                is OriginalNotFoundException -> return ORIGINAL_NOT_FOUND
                is UnknownTenantException -> return UNKNOWN_TENANT
                is ExtOptionalFieldNullException -> return EXT_OPTIONAL_FIELD_NULL
                is GroupLookupRaceFailureException -> return GROUP_LOOKUP_RACE_FAILURE
                is com.fasterxml.jackson.core.JsonProcessingException -> return PARSE_FAIL
            }
            if (cur.cause === cur) break
            cur = cur.cause
        }
        return UPSERT_FAIL
    }
}
```

### 2.10. `StatsPipelineStub.kt` 삭제 (존치)

파일 완전 제거. `StatsBatchPipelineImpl` 이 `@Primary` 이므로 빈 충돌 없음.

단건 interface `StatsPipeline` 도 더 이상 참조되지 않으면 제거. 제거 여부는 `StatsPipeline` 사용처 검색 후 GREEN 시 결정 — 선행 확인 필요.

### 2.11. Kafka 운영/개발 프로파일 분리 (설계서 §8.1)

**위치**: `stats-consumer/src/main/resources/application-prod.yml` / `application-dev.yml` (신규/확장)

**공통** (`application.yml` 유지):
```yaml
stats:
  topic: example-corp.stat.send-result.json
  dlt-topic: example-corp.stat.send-result-dlt.json
  dedup:
    ttl-seconds: 10800
spring:
  kafka:
    consumer:
      enable-auto-commit: false
      auto-offset-reset: latest
      properties:
        max.poll.interval.ms: 300000
        session.timeout.ms: 45000
        heartbeat.interval.ms: 15000
```

**운영** (`application-prod.yml`):
```yaml
spring:
  kafka:
    consumer:
      max-poll-records: 1000
      properties:
        fetch.min.bytes: 65536
        fetch.max.wait.ms: 200
```

**개발** (`application-dev.yml`):
```yaml
spring:
  kafka:
    consumer:
      max-poll-records: 100
      properties:
        fetch.min.bytes: 8192
        fetch.max.wait.ms: 100
```

---

## 3. TDD 순서

### RED 1: 본사 경로 배치 end-to-end 성공
```
준비:
  - primary DB: Lookup 3 테이블에 msg-1 / msg-2 / msg-3 (각 SND_RST_CD 설정)
  - Redis / stats 테이블 비어있음
실행: Kafka 에 3개 이벤트 한 번에 발행 → consumer 한 poll 에 3건 수신
검증:
  - stats_send_group 3행 (또는 같은 (tenant, send_date, memberId, channelType) 이면 1행)
  - stats_send_detail send_count 합 = 3
  - DLT 비어있음
  - ack 1회 (배치 단위)
```

### RED 2: EXT 경로 배치 — lookup 스킵 + upsert 직접
```
실행: 3개 EXT 이벤트 (tenant=__ext__, optional 6 채워짐) 발행
검증:
  - stats 테이블 3행 (또는 동일 차원이면 1행+count=3)
  - 원본 테이블 쿼리 실행 0회 (lookup 스킵)
  - DLT 비어있음
```

### RED 3: 배치 내 parse 실패 1건 + 나머지 정상
```
실행: 잘못된 JSON 1건 + 정상 이벤트 2건 발행
검증:
  - DLT 1건 + `x-error-reason: PARSE_FAIL`
  - stats_send_detail 2행 (나머지 정상 반영)
  - 배치 진행 (1건 때문에 전체 실패 X)
```

### RED 4: 배치 내 OriginalNotFound 1건 + 나머지 정상
```
준비: msg-1 / msg-3 만 원본 존재. msg-2 는 SND/SND_LOG 양쪽 없음
실행: 3개 이벤트 발행
검증:
  - DLT 1건 + `x-error-reason: ORIGINAL_NOT_FOUND` + messageId=msg-2
  - stats_send_detail 2행 (msg-1, msg-3 정상 반영)
```

### RED 5: batchUpsert 실패 → 재시도 후 성공
```
준비: jOOQ ExecuteListener mock 으로 첫 시도만 CannotAcquireLockException 던지게 설정
실행: 정상 이벤트 2건 발행
검증:
  - StatsBatchPipelineImpl.processBatch 가 2회 호출됨 (첫 실패 → 재시도)
  - 최종 stats 정상 반영
  - DLT 비어있음
  - FixedBackOff(1s) 준수 (최소 1초 지연 관측)
```

### RED 6: batchUpsert 재시도 초과 → 배치 전체 DLT + ack
```
준비: 모든 시도에서 CannotAcquireLockException 던지게 mock 설정
실행: 정상 이벤트 2건 발행
검증:
  - processBatch 3회 호출 (재시도 2회 포함)
  - 최종 2 record 모두 DLT + `x-error-reason: UPSERT_FAIL`
  - stats 테이블 0행 (모두 rollback)
  - offset 커밋됨 (다음 poll 진행)
```

### RED 7: 같은 배치 내 messageId 중복 → filterNew 1건만 통과
```
실행: 동일 (tenant=example-corp, messageId=msg-dup, channelCode=TKA) 이벤트 2건 발행 (같은 poll)
검증:
  - stats_send_detail send_count=1 (2 아님)
  - dedup 첫 건만 통과 / 두번째는 skip
  - DLT 비어있음
```

### RED 8: 동일 messageId + 다른 channelCode → filterNew 2건 모두 통과 (축 분리)
```
실행: (msg-sub, channelCode=TKA, resultCode=9001) + (msg-sub, channelCode=SMS, resultCode=0000) 발행
준비: 원본 DB 에 해당 2 행 (본발송 + 대체발송) 존재
검증:
  - 두 이벤트 모두 처리됨
  - stats_send_detail 2행 (original_channel_type 값으로 구분)
  - DLT 비어있음
```

### RED 9: Redis markAll 장애 → silent skip + 경고 로그 (best-effort 계약)
```
준비: Redis 테스트 컨테이너 일시 중단 또는 mock 예외
실행: 정상 이벤트 1건 → batchUpsert 성공 → markAll 실패
검증:
  - stats_send_detail 1행 (UPSERT 는 성공)
  - 경고 로그 `dedup markAll failed ...` 기록
  - ack 커밋됨
  - 같은 메시지 재발행 시 dedup 미등록 상태 → **count 2회 집계** (본 테스트에서는 관측만, §9 계약)
  - DLT 비어있음
```

### RED 10: EXT optional null → record DLT + 나머지 진행
```
실행: (tenant=__ext__, sendDate=null) 이벤트 1건 + 정상 EXT 이벤트 1건 발행
검증:
  - DLT 1건 + `x-error-reason: EXT_OPTIONAL_FIELD_NULL`
  - stats 테이블 1행 (정상 EXT 반영)
```

### RED 11: Unknown tenant → record DLT
```
실행: (tenant=unknown-xyz) 이벤트 발행
검증:
  - DLT 1건 + `x-error-reason: UNKNOWN_TENANT`
  - lookup/upsert 쿼리 실행 0회
  - ack 커밋
```

### RED 12: TenantRegistry 계약 단위 테스트 (존치, 기존 RED 8)
```
- isKnown("example-corp") == true
- isKnown("tenant-a") == true / isKnown("tenant-b") == true / isKnown("tenant-c") == true
- isKnown("__ext__") == false
- isKnown("unknown-xyz") == false
```

### GREEN
- `StatsBatchPipeline` + `StatsBatchPipelineImpl` + `StatsSendResultListener` (배치 listener)
- `KafkaConfig` 배치 ContainerFactory + `DefaultErrorHandler` (FixedBackOff + addNotRetryableExceptions)
- `DedupService` 2분할 (`filterNew` + `markAll`)
- `DltPublisher` + 메시지 스키마
- `DltErrorReason` (PARSE_FAIL / LOGIC_ERROR / UPSERT_FAIL 추가)
- `TenantRegistry` / `UnknownTenantException` (존치)
- 구 `StatsPipelineStub` 제거 + 구 단건 `StatsSendResultListener` 삭제
- `application-prod.yml` / `application-dev.yml` 프로파일 분리

### REFACTOR
- `StatsBatchPipelineImpl` 의 단계별 private 메서드 (`parseAndValidate`, `mapToDimension`, `markWithFallback`) 를 다른 클래스로 분리할지 검토 (현재 1 클래스 유지 OK)
- Grafana 메트릭 emit (Micrometer Timer) 지점: `processBatch` 전체 + 단계별 (parse/map/upsert) 타이머 분해 — 설계서 §8A.1 참조
- MDC 필드 `tenant` / `messageId` 도 lookup 성공 시점에 주입 (구조화 로그 §8A.2 계약)
- `DltErrorReason.from` 매핑을 `Map<Class<*>, String>` 으로 리팩토링 가능 (확장성)

---

## 4. 제약 조건

| # | 제약 |
|---|---|
| L1 | `StatsPipelineStub.kt` 및 기존 단건 `StatsSendResultListener` 는 **반드시 삭제**. 주석 처리 금지 |
| L2 | `StatsBatchPipelineImpl` 은 `@Primary` 등록 (단건 구 구현이 남아있을 경우 안전장치) |
| L3 | DLT `x-error-reason` 헤더는 `DltErrorReason` 상수만 사용. 문자열 하드코딩 금지 (공통 G4) |
| L4 | `TenantRegistry` 는 `TenantCode` enum 값 기반. `__ext__` 는 포함 금지. `when` 블록 EXT 최상단 순서 고정 |
| L5 | `UnknownTenantException` 은 lookup 진입 전에 throw. `TenantRoutingDataSource` 기본 폴백 의존 금지 (F-2) |
| L6 | Kafka `ConcurrentKafkaListenerContainerFactory.isBatchListener = true` 설정 필수. `ackMode = MANUAL` 필수 |
| L7 | `DefaultErrorHandler` 의 비재시도 예외 5종 등록 필수 (`JsonProcessingException`, `UnknownTenantException`, `ExtOptionalFieldNullException`, `OriginalNotFoundException`, `GroupLookupRaceFailureException`). 이 예외들은 즉시 DLT 직행 |
| L8 | `DltErrorReason.from` 은 cause 체인 순회 필수 (Spring Kafka `ListenerExecutionFailedException` 래퍼 대응) |
| L9 | `StatsBatchPipelineImpl.processBatch` 에 `@Transactional` 부착 금지 — DB 트랜잭션은 2E `batchUpsert` 내부로 한정 |
| L10 | `TenantContext.use("example-corp")` 는 `upsertService.batchUpsert` 호출 한 줄만 감싼다. lookup 호출은 2C 내부 (`TenantContext.use(event.tenant)`) 가 처리 |
| L11 | `markAll` 호출은 **반드시 `batchUpsert` 성공 후** (RDR D-3). 순서 뒤집기 금지 |
| L12 | `markAll` 실패는 silent skip + 경고 로그. 예외 전파 금지 (ack 는 계속 진행되어야 함, §9 best-effort 계약) |
| L13 | 공통 제약 G1~G9 적용 |

---

## 5. 성공 기준

- ✅ RED 1~12 → GREEN (12/12)
- ✅ `StatsPipelineStub.kt` 삭제 + 기존 단건 listener 삭제 + `StatsBatchPipelineImpl` 이 Spring 기본 빈
- ✅ `DedupService` 배치 API 전환 + 단건 `tryAcquire` 제거
- ✅ DLT 메시지에 §6A.2 스키마 (`tenant + messageId + batchId + reason + originalPayload + failedAt`) + `x-error-reason` 헤더
- ✅ 재시도 불가 예외 5종 발생 시 `processBatch` 1회만 호출 (배치 내 record 단위 격리 덕분)
- ✅ batchUpsert 예외 시 FixedBackOff 로 재시도 → 초과 시 배치 전체 DLT
- ✅ Phase 2A~2E 회귀 테스트 전체 통과
- ✅ Phase 1 기존 테스트 회귀 통과 (단건 listener 교체 감안)
- ✅ `application-{prod,dev}.yml` 프로파일 분리 적용
- ✅ MDC `batchId` 가 에러 로그 전 구간에 주입됨

---

## 6. 테스트 파일 위치

- `stats-consumer/src/test/kotlin/com/example/stats/consumer/pipeline/StatsBatchPipelineIntegrationTest.kt` (Kafka TC + Redis TC + MySQL TC — RED 1~11)
- `stats-consumer/src/test/kotlin/com/example/stats/consumer/pipeline/TenantRegistryTest.kt` (단위 — RED 12)
- `stats-consumer/src/test/kotlin/com/example/stats/consumer/dlt/DltPublisherTest.kt` (메시지 스키마 + 헤더 검증)
- `stats-consumer/src/test/kotlin/com/example/stats/consumer/dedup/BatchDedupServiceTest.kt` (filterNew/markAll 단위 + 통합)
- 기존 `DedupSmokeTest` / `DltRoutingTest` 는 배치 API 에 맞춰 전환

---

## 7. Canonical-model 영향 (변경 없음)

`StatsDimensions` 는 Phase 2D (`105acc9`) 산출물 그대로 재사용 — **9차원 data class 변경 없음** (설계서 §6.4 / §7 확정). 배치 오케스트레이션은 `Map<StatsDimensions, Long>` 형태로 `UpsertService.batchUpsert` 에 전달할 뿐, 데이터 모델 자체는 불변.

`StatSendResultEvent` 도 Phase 2D 에서 `channelCode` 기본 6필드 승격 완료 (`4ef4db4`). 본 Phase 2F 에서 추가 필드 개정 없음.

---

## 8. 관측가능성 배선 (설계서 §8A 계약)

### 8.1. MDC 주입 지점

| 단계 | 필드 | 값 |
|---|---|---|
| `processBatch` 진입 | `batchId` | `UUID.randomUUID().toString()` |
| `mapToDimension` 진입 | `tenant`, `messageId` | event 필드 (MDC 로컬 스코프) |
| `parseAndValidate` 실패 | `reason` | `PARSE_FAIL` |
| `batchUpsert` 실패 | `stage` | `upsert` |

### 8.2. Grafana 메트릭 emit (Micrometer)

설계서 §8A.1 의 5 메트릭:
- `consumer.records-lag-max` / `consumer.records-consumed-rate` — Kafka JMX (자동)
- 평균 배치 크기 — `meterRegistry.summary("stats.consumer.batch.size")` 에 `records.size` 기록
- `onBatch` latency — `Timer.record { processBatch(...) }`
- DLT publish rate — `Counter.increment()` with `reason` tag

Micrometer timer/counter 등록은 GREEN 단계에서 추가 (필수). F-12 Grafana 대시보드 신설과 연동.

### 8.3. 구조화 로그 필드

모든 `log.info` / `log.warn` / `log.error` 는 설계서 §8A.2 의 구조화 필드 포함:
- `tenant` / `messageId` / `batchId` / `reason` / `stage` / `attemptCount?` / `stackTrace`

MDC 에 batchId 가 있으므로 로그 패턴에 `%X{batchId}` 포함하면 자동 주입. `tenant` / `messageId` 는 record 단위 DLT 로그 시 명시 바인딩.

---

## 9. 참조

- 설계서: `01-stats-consumer-design.md`
  - §9 (Consumer 계약, 최우선 박스)
  - §1.1 (배치 파이프라인 8단계 흐름)
  - §5.3 (DedupService 배치 API + markAll 순서)
  - §6.5 (batchUpsert 계약 — 2E 책임)
  - §6A (배치 실패 계층 분리, DLT 메시지 스키마)
  - §7.3 (에러 분류표 — reason 카탈로그)
  - §8.1 (Kafka 운영/개발 프로파일)
  - §8A (관측가능성)
- RDR: `RDR-2026-04-17-stats-consumer-batch-processing-redesign.md` (D-1 ~ D-5)
- RDR (선행): `RDR-2026-04-17-kafka-payload-passthrough-discovery.md` (channelCode 승격, dedup 키 축)
- Phase 2A~2E 지시서 (전체 의존)
- Phase 1 지시서 §4.3, §4.4 (기존 Listener + DLT 배선 — 교체 대상)
- T-2 설계서: `50-pipeline/T2-stats-batch/01-stats-batch-design.md` §4.3 (대사 운영, §9 best-effort 계약의 복원 축)
- `TenantCode`: `code/TenantCode.kt`
- `TenantContext.use`: `shackled-shared-tenant-context-use-block.md`
- wtth 1라운드 RDR: `RDR-2026-04-17-phase2-directive-review.md` (묶음 2, 8, 9a, 11 재활용)
- 개요: `shackled-phase2-00-overview.md`
