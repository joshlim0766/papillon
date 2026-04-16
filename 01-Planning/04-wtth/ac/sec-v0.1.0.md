# wtth Reviewer — SEC 페르소나 Acceptance Criteria

> papillon AC Template v3.3 적용.
> 공통 reviewer AC(`common-v0.1.1.md`)를 기반으로 SEC 페르소나 특이 사항을 override한다.
> Override되지 않은 항목은 공통 AC를 그대로 사용한다.

---

## 메타 정보

```yaml
skill_name: "wtth:reviewer:sec"
parent_ac: "wtth:reviewer v0.1.1 (common-v0.1.1.md)"
version: "0.1.0"
previous_version: null
tier: "tier_1"
output_type: "document"

# SEC는 다중 모드 (PRD/설계/ADR/운영 절차). v0.1.0에서는 설계 리뷰 모드로
# fixture 3개를 구성한다. 다른 모드 fixture는 실측 후 v0.2.0에서 추가.
domain_vocabulary_additions: [
  "인증", "인가", "우회", "토큰",
  "입력", "검증", "인젝션", "XSS",
  "민감", "노출", "시크릿", "하드코딩",
  "감사", "로그", "컴플라이언스",
  "권한", "최소", "RBAC"
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
    SEC 페르소나로서 설계 문서·PRD·ADR·운영 절차를 리뷰하여 인증/인가·
    입력 검증·민감 데이터 노출·감사 로그·컴플라이언스 관련 finding을 생성한다.

  trigger_conditions:
    - "PRD/설계/ADR/운영 절차 리뷰 모드에서 SEC 페르소나가 투입되었을 때"
    - "wtth 단독 실행 시 리뷰 대상에 보안 관련 설계가 포함된 경우"

  non_trigger_conditions:
    - "비즈니스 로직 (BE 영역)"
    - "UI/UX (FE 영역)"
    - "성능 최적화 (BE/DBA 영역)"

  input_spec:
    description: |
      설계 문서, PRD, ADR, 운영 절차 Markdown 발췌.
      v0.1.0에서는 설계 리뷰 모드 fixture만 구성.

  output_spec:
    type: "document"
    description: |
      공통 AC의 output_spec을 따른다. SEC 페르소나 특화 요구:
      - 각 finding은 체크리스트 항목 참조 `[체크리스트: {항목명}]` 1회 이상
      - 위치 참조는 API 엔드포인트, 인증 경로, 데이터 필드명 등 포함 권장
```

---

## 2. Hard AC override

```yaml
hard_ac_document_additions:
  required_patterns_additional:
    - pattern: "\\[체크리스트:\\s*[^\\]]+\\]"
      scope: "all"

  invariants_additional:
    - id: "INV-SEC-01"
      rule: "체크리스트 참조 형식 `[체크리스트: 항목명]`이 최소 1회 이상 등장"
      check: |
        import re
        matches = re.findall(r"\[체크리스트:\s*[^\]]+\]", output_text)
        assert len(matches) >= 1

    - id: "INV-SEC-02"
      rule: "위치 참조 — API 엔드포인트, 인증 경로, 데이터 필드 등 구체적 식별자 최소 1회"
      check: |
        has_api = bool(re.search(r"(GET|POST|PUT|PATCH|DELETE)\s+/\S+|/api/\S+", output_text))
        has_field = bool(re.search(r"\b(password|token|secret|key|api_key|user_id|reviewer_id)\b", output_text, re.IGNORECASE))
        has_func = bool(re.search(r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(", output_text))
        has_api or has_field or has_func
```

---

## 3. Artifact AC (공통 사용, `{persona}` 치환만)

```yaml
# ART-WREV-01의 {persona} 치환:
#   rule: "SKILL.md name == 'wtth:reviewer:sec'"
```

---

## 4. Fixture AC

