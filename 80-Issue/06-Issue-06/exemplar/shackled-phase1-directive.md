# shackled Phase 1 지시서: stats-consumer 골격

- **체급**: L
- **산출물 유형**: code
- **코드 대상**: backend (Spring Boot 3 Kotlin)
- **TDD**: 없음 (골격 단계). Phase 2 에서 TDD 진행.
- **구현 위치**: `~/Work/example/example-stats-billing/stats-consumer/`
- **상위 설계서**: `T1-stats-consumer/01-stats-consumer-design.md` (480+ lines, 전체 읽지 말고 본 지시서 기준으로 작업)

---

## 1. 목적

T-1 stats-consumer 의 **인프라 골격**을 구축한다. 비즈니스 로직(Lookup, DimensionMapper, Upsert)은 stub 으로 두고, 메시지 수신 → dedup → stub 처리 → DLT 라우팅 경로만 e2e 동작하게 한다.

Phase 2 에서 stub 을 실제 비즈니스 로직으로 채울 예정이므로, **확장 포인트를 깔끔하게 열어둘 것**.

---

## 2. 기술 스택 (고정, 변경 금지)

| 항목 | 버전 | 비고 |
|---|---|---|
| Kotlin | 2.0.21 | |
| JDK | 21 | toolchain |
| Spring Boot | 3.5.13 | |
| Spring Kafka | Boot 관리 버전 | |
| jOOQ | 3.20.4 | Boot 기본 3.19.x override |
| HikariCP | 6.3.3 | Boot 기본 override |
| Redis | Spring Data Redis (Lettuce) | |
| kotlinx-coroutines | 1.9.0 | |
| TestContainers | 최신 안정 | mysql, kafka, redis (GenericContainer) |

---

## 3. 의존 모듈 (반드시 사용)

```kotlin
// project 의존 — example-stats-billing 모노레포 내 shared 모듈
implementation(project(":shared:tenant-routing-core"))        // TenantContext, TenantElement
implementation(project(":shared:tenant-routing-spring-boot3")) // TenantRoutingDataSource
implementation(project(":shared:canonical-model"))             // StatSendResultEvent, ResultType, ReconciliationAdapter

// jOOQ codegen artifact — Nexus (env 분기)
val targetEnv = (project.findProperty("targetEnv")
    ?: System.getenv("DEPLOYMENT_ENV")
    ?: "dev").toString()
val jooqVersion = "1.20260416.1"
implementation("com.example.database:jooq-${targetEnv}-java21:${jooqVersion}")
```

**Nexus repository 설정:**
```kotlin
repositories {
    mavenCentral()
    maven {
        url = uri("https://nexus.example-dev.com/repository/maven-public/")
        credentials {
            username = project.findProperty("nexusUsername") as? String ?: System.getenv("NEXUS_USERNAME") ?: "example-corp"
            password = project.findProperty("nexusPassword") as? String ?: System.getenv("NEXUS_PASSWORD") ?: ""
        }
    }
}
```

**jOOQ artifact 문제 발생 시**: 필요한 테이블/컬럼이 없거나 타입이 맞지 않으면 **즉시 작업 중단 + 구체적 누락 목록 보고**. 임의 workaround 금지. 주인님이 별도 세션에서 example-database 수정 후 Nexus 재발행.

---

## 4. Phase 1 산출물 목록

### 4.1. build.gradle.kts

- `application` plugin 아님 — Spring Boot 앱이므로 `org.springframework.boot` + `io.spring.dependency-management`
- ADR-2026-04-15: buildSrc / convention plugin / version catalog 미사용. 모든 의존성 독립 선언.
- jOOQ 3.20.4 + HikariCP 6.3.3 Boot override

### 4.2. Application + YAML

- `StatsConsumerApplication.kt` — `@SpringBootApplication`
- `application.yml` — Kafka, Redis, DataSource 설정 (프로파일: default + test)
- `application-test.yml` — TestContainers 전용 설정

### 4.3. Kafka Consumer

- `StatsSendResultListener.kt` — `@KafkaListener(topics = "example-corp.stat.send-result.json", groupId = "stats-consumer-group")`
- JSON 역직렬화: Jackson + `StatSendResultEvent` (canonical-model 의 data class)
- `ConsumerFactory` / `ConcurrentKafkaListenerContainerFactory` 설정
- 수동 오프셋 커밋 (`AckMode.MANUAL_IMMEDIATE`)

### 4.4. DLT 라우팅

- `DefaultErrorHandler` + `DeadLetterPublishingRecoverer`
- DLT 토픽: `example-corp.stat.send-result-dlt.json`
- DLT 메시지에 에러 reason 헤더 포함 (`__typeid__`, `x-error-reason`)
- 재시도: FixedBackOff(1초, 최대 3회) → 최종 실패 시 DLT

### 4.5. Multi DataSource + TenantRoutingDataSource

설계서 §2.1 기준 DataSource 2종:

| 식별자 | 대상 | 테넌트 |
|---|---|---|
| `primary-ds` | primary RDS | example-corp |
| `secondary-ds` | 외부 RDS | tenant-a, tenant-b, tenant-c, tenant-d, tenant-e, tenant-f, tenant-g, tenant-h |

구성:
```
TenantRoutingDataSource (shared:tenant-routing-spring-boot3)
  └─ LazyConnectionDataSourceProxy 래핑
      ├─ "example-corp" → HikariDataSource (primary-ds)
      └─ "tenant-a"  → HikariDataSource (secondary-ds)
```

Phase 1 범위: DataSource 2종 빈 등록 + TenantRoutingDataSource + LazyConnectionDataSourceProxy 배선까지.
외부 RDS 의 동적 `USE {tenant}` 전환은 Phase 2 Lookup 구현 시 처리.

### 4.6. jOOQ Configuration

