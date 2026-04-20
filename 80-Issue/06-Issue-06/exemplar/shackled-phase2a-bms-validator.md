# shackled Phase 2A 지시서: ExtEventValidator

- **체급**: S
- **산출물 유형**: code
- **코드 대상**: backend (Spring Boot 3 Kotlin)
- **TDD**: Red → Green → Refactor
- **구현 위치**: `~/Work/example/example-stats-billing/stats-consumer/`
- **개요**: `shackled-phase2-00-overview.md`

---

## 1. 목적

`StatSendResultEvent.tenant == "__ext__"` 인 이벤트의 **optional 6 필드가 전부 NOT NULL** 임을 검증한다. 하나라도 null 이면 `ExtOptionalFieldNullException` 을 던져 상위 파이프라인이 DLT 로 라우팅하게 한다 (DLT reason: `EXT_OPTIONAL_FIELD_NULL`).

본사 테넌트(`tenant != "__ext__"`) 이벤트는 no-op 으로 통과시킨다.

---

## 2. 산출물

### 2.1. `ExtEventValidator.kt`

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/pipeline/ExtEventValidator.kt`

```kotlin
@Component
class ExtEventValidator {
    /**
     * tenant == EXT_TENANT 인 경우 optional 6 필드 전부 NOT NULL 검증.
     * null 필드가 있으면 ExtOptionalFieldNullException 을 던진다.
     * 본사 테넌트는 no-op.
     */
    fun validate(event: StatSendResultEvent)
}
```

**검증 대상 6 필드** (설계서 §1.1 3a + `StatSendResultEvent` optional 6):
- `sendDate`
- `memberId`
- `channelType`
- `sendSystemType`
- `isSubstitute`
- `originalChannelType`

### 2.2. `ExtOptionalFieldNullException.kt`

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/pipeline/exceptions/ExtOptionalFieldNullException.kt`

```kotlin
class ExtOptionalFieldNullException(
    val missingFields: List<String>,
) : RuntimeException("EXT optional fields are null: $missingFields")
```

누락된 필드명 목록을 메시지에 포함 (운영 디버깅용).

---

## 3. TDD 순서

### RED 1: 본사 테넌트는 optional null 이어도 통과
```
테스트: tenant="example-corp", optional 6 모두 null 인 이벤트 → validate() 정상 리턴
```

### RED 2: EXT 테넌트 + optional 6 모두 채워짐 → 통과
```
테스트: tenant="__ext__", optional 6 모두 채워진 이벤트 → validate() 정상 리턴
```

### RED 3: EXT 테넌트 + optional 1개 null → 예외
```
테스트: tenant="__ext__", sendDate=null, 나머지 채워짐
     → ExtOptionalFieldNullException, missingFields == ["sendDate"]
```

### RED 4: EXT 테넌트 + optional 여러개 null → 예외 + 누락 목록 전부
```
테스트: tenant="__ext__", sendDate=null, memberId=null
     → ExtOptionalFieldNullException, missingFields == ["sendDate", "memberId"]
```

### GREEN
`ExtEventValidator` + `ExtOptionalFieldNullException` 구현. 위 4 테스트 통과.

### REFACTOR
- null 필드 수집은 `listOfNotNull` / `buildList` 관용구 사용
- `StatSendResultEvent.EXT_TENANT` 상수 사용 (문자열 리터럴 금지)

---

## 4. 제약 조건

| # | 제약 |
|---|---|
| L1 | `StatSendResultEvent.EXT_TENANT` 상수 사용. `"__ext__"` 하드코딩 금지 |
| L2 | 누락 필드 목록을 예외 메시지에 포함 (운영 대응 용이) |
| L3 | `ExtEventValidator` 는 stateless — 생성자 주입 의존 없음 |
| L4 | `exceptions/` 패키지 신규 생성 (후속 2C, 2D, 2E, 2F 에서 재사용). 패키지 위치는 overview §6 패키지 트리의 `pipeline/exceptions/` 로 고정. 기능 패키지 (`lookup/`, `upsert/`) 내부로 이동 금지 (DLT reason 매핑 응집성 유지) |
| L5 | 공통 제약 G6 (TDD 역순 금지), G7 (stub 유지) 적용 |
| L6 | `ExtOptionalFieldNullException` 은 Phase 2D `DimensionMapper.mapExt()` 방어 경로에서도 재사용됨 (wtth 묶음 9b). 생성자 시그니처 `(missingFields: List<String>)` 은 두 호출 경로 모두 지원해야 한다 |

---

## 5. 성공 기준

- ✅ RED 1 → GREEN: 본사 이벤트 통과
- ✅ RED 2 → GREEN: EXT + 완비 통과
- ✅ RED 3 → GREEN: EXT + 1개 null 예외
- ✅ RED 4 → GREEN: EXT + 복수 null 예외 + 누락 목록 정확성
- ✅ `ExtEventValidator` Spring 빈 등록 성공
- ✅ Phase 1 기존 테스트 회귀 통과

---

## 6. 테스트 파일 위치

`stats-consumer/src/test/kotlin/com/example/stats/consumer/pipeline/ExtEventValidatorTest.kt` (단위 테스트, Spring Context 불필요)

---

## 7. 참조

- 설계서: `01-stats-consumer-design.md` §1.1 3a, §7.3 (EXT_OPTIONAL_FIELD_NULL)
- `StatSendResultEvent`: optional 6 필드 + `EXT_TENANT` 상수
- 개요: `shackled-phase2-00-overview.md`
