# wtth Reviewer — ARCH 페르소나 Acceptance Criteria

> papillon AC Template v3.3 적용.
> 공통 reviewer AC(`common-v0.1.1.md`)를 기반으로 ARCH 페르소나 특이 사항을 override한다.
> Override되지 않은 항목은 공통 AC를 그대로 사용한다.

---

## 메타 정보

```yaml
skill_name: "wtth:reviewer:arch"
parent_ac: "wtth:reviewer v0.1.1 (common-v0.1.1.md)"
version: "0.1.0"
previous_version: null
tier: "tier_1"
output_type: "document"

# ARCH는 다중 모드 (PRD/설계/ADR). v0.1.0에서는 설계 리뷰 모드로
# fixture 3개를 구성한다. PRD/ADR 모드 fixture는 v0.2.0에서 추가.
domain_vocabulary_additions: [
  "모듈", "의존성", "순환", "레이어",
  "관심사", "분리", "패턴", "일관성",
  "확장", "수평", "기술", "부채",
  "정합성", "컴포넌트", "인터페이스",
  "ADR", "trade-off"
]

test_mode: "single_turn"
created_by: "Josh"
created_at: "2026-04-16"
updated_at: "2026-04-16"
```

---

## 1. Skill Identity (override)

```yaml
identity:
  purpose: |
    ARCH 페르소나로서 설계 문서·PRD·ADR을 리뷰하여 모듈 구조·의존성
    방향·레이어 분리·패턴 일관성·전체 설계 정합성 관련 finding을 생성한다.

  trigger_conditions:
    - "PRD/설계/ADR 리뷰 모드에서 ARCH 페르소나가 투입되었을 때"
    - "wtth 단독 실행 시 리뷰 대상이 아키텍처 설계 문서인 경우"

  non_trigger_conditions:
    - "비즈니스 가치 판단 (PO/PM 영역)"
    - "코드 스타일 (CODE 영역)"
    - "운영 절차 세부 (SRE 영역)"
    - "개별 API/필드 수준 설계 (BE/FE 영역)"

  input_spec:
    description: |
      설계 문서, PRD, ADR Markdown 발췌. 모듈 구조, 의존성 다이어그램, 기술 결정 등.
      v0.1.0에서는 설계 리뷰 모드 fixture만 구성.

  output_spec:
    type: "document"
    description: |
      공통 AC의 output_spec을 따른다. ARCH 페르소나 특화 요구:
      - 각 finding은 체크리스트 항목 참조 `[체크리스트: {항목명}]` 1회 이상
      - 위치 참조는 모듈명, 레이어명, 컴포넌트명 등 포함 권장
```

---

## 2. Hard AC override

```yaml
hard_ac_document_additions:
  required_patterns_additional:
    - pattern: "\\[체크리스트:\\s*[^\\]]+\\]"
      scope: "all"

  invariants_additional:
    - id: "INV-ARCH-01"
      rule: "체크리스트 참조 형식 `[체크리스트: 항목명]`이 최소 1회 이상 등장"
      check: |
        import re
        matches = re.findall(r"\[체크리스트:\s*[^\]]+\]", output_text)
        assert len(matches) >= 1

    - id: "INV-ARCH-02"
      rule: "위치 참조 — 모듈명, 레이어명, 컴포넌트명 등 구체적 식별자 최소 1회"
      check: |
        has_module = bool(re.search(r"(모듈|서비스|레이어|컴포넌트|패키지)\s*\S+", output_text))
        has_arrow = bool(re.search(r"\S+\s*→\s*\S+", output_text))
        has_named = bool(re.search(r"\b[A-Z][a-zA-Z]+(?:Service|Module|Layer|Controller|Repository)\b", output_text))
        has_module or has_arrow or has_named
```

---

## 3. Artifact AC (공통 사용, `{persona}` 치환만)

```yaml
# ART-WREV-01의 {persona} 치환:
#   rule: "SKILL.md name == 'wtth:reviewer:arch'"
```

---

## 4. Fixture AC

