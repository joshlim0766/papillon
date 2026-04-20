# shackled Phase 2B 지시서: ChannelType 정규화 + KnownChannel helper (rev2)

- **체급**: S
- **산출물 유형**: code
- **코드 대상**: backend (Kotlin)
- **TDD**: Red → Green → Refactor
- **구현 위치**: `~/Work/example/example-stats-billing/stats-consumer/`
- **개요**: `shackled-phase2-00-overview.md`
- **rev**: 2 (2026-04-17). rev1 의 `ChannelTypeCode` enum 구현은 revert (커밋 `26c5bd5`). 설계서 §4.2 재작성에 맞춰 구조 재설계 — **비즈니스(String 정규화) + 관측 helper(enum) 분리**.

---

## 1. 목적

원본 테이블 `SVC_KND_CD` / `ORG_SVC_KND_CD` 를 **원본 String 그대로** stats 에 저장한다 (데이터 fidelity). 유일한 정규화는 null → `"NONE"` 센티넬 + VARCHAR(40) 초과 truncate 2종.

별도로, 운영 관측/분류용 `KnownChannel` enum 을 helper 로 두어 알려진 채널 메타데이터를 제공한다. **비즈니스 로직은 이 enum 을 참조하지 않는다**.

---

## 2. 산출물

### 2.1. `ChannelType.kt` (비즈니스 — 정규화)

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/code/ChannelType.kt`

```kotlin
object ChannelType {
    const val NONE_SENTINEL = "NONE"
    private const val MAX_LENGTH = 40
    private val log = LoggerFactory.getLogger(ChannelType::class.java)

    /**
     * SVC_KND_CD / ORG_SVC_KND_CD 를 stats 저장용 String 으로 정규화.
     * - null → NONE_SENTINEL
     * - length > 40 → substring(0, 40) + WARN
     * - 그 외 → 원본 그대로
     */
    fun normalize(channelCode: String?): String
}
```

### 2.2. `KnownChannel.kt` (관측 helper — enum)

**위치**: `stats-consumer/src/main/kotlin/com/example/stats/consumer/code/KnownChannel.kt`

```kotlin
/**
 * 알려진 채널 등록부. **비즈니스 로직에 참여하지 않는다**.
 * 메트릭·대시보드·로그 컨텍스트 분류 전용 helper.
 *
 * 등록 누락은 허용 — enum 에 없는 코드가 들어와도 비즈니스 흐름은 정상 동작한다.
 * EXT 코드는 수집 분석 후 파악되는 대로 추가.
 */
enum class KnownChannel(val code: String, val humanReadable: String, val source: Source) {
    SMS("SMS", "SMS", Source.ENGINE),
    LMS("LMS", "LMS", Source.ENGINE),
    MMS("MMS", "MMS", Source.ENGINE),
    ALIMTALK("TKA", "ALIMTALK", Source.ENGINE),
    FRIENDTALK("TKF", "FRIENDTALK", Source.ENGINE),
    BIZMESSAGE("TKT", "BIZMESSAGE", Source.ENGINE),
    ;

    enum class Source { ENGINE, EXT }

