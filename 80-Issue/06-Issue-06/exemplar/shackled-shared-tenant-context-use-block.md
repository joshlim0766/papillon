# shackled 선행 지시서: TenantContext.use 블록 API 추가

- **체급**: XS
- **산출물 유형**: code
- **코드 대상**: backend (Kotlin, shared 모듈)
- **TDD**: Red → Green → Refactor
- **구현 위치**: `~/Work/example/example-stats-billing/shared/tenant-routing-core/`
- **선행 조건**: Phase 2 진입 전 이 지시서 완료 필수
- **목적**: wtth 리뷰 RDR-2026-04-17 묶음 1 (P0) 해소

---

## 1. 목적

`shared/tenant-routing-core/TenantContext` 에 **블록 스코프 내에서 tenant 를 안전하게 전환/복원** 하는 inline 함수 `use(tenant) { block }` 을 추가한다.

Phase 2C/2F 지시서가 이 API 를 전제로 작성되어 있으며, 현재 모듈에는 `set()` / `get()` / `currentOrNull()` / `clear()` 4개 메서드만 존재해 중첩 호출 시 컨텍스트 누출 리스크가 있다.

---

## 2. 배경

현재 `TenantSchemaRoutingTest` 등 기존 테스트는 `TenantContext.clear()` + `TenantContext.set(tenant)` + `@AfterEach clear()` 패턴을 수동으로 반복한다. 이 패턴은:
- `set(A)` 후 `set(B)` 중첩 상태에서 `clear()` 호출 시 A 도 소실
- try/finally 누락 시 예외 경로에서 컨텍스트 누출
- Phase 2 의 `StatsPipelineImpl.process()` 가 EXT 분기와 본사 분기에서 서로 다른 tenant 블록을 중첩해야 하므로 안전한 복원 필요

`use` 블록 API 가 이 복잡성을 내부로 은닉한다.

---

## 3. 산출물

### 3.1. `TenantContext.use` inline 함수 추가

**위치**: `shared/tenant-routing-core/src/main/kotlin/com/example/tenant/routing/TenantContext.kt`

기존 파일의 `clear()` 메서드 하단에 추가:

```kotlin
/**
 * 블록 스코프 내에서 tenant 를 전환하고, 블록 종료 시 이전 값을 복원한다.
 *
 * 중첩 호출 시나리오:
 *   TenantContext.use("example-corp") {
 *       // inner tenant = "example-corp"
 *       TenantContext.use("tenant-b") {
 *           // inner tenant = "tenant-b"
 *       }
 *       // 복원: tenant = "example-corp"
 *   }
 *   // 복원: tenant = null (바깥에 이전 값이 없었으므로 clear)
 *
 * 예외 발생 시에도 finally 블록이 이전 값을 복원한다.
 *
 * @param tenant 블록 내에서 사용할 tenant 식별자
 * @param block 블록. 반환값은 use() 의 반환값이 된다.
 */
inline fun <T> use(tenant: String, block: () -> T): T {
    val previous = currentOrNull()
    set(tenant)
    try {
        return block()
    } finally {
        if (previous != null) set(previous) else clear()
    }
}
```

### 3.2. 기존 `set()` / `clear()` 메서드 그대로 유지

기존 공개 API 4종 (`set`, `get`, `currentOrNull`, `clear`) 는 변경 없음 — 기존 호출부 회귀 방어.

---

## 4. TDD 순서

**위치**: `shared/tenant-routing-core/src/test/kotlin/com/example/tenant/routing/TenantContextUseTest.kt` (신규)

### RED 1: 기본 블록 전환 + 복원

```kotlin
@Test
fun `use 블록 진입 시 tenant 전환, 종료 시 이전 상태로 복원`() {
    TenantContext.clear()
    assertThat(TenantContext.currentOrNull()).isNull()

    val result = TenantContext.use("example-corp") {
        assertThat(TenantContext.get()).isEqualTo("example-corp")
        "OK"
    }

    assertThat(result).isEqualTo("OK")
    assertThat(TenantContext.currentOrNull()).isNull()  // 이전 null 로 복원
}
```