```yaml
# v0.1.0: 설계 리뷰 모드 fixture 3개. PRD/ADR 모드는 v0.2.0에서 추가.
fixtures:
  - id: "FIX-ARCH-01"
    description: "순환 의존 — A → B → C → A"
    meta:
      language: "markdown"
      complexity: "high"
    input:
      code_snippet: |
        ## 모듈 의존성 설계

        ### OrderService
        - 의존: `InventoryService`, `PaymentService`
        - 재고 확인 후 결제 진행

        ### InventoryService
        - 의존: `NotificationService`
        - 재고 부족 시 알림 발송

        ### NotificationService
        - 의존: `OrderService`
        - 주문 상태 변경 시 알림 내용 조회를 위해 OrderService 호출
    expected:
      must_match_patterns:
        - "P0"
        - "순환|circular|cycle|의존.*방향"
        - "\\[체크리스트:[^\\]]*(순환|의존)[^\\]]*\\]"
      must_include:
        - "OrderService"
      min_length: 100

  - id: "FIX-ARCH-02"
    description: "기존 패턴과 불일관 — 프로젝트는 레이어드 아키텍처인데 신규 모듈만 다른 패턴"
    meta:
      language: "markdown"
      complexity: "medium"
    input:
      code_snippet: |
        ## 신규 추천 서비스 설계

        ### 기존 구조 (레이어드 아키텍처)
        - Controller → Service → Repository → DB
        - 모든 비즈니스 로직은 Service 레이어에 위치

        ### 추천 서비스 구조
        - RecommendController → RecommendEngine (비즈니스 로직 + DB 직접 접근)
        - Redis 캐시는 RecommendEngine 내부에서 직접 관리
        - "성능상 이유로 Repository 레이어를 건너뜀"
    expected:
      must_match_patterns:
        - "P[01]"
        - "일관|패턴|레이어|Repository|건너뜀|사유"
        - "\\[체크리스트:[^\\]]*(패턴|일관)[^\\]]*\\]"
      min_length: 100

  - id: "FIX-ARCH-03"
    description: "모듈 간 정합성 깨짐 — 동일 도메인 이벤트를 두 모듈이 다르게 정의"
    meta:
      language: "markdown"
      complexity: "low"
    input:
      code_snippet: |
        ## 이벤트 설계

        ### OrderModule의 OrderCompleted 이벤트
        ```json
        { "orderId": "string", "userId": "string", "total": "number", "completedAt": "ISO8601" }
        ```

        ### ShippingModule이 수신하는 OrderCompleted 이벤트
        ```json
        { "order_id": "string", "user_id": "string", "amount": "number", "timestamp": "unix_epoch" }
        ```

        ShippingModule은 OrderModule이 발행한 이벤트를 구독합니다.
    expected:
      must_match_patterns:
        - "P[01]"
        - "정합성|불일치|스키마|필드명|이벤트"
        - "\\[체크리스트:[^\\]]*(정합성|모듈)[^\\]]*\\]"
      min_length: 100

fixture_policy:
  tier_1_minimum_count_document: 3
  pass_rate: 0.8
  verification: "regex, string match, numeric comparison. LLM 호출 없음."

stability:
  selected_fixture: "FIX-ARCH-01"
  runs: 3
```

---

## 5. Retry Policy

공통 AC의 `retry_policy` 그대로 사용. override 없음.

---

## 6. Tier 2 승격 체크 항목 (ARCH 특화)

| 관찰 항목 | 승격 트리거 |
|---|---|
| 개별 API/필드 금기 위반 ("이 API의 응답 필드를...") | 사례 3회 시 SEM-ARCH-01 도입 |
| 체크리스트 참조와 실제 finding 불일치 | 사례 2회 시 SEM-ARCH-02 도입 |
| 비즈니스 가치 판단 침범 ("이 기능은 필요 없다") | 사례 2회 시 SEM-ARCH-03 도입 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 0.1.0 | 2026-04-16 | 최초 작성. 설계 리뷰 모드 fixture 3개. PRD/ADR 모드는 v0.2.0 예정. |

## References
- 공통 AC: [`./common-v0.1.1.md`](./common-v0.1.1.md)
- ARCH 페르소나 정의: [`../../personas/arch.md`](../../personas/arch.md)