    companion object {
        fun findByCode(code: String?): KnownChannel?
    }
}
```

---

## 3. TDD 순서

### RED 1 (`ChannelType.normalize`) — null 입력
```
테스트: ChannelType.normalize(null) == "NONE"
검증: ChannelType.NONE_SENTINEL == "NONE"
검증: warn 로그 없음
```

### RED 2 (`ChannelType.normalize`) — 정확히 40자 (경계)
```
테스트: ChannelType.normalize("A".repeat(40)) == "A".repeat(40)
검증: warn 로그 없음
```

### RED 3 (`ChannelType.normalize`) — 41자 이상 (truncate)
```
테스트: ChannelType.normalize("A".repeat(41)) == "A".repeat(40)
검증: WARN "SVC_KND_CD truncated to 40 chars: AAAA...(41자 원본)"
```

### RED 4 (`ChannelType.normalize`) — 일반 코드 (known + unknown)
```
테스트: ChannelType.normalize("TKA") == "TKA"           // KnownChannel 등록된 코드도 pass-through
테스트: ChannelType.normalize("EXT_NEWTYPE") == "EXT_NEWTYPE"  // 미등록 코드도 pass-through
검증: 두 경우 모두 warn 로그 없음 (비즈니스 정상 동작)
```

### RED 5 (`KnownChannel.findByCode`) — 등록 코드 조회
```
테스트: KnownChannel.findByCode("TKA") == KnownChannel.ALIMTALK
테스트: KnownChannel.findByCode("SMS") == KnownChannel.SMS
검증: ALIMTALK.humanReadable == "ALIMTALK"
검증: ALIMTALK.source == KnownChannel.Source.ENGINE
```

### RED 6 (`KnownChannel.findByCode`) — null / 미등록
```
테스트: KnownChannel.findByCode(null) == null
테스트: KnownChannel.findByCode("EXT_NEWTYPE") == null
테스트: KnownChannel.findByCode("tka") == null   // case-sensitive 고정
```

### GREEN
`ChannelType` object + `KnownChannel` enum 2파일 구현. 위 6그룹 전부 통과.

### REFACTOR
- `BY_CODE` lookup 은 `entries.associateBy { it.code }` — companion 로딩 시 1회 초기화
- 로거는 `LoggerFactory.getLogger(ChannelType::class.java)`
- 로그 포맷은 설계서 §4.2.1 과 정확 일치

---

## 4. 제약 조건

| # | 제약 |
|---|---|
| L1 | `NONE_SENTINEL`, `MAX_LENGTH` 는 상수로 관리. 매직 값 금지 |
| L2 | `normalize()` 는 pass-through 기본 + null/length 2 케이스만 개입. 그 외 원본 가공 금지 (trim·case 변환 등) |
| L3 | **`KnownChannel` 은 비즈니스 로직에서 import 금지**. `pipeline/`·`upsert/`·`mapper/` 패키지 참조 금지 (KDoc 경고 명시). `DimensionMapper` 등 비즈니스 경로는 `ChannelType.normalize()` 만 사용 |
| L4 | 로그 포맷 설계서 §4.2.1 과 일치 (`"SVC_KND_CD truncated to 40 chars: {}"`) |
| L5 | 공통 제약 G6 (TDD 역순 금지) 적용 |
| L6 | `KnownChannel` 등록 누락은 장애 아님. 미등록 코드는 `findByCode(...) == null` 이 정상. 누락 발견 시 개별 PR 로 enum entry 추가 (비즈니스 재배포와 무관) |

---

## 5. 성공 기준

- ✅ RED 1~6 → GREEN: 전체 통과
- ✅ `ChannelType.normalize()` 테스트 4 그룹 (null / 40자 경계 / 41자 truncate / pass-through) 통과
- ✅ `KnownChannel.findByCode()` 테스트 2 그룹 (등록 조회 / null+미등록) 통과
- ✅ `KnownChannel.source` 메타 검증
- ✅ Phase 1 / Phase 2A 기존 테스트 회귀 통과

---

## 6. 테스트 파일 위치

- `stats-consumer/src/test/kotlin/com/example/stats/consumer/code/ChannelTypeTest.kt`
- `stats-consumer/src/test/kotlin/com/example/stats/consumer/code/KnownChannelTest.kt`

**로그 검증 도구**: Logback `ListAppender<ILoggingEvent>` 수동 주입 (Phase 2A 선례).

---

## 7. 참조

- 설계서: `01-stats-consumer-design.md` §4.2 (재작성 완료 — 정규화 규칙 + 관측 helper 분리)
- RDR: `example-stats-billing/docs/decisions/reviews/RDR-2026-04-17-channel-type-code-to-string.md` (구조 전환 결정, 별도 박제)
- DDL: `schema.sql` `stats_send_detail.original_channel_type VARCHAR(40) NOT NULL DEFAULT 'NONE'`
- 개요: `shackled-phase2-00-overview.md`
- Phase 2D 호출점: `shackled-phase2d-dimension-mapper.md` — `ChannelType.normalize(event.channelCode)` (Kafka 이벤트 직접 주입, RDR-2026-04-17-kafka-payload-passthrough-discovery) / `ChannelType.normalize(record.originalChannelCode)` 로 호출
