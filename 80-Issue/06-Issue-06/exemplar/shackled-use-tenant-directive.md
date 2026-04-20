# shackled 지시서: 외부 RDS 동적 USE {tenant} 전환

- **체급**: S
- **산출물 유형**: code
- **코드 대상**: backend (Spring Boot 3 Kotlin)
- **TDD**: Red → Green → Refactor
- **구현 위치**: `~/Work/example/example-stats-billing/`
- **상위 설계서**: `T1-stats-consumer/01-stats-consumer-design.md` §2

---

## 1. 목적

외부 RDS는 단일 MySQL 인스턴스에 테넌트별 database(schema)가 분리되어 있다.
현재 `TenantRoutingDataSource`가 모든 외부 테넌트를 동일한 `secondaryDataSource`로 라우팅하지만, **커넥션 획득 후 `USE {tenant}` 실행이 없어** 올바른 database에 접근하지 못한다.

**`SchemaAwareDataSource`** 래퍼를 구현하여, `getConnection()` 호출 시 자동으로 `USE {schema}`를 실행한다.

---

## 2. 현재 상태 (AS-IS)

```
TenantRoutingDataSource
  ├─ "example-corp"     → primaryDataSource (HikariDS, jdbc:mysql://.../example-corp)
  ├─ "tenant-a"      → secondaryDataSource  (HikariDS, jdbc:mysql://.../???)
  ├─ "tenant-b"          → secondaryDataSource  ← 같은 DS, schema 전환 없음
  ├─ "tenant-c"          → secondaryDataSource
  └─ ...8개 테넌트  → secondaryDataSource
```

문제: tenant-a, tenant-b, tenant-c 등이 모두 같은 커넥션 풀을 공유하되, `USE tenant-a` / `USE tenant-b` 분기가 없다.

---

## 3. 목표 상태 (TO-BE)

```
TenantRoutingDataSource
  ├─ "example-corp"     → primaryDataSource (변경 없음)
  ├─ "tenant-a"      → SchemaAwareDataSource(secondaryDS, "tenant-a")
  ├─ "tenant-b"          → SchemaAwareDataSource(secondaryDS, "tenant-b")
  ├─ "tenant-c"          → SchemaAwareDataSource(secondaryDS, "tenant-c")
  └─ ...            → SchemaAwareDataSource(secondaryDS, "{tenant}")
```

`SchemaAwareDataSource.getConnection()` → `delegate.getConnection()` → `stmt.execute("USE \`{schema}\`")` → 반환.

---

## 4. 산출물

### 4.1. SchemaAwareDataSource

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/config/SchemaAwareDataSource.kt`

```kotlin
class SchemaAwareDataSource(
    private val delegate: DataSource,
    private val schema: String
) : DataSource by delegate {

    override fun getConnection(): Connection {
        val conn = delegate.connection
        switchSchema(conn)
        return conn
    }

    override fun getConnection(username: String, password: String): Connection {
        val conn = delegate.getConnection(username, password)
        switchSchema(conn)
        return conn
    }

    private fun switchSchema(conn: Connection) {
        conn.createStatement().use { it.execute("USE `$schema`") }
    }
}
```

핵심 설계 결정:
- `DataSource by delegate` — Kotlin delegation. getConnection 2종만 override, 나머지 위임.
- schema는 생성 시점에 확정 (TenantContext 의존 없음 — 이미 TenantRoutingDataSource가 분기 완료).
- backtick 이스케이프 (`\`schema\``) — schema 이름에 예약어 포함 가능성 방어.

### 4.2. DataSourceConfig 수정

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/config/DataSourceConfig.kt`

변경 내용:
```kotlin
// AS-IS
secondaryTenants.forEach { tenant -> targetDataSources[tenant] = secondaryDataSource }

// TO-BE
secondaryTenants.forEach { tenant ->
    targetDataSources[tenant] = SchemaAwareDataSource(secondaryDataSource, tenant)
}
```

example-corp 테넌트는 변경 없음 (HikariCP jdbc-url에 database 지정됨).

### 4.3. AbstractIntegrationTest 수정

**위치**: `stats-consumer/src/test/kotlin/com/example/stats/consumer/AbstractIntegrationTest.kt`

변경 내용:
- MySQL TestContainers에 `withInitScript("init-schemas.sql")` 추가
- tenant-a jdbc-url에서 database 지정 제거 (root 커넥션, schema는 USE로 전환)

### 4.4. init-schemas.sql (TC 전용)

**위치**: `stats-consumer/src/test/resources/init-schemas.sql`

```sql
-- TestContainers 초기화: primary DB(기본) + 외부 테넌트 DB 2개 (테스트용 최소 셋)
-- 실 테넌트 8개 전부 만들 필요 없음. 대표 2개로 USE 전환 검증 충분.

CREATE DATABASE IF NOT EXISTS tenant-a;
CREATE DATABASE IF NOT EXISTS tenant-b;

