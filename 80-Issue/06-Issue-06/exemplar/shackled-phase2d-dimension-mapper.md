# shackled Phase 2D 지시서: DimensionMapper

- **체급**: S
- **산출물 유형**: code
- **코드 대상**: backend (Kotlin, 순수 로직)
- **TDD**: Red → Green → Refactor
- **구현 위치**: `~/Work/example/example-stats-billing/stats-consumer/`
- **개요**: `shackled-phase2-00-overview.md`
- **의존**: 2A (`ExtEventValidator`), 2B (`ChannelType.normalize`), 2C (`OriginalMessageRecord`)

---

## 1. 목적

`StatSendResultEvent` (DTO) + `OriginalMessageRecord` (원본 조회 결과) → `StatsDimensions` (9차원) 변환한다 (설계서 §4).

**두 경로**:
- 본사 경로: `map(event, record)` — DTO + 원본 조회 결과 조합. DTO optional 6 필드는 이 경로에서 미사용 (모두 원본 조회 값으로 치환)
- EXT 경로: `mapExt(event)` — DTO optional 6 필드만으로 완성 (lookup 생략)

---

## 2. 산출물

### 2.1. `StatsDimensions.kt`

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/mapper/StatsDimensions.kt`

```kotlin
data class StatsDimensions(
    val tenant: String,
    val sendDate: LocalDate,
    val memberId: String,
    val channelType: String,
    val originalChannelType: String,  // 본발송이면 "NONE"
    val isSubstitute: Boolean,
    val resultCode: String,
    val resultCategory: String,
    val sendSystemType: String,       // "API" | "WEB" | "EXT"
)
```

### 2.2. `DimensionMapper.kt`

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/mapper/DimensionMapper.kt`

```kotlin
@Component
class DimensionMapper {
    /**
     * 본사 경로: DTO + 원본 조회 결과 → 9차원.
     * - sendDate ← record.registeredAt.toLocalDate()
     * - memberId ← record.memberId
     * - channelType ← ChannelType.normalize(event.channelCode)  (Kafka 이벤트 직접 주입 — RDR-2026-04-17-kafka-payload-passthrough-discovery)
     * - originalChannelType ← ChannelType.normalize(record.originalChannelCode)  (null이면 "NONE")
     * - isSubstitute ← record.originalChannelCode != null  (§4.3 재정립)
     * - sendSystemType ← record.apiInstanceId 가 null 또는 blank → "WEB", 아니면 "API"
     */
    fun map(event: StatSendResultEvent, record: OriginalMessageRecord): StatsDimensions

    /**
     * EXT 경로: DTO optional 6 필드로 9차원 구성 (lookup 생략).
     * ExtEventValidator 가 선행 호출되어 optional 필드들의 NOT NULL 이 보장된 상태여야 한다.
     * 호출 순서 버그 방지를 위해 `!!` 대신 `?: throw ExtOptionalFieldNullException(...)` 사용.
     */
    fun mapExt(event: StatSendResultEvent): StatsDimensions
}
```

**`isSubstitute` 판정 로직** (설계서 §4.3 재정립):
```kotlin
private fun isSubstitute(record: OriginalMessageRecord): Boolean =
    record.originalChannelCode != null  // NULL=본발송 시도, NOT NULL=대체발송 시도
```

> **변경 이력 (2026-04-17 wtth 묶음 6+ 반영)**: 이전 SUBTXT 3컬럼 기반 판정 폐기. 레거시 `SendFailureRepository.updateTarget` 의 그룹 단위 이력 컬럼이라 시도 단위 플래그로 부적절. 올바른 판정은 `TNT_INTG_MSG_SND.ORG_SVC_KND_CD` null 여부.

**`mapExt` 방어 패턴** (wtth 묶음 9b 반영):
```kotlin
fun mapExt(event: StatSendResultEvent): StatsDimensions {
    val missing = buildList {
        if (event.sendDate == null) add("sendDate")
        if (event.memberId == null) add("memberId")
        if (event.channelType == null) add("channelType")
        if (event.sendSystemType == null) add("sendSystemType")
        if (event.isSubstitute == null) add("isSubstitute")
        if (event.originalChannelType == null) add("originalChannelType")
    }
    if (missing.isNotEmpty()) throw ExtOptionalFieldNullException(missing)

    return StatsDimensions(
        tenant = event.tenant,
        sendDate = event.sendDate!!,
        memberId = event.memberId!!,
        channelType = event.channelType!!,
        originalChannelType = event.originalChannelType!!,
        isSubstitute = event.isSubstitute!!,
        resultCode = event.resultCode,
        resultCategory = event.resultCategory,
        sendSystemType = event.sendSystemType!!,
    )
}
```

**`sendSystemType` 판정** (wtth DBA-11 반영):
```kotlin
private fun sendSystemType(record: OriginalMessageRecord): String =
    if (record.apiInstanceId.isNullOrBlank()) "WEB" else "API"
```

---

## 3. TDD 순서

### RED 1: 일반 본사 이벤트 → 9차원 정상 매핑 (본발송)
```
event: tenant="example-corp", messageId="msg-1", channelCode="TKA", resultCode="0000", resultType=SUCCESS, resultCategory="SUCCESS"
record: memberId="m1", originalChannelCode=null, registeredAt=2026-04-17T10:00:00, apiInstanceId=null
→ StatsDimensions(
    tenant="example-corp", sendDate=2026-04-17, memberId="m1",
    channelType="TKA", originalChannelType="NONE",
    isSubstitute=false, resultCode="0000", resultCategory="SUCCESS", sendSystemType="WEB"
  )
```