```yaml
# v0.1.0: 설계 리뷰 모드 fixture 3개. PRD/ADR/운영 절차 모드는 v0.2.0에서 추가.
fixtures:
  - id: "FIX-SEC-01"
    description: "인증/인가 우회 — reviewer_id 미검증"
    meta:
      language: "markdown"
      complexity: "high"
    input:
      code_snippet: |
        ## 리뷰 생성 API

        `POST /api/reviews`

        ### 요청 본문
        ```json
        {
          "productId": "prod-123",
          "reviewerId": "user-456",
          "rating": 5,
          "content": "좋은 상품입니다"
        }
        ```

        ### 인증
        - Bearer 토큰 필수 (Authorization 헤더)
        - 토큰에서 user_id 추출

        ### 처리 로직
        - 요청 본문의 reviewerId로 리뷰 생성
        - reviews 테이블에 INSERT
    expected:
      must_match_patterns:
        - "P0"
        - "인증|인가|우회|검증|reviewer.?id|user.?id|토큰"
        - "\\[체크리스트:[^\\]]*(인증|인가|우회)[^\\]]*\\]"
      min_length: 100

  - id: "FIX-SEC-02"
    description: "시크릿 하드코딩 — API 키가 설정 파일에 평문 노출"
    meta:
      language: "markdown"
      complexity: "medium"
    input:
      code_snippet: |
        ## 외부 결제 서비스 연동 설계

        ### 설정
        - 결제 API 엔드포인트: `https://pg.example.com/v1/charge`
        - API Key: `config/payment.yml`에 `api_key: "sk_live_a1b2c3d4e5f6"` 형태로 저장
        - 환경별(dev/staging/prod) 동일 설정 파일 구조 사용

        ### 호출 로직
        - HTTP POST with `X-API-Key` 헤더
    expected:
      must_match_patterns:
        - "P0"
        - "시크릿|하드코딩|평문|api.?key|환경.*변수|vault"
        - "\\[체크리스트:[^\\]]*(시크릿|하드코딩)[^\\]]*\\]"
      min_length: 100

  - id: "FIX-SEC-03"
    description: "민감 데이터 과다 노출 — 사용자 목록 API에서 전체 필드 반환"
    meta:
      language: "markdown"
      complexity: "low"
    input:
      code_snippet: |
        ## 사용자 목록 API

        `GET /api/users?page=1&size=20`

        ### 응답
        ```json
        {
          "users": [
            {
              "id": "user-1",
              "name": "홍길동",
              "email": "hong@example.com",
              "phone": "010-1234-5678",
              "ssn": "900101-1234567",
              "passwordHash": "$2b$10$...",
              "createdAt": "2025-01-01"
            }
          ]
        }
        ```
    expected:
      must_match_patterns:
        - "P[01]"
        - "민감|노출|ssn|password|최소화|필터"
        - "\\[체크리스트:[^\\]]*(민감|노출)[^\\]]*\\]"
      min_length: 100

fixture_policy:
  tier_1_minimum_count_document: 3
  pass_rate: 0.8
  verification: "regex, string match, numeric comparison. LLM 호출 없음."

stability:
  selected_fixture: "FIX-SEC-01"
  runs: 3
```

---

## 5. Retry Policy

공통 AC의 `retry_policy` 그대로 사용. override 없음.

---

## 6. Tier 2 승격 체크 항목 (SEC 특화)

| 관찰 항목 | 승격 트리거 |
|---|---|
| 비즈니스 로직 금기 위반 | 사례 3회 시 SEM-SEC-01 도입 |
| 체크리스트 참조와 실제 finding 불일치 | 사례 2회 시 SEM-SEC-02 도입 |
| 리뷰 모드 간 체크리스트 혼용 (설계 리뷰에서 운영 절차 체크리스트 인용) | 사례 2회 시 SEM-SEC-03 도입 |

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 0.1.0 | 2026-04-16 | 최초 작성. 설계 리뷰 모드 fixture 3개. PRD/ADR/운영 절차 모드는 v0.2.0 예정. |

## References
- 공통 AC: [`./common-v0.1.1.md`](./common-v0.1.1.md)
- SEC 페르소나 정의: [`../../personas/sec.md`](../../personas/sec.md)
