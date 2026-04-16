# wtth Reviewer — BE 페르소나 Acceptance Criteria

> papillon AC Template v3.3 적용.
> 공통 reviewer AC(`common-v0.1.1.md`)를 기반으로 BE 페르소나 특이 사항을 override한다.
> Override되지 않은 항목은 공통 AC를 그대로 사용한다.

---

## 메타 정보

```yaml
skill_name: "wtth:reviewer:be"
parent_ac: "wtth:reviewer v0.1.1 (common-v0.1.1.md)"
version: "0.1.0"
previous_version: null
tier: "tier_1"
output_type: "document"

domain_vocabulary_additions: [
  "트랜잭션", "경계", "정합성", "무결성",
  "스키마", "DDL", "인덱스", "쿼리",
  "API", "스키마", "에러", "응답",
  "락", "동시성", "호환성",
  "N+1", "하위호환"
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
    BE 페르소나로서 설계 문서를 리뷰하여 DB 스키마·트랜잭션 무결성·
    API 계약·비즈니스 로직 분리 관련 finding을 생성한다.

  trigger_conditions:
    - "설계 리뷰 모드에서 BE 페르소나가 투입되었을 때"
    - "wtth 단독 실행 시 리뷰 대상이 설계 문서로 판정된 경우"

  non_trigger_conditions:
    - "UI/UX 의견 (FE 영역)"
    - "인프라 배포 방식 (SRE 영역)"
    - "보안 정책 (SEC 영역)"
    - "쿼리 성능 심층 분석 (DBA 영역)"

  input_spec:
    description: |
      설계 문서 Markdown 발췌. API 명세, DB 스키마 설계, 시퀀스 다이어그램 등.

  output_spec:
    type: "document"
    description: |
      공통 AC의 output_spec을 따른다. BE 페르소나 특화 요구:
      - 각 finding은 체크리스트 항목 참조 `[체크리스트: {항목명}]` 1회 이상
      - 위치 참조는 API 엔드포인트명, 테이블명, 섹션명 등 포함 권장
```

---

## 2. Hard AC override

```yaml
hard_ac_document_additions:
  required_patterns_additional:
    - pattern: "\\[체크리스트:\\s*[^\\]]+\\]"
      scope: "all"

  invariants_additional:
    - id: "INV-BE-01"
      rule: "체크리스트 참조 형식 `[체크리스트: 항목명]`이 최소 1회 이상 등장"
      check: |
        import re
        matches = re.findall(r"\[체크리스트:\s*[^\]]+\]", output_text)
        assert len(matches) >= 1

    - id: "INV-BE-02"
      rule: "위치 참조 — API 엔드포인트, 테이블명, 모듈명 등 구체적 식별자 최소 1회"
      check: |
        has_api = bool(re.search(r"(GET|POST|PUT|PATCH|DELETE)\s+/\S+|/api/\S+", output_text))
        has_table = bool(re.search(r"\b[a-z_]+s?\b\s*(테이블|table)", output_text, re.IGNORECASE))
        has_func = bool(re.search(r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(", output_text))
        has_section = bool(re.search(r"§\d|섹션\s*\d", output_text))
        has_api or has_table or has_func or has_section
```

---

## 3. Artifact AC (공통 사용, `{persona}` 치환만)

```yaml
# ART-WREV-01의 {persona} 치환:
#   rule: "SKILL.md name == 'wtth:reviewer:be'"
```

---

## 4. Fixture AC

```yaml
fixtures:
  - id: "FIX-BE-01"
    description: "트랜잭션 경계 누락 — 주문+재고 분리 트랜잭션"
    meta:
      language: "markdown"
      complexity: "high"
    input:
      code_snippet: |
        ## 주문 생성 프로세스

        1. `POST /api/orders` 호출
        2. 재고 서비스에 `PUT /api/inventory/{itemId}/deduct` 호출하여 재고 차감
        3. 주문 서비스에서 orders 테이블에 INSERT
        4. 결제 서비스에 `POST /api/payments` 호출

        ### 에러 처리
        - 2단계 실패 시: 주문 생성 중단
        - 3단계 실패 시: 재고 원복 API 호출
        - 4단계 실패 시: 주문 상태를 "결제 대기"로 변경
    expected:
      must_match_patterns:
        - "P0"
        - "트랜잭션|정합성|원자성|atomicity"
        - "\\[체크리스트:[^\\]]*트랜잭션[^\\]]*\\]"
      min_length: 100

  - id: "FIX-BE-02"
    description: "N+1 쿼리 — 목록 조회에서 연관 데이터 개별 조회"
    meta:
      language: "markdown"
      complexity: "medium"
    input:
      code_snippet: |
        ## 주문 목록 API

        `GET /api/orders?page=1&size=20`

        ### 조회 로직
        1. orders 테이블에서 20건 조회
        2. 각 주문별로 order_items 테이블에서 상품 목록 조회
        3. 각 상품별로 products 테이블에서 상품 상세 조회
        4. 응답 조립
    expected:
      must_match_patterns:
        - "P[01]"
        - "N\\+1|n\\+1|개별\\s*조회|반복\\s*쿼리"
        - "\\[체크리스트:[^\\]]*N\\+1[^\\]]*\\]"
      min_length: 100

  - id: "FIX-BE-03"
    description: "API 에러 응답 규격 불통일"
    meta:
      language: "markdown"
      complexity: "low"
    input:
      code_snippet: |
        ## 에러 응답 설계

        ### 인증 실패
        ```json
        { "error": "Unauthorized" }
        ```

        ### 주문 생성 실패
        ```json
        { "code": 400, "message": "재고 부족", "detail": { "itemId": 123 } }
        ```

        ### 결제 실패
        ```json
        { "status": "FAIL", "reason": "카드 한도 초과" }
        ```
    expected:
      must_match_patterns:
        - "P[12]"
        - "에러|응답|규격|통일|일관"
        - "\\[체크리스트:[^\\]]*(에러|응답)[^\\]]*\\]"
      min_length: 100

fixture_policy:
  tier_1_minimum_count_document: 3
  pass_rate: 0.8
  verification: "regex, string match, numeric comparison. LLM 호출 없음."

stability:
  selected_fixture: "FIX-BE-01"
  runs: 3
```

---

## 5. Retry Policy

공통 AC의 `retry_policy` 그대로 사용. override 없음.

---

## 6. Tier 2 승격 체크 항목 (BE 특화)

| 관찰 항목 | 승격 트리거 |
|---|---|
| UI/UX 금기 위반 ("이 화면에서는...") | 사례 3회 시 SEM-BE-01 도입 |
| 체크리스트 참조와 실제 finding 불일치 | 사례 2회 시 SEM-BE-02 도입 |
| DBA 영역 침범 (쿼리 최적화 직접 제안) | 사례 2회 시 SEM-BE-03 도입 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 0.1.0 | 2026-04-16 | 최초 작성. code-v0.1.1 구조 복제 + BE 설계 리뷰 override. |

## References
- 공통 AC: [`./common-v0.1.1.md`](./common-v0.1.1.md)
- BE 페르소나 정의: [`../../personas/be.md`](../../personas/be.md)