### RED 2: `apiInstanceId=null` → sendSystemType="WEB"
### RED 3: `apiInstanceId="api-01"` → sendSystemType="API"
### RED 4: `apiInstanceId=""` (blank) → sendSystemType="WEB" (DBA-11 반영)

### RED 5: 대체발송 — `originalChannelCode != null` → isSubstitute=true
```
event: channelCode="SMS", ...
record: originalChannelCode="TKA", ...
→ channelType="SMS", originalChannelType="TKA", isSubstitute=true
```

### RED 6: 본발송 — `originalChannelCode=null` → isSubstitute=false, originalChannelType="NONE"
```
event: channelCode="TKA", ...
record: originalChannelCode=null, ...
→ channelType="TKA", originalChannelType="NONE", isSubstitute=false
```

### RED 7: EXT 경로 정상 — `mapExt()`
```
event: tenant="__ext__", messageId="bms-1", resultCode="9001", resultType=FAILURE,
       resultCategory="FAILURE",
       sendDate=2026-04-17, memberId="__ext__123_abc",
       channelType="EXT_A", sendSystemType="EXT",
       isSubstitute=false, originalChannelType="NONE"
→ StatsDimensions(
    tenant="__ext__", sendDate=2026-04-17, memberId="__ext__123_abc",
    channelType="EXT_A", originalChannelType="NONE",
    isSubstitute=false, resultCode="9001", resultCategory="FAILURE", sendSystemType="EXT"
  )
```

### RED 8: EXT 경로 방어 — validator 누락 시 `!!` 대신 ExtOptionalFieldNullException (wtth 9b 반영)
```
event: tenant="__ext__", sendDate=null, 나머지 채워짐
실행: mapExt(event)
검증: ExtOptionalFieldNullException(missingFields=["sendDate"])
      (NullPointerException 아님 — DLT reason 이 EXT_OPTIONAL_FIELD_NULL 로 귀결)
```

### GREEN
`DimensionMapper.map()` + `mapExt()` + `isSubstitute` / `sendSystemType` 헬퍼 구현. 위 8 케이스 통과.

### REFACTOR
- `isSubstitute` / `sendSystemType` 판정은 private 메서드로 추출
- `channelType` / `originalChannelType` 매핑은 `ChannelType.normalize` 위임 (이중 매핑 금지)
- `mapExt` 의 missing 필드 수집 로직 inline 유지 (readability)

---

## 4. 제약 조건

| # | 제약 |
|---|---|
| L1 | `DimensionMapper` 는 stateless 순수 함수. DB / 외부 호출 금지 |
| L2 | EXT 경로는 `!!` 대신 `?: throw ExtOptionalFieldNullException(missing)` 방어 패턴 사용. validator 선행 누락 시에도 DLT reason 이 `EXT_OPTIONAL_FIELD_NULL` 로 귀결되도록 한다 |
| L3 | `channelType` / `originalChannelType` 매핑은 `ChannelType.normalize` 위임 (DRY) |
| L4 | `sendDate` 는 `record.registeredAt.toLocalDate()` 만 사용. JDBC 세션 타임존이 `Asia/Seoul` 로 설정되어 있어야 정확 (application.yml `serverTimezone=Asia/Seoul` 확인 — DBA-13 반영) |
| L5 | `StatsDimensions` 는 data class (불변) |
| L6 | `isSubstitute` 는 `originalChannelCode != null` 단일 기준. SUBTXT 3컬럼 / `SBT_SND_YN` / `SUBTXT_USE_YN` 사용 금지 (설계서 §4.3) |
| L7 | `sendSystemType` 은 `apiInstanceId.isNullOrBlank()` 으로 판정 (빈 문자열 방어) |
| L8 | 공통 제약 G6 적용 |

---

## 5. 성공 기준

- ✅ RED 1 → GREEN: 본발송 기본 케이스
- ✅ RED 2, 3, 4 → GREEN: `sendSystemType` 3분기 (null / 값 / blank)
- ✅ RED 5, 6 → GREEN: `isSubstitute` 양방향 (대체발송 / 본발송)
- ✅ RED 7 → GREEN: EXT 정상 경로
- ✅ RED 8 → GREEN: EXT 방어 (NullPointerException 대신 ExtOptionalFieldNullException)
- ✅ Phase 1 + 2A + 2B + 2C 기존 테스트 회귀 통과

---

## 6. 테스트 파일 위치

`stats-consumer/src/test/kotlin/com/example/stats/consumer/mapper/DimensionMapperTest.kt` (단위 테스트, Spring Context 불필요)

---

## 7. 참조

- 설계서: `01-stats-consumer-design.md` §4 (전체), §4.1 (9차원 표), §4.2 (channel_type), §4.3 (is_substitute 재정립)
- wtth 1라운드 RDR: `example-stats-billing/docs/decisions/reviews/RDR-2026-04-17-phase2-directive-review.md` (묶음 6+, 9b, DBA-11, DBA-13 반영)
- `StatSendResultEvent`: 기본 6 (channelCode 승격) + optional 6 필드 (주석 교정은 2F 반영. RDR-2026-04-17-kafka-payload-passthrough-discovery)
- `OriginalMessageRecord` (2C, SUBTXT 3필드 + channelCode 제거된 4필드 버전)
- `ChannelType.normalize` (2B)
- `ExtOptionalFieldNullException` (2A)
- 개요: `shackled-phase2-00-overview.md`