### RED 2: 중첩 호출 시 각 레이어 복원

```kotlin
@Test
fun `use 블록 중첩 시 바깥 레이어의 tenant 가 정확히 복원된다`() {
    TenantContext.clear()

    TenantContext.use("example-corp") {
        assertThat(TenantContext.get()).isEqualTo("example-corp")

        TenantContext.use("tenant-b") {
            assertThat(TenantContext.get()).isEqualTo("tenant-b")
        }

        // 안쪽 블록 종료 후 바깥 tenant 로 복원
        assertThat(TenantContext.get()).isEqualTo("example-corp")
    }

    assertThat(TenantContext.currentOrNull()).isNull()
}
```

### RED 3: 블록 내부에서 예외 발생 시에도 복원

```kotlin
@Test
fun `use 블록 내부 예외 시 finally 경로로 이전 tenant 복원`() {
    TenantContext.set("example-corp")

    try {
        TenantContext.use("tenant-b") {
            assertThat(TenantContext.get()).isEqualTo("tenant-b")
            throw IllegalStateException("simulated")
        }
        fail("예외가 전파되어야 함")
    } catch (e: IllegalStateException) {
        assertThat(e.message).isEqualTo("simulated")
    }

    // 예외 경로에서도 복원
    assertThat(TenantContext.get()).isEqualTo("example-corp")

    TenantContext.clear()
}
```

### RED 4: 블록 반환값 전달

```kotlin
@Test
fun `use 블록의 반환값이 호출자에게 전달된다`() {
    val result: Int = TenantContext.use("example-corp") {
        42
    }
    assertThat(result).isEqualTo(42)
}
```

### GREEN

`TenantContext.use` inline 함수 추가. 위 4 테스트 통과.

### REFACTOR

- `inline` 키워드 유지 (람다 캡처 비용 제거)
- KDoc 에 중첩 시나리오 코드 예시 포함

---

## 5. 제약 조건

| # | 제약 |
|---|---|
| L1 | 기존 `set()` / `get()` / `currentOrNull()` / `clear()` 메서드 시그니처 변경 금지 (기존 호출부 회귀 방어) |
| L2 | `use` 는 **inline fun** 으로 선언 (람다 캡처 오버헤드 제거, 제네릭 타입 T 지원) |
| L3 | 블록 내부 예외는 그대로 전파. `use` 가 catch 하지 않음 |
| L4 | 중첩 호출 시 이전 값 복원은 `currentOrNull()` 로 읽어 저장 후 `set(previous)` 또는 `clear()` 로 분기 |

---

## 6. 성공 기준

- ✅ RED 1~4 → GREEN 전부 통과
- ✅ 기존 `TenantSchemaRoutingTest` / `TenantContextTest` 등 기존 테스트 회귀 통과
- ✅ `TenantContext.kt` 의 4개 기존 메서드 시그니처 변경 없음
- ✅ `./gradlew :shared:tenant-routing-core:test` 전체 통과
- ✅ Phase 2C/2F 지시서의 `TenantContext.use(tenant) { ... }` 예시 코드가 이 API 로 컴파일 가능함을 확인 (컴파일만, 실구현은 Phase 2 에서)

---

## 7. 참조

- wtth 1라운드 리뷰 묶음 1 결정: ARCH-01 + BE-01 + DBA-01 P0 수용 A
- RDR: `example-stats-billing/docs/decisions/reviews/RDR-2026-04-17-phase2-directive-review.md`
- Phase 2C 지시서: `shackled-phase2c-original-lookup.md` §2.3, §4 L3
- Phase 2F 지시서: `shackled-phase2f-pipeline-assembly.md` §2.1
- 현재 `TenantContext.kt`: `shared/tenant-routing-core/src/main/kotlin/com/example/tenant/routing/TenantContext.kt`