-- 각 DB에 Lookup 테이블 생성 (schema.sql 의 Lookup 부분 복제)
-- primary DB는 MySQLContainer.withDatabaseName("example-corp")로 이미 생성됨
```

schema.sql은 primary DB 전용. tenant-a/tenant-b DB에도 Lookup 테이블이 필요하므로 init-schemas.sql에서 `USE tenant-a; SOURCE lookup DDL;` 패턴 사용.

실제로는 init-schemas.sql에 CREATE DATABASE + 각 DB별 Lookup DDL을 인라인으로 넣는다 (MySQL SOURCE 명령은 클라이언트 전용이므로 JDBC init script에서 사용 불가).

### 4.5. 테스트 파일

**위치**: `stats-consumer/src/test/kotlin/com/example/stats/consumer/config/SchemaAwareDataSourceTest.kt`

---

## 5. TDD 순서

### RED 1: SchemaAwareDataSource 단위 테스트

```
테스트: getConnection 호출 시 USE 문 실행 확인
- mock DataSource → mock Connection → mock Statement
- SchemaAwareDataSource("tenant-b").getConnection()
- verify: stmt.execute("USE `tenant-b`") 호출됨
```

### GREEN 1: SchemaAwareDataSource 구현

최소 구현으로 RED 1 통과.

### RED 2: 실제 MySQL USE 전환 통합 테스트

```
테스트: TC MySQL에 tenant-a, tenant-b DB 생성 → SchemaAwareDataSource로 커넥션 → SELECT DATABASE() 검증
- SchemaAwareDataSource(rawDS, "tenant-a").getConnection() → SELECT DATABASE() == "tenant-a"
- SchemaAwareDataSource(rawDS, "tenant-b").getConnection() → SELECT DATABASE() == "tenant-b"
- 같은 underlying DataSource에서 schema만 다르게 전환되는지 확인
```

### GREEN 2: init-schemas.sql 작성 + AbstractIntegrationTest 수정

TC MySQL에 다중 DB 생성. GREEN 2 통과.

### RED 3: DataSourceConfig 통합 — TenantContext 기반 e2e

```
테스트: Spring Context 로드 + TenantContext.set("tenant-b") → @Primary dataSource.getConnection() → SELECT DATABASE() == "tenant-b"
- TenantContext.set("example-corp") → SELECT DATABASE() == "example-corp"
- TenantContext.set("tenant-a") → SELECT DATABASE() == "tenant-a"
```

### GREEN 3: DataSourceConfig 수정

secondaryTenants 루프에 SchemaAwareDataSource 래핑 적용. GREEN 3 통과.

### REFACTOR

- 불필요한 코드 제거
- 기존 Smoke Test (ConsumerSmokeTest, DltRoutingTest, DedupSmokeTest) 회귀 확인

---

## 6. 제약 조건

| # | 제약 | 위반 시 |
|---|---|---|
| C1 | SchemaAwareDataSource는 stats-consumer 내부 클래스로 둔다. shared 모듈 이동은 추후 결정. | 과도한 추상화 금지 |
| C2 | TenantRoutingDataSource, TenantContext 등 shared 모듈 API 변경 금지 | 기존 모듈 불변 |
| C3 | example-corp 테넌트 경로는 변경 없음 (HikariCP jdbc-url에 database 포함) | 회귀 금지 |
| C4 | init-schemas.sql에서 테스트용 외부 테넌트 DB는 최소 2개 (tenant-a, tenant-b) | 8개 전부 불필요 |
| C5 | schema.sql(기존)은 primary DB 전용. tenant-a/tenant-b Lookup DDL은 init-schemas.sql에 인라인 | 파일 분리 유지 |
| C6 | 기존 Smoke Test 3종 회귀 통과 필수 | 깨지면 수정 후 진행 |

---

## 7. 성공 기준

- ✅ RED 1 → GREEN 1: SchemaAwareDataSource 단위 테스트 통과
- ✅ RED 2 → GREEN 2: TC MySQL 다중 DB USE 전환 통합 테스트 통과
- ✅ RED 3 → GREEN 3: TenantContext 기반 e2e 테스트 통과
- ✅ 기존 Smoke Test 3종 (ConsumerSmokeTest, DltRoutingTest, DedupSmokeTest) 회귀 통과
- ✅ `./gradlew :stats-consumer:test` 전체 통과

---

## 8. 참조

- 설계서: `01-stats-consumer-design.md` §2 (Multi Datasource 라우팅)
- 현재 DataSourceConfig: `stats-consumer/src/main/kotlin/.../config/DataSourceConfig.kt`
- TenantRoutingDataSource: `shared/tenant-routing-spring-boot3/`
- TenantContext: `shared/tenant-routing-core/`
- Phase 1 지시서: `shackled-phase1-directive.md` §4.5 (AS-IS 구조)