- `DslContextFactory` — `forTenant(tenant)` 호출 시 새 Configuration 생성
- `TenantAssertingListener(expected)` — 매 쿼리 직전 `TenantContext.get() == expected` 검증 (ADR §3.4.3)
- Phase 1 에서는 팩토리 구조만 구현, 실제 쿼리 실행은 Phase 2

### 4.7. Redis Dedup 골격

- `DedupService` 인터페이스:
  ```kotlin
  interface DedupService {
      fun tryAcquire(tenant: String, messageId: String): Boolean
  }
  ```
- `RedisDedupService` 구현: `SET NX EX 10800` (3시간 TTL)
- Redis 장애 시 dedup skip + 경고 로그 (처리 계속)

### 4.8. 비즈니스 로직 Stub

Phase 2 에서 채울 자리. 인터페이스만 정의:

```kotlin
interface StatsPipeline {
    fun process(event: StatSendResultEvent)
}
```

Phase 1 구현: 로그만 출력하고 성공 반환.

### 4.9. TestContainers 인프라

- `AbstractIntegrationTest` 베이스 클래스:
  - Kafka (TestContainers)
  - Redis (GenericContainer, redis:7)
- Phase 1 에서는 MySQL TestContainers **불필요** (Smoke Test 가 DB 쿼리를 치지 않음).
- MySQL TestContainers + schema.sql 은 Phase 2 에서 Lookup/Upsert TDD 시작 시 추가.

### 4.10. Smoke Test (TDD 아님)

- `ConsumerSmokeTest` — Kafka 에 StatSendResultEvent JSON 발행 → consumer 수신 확인 → stub 처리 → 오프셋 커밋
- `DltRoutingTest` — 역직렬화 실패 메시지 발행 → DLT 토픽 수신 확인
- `DedupSmokeTest` — 동일 messageId 2회 발행 → 1회만 처리, 2회째 skip 확인

---

## 5. 패키지 구조

```
stats-consumer/
├── build.gradle.kts
├── src/main/kotlin/com/example/stats/consumer/
│   ├── StatsConsumerApplication.kt
│   ├── config/
│   │   ├── KafkaConfig.kt
│   │   ├── DataSourceConfig.kt          // Multi DS + TenantRoutingDataSource
│   │   ├── JooqConfig.kt                // DslContextFactory + TenantAssertingListener
│   │   └── RedisConfig.kt
│   ├── listener/
│   │   └── StatsSendResultListener.kt   // @KafkaListener
│   ├── dedup/
│   │   ├── DedupService.kt              // interface
│   │   └── RedisDedupService.kt         // SET NX 구현
│   ├── pipeline/
│   │   ├── StatsPipeline.kt             // interface
│   │   └── StatsPipelineStub.kt         // Phase 1 stub
│   └── dlt/
│       └── DltPublisher.kt              // DLT 발행 유틸
├── src/main/resources/
│   ├── application.yml
│   └── application-test.yml
├── src/test/kotlin/com/example/stats/consumer/
│   ├── AbstractIntegrationTest.kt       // TestContainers 베이스 (Kafka + Redis)
│   ├── ConsumerSmokeTest.kt
│   ├── DltRoutingTest.kt
│   └── DedupSmokeTest.kt
└── src/test/resources/
    └── (Phase 2 에서 schema.sql 추가 예정)
```

---

## 6. 제약 조건

| # | 제약 | 위반 시 |
|---|---|---|
| C1 | shared 모듈의 API 를 그대로 사용할 것 — TenantContext, TenantRoutingDataSource, StatSendResultEvent, ResultType | 자체 중복 구현 금지 |
| C2 | buildSrc / convention plugin / version catalog 미사용 | ADR 위반 |
| C3 | jOOQ codegen artifact 에서 필요 테이블/컬럼 누락 시 즉시 중단 + 보고 | 임의 workaround 금지 |
| C4 | `application.yml` 에 시크릿 하드코딩 금지 | 환경변수 또는 Secrets Manager 참조 |
| C5 | TestContainers 테스트는 로컬 Docker 에서 실행 가능해야 함 | 외부 서비스 런타임 의존 금지 |
| C6 | Phase 2 확장 포인트: `StatsPipeline` 인터페이스를 통해 비즈니스 로직 주입 | stub 에 로직 혼입 금지 |

---

## 7. 성공 기준

- ✅ `./gradlew :stats-consumer:compileKotlin` 성공 (jOOQ Nexus artifact resolve 포함)
- ✅ `ConsumerSmokeTest` — Kafka → consumer → stub 처리 → 오프셋 커밋
- ✅ `DltRoutingTest` — 잘못된 메시지 → DLT 토픽 수신
- ✅ `DedupSmokeTest` — 중복 메시지 skip
- ✅ Spring ApplicationContext 로드 성공 (DataSource, TenantRoutingDataSource, DslContextFactory, Redis 빈 등록)
- ✅ `StatsPipeline` stub 을 교체하면 비즈니스 로직 주입 가능한 구조 확인

---

## 8. 범위 밖 (Phase 2 에서 수행)

- 원본 테이블 Lookup (3테이블 조인)
- DimensionMapper (9개 차원 매핑)
- StatsUpsertService (2-Tier upsert)
- `__ext__` 경로 분기 처리
- channel_type 변환 enum
- is_substitute 판정 로직

---

## 참조

- T-1 설계서: `T1-stats-consumer/01-stats-consumer-design.md` §1~§8
- ADR-2026-04-14: tech stack + routing 메커니즘
- ADR-2026-04-15: repo strategy (buildSrc 금지, 독립 선언)
- example-database: Nexus artifact `com.example.database:jooq-{env}-java21`
- shared 모듈: tenant-routing-core, tenant-routing-spring-boot3, canonical-model
